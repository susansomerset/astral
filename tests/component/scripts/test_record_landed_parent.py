"""AST-683 / AST-693 / AST-800: record-landed-parent helper + prep-uat wiring."""

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
PREP_UAT_LAND_SH = REPO_ROOT / "scripts/git/prep-uat-land.sh"
REBUILD_SCRIPT = REPO_ROOT / "scripts/rebuild_merge_ticket_log.py"

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

_REBUILD_STUB = """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.merge_ticket_log import rebuild_merge_ticket_log

parent = "AST-999"
if "--landing-parent" in sys.argv:
    parent = sys.argv[sys.argv.index("--landing-parent") + 1]

rebuild_merge_ticket_log(
    [{"ticket_id": parent, "recorded_at": "2026-06-25T00:00:00+00:00"}]
)
print(json.dumps({"count": 1, "parents": [parent], "landing_parent": parent.upper()}))
"""


def _copy_tree(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _mini_repo(tmp_path: Path, *, with_rebuild: bool = True) -> Path:
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
        f'MERGE_TICKET_LOG_CONFIG = {{"log_path": Path(r"{log_path}"), "uat_state_name": "User Testing"}}\n',
        encoding="utf-8",
    )
    if with_rebuild:
        rebuild_path = repo / "scripts/rebuild_merge_ticket_log.py"
        rebuild_path.parent.mkdir(parents=True, exist_ok=True)
        rebuild_path.write_text(_REBUILD_STUB, encoding="utf-8")
    log_path.write_text("[]\n", encoding="utf-8")
    (repo / "scripts/git/record-landed-parent.sh").chmod(0o755)
    if with_rebuild:
        (repo / "scripts/rebuild_merge_ticket_log.py").chmod(0o755)

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


class TestRecordLandedParentShell:
    def test_record_landed_parent_wires_rebuild_not_append(self) -> None:
        text = RECORD_SCRIPT.read_text(encoding="utf-8")
        assert "rebuild_merge_ticket_log.py" in text
        assert "append_merge_ticket_log.py" not in text
        assert "rebuild merge ticket log" in text

    def test_record_landed_parent_passes_landing_parent_flag(self) -> None:
        text = RECORD_SCRIPT.read_text(encoding="utf-8")
        assert '--landing-parent "$PARENT_ID"' in text


class TestRecordLandedParent:
    def test_record_landed_parent_rebuilds_and_commits(self, tmp_path: Path) -> None:
        repo = _mini_repo(tmp_path)
        result = _run_record(repo, "AST-999")
        assert result.returncode == 0, result.stderr
        assert "RESULT: record-landed-parent status=ok parent=AST-999" in result.stdout

        log = json.loads((repo / "data/merge_ticket_log.json").read_text(encoding="utf-8"))
        assert len(log) == 1
        assert log[0]["ticket_id"] == "AST-999"
        assert "recorded_at" in log[0]
        assert '"landing_parent": "AST-999"' in result.stdout

        log_result = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "rebuild merge ticket log" in log_result.stdout

    def test_record_landed_parent_missing_rebuild_script_blocks(self, tmp_path: Path) -> None:
        repo = _mini_repo(tmp_path, with_rebuild=False)
        result = _run_record(repo)
        assert result.returncode != 0
        assert "BLOCKED" in result.stderr
        assert "rebuild script missing" in result.stderr


class TestMergeParentShell:
    def test_merge_parent_shell_does_not_record_merge_ticket_log(self) -> None:
        text = MERGE_PARENT_SH.read_text(encoding="utf-8")
        assert "record-landed-parent.sh" not in text


class TestPrepUatLandShell:
    def test_prep_uat_land_shell_wires_record_helper_after_push(self) -> None:
        text = PREP_UAT_LAND_SH.read_text(encoding="utf-8")
        push_idx = text.index('git -C "$MAIN" push origin dev')
        record_idx = text.index("record-landed-parent.sh")
        result_idx = text.index("RESULT: prep-uat-land status=ok")
        assert push_idx < record_idx < result_idx
        assert "BLOCKED: parent segment must contain AST-NNN" in text
        assert 'grep -oiE \'AST-[0-9]+\'' in text or 'grep -oiE "AST-[0-9]+"' in text
