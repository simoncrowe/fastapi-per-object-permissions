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

# Running

Different configurations of the app can be run using
docker-compose files in the root of this repository. For example:

```shell
docker-compose -f docker-compose-in-memory.yml up
```

Once the image is built and the containers are running, you should be
able to read the Swagger docs at http://127.0.0.1:8008/docs

# Testing

The integration tests are also run using docker compose. For example,
this will run the integration tests against the Redis backend:

```shell
docker-compose -f docker-compose-mongodb-tests.yml up --build --renew-anon-volume
```

## Test Performance
When one of the test docker-compose files is brought up and the tests
are allowed to run to completion, a junit XML file will be added to
the test\_output directory in the root of the repo.

The `compare_test_durations.py` script can be used to print a comparison of
each database backend's latest durations for each test.

Below is an example for the tests executed on a 2019 ThinkPad X1 Carbon
running the Ubuntu OS. 

The relatively simple MongoDB implementation's overall performance 
is beaten only by the in-memory implementation based on python sets.
The neo4j implementation struggles with inserting large numbers
of nodes and edges but otherwise generally outperforms the redis
implementation.

(This isn't intended as an objective database benchmark, but rather
an exercise in curiosity based on quick implementations of the same interface.)
```
FASTEST DURATIONS FOR EACH TEST

integration.test_api::test_create_and_delete_many
  in-memory: 6.009 seconds
  mongodb: 8.957 seconds
  postgres: 13.326 seconds
  redis: 14.402 seconds
  neo4j: 206.429 seconds

integration.test_api::test_create_and_delete_one
  in-memory: 0.011 seconds
  redis: 0.013 seconds
  mongodb: 0.050 seconds
  postgres: 0.060 seconds
  neo4j: 0.108 seconds

integration.test_api::test_create_and_read_many
  in-memory: 5.805 seconds
  mongodb: 8.007 seconds
  postgres: 13.003 seconds
  redis: 13.326 seconds
  neo4j: 218.268 seconds

integration.test_api::test_create_and_read_one
  in-memory: 0.006 seconds
  redis: 0.008 seconds
  postgres: 0.027 seconds
  mongodb: 0.036 seconds
  neo4j: 0.104 seconds

integration.test_api::test_create_many
  in-memory: 3.666 seconds
  mongodb: 4.824 seconds
  redis: 8.782 seconds
  postgres: 9.651 seconds
  neo4j: 183.594 seconds

integration.test_api::test_create_one
  in-memory: 0.003 seconds
  redis: 0.004 seconds
  mongodb: 0.017 seconds
  neo4j: 0.018 seconds
  postgres: 0.024 seconds

integration.test_api::test_delete_filter_by_many_predicates
  in-memory: 1.572 seconds
  postgres: 2.118 seconds
  mongodb: 2.355 seconds
  neo4j: 5.146 seconds
  redis: 5.546 seconds

integration.test_api::test_delete_filter_by_multiple_object_uuids[object_uuid_slice0-2500]
  in-memory: 0.170 seconds
  postgres: 0.181 seconds
  mongodb: 0.246 seconds
  redis: 0.437 seconds
  neo4j: 0.594 seconds

integration.test_api::test_delete_filter_by_multiple_object_uuids[object_uuid_slice1-5000]
  postgres: 0.333 seconds
  in-memory: 0.398 seconds
  mongodb: 0.414 seconds
  redis: 0.758 seconds
  neo4j: 0.861 seconds

integration.test_api::test_delete_filter_by_multiple_object_uuids[object_uuid_slice2-10000]
  in-memory: 0.682 seconds
  postgres: 0.682 seconds
  mongodb: 0.916 seconds
  redis: 1.246 seconds
  neo4j: 1.893 seconds

integration.test_api::test_delete_filter_by_multiple_subject_uuids[subject_uuid_slice0-2500]
  postgres: 0.153 seconds
  mongodb: 0.245 seconds
  in-memory: 0.267 seconds
  neo4j: 0.504 seconds
  redis: 0.505 seconds

integration.test_api::test_delete_filter_by_multiple_subject_uuids[subject_uuid_slice1-5000]
  mongodb: 0.339 seconds
  postgres: 0.342 seconds
  in-memory: 0.464 seconds
  redis: 0.689 seconds
  neo4j: 0.843 seconds

integration.test_api::test_delete_filter_by_multiple_subject_uuids[subject_uuid_slice2-10000]
  postgres: 0.670 seconds
  in-memory: 0.719 seconds
  mongodb: 0.845 seconds
  redis: 1.157 seconds
  neo4j: 1.836 seconds

integration.test_api::test_delete_filter_by_object_uuid[0]
  in-memory: 0.065 seconds
  mongodb: 0.067 seconds
  postgres: 0.083 seconds
  neo4j: 0.198 seconds
  redis: 0.240 seconds

integration.test_api::test_delete_filter_by_object_uuid[24]
  mongodb: 0.056 seconds
  in-memory: 0.067 seconds
  postgres: 0.082 seconds
  neo4j: 0.129 seconds
  redis: 0.278 seconds

integration.test_api::test_delete_filter_by_object_uuid[49]
  mongodb: 0.057 seconds
  in-memory: 0.063 seconds
  postgres: 0.068 seconds
  neo4j: 0.181 seconds
  redis: 0.270 seconds

integration.test_api::test_delete_filter_by_object_uuid[99]
  mongodb: 0.054 seconds
  postgres: 0.057 seconds
  in-memory: 0.065 seconds
  neo4j: 0.138 seconds
  redis: 0.248 seconds

integration.test_api::test_delete_filter_by_predicate
  in-memory: 0.595 seconds
  postgres: 0.676 seconds
  mongodb: 0.842 seconds
  neo4j: 1.696 seconds
  redis: 1.804 seconds

integration.test_api::test_delete_filter_by_predicate_and_nonexistent_object_uuid
  postgres: 0.018 seconds
  mongodb: 0.023 seconds
  in-memory: 0.030 seconds
  neo4j: 0.193 seconds
  redis: 0.203 seconds

integration.test_api::test_delete_filter_by_predicate_and_nonexistent_subject_uuid
  postgres: 0.016 seconds
  mongodb: 0.026 seconds
  in-memory: 0.040 seconds
  neo4j: 0.077 seconds
  redis: 0.193 seconds

integration.test_api::test_delete_filter_by_predicate_and_object_uuid
  in-memory: 0.037 seconds
  postgres: 0.039 seconds
  mongodb: 0.044 seconds
  neo4j: 0.211 seconds
  redis: 0.217 seconds

integration.test_api::test_delete_filter_by_predicate_and_subject_uuid
  mongodb: 0.023 seconds
  postgres: 0.030 seconds
  in-memory: 0.043 seconds
  neo4j: 0.135 seconds
  redis: 0.208 seconds

integration.test_api::test_delete_filter_by_predicate_subject_and_object_uuid
  mongodb: 0.019 seconds
  postgres: 0.027 seconds
  in-memory: 0.037 seconds
  neo4j: 0.083 seconds
  redis: 0.191 seconds

integration.test_api::test_delete_filter_by_subject_uuid[0]
  mongodb: 0.050 seconds
  in-memory: 0.065 seconds
  postgres: 0.121 seconds
  neo4j: 0.150 seconds
  redis: 0.246 seconds

integration.test_api::test_delete_filter_by_subject_uuid[24]
  in-memory: 0.062 seconds
  mongodb: 0.068 seconds
  postgres: 0.076 seconds
  neo4j: 0.145 seconds
  redis: 0.251 seconds

integration.test_api::test_delete_filter_by_subject_uuid[49]
  mongodb: 0.060 seconds
  in-memory: 0.065 seconds
  neo4j: 0.111 seconds
  postgres: 0.121 seconds
  redis: 0.255 seconds

integration.test_api::test_delete_filter_by_subject_uuid[99]
  mongodb: 0.051 seconds
  postgres: 0.053 seconds
  in-memory: 0.068 seconds
  neo4j: 0.124 seconds
  redis: 0.259 seconds

integration.test_api::test_read_filter_by_many_predicates
  in-memory: 1.486 seconds
  mongodb: 2.012 seconds
  postgres: 2.136 seconds
  neo4j: 4.433 seconds
  redis: 5.820 seconds

integration.test_api::test_read_filter_by_multiple_object_uuids[object_uuid_slice0-2500]
  in-memory: 0.175 seconds
  postgres: 0.196 seconds
  mongodb: 0.216 seconds
  redis: 0.370 seconds
  neo4j: 0.436 seconds

integration.test_api::test_read_filter_by_multiple_object_uuids[object_uuid_slice1-5000]
  in-memory: 0.324 seconds
  postgres: 0.340 seconds
  mongodb: 0.367 seconds
  redis: 0.632 seconds
  neo4j: 0.839 seconds

integration.test_api::test_read_filter_by_multiple_object_uuids[object_uuid_slice2-10000]
  postgres: 0.628 seconds
  in-memory: 0.661 seconds
  mongodb: 0.735 seconds
  redis: 1.035 seconds
  neo4j: 1.525 seconds

integration.test_api::test_read_filter_by_multiple_subject_uuids[subject_uuid_slice0-2500]
  in-memory: 0.166 seconds
  postgres: 0.170 seconds
  mongodb: 0.179 seconds
  redis: 0.375 seconds
  neo4j: 0.412 seconds

integration.test_api::test_read_filter_by_multiple_subject_uuids[subject_uuid_slice1-5000]
  postgres: 0.291 seconds
  in-memory: 0.302 seconds
  mongodb: 0.345 seconds
  redis: 0.629 seconds
  neo4j: 0.838 seconds

integration.test_api::test_read_filter_by_multiple_subject_uuids[subject_uuid_slice2-10000]
  postgres: 0.600 seconds
  mongodb: 0.617 seconds
  in-memory: 0.650 seconds
  redis: 1.067 seconds
  neo4j: 1.477 seconds

integration.test_api::test_read_filter_by_object_uuid[0]
  mongodb: 0.042 seconds
  postgres: 0.054 seconds
  in-memory: 0.061 seconds
  neo4j: 0.128 seconds
  redis: 0.238 seconds

integration.test_api::test_read_filter_by_object_uuid[24]
  mongodb: 0.043 seconds
  postgres: 0.049 seconds
  in-memory: 0.059 seconds
  neo4j: 0.124 seconds
  redis: 0.235 seconds

integration.test_api::test_read_filter_by_object_uuid[49]
  postgres: 0.055 seconds
  in-memory: 0.059 seconds
  mongodb: 0.062 seconds
  neo4j: 0.100 seconds
  redis: 0.254 seconds

integration.test_api::test_read_filter_by_object_uuid[99]
  mongodb: 0.042 seconds
  postgres: 0.049 seconds
  in-memory: 0.063 seconds
  neo4j: 0.117 seconds
  redis: 0.240 seconds

integration.test_api::test_read_filter_by_predicate
  in-memory: 0.495 seconds
  mongodb: 0.604 seconds
  postgres: 0.716 seconds
  neo4j: 1.657 seconds
  redis: 1.767 seconds

integration.test_api::test_read_filter_by_predicate_and_nonexistent_object_uuid
  mongodb: 0.021 seconds
  in-memory: 0.029 seconds
  postgres: 0.030 seconds
  neo4j: 0.063 seconds
  redis: 0.190 seconds

integration.test_api::test_read_filter_by_predicate_and_nonexistent_subject_uuid
  postgres: 0.015 seconds
  mongodb: 0.016 seconds
  in-memory: 0.036 seconds
  neo4j: 0.071 seconds
  redis: 0.192 seconds

integration.test_api::test_read_filter_by_predicate_and_object_uuid
  mongodb: 0.022 seconds
  postgres: 0.033 seconds
  in-memory: 0.035 seconds
  neo4j: 0.055 seconds
  redis: 0.221 seconds

integration.test_api::test_read_filter_by_predicate_and_subject_uuid
  mongodb: 0.021 seconds
  postgres: 0.022 seconds
  in-memory: 0.043 seconds
  neo4j: 0.203 seconds
  redis: 0.256 seconds

integration.test_api::test_read_filter_by_predicate_subject_and_object_uuid
  postgres: 0.016 seconds
  in-memory: 0.036 seconds
  mongodb: 0.036 seconds
  neo4j: 0.104 seconds
  redis: 0.180 seconds

integration.test_api::test_read_filter_by_subject_uuid[0]
  mongodb: 0.046 seconds
  postgres: 0.053 seconds
  in-memory: 0.059 seconds
  redis: 0.223 seconds
  neo4j: 0.227 seconds

integration.test_api::test_read_filter_by_subject_uuid[24]
  mongodb: 0.043 seconds
  postgres: 0.043 seconds
  in-memory: 0.061 seconds
  neo4j: 0.119 seconds
  redis: 0.228 seconds

integration.test_api::test_read_filter_by_subject_uuid[49]
  in-memory: 0.058 seconds
  mongodb: 0.060 seconds
  postgres: 0.091 seconds
  neo4j: 0.140 seconds
  redis: 0.249 seconds

integration.test_api::test_read_filter_by_subject_uuid[99]
  postgres: 0.043 seconds
  in-memory: 0.057 seconds
  mongodb: 0.070 seconds
  neo4j: 0.103 seconds
  redis: 0.240 seconds


BACKEND_NAME         TOTAL_DURATION
in-memory            25.989 seconds
mongodb              34.290 seconds
postgres             47.667 seconds
redis                66.377 seconds
neo4j                636.940 seconds
```
