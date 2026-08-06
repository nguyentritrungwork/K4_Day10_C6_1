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
    
    log = {
        "dropped_indices": [],
        "blank_summary_indices": [],
        "noise_injected_indices": [],
        "truncated_title_indices": [],
        "stale_date_indices": [],
        "duplicated_indices": []
    }
    
    n = len(df_corrupted)
    if n > 0:
        # 1. Drop mot so latest records.
        # Assuming the dataframe is sorted by published descending, 
        # dropping the first 2 rows simulates missing latest data.
        if n > 2:
            dropped = df_corrupted.index[:2].tolist()
            log["dropped_indices"] = dropped
            df_corrupted = df_corrupted.drop(index=dropped)
            
        df_corrupted = df_corrupted.reset_index(drop=True)
        n = len(df_corrupted)
        
        # Apply corruptions if we have enough rows left
        if n > 5:
            # 2. Blank summary o mot so dong
            df_corrupted.at[0, 'summary'] = ""
            log["blank_summary_indices"].append(0)
            
            # 3. Inject noise vao text
            df_corrupted.at[1, 'summary'] = str(df_corrupted.at[1, 'summary']) + " CORRUPTED_NOISE_123 "
            log["noise_injected_indices"].append(1)
            
            # 4. Lam title bi truncate
            df_corrupted.at[2, 'title'] = str(df_corrupted.at[2, 'title'])[:15]
            log["truncated_title_indices"].append(2)
            
            # 5. Lam published date cu di (change year to 1999 to simulate stale data)
            orig_date = str(df_corrupted.at[3, 'published'])
            if len(orig_date) >= 4:
                df_corrupted.at[3, 'published'] = "1999" + orig_date[4:]
            log["stale_date_indices"].append(3)
                
            # 6. Add duplicate rows
            row_to_dup = df_corrupted.iloc[[4]]
            df_corrupted = pd.concat([df_corrupted, row_to_dup], ignore_index=True)
            log["duplicated_indices"].append(4)
            
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
        json.dump(log, f, indent=4)
        
    return df_corrupted
