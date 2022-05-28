from typing import Callable, Iterable, Set, Tuple
from uuid import UUID

from per_object_permissions.protocols import PerObjectPermissionBackend


def _filter_pred(subject_uuids: Iterable[UUID] = None,
                 predicates: Iterable[str] = None,
                 object_uuids: Iterable[UUID] = None) -> Callable:
    """Returns a predicate function for filtering permission triples."""

    def pred(triple):
        subject_uuid, predicate, object_uuid = triple

        if subject_uuids and subject_uuid not in subject_uuids:
            return False
        if predicates and predicate not in predicates:
            return False
        if object_uuids and object_uuid not in object_uuids:
            return False

        return True

    return pred


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

        triple = (subject_uuid, predicate, object_uuid)
        self._data.add(triple)
        return triple

    def read(self,
             subject_uuids: Iterable[UUID] = None,
             predicates: Iterable[str] = None,
             object_uuids: Iterable[UUID] = None) -> Set[Tuple[UUID, str, UUID]]:

        pred = _filter_pred(subject_uuids, predicates, object_uuids)
        return set(filter(pred, self._data))

    def delete(self,
               subject_uuids: Iterable[UUID] = None,
               predicates: Iterable[str] = None,
               object_uuids: Iterable[UUID] = None):

        pred = _filter_pred(subject_uuids, predicates, object_uuids)
        to_delete = filter(pred, self._data)
        self._data = self._data.difference(to_delete)
