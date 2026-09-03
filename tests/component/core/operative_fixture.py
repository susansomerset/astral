"""Test-only registry for pilot base_resume current-read bodies (AST-1587)."""

from __future__ import annotations

from typing import Any

OPERATIVE_BODY_BY_CID: dict[str, Any] = {}


def register_operative_base(candidate_id: str, body: Any) -> None:
    """Wire operative current-read body for a candidate id in component tests."""
    cid = (candidate_id or "").strip()
    if cid:
        OPERATIVE_BODY_BY_CID[cid] = body


def clear_operative_bases() -> None:
    OPERATIVE_BODY_BY_CID.clear()
