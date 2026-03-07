from pydantic import BaseModel, Field


class CourseInSerializer(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: str = Field(default="", max_length=500)