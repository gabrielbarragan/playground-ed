import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.auth import hash_password, verify_password, create_access_token
from app.core.constants import JWT_ALGORITHM, JWT_SECRET
from app.api.users.querysets import UserQueryset
from app.api.courses.querysets import CourseQueryset

_users = UserQueryset()
_courses = CourseQueryset()

_RESET_EXPIRE_MINUTES = 15
_EMAIL_CHANGE_EXPIRE_MINUTES = 30


def _create_typed_token(user_id: str, token_type: str, expire_minutes: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload = {"sub": user_id, "type": token_type, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _decode_typed_token(token: str, expected_type: str) -> Optional[str]:
    """Retorna user_id si el token es válido y del tipo esperado, else None."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload.get("sub")
    except JWTError:
        return None


def _serialize_user(user) -> dict:
    course = user.course
    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_admin": user.is_admin,
        "badge": user.badge or "🐍",
        "is_superadmin": user.is_superadmin,
        "course": {
            "id": str(course.id),
            "name": course.name,
            "code": course.code,
        },
        "total_points": user.total_points,
        "created_at": user.created_at.isoformat(),
    }


def register(first_name: str, last_name: str, email: str, password: str, course_id: str) -> dict:
    if _users.get_by_email(email):
        raise ValueError("El correo ya está registrado")

    course = _courses.get_active_by_id(course_id)
    if not course:
        raise ValueError("Curso no encontrado")

    user = _users.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=hash_password(password),
        course=course,
    )
    return _serialize_user(user)


def login(email: str, password: str) -> dict:
    user = _users.get_active_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Credenciales incorrectas")

    _users.update(user, last_login=datetime.utcnow())
    return {
        "access_token": create_access_token(str(user.id)),
        "token_type": "bearer",
    }


def get_profile(user_id: str) -> Optional[dict]:
    user = _users.get_active_by_id(user_id)
    if not user:
        return None
    return _serialize_user(user)


def update_profile(user_id: str, first_name: Optional[str], last_name: Optional[str]) -> dict:
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    fields = {}
    if first_name:
        fields["first_name"] = first_name
    if last_name:
        fields["last_name"] = last_name
    if fields:
        _users.update(user, **fields)

    return _serialize_user(user)


def set_badge(user_id: str, emoji: str) -> dict:
    from app.api.badges.process import badge_exists
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")
    if not badge_exists(emoji):
        raise ValueError("Badge no válido")
    _users.update(user, badge=emoji)
    return _serialize_user(user)


# ── Recuperación de contraseña ─────────────────────────────

async def forgot_password_process(email: str) -> None:
    """Genera token y envía email. Siempre retorna sin error (anti-enumeration)."""
    from app.core.email import send_password_reset_email

    user = _users.get_active_by_email(email)
    if not user:
        return  # silencioso

    token = _create_typed_token(str(user.id), "password_reset", _RESET_EXPIRE_MINUTES)
    _users.set_reset_token(user, _hash_token(token))
    await send_password_reset_email(user.email, token)


async def reset_password_process(token: str, new_password: str) -> None:
    user_id = _decode_typed_token(token, "password_reset")
    if not user_id:
        raise ValueError("Token inválido o expirado")

    token_hash = _hash_token(token)
    user = _users.get_by_reset_token_hash(token_hash)
    if not user or str(user.id) != user_id:
        raise ValueError("Token inválido o ya utilizado")

    _users.update_password(user, hash_password(new_password))


# ── Cambio de email (estudiante) ───────────────────────────

async def request_email_change_process(user_id: str, new_email: str) -> None:
    from app.core.email import send_email_change_confirmation

    if _users.get_by_email(new_email):
        raise ValueError("El correo ya está en uso")

    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    token = _create_typed_token(user_id, "email_change", _EMAIL_CHANGE_EXPIRE_MINUTES)
    _users.set_pending_email(user, new_email, _hash_token(token))
    await send_email_change_confirmation(new_email, token)


async def confirm_email_change_process(token: str) -> None:
    user_id = _decode_typed_token(token, "email_change")
    if not user_id:
        raise ValueError("Token inválido o expirado")

    token_hash = _hash_token(token)
    user = _users.get_by_email_change_token_hash(token_hash)
    if not user or str(user.id) != user_id:
        raise ValueError("Token inválido o ya utilizado")

    _users.confirm_email_change(user)