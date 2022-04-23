import uuid

from backends import in_memory_backend


def test_create_one_triple():
    triple = (uuid.uuid4(), "read", uuid.uuid4())
    backend = in_memory_backend.InMemoryBackend()

    subject_uuid, predicate, object_uuid = triple
    backend.create(subject_uuid, predicate, object_uuid)

    assert set(backend) == {triple}


def test_create_two_triples():
    triple_one = (uuid.uuid4(), "read", uuid.uuid4())
    triple_two = (uuid.uuid4(), "write", uuid.uuid4())
    backend = in_memory_backend.InMemoryBackend()

    subject_uuid, predicate, object_uuid = triple_one
    backend.create(subject_uuid, predicate, object_uuid)
    backend.create(*triple_two)

    assert set(backend) == {triple_one, triple_two}


def test_create_same_triple_twice():
    triple = (uuid.uuid4(), "read", uuid.uuid4())
    backend = in_memory_backend.InMemoryBackend()

    subject_uuid, predicate, object_uuid = triple
    backend.create(subject_uuid, predicate, object_uuid)
    backend.create(subject_uuid, predicate, object_uuid)

    assert set(backend) == {triple}


def test_read_specifying_one_subject_uuid():
    subject_one_uuid, subject_two_uuid = uuid.uuid4(), uuid.uuid4()
    object_uuid = uuid.uuid4()
    subject_one_triple_one = (subject_one_uuid, "read", object_uuid)
    subject_one_triple_two = (subject_one_uuid, "write", object_uuid)
    subject_one_triple_three = (subject_one_uuid, "delete", object_uuid)
    subject_two_triple = (subject_two_uuid, "read", object_uuid)
    backend = in_memory_backend.InMemoryBackend(
        initial_data=(
            subject_one_triple_one,
            subject_one_triple_two,
            subject_one_triple_three,
            subject_two_triple,
        )
    )

    results = backend.read(subject_uuids=[subject_one_uuid])

    assert results == {subject_one_triple_one, subject_one_triple_two, subject_one_triple_three}
