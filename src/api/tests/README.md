# CigarLog API Tests

## Running the tests

```bash
cd src/api
pip install -e ".[dev]"
pytest tests/
```

## Test categories

| File | Coverage |
|------|----------|
| `test_health.py` | `/healthz` and `/readyz` liveness and readiness probes |
| `test_me.py` | `GET /v1/me` and `PATCH /v1/me` with auth and validation |
| `test_auth.py` | `verify_token` unit tests with mocked JWKS |

## Integration tests

Tests marked `@pytest.mark.integration` require a live PostgreSQL instance.
Set `DATABASE_URL` before running:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db \
  pytest tests/ -m integration
```

## Fixtures (conftest.py)

- `app`: FastAPI application with `get_current_user` overridden to return a fixed mock user.
- `client`: `httpx.AsyncClient` wired via `ASGITransport` (no network).
- `mock_token`: placeholder bearer token string.
- `auth_headers`: dict with `Authorization: Bearer ...` header.
- `mock_user`: a `MagicMock` shaped like an `AppUser` with deterministic test values.
