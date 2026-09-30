from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Optional

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield r
    finally:
        await r.close()


async def cache_get(r: aioredis.Redis, key: str) -> Optional[dict[str, Any]]:
    try:
        raw = await r.get(key)
        if raw:
            return json.loads(raw)
    except Exception as exc:
        logger.warning("Cache read error for %s: %s", key, exc)
    return None


async def cache_set(
    r: aioredis.Redis, key: str, value: dict[str, Any], ttl: int = 600
) -> None:
    try:
        await r.setex(key, ttl, json.dumps(value, ensure_ascii=False, default=str))
    except Exception as exc:
        logger.warning("Cache write error for %s: %s", key, exc)


def cache_key(query: dict[str, Any]) -> str:
    canonical = json.dumps(query, sort_keys=True, ensure_ascii=False)
    return "search:" + canonical
