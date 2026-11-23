from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict:
    """Liveness probe — always returns 200."""
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
    """Readiness probe — checks DB connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(exc)},
        )
