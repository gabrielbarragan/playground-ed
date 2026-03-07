from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    BooleanField,
    DateTimeField,
    IntField,
    ReferenceField,
)


class User(Document):
    first_name = StringField(required=True, max_length=100)
    last_name = StringField(required=True, max_length=100)
    email = StringField(required=True, max_length=200, unique=True)
    password_hash = StringField(required=True)
    course = ReferenceField("Course", required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField(null=True)
    # Desnormalizado para ranking en tiempo real sin aggregation costosa
    total_points = IntField(default=0)

    meta = {
        "collection": "users",
        "indexes": ["email", "course", "-total_points"],
    }

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"