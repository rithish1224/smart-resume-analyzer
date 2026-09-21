import numpy as np
import pandas as pd

from ml_training.feature_engineering import (
    extract_degree_level,
    extract_experience_years,
    extract_required_years,
)
from ml_training.train_real import grouped_split


def test_experience_and_required_year_parsing():
    assert extract_experience_years("Experience: 2018-2020; 2021 to present") >= 6
    assert extract_required_years("Requires 5+ years of experience") == 5
    assert np.isnan(extract_experience_years("No experience listed"))


def test_degree_level_missing_is_nan():
    assert extract_degree_level("Master of Science") == 3
    assert np.isnan(extract_degree_level("No education listed"))


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
