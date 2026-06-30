"""Analyze bug frequency metrics for dashboard reporting."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from utils import get_bug_storage_dir

SEVERITY_WEIGHTS = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def load_bug_records(repository_name: str) -> tuple[list[dict[str, Any]], str]:
    """Load bug records for a repository from local storage.

    Returns:
        Tuple of (records, data_source) where data_source is ``recorded`` or ``estimated``.
    """
    bug_path = get_bug_storage_dir() / f"{repository_name}.json"
    if bug_path.exists():
        payload = json.loads(bug_path.read_text(encoding="utf-8"))
        return payload.get("records", []), "recorded"

    return [], "estimated"


def estimate_bug_exposure(file_scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Estimate bug exposure when no recorded bug history exists."""
    estimated: list[dict[str, Any]] = []
    for item in file_scores:
        if item["score"] < 40:
            continue
        severity = "critical" if item["score"] >= 75 else "high" if item["score"] >= 55 else "medium"
        estimated.append(
            {
                "file_path": item["path"],
                "severity": severity,
                "reported_at": datetime.now(UTC).date().isoformat(),
                "category": "estimated_exposure",
                "source": "heuristic",
            }
        )
    return estimated


def summarize_bug_frequency(
    bug_records: list[dict[str, Any]],
    *,
    data_source: str,
) -> dict[str, Any]:
    """Aggregate bug records into dashboard bug-frequency metrics."""
    severity_distribution = Counter(record.get("severity", "medium") for record in bug_records)
    category_distribution = Counter(record.get("category", "unknown") for record in bug_records)
    file_distribution = Counter(record.get("file_path", "unknown") for record in bug_records)

    weighted_score = sum(
        SEVERITY_WEIGHTS.get(record.get("severity", "medium"), 1) for record in bug_records
    )

    top_buggy_files = [
        {"file_path": file_path, "bug_count": count}
        for file_path, count in file_distribution.most_common(10)
    ]

    return {
        "total_bugs": len(bug_records),
        "weighted_bug_score": weighted_score,
        "severity_distribution": dict(severity_distribution),
        "category_distribution": dict(category_distribution),
        "top_buggy_files": top_buggy_files,
        "data_source": data_source,
        "trend": _build_monthly_trend(bug_records),
    }


def _build_monthly_trend(bug_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    monthly = Counter()
    for record in bug_records:
        reported_at = record.get("reported_at", "")
        if not reported_at:
            continue
        month_key = reported_at[:7]
        monthly[month_key] += 1

    return [{"month": month, "count": count} for month, count in sorted(monthly.items())]
