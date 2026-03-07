from typing import Optional

from app.api.courses.querysets import CourseQueryset

_courses = CourseQueryset()


def _serialize(course) -> dict:
    return {
        "id": str(course.id),
        "name": course.name,
        "code": course.code,
        "description": course.description,
        "is_active": course.is_active,
        "created_at": course.created_at.isoformat(),
    }


def list_active() -> list:
    return [_serialize(c) for c in _courses.get_active()]


def get_by_id(course_id: str) -> Optional[dict]:
    course = _courses.get_by_id(course_id)
    return _serialize(course) if course else None


def create(name: str, code: str, description: str) -> dict:
    if _courses.get_by_code(code):
        raise ValueError(f"Ya existe un curso con el código '{code.upper()}'")

    course = _courses.create(name=name, code=code.upper(), description=description)
    return _serialize(course)


def toggle_active(course_id: str) -> dict:
    course = _courses.get_by_id(course_id)
    if not course:
        raise ValueError("Curso no encontrado")
    _courses.update(course, is_active=not course.is_active)
    return _serialize(course)