from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import settings
from app.models.schemas import JobOffer

logger = logging.getLogger(__name__)

JSEARCH_HEADERS = {
    "x-api-key": settings.rapidapi_key,
}


def _parse_item(item: dict) -> JobOffer:
    salary_from = item.get("job_min_salary")
    salary_to = item.get("job_max_salary")
    currency = item.get("job_salary_currency") or "USD"

    location_parts = [
        item.get("job_city"),
        item.get("job_state"),
        item.get("job_country"),
    ]
    location = ", ".join(p for p in location_parts if p)

    description = item.get("job_description") or ""
    skills = item.get("required_technologies") or []

    return JobOffer(
        id=str(item["job_id"]),
        title=item.get("job_title", ""),
        description=description,
        company=item.get("employer_name", ""),
        location=location,
        salary_from=int(salary_from) if salary_from else None,
        salary_to=int(salary_to) if salary_to else None,
        currency=currency,
        experience_required=item.get("job_required_experience"),
        employment_type=item.get("job_employment_type"),
        schedule_type=None,
        key_skills=skills,
        published_at=item.get("job_posted_at_datetime_utc"),
        alternate_url=item.get("job_apply_link", ""),
        source="jsearch",
    )


async def fetch_jsearch_vacancies(
    query: str,
    location: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[JobOffer], int]:
    params: dict = {
        "query": query,
        "page": str(page),
        "num_pages": "1",
    }
    if location:
        params["location"] = location

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{settings.jsearch_api_base}/search-v2",
            headers=JSEARCH_HEADERS,
            params=params,
        )
        if resp.status_code != 200:
            logger.warning("JSearch API error: %s", resp.status_code)
            return [], 0
        data = resp.json()

    jobs = data.get("data", {}).get("jobs", [])
    items = [_parse_item(i) for i in jobs]
    # JSearch doesn't return a total count directly; estimate from data length
    total = len(items)
    return items, total


async def fetch_jsearch_all(
    query: str,
    location: Optional[str] = None,
    experience: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    employment_type: Optional[str] = None,
    schedule_type: Optional[str] = None,
    skills: list[str] | None = None,
) -> list[JobOffer]:
    all_items: list[JobOffer] = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, 3):
            params: dict = {
                "query": query,
                "page": str(page),
                "num_pages": "1",
            }
            if location:
                params["location"] = location
            if experience:
                params["job_requirements"] = experience
            if employment_type:
                params["employment_types"] = employment_type

            resp = await client.get(
                f"{settings.jsearch_api_base}/search-v2",
                headers=JSEARCH_HEADERS,
                params=params,
            )
            if resp.status_code != 200:
                logger.warning("JSearch API error: %s", resp.status_code)
                break
            data = resp.json()
            jobs = data.get("data", {}).get("jobs", [])
            items = [_parse_item(i) for i in jobs]
            if not items:
                break
            all_items.extend(items)

    if skills:
        skill_set = set(s.lower() for s in skills)
        all_items = [
            j
            for j in all_items
            if any(s.lower() in " ".join(j.key_skills).lower() for s in skill_set)
        ]

    return all_items
