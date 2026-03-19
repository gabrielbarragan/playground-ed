from app.api.sandbox_achievements import process


class AchievementHandler:

    @staticmethod
    def seed() -> int:
        return process.seed_achievements()

    @staticmethod
    def list_all(include_inactive: bool = False) -> list[dict]:
        return process.list_achievements(include_inactive=include_inactive)

    @staticmethod
    def create(name, description, icon, trigger_type, trigger_value, points_bonus) -> dict:
        return process.create_achievement(name, description, icon, trigger_type, trigger_value, points_bonus)

    @staticmethod
    def update(achievement_id: str, fields: dict) -> dict:
        return process.update_achievement(achievement_id, fields)

    @staticmethod
    def delete(achievement_id: str) -> dict:
        return process.delete_achievement(achievement_id)

    @staticmethod
    def unlock_for_run(user_id: str, code: str) -> list[dict]:
        return process.unlock_achievements_for_run(user_id, code)

    @staticmethod
    def get_user_achievements(user_id: str) -> dict:
        return process.get_user_achievements(user_id)