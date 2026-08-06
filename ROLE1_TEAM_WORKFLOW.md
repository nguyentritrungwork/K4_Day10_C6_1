# Vai trò 1 và Flow làm việc của cả team

## 1. Mục tiêu của Vai trò 1
Vai trò 1 là người điều phối chính, đảm bảo team làm việc đúng hướng, giữ tiến độ qua từng checkpoint, và theo dõi tình trạng của các thành viên khác. Vai trò này không chỉ thực hiện một phần kỹ thuật cụ thể, mà còn kiểm soát giao diện giữa các phần ingestion, clean, retrieval, evaluation và observability.

### Trách nhiệm chính
- Định hướng tổng thể cho team và khóa scope của mỗi checkpoint.
- Xác nhận các điều kiện đầu vào / đầu ra của từng giai đoạn.
- Theo dõi tiến độ, phát hiện blocker và chuyển tiếp thông tin nhanh.
- Kiểm tra artifact đầu ra của các nhóm con để tránh sai lệch hoặc trùng lặp.
- Chuẩn bị demo, báo cáo và đảm bảo team dùng dữ liệu thật, không dùng số liệu giả.

## 2. Công việc của Vai trò 1 theo từng checkpoint

### CP0 — Khởi động, contract & ingestion raw
- Chốt ownership/branch và `definition of done` cho từng thành viên.
- Kiểm tra Python, dependency, provider config và `.env` của cả nhóm.
- Đảm bảo ingest/clean đã có raw sample rõ ràng và path artifact stable.
- Theo dõi: ai chịu trách nhiệm raw ingestion, ai chịu trách nhiệm clean schema.
- Ghi lại blocker nếu còn thiếu artifact, contract hoặc source evidence.

### CP1 — Cleaning, data model & quality gates
- Khóa clean contract: input, output, tên file và điều kiện dừng.
- Đếm raw/clean và ghi sơ bộ lý do filter/dedupe để cả team nắm.
- Giữ team không bắt đầu test set/index trước khi schema clean ổn định.
- Theo dõi: ingest/clean đã có output clean đọc được chưa.
- Kiểm tra count record và lý do loại giữa raw và clean.
- Nhắc ai chậm hoặc có dependency cần báo ngay.

### CP2 — Test set, RAG index & agent smoke test
- Khóa schema clean và điều phối handoff sang test set/index.
- Đảm bảo baseline path riêng, dễ tái lập và không đè lên dữ liệu khác.
- Tập trung xử lý blocker trước khi chạy end-to-end.
- Theo dõi: clean data đã có text_for_embedding và paper_id ổn định chưa.
- Xác nhận rag/test set đã chọn được sample test đúng.
- Kiểm tra không ai đổi source giữa chừng làm baseline thay đổi.

### CP3 — Baseline end-to-end & báo cáo
- Chạy baseline entrypoint end-to-end và kiểm tra artifact cuối cùng.
- Ghi lại lỗi, traceback, và issuer nếu baseline không chạy sạch.
- Đảm bảo report và metrics khớp với artifact thực tế.
- Theo dõi: các thành viên đã xuất artifact đúng đường dẫn chưa.
- Yêu cầu mỗi thành viên trình bày ngắn hit/miss phần mình.
- So sánh số liệu thực tế với nội dung trong `phase1_report`.

### CP4 — Nghỉ 15 phút
- Ghi baseline checklist, status và blocker còn lại trước khi nghỉ.
- Chuẩn bị corruption scenario và plan repair dựa trên raw source.
- Xác nhận cả nhóm hiểu mục tiêu phần corruption.
- Theo dõi: mọi người nghỉ đủ, không vội quay lại.
- Lưu note hiện trạng artifact để tránh nhầm lẫn khi tiếp tục.

### CP5 — Corruption có kiểm soát & đo impact
- Điều phối corruption flow: corrupt → rebuild → evaluate → compare.
- Kiểm tra output corrupted riêng biệt và không ghi đè baseline.
- Hỗ trợ tổng hợp evidence impact và báo cáo tiến độ.
- Theo dõi: ai làm corruption, ai rebuild index, ai chạy evaluate.
- Xác nhận log corruption rõ ràng cho mỗi thay đổi dữ liệu.
- Đảm bảo team biết đường dẫn baseline/corrupted/repaired riêng.

### CP6 — Repair từ raw, comparison, review & demo
- Điều phối repair từ raw và làm comparison cuối cùng.
- Đóng băng scope, kiểm tra report, artifacts và demo path.
- Đảm bảo không có secret/.env và không hard-code path vào report.
- Theo dõi: ai chịu trách nhiệm repaired dataset và ai chịu report.
- Xác nhận demo dùng artifact thật, không demo số liệu giả định.
- Kiểm tra mọi thành viên hiểu delta baseline/corrupted/repaired.

## 3. Flow làm việc của cả team

### 3.1. Bước 1 — Khởi động chung và phân công
- Tập trung đọc yêu cầu lab và định nghĩa chung về pipeline.
- Chia team theo chức năng: Lead, Ingest, Clean, RAG, Eval, Observe.
- Chốt toolchain, file path, artifact output và cách báo lỗi/tracker.
- Mỗi người biết rõ đầu ra họ phải giao và ai nhận phần tiếp theo.

### 3.2. Bước 2 — Xây dựng pipeline baseline
- `Ingest` chịu raw source, fetch/parse Crossref, lưu raw artifact.
- `Clean` xử lý raw → clean, build schema, text_for_embedding, age_days.
- `RAG` tạo embedding, xây dựng collection baseline và smoke test.
- `Eval` tạo test set cố định, chạy evaluator, lưu answers và metrics.
- `Observe` kiểm tra quality/freshness, tạo báo cáo baseline.
- Lead/Integrator kiểm tra cross-cutting contract, đường dẫn artifact và dependencies.

### 3.3. Bước 3 — Nhận diện và xử lý blocker
- Dùng checkpoint để xác định đâu là lỗi: raw fetch, clean schema, index, test set hay metrics.
- Ghi trắng blocker và evidence để tránh xử lý sai hướng.
- Khi gặp blocker, team dừng, điều phối sửa contract hoặc dữ liệu trước khi tiếp.

### 3.4. Bước 4 — Chạy corruption flow
- Chọn corruption scenario có chủ đích, có thể đo lường ảnh hưởng.
- Build corrupted clean dataset riêng, không đè baseline.
- Rebuild index corrupted, chạy evaluator cũ và lưu metrics mới.
- So sánh baseline vs corrupted, tập trung vào evidence cụ thể.
- Observe ghi quality/freshness signal của dataset corrupted.

### 3.5. Bước 5 — Repair và comparison
- Từ raw source, làm lại clean/repaired dataset theo đúng contract.
- Build collection repaired riêng và chạy cùng test set cũ.
- So sánh metrics baseline/corrupted/repaired và tạo report delta.
- Demo bằng artifacts thật, chỉ ra recovery được gì và giới hạn nào còn tồn.

### 3.6. Nguyên tắc làm việc chung
- Không ghi đè baseline; luôn dùng path/collection riêng cho baseline/corrupted/repaired.
- Giữ test set và evaluator cố định khi so sánh các trạng thái.
- Repair bằng chạy lại pipeline từ source, không sửa tay outputs.
- Báo cáo phải trỏ tới artifact thật, không dùng số liệu giả hoặc dữ liệu nội suy.
- Mỗi checkpoint phải rõ người chịu trách nhiệm và người theo dõi.

## 4. Gợi ý cấu trúc giao tiếp trong team
- Dùng 1 bảng ngắn mỗi checkpoint: `Ai đang làm gì`, `Ai chờ gì`, `Blocker`, `Next step`.
- Lead cập nhật nhanh tình trạng và điều phối ưu tiên sửa blocker.
- Ai xong nhiệm vụ thì báo “ready” cùng artifact path.
- Ai chậm hoặc gặp lỗi thì cập nhật ngay để tránh kéo cả team.

---

*Tài liệu này dùng cho nhóm 6 người, tách riêng phần vai trò 1 và flow làm việc của cả team để dễ theo dõi.*