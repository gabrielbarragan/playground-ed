from datetime import datetime
from typing import Optional

from app.api.challenges.querysets import ChallengeQueryset, AttemptQueryset
from app.api.courses.querysets import CourseQueryset
from app.api.users.querysets import UserQueryset
from app.core.ast_analyzer import check_required_functions
from app.core.code_quality import calculate_lines_bonus, count_effective_lines
from app.models.challenge import Challenge, TestCase
from app.models.challenge_attempt import ChallengeAttempt, TestCaseResult

_challenges = ChallengeQueryset()
_attempts = AttemptQueryset()
_courses = CourseQueryset()
_users = UserQueryset()


# ── Serializers ────────────────────────────────────────────────────────────────

def _serialize_test_case(tc: TestCase, index: int, hide_content: bool = False) -> dict:
    if hide_content and tc.is_hidden:
        return {"index": index, "is_hidden": True, "description": tc.description}
    return {
        "index": index,
        "input": tc.input,
        "expected_output": tc.expected_output,
        "is_hidden": tc.is_hidden,
        "description": tc.description,
    }


def _serialize_challenge(challenge: Challenge, admin_view: bool = True) -> dict:
    test_cases = [
        _serialize_test_case(tc, i, hide_content=not admin_view)
        for i, tc in enumerate(challenge.test_cases)
    ]
    courses = []
    for c in challenge.courses:
        try:
            courses.append({"id": str(c.id), "name": c.name, "code": c.code})
        except Exception:
            pass
    return {
        "id": str(challenge.id),
        "title": challenge.title,
        "description": challenge.description,
        "difficulty": challenge.difficulty,
        "points": challenge.points,
        "courses": courses,
        "starter_code": challenge.starter_code,
        "example_input": challenge.example_input,
        "example_output": challenge.example_output,
        "requires_review": challenge.requires_review,
        "required_functions": list(challenge.required_functions or []),
        "tags": challenge.tags,
        "test_cases": test_cases,
        "test_case_count": len(challenge.test_cases),
        "has_auto_grading": len(challenge.test_cases) > 0,
        "is_active": challenge.is_active,
        "optimal_lines_min": challenge.optimal_lines_min,
        "optimal_lines_max": challenge.optimal_lines_max,
        "lines_bonus_points": challenge.lines_bonus_points,
        "created_at": challenge.created_at.isoformat(),
        "updated_at": challenge.updated_at.isoformat(),
    }


def _serialize_attempt(attempt) -> dict:
    reviewer = None
    if attempt.reviewed_by:
        try:
            u = attempt.reviewed_by
            reviewer = {"id": str(u.id), "first_name": u.first_name, "last_name": u.last_name}
        except Exception:
            pass
    return {
        "id": str(attempt.id),
        "user": {
            "id": str(attempt.user.id),
            "first_name": attempt.user.first_name,
            "last_name": attempt.user.last_name,
            "email": attempt.user.email,
        },
        "challenge": {
            "id": str(attempt.challenge.id),
            "title": attempt.challenge.title,
            "difficulty": attempt.challenge.difficulty,
            "points": attempt.challenge.points,
        },
        "code": attempt.code,
        "attempt_number": attempt.attempt_number,
        "passed": attempt.passed,
        "points_earned": attempt.points_earned,
        "bonus_points_earned": attempt.bonus_points_earned,
        "effective_lines": count_effective_lines(attempt.code),
        "ast_validation_error": attempt.ast_validation_error or "",
        "review_status": attempt.review_status,
        "review_feedback": attempt.review_feedback,
        "reviewer": reviewer,
        "reviewed_at": attempt.reviewed_at.isoformat() if attempt.reviewed_at else None,
        "submitted_at": attempt.submitted_at.isoformat(),
        "results": [
            {
                "test_index": r.test_index,
                "passed": r.passed,
                "actual_output": r.actual_output,
                "error": r.error,
            }
            for r in attempt.results
        ],
    }


# ── Cálculo de puntos por intento ─────────────────────────────────────────────

_ATTEMPT_MULTIPLIERS = {1: 1.0, 2: 0.75, 3: 0.5, 4: 0.25}
_MIN_MULTIPLIER = 0.1


def _points_for_attempt(base: int, attempt_number: int) -> int:
    """
    Devuelve los puntos a acreditar según el número de intento (1-based).
    Intento 1 → 100 %  |  2 → 75 %  |  3 → 50 %  |  4 → 25 %  |  5+ → 10 %
    El mínimo es 1 punto si base > 0.
    """
    if base <= 0:
        return 0
    multiplier = _ATTEMPT_MULTIPLIERS.get(attempt_number, _MIN_MULTIPLIER)
    return max(1, int(base * multiplier))


# ── Challenge CRUD ─────────────────────────────────────────────────────────────

def create_challenge(
    title: str,
    description: str,
    difficulty: str,
    points: int,
    course_ids: list[str],
    starter_code: str,
    example_input: str,
    example_output: str,
    tags: list[str],
    requires_review: bool,
    required_functions: list[str] = None,
    optimal_lines_min: Optional[int] = None,
    optimal_lines_max: Optional[int] = None,
    lines_bonus_points: int = 0,
) -> dict:
    courses = []
    for cid in course_ids:
        course = _courses.get_active_by_id(cid)
        if not course:
            raise ValueError(f"Curso no encontrado: {cid}")
        courses.append(course)

    challenge = Challenge(
        title=title,
        description=description,
        difficulty=difficulty,
        points=points,
        courses=courses,
        starter_code=starter_code,
        example_input=example_input,
        example_output=example_output,
        tags=tags,
        requires_review=requires_review,
        required_functions=required_functions or [],
        optimal_lines_min=optimal_lines_min,
        optimal_lines_max=optimal_lines_max,
        lines_bonus_points=lines_bonus_points,
    ).save()
    return _serialize_challenge(challenge)


def list_challenges(include_inactive: bool = False) -> dict:
    challenges = _challenges.get_all(include_inactive=include_inactive)
    items = [_serialize_challenge(c) for c in challenges]
    return {"total": len(items), "challenges": items}


def get_challenge(challenge_id: str) -> dict:
    challenge = _challenges.get_by_id(challenge_id)
    if not challenge:
        raise ValueError("Reto no encontrado")
    return _serialize_challenge(challenge)


def update_challenge(challenge_id: str, fields: dict) -> dict:
    challenge = _challenges.get_by_id(challenge_id)
    if not challenge:
        raise ValueError("Reto no encontrado")

    if "course_ids" in fields:
        courses = []
        for cid in fields.pop("course_ids"):
            course = _courses.get_active_by_id(cid)
            if not course:
                raise ValueError(f"Curso no encontrado: {cid}")
            courses.append(course)
        fields["courses"] = courses

    fields["updated_at"] = datetime.utcnow()
    for key, value in fields.items():
        setattr(challenge, key, value)
    challenge.save()
    return _serialize_challenge(challenge)


def delete_challenge(challenge_id: str) -> dict:
    """Soft delete: desactiva el reto."""
    challenge = _challenges.get_by_id(challenge_id)
    if not challenge:
        raise ValueError("Reto no encontrado")
    challenge.is_active = False
    challenge.updated_at = datetime.utcnow()
    challenge.save()
    return _serialize_challenge(challenge)


# ── Test cases ─────────────────────────────────────────────────────────────────

def add_test_case(
    challenge_id: str,
    input: str,
    expected_output: str,
    is_hidden: bool,
    description: str,
) -> dict:
    challenge = _challenges.get_by_id(challenge_id)
    if not challenge:
        raise ValueError("Reto no encontrado")

    tc = TestCase(
        input=input,
        expected_output=expected_output,
        is_hidden=is_hidden,
        description=description,
    )
    challenge.test_cases.append(tc)
    challenge.updated_at = datetime.utcnow()
    challenge.save()
    return _serialize_challenge(challenge)


def remove_test_case(challenge_id: str, index: int) -> dict:
    challenge = _challenges.get_by_id(challenge_id)
    if not challenge:
        raise ValueError("Reto no encontrado")
    if index < 0 or index >= len(challenge.test_cases):
        raise ValueError(f"Índice de test case inválido: {index}")

    challenge.test_cases.pop(index)
    challenge.updated_at = datetime.utcnow()
    challenge.save()
    return _serialize_challenge(challenge)


# ── Manual review ──────────────────────────────────────────────────────────────

def list_pending_reviews(challenge_id: Optional[str] = None) -> dict:
    attempts = _attempts.get_pending_review()
    if challenge_id:
        attempts = [a for a in attempts if str(a.challenge.id) == challenge_id]
    items = [_serialize_attempt(a) for a in attempts]
    return {"total": len(items), "submissions": items}


# ── Student-facing ────────────────────────────────────────────────────────────

def list_challenges_for_user(user_id: str) -> dict:
    """Retos activos disponibles para el curso del usuario."""
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    challenges = _challenges.get_by_course(user.course)
    items = [_serialize_challenge(c, admin_view=False) for c in challenges]
    return {"total": len(items), "challenges": items}


def get_challenge_for_user(challenge_id: str, user_id: str) -> dict:
    """Detalle de un reto. Los test cases ocultos no muestran su contenido."""
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    challenge = _challenges.get_by_id(challenge_id)
    if not challenge or not challenge.is_active:
        raise ValueError("Reto no encontrado")

    # Verificar que el reto esté disponible para el curso del usuario
    course_ids = [str(c.id) for c in challenge.courses]
    if course_ids and str(user.course.id) not in course_ids:
        raise ValueError("Reto no disponible para tu curso")

    return _serialize_challenge(challenge, admin_view=False)


def get_my_attempts(challenge_id: str, user_id: str) -> dict:
    """Historial de intentos del usuario en un reto específico."""
    user = _users.get_active_by_id(user_id)
    challenge = _challenges.get_by_id(challenge_id)
    if not user or not challenge:
        raise ValueError("Reto o usuario no encontrado")

    attempts = _attempts.get_by_user_and_challenge(user, challenge)
    items = [_serialize_attempt(a) for a in attempts]
    return {
        "total": len(items),
        "already_passed": any(a["passed"] for a in items),
        "attempts": items,
    }


def get_my_progress(user_id: str) -> dict:
    """Progreso del usuario en todos los retos de su curso."""
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    challenges = list(_challenges.get_by_course(user.course))
    result = []
    for c in challenges:
        passed = _attempts.user_already_passed(user, c)
        pending = _attempts.model.objects(
            user=user, challenge=c, review_status="pending"
        ).count() > 0
        result.append({
            "id": str(c.id),
            "title": c.title,
            "difficulty": c.difficulty,
            "points": c.points,
            "requires_review": c.requires_review,
            "has_auto_grading": len(c.test_cases) > 0,
            "status": "passed" if passed else ("pending_review" if pending else "unsolved"),
            "courses": [{"id": str(course.id), "name": course.name, "code": course.code} for course in c.courses],
        })

    solved = sum(1 for r in result if r["status"] == "passed")
    return {
        "total_challenges": len(result),
        "solved": solved,
        "pending_review": sum(1 for r in result if r["status"] == "pending_review"),
        "challenges": result,
    }


async def submit_challenge(challenge_id: str, user_id: str, code: str) -> dict:
    """
    Evalúa el envío del estudiante.

    Flujo:
      1. Ejecuta el código contra cada test case (si los hay).
      2. Si requires_review=True  → review_status="pending", sin puntos aún.
      3. Si requires_review=False → puntos acreditados si pasó todos los tests
         (y es el primer pase).
      4. Si no hay test cases y requires_review=False → passed=True automático
         (el reto es de práctica libre, sin validación).
    """
    from app.core.process import CodeExecutor

    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    challenge = _challenges.get_by_id(challenge_id)
    if not challenge or not challenge.is_active:
        raise ValueError("Reto no encontrado")

    course_ids = [str(c.id) for c in challenge.courses]
    if course_ids and str(user.course.id) not in course_ids:
        raise ValueError("Reto no disponible para tu curso")

    # ── Validación AST: funciones requeridas ───────────────────────────────────
    ast_error = check_required_functions(code, list(challenge.required_functions or []))
    if ast_error:
        attempt_number = _attempts.count_attempts(user, challenge) + 1
        attempt = ChallengeAttempt(
            user=user,
            challenge=challenge,
            code=code,
            attempt_number=attempt_number,
            passed=False,
            results=[],
            points_earned=0,
            bonus_points_earned=0,
            ast_validation_error=ast_error,
            review_status=None,
        ).save()
        return _serialize_attempt(attempt)

    # ── Ejecutar contra test cases ─────────────────────────────────────────────
    results = []
    all_passed = True

    if challenge.test_cases:
        for i, tc in enumerate(challenge.test_cases):
            result = await CodeExecutor.execute_with_stdin(code, tc.input)
            actual = result["stdout"].strip()
            expected = tc.expected_output.strip()
            passed = (result["return_code"] == 0) and (actual == expected)
            if not passed:
                all_passed = False
            results.append(TestCaseResult(
                test_index=i,
                passed=passed,
                actual_output=actual,
                error=result["stderr"][:500] if not passed else "",
            ))
    else:
        # Sin test cases: sin validación automática
        all_passed = not challenge.requires_review

    # ── Determinar número de intento, puntos y estado de revisión ─────────────
    attempt_number = _attempts.count_attempts(user, challenge) + 1
    already_passed = _attempts.user_already_passed(user, challenge)
    points_earned = 0
    review_status = None

    bonus_points_earned = 0

    if challenge.requires_review:
        review_status = "pending"
        passed_flag = False   # se confirma cuando el docente apruebe
    else:
        passed_flag = all_passed
        if passed_flag and not already_passed:
            points_earned = _points_for_attempt(challenge.points, attempt_number)
            if challenge.lines_bonus_points and challenge.optimal_lines_min is not None:
                bonus_points_earned = calculate_lines_bonus(
                    code=code,
                    min_lines=challenge.optimal_lines_min,
                    max_lines=challenge.optimal_lines_max,
                    bonus_points=challenge.lines_bonus_points,
                )
            user.total_points += points_earned + bonus_points_earned
            user.save()

    attempt = ChallengeAttempt(
        user=user,
        challenge=challenge,
        code=code,
        attempt_number=attempt_number,
        passed=passed_flag,
        results=results,
        points_earned=points_earned,
        bonus_points_earned=bonus_points_earned,
        review_status=review_status,
    ).save()

    return _serialize_attempt(attempt)


def review_submission(
    attempt_id: str,
    reviewer_id: str,
    approved: bool,
    feedback: str,
) -> dict:
    attempt = _attempts.get_by_id(attempt_id)
    if not attempt:
        raise ValueError("Intento no encontrado")
    if attempt.review_status != "pending":
        raise ValueError("Este intento ya fue revisado")

    reviewer = _users.get_active_by_id(reviewer_id)
    now = datetime.utcnow()

    attempt.review_status = "approved" if approved else "rejected"
    attempt.review_feedback = feedback
    attempt.reviewed_by = reviewer
    attempt.reviewed_at = now

    if approved:
        attempt.passed = True
        # Solo acreditar puntos si no había pasado antes
        already_passed = _attempts.model.objects(
            user=attempt.user,
            challenge=attempt.challenge,
            passed=True,
            id__ne=attempt.id,
        ).count() > 0
        if not already_passed:
            points = _points_for_attempt(attempt.challenge.points, attempt.attempt_number)
            attempt.points_earned = points
            attempt.user.total_points += points
            attempt.user.save()

    attempt.save()
    return _serialize_attempt(attempt)