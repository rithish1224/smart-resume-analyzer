# Frozen baseline

This is the frozen `baseline_v1` model used for evaluation. The active model
files were copied to `backend/models/trained/baseline_v1/`; evaluation code
does not retrain or overwrite the active model.

## Model

- Algorithm: XGBoost `XGBRanker`
- Objective: `rank:ndcg`
- Trees: 200
- Maximum depth: 5
- Learning rate: 0.05
- Row subsampling: 0.8
- Column subsampling: 0.8
- Random seed: 42

The five model features are:

1. `exp_years`
2. `skill_match_ratio`
3. `num_projects`
4. `num_certs`
5. `gpa`

## Data and labels

The training data contains 500 synthetic candidate profiles across 8 domains.
Labels are synthetic: a candidate is shortlisted when its heuristic score is
above the domain's 75th percentile. The heuristic is 30% skill, 30%
experience, 25% education, and 15% projects, with additive noise.

## Reported baseline metrics

These are **in-sample, synthetic labels, no holdout** metrics:

| Metric | Value |
|---|---:|
| NDCG@5 | 0.9836 |
| NDCG@10 | 0.9533 |
| P@5 | 0.9750 |
| MAP | 0.8903 |
| ROC-AUC | 0.9485 |

These measurements describe fit to the generated labels only. They are not a
claim about performance on real resumes or hiring outcomes.
