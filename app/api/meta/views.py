from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.api.meta.serializer import (
    MetaSerializer,
    VersionSerializer,
    StatusSerializer
)
from app.core.constants import (
    API_VERSION
)

router = APIRouter()


@router.get("/", tags=["meta"], response_model=MetaSerializer)
async def root():
    return {
        "message": "Place to pay service",
        "docs": "/api/v1/docs"
    }


@router.get("/version", tags=["meta"], response_model=VersionSerializer)
async def version():
    response = {
        "version": API_VERSION,
        "message": "Service"
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )


@router.get("/health", tags=["status"], response_model=StatusSerializer)
async def health_check():
    response = {"status": "ok"}
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )
