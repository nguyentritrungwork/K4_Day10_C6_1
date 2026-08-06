# Team 6 Workflow — Data Pipeline Lab

## Mục tiêu

Tài liệu này trình bày flow làm việc rõ ràng cho nhóm 6 người: ai làm gì, khi nào, và cách các thành viên phối hợp qua từng giai đoạn.

## Thành viên và vai trò

- **Lead / Integrator**: điều phối, QA, demo, đảm bảo team tuân thủ contract và artifact.
- **Ingest**: lấy raw source, parse Crossref, lưu raw artifact, giữ lineage.
- **Clean**: chuyển raw → clean, chuẩn hóa schema, tính `text_for_embedding` và `age_days`.
- **RAG**: tạo embedding, xây dựng collection, kiểm tra semantic search và lookup.
- **Eval**: tạo test set, chạy evaluator, lưu answers và metrics.
- **Observe**: kiểm tra quality/freshness, tạo báo cáo baseline/corrupted/repaired.

## Flow chính cho team 6

### Giai đoạn 1 — Chuẩn bị và phân công (CP0)

1. Mục tiêu: xác định rõ artifact, contract, và ownership.
2. Lead và cả team đọc kỹ yêu cầu bài lab.
3. Ingest kiểm tra raw source, xác nhận payload có field cần thiết.
4. Clean xác định schema clean và điều kiện loại/dedupe.
5. RAG chọn model embedding, collection naming, metadata bắt buộc.
6. Eval định nghĩa cấu trúc test set và ground truth.
7. Observe liệt kê tín hiệu quality/freshness cần theo dõi.
8. Kết quả: branch, artifact path, contract giai đoạn, và list task rõ ràng.

### Giai đoạn 2 — Xây baseline clean & quality gate (CP1)

1. Ingest giữ raw artifact: raw records, raw response, stable `paper_id`.
2. Clean chạy sơ bộ clean pipeline, chuẩn hóa title/summary/authors/categories.
3. Clean thực hiện dedupe, tính `age_days`, tạo `text_for_embedding`.
4. Lead kiểm tra raw → clean count và ghi lý do lọc/dedupe.
5. Observe xây quality gate: row count, duplicate, missing title/summary.
6. Quy tắc: không bắt đầu test set/index nếu clean schema chưa ổn.

### Giai đoạn 3 — Tạo test set và xây RAG baseline (CP2)

1. Clean xác nhận clean data ổn, không trùng, không thiếu `text_for_embedding`.
2. Eval xây test set cố định từ clean data, chọn question/ground truth có thể kiểm chứng.
3. RAG tạo embedding và collection `papers-baseline` riêng.
4. RAG chạy smoke test: semantic search và exact lookup phải trả kết quả hợp lệ.
5. Lead kiểm tra các collection/path riêng, tránh ghi đè baseline.
6. Observe ghi baseline signals và audit metadata của collection.

### Giai đoạn 4 — Chạy baseline end-to-end và báo cáo (CP3)

1. Lead chạy entrypoint baseline (`script/run_phase1.py` hoặc tương đương).
2. Ingest, Clean, RAG, Eval, Observe đồng bộ để kiểm tra artifact cuối.
3. Eval tạo `answers`, `baseline_metrics.json` và kiểm tra hit/miss.
4. Observe tạo report quality/freshness và đối chiếu với JSON/CSV.
5. Lead kiểm tra mọi sản phẩm có thực tế và đúng đường dẫn.
6. Kết quả: baseline artifacts + phase1 report + evidence rõ ràng.

### Giai đoạn 5 — Nghỉ và chuẩn bị corruption (CP4)

1. Cả team nghỉ 15 phút.
2. Lead ghi checklist baseline, remaining blocker và scenario corruption.
3. Cả team xác định corruption intent rõ: lỗi nào, ảnh hưởng gì, cách repair.
4. Kết quả: plan corruption, artifact path riêng, không xóa baseline.

### Giai đoạn 6 — Corruption và đo impact (CP5)

1. Clean tạo corrupted clean dataset mới với corruption có chủ đích.
2. RAG xây collection `papers-corrupted` riêng từ corrupted data.
3. Eval dùng test set cũ để chạy corrupted answers và metrics.
4. Observe chạy quality/freshness cho corrupted dataset.
5. Lead giám sát: corrupted output phải tách riêng, block nếu baseline bị mutate.
6. Kết quả: corrupted artifacts, metrics, quality reports và comparison notes.

### Giai đoạn 7 — Repair, comparison và demo (CP6)

1. Clean tạo repair dataset từ raw source, không sao chép tay từ baseline.
2. RAG xây collection `papers-repaired` riêng và chạy smoke test.
3. Eval chạy test set cũ trên repaired dataset và thu repaired metrics.
4. Observe tạo comparison report giữa baseline/corrupted/repaired.
5. Lead kiểm tra tình trạng secret/.env, hard-coded path và xác nhận demo artifact thật.
6. Kết quả: final report, demo evidence, lessons learned.

## Quy tắc làm việc chung

- Luôn dùng paths/collections riêng cho baseline, corrupted, repaired.
- Giữ test set và evaluator cố định khi so sánh các trạng thái.
- Repair từ raw, không sửa tay outputs.
- Báo cáo phải trỏ tới artifact thật; không dùng số liệu ước lượng.
- Mỗi checkpoint cần rõ ai làm gì, ai chờ gì, và blocker nếu có.

## Mô hình giao tiếp nhanh trong team

- Trước mỗi checkpoint: cập nhật ngắn `Ai đang làm gì`, `Ai chờ gì`, `Blocker`, `Next step`.
- Ai xong task báo `ready` kèm artifact path.
- Ai gặp issue báo ngay để Lead điều phối.
- Ai chậm hay phụ thuộc data khác phải ghi rõ dependency.

## Recommended Checkpoint Board

| Checkpoint | Lead                    | Ingest               | Clean              | RAG             | Eval             | Observe         |
| ---------- | ----------------------- | -------------------- | ------------------ | --------------- | ---------------- | --------------- |
| CP0        | Contract + ownership    | Raw source           | Clean schema plan  | Embedding plan  | Test set plan    | Signals list    |
| CP1        | Gate + count review     | Raw artifact ready   | Clean artifact     | Index plan      | Draft test set   | Quality gate    |
| CP2        | Handoff baseline        | Raw/clean validation | Clean validation   | Baseline build  | Test set fixed   | Audit signals   |
| CP3        | Run baseline            | Artifact check       | Schema/clean check | Smoke test      | Baseline metrics | Baseline report |
| CP4        | Pause + plan corruption | Snapshot confirm     | Corruption design  | Corruption path | Test set reuse   | Impact forecast |
| CP5        | Monitor corruption      | Source lineage       | Corrupt dataset    | Corrupt index   | Corrupt metrics  | Corrupt report  |
| CP6        | Final comparison        | Raw restore          | Repaired dataset   | Repaired index  | Repaired metrics | Final report    |

---

_Tài liệu này dành cho nhóm 6, giúp chia flow rõ ràng ở mức giai đoạn và vai trò._
