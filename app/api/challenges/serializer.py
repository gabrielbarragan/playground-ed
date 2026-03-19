from typing import Optional
from pydantic import BaseModel, Field


class CreateChallengeSerializer(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    points: int = Field(..., ge=0)
    course_ids: list[str] = Field(default_factory=list)
    starter_code: str = Field(default="")
    example_input: str = Field(default="")
    example_output: str = Field(default="")
    tags: list[str] = Field(default_factory=list)
    requires_review: bool = Field(default=False)
    required_functions: list[str] = Field(default_factory=list)
    optimal_lines_min: Optional[int] = Field(default=None, ge=1)
    optimal_lines_max: Optional[int] = Field(default=None, ge=1)
    lines_bonus_points: int = Field(default=0, ge=0)


class UpdateChallengeSerializer(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    points: Optional[int] = Field(None, ge=0)
    course_ids: Optional[list[str]] = None
    starter_code: Optional[str] = None
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    tags: Optional[list[str]] = None
    requires_review: Optional[bool] = None
    is_active: Optional[bool] = None
    required_functions: Optional[list[str]] = None
    optimal_lines_min: Optional[int] = Field(default=None, ge=1)
    optimal_lines_max: Optional[int] = Field(default=None, ge=1)
    lines_bonus_points: Optional[int] = Field(default=None, ge=0)


class AddTestCaseSerializer(BaseModel):
    input: str = Field(default="")
    expected_output: str = Field(..., min_length=1)
    is_hidden: bool = Field(default=False)
    description: str = Field(default="")


class ReviewSerializer(BaseModel):
    feedback: str = Field(default="")


class SubmitChallengeSerializer(BaseModel):
    code: str = Field(..., min_length=1)