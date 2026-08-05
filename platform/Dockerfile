FROM python:3.12-slim AS builder

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

# --no-dev: bandit/pre-commit (the `dependency-groups.dev` group, distinct
# from the pytest/ruff/pyright/mkdocs/hypothesis `optional-dependencies`
# "dev" extra, which was never requested here) have no purpose in a
# running container and uv installs default dependency-groups unless
# told not to.
RUN uv sync --frozen --no-dev


FROM python:3.12-slim AS runtime

# ca-certificates is a genuine runtime dependency (outbound HTTPS to the
# Proxmox API, Anthropic API, cloud metadata probes); curl itself is not
# needed here -- it was only ever needed to fetch the uv installer, which
# already ran in the builder stage. Multi-stage keeps curl and apt's
# package cache/lists out of the image STARCORE actually runs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /usr/local/bin/uvx /usr/local/bin/uvx
COPY --from=builder /app /app
ENV PATH="/usr/local/bin:${PATH}"

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

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["sh", "-c", "uv run --no-sync alembic upgrade head && uv run --no-sync uvicorn core.main:app --host 0.0.0.0 --port 8000"]
