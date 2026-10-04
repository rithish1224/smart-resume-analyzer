"""Part B resume analysis endpoint.

This router is additive: the existing v1 upload and score routes remain
unchanged while this endpoint composes the current parser with v2 inference.
"""
import re
import time
import json
import pickle
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.auth.dependencies import get_optional_current_user
from backend.db.database import get_db
from backend.models.db_models import AnalysisReport, User

from backend.config import settings
from backend.services.parser import ResumeParser

router = APIRouter()
logger = logging.getLogger(__name__)


def requirement_check(coverage: dict | None) -> dict:
    if not coverage:
        return {"experience": "Not enough information", "education": "Not enough information"}
    experience = coverage.get("years_candidate") is None or coverage.get("years_required") is None
    education = coverage.get("degree_found") is None or coverage.get("degree_required") is None
    return {
        "experience": "Not enough information" if experience else ("Met" if coverage.get("years_met") else "Below"),
        "education": "Not enough information" if education else ("Met" if coverage.get("degree_met") else "Below"),
    }


def _preferred_requirement(jd_text: str, keywords: tuple[str, ...]) -> bool:
    for sentence in re.split(r"(?<=[.!?;])\s+|\n+", jd_text.lower()):
        if any(keyword in sentence for keyword in keywords) and re.search(
            r"\b(preferred|nice\s+to\s+have|plus)\b", sentence
        ):
            return True
    return False


def compute_overall_match(coverage: dict, jd_text: str = "") -> Optional[int]:
    parts = []
    skill = coverage.get("skill_coverage")
    if skill is not None:
        parts.append((float(skill) / 100, 70))
    years = coverage.get("years_candidate")
    required_years = coverage.get("years_required")
    if (
        years is not None and required_years
        and coverage.get("years_met") is not None
        and not coverage.get("experience_preferred", _preferred_requirement(
            jd_text, ("year", "years", "experience")
        ))
    ):
        parts.append((min(float(years) / float(required_years), 1), 20))
    degree = coverage.get("degree_found")
    required_degree = coverage.get("degree_required")
    if (
        degree is not None and required_degree
        and coverage.get("degree_met") is not None
        and not coverage.get("education_preferred", _preferred_requirement(
            jd_text, ("degree", "bachelor", "master", "education", "b.e", "b.tech", "b.sc", "m.sc", "mba")
        ))
    ):
        parts.append((1 if coverage["degree_met"] else min(float(degree) / float(required_degree), 1), 10))
    if not parts:
        return None
    total_weight = sum(weight for _, weight in parts)
    return round(sum(score * weight for score, weight in parts) / total_weight * 100)


def _overall_level(value: Optional[int]) -> str:
    if value is None:
        return "Not enough information"
    return "Strong match" if value >= 70 else "Partial match" if value >= 40 else "Weak match"


def _overall_summary(skill_result: dict, coverage: dict, overall: Optional[int]) -> str:
    summary = skill_result["summary"]
    additions = []
    if coverage.get("years_candidate") is not None and coverage.get("years_required") is not None:
        additions.append(
            f"Experience: {coverage['years_candidate']} yrs vs {coverage['years_required']}+ required "
            f"({'Met' if coverage.get('years_met') else 'Below'})."
        )
    if coverage.get("degree_found") is not None and coverage.get("degree_required") is not None:
        additions.append(f"Education: {'Met' if coverage.get('degree_met') else 'Below'}.")
    if additions:
        summary = f"{summary} {' '.join(additions)}"
    return summary

_SKILL_RE = re.compile(
    r"\b(python|java|c\+\+|javascript|typescript|sql|nosql|machine learning|"
    r"deep learning|fastapi|django|react|aws|azure|gcp|docker|kubernetes|"
    r"terraform|pandas|numpy|spark|git|api|rest|graphql)\b",
    re.IGNORECASE,
)
_parser: Optional[ResumeParser] = None
_v2_model = None
_v2_calibrator = None
_v2_features: Optional[List[str]] = None
_v2_vectorizer = None
_embedding_model = None
_shap_explainer = None
_v3_model = None
_v3_features = None
_v3_vectorizer = None
_v3_medians = None


def _load_v2():
    global _v2_model, _v2_calibrator, _v2_features, _v2_vectorizer, _shap_explainer
    if _v2_model is not None:
        return
    model_dir = Path(__file__).resolve().parents[1] / "models" / "trained" / "v2"
    model_path = model_dir / "xgb_classifier.json"
    metadata_path = model_dir / "model_version.json"
    if not model_path.exists():
        return
    try:
        import xgboost as xgb
        _v2_model = xgb.XGBClassifier()
        _v2_model.load_model(str(model_path))
        import shap
        _shap_explainer = shap.TreeExplainer(_v2_model)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        _v2_features = metadata.get("features", [])
        feature_metadata_path = metadata_path.parent / "feature_metadata.pkl"
        if feature_metadata_path.exists():
            with feature_metadata_path.open("rb") as handle:
                _v2_vectorizer = pickle.load(handle).get("vectorizer")
        calibrator_path = metadata_path.parent / "isotonic_calibrator.pkl"
        if calibrator_path.exists():
            with calibrator_path.open("rb") as handle:
                _v2_calibrator = pickle.load(handle)
    except (OSError, ValueError, ImportError) as exc:
        _v2_model = None
        raise RuntimeError(f"Unable to load v2 analysis assets: {exc}") from exc


def load_embedding_model() -> None:
    global _embedding_model
    if _embedding_model is not None:
        return
    from sentence_transformers import SentenceTransformer
    _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def _get_parser() -> ResumeParser:
    global _parser
    if _parser is None:
        _parser = ResumeParser()
    return _parser


def _skills(text: str) -> List[str]:
    from ml_training.train_v3 import normalized_skills
    return sorted(normalized_skills(text))


def _skill_analysis(resume_text: str, jd_text: str) -> Dict[str, Any]:
    required = set(_skills(jd_text))
    candidate = set(_skills(resume_text))
    matched = sorted(required & candidate)
    missing = sorted(required - candidate)
    if not required:
        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "skill_coverage": None,
            "match_level": "Not enough information",
            "summary": "No recognized required skills were found.",
        }
    coverage = round(len(matched) / len(required) * 100)
    level = "Strong match" if coverage >= 70 else "Partial match" if coverage >= 40 else "Weak match"
    missing_text = f" Missing: {', '.join(missing)}." if missing else ""
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_coverage": coverage,
        "match_level": level,
        "summary": f"Matched {len(matched)} of {len(required)} required skills ({coverage}%).{missing_text}",
    }


def _load_v3() -> None:
    global _v3_model, _v3_features, _v3_vectorizer, _v3_medians
    if _v3_model is not None:
        return
    import pickle
    import xgboost as xgb
    model_dir = Path(__file__).resolve().parents[1] / "models" / "trained" / "v3"
    _v3_model = xgb.XGBRanker()
    _v3_model.load_model(str(model_dir / "xgb_ranker.json"))
    metadata = json.loads((model_dir / "model_version.json").read_text(encoding="utf-8"))
    _v3_features = metadata["features"]
    with (model_dir / "feature_metadata.pkl").open("rb") as handle:
        assets = pickle.load(handle)
    _v3_vectorizer = assets["vectorizer"]
    _v3_medians = assets["medians"]


def _v3_raw_score(profile: Any, jd_text: str) -> float:
    """Return the ranker's raw score for a single candidate.

    A raw ranker score is not a probability and is only suitable for ordering
    candidates within the same job. It is used as a safe fallback when the
    legacy v2 explainability assets are unavailable.
    """
    import pandas as pd
    from ml_training.train_real import extract_pair_features
    from ml_training.train_v3 import add_fixed_features

    _load_v3()
    if _embedding_model is None:
        load_embedding_model()
    frame = pd.DataFrame([{
        "resume_text": getattr(profile, "raw_text", "") or "",
        "job_description_text": jd_text,
        "resume_id": "request-resume",
        "job_id": "request-job",
    }])
    base, _ = extract_pair_features(
        frame,
        vectorizer=_v3_vectorizer,
        embedding_model=_embedding_model,
        use_embeddings=True,
    )
    features = add_fixed_features(frame, base)
    for column, median in _v3_medians.items():
        features[column] = features[column].fillna(median)
    features = features.reindex(columns=_v3_features).fillna(0.0)
    return float(_v3_model.predict(features)[0])


def _v3_scores(profiles: List[Any], jd_text: str) -> List[Dict[str, float]]:
    import pandas as pd
    from ml_training.train_real import extract_pair_features
    from ml_training.train_v3 import add_fixed_features
    _load_v3()
    if _embedding_model is None:
        load_embedding_model()
    frame = pd.DataFrame([
        {
            "resume_text": getattr(profile, "raw_text", "") or "",
            "job_description_text": jd_text,
            "resume_id": f"request-resume-{index}",
            "job_id": "request-job",
        }
        for index, profile in enumerate(profiles)
    ])
    base, _ = extract_pair_features(
        frame,
        vectorizer=_v3_vectorizer,
        embedding_model=_embedding_model,
        use_embeddings=True,
    )
    features = add_fixed_features(frame, base)
    for column, median in _v3_medians.items():
        features[column] = features[column].fillna(median)
    features = features.reindex(columns=_v3_features).fillna(0.0)
    raw = _v3_model.predict(features)
    low, high = float(raw.min()), float(raw.max())
    relative = np.full(len(raw), 50.0) if len(raw) == 1 or high == low else (raw - low) / (high - low) * 100
    order = np.argsort(-relative, kind="stable")
    ranks = np.empty(len(raw), dtype=int)
    ranks[order] = np.arange(1, len(raw) + 1)
    return [{"rank": int(ranks[i]), "relative_score": round(float(relative[i]), 2)} for i in range(len(raw))]


def _model_version() -> str:
    metadata = Path(__file__).resolve().parents[1] / "models" / "trained" / "v3" / "model_version.json"
    if metadata.exists():
        try:
            return str(json.loads(metadata.read_text(encoding="utf-8")).get("version", "3.0"))
        except (OSError, ValueError):
            pass
    return getattr(settings, "MODEL_VERSION", "v1")


def _score(profile: Any, jd_text: str) -> Dict[str, Any]:
    from ml_training.train_v3 import normalized_skills
    from ml_training.feature_engineering import (
        extract_degree_level,
        extract_experience_years,
        extract_required_years,
    )
    resume_text = getattr(profile, "raw_text", "") or ""
    candidate_years = extract_experience_years(resume_text)
    required_years = extract_required_years(jd_text)
    candidate_degree = extract_degree_level(resume_text)
    required_degree = extract_degree_level(jd_text)

    def nullable(value: Any) -> Any:
        try:
            return None if value is None or not np.isfinite(float(value)) else float(value)
        except (TypeError, ValueError):
            return None

    resume_skills = normalized_skills(resume_text)
    resume_related = set()
    skill_result = _skill_analysis(resume_text, jd_text)
    jd_skills = set(skill_result["matched_skills"]) | set(skill_result["missing_skills"])
    matched = skill_result["matched_skills"]
    missing = skill_result["missing_skills"]
    v3_raw_score = None
    try:
        v3_raw_score = _v3_raw_score(profile, jd_text)
    except (OSError, RuntimeError, ValueError, ImportError) as exc:
        # Keep the established v2 path available when optional v3 dependencies
        # or artifacts are unavailable.
        v3_raw_score = None

    try:
        _load_v2()
    except RuntimeError:
        # v3 ranking remains usable when optional v2 explainability packages
        # such as SHAP are not installed.
        pass
    if _embedding_model is None:
        load_embedding_model()
    from ml_training.train_real import extract_pair_features
    import pandas as pd
    row = pd.DataFrame([{
        "resume_text": resume_text,
        "job_description_text": jd_text,
        "resume_id": "request-resume",
        "job_id": "request-job",
    }])
    pair_features = None
    score = None
    if _v2_model is not None and _v2_features:
        pair_features, _ = extract_pair_features(
            row, use_embeddings=True, vectorizer=_v2_vectorizer,
            embedding_model=_embedding_model,
        )
        pair_features = pair_features.reindex(columns=_v2_features).fillna(0.0)
        probability = float(_v2_model.predict_proba(pair_features)[0, 1])
        if _v2_calibrator is not None:
            probability = float(_v2_calibrator.predict([probability])[0])
        score = round(max(1.0, min(99.0, probability * 100.0)), 2)

    if _v2_model is None or _shap_explainer is None or pair_features is None:
        if v3_raw_score is None:
            raise RuntimeError("Neither v2 explainability nor v3 ranking assets are available")
        candidate_years_value = nullable(candidate_years)
        required_years_value = nullable(required_years)
        candidate_degree_value = nullable(candidate_degree)
        required_degree_value = nullable(required_degree)
        requirement_coverage = {
            "skill_coverage": skill_result["skill_coverage"],
            "skills_matched": len(matched),
            "skills_required": len(jd_skills),
            "coverage_pct": round(len(matched) / len(jd_skills) * 100, 2) if jd_skills else 100.0,
            "years_required": required_years_value,
            "years_candidate": candidate_years_value,
            "years_met": (
                None if required_years_value is None or candidate_years_value is None
                else candidate_years_value >= required_years_value
            ),
            "degree_required": required_degree_value,
            "degree_found": candidate_degree_value,
            "degree_met": (
                None if required_degree_value is None or candidate_degree_value is None
                else candidate_degree_value >= required_degree_value
            ),
            "experience_preferred": _preferred_requirement(jd_text, ("year", "years", "experience")),
            "education_preferred": _preferred_requirement(
                jd_text, ("degree", "bachelor", "master", "education", "b.e", "b.tech", "b.sc", "m.sc", "mba")
            ),
        }
        overall_match_percent = compute_overall_match(requirement_coverage, jd_text)
        display_score = 1.0 + 98.0 / (1.0 + math.exp(-float(v3_raw_score)))
        return {
            "fit_score": round(min(99.0, display_score), 2),
            "confidence": None,
            "competency_scores": {},
            "matched_skills": matched,
            "missing_skills": missing,
            "skill_coverage": skill_result["skill_coverage"],
            "match_level": _overall_level(overall_match_percent),
            "summary": _overall_summary(skill_result, requirement_coverage, overall_match_percent),
            "overall_match_percent": overall_match_percent,
            "note": "Assistive analysis only. Match level is based on skill overlap, not a hiring decision. A human must review. The v3 score is a raw ranking score, not a probability.",
            "related_skills": sorted(resume_related),
            "shap_top_positive": [],
            "shap_top_negative": [],
            "improvement_suggestions": [f"Add evidence of {skill} to the resume." for skill in missing[:5]],
            "requirement_coverage": requirement_coverage,
        }

    shap_values = _shap_explainer.shap_values(pair_features)[0]
    groups = {
        "technical": {"exp_years", "num_projects", "num_certs"},
        "domain": {"degree_level", "has_degree", "gpa", "has_gpa"},
        "experience": {"required_years", "exp_gap"},
        "education": {"degree_level", "has_degree", "gpa", "has_gpa"},
        "text_similarity": {"tfidf_similarity", "minilm_mean_cosine", "minilm_max_cosine"},
        "skills": {"skill_match_ratio", "resume_skill_count", "jd_skill_count", "missing_skill_count"},
    }
    excluded = {"jd_chars", "jd_skill_count", "required_years", "resume_chars"}
    groups = {
        group: {feature for feature in features if feature not in excluded}
        for group, features in groups.items()
    }
    contributions = [
        {"feature": feature, "value": round(float(value), 6)}
        for feature, value in zip(_v2_features, shap_values)
        if feature not in excluded
    ]
    positive = sorted((item for item in contributions if item["value"] > 0),
                      key=lambda item: item["value"], reverse=True)[:5]
    negative = sorted((item for item in contributions if item["value"] < 0),
                      key=lambda item: item["value"])[:5]
    group_values = {
        group: round(sum(item["value"] for item in contributions if item["feature"] in names), 4)
        for group, names in groups.items()
    }
    related = sorted(resume_related)
    competency = {
        group: round(50 + value * 10, 2)
        for group, value in group_values.items()
    }
    candidate_years_value = nullable(candidate_years)
    required_years_value = nullable(required_years)
    candidate_degree_value = nullable(candidate_degree)
    required_degree_value = nullable(required_degree)
    requirement_coverage = {
        "skill_coverage": skill_result["skill_coverage"],
        "skills_matched": len(matched),
        "skills_required": len(jd_skills),
        "coverage_pct": round(len(matched) / len(jd_skills) * 100, 2) if jd_skills else 100.0,
        "years_required": required_years_value,
        "years_candidate": candidate_years_value,
        "years_met": (
            None if required_years_value is None or candidate_years_value is None
            else candidate_years_value >= required_years_value
        ),
        "degree_required": required_degree_value,
        "degree_found": candidate_degree_value,
        "degree_met": (
            None if required_degree_value is None or candidate_degree_value is None
            else candidate_degree_value >= required_degree_value
        ),
        "experience_preferred": _preferred_requirement(jd_text, ("year", "years", "experience")),
        "education_preferred": _preferred_requirement(
            jd_text, ("degree", "bachelor", "master", "education", "b.e", "b.tech", "b.sc", "m.sc", "mba")
        ),
    }
    hard_requirements_met = (
        requirement_coverage["coverage_pct"] == 100.0
        and requirement_coverage["years_met"] is True
        and requirement_coverage["degree_met"] is not False
    )
    return {
        "fit_score": score,
        "confidence": round(min(0.99, 0.5 + abs(score - 50) / 100), 3),
        "competency_scores": competency,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_coverage": skill_result["skill_coverage"],
        "match_level": _overall_level(compute_overall_match(requirement_coverage, jd_text)),
        "summary": _overall_summary(
            skill_result, requirement_coverage, compute_overall_match(requirement_coverage, jd_text)
        ),
        "overall_match_percent": compute_overall_match(requirement_coverage, jd_text),
        "note": "Assistive analysis only. Match level is based on skill overlap, not a hiring decision. A human must review.",
        "related_skills": related,
        "shap_top_positive": positive,
        "shap_top_negative": negative,
        "improvement_suggestions": [f"Add evidence of {skill} to the resume." for skill in missing[:5]],
        "requirement_coverage": requirement_coverage,
    }


@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(""),
    role: str = Form(""),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    started = time.perf_counter()
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is required")
    if not resume.filename:
        raise HTTPException(status_code=400, detail="Resume filename is required")
    try:
        content = await resume.read()
        if not content:
            raise ValueError("Resume file is empty")
        profile = await _get_parser().parse(content, resume.filename)
    except (ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=422, detail=f"Resume parse error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Resume parse error: {exc}") from exc

    result = _score(profile, jd_text)
    result.update({
        "model_version": _model_version(),
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "candidate_name": getattr(profile, "name", None),
        "role": role,
    })
    if current_user is not None:
        try:
            report = AnalysisReport(
                user_id=current_user.id,
                resume_filename=resume.filename,
                target_role=role or None,
                job_description=jd_text[:5000],
                match_level=result.get("match_level") or "Not enough information",
                skill_coverage=result.get("skill_coverage"),
                overall_match_percent=result.get("overall_match_percent"),
                matched_skills=json.dumps(result.get("matched_skills", [])),
                missing_skills=json.dumps(result.get("missing_skills", [])),
                summary=result.get("summary") or "",
                requirement_coverage=json.dumps(result.get("requirement_coverage")),
            )
            db.add(report)
            await db.commit()
            result["report_id"] = str(report.id)
        except Exception as exc:
            await db.rollback()
            logger.warning("Could not save analysis report: %s", exc)
    return result


def set_app(app: Any) -> None:
    """Attach the FastAPI app so model version can be surfaced when available."""
    _model_version.app = app
