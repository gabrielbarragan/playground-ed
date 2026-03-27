"""
Funciones puras para extraer información estructurada del stderr de Python.
Usadas por el módulo de analítica docente (ErrorEvent).
"""
import re

_LINE_RE = re.compile(r'File ".+", line (\d+)')


def parse_error_line(stderr: str) -> int | None:
    """Extrae el número de línea del último frame del traceback."""
    matches = _LINE_RE.findall(stderr)
    return int(matches[-1]) if matches else None


def parse_error_type(stderr: str) -> str:
    """
    Extrae el tipo de excepción de la última línea del traceback.
    Retorna cadena vacía si no puede determinarse.
    """
    for line in reversed(stderr.splitlines()):
        line = line.strip()
        if not line or line.startswith("File") or line.startswith("Traceback"):
            continue
        # Líneas tipo "TypeError: ..." o "SyntaxError: invalid syntax"
        if ":" in line:
            candidate = line.split(":")[0].strip()
            # Filtra líneas que no son un nombre de excepción
            if candidate and candidate[0].isupper() and " " not in candidate:
                return candidate
    return ""


def parse_error_msg(stderr: str) -> str:
    """Retorna la última línea significativa del stderr (máx 300 chars)."""
    lines = [l.strip() for l in stderr.splitlines() if l.strip()]
    return lines[-1][:300] if lines else ""
