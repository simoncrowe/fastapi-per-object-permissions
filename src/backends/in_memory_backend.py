from typing import Iterable, Set, Tuple
from uuid import UUID

from protocols import PerObjectPermissionBackend


class InMemoryBackend(PerObjectPermissionBackend):
    """Stores per-object permission triples in memory."""

    def __init__(self, initial_data: Iterable[Tuple[UUID, str, UUID]] = None):
        self._data = set(initial_data) if initial_data else set()

    def __iter__(self):
        return iter(self._data)

    def create(self,
               subject_uuid: UUID,
               predicate: str,
               object_uuid: UUID) -> Tuple[UUID, str, UUID]:
        self._data.add((subject_uuid, predicate, object_uuid))

    def read(self,
             subject_uuids: Iterable[UUID] = None,
             predicates: Iterable[str] = None,
             object_uuids: Iterable[UUID] = None) -> Set[Tuple[UUID, str, UUID]]:

        def pred(triple):
            subject_uuid, predicate, object_uuid = triple

            if subject_uuids and subject_uuid not in subject_uuids:
                return False
            if predicates and predicate not in predicates:
                return False
            if object_uuids and object_uuid not in object_uuids:
                return False

            return True

        return set(filter(pred, self._data))

    def delete(self,
               subject_uuids: Iterable[UUID] = None,
               predicates: Iterable[str] = None,
               object_uuids: Iterable[UUID] = None):
        pass
