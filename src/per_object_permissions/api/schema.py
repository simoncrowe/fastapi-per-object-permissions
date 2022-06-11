import uuid
from typing import List

import pydantic


class PermTriple(pydantic.BaseModel):
    subject_uuid: uuid.UUID
    predicate: str
    object_uuid: uuid.UUID


class CreatedBody(pydantic.BaseModel):
    created: List[PermTriple]
