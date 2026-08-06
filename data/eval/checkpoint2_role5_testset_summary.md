# Checkpoint 2 - Vai tro 5: Evaluation Owner

## Output chinh

- Test set chinh thuc: `data/eval/test_set.json`

## Noi dung test set

| Hang muc | Ket qua |
| --- | --- |
| So cau hoi | 15 |
| So paper duoc dung | 5 |
| Question types | `summary`, `authors`, `date` |
| Category questions | Khong dung vi `categories_joined` dang rong |
| Nguon tao test set | `data/clean/papers_clean.csv` |
| Document ID dung cho ground truth | `paper_id` |

## Paper IDs duoc dung

- `10-21203-rs-3-rs-10012178-v1`
- `10-1093-sleep-zsag091-0346`
- `10-32473-flairs-39-1-141782`
- `10-3390-buildings16132637`
- `10-21203-rs-3-rs-10178277-v1`

## Kiem tra hop le

- Moi item co du `id`, `question_type`, `question`, `ground_truth`, `ground_truth_doc_ids`.
- `ground_truth_doc_ids` deu la `paper_id` that trong cleaned data.
- Khong co question rong.
- Khong co ground truth rong.
- Khong tao cau hoi `categories` do categories dang rong toan bo.

## Rule can giu tu checkpoint 2 tro di

Tu checkpoint 2 tro di, nhom phai dung co dinh `data/eval/test_set.json` cho ca ba trang thai:

1. baseline
2. corrupted
3. repaired

Khong tao test set rieng cho corrupted hoac repaired, vi nhu vay metric se khong con cong bang.

## Trang thai ban giao

Vai tro 5 da hoan thanh checkpoint 2. Test set da san sang de vai tro 4 va vai tro 1 dung trong baseline evaluation.
