from collections import namedtuple
from contextlib import asynccontextmanager
from typing import Callable, Iterable
from uuid import UUID

import redis.asyncio as redis

from per_object_permissions.protocols import PermTriple

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


def connection_factory(client_class, settings) -> Callable:
    @asynccontextmanager
    async def connection_manager():
        connection = client_class(host=settings.redis_host)
        yield connection
        if hasattr(connection, "close"):
            await connection.close()
    return connection_manager


class RedisBackend:
    """Stores per-object permission triples in Redis.

    Predicates are keyed by subject-object tuples.

    Searching by any of the three elements is around O(N)
    as no hash tables are used.
    """

    def __init__(self, settings, client_class=redis.Redis, **kwargs):
        self._get_connection = connection_factory(client_class, settings)

    def __iter__(self):
        return self.read()

    async def create(self, perms: Iterable[PermTriple]) -> list[Triple]:
        new = list()
        async with self._get_connection() as connection:
            for perm in perms:
                await connection.sadd(f"perms:{perm.subject_uuid}:{perm.object_uuid}", perm.predicate)
                new.append(Triple(subject_uuid=perm.subject_uuid,
                                  predicate=perm.predicate,
                                  object_uuid=perm.object_uuid))
        return new

    async def read(self,
                   subject_uuids: Iterable[UUID] = None,
                   predicates: Iterable[str] = None,
                   object_uuids: Iterable[UUID] = None) -> list[Triple]:

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

        results = list()

        async with self._get_connection() as connection:
            async for key in connection.scan_iter(match="perms:*"):
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
                        is_member = await connection.sismember(key, predicate)
                        if is_member:
                            results.append(Triple(subject_uuid=subject_uuid,
                                                  predicate=predicate,
                                                  object_uuid=object_uuid))
                else:
                    members = await connection.smembers(key)
                    for pred in members:
                        results.append(Triple(subject_uuid=subject_uuid,
                                              predicate=pred.decode(),
                                              object_uuid=object_uuid))
            return results

    async def delete(self,
                     subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> list[PermTriple]:

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

        deleted = list()

        async with self._get_connection() as connection:
            async for key in connection.scan_iter(match="perms:*"):
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
                        removed_count = await connection.srem(key, predicate)
                        if removed_count == 1:
                            deleted.append(Triple(subject_uuid=subject_uuid,
                                                  predicate=predicate,
                                                  object_uuid=object_uuid))
                else:
                    preds = await connection.smembers(key)
                    await connection.delete(key)
                    for pred in preds:
                        deleted.append(Triple(subject_uuid=subject_uuid,
                                              predicate=pred.decode(),
                                              object_uuid=object_uuid))

        return deleted
