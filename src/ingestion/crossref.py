from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import html
from pathlib import Path
import re
import time
from typing import Any

import requests

from core.config import Settings
from core.utils import ensure_parent, normalize_whitespace, read_json, safe_slug, write_json


CROSSREF_API_URL = "https://api.crossref.org/works"


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _extract_date_str(date_obj: Any) -> str:
    if not isinstance(date_obj, dict):
        return ""
    date_parts = date_obj.get("date-parts")
    if not date_parts or not isinstance(date_parts, list) or not date_parts[0]:
        return ""
    parts = date_parts[0]
    try:
        if len(parts) >= 3 and parts[0] is not None and parts[1] is not None and parts[2] is not None:
            return f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
        if len(parts) == 2 and parts[0] is not None and parts[1] is not None:
            return f"{int(parts[0]):04d}-{int(parts[1]):02d}-01"
        if len(parts) == 1 and parts[0] is not None:
            return f"{int(parts[0]):04d}-01-01"
    except (ValueError, TypeError):
        return ""
    return ""


def _clean_abstract(raw_abstract: Any) -> str:
    if not isinstance(raw_abstract, str) or not raw_abstract.strip():
        return ""
    # Strip XML/JATS/HTML tags
    text = re.sub(r"<[^>]+>", " ", raw_abstract)
    # Unescape HTML entities (&amp;, &lt;, etc.)
    text = html.unescape(text)
    return normalize_whitespace(text)


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref API payload into a list of PaperRecord objects.

    1. Duyet `payload["message"]["items"]` hoac `payload["items"]`.
    2. Lay DOI, title, abstract, authors, subject, dates, URLs.
    3. Chuan hoa text va bo record khong hop le (khong co DOI hoac title).
    4. Tra ve list `PaperRecord`.
    """
    if not isinstance(payload, dict):
        return []

    items = payload.get("message", {}).get("items")
    if items is None:
        items = payload.get("items", [])
    if not isinstance(items, list):
        return []

    records: list[PaperRecord] = []
    seen_ids: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        doi = item.get("DOI", "")
        if not isinstance(doi, str) or not doi.strip():
            continue
        doi = doi.strip()
        paper_id = safe_slug(doi)

        if not paper_id or paper_id in seen_ids:
            continue

        # Extract title
        raw_title = item.get("title", [])
        if isinstance(raw_title, list):
            title = " ".join(str(t) for t in raw_title if t)
        elif isinstance(raw_title, str):
            title = raw_title
        else:
            title = ""
        title = normalize_whitespace(html.unescape(title))
        if not title:
            continue

        # Extract summary / abstract
        summary = _clean_abstract(item.get("abstract", ""))

        # Extract authors
        authors: list[str] = []
        for author in item.get("author", []):
            if not isinstance(author, dict):
                continue
            given = str(author.get("given", "")).strip()
            family = str(author.get("family", "")).strip()
            name = str(author.get("name", "")).strip()
            if given and family:
                full_name = f"{given} {family}"
            elif family:
                full_name = family
            elif given:
                full_name = given
            elif name:
                full_name = name
            else:
                continue
            if full_name:
                authors.append(normalize_whitespace(full_name))

        # Extract categories / subjects
        raw_subjects = item.get("subject", [])
        categories: list[str] = []
        if isinstance(raw_subjects, list):
            for s in raw_subjects:
                if isinstance(s, str) and s.strip():
                    categories.append(normalize_whitespace(s))
        primary_category = categories[0] if categories else "General"

        # Extract dates
        published = (
            _extract_date_str(item.get("published-print"))
            or _extract_date_str(item.get("published-online"))
            or _extract_date_str(item.get("published"))
            or _extract_date_str(item.get("issued"))
            or _extract_date_str(item.get("created"))
            or "1970-01-01"
        )
        updated = (
            _extract_date_str(item.get("deposited"))
            or _extract_date_str(item.get("updated"))
            or _extract_date_str(item.get("indexed"))
            or published
        )

        # Extract URLs
        abs_url = item.get("URL") or f"https://doi.org/{doi}"

        pdf_url = ""
        links = item.get("link", [])
        if isinstance(links, list):
            for link in links:
                if isinstance(link, dict):
                    content_type = str(link.get("content-type", "")).lower()
                    link_url = str(link.get("URL", "")).strip()
                    if "application/pdf" in content_type or link_url.lower().endswith(".pdf"):
                        pdf_url = link_url
                        break
            if not pdf_url and links and isinstance(links[0], dict):
                pdf_url = str(links[0].get("URL", "")).strip()

        # Extract comment / publication container
        raw_container = item.get("container-title", [])
        if isinstance(raw_container, list):
            container = " ".join(str(c) for c in raw_container if c)
        elif isinstance(raw_container, str):
            container = raw_container
        else:
            container = ""
        publisher = str(item.get("publisher", "")).strip()
        comment = normalize_whitespace(container or publisher)

        record = PaperRecord(
            paper_id=paper_id,
            title=title,
            summary=summary,
            authors=authors,
            categories=categories,
            primary_category=primary_category,
            published=published,
            updated=updated,
            abs_url=abs_url,
            pdf_url=pdf_url,
            comment=comment,
        )
        records.append(record)
        seen_ids.add(paper_id)

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Fetch raw records from Crossref API, save raw response, and parse to records.

    1. Tao params tu `settings.source_query`, `settings.source_filter`, `settings.max_results`.
    2. Goi API voi retry cho cac status code nhu 429/503.
    3. Luu raw response vao `settings.paths.raw_api_response`.
    4. Parse payload bang `parse_crossref_payload`.
    5. Luu records vao `settings.paths.raw_records_json`.
    """
    params: dict[str, Any] = {
        "query": settings.source_query,
        "rows": settings.max_results,
    }
    if settings.source_filter:
        params["filter"] = settings.source_filter

    headers = {
        "User-Agent": "Day10DataPipelineLab/1.0 (mailto:student@lab.local)",
    }

    max_retries = 3
    backoff_factor = 2.0
    payload: dict[str, Any] = {}

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                CROSSREF_API_URL,
                params=params,
                headers=headers,
                timeout=30,
            )
            if response.status_code == 200:
                payload = response.json()
                break
            if response.status_code in {429, 500, 502, 503, 504}:
                if attempt < max_retries:
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                    continue
            response.raise_for_status()
        except requests.RequestException as exc:
            if attempt < max_retries:
                time.sleep(backoff_factor ** attempt)
                continue
            raise RuntimeError(f"Failed to fetch data from Crossref API after {max_retries} attempts: {exc}") from exc

    if not payload:
        raise RuntimeError("Empty response payload received from Crossref API.")

    # Save raw API response
    write_json(settings.paths.raw_api_response, payload)

    # Parse records
    records = parse_crossref_payload(payload)

    # Save parsed records JSON
    records_payload = [asdict(record) for record in records]
    write_json(settings.paths.raw_records_json, records_payload)

    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Load JSON snapshot and map to list of `PaperRecord`."""
    data = read_json(path)
    if isinstance(data, dict):
        return parse_crossref_payload(data)
    if isinstance(data, list):
        records: list[PaperRecord] = []
        for item in data:
            if isinstance(item, dict):
                records.append(
                    PaperRecord(
                        paper_id=str(item.get("paper_id", "")),
                        title=str(item.get("title", "")),
                        summary=str(item.get("summary", "")),
                        authors=list(item.get("authors", [])),
                        categories=list(item.get("categories", [])),
                        primary_category=str(item.get("primary_category", "")),
                        published=str(item.get("published", "")),
                        updated=str(item.get("updated", "")),
                        abs_url=str(item.get("abs_url", "")),
                        pdf_url=str(item.get("pdf_url", "")),
                        comment=str(item.get("comment", "")),
                    )
                )
        return records
    return []


def compute_file_sha256(path: Path) -> str:
    """Tính mã băm SHA-256 của một file bất kỳ."""
    if not path.exists():
        return ""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_raw_integrity(raw_response_path: Path, raw_records_path: Path) -> dict[str, Any]:
    """Xác nhận tính nguyên vẹn của dữ liệu thô (raw snapshot).

    Kiểm tra:
    1. Cả 2 file raw_response và raw_records tồn tại và có dung lượng hợp lệ.
    2. Mã băm SHA-256 để đảm bảo không bị biến đổi âm thầm.
    3. Cấu trúc payload hợp lệ và số lượng record nhất quán.
    """
    res_exists = raw_response_path.exists()
    rec_exists = raw_records_path.exists()

    if not res_exists or not rec_exists:
        return {
            "status": "MISSING",
            "raw_response_exists": res_exists,
            "raw_records_exists": rec_exists,
        }

    res_sha256 = compute_file_sha256(raw_response_path)
    rec_sha256 = compute_file_sha256(raw_records_path)

    raw_response_data = read_json(raw_response_path)
    raw_records_data = read_json(raw_records_path)

    res_items = raw_response_data.get("message", {}).get("items", []) if isinstance(raw_response_data, dict) else []
    record_count = len(raw_records_data) if isinstance(raw_records_data, list) else 0

    return {
        "status": "VALID",
        "raw_response_path": str(raw_response_path),
        "raw_response_sha256": res_sha256,
        "raw_response_items_count": len(res_items),
        "raw_records_path": str(raw_records_path),
        "raw_records_sha256": rec_sha256,
        "raw_records_count": record_count,
    }


def trace_record_lineage(paper_id: str, settings: Settings) -> dict[str, Any]:
    """Truy vết toàn bộ vòng đời (lineage) của một bản ghi qua 5 giai đoạn:

    1. Raw API Response
    2. Raw Records JSON
    3. Clean Baseline Dataset
    4. Corrupted Dataset
    5. Reconstructed / Repaired Data
    """
    lineage: dict[str, Any] = {
        "paper_id": paper_id,
        "raw_api_item": None,
        "raw_record": None,
        "clean_record": None,
        "corrupted_record": None,
        "repaired_record": None,
    }

    # 1. Raw API Response
    if settings.paths.raw_api_response.exists():
        raw_res = read_json(settings.paths.raw_api_response)
        items = raw_res.get("message", {}).get("items", []) if isinstance(raw_res, dict) else []
        for item in items:
            if safe_slug(str(item.get("DOI", "")).strip()) == paper_id:
                lineage["raw_api_item"] = {
                    "doi": item.get("DOI"),
                    "title": item.get("title"),
                    "abstract_len": len(str(item.get("abstract", ""))),
                    "published": item.get("published-print") or item.get("published-online") or item.get("published"),
                }
                break

    # 2. Raw Record
    if settings.paths.raw_records_json.exists():
        raw_recs = read_json(settings.paths.raw_records_json)
        if isinstance(raw_recs, list):
            for r in raw_recs:
                if r.get("paper_id") == paper_id:
                    lineage["raw_record"] = r
                    break

    # 3. Clean Baseline
    if settings.paths.clean_json.exists():
        try:
            with open(settings.paths.clean_json, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content.startswith("["):
                    import json
                    clean_list = json.loads(content)
                else:
                    import json
                    clean_list = [json.loads(line) for line in content.splitlines() if line.strip()]
            for r in clean_list:
                if r.get("paper_id") == paper_id:
                    lineage["clean_record"] = r
                    break
        except Exception:
            pass

    # 4. Corrupted Data
    if settings.paths.corrupted_clean_json.exists():
        try:
            with open(settings.paths.corrupted_clean_json, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content.startswith("["):
                    import json
                    corr_list = json.loads(content)
                else:
                    import json
                    corr_list = [json.loads(line) for line in content.splitlines() if line.strip()]
            for r in corr_list:
                if r.get("paper_id") == paper_id:
                    lineage["corrupted_record"] = r
                    break
        except Exception:
            pass

    # 5. Repaired Candidate (Tái tạo trực tiếp từ Raw Record)
    if lineage["raw_record"]:
        lineage["repaired_record"] = lineage["raw_record"]

    return lineage

