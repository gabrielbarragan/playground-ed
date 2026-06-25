from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, get_current_admin, get_admin_course_ids, UserContext
from app.api.course_requests import process
from app.api.course_requests.serializer import (
    CreateCourseChangeRequestSerializer,
    ResolveCourseChangeRequestSerializer,
)

student_router = APIRouter(prefix="/api/v1/users/me/course-change-request", tags=["Course Change Requests"])
admin_router = APIRouter(prefix="/api/v1/admin/course-change-requests", tags=["Admin - Course Change Requests"])


@student_router.post("", status_code=status.HTTP_201_CREATED)
async def create_request(
    body: CreateCourseChangeRequestSerializer,
    ctx: UserContext = Depends(get_current_user),
):
    try:
        return process.create_change_request(ctx.id, body.to_course_id, body.reason)
    except ValueError as e:
        code = status.HTTP_409_CONFLICT if "pendiente" in str(e) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(e))


@student_router.get("")
async def get_my_request(ctx: UserContext = Depends(get_current_user)):
    try:
        return process.get_my_pending_request(ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@admin_router.get("")
async def list_pending_requests(ctx: UserContext = Depends(get_current_admin)):
    return process.list_pending_requests(admin_course_ids=get_admin_course_ids(ctx))


@admin_router.put("/{request_id}/resolve")
async def resolve_request(
    request_id: str,
    body: ResolveCourseChangeRequestSerializer,
    ctx: UserContext = Depends(get_current_admin),
):
    try:
        return process.resolve_request(
            request_id=request_id,
            action=body.action,
            resolver_id=ctx.id,
            rejection_reason=body.rejection_reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
