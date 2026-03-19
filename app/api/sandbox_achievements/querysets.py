from app.core.queryset import BaseQueryset
from app.models.sandbox_achievement import SandboxAchievement, UserSandboxAchievement


class AchievementQueryset(BaseQueryset):
    model = SandboxAchievement

    def get_active(self):
        return list(self.model.objects(is_active=True).order_by("trigger_value"))

    def get_by_trigger_values(self, trigger_values: list[str]):
        return list(self.model.objects(trigger_value__in=trigger_values, is_active=True))


class UserAchievementQueryset(BaseQueryset):
    model = UserSandboxAchievement

    def get_for_user(self, user_id: str):
        return list(self.model.objects(user=user_id).order_by("-earned_at").select_related())

    def already_earned(self, user_id: str, achievement_id: str) -> bool:
        return self.model.objects(user=user_id, achievement=achievement_id).count() > 0

    def get_earned_ids(self, user_id: str) -> set:
        return {
            str(ua.achievement.id)
            for ua in self.model.objects(user=user_id).only("achievement")
        }