from __future__ import annotations

import re

from kubeval.domain.models import CheckResult, ERROR, FAIL, PASS, ResourceCheck
from kubeval.infrastructure.kubernetes.kubectl_client import KubectlClient


def matches_name(name: str, match_type: str, match_value: str) -> bool:
    if match_type == "exact":
        return name == match_value
    if match_type == "contains":
        return match_value in name
    if match_type == "regex":
        return re.search(match_value, name) is not None
    return False


def run_resource_check(check: ResourceCheck, client: KubectlClient) -> CheckResult:
    resources, err = client.get_resources(resource=check.resource, namespace=check.namespace)
    if err:
        return CheckResult(check_id=check.check_id, title=check.title, status=ERROR, details=err)

    matches = [r for r in resources if matches_name(r.name, check.match_type, check.match_value)]
    if len(matches) >= check.min_count:
        matched_text = ", ".join(f"{r.namespace}/{r.name}" for r in matches)
        return CheckResult(
            check_id=check.check_id,
            title=check.title,
            status=PASS,
            details=f"Found: {matched_text}",
        )

    ns_text = check.namespace if check.namespace else "all namespaces"
    return CheckResult(
        check_id=check.check_id,
        title=check.title,
        status=FAIL,
        details=(
            f"Expected at least {check.min_count} match(es) for {check.resource} "
            f"in {ns_text}; none matched {check.match_type}='{check.match_value}'"
        ),
    )


def run_checks(checks: list[ResourceCheck], client: KubectlClient) -> list[CheckResult]:
    return [run_resource_check(check, client) for check in checks]
