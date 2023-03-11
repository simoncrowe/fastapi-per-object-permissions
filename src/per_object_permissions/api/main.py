"""HTTP API for creating, reading and deleting permissions.

A RESTful API would be cumbersome for use cases like bulk creation and deletion.
Additionally, it would not add much value to identify permissions in URLs.
A RPC approach is used instead.
"""
from functools import cache
from importlib import import_module
from typing import List

import fastapi

from per_object_permissions import protocols
from per_object_permissions.api import config, schema

app = fastapi.FastAPI()


@cache
def get_settings():
    return config.Settings()


@cache
def get_backend() -> protocols.PerObjectPermissionBackend:
    settings = get_settings()
    module_path, class_name = settings.backend.split("::")
    backend_class = getattr(import_module(module_path), class_name)
    return backend_class(settings=settings)


@app.post("/create-perms", response_model=schema.CreateResults)
async def create_perms(perms: List[schema.PermTriple]):
    backend = get_backend()
    created_perms = await backend.create(perms)
    return {"created": [schema.PermTriple.from_orm(perm) for perm in created_perms]}


@app.post("/read-perms", response_model=schema.ReadResults)
async def read_perms(query: schema.PermQuery):
    backend = get_backend()
    perms = await backend.read(**query.dict())
    return {"results": [schema.PermTriple.from_orm(perm) for perm in perms]}


@app.post("/delete-perms", response_model=schema.DeleteResults)
async def delete_perms(query: schema.PermQuery):
    backend = get_backend()
    perms = await backend.delete(**query.dict())
    return {"deleted": [schema.PermTriple.from_orm(perm) for perm in perms]}
