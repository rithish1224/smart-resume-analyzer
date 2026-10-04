"""Train and evaluate the v3 grouped resume/job ranking model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import average_precision_score, ndcg_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml_training.train_real import (
    DEFAULT_DATASET,
    extract_pair_features,
    load_real_dataset,
)

OUT = ROOT / "backend" / "models" / "trained" / "v3"
SEED = 42
BASE_FEATURES = [
    "tfidf_similarity", "skill_match_ratio", "resume_skill_count",
    "jd_skill_count", "missing_skill_count", "exp_years", "required_years",
    "exp_gap", "num_projects", "num_certs", "degree_level", "has_degree",
    "gpa", "has_gpa", "resume_chars", "jd_chars",
    "minilm_mean_cosine", "minilm_max_cosine",
]
MISSING_FLAGS = ["exp_years_missing", "required_years_missing", "gpa_missing"]
FEATURES = BASE_FEATURES + MISSING_FLAGS
LABELS = {"no fit": 0, "potential fit": 1, "good fit": 2}
SKILL_ALIASES = {
    "nodejs": "node.js", "node js": "node.js", "postgres": "postgresql",
    "postgresql": "postgresql", "scikit learn": "scikit-learn",
    "spring boot": "spring boot", "mysql": "mysql",
}
SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "mysql",
    "nosql", "aws", "azure", "gcp", "docker", "kubernetes", "pytorch",
    "tensorflow", "scikit-learn", "machine learning", "deep learning", "nlp",
    "fastapi", "django", "react", "git", "spark", "airflow", "tableau",
    "power bi", "rest", "api", "terraform", "github actions", "postgresql",
    "redis", "flask", "node.js", "spring boot",
}


def clean_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = text.replace("\u00ad", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalized_skills(text: str) -> set[str]:
    lowered = clean_text(text).lower().replace("nodejs", "node.js")
    lowered = re.sub(r"\bpostgres\b", "postgresql", lowered)
    lowered = lowered.replace("scikit learn", "scikit-learn")
    found = set()
    for skill in sorted(SKILLS, key=len, reverse=True):
        if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", lowered):
            found.add(SKILL_ALIASES.get(skill, skill))
    return found


def degree_level(text: str) -> float:
    text = clean_text(text).lower()
    if re.search(r"\b(?:m\.?tech|m\.?sc|mba|master(?:'s)?|ph\.?d)\b", text):
        return 3.0
    if re.search(r"\b(?:b\.?tech|b\.?e|b\.?sc|bachelor(?:'s)?|bdes)\b", text):
        return 2.0
    if re.search(r"\b(?:b\.?com|diploma|associate)\b", text):
        return 1.0
    return np.nan


def project_count(text: str) -> float:
    text = clean_text(text)
    numbered = re.findall(
        r"\b(?:led|built|created|developed|implemented|completed)\s+(\d+)\s+"
        r"(?:projects?|web\s+apps?|applications?|apps?)\b", text, re.I)
    if numbered:
        return float(sum(map(int, numbered)))
    hits = re.findall(r"\b(?:projects?|portfolio|developed|built|implemented)\b", text, re.I)
    return float(len(hits))


def prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["resume_text"] = frame["resume_text"].map(clean_text)
    frame["job_description_text"] = frame["job_description_text"].map(clean_text)
    frame["label_id"] = frame["label"].map(
        lambda x: LABELS.get(str(x).strip().lower(), x if isinstance(x, (int, float)) else np.nan)
    )
    frame = frame[frame["label_id"].isin([0, 1, 2])].copy()
    frame = frame[
        frame["resume_text"].str.split().str.len().ge(30)
        & frame["job_description_text"].str.split().str.len().ge(30)
    ]
    frame = frame.drop_duplicates(["resume_text", "job_description_text"]).reset_index(drop=True)
    frame["label_id"] = frame["label_id"].astype(int)
    frame["resume_id"] = frame["resume_text"].map(lambda x: hashlib.sha256(x.encode()).hexdigest())
    frame["job_id"] = frame["job_description_text"].map(lambda x: hashlib.sha256(x.encode()).hexdigest())
    return frame.reset_index(drop=True)


def connected_components(frame: pd.DataFrame) -> list[list[int]]:
    parent: dict[str, str] = {}
    def find(x: str) -> str:
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(a: str, b: str) -> None:
        parent[find(a)] = find(b)
    for row in frame.itertuples():
        union("r:" + row.resume_id, "j:" + row.job_id)
    groups: dict[str, list[int]] = {}
    for i, row in frame.iterrows():
        groups.setdefault(find("r:" + row.resume_id), []).append(int(i))
    return list(groups.values())


def grouped_split(frame: pd.DataFrame, seed: int = SEED) -> dict[str, np.ndarray]:
    print(f"unique resume_ids: {frame.resume_id.nunique()}")
    print(f"unique job_ids: {frame.job_id.nunique()}")
    job_sizes = frame.groupby("job_id").size()
    print(f"rows per job (min, median, max): {job_sizes.min()}, {job_sizes.median()}, {job_sizes.max()}")
    print(f"resumes under more than one job: {int(frame.groupby('resume_id').job_id.nunique().gt(1).sum())}")
    rng = np.random.default_rng(seed)
    resumes = list(rng.permutation(frame.resume_id.unique()))
    targets = {"train": len(frame) * 0.60, "validation": len(frame) * 0.15, "test": len(frame) * 0.25}
    buckets = {name: [] for name in targets}
    sizes = {name: 0 for name in targets}
    for resume_id in resumes:
        name = min(targets, key=lambda n: sizes[n] / max(targets[n], 1))
        rows = frame.index[frame.resume_id == resume_id].tolist()
        buckets[name].extend(rows)
        sizes[name] += len(rows)
    result = {name: np.array(sorted(indices), dtype=int) for name, indices in buckets.items()}
    for _, rows in frame.groupby("resume_id").groups.items():
        memberships = {name for name, indices in result.items() if set(rows) & set(indices)}
        assert len(memberships) == 1
    shared_jobs = len(
        set(frame.loc[result["train"], "job_id"]) & set(frame.loc[result["test"], "job_id"])
    )
    print("split rows:", {k: len(v) for k, v in result.items()})
    print("split resumes:", {k: frame.loc[v, "resume_id"].nunique() for k, v in result.items()})
    print(f"job_ids shared between train and test: {shared_jobs}")
    print("qualifying job groups:", {k: len(_groups(frame, v)) for k, v in result.items()})
    return result


def resolve_training_label_noise(frame: pd.DataFrame, train_indices: np.ndarray) -> tuple[pd.DataFrame, list[int]]:
    train = frame.loc[train_indices]
    flagged: list[int] = []
    for _, rows in train.groupby(["resume_id", "job_id"]).groups.items():
        labels = frame.loc[list(rows), "label_id"]
        if labels.nunique() > 1:
            counts = labels.value_counts()
            if counts.iloc[0] == counts.iloc[1]:
                flagged.extend(int(i) for i in rows)
    return frame.drop(index=flagged), flagged


def add_fixed_features(frame: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    result = base.copy()
    result["skill_match_ratio"] = [
        len(normalized_skills(r) & normalized_skills(j)) / max(len(normalized_skills(j)), 1)
        for r, j in zip(frame.resume_text, frame.job_description_text)
    ]
    result["resume_skill_count"] = [float(len(normalized_skills(x))) for x in frame.resume_text]
    result["jd_skill_count"] = [float(len(normalized_skills(x))) for x in frame.job_description_text]
    result["missing_skill_count"] = [
        float(len(normalized_skills(j) - normalized_skills(r)))
        for r, j in zip(frame.resume_text, frame.job_description_text)
    ]
    result["degree_level"] = frame.resume_text.map(degree_level)
    result["has_degree"] = result["degree_level"].notna().astype(float)
    result["num_projects"] = frame.resume_text.map(project_count)
    for name, source in (("gpa", r"\b(?:gpa|cgpa)\s*[:=-]?\s*(\d+(?:\.\d+)?)"),
                         ("exp_years", r"(?i)(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s+(?:of\s+)?experience"),
                         ("required_years", r"(?i)(\d+(?:\.\d+)?)\s*\+\s*years?")):
        if name == "gpa":
            result[name] = frame.resume_text.str.extract(source, expand=False).astype(float)
        elif name == "exp_years":
            result[name] = frame.resume_text.str.extract(source, expand=False).astype(float)
        else:
            result[name] = frame.job_description_text.str.extract(source, expand=False).astype(float)
    result["exp_gap"] = result["exp_years"] - result["required_years"]
    result["exp_years_missing"] = result["exp_years"].isna().astype(float)
    result["required_years_missing"] = result["required_years"].isna().astype(float)
    result["gpa_missing"] = result["gpa"].isna().astype(float)
    return result


def impute_train_medians(features: pd.DataFrame, train: np.ndarray) -> tuple[pd.DataFrame, dict[str, float]]:
    medians = {c: float(features.loc[train, c].median()) for c in FEATURES if features[c].isna().any()}
    output = features.copy()
    for column, value in medians.items():
        output[column] = output[column].fillna(value)
    return output[FEATURES], medians


def scale_within_groups(scores: np.ndarray, group_ids: pd.Series) -> np.ndarray:
    out = np.zeros(len(scores), dtype=float)
    for _, indices in group_ids.groupby(group_ids).groups.items():
        idx = np.asarray(list(indices), dtype=int)
        values = scores[idx]
        lo, hi = values.min(), values.max()
        out[idx] = 50.0 if len(idx) == 1 or hi == lo else (values - lo) / (hi - lo) * 100.0
    return out


def _groups(frame: pd.DataFrame, indices: np.ndarray) -> list[np.ndarray]:
    return [
        g.index.to_numpy()
        for _, g in frame.loc[indices].groupby("job_id")
        if len(g) >= 2 and ("label_id" not in g or g.label_id.nunique() >= 2)
    ]


def metric_rows(frame: pd.DataFrame, scores: np.ndarray, indices: np.ndarray) -> list[dict[str, float]]:
    rows = []
    for group in _groups(frame, indices):
        labels = frame.loc[group, "label_id"].to_numpy()
        values = scores[group]
        rows.append({
            "ndcg@3": float(ndcg_score([labels], [values], k=3, sample_weight=None)),
            "ndcg@5": float(ndcg_score([labels], [values], k=5)),
            "ndcg@10": float(ndcg_score([labels], [values], k=10)),
            "map": float(average_precision_score(labels > 0, values)),
            "good_potential": _pair_accuracy(labels, values, 2, 1),
            "potential_no_fit": _pair_accuracy(labels, values, 1, 0),
            "good_no_fit": _pair_accuracy(labels, values, 2, 0),
        })
    return rows


def _pair_accuracy(labels: np.ndarray, scores: np.ndarray, high: int, low: int) -> float:
    high_scores, low_scores = scores[labels == high], scores[labels == low]
    return float(np.mean(high_scores[:, None] > low_scores[None, :])) if len(high_scores) and len(low_scores) else np.nan


def summarize(rows: list[dict[str, float]]) -> dict[str, float]:
    keys = rows[0].keys() if rows else ["ndcg@3", "ndcg@5", "ndcg@10", "map", "good_potential", "potential_no_fit", "good_no_fit"]
    return {key: float(np.nanmean([row[key] for row in rows])) if rows else float("nan") for key in keys} | {"qualified_groups": len(rows)}


def bootstrap(rows: list[dict[str, float]], seed: int = SEED, n: int = 500) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    if not rows:
        return {}
    keys = list(rows[0])
    samples = {key: [] for key in keys}
    for _ in range(n):
        chosen = rng.integers(0, len(rows), len(rows))
        for key in keys:
            samples[key].append(float(np.nanmean([rows[i][key] for i in chosen])))
    return {key: [float(np.nanpercentile(values, 2.5)), float(np.nanpercentile(values, 97.5))] for key, values in samples.items()}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-embeddings", action="store_true")
    args = parser.parse_args(argv)
    if args.no_embeddings:
        warnings.warn("This is a quick pipeline check; final v3 reports require MiniLM embeddings.")
    frame, source = load_real_dataset(DEFAULT_DATASET)
    frame = prepare_frame(frame)
    splits = grouped_split(frame)
    qualifying_test_groups = len(_groups(frame, splits["test"]))
    print("qualifying test groups:", qualifying_test_groups)
    if len(splits["train"]) < 2000 or qualifying_test_groups < 60:
        raise RuntimeError(
            f"Insufficient resume split: train={len(splits['train'])}, "
            f"qualifying_test_groups={qualifying_test_groups}; stopped before training."
        )
    frame, flagged = resolve_training_label_noise(frame, splits["train"])
    splits = {name: np.array([i for i in indices if i in frame.index]) for name, indices in splits.items()}
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=1500)
    vectorizer.fit((frame.loc[splits["train"], "resume_text"] + " " + frame.loc[splits["train"], "job_description_text"]).tolist())
    embedding_model = None
    if not args.no_embeddings:
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    raw, meta = extract_pair_features(frame, train_indices=splits["train"], vectorizer=vectorizer, embedding_model=embedding_model, use_embeddings=not args.no_embeddings)
    features = add_fixed_features(frame, raw)
    features, medians = impute_train_medians(features, splits["train"])
    train, val, test = (np.array(sorted(splits[x])) for x in ("train", "validation", "test"))
    ordered = np.concatenate([train, val, test])
    def fit_ranker(objective: str, depth: int, lr: float, trees: int, early: bool = True) -> xgb.XGBRanker:
        model = xgb.XGBRanker(objective=objective, n_estimators=trees, max_depth=depth, learning_rate=lr, subsample=.8, colsample_bytree=.8, random_state=SEED, n_jobs=2, eval_metric="ndcg@10", early_stopping_rounds=30 if early else None)
        train_order = train[np.argsort(frame.loc[train, "job_id"].to_numpy())]
        val_order = val[np.argsort(frame.loc[val, "job_id"].to_numpy())]
        model.fit(features.loc[train_order], frame.loc[train_order, "label_id"], group=frame.loc[train_order].groupby("job_id").size().to_numpy(), eval_set=[(features.loc[val_order], frame.loc[val_order, "label_id"])], eval_group=[frame.loc[val_order].groupby("job_id").size().to_numpy()], verbose=False)
        return model
    best = None
    for depth in (3, 4):
        for lr in (.05, .1):
            candidate = fit_ranker("rank:ndcg", depth, lr, 300)
            score = float(candidate.evals_result()["validation_0"]["ndcg@10"][-1])
            if best is None or score > best[0]:
                best = (score, depth, lr, candidate.best_iteration + 1 if candidate.best_iteration is not None else 300)
    _, depth, lr, trees = best
    model = fit_ranker("rank:ndcg", depth, lr, trees, early=False)
    pairwise = fit_ranker("rank:pairwise", depth, lr, trees, early=False)
    predictions = {name: model.predict(features) for name, model in (("v3", model), ("pairwise", pairwise))}
    rng = np.random.default_rng(SEED)
    predictions["random"] = rng.random(len(frame))
    predictions["tfidf"] = features["tfidf_similarity"].to_numpy()
    predictions["minilm"] = features["minilm_mean_cosine"].to_numpy()
    baseline_v2 = xgb.XGBClassifier(
        n_estimators=300, max_depth=4, learning_rate=.05, subsample=.8,
        colsample_bytree=.8, random_state=SEED, n_jobs=2,
        objective="binary:logistic", eval_metric="logloss",
        early_stopping_rounds=30,
    )
    baseline_v2.fit(
        features.loc[train, BASE_FEATURES], (frame.loc[train, "label_id"] > 1).astype(int),
        eval_set=[(features.loc[val, BASE_FEATURES], (frame.loc[val, "label_id"] > 1).astype(int))],
        verbose=False,
    )
    predictions["retrained v2 baseline"] = baseline_v2.predict_proba(features[BASE_FEATURES])[:, 1]
    try:
        saved_v2 = xgb.XGBClassifier()
        saved_v2.load_model(str(ROOT / "backend/models/trained/v2/xgb_classifier.json"))
        predictions["saved v2 (has seen some of these resumes, likely inflated)"] = saved_v2.predict_proba(features[BASE_FEATURES])[:, 1]
    except Exception as exc:
        warnings.warn(f"v2 comparison unavailable: {exc}")
    reports = {name: summarize(metric_rows(frame, values, test)) for name, values in predictions.items()}
    intervals = {name: bootstrap(metric_rows(frame, values, test)) for name, values in predictions.items()}
    out = OUT
    out.mkdir(parents=True, exist_ok=True)
    model.save_model(out / "xgb_ranker.json")
    with (out / "feature_metadata.pkl").open("wb") as handle:
        import pickle
        pickle.dump({"vectorizer": vectorizer, "medians": medians, "features": FEATURES}, handle)
    split_ids = {name: [{"row_id": int(i), "resume_id": frame.loc[i, "resume_id"], "job_id": frame.loc[i, "job_id"]} for i in indices] for name, indices in splits.items()}
    (out / "split_ids.json").write_text(json.dumps(split_ids, indent=2), encoding="utf-8")
    versions = {"numpy": np.__version__, "pandas": pd.__version__, "xgboost": xgb.__version__}
    import sklearn
    versions["scikit-learn"] = sklearn.__version__
    import sentence_transformers
    versions["sentence-transformers"] = sentence_transformers.__version__
    model_version = {"version": "3.0", "model_type": "XGBRanker", "features": FEATURES, "seed": SEED, "source": source, "hyperparameters": {"objective": "rank:ndcg", "max_depth": depth, "learning_rate": lr, "n_estimators": trees}, "library_versions": versions, "metrics": reports["v3"], "relative_score": True, "relative_score_is_probability": False}
    (out / "model_version.json").write_text(json.dumps(model_version, indent=2), encoding="utf-8")
    report = {"source": source, "rows": len(frame), "flagged_training_rows": flagged, "splits": {k: len(v) for k, v in splits.items()}, "qualifying_test_groups": qualifying_test_groups, "metrics": reports, "bootstrap_95": intervals, "notes": ["The dataset has one connected component, so splitting is by resume; job overlap is allowed for ranking.", "Only 642 unique resumes exist, so effective sample size is small and uncertain.", "Labels are proxy judgments.", "Dataset license is not declared.", "Use only as human-review assistance; no automatic rejects.", "Fairness check TODO.", "Saved v2 has seen some test resumes and may be inflated."]}
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# V3 evaluation", "", f"Rows: {len(frame)}; splits: {report['splits']}; flagged training conflicts: {len(flagged)}.", "", "| Method | NDCG@3 | NDCG@5 | NDCG@10 | MAP | Good>Potential | Potential>No Fit | Good>No Fit |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, values in reports.items():
        lines.append("| " + name + " | " + " | ".join(f"{values.get(k, float('nan')):.4f}" for k in ("ndcg@3", "ndcg@5", "ndcg@10", "map", "good_potential", "potential_no_fit", "good_no_fit")) + " |")
    lines += ["", "NDCG uses gain `2^relevance - 1`; intervals are 500 group bootstrap resamples.", "Scores are relative 0-100 values within each job, not probabilities.", "The dataset resumes and jobs form one connected component, so a split keeping both axes separate was impossible; splitting by resume is the appropriate axis for candidate ranking, and job overlap is allowed.", "Only 642 unique resumes exist, so the effective sample size is small and results are uncertain.", "The saved v2 comparison is labelled as potentially inflated because v2 saw some of these resumes; the retrained v2 baseline is the fairer comparison.", "The dataset has no declared license; labels are proxy judgments. The model assists human reviewers only and must not make automatic rejects. Fairness check TODO."]
    (ROOT / "docs" / "v3_eval.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(reports["v3"], indent=2))


if __name__ == "__main__":
    main()
