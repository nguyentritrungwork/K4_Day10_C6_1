# Checkpoint 5 - Vai tro 5: Corrupted Evaluation

## Trang thai artifact

| Artifact | Trang thai |
| --- | --- |
| `data/eval/test_set.json` | Co, 15 cau hoi, dung lai tu checkpoint 2 |
| `data/results/baseline_metrics.json` | Co |
| `data/results/baseline_answers.json` | Co |
| `data/clean/papers_clean_corrupted.json` | Co |
| `data/results/corruption_log.json` | Co |
| `data/embeddings/papers_embeddings_corrupted.json` | Co, collection `papers-corrupted`, 23 documents |
| `data/results/corrupted_metrics.json` | Chua co |
| `data/results/corrupted_answers.json` | Chua co |

## Ket luan quan trong

Vai tro 5 co the phan tich impact tu corrupted artifacts hien co, nhung chua the xac nhan official corrupted evaluation output vi `corruption_flow.py` van chua tao `data/results/corrupted_metrics.json` va `data/results/corrupted_answers.json`.

## Baseline metrics

| Metric | Baseline |
| --- | --- |
| samples | 15 |
| `retrieval_hit_rate` | 1.0 |
| `mean_token_f1` | 1.0 |
| `judge_accuracy` | 1.0 |
| `mean_judge_score` | 5.0 |

## Corruption log da kiem tra

| Corruption type | Record bi anh huong | Tac dong |
| --- | --- | --- |
| `drop_latest` | `10-1111-exsy-70341`, `10-2118-234689-pa` | 24 rows -> 22 rows |
| `blank_summary` | `10-1007-s10278-026-02086-9` | summary thanh rong |
| `inject_noise` | `10-21203-rs-3-rs-10178277-v1` | them `CORRUPTED_NOISE_123` vao summary |
| `truncate_title` | `10-2196-preprints-106157` | title bi cat ngan |
| `stale_date` | `10-3390-buildings16132637` | published doi tu `2026-07-02T00:00:00Z` sang `1999-07-02T00:00:00Z` |
| `duplicate_row` | `10-21079-11681-50309` | duplicate 1 row |

## Doi chieu voi test set

Tat ca 15 cau hoi trong `data/eval/test_set.json` van co `ground_truth_doc_ids` ton tai trong corrupted data.

Case bi anh huong ro nhat:

- Question ID: `q12`
- Question type: `date`
- Paper ID: `10-3390-buildings16132637`
- Ground truth baseline: `2026-07-02T00:00:00Z`
- Corrupted published date: `1999-07-02T00:00:00Z`
- Corruption type: `stale_date`
- Tac dong ky vong: retrieval van co the hit document dung, nhung answer cho cau hoi ngay publish se sai.

## Manual estimate cua vai tro 5

Do official corrupted metrics chua co, day la uoc tinh deterministic tu corrupted artifacts va logic answer theo exact title lookup:

| Metric | Baseline | Corrupted manual estimate | Delta |
| --- | --- | --- | --- |
| `retrieval_hit_rate` | 1.0 | 1.0 | 0.0 |
| `mean_token_f1` | 1.0 | 0.9333 | -0.0667 |
| `judge_accuracy` | 1.0 | 0.9333 | -0.0667 |
| `mean_judge_score` | 5.0 | 4.7333 | -0.2667 |

Ly do metric giam: cau `q12` hoi ngay publish cua paper `10-3390-buildings16132637`, trong khi corrupted data da doi ngay publish thanh nam 1999.

## Blocker can Role 1 / Role 4 xu ly

- `src/pipelines/corruption_flow.py` van dang `NotImplementedError`.
- Chua co official `data/results/corrupted_metrics.json`.
- Chua co official `data/results/corrupted_answers.json`.

De checkpoint 5 dat day du theo rubric, nhom can chay official corrupted evaluation bang dung `data/eval/test_set.json` va sinh ra hai file tren.

## Trang thai ban giao cua vai tro 5

Vai tro 5 da hoan thanh phan phan tich checkpoint 5 dua tren artifact hien co:

- Da xac nhan test set khong doi.
- Da doc corruption log.
- Da doi chieu test set voi corrupted dataset.
- Da tim duoc case bi anh huong: `q12`.
- Da tao manual metric estimate trong `data/eval/checkpoint5_role5_corrupted_manual_metrics.json`.

Phan con thieu khong thuoc rieng vai tro 5: official corrupted metrics/answers tu corruption flow.
