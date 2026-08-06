# Checkpoint 1 - Vai trò 5: Evaluation Owner

## Phạm vi

Nhóm 6 người, vai trò 5 phụ trách evaluation. Ở checkpoint 1, mục tiêu chưa phải khóa `test_set.json`, mà là xác minh cleaned data đã đủ điều kiện để tạo evaluation set ở checkpoint 2.

## Artifact đã kiểm tra

- Cleaned CSV: `data/clean/papers_clean.csv`
- Cleaned JSON: `data/clean/papers_clean.json`
- Raw records: `data/raw/crossref_records.json`
- Raw response: `data/raw/crossref_response.json`

## Kết quả kiểm tra cleaned data

| Hạng mục | Kết quả |
| --- | --- |
| Số paper sạch | 24 |
| Thiếu cột bắt buộc | Không |
| `paper_id` rỗng | 0 |
| `paper_id` trùng | 0 |
| `title` rỗng | 0 |
| `summary` rỗng | 0 |
| `authors_joined` rỗng | 0 |
| `published` rỗng | 0 |
| `age_days` rỗng | 0 |
| `text_for_embedding` rỗng | 0 |
| `categories_joined` rỗng | 24 |
| Summary ngắn hơn 200 ký tự | 0 |
| Độ dài summary trung bình | 1727.42 ký tự |
| Summary ngắn nhất | 826 ký tự |
| Summary dài nhất | 2610 ký tự |

## Kết luận checkpoint 1

Cleaned data đủ điều kiện để vai trò 5 tạo evaluation set ở checkpoint 2.

Điểm cần lưu ý: `categories_joined` đang rỗng toàn bộ, nên không nên tạo câu hỏi loại `categories` cho test set chính thức, trừ khi vai trò cleaning bổ sung được category thật.

## Contract cần giữ cho checkpoint 2

- Dùng `paper_id` làm document ID trong `ground_truth_doc_ids`.
- Không đổi cách tạo `paper_id` sau khi đã tạo `test_set.json`.
- Chỉ tạo câu hỏi từ `data/clean/papers_clean.csv` hoặc `data/clean/papers_clean.json`.
- Không tạo câu hỏi từ raw data.
- Sau khi tạo `data/eval/test_set.json`, phải dùng cùng test set cho baseline, corrupted và repaired.

## Paper ứng viên tốt cho test set

| `paper_id` | Loại câu hỏi nên dùng | Lý do chọn |
| --- | --- | --- |
| `10-21203-rs-3-rs-10012178-v1` | summary, authors, date | Summary dài, title rõ, có author và ngày publish |
| `10-1093-sleep-zsag091-0346` | summary, authors, date | Nội dung sleep medicine rõ, metadata đầy đủ |
| `10-32473-flairs-39-1-141782` | summary, authors, date | Nội dung mental health + agentic RAG rõ |
| `10-3390-buildings16132637` | summary, authors, date | Nội dung roof compliance rõ, summary dài |
| `10-21203-rs-3-rs-10178277-v1` | summary, authors, date | Nội dung forecasting rõ, metadata đầy đủ |

## Câu hỏi nháp cho checkpoint 2

Các câu dưới đây chỉ là bản nháp, chưa phải test set chính thức.

1. What is the main purpose of "Retrieval-Augmented Generation (RAG), Generative AI, and Agentic AI Governance: An Integrated Enterprise Governance Prioritization Architecture"?
   - `question_type`: summary
   - `ground_truth_doc_ids`: [`10-21203-rs-3-rs-10012178-v1`]

2. Who authored "0346 Retrieval Augmented Generation Improves Large Language Model Performance in Sleep Medicine"?
   - `question_type`: authors
   - `ground_truth_doc_ids`: [`10-1093-sleep-zsag091-0346`]

3. When was "An Exploratory Study of Agentic Retrieval Augmented Generation for Mental Health Oriented Language Models" published?
   - `question_type`: date
   - `ground_truth_doc_ids`: [`10-32473-flairs-39-1-141782`]

4. What is the main application domain of "An Agentic AI System for Roof Design Compliance Using Computer Vision, Retrieval-Augmented Generation and Large Language Models"?
   - `question_type`: summary
   - `ground_truth_doc_ids`: [`10-3390-buildings16132637`]

5. What does the paper "Retrieval-Augmented Large-Language-Model-Based Time-Series Forecasting for Cross-Market Equity Analysis" evaluate?
   - `question_type`: summary
   - `ground_truth_doc_ids`: [`10-21203-rs-3-rs-10178277-v1`]

## Blocker / rủi ro

- Không có blocker nghiêm trọng cho checkpoint 1.
- Rủi ro nhỏ: category rỗng toàn bộ, nên bỏ `categories` khỏi test set hoặc yêu cầu cleaning owner bổ sung categories thật.
- Không nên khóa test set nếu nhóm còn định thay đổi `paper_id`, filter row, hoặc regenerate cleaned data.

## Trạng thái bàn giao

Vai trò 5 sẵn sàng chuyển sang checkpoint 2 sau khi nhóm xác nhận cleaned data và `paper_id` sẽ không đổi.
