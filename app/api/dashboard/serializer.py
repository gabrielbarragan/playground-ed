from typing import List
from pydantic import BaseModel


class ActivityDaySchema(BaseModel):
    date: str
    executions: int
    successful_executions: int
    lines_of_code: int


class HeatmapResponseSchema(BaseModel):
    days: List[ActivityDaySchema]
    total_executions: int
    streak_days: int


class RankingEntrySchema(BaseModel):
    rank: int
    id: str
    first_name: str
    last_name: str
    total_points: int


class CourseRankingResponseSchema(BaseModel):
    course: dict
    ranking: List[RankingEntrySchema]