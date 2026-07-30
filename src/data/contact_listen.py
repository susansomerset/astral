"""Durable Contact Slack listen flag (AST-1067). Values only — no logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


def _listen_path() -> Path:
    return Path(ASTRAL_CONFIG["db_dir"]) / str(CONTACT_CONFIG["listen_state_filename"])


def load_contact_listen_enabled() -> Optional[bool]:
    """Return persisted listen bool, or None if missing/unreadable/invalid."""
    path = _listen_path()
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    val = raw.get("listen_enabled")
    if not isinstance(val, bool):
        return None
    return val


def save_contact_listen_enabled(enabled: bool) -> None:
    """Write ``{"listen_enabled": <bool>}`` (creates parent dirs as needed)."""
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    path = _listen_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"listen_enabled": enabled}, indent=2) + "\n",
        encoding="utf-8",
    )
