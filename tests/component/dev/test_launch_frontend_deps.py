"""AST-614: launch.sh --vite auto-installs frontend deps when @stytch/react missing."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
LAUNCH_SH = REPO_ROOT / "launch.sh"

_FAKE_NPM = """#!/usr/bin/env zsh
setopt errexit nounset pipefail
if [[ "$1" == "install" ]]; then
  mkdir -p node_modules/@stytch/react
  print -u2 "fake-npm-install"
  exit 0
fi
if [[ "$1" == "run" && "$2" == "dev" ]]; then
  print -u2 "fake-npm-dev"
  exit 0
fi
print -u2 "unexpected npm args: $*"
exit 1
"""


def _mini_repo(tmp_path: Path, *, with_stytch: bool) -> Path:
    repo = tmp_path / "repo"
    frontend = repo / "src/ui/frontend"
    frontend.mkdir(parents=True)
    (frontend / "package.json").write_text('{"name":"astral-frontend-test"}', encoding="utf-8")
    if with_stytch:
        (frontend / "node_modules/@stytch/react").mkdir(parents=True)
    shutil.copy2(LAUNCH_SH, repo / "launch.sh")
    (repo / "launch.sh").chmod(0o755)
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    npm = bin_dir / "npm"
    npm.write_text(_FAKE_NPM, encoding="utf-8")
    npm.chmod(0o755)
    return repo


def _run_vite(repo: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{repo / 'bin'}:{env['PATH']}"
    return subprocess.run(
        ["zsh", str(repo / "launch.sh"), "--vite"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


@pytest.mark.skipif(shutil.which("zsh") is None, reason="zsh required for launch.sh")
class TestLaunchFrontendDeps:
    def test_run_vite_installs_when_stytch_react_missing(self, tmp_path: Path) -> None:
        repo = _mini_repo(tmp_path, with_stytch=False)
        result = _run_vite(repo)
        assert result.returncode == 0, result.stderr
        assert "installing frontend deps (missing node_modules/@stytch/react)" in result.stderr
        assert "fake-npm-install" in result.stderr
        assert "fake-npm-dev" in result.stderr
        assert (repo / "src/ui/frontend/node_modules/@stytch/react").is_dir()

    def test_run_vite_skips_install_when_stytch_react_present(self, tmp_path: Path) -> None:
        repo = _mini_repo(tmp_path, with_stytch=True)
        result = _run_vite(repo)
        assert result.returncode == 0, result.stderr
        assert "installing frontend deps" not in result.stderr
        assert "fake-npm-install" not in result.stderr
        assert "fake-npm-dev" in result.stderr
