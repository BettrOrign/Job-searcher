from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class ElasticClient(BaseModel):
    client: AsyncElasticsearch

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    async def create(cls) -> ElasticClient:
        client = AsyncElasticsearch(
            settings.elasticsearch_url,
            basic_auth=(settings.elasticsearch_user, settings.elasticsearch_password),
            verify_certs=False,
            ssl_show_warn=False,
        )
        info = await client.info()
        logger.info("Elasticsearch connected: %s", info.get("version", {}).get("number"))
        return cls(client=client)

    async def close(self) -> None:
        await self.client.close()


async def get_elastic() -> AsyncGenerator[AsyncElasticsearch, None]:
    ec = await ElasticClient.create()
    try:
        yield ec.client
    finally:
        await ec.close()


async def ensure_index(client: AsyncElasticsearch) -> None:
    index = settings.elasticsearch_index
    if not await client.indices.exists(index=index):
        mapping: dict[str, Any] = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "ru_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "ru_stop", "ru_stemmer"],
                        },
                        "en_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "en_stop", "en_stemmer"],
                        },
                    },
                    "filter": {
                        "ru_stop": {"type": "stop", "stopwords": "_russian_"},
                        "ru_stemmer": {
                            "type": "stemmer",
                            "language": "russian",
                        },
                        "en_stop": {"type": "stop", "stopwords": "_english_"},
                        "en_stemmer": {
                            "type": "stemmer",
                            "language": "english",
                        },
                    },
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "ru_analyzer",
                        "fields": {"en": {"type": "text", "analyzer": "en_analyzer"}},
                    },
                    "description": {"type": "text", "analyzer": "ru_analyzer"},
                    "company": {"type": "keyword"},
                    "location": {"type": "keyword"},
                    "salary_from": {"type": "integer"},
                    "salary_to": {"type": "integer"},
                    "currency": {"type": "keyword"},
                    "experience_required": {"type": "keyword"},
                    "employment_type": {"type": "keyword"},
                    "schedule_type": {"type": "keyword"},
                    "key_skills": {"type": "keyword"},
                    "published_at": {"type": "date"},
                    "alternate_url": {"type": "keyword"},
                    "source": {"type": "keyword"},
                }
            },
        }
        await client.indices.create(index=index, body=mapping)
        logger.info("Index '%s' created", index)
