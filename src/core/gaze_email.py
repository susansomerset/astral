"""AST-1090: gaze_email mailbox runner for the null-candidate dispatch row.

Stage 2 lands the stub so dispatcher imports resolve; Stage 3 fills the body.
"""

from __future__ import annotations


async def run_gaze_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """AST-1090: process Astral inbox for the null-candidate gaze_email dispatch row."""
    del task, debug  # stub — Stage 3
    return {"total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0}
