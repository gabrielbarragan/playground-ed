from fastapi import APIRouter
from app.api.badges.handler import BadgeHandler

router = APIRouter(prefix="/api/v1/badges", tags=["Badges"])


@router.get("")
async def list_badges():
    """Lista todos los badges disponibles."""
    return BadgeHandler.list_badges()