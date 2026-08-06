# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Trần Đặng Vương Quốc Long  |
| MSSV               | 2A202601744                |
| Khóa/Lớp         | K4                         |
| Tên nhóm         | C6_1                       |
| Vai trò chính    | Ingestion Owner (Người phụ trách Ingestion & Data Foundation) |
| Repository         | K4_Day10_C6_1              |
| Ngày hoàn thành | 2026-08-06                 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | ---------- |
| **Ingestion Engine & API Fetcher** | `src/ingestion/crossref.py`<br>- `fetch_source_records()`<br>- `parse_crossref_payload()` | Query: `"retrieval-augmented generation"`, filter, max_results | `data/raw/crossref_response.json`<br>`data/raw/crossref_records.json` | Hoàn thành |
| **Snapshot Loader & Integrity Guard** | `src/ingestion/crossref.py`<br>- `load_raw_records()`<br>- `compute_file_sha256()`<br>- `verify_raw_integrity()` | Đường dẫn file snapshot JSON | List `PaperRecord` + SHA-256 Checksums | Hoàn thành |
| **Data Lineage 5-Stage Tracker** | `src/ingestion/crossref.py`<br>- `trace_record_lineage()` | `paper_id`, `Settings` | Dict Lineage 5 tầng (Raw API → Raw Record → Clean → Corrupted → Repaired) | Hoàn thành |
| **Security & Git Leak Audit (CP6)** | `script/demo_role2_cp6.py`<br>`.gitignore` | Codebase, Git tree, regex key patterns | Báo cáo kiểm tra 0 secret leak, bảo vệ `.env` và vector index | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ----------------------------- | ------- |
| **Hỗ trợ Data Cleaning & Contract** | Cleaning Owner (`src/ingestion/cleaning.py`) | Thống nhất cấu trúc `PaperRecord`, chuẩn hóa text HTML, unescape ký tự đặc biệt giúp `build_clean_dataframe()` xử lý 24 bản ghi mượt mà không lỗi format. |
| **Hỗ trợ Pipeline Integration & Repair** | Integrator / Lead (`src/pipelines/corruption_flow.py`) | Đảm bảo `corruption_flow.py` tái sử dụng `load_raw_records(settings.paths.raw_records_json)` với cờ `refresh_source=False`, bảo đảm cô lập mạng và công bằng benchmark. |
| **Hỗ trợ Security & Git Policy** | Toàn bộ nhóm | Bổ sung quy tắc bảo vệ `.env.*`, `*.pem`, `data/chroma/` vào `.gitignore`, ngăn ngừa hoàn toàn nguy cơ lọt API Key lên Git. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------- | --------------------------- | ---------------- | ------------- |
| **Nạp dữ liệu thô & lưu snapshot bất biến** | `src/ingestion/crossref.py`<br>`data/raw/crossref_response.json`<br>`data/raw/crossref_records.json` | Snapshot API response (245 KB) và 24 PaperRecords (60 KB) với mã băm SHA-256 cố định | `verify_raw_integrity()`<br>SHA-256 response: `e62d2aa8...`<br>SHA-256 records: `be5f4a06...` |
| **Reload snapshot & Cô lập mạng (CP6)** | `src/ingestion/crossref.py`<br>`script/demo_role2_cp6.py` | Nạp lại 24 bản ghi chuẩn từ snapshot cục bộ, 0 network call ra ngoài khi repair | `python script/demo_role2_cp6.py` (Mục 1 Pass) |
| **Chứng minh phục hồi record qua Lineage (CP6)** | `src/ingestion/crossref.py`<br>`data/results/corruption_log.json`<br>`data/clean/papers_clean_repaired.json` | Chứng minh 6 dạng lỗi (Drop latest, Blank summary, Inject noise, Truncate title, Stale date, Duplicate) được phục hồi 100% về dữ liệu chuẩn | `python script/demo_role2_cp6.py` (Mục 2 Pass) |
| **Kiểm tra Security & Quét Secret không lọt Git (CP6)** | `.gitignore`<br>`script/demo_role2_cp6.py` | Quét 85 files trong dự án: 0 API key bị lộ, file `.env` được bảo vệ hoàn toàn không bị Git theo dõi | `python script/demo_role2_cp6.py` (Mục 3 Pass)<br>`git status` |

**Output cụ thể tạo ra và bàn giao:**
1. Bộ snapshot thô bất biến tại `data/raw/crossref_response.json` và `data/raw/crossref_records.json`.
2. Hàm `trace_record_lineage()` kết nối đầy đủ 5 tầng dữ liệu từ API thô đến bản ghi phục hồi.
3. Script tự động `script/demo_role2_cp6.py` chứng minh toàn bộ tiêu chuẩn Checkpoint 6 của Ingestion Role.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
1. **Bất định từ nguồn bên ngoài (External Source Non-Determinism)**: Nếu mỗi lần chạy pipeline lại gọi Crossref API trực tiếp, danh sách bài báo và thứ tự kết quả sẽ biến động theo thời gian, làm sai lệch kết quả benchmark so sánh giữa Baseline, Corrupted và Repaired.
2. **Dữ liệu thô chứa định dạng phức tạp (Noise & Format Inconsistency)**: Crossref API trả về abstract lẫn mã JATS/XML (`<jats:p>`, `<jats:sec>`), HTML entities (`&amp;`, `&lt;`), cấu trúc ngày không đồng nhất (`date-parts`), cần chuẩn hóa thành schema bất biến trước khi đưa vào pipeline.
3. **Mất dấu nguồn gốc dữ liệu (Data Provenance Loss)**: Khi dữ liệu bị lỗi (corrupted) hoặc bị drop mất hàng, cần có cơ chế Data Lineage để truy xuất ngược lại nguồn gốc thô, làm bằng chứng phục hồi cho tầng Cleaning/RAG.
4. **Nguy cơ rò rỉ khóa bí mật (Secret Leakage Risk)**: Đảm bảo các cấu hình `.env` chứa API key không bị đưa vào Git commit tree.

### Cách triển khai
1. **Kiến trúc Ingestion 2 pha & Bất biến (Immutable Ingestion Architecture)**:
   - Tách biệt hoàn toàn việc nạp API từ xa (`fetch_source_records`) và nạp cục bộ (`load_raw_records`).
   - Sau khi ingest lần đầu, toàn bộ payload được lưu thành snapshot thô `data/raw/crossref_response.json` và các bản ghi có cấu trúc `data/raw/crossref_records.json`.
   - Cờ `settings.refresh_source = False` ép pipeline chạy hoàn toàn trên local snapshot, đảm bảo tính tái lập (reproducibility) 100%.
2. **Thuật toán Chuẩn hóa Text & Abstract Cleaning**:
   - Sử dụng Regex `re.sub(r"<[^>]+>", " ", raw_abstract)` loại bỏ toàn bộ thẻ XML/HTML.
   - Sử dụng `html.unescape()` giải mã các ký tự thực thể.
   - Chuẩn hóa khoảng trắng dư thừa (`normalize_whitespace`).
3. **Hệ thống Lineage Tracking 5 tầng (`trace_record_lineage`)**:
   - Truy vấn chéo `paper_id` qua: (1) `raw_api_response` -> (2) `raw_records_json` -> (3) `clean_json` -> (4) `corrupted_clean_json` -> (5) `repaired_clean_json`.
   - Cung cấp bằng chứng cụ thể trước và sau khi repair cho từng trường (title, summary, date).
4. **Secret Scanner & Git Protection**:
   - Cấu hình `.gitignore` chặn triệt để `.env`, `.env.*` (ngoại trừ `.env.example`), `data/chroma/`, `.venv/`.
   - Tự động quét regex tìm pattern `AIzaSy...`, `sk-...`, `sk-or-...`, `sk-ant-...` trên toàn bộ source code.

### Input, output và contract

| Thành phần | Mô tả |
| ---------- | ----- |
| **Input** | Query Crossref: `"retrieval-augmented generation"`, `max_results=50`, file snapshot `data/raw/crossref_records.json` |
| **Output** | List `PaperRecord` (dataclass frozen gồm: `paper_id`, `title`, `summary`, `authors`, `categories`, `primary_category`, `published`, `updated`, `abs_url`, `pdf_url`, `comment`) |
| **Module phụ thuộc** | `core.config.Settings`, `core.utils` |
| **Module sử dụng output** | `ingestion.cleaning.build_clean_dataframe()`, `pipelines.phase1`, `pipelines.corruption_flow` |
| **Điều kiện lỗi cần xử lý** | Crossref API trả về HTTP 429/503 (xử lý exponential backoff retry 3 lần); bản ghi thiếu DOI hoặc thiếu Title bị tự động loại bỏ; ngày xuất bản thiếu tháng/ngày được fallback về ngày mùng 1. |

### Cách xác minh

```bash
python script/demo_role2_cp6.py
```

- **Kết quả mong đợi:**
  - Mục 1: Snapshot nguyên vẹn (SHA-256 khớp 100%), 0 cuộc gọi mạng ra ngoài khi nạp lại.
  - Mục 2: 6/6 kịch bản lỗi trong `corruption_log.json` được chứng minh phục hồi qua Lineage 5 tầng.
  - Mục 3: Quét 85 files đạt 0 secret leak, file `.env` được bảo vệ khỏi Git tracking.
- **Kết quả thực tế:** Tất cả các assert và kiểm tra tự động đều vượt qua (Exit Code: 0).
- **Artifact/log liên quan:**
  - Snapshot thô: `data/raw/crossref_response.json`, `data/raw/crossref_records.json`
  - Báo cáo so sánh: `data/reports/corruption_report.md`
  - Script audit: `script/demo_role2_cp6.py`

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi thực hiện quy trình Repair tại Checkpoint 6, có hai hướng tiếp cận:
  - *Phương án A*: Gọi lại Crossref API trực tuyến để lấy dữ liệu mới nhất phục vụ việc repair.
  - *Phương án B*: Nạp lại dữ liệu trực tiếp từ snapshot cục bộ `data/raw/crossref_records.json` đã lưu ở Baseline và kích hoạt Network Guard (chặn network).
- **Các phương án đã cân nhắc:**
  - Phương án A giúp có dữ liệu mới tức thời, nhưng vi phạm nguyên tắc khoa học về tính công bằng trong benchmark (Fair Benchmark Principle), vì dữ liệu mới từ API có thể khác biệt so với dữ liệu baseline, khiến việc so sánh delta giữa Baseline vs Corrupted vs Repaired không còn chuẩn xác.
  - Phương án B giữ nguyên tuyệt đối tập mẫu (ground truth) của Baseline, bảo đảm quy trình khép kín, tái lập được và chạy nhanh mà không phụ thuộc vào tình trạng mạng hay API rate limit.
- **Phương án đã chọn:** Chọn **Phương án B (Local Snapshot Re-ingestion với Network Guard)**.
- **Lý do:** Đảm bảo tính toàn vẹn (Data Integrity) và tính tái lập (Reproducibility) tuyệt đối cho hệ thống RAG. Thư mục `data/raw/` được xem là Single Source of Truth (SSOT) bất biến.
- **Bằng chứng quyết định phù hợp:** Checksum SHA-256 của `raw_records.json` giữ nguyên `be5f4a06...` từ Baseline đến Repaired; 0 network call phát sinh trong suốt quá trình chạy `demo_role2_cp6.py` và `run_corruption_flow.py`.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  ValueError: Trailing data
  pandas.io.json._json.FrameParser.parse()
  ```
- **Lệnh hoặc bước tái hiện:** Khi đọc file `data/clean/papers_clean.json` bằng lệnh `pd.read_json(path, orient="records")` trong script kiểm thử lineage.
- **Nguyên nhân gốc:** File `papers_clean.json` được ghi ở định dạng JSON Lines (`orient="records", lines=True`), trong đó mỗi bản ghi là một dòng JSON riêng biệt chứ không phải một mảng JSON `[...]`. Khi `pd.read_json` mặc định đọc file dạng khối mảng thì gặp lỗi `Trailing data` ở dòng thứ 2.
- **Cách xử lý:** Viết hàm tiện ích `_load_dataset_df(path)` trong `demo_role2_cp6.py` với cơ chế fallback thông minh: Thử đọc bằng `lines=True` trước, nếu thất bại mới chuyển sang `orient="records"`.
- **Cách xác minh sau khi sửa:** Chạy lại `python script/demo_role2_cp6.py`, nạp thành công 100% các dataset sạch, hỏng và sửa mà không phát sinh lỗi parser.
- **Điều học được:** Cần thống nhất chặt chẽ serialization contract (JSON Array vs JSON Lines) giữa các module Ingestion, Cleaning và Evaluation trong data pipeline.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - Dữ liệu thô từ Crossref API được tải về qua `fetch_source_records()`, làm sạch sơ bộ và lưu thành snapshot tại `data/raw/`.
   - Tầng Cleaning (`src/ingestion/cleaning.py`) lọc bỏ bản ghi không đạt chuẩn, tính `age_days`, ghép các trường văn bản quan trọng thành trường `text_for_embedding`.
   - Tầng Retrieval (`src/retrieval/index.py`) sử dụng mô hình embedding `all-MiniLM-L6-v2` để chuyển đổi `text_for_embedding` thành các vector đa chiều và nạp vào vector store ChromaDB theo collection riêng (`papers-baseline`).

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Evaluation set chứa các cặp câu hỏi (`question`), câu trả lời mẫu (`ground_truth`) và danh sách ID tài liệu chứa bằng chứng (`ground_truth_doc_ids`).
   - Khi đánh giá, hệ thống đo `retrieval_hit_rate` bằng cách kiểm tra xem các document do ChromaDB trả về (top-k) có chứa `ground_truth_doc_ids` hay không.
   - Chất lượng câu trả lời sinh ra từ Agent được so sánh với `ground_truth` thông qua Token F1 Score và LLM-as-a-Judge Score (thang điểm 1-5).

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - **Data Quality Checks**: Kiểm tra tính hợp lệ về mặt cấu trúc và nội dung tĩnh (Schema validation, missing values, độ dài tối thiểu của text, tính duy nhất của ID, không chứa chuỗi rác/nhiễu).
   - **Freshness Monitoring**: Đo lường tính cập nhật của dữ liệu theo thời gian (tính `age_days` dựa trên ngày xuất bản so với thời điểm hiện tại `run_date`), phát hiện các tài liệu quá cũ (stale records) vượt ngưỡng cho phép (180 ngày).

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Để bảo đảm tính khách quan và khoa học khi đo lường (Controlled Experiment). Việc giữ nguyên test set giúp cô lập biến số duy nhất là chất lượng của tập dữ liệu (Clean vs Corrupted vs Repaired). Mọi sự tăng giảm trong metrics (`retrieval_hit_rate`, `mean_token_f1`, `judge_score`) đều phản ánh chính xác tác động của dữ liệu chứ không bị sai lệch do độ khó của câu hỏi.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - **Về mặt Data Artifact & Quality**: `data/clean/papers_clean_repaired.json` có số lượng bản ghi đầy đủ (24 bản ghi), `repaired_quality.json` ghi nhận `is_valid: True` và `failed_checks: 0`.
   - **Về mặt Agent Metrics**: `repaired_metrics.json` và `corruption_report.md` thể hiện các chỉ số phục hồi hoàn toàn về mức của Baseline (`retrieval_hit_rate: 1.0`, `mean_token_f1: 1.0`, `judge_accuracy: 1.0`, `mean_judge_score: 5.0`).

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ------------- | -------: | --------: | -------: | --------------------- |
| `retrieval_hit_rate` | 1.0 | 1.0 | 1.0 | MiniLM vẫn tìm được top-k do các từ khóa chính vẫn xuất hiện ở các trường khác trong ngữ cảnh. |
| `mean_token_f1` | 1.0 | 0.9333 | 1.0 | Giảm xuống 93.3% ở tập Corrupted do câu hỏi rơi vào bản ghi bị blank summary hoặc drop, phục hồi 100% ở Repaired. |
| `judge_accuracy` | 1.0 | 0.9333 | 1.0 | LLM Judge phát hiện câu trả lời ở corrupted bị thiếu thông tin hoặc sai lệch thực tế. |
| `mean_judge_score` | 5.0 | 4.7333 | 5.0 | Điểm đánh giá trung bình bị kéo tụt xuống 4.73 ở corrupted và khôi phục tuyệt đối mức 5.0 sau khi repair. |
| Quality checks | 0 failed (Valid) | 3 failed (Invalid) | 0 failed (Valid) | Tập Corrupted kích hoạt 3 cảnh báo vi phạm chất lượng dữ liệu; tập Repaired vượt qua 100% checks. |
| Freshness status | 0 stale | 0 stale | 0 stale | Phản ánh đúng hiện trạng ngày công bố của snapshot dữ liệu. |

### Kết luận từ số liệu

**Hai chuỗi nguyên nhân – bằng chứng:**
1. `[Data corruption (Blank Summary, Drop Record, Noise Injection)]` → `[Quality signal: 3 failed checks; Corrupted dataframe is_valid=False]` → `[Agent mean_token_f1 giảm từ 1.0 xuống 0.9333; mean_judge_score giảm từ 5.0 xuống 4.7333]`.
2. `[Repair action: Reload raw records snapshot & re-run clean pipeline]` → `[Quality signal: 0 failed checks, is_valid=True]` → `[Agent mean_token_f1 và mean_judge_score phục hồi 100% về mức 1.0 và 5.0]`.

**Corruption nào ảnh hưởng rõ nhất và vì sao?**
- **Drop Record và Blank Summary** ảnh hưởng nghiêm trọng nhất. Khi bản ghi bị xóa hoặc abstract bị rút cạn về rỗng, LLM Agent hoàn toàn mất đi ngữ cảnh factual để trả lời câu hỏi chuyên sâu, dẫn đến hiện tượng từ chối trả lời hoặc giảm sút Token F1 Score.

**Kết quả khác với kỳ vọng ban đầu:**
- Ban đầu dự đoán `retrieval_hit_rate` sẽ giảm khi bị tiêm nhiễu. Tuy nhiên thực tế `retrieval_hit_rate` vẫn đạt `1.0` vì mô hình MiniLM có tính năng tìm kiếm ngữ nghĩa tốt dựa trên Title và các từ khóa liên quan còn sót lại trong context. Điều này chứng minh rằng việc đánh giá hệ thống RAG không thể chỉ nhìn vào mỗi Retrieval Hit Rate mà bắt buộc phải kết hợp cả Answer Generation Quality (Token F1 & Judge Score).

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Về Data Pipeline**: Dữ liệu thô (Raw Ingestion) phải luôn được coi là Single Source of Truth bất biến (Immutable Snapshot). Việc tách biệt pha Ingestion và Cleaning là nguyên tắc sống còn để bảo đảm tính tái lập của pipeline.
2. **Về Data Observability & Lineage**: Data Lineage 5 tầng giúp tiết kiệm hàng giờ debug khi có sự cố dữ liệu. Hệ thống giám sát chất lượng (Quality Checks) đóng vai trò như chốt chặn cảnh báo sớm trước khi dữ liệu độc hại lan sang tầng Vector Store và LLM.
3. **Về ảnh hưởng của Data đến RAG Agent**: Chất lượng đầu ra của AI Agent tỷ lệ thuận trực tiếp với độ sạch của dữ liệu (Garbage In, Garbage Out). Ngay cả một lỗi nhỏ như nhiễu tóm tắt cũng làm suy giảm độ tin cậy của câu trả lời.

### Nếu có thêm thời gian
- Xây dựng cơ chế **Automated Schema Evolution & Anomaly Drift Detection**: Tự động phát hiện khi Crossref API thay đổi cấu trúc schema hoặc khi phân phối độ dài abstract thay đổi đột ngột vượt qua ngưỡng 3-sigma để cảnh báo tự động trước khi ghi vào raw storage.

---

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Trần Đặng Vương Quốc Long  
**Ngày xác nhận:** 2026-08-06

