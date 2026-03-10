from app.core.queryset import BaseQueryset
from app.models.badge import Badge


class BadgeQueryset(BaseQueryset):
    model = Badge

    def get_active(self):
        return self.model.objects(is_active=True).order_by("order")

    def get_by_emoji(self, emoji: str):
        return self.model.objects(emoji=emoji, is_active=True).first()

    def exists(self, emoji: str) -> bool:
        return self.model.objects(emoji=emoji, is_active=True).count() > 0