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
running the Ubuntu OS. The relatively simple MongoDB implementation's performance
is beaten only by the in-memory implementation based on python sets.
The neo4j implementation struggles with inserting large numbers
of nodes and edges but otherwise generally outperforms the redis
implementation.

(This isn't intended as an objective database benchmark, but rather
an rough exercise in curiosity based on quick implementations
of the same interface.)
```
▶ python compare_test_durations.py
FASTEST DURATIONS FOR EACH TEST

integration.test_api::test_create_and_delete_many
  in-memory: 6.009
  mongodb: 8.957
  postgres: 13.326
  redis: 14.402
  neo4j: 206.429

integration.test_api::test_create_and_delete_one
  in-memory: 0.011
  redis: 0.013
  mongodb: 0.050
  postgres: 0.060
  neo4j: 0.108

integration.test_api::test_create_and_read_many
  in-memory: 5.805
  mongodb: 8.007
  postgres: 13.003
  redis: 13.326
  neo4j: 218.268

integration.test_api::test_create_and_read_one
  in-memory: 0.006
  redis: 0.008
  postgres: 0.027
  mongodb: 0.036
  neo4j: 0.104

integration.test_api::test_create_many
  in-memory: 3.666
  mongodb: 4.824
  redis: 8.782
  postgres: 9.651
  neo4j: 183.594

integration.test_api::test_create_one
  in-memory: 0.003
  redis: 0.004
  mongodb: 0.017
  neo4j: 0.018
  postgres: 0.024

integration.test_api::test_delete_filter_by_many_predicates
  in-memory: 1.572
  postgres: 2.118
  mongodb: 2.355
  neo4j: 5.146
  redis: 5.546

integration.test_api::test_delete_filter_by_multiple_object_uuids[object_uuid_slice0-2500]
  in-memory: 0.170
  postgres: 0.181
  mongodb: 0.246
  redis: 0.437
  neo4j: 0.594

integration.test_api::test_delete_filter_by_multiple_object_uuids[object_uuid_slice1-5000]
  postgres: 0.333
  in-memory: 0.398
  mongodb: 0.414
  redis: 0.758
  neo4j: 0.861

integration.test_api::test_delete_filter_by_multiple_object_uuids[object_uuid_slice2-10000]
  in-memory: 0.682
  postgres: 0.682
  mongodb: 0.916
  redis: 1.246
  neo4j: 1.893

integration.test_api::test_delete_filter_by_multiple_subject_uuids[subject_uuid_slice0-2500]
  postgres: 0.153
  mongodb: 0.245
  in-memory: 0.267
  neo4j: 0.504
  redis: 0.505

integration.test_api::test_delete_filter_by_multiple_subject_uuids[subject_uuid_slice1-5000]
  mongodb: 0.339
  postgres: 0.342
  in-memory: 0.464
  redis: 0.689
  neo4j: 0.843

integration.test_api::test_delete_filter_by_multiple_subject_uuids[subject_uuid_slice2-10000]
  postgres: 0.670
  in-memory: 0.719
  mongodb: 0.845
  redis: 1.157
  neo4j: 1.836

integration.test_api::test_delete_filter_by_object_uuid[0]
  in-memory: 0.065
  mongodb: 0.067
  postgres: 0.083
  neo4j: 0.198
  redis: 0.240

integration.test_api::test_delete_filter_by_object_uuid[24]
  mongodb: 0.056
  in-memory: 0.067
  postgres: 0.082
  neo4j: 0.129
  redis: 0.278

integration.test_api::test_delete_filter_by_object_uuid[49]
  mongodb: 0.057
  in-memory: 0.063
  postgres: 0.068
  neo4j: 0.181
  redis: 0.270

integration.test_api::test_delete_filter_by_object_uuid[99]
  mongodb: 0.054
  postgres: 0.057
  in-memory: 0.065
  neo4j: 0.138
  redis: 0.248

integration.test_api::test_delete_filter_by_predicate
  in-memory: 0.595
  postgres: 0.676
  mongodb: 0.842
  neo4j: 1.696
  redis: 1.804

integration.test_api::test_delete_filter_by_predicate_and_nonexistent_object_uuid
  postgres: 0.018
  mongodb: 0.023
  in-memory: 0.030
  neo4j: 0.193
  redis: 0.203

integration.test_api::test_delete_filter_by_predicate_and_nonexistent_subject_uuid
  postgres: 0.016
  mongodb: 0.026
  in-memory: 0.040
  neo4j: 0.077
  redis: 0.193

integration.test_api::test_delete_filter_by_predicate_and_object_uuid
  in-memory: 0.037
  postgres: 0.039
  mongodb: 0.044
  neo4j: 0.211
  redis: 0.217

integration.test_api::test_delete_filter_by_predicate_and_subject_uuid
  mongodb: 0.023
  postgres: 0.030
  in-memory: 0.043
  neo4j: 0.135
  redis: 0.208

integration.test_api::test_delete_filter_by_predicate_subject_and_object_uuid
  mongodb: 0.019
  postgres: 0.027
  in-memory: 0.037
  neo4j: 0.083
  redis: 0.191

integration.test_api::test_delete_filter_by_subject_uuid[0]
  mongodb: 0.050
  in-memory: 0.065
  postgres: 0.121
  neo4j: 0.150
  redis: 0.246

integration.test_api::test_delete_filter_by_subject_uuid[24]
  in-memory: 0.062
  mongodb: 0.068
  postgres: 0.076
  neo4j: 0.145
  redis: 0.251

integration.test_api::test_delete_filter_by_subject_uuid[49]
  mongodb: 0.060
  in-memory: 0.065
  neo4j: 0.111
  postgres: 0.121
  redis: 0.255

integration.test_api::test_delete_filter_by_subject_uuid[99]
  mongodb: 0.051
  postgres: 0.053
  in-memory: 0.068
  neo4j: 0.124
  redis: 0.259

integration.test_api::test_read_filter_by_many_predicates
  in-memory: 1.486
  mongodb: 2.012
  postgres: 2.136
  neo4j: 4.433
  redis: 5.820

integration.test_api::test_read_filter_by_multiple_object_uuids[object_uuid_slice0-2500]
  in-memory: 0.175
  postgres: 0.196
  mongodb: 0.216
  redis: 0.370
  neo4j: 0.436

integration.test_api::test_read_filter_by_multiple_object_uuids[object_uuid_slice1-5000]
  in-memory: 0.324
  postgres: 0.340
  mongodb: 0.367
  redis: 0.632
  neo4j: 0.839

integration.test_api::test_read_filter_by_multiple_object_uuids[object_uuid_slice2-10000]
  postgres: 0.628
  in-memory: 0.661
  mongodb: 0.735
  redis: 1.035
  neo4j: 1.525

integration.test_api::test_read_filter_by_multiple_subject_uuids[subject_uuid_slice0-2500]
  in-memory: 0.166
  postgres: 0.170
  mongodb: 0.179
  redis: 0.375
  neo4j: 0.412

integration.test_api::test_read_filter_by_multiple_subject_uuids[subject_uuid_slice1-5000]
  postgres: 0.291
  in-memory: 0.302
  mongodb: 0.345
  redis: 0.629
  neo4j: 0.838

integration.test_api::test_read_filter_by_multiple_subject_uuids[subject_uuid_slice2-10000]
  postgres: 0.600
  mongodb: 0.617
  in-memory: 0.650
  redis: 1.067
  neo4j: 1.477

integration.test_api::test_read_filter_by_object_uuid[0]
  mongodb: 0.042
  postgres: 0.054
  in-memory: 0.061
  neo4j: 0.128
  redis: 0.238

integration.test_api::test_read_filter_by_object_uuid[24]
  mongodb: 0.043
  postgres: 0.049
  in-memory: 0.059
  neo4j: 0.124
  redis: 0.235

integration.test_api::test_read_filter_by_object_uuid[49]
  postgres: 0.055
  in-memory: 0.059
  mongodb: 0.062
  neo4j: 0.100
  redis: 0.254

integration.test_api::test_read_filter_by_object_uuid[99]
  mongodb: 0.042
  postgres: 0.049
  in-memory: 0.063
  neo4j: 0.117
  redis: 0.240

integration.test_api::test_read_filter_by_predicate
  in-memory: 0.495
  mongodb: 0.604
  postgres: 0.716
  neo4j: 1.657
  redis: 1.767

integration.test_api::test_read_filter_by_predicate_and_nonexistent_object_uuid
  mongodb: 0.021
  in-memory: 0.029
  postgres: 0.030
  neo4j: 0.063
  redis: 0.190

integration.test_api::test_read_filter_by_predicate_and_nonexistent_subject_uuid
  postgres: 0.015
  mongodb: 0.016
  in-memory: 0.036
  neo4j: 0.071
  redis: 0.192

integration.test_api::test_read_filter_by_predicate_and_object_uuid
  mongodb: 0.022
  postgres: 0.033
  in-memory: 0.035
  neo4j: 0.055
  redis: 0.221

integration.test_api::test_read_filter_by_predicate_and_subject_uuid
  mongodb: 0.021
  postgres: 0.022
  in-memory: 0.043
  neo4j: 0.203
  redis: 0.256

integration.test_api::test_read_filter_by_predicate_subject_and_object_uuid
  postgres: 0.016
  in-memory: 0.036
  mongodb: 0.036
  neo4j: 0.104
  redis: 0.180

integration.test_api::test_read_filter_by_subject_uuid[0]
  mongodb: 0.046
  postgres: 0.053
  in-memory: 0.059
  redis: 0.223
  neo4j: 0.227

integration.test_api::test_read_filter_by_subject_uuid[24]
  mongodb: 0.043
  postgres: 0.043
  in-memory: 0.061
  neo4j: 0.119
  redis: 0.228

integration.test_api::test_read_filter_by_subject_uuid[49]
  in-memory: 0.058
  mongodb: 0.060
  postgres: 0.091
  neo4j: 0.140
  redis: 0.249

integration.test_api::test_read_filter_by_subject_uuid[99]
  postgres: 0.043
  in-memory: 0.057
  mongodb: 0.070
  neo4j: 0.103
  redis: 0.240


BACKEND_NAME         TOTAL_DURATION
in-memory            25.989
mongodb              34.290
postgres             47.667
redis                66.377
neo4j                636.940
```
