"""
Astral Monitor: admin alerting and monitoring.

Entry point for all notification logic. The dispatcher calls auto_run_error()
after any AUTO task run that produces errors, and provider_balance_outage()
instead when the run was stopped by an LLM provider balance refusal. Future features (log scanning,
escalation, daily summaries) extend this module without touching the dispatcher.
"""

import re

from src.data import database
from src.external.gmail import send_email
from src.utils.config import ASTRAL_CONFIG, get_active_llm_provider
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

    Fetches log entries for the batch (already flushed to DB at this point),
    formats subject + body, and sends via Gmail. Never raises — a failed alert
    must not surface to the caller.
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
        logger.info("[monitor] fetching %s log entries for email body...", batch_id)
        body = _format_log_body(batch_id)
        logger.info("[monitor] sending alert to %s — subject: %s", to, subject)

        ok = send_email(to=to, subject=subject, body=body)
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
    Short body (no batch log dump). Never raises — a failed alert must not surface to the caller."""
    try:
        provider = get_active_llm_provider()
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
        if not send_email(to=ASTRAL_CONFIG["support_email"], subject=subject, body="\n".join(lines)):
            logger.warning("[monitor] send_email returned False for batch %s — check Gmail credentials", batch_id)
    except Exception as e:
        logger.warning("[monitor] provider_balance_outage raised unexpectedly for %s: %s", batch_id, e)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_log_body(batch_id: str) -> str:
    """Fetch log entries for batch_id and return them chronologically in a fenced code block.

    The fence makes Linear (which files these alert emails as issues) render the log as
    one code block instead of thousands of lines of description to scroll past. It is one
    backtick longer than any backtick run inside the logs, so a log line can't close it.
    """
    entries = database.list_log_entries(batch_id=batch_id)
    entries = list(reversed(entries))  # DB returns newest-first; email body is chronological
    if not entries:
        return "(no log entries found for this batch)"
    lines = [
        f"{e.get('created_at', '')}  [{e.get('level', '?')}]  {e.get('message', '')}"
        for e in entries
    ]
    text = "\n".join(lines)
    longest_run = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest_run + 1)
    return f"{fence}\n{text}\n{fence}"


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
