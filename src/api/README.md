# CigarLog API

FastAPI backend for the CigarLog application.

## Quick start

```bash
cd src/api
pip install -e .
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db` | Async PostgreSQL connection string |
| `OIDC_ISSUER` | `http://localhost:8080/local` | OIDC provider issuer URL (used to fetch JWKS and verify `iss` claim) |
| `JWT_AUDIENCE` | `cigarlog` | Expected `aud` claim in JWTs |
| `DEBUG` | `false` | Enable SQLAlchemy echo and FastAPI debug mode |

Create a `.env` file in `src/api/` to override defaults locally.

## Running tests

```bash
cd src/api
pip install -e ".[dev]"
pytest tests/
```

Skip integration tests (which need a live DB):

```bash
pytest tests/ -m "not integration"
```

## Auth flow

1. The browser authenticates with the OIDC provider (authorization code + PKCE) and receives a JWT access token.
2. Every API request includes the token as `Authorization: Bearer <token>`.
3. The API fetches the provider's JWKS from `{OIDC_ISSUER}/.well-known/jwks.json` (cached for 5 minutes) and verifies the token's signature, issuer, audience, and expiry.
4. On first sight of an `idp_subject` (`sub` claim), the API upserts a row in `app_user` — no separate registration step is required.
5. The resolved `app_user.id` and `app_user.role` are set as Postgres session-local variables (`app.current_user_id`, `app.current_role`) so row-level security policies apply to every statement in the transaction.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Liveness probe — always 200 |
| `GET` | `/readyz` | Readiness probe — checks DB connection |
| `GET` | `/v1/me` | Return current user profile |
| `PATCH` | `/v1/me` | Update `display_name`, `unit_system`, `timezone` |

## Container

Build with Podman:

```bash
podman build -t cigarlog-api src/api/
podman run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e OIDC_ISSUER=https://your-idp.example.com \
  -e JWT_AUDIENCE=cigarlog \
  cigarlog-api
```
