from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_admin, get_current_user, UserContext
from app.api.sandbox_achievements.handler import AchievementHandler
from app.api.sandbox_achievements.serializer import CreateAchievementSerializer, UpdateAchievementSerializer

admin_router = APIRouter(prefix="/api/v1/admin/sandbox-achievements", tags=["Admin – Logros"])
student_router = APIRouter(prefix="/api/v1/users/me", tags=["Logros"])


# ── Admin CRUD ─────────────────────────────────────────────────────────────────

@admin_router.get("")
async def list_achievements(
    include_inactive: bool = Query(default=False),
    _: UserContext = Depends(get_current_admin),
):
    """Lista todos los logros del sandbox."""
    return AchievementHandler.list_all(include_inactive=include_inactive)


@admin_router.post("", status_code=status.HTTP_201_CREATED)
async def create_achievement(
    body: CreateAchievementSerializer,
    _: UserContext = Depends(get_current_admin),
):
    """Crea un nuevo logro del sandbox."""
    try:
        return AchievementHandler.create(
            name=body.name,
            description=body.description,
            icon=body.icon,
            trigger_type=body.trigger_type,
            trigger_value=body.trigger_value,
            points_bonus=body.points_bonus,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.patch("/{achievement_id}")
async def update_achievement(
    achievement_id: str,
    body: UpdateAchievementSerializer,
    _: UserContext = Depends(get_current_admin),
):
    """Actualiza un logro (campos enviados)."""
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sin campos para actualizar")
    try:
        return AchievementHandler.update(achievement_id, fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.delete("/{achievement_id}")
async def delete_achievement(
    achievement_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Desactiva un logro (soft delete)."""
    try:
        return AchievementHandler.delete(achievement_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@admin_router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_achievements(_: UserContext = Depends(get_current_admin)):
    """Inserta los logros por defecto si la colección está vacía."""
    count = AchievementHandler.seed()
    return {"created": count}


# ── Student endpoint ───────────────────────────────────────────────────────────

@student_router.get("/sandbox-achievements")
async def my_sandbox_achievements(ctx: UserContext = Depends(get_current_user)):
    """Logros del sandbox desbloqueados y bloqueados del usuario autenticado."""
    return AchievementHandler.get_user_achievements(ctx.id)