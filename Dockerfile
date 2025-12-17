FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libpq-dev \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -U pip setuptools wheel

RUN python3 -m pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org "poetry==${POETRY_VERSION}"
RUN poetry --version

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main --no-ansi

COPY . .
COPY config.py ./
COPY alembic.ini ./

EXPOSE 8000
CMD ["uvicorn", "tprep.app.main:app", "--host", "0.0.0.0", "--port", "8000"]