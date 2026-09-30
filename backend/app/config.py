from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_user: str = "elastic"
    elasticsearch_password: str = "changeme"
    elasticsearch_index: str = "jobs"

    redis_url: str = "redis://redis:6379/0"

    jsearch_api_base: str = "https://api.openwebninja.com/jsearch"
    rapidapi_key: str = ""

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    log_level: str = "info"

    react_app_api_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
