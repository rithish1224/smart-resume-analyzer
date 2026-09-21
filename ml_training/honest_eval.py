"""Measure the frozen ranking baseline on synthetic holdout and public data.

This module intentionally never writes to backend/models/trained/xgb_ranker.json
or model_version.json. Run it from the repository root with:

    python ml_training/honest_eval.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import average_precision_score, ndcg_score, roc_auc_score
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml_training.feature_engineering import extract_features

FEATURES = ["exp_years", "skill_match_ratio", "num_projects", "num_certs", "gpa"]
MODEL_PARAMS = {
    "objective": "rank:ndcg",
    "n_estimators": 200,
    "max_depth": 5,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
}


def new_model() -> xgb.XGBRanker:
    return xgb.XGBRanker(**MODEL_PARAMS)


def grouped_metrics(
    frame: pd.DataFrame, scores: np.ndarray, label_column: str, group_column: str
) -> dict[str, float | int]:
    """Calculate ranking metrics only for groups with useful label variation."""
    groups: list[tuple[np.ndarray, np.ndarray]] = []
    for _, group in frame.groupby(group_column, sort=False):
        labels = group[label_column].to_numpy(dtype=float)
        group_scores = scores[group.index.to_numpy()]
        if len(labels) >= 2 and len(np.unique(labels)) > 1:
            groups.append((labels, group_scores))

    if not groups:
        return {
            "qualifying_groups": 0,
            "ndcg@5": float("nan"),
            "ndcg@10": float("nan"),
            "p@5": float("nan"),
        }

    ndcg5 = [ndcg_score([labels], [values], k=5) for labels, values in groups]
    ndcg10 = [ndcg_score([labels], [values], k=10) for labels, values in groups]
    precision = []
    for labels, values in groups:
        top = labels[np.argsort(values)[::-1][: min(5, len(labels))]]
        precision.append(float(np.sum(top > 0) / len(top)))
    return {
        "qualifying_groups": len(groups),
        "ndcg@5": float(np.mean(ndcg5)),
        "ndcg@10": float(np.mean(ndcg10)),
        "p@5": float(np.mean(precision)),
    }


def binary_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    binary = (labels > 0).astype(int)
    return {
        "roc_auc": float(roc_auc_score(binary, scores))
        if len(np.unique(binary)) > 1
        else float("nan"),
        "map": float(average_precision_score(binary, scores))
        if len(np.unique(binary)) > 1
        else float("nan"),
    }


def train_synthetic_holdout() -> dict[str, float | int]:
    path = Path(__file__).with_name("training_features.csv")
    data = pd.read_csv(path)
    rng = np.random.default_rng(42)
    train_parts = []
    test_parts = []
    for _, domain in data.groupby("domain", sort=False):
        order = rng.permutation(len(domain))
        split = int(len(domain) * 0.8)
        train_parts.append(domain.iloc[order[:split]])
        test_parts.append(domain.iloc[order[split:]])
    train = pd.concat(train_parts).sort_values("domain").reset_index(drop=True)
    test = pd.concat(test_parts).sort_values("domain").reset_index(drop=True)

    model = new_model()
    model.fit(
        train[FEATURES],
        train["is_shortlisted"],
        group=train.groupby("domain", sort=False).size().to_numpy(),
    )
    scores = model.predict(test[FEATURES])
    result = grouped_metrics(test, scores, "is_shortlisted", "domain")
    result.update(binary_metrics(test["is_shortlisted"].to_numpy(), scores))
    result["rows"] = len(test)
    return result


def load_roles() -> dict[str, dict[str, Any]]:
    import json

    with (ROOT / "backend" / "data" / "role_templates.json").open(
        encoding="utf-8"
    ) as handle:
        return json.load(handle)


def infer_role(jd: str, roles: dict[str, dict[str, Any]]) -> str:
    jd_lower = jd.lower()
    scores = {
        role: sum(skill.lower() in jd_lower for skill in data["critical_skills"])
        for role, data in roles.items()
    }
    return max(scores, key=scores.get) if scores else "software_engineer"


def extract_real_features(
    resume: str, jd: str, roles: dict[str, dict[str, Any]]
) -> dict[str, float]:
    role = infer_role(jd, roles)
    role_template = roles[role]
    skills = [
        skill
        for skill in role_template["critical_skills"]
        if skill.lower() in resume.lower()
    ]
    years = re.search(r"(?i)(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", resume)
    gpa = re.search(r"(?i)(?:gpa|cgpa)\s*[:=-]?\s*(\d+(?:\.\d+)?)", resume)
    project_hits = re.findall(r"(?i)\b(?:project|developed|built|implemented)\b", resume)
    cert_hits = re.findall(r"(?i)\b(?:certified|certification|certificate)\b", resume)
    candidate = {
        "experience_years": float(years.group(1)) if years else np.nan,
        "skills": skills,
        "projects": [{} for _ in project_hits] if project_hits else [],
        "certifications": cert_hits,
        "education": {"gpa": float(gpa.group(1)) if gpa else np.nan},
    }
    values = extract_features(candidate, role_template, jd).to_dict()
    # The shared helper's defaults are useful for structured profiles but would
    # falsely claim extraction on unstructured real text.
    values["exp_years"] = candidate["experience_years"]
    values["skill_match_ratio"] = values["critical_skill_ratio"]
    values["num_projects"] = float(len(project_hits)) if project_hits else np.nan
    values["num_certs"] = float(len(cert_hits)) if cert_hits else np.nan
    values["gpa"] = candidate["education"]["gpa"]
    return {feature: values.get(feature, np.nan) for feature in FEATURES}


def inspect_and_load_real_data() -> pd.DataFrame | None:
    try:
        from datasets import load_dataset, load_dataset_builder

        builder = load_dataset_builder("cnamuangtoun/resume-job-description-fit")
        print(f"Real dataset columns: {list(builder.info.features)}")
        print(f"Real dataset license: {builder.info.license or 'not declared'}")
        data = load_dataset("cnamuangtoun/resume-job-description-fit")
    except Exception as exc:
        print(
            "Could not download the real dataset. Install `datasets`, then run "
            "`python ml_training/honest_eval.py` with network access. "
            f"Details: {exc}"
        )
        return None

    split = next(iter(data.values())) if hasattr(data, "values") else data
    frame = split.to_pandas()
    required = {"resume_text", "job_description_text", "label"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    labels = {"No Fit": 0, "Potential Fit": 1, "Good Fit": 2}
    frame["label_id"] = frame["label"].map(labels)
    frame = frame.dropna(subset=["label_id"]).reset_index(drop=True)
    return frame


def score_real_data(frame: pd.DataFrame) -> dict[str, Any]:
    roles = load_roles()
    feature_rows = [
        extract_real_features(str(row.resume_text), str(row.job_description_text), roles)
        for row in frame.itertuples()
    ]
    features = pd.DataFrame(feature_rows, columns=FEATURES)
    print("Real extraction coverage:")
    for feature in FEATURES:
        print(f"  {feature}: {features[feature].notna().mean():.4f}")

    model = xgb.XGBRanker()
    model.load_model(ROOT / "backend" / "models" / "trained" / "baseline_v1" / "xgb_ranker.json")
    model_scores = model.predict(features)
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_scores = np.array(
        [
            cosine_similarity(
                vectorizer.fit_transform([row.resume_text, row.job_description_text])
            )[0, 1]
            for row in frame.itertuples()
        ]
    )
    rng = np.random.default_rng(42)
    random_scores = rng.random(len(frame))
    frame = frame.copy()
    frame["jd_group"] = frame["job_description_text"]
    results = {}
    for name, scores in (
        ("real data", model_scores),
        ("TF-IDF", tfidf_scores),
        ("random", random_scores),
    ):
        metrics = grouped_metrics(frame, scores, "label_id", "jd_group")
        metrics.update(binary_metrics(frame["label_id"].to_numpy(), scores))
        metrics["spearman"] = float(
            spearmanr(frame["label_id"], scores, nan_policy="omit").statistic
        )
        results[name] = metrics
    return results


def write_report(
    synthetic: dict[str, float | int], real: dict[str, dict[str, Any]] | None
) -> None:
    rows = [
        ("synthetic in-sample", "0.9836", "0.9533", "0.9750", "0.8903", "0.9485", "n/a"),
        (
            "synthetic holdout",
            synthetic["ndcg@5"],
            synthetic["ndcg@10"],
            synthetic["p@5"],
            synthetic["map"],
            synthetic["roc_auc"],
            "n/a",
        ),
    ]
    if real:
        for name in ("real data", "TF-IDF", "random"):
            m = real[name]
            rows.append(
                (
                    name,
                    m["ndcg@5"],
                    m["ndcg@10"],
                    m["p@5"],
                    m["map"],
                    m["roc_auc"],
                    m["spearman"],
                )
            )
    else:
        rows.extend((name, "skipped", "skipped", "skipped", "skipped", "skipped", "skipped")
                    for name in ("real data", "TF-IDF", "random"))
    lines = [
        "# Honest evaluation",
        "",
        "All measured values below are from this evaluation run. Synthetic "
        "in-sample values are the frozen report and are explicitly **in-sample, "
        "synthetic labels, no holdout**.",
        "",
        "| Evaluation | NDCG@5 | NDCG@10 | P@5 | MAP | ROC-AUC | Spearman |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                f"{value:.4f}" if isinstance(value, float) else str(value)
                for value in row[:5]
            )
            + " | "
            + " | ".join(
                f"{value:.4f}" if isinstance(value, float) else str(value)
                for value in row[5:]
            )
            + " |"
        )
    lines += [
        "",
        (
            f"Real-data qualifying JD groups: "
            f"{real['real data']['qualifying_groups'] if real else 'skipped'}."
        ),
        "",
        "## Limitations and assumptions",
        "",
        "- The synthetic holdout is an 80/20 random split within each domain "
        "with seed 42; no tuning was performed.",
        "- Real text feature extraction is heuristic. Missing experience, "
        "projects, certifications, or GPA remain NaN and are passed to XGBoost.",
        "- Real NDCG and P@5 use only job-description groups with at least two "
        "resumes and differing labels; the qualifying count is printed by the "
        "evaluator.",
        "- Real ROC-AUC treats `Good Fit` as positive and both other labels as "
        "negative. Spearman uses the ordinal labels 0, 1, and 2.",
        "- The dataset's license metadata is printed at runtime and is not "
        "assumed when it is blank.",
    ]
    (ROOT / "docs" / "honest_eval.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    synthetic = train_synthetic_holdout()
    print("\nSynthetic holdout:", synthetic)
    real_frame = inspect_and_load_real_data()
    real = score_real_data(real_frame) if real_frame is not None else None
    if real:
        print("\nReal-data comparison:")
        for name, metrics in real.items():
            print(f"{name}: {metrics}")
    write_report(synthetic, real)
    print(f"\nComparison report written to {ROOT / 'docs' / 'honest_eval.md'}")


if __name__ == "__main__":
    main()
