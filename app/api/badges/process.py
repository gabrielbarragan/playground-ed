from app.api.badges.querysets import BadgeQueryset

_badges = BadgeQueryset()

DEFAULT_BADGES = [
    ("🐍", "Serpiente", 0),
    ("🦊", "Zorro", 1),
    ("🦁", "León", 2),
    ("🐻", "Oso", 3),
    ("🦄", "Unicornio", 4),
    ("🐯", "Tigre", 5),
    ("🦋", "Mariposa", 6),
    ("🐉", "Dragón", 7),
    ("🦅", "Águila", 8),
    ("🌟", "Estrella", 9),
    ("⚡", "Rayo", 10),
    ("🔥", "Fuego", 11),
    ("💎", "Diamante", 12),
    ("🎯", "Diana", 13),
    ("🚀", "Cohete", 14),
    ("🎮", "Control", 15),
    ("🧠", "Cerebro", 16),
    ("👾", "Alien", 17),
    ("🤖", "Robot", 18),
    ("🎸", "Guitarra", 19),
    ("🏆", "Trofeo", 20),
    ("🌈", "Arcoíris", 21),
    ("🍀", "Trébol", 22),
    ("🎭", "Teatro", 23),
]


def seed_badges() -> int:
    """Inserta los badges por defecto si la colección está vacía. Devuelve cuántos se crearon."""
    if _badges.model.objects.count() > 0:
        return 0
    for emoji, label, order in DEFAULT_BADGES:
        _badges.model(emoji=emoji, label=label, order=order).save()
    return len(DEFAULT_BADGES)


def list_badges() -> list[dict]:
    return [
        {"emoji": b.emoji, "label": b.label, "order": b.order}
        for b in _badges.get_active()
    ]


def badge_exists(emoji: str) -> bool:
    return _badges.exists(emoji)