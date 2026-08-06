# Kế hoạch Triển khai Checkpoint 2: RAG Index & Agent Smoke Test

Dựa trên yêu cầu của Checkpoint 2 trong `role4.md`, tôi sẽ thực hiện các bước sau:

## 1. Xây dựng Index (Baseline)
Tôi sẽ tạo một script (hoặc cập nhật `src/pipelines/phase1.py`) để:
- Đọc file dữ liệu sạch từ `data/clean/papers_clean.json`.
- Sử dụng `LocalEmbeddingIndex.build()` để tạo embeddings bằng model `text-embedding-3-small` (như đã cấu hình ở CP0).
- Lưu metadata và embeddings vào ChromaDB (collection `papers-baseline`).

## 2. Test chức năng truy xuất (Retrieval Smoke Test)
Sau khi build xong, tôi sẽ chạy các câu lệnh test như đã lên cấu hình ở CP0:
- `semantic_search`: Thử tìm kiếm theo ngữ nghĩa (ví dụ: "papers about large language models").
- `exact lookup`: Tìm chính xác một bài báo bằng `title` hoặc `paper_id`.

## 3. Xây dựng Agent và Smoke Test
Tôi sẽ khởi tạo agent thông qua `build_agent()` trong `src/retrieval/agent.py`:
- Yêu cầu agent trả lời các câu hỏi dựa trên corpus vừa được index (ví dụ: "Who authored 'Speculative Retrieval-Augmented Generation for Cost-Efficient Large Language Model Inference'?").
- Kiểm tra xem agent có sử dụng tool `semantic_search_papers` hoặc `lookup_paper` trước khi trả lời hay không.

## 4. Báo cáo (Result)
- In ra console kết quả để dễ dàng theo dõi.
- Ghi lại log commit (nếu test thành công).

---
**Cần xác nhận:** Bạn vui lòng phản hồi `t=true` để tôi bắt đầu viết code và chạy test theo kế hoạch trên!
