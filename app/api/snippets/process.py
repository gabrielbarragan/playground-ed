from datetime import datetime
from typing import Optional

from app.api.snippets.querysets import SnippetQueryset
from app.api.users.querysets import UserQueryset

_snippets = SnippetQueryset()
_users = UserQueryset()


def _serialize(snippet) -> dict:
    return {
        "id": str(snippet.id),
        "title": snippet.title,
        "code": snippet.code,
        "language": snippet.language,
        "tags": snippet.tags,
        "is_public": snippet.is_public,
        "created_at": snippet.created_at.isoformat(),
        "updated_at": snippet.updated_at.isoformat(),
    }


def list_by_user(user_id: str) -> list:
    user = _users.get_active_by_id(user_id)
    if not user:
        return []
    return [_serialize(s) for s in _snippets.get_by_user(user)]


def get_by_id(snippet_id: str, user_id: str) -> Optional[dict]:
    user = _users.get_active_by_id(user_id)
    if not user:
        return None
    snippet = _snippets.get_by_id_and_user(snippet_id, user)
    return _serialize(snippet) if snippet else None


def save(user_id: str, title: str, code: str, language: str, tags: list) -> dict:
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    snippet = _snippets.create(
        user=user,
        title=title,
        code=code,
        language=language,
        tags=tags,
    )
    return _serialize(snippet)


def update(snippet_id: str, user_id: str, title: str, code: str, tags: list) -> dict:
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    snippet = _snippets.get_by_id_and_user(snippet_id, user)
    if not snippet:
        raise ValueError("Snippet no encontrado")

    _snippets.update(snippet, title=title, code=code, tags=tags, updated_at=datetime.utcnow())
    return _serialize(snippet)


def remove(snippet_id: str, user_id: str) -> None:
    user = _users.get_active_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    snippet = _snippets.get_by_id_and_user(snippet_id, user)
    if not snippet:
        raise ValueError("Snippet no encontrado")

    _snippets.delete(snippet)