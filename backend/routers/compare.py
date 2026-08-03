from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class CompareRequest(BaseModel):
    analysis_ids: Optional[List[str]] = None
    ids: Optional[List[str]] = None

async def handle_compare(request: CompareRequest):
    candidate_ids = request.analysis_ids or request.ids or []
    if len(candidate_ids) < 2:
        # Default mock candidate comparison if less than 2 provided for demo/testing
        candidate_ids = candidate_ids + ["candidate_demo_1", "candidate_demo_2"][:2 - len(candidate_ids)]
    
    return {
        "batch_id": "batch_999",
        "comparisons": [
            {
                "analysis_id": cid,
                "score": 80.0 + (i * 3.5),
                "gaps": ["Cloud Deployment", "System Design"],
                "competency": {"Technical": 85 + i, "Communication": 80, "Problem Solving": 90}
            } for i, cid in enumerate(candidate_ids)
        ]
    }

@router.post("", summary="Compare Candidates")
@router.post("/", summary="Compare Candidates Trailing Slash")
async def compare_analyses(request: CompareRequest):
    return await handle_compare(request)

@router.get("/batch/{batch_id}")
async def get_batch_comparison(batch_id: str):
    return {
        "batch_id": batch_id,
        "comparisons": []
    }
