from datetime import datetime

from mongoengine import (
    Document,
    DateTimeField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)


class ErrorEvent(Document):
    """
    Registra cada ejecución fallida (return_code != 0) para analítica docente.
    Solo se guarda cuando hay usuario autenticado para tener trazabilidad.
    """

    user = ReferenceField("User", required=True)
    challenge = ReferenceField("Challenge", null=True, default=None)
    code = StringField(required=True)
    error_type = StringField(default="")          # "SyntaxError", "TypeError", etc.
    error_line = IntField(null=True, default=None) # línea del error (parseada del traceback)
    error_msg = StringField(max_length=300, default="")  # última línea del traceback
    concepts = ListField(StringField(), default=list)    # ["loop_for", "recursion", ...]
    course = ReferenceField("Course", null=True, default=None)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "error_events",
        "indexes": [
            "user",
            "challenge",
            "course",
            "-created_at",
            ("challenge", "error_line"),
            ("course", "error_type"),
        ],
    }
