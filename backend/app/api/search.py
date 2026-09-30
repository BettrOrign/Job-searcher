from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.models.schemas import SearchQuery, SearchResult
from app.services.cache import cache_get, cache_key, cache_set, get_redis
from app.services.elastic import ensure_index
from app.services.jsearch import fetch_jsearch_all
from app.core.ranking import rank_results

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


class IndexHealth(BaseModel):
    elasticsearch: str
    redis: str


@router.get("/health")
async def health_check() -> dict[str, str]:
    from app.services.elastic import ElasticClient
    from app.services.cache import get_redis

    es_status = "unknown"
    redis_status = "unknown"
    try:
        ec = await ElasticClient.create()
        await ec.client.info()
        es_status = "ok"
        await ec.close()
    except Exception as exc:
        logger.warning("ES health check failed: %s", exc)
        es_status = "error"

    try:
        r = await get_redis().__anext__()
        await r.ping()
        redis_status = "ok"
        await r.close()
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        redis_status = "error"

    return {
        "status": "ok" if es_status == "ok" and redis_status == "ok" else "degraded",
        "elasticsearch": es_status,
        "redis": redis_status,
    }


@router.get("/search", response_model=SearchResult)
async def search(
    q: str = Query("", description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    experience: Optional[str] = Query(None, description="Experience level"),
    salary_min: Optional[int] = Query(None, ge=0, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, ge=0, description="Maximum salary"),
    employment_type: Optional[str] = Query(None, description="Employment type"),
    schedule_type: Optional[str] = Query(None, description="Schedule type"),
    skills: list[str] = Query([], description="Skills filter"),
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
) -> SearchResult:
    from app.services.elastic import ElasticClient

    query_params: dict[str, Any] = {
        "q": q,
        "location": location,
        "experience": experience,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "employment_type": employment_type,
        "schedule_type": schedule_type,
        "skills": skills,
        "page": page,
        "size": size,
    }

    # Try cache
    r_gen = get_redis()
    r = await r_gen.__anext__()
    try:
        cached = await cache_get(r, cache_key(query_params))
        if cached:
            cached["cached"] = True
            return SearchResult(**cached)
    finally:
        await r.close()

    # Fetch from JSearch
    jobs = await fetch_jsearch_all(
        query=q or "job",
        location=location,
        experience=experience,
        salary_min=salary_min,
        salary_max=salary_max,
        employment_type=employment_type,
        schedule_type=schedule_type,
        skills=skills if skills else None,
    )

    # Rank
    ranked = rank_results(jobs, SearchQuery(**query_params))
    total = len(ranked)
    start = page * size
    end = start + size
    page_results = [j for j, _ in ranked[start:end]]

    result = SearchResult(
        total=total,
        page=page,
        size=size,
        results=page_results,
        took_ms=0,
        cached=False,
    )

    # Cache result
    r_gen = get_redis()
    r = await r_gen.__anext__()
    try:
        await cache_set(r, cache_key(query_params), result.model_dump(), ttl=300)
    finally:
        await r.close()

    return result
