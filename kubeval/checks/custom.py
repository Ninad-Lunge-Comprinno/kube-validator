from __future__ import annotations

import json

from kubeval.models import ResourceCheck, VALID_MATCH_TYPES


def load_custom_checks(path: str) -> list[ResourceCheck]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    checks: list[ResourceCheck] = []
    for idx, raw in enumerate(data.get("checks", []), start=1):
        try:
            match_type = str(raw.get("match_type", "contains"))
            if match_type not in VALID_MATCH_TYPES:
                raise ValueError(
                    f"Invalid custom check #{idx}: unsupported match_type '{match_type}'"
                )

            checks.append(
                ResourceCheck(
                    check_id=str(raw["id"]),
                    title=str(raw["title"]),
                    resource=str(raw["resource"]),
                    namespace=raw.get("namespace"),
                    match_type=match_type,
                    match_value=str(raw["match_value"]),
                    min_count=int(raw.get("min_count", 1)),
                )
            )
        except KeyError as exc:
            raise ValueError(f"Invalid custom check #{idx}: missing key {exc}") from exc
    return checks
