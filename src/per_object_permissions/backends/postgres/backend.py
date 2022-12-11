import asyncio
from collections import namedtuple
from os import path
from typing import Iterable, Iterator, Set
from uuid import UUID

import psycopg

from per_object_permissions.protocols import PermTriple

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])

QUERIES_PATH = path.join(path.dirname(path.abspath(__file__)), "queries")


def _load_query(name: str) -> str:
    with open(path.join(QUERIES_PATH, name), "r") as fileobj:
        return fileobj.read()


def _where_clause_parts(subject_uuids: Iterable[UUID] = None,
                        predicates: Iterable[str] = None,
                        object_uuids: Iterable[UUID] = None) -> Iterator[tuple[str, list]]:
    if subject_uuids:
        yield "subject_uuid = ANY(%s)", list(subject_uuids)
    if predicates:
        yield "predicate = ANY(%s)", list(predicates)
    if object_uuids:
        yield "object_uuid = ANY(%s)", list(object_uuids)


def build_where_clause(
    subject_uuids: Iterable[UUID] = None,
    predicates: Iterable[str] = None,
    object_uuids: Iterable[UUID] = None
) -> tuple[tuple[str], tuple[list[str | UUID]]]:
    parts = list(_where_clause_parts(subject_uuids, predicates, object_uuids))
    if not parts:
        return (), ()

    return tuple(zip(*parts))


class PostgresBackend:
    """Stores per-object permission triples in PostgreSQL.

    This implementation uses RAW SQL.
    """

    def __init__(self, settings=None, **kwargs):
        self._db_host = settings.postgres_host
        self._db_name = settings.postgres_dbname
        self._db_user = settings.postgres_user
        self._db_password = settings.postgres_password
        self._create_perms_query = _load_query("create_perms.sql")
        self._table_initialized = False

    async def _make_connection(self):
        for _ in range(5):
            try:
                return await psycopg.AsyncConnection.connect(host=self._db_host,
                                                             dbname=self._db_name,
                                                             user=self._db_user,
                                                             password=self._db_password)
            except psycopg.OperationalError:
                await asyncio.sleep(1)

    async def _ensure_table(self):
        if not self._table_initialized:
            ensure_table_query = _load_query("ensure_table_exists.sql")
            async with await self._make_connection() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(ensure_table_query)
                    self._table_initialized = True

    async def create(self, perms: Iterable[PermTriple]) -> Set[Triple]:
        await self._ensure_table()
        async with await self._make_connection() as connection:
            async with connection.cursor() as cursor:
                perm_data = [(str(perm.subject_uuid),
                              perm.predicate,
                              str(perm.object_uuid))
                             for perm in perms]
                await cursor.executemany(self._create_perms_query, perm_data)

        return set(Triple(*perm) for perm in perm_data)

    async def read(self,
                   subject_uuids: Iterable[UUID] = None,
                   predicates: Iterable[str] = None,
                   object_uuids: Iterable[UUID] = None) -> Set[Triple]:

        await self._ensure_table()
        async with await self._make_connection() as connection:
            select_clause = "SELECT subject_uuid, predicate, object_uuid FROM perms"
            where_conditions, where_values = build_where_clause(subject_uuids,
                                                                predicates,
                                                                object_uuids)
            if where_conditions:
                where_clause = f"WHERE {' AND '.join(where_conditions)}"
                async with connection.cursor() as cursor:
                    await cursor.execute(f"{select_clause} {where_clause};", where_values)
                    results = await cursor.fetchall()
                    return set(Triple(*row) for row in results)
            else:
                async with connection.cursor() as cursor:
                    await cursor.execute(f"{select_clause};")
                    results = await cursor.fetchall()
                    return set(Triple(*row) for row in results)

    async def delete(self,
                     subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> Set[Triple]:

        await self._ensure_table()
        async with await self._make_connection() as connection:
            delete_clause = "DELETE FROM perms"
            returning_clause = "RETURNING subject_uuid, predicate, object_uuid"

            where_conditions, where_values = build_where_clause(subject_uuids,
                                                                predicates,
                                                                object_uuids)
            if where_conditions:
                where_clause = f"WHERE {' AND '.join(where_conditions)}"
                async with connection.cursor() as cursor:
                    await cursor.execute(f"{delete_clause} {where_clause} {returning_clause};", where_values)
                    results = await cursor.fetchall()
                    return set(Triple(*row) for row in results)
            else:
                async with connection.cursor() as cursor:
                    await cursor.execute(f"{delete_clause} {returning_clause};")
                    results = await cursor.fetchall()
                    return set(Triple(*row) for row in results)
