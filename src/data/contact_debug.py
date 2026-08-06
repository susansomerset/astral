"""Durable Contact Slack debug flag (AST-1206). Values only — no logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


def _debug_path() -> Path:
    return Path(ASTRAL_CONFIG["db_dir"]) / str(CONTACT_CONFIG["debug_state_filename"])


def load_contact_debug_enabled() -> Optional[bool]:
    """Return persisted debug bool, or None if missing/unreadable/invalid."""
    path = _debug_path()
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    val = raw.get("debug_enabled")
    if not isinstance(val, bool):
        return None
    return val


def save_contact_debug_enabled(enabled: bool) -> None:
    """Write ``{"debug_enabled": <bool>}`` (creates parent dirs as needed)."""
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    path = _debug_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"debug_enabled": enabled}, indent=2) + "\n",
        encoding="utf-8",
    )
