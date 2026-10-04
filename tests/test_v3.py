import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ml_training.train_v3 import (
    FEATURES,
    degree_level,
    grouped_split,
    project_count,
    scale_within_groups,
    normalized_skills,
)


def test_v3_skill_aliases_and_hedging():
    skills = normalized_skills("Some exposure to Python scripting and MySQL, NodeJS, Postgres, Spring Boot, scikit-learn")
    assert {"python", "mysql", "node.js", "postgresql", "spring boot", "scikit-learn"} <= skills


def test_v3_degree_aliases():
    assert degree_level("B.Tech B.E. B.Sc.") == 2
    assert degree_level("M.Tech M.Sc. MBA") == 3
    assert degree_level("B.Com") == 1


def test_v3_project_counts():
    assert project_count("Led 3 projects and Built 6 web apps") == 9


def test_v3_split_has_no_resume_overlap():
    frame = pd.DataFrame({
        "resume_id": ["r1", "r1", "r2", "r3", "r4", "r5"],
        "job_id": ["j1", "j2", "j2", "j3", "j4", "j5"],
    })
    splits = grouped_split(frame)
    where = {i: name for name, values in splits.items() for i in values}
    for _, rows in frame.groupby("resume_id").groups.items():
        assert len({where[int(i)] for i in rows}) == 1


def test_v3_resume_split_keeps_all_resume_rows():
    frame = pd.DataFrame({
        "resume_id": ["shared", "shared", "train-only", "val-only", "test-only", "test-only"],
        "job_id": ["j1", "j2", "j3", "j4", "j5", "j5"],
    })
    splits = grouped_split(frame)
    memberships = {}
    for name, indices in splits.items():
        for value in frame.loc[indices, "resume_id"]:
            memberships.setdefault(value, set()).add(name)
    assert all(len(names) <= 1 for names in memberships.values())


def test_minmax_edge_cases():
    assert np.all(scale_within_groups(np.array([4.0]), pd.Series(["a"])) == 50)
    assert np.all(scale_within_groups(np.array([2.0, 2.0]), pd.Series(["a", "a"])) == 50)


def test_v2_hashes_unchanged_after_v3_run():
    for name in ("xgb_classifier.json", "model_version.json"):
        path = Path(__file__).parents[1] / "backend" / "models" / "trained" / "v2" / name
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest()
