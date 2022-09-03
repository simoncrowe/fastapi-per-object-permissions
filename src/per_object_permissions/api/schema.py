import uuid
from typing import List, Optional

import pydantic


class PermTriple(pydantic.BaseModel):
    subject_uuid: uuid.UUID
    predicate: str
    object_uuid: uuid.UUID


class PermQuery(pydantic.BaseModel):
    subject_uuids: Optional[List[uuid.UUID]]
    predicates: Optional[List[str]]
    object_uuids: Optional[List[uuid.UUID]]


class CreateResults(pydantic.BaseModel):
    created: List[PermTriple]


class ReadResults(pydantic.BaseModel):
    results: List[PermTriple]
