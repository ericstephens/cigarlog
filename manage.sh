#!/usr/bin/env bash
# manage.sh — local dev helper for cigarlog
# Runs postgres + OIDC in containers; api and ui run directly on the host.
set -euo pipefail

COMPOSE="podman-compose -f podman-compose.yml"
DB_URL="postgresql://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db"

cmd="${1:-help}"
shift || true

case "$cmd" in

  # ── Infrastructure ──────────────────────────────────────────────────────────
  up)
    echo "Starting postgres and OIDC containers..."
    $COMPOSE up -d postgres oidc
    echo ""
    echo "  Postgres : localhost:5432"
    echo "  OIDC     : http://localhost:8080/local"
    echo ""
    echo "Next: ./manage.sh migrate  then  ./manage.sh api  (separate terminal)"
    ;;

  down)
    $COMPOSE down
    ;;

  # ── Setup ───────────────────────────────────────────────────────────────────
  install)
    echo "--- API (pip) ---"
    cd src/api
    pip install -e ".[dev]"
    cd ../..
    echo "--- DB (pip) ---"
    cd src/db
    pip install -r requirements.txt
    cd ../..
    echo "--- UI (npm) ---"
    cd src/ui
    npm install
    cd ../..
    echo "Done."
    ;;

  migrate)
    echo "Applying Alembic migrations..."
    cd src/db
    alembic upgrade head
    ;;

  # ── Dev servers (each in its own terminal) ──────────────────────────────────
  api)
    cd src/api
    DATABASE_URL="postgresql+asyncpg://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db" \
    OIDC_ISSUER="http://localhost:8080/local" \
    JWT_AUDIENCE="cigarlog" \
    uvicorn app.main:app --reload --port 8000
    ;;

  ui)
    cd src/ui
    VITE_OIDC_AUTHORITY="http://localhost:8080/local" \
    VITE_OIDC_CLIENT_ID="cigarlog" \
    VITE_API_BASE_URL="http://localhost:8000" \
    npm run dev
    ;;

  # ── User management ─────────────────────────────────────────────────────────
  promote)
    EMAIL="${1:-}"
    if [[ -z "$EMAIL" ]]; then
      echo "Usage: ./manage.sh promote <email>" >&2
      exit 1
    fi
    echo "Promoting $EMAIL to admin..."
    psql "$DB_URL" -c "UPDATE app_user SET role = 'admin' WHERE email = lower('${EMAIL}');"
    psql "$DB_URL" -c "SELECT id, email, display_name, role, trusted, created_at FROM app_user WHERE email = lower('${EMAIL}');"
    ;;

  users)
    psql "$DB_URL" -c "SELECT id, email, display_name, role, trusted, created_at FROM app_user ORDER BY created_at;"
    ;;

  # ── Help ────────────────────────────────────────────────────────────────────
  help|*)
    cat <<'EOF'
Usage: ./manage.sh <command>

Setup (one-time):
  install             Install Python and npm dependencies
  up                  Start postgres and OIDC containers
  migrate             Apply Alembic migrations

Dev servers (each in its own terminal):
  api                 Run FastAPI on :8000  (reload on save)
  ui                  Run Vite on :5173     (reload on save)

User management:
  promote <email>     Set a user's role to 'admin'
  users               List all registered users

Infra:
  down                Stop all containers

Workflow for first run:
  1. ./manage.sh install
  2. ./manage.sh up
  3. ./manage.sh migrate
  4. ./manage.sh api          # terminal 2
  5. ./manage.sh ui           # terminal 3
  6. Open http://localhost:5173 and sign in
     (mock OIDC: enter any subject/email, click Sign in)
  7. ./manage.sh promote <your-email>
EOF
    ;;

esac
