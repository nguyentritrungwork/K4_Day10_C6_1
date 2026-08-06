# Phase 1 Baseline Report

This report summarizes the baseline clean-data pipeline, including source ingestion, dataset artifacts, retrieval evaluation, data quality checks, and freshness signals.

## Source & Dataset Summary

| Field | Value |
| --- | --- |
| source_api | Crossref REST API |
| source_query | agentic retrieval augmented generation large language model |
| source_filter | from-pub-date:2026-02-07,has-abstract:true |
| max_results | 24 |
| raw_record_count | 24 |
| clean_row_count | 24 |
| raw_records_path | D:\K4_Day10_C6_1\data\raw\crossref_records.json |
| clean_csv | D:\K4_Day10_C6_1\data\clean\papers_clean.csv |
| clean_json | D:\K4_Day10_C6_1\data\clean\papers_clean.json |
| evaluation_test_set | D:\K4_Day10_C6_1\data\eval\test_set.json |
| embeddings_manifest | D:\K4_Day10_C6_1\data\embeddings\papers_embeddings.json |

## Retrieval & QA Metrics

| Field | Value |
| --- | --- |
| samples_evaluated | 15 |
| retrieval_hit_rate | 1.0 |
| mean_token_f1 | 1.0 |
| judge_accuracy | 1.0 |
| mean_judge_score | 5 |

## Data Quality Summary

| Field | Value |
| --- | --- |
| quality_report_name | baseline_quality.json |
| total_rows | 24 |
| is_valid | True |
| passed_checks | 10 |
| failed_checks | 0 |
| outlier_row_count | 24 |
| duplicate_paper_id_rows | 0 |
| summary_missing_rows | 0 |
| text_for_embedding_missing | 0 |

## Freshness Summary

| Field | Value |
| --- | --- |
| latest_published | 2026-08-01T00:00:00+00:00 |
| oldest_published | 2026-02-12T00:00:00+00:00 |
| stale_rows | 0 |
| missing_published_rows | 0 |
| missing_age_days_rows | 0 |
| freshness_threshold_days | 180 |
| is_fresh | True |

## Recommendations

- Review the baseline quality and freshness signals to confirm whether the clean dataset is production-ready.
- Use the same `data/eval/test_set.json` for baseline, corrupted, and repaired evaluations to keep comparisons valid.
- Investigate any failed quality checks before progressing to corruption and repair flows.
