from app.api.dashboard import process


class ActivityHandler:
    @staticmethod
    def log_execution(user_id, code: str, success: bool) -> None:
        process.log_execution(user_id, code, success)

    @staticmethod
    def get_user_heatmap(user_id: str) -> dict:
        return process.get_user_heatmap(user_id)

    @staticmethod
    def get_course_users_summary(course_id: str) -> dict:
        return process.get_course_users_summary(course_id)

    @staticmethod
    def get_course_ranking(course_id: str, limit: int = 20) -> dict:
        return process.get_course_ranking(course_id, limit)