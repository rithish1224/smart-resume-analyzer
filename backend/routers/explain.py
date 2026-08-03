from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/{analysis_id}")
async def get_explanation(analysis_id: str):
    # Mock SHAP data
    return {
        "analysis_id": analysis_id,
        "shap_values": [0.1, 0.2, -0.05, 0.4],
        "feature_names": ["Python", "SQL", "Java", "ML"]
    }

@router.get("/{analysis_id}/waterfall")
async def get_waterfall(analysis_id: str):
    # Mock waterfall chart data
    return {
        "analysis_id": analysis_id,
        "base_value": 50.0,
        "features": [
            {"name": "Python", "value": "+10"},
            {"name": "SQL", "value": "+5"},
            {"name": "Java", "value": "-2"}
        ]
    }
