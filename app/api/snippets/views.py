from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.auth import get_current_user, UserContext
from app.api.snippets.handler import SnippetHandler
from app.api.snippets.serializer import SnippetInSerializer, SnippetUpdateSerializer

router = APIRouter(prefix="/api/v1/snippets", tags=["Snippets"])


@router.get("/")
async def list_snippets(ctx: UserContext = Depends(get_current_user)):
    return SnippetHandler.list(ctx.id)


@router.get("/{snippet_id}")
async def get_snippet(snippet_id: str, ctx: UserContext = Depends(get_current_user)):
    snippet = SnippetHandler.get(snippet_id, ctx.id)
    if not snippet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snippet no encontrado")
    return snippet


@router.post("/", status_code=status.HTTP_201_CREATED)
async def save_snippet(body: SnippetInSerializer, ctx: UserContext = Depends(get_current_user)):
    try:
        snippet = SnippetHandler.save(
            user_id=ctx.id,
            title=body.title,
            code=body.code,
            language=body.language,
            tags=body.tags,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=snippet)


@router.put("/{snippet_id}")
async def update_snippet(
    snippet_id: str,
    body: SnippetUpdateSerializer,
    ctx: UserContext = Depends(get_current_user),
):
    try:
        snippet = SnippetHandler.update(
            snippet_id=snippet_id,
            user_id=ctx.id,
            title=body.title,
            code=body.code,
            tags=body.tags or [],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return snippet


@router.delete("/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snippet(snippet_id: str, ctx: UserContext = Depends(get_current_user)):
    try:
        SnippetHandler.remove(snippet_id, ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))