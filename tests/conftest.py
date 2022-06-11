import uuid

import pytest


@pytest.fixture(scope="session")
def read():
    return "read"


@pytest.fixture(scope="session")
def write():
    return "write"


@pytest.fixture(scope="session")
def delete():
    return "delete"


@pytest.fixture(scope="session")
def subject_one_uuid():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def subject_two_uuid():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def subject_three_uuid():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def object_A_uuid():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def object_B_uuid():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def object_C_uuid():
    return uuid.uuid4()
