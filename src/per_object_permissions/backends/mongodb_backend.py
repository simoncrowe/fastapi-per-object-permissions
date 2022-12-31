from collections import namedtuple
from typing import Callable, Iterable, Iterator
from urllib.parse import quote_plus
from uuid import UUID

from motor import motor_asyncio

from per_object_permissions.protocols import PermTriple

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


def client_factory(username: str, password: str, host: str) -> Callable:
    def get_client():
        db_url = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}"
        return motor_asyncio.AsyncIOMotorClient(db_url, uuidRepresentation='standard')
    return get_client


def query_key_values(subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> Iterator[tuple[str, str | UUID]]:

    if subject_uuids:
        yield "subject_uuid", {"$in": subject_uuids}

    if predicates:
        yield "predicate", {"$in": predicates}

    if object_uuids:
        yield "object_uuid", {"$in": object_uuids}


class MongoBackend:
    """Stores per-object permission triples in MongoDB."""

    def __init__(self, settings, **kwargs):
        self._get_client = client_factory(settings.mongo_user,
                                          settings.mongo_password,
                                          settings.mongo_host)
        self._indexes_created = False

    async def _ensure_indexes(self):
        if not self._indexes_created:
            client = self._get_client()
            await client.db.perms.create_index("subject_uuid")
            await client.db.perms.create_index("object_uuid")
            self._indexes_created = True

    async def create(self, perms: Iterable[PermTriple]) -> list[Triple]:

        await self._ensure_indexes()
        client = self._get_client()

        new_perms = [Triple(subject_uuid=perm.subject_uuid,
                            predicate=perm.predicate,
                            object_uuid=perm.object_uuid)
                     for perm in perms]
        await client.db.perms.insert_many(perm._asdict() for perm in new_perms)
        return new_perms

    async def read(self,
                   subject_uuids: Iterable[UUID] = None,
                   predicates: Iterable[str] = None,
                   object_uuids: Iterable[UUID] = None) -> Iterator[Triple]:

        await self._ensure_indexes()
        client = self._get_client()

        query = dict(query_key_values(subject_uuids, predicates, object_uuids))
        results = list()
        async for perm_doc in client.db.perms.find(query):
            del perm_doc["_id"]
            results.append(Triple(**perm_doc))
        return results

    async def delete(self,
                     subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> list[PermTriple]:

        await self._ensure_indexes()
        client = self._get_client()

        query = dict(query_key_values(subject_uuids, predicates, object_uuids))
        results, ids_to_delete = list(), list()
        async for perm_doc in client.db.perms.find(query):
            ids_to_delete.append(perm_doc.pop("_id"))
            results.append(Triple(**perm_doc))
        await client.db.perms.delete_many({"_id": {"$in": ids_to_delete}})
        return results
