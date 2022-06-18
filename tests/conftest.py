import uuid
from collections import namedtuple

import pytest

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


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


@pytest.fixture(scope="session")
def subject_one_read_object_A(subject_one_uuid, read, object_A_uuid):
    return Triple(subject_one_uuid, read, object_A_uuid)


@pytest.fixture(scope="session")
def subject_one_write_object_A(subject_one_uuid, write, object_A_uuid):
    return Triple(subject_one_uuid, write, object_A_uuid)


@pytest.fixture(scope="session")
def subject_one_delete_object_A(subject_one_uuid, delete, object_A_uuid):
    return Triple(subject_one_uuid, delete, object_A_uuid)


@pytest.fixture(scope="session")
def subject_one_read_object_B(subject_one_uuid, read, object_B_uuid):
    return Triple(subject_one_uuid, read, object_B_uuid)


@pytest.fixture(scope="session")
def subject_one_delete_object_C(subject_one_uuid, delete, object_C_uuid):
    return Triple(subject_one_uuid, delete, object_C_uuid)


@pytest.fixture(scope="session")
def subject_two_read_object_A(subject_two_uuid, read, object_A_uuid):
    return Triple(subject_two_uuid, read, object_A_uuid)


@pytest.fixture(scope="session")
def subject_two_write_object_A(subject_two_uuid, write, object_A_uuid):
    return Triple(subject_two_uuid, write, object_A_uuid)


@pytest.fixture(scope="session")
def subject_two_write_object_B(subject_two_uuid, write, object_B_uuid):
    return Triple(subject_two_uuid, write, object_B_uuid)


@pytest.fixture(scope="session")
def subject_two_write_object_C(subject_two_uuid, write, object_C_uuid):
    return Triple(subject_two_uuid, write, object_C_uuid)


@pytest.fixture(scope="session")
def subject_three_read_object_A(subject_three_uuid, read, object_A_uuid):
    return Triple(subject_three_uuid, read, object_A_uuid)


@pytest.fixture(scope="session")
def subject_three_write_object_A(subject_three_uuid, write, object_A_uuid):
    return Triple(subject_three_uuid, write, object_A_uuid)
