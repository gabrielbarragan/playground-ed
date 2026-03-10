from mongoengine import Document, StringField, BooleanField, IntField


class Badge(Document):
    emoji = StringField(required=True, unique=True)
    label = StringField(required=True)
    is_active = BooleanField(default=True)
    order = IntField(default=0)

    meta = {
        "collection": "badges",
        "indexes": ["is_active", "order"],
        "ordering": ["order"],
    }

    def __str__(self):
        return f"{self.emoji} {self.label}"