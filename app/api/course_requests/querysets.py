from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.course_change_request import CourseChangeRequest


class CourseChangeRequestQueryset(BaseQueryset):
    model = CourseChangeRequest

    def get_pending_by_user(self, user) -> Optional[CourseChangeRequest]:
        return self.model.objects(user=user, status="pending").first()

    def get_pending_by_courses(self, course_ids: Optional[list[str]] = None):
        qs = self.model.objects(status="pending").order_by("-created_at")
        if course_ids is not None:
            from mongoengine import Q
            qs = qs.filter(Q(from_course__in=course_ids) | Q(to_course__in=course_ids))
        return qs
