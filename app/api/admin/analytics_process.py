"""
Lógica de analítica docente — Mapa de calor de errores.
Toda la agregación se hace en Python sobre los documentos ya filtrados,
siguiendo el mismo patrón del módulo dashboard.
"""
from collections import Counter, defaultdict

from app.api.admin.analytics_querysets import ErrorEventQueryset

_qs = ErrorEventQueryset()


def _serialize_event(ev) -> dict:
    user = ev.user
    challenge = ev.challenge
    return {
        "id": str(ev.id),
        "student": f"{user.first_name} {user.last_name}" if user else "—",
        "challenge": challenge.title if challenge else None,
        "challenge_id": str(challenge.id) if challenge else None,
        "error_type": ev.error_type or "Unknown",
        "error_msg": ev.error_msg or "",
        "error_line": ev.error_line,
        "created_at": ev.created_at.isoformat(),
    }


def get_error_heatmap(
    course_id: str | None = None,
    challenge_id: str | None = None,
    days: int = 7,
) -> dict:
    events = _qs.get_in_range(days=days, course_id=course_id, challenge_id=challenge_id)

    if not events:
        return {
            "by_line": [],
            "by_concept": [],
            "by_error_type": [],
            "period_days": days,
            "total_errors": 0,
        }

    # ── by_line ────────────────────────────────────────────────────────────────
    line_data: dict[int, dict] = defaultdict(lambda: {"errors": [], "users": set()})
    for ev in events:
        if ev.error_line:
            key = ev.error_line
            line_data[key]["errors"].append(ev.error_type or "Unknown")
            line_data[key]["users"].add(str(ev.user.id) if ev.user else "anon")

    by_line = []
    for line_num, info in sorted(line_data.items()):
        top = Counter(info["errors"]).most_common(1)
        by_line.append({
            "line": line_num,
            "error_count": len(info["errors"]),
            "top_error": top[0][0] if top else "",
            "users_affected": len(info["users"]),
        })
    by_line.sort(key=lambda x: x["error_count"], reverse=True)

    # ── by_concept ─────────────────────────────────────────────────────────────
    concept_data: dict[str, dict] = defaultdict(lambda: {"count": 0, "users": set()})
    total_users = len({str(ev.user.id) for ev in events if ev.user})
    for ev in events:
        uid = str(ev.user.id) if ev.user else None
        for concept in (ev.concepts or []):
            concept_data[concept]["count"] += 1
            if uid:
                concept_data[concept]["users"].add(uid)

    by_concept = [
        {
            "concept": concept,
            "error_count": info["count"],
            "users_affected": len(info["users"]),
            "pct_users": round(len(info["users"]) / total_users * 100) if total_users else 0,
        }
        for concept, info in concept_data.items()
    ]
    by_concept.sort(key=lambda x: x["error_count"], reverse=True)

    # ── by_error_type ──────────────────────────────────────────────────────────
    type_counter: Counter = Counter(ev.error_type or "Unknown" for ev in events)
    by_error_type = [
        {"type": t, "count": c}
        for t, c in type_counter.most_common()
    ]

    return {
        "by_line": by_line,
        "by_concept": by_concept,
        "by_error_type": by_error_type,
        "period_days": days,
        "total_errors": len(events),
    }


def get_concepts_ranking(
    course_id: str | None = None,
    days: int = 7,
) -> dict:
    events = _qs.get_in_range(days=days, course_id=course_id)
    total_users = len({str(ev.user.id) for ev in events if ev.user})

    concept_data: dict[str, dict] = defaultdict(lambda: {"count": 0, "users": set()})
    for ev in events:
        uid = str(ev.user.id) if ev.user else None
        for concept in (ev.concepts or []):
            concept_data[concept]["count"] += 1
            if uid:
                concept_data[concept]["users"].add(uid)

    ranking = [
        {
            "concept": concept,
            "error_count": info["count"],
            "users_affected": len(info["users"]),
            "pct_users": round(len(info["users"]) / total_users * 100) if total_users else 0,
        }
        for concept, info in concept_data.items()
    ]
    ranking.sort(key=lambda x: x["error_count"], reverse=True)

    return {"total_users": total_users, "concepts": ranking}


def get_challenge_errors(challenge_id: str) -> dict:
    events = _qs.get_recent_for_challenge(challenge_id, limit=100)

    if not events:
        return {"challenge_id": challenge_id, "total_errors": 0, "by_line": [], "recent": []}

    line_data: dict[int, dict] = defaultdict(lambda: {"errors": [], "users": set()})
    for ev in events:
        if ev.error_line:
            key = ev.error_line
            line_data[key]["errors"].append(ev.error_type or "Unknown")
            line_data[key]["users"].add(str(ev.user.id) if ev.user else "anon")

    by_line = []
    for line_num, info in sorted(line_data.items()):
        top = Counter(info["errors"]).most_common(1)
        by_line.append({
            "line": line_num,
            "error_count": len(info["errors"]),
            "top_error": top[0][0] if top else "",
            "users_affected": len(info["users"]),
        })

    recent = [_serialize_event(ev) for ev in events[:20]]

    return {
        "challenge_id": challenge_id,
        "total_errors": len(events),
        "by_line": sorted(by_line, key=lambda x: x["error_count"], reverse=True),
        "recent": recent,
    }
