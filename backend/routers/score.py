from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()

class ScoreRequest(BaseModel):
    file_id: Optional[str] = "demo_file_1"
    role: Optional[str] = "Software Engineer"
    jd_text: Optional[str] = None
    domain: Optional[str] = None

class ScoreResponse(BaseModel):
    analysis_id: str
    score: float
    shap_summary: Dict[str, Any]
    skill_gap: List[str]
    competency_breakdown: Dict[str, float]

def get_current_user():
    return {"id": 1}

async def handle_score(request: ScoreRequest):
    analysis_id = "mock_analysis_123"
    return ScoreResponse(
        analysis_id=analysis_id,
        score=85.5,
        shap_summary={"Years of Experience": 0.2, "Skill Match": 0.5, "Education": 0.1},
        skill_gap=["Python", "FastAPI", "Docker"],
        competency_breakdown={"Communication": 80.0, "Technical": 90.0, "Problem Solving": 85.0}
    )

@router.post("")
@router.post("/")
async def score_candidate(request: ScoreRequest, current_user: dict = Depends(get_current_user)):
    return await handle_score(request)

@router.get("")
@router.get("/")
async def get_scores(current_user: dict = Depends(get_current_user)):
    return [
        {
            "analysis_id": "mock_analysis_123",
            "score": 85.5,
            "candidate_name": "Demo Candidate",
            "role": "Software Engineer",
            "date": "2026-08-01"
        }
    ]

@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    return await get_scores(current_user)

@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str, current_user: dict = Depends(get_current_user)):
    if analysis_id != "mock_analysis_123":
        return {"analysis_id": analysis_id, "score": 78.0, "candidate_name": "Candidate", "role": "Developer"}
    return {"analysis_id": analysis_id, "score": 85.5}
