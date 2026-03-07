from datetime import datetime

from mongoengine import Document, StringField, BooleanField, DateTimeField


class Course(Document):
    name = StringField(required=True, max_length=100)
    code = StringField(required=True, max_length=20, unique=True)
    description = StringField(default="")
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "courses",
        "indexes": ["code"],
    }

    def __str__(self):
        return f"{self.name} ({self.code})"