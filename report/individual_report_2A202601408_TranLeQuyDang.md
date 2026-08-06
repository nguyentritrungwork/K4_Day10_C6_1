# Member Role Report - Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Trần Lê Quý Đăng |
| MSSV | 2A202601408 |
| Khóa/Lớp | K4 |
| Tên nhóm | K4_Day10_C6_1 |
| Vai trò chính | Role 3 - Cleaning & Corruption Owner |
| Repository | `K4_Day10_C6_1` |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data cleaning (CP3) | `src/ingestion/cleaning.py::build_clean_dataframe` | Raw records (`data/raw/crossref_records.json`) | Clean dataframe, `data/clean/papers_clean.csv`, `data/clean/papers_clean.json` | Hoàn thành |
| Data corruption (CP5) | `src/ingestion/corruption.py::corrupt_clean_dataframe` | Clean dataframe | Corrupted dataframe, `data/results/corruption_log.json`, `data/clean/papers_clean_corrupted.json/.csv` | Hoàn thành |
| Data repair (CP6) | `script/demo_role3_cp6.py` | Raw records (`data/raw/crossref_records.json`) | Repaired dataframe, `data/clean/papers_clean_repaired.json/.csv` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Đảm bảo format `text_for_embedding` không bị rỗng | Module retrieval/indexing (Role 4) | Vector embedding có đủ văn bản để parse, không bị lỗi khi chunking. |
| Cung cấp log corruption chi tiết với IDs và giá trị before/after | Module evaluation (Role 5) và Observability (Role 6) | Role 5 và Role 6 dễ dàng đối chiếu record nào bị ảnh hưởng để lý giải việc giảm metrics và signal. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Làm sạch dữ liệu từ nguồn raw | `src/ingestion/cleaning.py`, `data/clean/papers_clean.json` | DataFrame gồm 24 records sạch, đầy đủ title, summary, age_days và text_for_embedding. | Đọc `papers_clean.json` xem đủ 24 dòng, schema chính xác không có missing value. |
| Giả lập lỗi dữ liệu (Corruption) | `src/ingestion/corruption.py`, `data/results/corruption_log.json` | Tạo ra file corrupted có lỗi như: mất record, title bị cắt, summary rỗng, sai năm xuất bản. Ghi log chi tiết. | Mở `corruption_log.json` và `papers_clean_corrupted.json`. |
| Phục hồi dữ liệu từ nguồn (Repair) | `script/demo_role3_cp6.py`, `data/clean/papers_clean_repaired.json` | Re-run cleaning trực tiếp từ raw. Mọi schema và row counts khớp 100% với baseline. Khôi phục thành công các giá trị rỗng/rác. | Chạy lệnh `python script/demo_role3_cp6.py` và so sánh output console. |

Output cụ thể của phần việc là bộ ba dataset (Clean, Corrupted, Repaired) nằm trong `data/clean/` cùng với logic tự động hóa tương ứng. Các artifact này tạo tiền đề để nhóm thử nghiệm độ vững (robustness) của toàn bộ pipeline RAG trước những biến động dữ liệu.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Dữ liệu thô từ Crossref API có thể thiếu trường hoặc định dạng không nhất quán. RAG agent đòi hỏi văn bản (text_for_embedding) rõ ràng và cấu trúc dữ liệu minh bạch. Sau khi có dữ liệu sạch (baseline), hệ thống cần khả năng phục hồi dữ liệu từ các kịch bản hỏng hóc (corruption) như rớt records, giá trị rỗng hay rác, nhằm đánh giá khả năng phản ứng và tự khắc phục của data pipeline.

### Cách triển khai

Trong `build_clean_dataframe`, tôi xử lý dữ liệu thô:
- Chuẩn hóa: `title`, `summary`, `authors` bằng cách strip() và gộp list.
- Drop bad rows: Loại bỏ các dòng thiếu `paper_id`, `title` hoặc `summary`. Drop duplicate `paper_id`.
- Parse Date & Tính age_days: Parse `published` thành datetime (UTC), tính `age_days` so với `run_date`.
- Ghép chuỗi text embedding.

Trong `corrupt_clean_dataframe`, tôi mô phỏng lỗi thực tế:
- `drop_latest`: Bỏ 2 records đầu.
- `blank_summary`: Đặt summary thành chuỗi rỗng.
- `inject_noise`: Chèn text rác ("CORRUPTED_NOISE_123").
- `truncate_title`: Cắt title xuống còn 15 ký tự.
- `stale_date`: Thay năm thành 1999.
- Mỗi thao tác được ghi chép qua hàm helper `add_log`, xuất ra `corruption_log.json`.

Trong `demo_role3_cp6.py` (Repair):
- Tôi bỏ qua việc "copy và sửa lỗi bằng tay" từ bản corrupted. Thay vào đó, load lại `raw_records.json` trực tiếp từ bước ingest và gọi lại `build_clean_dataframe()` để đảm bảo dữ liệu mới nhất (repaired) có schema và chất lượng tương đương baseline sạch.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | Raw records (`crossref_records.json`), Clean records (`papers_clean.json`) |
| Output | `papers_clean.json`, `papers_clean_corrupted.json`, `papers_clean_repaired.json`, `corruption_log.json` |
| Module phụ thuộc | `ingestion.crossref`, `core.config` |
| Module sử dụng output | Embeddings (Role 4), Quality Checks (Role 6), Evaluation (Role 5) |
| Điều kiện lỗi cần xử lý | Empty/Duplicate ID, thiếu raw source, text encoding (đặc biệt Windows charmap). |

### Cách xác minh

```powershell
python script\demo_role3_cp6.py
```

- **Kết quả mong đợi:** Schema và số lượng dòng của Repaired khớp 100% với Baseline (24 dòng). Không có giá trị text_for_embedding rỗng và 0 duplicates. Log chứng minh được các record rỗng/rác đã khôi phục lại nội dung.
- **Kết quả thực tế:** Script chạy xuất ra console xác nhận các record lỗi (VD: `10-1007-s10278-026-02086-9` bị blank summary) đã phục hồi từ 3 ký tự `nan` về nguyên bản 1869 ký tự. Schema đạt chuẩn.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi thực hiện CP6 (Repair), cần khôi phục lại dữ liệu bị hỏng trong `papers_clean_corrupted.json`.
- **Các phương án đã cân nhắc:** 
  1) Đọc file corrupted, tìm các dòng lỗi dựa vào `corruption_log.json` và vá víu lại thủ công. 
  2) Tái lập toàn bộ (Re-run) bằng cách đọc lại từ snapshot raw của Role 2 thông qua hàm `build_clean_dataframe`.
- **Phương án đã chọn:** Phương án 2 (Re-run từ Raw Data).
- **Lý do:** Trong hệ thống Data Pipeline thực tế, việc "vá lỗi dữ liệu" thủ công không mang tính bền vững (non-scalable) và dễ gây lỗi sinh thái. Khôi phục từ snapshot source of truth (Raw) đảm bảo tính toàn vẹn (integrity) cao nhất và thể hiện đúng tính chất Idempotent của pipeline.
- **Bằng chứng:** Output của hàm `build_clean_dataframe(records, run_date)` lập tức tạo ra file repaired có số dòng (24) và schema khớp hoàn toàn với baseline mà không cần viết các hàm gỡ rối phức tạp.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Gặp lỗi `UnicodeEncodeError: 'charmap' codec can't encode character...` khi in log ra console Windows trong kịch bản repair (`demo_role3_cp6.py`).
- **Nguyên nhân gốc:** Script cố in các string tiếng Việt và unicode từ abstract nhưng thiết bị terminal mặc định ở chế độ charmap không tương thích UTF-8.
- **Cách xử lý:** Thêm lệnh cấu hình luồng đầu ra stdout ngay đầu script: `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`.
- **Cách xác minh sau khi sửa:** Chạy lại `python script\demo_role3_cp6.py`, log console hiển thị tốt mọi tiếng Việt và abstract chứa dấu nháy đơn/đôi mà không sinh Exception.
- **Điều học được:** Khi build data pipeline xử lý text tự nhiên, luôn phải handle character encoding triệt để ở cả khâu đọc/ghi file lẫn khâu stdout/logging.

## 7. Hiểu biết về luồng end-to-end

1. Data vào từ Crossref API do Ingestion Layer thu thập và snapshot cứng thành `crossref_records.json` (Role 2).
2. Tới lượt Role 3 (Cleaning) load file raw này, áp dụng logic làm sạch, parse datetime và sinh text context (`papers_clean.json`), đóng vai trò là "Baseline".
3. Role 4 lấy clean data này, đưa vào MiniLM, index vào ChromaDB. Từ đó RAG agent thực hiện Retrieval. Role 5 chạy Benchmark (Judge F1/Accuracy) và Role 6 đánh giá Quality/Freshness của Baseline.
4. Ở Checkpoint 5 (Corruption), tôi lấy bản clean, thêm các nhiễu rác và lỗi thiếu hụt để xuất ra bản `corrupted`. Toàn bộ luồng Role 4, 5, 6 tiếp tục chạy trên bản corrupted này và đo lường sự suy giảm metric/chất lượng.
5. Cuối cùng ở Checkpoint 6, tôi lấy lại snapshot nguyên gốc, làm sạch tạo ra bản `repaired`. Lúc này Agent, Benchmark và Observability lại chạy lần nữa để chứng minh metrics phục hồi về mức baseline chuẩn ban đầu.

## 8. Phân tích kết quả

### Metrics chính (Từ góc nhìn Data Cleaning)

| Metric/signal | Baseline Clean | Corrupted | Repaired | Nhận xét cá nhân |
| --- | ---: | ---: | ---: | --- |
| Row Count | 24 | 23 | 24 | Corrupted bị drop mất 2 record, bù lại 1 record duplicate nên tổng còn 23. Repaired khôi phục chuẩn. |
| Duplicate IDs | 0 | 1 | 0 | Giả lập duplicate được loại bỏ ở bước repair. |
| Blank Summaries | 0 | 1 | 0 | Record bị làm trống `summary` đã khôi phục nguyên văn bản. |
| Truncated Titles | 0 | 1 | 0 | Record bị cắt title đã trở về độ dài đầy đủ. |

### Kết luận từ số liệu

1. Các kỹ thuật corruption như `drop_latest`, `blank_summary`, `truncate_title` đều có khả năng đánh lừa hệ thống Embedding nếu index layer (Role 4) không check dữ liệu đầu vào.
2. Việc repair thành công và trả về chính xác schema, count của Baseline cho thấy pipeline `build_clean_dataframe` được thiết kế chặt chẽ và an toàn (Idempotent), chỉ cần đầu vào đúng thì đầu ra luôn không đổi.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Việc cô lập logic (Clean độc lập, Corrupt độc lập) giúp việc khôi phục (Repair) trở nên mạch lạc và dễ dàng chứng minh tính đúng đắn.
2. Trong quá trình làm việc với Pandas, drop các giá trị rác trước khi tiến hành map/apply chuỗi phức tạp giúp tối ưu hóa hiệu năng và tránh NaN exception.
3. Việc tạo ra `corruption_log.json` cực kỳ hữu ích, giúp team tracking được đúng record nào bị lỗi để giải thích được vì sao câu hỏi trong Test Set của RAG agent bị trả lời sai tương ứng.

### Nếu có thêm thời gian

Tôi sẽ cập nhật thêm các kịch bản corruption phức tạp hơn, ví dụ như "Semantic Corruption" (Thay thế từ ngữ bằng các từ khóa phản văn cảnh nhưng cùng cấu trúc ngữ pháp) để xem LLM Judge (Role 5) có bị đánh lừa khi evaluate câu trả lời sinh ra từ retrieval hay không.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Trần Lê Quý Đăng  
**Ngày xác nhận:** 2026-08-06
