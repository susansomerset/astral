"""Server-side deploy status for admin nav footer (AST-646)."""

import os
import subprocess
import time
from pathlib import Path

_PROCESS_BOOT_TIME = time.time()
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


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


def is_local_deploy_env() -> bool:
    raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()
    return raw.lower() == "local"


def ui_llm_debug(*, explicit_debug: bool = False) -> bool:
    """True when caller explicitly requested debug or server deploy env is local."""
    return explicit_debug or is_local_deploy_env()


def _git_head_info() -> tuple[str, str]:
    cwd = _REPO_ROOT
    try:
        rev = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=cwd,
        )
        if rev.returncode != 0 or not rev.stdout.strip():
            return ("unknown", "")
        commit_short = rev.stdout.strip()
        log = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=cwd,
        )
        commit_message = log.stdout.strip() if log.returncode == 0 else ""
        return (commit_short, commit_message)
    except (OSError, subprocess.TimeoutExpired):
        return ("unknown", "")


def get_deploy_status_payload() -> dict:
    uptime_seconds = max(0.0, time.time() - _PROCESS_BOOT_TIME)
    commit_short, commit_message = _git_head_info()
    payload = {
        "commit_short": commit_short,
        "commit_message": commit_message,
        "uptime": format_uptime_seconds(uptime_seconds),
        "uptime_seconds": int(uptime_seconds),
    }
    env = _resolve_environment()
    if env is not None:
        payload["environment"] = env
    return payload
