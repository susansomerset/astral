"""AST-1727 — Railway Phase 1 toml + bidirectional service↔src CI fence."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_SERVICE_IMPORT = re.compile(
    r"^\s*(?:from|import)\s+service(?:\.|\s|,|$)",
    re.MULTILINE,
)


@pytest.fixture
def fence_script() -> Path:
    path = _REPO / "scripts" / "ci" / "check-service-src-import-fence.sh"
    assert path.is_file(), f"missing {path} — sync publish-ref product (AST-1727)"
    return path


@pytest.fixture
def fence_workflow() -> Path:
    path = _REPO / ".github" / "workflows" / "service-src-import-fence.yml"
    assert path.is_file(), f"missing {path} — sync publish-ref product (AST-1727)"
    return path


@pytest.fixture
def railway_toml(telescope_root: Path) -> Path:
    path = telescope_root / "railway.toml"
    assert path.is_file(), f"missing {path} — sync publish-ref product (AST-1727)"
    return path


class TestRailwayPhase1Toml:
    def test_num_replicas_one_and_dockerfile_paths(self, railway_toml: Path) -> None:
        text = railway_toml.read_text(encoding="utf-8")
        assert "numReplicas = 1" in text
        assert 'dockerfilePath = "service/telescope/Dockerfile"' in text
        assert 'builder = "DOCKERFILE"' in text
        assert "restartPolicyType" in text and "ON_FAILURE" in text
        assert "memoryBytes = 2147483648" in text

    def test_unauthenticated_healthcheck_drain_and_no_phase2_hooks(
        self, railway_toml: Path
    ) -> None:
        text = railway_toml.read_text(encoding="utf-8")
        # Queue worker: /healthz has no bearer, so Railway can probe it.
        assert 'healthcheckPath = "/healthz"' in text
        assert "drainingSeconds" in text
        assert "Judoscale" not in text
        assert "serviceInstanceUpdate" not in text


class TestBidirectionalImportFence:
    def test_src_py_files_have_zero_service_imports(self) -> None:
        src_root = _REPO / "src"
        assert src_root.is_dir()
        offenders: list[str] = []
        for path in sorted(src_root.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if _SERVICE_IMPORT.search(text):
                offenders.append(str(path.relative_to(_REPO)))
        assert offenders == [], f"service imports under src/: {offenders}"

    def test_ci_fence_script_exits_zero(self, fence_script: Path) -> None:
        proc = subprocess.run(
            ["bash", str(fence_script)],
            cwd=_REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "import fence: ok" in proc.stdout

    def test_ci_fence_script_catches_src_import_in_service(
        self, fence_script: Path, telescope_root: Path, tmp_path: Path
    ) -> None:
        # Copy tree to temp is heavy — instead write a throwaway offender under
        # service/telescope and remove in finally (engineer's tree must stay clean).
        offender = telescope_root / "_betty_fence_probe.py"
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

    def test_workflow_invokes_fence_script(self, fence_workflow: Path) -> None:
        text = fence_workflow.read_text(encoding="utf-8")
        assert "check-service-src-import-fence.sh" in text
        assert "Service↔src import fence" in text or "import fence" in text.lower()
        assert "dev" in text
        assert "ftr/**" in text
