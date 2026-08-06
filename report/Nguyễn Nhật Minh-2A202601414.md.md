# Member Role Report — Day 10: Data Pipeline & Data Observability

> Mỗi thành viên trong nhóm tự hoàn thành mẫu này để báo cáo đúng vai trò, phần việc và mức hiểu của mình. Không sao chép nguyên báo cáo chung hoặc báo cáo của thành viên khác. Thay nội dung trong dấu `[ ]` và xóa các dòng hướng dẫn không cần thiết trước khi nộp.

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Nhật Minh             |
| MSSV               | 2A202601414                     |
| Khóa/Lớp         | K4              |
| Tên nhóm         | Nhóm C6_1     |
| Vai trò chính    | Vai trò 4 (RAG & Agent owner)                 |
| Repository         | K4_Day10_C6_1 |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Quản lý Vector Database (Chroma) | `src/retrieval/index.py` | `papers_clean.json`, `papers_clean_corrupted.json`, `papers_clean_repaired.json` | 3 tập index: `papers-baseline`, `papers-corrupted`, `papers-repaired` | Hoàn thành |
| Agent Tools (Semantic Search, Lookup) | `src/retrieval/agent.py` | Câu truy vấn của người dùng, Index tương ứng | Kết quả documents truy xuất từ ChromaDB | Hoàn thành |
| Báo cáo khác biệt Retrieval | `script/demo_role4_cp*.py` | Các index baseline, corrupted, repaired | Script kiểm thử tự động, log kết quả chạy | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Cung cấp script demo Agent RAG để đánh giá lỗi | Role 3 (Cleaning/Corruption) | Đưa ra bằng chứng rõ rệt việc dữ liệu lỗi ảnh hưởng trực tiếp đến câu trả lời RAG (Score tụt, thiếu sót). |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Tạo Baseline Index | `demo_role4_cp3.py` | `papers_embeddings.json` và collection `papers-baseline` (24 docs) | Chạy thử truy vấn search, lookup và nhận kết quả đúng. |
| Tạo Corrupted Index | `demo_role4_cp5.py` | `papers_embeddings_corrupted.json` và collection `papers-corrupted` (23 docs) | Check output Agent, xác minh có bị loại bỏ mất 1 tài liệu. |
| Tạo Repaired Index | `demo_role4_cp6.py` | `papers_embeddings_repaired.json` và collection `papers-repaired` (24 docs) | Agent trả lời chuẩn xác trở lại trên dữ liệu phục hồi. |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

Đã phân lập thành công 3 index ChromaDB hoàn toàn riêng biệt không ghi đè lẫn nhau, giúp minh chứng thực nghiệm khả năng hoạt động của RAG Agent trên 3 trạng thái của dữ liệu từ chuẩn, nhiễu cho tới khi được sửa chữa.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Phần việc này giải quyết chặng cuối của luồng xử lý: chuyển đổi dữ liệu đã làm sạch thành vector, lưu vào cơ sở dữ liệu (ChromaDB) và cung cấp các công cụ cho LLM Agent. Thách thức cốt lõi là làm thế nào cách ly các trạng thái dữ liệu (baseline, corrupted, repaired) vào các collection riêng biệt để có thể đánh giá và so sánh mức độ ảnh hưởng của dữ liệu rác đến RAG.

### Cách triển khai

Tôi đã tinh chỉnh hàm `LocalEmbeddingIndex.build()`, ứng dụng logic phân nhánh `embeddings_output_path`. Logic này sinh ra các `collection_name` khác nhau và lưu tương ứng ra 3 file manifest JSON. Ở các file test `demo_role4_cp*.py`, script sẽ nạp dữ liệu từ các bước trước, dùng `HuggingFaceEmbeddings` để nhúng vào collection tương ứng. Sau đó khởi chạy mô hình LLM cùng Agent, giả lập các câu truy vấn cố định để đối chiếu retrieval hit và text generated.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | `df` (DataFrame dữ liệu JSON) và `settings` cấu hình hệ thống |
| Output                         | Persistent Collection trong ChromaDB, file Manifest `.json` |
| Module phụ thuộc             | `ingestion.cleaning` (nguồn dataframe), `core.config` |
| Module sử dụng output        | `retrieval.agent` (Agent Tool RAG), Evaluation Module |
| Điều kiện lỗi cần xử lý | Lỗi file input không tồn tại, tự động copy fallback hoặc báo lỗi log chi tiết. |

### Cách xác minh

```bash
uv run python script/demo_role4_cp5.py
```

- **Kết quả mong đợi:** Collection `papers-corrupted` được sinh ra, báo cáo 23 documents, truy vấn bị báo lỗi hoặc thay đổi thứ hạng rank so với baseline.
- **Kết quả thực tế:** `papers-corrupted` có 23 documents, truy vấn thay đổi score, tóm tắt Agent bị ảnh hưởng bởi lỗi nhiễu từ điển.
- **Artifact/log:** In ra console log terminal của Checkpoint 5.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần xây dựng và truy vấn nhiều phiên bản dữ liệu (baseline, corrupted) trên cùng một database Chroma mà không làm hỏng dữ liệu gốc.
- **Các phương án đã cân nhắc:** (1) Xóa và nạp lại DB mỗi khi test. (2) Đặt tên collection khác nhau và lưu path riêng.
- **Phương án đã chọn:** Đặt tên collection khác nhau và lưu manifest path riêng.
- **Lý do:** Trade-off: Giúp team so sánh trực tiếp, có tính reproducibility (tái lập) cao, ngăn ngừa ghi đè (mutate baseline) dù tốn thêm chút chi phí lưu trữ.
- **Bằng chứng quyết định phù hợp:** Script hiển thị rõ ràng 3 manifest JSON và 3 collections chạy độc lập trong DB.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `Lỗi khi load LocalEmbeddingIndex baseline: Collection [papers-baseline] does not exist`
- **Lệnh hoặc bước tái hiện:** Chạy lại `uv run python script/demo_role4_cp5.py` sau khi reload môi trường server.
- **Nguyên nhân gốc:** Trạng thái ChromaDB bị xóa hoặc một module khác (như Phase 1 reset) đã reset toàn bộ database, dẫn tới tập baseline biến mất.
- **Cách xử lý:** Gọi lại script sinh data pipeline chuẩn từ đầu (`run_phase1.py`) để nạp lại collection baseline.
- **Cách xác minh sau khi sửa:** Chạy lại file script CP5 báo thành công.
- **Điều học được:** Database Vector Persistent cần cẩn trọng với các thao tác overwrite của các tiến trình chạy chung thư mục. Luôn phải có quy trình build baseline sẵn sàng.

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?** Dữ liệu raw từ Crossref được nạp qua module ingestion, được làm sạch (loại bỏ HTML, null), định dạng lại thành JSON và truyền qua mô hình Embedding biến văn bản thành vector, lưu vào ChromaDB.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?** Evaluation set chứa các câu hỏi tương ứng với ID tài liệu đích thực. Nó giúp đối chiếu xem khi Agent chạy tìm kiếm, nó có lấy ra đúng ID bài báo đó hay không (Hit Rate), qua đó đo lường hiệu suất retrieval.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?** Quality checks kiểm tra giá trị dữ liệu (rỗng, kiểu dữ liệu sai, bất thường logic schema). Freshness monitor kiểm tra xem thời gian update dữ liệu có quá cũ so với ngưỡng hay không (sự lỗi thời).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?** Để bảo đảm độ công bằng và tính đối chứng. Nếu thay đổi bài thi thì sự chênh lệch điểm số không còn phản ánh được do chất lượng dữ liệu bị lỗi nữa.
5. **Repair được xem là thành công dựa trên artifact và metric nào?** Dựa trên Freshness/Quality report trở về trạng thái "Pass" và chỉ số của Evaluation metric (Hit Rate, F1) phải phục hồi ngang bằng kết quả baseline.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      Tốt |       Giảm |      Tốt | Trực tiếp sụt giảm do tài liệu lỗi hoặc bị xóa bỏ. |
| `mean_token_f1`      |      Tốt |       Thấp |      Tốt | Phản ánh hiện tượng hallucination ở corrupted. |
| `judge_accuracy`     |      Cao |       Thấp |      Cao | Trạng thái lỗi bị LLM Judge bắt gặp khá chính xác. |
| `mean_judge_score`   |      Cao |       Giảm |      Cao | Điểm số đánh giá tổng hợp sụt giảm. |
| Quality checks         |      Pass |       Fail |      Pass | Bản lỗi vi phạm schema rành rành. |
| Freshness status       |      Pass |       Stale |      Pass | Dữ liệu lỗi mô phỏng không có ngày tháng. |

### Kết luận từ số liệu

Hoàn thành hai chuỗi nguyên nhân–bằng chứng sau:

1. Dữ liệu bị xóa/nhiễu (Data corruption) → Lỗi schema/rỗng (quality signal fail) → Truy xuất sót tài liệu, Agent tóm tắt thiếu ý (agent metric giảm).
2. Tái tạo lại từ raw (Repair action) → Vượt qua kiểm tra (quality signal phục hồi) → Trả lời đúng trọng tâm trở lại (agent metric phục hồi).

Corruption nào ảnh hưởng rõ nhất và vì sao?

Việc "Drop document" (xóa ngẫu nhiên bài báo) ảnh hưởng nghiêm trọng nhất so với làm nhiễu chữ. Vì nếu tài liệu không tồn tại ở index thì Tool lookup sẽ ném Exception ngay lập tức và Agent hoàn toàn mù tịt.

Kết quả nào khác với kỳ vọng ban đầu?

Việc làm nhiễu từ ngữ (noise) trong nội dung không làm mất khả năng tìm kiếm của Semantic Search bằng Vector, hệ thống vẫn lôi ra được bài báo (chỉ giảm score). Điều này chứng minh sức mạnh của Embedding Model vượt trội hơn Keyword Search.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Quy trình RAG (Retrieval-Augmented Generation) phụ thuộc cực kỳ lớn vào chất lượng Data Foundation: "Garbage in, Garbage out".
2. Khả năng kháng lỗi tuyệt vời của Vector Embeddings đối với lỗi đánh máy/chính tả từ tài liệu thô.
3. Việc cách ly cấu trúc lưu trữ của các tập Index dữ liệu là yếu tố then chốt giúp cho việc quan sát, đối chiếu ở các vòng đời phát triển trở nên dễ dàng.

### Nếu có thêm thời gian

Tôi sẽ cài đặt cơ chế **Auto-Rollback** cho ChromaDB. Khi Quality Check phát hiện data lỗi, script tự động giữ nguyên collection bản cũ thay vì cho ghi đè hay thay thế, đo đạc qua thời gian uptime (không bị down dịch vụ RAG).

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Nhật Minh
**Ngày xác nhận:** 2026-08-06
