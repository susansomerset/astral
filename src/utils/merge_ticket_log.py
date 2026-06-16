"""Merge ticket log for deploy status (AST-681). Prep-uat records parent ids."""

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from src.utils.config import MERGE_TICKET_LOG_CONFIG

_TICKET_ID_RE = re.compile(r"^AST-\d+$")


def _log_path() -> Path:
    return Path(MERGE_TICKET_LOG_CONFIG["log_path"])


def _normalize_ticket_id(raw: str) -> str:
    ticket_id = (raw or "").strip().upper()
    if not _TICKET_ID_RE.match(ticket_id):
        raise ValueError(f"invalid ticket id: {raw!r} (expected AST-<number>)")
    return ticket_id


def read_merge_ticket_log() -> list[dict]:
    path = _log_path()
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError(f"merge ticket log must be a JSON array, got {type(data).__name__}")
    return data


def append_merge_ticket_log(ticket_id: str) -> dict:
    """Record parent id for deploy UI. Re-prep-uat of same id updates timestamp only."""
    normalized = _normalize_ticket_id(ticket_id)
    recorded_at = datetime.now(timezone.utc).isoformat()
    entry = {"ticket_id": normalized, "recorded_at": recorded_at}
    entries = read_merge_ticket_log()
    entries = [e for e in entries if e.get("ticket_id") != normalized]
    entries.append(entry)
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        Path(tmp_name).replace(path)
    except Exception:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    return entry
