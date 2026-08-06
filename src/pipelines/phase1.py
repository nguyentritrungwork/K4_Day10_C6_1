from __future__ import annotations
from datetime import datetime, UTC

from core.config import load_settings
from core.utils import read_json
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from observability import build_freshness_report, generate_phase1_report, run_data_quality_checks
from retrieval.index import LocalEmbeddingIndex


def _load_raw_or_fetch_records(settings):
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        return fetch_source_records(settings)
    return load_raw_records(settings.paths.raw_records_json)


def _build_or_load_test_set(df, settings) -> list[dict[str, object]]:
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        return build_test_set(df, str(settings.paths.eval_testset))
    return read_json(settings.paths.eval_testset)


def _build_embedding_index(df, settings) -> LocalEmbeddingIndex:
    return LocalEmbeddingIndex.build(df=df, settings=settings, embeddings_output_path=settings.paths.embeddings_json)


def _summarize_source(settings, records, df) -> dict[str, object]:
    return {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "source_filter": settings.source_filter,
        "max_results": settings.max_results,
        "raw_records_path": str(settings.paths.raw_records_json),
        "record_count": len(records),
        "clean_rows": len(df),
        "clean_csv": str(settings.paths.clean_csv),
        "clean_json": str(settings.paths.clean_json),
        "embedding_manifest": str(settings.paths.embeddings_json),
        "test_set_path": str(settings.paths.eval_testset),
        "run_date": datetime.now(UTC).isoformat(),
    }


def main() -> None:
    settings = load_settings()
    run_date = datetime.now(UTC)

    records = _load_raw_or_fetch_records(settings)
    df = build_clean_dataframe(records=records, run_date=run_date)

    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.paths.clean_csv, index=False)
    df.to_json(settings.paths.clean_json, orient="records", force_ascii=False, indent=4)

    test_set = _build_or_load_test_set(df, settings)
    index = _build_embedding_index(df, settings)

    evaluation = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )

    baseline_quality = run_data_quality_checks(df=df, settings=settings, report_name="baseline_quality.json")
    freshness_report = build_freshness_report(df=df, settings=settings, report_path=settings.paths.freshness_report)

    source_summary = _summarize_source(settings=settings, records=records, df=df)
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=evaluation.summary,
        quality=baseline_quality,
        freshness=freshness_report,
    )

    print("Baseline pipeline complete.")
    print(f"Baseline metrics: {settings.paths.baseline_metrics}")
    print(f"Baseline answers: {settings.paths.baseline_answers}")
    print(f"Quality report: {settings.paths.quality_dir / 'baseline_quality.json'}")
    print(f"Freshness report: {settings.paths.freshness_report}")
    print(f"Phase 1 report: {settings.paths.baseline_report}")
