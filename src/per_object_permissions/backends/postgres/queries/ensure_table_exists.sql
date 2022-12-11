CREATE TABLE IF NOT EXISTS perms (
	subject_uuid uuid,
	predicate text,
	object_uuid uuid
);
CREATE INDEX IF NOT EXISTS perms_subject_object_idx ON perms(subject_uuid, object_uuid);
CREATE INDEX IF NOT EXISTS perms_subject_predicate_object_idx ON perms(
	subject_uuid, predicate, object_uuid
);
