"""Smoke-check the three demo scoring cases and their ordering."""
import io
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.main import app


CASES = [
    ("good", "Python FastAPI SQL Docker AWS engineer with 5 years experience",
     "Python FastAPI SQL Docker AWS engineer with 3 years experience"),
    ("mediocre", "Python developer with 1 year experience",
     "Python FastAPI SQL Docker AWS engineer with 3 years experience"),
    ("unrelated", "Graphic designer skilled in Illustrator and typography",
     "Python FastAPI SQL Docker AWS engineer with 3 years experience"),
]


def main() -> int:
    scores = {}
    with TestClient(app) as client:
        for name, resume, jd in CASES:
            response = client.post(
                "/api/analyze",
                files={"resume": ("demo.txt", io.BytesIO(resume.encode()), "text/plain")},
                data={"jd_text": jd, "role": "Demo Engineer"},
            )
            if response.status_code != 200:
                print(f"{name}: ERROR {response.status_code} {response.text}")
                return 1
            payload = response.json()
            scores[name] = payload["fit_score"]
            print(f"{name}: score={payload['fit_score']:.2f} latency_ms={payload['latency_ms']:.2f}")
    if not (scores["good"] > scores["mediocre"] > scores["unrelated"]):
        print(f"FAIL: expected good > mediocre > unrelated, got {scores}")
        return 1
    print("PASS: score ordering is good > mediocre > unrelated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
