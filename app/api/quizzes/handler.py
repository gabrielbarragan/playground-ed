from app.api.quizzes import process


class QuizHandler:

    # ── CRUD admin ────────────────────────────────────────────
    @staticmethod
    def create(title, description, course_ids, passing_score,
               points_on_complete, points_on_pass, show_correct_answers,
               use_random_bank=False, questions_to_show=0) -> dict:
        return process.create_quiz(
            title=title, description=description, course_ids=course_ids,
            passing_score=passing_score, points_on_complete=points_on_complete,
            points_on_pass=points_on_pass, show_correct_answers=show_correct_answers,
            use_random_bank=use_random_bank, questions_to_show=questions_to_show,
        )

    @staticmethod
    def list_all(include_inactive: bool = False) -> dict:
        return process.list_quizzes(include_inactive=include_inactive)

    @staticmethod
    def get(quiz_id: str) -> dict:
        return process.get_quiz(quiz_id)

    @staticmethod
    def update(quiz_id: str, fields: dict) -> dict:
        return process.update_quiz(quiz_id, fields)

    @staticmethod
    def toggle(quiz_id: str) -> dict:
        return process.toggle_quiz(quiz_id)

    # ── Preguntas ─────────────────────────────────────────────
    @staticmethod
    def add_question(quiz_id, text, code_block, code_language,
                     options, correct_option_index, explanation) -> dict:
        return process.add_question(
            quiz_id=quiz_id, text=text, code_block=code_block,
            code_language=code_language, options=options,
            correct_option_index=correct_option_index, explanation=explanation,
        )

    @staticmethod
    def update_question(quiz_id, index, text, code_block, code_language,
                        options, correct_option_index, explanation) -> dict:
        return process.update_question(
            quiz_id=quiz_id, index=index, text=text, code_block=code_block,
            code_language=code_language, options=options,
            correct_option_index=correct_option_index, explanation=explanation,
        )

    @staticmethod
    def remove_question(quiz_id: str, index: int) -> dict:
        return process.remove_question(quiz_id, index)

    # ── Resultados admin ──────────────────────────────────────
    @staticmethod
    def get_results(quiz_id: str) -> dict:
        return process.get_quiz_results(quiz_id)

    @staticmethod
    def reset_attempt(quiz_id: str, user_id: str) -> dict:
        return process.reset_attempt(quiz_id, user_id)

    # ── Student-facing ────────────────────────────────────────
    @staticmethod
    def list_for_user(user_id: str) -> dict:
        return process.list_quizzes_for_user(user_id)

    @staticmethod
    def get_for_user(quiz_id: str, user_id: str) -> dict:
        return process.get_quiz_for_user(quiz_id, user_id)

    @staticmethod
    def get_my_result(quiz_id: str, user_id: str) -> dict:
        return process.get_my_result(quiz_id, user_id)

    @staticmethod
    def submit(quiz_id: str, user_id: str, answers: list[int]) -> dict:
        return process.submit_quiz(quiz_id, user_id, answers)