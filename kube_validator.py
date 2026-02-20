#!/usr/bin/env python3
"""Compatibility wrapper for the modular kubeval CLI."""

from kubeval.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

