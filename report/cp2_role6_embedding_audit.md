# CP2 - Role 6 Embedding Audit And Baseline Signals

## Scope

Role 6 checks that embedding/index artifacts are auditable before baseline reporting in CP3.

## Embedding / Index Audit

| Item | Result |
| --- | --- |
| Clean dataset | `data/clean/papers_clean.json` |
| Clean row count | 24 |
| Embedding manifest | `data/embeddings/papers_embeddings.json` |
| Backend | `chroma` |
| Embedding model | `all-MiniLM-L6-v2` |
| Manifest collection name | `papers-baseline` |
| Manifest document count | 24 |
| Chroma collection found | `papers-baseline` |
| Chroma collection count | 24 |
| Count match | Pass: clean rows = manifest docs = Chroma docs = 24 |

## Baseline Quality Signals Kept For Comparison

| Signal | Value |
| --- | ---: |
| `row_count` | 24 |
| `paper_id_missing` | 0 |
| `paper_id_duplicate_rows` | 0 |
| `title_missing` | 0 |
| `summary_missing` | 0 |
| `short_summary_rows` | 0 |
| `text_for_embedding_missing` | 0 |
| `age_days_missing` | 0 |
| `negative_age_rows` | 0 |
| `stale_rows` | 0 |
| `freshness_threshold_days` | 180 |

## Freshness Signals

| Signal | Value |
| --- | --- |
| `latest_published` | `2026-08-01T00:00:00+00:00` |
| `oldest_published` | `2026-02-12T00:00:00+00:00` |
| `stale_rows` | 0 |
| `missing_published_rows` | 0 |
| `missing_age_days_rows` | 0 |
| `is_fresh` | `true` |

## Warning

The embedding manifest currently stores this persist path:

```text
E:/26.AI-VIN/thuc_hanh/K4_Day10_C6_1/data/chroma
```

Current project settings point to:

```text
E:/Downloads/Learn_IT/VinUni/Unit_10/K4_Day10_C6_1/data/chroma
```

The local Chroma DB in the current project is usable and has `papers-baseline` with 24 documents, but the manifest should be regenerated or normalized before final submission so another machine can reproduce the path cleanly.

## CP3 Report Draft Inputs

Use these artifacts for `phase1_report.md`:

- `data/quality/baseline_quality.json`
- `data/quality/freshness_report.json`
- `data/quality/embedding_audit.json`
- `data/embeddings/papers_embeddings.json`
- `data/chroma/`

Report should include:

1. Source and clean row count.
2. Embedding model, collection name, and document count.
3. Baseline quality signals.
4. Freshness status.
5. Baseline metrics once Role 5 evaluation is done.
