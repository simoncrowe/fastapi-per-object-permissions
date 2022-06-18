from http import HTTPStatus

import pytest
from fastapi import testclient

from per_object_permissions.api import main


@pytest.fixture(scope="module")
def client():
    return testclient.TestClient(main.app)


@pytest.fixture(autouse=True)
def backend():
    backend = main.get_backend()
    backend.delete()
    return backend


@pytest.fixture(scope="module")
def subject_one_read_object_A_data(subject_one_read_object_A):
    return {
        "subject_uuid": str(subject_one_read_object_A.subject_uuid),
        "predicate": subject_one_read_object_A.predicate,
        "object_uuid": str(subject_one_read_object_A.object_uuid),
    }


@pytest.fixture(scope="module")
def subject_one_read_object_B_data(subject_one_read_object_B):
    return {
        "subject_uuid": str(subject_one_read_object_B.subject_uuid),
        "predicate": subject_one_read_object_B.predicate,
        "object_uuid": str(subject_one_read_object_B.object_uuid),
    }


@pytest.fixture(scope="module")
def subject_one_write_object_A_data(subject_one_write_object_A):
    return {
        "subject_uuid": str(subject_one_write_object_A.subject_uuid),
        "predicate": subject_one_write_object_A.predicate,
        "object_uuid": str(subject_one_write_object_A.object_uuid),
    }


@pytest.fixture(scope="module")
def subject_two_write_object_C_data(subject_two_write_object_C):
    return {
        "subject_uuid": str(subject_two_write_object_C.subject_uuid),
        "predicate": subject_two_write_object_C.predicate,
        "object_uuid": str(subject_two_write_object_C.object_uuid),
    }


def test_create_perm(client, subject_one_read_object_A_data):
    payload = [subject_one_read_object_A_data]

    response = client.post("/create_perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"created": [subject_one_read_object_A_data]}


def test_create_two_perms(
    client,
    subject_one_read_object_A_data,
    subject_one_write_object_A_data
):
    payload = [subject_one_read_object_A_data, subject_one_write_object_A_data]

    response = client.post("/create_perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["created"]) == 2
    assert subject_one_read_object_A_data in response_data["created"]
    assert subject_one_write_object_A_data in response_data["created"]


def test_read_one_perm(client, backend, subject_one_read_object_A, subject_one_read_object_A_data):
    backend.create([subject_one_read_object_A])

    response = client.post("/read_perms")

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["results"]) == 1
    assert subject_one_read_object_A_data in response_data["results"]


def test_read_perms_filtering_by_predicate(
    client,
    backend,
    subject_one_read_object_A,
    subject_one_read_object_A_data,
    subject_one_write_object_A,
    subject_one_write_object_A_data,
    write
):
    backend.create([subject_one_read_object_A, subject_one_write_object_A])
    payload = {"predicates": [write]}

    response = client.post("/read_perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["results"]) == 1
    assert subject_one_write_object_A_data in response_data["results"]


def test_read_perms_filtering_by_subject_predicate_and_object(
    client,
    backend,
    subject_one_read_object_A,
    subject_one_write_object_A,
    subject_one_read_object_B,
    subject_two_write_object_B,
    subject_two_write_object_C,
    subject_two_write_object_C_data,
    subject_three_read_object_A,
    subject_three_write_object_A,
    subject_two_uuid,
    write,
    object_C_uuid,
):
    backend.create([subject_one_read_object_A,
                    subject_one_write_object_A,
                    subject_one_read_object_B,
                    subject_two_write_object_B,
                    subject_two_write_object_C,
                    subject_three_read_object_A,
                    subject_three_write_object_A])

    payload = {
        "subject_uuids": [str(subject_two_uuid)],
        "predicates": [write],
        "object_uuids": [str(object_C_uuid)]
    }

    response = client.post("/read_perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["results"]) == 1
    assert subject_two_write_object_C_data in response_data["results"]


def test_read_perms_filtering_by_subject_and_two_predicates(
    client,
    backend,
    subject_one_read_object_A,
    subject_one_read_object_A_data,
    subject_one_write_object_A,
    subject_one_write_object_A_data,
    subject_one_read_object_B,
    subject_one_read_object_B_data,
    subject_two_write_object_B,
    subject_two_write_object_C,
    subject_three_read_object_A,
    subject_three_write_object_A,
    subject_one_uuid,
    read,
    write,
):
    backend.create([subject_one_read_object_A,
                    subject_one_write_object_A,
                    subject_one_read_object_B,
                    subject_two_write_object_B,
                    subject_two_write_object_C,
                    subject_three_read_object_A,
                    subject_three_write_object_A])

    payload = {
        "subject_uuids": [str(subject_one_uuid)],
        "predicates": [read, write],
    }

    response = client.post("/read_perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["results"]) == 3
    assert subject_one_read_object_A_data in response_data["results"]
    assert subject_one_read_object_A_data in response_data["results"]
    assert subject_one_read_object_B_data in response_data["results"]
