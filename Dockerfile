FROM python:3.13.3-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME=/usr/local/poetry \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y curl git

ENV POETRY_HOME=/usr/local/poetry
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH=$POETRY_HOME/bin:$PATH

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-ansi

COPY . .

CMD ["sh", "docker-entrypoint.sh"]