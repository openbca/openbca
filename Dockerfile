FROM python:3.11-slim

ARG DUCKDB_VERSION=1.2.2
ARG DUCKDB_ARCH=aarch64

WORKDIR /app

RUN apt-get update && apt-get install -y make curl unzip time \
    && curl -L -o duckdb_cli.zip "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/duckdb_cli-linux-${DUCKDB_ARCH}.zip" \
    && ln -s /app/duckdb /usr/local/bin/duckdb && unzip duckdb_cli.zip && rm duckdb_cli.zip

RUN pip install uv==0.5.30

COPY uv.lock .
COPY pyproject.toml .

RUN uv sync --locked --no-install-project
# Ensure installed CLI tools (e.g., sqlmesh) are on PATH
ENV PATH="/app/.venv/bin:${PATH}"

COPY Makefile .
#CMD ["make", "run"]
