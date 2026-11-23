# ── builder stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN pip install --upgrade pip

COPY pyproject.toml ./
# Install only runtime deps (no dev extras)
RUN pip install --no-cache-dir --prefix=/install .

# ── final stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/

# Non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
