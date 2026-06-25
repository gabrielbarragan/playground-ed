from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.user import User


class AdminUserQueryset(BaseQueryset):
    model = User

    def get_all(self, include_inactive: bool = False, course_ids: Optional[list[str]] = None):
        qs = self.model.objects()
        if not include_inactive:
            qs = qs.filter(is_active=True)
        if course_ids is not None:
            qs = qs.filter(course__in=course_ids)
        return qs.order_by("last_name", "first_name")

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.model.objects(id=user_id).first()

    def get_by_course(self, course, include_inactive: bool = False):
        qs = self.model.objects(course=course)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("last_name", "first_name")

    def count_active(self, course_ids: Optional[list[str]] = None) -> int:
        qs = self.model.objects(is_active=True, is_admin=False)
        if course_ids is not None:
            qs = qs.filter(course__in=course_ids)
        return qs.count()

    def count_inactive(self, course_ids: Optional[list[str]] = None) -> int:
        qs = self.model.objects(is_active=False, is_admin=False)
        if course_ids is not None:
            qs = qs.filter(course__in=course_ids)
        return qs.count()

    def get_by_email(self, email: str):
        return self.model.objects(email=email).first()

    def update_email(self, user, new_email: str) -> None:
        user.email = new_email
        user.pending_email = None
        user.email_change_token_hash = None
        user.save()