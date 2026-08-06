from __future__ import annotations

from datetime import UTC, datetime
from core.config import load_settings
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    settings = load_settings()

    print("=== Step 1: Load or Fetch Raw Records ===")
    # Đảm bảo không fetch lại nguồn ngoài ý muốn nếu refresh_source=False
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        print(f"Fetching from Crossref API (query='{settings.source_query}')...")
        records = fetch_source_records(settings)
    else:
        print(f"Loading local raw records from: {settings.paths.raw_records_json}")
        records = load_raw_records(settings.paths.raw_records_json)
    print(f"=> Loaded {len(records)} raw records.")

    print("\n=== Step 2: Clean and Transform Data ===")
    run_date = datetime.now(UTC)
    df = build_clean_dataframe(records=records, run_date=run_date)
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.paths.clean_csv, index=False)
    df.to_json(settings.paths.clean_json, orient="records", force_ascii=False, indent=4)
    print(f"=> Saved {len(df)} clean records to {settings.paths.clean_csv} và {settings.paths.clean_json}")

    print("\n=== Step 3: Build ChromaDB Embedding Index ===")
    index = LocalEmbeddingIndex.build(df, settings)
    print(f"=> Index built at {settings.paths.chroma_dir}")

    print("\n=== Step 4: Load or Build Evaluation Test Set ===")
    test_set_path = settings.paths.eval_test_set
    if not test_set_path.exists():
        build_test_set(df, str(test_set_path))
    print(f"=> Test set available at {test_set_path}")

    print("\n=== Step 5: Evaluate Baseline Performance ===")
    settings.paths.baseline_metrics.parent.mkdir(parents=True, exist_ok=True)
    answers_path = settings.paths.results_dir / "baseline_answers.json"
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=test_set_path,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=answers_path,
    )
    print(f"=> Saved baseline metrics to {settings.paths.baseline_metrics}")

    print("\n=== Step 6: Run Data Quality and Freshness Checks ===")
    quality_report = run_data_quality_checks(df, settings, "baseline_quality.json")
    freshness_report = build_freshness_report(df, settings, settings.paths.quality_dir / "baseline_freshness.json")
    print(f"=> Quality checks completed.")

    print("\nPhase 1 Baseline Pipeline Completed Successfully!")


if __name__ == "__main__":
    main()
