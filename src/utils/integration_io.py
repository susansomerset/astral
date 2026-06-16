"""Integration harness external I/O contract (AST-512 / AST-711)."""
import os

_INTEGRATION_ENV = "ASTRAL_INTEGRATION_MODE"
_LIVE_OPT_IN_ENV = "ASTRAL_ALLOW_LIVE_EXTERNAL_IO"


def is_integration_harness() -> bool:
    return os.environ.get(_INTEGRATION_ENV) == "1"


def require_controlled_external_io(caller: str) -> None:
    if not is_integration_harness():
        return
    if os.environ.get(_LIVE_OPT_IN_ENV) == "1":
        return
    raise RuntimeError(
        f"{caller}: live external I/O blocked in integration mode "
        f"(set {_LIVE_OPT_IN_ENV}=1 only for spikes or manual ops)"
    )
