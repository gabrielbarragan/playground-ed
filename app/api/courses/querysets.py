from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.course import Course


class CourseQueryset(BaseQueryset):
    model = Course

    def get_active(self):
        return self.model.objects(is_active=True).order_by("name")

    def get_active_by_id(self, course_id: str) -> Optional[Course]:
        return self.model.objects(id=course_id, is_active=True).first()

    def get_by_code(self, code: str) -> Optional[Course]:
        return self.model.objects(code=code.upper()).first()