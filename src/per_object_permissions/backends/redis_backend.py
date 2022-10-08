from collections import namedtuple
from typing import Generator, Iterable
from uuid import UUID

import redis

from per_object_permissions.protocols import (PermTriple,
                                              PerObjectPermissionBackend)

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


class RedisBackend(PerObjectPermissionBackend):
    """Stores per-object permission triples in Redis.

    Predicates are keyed by subject-object tuples.

    Searching by any of the three elements is around O(N)
    as no hash tables are used.
    """

    def __init__(self, initial_data: Iterable[PermTriple] = None,
                 settings=None, client_class=redis.Redis, **kwargs):
        self._client = client_class(host=settings.redis_host)
        if initial_data:
            self.create(initial_data)

    def __iter__(self):
        return self.read()

    def create(self, perms: Iterable[PermTriple]) -> Generator[Triple, None, None]:
        def new_triples():
            for perm in perms:
                self._client.sadd(f"perms:{perm.subject_uuid}:{perm.object_uuid}", perm.predicate)
                yield Triple(subject_uuid=perm.subject_uuid,
                             predicate=perm.predicate,
                             object_uuid=perm.object_uuid)
        return set(new_triples())

    def read(self,
             subject_uuids: Iterable[UUID] = None,
             predicates: Iterable[str] = None,
             object_uuids: Iterable[UUID] = None) -> Generator[Triple, None, None]:

        if subject_uuids:
            requested_subject_uuids = {str(subject_uuid)
                                       for subject_uuid in subject_uuids}
        else:
            requested_subject_uuids = set()
        if object_uuids:
            requested_object_uuids = {str(object_uuid)
                                      for object_uuid in object_uuids}
        else:
            requested_object_uuids = set()

        for key in self._client.scan_iter(match="perms:*"):
            _, subject_uuid, object_uuid = key.decode().split(":")

            if (
                requested_subject_uuids
                and subject_uuid not in requested_subject_uuids
            ):
                continue

            if (
                requested_object_uuids
                and object_uuid not in requested_object_uuids
            ):
                continue

            if predicates:
                for predicate in predicates:
                    if self._client.sismember(key, predicate):
                        yield Triple(subject_uuid=subject_uuid,
                                     predicate=predicate,
                                     object_uuid=object_uuid)
            else:
                for pred in self._client.smembers(key):
                    yield Triple(subject_uuid=subject_uuid,
                                 predicate=pred.decode(),
                                 object_uuid=object_uuid)

    def delete(self,
               subject_uuids: Iterable[UUID] = None,
               predicates: Iterable[str] = None,
               object_uuids: Iterable[UUID] = None):

        def deleted_triples():
            if subject_uuids:
                requested_subject_uuids = {str(subject_uuid)
                                           for subject_uuid in subject_uuids}
            else:
                requested_subject_uuids = set()
            if object_uuids:
                requested_object_uuids = {str(object_uuid)
                                          for object_uuid in object_uuids}
            else:
                requested_object_uuids = set()

            for key in self._client.scan_iter(match="perms:*"):
                _, subject_uuid, object_uuid = key.decode().split(":")

                if (
                    requested_subject_uuids
                    and subject_uuid not in requested_subject_uuids
                ):
                    continue

                if (
                    requested_object_uuids
                    and object_uuid not in requested_object_uuids
                ):
                    continue

                if predicates:
                    for predicate in predicates:
                        removed_count = self._client.srem(key, predicate)
                        if removed_count == 1:
                            yield Triple(subject_uuid=subject_uuid,
                                         predicate=predicate,
                                         object_uuid=object_uuid)
                else:
                    preds = self._client.smembers(key)
                    self._client.delete(key)
                    for pred in preds:
                        yield Triple(subject_uuid=subject_uuid,
                                     predicate=pred.decode(),
                                     object_uuid=object_uuid)

        return set(deleted_triples())
