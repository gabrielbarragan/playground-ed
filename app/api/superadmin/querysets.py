from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.user import User


class SuperAdminUserQueryset(BaseQueryset):
    model = User

    def get_all(self, include_inactive: bool = False):
        qs = self.model.objects()
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("last_name", "first_name")

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.model.objects(id=user_id).first()