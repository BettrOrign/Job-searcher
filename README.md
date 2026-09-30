# Job Aggregator + Search Engine

A full-stack job aggregator that fetches vacancies from JSearch (OpenWebNinja), indexes them in Elasticsearch, and serves search results via a FastAPI backend with a React + TypeScript frontend.

## Architecture

| Component     | Technology        | Role                                |
|---------------|-------------------|-------------------------------------|
| Frontend      | React + TypeScript | Search UI, filters, results         |
| Backend       | FastAPI (async)   | Search API, JSearch parser          |
| Search Engine | Elasticsearch 8.x | Full-text search with ranking       |
| Cache         | Redis 7           | Result caching (TTL 5 min)          |
| Job Source    | JSearch API       | Real-time jobs from LinkedIn, Indeed, Glassdoor, etc. |

## Quick Start

```bash
cp .env.example .env
# Edit .env and add your OpenWebNinja API key
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Elasticsearch: http://localhost:9200
- Redis: localhost:6379

## API Endpoints

- `GET /` — Root info
- `GET /api/v1/health` — Service health (ES + Redis)
- `GET /api/v1/search` — Search with filters

### Search Query Params

| Param           | Type     | Description             |
|-----------------|----------|-------------------------|
| q               | string   | Search query            |
| location        | string   | Location filter         |
| experience      | string   | Experience level        |
| salary_min      | integer  | Minimum salary          |
| salary_max      | integer  | Maximum salary          |
| employment_type | string   | Employment type         |
| schedule_type   | string   | Schedule type           |
| skills          | []string | Skills filter           |
| page            | integer  | Page number (0-based)   |
| size            | integer  | Results per page (1-100)|

## Project Structure

```
job-aggregator/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI app + lifespan
│       ├── config.py        # Settings
│       ├── models/
│       │   └── schemas.py   # Pydantic models
│       ├── services/
│       │   ├── elastic.py   # ES client + index setup
│       │   ├── cache.py     # Redis cache
│       │   └── jsearch.py   # JSearch API parser
│       ├── core/
│       │   └── ranking.py   # Scoring & ranking
│       └── api/
│           ├── search.py    # Search endpoint
│           └── health.py    # Health check
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── types.ts
        ├── api/client.ts
        └── components/
            ├── Search.tsx
            └── Results.tsx
```

## API Key

Get your free API key at [OpenWebNinja](https://www.openwebninja.com/api/jsearch) — 200 requests/month on the free tier.
