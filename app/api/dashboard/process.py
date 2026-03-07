from datetime import datetime, timedelta
from typing import Optional

from app.api.dashboard.querysets import ActivityQueryset
from app.api.users.querysets import UserQueryset
from app.api.courses.querysets import CourseQueryset

_activity = ActivityQueryset()
_users = UserQueryset()
_courses = CourseQueryset()

_15_DAYS = 14  # 14 días atrás + hoy = 15 días


def _day_start(d: datetime) -> datetime:
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def log_execution(user_id: Optional[str], code: str, success: bool) -> None:
    """Registra una ejecución de código. Si user_id es None no se loguea."""
    if not user_id:
        return
    user = _users.get_active_by_id(user_id)
    if not user:
        return
    today = _day_start(datetime.utcnow())
    lines = len(code.splitlines())
    _activity.upsert_execution(user=user, activity_date=today, success=success, lines=lines)


def get_user_heatmap(user_id: str) -> dict:
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    today = _day_start(datetime.utcnow())
    start = today - timedelta(days=_15_DAYS)

    records = _activity.get_by_user_in_range(user, start, today)
    activity_map = {_day_start(r.activity_date): r for r in records}

    days = []
    current = start
    while current <= today:
        record = activity_map.get(current)
        days.append({
            "date": current.strftime("%Y-%m-%d"),
            "executions": record.executions if record else 0,
            "successful_executions": record.successful_executions if record else 0,
            "lines_of_code": record.lines_of_code if record else 0,
        })
        current += timedelta(days=1)

    total = sum(d["executions"] for d in days)
    streak = _calculate_streak(activity_map, today)

    return {
        "days": days,
        "total_executions": total,
        "streak_days": streak,
    }


def get_course_users_summary(course_id: str) -> dict:
    course = _courses.get_by_id(course_id)
    if not course:
        raise ValueError("Curso no encontrado")

    today = _day_start(datetime.utcnow())
    start = today - timedelta(days=_15_DAYS)

    users = _users.get_by_course(course)
    result = []

    for user in users:
        records = _activity.get_by_user_in_range(user, start, today)
        activity_map = {_day_start(r.activity_date): r for r in records}

        days = []
        current = start
        while current <= today:
            record = activity_map.get(current)
            days.append({
                "date": current.strftime("%Y-%m-%d"),
                "executions": record.executions if record else 0,
            })
            current += timedelta(days=1)

        total = sum(d["executions"] for d in days)
        active_days = sum(1 for d in days if d["executions"] > 0)

        result.append({
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "total_points": user.total_points,
            "total_executions_last_15_days": total,
            "active_days_last_15_days": active_days,
            "activity": days,
        })

    return {
        "course": {"id": str(course.id), "name": course.name, "code": course.code},
        "total_users": len(result),
        "users": result,
    }


def get_course_ranking(course_id: str, limit: int = 20) -> dict:
    course = _courses.get_by_id(course_id)
    if not course:
        raise ValueError("Curso no encontrado")

    users = _users.get_ranking_by_course(course, limit)
    ranking = [
        {
            "rank": i,
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "total_points": user.total_points,
        }
        for i, user in enumerate(users, 1)
    ]

    return {
        "course": {"id": str(course.id), "name": course.name, "code": course.code},
        "ranking": ranking,
    }


def _calculate_streak(activity_map: dict, today: datetime) -> int:
    streak = 0
    current = today
    while current in activity_map and activity_map[current].executions > 0:
        streak += 1
        current -= timedelta(days=1)
    return streak