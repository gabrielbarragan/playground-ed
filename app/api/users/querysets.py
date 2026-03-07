from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.user import User


class UserQueryset(BaseQueryset):
    model = User

    def get_by_email(self, email: str) -> Optional[User]:
        return self.model.objects(email=email).first()

    def get_active_by_email(self, email: str) -> Optional[User]:
        return self.model.objects(email=email, is_active=True).first()

    def get_active_by_id(self, user_id: str) -> Optional[User]:
        return self.model.objects(id=user_id, is_active=True).first()

    def get_by_course(self, course):
        return self.model.objects(course=course, is_active=True)

    def get_ranking_by_course(self, course, limit: int = 20):
        return self.model.objects(course=course, is_active=True).order_by("-total_points").limit(limit)

    def add_points(self, user: User, points: int) -> User:
        user.total_points += points
        user.save()
        return user