from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RoadmapRequest(BaseModel):
    analysis_id: str
    enable_ai: bool = False

@router.post("/")
async def generate_roadmap(request: RoadmapRequest):
    # Mock roadmap generation
    milestones = [
        {"month": 1, "focus": "Core Python"},
        {"month": 2, "focus": "FastAPI & Async"}
    ]
    skill_plans = ["Complete Advanced Python course", "Build 2 REST APIs"]
    
    return {
        "milestones": milestones,
        "skill_plans": skill_plans,
        "provider_used": "OpenAI" if request.enable_ai else "Rule-based",
        "is_ai_generated": request.enable_ai
    }

@router.get("/provider-status")
async def get_provider_status():
    return {
        "status": "online",
        "provider": "OpenAI",
        "latency_ms": 120
    }
