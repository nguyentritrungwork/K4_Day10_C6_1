from __future__ import annotations

from typing import Any

import pandas as pd


def build_test_set(df: pd.DataFrame, output_path: str) -> list[dict[str, Any]]:
    if len(df) < 2:
        print("Not enough documents to build a test set.")
        return []

    # Select representative papers (e.g. max 5 papers)
    sample_df = df.head(5) if len(df) >= 5 else df
    
    test_set = []
    q_id = 1
    
    for _, row in sample_df.iterrows():
        paper_id = row.get("paper_id", "")
        title = row.get("title", "")
        
        if not paper_id or not title:
            continue
            
        # 1. Summary question
        if "summary" in row and pd.notna(row["summary"]):
            import re
            summary = str(row["summary"]).strip()
            # extract first sentence
            first_sentence = summary.split(". ")[0] + "." if ". " in summary else summary
            
            test_set.append({
                "id": f"q{q_id}",
                "question_type": "summary",
                "question": f"What is the summary of '{title}'?",
                "ground_truth": first_sentence,
                "ground_truth_doc_ids": [paper_id]
            })
            q_id += 1
            
        # 2. Authors question
        if "authors_joined" in row and pd.notna(row["authors_joined"]):
            test_set.append({
                "id": f"q{q_id}",
                "question_type": "authors",
                "question": f"Who authored '{title}'?",
                "ground_truth": str(row["authors_joined"]),
                "ground_truth_doc_ids": [paper_id]
            })
            q_id += 1
            
        # 3. Date question
        if "published" in row and pd.notna(row["published"]):
            test_set.append({
                "id": f"q{q_id}",
                "question_type": "date",
                "question": f"When was '{title}' published?",
                "ground_truth": str(row["published"]),
                "ground_truth_doc_ids": [paper_id]
            })
            q_id += 1
            
        # 4. Categories question
        if "categories_joined" in row and pd.notna(row["categories_joined"]):
            test_set.append({
                "id": f"q{q_id}",
                "question_type": "categories",
                "question": f"What categories does '{title}' belong to?",
                "ground_truth": str(row["categories_joined"]),
                "ground_truth_doc_ids": [paper_id]
            })
            q_id += 1

    import json
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_set, f, indent=2)

    return test_set
