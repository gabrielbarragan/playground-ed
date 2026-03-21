from datetime import datetime, timedelta
from typing import Optional

from app.api.admin.querysets import AdminUserQueryset
from app.api.courses.querysets import CourseQueryset
from app.api.dashboard.querysets import ActivityQueryset

_users = AdminUserQueryset()
_courses = CourseQueryset()
_activity = ActivityQueryset()


def _serialize_user(user) -> dict:
    course = user.course
    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "total_points": user.total_points,
        "course": {
            "id": str(course.id),
            "name": course.name,
            "code": course.code,
        } if course else None,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


def list_users(course_id: Optional[str] = None, include_inactive: bool = False) -> dict:
    if course_id:
        course = _courses.get_active_by_id(course_id)
        if not course:
            raise ValueError("Curso no encontrado")
        users = _users.get_by_course(course, include_inactive=include_inactive)
    else:
        users = _users.get_all(include_inactive=include_inactive)

    result = [_serialize_user(u) for u in users if not u.is_admin]
    return {"total": len(result), "users": result}


def set_user_active(user_id: str, is_active: bool) -> dict:
    user = _users.get_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")
    if user.is_admin:
        raise ValueError("No se puede modificar el estado de un administrador")

    user.is_active = is_active
    user.save()
    return _serialize_user(user)


def list_courses() -> dict:
    courses = list(_courses.get_all())
    result = [
        {
            "id": str(c.id),
            "name": c.name,
            "code": c.code,
            "description": c.description,
            "is_active": c.is_active,
            "created_at": c.created_at.isoformat(),
        }
        for c in courses
    ]
    return {"total": len(result), "courses": result}


def create_course(name: str, code: str, description: str) -> dict:
    from app.api.courses.querysets import CourseQueryset
    qs = CourseQueryset()
    if qs.get_by_code(code):
        raise ValueError(f"Ya existe un curso con el código '{code.upper()}'")
    course = qs.create(name=name, code=code.upper(), description=description)
    return {
        "id": str(course.id),
        "name": course.name,
        "code": course.code,
        "description": course.description,
        "is_active": course.is_active,
        "created_at": course.created_at.isoformat(),
    }


def toggle_course(course_id: str) -> dict:
    from app.api.courses.querysets import CourseQueryset
    qs = CourseQueryset()
    course = qs.get_by_id(course_id)
    if not course:
        raise ValueError("Curso no encontrado")
    qs.update(course, is_active=not course.is_active)
    return {
        "id": str(course.id),
        "name": course.name,
        "code": course.code,
        "description": course.description,
        "is_active": course.is_active,
        "created_at": course.created_at.isoformat(),
    }


async def admin_change_email_process(user_id: str, new_email: str) -> dict:
    from app.core.email import send_email_change_admin_notification

    user = _users.get_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")
    if user.is_admin:
        raise ValueError("No se puede modificar el email de un administrador")

    if _users.get_by_email(new_email):
        raise ValueError("El correo ya está en uso")

    old_email = user.email
    _users.update_email(user, new_email)
    await send_email_change_admin_notification(old_email, new_email)
    return _serialize_user(user)


def get_global_stats() -> dict:
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    last_7_days_start = today - timedelta(days=6)

    active_users = _users.count_active()
    inactive_users = _users.count_inactive()
    courses = list(_courses.get_active())

    activity_last_7 = _activity.get_all_users_in_range(last_7_days_start, today)
    total_executions_7d = sum(a.executions for a in activity_last_7)
    active_user_ids = {str(a.user.id) for a in activity_last_7}

    courses_summary = []
    for course in courses:
        users = list(_users.get_by_course(course))
        courses_summary.append({
            "id": str(course.id),
            "name": course.name,
            "code": course.code,
            "active_users": len(users),
        })

    return {
        "users": {
            "active": active_users,
            "inactive": inactive_users,
            "total": active_users + inactive_users,
            "active_last_7_days": len(active_user_ids),
        },
        "executions": {
            "last_7_days": total_executions_7d,
        },
        "courses": courses_summary,
    }