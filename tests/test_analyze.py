import io
import math

from fastapi.testclient import TestClient

from backend.main import app


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
        "latency_ms",
    ):
        assert field in payload
    assert math.isfinite(payload["fit_score"])
    assert 0 <= payload["fit_score"] <= 100


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
