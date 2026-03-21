from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.user import User


class UserQueryset(BaseQueryset):
    model = User

    def get_by_email(self, email: str) -> Optional[User]:
        return self.model.objects(email=email).first()

    def get_active_by_email(self, email: str) -> Optional[User]:
        return self.model.objects(email=email, is_active=True).first()

    def get_active_by_id(self, user_id: str) -> Optional[User]:
        return self.model.objects(id=user_id, is_active=True).first()

    def get_by_course(self, course):
        return self.model.objects(course=course, is_active=True)

    def get_ranking_by_course(self, course, limit: int = 20):
        return self.model.objects(course=course, is_active=True).order_by("-total_points").limit(limit)

    def add_points(self, user: User, points: int) -> User:
        user.total_points += points
        user.save()
        return user

    # ── Password reset ──────────────────────────────────────

    def set_reset_token(self, user: User, token_hash: str) -> None:
        user.reset_token_hash = token_hash
        user.save()

    def clear_reset_token(self, user: User) -> None:
        user.reset_token_hash = None
        user.save()

    def update_password(self, user: User, new_hash: str) -> None:
        user.password_hash = new_hash
        user.reset_token_hash = None
        user.save()

    def get_by_reset_token_hash(self, token_hash: str) -> Optional[User]:
        return self.model.objects(reset_token_hash=token_hash, is_active=True).first()

    # ── Email change ────────────────────────────────────────

    def set_pending_email(self, user: User, new_email: str, token_hash: str) -> None:
        user.pending_email = new_email
        user.email_change_token_hash = token_hash
        user.save()

    def confirm_email_change(self, user: User) -> None:
        user.email = user.pending_email
        user.pending_email = None
        user.email_change_token_hash = None
        user.save()

    def get_by_email_change_token_hash(self, token_hash: str) -> Optional[User]:
        return self.model.objects(email_change_token_hash=token_hash, is_active=True).first()