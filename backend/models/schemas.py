from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID
from backend.models.db_models import RoleEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    name: Optional[str] = None
    role: RoleEnum = RoleEnum.candidate

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class CandidateProfileSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    certifications: List[str] = []
    projects: List[Dict[str, Any]] = []
    raw_text: str = ""

class ScoreRequest(BaseModel):
    role: str
    jd_text: str
    domain: Optional[str] = None

class ScoreResponse(BaseModel):
    candidate_id: Optional[UUID] = None
    final_score: float
    confidence_score: float
    shortlist_decision: str
    competency_scores: Dict[str, float] = {}
    rule_scores: Dict[str, float] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SHAPResponse(BaseModel):
    base_score: float
    final_score: float
    waterfall: List[Dict[str, Any]] = []
    top_positive: List[Dict[str, Any]] = []
    top_negative: List[Dict[str, Any]] = []

class SkillGapResponse(BaseModel):
    required_skills: List[str] = []
    candidate_skills: List[str] = []
    gaps: List[Dict[str, Any]] = []  # dict with skill and priority score

class FairnessResponse(BaseModel):
    dir_score: float
    dp_difference: float
    eo_tpr_gap: float
    eo_fpr_gap: float
    dir_pass: bool
    dp_pass: bool
    eo_pass: bool
    overall_pass: bool

class RoadmapResponse(BaseModel):
    skill_gaps: List[str] = []
    milestones_30_day: List[str] = Field(default=[], alias="milestones_30_day")
    milestones_60_day: List[str] = Field(default=[], alias="milestones_60_day")
    milestones_90_day: List[str] = Field(default=[], alias="milestones_90_day")
    provider_used: str = ""
    is_ai_generated: bool = True

class ProviderStatusResponse(BaseModel):
    primary_provider: str
    primary_available: bool
    fallback_provider: str
    fallback_available: bool
    active_provider: str
    fallback_enabled: bool
    free_tier_used: int
    free_tier_limit: int
