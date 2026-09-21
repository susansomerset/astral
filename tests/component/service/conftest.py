"""Telescope service component fixtures — path + bearer for flat service imports."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_TELESCOPE = _REPO / "service" / "telescope"

# settings.py reads env at import — set before any telescope module load
os.environ.setdefault("TELESCOPE_BEARER_TOKEN", "test-telescope-bearer")

if _TELESCOPE.is_dir() and str(_TELESCOPE) not in sys.path:
    sys.path.insert(0, str(_TELESCOPE))


@pytest.fixture
def bearer_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-telescope-bearer"}


@pytest.fixture
def telescope_root() -> Path:
    return _TELESCOPE
