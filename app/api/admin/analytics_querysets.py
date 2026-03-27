from datetime import datetime, timedelta

from app.models.error_event import ErrorEvent


class ErrorEventQueryset:

    def get_in_range(
        self,
        days: int,
        course_id: str | None = None,
        challenge_id: str | None = None,
    ) -> list:
        since = datetime.utcnow() - timedelta(days=days)
        qs = ErrorEvent.objects(created_at__gte=since)

        if course_id:
            from app.models.course import Course
            course = Course.objects(id=course_id).first()
            if course:
                qs = qs.filter(course=course)

        if challenge_id:
            from app.models.challenge import Challenge
            challenge = Challenge.objects(id=challenge_id).first()
            if challenge:
                qs = qs.filter(challenge=challenge)

        return list(qs.order_by("-created_at"))

    def get_recent_for_challenge(self, challenge_id: str, limit: int = 50) -> list:
        from app.models.challenge import Challenge
        challenge = Challenge.objects(id=challenge_id).first()
        if not challenge:
            return []
        return list(
            ErrorEvent.objects(challenge=challenge).order_by("-created_at").limit(limit)
        )
