from datetime import datetime

from mongoengine import (
    Document,
    DateTimeField,
    ReferenceField,
)


class UserReward(Document):
    """
    Relación entre un usuario y una recompensa obtenida.
    El par (user, reward) es único: no se puede ganar la misma insignia dos veces.
    """
    user = ReferenceField("User", required=True)
    reward = ReferenceField("Reward", required=True)
    earned_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "user_rewards",
        "indexes": [
            "user",
            ("user", "reward"),  # unique lookup
        ],
    }