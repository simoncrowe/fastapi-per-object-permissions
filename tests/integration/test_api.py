"""API integration tests.

These tests serve two purposes:
- Ensuring that all the backend integrate well with the web service.
- Giving some idea idea of comparative performance of the backends
  as some tests create a moderately large number of records.
"""
import uuid
from http import HTTPStatus

import pytest
import requests

API_BASE_URL = "http://api:8008"
READ_URL = f"{API_BASE_URL}/read-perms"
CREATE_URL = f"{API_BASE_URL}/create-perms"
DELETE_URL = f"{API_BASE_URL}/delete-perms"


def setup_module():
    """Warm up the API server so the duration of the first test is not inflated."""
    data = [{"subject_uuid": "1637e5a2-1a13-4e65-a02c-ee0aee67214a",
             "predicate": "poke",
             "object_uuid": "4cb51999-de76-41ac-80e4-79cae8a68b78"}]
    requests.post(CREATE_URL, json=data)
    requests.post(READ_URL, json={})
    requests.post(DELETE_URL, json={})


def make_hashable(triple_data: dict) -> tuple:
    return (triple_data["subject_uuid"],
            triple_data["predicate"],
            triple_data["object_uuid"])


def teardown_function():
    """Clear all data after each test."""
    requests.post(DELETE_URL, json={})


@pytest.fixture
def subject_one_read_object_A_data(subject_one_uuid, read, object_A_uuid):
    return {"subject_uuid": str(subject_one_uuid),
            "predicate": read,
            "object_uuid": str(object_A_uuid)}


@pytest.fixture
def subject_uuids():
    return [str(uuid.uuid4()) for _ in range(100)]


@pytest.fixture
def predicates():
    return ["create", "read", "write", "delete", "share"]


@pytest.fixture
def object_uuids():
    return [str(uuid.uuid4()) for _ in range(100)]


@pytest.fixture
def triples_data(subject_uuids,
                 predicates,
                 object_uuids):
    return [
        {"subject_uuid": subject_uuid,
         "predicate": predicate,
         "object_uuid": object_uuid}
        for subject_uuid in subject_uuids
        for predicate in predicates
        for object_uuid in object_uuids
    ]


@pytest.fixture
def triples_created(triples_data):
    """Putting the data creation call in a fixture so it's excluded
    from the test durations.
    """
    requests.post(CREATE_URL, json=triples_data)


def test_create_one(subject_one_read_object_A_data):
    data = [subject_one_read_object_A_data]

    response = requests.post(CREATE_URL, json=data)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"created": data}


def test_create_and_read_one(subject_one_read_object_A_data):
    data = [subject_one_read_object_A_data]

    requests.post(CREATE_URL, json=data)
    response = requests.post(READ_URL, json={})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"results": data}


def test_create_and_delete_one(subject_one_read_object_A_data):
    data = [subject_one_read_object_A_data]

    requests.post(CREATE_URL, json=data)
    delete_response = requests.post(DELETE_URL, json={})

    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json() == {"deleted": data}

    read_response = requests.post(READ_URL, json={})

    assert read_response.status_code == HTTPStatus.OK
    assert read_response.json() == {"results": []}


def test_create_a_hundred_thousand(triples_data):
    data = triples_data

    response = requests.post(CREATE_URL, json=data)

    assert response.status_code == HTTPStatus.OK
    expected_triples = set(make_hashable(triple) for triple in data)
    actual_triples = set(make_hashable(triple) for triple in response.json()["created"])
    assert actual_triples == expected_triples


def test_create_and_read_a_hundred_thousand(triples_data):
    data = triples_data

    create_response = requests.post(CREATE_URL, json=data)

    assert create_response.status_code == HTTPStatus.OK

    read_response = requests.post(READ_URL, json={})

    assert read_response.status_code == HTTPStatus.OK
    expected_triples = set(make_hashable(triple) for triple in data)
    actual_triples = set(make_hashable(triple)
                         for triple in read_response.json()["results"])
    assert actual_triples == expected_triples


def test_create_and_delete_a_hundred_thousand(triples_data):
    data = triples_data

    create_response = requests.post(CREATE_URL, json=data)

    assert create_response.status_code == HTTPStatus.OK

    delete_response = requests.post(DELETE_URL, json={})

    assert delete_response.status_code == HTTPStatus.OK
    expected_triples = set(make_hashable(triple) for triple in data)
    actual_triples = set(make_hashable(triple)
                         for triple in delete_response.json()["deleted"])
    assert actual_triples == expected_triples


@pytest.mark.parametrize("subject_uuid_index", [0, 24, 49, 99])
def test_read_filter_by_subject_uuid(subject_uuids,
                                     triples_created,
                                     subject_uuid_index):
    """Test reading triples, filtered by subject UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    read_payload = {"subject_uuids": [subject_uuids[subject_uuid_index]]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 500


@pytest.mark.parametrize("object_uuid_index", [0, 24, 49, 99])
def test_read_filter_by_object_uuid(object_uuids,
                                    triples_created,
                                    object_uuid_index):
    """Test reading triples, filtered by object UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    read_payload = {"object_uuids": [object_uuids[object_uuid_index]]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 500


@pytest.mark.parametrize(
    "subject_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 2500),
        (slice(40, 50), 5000),
        (slice(80, None), 10000),
    ]
)
def test_read_filter_by_multiple_subject_uuids(subject_uuids,
                                               triples_created,
                                               subject_uuid_slice,
                                               expected_result_count):
    """Test reading triples, filtered by multiple subject UUIDs."""
    read_payload = {"subject_uuids": subject_uuids[subject_uuid_slice]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == expected_result_count


@pytest.mark.parametrize(
    "object_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 2500),
        (slice(40, 50), 5000),
        (slice(80, None), 10000),
    ]
)
def test_read_filter_by_multiple_object_uuids(object_uuids,
                                              triples_created,
                                              object_uuid_slice,
                                              expected_result_count):
    """Test reading triples, filtered by multiple object UUIDs."""
    read_payload = {"object_uuids": object_uuids[object_uuid_slice]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == expected_result_count


def test_read_filter_by_predicate(predicates, triples_created):
    """Test reading triples, filtered by a predicate."""
    read_payload = {"predicates": predicates[:1]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 10000


def test_read_filter_by_many_predicates(predicates, triples_created):
    """Test reading triples, filtered by three predicates."""
    read_payload = {"predicates": predicates[:3]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 30000


def test_read_filter_by_predicate_and_object_uuid(predicates,
                                                  object_uuids,
                                                  triples_created):
    """Test reading triples, filtered by a predicate and object UUID."""
    read_payload = {"predicates": predicates[:1], "object_uuids": object_uuids[49:50]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 100


def test_read_filter_by_predicate_and_nonexistent_object_uuid(predicates,
                                                              triples_created):
    """Test reading triples, filtered by a predicate and nonexistent object UUID."""
    read_payload = {"predicates": predicates[:1],
                    "object_uuids": [str(uuid.uuid4())]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 0


def test_read_filter_by_predicate_and_nonexistent_subject_uuid(predicates,
                                                               triples_created):
    """Test reading triples, filtered by a predicate and nonexistent subject UUID."""
    read_payload = {"predicates": predicates[:1],
                    "subject_uuids": [str(uuid.uuid4())]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 0


def test_read_filter_by_predicate_and_subject_uuid(predicates,
                                                   subject_uuids,
                                                   triples_created):
    """Test reading triples, filtered by a predicate and subject UUID."""
    read_payload = {"predicates": predicates[:1], "subject_uuids": subject_uuids[49:50]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 100


def test_read_filter_by_predicate_subject_and_object_uuid(predicates,
                                                          subject_uuids,
                                                          object_uuids,
                                                          triples_created):
    """Test reading triples, filtered by a predicate subject UUID and object UUID."""
    read_payload = {"predicates": predicates[:1],
                    "subject_uuids": subject_uuids[49:50],
                    "object_uuids": object_uuids[49:50]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 1


@pytest.mark.parametrize("subject_uuid_index", [0, 24, 49, 99])
def test_delete_filter_by_subject_uuid(subject_uuids,
                                       triples_created,
                                       subject_uuid_index):
    """Test deleting triples, filtered by subject UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    delete_payload = {"subject_uuids": [subject_uuids[subject_uuid_index]]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 500


@pytest.mark.parametrize("object_uuid_index", [0, 24, 49, 99])
def test_delete_filter_by_object_uuid(object_uuids,
                                      triples_created,
                                      object_uuid_index):
    """Test deleting triples, filtered by object UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    delete_payload = {"object_uuids": [object_uuids[object_uuid_index]]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 500


@pytest.mark.parametrize(
    "subject_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 2500),
        (slice(40, 50), 5000),
        (slice(80, None), 10000),
    ]
)
def test_delete_filter_by_multiple_subject_uuids(subject_uuids,
                                                 triples_created,
                                                 subject_uuid_slice,
                                                 expected_result_count):
    """Test deleting triples, filtered by multiple subject UUIDs."""
    delete_payload = {"subject_uuids": subject_uuids[subject_uuid_slice]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == expected_result_count


@pytest.mark.parametrize(
    "object_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 2500),
        (slice(40, 50), 5000),
        (slice(80, None), 10000),
    ]
)
def test_delete_filter_by_multiple_object_uuids(object_uuids,
                                                triples_created,
                                                object_uuid_slice,
                                                expected_result_count):
    """Test deleting triples, filtered by multiple object UUIDs."""
    delete_payload = {"object_uuids": object_uuids[object_uuid_slice]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == expected_result_count


def test_delete_filter_by_predicate(predicates, triples_created):
    """Test deleting triples, filtered by a predicate."""
    delete_payload = {"predicates": predicates[:1]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 10000


def test_delete_filter_by_many_predicates(predicates, triples_created):
    """Test deleting triples, filtered by three predicates."""
    delete_payload = {"predicates": predicates[:3]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 30000


def test_delete_filter_by_predicate_and_object_uuid(predicates,
                                                    object_uuids,
                                                    triples_created):
    """Test deleting triples, filtered by a predicate and object UUID."""
    delete_payload = {"predicates": predicates[:1],
                      "object_uuids": object_uuids[49:50]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 100


def test_delete_filter_by_predicate_and_nonexistent_object_uuid(predicates,
                                                                triples_created):
    """Test deleting triples, filtered by a predicate and nonexistent object UUID."""
    delete_payload = {"predicates": predicates[:1],
                      "object_uuids": [str(uuid.uuid4())]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 0


def test_delete_filter_by_predicate_and_nonexistent_subject_uuid(predicates,
                                                                 triples_created):
    """Test deleting triples, filtered by a predicate and nonexistent subject UUID."""
    delete_payload = {"predicates": predicates[:1],
                      "subject_uuids": [str(uuid.uuid4())]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 0


def test_delete_filter_by_predicate_and_subject_uuid(predicates,
                                                     subject_uuids,
                                                     triples_created):
    """Test deleting triples, filtered by a predicate and subject UUID."""
    delete_payload = {"predicates": predicates[:1],
                      "subject_uuids": subject_uuids[49:50]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 100


def test_delete_filter_by_predicate_subject_and_object_uuid(predicates,
                                                            subject_uuids,
                                                            object_uuids,
                                                            triples_created):
    """Test deleting triples, filtered by a predicate subject UUID and object UUID."""
    delete_payload = {"predicates": predicates[:1],
                      "subject_uuids": subject_uuids[49:50],
                      "object_uuids": object_uuids[49:50]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 1
