# Báo cáo cá nhân - Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Văn Qúy |
| MSSV | 2A202601508 |
| Khóa/Lớp | K4 |
| Nhóm | Nhóm 6 người |
| Vai trò chính | Vai trò 5 - Evaluation Owner |
| Repository | Dự án Day 10 Data Pipeline & Data Observability |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

Trong nhóm 6 người, tôi đảm nhiệm vai trò 5: Evaluation Owner. Phạm vi chính của vai trò này là kiểm tra dữ liệu sạch có đủ điều kiện để tạo evaluation set, tạo test set cố định, kiểm tra baseline evaluation, và phân tích tác động của corrupted data lên kết quả đánh giá.

| Module/deliverable | File/artifact phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Evaluation readiness | `data/clean/papers_clean.csv`, `data/eval/checkpoint1_role5_evaluation_readiness.md` | Cleaned dataset từ vai trò cleaning | Báo cáo kiểm tra schema, `paper_id`, summary, `text_for_embedding` | Hoàn thành |
| Evaluation test set | `data/eval/test_set.json` | Cleaned dataset đã ổn định | 15 câu hỏi cố định cho baseline/corrupted/repaired | Hoàn thành |
| Test set summary | `data/eval/checkpoint2_role5_testset_summary.md` | `test_set.json` | Báo cáo cấu trúc test set và rule sử dụng | Hoàn thành |
| Baseline evaluation check | `data/results/baseline_metrics.json`, `data/results/baseline_answers.json` | Baseline index và test set | Báo cáo baseline evaluation | Hoàn thành |
| Corrupted impact analysis | `data/results/corrupted_metrics.json`, `data/results/corrupted_answers.json`, `data/results/corruption_log.json` | Corrupted artifacts và official metrics | Official corrupted evaluation summary và case bị ảnh hưởng | Hoàn thành |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | Artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Kiểm tra cleaned data trước khi tạo test set | `data/eval/checkpoint1_role5_evaluation_readiness.md` | Xác nhận 24 paper sạch, `paper_id` không trùng, không rỗng | Đối chiếu `data/clean/papers_clean.csv` |
| Tạo evaluation set chính thức | `data/eval/test_set.json` | 15 câu hỏi từ 5 paper thật, gồm `summary`, `authors`, `date` | Đọc JSON và kiểm tra `ground_truth_doc_ids` tồn tại |
| Ghi summary cho checkpoint 2 | `data/eval/checkpoint2_role5_testset_summary.md` | Mô tả số câu hỏi, loại câu hỏi, paper ID được dùng | Đối chiếu với `test_set.json` |
| Kiểm tra baseline metrics | `data/results/baseline_metrics.json` | Baseline đạt `retrieval_hit_rate = 1.0`, `mean_token_f1 = 1.0`, `judge_accuracy = 1.0` | Đọc metrics và answers |
| Phân tích corrupted impact | `data/eval/checkpoint5_role5_corrupted_evaluation_summary.md` | Tìm case `q12` bị ảnh hưởng do stale date | Đối chiếu `corruption_log.json` và corrupted data |

Output quan trọng nhất của tôi là `data/eval/test_set.json`. File này là bộ evaluation cố định để so sánh công bằng giữa baseline, corrupted và repaired.

## 4. Giải thích kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Pipeline RAG cần một bộ câu hỏi đánh giá cố định để đo chất lượng retrieval và answer. Nếu baseline, corrupted và repaired dùng các test set khác nhau thì metric không còn công bằng. Vì vậy phần việc của tôi tập trung vào việc tạo và giữ cố định test set dựa trên cleaned data thật.

### Cách triển khai

Tôi kiểm tra cleaned data trước khi tạo test set. Các điều kiện chính gồm: phải có `paper_id`, `title`, `summary`, `authors_joined`, `published`, `age_days`, `text_for_embedding`; `paper_id` không được rỗng hoặc trùng; summary và text embedding không được rỗng. Sau đó tôi chọn 5 paper có metadata đầy đủ để tạo 15 câu hỏi thuộc 3 loại: summary, authors và date.

Tôi không tạo câu hỏi `categories` vì `categories_joined` đang rỗng toàn bộ trong cleaned data. Đây là quyết định để tránh tạo ground truth yếu hoặc không có ý nghĩa.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | `data/clean/papers_clean.csv`, `data/clean/papers_clean.json` |
| Output | `data/eval/test_set.json` |
| Schema test set | `id`, `question_type`, `question`, `ground_truth`, `ground_truth_doc_ids` |
| Module phụ thuộc | Ingestion, cleaning, RAG index |
| Module sử dụng output | Baseline evaluation, corrupted evaluation, repaired evaluation |
| Điều kiện lỗi cần xử lý | Thiếu `paper_id`, `paper_id` trùng, ground truth rỗng, test set bị regenerate |

### Cách xác minh

Các artifact đã dùng để xác minh:

```bash
data/eval/test_set.json
data/results/baseline_metrics.json
data/results/baseline_answers.json
data/results/corruption_log.json
data/clean/papers_clean_corrupted.json
```

- Kết quả mong đợi: test set có đủ câu hỏi, ground truth không rỗng, document IDs tồn tại trong cleaned data.
- Kết quả thực tế: `test_set.json` có 15 câu hỏi, 5 paper ID thật, không có câu hỏi rỗng.
- Artifact/log: `data/eval/checkpoint2_role5_testset_summary.md`.

## 5. Một quyết định kỹ thuật quan trọng

- Bối cảnh: cleaned data có `categories_joined` rỗng toàn bộ.
- Các phương án đã cân nhắc: vẫn tạo câu hỏi categories với ground truth rỗng, hoặc bỏ categories khỏi test set.
- Phương án đã chọn: bỏ câu hỏi `categories`, chỉ dùng `summary`, `authors`, `date`.
- Lý do: câu hỏi category với ground truth rỗng sẽ làm metric không có ý nghĩa và có thể gây sai lệch đánh giá.
- Bằng chứng: trong checkpoint 1, `categories_joined` rỗng ở 24/24 paper; các trường `summary`, `authors_joined`, `published` đều có dữ liệu đầy đủ.

## 6. Một lỗi hoặc blocker đã xử lý

- Triệu chứng/blocker ban đầu: ở checkpoint 5 từng thiếu `data/results/corrupted_metrics.json` và `data/results/corrupted_answers.json`.
- Bước tái hiện: kiểm tra thư mục `data/results/` trước đó chỉ thấy baseline metrics/answers và corruption log.
- Nguyên nhân gốc: `corruption_flow.py` ở thời điểm trước chưa sinh official corrupted evaluation output.
- Cách xử lý: sau khi nhóm cập nhật flow, tôi kiểm tra lại official `corrupted_metrics.json` và `corrupted_answers.json`, sau đó cập nhật summary checkpoint 5.
- Cách xác minh: artifact `data/eval/checkpoint5_role5_corrupted_official_metrics.json` và `data/eval/checkpoint5_role5_corrupted_evaluation_summary.md`.
- Điều học được: evaluation owner cần cập nhật báo cáo theo artifact mới nhất và phân biệt rõ giữa phân tích tạm thời với official metrics từ pipeline.

## 7. Hiểu biết về luồng end-to-end

Dữ liệu đi từ Crossref API vào raw records, sau đó được cleaning để tạo cleaned dataset có `paper_id`, metadata và `text_for_embedding`. Từ cleaned dataset, nhóm build embedding và Chroma index để agent có thể search hoặc lookup tài liệu. Evaluation set dùng `ground_truth_doc_ids` trỏ về `paper_id` thật để kiểm tra retrieval có tìm đúng tài liệu không và answer có khớp ground truth không.

Quality checks tập trung vào tính hợp lệ của dữ liệu như thiếu field, duplicate, summary rỗng; freshness monitoring tập trung vào độ mới của dữ liệu, ví dụ ngày published có quá cũ không. Cùng một test set phải được dùng cho baseline, corrupted và repaired để metric phản ánh thay đổi do dữ liệu, không phải do bộ câu hỏi thay đổi. Repair được xem là thành công khi dữ liệu repaired được tạo lại từ raw/source đáng tin và metrics/quality signals phục hồi so với corrupted.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0 | 1.0 | 1.0 | Corrupted vẫn retrieve đúng document, nên hit rate không giảm |
| `mean_token_f1` | 1.0 | 0.9333 | 1.0 | Giảm do case `q12` bị stale date, repaired phục hồi |
| `judge_accuracy` | 1.0 | 0.9333 | 1.0 | Một câu date bị sai ở corrupted, repaired đúng lại |
| `mean_judge_score` | 5.0 | 4.7333 | 5.0 | Điểm trung bình giảm nhẹ rồi phục hồi |
| Quality checks | Valid | Invalid, 3 failed checks | Valid | Corrupted fail duplicate/summary checks, repaired pass lại |
| Freshness status | Fresh | Có oldest published năm 1999 do stale date | Fresh | Stale date ảnh hưởng rõ tới câu hỏi date |

### Kết luận từ số liệu

Chuỗi nguyên nhân - bằng chứng rõ nhất:

1. `stale_date` trên paper `10-3390-buildings16132637` làm `published` đổi từ `2026-07-02T00:00:00Z` sang `1999-07-02T00:00:00Z`.
2. Câu `q12` trong test set hỏi ngày publish của đúng paper này.
3. Official `corrupted_answers.json` cho thấy answer của `q12` là `1999-07-02T00:00:00Z`, khác ground truth baseline `2026-07-02T00:00:00Z`.
4. Official `corrupted_metrics.json` cho thấy `mean_token_f1`, `judge_accuracy`, `mean_judge_score` giảm so với baseline.

Kết quả khác kỳ vọng: một số corruption như drop latest, blank summary, truncate title chưa ảnh hưởng trực tiếp tới test set hiện tại vì các record đó không nằm trong 5 paper được chọn, hoặc câu hỏi vẫn lookup được theo title. Điều này cho thấy test set nên được thiết kế bao phủ cả record dự kiến bị corrupt nếu muốn chứng minh impact mạnh hơn.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Evaluation set phải dựa trên document ID thật và phải được giữ cố định để so sánh công bằng.
2. Không nên tạo ground truth từ field rỗng hoặc thiếu, vì metric sẽ mất ý nghĩa.
3. Data corruption không phải lúc nào cũng làm metric giảm mạnh; nó chỉ thể hiện rõ khi corruption tác động đến document hoặc field mà test set đang kiểm tra.

### Nếu có thêm thời gian

Tôi sẽ mở rộng test set để bao phủ nhiều loại corruption hơn, ví dụ thêm câu hỏi cho record bị blank summary, truncate title và dropped record. Khi đó phần so sánh `corrupted_metrics.json` và `repaired_metrics.json` sẽ phản ánh nhiều kiểu lỗi dữ liệu hơn, không chỉ stale date.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Văn Qúy  
**Ngày xác nhận:** 2026-08-06
