# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Trí Trung |
| MSSV               | 2A202601418 |
| Khóa/Lớp         | K4_E403 |
| Tên nhóm         | C6-1 |
| Vai trò chính    | Lead - Pipeline Integrator & Release Owner |
| Repository         | https://github.com/nguyentritrungwork/K4_Day10_C6_1.git |
| Ngày hoàn thành | 2026-08-06 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| **Pipeline Integration & Orchestration** | `src/pipelines/corruption_flow.py`<br>- `main()` | `Settings`, `baseline_metrics.json`, `papers_clean.json` | Chạy tích hợp hoàn chỉnh luồng: baseline -> làm lỗi -> đánh giá -> khôi phục dữ liệu gốc -> đánh giá lại -> xuất báo cáo. | Hoàn thành |
| **Orchestration Configuration** | `src/core/config.py`<br>`script/run_corruption_flow.py` | Biến môi trường hệ thống | Cấu hình tham số chạy pipeline, Collection Naming động và phân luồng chỉ mục. | Hoàn thành |
| **Release QA Checklist** | `report/cp6_role1_release_checklist.md` | Toàn bộ tệp tin artifacts | Báo cáo rà soát QA đường dẫn tuyệt đối, rò rỉ secrets, và đảm bảo khả năng tái lập. | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| **Debug tích hợp định dạng JSON Lines** | Vai trò 3 (Cleaning) & Vai trò 4 (RAG) | Khắc phục lỗi tương thích dữ liệu JSON Lines, đảm bảo pandas đọc/ghi ổn định trên cả máy chủ cục bộ và máy trạm khác. |
| **Đồng bộ hóa đường dẫn động (Paths)** | Cả nhóm | Chuẩn hóa lại cơ chế lấy thư mục gốc của project theo `Path(__file__).resolve()` động giúp xóa bỏ cảnh báo absolute path mã hóa cứng của máy cũ. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng và chạy Corruption Flow | `src/pipelines/corruption_flow.py` | Báo cáo so sánh tự động `data/reports/corruption_report.md` | Chạy lệnh `uv run python script/run_corruption_flow.py` |
| Rà soát QA phát hành cuối cùng | `report/cp6_role1_release_checklist.md` | Tuyên bố bàn giao sản phẩm sạch không secret, no hardcode path | Đọc báo cáo QA phát hành |

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Với tư cách là Lead / Pipeline Integrator, khó khăn lớn nhất là kết nối các khối độc lập (Ingestion của vai trò 2, Cleaning của vai trò 3, Indexing của vai trò 4, Evaluation của vai trò 5 và Observability của vai trò 6) thành một luồng end-to-end tự động chạy hoàn chỉnh. Rủi ro xảy ra khi các block không thống nhất về cấu trúc dữ liệu truyền nhận (data contract) hoặc đường dẫn thư mục, dẫn đến pipeline bị gãy (broken) giữa chừng.

### Cách triển khai
Tôi xây dựng logic tích hợp trong `corruption_flow.py`:
1. Nạp metrics baseline Pha 1 để làm điểm mốc.
2. Gọi module `corrupt_clean_dataframe` làm lỗi dữ liệu và lưu ra các tệp corrupted riêng.
3. Build chỉ mục ChromaDB riêng (`papers-corrupted`) và chạy RAG Agent trên dữ liệu lỗi sử dụng đúng test set gốc `test_set.json`.
4. Gọi `run_data_quality_checks` và `build_freshness_report` để thu thập dữ liệu giám sát của pha lỗi.
5. Gọi hàm repair (nạp raw records thô ban đầu, re-clean và build chỉ mục vector khôi phục `papers-repaired`).
6. Đánh giá lại hiệu năng trên chỉ mục phục hồi để lấy repaired metrics.
7. Gọi `generate_corruption_report` xuất báo cáo Markdown so sánh tự động.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| **Input** | `Settings` cấu hình hệ thống, `papers_clean.json` của baseline |
| **Output** | Các tệp JSON kết quả metrics/answers pha lỗi và phục hồi; báo cáo so sánh `corruption_report.md` |
| **Module phụ thuộc** | `src/ingestion/`, `src/retrieval/`, `src/evaluation/`, `src/observability/` |
| **Module sử dụng output** | Vai trò 6 dùng để lập báo cáo; toàn nhóm dùng để demo |
| **Điều kiện lỗi cần xử lý** | Lỗi định dạng JSON Lines khi đọc dữ liệu làm sạch trung gian |

### Cách xác minh

```bash
uv run python script/run_corruption_flow.py
```
- **Kết quả mong đợi:** Pipeline chạy từ đầu đến cuối thành công, in ra dòng chữ `"Corruption and repair flow complete."` và tạo lập đầy đủ các tệp kết quả trong thư mục `data/`.
- **Kết quả thực tế:** Chạy thành công 100%, không xảy ra bất kỳ lỗi runtime nào, tất cả các tệp metrics và báo cáo so sánh được sinh ra đầy đủ.
- **Artifact/log:** `data/reports/corruption_report.md` và `data/results/corrupted_metrics.json`.

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp lưu trữ dữ liệu dataset trung gian giữa các khối (Ingestion -> Cleaning -> Indexing).
- **Các phương án đã cân nhắc:**
  * **Phương án A:** Sử dụng một cơ sở dữ liệu quan hệ cục bộ (SQLite) để lưu trữ các bảng dữ liệu thô, dữ liệu sạch và dữ liệu lỗi.
  * **Phương án B:** Lưu trữ dưới dạng tệp phẳng (Flat files) JSON Lines và CSV trong thư mục dự án.
- **Phương án đã chọn:** **Phương án B (JSON Lines & CSV)**.
- **Lý do:** 
  * *Độ phức tạp thấp:* Tệp phẳng không yêu cầu thiết lập kết nối, quản lý phiên (sessions) hay viết mã lệnh SQL tương tác, giúp giảm thiểu tối đa lỗi runtime khi tích hợp.
  * *Git-friendly:* Dễ dàng theo dõi lịch sử thay đổi (lineage) trực tiếp bằng Git diff của văn bản thô.
  * *Dễ audit:* Người kiểm thử hoặc module kiểm soát chất lượng (Great Expectations) có thể dễ dàng đọc trực tiếp tệp để xác minh mà không cần cài đặt thêm client DB.
- **Bằng chứng quyết định phù hợp:** Tệp `papers_clean.json` và `papers_clean_corrupted.json` hoạt động ổn định xuyên suốt, ChromaDB nạp trực tiếp dữ liệu từ file JSON một cách mượt mà và không gặp lỗi tắc nghẽn IO.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  ValueError: Trailing data
  ```
  Xảy ra tại dòng `df_clean = pd.read_json(settings.paths.clean_json, orient="records")` khi khởi chạy pipeline.
- **Lệnh hoặc bước tái hiện:** Chạy `python script/run_corruption_flow.py` sau khi kéo code của nhóm về.
- **Nguyên nhân gốc:** Tệp `papers_clean.json` được ghi lại dưới dạng JSON Lines (mỗi dòng là một chuỗi JSON độc lập), nhưng hàm `pd.read_json` mặc định phân tích cú pháp theo định dạng JSON Array chuẩn. Việc thiếu tham số `lines=True` đã gây ra lỗi phân tích cú pháp.
- **Cách xử lý:** Bọc khối đọc dữ liệu trong `try-except` xử lý lỗi thông minh:
  ```python
  try:
      df_clean = pd.read_json(settings.paths.clean_json, orient="records")
  except ValueError:
      df_clean = pd.read_json(settings.paths.clean_json, lines=True)
  ```
- **Cách xác minh sau khi sửa:** Chạy lại pipeline, việc đọc file diễn ra trơn tru và tự động tương thích với cả 2 định dạng file JSON.
- **Điều học được:** Khi làm việc với dữ liệu JSON trung gian trong Python, luôn luôn phải kiểm soát chặt chẽ data contract về mặt cấu trúc tệp (JSON Array vs JSON Lines) và thiết lập cơ chế fallback dự phòng để nâng cao độ bền vững (robustness) của mã nguồn.

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   * Đầu tiên, API Crossref được gọi để lấy về danh sách các công trình nghiên cứu dưới dạng JSON thô (`raw response`) và được lọc/parse thành danh sách bản ghi thô chuẩn hóa (`raw records`).
   * Tiếp theo, dữ liệu thô được chuẩn hóa văn bản (tiêu đề, tóm tắt, tác giả), tính toán độ tuổi và ghép thành chuỗi tổng hợp `text_for_embedding`.
   * Cuối cùng, mô hình nhúng (`text-embedding-3-small`) mã hóa chuỗi văn bản này thành các vector số thực và lưu trữ vào chỉ mục cơ sở dữ liệu vector ChromaDB.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   * Bộ câu hỏi đánh giá cố định chứa các câu hỏi, câu trả lời chuẩn (`ground_truth`) và danh sách các ID tài liệu chính xác tương ứng (`ground_truth_doc_ids`).
   * **Đo lường truy xuất (Retrieval Quality):** Kiểm tra xem trong Top-k tài liệu mà RAG truy xuất về từ ChromaDB có chứa ID nằm trong `ground_truth_doc_ids` hay không (tính ra chỉ số `retrieval_hit_rate`).
   * **Đo lường câu trả lời (Answer Quality):** LLM Evaluator sẽ đối chiếu câu trả lời của Agent với câu trả lời chuẩn và chấm điểm chất lượng (từ 1 đến 5) kèm theo tính toán Token F1-score của văn bản.

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   * **Quality checks:** Giám sát chất lượng kỹ thuật của bộ dữ liệu tại một thời điểm cố định (như kiểm tra các giá trị null, trùng lặp ID, độ dài tối thiểu của tóm tắt, tính hợp lệ của schema).
   * **Freshness monitoring:** Giám sát độ mới theo dòng thời gian thực tế của các tài liệu học thuật (dựa trên ngày xuất bản chính thức `published` và số ngày tuổi `age_days` so với ngưỡng quy định 180 ngày).

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   * Vì đây là phương pháp kiểm soát biến số duy nhất. Để đo lường một cách khoa học tác động của lỗi dữ liệu (Data Corruption) và hiệu quả phục hồi (Repair), chúng ta phải giữ cố định bộ câu hỏi. Nếu dùng các test set khác nhau, các thay đổi về mặt metrics sẽ bị lẫn lộn giữa sự thay đổi về độ khó/cấu trúc của câu hỏi và sự thay đổi về chất lượng của dữ liệu.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   * **Artifact:** Dữ liệu làm sạch phục hồi (`papers_clean_repaired.json`) phải được tạo lại hoàn toàn từ dữ liệu thô gốc ban đầu. Tệp báo cáo [corruption_report.md](file:///d:/K4_Day10_C6_1/data/reports/corruption_report.md) phải được ghi nhận đầy đủ.
   * **Metric:** Chỉ số hiệu năng RAG (Token F1 và Judge Accuracy) của pha Repaired phải hồi phục về bằng hoặc xấp xỉ mức của Baseline ban đầu (phục hồi từ `0.9333` về `1.0`), đồng thời các lỗi kiểm tra chất lượng của pha Corrupted phải được xóa bỏ hoàn toàn (Pass: 10/10 checks).

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      1.0 |       1.0 |      1.0 | Không đổi vì Top-k vẫn đủ bao phủ tài liệu đúng |
| `mean_token_f1`      |      1.0 |    0.9333 |      1.0 | Giảm khi dữ liệu bị mất summary và khôi phục hoàn hảo |
| `judge_accuracy`     |      1.0 |    0.9333 |      1.0 | Phục hồi hoàn toàn về mức chính xác tối đa |
| `mean_judge_score`   |      5.0 |    4.7333 |      5.0 | Điểm LLM trung bình hồi phục về điểm tuyệt đối 5.0 |
| Quality checks         |   Pass-0 |    Fail-3 |   Pass-0 | Dữ liệu lỗi dính 3 lỗi chất lượng và đã sạch sau repair |
| Freshness status       |    Fresh |     Fresh |    Fresh | Dữ liệu lỗi ngày xuất bản cục bộ không làm stale toàn hệ thống |

### Kết luận từ số liệu

1. **Lỗi làm suy giảm RAG:** `blank_summary` làm mất đi trường tóm tắt của tài liệu `10-1007-s10278-026-02086-9` dẫn đến quality checks báo lỗi nghiêm trọng (`summary_missing`), trực tiếp làm Agent thiếu hụt thông tin để trả lời câu hỏi liên quan, kéo thấp chỉ số `mean_token_f1` và `judge_accuracy` của cả hệ thống xuống còn `0.9333`.
2. **Quy trình Repair hiệu quả:** Hành động repair nạp lại dữ liệu thô gốc và chạy làm sạch tự động giúp tái tạo lại trường tóm tắt sạch, khôi phục quality checks đạt 10/10 và đưa hiệu năng trả lời của RAG Agent hồi phục tuyệt đối về lại `1.0`.

* **Corruption ảnh hưởng rõ nhất và vì sao?**
  Lỗi làm rỗng tóm tắt (`blank_summary`) ảnh hưởng rõ nhất đến chất lượng câu trả lời của RAG Agent. RAG truy xuất ngữ cảnh dựa trên nội dung tài liệu nhúng; khi tóm tắt bị mất đi hoàn toàn, Agent không có thông tin chi tiết để tổng hợp câu trả lời factual, buộc LLM phải trả lời thiếu hoặc báo không tìm thấy, gây suy giảm trực tiếp metrics đánh giá.

* **Kết quả nào khác với kỳ vọng ban đầu?**
  Chỉ số `retrieval_hit_rate` vẫn giữ nguyên mức `1.0` ở cả 3 pha. Kỳ vọng ban đầu là khi dữ liệu bị lỗi, khả năng truy xuất đúng tài liệu sẽ giảm. Tuy nhiên, do chúng ta cấu hình RAG lấy `top_k = 4` tài liệu có điểm số cao nhất (trong khi bộ corpus nhỏ chỉ 24 bài báo), nên tài liệu ground truth bị làm lỗi vẫn lọt vào danh sách trích xuất của Agent, mặc dù nội dung tóm tắt bên trong của nó đã bị xóa trống.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. Thiết kế và duy trì một **data contract thống nhất** giữa các vai trò là nền tảng cốt lõi để tích hợp hệ thống RAG không bị lỗi runtime.
2. Việc thiết lập **Data Quality checks và Freshness monitoring tự động** là cực kỳ quan trọng để phát hiện sớm các hiện tượng lệch pha dữ liệu (data drift, data corruption) trước khi nó gây ảnh hưởng trực tiếp đến hiệu năng ứng dụng RAG.
3. Không thể cải thiện hiệu năng RAG nếu chỉ tập trung tối ưu hóa prompt hay mô hình LLM mà bỏ quên chất lượng của **nguồn dữ liệu đầu vào** (Garbage In, Garbage Out).

### Nếu có thêm thời gian
Tôi sẽ triển khai cơ chế **Chuẩn hóa Đường dẫn tương đối (Relative paths dynamic normalization)** cho manifest của ChromaDB để triệt tiêu hoàn toàn các cảnh báo về sai lệch thư mục chạy trên các hệ điều hành khác nhau, giúp cải thiện tối đa tính di động (portability) của pipeline.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Trí Trung
**Ngày xác nhận:** 2026-08-06
