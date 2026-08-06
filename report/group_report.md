# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | K4_E403           |
| Tên nhóm         | C6-1   |
| Repository         | https://github.com/nguyentritrungwork/K4_Day10_C6_1.git |
| Ngày hoàn thành | 2026-08-06               |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Nguyễn Trí Trung | 2A202601418 | Lead - Pipeline Integrator | `src/pipelines/`, `script/` |
| 2 | Trần Đặng Vương Quốc Long | 2A202601744 | Ingestion Owner | `src/ingestion/crossref.py`, `data/raw/` |
| 3 | Trần Lê Quý Đăng | 2A202601408 | Cleaning & Corruption Owner | `src/ingestion/cleaning.py`, `src/ingestion/corruption.py` |
| 4 | Nguyễn Nhật Minh | 2A202601414 | RAG & Agent Owner | `src/retrieval/`, `data/embeddings/` |
| 5 | Nguyễn Văn Qúy | 2A202601508 | Evaluation Owner | `src/evaluation/`, `data/eval/` |
| 6 | Phạm Việt Bách | 2A202601410 | Observability Owner | `src/observability/`, `data/quality/` |

## 2. Tóm tắt kết quả

Nhóm C6-1 đã hoàn thành xuất sắc toàn bộ 2 pha của bài lab xây dựng RAG Data Pipeline & Data Observability.
* **Pha 1 (Baseline)**: Tự động thu thập dữ liệu sạch từ Crossref API (24 records), làm sạch dữ liệu, xây dựng cơ sở dữ liệu vector ChromaDB (`papers-baseline`) và đánh giá hiệu năng (đạt chỉ số hoàn hảo 1.0 trên test set 15 câu hỏi).
* **Pha 2 (Corruption & Repair)**: Giả lập 6 kịch bản lỗi dữ liệu có chủ đích (Drop records, Blank summary, Noise summary, Truncate title, Stale published date, Duplicate rows) và đo đạc tác động lên RAG Agent. Lỗi dữ liệu làm giảm hiệu năng của RAG Agent (F1-score và Judge Accuracy sụt giảm từ 1.0 xuống còn **0.9333** và phá hỏng các kiểm tra dữ liệu với 3 lỗi nghiêm trọng).
* **Repair**: Bằng cách chạy lại quy trình làm sạch từ tệp dữ liệu thô ban đầu đáng tin cậy (re-clean) và xây dựng chỉ mục vector phục hồi (`papers-repaired`), toàn bộ hiệu năng RAG và chất lượng dữ liệu được phục hồi hoàn toàn 100% về mức baseline gốc.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API
    -> raw response/raw records (data/raw/)
    -> cleaning và data modeling (data/clean/)
    -> embedding + ChromaDB index (data/chroma/)
    -> evaluation baseline (data/results/baseline_metrics.json)
    -> quality/freshness reports (data/quality/)
    -> corruption (data/clean/papers_clean_corrupted.json)
    -> re-index và re-evaluate (data/results/corrupted_metrics.json)
    -> repair từ dữ liệu nguồn (data/clean/papers_clean_repaired.json)
    -> comparison report (data/reports/corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | Crossref REST API | Fetch API, retry-backoff, parse raw payload | `crossref_response.json`, `crossref_records.json` | Trần Đặng Vương Quốc Long |
| Cleaning          | `crossref_records.json` | Chuẩn hóa chuỗi, tính toán `age_days`, tạo `text_for_embedding` | `papers_clean.csv` / `.json` | Trần Lê Quý Đăng |
| Embedding/index   | Cleaned Dataframe | Embed văn bản bằng MiniLM, lưu trữ Chroma DB | `papers_embeddings.json` & thư mục `chroma/` | Nguyễn Nhật Minh |
| Evaluation        | Chroma Index | Gọi LLM sinh câu trả lời, dùng LLM đánh giá Verdict | `test_set.json`, `baseline_answers.json`, `baseline_metrics.json` | Nguyễn Văn Qúy |
| Observability     | Cleaned Dataframe | Kiểm tra null, trùng lặp, độ dài, stale ngày xuất bản | `baseline_quality.json`, `freshness_report.json` | Phạm Việt Bách |
| Corruption/repair | Cleaned Dataframe / Raw records | Chạy corrupt tạo lỗi / Chạy re-clean dữ liệu thô gốc | `papers_clean_corrupted.json`, `papers_clean_repaired.json` | Trần Lê Quý Đăng |
| Orchestration     | `Settings` | Điều phối quy trình tuần tự Phase 1 & Corruption Flow | `phase1_report.md`, `corruption_report.md` | Nguyễn Trí Trung |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | `openai` |
| `LLM_MODEL`                | `gpt-4o-mini` |
| Embedding model              | `text-embedding-3-small` |
| Số lượng Crossref records | `24` |
| Retrieval `top_k`           | `4` |
| Freshness threshold          | `180` (ngày) |
| Random seed, nếu có        | Không cấu hình |

### Lệnh cài đặt

```bash
uv sync
```

### Lệnh chạy

Baseline:
```bash
uv run python script/run_phase1.py
```

Corruption flow:
```bash
uv run python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | 2026-08-06 21:46 | `data/results/baseline_metrics.json` |
| Corruption flow   | Thành công | 2026-08-06 21:47 | `data/reports/corruption_report.md` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref REST API (https://api.crossref.org/works) |
| Query/filter                | query: `agentic retrieval augmented generation large language model`, filter: `from-pub-date:2026-02-07,has-abstract:true` |
| Thời điểm lấy dữ liệu | 2026-08-06T21:45:00Z |
| Số record nhận được    | `24` |
| Cơ chế retry/backoff      | Thử lại tối đa 3 lần, sleep lũy thừa tăng dần (`backoff_factor = 2.0`) khi gặp lỗi 429/500/503 |

### Raw và clean schema

| Trường        | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa   | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| `paper_id` | string | Có | DOI duy nhất của paper | Bỏ qua dòng dữ liệu |
| `title` | string | Có | Tiêu đề của paper | Bỏ qua dòng dữ liệu |
| `summary` | string | Có | Tóm tắt (Abstract) của bài báo | Bỏ qua dòng dữ liệu |
| `authors` | list | Không | Danh sách tác giả | Gán danh sách rỗng |
| `categories` | list | Không | Danh mục học thuật | Gán danh sách rỗng |
| `published` | string | Có | Ngày xuất bản chính thức | Bỏ qua dòng dữ liệu |
| `age_days` | int | Có | Tuổi của tài liệu so với ngày chạy | Tính toán tự động |
| `text_for_embedding` | string | Có | Nội dung văn bản phục vụ embedding | Ghép tiêu đề + tóm tắt + tác giả |

### Quy tắc cleaning

| Quy tắc | Quality dimension liên quan | Số record bị tác động | Cách xác minh |
| --- | --- | :---: | --- |
| Loại bỏ dòng thiếu `paper_id`, `title`, `summary` | Completeness / Validity | 0 | Kiểm tra số dòng sau loại bỏ |
| Loại bỏ các bản ghi trùng lặp khóa `paper_id` | Uniqueness | 0 | Kiểm tra trùng lặp trên cột `paper_id` |
| Loại bỏ bản ghi có ngày xuất bản lỗi không parse được | Validity | 0 | Kiểm tra định dạng trường `published` |

* **Cách tạo `text_for_embedding`**: Ghép nối các trường thông tin theo cấu trúc: `Title: <title>\nSummary: <summary>\nAuthors: <authors_joined>\nCategories: <categories_joined>`
* **Cách tạo `age_days`**: Trừ ngày chạy thực tế `run_date` (timezone aware) cho trường `published`.

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | `15` |
| Các `question_type`                    | `summary`, `authors`, `date` |
| Ground-truth document ID                 | Khớp theo `paper_id` |
| Embedding model                          | `text-embedding-3-small` |
| Vector store/collection                  | ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`) |
| Retrieval `top_k`                       | `4` |
| LLM provider/model                       | `openai` / `gpt-4o-mini` |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

* **Giải thích việc giữ nguyên test set**: Để đảm bảo tính so sánh công bằng và khoa học. Nếu thay đổi tập câu hỏi giữa các pha, sự thay đổi về metrics sẽ phản ánh cả sự khác biệt của câu hỏi chứ không chỉ phản ánh thuần túy tác động từ lỗi dữ liệu.

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/`                          | Có | Gồm `crossref_response.json` & `crossref_records.json` |
| Cleaned dataset          | `data/clean/`                        | Có | Gồm `papers_clean.csv` & `papers_clean.json` |
| Embedding manifest/index | `data/embeddings/`                   | Có | Chỉ mục vector ChromaDB đã được nạp |
| Evaluation set           | `data/eval/`                         | Có | Chứa tệp `test_set.json` cố định |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có | Đầy đủ metrics |
| Quality/freshness        | `data/quality/`                      | Có | `baseline_quality.json` & `freshness_report.json` |
| Baseline report          | `data/reports/phase1_report.md`      | Có | Báo cáo Markdown Pha 1 |

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` | 1.0 | RAG Agent tìm thấy chính xác tài liệu chứa đáp án cho cả 15/15 câu hỏi. |
| `mean_token_f1`      | 1.0 | Câu trả lời của RAG trùng khớp hoàn hảo với ground truth. |
| `judge_accuracy`     | 1.0 | LLM Evaluator đánh giá toàn bộ câu trả lời là chính xác (15/15). |
| `mean_judge_score`   | 5.0 | Điểm số trung bình tuyệt đối là 5/5. |
| Ragas, nếu có        | N/A | Bị bỏ qua để tối ưu tốc độ chạy. |

## 8. Data quality và freshness

### Quality checks

| Check | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline | Bằng chứng |
| --- | --- | --- | --- | --- |
| `row_count_positive` | Validity | > 0 rows | Pass (24 rows) | `baseline_quality.json` |
| `paper_id_unique` | Uniqueness | 0 duplicates | Pass (0 duplicate) | `baseline_quality.json` |
| `summary_min_length` | Validity | 0 rows < 40 chars | Pass (0 short rows) | `baseline_quality.json` |
| `freshness_threshold` | Freshness | 0 rows > 180 days | Pass (0 stale rows) | `baseline_quality.json` |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | Tập dữ liệu sạch làm baseline (`data/clean/papers_clean.json`) |
| Timestamp mới nhất       | `2026-08-01T00:00:00+00:00` |
| Ngưỡng freshness         | `180` ngày |
| Trạng thái baseline      | `Fresh` |
| Lý do                     | Tài liệu mới nhất có tuổi là 5 ngày, tài liệu cũ nhất có tuổi là 175 ngày, không có tài liệu nào vượt quá 180 ngày. |

## 9. Corruption scenarios và repair

| Corruption | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair |
| --- | --- | :---: | --- | --- | --- |
| `drop_latest` | Xóa 2 record mới nhất | 2 | `row_count` giảm | Số dòng giảm từ 24 xuống 22 | Nạp lại raw records |
| `blank_summary` | Xóa tóm tắt của 1 dòng | 1 | `summary_missing` tăng | `mean_token_f1` giảm xuống 0.93 | Làm sạch lại từ raw |
| `truncate_title` | Cắt ngắn tiêu đề bài báo | 1 | Không ảnh hưởng trực tiếp | Agent lookup lỗi | Làm sạch lại từ raw |
| `stale_date` | Đổi năm xuất bản thành 1999 | 1 | `stale_rows` tăng | Freshness chuyển thành Stale | Làm sạch lại từ raw |
| `duplicate_row` | Nhân đôi 1 bản ghi | 1 | `paper_id_duplicate` tăng | `row_count` tăng nhẹ | Làm sạch lại từ raw |

* **Cơ chế Repair**: Nạp lại snapshot dữ liệu thô gốc, chạy lại toàn bộ quy trình làm sạch dữ liệu tự động (`build_clean_dataframe`) thay vì sửa tay kết quả bị lỗi.

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate`   | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | Retrieval vẫn lấy đủ top-k chứa tài liệu đúng |
| `mean_token_f1`        | 1.0 | 0.9333 | 1.0 | -0.0667 | +0.0667 | Hiệu năng trả lời giảm khi mất context và đã phục hồi hoàn toàn |
| `judge_accuracy`       | 1.0 | 0.9333 | 1.0 | -0.0667 | +0.0667 | Độ chính xác câu trả lời giảm và phục hồi về 100% |
| `mean_judge_score`     | 5.0 | 4.7333 | 5.0 | -0.2667 | +0.2667 | Điểm số đánh giá của LLM phục hồi hoàn hảo về 5.0 |
| Quality checks pass/fail | 10 / 0 | 7 / 3 | 10 / 0 | 3 checks bị hỏng | Phục hồi hoàn hảo | Dữ liệu lỗi vi phạm kiểm tra chất lượng nghiêm trọng |
| Freshness status         | Fresh | Fresh | Fresh | Không đổi | Không đổi | Lỗi ngày cũ chỉ xảy ra trên 1 dòng nên không kéo stale toàn tập |

### Kết luận nhân quả:
1. **Lỗi dữ liệu làm suy giảm RAG**: Lỗi làm rỗng summary (`blank_summary`) làm mất ngữ cảnh của bài báo `10-1007-s10278-026-02086-9`, dẫn đến RAG Agent không có thông tin chi tiết để trả lời câu hỏi liên quan, kéo thấp chỉ số `mean_token_f1` và `judge_accuracy` của cả hệ thống xuống còn `0.9333`.
2. **Quy trình Repair khôi phục RAG thành công**: Hành động repair tái tạo lại dữ liệu sạch từ file thô đáng tin cậy đã khôi phục đầy đủ tóm tắt của bài báo, khôi phục `mean_token_f1` và `judge_accuracy` về lại mức tối đa `1.0`.

## 11. Vấn đề tích hợp quan trọng

* **Triệu chứng**: Khi tích hợp quy trình `corruption_flow.py`, hàm `pd.read_json` bị ném lỗi `ValueError: Trailing data` khi đọc file `papers_clean.json`.
* **Nguyên nhân**: File `papers_clean.json` được lưu dưới dạng JSON Lines (mỗi bản ghi là 1 dòng JSON độc lập), trong khi hàm `pd.read_json` mặc định đọc dạng JSON Array.
* **Cách xử lý**: Bọc hàm đọc trong khối `try-except`, nếu gặp lỗi sẽ tự động fallback sang đọc ở chế độ `lines=True`.
* **Cách xác minh**: Chạy lại pipeline thành công và ghi nhận đầu ra đầy đủ.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Trường `categories_joined` bị rỗng hoàn toàn | Không kiểm thử được câu hỏi dạng category | Cải thiện parser Crossref để trích xuất trường `subject` |
| Hard-coded persist path trong manifest | Báo cáo bị cảnh báo đường dẫn không khớp trên máy khác | Tự động chuẩn hóa đường dẫn tương đối (relative path) |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
