# Member Role Report - Day 10: Data Pipeline & Data Observability

## 1. Thong tin ca nhan

| Thong tin | Noi dung |
| --- | --- |
| Ho va ten | Pham Viet Bach |
| MSSV | 2A202601410 |
| Khoa/Lop | K4 |
| Ten nhom | K4_Day10_C6_1 |
| Vai tro chinh | Role 6 - Observability owner |
| Repository | `K4_Day10_C6_1` |
| Ngay hoan thanh | 2026-08-06 |

## 2. Vai tro va pham vi cong viec

### Phan viec so huu

| Module/deliverable | File/ham phu trach | Input nhan vao | Output ban giao | Trang thai |
| --- | --- | --- | --- | --- |
| Ke hoach observability | `report/cp0_role6_observability_plan.md` | Yeu cau lab, luong baseline/corruption/repair | Danh sach artifact, signal va khung report can theo doi | Hoan thanh |
| Data quality checks | `src/observability/quality.py` | Clean dataframe tu pipeline | `data/quality/baseline_quality.json` | Hoan thanh |
| Freshness report | `src/observability/quality.py::build_freshness_report` | Truong `published`, `age_days` va nguong freshness | `data/quality/freshness_report.json` | Hoan thanh |
| Embedding/index audit | `data/quality/embedding_audit.json`, `report/cp2_role6_embedding_audit.md` | Clean data, embedding manifest va Chroma collection | Audit document count, collection, model va warning ve persist path | Hoan thanh |
| Phase 1 baseline report | `src/observability/reporting.py`, `data/reports/phase1_report.md` | Source summary, metrics, quality, freshness, embedding audit | Baseline evidence pack de so sanh cac lan corrupted/repaired | Hoan thanh |

### Viec ho tro ngoai pham vi chinh

| Hoat dong | Thanh vien/module duoc ho tro | Ket qua |
| --- | --- | --- |
| Chot artifact contract cho baseline, corrupted va repaired | Cac module ingestion, retrieval, evaluation | Cac duong dan report/metric duoc thong nhat trong `report/cp0_role6_observability_plan.md` |
| Kiem tra embedding/index truoc khi bao cao baseline | Module retrieval/indexing | Xac nhan clean rows = manifest docs = Chroma docs = 24 |
| Ghi nhan gioi han reproducibility | Module embedding/index | Phat hien warning ve `manifest_persist_path_differs_from_current_settings` trong `embedding_audit.json` |

## 3. Ket qua theo vai tro

| Nhiem vu da thuc hien | File/ham/artifact lien quan | Ket qua ban giao | Cach xac minh |
| --- | --- | --- | --- |
| Dinh nghia cac signal observability can theo doi | `report/cp0_role6_observability_plan.md` | Signal ve row count, missing ID/title/summary, duplicate, stale rows, retrieval metrics | Doc checklist CP0 trong file plan |
| Chay va luu data quality baseline | `src/observability/quality.py`, `data/quality/baseline_quality.json` | 24 rows, 10 passed checks, 0 failed checks, `is_valid=true` | Mo `data/quality/baseline_quality.json` |
| Tao freshness report | `data/quality/freshness_report.json` | Latest published `2026-08-01`, oldest `2026-02-12`, stale rows = 0, `is_fresh=true` | Mo `data/quality/freshness_report.json` |
| Audit embedding/index | `data/quality/embedding_audit.json` | Manifest co 24 documents, collection `papers-baseline`, Chroma count = 24 | Mo `data/quality/embedding_audit.json` |
| Tong hop baseline report | `data/reports/phase1_report.md` | Report gom source, artifact checklist, metrics, quality, freshness va embedding audit | Mo `data/reports/phase1_report.md` |

Output cu the cua phan viec la bo artifact observability trong `data/quality/` va baseline report `data/reports/phase1_report.md`. Cac artifact nay giup nhom chung minh baseline data dang sach, index co the audit duoc, va co moc so sanh cho corruption/repair.

## 4. Giai thich phan ky thuat da thuc hien

### Van de can giai quyet

Pipeline RAG khong chi can chay duoc ma con can co bang chung ve chat luong du lieu. Neu raw data bi mat record, bi trung ID, bi rong summary, bi stale ngay cong bo, hoac index khong khop clean dataset, retrieval/answer metrics co the sai nhung kho truy nguyen nguyen nhan. Phan observability cua toi tao cac report de phat hien nhung loi do.

### Cach trien khai

Trong `run_data_quality_checks`, toi kiem tra cac cot bat buoc nhu `paper_id`, `title`, `summary`, `published`, `age_days`, `text_for_embedding`. Ham dem cac truong rong, duplicate `paper_id`, summary ngan hon 40 ky tu, `age_days` am/thieu, va so dong vuot nguong freshness. Moi check co `name`, `passed`, `value`, `expected`, `severity`, giup report khong chi noi pass/fail ma con co so lieu doi chieu.

Trong `build_freshness_report`, toi chuyen `published` sang datetime UTC, lay latest/oldest published date, dem stale rows, missing published rows va missing age days rows. Dataset chi duoc coi la fresh khi co du row, khong stale, khong thieu published va khong thieu `age_days`.

Trong `generate_phase1_report`, toi tong hop source summary, artifact checklist, retrieval metrics, quality summary, freshness summary va embedding/index audit thanh mot report baseline de nhom nop va dung lam moc so sanh.

### Input, output va contract

| Thanh phan | Mo ta |
| --- | --- |
| Input | Clean dataframe tu `data/clean/papers_clean.json`/`.csv`, settings ve `freshness_threshold_days`, metrics tu `data/results/baseline_metrics.json` |
| Output | `baseline_quality.json`, `freshness_report.json`, `embedding_audit.json`, `phase1_report.md` |
| Module phu thuoc | `core.config.Settings`, `core.utils.write_json`, pandas dataframe tu ingestion/cleaning |
| Module su dung output | Reporting, evaluation comparison, corruption/repair analysis |
| Dieu kien loi can xu ly | Thieu cot bat buoc, duplicate paper ID, summary rong/ngan, text embedding rong, date parse loi, stale rows, index count khong khop clean data |

### Cach xac minh

```powershell
Get-Content data\quality\baseline_quality.json -Raw
Get-Content data\quality\freshness_report.json -Raw
Get-Content data\quality\embedding_audit.json -Raw
Get-Content data\reports\phase1_report.md -Raw
```

- **Ket qua mong doi:** Quality baseline pass, freshness fresh, embedding count khop clean data, report phase 1 co du artifact.
- **Ket qua thuc te:** `baseline_quality.json` co 24 rows, 10 checks pass, 0 failed; `freshness_report.json` co stale rows = 0 va `is_fresh=true`; `embedding_audit.json` xac nhan 24 documents trong manifest va Chroma.
- **Artifact/log:** `data/quality/baseline_quality.json`, `data/quality/freshness_report.json`, `data/quality/embedding_audit.json`, `data/reports/phase1_report.md`.

## 5. Mot quyet dinh ky thuat quan trong

- **Boi canh:** Nhom can ket luan corruption/repair dua tren artifact that, khong chi dua vao cam tinh rang pipeline da chay.
- **Cac phuong an da can nhac:** Chi viet report thu cong sau khi chay pipeline; hoac tao cac JSON artifact co cau truc roi generate report tu artifact.
- **Phuong an da chon:** Tao quality/freshness/embedding audit JSON truoc, sau do generate `phase1_report.md` tu cac artifact do.
- **Ly do:** JSON co cau truc de doi chieu, tai su dung cho comparison report, va tranh tinh trang report ghi sai so lieu so voi output that.
- **Bang chung quyet dinh phu hop:** `phase1_report.md` hien thi dung cac metric trong `baseline_metrics.json`: `retrieval_hit_rate=1.0`, `mean_token_f1=1.0`, `judge_accuracy=1.0`, `mean_judge_score=5`.

## 6. Mot loi hoac blocker da xu ly

- **Trieu chung/loi nguyen van:** Embedding audit tra ve warning `manifest_persist_path_differs_from_current_settings`.
- **Lenh hoac buoc tai hien:** Kiem tra `data/quality/embedding_audit.json` sau khi audit embedding manifest va Chroma collection.
- **Nguyen nhan goc:** Manifest luu persist path cu khac voi workspace hien tai, trong khi local Chroma DB hien tai van doc duoc collection `papers-baseline`.
- **Cach xu ly:** Ghi warning ro trong `embedding_audit.json` va `phase1_report.md` thay vi bo qua. Report khuyen nghi regenerate/normalize embedding manifest truoc khi nop cuoi cung.
- **Cach xac minh sau khi sua:** Audit van xac nhan collection count = 24 va document count matches clean rows = true.
- **Dieu hoc duoc:** Observability khong chi bat loi data content, ma con phai bat loi reproducibility cua artifact path/model/index.

## 7. Hieu biet ve luong end-to-end

1. Du lieu di tu Crossref API vao raw response/records, sau do cleaning tao `papers_clean`, ghep cac truong quan trong thanh `text_for_embedding`, build embedding manifest va Chroma collection `papers-baseline`. Retrieval agent dung vector index nay de tim document lien quan cho cau hoi trong test set.
2. Evaluation set `data/eval/test_set.json` gom cac cau hoi va ground-truth document IDs. Khi chay evaluation, retrieval duoc tinh hit/miss dua tren viec top-k co tra ve dung document ID hay khong; answer quality duoc do bang token F1 va judge metrics.
3. Quality checks tap trung vao tinh hop le cua dataset tai mot thoi diem: row count, missing fields, duplicate, summary length, embedding text, age days. Freshness monitoring tap trung rieng vao do moi cua published date va stale rows theo nguong 180 ngay.
4. Phai dung cung test set cho baseline, corrupted va repaired vi neu doi cau hoi/ground truth thi metric thay doi co the den tu test set, khong phai do corruption hay repair.
5. Repair chi nen xem la thanh cong khi artifact repaired quality/freshness va repaired metrics phuc hoi gan baseline. Hien repo moi co baseline metrics va corruption log; chua co artifact `repaired_metrics.json`/`repaired_quality.json`, nen chua the ket luan repair thanh cong.

## 8. Phan tich ket qua

### Metrics chinh

| Metric/signal | Baseline | Corrupted | Repaired | Nhan xet ca nhan |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0 | N/A | N/A | Baseline retrieval hit toan bo 15 mau; chua co corrupted/repaired metrics de so sanh |
| `mean_token_f1` | 1.0 | N/A | N/A | Baseline answer trung khop cao voi expected answer |
| `judge_accuracy` | 1.0 | N/A | N/A | Judge accuracy baseline dat 1.0 |
| `mean_judge_score` | 5 | N/A | N/A | Diem judge baseline dat muc toi da |
| Quality checks | 10/10 pass | N/A | N/A | Baseline khong co failed check |
| Freshness status | Fresh | N/A | N/A | Baseline co 0 stale rows voi nguong 180 ngay |

### Ket luan tu so lieu

1. `drop_latest`, `blank_summary`, `inject_noise`, `truncate_title`, `stale_date`, `duplicate_row` duoc ghi trong `data/results/corruption_log.json` -> ky vong lam xau row count, summary quality, title quality, freshness va duplicate signal -> chua co corrupted metrics nen chua ket luan duoc muc giam cua agent metric.
2. Repair action theo design phai khoi phuc tu raw records -> quality/freshness signal phai ve gan baseline -> chua co repaired artifact nen chua the xac nhan metric phuc hoi.

Corruption co kha nang anh huong ro nhat ve observability la `stale_date` va `duplicate_row`, vi chung truc tiep lam tang stale rows/duplicate rows, hai signal co nguong pass/fail ro rang. Tuy nhien ve retrieval quality, `blank_summary` hoac `truncate_title` co the tac dong manh hon neu record bi sua nam trong ground truth cua test set.

Ket qua khac ky vong la corruption flow trong `src/pipelines/corruption_flow.py` van de `NotImplementedError`, nen repo moi co corrupted clean artifacts va corruption log, chua co full comparison report baseline - corrupted - repaired.

## 9. Dieu hoc duoc va huong cai thien

### Ba dieu quan trong nhat

1. Data pipeline can co artifact audit rieng cho tung buoc, vi chi nhin final metric khong du de biet loi den tu ingestion, cleaning, indexing hay evaluation.
2. Data quality va freshness nen duoc do bang signal co cau truc, co nguong, co severity; nhu vay report co the truy vet va lap lai.
3. RAG agent phu thuoc rat manh vao chat luong data: mat title/summary, duplicate ID, stale date hoac index count khong khop deu co the lam retrieval va answer evaluation sai lech.

### Neu co them thoi gian

Toi se hoan thien `src/pipelines/corruption_flow.py` de tao day du `corrupted_metrics.json`, `corrupted_quality.json`, `corrupted_freshness.json`, `repaired_metrics.json`, `repaired_quality.json`, `repaired_freshness.json` va `data/reports/corruption_report.md`. Cai tien nay co the do bang muc do phuc hoi cua metrics va so failed quality checks so voi baseline.

## 10. Cam ket cua thanh vien

- [x] Noi dung bao cao phan anh dung phan viec va muc hieu cua toi.
- [x] Toi co the giai thich luong end-to-end, khong chi module minh phu trach.
- [x] Moi ket luan ve ket qua deu co artifact hoac metric de doi chieu.
- [x] Toi khong ghi "da chay thanh cong" cho phan chua duoc kiem chung.
- [x] Bao cao khong chua `.env`, API key, token hoac secret.
- [x] Bao cao nay khong phai ban sao nguyen van cua bao cao nhom hoac bao cao thanh vien khac.

**Ho va ten:** Pham Viet Bach  
**Ngay xac nhan:** 2026-08-06
