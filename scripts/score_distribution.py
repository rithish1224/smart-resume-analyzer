"""Report calibrated validation-score distribution without retraining."""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml_training.train_real import DEFAULT_DATASET, extract_pair_features, load_real_dataset


def _percentile_rows(scores: np.ndarray) -> list[tuple[str, float]]:
    return [
        ("min", float(np.min(scores))),
        ("median", float(np.percentile(scores, 50))),
        ("90th percentile", float(np.percentile(scores, 90))),
        ("95th percentile", float(np.percentile(scores, 95))),
        ("99th percentile", float(np.percentile(scores, 99))),
        ("max", float(np.max(scores))),
    ]


def _calibration_rows(
    scores: np.ndarray,
    labels: np.ndarray,
    bootstrap_count: int = 2000,
) -> list[dict[str, float | int | str]]:
    rng = np.random.default_rng(42)
    rows = []
    for lower in range(0, 100, 10):
        upper = lower + 10
        mask = (scores >= lower) & ((scores < upper) if upper < 100 else (scores <= upper))
        bin_scores = scores[mask]
        bin_labels = labels[mask]
        if len(bin_scores):
            boot_indices = rng.integers(0, len(bin_scores), size=(bootstrap_count, len(bin_scores)))
            predicted_boot = bin_scores[boot_indices].mean(axis=1)
            actual_boot = bin_labels[boot_indices].mean(axis=1)
            predicted_ci = np.percentile(predicted_boot, [2.5, 97.5])
            actual_ci = np.percentile(actual_boot, [2.5, 97.5])
        else:
            predicted_ci = actual_ci = (np.nan, np.nan)
        rows.append({
            "bin": f"{lower}-{upper}%",
            "mean_predicted": float(np.mean(bin_scores)) if len(bin_scores) else float("nan"),
            "predicted_ci_low": float(predicted_ci[0]),
            "predicted_ci_high": float(predicted_ci[1]),
            "actual_good_fit_rate": float(np.mean(bin_labels)) if len(bin_labels) else float("nan"),
            "actual_ci_low": float(actual_ci[0]),
            "actual_ci_high": float(actual_ci[1]),
            "count": int(len(bin_scores)),
            "reliable": len(bin_scores) >= 30,
        })
    return rows


def _validation_scores(
    frame: pd.DataFrame,
    split_ids: dict,
    model,
    vectorizer,
    model_dir: Path,
    use_embedding_cache: bool,
) -> tuple[np.ndarray, np.ndarray]:
    train_ids = [item["row_id"] for item in split_ids["train"]]
    validation_ids = sorted(item["row_id"] for item in split_ids["validation"])
    features, _ = extract_pair_features(
        frame,
        train_indices=train_ids,
        cache_dir=model_dir / "cache",
        use_embeddings=True,
        vectorizer=vectorizer,
    )
    model_features = features.fillna(features.loc[train_ids].median(numeric_only=True)).fillna(0)
    with (model_dir / "isotonic_calibrator.pkl").open("rb") as handle:
        calibrator = pickle.load(handle)
    raw = model.predict_proba(model_features.loc[validation_ids])[:, 1]
    scores = np.asarray(calibrator.predict(raw), dtype=float) * 100
    labels = (frame.loc[validation_ids, "label_id"].to_numpy() == 2).astype(float)
    return scores, labels


def _distribution_table(scores: np.ndarray) -> str:
    rows = _percentile_rows(scores)
    lines = ["| Statistic | Calibrated score |", "|---|---:|"]
    lines.extend(f"| {name} | {value:.6f} |" for name, value in rows)
    lines.extend(["", "| Threshold | Count |", "|---:|---:|"])
    lines.extend(f"| > {threshold} | {int(np.sum(scores > threshold))} |" for threshold in (60, 70, 80, 90))
    return "\n".join(lines)


def _calibration_table(scores: np.ndarray, labels: np.ndarray) -> str:
    lines = [
        "| Score bin | Mean predicted (95% CI) | Actual Good Fit rate (95% CI) | Samples | Reliability |",
        "|---|---:|---:|---:|---|",
    ]
    for row in _calibration_rows(scores, labels):
        if np.isnan(row["mean_predicted"]):
            predicted = actual = "—"
        else:
            predicted = f"{row['mean_predicted']:.6f} ({row['predicted_ci_low']:.6f}, {row['predicted_ci_high']:.6f})"
            actual = f"{row['actual_good_fit_rate']:.6f} ({row['actual_ci_low']:.6f}, {row['actual_ci_high']:.6f})"
        reliability = "reliable" if row["reliable"] else "unreliable (<30)"
        lines.append(f"| {row['bin']} | {predicted} | {actual} | {row['count']} | {reliability} |")
    return "\n".join(lines)


def build_report(data_path: str | None = None, dataset: str = DEFAULT_DATASET) -> str:
    import xgboost as xgb

    model_dir = ROOT / "backend" / "models" / "trained" / "v2"
    model = xgb.XGBClassifier()
    model.load_model(str(ROOT / "backend" / "models" / "trained" / "xgb_ranker_v2.json"))
    with (model_dir / "isotonic_calibrator.pkl").open("rb") as handle:
        calibrator = pickle.load(handle)
    with (model_dir / "feature_metadata.pkl").open("rb") as handle:
        metadata = pickle.load(handle)
    split_ids = json.loads((model_dir / "split_ids.json").read_text(encoding="utf-8"))

    frame, source = load_real_dataset(dataset=dataset, data_path=data_path)
    cached_scores, cached_labels = _validation_scores(
        frame, split_ids, model, metadata.get("vectorizer"), model_dir, True
    )
    live_scores, live_labels = _validation_scores(
        frame, split_ids, model, metadata.get("vectorizer"), model_dir, False
    )

    lines = [
        "# Calibrated Validation Score Distribution",
        "",
        "This report was generated without retraining, changing the model, or",
        "changing frontend match-band thresholds.",
        "",
        f"- Dataset: `{source['source']}`",
        f"- Validation rows: **{len(cached_scores)}**",
        "- Score unit: calibrated model-estimated Good Fit probability, displayed as 0-100",
        "",
        "## Feature provenance",
        "",
        "The previous script did not load a cached training-time feature matrix.",
        "It recomputed features with the current `extract_pair_features` extractor,",
        "using the saved TF-IDF vectorizer and allowing the MiniLM embedding cache.",
        "The second pass reruns the same current extractor after the embedding",
        "cache is populated. A complete cached training-time feature matrix was",
        "not saved by the training run, so there is no separate historical",
        "feature-vector version to load. Both passes use the same saved",
        "model, calibrator, split, and training-partition median imputation.",
    ]
    for title, scores in (
        ("Cache-allowed current extractor", cached_scores),
        ("Current extractor, cache-reused pass", live_scores),
    ):
        lines.extend([
            f"## {title}",
            "",
            _distribution_table(scores),
            "",
        ])
    lines.extend([
        "## Side-by-side calibration tables",
        "",
        "Bootstrap intervals use 2,000 row-resamples within each bin and the",
        "2.5th/97.5th percentiles. Bins with fewer than 30 rows are marked",
        "unreliable.",
        "",
        "### Cache-allowed current extractor",
        "",
        _calibration_table(cached_scores, cached_labels),
        "",
        "### Current extractor, cache-reused pass",
        "",
        _calibration_table(live_scores, live_labels),
        "",
        "The two paths should match numerically when the embedding cache is valid.",
        "",
        "These are validation-set calibration diagnostics, not hiring accuracy.",
        "They describe how the saved calibrator behaves on the validation split.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path")
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    args = parser.parse_args()
    report = build_report(args.data_path, args.dataset)
    output = ROOT / "docs" / "score_distribution.md"
    output.write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
