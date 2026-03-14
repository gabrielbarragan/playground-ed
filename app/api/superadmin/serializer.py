from typing import Literal

from pydantic import BaseModel, Field


class RoleUpdateSerializer(BaseModel):
    role: Literal["student", "admin", "superadmin"]