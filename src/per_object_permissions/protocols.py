from typing import Iterable, Protocol
from uuid import UUID


class PermTriple(Protocol):
    subject_uuid: UUID
    predicate: str
    object_uuid: UUID


class PerObjectPermissionBackend(Protocol):
    async def create(self, perms: Iterable[PermTriple]) -> Iterable[PermTriple]:
        """Create a permission triple linking a subject and object via a predicate.

        This method persists the fact that some entity can perform some action
        on some other entity.
        """

    async def read(self,
                   subject_uuids: Iterable[UUID] = None,
                   predicates: Iterable[str] = None,
                   object_uuids: Iterable[UUID] = None) -> Iterable[PermTriple]:
        """Query permission triples for any combination or subjects, objects and predicates.

        If no arguments are passed in, all permission triples will be returned.
        """

    async def delete(self,
                     subject_uuids: Iterable[UUID] = None,
                     predicates: Iterable[str] = None,
                     object_uuids: Iterable[UUID] = None) -> Iterable[PermTriple]:
        """Delete permission triples for any combination or subjects, objects and predicates.

        If no arguments are passed in, all permission triples will be deleted.
        """
