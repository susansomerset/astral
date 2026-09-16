"""Manage Email admin API (AST-1558 / AST-1608).

List is All (`list_inbox_messages`) or candidate-scoped (aliases →
`fetch_candidate_email`). Land requires `candidate_id` and calls
`ingest_candidate_email_message` (same fan-out/archive as check_inbox).
No bind enrichment; no create-job.
"""

from __future__ import annotations

import asyncio
from email.utils import parseaddr

from flask import Blueprint, jsonify, request

from ui.auth import require_admin
from src.core.candidate import get_candidate
from src.core.inbox import (
    fetch_candidate_email,
    get_message_with_assembled_html,
    list_inbox_messages,
)
from src.utils.config import (
    CANDIDATE_LOOKUP_CONFIG,
    METEORITE_MONITORING_CONFIG,
    STAGE_METEORITE_CONFIG,
)
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger

logger = get_logger(__name__)

inbox_bp = Blueprint("inbox", __name__, url_prefix="/api/admin/inbox")


def _lookup_dotted_scalar(candidate: dict, dotted_path: str) -> str:
    """Resolve one scalar email path against top-level columns or candidate_data."""
    parts = dotted_path.split(".")
    for root in (candidate, candidate.get("candidate_data") or {}):
        if not isinstance(root, dict):
            continue
        cur: object = root
        ok = True
        for seg in parts:
            if not isinstance(cur, dict) or seg not in cur:
                ok = False
                break
            cur = cur[seg]
        if ok and isinstance(cur, str) and cur.strip():
            return cur.strip()
    return ""


def _lookup_dotted_list(candidate: dict, dotted_path: str) -> list[str]:
    """Resolve one list email path under candidate_data."""
    parts = dotted_path.split(".")
    cur: object = candidate.get("candidate_data") or {}
    if not isinstance(cur, dict):
        return []
    for seg in parts:
        if not isinstance(cur, dict):
            return []
        cur = cur.get(seg)
    out: list[str] = []
    if isinstance(cur, list):
        for item in cur:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
    elif isinstance(cur, str) and cur.strip():
        out.append(cur.strip())
    return out


def _email_aliases_for_candidate(candidate_id: str) -> list[str]:
    """Bare email addresses from CANDIDATE_LOOKUP_CONFIG paths (order-stable, unique)."""
    cid = (candidate_id or "").strip()
    if not cid:
        return []
    row = get_candidate(cid)
    if not row:
        return []
    seen: set[str] = set()
    aliases: list[str] = []
    for path in CANDIDATE_LOOKUP_CONFIG["email_paths"]:
        raw = _lookup_dotted_scalar(row, path)
        if not raw:
            continue
        _display, parsed = parseaddr(raw)
        token = (parsed or raw).strip()
        if "@" not in token:
            continue
        folded = token.casefold()
        if folded in seen:
            continue
        seen.add(folded)
        aliases.append(token)
    for path in CANDIDATE_LOOKUP_CONFIG["email_list_paths"]:
        for raw in _lookup_dotted_list(row, path):
            _display, parsed = parseaddr(raw)
            token = (parsed or raw).strip()
            if "@" not in token:
                continue
            folded = token.casefold()
            if folded in seen:
                continue
            seen.add(folded)
            aliases.append(token)
    return aliases


@inbox_bp.route("/messages", methods=["GET"])
@require_admin
def inbox_list_messages():
    debug = ui_llm_debug(
        explicit_debug=request.args.get("debug", "").lower() in ("1", "true", "yes")
    )
    candidate_id = (request.args.get("candidate_id") or "").strip()
    try:
        if not candidate_id:
            messages = list_inbox_messages(debug=debug)
        else:
            aliases = _email_aliases_for_candidate(candidate_id)
            messages = fetch_candidate_email(aliases, debug=debug)
    except Exception as e:
        logger.warning("[api_inbox] list failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify({"messages": messages}), 200


@inbox_bp.route("/messages/<message_id>", methods=["GET"])
@require_admin
def inbox_get_message(message_id: str):
    mid = (message_id or "").strip()
    if not mid:
        return jsonify({"error": "message_id is required"}), 400
    try:
        payload = get_message_with_assembled_html(mid)
    except Exception as e:
        logger.warning("[api_inbox] get failed id=%s: %s", mid, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(payload), 200


@inbox_bp.route("/land-meteorite", methods=["POST"])
@require_admin
def inbox_land_meteorite():
    body = request.get_json(silent=True) or {}
    cid = str(body.get("candidate_id") or "").strip()
    if not cid:
        return jsonify({"error": "candidate_id is required"}), 400
    raw_ids = body.get("message_ids")
    if not isinstance(raw_ids, list):
        return jsonify({"error": "message_ids must be a list"}), 400
    message_ids = [str(x).strip() for x in raw_ids if str(x or "").strip()]
    if not message_ids:
        return jsonify({"error": "message_ids is required"}), 400
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)

    already = METEORITE_MONITORING_CONFIG["outcome_already_ingested"]
    skip_outcomes = set(STAGE_METEORITE_CONFIG["skip_outcomes"])
    landable = set(STAGE_METEORITE_CONFIG["landable_outcomes"])

    async def _land_all() -> dict:
        from src.core.meteorite import ingest_candidate_email_message

        results: list[dict] = []
        total_processed = total_passed = total_failed = total_errors = total_skipped = 0
        n = len(message_ids)
        for i, mid in enumerate(message_ids, start=1):
            row = await ingest_candidate_email_message(
                cid, mid, debug=debug, index=i, total=n,
            )
            outcome = str(row.get("outcome") or "")
            job_count = int(row.get("job_count") or 0)
            public = {
                "message_id": row.get("message_id") or mid,
                "outcome": outcome,
                "astral_candidate_id": row.get("astral_candidate_id") or cid,
                "job_count": job_count,
            }
            if row.get("error"):
                public["error"] = str(row["error"])
            results.append(public)
            total_processed += 1
            # Prefer ingest counter; else public shape (skip / already / landable+jobs).
            counter = row.get("counter")
            if counter == "error":
                is_passed = False
            elif counter == "passed":
                is_passed = True
            else:
                is_passed = (
                    outcome in skip_outcomes
                    or outcome == already
                    or (outcome in landable and job_count > 0)
                )
            if is_passed:
                total_passed += 1
                if outcome in skip_outcomes or outcome == already:
                    total_skipped += 1
            else:
                total_failed += 1
                if row.get("error"):
                    total_errors += 1

        return {
            "results": results,
            "total_processed": total_processed,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
        }

    try:
        result = asyncio.run(_land_all())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_inbox] land-meteorite failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify(result), 200
