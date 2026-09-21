"""Process runtime bootstrap (AST-654 / AST-782 / AST-1455).

Called once from ``src/ui/server.py`` after Flask blueprints register.

Order: ``_validate_runtime_coupling()``
→ ``database.ensure_all_upsert_registry_schemas_at_startup()``
→ ``start_scheduler()``.

Boot does not apply repo admin JSON or ``sync_agent_tasks`` blank inserts
(AST-1455 — schema ensure only; explicit Revert to file applies JSON→DB).

Does not run AST-381 admin snapshot export/import/preview.
"""

from src.core.dispatcher import start_scheduler
from src.data import database
from src.utils.config import (
    TASK_CONFIG,
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


def bootstrap_runtime() -> None:
    _validate_runtime_coupling()
    database.ensure_all_upsert_registry_schemas_at_startup()
    start_scheduler()
