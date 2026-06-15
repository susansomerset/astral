"""AST-683: finish-up record-landed-parent helper + merge-parent wiring."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RECORD_SCRIPT = REPO_ROOT / "scripts/git/record-landed-parent.sh"
MERGE_PARENT_SH = REPO_ROOT / "scripts/git/merge-parent.sh"
APPEND_SCRIPT = REPO_ROOT / "scripts/append_merge_ticket_log.py"

_FAKE_GIT = """#!/usr/bin/env bash
set -euo pipefail
REAL_GIT="${REAL_GIT:-/usr/bin/git}"
for arg in "$@"; do
  if [[ "$arg" == "push" ]]; then
    exit 0
  fi
done
exec "$REAL_GIT" "$@"
"""


def _copy_tree(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _mini_repo(tmp_path: Path, *, with_append: bool = True) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    for rel in (
        "src/__init__.py",
        "src/utils/__init__.py",
        "src/utils/merge_ticket_log.py",
        "scripts/git/record-landed-parent.sh",
    ):
        _copy_tree(REPO_ROOT / rel, repo / rel)
    log_path = repo / "data" / "merge_ticket_log.json"
    (repo / "data").mkdir()
    (repo / "src/utils/config.py").write_text(
        f'"""Minimal config stub for AST-683 shell tests."""\n'
        f"from pathlib import Path\n\n"
        f'MERGE_TICKET_LOG_CONFIG = {{"log_path": Path(r"{log_path}")}}\n',
        encoding="utf-8",
    )
    if with_append:
        _copy_tree(APPEND_SCRIPT, repo / "scripts/append_merge_ticket_log.py")
    log_path.write_text("[]\n", encoding="utf-8")
    (repo / "scripts/git/record-landed-parent.sh").chmod(0o755)
    if with_append:
        (repo / "scripts/append_merge_ticket_log.py").chmod(0o755)

    real_git = shutil.which("git") or "/usr/bin/git"
    subprocess.run(
        [real_git, "init"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [real_git, "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [real_git, "config", "user.name", "AST-683 Test"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [real_git, "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [real_git, "commit", "-m", "seed"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return repo


def _run_record(repo: Path, parent_id: str = "AST-999") -> subprocess.CompletedProcess[str]:
    fake_bin = repo.parent / "bin"
    fake_bin.mkdir(exist_ok=True)
    fake_git = fake_bin / "git"
    fake_git.write_text(_FAKE_GIT, encoding="utf-8")
    fake_git.chmod(0o755)
    fake_python = fake_bin / "python3"
    fake_python.write_text(
        f'#!/usr/bin/env bash\nexec "{sys.executable}" "$@"\n',
        encoding="utf-8",
    )
    fake_python.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["REAL_GIT"] = shutil.which("git") or "/usr/bin/git"
    env["ASTRAL_DB_DIR"] = str(repo / "data")
    env["PYTHONUNBUFFERED"] = "1"
    return subprocess.run(
        ["bash", str(repo / "scripts/git/record-landed-parent.sh"), str(repo), parent_id],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class TestRecordLandedParent:
    def test_record_landed_parent_appends_and_commits(self, tmp_path: Path) -> None:
        repo = _mini_repo(tmp_path)
        result = _run_record(repo, "AST-999")
        assert result.returncode == 0, result.stderr
        assert "RESULT: record-landed-parent status=ok parent=AST-999" in result.stdout

        log = json.loads((repo / "data/merge_ticket_log.json").read_text(encoding="utf-8"))
        assert len(log) == 1
        assert log[0]["ticket_id"] == "AST-999"
        assert "recorded_at" in log[0]

        log_result = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "finish-up(AST-999)" in log_result.stdout

    def test_record_landed_parent_missing_append_script_blocks(self, tmp_path: Path) -> None:
        repo = _mini_repo(tmp_path, with_append=False)
        result = _run_record(repo)
        assert result.returncode != 0
        assert "BLOCKED" in result.stderr
        assert "append script missing" in result.stderr


class TestMergeParentShell:
    def test_merge_parent_shell_references_record_helper(self) -> None:
        text = MERGE_PARENT_SH.read_text(encoding="utf-8")
        assert "record-landed-parent.sh" in text
        assert 'grep -oiE \'AST-[0-9]+\'' in text or 'grep -oiE "AST-[0-9]+"' in text
