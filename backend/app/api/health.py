from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    es_status = "ok"
    redis_status = "ok"

    try:
        from app.services.elastic import ElasticClient

        ec = await ElasticClient.create()
        await ec.client.info()
        await ec.close()
    except Exception:
        es_status = "error"

    try:
        from app.services.cache import get_redis

        r_gen = get_redis()
        r = await r_gen.__anext__()
        await r.ping()
        await r.close()
    except Exception:
        redis_status = "error"

    return HealthResponse(
        status="ok" if es_status == "ok" and redis_status == "ok" else "degraded",
        elasticsearch=es_status,
        redis=redis_status,
    )
