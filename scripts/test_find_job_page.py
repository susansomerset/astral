#!/usr/bin/env python3
"""
DEPRECATED (AST-721): monolithic find_job_page removed.

Use decomposed dispatch instead:
  PREFILTER_PASSED → fetch_job_pages → PJL_READY → select_job_page
  → JOBLIST_IDENTIFIED → parse_job_list → WATCH

See docs/features/roster/ast-721-parse-job-list-dispatch-refactor.md
"""

import sys

print(__doc__)
sys.exit(1)
