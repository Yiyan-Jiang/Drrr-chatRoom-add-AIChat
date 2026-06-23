from contextlib import asynccontextmanager

from fastapi import FastAPI

from ai.database import init_ai_db
from normal_system.bootstrap import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    await init_ai_db()
    yield
