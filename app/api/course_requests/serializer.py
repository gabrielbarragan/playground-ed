from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreateCourseChangeRequestSerializer(BaseModel):
    to_course_id: str
    reason: str = Field(default="", max_length=500)


class ResolveCourseChangeRequestSerializer(BaseModel):
    action: Literal["approve", "reject"]
    rejection_reason: str = Field(default="", max_length=500)
