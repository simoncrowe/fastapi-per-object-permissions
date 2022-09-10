from dataclasses import dataclass
from typing import Generator, Iterable
from uuid import UUID

import redis

from per_object_permissions.protocols import (PermTriple,
                                              PerObjectPermissionBackend)


@dataclass
class Triple:
    subject_uuid: UUID
    predicate: str
    object_uuid: UUID


class RedisBackend(PerObjectPermissionBackend):
    """Stores per-object permission triples in memory."""

    def __init__(self, initial_data: Iterable[PermTriple] = None,
                 settings=None, client_class=redis.Redis, **kwargs):
        self._client = client_class(host=settings.redis_host)

    def __iter__(self):
        return self.read()

    def create(self, perms: Iterable[PermTriple]) -> Generator[Triple, None, None]:
        for perm in perms:
            self._client.sadd(f"perms:{perm.subject_uuid}:{perm.object_uuid}", perm.predicate)
            yield Triple(subject_uuid=perm.subject_uuid,
                         predicate=perm.predicate,
                         object_uuid=perm.object_uuid)

    def read(self,
             subject_uuids: Iterable[UUID] = None,
             predicates: Iterable[str] = None,
             object_uuids: Iterable[UUID] = None) -> Generator[Triple, None, None]:

        for key in self._client.scan_iter(match="*"):
            _, subject_uuid, object_uuid = key.split(":")

            if subject_uuids and subject_uuid not in subject_uuids:
                continue

            if object_uuids and object_uuid not in object_uuids:
                continue

            if not predicates:
                for pred in self._client.smembers(key):
                    yield Triple(subject_uuid=subject_uuid,
                                 predicate=pred,
                                 object_uuid=object_uuid)

            for predicate in predicates:
                if self._client.sismember(key, predicate):
                    yield Triple(subject_uuid=subject_uuid,
                                 predicate=predicate,
                                 object_uuid=object_uuid)

    def delete(self,
               subject_uuids: Iterable[UUID] = None,
               predicates: Iterable[str] = None,
               object_uuids: Iterable[UUID] = None):
        pass
