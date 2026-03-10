from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.user import User


class AdminUserQueryset(BaseQueryset):
    model = User

    def get_all(self, include_inactive: bool = False):
        if include_inactive:
            return self.model.objects().order_by("last_name", "first_name")
        return self.model.objects(is_active=True).order_by("last_name", "first_name")

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.model.objects(id=user_id).first()

    def get_by_course(self, course, include_inactive: bool = False):
        qs = self.model.objects(course=course)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("last_name", "first_name")

    def count_active(self) -> int:
        return self.model.objects(is_active=True, is_admin=False).count()

    def count_inactive(self) -> int:
        return self.model.objects(is_active=False, is_admin=False).count()