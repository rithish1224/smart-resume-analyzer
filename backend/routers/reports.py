import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.auth.dependencies import get_current_user
from backend.db.database import get_db
from backend.models.db_models import AnalysisReport, User

router = APIRouter()
logger = logging.getLogger(__name__)


def _serialize(report: AnalysisReport) -> dict:
    return {
        "id": str(report.id),
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "resume_filename": report.resume_filename,
        "target_role": report.target_role,
        "job_description": report.job_description,
        "match_level": report.match_level,
        "skill_coverage": report.skill_coverage,
        "overall_match_percent": report.overall_match_percent if report.overall_match_percent is not None else report.skill_coverage,
        "matched_skills": json.loads(report.matched_skills or "[]"),
        "missing_skills": json.loads(report.missing_skills or "[]"),
        "summary": report.summary,
        "requirement_coverage": json.loads(report.requirement_coverage) if report.requirement_coverage else None,
    }


@router.get("/reports")
async def list_reports(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(AnalysisReport).where(AnalysisReport.user_id == current_user.id)
    result = await db.execute(query.order_by(AnalysisReport.created_at.desc()).offset(offset).limit(limit))
    total = await db.scalar(select(func.count(AnalysisReport.id)).where(AnalysisReport.user_id == current_user.id))
    return {"reports": [_serialize(report) for report in result.scalars().all()], "total": total or 0}


async def _owned_report(report_id: UUID, db: AsyncSession, user: User) -> AnalysisReport:
    result = await db.execute(
        select(AnalysisReport).where(
            AnalysisReport.id == report_id,
            AnalysisReport.user_id == user.id,
        )
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/reports/{report_id}")
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _serialize(await _owned_report(report_id, db, current_user))


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await _owned_report(report_id, db, current_user)
    await db.delete(report)
    await db.commit()
    return {"message": "Report deleted"}
