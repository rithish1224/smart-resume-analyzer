"""Part B resume analysis endpoint.

This router is additive: the existing v1 upload and score routes remain
unchanged while this endpoint composes the current parser with v2 inference.
"""
import re
import time
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.config import settings
from backend.services.parser import ResumeParser

router = APIRouter()

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


def _load_v2():
    global _v2_model, _v2_calibrator, _v2_features, _v2_vectorizer, _shap_explainer
    if _v2_model is not None:
        return
    model_path = Path(__file__).resolve().parents[1] / "models" / "trained" / "xgb_ranker_v2.json"
    metadata_path = Path(__file__).resolve().parents[1] / "models" / "trained" / "v2" / "model_version.json"
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
    from ml_training.train_real import extract_normalized_skills
    active, _ = extract_normalized_skills(text)
    return sorted(active)


def _model_version() -> str:
    metadata = Path(__file__).resolve().parents[1] / "models" / "trained" / "v2" / "model_version.json"
    if metadata.exists():
        try:
            return str(json.loads(metadata.read_text(encoding="utf-8")).get("version", "2.0"))
        except (OSError, ValueError):
            pass
    return getattr(settings, "MODEL_VERSION", "v1")


def _score(profile: Any, jd_text: str) -> Dict[str, Any]:
    from ml_training.train_real import extract_normalized_skills
    resume_skills, resume_related = extract_normalized_skills(
        getattr(profile, "raw_text", "") or ""
    )
    jd_skills = set(_skills(jd_text))
    matched = sorted(resume_skills.intersection(jd_skills))
    missing = sorted(jd_skills - resume_skills)
    _load_v2()
    if _embedding_model is None:
        load_embedding_model()
    from ml_training.train_real import extract_pair_features
    import pandas as pd
    row = pd.DataFrame([{
        "resume_text": getattr(profile, "raw_text", "") or "",
        "job_description_text": jd_text,
        "resume_id": "request-resume",
        "job_id": "request-job",
    }])
    pair_features, _ = extract_pair_features(
        row, use_embeddings=True, vectorizer=_v2_vectorizer,
        embedding_model=_embedding_model,
    )
    pair_features = pair_features.reindex(columns=_v2_features).fillna(0.0)
    probability = float(_v2_model.predict_proba(pair_features)[0, 1])
    if _v2_calibrator is not None:
        probability = float(_v2_calibrator.predict([probability])[0])
    score = round(max(0.0, min(100.0, probability * 100.0)), 2)

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
    return {
        "fit_score": score,
        "confidence": round(min(0.99, 0.5 + abs(score - 50) / 100), 3),
        "competency_scores": competency,
        "matched_skills": matched,
        "missing_skills": missing,
        "related_skills": related,
        "shap_top_positive": positive,
        "shap_top_negative": negative,
        "improvement_suggestions": [f"Add evidence of {skill} to the resume." for skill in missing[:5]],
    }


@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
    role: str = Form(""),
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
    return result


def set_app(app: Any) -> None:
    """Attach the FastAPI app so model version can be surfaced when available."""
    _model_version.app = app
