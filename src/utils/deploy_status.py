"""Server-side deploy status for admin nav footer (AST-646)."""

import os
import time

_PROCESS_BOOT_TIME = time.time()


def format_uptime_seconds(seconds: float) -> str:
    if seconds < 60:
        return "<1m"
    total_minutes = int(seconds // 60)
    if total_minutes < 60:
        return f"{total_minutes}m"
    total_hours = total_minutes // 60
    rem_minutes = total_minutes % 60
    if total_hours < 24:
        return f"{total_hours}h{rem_minutes}m"
    total_days = total_hours // 24
    rem_hours = total_hours % 24
    rem_mins = total_minutes % 60
    return f"{total_days}d{rem_hours}h{rem_mins:02d}m"


def _resolve_environment() -> str | None:
    raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()
    if not raw:
        return None
    return raw


def get_deploy_label() -> str:
    """Display label for deploy env in alerts and UI; Astral when unset."""
    return _resolve_environment() or "Astral"


def is_local_deploy_env() -> bool:
    raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()
    return raw.lower() == "local"


def ui_llm_debug(*, explicit_debug: bool = False) -> bool:
    """True when caller explicitly requested debug or server deploy env is local."""
    return explicit_debug or is_local_deploy_env()


def get_deploy_status_payload() -> dict:
    """Base deploy fields only (uptime, optional environment). merge_tickets: core layer."""
    uptime_seconds = max(0.0, time.time() - _PROCESS_BOOT_TIME)
    payload = {
        "uptime": format_uptime_seconds(uptime_seconds),
        "uptime_seconds": int(uptime_seconds),
    }
    env = _resolve_environment()
    if env is not None:
        payload["environment"] = env
    return payload


def merge_tickets_recent_first(entries: list[dict]) -> list[dict]:
    return list(reversed(entries))


def filter_merge_tickets_by_state(
    entries: list[dict],
    state_by_id: dict[str, str | None],
    *,
    uat_state_name: str,
) -> list[dict]:
    return [
        e
        for e in entries
        if state_by_id.get(e.get("ticket_id", "")) == uat_state_name
    ]
