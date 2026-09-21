"""AST-1725 — service/telescope import fence + Dockerfile contract (no Docker build)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_SRC_IMPORT = re.compile(
    r"^\s*(?:from|import)\s+src(?:\.|\s|,|$)",
    re.MULTILINE,
)


def test_telescope_py_files_have_zero_src_imports(telescope_root: Path) -> None:
    assert telescope_root.is_dir(), f"missing {telescope_root} — sync publish-ref product"
    offenders: list[str] = []
    for path in sorted(telescope_root.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if _SRC_IMPORT.search(text):
            offenders.append(path.name)
    assert offenders == [], f"src imports under service/telescope/: {offenders}"


def test_dockerfile_playwright_pin_single_worker(telescope_root: Path) -> None:
    dockerfile = (telescope_root / "Dockerfile").read_text(encoding="utf-8")
    assert "mcr.microsoft.com/playwright/python:v1.49.1-jammy" in dockerfile
    assert '--workers", "1"' in dockerfile or "--workers', '1'" in dockerfile
    assert "USER pwuser" in dockerfile
    # Image copies package only — no src tree
    assert "COPY service/telescope/" in dockerfile
    assert "COPY src" not in dockerfile


def test_requirements_pins_playwright_1491(telescope_root: Path) -> None:
    req = (telescope_root / "requirements.txt").read_text(encoding="utf-8")
    assert "playwright==1.49.1" in req
    assert "fastapi" in req
