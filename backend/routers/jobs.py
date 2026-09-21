"""Lightweight jobs/candidates API for the Part B workflow."""
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()
_jobs: Dict[str, dict] = {}
_candidates: List[dict] = []


class JobCreate(BaseModel):
    title: str
    description: str = ""
    required_skills: List[str] = Field(default_factory=list)


@router.post("/jobs", status_code=201)
async def create_job(job: JobCreate):
    job_id = str(uuid4())
    record = {"id": job_id, **job.model_dump()}
    _jobs[job_id] = record
    return record


@router.get("/jobs")
async def list_jobs():
    return list(_jobs.values())


@router.get("/candidates")
async def list_candidates(job_id: Optional[str] = None):
    if job_id is None:
        return _candidates
    return [candidate for candidate in _candidates if candidate.get("job_id") == job_id]
