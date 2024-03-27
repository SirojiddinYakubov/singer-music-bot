FROM python:3.11-slim-bullseye
LABEL maintainer="Sirojiddin Yakubov <yakubov9791999@gmail.com>" \
      description="Singer Music Bot"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Poetry
RUN apt clean && apt update && apt install curl netcat vim -y
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* /

RUN poetry install

WORKDIR /aiogram_bot
COPY . /aiogram_bot/

ENTRYPOINT ["/bin/bash", "-c", "alembic upgrade head && python run.py"]