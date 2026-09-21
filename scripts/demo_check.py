"""Smoke-check the demo scoring cases, ordering and score gaps."""
import io
import hashlib
import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.main import app

SAMPLES = Path(__file__).parent / "demo_samples"
JD = (SAMPLES / "jd.txt").read_text(encoding="utf-8")
CASES = [
    ("good", "good_resume.txt"),
    ("mediocre", "mediocre_resume.txt"),
    ("unrelated", "unrelated_resume.txt"),
]
MIN_GAP = 10.0  # score points between good and unrelated


def analyze(client, filename, text):
    return client.post(
        "/api/analyze",
        files={"resume": (filename, io.BytesIO(text.encode()), "text/plain")},
        data={"jd_text": JD, "role": "Demo"},
    )


def main() -> int:
    scores = {}
    response_dir = Path(__file__).parent / "demo_responses"
    response_dir.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with TestClient(app) as client:
        # Warm-up request so startup cost doesn't skew latency
        analyze(client, "warmup.txt", (SAMPLES / CASES[0][1]).read_text(encoding="utf-8"))
        for name, fname in CASES:
            text = (SAMPLES / fname).read_text(encoding="utf-8")
            r = analyze(client, fname, text)
            if r.status_code != 200:
                print(f"{name}: ERROR {r.status_code} {r.text}")
                return 1
            p = r.json()
            response_path = response_dir / f"{name}.json"
            response_path.write_text(json.dumps(p, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            manifest[name] = hashlib.sha256(response_path.read_bytes()).hexdigest()
            scores[name] = p["fit_score"]
            print(f"{name}: score={p['fit_score']:.2f} "
                  f"latency_ms={p['latency_ms']:.0f}")
            print(f"   matched: {p.get('matched_skills')}")
            print(f"   missing: {p.get('missing_skills')}")
    ok_order = scores["good"] > scores["mediocre"] > scores["unrelated"]
    ok_gap = scores["good"] - scores["unrelated"] >= MIN_GAP
    if not (ok_order and ok_gap):
        (response_dir / "manifest.json").write_text(
            json.dumps({"generated_by": "scripts/demo_check.py", "sha256": manifest}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"FAIL: order ok={ok_order}, gap ok={ok_gap}, scores={scores}")
        return 1
    (response_dir / "manifest.json").write_text(
        json.dumps({"generated_by": "scripts/demo_check.py", "sha256": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
