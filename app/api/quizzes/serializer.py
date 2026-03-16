from typing import Optional
from pydantic import BaseModel, Field


class QuizOptionIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class QuizQuestionIn(BaseModel):
    text: str = Field(..., min_length=1)
    code_block: str = Field(default="")
    code_language: str = Field(default="python")
    options: list[QuizOptionIn] = Field(..., min_length=2, max_length=6)
    correct_option_index: int = Field(..., ge=0)
    explanation: str = Field(default="")


class CreateQuizSerializer(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")
    course_ids: list[str] = Field(default_factory=list)
    passing_score: int = Field(..., ge=1)
    points_on_complete: int = Field(default=0, ge=0)
    points_on_pass: int = Field(default=0, ge=0)
    show_correct_answers: bool = Field(default=True)


class UpdateQuizSerializer(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    course_ids: Optional[list[str]] = None
    passing_score: Optional[int] = Field(None, ge=1)
    points_on_complete: Optional[int] = Field(None, ge=0)
    points_on_pass: Optional[int] = Field(None, ge=0)
    show_correct_answers: Optional[bool] = None
    is_active: Optional[bool] = None


class SubmitQuizSerializer(BaseModel):
    # Una entrada por pregunta (en orden): el índice de la opción seleccionada (0-based)
    answers: list[int] = Field(..., min_length=1)