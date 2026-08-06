# CP5 - Role 6 Observability Owner

## Pham vi CP5

Role 6 phu trach observability cho corrupted dataset. Muc tieu cua CP5 la:

- Kiem tra quality/freshness rieng cho corrupted data.
- Khong ghi de baseline quality/freshness artifacts.
- Noi corruption log voi quality signals va metric change.
- Ghi ro signal nao thay doi va signal nao khong doi de tranh ket luan qua muc.

## Artifact da kiem tra

| Artifact | Trang thai | Muc dich |
| --- | --- | --- |
| `data/results/corruption_log.json` | Co | Ghi lai corruption type, record ID, before/after |
| `data/clean/papers_clean_corrupted.json` | Co | Dataset loi co chu dich |
| `data/quality/corrupted_quality.json` | Co | Quality checks tren corrupted data |
| `data/quality/corrupted_freshness.json` | Co | Freshness report tren corrupted data |
| `data/results/corrupted_metrics.json` | Co | Metric impact tren RAG/evaluation |
| `data/results/corrupted_answers.json` | Co | Answer-level evidence |
| `data/reports/corruption_report.md` | Co | Comparison report baseline/corrupted/repaired |

## Quality summary

| Signal | Baseline | Corrupted | Nhan xet |
| --- | ---: | ---: | --- |
| `total_rows` | 24 | 23 | Giam do `drop_latest`, sau do co duplicate row |
| `is_valid` | true | false | Corrupted data fail quality gate |
| `passed_checks` | 10 | 7 | Giam 3 checks |
| `failed_checks` | 0 | 3 | Co loi du lieu co chu dich |
| `paper_id_missing` | 0 | 0 | Khong anh huong |
| `paper_id_duplicate_rows` | 0 | 2 | Bi tac dong boi `duplicate_row` |
| `summary_missing` | 0 | 1 | Bi tac dong boi `blank_summary` |
| `short_summary_rows` | 0 | 1 | Bi tac dong boi `blank_summary` |
| `text_for_embedding_missing` | 0 | 0 | Khong bi rong hoan toan |
| `age_days_missing` | 0 | 0 | Khong bi mat |
| `negative_age_rows` | 0 | 0 | Khong anh huong |

## Failed checks trong corrupted data

| Check | Value | Expected | Severity | Nguyen nhan lien quan |
| --- | ---: | --- | --- | --- |
| `paper_id_unique` | 2 | 0 duplicate rows | critical | `duplicate_row` voi `10-21079-11681-50309` |
| `summary_not_null` | 1 | 0 missing | warning | `blank_summary` voi `10-1007-s10278-026-02086-9` |
| `summary_min_length` | 1 | 0 rows shorter than 40 chars | warning | Summary bi blank nen qua ngan |

## Freshness summary

| Signal | Corrupted value | Nhan xet |
| --- | ---: | --- |
| `total_rows` | 23 | Khop corrupted dataset |
| `latest_published` | `2026-07-13T00:00:00+00:00` | Latest record van gan baseline |
| `oldest_published` | `1999-07-02T00:00:00+00:00` | Phan anh `stale_date` da xuat hien |
| `stale_rows` | 0 | Luu y: check hien dua vao `age_days`, khong bat duoc stale date neu chi doi `published` |
| `missing_published_rows` | 0 | Khong mat published |
| `missing_age_days_rows` | 0 | Khong mat age_days |
| `is_fresh` | true | Can dien giai can than vi oldest published da la 1999 |

## Noi corruption log voi signals

| Corruption type | Record ID | Expected signal | Actual evidence |
| --- | --- | --- | --- |
| `drop_latest` | `10-1111-exsy-70341`, `10-2118-234689-pa` | Row count giam | Corrupted rows = 23 so voi baseline 24 |
| `blank_summary` | `10-1007-s10278-026-02086-9` | `summary_missing`, `short_summary_rows` tang | Ca hai signal = 1 |
| `inject_noise` | `10-21203-rs-3-rs-10178277-v1` | Metric/answer co the xau di neu test cham record | Chua lam metric giam trong answers hien tai |
| `truncate_title` | `10-2196-preprints-106157` | Title bi cat, retrieval co the xau di | Chua lam metric giam trong test set hien tai |
| `stale_date` | `10-3390-buildings16132637` | Oldest published doi ve 1999, answer date co the sai | `q12` tra loi 1999 thay vi 2026 |
| `duplicate_row` | `10-21079-11681-50309` | Duplicate paper ID tang | `paper_id_duplicate_rows = 2` |

## Noi quality signals voi metric impact

| Metric | Baseline | Corrupted | Delta | Giai thich |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0 | 1.0 | 0.0 | Retrieval van tim duoc ground truth documents |
| `mean_token_f1` | 1.0 | 0.9333 | -0.0667 | `q12` sai ngay publish do stale date |
| `judge_accuracy` | 1.0 | 0.9333 | -0.0667 | `q12` bi judge false |
| `mean_judge_score` | 5.0 | 4.7333 | -0.2667 | Diem giam do mot answer sai |

Case evidence ro nhat:

- Question ID: `q12`
- Paper ID: `10-3390-buildings16132637`
- Corruption: `stale_date`
- Ground truth: `2026-07-02T00:00:00Z`
- Corrupted answer: `1999-07-02T00:00:00Z`
- Retrieval hit: true
- Token F1: 0.0
- Judge score: 1
- Judge correct: false

## Signal khong doi / can tranh ket luan qua muc

- `retrieval_hit_rate` khong giam, nen khong nen ket luan corrupted data lam retrieval hong trong test set hien tai.
- `text_for_embedding_missing = 0`, nen corruption khong lam mat toan bo embedding text.
- `stale_rows = 0` trong freshness report, nhung `oldest_published = 1999-07-02`. Dieu nay cho thay freshness check hien tai chua bat duoc stale date neu `age_days` khong duoc tinh lai sau khi doi `published`.
- Mot so corruption nhu `inject_noise`, `truncate_title`, `drop_latest` chua the hien thanh metric drop ro trong test set hien tai.

## Ket luan CP5 cua Role 6

Role 6 CP5 da hoan thanh:

- Da co corrupted quality/freshness artifacts rieng, khong ghi de baseline.
- Corrupted quality fail 3 checks: duplicate ID, missing summary, short summary.
- Corruption log co the noi truc tiep voi quality signals.
- Metric impact ro nhat la `q12` sai do stale date, lam `mean_token_f1`, `judge_accuracy`, `mean_judge_score` giam.
- Can ghi chu gioi han: freshness report hien tai co `oldest_published` nam 1999 nhung `stale_rows = 0`, vi stale check dua tren `age_days`.

## Handoff cho CP6

- Dung `data/quality/repaired_quality.json` va `data/quality/repaired_freshness.json` de chung minh repair co phuc hoi quality hay khong.
- Dung `data/reports/corruption_report.md` de so sanh baseline - corrupted - repaired.
- Neu co thoi gian, nen sua freshness logic de tinh lai `age_days` tu `published` sau corruption hoac flag oldest published bat thuong.
