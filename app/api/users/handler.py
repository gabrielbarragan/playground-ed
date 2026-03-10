from typing import Optional
from app.api.users import process


class UserHandler:
    @staticmethod
    def register(first_name: str, last_name: str, email: str, password: str, course_id: str) -> dict:
        return process.register(first_name, last_name, email, password, course_id)

    @staticmethod
    def login(email: str, password: str) -> dict:
        return process.login(email, password)

    @staticmethod
    def get_profile(user_id: str) -> Optional[dict]:
        return process.get_profile(user_id)

    @staticmethod
    def update_profile(user_id: str, first_name: Optional[str], last_name: Optional[str]) -> dict:
        return process.update_profile(user_id, first_name, last_name)

    @staticmethod
    def set_badge(user_id: str, emoji: str) -> dict:
        return process.set_badge(user_id, emoji)