#!/usr/bin/env python3
"""One-off: ensure every candidate (and template) has a fetch_timesheet dispatch_task row (AST-2218)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.core.dispatcher import provision_fetch_timesheet_dispatch_tasks

if __name__ == "__main__":
    print(provision_fetch_timesheet_dispatch_tasks())
