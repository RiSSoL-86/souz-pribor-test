FROM ghcr.io/astral-sh/uv:0.11.30 AS uv

FROM python:3.14.6-slim

COPY --from=uv /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PORT=8000

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY src ./

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn django_project.asgi:application --host 0.0.0.0 --port \"$PORT\" --reload --reload-dir /app"]
