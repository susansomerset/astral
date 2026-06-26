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


def _write_entries(entries: list[dict]) -> None:
    if not isinstance(entries, list):
        raise ValueError(f"merge ticket log must be a JSON array, got {type(entries).__name__}")
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


def rewrite_merge_ticket_log(entries: list[dict]) -> None:
    """Replace log contents atomically (prune / lifecycle tooling)."""
    _write_entries(entries)


def rebuild_merge_ticket_log(entries: list[dict]) -> None:
    """Replace log contents from prep-uat rebuild (AST-800)."""
    rewrite_merge_ticket_log(entries)


def append_merge_ticket_log(ticket_id: str) -> dict:
    """Record parent id for deploy UI. Re-prep-uat of same id updates timestamp only."""
    normalized = _normalize_ticket_id(ticket_id)
    recorded_at = datetime.now(timezone.utc).isoformat()
    entry = {"ticket_id": normalized, "recorded_at": recorded_at}
    entries = read_merge_ticket_log()
    entries = [e for e in entries if e.get("ticket_id") != normalized]
    entries.append(entry)
    _write_entries(entries)
    return entry


def remove_merge_ticket_log(ticket_id: str) -> bool:
    """Drop one parent id from the log. Returns True when an entry was removed."""
    normalized = _normalize_ticket_id(ticket_id)
    entries = read_merge_ticket_log()
    filtered = [e for e in entries if e.get("ticket_id") != normalized]
    if len(filtered) == len(entries):
        return False
    _write_entries(filtered)
    return True
