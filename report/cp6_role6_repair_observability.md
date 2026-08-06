# CP6 - Role 6 Observability Owner

## Phạm vi CP6

Role 6 phụ trách kiểm tra observability sau repair và đối chiếu baseline - corrupted - repaired bằng artifact thật.

## Output chính đã kiểm tra

- Baseline quality: `data/quality/baseline_quality.json`
- Corrupted quality: `data/quality/corrupted_quality.json`
- Repaired quality: `data/quality/repaired_quality.json`
- Baseline freshness: `data/quality/freshness_report.json`
- Corrupted freshness: `data/quality/corrupted_freshness.json`
- Repaired freshness: `data/quality/repaired_freshness.json`
- Comparison report: `data/reports/corruption_report.md`

## Quality comparison

| Signal | Baseline | Corrupted | Repaired | Nhận xét |
| --- | ---: | ---: | ---: | --- |
| `total_rows` | 24 | 23 | 24 | Repair phục hồi row count |
| `is_valid` | true | false | true | Repair phục hồi quality gate |
| `passed_checks` | 10 | 7 | 10 | Repaired pass lại toàn bộ checks |
| `failed_checks` | 0 | 3 | 0 | Corrupted fail 3 checks, repaired về 0 |
| `paper_id_duplicate_rows` | 0 | 2 | 0 | Duplicate được loại bỏ sau repair |
| `summary_missing` | 0 | 1 | 0 | Blank summary được phục hồi |
| `short_summary_rows` | 0 | 1 | 0 | Summary quá ngắn không còn |
| `text_for_embedding_missing` | 0 | 0 | 0 | Không có text embedding rỗng |

## Freshness comparison

| Signal | Baseline | Corrupted | Repaired | Nhận xét |
| --- | --- | --- | --- | --- |
| `total_rows` | 24 | 23 | 24 | Repaired khớp baseline |
| `latest_published` | `2026-08-01T00:00:00+00:00` | `2026-07-13T00:00:00+00:00` | `2026-08-01T00:00:00+00:00` | Latest phục hồi |
| `oldest_published` | `2026-02-12T00:00:00+00:00` | `1999-07-02T00:00:00+00:00` | `2026-02-12T00:00:00+00:00` | Stale date được phục hồi |
| `stale_rows` | 0 | 0 | 0 | Lưu ý check dựa trên `age_days` |
| `is_fresh` | true | true | true | Freshness status vẫn true, nhưng oldest published cho thấy corrupted có bất thường |

## Liên hệ observability với metric recovery

| Metric | Baseline | Corrupted | Repaired | Liên hệ với quality |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0 | 1.0 | 1.0 | Retrieval không bị ảnh hưởng rõ trong test set |
| `mean_token_f1` | 1.0 | 0.9333 | 1.0 | Sai ở `q12` do stale date, repair phục hồi |
| `judge_accuracy` | 1.0 | 0.9333 | 1.0 | Repaired trả lại answer đúng |
| `mean_judge_score` | 5.0 | 4.7333 | 5.0 | Judge score phục hồi về baseline |

## Evidence recovery

Case `q12`:

- Paper ID: `10-3390-buildings16132637`
- Corruption: `stale_date`
- Baseline answer: `2026-07-02T00:00:00Z`
- Corrupted answer: `1999-07-02T00:00:00Z`
- Repaired answer: `2026-07-02T00:00:00Z`
- Repaired judge correct: true

Quality/freshness cũng phục hồi:

- `failed_checks`: 3 -> 0
- `paper_id_duplicate_rows`: 2 -> 0
- `summary_missing`: 1 -> 0
- `oldest_published`: 1999 -> 2026

## Giới hạn cần ghi trong báo cáo

- `stale_rows` vẫn là 0 ở corrupted vì logic freshness hiện dựa trên `age_days`; trong khi corruption đổi `published` nhưng không cập nhật lại `age_days`.
- Vì vậy nên dùng thêm `oldest_published` để phát hiện stale date bất thường.
- Một số corruption khác như `inject_noise`, `truncate_title`, `drop_latest` chưa làm metric giảm rõ vì test set hiện tại không bao phủ trực tiếp các record đó.

## Kết luận CP6 của Role 6

Role 6 đã xác nhận repair phục hồi observability signals:

- Repaired quality valid trở lại.
- Failed checks giảm từ 3 về 0.
- Duplicate và missing summary được phục hồi.
- Freshness oldest published phục hồi từ năm 1999 về năm 2026.
- Comparison report đã có đủ baseline - corrupted - repaired.

Kết luận trung thực: repair phục hồi các quality signals và answer metric đã bị ảnh hưởng bởi stale date; tuy nhiên freshness logic nên được cải thiện để stale date được tính vào `stale_rows` khi `published` thay đổi.
