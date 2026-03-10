from typing import Optional
from app.core.queryset import BaseQueryset
from app.models.challenge import Challenge
from app.models.challenge_attempt import ChallengeAttempt


class ChallengeQueryset(BaseQueryset):
    model = Challenge

    def get_all(self, include_inactive: bool = False):
        qs = self.model.objects()
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("-created_at")

    def get_by_id(self, challenge_id: str) -> Optional[Challenge]:
        try:
            return self.model.objects(id=challenge_id).first()
        except Exception:
            return None

    def get_by_course(self, course, include_inactive: bool = False):
        qs = self.model.objects(courses=course)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("difficulty", "-points")


class AttemptQueryset(BaseQueryset):
    model = ChallengeAttempt

    def get_pending_review(self):
        """Intentos que esperan revisión manual del docente."""
        return self.model.objects(review_status="pending").order_by("submitted_at")

    def get_by_id(self, attempt_id: str) -> Optional[ChallengeAttempt]:
        try:
            return self.model.objects(id=attempt_id).first()
        except Exception:
            return None

    def get_by_user_and_challenge(self, user, challenge):
        return self.model.objects(user=user, challenge=challenge).order_by("-submitted_at")

    def count_attempts(self, user, challenge) -> int:
        return self.model.objects(user=user, challenge=challenge).count()

    def user_already_passed(self, user, challenge) -> bool:
        return self.model.objects(user=user, challenge=challenge, passed=True).count() > 0