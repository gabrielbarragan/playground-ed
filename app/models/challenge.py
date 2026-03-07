from datetime import datetime

from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    BooleanField,
    DateTimeField,
    IntField,
    ListField,
    EmbeddedDocumentField,
    ReferenceField,
)


class TestCase(EmbeddedDocument):
    input = StringField(default="")
    expected_output = StringField(required=True)
    is_hidden = BooleanField(default=False)
    description = StringField(default="")


class Challenge(Document):
    title = StringField(required=True, max_length=200)
    description = StringField(required=True)  # Soporta markdown
    difficulty = StringField(
        required=True,
        choices=["easy", "medium", "hard"],
    )
    # El reto puede estar disponible para uno o varios cursos
    courses = ListField(ReferenceField("Course"), default=list)
    starter_code = StringField(default="")
    test_cases = ListField(EmbeddedDocumentField(TestCase), default=list)
    points = IntField(required=True, min_value=0)
    tags = ListField(StringField(max_length=50), default=list)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "challenges",
        "indexes": ["difficulty", "is_active"],
    }