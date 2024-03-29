from http import HTTPStatus

import pytest
from fastapi import testclient

from per_object_permissions.api import main


async def teardown_function(function):
    """Clear data from the cached in-memory backend."""
    await main.get_backend().delete()


@pytest.fixture(scope="module")
def client():
    return testclient.TestClient(main.app)


@pytest.fixture(scope="module")
def subject_one_read_object_A_data(subject_one_uuid, read, object_A_uuid):
    return {
        "subject_uuid": str(subject_one_uuid),
        "predicate": read,
        "object_uuid": str(object_A_uuid)
    }


@pytest.fixture(scope="module")
def subject_one_write_object_A_data(subject_one_uuid, write, object_A_uuid):
    return {
        "subject_uuid": str(subject_one_uuid),
        "predicate": write,
        "object_uuid": str(object_A_uuid)
    }


@pytest.fixture(scope="module")
def subject_two_write_object_A_data(subject_two_uuid, write, object_A_uuid):
    return {
        "subject_uuid": str(subject_two_uuid),
        "predicate": write,
        "object_uuid": str(object_A_uuid)
    }


@pytest.fixture(scope="module")
def subject_two_read_object_B_data(subject_two_uuid, read, object_B_uuid):
    return {
        "subject_uuid": str(subject_two_uuid),
        "predicate": read,
        "object_uuid": str(object_B_uuid)
    }


@pytest.fixture(scope="module")
def subject_two_write_object_B_data(subject_two_uuid, write, object_B_uuid):
    return {
        "subject_uuid": str(subject_two_uuid),
        "predicate": write,
        "object_uuid": str(object_B_uuid)
    }


@pytest.fixture(scope="module")
def subject_two_delete_object_B_data(subject_two_uuid, delete, object_B_uuid):
    return {
        "subject_uuid": str(subject_two_uuid),
        "predicate": delete,
        "object_uuid": str(object_B_uuid)
    }


@pytest.fixture(scope="module")
def subject_three_read_object_B_data(subject_three_uuid, read, object_B_uuid):
    return {
        "subject_uuid": str(subject_three_uuid),
        "predicate": read,
        "object_uuid": str(object_B_uuid)
    }


@pytest.fixture(scope="module")
def subject_three_read_object_C_data(subject_three_uuid, read, object_C_uuid):
    return {
        "subject_uuid": str(subject_three_uuid),
        "predicate": read,
        "object_uuid": str(object_C_uuid)
    }


@pytest.fixture(scope="module")
def subject_three_write_object_C_data(subject_three_uuid, write, object_C_uuid):
    return {
        "subject_uuid": str(subject_three_uuid),
        "predicate": write,
        "object_uuid": str(object_C_uuid)
    }


@pytest.fixture(scope="module")
def all_data(
    subject_one_read_object_A_data,
    subject_one_write_object_A_data,
    subject_two_delete_object_B_data,
    subject_two_read_object_B_data,
    subject_two_write_object_A_data,
    subject_two_write_object_B_data,
    subject_three_read_object_B_data,
    subject_three_read_object_C_data,
    subject_three_write_object_C_data,
):
    return [
        subject_one_read_object_A_data,
        subject_one_write_object_A_data,
        subject_two_delete_object_B_data,
        subject_two_read_object_B_data,
        subject_two_write_object_A_data,
        subject_two_write_object_B_data,
        subject_three_read_object_B_data,
        subject_three_read_object_C_data,
        subject_three_write_object_C_data,
    ]


def test_create_perm(client, subject_one_read_object_A_data):
    payload = [subject_one_read_object_A_data]

    response = client.post("create-perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"created": [subject_one_read_object_A_data]}


def test_create_two_perms(
    client,
    subject_one_read_object_A_data,
    subject_one_write_object_A_data
):
    payload = [subject_one_read_object_A_data, subject_one_write_object_A_data]

    response = client.post("create-perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["created"]) == 2
    assert subject_one_read_object_A_data in response_data["created"]
    assert subject_one_write_object_A_data in response_data["created"]


def query_key_values_from_fixture_names(request: pytest.FixtureRequest,
                                        query_fixture_names: dict):
    if "subject_uuids" in query_fixture_names:
        yield ("subject_uuids", [str(request.getfixturevalue(name))
                                 for name in query_fixture_names["subject_uuids"]])
    if "predicates" in query_fixture_names:
        yield ("predicates", [str(request.getfixturevalue(name))
                              for name in query_fixture_names["predicates"]])
    if "object_uuids" in query_fixture_names:
        yield ("object_uuids", [str(request.getfixturevalue(name))
                                for name in query_fixture_names["object_uuids"]])


@pytest.mark.parametrize("query_fixture_names,result_fixture_names", [
    (
        {"subject_uuids": ["subject_one_uuid"]},
        ["subject_one_read_object_A_data", "subject_one_write_object_A_data"]
    ),
    (
        {"subject_uuids": ["subject_one_uuid", "subject_three_uuid"]},
        ["subject_one_write_object_A_data", "subject_one_write_object_A_data",
         "subject_three_read_object_B_data", "subject_three_read_object_C_data",
         "subject_three_write_object_C_data"]
    ),
    (
        {"subject_uuids": ["subject_one_uuid"], "predicates": ["write"]},
        ["subject_one_write_object_A_data"]
    ),
    (
        {"subject_uuids": ["subject_three_uuid"],
         "predicates": ["write", "read", "delete"],
         "object_uuids": ["object_C_uuid"]},
        ["subject_three_read_object_C_data", "subject_three_write_object_C_data"]),
])
def test_read_perms(client, all_data, request,
                    query_fixture_names, result_fixture_names):
    client.post("create-perms", json=all_data)

    payload = dict(query_key_values_from_fixture_names(request, query_fixture_names))

    response = client.post("read-perms", json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    expected_results = [request.getfixturevalue(name) for name in result_fixture_names]
    assert len(response_data["results"]) == len(expected_results)
    for result in expected_results:
        assert result in response_data["results"]


@pytest.mark.parametrize("query_fixture_names,deleted_fixture_names", [
    (
        {"object_uuids": ["object_B_uuid"]},
        ["subject_two_delete_object_B_data", "subject_two_read_object_B_data",
         "subject_two_write_object_B_data", "subject_three_read_object_B_data"]
    ),
    (
        {"subject_uuids": ["subject_one_uuid", "subject_two_uuid"]},
        ["subject_one_write_object_A_data", "subject_one_write_object_A_data",
         "subject_two_delete_object_B_data", "subject_two_read_object_B_data",
         "subject_two_write_object_A_data", "subject_two_write_object_B_data"]
    ),
    (
        {"subject_uuids": ["subject_one_uuid"], "predicates": ["read"]},
        ["subject_one_read_object_A_data"]
    ),
    (
        {"subject_uuids": ["subject_three_uuid"],
         "predicates": ["write", "read", "delete"],
         "object_uuids": ["object_C_uuid"]},
        ["subject_three_read_object_C_data", "subject_three_write_object_C_data"]),
])
def test_delete_perms(client, all_data, request,
                      query_fixture_names, deleted_fixture_names):
    client.post("create-perms", json=all_data)

    payload = dict(query_key_values_from_fixture_names(request, query_fixture_names))

    delete_response = client.post("/delete-perms", json=payload)

    assert delete_response.status_code == HTTPStatus.OK
    response_data = delete_response.json()
    expected_deleted = [request.getfixturevalue(name) for name in deleted_fixture_names]
    assert len(response_data["deleted"]) == len(expected_deleted)
    for result in expected_deleted:
        assert result in response_data["deleted"]

    read_response = client.post("/read-perms", json=payload)
    assert len(read_response.json()["results"]) == 0
