import random
from datetime import datetime

from app.api.quizzes.querysets import QuizQueryset, AttemptQueryset
from app.api.courses.querysets import CourseQueryset
from app.api.users.querysets import UserQueryset
from app.models.quiz import Quiz, QuizQuestion, QuizOption
from app.models.quiz_attempt import QuizAttempt, QuizAnswerRecord

def _get_random_indices(pool_size: int, count: int, seed: str) -> list[int]:
    """Retorna índices únicos del pool en orden aleatorio, determinístico por seed."""
    rng = random.Random(seed)
    indices = list(range(pool_size))
    rng.shuffle(indices)
    return indices[:min(count, pool_size)]


_quizzes = QuizQueryset()
_attempts = AttemptQueryset()
_courses = CourseQueryset()
_users = UserQueryset()


# ── Serializers ────────────────────────────────────────────────────────────────

def _serialize_quiz_for_admin(quiz: Quiz) -> dict:
    """Incluye correct_option_index. Solo para vistas de admin."""
    courses = []
    for c in quiz.courses:
        try:
            courses.append({"id": str(c.id), "name": c.name, "code": c.code})
        except Exception:
            pass
    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description,
        "courses": courses,
        "questions": [
            {
                "index": i,
                "text": q.text,
                "code_block": q.code_block,
                "code_language": q.code_language,
                "options": [{"text": o.text} for o in q.options],
                "correct_option_index": q.correct_option_index,
                "explanation": q.explanation,
            }
            for i, q in enumerate(quiz.questions)
        ],
        "question_count": len(quiz.questions),
        "passing_score": quiz.passing_score,
        "points_on_complete": quiz.points_on_complete,
        "points_on_pass": quiz.points_on_pass,
        "show_correct_answers": quiz.show_correct_answers,
        "use_random_bank": quiz.use_random_bank,
        "questions_to_show": quiz.questions_to_show,
        "is_active": quiz.is_active,
        "created_at": quiz.created_at.isoformat(),
        "updated_at": quiz.updated_at.isoformat(),
    }


def _serialize_quiz_for_student(quiz: Quiz, user_id: str | None = None) -> dict:
    """
    NUNCA incluye correct_option_index ni explanation. Para vistas del estudiante pre-entrega.
    Si use_random_bank=True, filtra el subconjunto determinístico para ese usuario.
    El campo 'index' de cada pregunta siempre es el índice original del pool.
    """
    courses = []
    for c in quiz.courses:
        try:
            courses.append({"id": str(c.id), "name": c.name, "code": c.code})
        except Exception:
            pass

    if quiz.use_random_bank and user_id:
        seed = f"{user_id}_{str(quiz.id)}"
        indices = _get_random_indices(len(quiz.questions), quiz.questions_to_show, seed)
        questions_to_render = [(orig_i, quiz.questions[orig_i]) for orig_i in indices]
        question_count = len(indices)
    else:
        questions_to_render = list(enumerate(quiz.questions))
        question_count = len(quiz.questions)

    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description,
        "courses": courses,
        "questions": [
            {
                "index": orig_i,  # índice original del pool, no posicional
                "text": q.text,
                "code_block": q.code_block,
                "code_language": q.code_language,
                "options": [{"text": o.text} for o in q.options],
                # correct_option_index y explanation omitidos intencionalmente
            }
            for orig_i, q in questions_to_render
        ],
        "question_count": question_count,
        "passing_score": quiz.passing_score,
        "points_on_complete": quiz.points_on_complete,
        "points_on_pass": quiz.points_on_pass,
        "show_correct_answers": quiz.show_correct_answers,
        "use_random_bank": quiz.use_random_bank,
        "questions_to_show": quiz.questions_to_show if quiz.use_random_bank else None,
        "pool_size": len(quiz.questions) if quiz.use_random_bank else None,
    }


def _serialize_attempt_result(attempt: QuizAttempt, quiz: Quiz) -> dict:
    """
    Resultado post-entrega para el estudiante.
    Incluye corrección por pregunta solo si quiz.show_correct_answers=True.
    """
    result = {
        "id": str(attempt.id),
        "quiz_id": str(quiz.id),
        "correct_count": attempt.correct_count,
        "total_questions": attempt.total_questions,
        "passed": attempt.passed,
        "points_earned": attempt.points_earned,
        "submitted_at": attempt.submitted_at.isoformat(),
    }

    if quiz.show_correct_answers:
        # Lookup por question_index (índice del pool) para soportar banco aleatorio.
        answers_by_q_index = {a.question_index: a for a in attempt.answers}
        # Reconstruir el subconjunto que vio el alumno.
        if attempt.selected_question_indices:
            questions_shown = [(i, quiz.questions[i]) for i in attempt.selected_question_indices]
        else:
            questions_shown = list(enumerate(quiz.questions))

        result["questions"] = [
            {
                "index": orig_i,
                "text": q.text,
                "code_block": q.code_block,
                "code_language": q.code_language,
                "options": [{"text": o.text} for o in q.options],
                "correct_option_index": q.correct_option_index,
                "explanation": q.explanation,
                "selected_option_index": answers_by_q_index[orig_i].selected_option_index,
                "is_correct": answers_by_q_index[orig_i].is_correct,
            }
            for orig_i, q in questions_shown
        ]

    return result


def _serialize_attempt_for_admin(attempt: QuizAttempt) -> dict:
    """Vista de admin: resultado de un estudiante sin detalle de corrección por pregunta."""
    user = attempt.user
    return {
        "id": str(attempt.id),
        "user": {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
        "correct_count": attempt.correct_count,
        "total_questions": attempt.total_questions,
        "passed": attempt.passed,
        "points_earned": attempt.points_earned,
        "submitted_at": attempt.submitted_at.isoformat(),
        "selected_question_indices": attempt.selected_question_indices,
    }


# ── Quiz CRUD (admin) ──────────────────────────────────────────────────────────

def create_quiz(
    title: str,
    description: str,
    course_ids: list[str],
    passing_score: int,
    points_on_complete: int,
    points_on_pass: int,
    show_correct_answers: bool,
    use_random_bank: bool = False,
    questions_to_show: int = 0,
) -> dict:
    if use_random_bank:
        if questions_to_show < 1:
            raise ValueError("questions_to_show debe ser al menos 1 cuando se usa banco aleatorio")
        if passing_score > questions_to_show:
            raise ValueError("passing_score no puede superar questions_to_show")
    courses = _resolve_courses(course_ids)
    quiz = Quiz(
        title=title,
        description=description,
        courses=courses,
        passing_score=passing_score,
        points_on_complete=points_on_complete,
        points_on_pass=points_on_pass,
        show_correct_answers=show_correct_answers,
        use_random_bank=use_random_bank,
        questions_to_show=questions_to_show,
    ).save()
    return _serialize_quiz_for_admin(quiz)


def list_quizzes(include_inactive: bool = False) -> dict:
    quizzes = _quizzes.get_all(include_inactive=include_inactive)
    items = [_serialize_quiz_for_admin(q) for q in quizzes]
    return {"total": len(items), "quizzes": items}


def get_quiz(quiz_id: str) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")
    return _serialize_quiz_for_admin(quiz)


def update_quiz(quiz_id: str, fields: dict) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")

    if "course_ids" in fields:
        fields["courses"] = _resolve_courses(fields.pop("course_ids"))

    fields["updated_at"] = datetime.utcnow()
    for key, value in fields.items():
        setattr(quiz, key, value)

    # Re-validar invariante del banco aleatorio con los valores resultantes
    if quiz.use_random_bank:
        if quiz.questions_to_show < 1:
            raise ValueError("questions_to_show debe ser al menos 1 cuando se usa banco aleatorio")
        if quiz.passing_score > quiz.questions_to_show:
            raise ValueError("passing_score no puede superar questions_to_show")

    quiz.save()
    return _serialize_quiz_for_admin(quiz)


def toggle_quiz(quiz_id: str) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")
    quiz.is_active = not quiz.is_active
    quiz.updated_at = datetime.utcnow()
    quiz.save()
    return _serialize_quiz_for_admin(quiz)


# ── Gestión de preguntas (admin) ───────────────────────────────────────────────

def add_question(
    quiz_id: str,
    text: str,
    code_block: str,
    code_language: str,
    options: list[dict],
    correct_option_index: int,
    explanation: str,
) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")

    if correct_option_index >= len(options):
        raise ValueError("correct_option_index fuera de rango")

    question = QuizQuestion(
        text=text,
        code_block=code_block,
        code_language=code_language,
        options=[QuizOption(text=o["text"]) for o in options],
        correct_option_index=correct_option_index,
        explanation=explanation,
    )
    quiz.questions.append(question)
    quiz.updated_at = datetime.utcnow()
    quiz.save()
    return _serialize_quiz_for_admin(quiz)


def update_question(
    quiz_id: str,
    index: int,
    text: str,
    code_block: str,
    code_language: str,
    options: list[dict],
    correct_option_index: int,
    explanation: str,
) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")
    if index < 0 or index >= len(quiz.questions):
        raise ValueError(f"Índice de pregunta inválido: {index}")
    if correct_option_index >= len(options):
        raise ValueError("correct_option_index fuera de rango")

    quiz.questions[index] = QuizQuestion(
        text=text,
        code_block=code_block,
        code_language=code_language,
        options=[QuizOption(text=o["text"]) for o in options],
        correct_option_index=correct_option_index,
        explanation=explanation,
    )
    quiz.updated_at = datetime.utcnow()
    quiz.save()
    return _serialize_quiz_for_admin(quiz)


def remove_question(quiz_id: str, index: int) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")
    if index < 0 or index >= len(quiz.questions):
        raise ValueError(f"Índice de pregunta inválido: {index}")

    quiz.questions.pop(index)
    quiz.updated_at = datetime.utcnow()
    quiz.save()
    return _serialize_quiz_for_admin(quiz)


# ── Resultados (admin) ────────────────────────────────────────────────────────

def get_quiz_results(quiz_id: str) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")
    attempts = _attempts.get_by_quiz(quiz)
    items = [_serialize_attempt_for_admin(a) for a in attempts]
    return {"total": len(items), "results": items}


def reset_attempt(quiz_id: str, user_id: str) -> dict:
    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")
    attempt = _attempts.get_by_user_and_quiz(user, quiz)
    if not attempt:
        raise ValueError("El usuario no tiene un intento para este quiz")
    attempt.delete()
    return {"message": "Intento eliminado. Los puntos acreditados no fueron revertidos."}


# ── Vista estudiante ──────────────────────────────────────────────────────────

def list_quizzes_for_user(user_id: str) -> dict:
    """Quizzes activos del curso del estudiante con su estado (pending/completed/passed)."""
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    quizzes = list(_quizzes.get_by_course(user.course))
    result = []
    for q in quizzes:
        attempt = _attempts.get_by_user_and_quiz(user, q)
        if attempt is None:
            status = "pending"
        elif attempt.passed:
            status = "passed"
        else:
            status = "completed"

        courses = []
        for c in q.courses:
            try:
                courses.append({"id": str(c.id), "name": c.name, "code": c.code})
            except Exception:
                pass

        result.append({
            "id": str(q.id),
            "title": q.title,
            "description": q.description,
            "question_count": len(q.questions),
            "passing_score": q.passing_score,
            "points_on_complete": q.points_on_complete,
            "points_on_pass": q.points_on_pass,
            "show_correct_answers": q.show_correct_answers,
            "use_random_bank": q.use_random_bank,
            "questions_to_show": q.questions_to_show if q.use_random_bank else None,
            "status": status,
            "courses": courses,
        })

    return {"total": len(result), "quizzes": result}


def get_quiz_for_user(quiz_id: str, user_id: str) -> dict:
    """Detalle del quiz para responder. NUNCA incluye correct_option_index."""
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    quiz = _quizzes.get_active_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")

    course_ids = [str(c.id) for c in quiz.courses]
    if course_ids and str(user.course.id) not in course_ids:
        raise ValueError("Quiz no disponible para tu curso")

    return _serialize_quiz_for_student(quiz, user_id=user_id)


def get_my_result(quiz_id: str, user_id: str) -> dict:
    """Resultado del intento propio. Incluye corrección si show_correct_answers=True."""
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    quiz = _quizzes.get_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")

    attempt = _attempts.get_by_user_and_quiz(user, quiz)
    if not attempt:
        raise ValueError("No has completado este quiz")

    return _serialize_attempt_result(attempt, quiz)


def submit_quiz(quiz_id: str, user_id: str, answers: list[int]) -> dict:
    """
    Evalúa las respuestas del estudiante.

    Flujo:
      1. Verificar acceso al quiz.
      2. Verificar que no exista intento previo (un solo intento).
      3. Validar cantidad y rango de respuestas.
      4. Calcular correctas y si aprobó.
      5. Acreditar puntos (complete + pass si corresponde).
      6. Guardar QuizAttempt.
      7. Retornar resultado (con corrección si show_correct_answers=True).
    """
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    quiz = _quizzes.get_active_by_id(quiz_id)
    if not quiz:
        raise ValueError("Quiz no encontrado")

    course_ids = [str(c.id) for c in quiz.courses]
    if course_ids and str(user.course.id) not in course_ids:
        raise ValueError("Quiz no disponible para tu curso")

    existing = _attempts.get_by_user_and_quiz(user, quiz)
    if existing:
        raise ValueError("Ya completaste este quiz. Solo se permite un intento.")

    # Determinar el subconjunto de preguntas a evaluar
    if quiz.use_random_bank:
        seed = f"{user_id}_{quiz_id}"
        selected_indices = _get_random_indices(len(quiz.questions), quiz.questions_to_show, seed)
    else:
        selected_indices = list(range(len(quiz.questions)))

    expected_count = len(selected_indices)
    if len(answers) != expected_count:
        raise ValueError(
            f"Se esperaban {expected_count} respuestas, se recibieron {len(answers)}"
        )

    answer_records = []
    correct_count = 0
    for pos, orig_idx in enumerate(selected_indices):
        question = quiz.questions[orig_idx]
        selected = answers[pos]
        if selected < 0 or selected >= len(question.options):
            raise ValueError(f"Índice de opción inválido en pregunta {orig_idx}: {selected}")
        is_correct = selected == question.correct_option_index
        if is_correct:
            correct_count += 1
        answer_records.append(QuizAnswerRecord(
            question_index=orig_idx,  # índice original del pool
            selected_option_index=selected,
            is_correct=is_correct,
        ))

    passed = correct_count >= quiz.passing_score

    points_earned = 0
    if quiz.points_on_complete > 0:
        points_earned += quiz.points_on_complete
    if passed and quiz.points_on_pass > 0:
        points_earned += quiz.points_on_pass

    if points_earned > 0:
        user.total_points += points_earned
        user.save()

    attempt = QuizAttempt(
        user=user,
        quiz=quiz,
        answers=answer_records,
        correct_count=correct_count,
        total_questions=expected_count,
        passed=passed,
        points_earned=points_earned,
        selected_question_indices=selected_indices,
    ).save()

    return _serialize_attempt_result(attempt, quiz)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_courses(course_ids: list[str]) -> list:
    courses = []
    for cid in course_ids:
        course = _courses.get_active_by_id(cid)
        if not course:
            raise ValueError(f"Curso no encontrado: {cid}")
        courses.append(course)
    return courses