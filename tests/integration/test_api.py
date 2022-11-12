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
def a_hundred_subject_uuids():
    return [str(uuid.uuid4()) for _ in range(100)]


@pytest.fixture
def ten_predicates():
    return ["launch", "hold", "use", "scratch", "grasp",
            "melt", "kick", "train", "wake", "sue"]


@pytest.fixture
def a_hundred_object_uuids():
    return [str(uuid.uuid4()) for _ in range(100)]


@pytest.fixture
def a_hundred_thousand_triples_data(a_hundred_subject_uuids,
                                    ten_predicates,
                                    a_hundred_object_uuids):
    return [
        {"subject_uuid": subject_uuid,
         "predicate": predicate,
         "object_uuid": object_uuid}
        for subject_uuid in a_hundred_subject_uuids
        for predicate in ten_predicates
        for object_uuid in a_hundred_object_uuids
    ]


@pytest.fixture
def a_hundred_thousand_triples_created(a_hundred_thousand_triples_data):
    """Putting the data creation call in a fixture so it's excluded
    from the test durations.
    """
    requests.post(CREATE_URL, json=a_hundred_thousand_triples_data)


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


def test_create_a_hundred_thousand(a_hundred_thousand_triples_data):
    data = a_hundred_thousand_triples_data

    response = requests.post(CREATE_URL, json=data)

    assert response.status_code == HTTPStatus.OK
    expected_triples = set(make_hashable(triple) for triple in data)
    actual_triples = set(make_hashable(triple) for triple in response.json()["created"])
    assert actual_triples == expected_triples


def test_create_and_read_a_hundred_thousand(a_hundred_thousand_triples_data):
    data = a_hundred_thousand_triples_data

    create_response = requests.post(CREATE_URL, json=data)

    assert create_response.status_code == HTTPStatus.OK

    read_response = requests.post(READ_URL, json={})

    assert read_response.status_code == HTTPStatus.OK
    expected_triples = set(make_hashable(triple) for triple in data)
    actual_triples = set(make_hashable(triple)
                         for triple in read_response.json()["results"])
    assert actual_triples == expected_triples


def test_create_and_delete_a_hundred_thousand(a_hundred_thousand_triples_data):
    data = a_hundred_thousand_triples_data

    create_response = requests.post(CREATE_URL, json=data)

    assert create_response.status_code == HTTPStatus.OK

    delete_response = requests.post(DELETE_URL, json={})

    assert delete_response.status_code == HTTPStatus.OK
    expected_triples = set(make_hashable(triple) for triple in data)
    actual_triples = set(make_hashable(triple)
                         for triple in delete_response.json()["deleted"])
    assert actual_triples == expected_triples


@pytest.mark.parametrize("subject_uuid_index", [0, 24, 49, 99])
def test_read_filter_by_subject_uuid(a_hundred_subject_uuids,
                                     a_hundred_thousand_triples_created,
                                     subject_uuid_index):
    """Test reading triples, filtered by subject UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    read_payload = {"subject_uuids": [a_hundred_subject_uuids[subject_uuid_index]]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 1000


@pytest.mark.parametrize("object_uuid_index", [0, 24, 49, 99])
def test_read_filter_by_object_uuid(a_hundred_object_uuids,
                                    a_hundred_thousand_triples_created,
                                    object_uuid_index):
    """Test reading triples, filtered by object UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    read_payload = {"object_uuids": [a_hundred_object_uuids[object_uuid_index]]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == 1000


@pytest.mark.parametrize(
    "subject_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 5000),
        (slice(40, 50), 10000),
        (slice(80, None), 20000),
    ]
)
def test_read_filter_by_multiple_subject_uuids(a_hundred_subject_uuids,
                                               a_hundred_thousand_triples_created,
                                               subject_uuid_slice,
                                               expected_result_count):
    """Test reading triples, filtered by multiple subject UUIDs."""
    read_payload = {"subject_uuids": a_hundred_subject_uuids[subject_uuid_slice]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == expected_result_count


@pytest.mark.parametrize(
    "object_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 5000),
        (slice(40, 50), 10000),
        (slice(80, None), 20000),
    ]
)
def test_read_filter_by_multiple_object_uuids(a_hundred_object_uuids,
                                              a_hundred_thousand_triples_created,
                                              object_uuid_slice,
                                              expected_result_count):
    """Test reading triples, filtered by multiple object UUIDs."""
    read_payload = {"object_uuids": a_hundred_object_uuids[object_uuid_slice]}

    read_response = requests.post(READ_URL, json=read_payload)

    assert read_response.status_code == HTTPStatus.OK
    assert len(read_response.json()["results"]) == expected_result_count


@pytest.mark.parametrize("subject_uuid_index", [0, 24, 49, 99])
def test_delete_filter_by_subject_uuid(a_hundred_subject_uuids,
                                       a_hundred_thousand_triples_created,
                                       subject_uuid_index):
    """Test deleting triples, filtered by subject UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    delete_payload = {"subject_uuids": [a_hundred_subject_uuids[subject_uuid_index]]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 1000


@pytest.mark.parametrize("object_uuid_index", [0, 24, 49, 99])
def test_delete_filter_by_object_uuid(a_hundred_object_uuids,
                                      a_hundred_thousand_triples_created,
                                      object_uuid_index):
    """Test deleting triples, filtered by object UUIDs.

    Different indexes of the input list are used to check for performance
    differences based on insertion order.
    """
    delete_payload = {"object_uuids": [a_hundred_object_uuids[object_uuid_index]]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == 1000


@pytest.mark.parametrize(
    "subject_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 5000),
        (slice(40, 50), 10000),
        (slice(80, None), 20000),
    ]
)
def test_delete_filter_by_multiple_subject_uuids(a_hundred_subject_uuids,
                                                 a_hundred_thousand_triples_created,
                                                 subject_uuid_slice,
                                                 expected_result_count):
    """Test deleting triples, filtered by multiple subject UUIDs."""
    delete_payload = {"subject_uuids": a_hundred_subject_uuids[subject_uuid_slice]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == expected_result_count


@pytest.mark.parametrize(
    "object_uuid_slice,expected_result_count",
    [
        (slice(0, 5), 5000),
        (slice(40, 50), 10000),
        (slice(80, None), 20000),
    ]
)
def test_delete_filter_by_multiple_object_uuids(a_hundred_object_uuids,
                                                a_hundred_thousand_triples_created,
                                                object_uuid_slice,
                                                expected_result_count):
    """Test deleting triples, filtered by multiple object UUIDs."""
    delete_payload = {"object_uuids": a_hundred_object_uuids[object_uuid_slice]}

    delete_response = requests.post(DELETE_URL, json=delete_payload)

    assert delete_response.status_code == HTTPStatus.OK
    assert len(delete_response.json()["deleted"]) == expected_result_count
