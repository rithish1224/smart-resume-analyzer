from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
import json
from datetime import datetime

from ..models.improvement_schemas import (
    ImprovementRequest, 
    ResumeImprovementResponse,
    FeedbackRequest,
    ATSCheckResponse,
    TrendingKeywordsResponse,
    LearningStatsResponse,
    BulletRewrite
)
from ..services.resume_improvement import ResumeImprovementEngine
from ..services.self_learning import SelfLearningEngine

router = APIRouter(prefix="/api/improve", tags=["Improvement"])

improvement_engine = ResumeImprovementEngine()
learning_engine = SelfLearningEngine()

class DummyAIProvider:
    async def route_request(self, skill_gaps, role, profile_summary, domain, custom_prompt):
        return ["AI Suggestion 1: Expand on your AWS experience.", "AI Suggestion 2: Make achievements more quantifiable."], "OpenRouter"

ai_router = DummyAIProvider()

# Mock dependencies for auth, parsing
async def get_current_user():
    return {"id": "123", "role": "user"}

async def get_admin_user():
    return {"id": "999", "role": "admin"}

@router.post("/analyze", response_model=ResumeImprovementResponse)
async def analyze_resume(request: ImprovementRequest, current_user: dict = Depends(get_current_user)):
    resume_text = "Experienced software engineer. Worked on python backend. Assisted in cloud deployment."
    
    report = improvement_engine.analyze(
        resume_text=resume_text,
        domain=request.domain,
        company=request.company,
        jd_text=request.jd_text
    )
    
    ai_enhanced = False
    ai_provider_used = "None"
    
    if request.enable_ai:
        ai_suggestions, provider = await enhance_with_ai(report, resume_text, request.company or "", request.domain)
        report.general_suggestions.extend(ai_suggestions)
        ai_enhanced = True
        ai_provider_used = provider

    return ResumeImprovementResponse(
        domain=report.domain,
        company=report.company,
        ats_score=report.ats_score,
        ats_issues=report.ats_issues,
        bullet_quality_score=report.bullet_quality_score,
        weak_bullets=report.weak_bullets,
        strong_bullet_rewrites=[BulletRewrite(original=r["original"], suggested=r["suggested_rewrite"], reason="Action verb improvement") for r in report.strong_bullet_rewrites],
        keyword_gaps=report.keyword_gaps,
        keyword_density_score=report.keyword_density_score,
        quantification_score=report.quantification_score,
        missing_sections=report.missing_sections,
        general_suggestions=report.general_suggestions,
        domain_suggestions=report.domain_suggestions,
        company_suggestions=report.company_suggestions,
        overall_improvement_score=report.overall_improvement_score,
        priority_actions=report.priority_actions,
        ai_enhanced=ai_enhanced,
        ai_provider_used=ai_provider_used,
        generated_at=datetime.utcnow()
    )

async def enhance_with_ai(suggestions, resume_text: str, company: str, domain: str) -> tuple[List[str], str]:
    prompt = f"""
You are a professional resume coach. Analyze this resume and provide specific, actionable improvement suggestions.
Do NOT invent skills or experience. Only suggest improvements to presentation, keywords, and structure.

Domain: {domain}
Target Company: {company or 'General'}
Current Issues Found:
{json.dumps(suggestions.ats_issues + suggestions.domain_suggestions, indent=2)}

Resume Text (truncated):
{resume_text[:2000]}

Provide 5 specific, honest, improvement suggestions. Each suggestion must be:
1. Specific and actionable
2. Based only on actual content visible in the resume
3. Never suggest adding skills the candidate doesn't have"""
    
    result, provider = await ai_router.route_request(
        skill_gaps=[], role=domain, profile_summary=resume_text[:500], domain=domain,
        custom_prompt=prompt
    )
    return result, provider

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    learning_engine.record_feedback(
        analysis_id=request.analysis_id,
        resume_text="...",
        domain="unknown",
        user_rating=request.user_rating,
        recruiter_decision="pending",
        suggestions_helpful="yes" if request.overall_helpful else "no"
    )
    if learning_engine.should_retrain():
        learning_engine.trigger_retrain()
    return {"message": "Thank you for your feedback"}

class ATSCheckRequest(BaseModel):
    file_id: str
    jd_text: str

@router.post("/ats-check", response_model=ATSCheckResponse)
async def ats_check(request: ATSCheckRequest, current_user: dict = Depends(get_current_user)):
    report = improvement_engine.analyze(resume_text="Dummy parsed text", domain="general", jd_text=request.jd_text)
    
    pass_rate = "Low (<50%)"
    if report.ats_score > 80:
        pass_rate = "High (>80%)"
    elif report.ats_score > 50:
        pass_rate = "Medium (50-80%)"
        
    return ATSCheckResponse(
        ats_score=report.ats_score,
        pass_rate_estimate=pass_rate,
        issues=report.ats_issues,
        recommendations=report.priority_actions
    )

@router.get("/company-profiles")
async def get_company_profiles(current_user: dict = Depends(get_current_user)):
    return improvement_engine.company_profiles

@router.get("/trending-keywords/{domain}", response_model=TrendingKeywordsResponse)
async def get_trending_keywords(domain: str, current_user: dict = Depends(get_current_user)):
    keywords = learning_engine.get_trending_keywords(domain)
    return TrendingKeywordsResponse(
        domain=domain,
        trending_keywords=keywords,
        last_updated=datetime.utcnow(),
        source="learned_from_jds" if keywords else "static_fallback"
    )

@router.get("/learning-stats", response_model=LearningStatsResponse)
async def get_learning_stats(current_user: dict = Depends(get_admin_user)):
    stats = learning_engine.get_learning_stats()
    last_retrain_dt = datetime.strptime(stats['last_retrain'], '%Y-%m-%d %H:%M:%S') if stats['last_retrain'] else None
    
    return LearningStatsResponse(
        total_feedback_samples=stats['total_samples'],
        total_ats_samples=stats['total_samples'],
        total_jd_corpus_size=100,
        last_retrain=last_retrain_dt,
        trending_keywords_by_domain=stats['trending_keywords_by_domain'],
        model_files=["tfidf_software_engineer.joblib"]
    )
