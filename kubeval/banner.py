from __future__ import annotations

import sys

RESET = "\033[0m"
RED = "\033[91m"
ORANGE = "\033[38;5;208m"
YELLOW = "\033[93m"
GOLD = "\033[38;5;220m"

BANNER = r"""
█▄▀ █ █ █▄▄ █▀▀   █ █ ▄▀█ █   █ █▀▄ ▄▀█ ▀█▀ █▀█ █▀█
█ █ █▄█ █▄█ ██▄   ▀▄▀ █▀█ █▄▄ █ █▄▀ █▀█  █  █▄█ █▀▄
               E  K  S   C L U S T E R   C H E C K E R
"""


def print_banner() -> None:
    if sys.stdout.isatty():
        lines = [line for line in BANNER.splitlines() if line.strip()]
        palette = [RED, ORANGE, YELLOW]
        for idx, line in enumerate(lines):
            print(f"{palette[min(idx, len(palette)-1)]}{line}{RESET}")
        print(f"{GOLD}🕹️  CONTRA MODE{RESET}  {YELLOW}⚡ fast checks{RESET}  {ORANGE}🎯 clear signal{RESET}")
    else:
        print(BANNER)
