FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install to /usr/local/bin (world-readable) rather than leaving the
# binaries under /root/.local/bin: /root is mode 700, so a non-root user
# (added below, TD-14) would not be able to reach them there.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /root/.local/bin/uvx /usr/local/bin/
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY apps ./apps
COPY packages ./packages
COPY migrations ./migrations
COPY alembic.ini ./
COPY plugins ./plugins

RUN uv sync --frozen

RUN mkdir -p /data

# Run as a dedicated non-root user (TD-14): nothing the application does
# (serving HTTP, running migrations, talking to Docker/Proxmox over their
# respective client libraries) requires root inside the container. /app
# (source + venv) and /data (the SQLite volume) are owned by this user so
# both build-time-installed code and the runtime-writable database work
# without permission errors.
RUN groupadd --system starcore \
    && useradd --system --gid starcore --home-dir /app --shell /usr/sbin/nologin starcore \
    && chown -R starcore:starcore /app /data
ENV HOME=/app
USER starcore

VOLUME ["/data"]

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn core.main:app --host 0.0.0.0 --port 8000"]
