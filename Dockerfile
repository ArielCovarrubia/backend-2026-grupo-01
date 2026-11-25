# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

# Instalar uv (gestor de paquetes ultrarrápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copiar archivos de dependencias primero (mejor aprovechamiento del caché)
COPY pyproject.toml uv.lock ./

# Instalar dependencias en un venv aislado (sin dev deps)
RUN uv sync --frozen --no-dev --no-install-project

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

WORKDIR /app

# Copiar el venv instalado desde el stage anterior
COPY --from=builder /app/.venv /app/.venv

# Copiar código fuente y configuración de migraciones
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Usar el Python del venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Ejecutar migraciones y luego levantar el servidor
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
