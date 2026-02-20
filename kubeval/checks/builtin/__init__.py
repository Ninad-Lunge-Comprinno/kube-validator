from __future__ import annotations

import json
from pathlib import Path

from kubeval.models import ResourceCheck, VALID_MATCH_TYPES

_BUILTIN_CHECK_FILES = [
    Path(__file__).with_name("metrics-server") / "check.json",
    Path(__file__).with_name("cluster-autoscaler") / "check.json",
    Path(__file__).with_name("karpenter") / "check.json",
    Path(__file__).with_name("ebs-csi-driver-controller") / "check.json",
    Path(__file__).with_name("ebs-csi-driver-node") / "check.json",
    Path(__file__).with_name("vpc-cni") / "check.json",
    Path(__file__).with_name("coredns") / "check.json",
    Path(__file__).with_name("kube-proxy") / "check.json",
]


def _load_builtin_check(path: Path) -> ResourceCheck:
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    try:
        match_type = str(raw.get("match_type", "contains"))
        if match_type not in VALID_MATCH_TYPES:
            raise ValueError(f"unsupported match_type '{match_type}'")

        return ResourceCheck(
            check_id=str(raw["id"]),
            title=str(raw["title"]),
            resource=str(raw["resource"]),
            namespace=raw.get("namespace"),
            match_type=match_type,
            match_value=str(raw["match_value"]),
            min_count=int(raw.get("min_count", 1)),
        )
    except KeyError as exc:
        raise ValueError(f"Invalid built-in check definition '{path}': missing key {exc}") from exc


def builtin_checks() -> list[ResourceCheck]:
    return [_load_builtin_check(path) for path in _BUILTIN_CHECK_FILES]
