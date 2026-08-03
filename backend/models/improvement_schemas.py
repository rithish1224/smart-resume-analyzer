from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ImprovementRequest(BaseModel):
    file_id: str
    domain: str
    company: Optional[str] = None
    jd_text: str = ""
    enable_ai: bool = True

class BulletRewrite(BaseModel):
    original: str
    suggested: str
    reason: str

class ResumeImprovementResponse(BaseModel):
    domain: str
    company: Optional[str] = None
    ats_score: float
    ats_issues: List[str]
    bullet_quality_score: float
    weak_bullets: List[str]
    strong_bullet_rewrites: List[BulletRewrite]
    keyword_gaps: List[str]
    keyword_density_score: float
    quantification_score: float
    missing_sections: List[str]
    general_suggestions: List[str]
    domain_suggestions: List[str]
    company_suggestions: List[str]
    overall_improvement_score: float
    priority_actions: List[str]
    ai_enhanced: bool
    ai_provider_used: str
    generated_at: datetime

class FeedbackRequest(BaseModel):
    analysis_id: str
    overall_helpful: bool
    suggestions_acted_on: List[str] = []
    user_rating: int = Field(ge=1, le=5)
    comments: str = ""

class ATSCheckResponse(BaseModel):
    ats_score: float
    pass_rate_estimate: str
    issues: List[str]
    recommendations: List[str]

class TrendingKeywordsResponse(BaseModel):
    domain: str
    trending_keywords: List[str]
    last_updated: datetime
    source: str

class LearningStatsResponse(BaseModel):
    total_feedback_samples: int
    total_ats_samples: int
    total_jd_corpus_size: int
    last_retrain: Optional[datetime]
    trending_keywords_by_domain: dict[str, List[str]]
    model_files: List[str]
