"""Durable Contact @Estelle activity summary (AST-1094). Values only — no logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


def _activity_path() -> Path:
    return Path(ASTRAL_CONFIG["db_dir"]) / str(CONTACT_CONFIG["activity_state_filename"])


def _empty_store() -> dict:
    return {"by_slack_user_id": {}}


def load_estelle_activity_store() -> dict:
    """Return ``{"by_slack_user_id": {<id>: <row>}}``. Missing/corrupt → empty store."""
    path = _activity_path()
    if not path.is_file():
        return _empty_store()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return _empty_store()
    if not isinstance(raw, dict):
        return _empty_store()
    by = raw.get("by_slack_user_id")
    if not isinstance(by, dict):
        return _empty_store()
    # Keep only string keys → dict rows (drop garbage entries).
    cleaned: dict[str, dict] = {}
    for k, v in by.items():
        if isinstance(k, str) and k.strip() and isinstance(v, dict):
            cleaned[k] = v
    return {"by_slack_user_id": cleaned}


def save_estelle_activity_store(store: dict) -> None:
    """Write the activity store (creates parent dirs as needed)."""
    if not isinstance(store, dict):
        raise TypeError("store must be dict")
    by = store.get("by_slack_user_id")
    if not isinstance(by, dict):
        raise TypeError("store.by_slack_user_id must be dict")
    path = _activity_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"by_slack_user_id": by}, indent=2) + "\n",
        encoding="utf-8",
    )


def record_estelle_activity(
    *,
    slack_user_id: str,
    bind_ok: bool,
    astral_candidate_id: Optional[str],
    candidate_state: Optional[str],
    last_channel: Optional[str],
    last_message_ts: Optional[str],
) -> dict:
    """Upsert one Slack user: increment inbound count; refresh bind + last seen.

    Returns the updated row dict. Raises ``TypeError`` if ``slack_user_id`` is empty
    or ``bind_ok`` is not bool.
    """
    if not isinstance(slack_user_id, str) or not slack_user_id.strip():
        raise TypeError("slack_user_id must be non-empty str")
    if not isinstance(bind_ok, bool):
        raise TypeError("bind_ok must be bool")
    uid = slack_user_id.strip()
    store = load_estelle_activity_store()
    by = store["by_slack_user_id"]
    prev = by.get(uid) if isinstance(by.get(uid), dict) else {}
    prev_count = prev.get("inbound_message_count")
    count = int(prev_count) + 1 if isinstance(prev_count, int) and prev_count >= 0 else 1
    row = {
        "slack_user_id": uid,
        "bind_ok": bind_ok,
        "astral_candidate_id": astral_candidate_id if isinstance(astral_candidate_id, str) else None,
        "candidate_state": candidate_state if isinstance(candidate_state, str) else None,
        "inbound_message_count": count,
        "last_channel": last_channel if isinstance(last_channel, str) and last_channel else None,
        "last_message_ts": last_message_ts if isinstance(last_message_ts, str) and last_message_ts else None,
    }
    by[uid] = row
    save_estelle_activity_store(store)
    return row


def list_estelle_activity_rows() -> list[dict[str, Any]]:
    """All activity rows, sorted by ``last_message_ts`` descending (empty last)."""
    by = load_estelle_activity_store()["by_slack_user_id"]
    rows = [dict(v) for v in by.values() if isinstance(v, dict)]
    # Slack ``ts`` strings sort lexicographically in time order.
    rows.sort(key=lambda r: str(r.get("last_message_ts") or ""), reverse=True)
    return rows
