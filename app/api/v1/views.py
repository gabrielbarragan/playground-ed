from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

from app.core.auth import get_optional_user, UserContext, decode_token
from app.core.handlers import CodeExecutorHandler
from app.core.process import InteractiveExecutor
from app.api.v1.serializer import CodeExecutionInSerializer
from app.api.dashboard.handler import ActivityHandler

router = APIRouter()


@router.post("/api/code-runs", tags=["Code Runs"])
async def run_code(
    request: CodeExecutionInSerializer,
    ctx: Optional[UserContext] = Depends(get_optional_user),
) -> JSONResponse:
    """Ejecución no interactiva (sin input()). Registra actividad si hay sesión."""
    try:
        response = await CodeExecutorHandler.execute_code(request.code)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    success = response.get("return_code", 1) == 0
    ActivityHandler.log_execution(
        user_id=ctx.id if ctx else None,
        code=request.code,
        success=success,
    )

    return JSONResponse(content=response, status_code=200)


@router.websocket("/ws/run")
async def ws_run(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
):
    """
    Ejecución interactiva. Acepta token JWT como query param para loguear actividad.
    Cliente envía:
      { "type": "run",   "code": "..." }
      { "type": "stdin", "data": "..." }
      { "type": "kill" }
    """
    user_id = None
    if token:
        user_id_raw = decode_token(token)
        if user_id_raw:
            user_id = user_id_raw

    await websocket.accept()
    try:
        msg = await websocket.receive_json()
        if msg.get("type") != "run" or not msg.get("code", "").strip():
            await websocket.send_json({
                "type": "error",
                "message": "Se esperaba { type: 'run', code: '...' }",
            })
            return

        code = msg["code"]
        ActivityHandler.log_execution(user_id=user_id, code=code, success=True)

        await InteractiveExecutor().run(code, websocket)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass