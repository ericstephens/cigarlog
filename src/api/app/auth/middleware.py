"""
Middleware helpers to set app.current_user_id and app.current_role
as PostgreSQL session-local variables within each transaction.
These are called from deps.py get_db, not as ASGI middleware, because
they must run inside the SQLAlchemy transaction context.
"""
from sqlalchemy.ext.asyncio import AsyncSession


async def set_transaction_identity(
    session: AsyncSession, user_id: str, role: str
) -> None:
    """
    Set Postgres local variables for row-level security.
    Must be called after BEGIN (i.e., inside an open transaction).

    Uses exec_driver_sql to bypass SQLAlchemy's compiled-query / prepared-
    statement pipeline. asyncpg cannot prepare SET LOCAL statements and raises
    when session.execute(text(...)) is used for them.
    """
    conn = await session.connection()
    await conn.exec_driver_sql(
        f"SET LOCAL \"app.current_user_id\" = '{_safe(user_id)}'"
    )
    await conn.exec_driver_sql(
        f"SET LOCAL \"app.current_role\" = '{_safe(role)}'"
    )


def _safe(value: str) -> str:
    """Remove single quotes from a value used in SET LOCAL."""
    return value.replace("'", "")
