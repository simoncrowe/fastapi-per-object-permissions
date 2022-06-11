from collections import namedtuple

import pytest

from per_object_permissions.backends import in_memory_backend

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


@pytest.fixture(scope="module")
def subject_one_read_object_A(subject_one_uuid, read, object_A_uuid):
    return Triple(subject_one_uuid, read, object_A_uuid)


@pytest.fixture(scope="module")
def subject_one_write_object_A(subject_one_uuid, write, object_A_uuid):
    return Triple(subject_one_uuid, write, object_A_uuid)


@pytest.fixture(scope="module")
def subject_one_delete_object_A(subject_one_uuid, delete, object_A_uuid):
    return Triple(subject_one_uuid, delete, object_A_uuid)


@pytest.fixture(scope="module")
def subject_one_read_object_B(subject_one_uuid, read, object_B_uuid):
    return Triple(subject_one_uuid, read, object_B_uuid)


@pytest.fixture(scope="module")
def subject_one_delete_object_C(subject_one_uuid, delete, object_C_uuid):
    return Triple(subject_one_uuid, delete, object_C_uuid)


@pytest.fixture(scope="module")
def subject_two_read_object_A(subject_two_uuid, read, object_A_uuid):
    return Triple(subject_two_uuid, read, object_A_uuid)


@pytest.fixture(scope="module")
def subject_two_write_object_A(subject_two_uuid, write, object_A_uuid):
    return Triple(subject_two_uuid, write, object_A_uuid)


@pytest.fixture(scope="module")
def subject_two_write_object_B(subject_two_uuid, write, object_B_uuid):
    return Triple(subject_two_uuid, write, object_B_uuid)


@pytest.fixture(scope="module")
def subject_two_write_object_C(subject_two_uuid, write, object_C_uuid):
    return Triple(subject_two_uuid, write, object_C_uuid)


@pytest.fixture(scope="module")
def subject_three_read_object_A(subject_three_uuid, read, object_A_uuid):
    return Triple(subject_three_uuid, read, object_A_uuid)


@pytest.fixture(scope="module")
def subject_three_write_object_A(subject_three_uuid, write, object_A_uuid):
    return Triple(subject_three_uuid, write, object_A_uuid)


def test_create_one_triple_should_be_persisted(subject_one_read_object_A):
    backend = in_memory_backend.InMemoryBackend()

    backend.create([subject_one_read_object_A])

    assert set(backend) == {subject_one_read_object_A}


def test_create_one_triple_should_be_returned(subject_one_read_object_B):
    backend = in_memory_backend.InMemoryBackend()

    resulting_triples = backend.create([subject_one_read_object_B])

    assert resulting_triples == [subject_one_read_object_B]


def test_create_two_triples(
    subject_one_read_object_A,
    subject_one_write_object_A
):
    backend = in_memory_backend.InMemoryBackend()

    backend.create([subject_one_read_object_A, subject_one_write_object_A])

    assert set(backend) == {subject_one_read_object_A,
                            subject_one_write_object_A}


def test_create_same_triple_twice(subject_one_read_object_A):
    backend = in_memory_backend.InMemoryBackend()

    backend.create([subject_one_read_object_A])
    backend.create([subject_one_read_object_A])

    assert set(backend) == {subject_one_read_object_A}


def test_read_specifying_nothing(
    subject_one_read_object_A,
    subject_one_write_object_A,
    subject_one_delete_object_A,
    subject_two_read_object_A
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A, subject_one_write_object_A,
            subject_one_delete_object_A, subject_two_read_object_A
        )
    )

    results = backend.read()

    assert results == {subject_one_read_object_A, subject_one_write_object_A,
                       subject_one_delete_object_A, subject_two_read_object_A}


def test_read_specifying_one_subject_uuid(
    subject_one_read_object_A,
    subject_one_write_object_A,
    subject_one_delete_object_A,
    subject_two_read_object_A,
    subject_one_uuid,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A, subject_one_write_object_A,
            subject_one_delete_object_A, subject_two_read_object_A
        )
    )

    results = backend.read(subject_uuids=[subject_one_uuid])

    assert results == {subject_one_read_object_A, subject_one_write_object_A,
                       subject_one_delete_object_A}


def test_read_specifying_multiple_subject_uuids(
    subject_one_read_object_A,
    subject_one_write_object_A,
    subject_one_delete_object_A,
    subject_two_read_object_A,
    subject_three_read_object_A,
    subject_one_uuid,
    subject_three_uuid,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_write_object_A,
            subject_one_delete_object_A,
            subject_two_read_object_A,
            subject_three_read_object_A,
        )
    )

    results = backend.read(subject_uuids=[subject_one_uuid, subject_three_uuid])

    assert results == {subject_one_read_object_A, subject_one_write_object_A,
                       subject_one_delete_object_A, subject_three_read_object_A}


def test_read_specifying_one_predicate(
    subject_one_read_object_A,
    subject_one_write_object_A,
    subject_two_read_object_A,
    read,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_write_object_A,
            subject_two_read_object_A,
        )
    )

    results = backend.read(predicates=[read])

    assert results == {subject_one_read_object_A, subject_two_read_object_A}


def test_read_specifying_multiple_predicates(
    subject_one_read_object_A,
    subject_one_write_object_A,
    subject_one_delete_object_A,
    subject_two_read_object_A,
    subject_two_write_object_A,
    subject_three_read_object_A,
    subject_three_write_object_A,
    write,
    delete,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_write_object_A,
            subject_one_delete_object_A,
            subject_two_read_object_A,
            subject_two_write_object_A,
            subject_three_read_object_A,
            subject_three_write_object_A,
        )
    )

    results = backend.read(predicates=[write, delete])

    assert results == {subject_one_write_object_A, subject_one_delete_object_A,
                       subject_two_write_object_A, subject_three_write_object_A}


def test_read_specifying_single_object_uuid(
    subject_one_read_object_A,
    subject_two_write_object_B,
    object_B_uuid,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_two_write_object_B,
        )
    )

    results = backend.read(object_uuids=[object_B_uuid])

    assert results == {subject_two_write_object_B}


def test_read_specifying_multiple_object_uuids(
    subject_one_read_object_A,
    subject_one_read_object_B,
    subject_one_delete_object_C,
    subject_two_write_object_B,
    object_A_uuid,
    object_C_uuid,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_read_object_B,
            subject_one_delete_object_C,
            subject_two_write_object_B,
        )
    )

    results = backend.read(object_uuids=[object_A_uuid, object_C_uuid])

    assert results == {subject_one_read_object_A, subject_one_delete_object_C}


def test_read_specifying_object_uuids_and_predicate(
    subject_one_read_object_A,
    subject_one_read_object_B,
    subject_one_delete_object_C,
    subject_two_write_object_B,
    object_A_uuid,
    object_C_uuid,
    delete,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_read_object_B,
            subject_one_delete_object_C,
            subject_two_write_object_B,
        )
    )

    results = backend.read(object_uuids=[object_A_uuid, object_C_uuid],
                           predicates=[delete])

    assert results == {subject_one_delete_object_C}


def test_read_specifying_object_uuids_subject_uuids_and_predicates(
    subject_one_read_object_A,
    subject_one_write_object_A,
    subject_one_delete_object_A,
    subject_one_read_object_B,
    subject_one_delete_object_C,
    subject_two_read_object_A,
    subject_two_write_object_A,
    subject_two_write_object_B,
    subject_two_write_object_C,
    subject_one_uuid,
    subject_two_uuid,
    object_A_uuid,
    object_C_uuid,
    read,
    write,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_write_object_A,
            subject_one_delete_object_A,
            subject_one_read_object_B,
            subject_one_delete_object_C,
            subject_two_read_object_A,
            subject_two_write_object_A,
            subject_two_write_object_B,
            subject_two_write_object_C,
        )
    )

    results = backend.read(subject_uuids=[subject_one_uuid, subject_two_uuid],
                           predicates=[read, write],
                           object_uuids=[object_A_uuid, object_C_uuid])

    assert results == {subject_one_read_object_A, subject_one_write_object_A,
                       subject_two_read_object_A, subject_two_write_object_A,
                       subject_two_write_object_C}


def test_delete_subject(
    subject_one_read_object_A,
    subject_one_read_object_B,
    subject_two_write_object_C,
    subject_three_write_object_A,
    subject_one_uuid
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_read_object_B,
            subject_two_write_object_C,
            subject_three_write_object_A,
        )
    )

    backend.delete(subject_uuids=[subject_one_uuid])

    assert set(backend) == {subject_two_write_object_C, subject_three_write_object_A}


def test_delete_predicate(
    subject_one_read_object_A,
    subject_one_delete_object_C,
    subject_three_write_object_A,
    read,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_delete_object_C,
            subject_three_write_object_A,
        )
    )

    backend.delete(predicates=[read])

    assert set(backend) == {subject_one_delete_object_C, subject_three_write_object_A}


def test_delete_object(
    subject_one_read_object_A,
    subject_one_read_object_B,
    subject_one_delete_object_C,
    object_A_uuid,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_read_object_A,
            subject_one_read_object_B,
            subject_one_delete_object_C,
        )
    )

    backend.delete(object_uuids=[object_A_uuid])

    assert set(backend) == {subject_one_read_object_B, subject_one_delete_object_C}


def test_delete_based_on_subject_predicate_and_object(
    subject_one_delete_object_A,
    subject_one_delete_object_C,
    subject_one_read_object_A,
    subject_one_read_object_B,
    subject_one_write_object_A,
    subject_two_read_object_A,
    subject_two_write_object_B,
    subject_two_write_object_C,
    subject_three_read_object_A,
    subject_three_write_object_A,
    subject_one_uuid,
    write,
    delete,
    object_A_uuid,
):
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_delete_object_A,
            subject_one_delete_object_C,
            subject_one_read_object_A,
            subject_one_read_object_B,
            subject_one_write_object_A,
            subject_two_read_object_A,
            subject_two_write_object_B,
            subject_two_write_object_C,
            subject_three_read_object_A,
            subject_three_write_object_A,
        )
    )

    backend.delete(subject_uuids=[subject_one_uuid],
                   predicates=[write, delete],
                   object_uuids=[object_A_uuid])

    assert set(backend) == {
        subject_one_delete_object_C,
        subject_one_read_object_A,
        subject_one_read_object_B,
        subject_two_read_object_A,
        subject_two_write_object_B,
        subject_two_write_object_C,
        subject_three_read_object_A,
        subject_three_write_object_A,
    }
