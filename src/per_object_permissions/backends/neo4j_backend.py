from collections import namedtuple
from typing import Callable, Iterable, Iterator
from urllib.parse import quote_plus
from uuid import UUID

from neo4j import AsyncGraphDatabase

from per_object_permissions.protocols import PermTriple

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


def driver_factory(username: str, password: str, host: str) -> Callable:
    def get_driver():
        db_url = f"neo4j://{host}:7687"
        return AsyncGraphDatabase.driver(db_url, auth=(username, password))
    return get_driver


def query_key_values(subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> Iterator[tuple[str, str | UUID]]:

    if subject_uuids:
        yield "subject_uuid", {"$in": subject_uuids}

    if predicates:
        yield "predicate", {"$in": predicates}

    if object_uuids:
        yield "object_uuid", {"$in": object_uuids}


class Neo4jBackend:
    """Stores per-object permission triples in MongoDB."""

    def __init__(self, settings, **kwargs):
        self._get_driver = driver_factory(settings.neo4j_user,
                                          settings.neo4j_password,
                                          settings.neo4j_host)
        self._indexes_created = False

    async def _ensure_indexes(self):
        return
        if not self._indexes_created:
            driver = self._get_driver()
            await driver.db.perms.create_index("subject_uuid")
            await driver.db.perms.create_index("object_uuid")
            self._indexes_created = True

    async def create(self, perms: Iterable[PermTriple]) -> list[Triple]:

        await self._ensure_indexes()
        async with self._get_driver() as driver:

            new_perms = [Triple(subject_uuid=perm.subject_uuid,
                                predicate=perm.predicate,
                                object_uuid=perm.object_uuid)
                         for perm in perms]
        return new_perms

    async def read(self,
                   subject_uuids: Iterable[UUID] = None,
                   predicates: Iterable[str] = None,
                   object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

        await self._ensure_indexes()
        async with self._get_driver() as driver:
            query = dict(query_key_values(subject_uuids, predicates, object_uuids))
            results = list()
            async for perm_doc in driver.db.perms.find(query):
                del perm_doc["_id"]
                results.append(Triple(**perm_doc))
        return results

    async def delete(self,
                     subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> list[PermTriple]:

        await self._ensure_indexes()
        async with self._get_driver() as driver:
            pass
