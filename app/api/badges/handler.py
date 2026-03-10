from app.api.badges import process


class BadgeHandler:
    @staticmethod
    def list_badges() -> list[dict]:
        return process.list_badges()

    @staticmethod
    def seed_badges() -> int:
        return process.seed_badges()

    @staticmethod
    def badge_exists(emoji: str) -> bool:
        return process.badge_exists(emoji)