# Giải thích kết quả và Ý nghĩa các việc Role 4 làm trong CP0

Dưới đây là phần giải thích chi tiết về mặt kỹ thuật cho những nhiệm vụ mà Role 4 (RAG & Agent) cần nắm bắt trong Checkpoint 0, cũng như phân tích các đoạn code tương ứng.

---

## 1. Đọc `LocalEmbeddingIndex`, `embeddings`, `agent` để nắm Input/Output

### a. `embeddings.py` (Mô hình nhúng - Embedding)
- **Code làm gì?** File này định nghĩa class `MiniLMEmbeddings` bọc lại thư viện `sentence-transformers`.
- **Input/Output:**
  - Hàm `embed_documents(texts)`: Nhận vào một list các chuỗi văn bản (ví dụ: `text_for_embedding` của từng bài báo) và trả về một ma trận các vector nhúng (để lưu vào database).
  - Hàm `embed_query(text)`: Nhận vào câu hỏi của người dùng và chuyển thành 1 vector duy nhất để mang đi so sánh.
- **Ý nghĩa:** Đây là "bộ não" chuyển đổi ngôn ngữ tự nhiên thành các con số toán học (vector). Code sử dụng `@lru_cache` để đảm bảo mô hình (model) chỉ được tải lên bộ nhớ đúng 1 lần, giúp tiết kiệm RAM và tăng tốc độ.

### b. `index.py` (`LocalEmbeddingIndex` - Cơ sở dữ liệu Vector)
- **Code làm gì?** File này quản lý vòng đời của ChromaDB (tạo, lưu, tìm kiếm dữ liệu).
- **Quá trình Build (Input/Output):**
  - **Input:** Hàm `build()` nhận vào một `pd.DataFrame` (dữ liệu sạch từ bước trước).
  - **Xử lý:** Code duyệt qua DataFrame, nối các trường cần thiết thành `text_for_embedding` và trích xuất `metadata`. Sau đó đẩy toàn bộ vào ChromaDB (dùng cosine similarity).
  - **Output:** Trả ra đối tượng `LocalEmbeddingIndex` và lưu file `manifest.json` ghi lại thông tin database.
- **Quá trình Search & Lookup:**
  - Hàm `search(query, top_k)`: Dùng vector của câu hỏi để tìm `top_k` tài liệu gần giống nhất trong ChromaDB. Output là danh sách `SearchResult` (chứa `score`, `paper_id`, `content`). Điểm `score` được tính bằng `1.0 - distance` (distance càng nhỏ thì score càng cao).
  - Hàm `lookup(value)`: Tìm chính xác 1 bài báo dựa vào ID hoặc Tiêu đề (nhờ 2 dictionary `documents_by_paper_id` và `documents_by_title` được nạp sẵn lên RAM).

### c. `agent.py` (Tác tử LLM)
- **Code làm gì?** Tạo ra một Agent thông minh sử dụng LangChain.
- **Input/Output:**
  - Nó cung cấp cho LLM 2 công cụ (tools): `semantic_search_papers` (gọi hàm `search` của index) và `lookup_paper` (gọi hàm `lookup`).
  - LLM sẽ tự quyết định xem với câu hỏi của người dùng, nó nên dùng tool nào. Kết quả từ tool sẽ là Input để LLM tổng hợp ra Output cuối cùng.
- **Ý nghĩa:** System Prompt ép LLM: *"Use tools before answering factual questions"* (Phải dùng tool trước khi trả lời sự kiện thực tế). Điều này ngăn chặn tình trạng ảo giác (hallucination) của AI.

---

## 2. Chốt embedding model, collection naming và metadata

- **Embedding Model:** Chúng ta chốt sử dụng dòng họ `MiniLM` (ví dụ `all-MiniLM-L6-v2`) vì nó nhỏ, nhẹ, chạy được cục bộ (local) rất nhanh mà vẫn đảm bảo khả năng tìm kiếm ngữ nghĩa tiếng Anh tốt.
- **Collection Naming (Tên bộ sưu tập):**
  Trong hàm `_derive_collection_name`, hệ thống đã thiết kế sẵn việc đổi tên linh hoạt:
  - Dữ liệu sạch ban đầu: `papers-baseline`
  - Dữ liệu bị làm hỏng: `papers-corrupted`
  - Dữ liệu đã sửa lỗi: `papers-repaired`
  - *Ý nghĩa:* Việc tách tên collection giúp chúng ta lưu được cả 3 phiên bản database để so sánh ở CP6 mà không bị ghi đè lên nhau.
- **Metadata tối thiểu:** Code lấy `paper_id`, `title`, `published`, `authors_joined`, `categories_joined`, và `summary`.
  - *Ý nghĩa:* Bắt buộc phải có metadata này vì LLM không chỉ cần đọc text, mà file `qa.py` (phần Evaluation) còn dùng code Python cứng để bóc tách thông tin từ metadata (vd: khi hỏi "who authored...", nó bóc đúng trường `authors_joined` để so sánh với Ground Truth).

---

## 3. Chuẩn bị smoke query/lookup

Dựa vào hàm `_extract_answer` trong `qa.py`, chúng ta chuẩn bị sẵn các câu truy vấn mẫu (smoke query) sau khi index xong:
- **Câu hỏi Summary:** `What is the summary of '{title}'?`
- **Câu hỏi Authors:** `Who authored '{title}'?`
- **Câu hỏi Date:** `When was '{title}' published?`
- **Câu hỏi Categories:** `What categories does '{title}' belong to?`

*Ý nghĩa:* Đây là các câu hỏi "mồi" để chạy thử. Nếu database trả về kết quả đúng với những câu này, chứng tỏ luồng (pipeline) từ Raw -> Clean -> Embeddings đã thông suốt và sẵn sàng cho việc Đánh giá (Evaluation) tự động.
