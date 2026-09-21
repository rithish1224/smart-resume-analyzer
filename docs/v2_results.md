# Real-data v2 results

The v2 model was trained on the Hugging Face dataset
`cnamuangtoun/resume-job-description-fit`.

- Rows used: **6,241**
- CPU subset: **none**; the full dataset was used
- Positive class: `Good Fit` versus `No Fit` and `Potential Fit`
- Split: train/validation/test with disjoint synthetic resume/job IDs
- Ranking groups: repeated job-description text groups on the untouched test set
- Tuning: fixed hyperparameters only; no Optuna
- Early stopping: validation log-loss, patience 30
- Calibration: isotonic regression fit on validation predictions only

## Test metrics

| Method | ROC-AUC | Spearman | F1 | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|---:|
| v2 all features | 0.8572466263478467 | 0.4367805043878437 | 0.5042016806722689 | 0.7716852429281827 | 0.8272984417283406 |
| TF-IDF cosine | 0.6581778332580046 | 0.31143806653445943 | 0.0000000000000000 | 0.765202077278734 | 0.826007973154139 |
| MiniLM embedding cosine | 0.6354446907575204 | 0.2748599877583103 | 0.0911854103343465 | 0.7472360712032962 | 0.8088817740798101 |
| v1 baseline | 0.5385288652619648 | 0.0833890819801777 | 0.17733990147783252 | 0.7027543262623278 | 0.7782574319791232 |
| Random | 0.5004125146173658 | -0.010843938246297107 | 0.30803080308030806 | 0.661658610793969 | 0.7440018600877281 |

The comparison values above are measured on the same untouched test rows.
The v2 model beats TF-IDF on ROC-AUC and Spearman in this run, but these
numbers are still benchmark results on noisy proxy labels, not hiring
accuracy.

## Ablation

| Feature set | ROC-AUC | Spearman |
|---|---:|---:|
| Original 5 features | 0.5941591517264634 | 0.16399682358295029 |
| Plus TF-IDF | 0.8358819562519282 | 0.40823885566951473 |
| Plus embeddings | 0.7108810594810206 | 0.3887040786221697 |
| Plus skill features | 0.7547152214306725 | 0.40485411083065 |
| All features | 0.8572466263478467 | 0.4367805043878437 |

## Extraction coverage

| Feature | Coverage |
|---|---:|
| `exp_years` | 0.4448005127383432 |
| `required_years` | 0.20990225925332479 |
| `num_certs` | 0.6398013138920045 |
| `degree_level` | 0.9814132350584842 |
| `gpa` | 0.1895529562570101 |

Missing numeric values are median-imputed using the training partition only.
MiniLM embeddings are chunked and cached under
`backend/models/trained/v2/cache/`. The saved model is
`backend/models/trained/xgb_ranker_v2.json`; v1 remains unchanged.

## Limitations and assumptions

- The source dataset does not declare a license in its metadata.
- The public labels are proxy judgments and may contain noise.
- When the dataset has no explicit resume/job identifiers, stable row-qualified
  IDs are synthesized for leakage-safe splitting. Repeated job-description text
  is retained separately for ranking-group evaluation.
- NDCG is reported only for test job-text groups with at least two resumes and
  differing labels.
- The calibrated 0-100 score is intended for ranking support, not a probability
  of hiring success.
