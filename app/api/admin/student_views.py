from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_admin, UserContext
from app.api.admin import student_profile as sp

router = APIRouter(prefix="/api/v1/admin/users", tags=["Admin - Student Profile"])


@router.get("/{user_id}/profile-summary")
async def get_profile_summary(
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    try:
        return sp.get_profile_summary(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/challenges")
async def get_student_challenges(
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    try:
        return sp.get_student_challenges(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/quizzes")
async def get_student_quizzes(
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    try:
        return sp.get_student_quizzes(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/attempts")
async def get_student_attempts(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    _: UserContext = Depends(get_current_admin),
):
    try:
        return sp.get_student_attempts(user_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/snippets")
async def get_student_snippets(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=50),
    _: UserContext = Depends(get_current_admin),
):
    try:
        return sp.get_student_snippets(user_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/achievements")
async def get_student_achievements(
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    try:
        return sp.get_student_achievements(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{user_id}/points-breakdown")
async def get_points_breakdown(
    user_id: str,
    _: UserContext = Depends(get_current_admin),
):
    try:
        return sp.get_points_breakdown_by_day(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
