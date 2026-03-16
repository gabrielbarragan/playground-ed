from datetime import datetime

from mongoengine import (
    Document,
    EmbeddedDocument,
    BooleanField,
    DateTimeField,
    IntField,
    ListField,
    EmbeddedDocumentField,
    ReferenceField,
)


class QuizAnswerRecord(EmbeddedDocument):
    """Respuesta del estudiante a una pregunta específica."""
    question_index = IntField(required=True)
    selected_option_index = IntField(required=True)
    # is_correct desnormalizado: si la pregunta se edita en el futuro,
    # el resultado histórico permanece inmutable.
    is_correct = BooleanField(required=True)


class QuizAttempt(Document):
    """
    Intento de quiz por usuario. Se permite UN solo intento por (user, quiz).
    El docente puede resetear el intento individualmente; al hacerlo los puntos
    acreditados NO se revierten (para evitar saldo negativo).
    """
    user = ReferenceField("User", required=True)
    quiz = ReferenceField("Quiz", required=True)
    answers = ListField(EmbeddedDocumentField(QuizAnswerRecord), default=list)

    correct_count = IntField(required=True, default=0)
    total_questions = IntField(required=True)
    passed = BooleanField(required=True, default=False)
    points_earned = IntField(default=0)

    submitted_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "quiz_attempts",
        "indexes": [
            "user",
            "quiz",
            ("user", "quiz"),
            ("quiz", "-submitted_at"),
        ],
    }