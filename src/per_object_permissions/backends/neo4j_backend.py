from collections import namedtuple
from itertools import count
from typing import Callable, Iterable, Iterator
from uuid import UUID

from neo4j import AsyncGraphDatabase

from per_object_permissions.protocols import PermTriple

DB_NAME = "perms"

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


def driver_factory(username: str, password: str, host: str) -> Callable:
    def get_driver():
        db_url = f"neo4j://{host}:7687"
        return AsyncGraphDatabase.driver(db_url, auth=(username, password))
    return get_driver


def create_triples(tx, perms: Iterable[PermTriple]):
    def iter_query_data():
        counter = count()
        node_ids = {}
        for perm in perms:
            subject_name = node_ids.setdefault(perm.subject_uuid, f"n{next(counter)}")
            object_name = node_ids.setdefault(perm.object_uuid, f"n{next(counter)}")

            yield (f'({subject_name} {{ uuid: "{perm.subject_uuid}" }}) '
                   f'-[:PREDICATE {{predicate: "{perm.predicate}"}}]-> '
                   f'({object_name} {{ uuid: "{perm.object_uuid}" }})')

    return tx.run(f"MERGE {', '.join(iter_query_data())};")


class Neo4jBackend:
    """Stores per-object permission triples in Neo4j."""

    def __init__(self, settings, **kwargs):
        self._get_driver = driver_factory(settings.neo4j_user,
                                          settings.neo4j_password,
                                          settings.neo4j_host)
        self._indexes_created = False

    async def create(self, perms: Iterable[PermTriple]) -> list[Triple]:

        async with self._get_driver() as driver:
            async with driver.session() as session:
                await session.execute_write(create_triples, perms=perms)

        new_perms = [Triple(subject_uuid=perm.subject_uuid,
                            predicate=perm.predicate,
                            object_uuid=perm.object_uuid)
                     for perm in perms]
        return new_perms

    async def read(self,
                   subject_uuids: Iterable[UUID] = None,
                   predicates: Iterable[str] = None,
                   object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

        async with self._get_driver() as driver:
            async with driver.session() as session: # noqa
                pass

    async def delete(self,
                     subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> list[PermTriple]:

        async with self._get_driver() as driver:
            async with driver.session() as session: # noqa
                pass
