from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """TODO(student): simulate nhieu dang data corruption.

    Pseudo-code:
    1. Drop mot so latest records.
    2. Blank summary o mot so dong.
    3. Inject noise vao text.
    4. Lam title bi truncate.
    5. Lam published date cu di.
    6. Add duplicate rows.
    7. Rebuild `text_for_embedding`.
    8. Ghi corruption log vao output_log_path.
    """
    df_corrupted = df.copy()
    
    logs = []
    
    # helper for logging
    def add_log(corruption_type, record_ids, param, before_val, after_val):
        logs.append({
            "type": corruption_type,
            "record_ids": record_ids,
            "parameter": param,
            "before": before_val,
            "after": after_val
        })

    n_initial = len(df_corrupted)
    if n_initial > 5:
        # 1. Drop mot so latest records.
        dropped_records = df_corrupted.iloc[:2]['paper_id'].tolist()
        df_corrupted = df_corrupted.iloc[2:].reset_index(drop=True)
        add_log("drop_latest", dropped_records, "dropped 2 rows", n_initial, len(df_corrupted))
        
        # 2. Blank summary o mot so dong
        target_idx = 0
        record_id = df_corrupted.at[target_idx, 'paper_id']
        before_len = len(str(df_corrupted.at[target_idx, 'summary']))
        df_corrupted.at[target_idx, 'summary'] = ""
        add_log("blank_summary", [record_id], "set summary to empty string", before_len, 0)
        
        # 3. Inject noise vao text
        target_idx = 1
        record_id = df_corrupted.at[target_idx, 'paper_id']
        before_len = len(str(df_corrupted.at[target_idx, 'summary']))
        noise = " CORRUPTED_NOISE_123 "
        df_corrupted.at[target_idx, 'summary'] = str(df_corrupted.at[target_idx, 'summary']) + noise
        after_len = len(str(df_corrupted.at[target_idx, 'summary']))
        add_log("inject_noise", [record_id], f"added '{noise}'", before_len, after_len)
        
        # 4. Lam title bi truncate
        target_idx = 2
        record_id = df_corrupted.at[target_idx, 'paper_id']
        before_len = len(str(df_corrupted.at[target_idx, 'title']))
        truncate_len = 15
        df_corrupted.at[target_idx, 'title'] = str(df_corrupted.at[target_idx, 'title'])[:truncate_len]
        after_len = len(str(df_corrupted.at[target_idx, 'title']))
        add_log("truncate_title", [record_id], f"truncated to {truncate_len} chars", before_len, after_len)
        
        # 5. Lam published date cu di (change year to 1999 to simulate stale data)
        target_idx = 3
        record_id = df_corrupted.at[target_idx, 'paper_id']
        orig_date = str(df_corrupted.at[target_idx, 'published'])
        new_date = "1999" + orig_date[4:] if len(orig_date) >= 4 else "1999-01-01T00:00:00Z"
        df_corrupted.at[target_idx, 'published'] = new_date
        add_log("stale_date", [record_id], "changed year to 1999", orig_date, new_date)
            
        # 6. Add duplicate rows
        target_idx = 4
        record_id = df_corrupted.at[target_idx, 'paper_id']
        row_to_dup = df_corrupted.iloc[[target_idx]]
        before_rows = len(df_corrupted)
        df_corrupted = pd.concat([df_corrupted, row_to_dup], ignore_index=True)
        after_rows = len(df_corrupted)
        add_log("duplicate_row", [record_id], "duplicated 1 row", before_rows, after_rows)
            
    # 7. Rebuild `text_for_embedding`.
    df_corrupted['text_for_embedding'] = (
        "Title: " + df_corrupted['title'].astype(str) + "\n" +
        "Summary: " + df_corrupted['summary'].astype(str) + "\n" +
        "Authors: " + df_corrupted['authors_joined'].astype(str) + "\n" +
        "Categories: " + df_corrupted['categories_joined'].astype(str)
    )
    
    # 8. Ghi corruption log vao output_log_path.
    path = Path(output_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"corruptions": logs}, f, indent=4)
        
    return df_corrupted
