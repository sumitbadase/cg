"""Prompt templates for AI-driven change analysis."""

from __future__ import annotations

from typing import Any

CHANGE_ANALYSIS_SYSTEM_PROMPT = """\
You are an expert software change analyst. Given JIRA ticket details, GitHub PR \
diffs, and optional graph context, produce a concise impact assessment covering \
risk level, affected services, and recommended review steps.
"""


def build_change_analysis_prompt(
    jira_data: dict[str, Any] | None = None,
    pr_data: dict[str, Any] | None = None,
    graph_context: dict[str, Any] | None = None,
) -> str:
    """Build the user prompt for a change analysis LLM call.

    Args:
        jira_data: Normalized JIRA issue fields.
        pr_data: Normalized pull request and diff summary.
        graph_context: Related graph nodes and edges for impact tracing.

    Returns:
        Formatted prompt string ready for the LLM.
    """
    # TODO: Render structured sections from input data with token budget controls
    sections: list[str] = ["Analyze the following change:"]

    if jira_data:
        sections.append(f"JIRA: {jira_data}")
    if pr_data:
        sections.append(f"PR: {pr_data}")
    if graph_context:
        sections.append(f"Graph context: {graph_context}")

    return "\n\n".join(sections)
