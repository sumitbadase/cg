"""Score source files by operational and safety criticality."""

from __future__ import annotations

from typing import Any

# Weighted path keywords for safety-critical and high-impact code areas.
CRITICALITY_KEYWORDS: dict[str, int] = {
    "safety": 30,
    "asil": 30,
    "brake": 28,
    "steer": 28,
    "airbag": 28,
    "ecu": 24,
    "fusa": 24,
    "functional-safety": 24,
    "watchdog": 22,
    "diagnostic": 18,
    "crypto": 18,
    "auth": 16,
    "kernel": 16,
    "driver": 14,
    "hal": 14,
    "control": 12,
    "sensor": 12,
    "actuator": 12,
    "security": 12,
    "boot": 10,
}

HIGH_RISK_EXTENSIONS: dict[str, int] = {
    ".c": 8,
    ".cc": 8,
    ".cpp": 8,
    ".h": 6,
    ".hpp": 6,
    ".py": 4,
    ".rs": 5,
    ".go": 4,
}


def score_file_criticality(file_record: dict[str, Any]) -> dict[str, Any]:
    """Compute a 0-100 criticality score for a repository file record."""
    path = file_record.get("path", "").lower()
    extension = file_record.get("extension", "").lower()
    size_bytes = int(file_record.get("size_bytes", 0))

    keyword_score = sum(weight for keyword, weight in CRITICALITY_KEYWORDS.items() if keyword in path)
    extension_score = HIGH_RISK_EXTENSIONS.get(extension, 2)
    size_score = min(size_bytes // 10_000, 15)

    raw_score = keyword_score + extension_score + size_score
    score = min(raw_score, 100)

    if score >= 75:
        level = "critical"
    elif score >= 50:
        level = "high"
    elif score >= 25:
        level = "medium"
    else:
        level = "low"

    matched_keywords = [keyword for keyword in CRITICALITY_KEYWORDS if keyword in path]

    return {
        "path": file_record.get("path", ""),
        "score": score,
        "level": level,
        "matched_keywords": matched_keywords,
        "extension": extension,
        "size_bytes": size_bytes,
    }


def summarize_criticality(file_scores: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate file criticality scores into dashboard summary metrics."""
    if not file_scores:
        return {
            "average_score": 0.0,
            "max_score": 0,
            "distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "top_critical_files": [],
        }

    distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for item in file_scores:
        distribution[item["level"]] = distribution.get(item["level"], 0) + 1

    sorted_files = sorted(file_scores, key=lambda item: item["score"], reverse=True)
    total_score = sum(item["score"] for item in file_scores)

    return {
        "average_score": round(total_score / len(file_scores), 2),
        "max_score": sorted_files[0]["score"],
        "distribution": distribution,
        "top_critical_files": sorted_files[:15],
    }
