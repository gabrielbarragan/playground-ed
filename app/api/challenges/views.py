from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_admin, get_current_user, UserContext
from app.api.challenges.handler import ChallengeHandler
from app.api.challenges.serializer import (
    CreateChallengeSerializer,
    UpdateChallengeSerializer,
    AddTestCaseSerializer,
    ReviewSerializer,
    SubmitChallengeSerializer,
)

router = APIRouter(prefix="/api/v1/admin/challenges", tags=["Admin – Challenges"])
submissions_router = APIRouter(prefix="/api/v1/admin/submissions", tags=["Admin – Submissions"])
student_router = APIRouter(prefix="/api/v1/challenges", tags=["Challenges"])


# ── Challenge CRUD ─────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_challenge(
    body: CreateChallengeSerializer,
    ctx: UserContext = Depends(get_current_admin),
):
    """Crea un nuevo reto. Los test cases se agregan por separado."""
    try:
        return ChallengeHandler.create(
            title=body.title,
            description=body.description,
            difficulty=body.difficulty,
            points=body.points,
            course_ids=body.course_ids,
            starter_code=body.starter_code,
            example_input=body.example_input,
            example_output=body.example_output,
            tags=body.tags,
            requires_review=body.requires_review,
            optimal_lines_min=body.optimal_lines_min,
            optimal_lines_max=body.optimal_lines_max,
            lines_bonus_points=body.lines_bonus_points,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")
async def list_challenges(
    include_inactive: bool = Query(default=False),
    _: UserContext = Depends(get_current_admin),
):
    """Lista todos los retos. Por defecto solo los activos."""
    return ChallengeHandler.list_all(include_inactive=include_inactive)


@router.get("/{challenge_id}")
async def get_challenge(
    challenge_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Detalle de un reto incluyendo todos sus test cases (visible para admin)."""
    try:
        return ChallengeHandler.get(challenge_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{challenge_id}")
async def update_challenge(
    challenge_id: str,
    body: UpdateChallengeSerializer,
    _: UserContext = Depends(get_current_admin),
):
    """Actualiza los campos enviados (parcial). course_ids reemplaza la lista completa."""
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sin campos para actualizar")
    try:
        return ChallengeHandler.update(challenge_id, fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{challenge_id}")
async def delete_challenge(
    challenge_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Desactiva un reto (soft delete). No elimina los intentos existentes."""
    try:
        return ChallengeHandler.delete(challenge_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── Test cases ─────────────────────────────────────────────────────────────────

@router.post("/{challenge_id}/test-cases", status_code=status.HTTP_201_CREATED)
async def add_test_case(
    challenge_id: str,
    body: AddTestCaseSerializer,
    _: UserContext = Depends(get_current_admin),
):
    """
    Agrega un test case al reto.
    - `is_hidden=true`: el estudiante sabe que existe pero no ve su contenido.
    - `is_hidden=false`: visible como ejemplo confirmado.
    """
    try:
        return ChallengeHandler.add_test_case(
            challenge_id=challenge_id,
            input=body.input,
            expected_output=body.expected_output,
            is_hidden=body.is_hidden,
            description=body.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{challenge_id}/test-cases/{index}")
async def remove_test_case(
    challenge_id: str,
    index: int,
    _: UserContext = Depends(get_current_admin),
):
    """Elimina el test case en la posición `index` (0-based)."""
    try:
        return ChallengeHandler.remove_test_case(challenge_id, index)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Manual review ──────────────────────────────────────────────────────────────

@submissions_router.get("/pending")
async def list_pending(
    challenge_id: Optional[str] = Query(default=None),
    _: UserContext = Depends(get_current_admin),
):
    """
    Lista todos los intentos pendientes de revisión manual.
    Se puede filtrar por `challenge_id`.
    """
    return ChallengeHandler.list_pending(challenge_id=challenge_id)


@submissions_router.put("/{attempt_id}/approve")
async def approve_submission(
    attempt_id: str,
    body: ReviewSerializer,
    ctx: UserContext = Depends(get_current_admin),
):
    """Aprueba un intento manual. Acredita puntos si es el primer pase."""
    try:
        return ChallengeHandler.approve(attempt_id, reviewer_id=ctx.id, feedback=body.feedback)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@submissions_router.put("/{attempt_id}/reject")
async def reject_submission(
    attempt_id: str,
    body: ReviewSerializer,
    ctx: UserContext = Depends(get_current_admin),
):
    """Rechaza un intento manual. No acredita puntos."""
    try:
        return ChallengeHandler.reject(attempt_id, reviewer_id=ctx.id, feedback=body.feedback)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Student endpoints ──────────────────────────────────────────────────────────

@student_router.get("/my-progress")
async def my_progress(ctx: UserContext = Depends(get_current_user)):
    """Progreso del estudiante: estado (passed/pending_review/unsolved) por reto."""
    try:
        return ChallengeHandler.get_my_progress(ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@student_router.get("")
async def list_challenges(ctx: UserContext = Depends(get_current_user)):
    """Retos activos disponibles para el curso del estudiante."""
    try:
        return ChallengeHandler.list_for_user(ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@student_router.get("/{challenge_id}")
async def get_challenge(
    challenge_id: str,
    ctx: UserContext = Depends(get_current_user),
):
    """Detalle del reto. Los test cases ocultos no exponen input/output esperado."""
    try:
        return ChallengeHandler.get_for_user(challenge_id, ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@student_router.get("/{challenge_id}/my-attempts")
async def my_attempts(
    challenge_id: str,
    ctx: UserContext = Depends(get_current_user),
):
    """Historial de intentos del estudiante en este reto."""
    try:
        return ChallengeHandler.get_my_attempts(challenge_id, ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@student_router.post("/{challenge_id}/submit", status_code=status.HTTP_201_CREATED)
async def submit_challenge(
    challenge_id: str,
    body: SubmitChallengeSerializer,
    ctx: UserContext = Depends(get_current_user),
):
    """
    Envía una solución al reto.

    - Con test cases y `requires_review=false`: se auto-evalúa y acredita puntos si pasa.
    - Con `requires_review=true`: queda pendiente de aprobación del docente.
    - Sin test cases y `requires_review=false`: se registra como práctica libre (passed=true).
    """
    try:
        return await ChallengeHandler.submit(challenge_id, ctx.id, body.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))