"""Print the inference evidence for each sample demo pair."""
import asyncio
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.routers import analyze
from backend.services.parser import ResumeParser
from ml_training.feature_engineering import (
    extract_degree_level,
    extract_experience_years,
    extract_required_years,
)
from ml_training.train_real import extract_pair_features, extract_normalized_skills


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "scripts" / "demo_samples"
CASES = ("good", "mediocre", "unrelated")


async def parse(parser, path: Path):
    return await parser.parse(path.read_bytes(), path.name)


def main() -> None:
    analyze._load_v2()
    analyze.load_embedding_model()
    parser = ResumeParser()
    for name in CASES:
        resume_text = (SAMPLES / f"{name}_resume.txt").read_text(encoding="utf-8")
        jd_text = (SAMPLES / "jd.txt").read_text(encoding="utf-8")
        frame = pd.DataFrame([{
            "resume_text": resume_text,
            "job_description_text": jd_text,
            "resume_id": f"demo-{name}",
            "job_id": "demo-jd",
        }])
        features, _ = extract_pair_features(
            frame, use_embeddings=True, vectorizer=analyze._v2_vectorizer,
            embedding_model=analyze._embedding_model,
        )
        ordered = features.reindex(columns=analyze._v2_features)
        missing = [feature for feature in analyze._v2_features
                   if pd.isna(ordered.iloc[0][feature])]
        imputed = ordered.fillna(0.0)
        raw_probability = float(analyze._v2_model.predict_proba(imputed)[0, 1])
        calibrated = float(
            analyze._v2_calibrator.predict([raw_probability])[0]
        ) if analyze._v2_calibrator is not None else raw_probability
        shap_values = analyze._shap_explainer.shap_values(imputed)[0]
        contributions = sorted(
            [
                {"feature": feature, "value": round(float(value), 6)}
                for feature, value in zip(analyze._v2_features, shap_values)
            ],
            key=lambda item: abs(item["value"]),
            reverse=True,
        )[:10]
        resume_active, resume_related = extract_normalized_skills(resume_text)
        jd_active, jd_related = extract_normalized_skills(jd_text)
        print(f"\n=== {name} ===")
        print("features=" + json.dumps({
            feature: (None if pd.isna(value) else round(float(value), 6))
            for feature, value in ordered.iloc[0].items()
        }, sort_keys=True))
        print("imputed=" + json.dumps(missing))
        print(f"raw_score={raw_probability:.6f} calibrated_score={calibrated:.6f}")
        print("top_shap=" + json.dumps(contributions))
        print("extraction=" + json.dumps({
            "resume_exp_years": extract_experience_years(resume_text),
            "jd_required_years": extract_required_years(jd_text),
            "resume_degree": extract_degree_level(resume_text),
            "jd_degree": extract_degree_level(jd_text),
            "resume_skills": sorted(resume_active),
            "resume_related_skills": sorted(resume_related),
            "jd_skills": sorted(jd_active),
            "jd_related_skills": sorted(jd_related),
        }, allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    main()
