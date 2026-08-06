from __future__ import annotations

from datetime import datetime

import pandas as pd

from ingestion.crossref import PaperRecord


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """TODO(student): clean raw records thanh dataframe san sang de embed.

    Pseudo-code:
    1. Normalize title, summary, authors, categories.
    2. Parse published/updated date.
    3. Tinh age_days.
    4. Tao cot helper:
       - authors_joined
       - categories_joined
       - summary_chars
       - text_for_embedding
    5. Drop duplicates va filter row xau.
    6. Sort dataframe va return.
    """
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame([vars(r) for r in records])

    # 1. Normalize title, summary, authors, categories.
    df['title'] = df['title'].astype(str).str.strip()
    df['summary'] = df['summary'].astype(str).str.strip()
    df['authors'] = df['authors'].apply(lambda x: [str(a).strip() for a in x] if isinstance(x, list) else [])
    df['categories'] = df['categories'].apply(lambda x: [str(c).strip() for c in x] if isinstance(x, list) else [])

    # 5. Drop duplicates va filter row xau.
    # We do this before heavy text ops to save time
    df = df.dropna(subset=['paper_id', 'title', 'summary'])
    df = df[(df['paper_id'] != '') & (df['title'] != '') & (df['summary'] != '')]
    df = df.drop_duplicates(subset=['paper_id'], keep='first')

    # 2. Parse published/updated date.
    df['published'] = pd.to_datetime(df['published'], utc=True, errors='coerce')
    df['updated'] = pd.to_datetime(df['updated'], utc=True, errors='coerce')

    # Drop rows that failed to parse published date
    df = df.dropna(subset=['published'])

    # 3. Tinh age_days.
    # run_date might be naive or aware. We ensure it's timezone aware for subtraction
    if run_date.tzinfo is None:
        from datetime import timezone
        run_date = run_date.replace(tzinfo=timezone.utc)
    
    df['age_days'] = (run_date - df['published']).dt.days

    # 4. Tao cot helper:
    df['authors_joined'] = df['authors'].apply(lambda x: ', '.join(x))
    df['categories_joined'] = df['categories'].apply(lambda x: ', '.join(x))
    df['summary_chars'] = df['summary'].str.len()
    
    df['text_for_embedding'] = (
        "Title: " + df['title'] + "\n" +
        "Summary: " + df['summary'] + "\n" +
        "Authors: " + df['authors_joined'] + "\n" +
        "Categories: " + df['categories_joined']
    )

    # 6. Sort dataframe va return.
    df = df.sort_values(by='published', ascending=False).reset_index(drop=True)

    # Note: we convert published and updated back to ISO 8601 strings
    # because downstream (like ChromaDB metadata) usually require strings.
    df['published'] = df['published'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df['updated'] = df['updated'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    return df
