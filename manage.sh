#!/usr/bin/env bash
# manage.sh — dev + infra helper for cigarlog
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="podman-compose -f $REPO_ROOT/podman-compose.yml"
INFRA_DIR="$REPO_ROOT/src/infra"
DB_DIR="$REPO_ROOT/src/db"
API_DIR="$REPO_ROOT/src/api"
UI_DIR="$REPO_ROOT/src/ui"
DB_URL="postgresql://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db"

cmd="${1:-help}"
shift || true

# ── Helpers ──────────────────────────────────────────────────────────────────

_require_tofu() {
  if ! command -v tofu &>/dev/null; then
    echo "Error: 'tofu' (OpenTofu) not found in PATH" >&2
    exit 1
  fi
}

_require_psql() {
  if ! command -v psql &>/dev/null; then
    echo "Error: 'psql' not found in PATH" >&2
    exit 1
  fi
}

_tofu_output() {
  cd "$INFRA_DIR"
  tofu output -raw "$1" 2>/dev/null || echo ""
}

_env_file() {
  # Writes .env files for api and ui from tofu outputs (Cognito mode)
  local issuer client_id
  issuer=$(_tofu_output cognito_issuer)
  client_id=$(_tofu_output cognito_client_id)

  if [[ -z "$issuer" || -z "$client_id" ]]; then
    echo "Error: tofu outputs not available. Run './manage.sh infra:apply' first." >&2
    exit 1
  fi

  cat > "$API_DIR/.env" <<EOF
DATABASE_URL=postgresql+asyncpg://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db
OIDC_ISSUER=$issuer
JWT_AUDIENCE=$client_id
DEBUG=false
EOF

  cat > "$UI_DIR/.env.local" <<EOF
VITE_OIDC_AUTHORITY=$issuer
VITE_OIDC_CLIENT_ID=$client_id
VITE_API_BASE_URL=http://localhost:8000
EOF

  echo "Wrote $API_DIR/.env"
  echo "Wrote $UI_DIR/.env.local"
}

# ── Commands ─────────────────────────────────────────────────────────────────

case "$cmd" in

  # ── First-time setup ────────────────────────────────────────────────────────
  install)
    echo "=== API (pip) ==="
    cd "$API_DIR" && pip install -e ".[dev]"
    echo "=== DB (pip) ==="
    cd "$DB_DIR" && pip install -r requirements.txt
    echo "=== UI (npm) ==="
    cd "$UI_DIR" && npm install
    echo ""
    echo "Done. Next: ./manage.sh up && ./manage.sh migrate"
    ;;

  # ── Local containers ────────────────────────────────────────────────────────
  up)
    echo "Starting postgres and mock OIDC..."
    $COMPOSE up -d postgres oidc
    echo ""
    echo "  Postgres  : localhost:5432  (db: cigarlog_db)"
    echo "  Mock OIDC : http://localhost:8080/local"
    echo ""
    echo "Next: ./manage.sh migrate"
    ;;

  down)
    $COMPOSE down
    ;;

  logs)
    SERVICE="${1:-}"
    if [[ -n "$SERVICE" ]]; then
      $COMPOSE logs -f "$SERVICE"
    else
      $COMPOSE logs -f
    fi
    ;;

  ps)
    $COMPOSE ps
    ;;

  # ── Database ────────────────────────────────────────────────────────────────
  migrate)
    echo "Applying Alembic migrations..."
    cd "$DB_DIR"
    alembic upgrade head
    echo "Done."
    ;;

  migrate:down)
    STEPS="${1:-1}"
    echo "Rolling back $STEPS migration(s)..."
    cd "$DB_DIR"
    alembic downgrade "-$STEPS"
    ;;

  migrate:status)
    cd "$DB_DIR" && alembic current
    ;;

  # ── Dev servers ─────────────────────────────────────────────────────────────
  api)
    # Uses mock OIDC by default; override by setting OIDC_ISSUER + JWT_AUDIENCE
    cd "$API_DIR"
    DATABASE_URL="postgresql+asyncpg://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db" \
    OIDC_ISSUER="${OIDC_ISSUER:-http://localhost:8080/local}" \
    JWT_AUDIENCE="${JWT_AUDIENCE:-cigarlog}" \
    DEBUG="${DEBUG:-true}" \
    uvicorn app.main:app --reload --port 8000
    ;;

  ui)
    # Uses mock OIDC by default; .env.local overrides for Cognito
    cd "$UI_DIR"
    VITE_OIDC_AUTHORITY="${VITE_OIDC_AUTHORITY:-http://localhost:8080/local}" \
    VITE_OIDC_CLIENT_ID="${VITE_OIDC_CLIENT_ID:-cigarlog}" \
    VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://localhost:8000}" \
    npm run dev
    ;;

  # ── Tests ───────────────────────────────────────────────────────────────────
  test:db)
    cd "$DB_DIR" && pytest tests/ "${@}"
    ;;

  test:api)
    cd "$API_DIR" && pytest tests/ "${@}"
    ;;

  test:ui)
    cd "$UI_DIR" && npm test "${@}"
    ;;

  test:infra)
    bash "$INFRA_DIR/tests/validate_test.sh"
    ;;

  test)
    echo "=== infra ===" && bash "$INFRA_DIR/tests/validate_test.sh"
    echo "=== db ===" && (cd "$DB_DIR" && pytest tests/ -x)
    echo "=== api ===" && (cd "$API_DIR" && pytest tests/ -x)
    echo "=== ui ===" && (cd "$UI_DIR" && npm test)
    echo ""
    echo "All tests passed."
    ;;

  # ── Infrastructure (OpenTofu / real AWS) ────────────────────────────────────
  infra:init)
    _require_tofu
    cd "$INFRA_DIR" && tofu init
    ;;

  infra:plan)
    _require_tofu
    cd "$INFRA_DIR" && tofu plan "${@}"
    ;;

  infra:apply)
    _require_tofu
    cd "$INFRA_DIR"
    tofu apply "${@}"
    echo ""
    echo "Writing .env files from tofu outputs..."
    cd "$REPO_ROOT" && _env_file
    echo ""
    echo "Restart './manage.sh api' and './manage.sh ui' to pick up Cognito settings."
    ;;

  infra:destroy)
    _require_tofu
    echo "WARNING: this will destroy all AWS resources for cigarlog."
    read -r -p "Type 'yes' to confirm: " confirm
    if [[ "$confirm" != "yes" ]]; then
      echo "Aborted."
      exit 0
    fi
    cd "$INFRA_DIR" && tofu destroy "${@}"
    ;;

  infra:outputs)
    _require_tofu
    cd "$INFRA_DIR" && tofu output
    ;;

  infra:env)
    # Write .env / .env.local from current tofu outputs without re-applying
    _env_file
    ;;

  # ── User management ─────────────────────────────────────────────────────────
  users)
    _require_psql
    psql "$DB_URL" -c \
      "SELECT id, email, display_name, role, trusted, created_at FROM app_user ORDER BY created_at;"
    ;;

  promote)
    EMAIL="${1:-}"
    if [[ -z "$EMAIL" ]]; then
      echo "Usage: ./manage.sh promote <email>" >&2
      exit 1
    fi
    _require_psql
    echo "Promoting $EMAIL to admin..."
    psql "$DB_URL" -c \
      "UPDATE app_user SET role = 'admin', trusted = true WHERE email = lower('${EMAIL}');"
    psql "$DB_URL" -c \
      "SELECT id, email, display_name, role, trusted FROM app_user WHERE email = lower('${EMAIL}');"
    ;;

  demote)
    EMAIL="${1:-}"
    if [[ -z "$EMAIL" ]]; then
      echo "Usage: ./manage.sh demote <email>" >&2
      exit 1
    fi
    _require_psql
    psql "$DB_URL" -c \
      "UPDATE app_user SET role = 'member', trusted = false WHERE email = lower('${EMAIL}');"
    psql "$DB_URL" -c \
      "SELECT id, email, display_name, role, trusted FROM app_user WHERE email = lower('${EMAIL}');"
    ;;

  curator)
    EMAIL="${1:-}"
    if [[ -z "$EMAIL" ]]; then
      echo "Usage: ./manage.sh curator <email>" >&2
      exit 1
    fi
    _require_psql
    echo "Setting $EMAIL as curator..."
    psql "$DB_URL" -c \
      "UPDATE app_user SET role = 'curator', trusted = true WHERE email = lower('${EMAIL}');"
    psql "$DB_URL" -c \
      "SELECT id, email, display_name, role, trusted FROM app_user WHERE email = lower('${EMAIL}');"
    ;;

  # ── Help ────────────────────────────────────────────────────────────────────
  help|*)
    cat <<'EOF'
Usage: ./manage.sh <command> [args]

── First-time setup ──────────────────────────────────────────────────────────
  install               Install Python (pip) and Node (npm) dependencies

── Local dev (mock OIDC) ─────────────────────────────────────────────────────
  up                    Start postgres + mock OIDC containers
  down                  Stop all containers
  logs [service]        Tail container logs (postgres | oidc)
  ps                    Show running containers

  migrate               Apply Alembic migrations (run after 'up')
  migrate:down [n]      Roll back n migrations (default 1)
  migrate:status        Show current migration revision

  api                   Run FastAPI dev server on :8000 (hot reload)
  ui                    Run Vite dev server on :5173 (hot reload)

── Tests ─────────────────────────────────────────────────────────────────────
  test                  Run all test suites
  test:infra            tofu validate
  test:db               pytest src/db/tests/
  test:api              pytest src/api/tests/
  test:ui               vitest run

── Infrastructure (real AWS / OpenTofu) ──────────────────────────────────────
  infra:init            tofu init
  infra:plan [args]     tofu plan
  infra:apply [args]    tofu apply, then write .env files from outputs
  infra:destroy [args]  tofu destroy (prompts for confirmation)
  infra:outputs         Show all tofu outputs
  infra:env             Write .env / .env.local from current tofu outputs
                        (use after apply to switch api + ui to Cognito)

── User management ───────────────────────────────────────────────────────────
  users                 List all registered users
  promote <email>       Set role = admin, trusted = true
  curator <email>       Set role = curator, trusted = true
  demote <email>        Set role = member, trusted = false

── Typical workflows ─────────────────────────────────────────────────────────
  Local dev (mock OIDC):
    1. ./manage.sh install
    2. ./manage.sh up
    3. ./manage.sh migrate
    4. ./manage.sh api          ← terminal 2
    5. ./manage.sh ui           ← terminal 3
    6. Open http://localhost:5173
    7. ./manage.sh promote <your-email>

  Switch to Cognito (needs AWS credentials):
    1. ./manage.sh infra:init
    2. ./manage.sh infra:apply -var="cognito_domain_prefix=cigarlog-yourname"
    3. Restart api + ui terminals (they pick up .env / .env.local automatically)
EOF
    ;;

esac
