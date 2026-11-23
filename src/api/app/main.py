from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.config import settings
from app.db.session import engine
from app.routers import health, me


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: nothing to do (engine is created on import)
    yield
    # Shutdown: dispose the engine connection pool
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="CigarLog API",
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.include_router(health.router)
    app.include_router(me.router)

    return app


app = create_app()
