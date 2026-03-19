# config/routers.py
from fastapi import APIRouter

from app.api.meta import views as meta
from app.api.v1 import views as api_v1
from app.api.users import views as users
from app.api.courses import views as courses
from app.api.snippets import views as snippets
from app.api.dashboard import views as dashboard
from app.api.admin import views as admin
from app.api.superadmin import views as superadmin
from app.api.badges import views as badges
from app.api.challenges import views as challenges
from app.api.quizzes import views as quizzes
from app.api.sandbox_achievements import views as sandbox_achievements

urls = APIRouter()

urls.include_router(meta.router)
urls.include_router(api_v1.router)
urls.include_router(users.router)
urls.include_router(users.users_router)
urls.include_router(courses.router)
urls.include_router(snippets.router)
urls.include_router(dashboard.router)
urls.include_router(admin.router)
urls.include_router(superadmin.router)
urls.include_router(badges.router)
urls.include_router(challenges.router)
urls.include_router(challenges.submissions_router)
urls.include_router(challenges.student_router)
urls.include_router(quizzes.admin_router)
urls.include_router(quizzes.student_router)
urls.include_router(sandbox_achievements.admin_router)
urls.include_router(sandbox_achievements.student_router)