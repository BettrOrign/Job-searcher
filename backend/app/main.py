import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.search import router as search_router
from app.api.health import router as health_router
from app.services.elastic import ElasticClient, ensure_index
from app.services.cache import get_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ec = await ElasticClient.create()
    await ensure_index(ec.client)
    await ec.close()

    r_gen = get_redis()
    r = await r_gen.__anext__()
    await r.ping()
    await r.close()
    logger.info("Services connected")

    yield

    # Shutdown
    logger.info("Shutting down")


app = FastAPI(title="Job Aggregator API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(health_router)


@app.get("/")
async def root():
    return {"service": "Job Aggregator API", "version": "1.0.0"}
