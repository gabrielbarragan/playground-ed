from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_admin, UserContext
from app.api.admin import process

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/users")
async def list_users(
    course_id: Optional[str] = Query(default=None),
    include_inactive: bool = Query(default=False),
    _: UserContext = Depends(get_current_admin),
):
    """Lista todos los usuarios. Filtrable por curso e incluye inactivos opcionalmente."""
    try:
        return process.list_users(course_id=course_id, include_inactive=include_inactive)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Activa un usuario desactivado."""
    try:
        return process.set_user_active(user_id, is_active=True)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Desactiva un usuario activo."""
    try:
        return process.set_user_active(user_id, is_active=False)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/stats")
async def global_stats(_: UserContext = Depends(get_current_admin)):
    """Estadísticas globales: usuarios, ejecuciones y resumen por curso."""
    return process.get_global_stats()