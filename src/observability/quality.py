from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import write_json


def _blank_count(series: pd.Series) -> int:
    return int(series.fillna("").astype(str).str.strip().eq("").sum())


def _missing_column_check(df: pd.DataFrame, column: str) -> dict[str, Any] | None:
    if column in df.columns:
        return None
    return {
        "name": f"{column}_exists",
        "passed": False,
        "value": "missing",
        "expected": "column exists",
        "severity": "critical",
    }


def _check_payload(name: str, value: Any, passed: bool, expected: str, severity: str = "warning") -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "value": value,
        "expected": expected,
        "severity": severity,
    }


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Run baseline data quality checks and write a JSON report."""
    report_path = settings.paths.quality_dir / report_name
    if report_path.suffix.lower() != ".json":
        report_path = report_path.with_suffix(".json")

    total_rows = int(len(df))
    checks: list[dict[str, Any]] = [
        _check_payload("row_count_positive", total_rows, total_rows > 0, "> 0 rows", "critical"),
    ]

    for column in ["paper_id", "title", "summary", "published", "age_days", "text_for_embedding"]:
        missing_check = _missing_column_check(df, column)
        if missing_check:
            checks.append(missing_check)

    if "paper_id" in df.columns:
        paper_id_missing = _blank_count(df["paper_id"])
        paper_id_duplicate_rows = int(df["paper_id"].fillna("").astype(str).str.strip().duplicated(keep=False).sum())
        duplicate_ids = (
            df["paper_id"]
            .fillna("")
            .astype(str)
            .str.strip()
            .loc[lambda s: s.ne("") & s.duplicated(keep=False)]
            .drop_duplicates()
            .head(10)
            .tolist()
        )
        checks.extend(
            [
                _check_payload("paper_id_not_null", paper_id_missing, paper_id_missing == 0, "0 missing", "critical"),
                _check_payload(
                    "paper_id_unique",
                    paper_id_duplicate_rows,
                    paper_id_duplicate_rows == 0,
                    "0 duplicate rows",
                    "critical",
                ),
            ]
        )
    else:
        paper_id_missing = None
        paper_id_duplicate_rows = None
        duplicate_ids = []

    title_missing = _blank_count(df["title"]) if "title" in df.columns else None
    summary_missing = _blank_count(df["summary"]) if "summary" in df.columns else None
    text_missing = _blank_count(df["text_for_embedding"]) if "text_for_embedding" in df.columns else None

    if title_missing is not None:
        checks.append(_check_payload("title_not_null", title_missing, title_missing == 0, "0 missing", "critical"))
    if summary_missing is not None:
        checks.append(_check_payload("summary_not_null", summary_missing, summary_missing == 0, "0 missing"))
        summary_lengths = df["summary"].fillna("").astype(str).str.strip().str.len()
        short_summary_rows = int((summary_lengths < 40).sum())
        checks.append(
            _check_payload(
                "summary_min_length",
                short_summary_rows,
                short_summary_rows == 0,
                "0 rows shorter than 40 characters",
            )
        )
    else:
        short_summary_rows = None

    if text_missing is not None:
        checks.append(
            _check_payload("text_for_embedding_not_null", text_missing, text_missing == 0, "0 missing", "critical")
        )

    if "age_days" in df.columns:
        age_days = pd.to_numeric(df["age_days"], errors="coerce")
        age_days_missing = int(age_days.isna().sum())
        stale_rows = int((age_days > settings.freshness_threshold_days).sum())
        negative_age_rows = int((age_days < 0).sum())
        checks.extend(
            [
                _check_payload("age_days_not_null", age_days_missing, age_days_missing == 0, "0 missing"),
                _check_payload("age_days_not_negative", negative_age_rows, negative_age_rows == 0, "0 negative rows"),
                _check_payload(
                    "freshness_threshold",
                    stale_rows,
                    stale_rows == 0,
                    f"0 rows older than {settings.freshness_threshold_days} days",
                ),
            ]
        )
    else:
        age_days_missing = None
        stale_rows = None
        negative_age_rows = None

    failed_checks = [check for check in checks if not check["passed"]]
    payload: dict[str, Any] = {
        "report_name": report_path.name,
        "total_rows": total_rows,
        "is_valid": not any(check["severity"] == "critical" and not check["passed"] for check in checks),
        "passed_checks": len(checks) - len(failed_checks),
        "failed_checks": len(failed_checks),
        "signals": {
            "row_count": total_rows,
            "paper_id_missing": paper_id_missing,
            "paper_id_duplicate_rows": paper_id_duplicate_rows,
            "duplicate_paper_id_examples": duplicate_ids,
            "title_missing": title_missing,
            "summary_missing": summary_missing,
            "short_summary_rows": short_summary_rows,
            "text_for_embedding_missing": text_missing,
            "age_days_missing": age_days_missing,
            "negative_age_rows": negative_age_rows,
            "stale_rows": stale_rows,
            "freshness_threshold_days": settings.freshness_threshold_days,
        },
        "checks": checks,
    }
    write_json(report_path, payload)
    return payload


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """Summarize published-date freshness and write a JSON report."""
    report_path = Path(report_path)
    total_rows = int(len(df))

    published = pd.to_datetime(df["published"], utc=True, errors="coerce") if "published" in df.columns else pd.Series(dtype="datetime64[ns, UTC]")
    age_days = pd.to_numeric(df["age_days"], errors="coerce") if "age_days" in df.columns else pd.Series(dtype="float64")

    valid_published = published.dropna()
    stale_mask = age_days > settings.freshness_threshold_days
    stale_rows = int(stale_mask.sum()) if not age_days.empty else None
    missing_published_rows = int(published.isna().sum()) if len(published) else total_rows
    missing_age_days_rows = int(age_days.isna().sum()) if len(age_days) else total_rows

    latest = valid_published.max() if not valid_published.empty else None
    oldest = valid_published.min() if not valid_published.empty else None

    payload: dict[str, Any] = {
        "total_rows": total_rows,
        "latest_published": latest.isoformat() if latest is not None else None,
        "oldest_published": oldest.isoformat() if oldest is not None else None,
        "stale_rows": stale_rows,
        "missing_published_rows": missing_published_rows,
        "missing_age_days_rows": missing_age_days_rows,
        "freshness_threshold_days": settings.freshness_threshold_days,
        "is_fresh": bool(total_rows > 0 and stale_rows == 0 and missing_published_rows == 0 and missing_age_days_rows == 0),
    }
    write_json(report_path, payload)
    return payload
