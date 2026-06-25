from typing import Literal

from pydantic import BaseModel, Field


class RoleUpdateSerializer(BaseModel):
    role: Literal["student", "admin", "superadmin"]


class AssignCoursesSerializer(BaseModel):
    course_ids: list[str]