from __future__ import annotations

import logging
from typing import Optional

from app.models.schemas import JobOffer, SearchQuery

logger = logging.getLogger(__name__)


def compute_score(job: JobOffer, query: SearchQuery) -> float:
    score = 0.0
    title_lower = job.title.lower()
    desc_lower = job.description.lower()
    q = query.q.lower()

    # Query match in title
    if q and q in title_lower:
        score += 10.0
    if q and q in desc_lower:
        score += 3.0

    # Skills match
    for skill in query.skills:
        skill_lower = skill.lower()
        if any(skill_lower in s.lower() for s in job.key_skills):
            score += 5.0
        if skill_lower in desc_lower or skill_lower in title_lower:
            score += 2.0

    # Salary proximity bonus (jobs closer to midpoint of range are better)
    if query.salary_min is not None:
        if job.salary_from and job.salary_from >= query.salary_min:
            score += 4.0
        elif job.salary_from:
            score += max(0, 4.0 - (query.salary_min - job.salary_from) / 1000)
        elif job.salary_to and job.salary_to >= query.salary_min:
            score += 3.0

    if query.salary_max is not None and job.salary_to:
        if job.salary_to <= query.salary_max:
            score += 2.0

    # Location match
    if query.location and query.location.lower() in job.location.lower():
        score += 5.0

    # Experience match
    if query.experience and job.experience_required:
        exp_order = {"noExperience": 0, "between1And3": 1, "between3And6": 2, "moreThan6": 3}
        query_exp = exp_order.get(query.experience, 0)
        job_exp = exp_order.get(job.experience_required, 0)
        if job_exp <= query_exp:
            score += 2.0

    # Recency bonus
    if job.published_at:
        try:
            from datetime import datetime, timezone, timedelta

            published = datetime.fromisoformat(job.published_at.replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - published).total_seconds() / 3600
            if age_hours < 24:
                score += 3.0
            elif age_hours < 72:
                score += 1.0
        except Exception:
            pass

    return score


def rank_results(
    jobs: list[JobOffer], query: SearchQuery
) -> list[tuple[JobOffer, float]]:
    scored = [(j, compute_score(j, query)) for j in jobs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
