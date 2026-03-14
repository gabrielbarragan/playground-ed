from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_superadmin, UserContext
from app.api.superadmin import process
from app.api.superadmin.serializer import RoleUpdateSerializer
from app.api.courses.serializer import CourseInSerializer

router = APIRouter(prefix="/api/v1/superadmin", tags=["Superadmin"])


@router.get("/users")
async def list_users(
    include_inactive: bool = Query(default=False),
    _: UserContext = Depends(get_current_superadmin),
):
    return process.list_users(include_inactive=include_inactive)


@router.put("/users/{user_id}/role")
async def update_role(
    user_id: str,
    body: RoleUpdateSerializer,
    ctx: UserContext = Depends(get_current_superadmin),
):
    try:
        return process.update_role(user_id, body.role, requesting_user_id=ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/courses")
async def list_courses(_: UserContext = Depends(get_current_superadmin)):
    return process.list_courses()


@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(
    body: CourseInSerializer,
    _: UserContext = Depends(get_current_superadmin),
):
    try:
        return process.create_course(name=body.name, code=body.code, description=body.description)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/courses/{course_id}/toggle")
async def toggle_course(
    course_id: str,
    _: UserContext = Depends(get_current_superadmin),
):
    try:
        return process.toggle_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))