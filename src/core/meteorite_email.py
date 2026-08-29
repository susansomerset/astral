"""Candidate-bound meteorite_email mailbox runner.

List Astral inbox → filter From→selected candidate → unbound age→Trash
(shared hygiene) → bind → stage_meteorite → archive on land success / all-skip
(including stage skip outcomes) / leave inbox on error; stamp last_email_check
(AST-1531). Style D when debug=True. Never calls qualify/GDL.

AST-1140: ``run_meteorite_email_selected_ids`` — Land Meteorite selected-ids
sharing the same bound helper; does not stamp ``candidate.last_email_check``.

AST-1522: test/bible gap only — no further product change on this sub.
"""

from __future__ import annotations

import os
import time
from typing import Any

from src.core.agent import do_task  # noqa: F401 — AST-1522 [bug-repro] still monkeypatches this name
from src.core.candidate import get_candidate
from src.core.inbox import get_message_html, list_inbox_messages
from src.data.database import update_candidate_last_email_check
from src.external.gmail import archive_message, trash_message
from src.utils.config import (
    METEORITE_CONFIG,
    METEORITE_EMAIL_MAILBOX_CONFIG,
)
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)


def _unbound_is_stale(internal_date_ms: int, *, now_ms: int) -> bool:
    days = int(METEORITE_EMAIL_MAILBOX_CONFIG["unbound_retention_days"])
    if internal_date_ms <= 0:
        return False  # unknown age → leave untouched
    age_ms = now_ms - internal_date_ms
    return age_ms > days * 24 * 60 * 60 * 1000


def _dbg(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )


def _dbg_selected(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=METEORITE_EMAIL_MAILBOX_CONFIG["debug_func_selected"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )


def _detail(debug: bool, line: str) -> None:
    if debug:
        logger.debug_detail(line)


def _land_outcome_token(land: dict[str, Any]) -> str:
    """Map land_meteorite rollup → archive tokens created|skipped|error."""
    outcome = (land or {}).get("outcome") or METEORITE_CONFIG["land_outcome_error"]
    if outcome == METEORITE_CONFIG["land_outcome_created"]:
        return "created"
    if outcome in (
        METEORITE_CONFIG["land_outcome_duplicate_skip"],
        METEORITE_CONFIG["land_outcome_superseded"],
    ):
        return "skipped"
    return "error"


def _stage_archive_token(stage: dict[str, Any]) -> str:
    """Map stage_meteorite result → archive tokens created|skipped|error."""
    if stage.get("skipped"):
        return "skipped"
    land = stage.get("land")
    if isinstance(land, dict):
        return _land_outcome_token(land)
    return _land_outcome_token(stage)


async def _finalize_archive(
    msg_id: str,
    outcomes: list[str],
    *,
    debug: bool,
    index: int,
    total: int,
    index_dbg=_dbg,
) -> tuple[int, int, int, str]:
    """Archive when ≥1 create or all attempts were skips. Empty outcomes → error."""
    if not outcomes:
        # No pass-without-ingest — leave inbox and fail the run.
        index_dbg(debug, index=index, total=total, mid=msg_id, outcome="error")
        return (0, 0, 1, "error")
    n_created = outcomes.count("created")
    n_skipped = outcomes.count("skipped")
    n_error = outcomes.count("error")
    if n_created > 0 or (n_skipped > 0 and n_error == 0 and n_created == 0):
        # all-duplicate / supersede skips still archive
        try:
            archive_message(msg_id)
        except Exception as exc:
            _detail(debug, f"archive_error={type(exc).__name__}")
            index_dbg(debug, index=index, total=total, mid=msg_id, outcome="error")
            return (0, 0, 1, "error")
        _detail(debug, f"created={n_created} skipped={n_skipped}")
        index_dbg(debug, index=index, total=total, mid=msg_id, outcome="archived")
        return (1, 0, 0, "archived")
    # only errors → leave inbox
    index_dbg(debug, index=index, total=total, mid=msg_id, outcome="error")
    return (0, 0, 1, "error")


async def _handle_bound(
    msg: dict,
    match: dict,
    *,
    debug: bool,
    index: int,
    total: int,
    index_dbg=_dbg,
) -> tuple[int, int, int, int, str]:
    """Returns (processed, passed, failed, errors, outcome) for one bound message."""
    cid = match.get("astral_candidate_id") or ""
    mid = msg.get("id") or ""
    ctx = get_candidate(cid) if cid else None
    if not ctx or not ctx.get("candidate_api_key"):
        index_dbg(debug, index=index, total=total, mid=mid, outcome="error")
        _detail(debug, "missing candidate or API key — leave inbox")
        return (1, 0, 1, 0, "failed")

    try:
        payload = get_message_html(mid)
    except Exception as exc:
        index_dbg(debug, index=index, total=total, mid=mid, outcome="error")
        _detail(debug, f"get_html_error={type(exc).__name__}")
        return (1, 0, 0, 1, "error")

    # Caller-owned blob (no strip_extract — inbox owns strip).
    subject = (payload.get("subject") or "").strip()
    html = payload.get("html_body") or ""
    if subject and html:
        blob = f"{subject}\n\n{html}"
    else:
        blob = subject or html

    from src.core.meteorite import stage_meteorite

    stage = await stage_meteorite(
        cid,
        blob,
        source_kind="email",
        source_id=mid,
        debug=debug,
    )
    outcomes = [_stage_archive_token(stage)]
    _detail(
        debug,
        f"stage_outcome={stage.get('stage_outcome')!r} "
        f"skipped={stage.get('skipped')!r} archive_token={outcomes[0]}",
    )
    p, f, e, outcome = await _finalize_archive(
        mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
    )
    return (1, p, f, e, outcome)


async def process_meteorite_email_messages(
    candidate_id: str,
    messages: list[dict],
    *,
    debug: bool = False,
) -> dict[str, int]:
    """Bound-ingest only for messages whose From binds to candidate_id.

    Same stage/archive outcomes as the dispatch runner.
    Does not list Gmail, does not Trash unbound mail, does not stamp
    last_email_check. AST-1129 Land Meteorite calls this with selected rows.
    """
    cid = str(candidate_id or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if debug:
        logger.set_debug_flag(True)

    n = len(messages)
    processed = passed = failed = errors = 0
    for i, msg in enumerate(messages, start=1):
        mid = msg.get("id") or ""
        try:
            _dbg(debug, index=i, total=n, mid=mid, outcome="found")
            _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
            match = msg.get("candidate_match") or {}
            if not match.get("matched"):
                _dbg(debug, index=i, total=n, mid=mid, outcome="skipped-unbound")
                _detail(debug, "process_meteorite_email_messages does not mutate unbound mail")
                processed += 1
                passed += 1
                continue
            bound_cid = str(match.get("astral_candidate_id") or "").strip()
            if bound_cid != cid:
                _dbg(debug, index=i, total=n, mid=mid, outcome="skipped-other-candidate")
                processed += 1
                passed += 1
                continue
            _detail(debug, f"astral_candidate_id={bound_cid}")
            # 5th return is outcome string for selected-ids; ignore here
            p, pa, fa, er, _outcome = await _handle_bound(
                msg, match, debug=debug, index=i, total=n
            )
            processed += p
            passed += pa
            failed += fa
            errors += er
        except Exception as exc:
            errors += 1
            processed += 1
            _dbg(debug, index=i, total=n, mid=mid, outcome="error")
            _detail(debug, f"message_error={type(exc).__name__}: {exc}")
            for line in truncate_debug_content(str(exc)):
                _detail(debug, line)

    return {
        "total_processed": processed,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }


async def run_meteorite_email_selected_ids(
    message_ids: list[str],
    *,
    debug: bool = False,
) -> dict:
    """Land Meteorite: ingest only these Astral inbox message ids (AST-1140).

    Same bind/stage/archive outcomes as dispatcher meteorite_email.
    Does not stamp candidate.last_email_check. Does not call Create strip/extract.
    """
    if debug:
        logger.set_debug_flag(True)

    # Preserve caller order; strip empties — do not invent ids.
    normalized_ids = [raw.strip() for raw in (message_ids or []) if (raw or "").strip()]
    by_id = {(m.get("id") or ""): m for m in list_inbox_messages(debug=debug)}

    results: list[dict] = []
    total_processed = total_passed = total_failed = total_errors = total_skipped = 0
    n = len(normalized_ids)

    for i, mid in enumerate(normalized_ids, start=1):
        _dbg_selected(debug, index=i, total=n, mid=mid, outcome="found")
        if mid not in by_id:
            outcome = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_not_in_inbox"]
            results.append(
                {"message_id": mid, "outcome": outcome, "astral_candidate_id": None}
            )
            total_skipped += 1
            total_processed += 1
            _dbg_selected(debug, index=i, total=n, mid=mid, outcome=outcome)
            continue

        msg = by_id[mid]
        match = msg.get("candidate_match") or {}
        cid = (match.get("astral_candidate_id") or "").strip()
        if not match.get("matched") or not cid:
            # Skip only — retention Trash stays on the dispatcher hygiene path.
            if not match.get("matched"):
                outcome = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_unbound"]
            else:
                outcome = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_unmatched"]
            results.append(
                {"message_id": mid, "outcome": outcome, "astral_candidate_id": None}
            )
            total_skipped += 1
            total_processed += 1
            _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
            _dbg_selected(debug, index=i, total=n, mid=mid, outcome=outcome)
            continue

        _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
        _detail(debug, f"astral_candidate_id={cid}")
        p, pa, fa, er, outcome = await _handle_bound(
            msg, match, debug=debug, index=i, total=n, index_dbg=_dbg_selected
        )
        results.append(
            {
                "message_id": mid,
                "outcome": outcome,
                "astral_candidate_id": match["astral_candidate_id"],
            }
        )
        total_processed += p
        total_passed += pa
        total_failed += fa
        total_errors += er

    return {
        "results": results,
        "total_processed": total_processed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "total_skipped": total_skipped,
    }


async def run_meteorite_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """Candidate-bound mailbox run + unbound hygiene + last_email_check stamp."""
    cid = str((task or {}).get("candidate_id") or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if debug:
        logger.set_debug_flag(True)
        _dbg(debug, index=1, total=1, mid=cid, outcome="run-start")
        env_user = (os.environ.get("GMAIL_USER") or "").casefold()
        expected = (METEORITE_EMAIL_MAILBOX_CONFIG["account_address"] or "").casefold()
        if env_user != expected:
            _detail(True, f"account_mismatch GMAIL_USER={env_user!r} expected={expected!r}")

    messages = list_inbox_messages(debug=debug)
    n = len(messages)
    processed = passed = failed = errors = 0
    now_ms = int(time.time() * 1000)

    for i, msg in enumerate(messages, start=1):
        mid = msg.get("id") or ""
        try:
            _dbg(debug, index=i, total=n, mid=mid, outcome="found")
            _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
            match = msg.get("candidate_match") or {}
            if not match.get("matched"):
                if _unbound_is_stale(int(msg.get("internal_date_ms") or 0), now_ms=now_ms):
                    trash_message(mid)
                    _dbg(debug, index=i, total=n, mid=mid, outcome="trashed")
                else:
                    _dbg(debug, index=i, total=n, mid=mid, outcome="ignored-unbound")
                processed += 1
                passed += 1
                continue

            bound_cid = str(match.get("astral_candidate_id") or "").strip()
            if bound_cid != cid:
                _dbg(debug, index=i, total=n, mid=mid, outcome="skipped-other-candidate")
                processed += 1
                passed += 1
                continue

            _detail(debug, f"astral_candidate_id={bound_cid}")
            p, pa, fa, er, _outcome = await _handle_bound(
                msg, match, debug=debug, index=i, total=n
            )
            processed += p
            passed += pa
            failed += fa
            errors += er
        except Exception as exc:
            errors += 1
            processed += 1
            _dbg(debug, index=i, total=n, mid=mid, outcome="error")
            _detail(debug, f"message_error={type(exc).__name__}: {exc}")
            for line in truncate_debug_content(str(exc)):
                _detail(debug, line)

    # Stamp after a completed run (incl. zero bound matches / empty inbox).
    update_candidate_last_email_check(cid)
    if debug:
        _dbg(debug, index=1, total=1, mid=cid, outcome="run-complete")
        _detail(debug, "last_email_check=stamped")
        _detail(
            debug,
            f"summary={{total_processed={processed}, total_passed={passed}, "
            f"total_failed={failed}, total_errors={errors}}}",
        )

    return {
        "total_processed": processed,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }
