"""Process runtime bootstrap (AST-654 / AST-782).

Called once from ``src/ui/server.py`` after Flask blueprints register.

Order: ``_validate_runtime_coupling()`` → ``apply_repo_admin_json_at_startup()``
→ ``database.sync_agent_tasks(get_task_keys())`` → ``start_scheduler()``.

Does not run AST-381 admin snapshot export/import/preview.
"""

from src.core.dispatcher import start_scheduler
from src.core.repo_admin_json import apply_repo_admin_json_at_startup
from src.data import database
from src.utils.config import (
    DISPATCH_SCHEDULABLE_TASK_KEYS,
    TASK_CONFIG,
    dispatch_task_admin_defaults,
    get_task_keys,
    validate_llm_provider_environment,
)

__all__ = ["bootstrap_runtime"]


def _validate_runtime_coupling() -> None:
    validate_llm_provider_environment()
    task_keys = get_task_keys()
    if not task_keys:
        raise RuntimeError("bootstrap: TASK_CONFIG defines no task keys")
    for key in task_keys:
        if key not in TASK_CONFIG:
            raise RuntimeError(f"bootstrap: task key {key!r} missing from TASK_CONFIG")
    for key in DISPATCH_SCHEDULABLE_TASK_KEYS:
        if key in TASK_CONFIG:
            continue
        try:
            dispatch_task_admin_defaults(key)
        except KeyError as exc:
            raise RuntimeError(
                f"bootstrap: dispatch schedulable key {key!r} missing from TASK_CONFIG"
            ) from exc


def bootstrap_runtime() -> None:
    _validate_runtime_coupling()
    apply_repo_admin_json_at_startup()
    database.sync_agent_tasks(get_task_keys())
    start_scheduler()
