from datetime import datetime, timedelta

from app.models.user import User
from app.models.challenge_attempt import ChallengeAttempt
from app.models.quiz_attempt import QuizAttempt
from app.models.code_snippet import CodeSnippet
from app.models.sandbox_achievement import UserSandboxAchievement
from app.models.challenge import Challenge
from app.models.quiz import Quiz
from app.api.dashboard.process import get_user_heatmap


def _get_user(user_id: str) -> User:
    user = User.objects(id=user_id).first()
    if not user:
        raise ValueError("Usuario no encontrado")
    return user


def _serialize_attempt_brief(attempt: ChallengeAttempt) -> dict:
    challenge = attempt.challenge
    return {
        "id": str(attempt.id),
        "challenge_id": str(challenge.id),
        "challenge_title": challenge.title,
        "challenge_difficulty": challenge.difficulty,
        "passed": attempt.passed,
        "points_earned": attempt.points_earned,
        "bonus_points_earned": attempt.bonus_points_earned,
        "attempt_number": attempt.attempt_number,
        "review_status": attempt.review_status,
        "submitted_at": attempt.submitted_at.isoformat(),
    }


def _serialize_quiz_result_brief(attempt: QuizAttempt) -> dict:
    quiz = attempt.quiz
    return {
        "id": str(attempt.id),
        "quiz_id": str(quiz.id),
        "quiz_title": quiz.title,
        "correct_count": attempt.correct_count,
        "total_questions": attempt.total_questions,
        "passed": attempt.passed,
        "points_earned": attempt.points_earned,
        "submitted_at": attempt.submitted_at.isoformat(),
    }


def get_profile_summary(user_id: str) -> dict:
    user = _get_user(user_id)

    now = datetime.utcnow()
    start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    challenge_attempts_week = list(ChallengeAttempt.objects(
        user=user,
        passed=True,
        submitted_at__gte=start,
    ).only("points_earned", "bonus_points_earned"))

    quiz_attempts_week = list(QuizAttempt.objects(
        user=user,
        submitted_at__gte=start,
    ).only("points_earned"))

    points_challenges = sum(a.points_earned for a in challenge_attempts_week)
    points_bonus = sum(a.bonus_points_earned for a in challenge_attempts_week)
    points_quizzes = sum(a.points_earned for a in quiz_attempts_week)

    course_challenges = Challenge.objects(courses=user.course, is_active=True)
    solved_ids = set(
        str(a.challenge.id)
        for a in ChallengeAttempt.objects(user=user, passed=True).only("challenge")
    )

    course_quizzes = Quiz.objects(courses=user.course, is_active=True)
    completed_quiz_ids = set(
        str(a.quiz.id)
        for a in QuizAttempt.objects(user=user).only("quiz")
    )
    passed_quiz_ids = set(
        str(a.quiz.id)
        for a in QuizAttempt.objects(user=user, passed=True).only("quiz")
    )

    snippets_count = CodeSnippet.objects(user=user).count()
    achievements_count = UserSandboxAchievement.objects(user=user).count()

    recent_attempts = list(
        ChallengeAttempt.objects(user=user).order_by("-submitted_at").limit(5)
    )
    recent_quiz_results = list(
        QuizAttempt.objects(user=user).order_by("-submitted_at").limit(3)
    )

    heatmap = get_user_heatmap(str(user.id))

    # Entregas pendientes de revisión manual
    pending_review_count = ChallengeAttempt.objects(
        user=user, review_status="pending"
    ).count()

    return {
        "user": {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "badge": user.badge,
            "total_points": user.total_points,
            "course": {
                "id": str(user.course.id),
                "name": user.course.name,
                "code": user.course.code,
            } if user.course else None,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        },
        "points_this_week": points_challenges + points_bonus + points_quizzes,
        "points_breakdown": {
            "challenges": points_challenges,
            "quizzes": points_quizzes,
            "bonus": points_bonus,
        },
        "challenges_solved": len(solved_ids),
        "challenges_total": course_challenges.count(),
        "quizzes_passed": len(passed_quiz_ids),
        "quizzes_completed": len(completed_quiz_ids),
        "quizzes_total": course_quizzes.count(),
        "snippets_count": snippets_count,
        "achievements_count": achievements_count,
        "pending_review_count": pending_review_count,
        "streak_days": heatmap["streak_days"],
        "activity_heatmap": heatmap["days"],
        "recent_attempts": [_serialize_attempt_brief(a) for a in recent_attempts],
        "recent_quiz_results": [_serialize_quiz_result_brief(a) for a in recent_quiz_results],
    }


def get_student_challenges(user_id: str) -> dict:
    user = _get_user(user_id)

    course_challenges = list(Challenge.objects(courses=user.course, is_active=True))

    attempts_map: dict = {}
    for a in ChallengeAttempt.objects(user=user, passed=True).order_by("attempt_number"):
        cid = str(a.challenge.id)
        if cid not in attempts_map:
            attempts_map[cid] = a

    solved = []
    pending = []

    for c in course_challenges:
        cid = str(c.id)
        if cid in attempts_map:
            a = attempts_map[cid]
            solved.append({
                "challenge_id": cid,
                "title": c.title,
                "difficulty": c.difficulty,
                "points": c.points,
                "points_earned": a.points_earned,
                "bonus_points_earned": a.bonus_points_earned,
                "attempt_number": a.attempt_number,
                "solved_at": a.submitted_at.isoformat(),
            })
        else:
            total_attempts = ChallengeAttempt.objects(user=user, challenge=c).count()
            pending.append({
                "challenge_id": cid,
                "title": c.title,
                "difficulty": c.difficulty,
                "points": c.points,
                "total_attempts": total_attempts,
                "requires_review": c.requires_review,
            })

    return {
        "solved": sorted(solved, key=lambda x: x["solved_at"], reverse=True),
        "pending": sorted(pending, key=lambda x: x["total_attempts"], reverse=True),
    }


def get_student_quizzes(user_id: str) -> dict:
    user = _get_user(user_id)

    course_quizzes = list(Quiz.objects(courses=user.course, is_active=True))
    attempt_map = {
        str(a.quiz.id): a
        for a in QuizAttempt.objects(user=user)
    }

    completed = []
    pending = []

    for q in course_quizzes:
        qid = str(q.id)
        if qid in attempt_map:
            a = attempt_map[qid]
            completed.append({
                "quiz_id": qid,
                "title": q.title,
                "correct_count": a.correct_count,
                "total_questions": a.total_questions,
                "passed": a.passed,
                "points_earned": a.points_earned,
                "submitted_at": a.submitted_at.isoformat(),
            })
        else:
            pending.append({
                "quiz_id": qid,
                "title": q.title,
                "question_count": len(q.questions),
                "points_on_complete": q.points_on_complete,
                "points_on_pass": q.points_on_pass,
                "passing_score": q.passing_score,
            })

    return {
        "completed": sorted(completed, key=lambda x: x["submitted_at"], reverse=True),
        "pending": pending,
    }


def get_student_attempts(user_id: str, limit: int = 10) -> dict:
    user = _get_user(user_id)
    limit = min(limit, 50)
    attempts = list(
        ChallengeAttempt.objects(user=user).order_by("-submitted_at").limit(limit)
    )
    return {
        "attempts": [
            {
                "id": str(a.id),
                "challenge_id": str(a.challenge.id),
                "challenge_title": a.challenge.title,
                "challenge_difficulty": a.challenge.difficulty,
                "code": a.code,
                "passed": a.passed,
                "points_earned": a.points_earned,
                "bonus_points_earned": a.bonus_points_earned,
                "attempt_number": a.attempt_number,
                "review_status": a.review_status,
                "review_feedback": a.review_feedback,
                "submitted_at": a.submitted_at.isoformat(),
            }
            for a in attempts
        ]
    }


def get_student_snippets(user_id: str, limit: int = 20) -> dict:
    user = _get_user(user_id)
    limit = min(limit, 50)
    snippets = list(
        CodeSnippet.objects(user=user).order_by("-updated_at").limit(limit)
    )
    return {
        "snippets": [
            {
                "id": str(s.id),
                "title": s.title,
                "language": s.language,
                "tags": s.tags,
                "code_preview": "\n".join(s.code.splitlines()[:3]),
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in snippets
        ]
    }


def get_student_achievements(user_id: str) -> dict:
    user = _get_user(user_id)
    user_achievements = list(
        UserSandboxAchievement.objects(user=user).order_by("-earned_at")
    )
    return {
        "achievements": [
            {
                "id": str(ua.id),
                "name": ua.achievement.name,
                "description": ua.achievement.description,
                "icon": ua.achievement.icon,
                "trigger_value": ua.achievement.trigger_value,
                "points_bonus": ua.achievement.points_bonus,
                "earned_at": ua.earned_at.isoformat(),
            }
            for ua in user_achievements
        ]
    }


def get_points_breakdown_by_day(user_id: str) -> dict:
    user = _get_user(user_id)

    now = datetime.utcnow()
    start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    days: dict = {}
    current = start
    while current <= now:
        days[current.strftime("%Y-%m-%d")] = {"challenges": 0, "quizzes": 0, "bonus": 0}
        current += timedelta(days=1)

    for a in ChallengeAttempt.objects(user=user, passed=True, submitted_at__gte=start):
        key = a.submitted_at.strftime("%Y-%m-%d")
        if key in days:
            days[key]["challenges"] += a.points_earned
            days[key]["bonus"] += a.bonus_points_earned

    for a in QuizAttempt.objects(user=user, submitted_at__gte=start):
        key = a.submitted_at.strftime("%Y-%m-%d")
        if key in days:
            days[key]["quizzes"] += a.points_earned

    result = [
        {"date": day, **breakdown, "total": sum(breakdown.values())}
        for day, breakdown in sorted(days.items())
    ]

    return {
        "days": result,
        "total_week": sum(d["total"] for d in result),
    }
