from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_admin, UserContext
from app.api.admin import analytics_process as process

router = APIRouter(prefix="/api/v1/admin/analytics", tags=["Admin Analytics"])


@router.get("/error-heatmap")
async def error_heatmap(
    course_id: Optional[str] = Query(default=None),
    challenge_id: Optional[str] = Query(default=None),
    days: int = Query(default=7, ge=1, le=30),
    _: UserContext = Depends(get_current_admin),
):
    """
    Mapa de calor de errores: agrupado por línea, concepto y tipo de error.
    Filtros opcionales: course_id, challenge_id, days (1–30).
    """
    return process.get_error_heatmap(
        course_id=course_id,
        challenge_id=challenge_id,
        days=days,
    )


@router.get("/concepts")
async def concepts_ranking(
    course_id: Optional[str] = Query(default=None),
    days: int = Query(default=7, ge=1, le=30),
    _: UserContext = Depends(get_current_admin),
):
    """Ranking de conceptos Python con más errores en el período."""
    return process.get_concepts_ranking(course_id=course_id, days=days)


@router.get("/challenges/{challenge_id}/errors")
async def challenge_errors(
    challenge_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Detalle de errores por línea y historial reciente para un reto específico."""
    return process.get_challenge_errors(challenge_id)
