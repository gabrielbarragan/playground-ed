from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    IntField,
    ReferenceField,
    DateTimeField,
)


class Reward(Document):
    name = StringField(required=True, max_length=100)
    description = StringField(required=True)
    badge_icon = StringField(default="star")
    trigger_type = StringField(
        required=True,
        choices=[
            "challenges_completed",  # completó N retos
            "streak_days",           # N días consecutivos de actividad
            "points_total",          # acumuló N puntos
            "first_snippet",         # guardó su primer snippet
        ],
    )
    trigger_value = IntField(required=True, min_value=1)
    # null = recompensa global; con valor = exclusiva del curso
    course = ReferenceField("Course", null=True)
    points_bonus = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "rewards",
        "indexes": ["trigger_type"],
    }