# ── Herramienta uv (versión fija para builds reproducibles) ───────────────────
FROM ghcr.io/astral-sh/uv:0.12.24 AS uv

# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.14-slim AS builder

COPY --from=uv /uv /uvx /usr/local/bin/

# Usar el Python de la imagen: el mismo que existe en la etapa final
ENV UV_PYTHON_DOWNLOADS=0 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Copiar archivos de dependencias primero (mejor aprovechamiento del caché)
COPY pyproject.toml uv.lock ./

# Instalar dependencias en un venv aislado (sin dependencias de desarrollo)
RUN uv sync --frozen --no-dev --no-install-project

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.14-slim AS runtime

WORKDIR /app

# Usuario sin privilegios para ejecutar la API
RUN groupadd --system app && useradd --system --gid app --no-create-home app

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

USER app

EXPOSE 8000

# Aplicar migraciones y levantar el servidor (PORT permite cambiar el puerto)
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]