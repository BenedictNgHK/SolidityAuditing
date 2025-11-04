#!/usr/bin/env python3
"""
Legacy CLI entry point - redirects to new CLI structure.
"""

from solidity_auditing.cli.commands import main

if __name__ == "__main__":
    exit(main())