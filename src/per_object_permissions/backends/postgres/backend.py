import time
from collections import namedtuple
from os import path
from typing import Iterable, Iterator, Set
from uuid import UUID

import psycopg2
from psycopg2.extras import execute_batch, register_uuid

from per_object_permissions.protocols import PermTriple

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])

QUERIES_PATH = path.join(path.dirname(path.abspath(__file__)), "queries")


def _load_query(name: str) -> str:
    with open(path.join(QUERIES_PATH, name), "r") as fileobj:
        return fileobj.read()


def _where_clause_parts(subject_uuids: Iterable[UUID] = None,
                        predicates: Iterable[str] = None,
                        object_uuids: Iterable[UUID] = None) -> Iterator[str]:
    if subject_uuids:
        yield "subject_uuid IN %s", tuple(subject_uuids)
    if predicates:
        yield "predicate IN %s", tuple(predicates)
    if object_uuids:
        yield "object_uuid IN %s", tuple(object_uuids)


def build_where_clause(
    subject_uuids: Iterable[UUID] = None,
    predicates: Iterable[str] = None,
    object_uuids: Iterable[UUID] = None
) -> tuple[tuple[str], tuple[str]]:
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

        register_uuid()

        ensure_table_query = _load_query("ensure_table_exists.sql")
        with self._make_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ensure_table_query)

        self._create_perms_query = _load_query("create_perms.sql")

    def _make_connection(self):
        for _ in range(5):
            try:
                return psycopg2.connect(host=self._db_host,
                                        dbname=self._db_name,
                                        user=self._db_user,
                                        password=self._db_password)
            except psycopg2.OperationalError:
                time.sleep(1)

    def create(self, perms: Iterable[PermTriple]) -> Set[Triple]:
        with self._make_connection() as connection:
            with connection.cursor() as cursor:
                perm_data = [(str(perm.subject_uuid),
                              perm.predicate,
                              str(perm.object_uuid))
                             for perm in perms]
                execute_batch(cursor, self._create_perms_query, perm_data)

        return set(Triple(*perm) for perm in perm_data)

    def read(self,
             subject_uuids: Iterable[UUID] = None,
             predicates: Iterable[str] = None,
             object_uuids: Iterable[UUID] = None) -> Set[Triple]:
        with self._make_connection() as connection:
            select_clause = "SELECT subject_uuid, predicate, object_uuid FROM perms"
            where_conditions, where_values = build_where_clause(subject_uuids,
                                                                predicates,
                                                                object_uuids)
            if where_conditions:
                where_clause = f"WHERE {' AND '.join(where_conditions)}"
                with connection.cursor() as cursor:
                    cursor.execute(f"{select_clause} {where_clause};", where_values)
                    return set(Triple(*row) for row in cursor.fetchall())
            else:
                with connection.cursor() as cursor:
                    cursor.execute(f"{select_clause};")
                    return set(Triple(*row) for row in cursor.fetchall())

    def delete(self,
               subject_uuids: Iterable[UUID] = None,
               predicates: Iterable[str] = None,
               object_uuids: Iterable[UUID] = None) -> Set[Triple]:

        with self._make_connection() as connection:
            delete_clause = "DELETE FROM perms"
            returning_clause = "RETURNING subject_uuid, predicate, object_uuid"

            where_conditions, where_values = build_where_clause(subject_uuids,
                                                                predicates,
                                                                object_uuids)
            if where_conditions:
                where_clause = f"WHERE {' AND '.join(where_conditions)}"
                with connection.cursor() as cursor:
                    cursor.execute(f"{delete_clause} {where_clause} {returning_clause};", where_values)
                    return set(Triple(*row) for row in cursor.fetchall())
            else:
                with connection.cursor() as cursor:
                    cursor.execute(f"{delete_clause} {returning_clause};")
                    return set(Triple(*row) for row in cursor.fetchall())
