FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y make curl unzip time

RUN pip install uv==0.5.30

COPY uv.lock .
COPY pyproject.toml .

RUN uv sync --locked --no-install-project
# Ensure installed CLI tools (e.g., sqlmesh) are on PATH
ENV PATH="/app/.venv/bin:${PATH}"

COPY Makefile .
#CMD ["make", "run"]
