# Giải thích nhiệm vụ của Vai trò 4 (Role 4: RAG & Agent)

Dựa trên cấu hình phân công nhóm, **Vai trò 4** đảm nhận vị trí **"RAG & Agent người phụ trách"**. 
Phạm vi trách nhiệm chính của bạn xoay quanh việc xây dựng hệ thống truy xuất (RAG), tạo embeddings (MiniLM), quản lý vector database (Chroma), và xây dựng Agent để trả lời câu hỏi dựa trên dữ liệu. Khu vực code chính: `src/retrieval/` và thư mục `data/embeddings/`.

Dưới đây là chi tiết công việc bạn cần làm theo từng giai đoạn (Checkpoints):

## 1. Checkpoint 0 (00:00–00:30): Khởi động & Contract
- **Đọc code hiện có:** Đọc các file liên quan đến `LocalEmbeddingIndex`, `embeddings`, và `agent` trong `src/retrieval/` để hiểu rõ dữ liệu đầu vào (input) hệ thống cần và kết quả đầu ra (output) mong đợi.
- **Thống nhất cấu hình:** Quyết định sẽ dùng embedding model nào (vd: MiniLM), đặt tên cho Chroma collection là gì (vd: `papers-baseline`), và chốt các trường metadata tối thiểu cần thiết để đưa vào index.
- **Chuẩn bị Test:** Lên sẵn một vài câu truy vấn (smoke query/lookup) để chuẩn bị test hệ thống ngay khi có dữ liệu.

## 2. Checkpoint 1 (00:30–01:05): Cleaning & Data Model
- **Kiểm tra dữ liệu Clean:** Đọc thử vài dòng dữ liệu trường `text_for_embedding` (do team Clean làm) để đảm bảo nó đủ thông tin (có title, summary), không bị rỗng hay lặp vô ích.
- **Xác nhận Schema:** Đảm bảo dataframe được bàn giao chứa đủ các cột cần thiết cho việc index: `paper_id`, `title`, `content` (text_for_embedding) và metadata.
- **Chuẩn bị cấu hình Index:** Thiết lập trước đường dẫn đọc file data clean, sẵn sàng để build collection (nhưng chưa build chính thức).

## 3. Checkpoint 2 (01:05–01:35): Test set, RAG index & Agent smoke test
- **Xây dựng Index (Baseline):** Chạy hàm để tạo ra MiniLM embeddings và build Chroma collection gốc có tên như `papers-baseline` từ file data sạch.
- **Test chức năng truy xuất:** Chạy thử `semantic_search` và exact `lookup` với các query đã chuẩn bị ở CP0 để xem hệ thống trả về đúng tài liệu không.
- **Xây dựng Agent:** Build Agent và yêu cầu nó sử dụng tool tìm kiếm trước khi trả lời các sự kiện (factual), đồng thời kiểm tra xem tool output có chính xác không.

## 4. Checkpoint 3 (01:35–02:00): Baseline end-to-end & Báo cáo
- **Nghiệm thu Baseline:** Xác nhận lại rằng collection `papers-baseline` và embedding manifest hoàn toàn khớp với file clean dataset ban đầu.
- **Demo chức năng:** Trình bày (demo) cho team xem một lượt chạy `semantic_search` và một lượt `exact lookup` thành công.
- **Kiểm tra độ chính xác của Agent:** Xác minh rằng câu trả lời của Agent hoàn toàn dựa trên kết quả của tool, không tự ảo giác ngoài tập dữ liệu (corpus).

## 5. Checkpoint 4 (02:00–02:15): Nghỉ 15 phút
- Lưu lại một vài câu truy vấn mẫu ở phần Baseline để dùng đối chiếu sự khác biệt ở giai đoạn sau.

## 6. Checkpoint 5 (02:15–03:15): Corruption có kiểm soát
- **Build Index lỗi:** Xây dựng một collection riêng (vd: `papers-corrupted`) từ bộ dữ liệu đã bị làm hỏng có chủ đích (do team Clean cung cấp).
- **So sánh kết quả:** Chạy lại các câu query mẫu chuẩn và quan sát xem kết quả truy xuất bị sai lệch, giảm chất lượng như thế nào.
- **Bảo vệ Baseline:** Chắc chắn rằng collection cũ `papers-baseline` vẫn còn nguyên vẹn, đọc được và không bị ghi đè.

## 7. Checkpoint 6 (03:15–04:00): Repair, Comparison & Demo
- **Build Index phục hồi:** Xây dựng collection cuối cùng (vd: `papers-repaired`) từ bộ dữ liệu đã được phục hồi.
- **Test lại hệ thống:** Dùng lại các query mẫu để smoke test, đảm bảo Agent và hệ thống truy xuất đã trả về đúng document cần thiết.
- **Demo tổng kết:** Trình bày cho team thấy rõ 3 collection tách biệt (`baseline`, `corrupted`, `repaired`), chạy demo để thấy chất lượng của Agent phụ thuộc thế nào vào dữ liệu nguồn.
