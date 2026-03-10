from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.code_snippet import CodeSnippet


class SnippetQueryset(BaseQueryset):
    model = CodeSnippet

    def get_by_user(self, user):
        return self.model.objects(user=user).order_by("-created_at")

    def get_by_id_and_user(self, snippet_id: str, user) -> Optional[CodeSnippet]:
        return self.model.objects(id=snippet_id, user=user).first()