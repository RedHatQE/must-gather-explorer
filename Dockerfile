FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY README.md pyproject.toml uv.lock entrypoint.sh /app/
COPY scripts /app/scripts/
COPY must_gather_explorer /app/must_gather_explorer/
WORKDIR /app
RUN uv sync --frozen
ENTRYPOINT [ "./entrypoint.sh" ]
