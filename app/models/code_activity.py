from datetime import datetime

from mongoengine import (
    Document,
    ReferenceField,
    DateTimeField,
    IntField,
)


class CodeActivity(Document):
    """
    Un registro por (usuario, día). Se hace upsert cada vez que el usuario
    ejecuta código. Es la fuente de datos para el heatmap tipo GitHub.
    """
    user = ReferenceField("User", required=True)
    # Almacenado como DateTimeField con hora 00:00:00 UTC para compatibilidad
    # con mongoengine. Se compara usando __gte / __lte con datetime(y, m, d).
    activity_date = DateTimeField(required=True)
    executions = IntField(default=1)
    successful_executions = IntField(default=0)
    lines_of_code = IntField(default=0)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "code_activity",
        "indexes": [
            ("user", "activity_date"),  # lookup principal del dashboard
            "activity_date",            # actividad global por día
        ],
    }