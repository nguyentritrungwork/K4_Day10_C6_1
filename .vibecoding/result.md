# Kết quả: Chuẩn bị Script Test cho Checkpoint 2

Theo đúng mong muốn "tự test" của bạn, tôi đã không tự động chạy code mà thay vào đó đã tạo sẵn một file test script hoàn chỉnh cho Checkpoint 2. 

Bạn có thể tự chạy và kiểm chứng nghiệm thu Baseline, RAG index, cũng như Agent smoke test.

## Hướng dẫn Test
Tôi đã tạo file `script/test_cp2.py`. Script này sẽ:
1. Đọc dữ liệu từ `papers_clean.json` (kết quả của CP1).
2. Gọi `LocalEmbeddingIndex.build()` để tạo embeddings và lưu vào collection `papers-baseline` trên ChromaDB.
3. Test chức năng truy xuất với 1 paper cụ thể (`exact lookup`) và truy vấn ngữ nghĩa (`semantic_search`).
4. Khởi tạo Agent và đặt các câu hỏi factual (ví dụ: tác giả là ai, năm xuất bản) để kiểm tra xem Agent có dùng tool search không.

### Cách chạy:
Bạn hãy mở terminal trong thư mục gốc của project (nơi đã activate môi trường ảo, vd `.venv`) và chạy lệnh sau:

```bash
python script/test_cp2.py
```

Chúc bạn test thành công! Nếu có lỗi hay vấn đề gì trong lúc test, hãy báo lại để tôi hỗ trợ nhé.
