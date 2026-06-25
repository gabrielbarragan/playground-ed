from datetime import datetime
from typing import Optional

from app.api.course_requests.querysets import CourseChangeRequestQueryset
from app.api.courses.querysets import CourseQueryset
from app.api.users.querysets import UserQueryset

_requests = CourseChangeRequestQueryset()
_courses = CourseQueryset()
_users = UserQueryset()


def _serialize_request(req) -> dict:
    return {
        "id": str(req.id),
        "user": {
            "id": str(req.user.id),
            "first_name": req.user.first_name,
            "last_name": req.user.last_name,
            "email": req.user.email,
        },
        "from_course": {
            "id": str(req.from_course.id),
            "name": req.from_course.name,
            "code": req.from_course.code,
        },
        "to_course": {
            "id": str(req.to_course.id),
            "name": req.to_course.name,
            "code": req.to_course.code,
        },
        "reason": req.reason,
        "status": req.status,
        "rejection_reason": req.rejection_reason,
        "resolved_by": str(req.resolved_by.id) if req.resolved_by else None,
        "resolved_at": req.resolved_at.isoformat() if req.resolved_at else None,
        "created_at": req.created_at.isoformat(),
    }


def create_change_request(user_id: str, to_course_id: str, reason: str = "") -> dict:
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    to_course = _courses.get_active_by_id(to_course_id)
    if not to_course:
        raise ValueError("El curso destino no existe o no está activo")

    if str(user.course.id) == to_course_id:
        raise ValueError("No podés solicitar cambio al mismo curso en el que estás")

    existing = _requests.get_pending_by_user(user)
    if existing:
        raise ValueError("Ya tenés una solicitud de cambio de curso pendiente")

    req = _requests.create(
        user=user,
        from_course=user.course,
        to_course=to_course,
        reason=reason,
    )
    return _serialize_request(req)


def get_my_pending_request(user_id: str) -> Optional[dict]:
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    req = _requests.get_pending_by_user(user)
    if not req:
        return None
    return _serialize_request(req)


def list_pending_requests(admin_course_ids: Optional[list[str]] = None) -> dict:
    requests = list(_requests.get_pending_by_courses(admin_course_ids))
    items = [_serialize_request(r) for r in requests]
    return {"total": len(items), "requests": items}


def resolve_request(
    request_id: str,
    action: str,
    resolver_id: str,
    rejection_reason: str = "",
) -> dict:
    req = _requests.get_by_id(request_id)
    if not req:
        raise ValueError("Solicitud no encontrada")
    if req.status != "pending":
        raise ValueError("Esta solicitud ya fue resuelta")

    from app.models.user import User
    resolver = User.objects(id=resolver_id).first()

    if action == "approve":
        req.user.course = req.to_course
        req.user.save()
        req.status = "approved"
    elif action == "reject":
        req.status = "rejected"
        req.rejection_reason = rejection_reason
    else:
        raise ValueError("Acción inválida")

    req.resolved_by = resolver
    req.resolved_at = datetime.utcnow()
    req.save()
    return _serialize_request(req)
