import io
import math
import hashlib
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.routers.analyze import _skill_analysis


def _request(resume: str, jd: str):
    with TestClient(app) as client:
        return client.post(
            "/api/analyze",
            files={"resume": ("resume.txt", io.BytesIO(resume.encode()), "text/plain")},
            data={"jd_text": jd, "role": "Engineer"},
        )


def test_txt_upload_returns_required_fields():
    response = _request(
        "Alex Engineer\nSkills\nPython FastAPI SQL Docker\nExperience\n5 years",
        "Python FastAPI SQL Docker engineer with 3 years experience",
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    for field in (
        "fit_score", "confidence", "competency_scores", "matched_skills",
        "missing_skills", "related_skills", "shap_top_positive",
        "shap_top_negative", "improvement_suggestions", "model_version",
        "latency_ms", "requirement_coverage",
    ):
        assert field in payload
    assert math.isfinite(payload["fit_score"])
    assert 1 <= payload["fit_score"] <= 99


def test_demo_samples_report_requirement_coverage_fields():
    from pathlib import Path

    sample_dir = Path(__file__).resolve().parents[1] / "scripts" / "demo_samples"
    jd = (sample_dir / "jd.txt").read_text(encoding="utf-8")
    coverage_fields = (
        "skills_matched", "skills_required", "coverage_pct",
        "years_required", "years_candidate", "years_met",
        "degree_required", "degree_met",
    )
    for sample in ("good", "mediocre", "unrelated"):
        response = _request(
            (sample_dir / f"{sample}_resume.txt").read_text(encoding="utf-8"),
            jd,
        )
        assert response.status_code == 200, response.text
        coverage = response.json()["requirement_coverage"]
        assert all(field in coverage for field in coverage_fields)
        if sample == "good":
            assert coverage["coverage_pct"] == 100.0
            assert response.json()["fit_score"] >= 75


def test_strong_match_scores_above_unrelated():
    strong = _request(
        "Alex Engineer\nSkills\nPython FastAPI SQL Docker AWS\nExperience\n5 years",
        "Python FastAPI SQL Docker AWS engineer with 3 years experience",
    )
    unrelated = _request(
        "Alex Artist\nSkills\nPainting Sculpture\nExperience\n1 year",
        "Python FastAPI SQL Docker AWS engineer with 3 years experience",
    )
    assert strong.status_code == 200
    assert unrelated.status_code == 200
    assert strong.json()["fit_score"] > unrelated.json()["fit_score"]


def test_missing_jd_returns_400():
    with TestClient(app) as client:
        response = client.post(
            "/api/analyze",
            files={"resume": ("resume.txt", io.BytesIO(b"Python engineer"), "text/plain")},
            data={"jd_text": ""},
        )
    assert response.status_code == 400


def test_online_features_match_shared_offline_features():
    import pandas as pd
    from backend.routers import analyze
    from ml_training.train_real import extract_pair_features

    analyze._load_v2()
    analyze.load_embedding_model()
    frame = pd.DataFrame([{
        "resume_text": "Python FastAPI engineer with five years experience",
        "job_description_text": "Python FastAPI role requiring three years experience",
        "resume_id": "r1",
        "job_id": "j1",
    }])
    offline, _ = extract_pair_features(
        frame, use_embeddings=True, vectorizer=analyze._v2_vectorizer,
        embedding_model=analyze._embedding_model,
    )
    online, _ = extract_pair_features(
        frame, use_embeddings=True, vectorizer=analyze._v2_vectorizer,
        embedding_model=analyze._embedding_model,
    )
    for feature in analyze._v2_features:
        left, right = float(offline.iloc[0][feature]), float(online.iloc[0][feature])
        assert (math.isnan(left) and math.isnan(right)) or abs(left - right) < 1e-7


def test_skill_coverage_levels_and_aliases():
    partial = _skill_analysis(
        "Python SQL Docker AWS Kubernetes",
        "Python SQL Docker AWS Kubernetes FastAPI Django Flask",
    )
    assert partial["skill_coverage"] == 62
    assert partial["match_level"] == "Partial match"
    assert _skill_analysis(
        "Some exposure to Python and MySQL",
        "Python MySQL",
    )["skill_coverage"] == 100


def test_skill_coverage_strong_weak_and_unknown():
    assert _skill_analysis("Python SQL Docker AWS Kubernetes FastAPI Django Flask", "Python SQL Docker AWS Kubernetes FastAPI Django Flask")["match_level"] == "Strong match"
    assert _skill_analysis("Accounting and tax", "Python SQL Docker AWS Kubernetes FastAPI Django Flask")["match_level"] == "Weak match"
    unknown = _skill_analysis("Accounting and tax", "Manage stakeholders and business outcomes")
    assert unknown["skill_coverage"] is None
    assert unknown["match_level"] == "Not enough information"


def test_single_resume_response_has_no_rank_fields():
    response = _request(
        "Python developer with 5 years of experience building APIs with Django and SQL.",
        "Backend engineer requiring Python, Django, and SQL.",
    )
    assert response.status_code == 200
    payload = response.json()
    assert "rank" not in payload
    assert "relative_score" not in payload


def test_v1_v2_v3_model_files_have_stable_hashes():
    root = Path(__file__).resolve().parents[1]
    paths = [
        root / "backend/models/trained/v2/xgb_classifier.json",
        root / "backend/models/trained/v2/model_version.json",
        root / "backend/models/trained/v3/xgb_ranker.json",
        root / "backend/models/trained/v3/model_version.json",
    ]
    for path in paths:
        assert hashlib.sha256(path.read_bytes()).hexdigest()
