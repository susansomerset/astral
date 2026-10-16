"""AST-2087: retired terminal-state remap (`_terminal_state_remap_conn`, `migrate_terminal_state_names`, operator CLI).

Branches: resolver — single target / page-status error prefix (hit, miss) / bare-family widening /
no predecessor / hop label (run_next hit, no target) / trigger match (one, none, shared → dispatch
tie-break by candidate or NULL row, still ambiguous); predecessor — from_state, prior to_state,
_RETRY stripped, bad JSON, no entry; remap — skipped / unregistered / dry run / execute write surface;
dispatch_task — catalog trigger in targets, not in targets, no catalog default.
Retired names are typed here on purpose: the AC 2 no-retired-names grep covers `src/` only.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
_SCRIPT = REPO_ROOT / "scripts/migrations/migrate_terminal_state_names.py"

_TS = "2026-01-01T00:00:00"


@pytest.fixture
def remap_db(sqlite_in_memory):
    """Fresh DB with every table the remap reads; ensure runs here because the remap never does."""
    db = sqlite_in_memory
    db.ensure_all_upsert_registry_schemas_at_startup()
    conn = db._get_connection()
    try:
        db._ensure_meteorite_schema(conn)
    finally:
        conn.close()
    return db


def _hist(*states: str, from_states: Optional[List[Optional[str]]] = None) -> str:
    # job/meteorite history has no from_state; company/candidate pass one per entry
    out = []
    for i, s in enumerate(states):
        e: Dict[str, Any] = {"to_state": s, "timestamp": _TS}
        if from_states is not None and from_states[i] is not None:
            e["from_state"] = from_states[i]
        out.append(e)
    return json.dumps(out)


def _job(conn, jid: str, state: str, history: Optional[str] = None, cid: str = "c1") -> None:
    conn.execute(
        "INSERT INTO job (astral_job_id, candidate_id, state, state_history, created_at, updated_at, state_changed_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (jid, cid, state, history, _TS, _TS, _TS),
    )


def _company(conn, sn: str, state: str, history: Optional[str] = None) -> None:
    conn.execute(
        "INSERT INTO company (short_name, candidate_id, state, state_history, updated_at, state_changed_at)"
        " VALUES (?, 'c1', ?, ?, ?, ?)",
        (sn, state, history, _TS, _TS),
    )


def _candidate(conn, cid: str, state: str, history: Optional[str] = None) -> None:
    conn.execute(
        "INSERT INTO candidate (astral_candidate_id, state, state_history, updated_at, state_changed_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (cid, state, history, _TS, _TS),
    )


def _meteorite(conn, src_id: str, state: str, error: Optional[str] = None, history: Optional[str] = None) -> None:
    conn.execute(
        "INSERT INTO meteorite (candidate_id, source_kind, source_id, state, error, state_history,"
        " created_at, updated_at, state_changed_at) VALUES ('c1', 'email', ?, ?, ?, ?, ?, ?, ?)",
        (src_id, state, error, history, _TS, _TS, _TS),
    )


def _dispatch(conn, task_key: str, trigger: str, cid: Optional[str] = None) -> None:
    conn.execute(
        "INSERT INTO dispatch_task (candidate_id, task_key, trigger_state, min_count) VALUES (?, ?, ?, 1)",
        (cid, task_key, trigger),
    )


def _run_next(conn, task_key: str, nxt: str, current: int = 1) -> None:
    conn.execute("INSERT INTO agent_task (task_key, run_next, current) VALUES (?, ?, ?)", (task_key, nxt, current))


def _seeded(db, seed) -> None:
    conn = db._get_connection()
    try:
        seed(conn)
        conn.commit()
    finally:
        conn.close()


def _remap(db, seed=None, *, dry_run: bool = False) -> Dict[str, Any]:
    if seed is not None:
        _seeded(db, seed)
    conn = db._get_connection()
    try:
        return db._terminal_state_remap_conn(conn, dry_run=dry_run)
    finally:
        conn.close()


def _query(db, sql: str, args: tuple = ()) -> List[tuple]:
    conn = db._get_connection()
    try:
        return [tuple(r) for r in conn.execute(sql, args)]
    finally:
        conn.close()


def _state(db, table: str, pk: str, key: Any) -> str:
    return _query(db, f"SELECT state FROM {table} WHERE {pk} = ?", (key,))[0][0]


def _dump(db) -> Dict[str, List[tuple]]:
    return {t: _query(db, f"SELECT * FROM {t} ORDER BY 1") for t in ("job", "company", "candidate", "meteorite", "dispatch_task")}


class TestAst2087TerminalPredecessor:
    """`_terminal_predecessor`: the state a row left to land on its retired name."""

    @pytest.mark.parametrize(
        ("raw", "state", "want"),
        [
            pytest.param(_hist("PASSED_JOBLIST", "JD_SCRAPE_FAIL"), "JD_SCRAPE_FAIL", "PASSED_JOBLIST", id="prior_to_state"),
            pytest.param(
                _hist("WEBSITE_FOUND", "CANNOT_READ_WEBSITE", from_states=[None, "HOMEPAGE_READY"]),
                "CANNOT_READ_WEBSITE",
                "HOMEPAGE_READY",
                id="from_state_wins",
            ),
            # the last landing on the state counts, not the first
            pytest.param(
                _hist("PASSED_JOBLIST", "JD_SCRAPE_FAIL", "RELATIVE_JOB_LINK", "JD_SCRAPE_FAIL"),
                "JD_SCRAPE_FAIL",
                "RELATIVE_JOB_LINK",
                id="last_entry",
            ),
            pytest.param(_hist("JD_SCRAPE_FAIL"), "JD_SCRAPE_FAIL", None, id="only_entry"),
            pytest.param(_hist("PASSED_JOBLIST"), "JD_SCRAPE_FAIL", None, id="never_landed"),
            pytest.param("not json", "JD_SCRAPE_FAIL", None, id="bad_json"),
            pytest.param(None, "JD_SCRAPE_FAIL", None, id="null"),
            pytest.param(json.dumps(["x", {"to_state": "JD_SCRAPE_FAIL"}]), "JD_SCRAPE_FAIL", None, id="non_dict_prior"),
        ],
    )
    def test_predecessor(self, remap_db, raw: Optional[str], state: str, want: Optional[str]) -> None:
        assert remap_db._terminal_predecessor(raw, state) == want


class TestAst2087ResolutionRules:
    """Each resolution rule, end to end on real rows (execute)."""

    def test_single_target_needs_no_history(self, remap_db) -> None:
        out = _remap(remap_db, lambda c: _job(c, "j1", "FAILED_TECHNICAL_DO"))
        assert _state(remap_db, "job", "astral_job_id", "j1") == "ERROR_GRADE_DO"
        assert out["remapped"]["job"]["FAILED_TECHNICAL_DO"] == {"ERROR_GRADE_DO": 1}

    @pytest.mark.parametrize(
        ("pred", "want"),
        [
            ("PASSED_JOBLIST", "ERROR_FETCH_JD_UNREADABLE"),
            ("RELATIVE_JOB_LINK", "ERROR_FETCH_RELATIVE_JD_UNREADABLE"),
            # a _RETRY holding predecessor resolves through its base
            ("RELATIVE_JOB_LINK_RETRY", "ERROR_FETCH_RELATIVE_JD_UNREADABLE"),
        ],
    )
    def test_trigger_predecessor(self, remap_db, pred: str, want: str) -> None:
        _remap(remap_db, lambda c: _job(c, "j1", "JD_SCRAPE_FAIL", _hist(pred, "JD_SCRAPE_FAIL")))
        assert _state(remap_db, "job", "astral_job_id", "j1") == want

    def test_company_from_state_predecessor(self, remap_db) -> None:
        h = _hist("WEBSITE_FOUND", "HOMEPAGE_READY", "CANNOT_READ_WEBSITE",
                  from_states=[None, "WEBSITE_FOUND", "HOMEPAGE_READY"])
        _remap(remap_db, lambda c: _company(c, "co1", "CANNOT_READ_WEBSITE", h))
        assert _state(remap_db, "company", "short_name", "co1") == "ERROR_PREFILTER_COMPANY_UNREADABLE"

    def test_bare_family_widens_to_history_task(self, remap_db) -> None:
        # grade_do is not a FAILED_TECHNICAL map key; its bare error is registered on job.
        _remap(remap_db, lambda c: _job(c, "j1", "FAILED_TECHNICAL", _hist("PASSED_JD", "FAILED_TECHNICAL")))
        assert _state(remap_db, "job", "astral_job_id", "j1") == "ERROR_GRADE_DO"

    def test_non_bare_family_does_not_widen(self, remap_db) -> None:
        # JD_SCRAPE_FAIL values are _UNREADABLE (not bare), so a PASSED_JD (grade_do) predecessor stays unresolved.
        out = _remap(remap_db, lambda c: _job(c, "j1", "JD_SCRAPE_FAIL", _hist("PASSED_JD", "JD_SCRAPE_FAIL")))
        assert _state(remap_db, "job", "astral_job_id", "j1") == "JD_SCRAPE_FAIL"
        assert out["skipped"]["job"] == {"JD_SCRAPE_FAIL": 1}

    def test_hop_label_resolves_to_live_run_next(self, remap_db) -> None:
        def seed(c):
            _run_next(c, "anticipate_scan", "contemplate_job")
            _run_next(c, "anticipate_scan", "draft_cover_letter", current=0)  # non-current row ignored
            _job(c, "j1", "ERROR_BUILD_ARTIFACTS",
                 _hist("BUILD_ARTIFACTS", "BUILD_ARTIFACTS.anticipate_scan", "ERROR_BUILD_ARTIFACTS"))

        _remap(remap_db, seed)
        assert _state(remap_db, "job", "astral_job_id", "j1") == "ERROR_CONTEMPLATE_JOB"

    def test_hop_label_without_target_is_skipped(self, remap_db) -> None:
        # the completed hop has no run_next row → unresolved
        out = _remap(remap_db, lambda c: _job(
            c, "j1", "ERROR_BUILD_ARTIFACTS", _hist("BUILD_ARTIFACTS.anticipate_scan", "ERROR_BUILD_ARTIFACTS")))
        assert _state(remap_db, "job", "astral_job_id", "j1") == "ERROR_BUILD_ARTIFACTS"
        assert out["skipped"]["job"] == {"ERROR_BUILD_ARTIFACTS": 1}

    @pytest.mark.parametrize("cid", ["c1", None], ids=["own_candidate_row", "null_candidate_row"])
    def test_shared_trigger_tie_break_by_dispatch(self, remap_db, cid: Optional[str]) -> None:
        def seed(c):
            _dispatch(c, "anticipate_scan", "BUILD_ARTIFACTS", cid)
            _dispatch(c, "contemplate_job", "BUILD_ARTIFACTS", "other-cand")  # another candidate's row is ignored
            _job(c, "j1", "ERROR_BUILD_ARTIFACTS", _hist("BUILD_ARTIFACTS", "ERROR_BUILD_ARTIFACTS"))

        _remap(remap_db, seed)
        assert _state(remap_db, "job", "astral_job_id", "j1") == "ERROR_ANTICIPATE_SCAN"

    @pytest.mark.parametrize("claimants", [(), ("anticipate_scan", "contemplate_job")], ids=["none", "two"])
    def test_shared_trigger_still_ambiguous_is_skipped(self, remap_db, claimants) -> None:
        def seed(c):
            for k in claimants:
                _dispatch(c, k, "BUILD_ARTIFACTS", "c1")
            _job(c, "j1", "ERROR_BUILD_ARTIFACTS", _hist("BUILD_ARTIFACTS", "ERROR_BUILD_ARTIFACTS"))

        out = _remap(remap_db, seed)
        assert _state(remap_db, "job", "astral_job_id", "j1") == "ERROR_BUILD_ARTIFACTS"
        assert out["skipped"]["job"] == {"ERROR_BUILD_ARTIFACTS": 1}

    @pytest.mark.parametrize(
        ("error", "want"),
        [
            ("scrape_closed signal=x text_len=10 final_url=u", "JD_SCRAPE_FAIL_CLOSED"),
            ("scrape_missing signal=x text_len=0 final_url=u", "JD_SCRAPE_FAIL_MISSING"),
            ("scrape_blocked signal=x", "LINK_EXPIRED"),
            (None, "LINK_EXPIRED"),
        ],
        ids=["closed", "missing", "other_status", "no_error"],
    )
    def test_meteorite_expired_link_from_error_prefix(self, remap_db, error: Optional[str], want: str) -> None:
        _remap(remap_db, lambda c: _meteorite(c, "m1", "LINK_EXPIRED", error))
        assert _state(remap_db, "meteorite", "source_id", "m1") == want

    @pytest.mark.parametrize(
        "history",
        [None, _hist("JD_SCRAPE_FAIL"), _hist("NEW", "JD_SCRAPE_FAIL")],
        ids=["no_history", "no_predecessor", "pred_matches_no_trigger"],
    )
    def test_unresolvable_rows_are_skipped(self, remap_db, history: Optional[str]) -> None:
        out = _remap(remap_db, lambda c: _job(c, "j1", "JD_SCRAPE_FAIL", history))
        assert _state(remap_db, "job", "astral_job_id", "j1") == "JD_SCRAPE_FAIL"
        assert out["skipped"]["job"] == {"JD_SCRAPE_FAIL": 1}
        assert out["remapped"]["job"] == {}


class TestAst2087RemapContract:
    """AC 9: dry run writes nothing; execute writes only `state`; skipped == retired left; dead states untouched."""

    _SURFACE = "SELECT rowid, state_history, state_changed_at, updated_at FROM {}"

    @staticmethod
    def _seed(c) -> None:
        _job(c, "j-single", "FAILED_TECHNICAL_DO", _hist("PASSED_JD", "FAILED_TECHNICAL_DO"))
        _job(c, "j-skip", "JD_SCRAPE_FAIL")
        _job(c, "j-new", "NEW")
        _job(c, "j-hop", "BUILD_ARTIFACTS.anticipate_scan")
        for i, dead in enumerate(("PREFILTER_UNKNOWN", "HARD_PARSE", "BUILD_FAILED")):
            _job(c, f"j-dead{i}", dead, _hist("NEW", dead))
        _job(c, "j-dead3", "BUILD_FAILED")
        _company(c, "co1", "NO_WEBSITE", _hist("DISCOVERED", "NO_WEBSITE", from_states=[None, "DISCOVERED"]))
        _candidate(c, "cand1", "REQUESTED_RESUME_ERROR")
        _meteorite(c, "m1", "NEW_EMAIL_ERROR", None, _hist("NEW_EMAIL_ERROR"))
        _dispatch(c, "meteorite_bot_blocked_notify", "BOT_BLOCKED")

    def test_dry_run_counts_but_writes_nothing(self, remap_db) -> None:
        _seeded(remap_db, self._seed)
        before = _dump(remap_db)
        out = _remap(remap_db, dry_run=True)
        assert _dump(remap_db) == before
        assert out["dry_run"] is True
        assert out["remapped"]["job"] == {"FAILED_TECHNICAL_DO": {"ERROR_GRADE_DO": 1}}
        assert out["dispatch_task"]["remapped"] == {"BOT_BLOCKED": {"BOT_BLOCKED_SCRAPE_METEORITE": 1}}

    def test_execute_write_surface_and_counts(self, remap_db) -> None:
        _seeded(remap_db, self._seed)
        tables = ("job", "company", "candidate", "meteorite")
        before = {t: _query(remap_db, self._SURFACE.format(t)) for t in tables}
        out = _remap(remap_db)

        assert out["dry_run"] is False
        assert out["remapped"] == {
            "job": {"FAILED_TECHNICAL_DO": {"ERROR_GRADE_DO": 1}},
            "company": {"NO_WEBSITE": {"ERROR_INFLOW_RESOLVE_WEBSITE_NOT_FOUND": 1}},
            "candidate": {},
            "meteorite": {"NEW_EMAIL_ERROR": {"ERROR_STAGE_METEORITE": 1}},
        }
        assert out["skipped"] == {
            "job": {"JD_SCRAPE_FAIL": 1},
            "company": {},
            "candidate": {"REQUESTED_RESUME_ERROR": 1},
            "meteorite": {},
        }
        # dead states counted under the name read from data; registered and hop-label states are not
        assert out["unregistered"]["job"] == {"PREFILTER_UNKNOWN": 1, "HARD_PARSE": 1, "BUILD_FAILED": 2}
        assert out["dispatch_task"] == {"remapped": {"BOT_BLOCKED": {"BOT_BLOCKED_SCRAPE_METEORITE": 1}}, "skipped": {}}

        # state_history / state_changed_at / updated_at byte-identical
        for t in tables:
            assert _query(remap_db, self._SURFACE.format(t)) == before[t], t
        # retired rows left == skipped, per table (AC 9)
        for t, olds in remap_db.RETIRED_TERMINAL_STATE_MAP.items():
            marks = ",".join("?" * len(olds))
            left = _query(remap_db, f"SELECT COUNT(*) FROM {t} WHERE state IN ({marks})", tuple(olds))[0][0]
            assert left == sum(out["skipped"][t].values()), t
        assert _query(remap_db, "SELECT astral_job_id, state FROM job WHERE astral_job_id LIKE 'j-dead%' ORDER BY 1") == [
            ("j-dead0", "PREFILTER_UNKNOWN"), ("j-dead1", "HARD_PARSE"),
            ("j-dead2", "BUILD_FAILED"), ("j-dead3", "BUILD_FAILED"),
        ]
        # AC 8 live half
        assert _query(remap_db, "SELECT trigger_state FROM dispatch_task WHERE task_key = 'meteorite_bot_blocked_notify'") == [
            ("BOT_BLOCKED_SCRAPE_METEORITE",)
        ]

    def test_second_execute_is_a_no_op(self, remap_db) -> None:
        _remap(remap_db, self._seed)
        before = _dump(remap_db)
        out = _remap(remap_db)
        assert _dump(remap_db) == before
        assert out["dispatch_task"]["remapped"] == {}
        assert out["remapped"]["job"] == {}


class TestAst2087DispatchTaskRemap:
    """dispatch_task.trigger_state: the catalog trigger wins only when it is one of the retired name's targets."""

    @pytest.mark.parametrize(
        ("task_key", "old"),
        [
            ("grade_do", "JD_SCRAPE_FAIL"),  # catalog trigger PASSED_JD is not a JD_SCRAPE_FAIL target
            ("craft_do_rubric", "REQUESTED_RESUME_ERROR"),  # chain hop: no catalog default
        ],
        ids=["trigger_not_a_target", "no_catalog_default"],
    )
    def test_skipped_and_untouched(self, remap_db, task_key: str, old: str) -> None:
        out = _remap(remap_db, lambda c: _dispatch(c, task_key, old, "c1"))
        assert out["dispatch_task"] == {"remapped": {}, "skipped": {old: 1}}
        assert _query(remap_db, "SELECT trigger_state FROM dispatch_task WHERE task_key = ?", (task_key,)) == [(old,)]

    def test_registered_trigger_rows_not_scanned(self, remap_db) -> None:
        out = _remap(remap_db, lambda c: _dispatch(c, "grade_do", "PASSED_JD"))
        assert out["dispatch_task"] == {"remapped": {}, "skipped": {}}


class TestAst2087PublicWrapperAndCli:
    """`migrate_terminal_state_names` opens its own connection; the CLI is a dry run unless --execute."""

    def test_wrapper_dry_run_default(self, remap_db) -> None:
        _seeded(remap_db, lambda c: _job(c, "j1", "FAILED_TECHNICAL_DO"))
        assert remap_db.migrate_terminal_state_names()["dry_run"] is True
        assert _state(remap_db, "job", "astral_job_id", "j1") == "FAILED_TECHNICAL_DO"
        assert remap_db.migrate_terminal_state_names(dry_run=False)["dry_run"] is False
        assert _state(remap_db, "job", "astral_job_id", "j1") == "ERROR_GRADE_DO"

    @pytest.mark.parametrize(("argv", "dry"), [([], True), (["--execute"], False)], ids=["default", "execute"])
    def test_cli(self, remap_db, monkeypatch, capsys, argv: List[str], dry: bool) -> None:
        spec = importlib.util.spec_from_file_location("migrate_terminal_state_names", _SCRIPT)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _seeded(remap_db, lambda c: _job(c, "j1", "FAILED_TECHNICAL_DO"))
        monkeypatch.setattr(sys, "argv", ["migrate_terminal_state_names.py", *argv])
        assert mod.main() == 0
        printed = json.loads(capsys.readouterr().out)
        assert printed["dry_run"] is dry
        assert printed["remapped"]["job"] == {"FAILED_TECHNICAL_DO": {"ERROR_GRADE_DO": 1}}
        assert _state(remap_db, "job", "astral_job_id", "j1") == ("FAILED_TECHNICAL_DO" if dry else "ERROR_GRADE_DO")
