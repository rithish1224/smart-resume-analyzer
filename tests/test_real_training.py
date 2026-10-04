import numpy as np
import pandas as pd

from ml_training.feature_engineering import (
    extract_degree_level,
    extract_experience_years,
    extract_required_years,
)
from ml_training.train_real import extract_normalized_skills
from ml_training.train_real import grouped_split


def test_experience_and_required_year_parsing():
    assert extract_experience_years("Experience: 2018-2020; 2021 to present") >= 6
    assert extract_required_years("Requires 5+ years of experience") == 5
    assert np.isnan(extract_experience_years("No experience listed"))


def test_degree_level_missing_is_nan():
    assert extract_degree_level("Master of Science") == 3
    assert np.isnan(extract_degree_level("No education listed"))


def test_sample_skill_normalization_and_learning_context():
    sample_dir = __import__("pathlib").Path(__file__).resolve().parents[1] / "scripts" / "demo_samples"
    resume = (sample_dir / "good_resume.txt").read_text(encoding="utf-8")
    jd = (sample_dir / "jd.txt").read_text(encoding="utf-8")
    resume_skills, resume_related = extract_normalized_skills(resume)
    jd_skills, _ = extract_normalized_skills(jd)
    assert {"git", "rest", "api", "terraform", "ci/cd", "github actions",
            "postgresql", "redis", "flask"} <= resume_skills
    assert {"flask", "postgresql", "ci/cd", "redis"} <= jd_skills
    learning_skills, learning_related = extract_normalized_skills("Currently learning Docker")
    assert "docker" in learning_related
    assert "docker" not in learning_skills


def test_decimal_and_hedged_experience_years():
    assert extract_experience_years("about 1.5 years of experience") == 1.5
    assert extract_experience_years("5 years of experience") == 5
    assert extract_required_years("3+ years of professional experience") == 3


def test_explicit_experience_total_takes_precedence_over_date_ranges():
    assert extract_experience_years(
        "about 1.5 years of experience; Jan 2025 - Present; Jun 2024 - Dec 2024"
    ) == 1.5
    assert extract_experience_years(
        "5 years of experience; Jan 2022 - Present; Jul 2019 - Dec 2021"
    ) == 5
    assert extract_experience_years(
        "6 years of experience; Mar 2021 - Present; Jun 2019 - Feb 2021"
    ) == 6


def test_demo_resume_experience_values():
    from pathlib import Path

    sample_dir = Path(__file__).resolve().parents[1] / "scripts" / "demo_samples"
    expected = {"good": 5.0, "mediocre": 1.5, "unrelated": 6.0}
    for name, years in expected.items():
        text = (sample_dir / f"{name}_resume.txt").read_text(encoding="utf-8")
        assert extract_experience_years(text) == years


def test_group_split_has_no_resume_or_job_overlap():
    frame = pd.DataFrame(
        {
            "resume_id": ["r1", "r1", "r2", "r3", "r4", "r5"],
            "job_id": ["j1", "j2", "j2", "j3", "j4", "j5"],
        }
    )
    splits = grouped_split(frame, seed=42)
    assignments = {
        index: split for split, indices in splits.items() for index in indices
    }
    assert set(assignments) == set(frame.index)
    for column in ("resume_id", "job_id"):
        for _, group in frame.groupby(column):
            assert len({assignments[index] for index in group.index}) == 1
