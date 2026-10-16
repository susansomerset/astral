"""AST-2237 — service/astral_agent tree, import fence, ban greps, Dockerfile (no Docker build)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_SRC_IMPORT = re.compile(
    r"^\s*(?:from|import)\s+src(?:\.|\s|,|$)",
    re.MULTILINE,
)
# AC3 entity / dispatch ban + AC5 platform-write ban (ticket Acceptance criteria).
_BAN = re.compile(
    r"do_task|run_next|entity_id|TASK_CONFIG|dispatch_|app_log|astral\.db|"
    r"save_agent_data|add_log_entry"
)


@pytest.fixture
def root(astral_agent_root: Path) -> Path:
    assert astral_agent_root.is_dir(), (
        f"missing {astral_agent_root} — sync publish-ref product (AST-2237)"
    )
    return astral_agent_root


class TestAst2237ServiceTree:
    def test_required_paths_exist(self, root: Path) -> None:
        assert (root / "Dockerfile").is_file()
        assert (root / "jobqueue.py").is_file()
        assert (root / "requirements.txt").is_file()
        assert (root / "app.py").is_file()
        assert (root / "worker.py").is_file()
        assert (root / "executor.py").is_file()


class TestAst2237ImportAndBanFence:
    def test_py_files_have_zero_src_imports(self, root: Path) -> None:
        offenders: list[str] = []
        for path in sorted(root.glob("*.py")):
            if _SRC_IMPORT.search(path.read_text(encoding="utf-8")):
                offenders.append(path.name)
        assert offenders == [], f"src imports under service/astral_agent/: {offenders}"

    def test_ban_strings_absent(self, root: Path) -> None:
        hits: list[str] = []
        for path in sorted(root.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            if _BAN.search(text):
                hits.append(path.name)
        assert hits == [], f"AC3/AC5 ban hits under service/astral_agent/: {hits}"


class TestAst2237DockerfileAndRequirements:
    def test_dockerfile_copies_package_only_single_worker(self, root: Path) -> None:
        dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
        assert "COPY service/astral_agent/" in dockerfile
        assert "COPY src" not in dockerfile
        assert '--workers", "1"' in dockerfile or "--workers', '1'" in dockerfile
        assert "EXPOSE 8080" in dockerfile
        assert "python:3.12-slim-bookworm" in dockerfile

    def test_requirements_pins_fastapi_uvicorn_asyncpg_only(self, root: Path) -> None:
        req = (root / "requirements.txt").read_text(encoding="utf-8")
        assert "fastapi" in req
        assert "uvicorn" in req
        assert "asyncpg" in req
        # Provider SDKs / Playwright land with siblings — not this skeleton.
        assert "playwright" not in req.lower()
        assert "anthropic" not in req.lower()
        assert "openai" not in req.lower()
        assert "httpx" not in req.lower()
