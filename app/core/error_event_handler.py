"""
Handler para guardar ErrorEvent tras ejecuciones fallidas.
Centraliza la lógica de captura para ser llamado desde code-runs (HTTP) y ws/run (WS).
"""
from app.core.error_parser import parse_error_line, parse_error_type, parse_error_msg
from app.core.ast_analyzer import detect_concepts


class ErrorEventHandler:

    @staticmethod
    def save(user_id: str, code: str, stderr: str, challenge_id: str | None = None) -> None:
        """
        Guarda un ErrorEvent si hay stderr significativo.
        Importación lazy del modelo para evitar ciclos en el arranque.
        """
        if not stderr or not stderr.strip():
            return
        try:
            from app.models.error_event import ErrorEvent
            from app.models.user import User

            user = User.objects(id=user_id).first()
            if not user:
                return

            challenge_ref = None
            if challenge_id:
                from app.models.challenge import Challenge
                challenge_ref = Challenge.objects(id=challenge_id).first()

            ErrorEvent(
                user=user,
                challenge=challenge_ref,
                code=code,
                error_type=parse_error_type(stderr),
                error_line=parse_error_line(stderr),
                error_msg=parse_error_msg(stderr),
                concepts=detect_concepts(code),
                course=user.course if hasattr(user, "course") else None,
            ).save()
        except Exception:
            # Nunca propagar errores de logging para no romper la ejecución del usuario
            pass
