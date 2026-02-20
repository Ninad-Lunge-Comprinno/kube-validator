from __future__ import annotations

from kubeval.models import CheckResult, FAIL, PASS


def enforce_autoscaling_coverage(results: list[CheckResult]) -> None:
    autoscaler = next((r for r in results if r.check_id == "cluster-autoscaler"), None)
    karpenter = next((r for r in results if r.check_id == "karpenter"), None)
    if autoscaler is None or karpenter is None:
        return

    if autoscaler.status == PASS and karpenter.status == FAIL:
        karpenter.status = PASS
        karpenter.details = "Optional: Karpenter not installed, Cluster Autoscaler is present."
    elif karpenter.status == PASS and autoscaler.status == FAIL:
        autoscaler.status = PASS
        autoscaler.details = "Optional: Cluster Autoscaler not installed, Karpenter is present."
