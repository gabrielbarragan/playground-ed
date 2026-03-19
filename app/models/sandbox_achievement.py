from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    BooleanField,
    IntField,
    DateTimeField,
    ReferenceField,
)


class SandboxAchievement(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    icon = StringField(default="🏆")
    # "ast_concept" | "combo"
    trigger_type = StringField(required=True)
    # Slug devuelto por detect_concepts, ej: "loop_while", "list_comp"
    # Para combos: slugs separados por "+", ej: "list_comp+lambda"
    trigger_value = StringField(required=True, unique=True)
    points_bonus = IntField(default=0)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "sandbox_achievements",
        "indexes": ["is_active", "trigger_value"],
    }

    def __str__(self):
        return f"{self.icon} {self.name} ({self.trigger_value})"


class UserSandboxAchievement(Document):
    user = ReferenceField("User", required=True)
    achievement = ReferenceField(SandboxAchievement, required=True)
    earned_at = DateTimeField(default=datetime.utcnow)
    code_sample = StringField(default="")

    meta = {
        "collection": "user_sandbox_achievements",
        "indexes": [
            {"fields": ("user", "achievement"), "unique": True},
            "user",
            "earned_at",
        ],
    }