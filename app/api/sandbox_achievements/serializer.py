from typing import Optional
from pydantic import BaseModel


class CreateAchievementSerializer(BaseModel):
    name: str
    description: str
    icon: str = "🏆"
    trigger_type: str  # "ast_concept" | "combo"
    trigger_value: str
    points_bonus: int = 0


class UpdateAchievementSerializer(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_value: Optional[str] = None
    points_bonus: Optional[int] = None
    is_active: Optional[bool] = None