from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()

def require_role(roles: List[str]):
    def role_checker():
        # Mock role checking
        user_role = "admin"
        if user_role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return True
    return role_checker

@router.get("/users", dependencies=[Depends(require_role(["recruiter", "admin"]))])
async def list_users():
    return [{"id": 1, "name": "Admin"}, {"id": 2, "name": "User"}]

@router.get("/analyses", dependencies=[Depends(require_role(["recruiter", "admin"]))])
async def list_analyses():
    return [{"id": "a1", "score": 90}, {"id": "a2", "score": 75}]

@router.get("/model-versions", dependencies=[Depends(require_role(["admin"]))])
async def list_model_versions():
    return [{"version": "v1.0.0", "active": False}, {"version": "v1.1.0", "active": True}]

@router.get("/stats", dependencies=[Depends(require_role(["recruiter", "admin"]))])
async def get_stats():
    return {
        "total_candidates": 1500,
        "avg_score": 76.5,
        "shortlist_rate": 0.25
    }

@router.post("/model/activate/{version_id}", dependencies=[Depends(require_role(["admin"]))])
async def activate_model(version_id: str):
    return {"message": f"Model {version_id} activated successfully"}
