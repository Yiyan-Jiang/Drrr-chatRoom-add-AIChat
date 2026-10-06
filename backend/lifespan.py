from contextlib import asynccontextmanager

from fastapi import FastAPI

from normal_system.bootstrap import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
