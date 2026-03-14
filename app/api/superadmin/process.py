from app.api.superadmin.querysets import SuperAdminUserQueryset
from app.api.courses.querysets import CourseQueryset

_users = SuperAdminUserQueryset()
_courses = CourseQueryset()

_ROLE_FIELDS = {
    "student":    {"is_admin": False, "is_superadmin": False},
    "admin":      {"is_admin": True,  "is_superadmin": False},
    "superadmin": {"is_admin": True,  "is_superadmin": True},
}


def _serialize_user(user) -> dict:
    course = user.course
    role = "superadmin" if user.is_superadmin else "admin" if user.is_admin else "student"
    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "is_superadmin": user.is_superadmin,
        "role": role,
        "total_points": user.total_points,
        "course": {
            "id": str(course.id),
            "name": course.name,
            "code": course.code,
        } if course else None,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


def _serialize_course(course) -> dict:
    return {
        "id": str(course.id),
        "name": course.name,
        "code": course.code,
        "description": course.description,
        "is_active": course.is_active,
        "created_at": course.created_at.isoformat(),
    }


def list_users(include_inactive: bool = False) -> dict:
    users = _users.get_all(include_inactive=include_inactive)
    result = [_serialize_user(u) for u in users]
    return {"total": len(result), "users": result}


def update_role(user_id: str, role: str, requesting_user_id: str) -> dict:
    if user_id == requesting_user_id:
        raise ValueError("No podés cambiar tu propio rol")

    user = _users.get_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    fields = _ROLE_FIELDS[role]
    user.is_admin = fields["is_admin"]
    user.is_superadmin = fields["is_superadmin"]
    user.save()
    return _serialize_user(user)


def list_courses() -> dict:
    courses = _courses.get_all()
    result = [_serialize_course(c) for c in courses]
    return {"total": len(result), "courses": result}


def create_course(name: str, code: str, description: str) -> dict:
    if _courses.get_by_code(code):
        raise ValueError(f"Ya existe un curso con el código '{code.upper()}'")
    course = _courses.create(name=name, code=code.upper(), description=description)
    return _serialize_course(course)


def toggle_course(course_id: str) -> dict:
    course = _courses.get_by_id(course_id)
    if not course:
        raise ValueError("Curso no encontrado")
    _courses.update(course, is_active=not course.is_active)
    return _serialize_course(course)