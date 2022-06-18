"""HTTP API for creating, reading and deleting permissions.

A RESTful API would be cumbersome for use cases like bulk creation and deletion.
Additionally, identifying permissions in URIs would not add much value.
An RPC approach is used instead.
"""
from functools import lru_cache
from importlib import import_module
from typing import List

import fastapi

from per_object_permissions import protocols
from per_object_permissions.api import config, schema

app = fastapi.FastAPI()


@lru_cache()
def get_settings():
    return config.Settings()


@lru_cache()
def get_backend() -> protocols.PerObjectPermissionBackend:
    settings = get_settings()
    module_path, class_name = settings.backend.split("::")
    backend_class = getattr(import_module(module_path), class_name)
    return backend_class()


@app.post("/create_perms", response_model=schema.CreatedBody)
async def create_perms(perms: List[schema.PermTriple]):
    backend = get_backend()
    created_perms = backend.create(perms)
    return {"created": [perm._asdict() for perm in created_perms]}


@app.post("/read_perms", response_model=schema.ResultsBody)
async def read_perms(options: schema.PermFilter = None):
    filter_options = options.dict() if options else {}
    backend = get_backend()
    perms = backend.read(**filter_options)
    return {"results": [perm._asdict() for perm in perms]}
