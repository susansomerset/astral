"""search_entity_rows — candidate-scoped literal LIKE over SEARCH_ENTITY_CONFIG fields (AST-2173)."""

from __future__ import annotations

import copy

import pytest

from src.utils.config import METEORITE_CONFIG, SEARCH_ENTITY_CONFIG


def _company(db, short: str, cid: str, **kw) -> None:
    db.save_company(short, state="IMPORTED", candidate_id=cid, **kw)


def _job(db, jid: str, cid: str, company: str, **kw) -> None:
    # company_job_id defaults per job so the job identity triple never collides between rows.
    kw.setdefault("company_job_id", f"cj-{jid}")
    db.save_job(jid, company_id=company, candidate_id=cid, state=kw.pop("state", "NEW"), **kw)


def _meteorite(db, cid: str, **kw) -> int:
    return db.insert_meteorite_rows([{"candidate_id": cid, "source_kind": "email", "source_id": "mid", **kw}])[0]


def _sql(db, stmt: str, params: tuple = ()) -> None:
    # Direct column writes for fields the public save helpers do not expose (meteorite.astral_job_id, NULL stamps).
    conn = db._get_connection()
    try:
        conn.execute(stmt, params)
        conn.commit()
    finally:
        conn.close()


def _ids(rows, key: str) -> list:
    return [r[key] for r in rows]


# Branches: every SEARCH_ENTITY_CONFIG key is a real table and every field a real column (+ candidate_id,
# state_changed_at the read filters / sorts on) — a typo would only surface as a 500 at request time.
class TestAst2173RegistryMatchesSchema:
    @pytest.mark.parametrize("entity_type", list(SEARCH_ENTITY_CONFIG))
    def test_fields_are_columns(self, sqlite_in_memory, entity_type) -> None:
        db = sqlite_in_memory
        db.search_entity_rows(entity_type, "cand-a", "x")  # runs the table's ensure on a fresh DB
        conn = db._get_connection()
        try:
            cols = {r[1] for r in conn.execute(f"PRAGMA table_info({entity_type})").fetchall()}
        finally:
            conn.close()
        entry = SEARCH_ENTITY_CONFIG[entity_type]
        wanted = {*entry["base_fields"], *entry["payload_fields"], *entry["name_fields"], "candidate_id", "state_changed_at"}
        assert wanted <= cols, wanted - cols


# Branches: candidate_id = ? on all three tables (AC1).
class TestAst2173CandidateScope:
    def test_other_candidates_rows_never_returned(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        for cid in ("cand-a", "cand-b"):
            _company(db, f"zebra-co-{cid}", cid, company_name=f"Zebra Inc {cid}")
            _job(db, f"job-{cid}", cid, f"zebra-co-{cid}", job_title="Zebra Wrangler")
            _meteorite(db, cid, job_title="Zebra Keeper")
        jobs = db.search_entity_rows("job", "cand-a", "zebra")
        companies = db.search_entity_rows("company", "cand-a", "zebra")
        mets = db.search_entity_rows("meteorite", "cand-a", "zebra")
        assert _ids(jobs, "astral_job_id") == ["job-cand-a"]
        assert _ids(companies, "short_name") == ["zebra-co-cand-a"]
        assert len(mets) == 1
        assert all(r["candidate_id"] == "cand-a" for r in [*jobs, *companies, *mets])


# Branches: id columns are base fields; INTEGER meteorite.id coerces to text under LIKE (AC3 data half).
class TestAst2173IdsFindable:
    def test_job_full_id_company_job_id_and_middle_substring(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _company(db, "acme", "cand-a")
        jid = "a1b2c3d4e5f6g7h8"
        _job(db, jid, "cand-a", "acme", company_job_id="REQ-77812", job_title="Plain")
        for needle, field in ((jid, "astral_job_id"), ("REQ-77812", "company_job_id"), (jid[5:11], "astral_job_id")):
            rows = db.search_entity_rows("job", "cand-a", needle)
            assert _ids(rows, "astral_job_id") == [jid], needle
            assert field in rows[0]["matched_fields"], needle

    def test_meteorite_numeric_id(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        mid = _meteorite(db, "cand-a", job_title="Plain")
        rows = db.search_entity_rows("meteorite", "cand-a", str(mid))
        assert mid in _ids(rows, "id")
        assert "id" in next(r for r in rows if r["id"] == mid)["matched_fields"]

    def test_meteorite_astral_job_id(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        mid = _meteorite(db, "cand-a", job_title="Plain")
        _sql(db, "UPDATE meteorite SET astral_job_id = ? WHERE id = ?", ("met-job-xyz", mid))
        rows = db.search_entity_rows("meteorite", "cand-a", "met-job-xyz")
        assert _ids(rows, "id") == [mid]
        assert rows[0]["matched_fields"] == ["astral_job_id"]


# Branches: matched_fields names every hit field in config order; __hit_ flag columns never leak.
class TestAst2173MatchedFields:
    def test_base_and_payload_fields_reported_in_config_order(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _company(db, "acme", "cand-a")
        _job(db, "j1", "cand-a", "acme", job_title="Quokka Lead", job_data={"note": "quokka"})
        _job(db, "j2", "cand-a", "acme", job_title="Other", job_data={"note": "quokka"})
        rows = {r["astral_job_id"]: r for r in db.search_entity_rows("job", "cand-a", "quokka")}
        assert rows["j1"]["matched_fields"] == ["job_title", "job_data"]
        assert rows["j2"]["matched_fields"] == ["job_data"]
        assert not any(k.startswith("__hit_") for r in rows.values() for k in r)

    def test_company_and_meteorite_payload_fields(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _company(db, "acme", "cand-a", company_data={"blurb": "wombat"})
        mid = _meteorite(db, "cand-a", content="wombat jd", classify_outcome="wombat?", error="wombat err")
        assert db.search_entity_rows("company", "cand-a", "wombat")[0]["matched_fields"] == ["company_data"]
        met = db.search_entity_rows("meteorite", "cand-a", "wombat")
        assert _ids(met, "id") == [mid]
        assert met[0]["matched_fields"] == ["content", "classify_outcome", "error"]

    def test_meteorite_electronic_contact_column_from_config(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        col = METEORITE_CONFIG["electronic_contact_column"]
        mid = _meteorite(db, "cand-a", **{col: "recruiter@numbat.example"})
        rows = db.search_entity_rows("meteorite", "cand-a", "numbat")
        assert _ids(rows, "id") == [mid]
        assert rows[0]["matched_fields"] == [col]


# Branches: SQLite LIKE case-folds; escape order \ then % then _ keeps all three literal (AC5).
class TestAst2173CaseAndLiteralWildcards:
    def test_case_insensitive(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _company(db, "acme", "cand-a")
        _job(db, "j1", "cand-a", "acme", job_title="Quokka Lead")
        upper = _ids(db.search_entity_rows("job", "cand-a", "QUOKKA"), "astral_job_id")
        lower = _ids(db.search_entity_rows("job", "cand-a", "quokka"), "astral_job_id")
        assert upper == lower == ["j1"]

    def test_percent_underscore_backslash_match_literally(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        # "acme" / ids / states / cj- prefixes carry no % _ \ so only the titles can hit.
        _company(db, "acme", "cand-a")
        _job(db, "jpct", "cand-a", "acme", company_job_id="P1", job_title="Growth 50% role")
        _job(db, "jusc", "cand-a", "acme", company_job_id="U1", job_title="snake_case dev")
        _job(db, "jbsl", "cand-a", "acme", company_job_id="B1", job_title=r"C:\path tools")
        _job(db, "jplain", "cand-a", "acme", company_job_id="N1", job_title="Plain Title")
        assert _ids(db.search_entity_rows("job", "cand-a", "%"), "astral_job_id") == ["jpct"]
        assert _ids(db.search_entity_rows("job", "cand-a", "_"), "astral_job_id") == ["jusc"]
        assert _ids(db.search_entity_rows("job", "cand-a", "\\"), "astral_job_id") == ["jbsl"]


# Branches: no LIMIT on the read (AC6).
class TestAst2173NoCap:
    def test_all_600_matches_returned(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _company(db, "acme", "cand-a")
        for i in range(600):
            _job(db, f"eng-{i:04d}", "cand-a", "acme", job_title=f"Engineer {i}")
        assert len(db.search_entity_rows("job", "cand-a", "engineer")) == 600


# Branches: searched columns come only from SEARCH_ENTITY_CONFIG (AC7).
class TestAst2173FieldsFromConfig:
    def test_dropping_job_link_from_config_stops_link_only_match(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        _company(db, "acme", "cand-a")
        _job(db, "jlink", "cand-a", "acme", job_title="Plain", job_link="https://jobs.example/platypus-42")
        assert _ids(db.search_entity_rows("job", "cand-a", "platypus"), "astral_job_id") == ["jlink"]
        trimmed = copy.deepcopy(SEARCH_ENTITY_CONFIG)
        trimmed["job"]["base_fields"].remove("job_link")
        monkeypatch.setattr(db, "SEARCH_ENTITY_CONFIG", trimmed)
        assert db.search_entity_rows("job", "cand-a", "platypus") == []


# Branches: ORDER BY state_changed_at DESC NULLS LAST.
class TestAst2173Order:
    def test_newest_state_change_first_nulls_last(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _company(db, "acme", "cand-a")
        _job(db, "old", "cand-a", "acme", job_title="Kiwi", state_changed_at="2026-01-01T00:00:00Z")
        _job(db, "new", "cand-a", "acme", job_title="Kiwi", state_changed_at="2026-06-01T00:00:00Z")
        _job(db, "nul", "cand-a", "acme", job_title="Kiwi")
        _sql(db, "UPDATE job SET state_changed_at = NULL WHERE astral_job_id = 'nul'")
        assert _ids(db.search_entity_rows("job", "cand-a", "kiwi"), "astral_job_id") == ["new", "old", "nul"]


# Branches: blank candidate_id / needle → ValueError; unknown type → KeyError; fresh DB → [].
class TestAst2173Guards:
    @pytest.mark.parametrize("cid", ["", "   ", None])
    def test_blank_candidate_raises(self, sqlite_in_memory, cid) -> None:
        with pytest.raises(ValueError, match="candidate_id required"):
            sqlite_in_memory.search_entity_rows("job", cid, "x")

    @pytest.mark.parametrize("needle", ["", "  ", None])
    def test_blank_needle_raises(self, sqlite_in_memory, needle) -> None:
        with pytest.raises(ValueError, match="needle required"):
            sqlite_in_memory.search_entity_rows("job", "cand-a", needle)

    def test_unknown_entity_type_raises(self, sqlite_in_memory) -> None:
        with pytest.raises(KeyError):
            sqlite_in_memory.search_entity_rows("candidate", "cand-a", "x")

    @pytest.mark.parametrize("entity_type", list(SEARCH_ENTITY_CONFIG))
    def test_no_match_is_empty_list_on_fresh_db(self, sqlite_in_memory, entity_type) -> None:
        assert sqlite_in_memory.search_entity_rows(entity_type, "cand-a", "nothing-here") == []

    def test_inventory_lists_search_read(self, sqlite_in_memory) -> None:
        doc = sqlite_in_memory.__doc__ or ""
        assert "search_entity_rows" in doc and "AST-2173" in doc
