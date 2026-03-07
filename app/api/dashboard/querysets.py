from datetime import datetime
from typing import Optional

from app.core.queryset import BaseQueryset
from app.models.code_activity import CodeActivity


class ActivityQueryset(BaseQueryset):
    model = CodeActivity

    def get_by_user_and_date(self, user, activity_date: datetime) -> Optional[CodeActivity]:
        return self.model.objects(user=user, activity_date=activity_date).first()

    def get_by_user_in_range(self, user, start: datetime, end: datetime):
        return self.model.objects(
            user=user,
            activity_date__gte=start,
            activity_date__lte=end,
        ).order_by("activity_date")

    def get_all_users_in_range(self, start: datetime, end: datetime):
        return self.model.objects(
            activity_date__gte=start,
            activity_date__lte=end,
        )

    def upsert_execution(self, user, activity_date: datetime, success: bool, lines: int) -> CodeActivity:
        activity = self.get_by_user_and_date(user, activity_date)
        if activity:
            activity.executions += 1
            if success:
                activity.successful_executions += 1
            activity.lines_of_code = max(activity.lines_of_code, lines)
            activity.updated_at = datetime.utcnow()
            activity.save()
        else:
            activity = self.model(
                user=user,
                activity_date=activity_date,
                executions=1,
                successful_executions=1 if success else 0,
                lines_of_code=lines,
            ).save()
        return activity