from typing import Optional
from app.api.snippets import process


class SnippetHandler:
    @staticmethod
    def list(user_id: str) -> list:
        return process.list_by_user(user_id)

    @staticmethod
    def get(snippet_id: str, user_id: str) -> Optional[dict]:
        return process.get_by_id(snippet_id, user_id)

    @staticmethod
    def save(user_id: str, title: str, code: str, language: str, tags: list) -> dict:
        return process.save(user_id, title, code, language, tags)

    @staticmethod
    def update(snippet_id: str, user_id: str, title: str, code: str, tags: list) -> dict:
        return process.update(snippet_id, user_id, title, code, tags)

    @staticmethod
    def remove(snippet_id: str, user_id: str) -> None:
        return process.remove(snippet_id, user_id)