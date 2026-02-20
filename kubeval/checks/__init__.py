from __future__ import annotations

from kubeval.checks.builtin import builtin_checks
from kubeval.checks.custom import load_custom_checks
from kubeval.checks.policies import enforce_autoscaling_coverage

__all__ = ["builtin_checks", "enforce_autoscaling_coverage", "load_custom_checks"]
