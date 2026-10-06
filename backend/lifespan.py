from contextlib import asynccontextmanager

from fastapi import FastAPI

from common.normal_database import engine
from normal_system.bootstrap import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await init_db()
        yield
    finally:
        await engine.dispose()
