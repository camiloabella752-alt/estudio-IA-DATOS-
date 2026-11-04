# Etapa 1: construir el entorno con las dependencias
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev

# Etapa 2: imagen final, solo lo necesario para correr
FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home appuser
COPY --from=builder --chown=appuser:appuser /app /app
RUN chown appuser:appuser /app
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8000
CMD ["uvicorn", "estudio_ia_datos.api:app", "--host", "0.0.0.0", "--port", "8000"]