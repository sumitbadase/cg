"""Functional safety (FuSa) classification for CFUSA safety dashboard views."""

from __future__ import annotations

from typing import Any

# ASIL-inspired mapping for dashboard visualization (QM = non-safety).
ASIL_LEVELS = ("ASIL-D", "ASIL-C", "ASIL-B", "ASIL-A", "QM")

SAFETY_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "braking": ["brake", "abs", "esc"],
    "steering": ["steer", "eps", "lane"],
    "powertrain": ["engine", "motor", "powertrain", "battery"],
    "sensing": ["sensor", "lidar", "radar", "camera"],
    "diagnostics": ["diagnostic", "dtc", "uds"],
    "platform": ["kernel", "driver", "hal", "boot"],
}


def classify_functional_safety(file_record: dict[str, Any], criticality_score: int) -> dict[str, Any]:
    """Assign FuSa/CFUSA safety attributes to a file based on path and criticality."""
    path = file_record.get("path", "").lower()
    domains = [
        domain
        for domain, keywords in SAFETY_DOMAIN_KEYWORDS.items()
        if any(keyword in path for keyword in keywords)
    ]

    asil_level = _map_score_to_asil(criticality_score, domains)
    compliance_gaps = _detect_compliance_gaps(path, criticality_score)

    return {
        "path": file_record.get("path", ""),
        "asil_level": asil_level,
        "safety_domains": domains or ["general"],
        "requires_safety_review": asil_level in {"ASIL-D", "ASIL-C", "ASIL-B"},
        "compliance_gaps": compliance_gaps,
    }


def summarize_safety_metrics(safety_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-file FuSa classifications into dashboard metrics."""
    asil_distribution = {level: 0 for level in ASIL_LEVELS}
    domain_distribution: dict[str, int] = {}
    review_required = 0
    gap_counts: dict[str, int] = {}

    for record in safety_records:
        asil_distribution[record["asil_level"]] = asil_distribution.get(record["asil_level"], 0) + 1
        if record["requires_safety_review"]:
            review_required += 1
        for domain in record["safety_domains"]:
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        for gap in record["compliance_gaps"]:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1

    return {
        "asil_distribution": asil_distribution,
        "domain_distribution": domain_distribution,
        "files_requiring_safety_review": review_required,
        "compliance_gap_summary": gap_counts,
        "cfusa_readiness_score": _cfusa_readiness_score(asil_distribution, gap_counts, len(safety_records)),
    }


def _map_score_to_asil(score: int, domains: list[str]) -> str:
    if score >= 80 and domains:
        return "ASIL-D"
    if score >= 65:
        return "ASIL-C"
    if score >= 45:
        return "ASIL-B"
    if score >= 25:
        return "ASIL-A"
    return "QM"


def _detect_compliance_gaps(path: str, score: int) -> list[str]:
    gaps: list[str] = []
    if score >= 45 and "test" not in path and "tests" not in path:
        gaps.append("missing_linked_safety_test")
    if score >= 65 and not any(token in path for token in ("doc", "safety", "hazard")):
        gaps.append("missing_safety_documentation")
    if score >= 80 and "watchdog" not in path:
        gaps.append("watchdog_coverage_unknown")
    return gaps


def _cfusa_readiness_score(
    asil_distribution: dict[str, int],
    gap_counts: dict[str, int],
    total_files: int,
) -> float:
    if total_files == 0:
        return 0.0

    weighted_risk = (
        asil_distribution.get("ASIL-D", 0) * 1.0
        + asil_distribution.get("ASIL-C", 0) * 0.8
        + asil_distribution.get("ASIL-B", 0) * 0.6
        + asil_distribution.get("ASIL-A", 0) * 0.3
    )
    gap_penalty = sum(gap_counts.values()) * 0.05
    normalized_risk = min(weighted_risk / total_files, 1.0)
    readiness = max(0.0, 1.0 - normalized_risk - gap_penalty)
    return round(readiness * 100, 2)
