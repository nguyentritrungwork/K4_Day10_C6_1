# Checkpoint 6 - Vai trò 5: Repaired Evaluation

## Trạng thái

Checkpoint 6 của vai trò 5 đã hoàn thành với official repaired evaluation artifacts.

## Output chính đã kiểm tra

- Test set cố định: `data/eval/test_set.json`
- Baseline metrics: `data/results/baseline_metrics.json`
- Corrupted metrics: `data/results/corrupted_metrics.json`
- Repaired metrics: `data/results/repaired_metrics.json`
- Baseline answers: `data/results/baseline_answers.json`
- Corrupted answers: `data/results/corrupted_answers.json`
- Repaired answers: `data/results/repaired_answers.json`
- Comparison report: `data/reports/corruption_report.md`

## Kiểm tra tính công bằng

| Hạng mục | Kết quả |
| --- | --- |
| Test set dùng cho cả 3 trạng thái | `data/eval/test_set.json` |
| Samples baseline | 15 |
| Samples corrupted | 15 |
| Samples repaired | 15 |
| Question types | `summary`: 5, `authors`: 5, `date`: 5 |

## So sánh metrics 3 trạng thái

| Metric | Baseline | Corrupted | Repaired | Nhận xét |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0 | 1.0 | 1.0 | Retrieval vẫn tìm được ground truth document ở cả 3 trạng thái |
| `mean_token_f1` | 1.0 | 0.9333 | 1.0 | Corrupted giảm do `q12`, repaired phục hồi hoàn toàn |
| `judge_accuracy` | 1.0 | 0.9333 | 1.0 | Một câu sai ở corrupted, repaired đúng lại |
| `mean_judge_score` | 5.0 | 4.7333 | 5.0 | Điểm judge phục hồi về baseline |

## Delta chính

| Metric | Corrupted - Baseline | Repaired - Corrupted | Repaired - Baseline |
| --- | ---: | ---: | ---: |
| `retrieval_hit_rate` | 0.0 | 0.0 | 0.0 |
| `mean_token_f1` | -0.0667 | +0.0667 | 0.0 |
| `judge_accuracy` | -0.0667 | +0.0667 | 0.0 |
| `mean_judge_score` | -0.2667 | +0.2667 | 0.0 |

## Evidence case: q12 phục hồi sau repair

| State | Answer | Retrieval hit | Token F1 | Judge score | Judge correct |
| --- | --- | --- | ---: | ---: | --- |
| Baseline | `2026-07-02T00:00:00Z` | true | 1.0 | 5 | true |
| Corrupted | `1999-07-02T00:00:00Z` | true | 0.0 | 1 | false |
| Repaired | `2026-07-02T00:00:00Z` | true | 1.0 | 5 | true |

Question `q12` hỏi ngày publish của paper `10-3390-buildings16132637`. Corrupted state sai vì corruption `stale_date` đổi năm publish sang 1999. Repaired state trả lại đúng ngày `2026-07-02T00:00:00Z`, nên metric phục hồi.

## Kết luận CP6 của Role 5

Vai trò 5 đã xác nhận repaired evaluation phục hồi về baseline:

- Số sample khớp test set ở cả 3 trạng thái.
- Corrupted làm giảm answer quality nhưng không làm giảm retrieval hit.
- Repaired phục hồi `mean_token_f1`, `judge_accuracy`, `mean_judge_score` về giá trị baseline.
- Case `q12` là evidence rõ nhất: sai ở corrupted, đúng lại ở repaired.

## Handoff cho báo cáo nhóm

Khi viết report nhóm, có thể dùng kết luận ngắn:

> Corruption `stale_date` làm câu hỏi `q12` trả sai ngày publish, khiến `mean_token_f1` giảm từ 1.0 xuống 0.9333 và `judge_accuracy` giảm từ 1.0 xuống 0.9333. Sau repair từ raw records, repaired metrics phục hồi về baseline: `mean_token_f1 = 1.0`, `judge_accuracy = 1.0`, `mean_judge_score = 5.0`.
