from datetime import datetime
from mongoengine import NotUniqueError

from app.api.sandbox_achievements.querysets import AchievementQueryset, UserAchievementQueryset
from app.api.users.querysets import UserQueryset
from app.core.achievement_detector import get_triggered_values
from app.models.sandbox_achievement import SandboxAchievement, UserSandboxAchievement

_achievements = AchievementQueryset()
_user_achievements = UserAchievementQueryset()
_users = UserQueryset()

# ── Logros iniciales del sistema ───────────────────────────────────────────────

DEFAULT_ACHIEVEMENTS = [
    {
        "name": "Maestro del bucle",
        "description": "Usaste un bucle while por primera vez. ¡El loop está contigo!",
        "icon": "🔄",
        "trigger_type": "ast_concept",
        "trigger_value": "loop_while",
        "points_bonus": 10,
    },
    {
        "name": "Manejo de errores",
        "description": "Controlaste una excepción con try/except. El código robusto empieza aquí.",
        "icon": "🛡️",
        "trigger_type": "ast_concept",
        "trigger_value": "try_except",
        "points_bonus": 10,
    },
    {
        "name": "Comprensión de listas",
        "description": "Usaste una list comprehension. Pythónico y elegante.",
        "icon": "📋",
        "trigger_type": "ast_concept",
        "trigger_value": "list_comp",
        "points_bonus": 15,
    },
    {
        "name": "Arquitecto de clases",
        "description": "Definiste una clase. Bienvenido a la programación orientada a objetos.",
        "icon": "🏗️",
        "trigger_type": "ast_concept",
        "trigger_value": "class",
        "points_bonus": 20,
    },
    {
        "name": "Función anónima",
        "description": "Usaste un lambda. Las funciones también pueden ser anónimas.",
        "icon": "⚡",
        "trigger_type": "ast_concept",
        "trigger_value": "lambda",
        "points_bonus": 10,
    },
    {
        "name": "Código funcional",
        "description": "Usaste una expresión generadora. Memoria eficiente al siguiente nivel.",
        "icon": "⚙️",
        "trigger_type": "ast_concept",
        "trigger_value": "generator",
        "points_bonus": 15,
    },
    {
        "name": "Maestro de la recursión",
        "description": "Una función que se llama a sí misma. La elegancia en su máxima expresión.",
        "icon": "🌀",
        "trigger_type": "ast_concept",
        "trigger_value": "recursion",
        "points_bonus": 25,
    },
    {
        "name": "Doble poder",
        "description": "Usaste list comprehension Y lambda en el mismo código. ¡Imparable!",
        "icon": "💥",
        "trigger_type": "combo",
        "trigger_value": "lambda+list_comp",
        "points_bonus": 20,
    },
]


# ── Serializers ────────────────────────────────────────────────────────────────

def _serialize_achievement(a: SandboxAchievement) -> dict:
    return {
        "id": str(a.id),
        "name": a.name,
        "description": a.description,
        "icon": a.icon,
        "trigger_type": a.trigger_type,
        "trigger_value": a.trigger_value,
        "points_bonus": a.points_bonus,
        "is_active": a.is_active,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _serialize_user_achievement(ua: UserSandboxAchievement) -> dict:
    a = ua.achievement
    return {
        "id": str(ua.id),
        "earned_at": ua.earned_at.isoformat() if ua.earned_at else None,
        "achievement": {
            "id": str(a.id),
            "name": a.name,
            "description": a.description,
            "icon": a.icon,
            "points_bonus": a.points_bonus,
        },
    }


# ── Seed ───────────────────────────────────────────────────────────────────────

def seed_achievements() -> int:
    """Inserta los logros por defecto si la colección está vacía."""
    if _achievements.model.objects.count() > 0:
        return 0
    for data in DEFAULT_ACHIEVEMENTS:
        _achievements.model(**data).save()
    return len(DEFAULT_ACHIEVEMENTS)


# ── CRUD admin ─────────────────────────────────────────────────────────────────

def list_achievements(include_inactive: bool = False) -> list[dict]:
    if include_inactive:
        achievements = list(_achievements.model.objects.all().order_by("trigger_value"))
    else:
        achievements = _achievements.get_active()
    return [_serialize_achievement(a) for a in achievements]


def create_achievement(name, description, icon, trigger_type, trigger_value, points_bonus) -> dict:
    if _achievements.model.objects(trigger_value=trigger_value).first():
        raise ValueError(f"Ya existe un logro con trigger_value '{trigger_value}'")
    a = _achievements.model(
        name=name,
        description=description,
        icon=icon,
        trigger_type=trigger_type,
        trigger_value=trigger_value,
        points_bonus=points_bonus,
    ).save()
    return _serialize_achievement(a)


def update_achievement(achievement_id: str, fields: dict) -> dict:
    a = _achievements.get_by_id(achievement_id)
    if not a:
        raise ValueError("Logro no encontrado")
    for k, v in fields.items():
        setattr(a, k, v)
    a.save()
    return _serialize_achievement(a)


def delete_achievement(achievement_id: str) -> dict:
    a = _achievements.get_by_id(achievement_id)
    if not a:
        raise ValueError("Logro no encontrado")
    a.is_active = False
    a.save()
    return {"ok": True}


# ── Detección y unlock ─────────────────────────────────────────────────────────

def unlock_achievements_for_run(user_id: str, code: str) -> list[dict]:
    """
    Detecta conceptos en el código y desbloquea logros nuevos para el usuario.
    Retorna los logros recién desbloqueados (vacío si ninguno es nuevo).
    """
    triggered = get_triggered_values(code)
    if not triggered:
        return []

    matching = _achievements.get_by_trigger_values(triggered)
    if not matching:
        return []

    earned_ids = _user_achievements.get_earned_ids(user_id)
    user = _users.get_by_id(user_id)

    new_unlocked = []
    for achievement in matching:
        if str(achievement.id) in earned_ids:
            continue
        try:
            ua = UserSandboxAchievement(
                user=user_id,
                achievement=achievement,
                earned_at=datetime.utcnow(),
                code_sample=code[:500],
            ).save()
            # Acumular puntos bonus en el usuario
            if achievement.points_bonus > 0 and user:
                user.update(inc__total_points=achievement.points_bonus)
            new_unlocked.append(_serialize_user_achievement(ua))
        except NotUniqueError:
            # Race condition — ya existía, ignorar
            pass

    return new_unlocked


# ── Student endpoint ───────────────────────────────────────────────────────────

def get_user_achievements(user_id: str) -> dict:
    earned = _user_achievements.get_for_user(user_id)
    all_active = _achievements.get_active()
    earned_ids = {str(ua.achievement.id) for ua in earned}

    return {
        "earned": [_serialize_user_achievement(ua) for ua in earned],
        "locked": [
            {
                "id": str(a.id),
                "icon": "❓",
                "name": "???",
                "description": "Logro oculto. ¡Sigue explorando!",
                "points_bonus": a.points_bonus,
            }
            for a in all_active if str(a.id) not in earned_ids
        ],
        "total": len(all_active),
        "earned_count": len(earned),
    }