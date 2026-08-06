# Checkpoint 3 - Vai tro 5: Baseline Evaluation

## Output chinh da kiem tra

- Test set co dinh: `data/eval/test_set.json`
- Baseline metrics: `data/results/baseline_metrics.json`
- Baseline answers: `data/results/baseline_answers.json`
- Embedding manifest: `data/embeddings/papers_embeddings.json`
- Phase 1 report: `data/reports/phase1_report.md`

## Ket qua baseline evaluation

| Metric | Gia tri |
| --- | --- |
| Samples trong `test_set.json` | 15 |
| Samples trong `baseline_answers.json` | 15 |
| Samples trong `baseline_metrics.json` | 15 |
| `retrieval_hit_rate` | 1.0 |
| `mean_token_f1` | 1.0 |
| `judge_accuracy` | 1.0 |
| `mean_judge_score` | 5 |
| Ragas | skipped |

## Phan bo cau hoi

| Question type | So cau |
| --- | --- |
| `summary` | 5 |
| `authors` | 5 |
| `date` | 5 |

## Evidence case tieu bieu

### Case q1 - retrieval dung

- Question type: `summary`
- Ground truth doc ID: `10-21203-rs-3-rs-10012178-v1`
- Retrieved doc IDs:
  - `10-21203-rs-3-rs-10012178-v1`
  - `10-36227-techrxiv-177272838-89432844-v1`
  - `10-63646-kpqm1958`
  - `10-1111-exsy-70341`
- `retrieval_hit`: true
- `token_f1`: 1.0
- Judge score: 5
- Judge correct: true

Ket luan: document ground truth nam trong retrieved results, cau tra loi trung voi ground truth, nen baseline case nay dat.

## Miss case

Khong co retrieval miss trong baseline: 15/15 cau hoi co `retrieval_hit = true`.

## Luu y quan trong cho cac checkpoint sau

- `data/eval/test_set.json` phai duoc giu co dinh cho corrupted va repaired.
- Khong regenerate test set rieng cho corrupted/repaired.
- Baseline hien tai la moc so sanh chinh thuc cho Checkpoint 5 va Checkpoint 6.
- Neu corrupted metrics giam, so sanh truc tiep voi cac baseline metrics trong file nay.

## Trang thai ban giao

Vai tro 5 da hoan thanh checkpoint 3. Baseline evaluation co du metrics va answers, so samples khop voi test set, va baseline du dieu kien lam moc so sanh.
