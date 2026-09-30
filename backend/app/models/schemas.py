from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class JobOffer(BaseModel):
    id: str
    title: str
    description: str
    company: str
    location: str
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    currency: str = "RUB"
    experience_required: Optional[str] = None
    employment_type: Optional[str] = None
    schedule_type: Optional[str] = None
    key_skills: list[str] = Field(default_factory=list)
    published_at: Optional[str] = None
    alternate_url: str = ""
    source: str = "jsearch"

    @field_validator("key_skills", mode="before")
    @classmethod
    def _normalise_skills(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            return [str(s).strip() for s in v if s]
        return []


class SearchQuery(BaseModel):
    q: str = ""
    location: Optional[str] = None
    experience: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    employment_type: Optional[str] = None
    schedule_type: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    page: int = Field(0, ge=0)
    size: int = Field(20, ge=1, le=100)


class SearchResult(BaseModel):
    total: int
    page: int
    size: int
    results: list[JobOffer]
    took_ms: int
    cached: bool = False


class HealthResponse(BaseModel):
    status: str
    elasticsearch: str
    redis: str
