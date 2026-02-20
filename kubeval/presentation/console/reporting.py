from __future__ import annotations

import sys
from typing import Any

from kubeval.domain.models import CheckResult, ERROR, FAIL, PASS, ResourceCheck

RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"


def summarize(results: list[CheckResult]) -> dict[str, int]:
    summary = {PASS: 0, FAIL: 0, ERROR: 0}
    for res in results:
        summary[res.status] = summary.get(res.status, 0) + 1
    return summary


def _supports_color() -> bool:
    return sys.stdout.isatty()


def _status_emoji(status: str) -> str:
    if status == PASS:
        return "✅"
    if status == FAIL:
        return "❌"
    if status == ERROR:
        return "⚠️"
    return "•"


def _status_label(status: str) -> str:
    return f"{_status_emoji(status)} {status}"


def _status_colored(text: str, status: str) -> str:
    if not _supports_color():
        return text
    if status == PASS:
        return f"{GREEN}{text}{RESET}"
    if status == FAIL:
        return f"{RED}{text}{RESET}"
    if status == ERROR:
        return f"{YELLOW}{text}{RESET}"
    return text


def _title_emoji(check_id: str) -> str:
    if "metrics" in check_id:
        return "📊"
    if "autoscaler" in check_id or "karpenter" in check_id:
        return "📈"
    if "coredns" in check_id:
        return "🌐"
    if "proxy" in check_id:
        return "🔀"
    if "csi" in check_id:
        return "💾"
    if "cni" in check_id:
        return "🧩"
    return "🔎"


def print_table(results: list[CheckResult]) -> None:
    id_w = max(8, *(len(r.check_id) for r in results))
    status_w = max(8, *(len(_status_label(r.status)) for r in results))
    title_w = max(14, *(len(r.title) + 2 for r in results))
    header = f"{'CHECK ID':<{id_w}}  {'STATUS':<{status_w}}  {'TITLE':<{title_w}}  DETAILS"
    print(header)
    print("-" * len(header))
    for result in results:
        title = f"{_title_emoji(result.check_id)} {result.title}"
        padded_status = f"{_status_label(result.status):<{status_w}}"
        print(
            f"{result.check_id:<{id_w}}  {_status_colored(padded_status, result.status)}  "
            f"{title:<{title_w}}  {result.details}"
        )


def print_checks_catalog(checks: list[ResourceCheck]) -> None:
    id_w = max(8, *(len(c.check_id) for c in checks))
    resource_w = max(8, *(len(c.resource) for c in checks))
    title_w = max(14, *(len(c.title) + 2 for c in checks))
    header = f"{'CHECK ID':<{id_w}}  {'RESOURCE':<{resource_w}}  {'TITLE':<{title_w}}  MATCH"
    print(header)
    print("-" * len(header))
    for check in checks:
        ns_text = check.namespace or "all-namespaces"
        match = f"{check.match_type}:{check.match_value} ({ns_text})"
        title = f"{_title_emoji(check.check_id)} {check.title}"
        print(f"{check.check_id:<{id_w}}  {check.resource:<{resource_w}}  {title:<{title_w}}  {match}")


def to_results_payload(results: list[CheckResult]) -> dict[str, Any]:
    return {
        "summary": summarize(results),
        "results": [r.__dict__ for r in results],
    }


def to_checks_payload(checks: list[ResourceCheck]) -> dict[str, Any]:
    return {
        "count": len(checks),
        "checks": [
            {
                "id": c.check_id,
                "title": c.title,
                "resource": c.resource,
                "namespace": c.namespace,
                "match_type": c.match_type,
                "match_value": c.match_value,
                "min_count": c.min_count,
            }
            for c in checks
        ],
    }
