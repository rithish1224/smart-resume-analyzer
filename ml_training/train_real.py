"""Train the v2 resume/job pair model on real labels.

The script is deliberately independent of the frozen v1 model.  It accepts a
local parquet/csv/json file or a HuggingFace dataset and writes all v2 output
below ``backend/models/trained/v2``.  Feature fitting is performed on the
training partition only, so the test report is an untouched evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import re
import warnings
from pathlib import Path
from typing import Any, Iterable
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    ndcg_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from scipy.stats import spearmanr
try:
    from .feature_engineering import (
        extract_certifications,
        extract_degree_level,
        extract_experience_years,
        extract_required_years,
    )
except ImportError:
    from feature_engineering import (
        extract_certifications,
        extract_degree_level,
        extract_experience_years,
        extract_required_years,
    )

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DEFAULT_DATASET = "cnamuangtoun/resume-job-description-fit"
LABELS = {"No Fit": 0, "Potential Fit": 1, "Good Fit": 2, "no fit": 0, "potential fit": 1, "good fit": 2}
DEFAULT_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "sql", "nosql", "aws",
    "azure", "gcp", "docker", "kubernetes", "pytorch", "tensorflow",
    "scikit-learn", "machine learning", "deep learning", "nlp", "fastapi",
    "django", "react", "git", "spark", "airflow", "tableau", "power bi",
}


def load_real_dataset(
    dataset: str = DEFAULT_DATASET,
    data_path: str | Path | None = None,
    split: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load and canonicalise a local or HF dataset.

    Canonical columns are ``resume_text``, ``job_description_text``, ``label``,
    and stable ``resume_id``/``job_id`` where available.
    """
    info: dict[str, Any] = {"source": str(data_path or dataset), "license": None}
    if data_path:
        path = Path(data_path)
        if path.suffix.lower() == ".csv":
            frame = pd.read_csv(path)
        elif path.suffix.lower() in {".json", ".jsonl"}:
            frame = pd.read_json(path, lines=path.suffix.lower() == ".jsonl")
        elif path.suffix.lower() in {".parquet", ".pq"}:
            frame = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported dataset file: {path}")
    else:
        try:
            from datasets import load_dataset, load_dataset_builder
            builder = load_dataset_builder(dataset)
            info["license"] = getattr(builder.info, "license", None)
            data = load_dataset(dataset)
        except Exception as exc:
            raise RuntimeError(
                "Unable to load the HuggingFace dataset. Pass --data-path for a local export."
            ) from exc
        selected = data[split] if split and split in data else next(iter(data.values())) if hasattr(data, "values") else data
        frame = selected.to_pandas()

    aliases = {
        "resume_text": ("resume_text", "resume", "cv", "resume_texts", "candidate_text"),
        "job_description_text": ("job_description_text", "job_description", "job", "jd", "description"),
        "label": ("label", "fit", "fit_label", "target", "rating"),
        "resume_id": ("resume_id", "candidate_id", "cv_id", "profile_id"),
        "job_id": ("job_id", "jd_id", "job_description_id", "role_id"),
    }
    for canonical, names in aliases.items():
        if canonical not in frame:
            for name in names:
                if name in frame:
                    frame[canonical] = frame[name]
                    break
    required = {"resume_text", "job_description_text", "label"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    frame["resume_text"] = frame["resume_text"].fillna("").astype(str)
    frame["job_description_text"] = frame["job_description_text"].fillna("").astype(str)
    frame["label_id"] = frame["label"].map(
        lambda x: LABELS.get(str(x).strip(), x if isinstance(x, (int, float)) else np.nan)
    )
    frame["label_id"] = pd.to_numeric(frame["label_id"], errors="coerce")
    frame = frame[frame["label_id"].isin([0, 1, 2])].copy()
    frame["label_id"] = frame["label_id"].astype(int)
    frame["resume_id"] = frame.get("resume_id", pd.Series(index=frame.index, dtype=object))
    frame["job_id"] = frame.get("job_id", pd.Series(index=frame.index, dtype=object))
    frame["resume_id"] = frame["resume_id"].fillna("").astype(str)
    frame["job_id"] = frame["job_id"].fillna("").astype(str)
    frame["ranking_job_id"] = frame["job_description_text"].map(
        lambda text: f"job-text-{hashlib.sha1(str(text).encode()).hexdigest()[:16]}"
    )
    # Use stable content identifiers when the export has no explicit IDs. This
    # preserves repeated JDs as ranking groups while preventing train/test
    # leakage through identical resume or job text.
    missing_resume = frame["resume_id"].eq("")
    missing_job = frame["job_id"].eq("")
    frame.loc[missing_resume, "resume_id"] = [
        f"text-{hashlib.sha1(str(text).encode()).hexdigest()[:16]}-row-{i}"
        for i, text in frame.loc[missing_resume, "resume_text"].items()
    ]
    frame.loc[missing_job, "job_id"] = [
        f"text-{hashlib.sha1(str(text).encode()).hexdigest()[:16]}-row-{i}"
        for i, text in frame.loc[missing_job, "job_description_text"].items()
    ]
    return frame.reset_index(drop=True), info


def _count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.I))


def extract_pair_features(
    frame: pd.DataFrame,
    train_indices: Iterable[int] | None = None,
    cache_dir: str | Path | None = None,
    use_embeddings: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Extract interpretable pair features and optionally cached MiniLM vectors."""
    train_idx = list(train_indices) if train_indices is not None else list(frame.index)
    skills = sorted(DEFAULT_SKILLS | {
        token.lower() for text in frame["job_description_text"]
        for token in re.findall(r"[A-Za-z][A-Za-z+#.-]{2,}", str(text))
        if token.lower() in DEFAULT_SKILLS
    })
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, max_features=1500)
    vectorizer.fit((frame.loc[train_idx, "resume_text"] + " " + frame.loc[train_idx, "job_description_text"]).tolist())
    rows: list[dict[str, float]] = []
    for _, row in frame.iterrows():
        resume, jd = row.resume_text.lower(), row.job_description_text.lower()
        jd_skills = {s for s in skills if re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", jd)}
        resume_skills = {s for s in skills if re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", resume)}
        years = extract_experience_years(resume)
        required_years = extract_required_years(jd)
        degree = extract_degree_level(resume)
        certs = extract_certifications(resume)
        gpa_match = re.search(r"(?i)\b(?:gpa|cgpa)\s*[:=-]?\s*(\d+(?:\.\d+)?)", resume)
        rows.append({
            "tfidf_similarity": float(np.nan_to_num(
                (vectorizer.transform([row.resume_text]) @ vectorizer.transform([row.job_description_text]).T).toarray()[0, 0],
                nan=0.0)),
            "skill_match_ratio": len(resume_skills & jd_skills) / len(jd_skills) if jd_skills else 0.0,
            "resume_skill_count": float(len(resume_skills)),
            "jd_skill_count": float(len(jd_skills)),
            "missing_skill_count": float(len(jd_skills - resume_skills)),
            "exp_years": years,
            "required_years": required_years,
            "exp_gap": years - required_years if np.isfinite(required_years) else np.nan,
            "num_projects": float(_count(r"\b(?:projects?|portfolio|developed|built|implemented)\b", resume)),
            "num_certs": float(len(certs)) if certs else np.nan,
            "degree_level": degree,
            "has_degree": float(np.isfinite(degree)),
            "gpa": float(gpa_match.group(1)) if gpa_match else np.nan,
            "has_gpa": float(gpa_match is not None),
            "resume_chars": float(len(resume)),
            "jd_chars": float(len(jd)),
        })
    features = pd.DataFrame(rows, index=frame.index)
    meta: dict[str, Any] = {"tfidf_features": len(vectorizer.vocabulary_), "skills": skills}
    if cache_dir and use_embeddings:
        try:
            from sentence_transformers import SentenceTransformer
            cache = Path(cache_dir)
            cache.mkdir(parents=True, exist_ok=True)
            key = hashlib.sha256("\n".join(frame["resume_text"] + "\n" + frame["job_description_text"]).encode()).hexdigest()[:20]
            path = cache / f"minilm_{key}.npy"
            if path.exists():
                embeddings = np.load(path)
            else:
                model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                def chunks(text: str) -> list[str]:
                    words = text.split()
                    return [" ".join(words[i:i + 256]) for i in range(0, len(words), 256)] or [""]
                all_chunks = []
                boundaries = []
                for resume, jd in zip(frame["resume_text"], frame["job_description_text"]):
                    resume_chunks, jd_chunks = chunks(resume), chunks(jd)
                    start = len(all_chunks)
                    all_chunks.extend(resume_chunks + jd_chunks)
                    boundaries.append((start, start + len(resume_chunks), start + len(resume_chunks), len(all_chunks)))
                encoded = model.encode(all_chunks, show_progress_bar=False, normalize_embeddings=True)
                embeddings = []
                for resume_start, resume_end, jd_start, jd_end in boundaries:
                    resume_vectors = encoded[resume_start:resume_end]
                    jd_vectors = encoded[jd_start:jd_end]
                    embeddings.append(np.stack([
                        resume_vectors.mean(axis=0), resume_vectors.max(axis=0),
                        jd_vectors.mean(axis=0), jd_vectors.max(axis=0),
                    ]))
                embeddings = np.asarray(embeddings)
                np.save(path, embeddings)
            if embeddings.ndim == 3 and embeddings.shape[1:] == (4, 384):
                features["minilm_mean_cosine"] = np.sum(
                    embeddings[:, 0] * embeddings[:, 2], axis=1
                )
                features["minilm_max_cosine"] = np.sum(
                    embeddings[:, 1] * embeddings[:, 3], axis=1
                )
            else:
                features["minilm_mean_cosine"] = 0.0
                features["minilm_max_cosine"] = 0.0
            meta["embedding_cache"] = str(path)
        except Exception as exc:
            warnings.warn(f"MiniLM unavailable; continuing without embeddings: {exc}")
            meta["embedding_cache"] = None
    return features.replace([np.inf, -np.inf], np.nan), {"vectorizer": vectorizer, **meta}


def grouped_split(frame: pd.DataFrame, seed: int = SEED) -> dict[str, np.ndarray]:
    """Split by connected resume/job groups, preventing either-side leakage."""
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
    components = frame.apply(lambda r: find("r:" + r.resume_id), axis=1).to_numpy()
    n_components = len(np.unique(components))
    if n_components < 3:
        raise ValueError(
            "Need at least 3 disjoint resume/job connected groups for train/validation/test; "
            f"found {n_components}. Provide resume_id/job_id columns in the dataset."
        )
    test_size: float | int = 1 if n_components < 5 else 0.2
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_pos, test_pos = next(splitter.split(frame, groups=components))
    train_components = components[train_pos]
    n_train_components = len(np.unique(train_components))
    inner_size: float | int = 1 if n_train_components < 5 else 0.2
    inner = GroupShuffleSplit(n_splits=1, test_size=inner_size, random_state=seed)
    tr_pos, val_pos = next(inner.split(frame.iloc[train_pos], groups=train_components))
    return {"train": frame.index[train_pos[tr_pos]].to_numpy(), "validation": frame.index[train_pos[val_pos]].to_numpy(), "test": frame.index[test_pos].to_numpy()}


def _metrics(frame: pd.DataFrame, scores: np.ndarray) -> dict[str, float]:
    y = frame["label_id"].to_numpy()
    binary = (y == 2).astype(int)
    predicted = (scores >= 0.5).astype(int)
    out: dict[str, float] = {
        "accuracy": float(accuracy_score(binary, predicted)),
        "f1": float(f1_score(binary, predicted, zero_division=0)),
    }
    out["roc_auc"] = float(roc_auc_score(binary, scores)) if len(np.unique(binary)) > 1 else float("nan")
    out["map"] = float(average_precision_score(binary, scores)) if len(np.unique(binary)) > 1 else float("nan")
    groups = []
    group_column = "ranking_job_id" if "ranking_job_id" in frame else "job_id"
    for _, group in frame.assign(_score=scores).groupby(group_column, sort=False):
        if len(group) > 1 and group.label_id.nunique() > 1:
            groups.append((group.label_id.to_numpy(), group._score.to_numpy()))
    out["qualifying_groups"] = len(groups)
    out["ndcg@5"] = float(np.mean([ndcg_score([a], [b], k=5) for a, b in groups])) if groups else float("nan")
    out["ndcg@10"] = float(np.mean([ndcg_score([a], [b], k=10) for a, b in groups])) if groups else float("nan")
    out["spearman"] = float(spearmanr(y, scores).statistic) if len(np.unique(y)) > 1 else float("nan")
    return out


def _bootstrap(frame: pd.DataFrame, scores: np.ndarray, n: int = 200) -> dict[str, list[float]]:
    rng = np.random.default_rng(SEED)
    jobs = np.array(frame.job_id.unique())
    samples = []
    for _ in range(n):
        chosen = rng.choice(jobs, len(jobs), replace=True)
        idx = np.concatenate([np.flatnonzero(frame.job_id.to_numpy() == job) for job in chosen])
        samples.append(_metrics(frame.iloc[idx], scores[idx])["ndcg@5"])
    samples = np.asarray(samples, dtype=float)
    return {"ndcg@5_ci95": [float(np.nanpercentile(samples, 2.5)), float(np.nanpercentile(samples, 97.5))]}


def train_real(
    data_path: str | Path | None = None,
    dataset: str = DEFAULT_DATASET,
    output_dir: str | Path | None = None,
    use_embeddings: bool = True,
    n_bootstrap: int = 200,
) -> dict[str, Any]:
    """Train v2 and return the persisted report."""
    import xgboost as xgb
    frame, source = load_real_dataset(dataset, data_path)
    splits = grouped_split(frame)
    features, feature_meta = extract_pair_features(frame, splits["train"], Path(output_dir or ROOT / "backend/models/trained/v2") / "cache", use_embeddings)
    feature_names = list(features.columns)
    X = features.fillna(features.loc[splits["train"]].median(numeric_only=True)).fillna(0)
    y = frame.label_id.to_numpy()
    train, val, test = splits["train"], splits["validation"], splits["test"]
    params = {
        "n_estimators": 400,
        "max_depth": 5,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": SEED,
        "n_jobs": 2,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "early_stopping_rounds": 30,
    }
    binary_y = (y > 1).astype(int)
    classifier = xgb.XGBClassifier(**params)
    classifier.fit(
        X.loc[train],
        binary_y[train],
        eval_set=[(X.loc[val], binary_y[val])],
        verbose=False,
    )
    pred = classifier.predict_proba(X.loc[test])
    scores = pred[:, 1]
    report: dict[str, Any] = {
        "version": "2.0", "source": source, "rows": int(len(frame)), "features": feature_names,
        "splits": {k: [int(x) for x in v] for k, v in splits.items()},
        "model": {"objective": "binary:logistic", "positive_label": "Good Fit", "hyperparameters": params},
        "test": _metrics(frame.loc[test], scores),
        "bootstrap": _bootstrap(frame.loc[test], scores, n_bootstrap),
        "ablation": {},
        "coverage": {
            name: float(features[name].notna().mean())
            for name in ("exp_years", "required_years", "num_certs", "degree_level", "gpa")
        },
    }
    # Transparent baselines are scored on exactly the same untouched test rows.
    rng = np.random.default_rng(SEED)
    report["comparisons"] = {
        "tfidf": _metrics(frame.loc[test], X.loc[test, "tfidf_similarity"].to_numpy()),
        "embedding": _metrics(frame.loc[test], X.loc[test, "minilm_mean_cosine"].to_numpy()),
        "random": _metrics(frame.loc[test], rng.random(len(test))),
    }
    try:
        from sklearn.isotonic import IsotonicRegression
        val_prob = classifier.predict_proba(X.loc[val])[:, 1]
        test_prob = pred[:, 1]
        calibrator = IsotonicRegression(out_of_bounds="clip").fit(val_prob, binary_y[val])
        calibrated = calibrator.predict(test_prob)
        out = Path(output_dir or ROOT / "backend/models/trained/v2")
        out.mkdir(parents=True, exist_ok=True)
        with (out / "isotonic_calibrator.pkl").open("wb") as handle:
            pickle.dump(calibrator, handle)
        report["calibration"] = {
            "bins": [
                {"mean_predicted": float(np.mean(calibrated[mask])), "fraction_positive": float(np.mean((y[test] > 0)[mask]))}
                for mask in [calibrated < .2, (calibrated >= .2) & (calibrated < .4), (calibrated >= .4) & (calibrated < .6), (calibrated >= .6) & (calibrated < .8), calibrated >= .8]
                if np.any(mask)
            ]
        }
    except Exception as exc:
        report["calibration"] = {"error": str(exc)}
    ladders = [
        ("original_5", [x for x in ("exp_years", "skill_match_ratio", "num_projects", "num_certs", "gpa") if x in feature_names]),
        ("plus_tfidf", [x for x in feature_names if x not in {"minilm_mean_cosine", "minilm_max_cosine", "resume_skill_count", "jd_skill_count", "missing_skill_count"}]),
        ("plus_embeddings", [x for x in feature_names if x not in {"resume_skill_count", "jd_skill_count", "missing_skill_count", "required_years", "exp_gap", "num_projects", "num_certs", "degree_level", "has_degree", "has_gpa", "resume_chars", "jd_chars"}]),
        ("plus_skill_features", [x for x in feature_names if x not in {"required_years", "exp_gap", "num_projects", "num_certs", "degree_level", "has_degree", "has_gpa", "resume_chars", "jd_chars"}]),
        ("all", feature_names),
    ]
    for name, columns in ladders:
        ab = xgb.XGBClassifier(**params).fit(
            X.loc[train, columns],
            binary_y[train],
            eval_set=[(X.loc[val, columns], binary_y[val])],
            verbose=False,
        )
        report["ablation"][name] = _metrics(
            frame.loc[test], ab.predict_proba(X.loc[test, columns])[:, 1]
        )
    try:
        v1 = xgb.XGBRanker()
        v1.load_model(ROOT / "backend" / "models" / "trained" / "baseline_v1" / "xgb_ranker.json")
        v1_features = X.loc[test, ["exp_years", "skill_match_ratio", "num_projects", "num_certs", "gpa"]]
        report["comparisons"]["v1"] = _metrics(frame.loc[test], v1.predict(v1_features))
    except Exception as exc:
        report["comparisons"]["v1"] = {"error": str(exc)}
    try:
        import shap  # type: ignore
        explanation = shap.TreeExplainer(classifier)(X.loc[test])
        values = np.asarray(explanation.values)
        if values.ndim == 3:
            values = np.abs(values).mean(axis=(0, 2))
        else:
            values = np.abs(values).mean(axis=0)
        report["shap"] = {
            "available": True,
            "mean_abs": {name: float(value) for name, value in zip(feature_names, values)},
        }
    except Exception as exc:
        report["shap"] = {"available": False, "reason": str(exc)}
    out = Path(output_dir or ROOT / "backend/models/trained/v2")
    out.mkdir(parents=True, exist_ok=True)
    classifier.save_model(out / "xgb_classifier.json")
    classifier.save_model(ROOT / "backend" / "models" / "trained" / "xgb_ranker_v2.json")
    (ROOT / "backend" / "models" / "trained" / "xgb_ranker_v2_meta.json").write_text(
        json.dumps({"version": "2.0", "model_type": "XGBClassifier", "features": feature_names}, indent=2),
        encoding="utf-8",
    )
    with (out / "feature_metadata.pkl").open("wb") as handle:
        pickle.dump(feature_meta, handle)
    (out / "model_version.json").write_text(json.dumps({
        "version": "2.0", "model_type": "XGBClassifier",
        "features": feature_names, "metrics": report["test"], "report": "report.json",
    }, indent=2), encoding="utf-8")
    split_ids = {
        name: [
            {"row_id": int(i), "resume_id": str(frame.loc[i, "resume_id"]), "job_id": str(frame.loc[i, "job_id"])}
            for i in indices
        ]
        for name, indices in splits.items()
    }
    (out / "split_ids.json").write_text(json.dumps(split_ids, indent=2), encoding="utf-8")
    (out / "report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    (ROOT / "backend" / "models" / "trained" / "model_version_v2.json").write_text(
        json.dumps({"version": "2.0", "model_type": "XGBClassifier", "metrics": report["test"]}, indent=2),
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path")
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--output-dir")
    parser.add_argument("--no-embeddings", action="store_true")
    parser.add_argument("--bootstrap", type=int, default=200)
    args = parser.parse_args()
    result = train_real(args.data_path, args.dataset, args.output_dir, not args.no_embeddings, args.bootstrap)
    print(json.dumps(result["test"], indent=2))


if __name__ == "__main__":
    main()
