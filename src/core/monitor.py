"""
Astral Monitor: admin alerting and monitoring.

Entry point for all notification logic. The dispatcher calls auto_run_error()
after any AUTO task run that produces errors (support alias: metadata header,
WARNING/ERROR body, full log attached), and provider_balance_outage()
instead when the run was stopped by an LLM provider balance refusal (admin
address(es), short body, no log). Future features (log scanning,
escalation, daily summaries) extend this module without touching the dispatcher.
"""

import re

from src.data import database
from src.external.gmail import send_email
from src.core.agent import task_llm_server_id
from src.utils.config import ASTRAL_CONFIG, AUTH_CONFIG, get_llm_server
from src.utils.deploy_status import get_deploy_label
from src.utils.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

def auto_run_error(
    task_key: str,
    batch_id: str,
    accumulated: dict,
    final_status: str,
    candidate_id: str = "",
) -> None:
    """Send an error alert email after an AUTO task run with errors.

    Called by dispatcher._dispatch_one() when:
      - task is AUTO mode (not a CLICK run)
      - total_errors > 0

    Subject prefix is [{deploy_label}] or [{deploy_label}/{last_name}] from
    ASTRAL_DEPLOY_ENV and the dispatch task candidate's last name column.

    Fetches log entries for the batch once (already flushed to DB at this point).
    Body = metadata header + WARNING/ERROR-only fenced block; the full log at every
    level goes as a <batch_id>.txt attachment (AST-2214). Never raises — a failed
    alert must not surface to the caller.
    """
    logger.info("[monitor] auto_run_error triggered — task=%s status=%s errors=%s processed=%s batch=%s",
                task_key, final_status,
                accumulated.get("total_errors", 0), accumulated.get("total_processed", 0), batch_id)
    try:
        to = ASTRAL_CONFIG["support_email"]
        total_processed = accumulated.get("total_processed", 0)
        total_errors = accumulated.get("total_errors", 0)

        deploy_label = get_deploy_label()
        last_name = _resolve_candidate_last_name(candidate_id)
        prefix = _format_alert_subject_prefix(deploy_label, last_name)
        subject = (
            f"{prefix} {task_key} {final_status}: "
            f"{total_errors} error(s) / {total_processed} processed | {batch_id}"
        )
        header = _format_alert_header(
            deploy_label, candidate_id, last_name, task_key, batch_id, final_status, accumulated,
        )
        logger.info("[monitor] fetching %s log entries for email body...", batch_id)
        # one fetch feeds both the body block and the attachment; DB returns newest-first
        entries = list(reversed(database.list_log_entries(batch_id=batch_id)))
        body = f"{header}\n\n{_format_warning_error_block(entries)}"
        attachments = {f"{batch_id}.txt": _format_full_log(entries)}
        logger.info("[monitor] sending alert to %s — subject: %s", to, subject)

        ok = send_email(to=to, subject=subject, body=body, attachments=attachments)
        if ok:
            logger.info("[monitor] alert sent OK to %s", to)
        else:
            logger.warning("[monitor] send_email returned False for batch %s — check Gmail credentials", batch_id)
    except Exception as e:
        logger.warning("[monitor] auto_run_error raised unexpectedly for %s: %s", batch_id, e)


def provider_balance_outage(
    task_key: str,
    batch_id: str,
    accumulated: dict,
    outage: dict,
    candidate_id: str = "",
) -> None:
    """AST-1867: one alert per AUTO run stopped by an LLM provider balance refusal.
    AST-2214: sent to the admin address(es) in AUTH_CONFIG["admin_emails"], not the support
    alias; short body, no batch log, no attachment. No admin configured -> one WARNING, no send.
    Never raises — a failed alert must not surface to the caller."""
    try:
        # sorted: admin_emails is a frozenset, so a multi-admin `to` would otherwise reorder per process
        admins = sorted(AUTH_CONFIG["admin_emails"])
        if not admins:
            logger.warning(
                "[monitor] provider_balance_outage: no ASTRAL_ADMIN_EMAILS configured — balance alert for %s not sent",
                batch_id,
            )
            return
        # The server the refused task's agent actually called (AST-1880), not a global setting.
        provider = get_llm_server(task_llm_server_id(task_key))["label"]
        prefix = _format_alert_subject_prefix(get_deploy_label(), _resolve_candidate_last_name(candidate_id))
        subject = f"{prefix} {provider} insufficient balance — {task_key} stopped | {batch_id}"
        lines = [
            f"Provider: {provider}",
            f"Refusal: {outage.get('error') or '-'}",
            f"Task: {task_key}   Batch: {batch_id}",
            f"Processed: {accumulated.get('total_processed', 0)}  Passed: {accumulated.get('total_passed', 0)}  "
            f"Failed: {accumulated.get('total_failed', 0)}  Errors: {accumulated.get('total_errors', 0)}",
        ]
        if outage.get("held"):
            lines.append(f"Held (state unchanged): {outage['held']}")
        lines.append("Entity state was held; the task stays enabled and resumes once provider credit is restored.")
        if not send_email(to=", ".join(admins), subject=subject, body="\n".join(lines)):
            logger.warning("[monitor] send_email returned False for batch %s — check Gmail credentials", batch_id)
    except Exception as e:
        logger.warning("[monitor] provider_balance_outage raised unexpectedly for %s: %s", batch_id, e)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_log_line(entry: dict) -> str:
    """One app_log row in the alert/attachment line format."""
    return f"{entry.get('created_at', '')}  [{entry.get('level', '?')}]  {entry.get('message', '')}"


def _format_full_log(entries: list[dict]) -> str:
    """Every row at every level, in the order given (chronological), for the .txt attachment."""
    if not entries:
        return "(no log entries found for this batch)"
    return "\n".join(_format_log_line(e) for e in entries)


def _format_warning_error_block(entries: list[dict]) -> str:
    """WARNING and ERROR rows only, in the order given, in a fenced code block for the email body.

    The fence makes Linear (which files these alert emails as issues) render the log as
    one code block instead of a long description to scroll past. It is one
    backtick longer than any backtick run inside the logs, so a log line can't close it.
    """
    # filter on the stored level name (logging levelname), not on message text
    text = "\n".join(_format_log_line(e) for e in entries if e.get("level") in ("WARNING", "ERROR"))
    if not text:
        return "(no WARNING or ERROR entries for this batch)"
    longest_run = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest_run + 1)
    return f"{fence}\n{text}\n{fence}"


_ALERT_COUNT_KEYS = {
    "Processed": "total_processed",
    "Passed": "total_passed",
    "Failed": "total_failed",
    "Errors": "total_errors",
}


def _format_alert_header(
    deploy_label: str,
    candidate_id: str,
    last_name: str | None,
    task_key: str,
    batch_id: str,
    final_status: str,
    accumulated: dict,
) -> str:
    """Labelled triage block that opens every support-alias alert (AST-2214).

    Every label is always present; a value the run doesn't have shows '-'.
    """
    cid = (candidate_id or "").strip()
    # "cand-1 (Somerset)" when the last name is known, bare id otherwise, '-' with no candidate
    candidate = f"{cid} ({last_name})" if cid and last_name else (cid or "-")
    # one line, same "Label: n  Label: n" shape as the balance-outage body
    counts = "  ".join(f"{label}: {accumulated.get(key, '-')}" for label, key in _ALERT_COUNT_KEYS.items())
    return "\n".join([
        f"Deploy: {deploy_label or '-'}",
        f"Candidate: {candidate}",
        f"Task: {task_key or '-'}",
        f"Batch: {batch_id or '-'}",
        f"Status: {final_status or '-'}",
        counts,
    ])


def _resolve_candidate_last_name(candidate_id: str) -> str | None:
    """Candidate last name column for subject triage; None when missing or empty."""
    if not (candidate_id or "").strip():
        return None
    row = database.get_candidate(candidate_id.strip())
    if not row:
        return None
    last = (row.get("last") or "").strip()
    return last or None


def _format_alert_subject_prefix(deploy_label: str, last_name: str | None) -> str:
    """Bracket prefix: [deploy] or [deploy/LastName]."""
    if last_name:
        return f"[{deploy_label}/{last_name}]"
    return f"[{deploy_label}]"
