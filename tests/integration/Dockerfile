FROM python:3.10-slim

WORKDIR /tests

COPY poetry.lock pyproject.toml /tests/
RUN pip install poetry==1.2.0 && \
    poetry config virtualenvs.create false && \
    poetry install --only test

COPY tests/ /tests

CMD pytest -v --durations=0 --random-order /tests/integration/test_api.py --junitxml=/test_output/${BACKEND_NAME}.xml
