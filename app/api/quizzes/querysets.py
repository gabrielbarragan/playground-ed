from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt


class QuizQueryset(BaseQueryset):
    model = Quiz

    def get_all(self, include_inactive: bool = False):
        qs = self.model.objects()
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("-created_at")

    def get_by_id(self, quiz_id: str) -> Optional[Quiz]:
        try:
            return self.model.objects(id=quiz_id).first()
        except Exception:
            return None

    def get_active_by_id(self, quiz_id: str) -> Optional[Quiz]:
        try:
            return self.model.objects(id=quiz_id, is_active=True).first()
        except Exception:
            return None

    def get_by_course(self, course):
        return self.model.objects(courses=course, is_active=True).order_by("-created_at")


class AttemptQueryset(BaseQueryset):
    model = QuizAttempt

    def get_by_user_and_quiz(self, user, quiz) -> Optional[QuizAttempt]:
        return self.model.objects(user=user, quiz=quiz).first()

    def get_by_quiz(self, quiz):
        return self.model.objects(quiz=quiz).order_by("-submitted_at")

    def get_by_user(self, user):
        return self.model.objects(user=user).order_by("-submitted_at")