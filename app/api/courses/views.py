from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.courses.handler import CourseHandler
from app.api.courses.serializer import CourseInSerializer

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


@router.get("/")
async def list_courses():
    return CourseHandler.list_active()


@router.get("/{course_id}")
async def get_course(course_id: str):
    course = CourseHandler.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    return course


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_course(body: CourseInSerializer):
    try:
        course = CourseHandler.create(
            name=body.name,
            code=body.code,
            description=body.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=course)


@router.patch("/{course_id}/toggle")
async def toggle_course(course_id: str):
    try:
        course = CourseHandler.toggle_active(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return course