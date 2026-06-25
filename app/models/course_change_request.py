from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    ReferenceField,
)


class CourseChangeRequest(Document):
    user = ReferenceField("User", required=True)
    from_course = ReferenceField("Course", required=True)
    to_course = ReferenceField("Course", required=True)
    reason = StringField(default="")
    status = StringField(default="pending", choices=["pending", "approved", "rejected"])
    resolved_by = ReferenceField("User", null=True)
    resolved_at = DateTimeField(null=True)
    rejection_reason = StringField(default="")
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "course_change_requests",
        "indexes": ["user", "status", ("user", "status")],
    }
