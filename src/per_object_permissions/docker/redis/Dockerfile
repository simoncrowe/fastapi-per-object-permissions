FROM python:3.11-slim

WORKDIR /code

COPY poetry.lock pyproject.toml /code/
RUN pip install poetry==1.2.0 && \
    poetry config virtualenvs.create false && \
    poetry install --only main,redis

COPY src/ /code/
COPY src/per_object_permissions/docker/redis/env /code/.env

CMD ["uvicorn", "per_object_permissions.api.main:app", "--host", "0.0.0.0", "--port", "8008"]
