This project is a work in progress.

# Introduction

The motivation for this project is partly autodidactic and partly a desire to build
a faster, simpler alternative to Django Guardian. Having used it in production,
I can say that is stable, works and has a simple API. However, this API hides a lot of complexity.
The SQL it emits is seldom optimal and the schemas involved are complex.

The key idea here is to do away with _generic foreign keys_ and other Django-isms.
All that this system requires is that entities are identified by UUIDs. Once this requirement is met,
the permission state can be persisted with this triple: `subject_uuid, verb, object_uuid`.
It doesn't matter what the entities are or whether they are stored in different databases,
universally unique identifiers make it possible to populate per-object permissions for them.
The simplicity of the data structure also means that it can be persisted in many types of databases
including graph and key-value.

# Testing and Running

Different configurations of the app can be run using docker-compose files in the root of this repository. For example:

```shell
docker-compose -f docker-compose-in-memory.yml up
```

Once the image is built and the container is running, you should be
able to read the Swagger docs at http://127.0.0.1:8008/docs
