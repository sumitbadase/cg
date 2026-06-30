"""Aggregate criticality, bug frequency, and FuSa metrics for dashboard APIs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from dashboard.bug_frequency_analyzer import (
    estimate_bug_exposure,
    load_bug_records,
    summarize_bug_frequency,
)
from dashboard.criticality_scorer import score_file_criticality, summarize_criticality
from dashboard.safety_classifier import classify_functional_safety, summarize_safety_metrics
from exceptions import ParserError
from git_integration.inventory_store import InventoryStore
from utils import get_inventory_storage_dir


def build_dashboard_metrics(repository_name: str) -> dict[str, Any]:
    """Build full dashboard metrics for a parsed repository inventory."""
    store = InventoryStore(get_inventory_storage_dir())
    inventory = store.load(repository_name)
    if inventory is None:
        raise ParserError(
            f"No inventory found for repository '{repository_name}'. Run /parse-repository first.",
            details={"repository_name": repository_name},
        )

    file_scores = [score_file_criticality(file_record) for file_record in inventory.get("files", [])]
    criticality_summary = summarize_criticality(file_scores)

    safety_records = [
        classify_functional_safety(
            {"path": item["path"]},
            item["score"],
        )
        for item in file_scores
    ]
    safety_summary = summarize_safety_metrics(safety_records)

    bug_records, data_source = load_bug_records(repository_name)
    if data_source == "estimated":
        bug_records = estimate_bug_exposure(file_scores)
    bug_summary = summarize_bug_frequency(bug_records, data_source=data_source)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "repository_name": repository_name,
        "head_commit": inventory.get("head_commit"),
        "file_count": inventory.get("file_count", 0),
        "criticality": criticality_summary,
        "bug_frequency": bug_summary,
        "functional_safety": safety_summary,
        "cfusa_dashboard": {
            "readiness_score": safety_summary["cfusa_readiness_score"],
            "asil_distribution": safety_summary["asil_distribution"],
            "files_requiring_review": safety_summary["files_requiring_safety_review"],
            "top_compliance_gaps": safety_summary["compliance_gap_summary"],
        },
    }
