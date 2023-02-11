from collections import namedtuple
from typing import Callable, Iterable, Iterator
from uuid import UUID

from more_itertools import chunked
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
    perms_data = (
        {"subject_uuid": str(perm.subject_uuid),
         "predicate": perm.predicate,
         "object_uuid": str(perm.object_uuid)}
        for perm in perms
    )
    query = (
        "UNWIND $perms as perm "
        "MERGE "
        "(:NODE {uuid: perm.subject_uuid})"
        "-[:PREDICATE {predicate: perm.predicate}]->"
        "(:NODE {uuid: perm.object_uuid })"
    )
    for perms_chunk in chunked(perms_data, 100):
        await tx.run(query, perms=perms_chunk)


def _where_clause_parts(subject_uuids: Iterable[UUID] = None,
                        predicates: Iterable[str] = None,
                        object_uuids: Iterable[UUID] = None) -> Iterator[tuple[str, list]]:
    if subject_uuids:
        sub_key = "subject_uuids"
        yield f"subject.uuid IN ${sub_key}", sub_key, list(map(str, subject_uuids))
    if predicates:
        pred_key = "predicates"
        yield f"edge.predicate IN ${pred_key}", pred_key, list(predicates)
    if object_uuids:
        obj_key = "object_uuids"
        yield f"object.uuid IN ${obj_key}", obj_key, list(map(str, object_uuids))


def build_where_clause(
    subject_uuids: Iterable[UUID] = None,
    predicates: Iterable[str] = None,
    object_uuids: Iterable[UUID] = None
) -> tuple[tuple[str], dict[str, list[str]]]:
    parts = list(_where_clause_parts(subject_uuids, predicates, object_uuids))
    if not parts:
        return (), {}

    conditions, data_keys, data_values = zip(*parts)
    return conditions, dict(zip(data_keys, data_values))


async def read_triples(tx,
                       subject_uuids: Iterable[UUID] = None,
                       predicates: Iterable[str] = None,
                       object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

    path = "(subject:NODE)-[edge:PREDICATE]->(object:NODE)"
    where_conditions, where_data = build_where_clause(subject_uuids,
                                                      predicates,
                                                      object_uuids)
    conditions = " AND ".join(where_conditions)
    where_clause = f"WHERE {conditions}" if conditions else ""
    output = ("subject.uuid AS subject_uuid, "
              "edge.predicate AS predicate, "
              "object.uuid AS object_uuid ")

    result = await tx.run(f"MATCH {path} {where_clause} RETURN {output}", where_data)

    return [record.data() async for record in result]


async def delete_triples(tx,
                         subject_uuids: Iterable[UUID] = None,
                         predicates: Iterable[str] = None,
                         object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

    path = "(subject:NODE)-[edge:PREDICATE]->(object:NODE)"
    where_conditions, where_data = build_where_clause(subject_uuids,
                                                      predicates,
                                                      object_uuids)
    conditions = " AND ".join(where_conditions)
    where_clause = f"WHERE {conditions}" if conditions else ""
    with_clause = "WITH subject, object, edge, properties(edge) as deleted_edge"
    delete_clause = "DELETE edge"
    output = ("subject.uuid AS subject_uuid, "
              "deleted_edge.predicate AS predicate, "
              "object.uuid AS object_uuid ")

    result = await tx.run(f"MATCH {path} {where_clause} "
                          f"{with_clause} {delete_clause} RETURN {output}",
                          where_data)

    return [record.data() async for record in result]


class Neo4jBackend:
    """Stores per-object permission triples in Neo4j."""

    def __init__(self, settings, **kwargs):
        self._get_driver = driver_factory(settings.neo4j_user,
                                          settings.neo4j_password,
                                          settings.neo4j_host)
        self._indexes_created = False

    async def _ensure_indexes(self):
        if not self._indexes_created:
            async with self._get_driver() as driver:
                async with driver.session() as session:
                    await session.run("CREATE INDEX node_index FOR (n:NODE) ON (n.uuid)")
                    await session.run("CREATE INDEX pred_index FOR ()-[r:PREDICATE]-() "
                                      "ON (r.predicate)")
            self._indexes_created = True

    async def create(self, perms: Iterable[PermTriple]) -> list[Triple]:

        await self._ensure_indexes()

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

        await self._ensure_indexes()

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

        await self._ensure_indexes()

        async with self._get_driver() as driver:
            async with driver.session() as session: # noqa
                results = await session.execute_write(delete_triples,
                                                      subject_uuids=subject_uuids,
                                                      predicates=predicates,
                                                      object_uuids=object_uuids)
                return [Triple(**result) for result in results]
