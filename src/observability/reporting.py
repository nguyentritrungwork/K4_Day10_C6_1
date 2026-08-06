from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _format_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _render_table(payload: dict[str, Any]) -> str:
    rows = ["| Field | Value |", "| --- | --- |"]
    for key, value in payload.items():
        rows.append(f"| {key} | {_format_value(value).replace(chr(10), '<br>')} |")
    return "\n".join(rows)


def _artifact_status(path_value: Any) -> str:
    if not path_value:
        return "missing path"
    return "exists" if Path(str(path_value)).exists() else "missing"


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Phase 1 Baseline Report",
        "",
        "This report summarizes the baseline clean-data pipeline, including source ingestion, dataset artifacts, retrieval evaluation, data quality checks, and freshness signals.",
        "",
        "## Source & Dataset Summary",
        "",
        _render_table({
            "source_api": source_summary.get("source_api"),
            "source_query": source_summary.get("source_query"),
            "source_filter": source_summary.get("source_filter"),
            "max_results": source_summary.get("max_results"),
            "raw_record_count": source_summary.get("record_count"),
            "clean_row_count": source_summary.get("clean_rows"),
            "raw_records_path": source_summary.get("raw_records_path"),
            "clean_csv": source_summary.get("clean_csv"),
            "clean_json": source_summary.get("clean_json"),
            "evaluation_test_set": source_summary.get("test_set_path"),
            "embeddings_manifest": source_summary.get("embedding_manifest"),
        }),
        "",
        "## Artifact Checklist",
        "",
        _render_table({
            "raw_records_path": _artifact_status(source_summary.get("raw_records_path")),
            "clean_csv": _artifact_status(source_summary.get("clean_csv")),
            "clean_json": _artifact_status(source_summary.get("clean_json")),
            "evaluation_test_set": _artifact_status(source_summary.get("test_set_path")),
            "embeddings_manifest": _artifact_status(source_summary.get("embedding_manifest")),
            "baseline_metrics": _artifact_status(source_summary.get("baseline_metrics_path")),
            "baseline_answers": _artifact_status(source_summary.get("baseline_answers_path")),
            "quality_report": _artifact_status(source_summary.get("quality_report_path")),
            "freshness_report": _artifact_status(source_summary.get("freshness_report_path")),
        }),
        "",
        "## Retrieval & QA Metrics",
        "",
        _render_table({
            "samples_evaluated": metrics.get("samples"),
            "retrieval_hit_rate": metrics.get("retrieval_hit_rate"),
            "mean_token_f1": metrics.get("mean_token_f1"),
            "judge_accuracy": metrics.get("judge_accuracy"),
            "mean_judge_score": metrics.get("mean_judge_score"),
        }),
        "",
        "## Data Quality Summary",
        "",
        _render_table({
            "quality_report_name": quality.get("report_name"),
            "total_rows": quality.get("total_rows"),
            "is_valid": quality.get("is_valid"),
            "passed_checks": quality.get("passed_checks"),
            "failed_checks": quality.get("failed_checks"),
            "outlier_row_count": quality.get("signals", {}).get("row_count"),
            "duplicate_paper_id_rows": quality.get("signals", {}).get("paper_id_duplicate_rows"),
            "summary_missing_rows": quality.get("signals", {}).get("summary_missing"),
            "text_for_embedding_missing": quality.get("signals", {}).get("text_for_embedding_missing"),
            "stale_rows": quality.get("signals", {}).get("stale_rows"),
        }),
        "",
        "## Freshness Summary",
        "",
        _render_table({
            "latest_published": freshness.get("latest_published"),
            "oldest_published": freshness.get("oldest_published"),
            "stale_rows": freshness.get("stale_rows"),
            "missing_published_rows": freshness.get("missing_published_rows"),
            "missing_age_days_rows": freshness.get("missing_age_days_rows"),
            "freshness_threshold_days": freshness.get("freshness_threshold_days"),
            "is_fresh": freshness.get("is_fresh"),
        }),
        "",
        "## Embedding Index Audit",
        "",
        _render_table({
            "embedding_manifest_documents": source_summary.get("embedding_manifest_documents"),
            "embedding_manifest_collection": source_summary.get("embedding_manifest_collection"),
            "embedding_manifest_model": source_summary.get("embedding_manifest_model"),
            "chroma_collection": source_summary.get("chroma_collection"),
            "chroma_document_count": source_summary.get("chroma_document_count"),
            "counts_match_clean_data": source_summary.get("embedding_counts_match"),
            "audit_warning": source_summary.get("embedding_audit_warning"),
        }),
        "",
        "## Recommendations",
        "",
        "- Treat this report as the baseline evidence pack for comparison with corrupted and repaired runs.",
        "- Use the same `data/eval/test_set.json` for baseline, corrupted, and repaired evaluations to keep comparisons valid.",
        "- Regenerate embedding artifacts if manifest paths or model names do not match the current project settings.",
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Corruption & Repair Comparison Report",
        "",
        "This report compares baseline, corrupted, and repaired data artifacts across retrieval metrics, data quality checks, and freshness signals.",
        "",
        "## Baseline Metrics",
        "",
        _render_table({
            "samples_evaluated": baseline_metrics.get("samples"),
            "retrieval_hit_rate": baseline_metrics.get("retrieval_hit_rate"),
            "mean_token_f1": baseline_metrics.get("mean_token_f1"),
            "judge_accuracy": baseline_metrics.get("judge_accuracy"),
            "mean_judge_score": baseline_metrics.get("mean_judge_score"),
        }),
        "",
        "## Corrupted Metrics",
        "",
        _render_table({
            "samples_evaluated": corrupted_metrics.get("samples"),
            "retrieval_hit_rate": corrupted_metrics.get("retrieval_hit_rate"),
            "mean_token_f1": corrupted_metrics.get("mean_token_f1"),
            "judge_accuracy": corrupted_metrics.get("judge_accuracy"),
            "mean_judge_score": corrupted_metrics.get("mean_judge_score"),
        }),
        "",
        "## Repaired Metrics",
        "",
        _render_table({
            "samples_evaluated": repaired_metrics.get("samples"),
            "retrieval_hit_rate": repaired_metrics.get("retrieval_hit_rate"),
            "mean_token_f1": repaired_metrics.get("mean_token_f1"),
            "judge_accuracy": repaired_metrics.get("judge_accuracy"),
            "mean_judge_score": repaired_metrics.get("mean_judge_score"),
        }),
        "",
        "## Corrupted Quality Summary",
        "",
        _render_table({
            "is_valid": corrupted_quality.get("is_valid"),
            "failed_checks": corrupted_quality.get("failed_checks"),
            "stale_rows": corrupted_quality.get("signals", {}).get("stale_rows"),
        }),
        "",
        "## Repaired Quality Summary",
        "",
        _render_table({
            "is_valid": repaired_quality.get("is_valid"),
            "failed_checks": repaired_quality.get("failed_checks"),
            "stale_rows": repaired_freshness.get("stale_rows"),
        }),
        "",
        "## Recommendations",
        "",
        "- Compare the corrupted and repaired metrics to baseline to confirm whether repair improved retrieval quality.",
        "- Pay attention to freshness signals after repair because stale data can still hurt answer quality.",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
