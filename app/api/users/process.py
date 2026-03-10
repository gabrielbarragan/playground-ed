from datetime import datetime
from typing import Optional

from app.core.auth import hash_password, verify_password, create_access_token
from app.api.users.querysets import UserQueryset
from app.api.courses.querysets import CourseQueryset

_users = UserQueryset()
_courses = CourseQueryset()


def _serialize_user(user) -> dict:
    course = user.course
    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_admin": user.is_admin,
        "badge": user.badge or "🐍",
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