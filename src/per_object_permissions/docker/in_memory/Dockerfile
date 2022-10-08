FROM python:3.10-slim

WORKDIR /code

COPY poetry.lock pyproject.toml /code/
RUN pip install poetry==1.2.0 && \
    poetry config virtualenvs.create false && \
    poetry install --only main

COPY src/ /code/
COPY src/per_object_permissions/docker/in_memory/env /code/.env

CMD ["uvicorn", "per_object_permissions.api.main:app", "--host", "0.0.0.0", "--port", "8008"]
