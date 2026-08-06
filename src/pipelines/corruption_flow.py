from __future__ import annotations

from datetime import datetime, UTC
import pandas as pd

from core.config import load_settings
from core.utils import read_json
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import load_raw_records
from evaluation.metrics import evaluate_pipeline
from retrieval.index import LocalEmbeddingIndex
from observability import run_data_quality_checks, build_freshness_report, generate_corruption_report


def main() -> None:
    settings = load_settings()
    run_date = datetime.now(UTC)

    # 1. Load baseline metrics va clean dataset.
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    try:
        df_clean = pd.read_json(settings.paths.clean_json, orient="records")
    except ValueError:
        df_clean = pd.read_json(settings.paths.clean_json, lines=True)

    # 2. Tao corrupted dataframe.
    df_corrupted = corrupt_clean_dataframe(df_clean, settings.paths.corruption_log)

    # 3. Save corrupted artifacts.
    settings.paths.corrupted_clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df_corrupted.to_csv(settings.paths.corrupted_clean_csv, index=False)
    df_corrupted.to_json(settings.paths.corrupted_clean_json, orient="records", lines=True, force_ascii=False)

    # 4. Rebuild index va evaluate.
    corrupted_index = LocalEmbeddingIndex.build(
        df=df_corrupted,
        settings=settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json
    )
    corrupted_eval = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )

    # 5. Run quality checks/freshness tren corrupted data.
    corrupted_quality = run_data_quality_checks(
        df=df_corrupted,
        settings=settings,
        report_name="corrupted_quality.json"
    )
    corrupted_freshness = build_freshness_report(
        df=df_corrupted,
        settings=settings,
        report_path=settings.paths.quality_dir / "corrupted_freshness.json"
    )

    # 6. Repair lai tu raw records.
    records = load_raw_records(settings.paths.raw_records_json)
    df_repaired = build_clean_dataframe(records=records, run_date=run_date)

    settings.paths.repaired_clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df_repaired.to_csv(settings.paths.repaired_clean_csv, index=False)
    df_repaired.to_json(settings.paths.repaired_clean_json, orient="records", lines=True, force_ascii=False)

    repaired_index = LocalEmbeddingIndex.build(
        df=df_repaired,
        settings=settings,
        embeddings_output_path=settings.paths.repaired_embeddings_json
    )

    # 7. Evaluate repaired dataset.
    repaired_eval = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )
    repaired_quality = run_data_quality_checks(
        df=df_repaired,
        settings=settings,
        report_name="repaired_quality.json"
    )
    repaired_freshness = build_freshness_report(
        df=df_repaired,
        settings=settings,
        report_path=settings.paths.quality_dir / "repaired_freshness.json"
    )

    # 8. Tao comparison report.
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_eval.summary,
        repaired_metrics=repaired_eval.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )
    print("Corruption and repair flow complete.")

