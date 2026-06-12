"""
Astral Monitor: admin alerting and monitoring.

Entry point for all notification logic. The dispatcher calls auto_run_error()
after any AUTO task run that produces errors. Future features (log scanning,
escalation, daily summaries) extend this module without touching the dispatcher.
"""

from src.data import database
from src.external.gmail import send_email
from src.utils.config import ASTRAL_CONFIG
from src.utils.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

def auto_run_error(task_key: str, batch_id: str, accumulated: dict, final_status: str) -> None:
    """Send an error alert email after an AUTO task run with errors.

    Called by dispatcher._dispatch_one() when:
      - task is AUTO mode (not a CLICK run)
      - total_errors > 0

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

        subject = (
            f"[Astral] {task_key} {final_status}: "
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_log_body(batch_id: str) -> str:
    """Fetch log entries for batch_id and return them as chronological plain text."""
    entries = database.list_log_entries(batch_id=batch_id)
    entries = list(reversed(entries))  # DB returns newest-first; email body is chronological
    if not entries:
        return "(no log entries found for this batch)"
    lines = [
        f"{e.get('created_at', '')}  [{e.get('level', '?')}]  {e.get('message', '')}"
        for e in entries
    ]
    return "\n".join(lines)
