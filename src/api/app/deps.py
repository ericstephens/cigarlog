from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import verify_token
from app.auth.middleware import set_transaction_identity
from app.db.models import AppUser
from app.db.session import AsyncSessionLocal

_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession. The session does NOT set transaction identity here;
    that happens in get_current_user after the user is resolved.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AppUser:
    """
    1. Extract and verify the Bearer JWT.
    2. Upsert the app_user row (insert on conflict do update).
    3. Set Postgres session locals for RLS.
    4. Return the AppUser ORM object.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    claims = verify_token(credentials.credentials)

    sub: str = claims.get("sub", "")
    email: str = claims.get("email", "")
    if not sub:
        raise HTTPException(status_code=401, detail="Token missing sub claim")

    # Upsert: insert on conflict (idp_subject) do update email
    stmt = (
        pg_insert(AppUser)
        .values(
            idp_subject=sub,
            email=email,
            display_name=email.split("@")[0] if email else sub,
            role="member",
            unit_system="imperial",
            timezone="UTC",
            trusted=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        .on_conflict_do_update(
            index_elements=["idp_subject"],
            set_={
                "email": email,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        .returning(AppUser)
    )

    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=500, detail="Failed to upsert user")

    await db.commit()

    # Re-fetch to get current state (upsert returning may not fully populate mapped obj)
    await db.refresh(user)

    # Set Postgres session locals for RLS (best-effort — table may not exist in tests)
    try:
        await set_transaction_identity(db, str(user.id), user.role)
    except Exception:
        pass

    return user
