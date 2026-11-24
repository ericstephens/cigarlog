from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import verify_token
from app.auth.middleware import set_transaction_identity
from app.db.models import AppUser
from app.db.session import AsyncSessionLocal

_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AppUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    claims = verify_token(credentials.credentials)

    sub: str = (
        claims.get("sub", "")
        or claims.get("preferred_username", "")
        or claims.get("email", "")
    )
    email: str = claims.get("email", "")
    name: str = claims.get("name", "") or claims.get("preferred_username", "")
    if not sub:
        raise HTTPException(status_code=401, detail="Token missing sub claim")

    display_name = name or (email.split("@")[0] if email else sub)
    now = datetime.now(timezone.utc)

    # Use raw SQL so enum columns get inline ::type casts rather than
    # bound parameters, which asyncpg cannot implicitly cast to native PG enums.
    #
    # ON CONFLICT (idp_subject) handles the normal "returning user" path.
    # If the email is already claimed by a different idp_subject (e.g. the user
    # previously logged in via mock OIDC and now uses Keycloak), we catch the
    # IntegrityError, roll back, and re-point that row to the new subject so
    # the two sessions merge into one account.
    try:
        await db.execute(
            text("""
                INSERT INTO app_user
                    (id, idp_subject, email, display_name, role, unit_system,
                     timezone, trusted, adult_attested_at, created_at, updated_at)
                VALUES
                    (gen_random_uuid(), :sub, :email, :display_name,
                     'member'::user_role, 'imperial'::unit_system,
                     'UTC', false, :now, :now, :now)
                ON CONFLICT (idp_subject) DO UPDATE SET
                    email      = EXCLUDED.email,
                    updated_at = EXCLUDED.updated_at
            """),
            {"sub": sub, "email": email, "display_name": display_name, "now": now},
        )
        await db.commit()
    except IntegrityError:
        # Email already exists under a different idp_subject — merge by
        # updating that row's subject to the current one.
        await db.rollback()
        await db.execute(
            text("""
                UPDATE app_user
                SET idp_subject = :sub, updated_at = :now
                WHERE email = :email
            """),
            {"sub": sub, "email": email, "now": now},
        )
        await db.commit()

    result = await db.execute(select(AppUser).where(AppUser.idp_subject == sub))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=500, detail="Failed to upsert user")

    # Detach the user from the session before RLS setup.
    # If set_transaction_identity fails and we rollback, a session-attached
    # object would be expired by the rollback and become unusable outside
    # an async greenlet. Detached objects retain their loaded attributes.
    db.expunge(user)

    try:
        await set_transaction_identity(db, str(user.id), user.role)
    except Exception:
        # Don't leave the session in an aborted-transaction state.
        await db.rollback()

    return user
