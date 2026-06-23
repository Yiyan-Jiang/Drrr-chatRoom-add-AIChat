from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from socketio import ASGIApp

from settings import (
    API_PREFIX,
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    CORS_ORIGINS,
    OPENAPI_TAGS,
)
from ai.routers import chat_router, turn_router
from lifespan import lifespan
from normal_system.routers import (
    auth_router,
    gate_router,
    github_router,
    message_router,
    room_router,
    socket_io_server as sio,
    user_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        openapi_tags=OPENAPI_TAGS,
    )
    configure_cors(app)
    include_routers(app)
    return app


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )


def include_routers(app: FastAPI) -> None:
    for router in (
        user_router,
        auth_router,
        room_router,
        message_router,
        chat_router,
        turn_router,
        gate_router,
        github_router,
    ):
        app.include_router(router, prefix=API_PREFIX)


app = create_app()
socketio_app = ASGIApp(sio, other_asgi_app=app)
