#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import threading
import time

from kubeval.application.checks.runner import run_checks, run_resource_check
from kubeval.banner import print_banner
from kubeval.checks import builtin_checks, enforce_autoscaling_coverage, load_custom_checks
from kubeval.domain.models import CheckResult, ERROR, FAIL, PASS, ResourceCheck
from kubeval.infrastructure.kubernetes.kubectl_client import KubectlClient
from kubeval.presentation.console.reporting import (
    print_checks_catalog,
    print_table,
    summarize,
    to_checks_payload,
    to_results_payload,
)

RESET = "\033[0m"
RED = "\033[91m"
ORANGE = "\033[38;5;208m"
YELLOW = "\033[93m"
GREEN = "\033[92m"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate EKS cluster best-practice components with kubectl."
    )
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Run checks against the current cluster")
    scan_parser.add_argument("--context", help="kubectl context to use", default=None)
    scan_parser.add_argument(
        "--checks-file",
        help="Path to JSON file containing additional checks",
        default=None,
    )
    scan_parser.add_argument(
        "--output",
        choices=("table", "json"),
        default="table",
        help="Output format",
    )
    scan_parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Disable pixel banner in table output",
    )
    scan_parser.add_argument(
        "--no-spinner",
        action="store_true",
        help="Disable retro spinner animation during scan",
    )

    list_parser = subparsers.add_parser("list-checks", help="List available built-in checks")
    list_parser.add_argument(
        "--output",
        choices=("table", "json"),
        default="table",
        help="Output format",
    )

    return parser


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        argv = ["scan"]
    elif argv[0] in ("-h", "--help"):
        pass
    elif argv[0].startswith("-"):
        argv = ["scan", *argv]

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        args.command = "scan"
    return args


def _command_scan(args: argparse.Namespace) -> int:
    client = KubectlClient(context=args.context)
    kubectl_err = client.validate()
    if kubectl_err:
        print(f"ERROR: {kubectl_err}", file=sys.stderr)
        return 2

    checks = builtin_checks()
    if args.checks_file:
        try:
            checks.extend(load_custom_checks(args.checks_file))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR: unable to load checks file '{args.checks_file}': {exc}", file=sys.stderr)
            return 2

    use_spinner = args.output == "table" and sys.stdout.isatty() and not args.no_spinner
    results = _run_checks_with_spinner(checks, client) if use_spinner else run_checks(checks, client)
    enforce_autoscaling_coverage(results)
    summary = summarize(results)

    if args.output == "json":
        print(json.dumps(to_results_payload(results), indent=2))
    else:
        if not args.no_banner:
            print_banner()
        print_table(results)
        print()
        print(f"Summary: PASS={summary['PASS']} FAIL={summary['FAIL']} ERROR={summary['ERROR']}")
        print("Note: Cluster scaling is considered covered if Cluster Autoscaler or Karpenter is present.")

    return 1 if summary[FAIL] > 0 or summary[ERROR] > 0 else 0


def _run_checks_with_spinner(
    checks: list[ResourceCheck],
    client: KubectlClient,
) -> list[CheckResult]:
    frames = ["[■□□□□]", "[□■□□□]", "[□□■□□]", "[□□□■□]", "[□□□□■]"]
    frame_colors = [RED, ORANGE, YELLOW]
    status_icons = {
        PASS: f"{GREEN}✅{RESET}",
        FAIL: f"{RED}❌{RESET}",
        ERROR: f"{YELLOW}⚠️{RESET}",
    }
    results = []
    total = len(checks)

    for idx, check in enumerate(checks, start=1):
        stop_event = threading.Event()

        def _spin() -> None:
            frame_idx = 0
            while not stop_event.is_set():
                frame = frames[frame_idx % len(frames)]
                color = frame_colors[frame_idx % len(frame_colors)]
                print(
                    f"\r{color}{frame}{RESET} {YELLOW}Scanning{RESET} {idx}/{total}: {check.title:<45}",
                    end="",
                    flush=True,
                )
                frame_idx += 1
                time.sleep(0.08)

        spinner_thread = threading.Thread(target=_spin, daemon=True)
        spinner_thread.start()
        result = run_resource_check(check, client)
        stop_event.set()
        spinner_thread.join()

        icon = status_icons.get(result.status, "•")
        print("\r\033[2K", end="", flush=True)
        print(
            f"{icon} {ORANGE}Finished{RESET} {idx}/{total}: {check.check_id} -> {result.status:<5}"
        )
        results.append(result)

    print()
    return results


def _command_list_checks(args: argparse.Namespace) -> int:
    checks = builtin_checks()
    if args.output == "json":
        print(json.dumps(to_checks_payload(checks), indent=2))
    else:
        print_banner()
        print_checks_catalog(checks)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.command == "list-checks":
        return _command_list_checks(args)
    return _command_scan(args)
