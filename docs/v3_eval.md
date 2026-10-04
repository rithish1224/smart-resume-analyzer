# V3 evaluation

Rows: 6180; splits: {'train': 3719, 'validation': 921, 'test': 1540}; flagged training conflicts: 0.

| Method | NDCG@3 | NDCG@5 | NDCG@10 | MAP | Good>Potential | Potential>No Fit | Good>No Fit |
|---|---:|---:|---:|---:|---:|---:|---:|
| v3 | 0.7197 | 0.7432 | 0.8055 | 0.7637 | 0.5636 | 0.6572 | 0.6742 |
| pairwise | 0.6969 | 0.7298 | 0.7962 | 0.7506 | 0.5969 | 0.6246 | 0.6776 |
| random | 0.5844 | 0.6452 | 0.7326 | 0.6616 | 0.4298 | 0.4735 | 0.5202 |
| tfidf | 0.6930 | 0.7221 | 0.7989 | 0.7502 | 0.5046 | 0.6471 | 0.6528 |
| minilm | 0.6709 | 0.7143 | 0.7779 | 0.7319 | 0.5341 | 0.6366 | 0.6431 |
| retrained v2 baseline | 0.7289 | 0.7486 | 0.8153 | 0.7673 | 0.5243 | 0.6516 | 0.6653 |
| saved v2 (has seen some of these resumes, likely inflated) | 0.7622 | 0.7960 | 0.8481 | 0.7971 | 0.7194 | 0.6283 | 0.8294 |

NDCG uses gain `2^relevance - 1`; intervals are 500 group bootstrap resamples.
Scores are relative 0-100 values within each job, not probabilities.
The dataset resumes and jobs form one connected component, so a split keeping both axes separate was impossible; splitting by resume is the appropriate axis for candidate ranking, and job overlap is allowed.
Only 642 unique resumes exist, so the effective sample size is small and results are uncertain.
The saved v2 comparison is labelled as potentially inflated because v2 saw some of these resumes; the retrained v2 baseline is the fairer comparison.
The dataset has no declared license; labels are proxy judgments. The model assists human reviewers only and must not make automatic rejects. Fairness check TODO.
