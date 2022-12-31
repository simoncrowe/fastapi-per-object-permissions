import pydantic


class Settings(pydantic.BaseSettings):
    backend: str = "per_object_permissions.backends.in_memory_backend::InMemoryBackend"

    redis_host: str = "redis"

    postgres_host: str = "postgres"
    postgres_dbname: str = "per_object_perms"
    postgres_user: str = "username"
    postgres_password: str = "password"

    mongo_host: str = "mongo"
    mongo_user: str = "username"
    mongo_password: str = "password"

    class Config:
        env_file = ".env"
