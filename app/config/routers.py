# config/routers.py
from fastapi import APIRouter

from app.api.meta import views as meta
from app.api.v1 import views as api_v1
from app.api.users import views as users
from app.api.courses import views as courses
from app.api.snippets import views as snippets
from app.api.dashboard import views as dashboard

urls = APIRouter()

urls.include_router(meta.router)
urls.include_router(api_v1.router)
urls.include_router(users.router)
urls.include_router(users.users_router)
urls.include_router(courses.router)
urls.include_router(snippets.router)
urls.include_router(dashboard.router)