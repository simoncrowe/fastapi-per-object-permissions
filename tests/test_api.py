import pytest
from fastapi import testclient

from per_object_permissions.api.main import app


@pytest.fixture(scope="module")
def client():
    return testclient.TestClient(app)


@pytest.fixture(scope="module")
def subject_one_read_object_A_payload(subject_one_uuid, read, object_A_uuid):
    return {
        "subject_uuid": str(subject_one_uuid),
        "predicate": read,
        "object_uuid": str(object_A_uuid)
    }


@pytest.fixture(scope="module")
def subject_one_write_object_A_payload(subject_one_uuid, write, object_A_uuid):
    return {
        "subject_uuid": str(subject_one_uuid),
        "predicate": write,
        "object_uuid": str(object_A_uuid)
    }


def test_create_perm(client, subject_one_read_object_A_payload):
    payload = [subject_one_read_object_A_payload]

    response = client.post("/create_perms", json=payload)

    assert response.status_code == 200
    assert response.json() == {"created": [subject_one_read_object_A_payload]}


def test_create_two_perms(
    client,
    subject_one_read_object_A_payload,
    subject_one_write_object_A_payload
):
    payload = [subject_one_read_object_A_payload, subject_one_write_object_A_payload]

    response = client.post("/create_perms", json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["created"]) == 2
    assert subject_one_read_object_A_payload in response_data["created"]
    assert subject_one_write_object_A_payload in response_data["created"]
