"""AST-2135: migrate_company_scrape_to_telescope_data — export / load / clear on a temp DB only."""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/migrate_company_scrape_to_telescope_data.py"
# api_admin imports `ui.*` (src on sys.path), same as tests/component/ui/conftest.py
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))


def _load_module():
    spec = importlib.util.spec_from_file_location("migrate_company_scrape_ast2135", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()


@pytest.fixture
def db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Fresh astral.db under tmp_path — never data/astral.db (live symlink in epic worktrees)."""
    from src.data import database
    from src.utils import logging as log_mod

    monkeypatch.setenv("ASTRAL_DB_DIR", str(tmp_path))
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "astral.db")
    # Every process-global schema guard, so tables are created in this DB
    for name in dir(database):
        if name.startswith("_") and name.endswith(("_ensured", "_applied")) and isinstance(getattr(database, name), bool):
            monkeypatch.setattr(database, name, False)
    database.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_data={"name": "T"})
    yield database
    # Buffered app_log rows (the script's log lines) flush while DB_PATH still points at tmp
    if log_mod._db_handler_instance is not None:
        log_mod._db_handler_instance.flush()


def _rows(db) -> dict[str, tuple]:
    conn = db._get_connection()
    try:
        return {r[0]: (r[1], r[2]) for r in conn.execute("SELECT short_name, company_data, updated_at FROM company")}
    finally:
        conn.close()


def _tele_count(db) -> int:
    conn = db._get_connection()
    try:
        db._ensure_telescope_data_schema(conn)
        return conn.execute("SELECT COUNT(*) FROM telescope_data").fetchone()[0]
    finally:
        conn.close()


_ACME_PAGES = [
    {"url": "https://acme.com/careers", "visible_text": "Open roles", "enumerated_nav_links": "1: https://acme.com/jobs/a"},
    {"url": "https://acme.com/jobs", "visible_text": "More roles"},
]


def _seed(db) -> None:
    """Legacy (pre-AST-2130) blobs in every reader shape, plus already-migrated and odd-shaped companies."""
    from src.core import gazer
    from src.core.roster import _assemble_pjl_content, _rebuilt_pjl_nav_links

    acme_cd: dict[str, Any] = {
        "homepage_text": "Acme homepage",
        "nav_links": "1: https://acme.com/about\n2: https://acme.com/careers",
        "website_content": [{"url": "https://acme.com/c1", "content": "Culture one"},
                            {"url": "https://acme.com/c2", "content": "Culture two"}],
        "job_list_visible": "Job list page",
        "pjl_scrape_pages": _ACME_PAGES,
        "possible_joblist_links": ["https://acme.com/careers", "https://acme.com/jobs"],
        "prefilter_company_notes": "untouched",
    }
    acme_cd["pjl_assembled_content"] = _assemble_pjl_content(_ACME_PAGES)
    acme_cd["pjl_nav_links"] = _rebuilt_pjl_nav_links(acme_cd)
    db.save_company("acme", "WATCH", company_website="https://acme.com", job_site="https://acme.com/careers",
                    candidate_id="cand-1", company_data=acme_cd)
    # Oldest website_content shape; derived PJL text that no longer matches a rebuild -> kept stored
    db.save_company("beta", "WATCH", company_website="https://beta.io", candidate_id="cand-1", company_data={
        "website_content": "Beta culture blob",
        "pjl_scrape_pages": [{"url": "https://beta.io/jobs", "visible_text": "Beta roles"}],
        "possible_joblist_links": ["https://beta.io/jobs"],
        "pjl_assembled_content": "hand-edited assembled text",
        "pjl_nav_links": "1: https://beta.io/stale",
    })
    # Written after AST-2134: ids already — nothing to move
    rid = gazer.keep_telescope_data("cand-1", "https://gamma.dev", "VISIBLE_TEXT", "Gamma home")
    db.save_company("gamma", "WATCH", company_website="https://gamma.dev", candidate_id="cand-1",
                    company_data={"homepage_text": rid, "website_content": [{"url": "https://gamma.dev/c", "id": rid}]})
    # Shapes no reader writes: left as they are, warned
    db.save_company("delta", "WATCH", company_website="https://delta.co", company_data={
        "homepage_text": {"not": "text"},
        "website_content": [{"url": "https://delta.co/c", "content": "Delta", "extra": 1}, {"url": "u", "content": "  "}],
    })
    db.save_company("empty", "NEW", company_website="https://empty.org")
    # PJL pages with no stored derived fields (post-AST-2132 shape) plus one odd row the resolver would drop
    db.save_company("epsilon", "WATCH", company_website="https://eps.net", company_data={
        "pjl_scrape_pages": [{"url": "https://eps.net/jobs", "visible_text": "Eps roles"},
                             {"url": "https://eps.net/x", "visible_text": "odd", "note": "?"}],
        "possible_joblist_links": ["https://eps.net/jobs"],
    })


def _admin_previews(monkeypatch: pytest.MonkeyPatch, short_name: str) -> dict[str, str]:
    from ui.api import api_admin as admin_mod

    monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "company"})
    return {t: admin_mod._build_adhoc_live_content(t, short_name) for t in ("prefilter_company", "select_job_page", "gaze")}


def _reader_view(cd: dict) -> dict:
    """What roster readers see for a company_data blob (ids resolved, derived PJL rebuilt)."""
    from src.core import roster

    r = roster._resolved_company_data(cd)
    keys = ("homepage_text", "nav_links", "website_content", "job_list_visible", "pjl_scrape_pages", "pjl_nav_links")
    return {**{k: r.get(k) for k in keys}, "pjl_maps": roster._pjl_maps_from_company_data(r)}


class TestAst2135Export:
    def test_ac10_export_writes_file_and_no_db_change(self, db, tmp_path: Path, capsys) -> None:
        _seed(db)
        before, count = _rows(db), _tele_count(db)
        out = tmp_path / "scrape.json"
        assert _mod._export(out) == 0
        assert _rows(db) == before and _tele_count(db) == count
        data = json.loads(out.read_text())
        assert data["db_path"] == str(db.DB_PATH)
        assert set(data["companies"]) == {"acme", "beta", "epsilon"}  # gamma already ids; delta / empty nothing movable
        printed = capsys.readouterr().out
        assert "Companies scanned: 6  with changes: 3" in printed and f"Wrote {out}" in printed

    def test_export_refuses_existing_file(self, db, tmp_path: Path) -> None:
        out = tmp_path / "scrape.json"
        out.write_text("keep me")
        assert _mod._export(out) == 2
        assert out.read_text() == "keep me"

    def test_export_rows_and_target_values(self, db, tmp_path: Path, capsys) -> None:
        _seed(db)
        out = tmp_path / "scrape.json"
        _mod._export(out)
        data = json.loads(out.read_text())
        rows, acme, beta = data["rows"], data["companies"]["acme"]["keys"], data["companies"]["beta"]["keys"]

        def row(rid: str) -> tuple:
            r = rows[rid]
            return r["candidate_id"], r["url"], r["data_type"], r["content"]

        assert row(acme["homepage_text"]["value"]) == ("cand-1", "https://acme.com", "VISIBLE_TEXT", "Acme homepage")
        assert row(acme["nav_links"]["value"]) == (
            "cand-1", "https://acme.com", "PAGE_LINKS", "1: https://acme.com/about\n2: https://acme.com/careers")
        assert row(acme["job_list_visible"]["value"]) == ("cand-1", "https://acme.com/careers", "VISIBLE_TEXT", "Job list page")
        wc = acme["website_content"]["value"]
        assert [e["url"] for e in wc] == ["https://acme.com/c1", "https://acme.com/c2"]
        assert [row(e["id"]) for e in wc] == [("cand-1", "https://acme.com/c1", "VISIBLE_TEXT", "Culture one"),
                                              ("cand-1", "https://acme.com/c2", "VISIBLE_TEXT", "Culture two")]
        pages = acme["pjl_scrape_pages"]["value"]
        assert [set(p) for p in pages] == [{"url", "id", "links_id"}, {"url", "id"}]
        assert row(pages[0]["links_id"]) == ("cand-1", "https://acme.com/careers", "PAGE_LINKS", "1: https://acme.com/jobs/a")
        # Derived PJL fields equal their rebuild -> NULL; prefilter notes never touched
        assert acme["pjl_assembled_content"]["value"] is None and acme["pjl_nav_links"]["value"] is None
        assert "prefilter_company_notes" not in acme
        # beta: plain-string website_content -> one row; mismatched derived text kept stored (warned)
        assert row(beta["website_content"]["value"]) == ("cand-1", "https://beta.io", "VISIBLE_TEXT", "Beta culture blob")
        assert "pjl_assembled_content" not in beta and "pjl_nav_links" not in beta
        # acme 8 (home, nav, 2 culture, job list, 2 pages + 1 links) + beta 2 (website_content, 1 page)
        assert len(rows) == 11  # + epsilon's one movable page
        eps = data["companies"]["epsilon"]["keys"]
        assert set(eps) == {"pjl_scrape_pages"}  # no derived fields stored -> none to clear
        assert eps["pjl_scrape_pages"]["value"][1] == {"url": "https://eps.net/x", "visible_text": "odd", "note": "?"}
        assert "Warnings: 5" in capsys.readouterr().out  # beta asm + nav, delta homepage + website_content, epsilon odd page


class TestAst2135LoadClear:
    def _export(self, db, tmp_path: Path) -> Path:
        _seed(db)
        out = tmp_path / "scrape.json"
        assert _mod._export(out) == 0
        return out

    def test_ac10_load_twice_adds_nothing_second_time(self, db, tmp_path: Path, capsys) -> None:
        out = self._export(db, tmp_path)
        rows = json.loads(out.read_text())["rows"]
        base = _tele_count(db)
        assert _mod._load(out) == 0
        assert _tele_count(db) == base + len(rows)
        assert _mod._load(out) == 0
        assert _tele_count(db) == base + len(rows)
        printed = capsys.readouterr().out
        assert f"inserted: 0  already present: {len(rows)}" in printed
        # Stored content round-trips through compression verbatim
        assert db.get_telescope_data_for_ids(list(rows)) == {k: r["content"] for k, r in rows.items()}

    def test_ac10_clear_refuses_on_empty_telescope_data(self, db, tmp_path: Path) -> None:
        out = self._export(db, tmp_path)
        before = _rows(db)
        assert _mod._clear(out) == 1
        assert _rows(db) == before

    def test_clear_refuses_when_any_row_missing(self, db, tmp_path: Path) -> None:
        out = self._export(db, tmp_path)
        _mod._load(out)
        some_id = next(iter(json.loads(out.read_text())["rows"]))
        conn = db._get_connection()
        try:
            conn.execute("DELETE FROM telescope_data WHERE telescope_data_id = ?", (some_id,))
            conn.commit()
        finally:
            conn.close()
        before = _rows(db)
        assert _mod._clear(out) == 1
        assert _rows(db) == before

    def test_ac5_ac6_ac11_after_load_and_clear(self, db, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import gazer

        out = self._export(db, tmp_path)
        names = ("acme", "beta", "gamma", "delta", "empty", "epsilon")
        views = {sn: _reader_view(db.get_company(sn)["company_data"] or {}) for sn in names}
        previews = {sn: _admin_previews(monkeypatch, sn) for sn in names}
        before = _rows(db)
        assert _mod._load(out) == 0
        assert _mod._clear(out) == 0
        after = _rows(db)

        # AC 6 / AC 11 across every company: reader view and admin previews byte-identical
        for sn in names:
            assert _reader_view(db.get_company(sn)["company_data"] or {}) == views[sn], sn
            assert _admin_previews(monkeypatch, sn) == previews[sn], sn
        assert previews["acme"]["prefilter_company"] and previews["acme"]["gaze"]  # non-vacuous

        # AC 5: acme's scraped keys hold ids; derived PJL fields are NULL
        conn = db._get_connection()
        try:
            j = lambda path: conn.execute(
                f"SELECT json_extract(company_data, '$.{path}') FROM company WHERE short_name='acme'").fetchone()[0]
            for key in ("homepage_text", "nav_links", "job_list_visible"):
                assert gazer.is_telescope_id(j(key)), key
            assert j("pjl_assembled_content") is None and j("pjl_nav_links") is None
        finally:
            conn.close()
        cd = db.get_company("acme")["company_data"]
        assert all(set(e) == {"url", "id"} for e in cd["website_content"])
        assert [set(p) for p in cd["pjl_scrape_pages"]] == [{"url", "id", "links_id"}, {"url", "id"}]
        assert cd["prefilter_company_notes"] == "untouched"
        assert gazer.is_telescope_id(db.get_company("beta")["company_data"]["website_content"])
        # Untouched companies byte-identical; updated_at kept on migrated ones
        for sn in ("gamma", "delta", "empty"):
            assert after[sn] == before[sn], sn
        for sn in ("acme", "beta", "epsilon"):
            assert after[sn][1] == before[sn][1], sn

    def test_clear_leaves_keys_changed_since_export(self, db, tmp_path: Path, capsys) -> None:
        out = self._export(db, tmp_path)
        _mod._load(out)
        cd = db.get_company("acme")["company_data"]
        db.update_company("acme", company_data={**cd, "homepage_text": "Re-scraped since export"})
        assert _mod._clear(out) == 0
        cd = db.get_company("acme")["company_data"]
        assert cd["homepage_text"] == "Re-scraped since export"
        from src.core import gazer
        assert gazer.is_telescope_id(cd["nav_links"])
        assert "left as is: 1" in capsys.readouterr().out

    def test_clear_rerun_and_deleted_company(self, db, tmp_path: Path, capsys) -> None:
        out = self._export(db, tmp_path)
        _mod._load(out)
        conn = db._get_connection()
        try:
            conn.execute("DELETE FROM company WHERE short_name='beta'")
            conn.commit()
        finally:
            conn.close()
        assert _mod._clear(out) == 0
        first = _rows(db)
        assert "Companies updated: 2/3" in capsys.readouterr().out
        # Re-run: every key already swapped -> nothing written
        assert _mod._clear(out) == 0
        assert _rows(db) == first
        assert "Companies updated: 0/3  keys swapped: 0" in capsys.readouterr().out


class TestAst2135Cli:
    def test_main_prints_db_path_then_dispatches(self, db, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        out = tmp_path / "m.json"
        out.write_text(json.dumps({"rows": {}, "companies": {}}))
        monkeypatch.setattr(sys, "argv", ["migrate", "load", "--file", str(out), "--db-dir", str(tmp_path)])
        assert _mod.main() == 0
        printed = capsys.readouterr().out.splitlines()
        # Sibling script tests can leave DEBUG logging on stdout, so the summary line is matched anywhere
        assert printed[0] == f"DB: {db.DB_PATH}" and any("inserted: 0" in ln for ln in printed)
        assert os.environ["ASTRAL_DB_DIR"] == str(tmp_path.resolve())
        # Without --db-dir the app's DB is used (here the fixture's tmp DB) and still printed first
        monkeypatch.setattr(sys, "argv", ["migrate", "load", "--file", str(out)])
        assert _mod.main() == 0
        assert capsys.readouterr().out.splitlines()[0] == f"DB: {db.DB_PATH}"

    def test_db_dir_pins_every_mode_to_the_given_folder(self, db, tmp_path: Path) -> None:
        """Subprocess end-to-end: --db-dir wins over ASTRAL_DB_DIR (pointed at a decoy temp folder)."""
        _seed(db)
        decoy = tmp_path / "decoy"
        decoy.mkdir()
        out = tmp_path / "cli.json"
        env = {**os.environ, "ASTRAL_DB_DIR": str(decoy)}

        def run(mode: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(_SCRIPT), mode, "--file", str(out), "--db-dir", str(tmp_path)],
                capture_output=True, text=True, env=env, cwd=str(REPO_ROOT), timeout=120, check=False,
            )

        for mode in ("export", "load", "clear"):
            res = run(mode)
            assert res.returncode == 0, (mode, res.stdout, res.stderr)
            assert res.stdout.splitlines()[0] == f"DB: {tmp_path.resolve() / 'astral.db'}", mode
        from src.core import gazer
        assert gazer.is_telescope_id(db.get_company("acme")["company_data"]["homepage_text"])
        assert not (decoy / "astral.db").exists() or sqlite3.connect(decoy / "astral.db").execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name IN ('company', 'telescope_data')").fetchone()[0] == 0
