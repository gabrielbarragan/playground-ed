import asyncio
import os
import resource
import sys
import tempfile
from abc import ABC, abstractmethod


# ── Helpers compartidos ───────────────────────────────────────────────────────

def _apply_resource_limits() -> None:
    """
    Corre en el proceso hijo (preexec_fn) antes de exec().
    Nota: RLIMIT_AS se omite — Python necesita > 256MB de espacio virtual
    solo para arrancar. El tiempo de CPU lo limita RLIMIT_CPU y el tiempo
    de pared lo controla asyncio.wait_for.
    """
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 * 1024 * 1024, 1 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))


def _clean_env() -> dict:
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": "/tmp",
        "LANG": os.environ.get("LANG", "en_US.UTF-8"),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _write_temp(code: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False,
        encoding="utf-8", prefix="playground_",
    ) as f:
        f.write(code)
        return f.name


# ── Strategy base ─────────────────────────────────────────────────────────────

class SandboxStrategy(ABC):
    @abstractmethod
    async def execute(self, code: str) -> dict:
        """Retorna {stdout, stderr, return_code}."""


# ── Strategy: Subprocess sin interactividad (POST /api/code-runs) ─────────────

class SubprocessSandbox(SandboxStrategy):

    TIMEOUT = 10
    MAX_OUTPUT = 50_000

    async def execute(self, code: str) -> dict:
        tmp_path = _write_temp(code)
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, tmp_path,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=_clean_env(),
                preexec_fn=_apply_resource_limits,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=self.TIMEOUT,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return {
                    "stdout": "",
                    "stderr": f"TimeoutError: ejecución superó {self.TIMEOUT}s.",
                    "return_code": 1,
                }

            return {
                "stdout": stdout_b.decode("utf-8", errors="replace")[: self.MAX_OUTPUT],
                "stderr": stderr_b.decode("utf-8", errors="replace")[: self.MAX_OUTPUT],
                "return_code": 0 if proc.returncode == 0 else 1,
            }
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# ── Strategy: WebSocket interactivo (/ws/run) ─────────────────────────────────

class InteractiveExecutor:
    """
    Ejecuta código Python en un subprocess con stdin/stdout/stderr
    conectados a un WebSocket. Permite input() interactivo en tiempo real.

    Protocolo de mensajes
    ─────────────────────
    Cliente → Servidor:
      { "type": "stdin", "data": "texto\n" }
      { "type": "kill" }

    Servidor → Cliente:
      { "type": "stdout", "data": "..." }
      { "type": "stderr", "data": "..." }
      { "type": "exit",   "return_code": 0 }
      { "type": "timeout" }
    """

    WALL_TIMEOUT = 120  # tiempo máximo total de sesión en segundos
    MAX_OUTPUT = 50_000

    async def run(self, code: str, websocket) -> int:
        tmp_path = _write_temp(code)
        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, tmp_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=_clean_env(),
                preexec_fn=_apply_resource_limits,
            )

            stdout_task = asyncio.create_task(
                self._stream_pipe(proc.stdout, "stdout", websocket)
            )
            stderr_task = asyncio.create_task(
                self._stream_pipe(proc.stderr, "stderr", websocket)
            )
            stdin_task = asyncio.create_task(
                self._handle_stdin(proc, websocket)
            )

            # Espera a que el proceso termine o se agote el tiempo de pared
            try:
                await asyncio.wait_for(proc.wait(), timeout=self.WALL_TIMEOUT)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                await self._send(websocket, {"type": "timeout"})

            # El proceso ya terminó; cancelar stdin y drenar el output restante
            stdin_task.cancel()
            try:
                await stdin_task
            except asyncio.CancelledError:
                pass

            await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)

            exit_code = proc.returncode if proc.returncode is not None else 1
            await self._send(websocket, {
                "type": "exit",
                "return_code": exit_code,
            })
            return exit_code

        except Exception:
            if proc and proc.returncode is None:
                proc.kill()
            return 1
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def _stream_pipe(self, pipe, msg_type: str, websocket) -> None:
        total = 0
        try:
            while True:
                chunk = await pipe.read(4096)
                if not chunk:
                    break
                total += len(chunk)
                if total > self.MAX_OUTPUT:
                    await self._send(websocket, {
                        "type": "stderr",
                        "data": "\n[Salida truncada: límite de 50 KB alcanzado]\n",
                    })
                    break
                await self._send(websocket, {
                    "type": msg_type,
                    "data": chunk.decode("utf-8", errors="replace"),
                })
        except Exception:
            pass

    async def _handle_stdin(self, proc, websocket) -> None:
        try:
            while proc.returncode is None:
                msg = await websocket.receive_json()
                kind = msg.get("type")
                if kind == "stdin" and proc.stdin:
                    data = msg.get("data", "")
                    proc.stdin.write(data.encode("utf-8"))
                    await proc.stdin.drain()
                elif kind == "kill":
                    proc.kill()
                    break
        except Exception:
            if proc.returncode is None:
                proc.kill()

    @staticmethod
    async def _send(websocket, data: dict) -> None:
        try:
            await websocket.send_json(data)
        except Exception:
            pass


# ── Strategy: Ejecución con stdin para test cases ─────────────────────────────

class TestCaseSandbox(SandboxStrategy):
    """Ejecuta código con stdin predefinido. Usado para evaluar test cases."""

    TIMEOUT = 10
    MAX_OUTPUT = 50_000

    def __init__(self, stdin_data: str = ""):
        self._stdin = stdin_data

    async def execute(self, code: str) -> dict:
        tmp_path = _write_temp(code)
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, tmp_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=_clean_env(),
                preexec_fn=_apply_resource_limits,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(input=self._stdin.encode("utf-8")),
                    timeout=self.TIMEOUT,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return {
                    "stdout": "",
                    "stderr": f"TimeoutError: ejecución superó {self.TIMEOUT}s.",
                    "return_code": 1,
                }
            return {
                "stdout": stdout_b.decode("utf-8", errors="replace")[: self.MAX_OUTPUT],
                "stderr": stderr_b.decode("utf-8", errors="replace")[: self.MAX_OUTPUT],
                "return_code": 0 if proc.returncode == 0 else 1,
            }
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# ── Context (compatibilidad con handlers.py) ──────────────────────────────────

class CodeExecutor:
    def __init__(self, strategy: SandboxStrategy | None = None):
        self._sandbox: SandboxStrategy = strategy or SubprocessSandbox()

    async def execute(self, code: str) -> dict:
        return await self._sandbox.execute(code)

    @classmethod
    async def execute_with_stdin(cls, code: str, stdin: str) -> dict:
        return await TestCaseSandbox(stdin_data=stdin).execute(code)