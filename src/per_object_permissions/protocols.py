from typing import Iterable, Protocol, Set, Tuple
from uuid import UUID


class PerObjectPermissionBackend(Protocol):
    def create(self,
               subject_uuid: UUID,
               predicate: str,
               object_uuid: UUID) -> Tuple[UUID, str, UUID]:
        """Create a permission triple linking a subject and object via a predicate.

        This method persists the fact that some entity can perform some action
        on some other entity.
        """

    def read(self,
             subject_uuids: Iterable[UUID] = None,
             predicates: Iterable[str] = None,
             object_uuids: Iterable[UUID] = None) -> Set[Tuple[UUID, str, UUID]]:
        """Query permission triples for any combination or subjects, objects and predicates.

        If no arguments are passed in, all permission triples will be returned.
        """

    def delete(self,
               subject_uuids: Iterable[UUID] = None,
               predicates: Iterable[str] = None,
               object_uuids: Iterable[UUID] = None):
        """Delete permission triples for any combination or subjects, objects and predicates.

        If no arguments are passed in, all permission triples will be deleted.
        """
