# Calibrated Validation Score Distribution

This report was generated without retraining, changing the model, or
changing frontend match-band thresholds.

- Dataset: `cnamuangtoun/resume-job-description-fit`
- Validation rows: **999**
- Score unit: calibrated model-estimated Good Fit probability, displayed as 0-100

## Feature provenance

The previous script did not load a cached training-time feature matrix.
It recomputed features with the current `extract_pair_features` extractor,
using the saved TF-IDF vectorizer and allowing the MiniLM embedding cache.
The second pass reruns the same current extractor after the embedding
cache is populated. A complete cached training-time feature matrix was
not saved by the training run, so there is no separate historical
feature-vector version to load. Both passes use the same saved
model, calibrator, split, and training-partition median imputation.
## Cache-allowed current extractor

| Statistic | Calibrated score |
|---|---:|
| min | 0.000000 |
| median | 10.000000 |
| 90th percentile | 70.454544 |
| 95th percentile | 72.000003 |
| 99th percentile | 86.274511 |
| max | 100.000000 |

| Threshold | Count |
|---:|---:|
| > 60 | 169 |
| > 70 | 103 |
| > 80 | 45 |
| > 90 | 2 |

## Current extractor, cache-reused pass

| Statistic | Calibrated score |
|---|---:|
| min | 0.000000 |
| median | 10.000000 |
| 90th percentile | 70.454544 |
| 95th percentile | 72.000003 |
| 99th percentile | 86.274511 |
| max | 100.000000 |

| Threshold | Count |
|---:|---:|
| > 60 | 169 |
| > 70 | 103 |
| > 80 | 45 |
| > 90 | 2 |

## Side-by-side calibration tables

Bootstrap intervals use 2,000 row-resamples within each bin and the
2.5th/97.5th percentiles. Bins with fewer than 30 rows are marked
unreliable.

### Cache-allowed current extractor

| Score bin | Mean predicted (95% CI) | Actual Good Fit rate (95% CI) | Samples | Reliability |
|---|---:|---:|---:|---|
| 0-10% | 1.985515 (1.778667, 2.203901) | 0.040712 (0.022901, 0.061069) | 393 | reliable |
| 10-20% | 11.832701 (11.607369, 12.073055) | 0.173387 (0.125000, 0.221774) | 248 | reliable |
| 20-30% | 26.522461 (24.849558, 28.195363) | 0.000000 (0.000000, 0.000000) | 2 | unreliable (<30) |
| 30-40% | 35.617457 (35.588004, 35.632184) | 0.371795 (0.269231, 0.474359) | 78 | reliable |
| 40-50% | 43.797023 (43.286965, 44.325733) | 0.509259 (0.416667, 0.601852) | 108 | reliable |
| 50-60% | 58.377606 (58.377606, 58.377606) | 1.000000 (1.000000, 1.000000) | 1 | unreliable (<30) |
| 60-70% | 65.737033 (65.352129, 66.153845) | 0.651515 (0.530303, 0.772727) | 66 | reliable |
| 70-80% | 71.094044 (70.907523, 71.280565) | 0.793103 (0.689655, 0.896552) | 58 | reliable |
| 80-90% | 86.274511 (86.274511, 86.274511) | 0.697674 (0.558140, 0.837209) | 43 | reliable |
| 90-100% | 100.000000 (100.000000, 100.000000) | 0.500000 (0.000000, 1.000000) | 2 | unreliable (<30) |

### Current extractor, cache-reused pass

| Score bin | Mean predicted (95% CI) | Actual Good Fit rate (95% CI) | Samples | Reliability |
|---|---:|---:|---:|---|
| 0-10% | 1.985515 (1.778667, 2.203901) | 0.040712 (0.022901, 0.061069) | 393 | reliable |
| 10-20% | 11.832701 (11.607369, 12.073055) | 0.173387 (0.125000, 0.221774) | 248 | reliable |
| 20-30% | 26.522461 (24.849558, 28.195363) | 0.000000 (0.000000, 0.000000) | 2 | unreliable (<30) |
| 30-40% | 35.617457 (35.588004, 35.632184) | 0.371795 (0.269231, 0.474359) | 78 | reliable |
| 40-50% | 43.797023 (43.286965, 44.325733) | 0.509259 (0.416667, 0.601852) | 108 | reliable |
| 50-60% | 58.377606 (58.377606, 58.377606) | 1.000000 (1.000000, 1.000000) | 1 | unreliable (<30) |
| 60-70% | 65.737033 (65.352129, 66.153845) | 0.651515 (0.530303, 0.772727) | 66 | reliable |
| 70-80% | 71.094044 (70.907523, 71.280565) | 0.793103 (0.689655, 0.896552) | 58 | reliable |
| 80-90% | 86.274511 (86.274511, 86.274511) | 0.697674 (0.558140, 0.837209) | 43 | reliable |
| 90-100% | 100.000000 (100.000000, 100.000000) | 0.500000 (0.000000, 1.000000) | 2 | unreliable (<30) |

The two paths should match numerically when the embedding cache is valid.

These are validation-set calibration diagnostics, not hiring accuracy.
They describe how the saved calibrator behaves on the validation split.
