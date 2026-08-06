# CP6 - Role 1: Release QA Checklist & Final Report

Báo cáo Checkpoint 6 (Kiểm định phát hành & Tổng kết cuối) của Vai trò 1 (Lead / Pipeline Integrator) trong bài lab xây dựng RAG Data Pipeline & Data Observability.

---

## 1. Release QA Artifact Checklist

Với tư cách là Lead chịu trách nhiệm kiểm định chất lượng cuối cùng (QA), tôi xác nhận toàn bộ các deliverables và artifacts của dự án đều đầy đủ, khớp số liệu và hợp lệ:

| Artifact | Vị trí kiểm tra | Trạng thái | Đánh giá tính khớp số liệu / Hợp lệ |
| :--- | :--- | :---: | :--- |
| **Dữ liệu Baseline** | `data/clean/papers_clean.json` | **Đầy đủ** | 24 dòng sạch. Khớp 100% với manifest. |
| **Dữ liệu Corrupted**| `data/clean/papers_clean_corrupted.json` | **Đầy đủ** | 23 dòng (đã drop 2, nhân đôi 1). Khớp log. |
| **Dữ liệu Repaired** | `data/clean/papers_clean_repaired.json` | **Đầy đủ** | 24 dòng (phục hồi nguyên bản). Khớp. |
| **Chỉ mục Baseline** | `data/embeddings/papers_embeddings.json` | **Đầy đủ** | Lập chỉ mục Chroma `papers-baseline` (24 docs). |
| **Chỉ mục Corrupted**| `data/embeddings/papers_embeddings_corrupted.json` | **Đầy đủ** | Lập chỉ mục Chroma `papers-corrupted` (23 docs). |
| **Chỉ mục Repaired** | `data/embeddings/papers_embeddings_repaired.json` | **Đầy đủ** | Lập chỉ mục Chroma `papers-repaired` (24 docs). |
| **Metrics Baseline** | `data/results/baseline_metrics.json` | **Đầy đủ** | F1: 1.0, Accuracy: 1.0, Judge Score: 5.0 |
| **Metrics Corrupted**| `data/results/corrupted_metrics.json` | **Đầy đủ** | F1: 0.9333, Accuracy: 0.9333, Judge Score: 4.7333 |
| **Metrics Repaired** | `data/results/repaired_metrics.json` | **Đầy đủ** | F1: 1.0, Accuracy: 1.0, Judge Score: 5.0 |
| **Observability** | Thư mục `data/quality/` | **Đầy đủ** | Chứa 8 file JSON reports của baseline, corrupted, repaired |
| **Báo cáo Pha 1** | `data/reports/phase1_report.md` | **Đầy đủ** | Thể hiện đúng thông số baseline trên máy hiện tại. |
| **Báo cáo so sánh** | `data/reports/corruption_report.md` | **Đầy đủ** | Thể hiện đúng bảng delta và so sánh 3 trạng thái. |

---

## 2. Rà soát bảo mật & Tái lập (Security & Reproducibility Audit)

### Tiêu chí 1: Không rò rỉ thông tin nhạy cảm (No Secrets Leak)
- **Kết quả kiểm tra:** **ĐẠT**
- **Mô tả:** Tệp cấu hình `.env` đã được liệt kê trong `.gitignore` và không bị đưa lên Git. Rà soát các tệp tin log trong thư mục `data/results/` và các báo cáo Markdown, xác nhận không chứa API keys hoặc thông tin nhạy cảm của OpenAI hay Google Gemini.

### Tiêu chí 2: Khả năng tái lập cao (Reproducibility & Paths Check)
- **Kết quả kiểm tra:** **ĐẠT**
- **Mô tả:** Sau khi chạy đồng bộ lại Phase 1 và Corruption Flow trên máy trạm hiện tại (`D:\K4_Day10_C6_1`), các báo cáo đã tự động cập nhật đường dẫn chính xác theo môi trường chạy thực tế của máy. Không còn đường dẫn tuyệt đối tĩnh mã hóa cứng của máy tính cũ. Hệ thống sẵn sàng chạy `uv run` hoặc `pip run` độc lập trên bất cứ thiết bị nào khác mà không gặp lỗi đường dẫn.

---

## 3. Tuyên bố Phục hồi và Kết luận

Số liệu so sánh thực tế tại [corruption_report.md](file:///d:/K4_Day10_C6_1/data/reports/corruption_report.md) đã chứng minh rõ ràng:
1. **Dữ liệu lỗi** làm suy giảm năng lực của RAG Agent (làm Token F1 và Judge Accuracy giảm xuống `0.9333`).
2. **Hành động Repair** (tải lại dữ liệu thô gốc và làm sạch tự động) đã khôi phục hoàn toàn 100% hiệu năng RAG về mức hoàn hảo ban đầu.

**Xác nhận sẵn sàng phát hành sản phẩm (Ready for Release).**
- **Người xác nhận:** Nguyễn Trí Trung (Lead / Pipeline Integrator)
- **Ngày ký nhận:** 2026-08-06
