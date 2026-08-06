# CP0 - Role 6 Observability Owner

## Pham vi CP0

Vai tro 6 phu trach observability cho pipeline RAG:

- Module chinh: `src/observability/quality.py`, `src/observability/reporting.py`
- Artifact chinh: `data/quality/`, `data/reports/`
- Muc tieu CP0: thong nhat artifact can theo doi, signals can do, va khung report dung de chung minh corruption lam chat luong RAG thay doi.

## Artifact can co sau baseline va corruption flow

### Baseline

| Nhom artifact | Duong dan du kien | Muc dich kiem tra |
| --- | --- | --- |
| Raw response | `data/raw/crossref_response.json` | Chung minh du lieu lay tu Crossref va co the truy vet source. |
| Raw records | `data/raw/crossref_records.json` | Dau vao cho cleaning va repair. |
| Clean dataset | `data/clean/papers_clean.csv`, `data/clean/papers_clean.json` | Dataset sach dung de build index baseline. |
| Embedding manifest | `data/embeddings/papers_embeddings.json` | Chung minh index duoc build tu clean data va dung model da chot. |
| Evaluation set | `data/eval/test_set.json` | Bo cau hoi co dinh cho baseline, corrupted va repaired. |
| Baseline answers | `data/results/baseline_answers.json` | Cau tra loi va source retrieved cua baseline. |
| Baseline metrics | `data/results/baseline_metrics.json` | Do `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score`. |
| Quality report | `data/quality/baseline_quality.json` | Evidence ve row count, null, duplicate, summary length va freshness. |
| Freshness report | `data/quality/freshness_report.json` | Latest/oldest published date, stale rows, trang thai fresh/stale. |
| Phase 1 report | `data/reports/phase1_report.md` | Tom tat source, metrics, quality va freshness cua baseline. |

### Corrupted va repaired

| Nhom artifact | Duong dan du kien | Muc dich kiem tra |
| --- | --- | --- |
| Corruption log | `data/results/corruption_log.json` | Ghi ro corruption type, record bi tac dong, before/after count. |
| Corrupted clean data | `data/clean/papers_clean_corrupted.csv`, `data/clean/papers_clean_corrupted.json` | Dataset loi co chu dich, khong ghi de baseline. |
| Corrupted metrics/answers | `data/results/corrupted_metrics.json`, `data/results/corrupted_answers.json` | Do impact cua data loi len retrieval/answer. |
| Corrupted quality/freshness | `data/quality/corrupted_quality.json`, `data/quality/corrupted_freshness.json` | Signals ky vong xau di sau corruption. |
| Repaired clean data | `data/clean/papers_clean_repaired.csv`, `data/clean/papers_clean_repaired.json` | Dataset repair tu raw records, khong sua tay tu baseline. |
| Repaired metrics/answers | `data/results/repaired_metrics.json`, `data/results/repaired_answers.json` | Do muc do phuc hoi sau repair. |
| Repaired quality/freshness | `data/quality/repaired_quality.json`, `data/quality/repaired_freshness.json` | Signals sau repair de doi chieu voi baseline/corrupted. |
| Comparison report | `data/reports/corruption_report.md` | So sanh baseline - corrupted - repaired va delta. |

## Signals can dinh nghia trong CP0

| Signal | Cach tinh / nguon | Ky vong baseline | Ky vong khi corrupted | Ly do quan trong |
| --- | --- | --- | --- | --- |
| `row_count` | `len(df)` | > 0 va khop voi clean artifact | Giam khi drop latest records, tang khi duplicate | Phat hien mat/tang bat thuong so record. |
| `paper_id_missing` | So dong `paper_id` null/rong | 0 | Co the tang neu corruption lam hong ID | `paper_id` la khoa de truy vet ground truth va lookup. |
| `paper_id_duplicate` | So paper_id bi trung | 0 | Tang khi add duplicate rows | Duplicate lam sai count va co the anh huong retrieval. |
| `title_missing` | So dong title null/rong | 0 hoac rat thap | Tang neu truncate/blank title loi | Title la tin hieu manh cho embedding va answer. |
| `summary_missing` | So dong summary null/rong | 0 hoac thap | Tang khi blank summary | Summary rong lam giam ngu canh cho embedding. |
| `short_summary_rows` | Summary co do dai < 40 ky tu | Thap | Tang khi summary bi blank/truncate | Phat hien content khong du nghia. |
| `text_for_embedding_missing` | So dong text_for_embedding null/rong | 0 | Tang neu clean/corruption lam hong text | Index can text khong rong de embedding. |
| `age_days_missing` | So dong age_days null | 0 hoac co ly do ro | Tang neu date parse loi | Freshness phu thuoc vao published/age_days. |
| `stale_rows` | So dong `age_days > freshness_threshold_days` | Phu hop filter Crossref | Tang khi lam stale publication date | Chung minh data cu anh huong freshness. |
| `latest_published` | Max published date | Gan voi source filter | Co the cu hon neu drop latest records | Phat hien source khong con moi. |
| `retrieval_hit_rate` | Tu metrics evaluation | Lam moc baseline | Co the giam khi corruption tac dong document trong test set | Lien ket data quality voi retrieval quality. |
| `mean_token_f1` | Tu metrics evaluation | Lam moc baseline | Co the giam neu answer mat context | Lien ket data quality voi answer quality. |

## Khung report de chung minh impact

### `phase1_report.md`

1. Source summary: Crossref API, query/filter, raw count, clean count.
2. Artifact checklist: raw, clean, embeddings, eval, answers, metrics, quality/freshness.
3. Baseline metrics: `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score`.
4. Quality signals: row count, missing field, duplicate, stale rows.
5. Freshness: latest/oldest published, threshold, `is_fresh`.
6. Ket luan baseline: dataset co du sach de lam moc so sanh hay chua.

### `corruption_report.md`

1. Corruption log summary: moi corruption type, so record bi tac dong, parameter.
2. Bang so sanh metrics: baseline, corrupted, repaired, delta.
3. Bang so sanh quality/freshness: baseline, corrupted, repaired.
4. Mot case evidence: question/test item nao bi hit/miss thay doi, source doc nao bi anh huong.
5. Ket luan co dieu kien: corruption nao co evidence lam giam metric, repair da phuc hoi den muc nao.
6. Gioi han ket luan: neu metric khong doi, neu sample size nho, hoac judge metric khong chay duoc.

## Checklist CP0 cua role 6

- [x] Da xac dinh artifact observability phai co cho baseline, corrupted va repaired.
- [x] Da dinh nghia signals ve row count, null, duplicate, summary, freshness va metric impact.
- [x] Da phac thao cau truc `phase1_report.md` va `corruption_report.md`.
- [x] Da thong nhat nguyen tac: report phai khop artifact that, khong to dep so lieu.
- [x] Da thong nhat dung cung `data/eval/test_set.json` cho baseline, corrupted va repaired.

## Lenh kiem tra nhanh o CP0

```powershell
rg -n "TODO\(student\)|NotImplementedError" src\observability src\pipelines
Get-ChildItem data -Recurse -File
git status --short
```

## Handoff cho CP tiep theo

- CP1: implement `run_data_quality_checks` trong `src/observability/quality.py` de tao quality JSON dau tien.
- CP2: kiem tra embedding manifest va document count co the audit duoc.
- CP3: tao `phase1_report.md` tu metrics, quality va freshness that.
- CP5: tao quality/freshness rieng cho corrupted dataset, khong ghi de baseline.
- CP6: tao comparison report baseline - corrupted - repaired, chi ket luan recovery neu co evidence.
