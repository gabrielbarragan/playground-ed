from typing import Optional
from app.api.challenges import process


class ChallengeHandler:

    # ── CRUD ──────────────────────────────────────────────────
    @staticmethod
    def create(
        title, description, difficulty, points,
        course_ids, starter_code, example_input, example_output,
        tags, requires_review,
        optimal_lines_min=None, optimal_lines_max=None, lines_bonus_points=0,
    ) -> dict:
        return process.create_challenge(
            title=title, description=description, difficulty=difficulty,
            points=points, course_ids=course_ids, starter_code=starter_code,
            example_input=example_input, example_output=example_output,
            tags=tags, requires_review=requires_review,
            optimal_lines_min=optimal_lines_min,
            optimal_lines_max=optimal_lines_max,
            lines_bonus_points=lines_bonus_points,
        )

    @staticmethod
    def list_all(include_inactive: bool = False) -> dict:
        return process.list_challenges(include_inactive=include_inactive)

    @staticmethod
    def get(challenge_id: str) -> dict:
        return process.get_challenge(challenge_id)

    @staticmethod
    def update(challenge_id: str, fields: dict) -> dict:
        return process.update_challenge(challenge_id, fields)

    @staticmethod
    def delete(challenge_id: str) -> dict:
        return process.delete_challenge(challenge_id)

    # ── Test cases ────────────────────────────────────────────
    @staticmethod
    def add_test_case(challenge_id, input, expected_output, is_hidden, description) -> dict:
        return process.add_test_case(challenge_id, input, expected_output, is_hidden, description)

    @staticmethod
    def remove_test_case(challenge_id: str, index: int) -> dict:
        return process.remove_test_case(challenge_id, index)

    # ── Manual review ─────────────────────────────────────────
    @staticmethod
    def list_pending(challenge_id: Optional[str] = None) -> dict:
        return process.list_pending_reviews(challenge_id)

    @staticmethod
    def approve(attempt_id: str, reviewer_id: str, feedback: str) -> dict:
        return process.review_submission(attempt_id, reviewer_id, approved=True, feedback=feedback)

    @staticmethod
    def reject(attempt_id: str, reviewer_id: str, feedback: str) -> dict:
        return process.review_submission(attempt_id, reviewer_id, approved=False, feedback=feedback)

    # ── Student-facing ────────────────────────────────────────
    @staticmethod
    def list_for_user(user_id: str) -> dict:
        return process.list_challenges_for_user(user_id)

    @staticmethod
    def get_for_user(challenge_id: str, user_id: str) -> dict:
        return process.get_challenge_for_user(challenge_id, user_id)

    @staticmethod
    def get_my_attempts(challenge_id: str, user_id: str) -> dict:
        return process.get_my_attempts(challenge_id, user_id)

    @staticmethod
    def get_my_progress(user_id: str) -> dict:
        return process.get_my_progress(user_id)

    @staticmethod
    async def submit(challenge_id: str, user_id: str, code: str) -> dict:
        return await process.submit_challenge(challenge_id, user_id, code)