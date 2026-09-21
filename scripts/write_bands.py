"""Generate frontend match-band thresholds from the v2 validation scores."""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "frontend" / "src" / "config" / "bands.json"
sys.path.insert(0, str(ROOT))


def main() -> None:
    from ml_training.train_real import extract_pair_features, load_real_dataset
    import xgboost as xgb

    artifact_dir = ROOT / "backend" / "models" / "trained" / "v2"
    metadata = json.loads((artifact_dir / "model_version.json").read_text(encoding="utf-8"))
    report = json.loads((artifact_dir / "report.json").read_text(encoding="utf-8"))
    frame, _ = load_real_dataset()
    splits = report["splits"]
    train = np.asarray(splits["train"], dtype=int)
    validation = np.asarray(splits["validation"], dtype=int)
    features, _ = extract_pair_features(
        frame,
        train_indices=train,
        cache_dir=artifact_dir / "cache",
        use_embeddings=True,
    )
    X = features.fillna(features.loc[train].median(numeric_only=True)).fillna(0)
    model = xgb.XGBClassifier()
    model.load_model(str(ROOT / "backend" / "models" / "trained" / "xgb_ranker_v2.json"))
    raw = model.predict_proba(X.loc[validation])[:, 1]
    calibrator_path = artifact_dir / "isotonic_calibrator.pkl"
    if calibrator_path.exists():
        with calibrator_path.open("rb") as handle:
            raw = pickle.load(handle).predict(raw)
    scores = np.asarray(raw, dtype=float) * 100
    thresholds = {
        "strong": round(float(np.percentile(scores, 75)), 6),
        "possible": round(float(np.percentile(scores, 50)), 6),
    }
    OUTPUT.write_text(json.dumps({
        "thresholds": thresholds,
        "source": "v2 validation split calibrated scores",
        "validation_rows": int(len(scores)),
        "definition": "Strong is the top 25%; Possible is the next 25%; remaining scores are Weak.",
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(thresholds, indent=2))


if __name__ == "__main__":
    main()
