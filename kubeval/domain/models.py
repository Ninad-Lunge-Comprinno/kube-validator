from __future__ import annotations

from dataclasses import dataclass

PASS = "PASS"
FAIL = "FAIL"
ERROR = "ERROR"
VALID_MATCH_TYPES = {"exact", "contains", "regex"}


@dataclass
class CheckResult:
    check_id: str
    title: str
    status: str
    details: str


@dataclass
class ResourceRef:
    name: str
    namespace: str


@dataclass
class ResourceCheck:
    check_id: str
    title: str
    resource: str
    namespace: str | None
    match_type: str
    match_value: str
    min_count: int = 1
