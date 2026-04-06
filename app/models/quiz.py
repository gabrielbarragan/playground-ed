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


class QuizOption(EmbeddedDocument):
    text = StringField(required=True, max_length=500)


class QuizQuestion(EmbeddedDocument):
    text = StringField(required=True)
    code_block = StringField(default="")
    code_language = StringField(default="python")
    # 2–6 opciones de respuesta
    options = ListField(EmbeddedDocumentField(QuizOption), default=list)
    # NUNCA se expone al estudiante antes de entregar
    correct_option_index = IntField(required=True, min_value=0)
    # Mostrada al estudiante solo si show_correct_answers=True (post-entrega)
    explanation = StringField(default="")


class Quiz(Document):
    title = StringField(required=True, max_length=200)
    description = StringField(default="")
    courses = ListField(ReferenceField("Course"), default=list)
    questions = ListField(EmbeddedDocumentField(QuizQuestion), default=list)

    # Configuración de evaluación
    passing_score = IntField(required=True, min_value=1)   # mínimo de correctas para aprobar
    points_on_complete = IntField(default=0)               # puntos por entregar (aunque no apruebe)
    points_on_pass = IntField(default=0)                   # puntos extra por aprobar

    # Configuración de Banco Aleatorio
    use_random_bank = BooleanField(default=False)
    questions_to_show = IntField(default=0)  # N preguntas a mostrar del pool (0 = sin banco)

    # Configuración de feedback post-entrega
    show_correct_answers = BooleanField(default=True)

    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "quizzes",
        "indexes": ["is_active", "courses"],
    }