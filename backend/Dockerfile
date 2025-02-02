FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/ 

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Compile bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project


ENV PYTHONPATH=/app

COPY ./pyproject.toml ./uv.lock /app/

COPY ./app /app/app

RUN mkdir -p data/pdfs

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--port", "8000", "--host", "0.0.0.0"]

HEALTHCHECK --interval=20s --timeout=20s --start-period=5s --retries=3 CMD bash -c 'exec 3<>/dev/tcp/127.0.0.1/8000 && \
echo -e "GET /health HTTP/1.1\r\nhost: 127.0.0.1:8000\r\nConnection: close\r\n\r\n" >&3 && \
cat <&3 | grep "healthy" || exit 1'