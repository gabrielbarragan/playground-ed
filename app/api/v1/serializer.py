from pydantic import BaseModel, Field, field_validator


class CodeExecutionInSerializer(BaseModel):
    code: str = Field(..., min_length=1, max_length=100_000)

    @field_validator("code")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("El código no puede estar vacío.")
        return stripped