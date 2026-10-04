# Honest evaluation

All measured values below are from this evaluation run. Synthetic in-sample values are the frozen report and are explicitly **in-sample, synthetic labels, no holdout**.

| Evaluation | NDCG@5 | NDCG@10 | P@5 | MAP | ROC-AUC | Spearman |
|---|---:|---:|---:|---:|---:|---:|
| synthetic in-sample | 0.9836 | 0.9533 | 0.9750 | 0.8903 | 0.9485 | n/a |
| synthetic holdout | 0.9138 | 0.9648 | 0.4500 | 0.8370 | 0.9234 | n/a |
| real data | 0.5218 | 0.5816 | 0.4427 | 0.4927 | 0.4910 | -0.0179 |
| TF-IDF | 0.7086 | 0.7268 | 0.5464 | 0.6029 | 0.6463 | 0.2654 |
| random | 0.5176 | 0.5685 | 0.4287 | 0.4840 | 0.4871 | -0.0246 |

Real-data qualifying JD groups: 243.

## Limitations and assumptions

- The synthetic holdout is an 80/20 random split within each domain with seed 42; no tuning was performed.
- Real text feature extraction is heuristic. Missing experience, projects, certifications, or GPA remain NaN and are passed to XGBoost.
- Real NDCG and P@5 use only job-description groups with at least two resumes and differing labels; the qualifying count is printed by the evaluator.
- Real ROC-AUC treats `Good Fit` as positive and both other labels as negative. Spearman uses the ordinal labels 0, 1, and 2.
- The dataset's license metadata is printed at runtime and is not assumed when it is blank.
