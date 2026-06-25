"""AST-614: launch.sh --vite auto-installs frontend deps when @stytch/react missing.
AST-758: launch.sh --flask rebuilds stale frontend dist before Flask start."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
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
if [[ "$1" == "run" && "$2" == "build" ]]; then
  mkdir -p dist
  print -u2 "ok" > dist/index.html
  print -u2 "fake-npm-build"
  exit 0
fi
print -u2 "unexpected npm args: $*"
exit 1
"""

_FAKE_PYTHON = """#!/usr/bin/env zsh
setopt errexit nounset pipefail
if [[ "$1" == "-c" && "$2" == "import stytch" ]]; then
  exit 0
fi
if [[ "$1" == "server.py" ]]; then
  print -u2 "fake-python-server"
  exit 0
fi
print -u2 "unexpected python args: $*"
exit 1
"""

_VENV_ACTIVATE = """#!/usr/bin/env zsh
export VIRTUAL_ENV="${PWD}/.venv"
export PATH="${VIRTUAL_ENV}/bin:${PATH}"
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


def _mini_flask_repo(tmp_path: Path, *, stale_dist: bool) -> Path:
    repo = _mini_repo(tmp_path, with_stytch=True)
    venv_bin = repo / ".venv/bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "activate").write_text(_VENV_ACTIVATE, encoding="utf-8")
    py = venv_bin / "python"
    py.write_text(_FAKE_PYTHON, encoding="utf-8")
    py.chmod(0o755)
    ui_dir = repo / "src/ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    (ui_dir / "server.py").write_text("# stub\n", encoding="utf-8")
    frontend = repo / "src/ui/frontend"
    src_dir = frontend / "src"
    src_dir.mkdir(parents=True)
    tsx = src_dir / "App.tsx"
    tsx.write_text("export default function App() { return null }\n", encoding="utf-8")
    dist_dir = frontend / "dist"
    dist_dir.mkdir(parents=True)
    dist_index = dist_dir / "index.html"
    dist_index.write_text("old", encoding="utf-8")
    now = time.time()
    if stale_dist:
        os.utime(dist_index, (now - 120, now - 120))
        os.utime(tsx, (now, now))
    else:
        os.utime(tsx, (now - 120, now - 120))
        os.utime(dist_index, (now, now))
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


def _run_flask(repo: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{repo / 'bin'}:{env['PATH']}"
    return subprocess.run(
        ["zsh", str(repo / "launch.sh"), "--flask"],
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


@pytest.mark.skipif(shutil.which("zsh") is None, reason="zsh required for launch.sh")
class TestLaunchFrontendBuild:
    def test_run_flask_rebuilds_when_dist_older_than_src(self, tmp_path: Path) -> None:
        repo = _mini_flask_repo(tmp_path, stale_dist=True)
        result = _run_flask(repo)
        assert result.returncode == 0, result.stderr
        assert "frontend dist stale or missing — running npm run build" in result.stderr
        assert "fake-npm-build" in result.stderr
        assert "fake-python-server" in result.stderr

    def test_run_flask_skips_build_when_dist_is_fresh(self, tmp_path: Path) -> None:
        repo = _mini_flask_repo(tmp_path, stale_dist=False)
        result = _run_flask(repo)
        assert result.returncode == 0, result.stderr
        assert "frontend dist stale or missing" not in result.stderr
        assert "fake-npm-build" not in result.stderr
        assert "fake-python-server" in result.stderr
