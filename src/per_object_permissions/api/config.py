import pydantic


class Settings(pydantic.BaseSettings):
    backend: str = "per_object_permissions.backends.in_memory_backend::InMemoryBackend"
    redis_host: str = "redis"

    class Config:
        env_file = ".env"
