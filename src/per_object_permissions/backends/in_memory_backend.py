from collections import namedtuple
from typing import Callable, Iterable, Set
from uuid import UUID

from per_object_permissions.protocols import (PermTriple,
                                              PerObjectPermissionBackend)

Triple = namedtuple("PermTriple", ["subject_uuid", "predicate", "object_uuid"])


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

    def __init__(self, initial_data: Iterable[PermTriple] = None, **kwargs):
        self._data = set(initial_data) if initial_data else set()

    def __iter__(self):
        return iter(self._data)

    def create(self, perms: Iterable[PermTriple]) -> Set[Triple]:
        triples = [
            Triple(perm.subject_uuid, perm.predicate, perm.object_uuid)
            for perm in perms
        ]
        self._data.update(triples)
        return triples

    def read(self,
             subject_uuids: Iterable[UUID] = None,
             predicates: Iterable[str] = None,
             object_uuids: Iterable[UUID] = None) -> Set[Triple]:

        pred = _filter_pred(subject_uuids, predicates, object_uuids)
        return set(filter(pred, self._data))

    def delete(self,
               subject_uuids: Iterable[UUID] = None,
               predicates: Iterable[str] = None,
               object_uuids: Iterable[UUID] = None) -> Set[Triple]:

        pred = _filter_pred(subject_uuids, predicates, object_uuids)
        to_delete = set(filter(pred, self._data))
        self._data = self._data.difference(to_delete)
        return to_delete
