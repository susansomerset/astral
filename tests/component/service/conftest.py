"""Service component fixtures — path + env for flat service imports.

Telescope and astral-agent both use flat module names (`app`, `jobqueue`, …).
Default path is Telescope; astral-agent tests swap via ``astral_agent_modules``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator

import pytest

_REPO = Path(__file__).resolve().parents[3]
_TELESCOPE = _REPO / "service" / "telescope"
_ASTRAL_AGENT = _REPO / "service" / "astral_agent"

# Flat modules either service may bind — purge when swapping path.
_FLAT_SERVICE_MODULES = (
    "app",
    "jobqueue",
    "settings",
    "worker",
    "executor",
    "agent_config",
    "logging_util",
    "auth",
    "capture",
    "interact",
    "scrape",
    "browser_pool",
)

# settings.py reads env at import — set before any telescope module load
os.environ.setdefault("TELESCOPE_BEARER_TOKEN", "test-telescope-bearer")
# astral-agent settings also load at import; safe placeholder until a test overrides
os.environ.setdefault("ASTRAL_DATABASE_URL", "postgresql://astral-agent-test/unused")

if _TELESCOPE.is_dir() and str(_TELESCOPE) not in sys.path:
    sys.path.insert(0, str(_TELESCOPE))


def _purge_flat_modules() -> None:
    for name in _FLAT_SERVICE_MODULES:
        sys.modules.pop(name, None)


@pytest.fixture
def bearer_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-telescope-bearer"}


@pytest.fixture
def telescope_root() -> Path:
    return _TELESCOPE


@pytest.fixture
def astral_agent_root() -> Path:
    return _ASTRAL_AGENT


@pytest.fixture
def astral_agent_modules(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Put service/astral_agent/ first on sys.path; purge colliding flat imports."""
    monkeypatch.setenv("ASTRAL_DATABASE_URL", "postgresql://astral-agent-test/harness")
    agent = str(_ASTRAL_AGENT)
    tel = str(_TELESCOPE)
    # Prefer astral-agent over telescope for this test's flat imports.
    sys.path = [p for p in sys.path if p not in (agent, tel)]
    sys.path.insert(0, agent)
    _purge_flat_modules()
    yield _ASTRAL_AGENT
    _purge_flat_modules()
    sys.path = [p for p in sys.path if p != agent]
    if _TELESCOPE.is_dir() and tel not in sys.path:
        sys.path.insert(0, tel)
