"""AST-2241 — astral-agent Railway Phase 1 toml + service↔src fence extension."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]


@pytest.fixture
def fence_script() -> Path:
    path = _REPO / "scripts" / "ci" / "check-service-src-import-fence.sh"
    assert path.is_file(), f"missing {path} — sync publish-ref product (AST-2241)"
    return path


@pytest.fixture
def fence_workflow() -> Path:
    path = _REPO / ".github" / "workflows" / "service-src-import-fence.yml"
    assert path.is_file(), f"missing {path} — sync publish-ref product (AST-2241)"
    return path


@pytest.fixture
def astral_agent_railway(astral_agent_root: Path) -> Path:
    path = astral_agent_root / "railway.toml"
    assert path.is_file(), f"missing {path} — sync publish-ref product (AST-2241)"
    return path


class TestAst2241RailwayPhase1Toml:
    def test_num_replicas_dockerfile_memory_healthcheck(
        self, astral_agent_railway: Path
    ) -> None:
        text = astral_agent_railway.read_text(encoding="utf-8")
        assert "numReplicas = 1" in text
        assert 'builder = "DOCKERFILE"' in text
        assert 'dockerfilePath = "service/astral_agent/Dockerfile"' in text
        assert 'watchPatterns = ["service/astral_agent/**"]' in text
        assert "restartPolicyType" in text and "ON_FAILURE" in text
        # Step 3: no memory cap — the worker holds every claimable job.
        live = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
        assert "limitOverride" not in live and "memoryBytes" not in live
        assert 'healthcheckPath = "/healthz"' in text
        assert "drainingSeconds = 30" in text

    def test_no_phase2_autoscaler_hooks(self, astral_agent_railway: Path) -> None:
        # Comments may name Judoscale as a ban; assert no live (non-comment) keys.
        text = astral_agent_railway.read_text(encoding="utf-8")
        live = "\n".join(
            ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
        )
        assert "Judoscale" not in live
        assert "serviceInstanceUpdate" not in live
        assert "startCommand" not in live
        assert "startCommand =" not in text


class TestAst2241ImportFenceExtension:
    def test_ci_fence_script_exits_zero(self, fence_script: Path) -> None:
        proc = subprocess.run(
            ["bash", str(fence_script)],
            cwd=_REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "import fence: ok (service ↔ src)" in proc.stdout

    def test_ci_fence_catches_src_import_under_astral_agent(
        self, fence_script: Path, astral_agent_root: Path
    ) -> None:
        offender = astral_agent_root / "_betty_fence_probe.py"
        assert not offender.exists()
        offender.write_text("from src.utils import config  # betty probe\n", encoding="utf-8")
        try:
            proc = subprocess.run(
                ["bash", str(fence_script)],
                cwd=_REPO,
                capture_output=True,
                text=True,
                check=False,
            )
            assert proc.returncode != 0
            assert "must not import src" in proc.stdout
        finally:
            offender.unlink(missing_ok=True)

    def test_workflow_step_names_full_service_fence(self, fence_workflow: Path) -> None:
        text = fence_workflow.read_text(encoding="utf-8")
        assert "check-service-src-import-fence.sh" in text
        assert "Check service ↔ src import fence" in text
        # Old telescope-only step title must be gone
        assert "Check service/telescope ↔ src import fence" not in text
        assert "dev" in text
        assert "ftr/**" in text
