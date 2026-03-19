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


class TestCaseResult(EmbeddedDocument):
    """Resultado de un caso de prueba individual dentro de un intento."""
    test_index = IntField(required=True)
    passed = BooleanField(required=True)
    actual_output = StringField(default="")
    error = StringField(default="")


class ChallengeAttempt(Document):
    """
    Registro de un intento de resolución de un reto por parte de un usuario.
    Se guarda cada envío; un mismo usuario puede tener múltiples intentos.

    Flujo de estados:
      - Auto-graded (requires_review=False): review_status=None, passed determina si ganó puntos.
      - Manual (requires_review=True): review_status="pending" → "approved"/"rejected" por docente.
    """
    user = ReferenceField("User", required=True)
    challenge = ReferenceField("Challenge", required=True)
    code = StringField(required=True)
    passed = BooleanField(required=True, default=False)
    # Resultado por cada test case del challenge
    results = ListField(EmbeddedDocumentField(TestCaseResult), default=list)
    # Número de intento del usuario en este reto (1 = primero, 2 = segundo, ...)
    attempt_number = IntField(default=1)
    # Puntos acreditados en este intento (decrece con cada reintento)
    points_earned = IntField(default=0)
    # Puntos bonus por eficiencia de líneas (0 si no aplica o no ganó el bono)
    bonus_points_earned = IntField(default=0)
    # Error de validación AST (vacío si no aplica o si pasó la validación)
    ast_validation_error = StringField(default="")
    submitted_at = DateTimeField(default=datetime.utcnow)

    # Revisión manual (None = no aplica / auto-graded)
    review_status = StringField(choices=["pending", "approved", "rejected"], null=True, default=None)
    review_feedback = StringField(default="")
    reviewed_by = ReferenceField("User", null=True)
    reviewed_at = DateTimeField(null=True)

    meta = {
        "collection": "challenge_attempts",
        "indexes": [
            "user",
            "challenge",
            ("user", "challenge"),
            ("user", "-submitted_at"),
            "review_status",            # filtrar pendientes de revisión
        ],
    }