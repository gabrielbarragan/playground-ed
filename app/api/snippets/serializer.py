from typing import List, Optional
from pydantic import BaseModel, Field


class SnippetInSerializer(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1)
    language: str = Field(default="python", max_length=50)
    tags: List[str] = Field(default_factory=list)


class SnippetUpdateSerializer(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1)
    tags: Optional[List[str]] = Field(default_factory=list)