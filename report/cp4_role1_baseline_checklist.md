# CP4 - Role 1: Pipeline Integrator / Lead Report

Báo cáo Checkpoint 4 (Nghỉ 15 phút) của Vai trò 1 (Lead / Pipeline Integrator) trong bài lab xây dựng RAG Data Pipeline & Data Observability. 
Nhiệm vụ chính ở mốc này: **Xác nhận danh sách các tệp tin kết quả baseline (Baseline Checklist), kiểm tra tính toàn vẹn của chúng và ghi nhận blocker còn lại trước khi chuyển sang pha data corruption và repair.**

---

## 1. Baseline Artifact Checklist

Tính đến thời điểm hiện tại, toàn bộ các tệp tin của pha 1 (Baseline) đã được tạo lập thành công. Dưới đây là bảng đối chiếu chi tiết trạng thái, vị trí vật lý và tính hợp lệ của từng tệp tin kết quả trong thư mục dự án (`D:/K4_Day10_C6_1`):

| Nhóm kết quả | Đường dẫn tệp tin thực tế | Trạng thái | Số lượng / Chỉ số chính | Đánh giá hợp lệ |
| :--- | :--- | :---: | :--- | :---: |
| **Raw Data** | [crossref_response.json](file:///D:/K4_Day10_C6_1/data/raw/crossref_response.json) | **Có mặt** | Phản hồi thô JSON từ API Crossref | Hợp lệ (Lưu vết API) |
| | [crossref_records.json](file:///D:/K4_Day10_C6_1/data/raw/crossref_records.json) | **Có mặt** | 24 bản ghi thô sau khi parse | Hợp lệ |
| **Cleaned Data** | [papers_clean.csv](file:///D:/K4_Day10_C6_1/data/clean/papers_clean.csv) | **Có mặt** | 24 dòng dữ liệu làm sạch | Hợp lệ |
| | [papers_clean.json](file:///D:/K4_Day10_C6_1/data/clean/papers_clean.json) | **Có mặt** | 24 bản ghi JSON hoàn thiện | Hợp lệ (Khớp số dòng) |
| **Embedding & DB** | [papers_embeddings.json](file:///D:/K4_Day10_C6_1/data/embeddings/papers_embeddings.json) | **Có mặt** | Manifest chứa 24 bản ghi được lập chỉ mục | Hợp lệ (all-MiniLM-L6-v2) |
| | [chroma/](file:///D:/K4_Day10_C6_1/data/chroma/) | **Có mặt** | Thư mục cơ sở dữ liệu vector Chroma | Hợp lệ (`papers-baseline`) |
| **Evaluation Set** | [test_set.json](file:///D:/K4_Day10_C6_1/data/eval/test_set.json) | **Có mặt** | 15 câu hỏi (5 `summary`, 5 `authors`, 5 `date`) | Hợp lệ (Ground truth doc IDs khớp) |
| **Baseline Results**| [baseline_answers.json](file:///D:/K4_Day10_C6_1/data/results/baseline_answers.json) | **Có mặt** | 15 câu trả lời kèm tài liệu truy xuất | Hợp lệ |
| | [baseline_metrics.json](file:///D:/K4_Day10_C6_1/data/results/baseline_metrics.json) | **Có mặt** | `hit_rate`: 1.0, `token_f1`: 1.0, `judge_score`: 5.0 | Hợp lệ (Baseline hoàn hảo) |
| **Observability** | [baseline_quality.json](file:///D:/K4_Day10_C6_1/data/quality/baseline_quality.json) | **Có mặt** | 10 kiểm tra chất lượng đều đạt (Pass: 10/10) | Hợp lệ |
| | [freshness_report.json](file:///D:/K4_Day10_C6_1/data/quality/freshness_report.json) | **Có mặt** | Trạng thái: `fresh` (Dữ liệu trong vòng 180 ngày) | Hợp lệ |
| **Final Report** | [phase1_report.md](file:///D:/K4_Day10_C6_1/data/reports/phase1_report.md) | **Có mặt** | Báo cáo chi tiết Markdown của Pha 1 | Cần sửa đổi (xem Blocker) |

---

## 2. Blocker và Rủi ro còn lại

Với tư cách là Lead / Pipeline Integrator chịu trách nhiệm kiểm thử tích hợp toàn dự án, tôi ghi nhận hai blocker quan trọng sau cần được giải quyết ở các bước tiếp theo hoặc ghi chú vào báo cáo chung:

### Blocker 1: Sự không nhất quán và Hard-coded Đường dẫn tuyệt đối (Path Reproducibility Issue)
- **Triệu chứng:**
  Báo cáo [phase1_report.md](file:///D:/K4_Day10_C6_1/data/reports/phase1_report.md) được tạo ra có chứa các đường dẫn tuyệt đối dạng `E:\Downloads\Learn_IT\VinUni\Unit_10\K4_Day10_C6_1\data\...` từ môi trường máy tính trước đó. Trong khi đó, dự án đang chạy thực tế trên thư mục `D:\K4_Day10_C6_1`. 
  Ngoài ra, tệp manifest `papers_embeddings.json` lưu giá trị `persist_path` tuyệt đối là `D:\\K4_Day10_C6_1\\data\\chroma`.
- **Hệ quả:**
  Khi mang dự án sang máy tính khác chạy thử nghiệm hoặc chấm điểm, việc đọc các đường dẫn tuyệt đối cũ này trong báo cáo hoặc trong manifest sẽ gây lỗi hoặc không tìm thấy tệp tin. Điều này vi phạm nghiêm trọng tính tái lập (reproducibility) của data pipeline.
- **Giải pháp đề xuất:**
  Trong code viết báo cáo (`src/observability/reporting.py`) và ghi chỉ mục (`src/retrieval/index.py`), các đường dẫn tuyệt đối nên được rút gọn thành đường dẫn tương đối (relative path) tính từ thư mục gốc của project, hoặc tự động chuẩn hóa động theo `Settings.paths.project_dir`.

### Blocker 2: Trường thông tin `categories_joined` bị rỗng hoàn toàn
- **Triệu chứng:**
  Qua đối chiếu chất lượng tại [checkpoint1_role5_evaluation_readiness.md](file:///D:/K4_Day10_C6_1/data/eval/checkpoint1_role5_evaluation_readiness.md), toàn bộ 24 tài liệu được làm sạch đều có trường `categories_joined` rỗng.
- **Hệ quả:**
  Vai trò 5 (Evaluation Owner) không thể thiết kế các câu hỏi kiểm tra dạng phân loại hoặc lọc theo category học thuật cho RAG Agent.
- **Giải pháp đề xuất:**
  Ở pha Ingestion/Cleaning tiếp theo hoặc khi nâng cấp hệ thống, cần cấu hình parser để trích xuất trường `subject` hoặc `container-title` từ API Crossref và lưu vào `categories_joined`. Trong ngắn hạn, chúng tôi chấp nhận loại bỏ câu hỏi category khỏi bộ đánh giá để giữ tính công bằng.

---

## 3. Kế hoạch cho Checkpoint tiếp theo

Sau khi kết thúc thời gian nghỉ ngơi tại Checkpoint 4, vai trò Lead sẽ điều phối các thành viên thực hiện các công việc của Checkpoint 5 và Checkpoint 6:
1. **Pha lỗi dữ liệu (Data Corruption)**: Kích hoạt hàm `corrupt_clean_dataframe` để làm hỏng dữ liệu một cách có chủ đích, ghi nhật ký lỗi dữ liệu ra `data/results/corruption_log.json`.
2. **Đánh giá lại (Re-evaluate)**: Chạy thử nghiệm RAG trên tập dữ liệu lỗi và so sánh với baseline.
3. **Phục hồi (Repair)**: Viết logic tải lại dữ liệu thô đáng tin cậy ban đầu và re-clean để khôi phục chỉ số metrics.
4. **Tạo báo cáo so sánh**: Tự động hóa việc tổng hợp kết quả so sánh Baseline - Corrupted - Repaired vào [corruption_report.md](file:///D:/K4_Day10_C6_1/data/reports/corruption_report.md).
