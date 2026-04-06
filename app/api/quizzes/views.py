from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_admin, get_current_user, UserContext
from app.api.quizzes.handler import QuizHandler
from app.api.quizzes.serializer import (
    CreateQuizSerializer,
    UpdateQuizSerializer,
    QuizQuestionIn,
    SubmitQuizSerializer,
)

admin_router = APIRouter(prefix="/api/v1/admin/quizzes", tags=["Admin – Quizzes"])
student_router = APIRouter(prefix="/api/v1/quizzes", tags=["Quizzes"])


# ── Quiz CRUD (admin) ──────────────────────────────────────────────────────────

@admin_router.post("", status_code=status.HTTP_201_CREATED)
async def create_quiz(
    body: CreateQuizSerializer,
    _: UserContext = Depends(get_current_admin),
):
    """Crea un nuevo quiz. Las preguntas se agregan por separado."""
    try:
        return QuizHandler.create(
            title=body.title,
            description=body.description,
            course_ids=body.course_ids,
            passing_score=body.passing_score,
            points_on_complete=body.points_on_complete,
            points_on_pass=body.points_on_pass,
            show_correct_answers=body.show_correct_answers,
            use_random_bank=body.use_random_bank,
            questions_to_show=body.questions_to_show,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.get("")
async def list_quizzes(
    include_inactive: bool = Query(default=False),
    _: UserContext = Depends(get_current_admin),
):
    """Lista todos los quizzes. Por defecto solo los activos."""
    return QuizHandler.list_all(include_inactive=include_inactive)


@admin_router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Detalle del quiz incluyendo correct_option_index de cada pregunta."""
    try:
        return QuizHandler.get(quiz_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@admin_router.put("/{quiz_id}")
async def update_quiz(
    quiz_id: str,
    body: UpdateQuizSerializer,
    _: UserContext = Depends(get_current_admin),
):
    """Actualiza los campos enviados (parcial). course_ids reemplaza la lista completa."""
    fields = body.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sin campos para actualizar")
    try:
        return QuizHandler.update(quiz_id, fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.patch("/{quiz_id}/toggle")
async def toggle_quiz(
    quiz_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Activa o desactiva el quiz."""
    try:
        return QuizHandler.toggle(quiz_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── Gestión de preguntas (admin) ───────────────────────────────────────────────

@admin_router.post("/{quiz_id}/questions", status_code=status.HTTP_201_CREATED)
async def add_question(
    quiz_id: str,
    body: QuizQuestionIn,
    _: UserContext = Depends(get_current_admin),
):
    """Agrega una pregunta al quiz."""
    try:
        return QuizHandler.add_question(
            quiz_id=quiz_id,
            text=body.text,
            code_block=body.code_block,
            code_language=body.code_language,
            options=[o.model_dump() for o in body.options],
            correct_option_index=body.correct_option_index,
            explanation=body.explanation,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.put("/{quiz_id}/questions/{index}")
async def update_question(
    quiz_id: str,
    index: int,
    body: QuizQuestionIn,
    _: UserContext = Depends(get_current_admin),
):
    """Reemplaza la pregunta en la posición `index` (0-based)."""
    try:
        return QuizHandler.update_question(
            quiz_id=quiz_id,
            index=index,
            text=body.text,
            code_block=body.code_block,
            code_language=body.code_language,
            options=[o.model_dump() for o in body.options],
            correct_option_index=body.correct_option_index,
            explanation=body.explanation,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.delete("/{quiz_id}/questions/{index}")
async def remove_question(
    quiz_id: str,
    index: int,
    _: UserContext = Depends(get_current_admin),
):
    """Elimina la pregunta en la posición `index` (0-based)."""
    try:
        return QuizHandler.remove_question(quiz_id, index)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Resultados (admin) ────────────────────────────────────────────────────────

@admin_router.get("/{quiz_id}/results")
async def get_results(
    quiz_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """Lista los resultados de todos los estudiantes que completaron el quiz."""
    try:
        return QuizHandler.get_results(quiz_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@admin_router.delete("/{quiz_id}/attempts/{user_id}")
async def reset_attempt(
    quiz_id: str,
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    """
    Elimina el intento de un estudiante, permitiéndole volver a responder.
    Los puntos acreditados NO se remueven.
    """
    try:
        return QuizHandler.reset_attempt(quiz_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ── Student endpoints ──────────────────────────────────────────────────────────

@student_router.get("")
async def list_quizzes(ctx: UserContext = Depends(get_current_user)):
    """Quizzes activos del curso del estudiante con estado (pending/completed/passed)."""
    try:
        return QuizHandler.list_for_user(ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@student_router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: str,
    ctx: UserContext = Depends(get_current_user),
):
    """Detalle del quiz para responder. No incluye las respuestas correctas."""
    try:
        return QuizHandler.get_for_user(quiz_id, ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@student_router.get("/{quiz_id}/my-result")
async def my_result(
    quiz_id: str,
    ctx: UserContext = Depends(get_current_user),
):
    """Resultado del intento propio. Incluye corrección si el docente lo configuró."""
    try:
        return QuizHandler.get_my_result(quiz_id, ctx.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@student_router.post("/{quiz_id}/submit", status_code=status.HTTP_201_CREATED)
async def submit_quiz(
    quiz_id: str,
    body: SubmitQuizSerializer,
    ctx: UserContext = Depends(get_current_user),
):
    """
    Entrega las respuestas del quiz.
    `answers` es una lista de índices de opción (0-based), uno por pregunta, en orden.
    Solo se permite un intento por usuario.
    """
    try:
        return QuizHandler.submit(quiz_id, ctx.id, body.answers)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))