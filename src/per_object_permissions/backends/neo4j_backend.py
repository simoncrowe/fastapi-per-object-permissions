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


async def create_triples(tx, perms: Iterable[PermTriple]):
    def iter_query_data():
        counter = count()
        node_ids = {}
        for perm in perms:
            subject_name = node_ids.setdefault(perm.subject_uuid, f"n{next(counter)}")
            object_name = node_ids.setdefault(perm.object_uuid, f"n{next(counter)}")

            yield (f'({subject_name} {{ uuid: "{perm.subject_uuid}" }}) '
                   f'-[:PREDICATE {{predicate: "{perm.predicate}"}}]-> '
                   f'({object_name} {{ uuid: "{perm.object_uuid}" }})')

    return await tx.run(f"MERGE {', '.join(iter_query_data())};")


def _iter_where_query_parts(subject_uuids: Iterable[UUID] = None,
                            predicates: Iterable[str] = None,
                            object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:
    if subject_uuids:
        yield f"subject.uuid IN {subject_uuids}"
    if predicates:
        yield f"edge.predicate IN {predicates}"
    if object_uuids:
        yield f"object.uuid IN {object_uuids}"


async def read_triples(tx,
                       subject_uuids: Iterable[UUID] = None,
                       predicates: Iterable[str] = None,
                       object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

    path = "(subject)-[edge:PREDICATE]-(object)"
    conditions = " AND ".join(_iter_where_query_parts(subject_uuids,
                                                      predicates,
                                                      object_uuids))
    where_clause = "WHERE {conditions}" if conditions else ""
    output = ("subject.uuid AS subject_uuid, "
              "edge.predicate AS predicate, "
              "object.uuid AS object_uuid ")

    result = await tx.run(f"MATCH {path} {where_clause} RETURN {output}")

    return [record.data() async for record in result]


async def delete_triples(tx,
                         subject_uuids: Iterable[UUID] = None,
                         predicates: Iterable[str] = None,
                         object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

    path = "(subject)-[edge:PREDICATE]-(object)"
    conditions = " AND ".join(_iter_where_query_parts(subject_uuids,
                                                      predicates,
                                                      object_uuids))
    where_clause = "WHERE {conditions}" if conditions else ""
    with_clause = "WITH properties(edge) as deleted_edge"
    delete_clause = "DELETE edge"
    output = ("subject.uuid AS subject_uuid, "
              "deleted_edge.predicate AS predicate, "
              "object.uuid AS object_uuid ")

    result = await tx.run(f"MATCH {path} {where_clause} "
                          f"{with_clause} {delete_clause} RETURN {output}")

    return [record.data() async for record in result]


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

        return [Triple(subject_uuid=perm.subject_uuid,
                       predicate=perm.predicate,
                       object_uuid=perm.object_uuid)
                for perm in perms]

    async def read(self,
                   subject_uuids: Iterable[UUID] = None,
                   predicates: Iterable[str] = None,
                   object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

        async with self._get_driver() as driver:
            async with driver.session() as session: # noqa
                results = await session.execute_read(read_triples,
                                                     subject_uuids=subject_uuids,
                                                     predicates=predicates,
                                                     object_uuids=object_uuids)
                return [Triple(**result) for result in results]

    async def delete(self,
                     subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> list[PermTriple]:

        async with self._get_driver() as driver:
            async with driver.session() as session: # noqa
                results = await session.execute_write(delete_triples,
                                                      subject_uuids=subject_uuids,
                                                      predicates=predicates,
                                                      object_uuids=object_uuids)
                return [Triple(**result) for result in results]
