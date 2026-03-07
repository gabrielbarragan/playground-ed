from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_user, UserContext
from app.api.dashboard.handler import ActivityHandler

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/activity")
async def my_activity(ctx: UserContext = Depends(get_current_user)):
    """Heatmap de actividad de los últimos 15 días del usuario autenticado."""
    try:
        return ActivityHandler.get_user_heatmap(ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/courses/{course_id}/users")
async def course_users(course_id: str):
    """Resumen de actividad de todos los usuarios de un curso (últimos 15 días)."""
    try:
        return ActivityHandler.get_course_users_summary(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/courses/{course_id}/ranking")
async def course_ranking(
    course_id: str,
    limit: int = Query(default=20, ge=1, le=100),
):
    """Ranking de usuarios de un curso ordenado por puntos totales."""
    try:
        return ActivityHandler.get_course_ranking(course_id, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))