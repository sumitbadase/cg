"""Regular expression patterns for CPP query parsing."""

from __future__ import annotations

import re

# Named regex patterns used when parsing CPP queries and change descriptions.
CPP_REGEX_PATTERNS: dict[str, re.Pattern[str]] = {
    # TODO: Define patterns for service names, endpoints, database objects, etc.
    "service_name": re.compile(r""),  # placeholder
    "endpoint_path": re.compile(r""),  # placeholder
    "table_name": re.compile(r""),  # placeholder
}
