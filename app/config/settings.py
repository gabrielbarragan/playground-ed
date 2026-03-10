from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect, disconnect_all

from app.config import routers
from app.core.constants import MONGO_URI
import app.models  # noqa: F401 — registra todos los Documents antes de cualquier query

API_VERSION = "v2026.02"


def connect_db() -> None:
    """

    :return: connect mongodb
    """
    connect(
        host=MONGO_URI
    )


async def close_db():
    disconnect_all()


def seed_initial_data() -> None:
    from app.api.badges.handler import BadgeHandler
    BadgeHandler.seed_badges()

connect(
        host=MONGO_URI
)


app = FastAPI(
    title="Ofline playgound api",
    description="Service to implement an offline playground",
    version=API_VERSION,
    redoc_url="/api/v1/redoc",
    docs_url='/api/v1/docs',
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    routers.urls
)

app.add_event_handler(
    "startup",
    connect_db
)

app.add_event_handler(
    "startup",
    seed_initial_data
)


app.add_event_handler(
    "shutdown",
    close_db
)

