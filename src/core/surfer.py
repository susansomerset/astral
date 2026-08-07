# -*- coding: utf-8 -*-
"""Surfer batch entity — durable client-driven worklist (AST-1229).

HTTP / page_intake wiring is siblings AST-1230 / AST-1231.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.core.candidate import get_candidate, save_candidate_data
from src.data import database
from src.utils.config import SURFER_BATCH_CONFIG
from src.utils.logging import get_logger

logger = get_logger(__name__)


def create_surfer_batch(
    candidate_id: str,
    urls: List[str],
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Create a RUNNING Surfer batch with URL worklist; set candidate lifecycle pointer."""
    logger.set_debug_flag(debug)
    cid = (candidate_id or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if get_candidate(cid) is None:
        raise ValueError(f"Candidate not found: {cid}")

    if not isinstance(urls, list) or not urls:
        raise ValueError("urls must be a non-empty list")
    cleaned: List[str] = []
    seen: set[str] = set()
    for raw in urls:
        u = (raw or "").strip() if isinstance(raw, str) else ""
        if not u:
            raise ValueError("urls entries must be non-empty strings")
        if u in seen:
            continue
        seen.add(u)
        cleaned.append(u)
    if not cleaned:
        raise ValueError("urls must be a non-empty list")

    existing_id = _read_active_pointer(cid)
    if existing_id:
        existing = database.get_surfer_batch(existing_id)
        if existing is not None and not _is_terminal_status(str(existing.get("status") or "")):
            raise ValueError(
                f"Candidate {cid} already has a non-terminal Surfer batch: {existing_id}"
            )
        _set_active_pointer(cid, None, debug=debug)

    batch_id = _new_batch_id()
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    initial_outcome = SURFER_BATCH_CONFIG["initial_url_outcome"]
    url_entries = [
        {"url": u, "outcome": initial_outcome, "updated_at": None} for u in cleaned
    ]
    ok = database.insert_surfer_batch(
        batch_id,
        cid,
        SURFER_BATCH_CONFIG["initial_status"],
        started_at,
        url_entries,
        [],
    )
    if not ok:
        raise RuntimeError(f"Failed to insert surfer_batch: {batch_id}")
    _set_active_pointer(cid, batch_id, debug=debug)
    row = database.get_surfer_batch(batch_id)
    if row is None:
        raise RuntimeError(f"surfer_batch missing after insert: {batch_id}")
    return row


def get_active_surfer_batch(
    candidate_id: str,
    *,
    debug: bool = False,
) -> Optional[Dict[str, Any]]:
    """Return the candidate's non-terminal Surfer batch via lifecycle pointer, or None."""
    logger.set_debug_flag(debug)
    cid = (candidate_id or "").strip()
    pointer = _read_active_pointer(cid)
    if not pointer:
        return None
    batch = database.get_surfer_batch(pointer)
    if batch is None or _is_terminal_status(str(batch.get("status") or "")):
        _set_active_pointer(cid, None, debug=debug)
        return None
    return batch


def transition_surfer_batch_status(
    batch_id: str,
    to_status: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Move a Surfer batch to to_status; clear pointer when landing terminal."""
    logger.set_debug_flag(debug)
    batch = database.get_surfer_batch(batch_id)
    if batch is None:
        raise ValueError(f"surfer_batch not found: {batch_id}")
    cfg = _status_cfg(to_status)
    from_status = str(batch.get("status") or "")
    if to_status == from_status:
        return batch
    if _is_terminal_status(from_status):
        raise ValueError(
            f"Cannot transition terminal surfer_batch {batch_id} from {from_status}"
        )
    if cfg.get("requires_all_urls_terminal"):
        for entry in batch.get("urls") or []:
            outcome = str((entry or {}).get("outcome") or "")
            if not _is_terminal_url_outcome(outcome):
                raise ValueError(
                    f"Cannot move surfer_batch {batch_id} to {to_status}: "
                    f"URL {entry.get('url')!r} outcome {outcome!r} is not terminal"
                )
    database.update_surfer_batch(batch_id, status=to_status)
    if _is_terminal_status(to_status):
        cid = str(batch.get("candidate_id") or "")
        if cid and _read_active_pointer(cid) == batch_id:
            _set_active_pointer(cid, None, debug=debug)
    updated = database.get_surfer_batch(batch_id)
    if updated is None:
        raise RuntimeError(f"surfer_batch missing after transition: {batch_id}")
    return updated


def set_surfer_batch_url_outcome(
    batch_id: str,
    url: str,
    outcome: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Set one URL's outcome; auto-complete when all outcomes are terminal."""
    logger.set_debug_flag(debug)
    _url_outcome_cfg(outcome)
    batch = database.get_surfer_batch(batch_id)
    if batch is None:
        raise ValueError(f"surfer_batch not found: {batch_id}")
    entries = list(batch.get("urls") or [])
    found = False
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for i, entry in enumerate(entries):
        if (entry or {}).get("url") == url:
            updated = dict(entry)
            updated["outcome"] = outcome
            updated["updated_at"] = now
            entries[i] = updated
            found = True
            break
    if not found:
        raise ValueError(f"URL not in surfer_batch {batch_id}: {url!r}")
    database.update_surfer_batch(batch_id, urls=entries)
    batch = database.get_surfer_batch(batch_id)
    if batch is None:
        raise RuntimeError(f"surfer_batch missing after url update: {batch_id}")
    status = str(batch.get("status") or "")
    if not _is_terminal_status(status):
        all_terminal = all(
            _is_terminal_url_outcome(str((e or {}).get("outcome") or ""))
            for e in (batch.get("urls") or [])
        )
        if all_terminal:
            return transition_surfer_batch_status(
                batch_id, _auto_complete_status(), debug=debug
            )
    return batch


def add_surfer_batch_job(
    batch_id: str,
    astral_job_id: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Append astral_job_id to batch job_ids (idempotent). Does not touch job.batch_id."""
    logger.set_debug_flag(debug)
    jid = (astral_job_id or "").strip()
    if not jid:
        raise ValueError("astral_job_id is required")
    batch = database.get_surfer_batch(batch_id)
    if batch is None:
        raise ValueError(f"surfer_batch not found: {batch_id}")
    job_ids = list(batch.get("job_ids") or [])
    if jid not in job_ids:
        job_ids.append(jid)
        database.update_surfer_batch(batch_id, job_ids=job_ids)
    updated = database.get_surfer_batch(batch_id)
    if updated is None:
        raise RuntimeError(f"surfer_batch missing after job add: {batch_id}")
    return updated


def list_surfer_batch_jobs(
    batch_id: str,
    *,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """Jobs associated with the batch via job_ids (independent of job.batch_id)."""
    logger.set_debug_flag(debug)
    batch = database.get_surfer_batch(batch_id)
    if batch is None:
        raise ValueError(f"surfer_batch not found: {batch_id}")
    out: List[Dict[str, Any]] = []
    for jid in batch.get("job_ids") or []:
        job = database.get_job(str(jid))
        if job is not None:
            out.append(job)
    return out


# ---- helpers ----


def _status_cfg(name: str) -> dict:
    cfg = SURFER_BATCH_CONFIG["statuses"].get(name)
    if not isinstance(cfg, dict):
        raise ValueError(f"Unknown surfer_batch status: {name!r}")
    return cfg


def _url_outcome_cfg(name: str) -> dict:
    cfg = SURFER_BATCH_CONFIG["url_outcomes"].get(name)
    if not isinstance(cfg, dict):
        raise ValueError(f"Unknown surfer_batch URL outcome: {name!r}")
    return cfg


def _is_terminal_status(name: str) -> bool:
    return bool(_status_cfg(name).get("terminal"))


def _is_terminal_url_outcome(name: str) -> bool:
    return bool(_url_outcome_cfg(name).get("terminal"))


def _auto_complete_status() -> str:
    for status_name, cfg in SURFER_BATCH_CONFIG["statuses"].items():
        if cfg.get("requires_all_urls_terminal"):
            return status_name
    raise RuntimeError("SURFER_BATCH_CONFIG has no requires_all_urls_terminal status")


def _new_batch_id() -> str:
    return f"{SURFER_BATCH_CONFIG['batch_id_prefix']}-{uuid4()}"


def _lifecycle_pointer_key() -> str:
    return str(SURFER_BATCH_CONFIG["candidate_data_lifecycle_key"])


def _read_active_pointer(candidate_id: str) -> Optional[str]:
    cand = get_candidate(candidate_id)
    if not cand:
        return None
    life = (cand.get("candidate_data") or {}).get("lifecycle") or {}
    if not isinstance(life, dict):
        return None
    val = life.get(_lifecycle_pointer_key())
    if val is None or val == "":
        return None
    return str(val)


def _set_active_pointer(
    candidate_id: str,
    batch_id: Optional[str],
    *,
    debug: bool = False,
) -> None:
    # Overlay-with-None clears via _deep_merge overwrite; do not omit the key.
    save_candidate_data(
        candidate_id,
        {"lifecycle": {_lifecycle_pointer_key(): batch_id}},
        debug=debug,
    )
