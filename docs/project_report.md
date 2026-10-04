# Smart Competency Diagnostic: Beginner-Friendly Project Report

## 1. What this project does

Smart Competency Diagnostic is a resume-to-job-description matching application.
It accepts:

- a resume file (PDF, DOCX, or TXT), and
- a job description.

The backend extracts information from both texts, sends the resulting feature
vector to a machine-learning model, and returns:

- a calibrated fit score from 0 to 100,
- matched, missing, and related skills,
- competency-style scores,
- SHAP explanations showing which model features pushed the result up or down,
- improvement suggestions,
- model version and request latency.

The frontend displays these results for recruiter or candidate decision support.
The result is not an automatic hiring decision. Human review is required.

## 2. High-level flow

The live request path is:

1. The user uploads a resume and enters a job description.
2. FastAPI receives the request at `POST /api/analyze`.
3. The resume parser converts the file into text.
4. Shared feature-engineering code extracts resume/JD features.
5. The saved v2 XGBoost classifier predicts the probability of the `Good Fit`
   class.
6. An isotonic calibration model converts that raw probability into a better
   calibrated value based on the validation set.
7. The calibrated value is multiplied by 100 and returned as `fit_score`.
8. SHAP calculates feature contributions for explanation.
9. The React frontend renders the score, skill lists, explanations, and
   suggestions.

The main online implementation is
[`backend/routers/analyze.py`](../backend/routers/analyze.py). The shared
training and inference feature code is
[`ml_training/train_real.py`](../ml_training/train_real.py).

## 3. Algorithms used

### 3.1 XGBoost v1 baseline

The original baseline uses an XGBoost `XGBRanker` with the
`rank:ndcg` objective. Ranking is useful when the goal is to order candidates
for a job rather than only predict a yes/no label.

The frozen v1 configuration is:

- 200 trees
- maximum depth 5
- learning rate 0.05
- row subsampling 0.8
- column subsampling 0.8
- random seed 42

The v1 model uses five features and synthetic labels. It is retained as a
historical baseline and is not the active model used by `/api/analyze`.
Details are in [`docs/baseline.md`](./baseline.md).

### 3.2 XGBoost v2 production/demo model

The active model is an XGBoost `XGBClassifier` using the binary logistic
objective. Its positive class is:

```text
Good Fit
```

The negative class combines:

```text
No Fit + Potential Fit
```

This model was selected because it works well with mixed tabular features,
handles nonlinear relationships, is fast enough for CPU inference, and
supports feature-level explanations through TreeSHAP.

The saved model is
[`backend/models/trained/xgb_ranker_v2.json`](../backend/models/trained/xgb_ranker_v2.json).
Despite the historical filename containing `ranker`, the v2 model is an
XGBoost classifier.

### 3.3 TF-IDF similarity

TF-IDF converts words into numeric weights. Words that are frequent in one
text but less common across documents receive useful weight. Cosine similarity
then measures how similar the resume wording is to the job-description
wording.

This is a strong simple baseline because resumes and job descriptions often
share important terms such as technologies, tools, and role names.

### 3.4 MiniLM embedding similarity

The system also uses
`sentence-transformers/all-MiniLM-L6-v2`. It converts text chunks into
semantic vectors. This can identify related wording even when the exact words
are different.

Long texts are split into chunks. The system computes mean and maximum
similarity features from the chunk embeddings. The embedding model is loaded
once at application startup rather than once per request.

### 3.5 Isotonic calibration

The classifier's raw probability is not automatically a trustworthy
percentage. Isotonic regression is fitted on validation predictions to map
raw probabilities to values that better reflect the observed validation
outcomes.

The calibrator is stored at
[`backend/models/trained/v2/isotonic_calibrator.pkl`](../backend/models/trained/v2/isotonic_calibrator.pkl).

### 3.6 TreeSHAP explanations

TreeSHAP explains how individual features contributed to an XGBoost prediction.
Positive values push the prediction toward `Good Fit`; negative values push it
away from `Good Fit`.

The frontend labels these values as impact on score in log-odds. They are not
percentages.

## 4. Datasets

### 4.1 Synthetic v1 dataset

The v1 baseline uses locally generated data:

- [`ml_training/training_features.csv`](../ml_training/training_features.csv)
- [`ml_training/synthetic_candidates.json`](../ml_training/synthetic_candidates.json)
- [`ml_training/generate_synthetic_data.py`](../ml_training/generate_synthetic_data.py)

It contains approximately 500 synthetic candidate profiles across eight
domains. Its five features are:

1. `exp_years`
2. `skill_match_ratio`
3. `num_projects`
4. `num_certs`
5. `gpa`

Synthetic labels are generated from a heuristic:

- 30% skill
- 30% experience
- 25% education
- 15% projects
- additional noise

A candidate is labeled based on the domain-specific 75th percentile of that
heuristic score. These labels are useful for a reproducible baseline, but they
are not real hiring outcomes.

### 4.2 Real v2 dataset

The active v2 model was trained on the Hugging Face dataset:

```text
cnamuangtoun/resume-job-description-fit
```

The training run used:

- 6,241 resume/job-description pairs
- labels `No Fit`, `Potential Fit`, and `Good Fit`
- binary training target: `Good Fit` versus the other two labels
- grouped train/validation/test splitting
- fixed hyperparameters
- early stopping using validation log-loss
- isotonic calibration using validation predictions

The training script is
[`ml_training/train_real.py`](../ml_training/train_real.py). The dataset is
downloaded through the Hugging Face `datasets` library rather than committed
as a complete copy in this repository.

The public labels are proxy judgments and may contain noise. They should not be
interpreted as verified employment success.

### 4.3 Demo samples

The files in [`scripts/demo_samples/`](../scripts/demo_samples/) are only
manual demo inputs:

- `jd.txt`
- `good_resume.txt`
- `mediocre_resume.txt`
- `unrelated_resume.txt`

They were not used to train the v2 model.

## 5. Features used by the active v2 model

The exact model feature order is recorded in
[`backend/models/trained/v2/model_version.json`](../backend/models/trained/v2/model_version.json).

### Text similarity

| Feature | Meaning |
|---|---|
| `tfidf_similarity` | Word-level cosine similarity between resume and JD |
| `minilm_mean_cosine` | Mean-pooled semantic embedding similarity |
| `minilm_max_cosine` | Maximum chunk-level semantic similarity |

### Skills

| Feature | Meaning |
|---|---|
| `skill_match_ratio` | Matched active JD skills divided by detected JD skills |
| `resume_skill_count` | Number of normalized active skills in the resume |
| `jd_skill_count` | Number of normalized skills detected in the JD |
| `missing_skill_count` | JD skills not found as active resume skills |

The extractor normalizes terms such as `Postgres` to `postgresql` and
recognizes terms including Git, REST, APIs, Terraform, CI/CD, GitHub Actions,
Redis, Flask, and PostgreSQL. Phrases such as `learning Docker`, `familiar
with Redis`, and `exposure to Kubernetes` are treated as related/learning
skills rather than confirmed active skills.

### Experience

| Feature | Meaning |
|---|---|
| `exp_years` | Experience extracted from the resume |
| `required_years` | Required experience extracted from the JD |
| `exp_gap` | Candidate experience minus required experience |

The parser recognizes decimal and hedged forms such as `1.5 years`, `about
1.5 years`, and `5 years`, as well as several date-range formats.

### Resume evidence

| Feature | Meaning |
|---|---|
| `num_projects` | Extracted project evidence/count |
| `num_certs` | Extracted certification evidence/count |

### Education

| Feature | Meaning |
|---|---|
| `degree_level` | Approximate education level |
| `has_degree` | Whether a degree was detected |
| `gpa` | Extracted GPA/CGPA when present |
| `has_gpa` | Whether a GPA was detected |

### Length

| Feature | Meaning |
|---|---|
| `resume_chars` | Resume character count |
| `jd_chars` | Job-description character count |

The length and JD-only features are used internally by the model but are
excluded from candidate-facing SHAP display and competency group totals because
they are not direct candidate competencies.

## 6. How score calculation works

For one resume/JD pair, the model receives a row containing the 18 features
above.

Conceptually:

```text
features
    -> XGBoost classifier
    -> raw probability of Good Fit
    -> isotonic calibration
    -> calibrated value from 0 to 1
    -> multiply by 100
    -> fit_score from 0 to 100
```

In the current online path, missing feature values are filled with `0.0`
before prediction. This is important because a missing GPA, certification, or
experience value is not always equivalent to a real numeric zero.

The training report states that training-partition medians were used for
missing values during training. Therefore, online zero-imputation is a known
consistency limitation and can affect scores for resumes with incomplete
extractable information. It should be corrected before treating the score as
highly calibrated.

## 7. What can increase or decrease a score?

A score can increase when the pair has:

- high word-level similarity,
- high semantic similarity,
- a high ratio of matched JD skills,
- few missing skills,
- experience meeting or exceeding the requirement,
- detected projects and certifications,
- matching education evidence,
- feature combinations that resemble `Good Fit` examples in training.

A score can decrease when the pair has:

- low text similarity,
- many missing skills,
- experience below the JD requirement,
- little extracted resume evidence,
- education or GPA patterns associated with lower validation predictions,
- feature combinations unlike the training data.

The exact effect is learned by the XGBoost trees. It is not a manually written
formula such as “skills are worth 40% and experience is worth 30%.”

## 8. Accuracy and measured performance

There is no single perfect “accuracy” number for this project. Different
metrics answer different questions, and the dataset labels are proxy labels.

### v2 held-out test results

These are measured on the untouched v2 test set:

| Metric | v2 all features |
|---|---:|
| Accuracy | 0.811048839071257 |
| ROC-AUC | 0.8572466263478467 |
| F1 | 0.5042016806722689 |
| Spearman correlation | 0.4367805043878437 |
| NDCG@5 | 0.7716852429281827 |
| NDCG@10 | 0.8272984417283406 |

In percentage-style wording, the measured classification accuracy is about
**81.10%**, but accuracy alone is not sufficient here because the positive
`Good Fit` class is not balanced and the application is intended to rank and
support review.

ROC-AUC of about **0.857** means the model generally ranks a randomly selected
`Good Fit` pair above a randomly selected non-`Good Fit` pair. It does not mean
that 85.7% of hiring decisions will be correct.

Spearman correlation of about **0.437** measures moderate agreement between
model ordering and the ordered labels. F1 of about **0.504** shows that the
positive-class decision quality is substantially weaker than the overall
accuracy number suggests.

### Baseline comparison on the same test rows

| Method | ROC-AUC | Spearman | F1 |
|---|---:|---:|---:|
| v2 all features | 0.8572466263478467 | 0.4367805043878437 | 0.5042016806722689 |
| TF-IDF cosine | 0.6581778332580046 | 0.31143806653445943 | 0.0000000000000000 |
| MiniLM cosine | 0.6354446907575204 | 0.2748599877583103 | 0.0911854103343465 |
| v1 baseline | 0.5385288652619648 | 0.0833890819801777 | 0.17733990147783252 |
| Random | 0.5004125146173658 | -0.010843938246297107 | 0.30803080308030806 |

The v2 model outperformed the simple TF-IDF and MiniLM baselines on ROC-AUC
and Spearman in this run. These results are benchmark results on the public
dataset, not proof of real-world hiring accuracy.

### v1 baseline results

The v1 values are in-sample results on synthetic labels with no holdout:

| Metric | v1 value |
|---|---:|
| NDCG@5 | 0.9836 |
| NDCG@10 | 0.9533 |
| P@5 | 0.9750 |
| MAP | 0.8903 |
| ROC-AUC | 0.9485 |

These high values should not be compared directly with v2 as evidence that v1
is better. V1 was measured on the same synthetic process used to create its
labels, while v2 was evaluated on held-out real-data rows.

## 9. Why a strong-looking demo resume can show 35.63

The displayed score is a calibrated model output, not a human rating. In the
current demo:

```text
Good resume:       35.63
Mediocre resume:   35.63
Unrelated resume:   0.00
```

The good and mediocre resumes had different raw model probabilities, but the
isotonic calibrator mapped them to approximately the same calibrated value.
This shows that the current demo pipeline can separate an unrelated resume but
does not reliably separate two plausible matches.

The score can also be affected by:

1. differences between the demo text and the v2 training distribution,
2. incomplete information extraction,
3. the public dataset's noisy labels,
4. calibration compression,
5. online zero-imputation versus training median-imputation.

The score should therefore be used to support ranking and review, not as an
absolute hiring percentage.

## 10. Frontend match bands

The frontend does not convert the score into a hiring decision. It assigns a
display band using validation-derived thresholds stored in
[`frontend/src/config/bands.json`](../frontend/src/config/bands.json):

```text
Strong:   score >= 41.379312
Possible: score >= 10.0
Weak:     score < 10.0
```

The thresholds were generated from validation-score percentiles, not adjusted
using the demo samples. The page displays decision-support language and states
that human review is required.

## 11. What is real and what is still demo data?

### Real model-backed path

- `/api/analyze`
- v2 XGBoost prediction
- TF-IDF and MiniLM feature extraction
- normalized skill extraction
- SHAP values
- matched/missing/related skills
- API-generated improvement suggestions
- model version and latency

### Still marked as demo/static

Some separate frontend areas, including Admin, Compare, and the improvement
hook/module, still contain mock or static data. They are visibly marked:

```text
DEMO DATA - not from the model
```

They should not be interpreted as outputs from the trained model.

## 12. Main limitations and recommended next steps

The most important limitations are:

1. The v2 labels are public proxy labels, not verified hiring outcomes.
2. The dataset does not provide a guaranteed real-world license signal in the
   current metadata.
3. Feature extraction coverage is incomplete for some fields:
   `exp_years` about 44.48%, `required_years` about 20.99%, `num_certs`
   about 63.98%, `degree_level` about 98.14%, and `gpa` about 18.96%.
4. Online missing-value handling does not currently match the training
   median-imputation process.
5. The demo good and mediocre candidates currently tie after calibration.
6. Fairness auditing has not yet been computed for the active model.
7. Synthetic data is appropriate only for the frozen v1 baseline, not for
   claiming production accuracy.

Recommended next steps:

1. Make online imputation use the saved training medians.
2. Add a regression test proving online and offline features match, including
   missing values.
3. Collect organization-specific, consented, and legally reviewable labeled
   outcomes.
4. Re-evaluate calibration and ranking on a future held-out dataset.
5. Run and document a real fairness audit before making high-impact decisions.
6. Keep human review in the workflow and avoid automatic rejection.

## 13. Short conclusion

The project is a resume/JD matching and explanation system. Its active v2
model uses XGBoost over text similarity, semantic embeddings, skills,
experience, education, resume evidence, and text-length features. On the
held-out public test set it achieved approximately 81.10% accuracy and
0.857 ROC-AUC, with moderate ranking correlation.

Those numbers indicate useful benchmark performance, not guaranteed hiring
accuracy. The current 35.63 demo score is a calibrated model output and should
not be read as “the candidate is only 35% qualified.” The most important
technical improvement is to make online missing-value handling identical to
training before further interpreting or recalibrating scores.
