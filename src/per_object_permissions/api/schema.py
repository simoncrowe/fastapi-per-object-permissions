import uuid

import pydantic


class PermTriple(pydantic.BaseModel):
    subject_uuid: uuid.UUID
    predicate: str
    object_uuid: uuid.UUID
