from typing import Optional
from app.api.courses import process


class CourseHandler:
    @staticmethod
    def list_active() -> list:
        return process.list_active()

    @staticmethod
    def get_by_id(course_id: str) -> Optional[dict]:
        return process.get_by_id(course_id)

    @staticmethod
    def create(name: str, code: str, description: str) -> dict:
        return process.create(name, code, description)

    @staticmethod
    def toggle_active(course_id: str) -> dict:
        return process.toggle_active(course_id)