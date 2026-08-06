# Checkpoint 5 - Vai trò 5: Corrupted Evaluation

## Trạng thái

Checkpoint 5 của vai trò 5 đã có official corrupted evaluation artifacts từ pipeline.

## Output chính đã kiểm tra

- Test set cố định: `data/eval/test_set.json`
- Baseline metrics: `data/results/baseline_metrics.json`
- Baseline answers: `data/results/baseline_answers.json`
- Corrupted metrics: `data/results/corrupted_metrics.json`
- Corrupted answers: `data/results/corrupted_answers.json`
- Corruption log: `data/results/corruption_log.json`
- Corrupted quality report: `data/quality/corrupted_quality.json`
- Corrupted freshness report: `data/quality/corrupted_freshness.json`
- Corrupted embedding manifest: `data/embeddings/papers_embeddings_corrupted.json`

## Kiểm tra tính công bằng

| Hạng mục | Kết quả |
| --- | --- |
| Test set dùng lại từ checkpoint 2 | Đúng |
| Số câu hỏi trong `test_set.json` | 15 |
| Số answers trong `corrupted_answers.json` | 15 |
| Question types | `summary`: 5, `authors`: 5, `date`: 5 |
| Corrupted collection | `papers-corrupted` |
| Corrupted embedding documents | 23 |

## So sánh metric baseline và corrupted

| Metric | Baseline | Corrupted | Delta |
| --- | ---: | ---: | ---: |
| `samples` | 15 | 15 | 0 |
| `retrieval_hit_rate` | 1.0 | 1.0 | 0.0 |
| `mean_token_f1` | 1.0 | 0.9333 | -0.0667 |
| `judge_accuracy` | 1.0 | 0.9333 | -0.0667 |
| `mean_judge_score` | 5.0 | 4.7333 | -0.2667 |

Kết luận: corrupted data chưa làm giảm retrieval hit rate vì các document ground truth trong test set vẫn được retrieve, nhưng đã làm giảm answer quality ở câu hỏi ngày publish.

## Case bị ảnh hưởng rõ nhất

| Hạng mục | Giá trị |
| --- | --- |
| Question ID | `q12` |
| Question type | `date` |
| Paper ID | `10-3390-buildings16132637` |
| Question | When was "An Agentic AI System for Roof Design Compliance Using Computer Vision, Retrieval-Augmented Generation and Large Language Models" published? |
| Ground truth | `2026-07-02T00:00:00Z` |
| Corrupted answer | `1999-07-02T00:00:00Z` |
| Retrieval hit | `true` |
| Token F1 | `0.0` |
| Judge score | `1` |
| Judge correct | `false` |
| Judge reasoning | The model answer provides an incorrect publication date, which is significantly earlier than the reference answer. |

Giải thích: retrieval vẫn tìm đúng document `10-3390-buildings16132637`, nhưng field `published` của document này đã bị corrupt thành năm 1999, nên answer sai dù retrieval hit.

## Đối chiếu với corruption log

Corruption log ghi rõ:

```json
{
  "type": "stale_date",
  "record_ids": ["10-3390-buildings16132637"],
  "parameter": "changed year to 1999",
  "before": "2026-07-02T00:00:00Z",
  "after": "1999-07-02T00:00:00Z"
}
```

Đây là evidence trực tiếp giải thích vì sao `q12` sai trong corrupted evaluation.

## Quality signals của corrupted data

| Signal | Giá trị |
| --- | ---: |
| `total_rows` | 23 |
| `is_valid` | false |
| `passed_checks` | 7 |
| `failed_checks` | 3 |
| `paper_id_duplicate_rows` | 2 |
| `summary_missing` | 1 |
| `short_summary_rows` | 1 |
| `text_for_embedding_missing` | 0 |

Các check fail trong corrupted quality:

- `paper_id_unique`
- `summary_not_null`
- `summary_min_length`

Freshness report ghi `oldest_published = 1999-07-02T00:00:00+00:00`, phản ánh stale date xuất hiện trong corrupted data. Tuy nhiên `stale_rows` vẫn là 0 vì freshness check hiện dựa vào `age_days`, trong khi corruption chỉ đổi `published` mà chưa cập nhật lại `age_days`.

## Kết luận checkpoint 5

Vai trò 5 đã hoàn thành checkpoint 5 với official artifacts:

- Đã xác nhận corrupted evaluation dùng lại đúng `data/eval/test_set.json`.
- Đã đối chiếu `baseline_metrics.json` với `corrupted_metrics.json`.
- Đã xác định metric giảm ở `mean_token_f1`, `judge_accuracy`, `mean_judge_score`.
- Đã tìm được case bị ảnh hưởng trực tiếp: `q12`.
- Đã liên hệ case sai với `stale_date` trong `corruption_log.json`.
- Đã kiểm tra quality signals cho corrupted data.

Baseline vẫn là mốc so sánh chính thức; corrupted state cho thấy data quality issue có thể làm answer sai dù retrieval vẫn hit document đúng.
