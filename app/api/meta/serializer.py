from pydantic import (
    BaseModel
)


class MetaSerializer(BaseModel):
    message: str
    docs: str


class VersionSerializer(BaseModel):
    version: str
    message: str


class StatusSerializer(BaseModel):
    status: str


class HealthSerializer(BaseModel):
    status_code: int
    content: StatusSerializer
