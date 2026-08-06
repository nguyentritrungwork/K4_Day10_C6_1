# Corruption & Repair Comparison Report

This report compares baseline, corrupted, and repaired data artifacts across retrieval metrics, data quality checks, and freshness signals.

## Baseline Metrics

| Field | Value |
| --- | --- |
| samples_evaluated | 15 |
| retrieval_hit_rate | 1.0 |
| mean_token_f1 | 1.0 |
| judge_accuracy | 1.0 |
| mean_judge_score | 5 |

## Corrupted Metrics

| Field | Value |
| --- | --- |
| samples_evaluated | 15 |
| retrieval_hit_rate | 1.0 |
| mean_token_f1 | 0.9333333333333333 |
| judge_accuracy | 0.9333333333333333 |
| mean_judge_score | 4.733333333333333 |

## Repaired Metrics

| Field | Value |
| --- | --- |
| samples_evaluated | 15 |
| retrieval_hit_rate | 1.0 |
| mean_token_f1 | 1.0 |
| judge_accuracy | 1.0 |
| mean_judge_score | 5 |

## Corrupted Quality Summary

| Field | Value |
| --- | --- |
| is_valid | False |
| failed_checks | 3 |
| stale_rows | 0 |

## Repaired Quality Summary

| Field | Value |
| --- | --- |
| is_valid | True |
| failed_checks | 0 |
| stale_rows | 0 |

## Recommendations

- Compare the corrupted and repaired metrics to baseline to confirm whether repair improved retrieval quality.
- Pay attention to freshness signals after repair because stale data can still hurt answer quality.