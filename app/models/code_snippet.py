from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    BooleanField,
    DateTimeField,
    ListField,
    ReferenceField,
)


class CodeSnippet(Document):
    user = ReferenceField("User", required=True)
    title = StringField(required=True, max_length=200)
    code = StringField(required=True)
    language = StringField(default="python", max_length=50)
    tags = ListField(StringField(max_length=50), default=list)
    is_public = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "code_snippets",
        "indexes": [
            "user",
            "-created_at",
            ("user", "-created_at"),
        ],
    }