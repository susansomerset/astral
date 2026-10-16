"""Component tests for candidate table cluster (AST-392 / AST-971)."""

from __future__ import annotations

import json

import pytest

# Branches: insert requires state; invalid state; update merge vs overwrite.
class TestSaveCandidate:
    def test_insert_requires_state(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="state required"):
            sqlite_in_memory.save_candidate("cand-1")

    def test_rejects_invalid_state(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Invalid candidate state"):
            sqlite_in_memory.save_candidate("cand-1", state="NOT_A_STATE")

    def test_update_accepts_requested_artifacts_hop_label(self, sqlite_in_memory) -> None:
        from src.utils.config import CANDIDATE_STAGE_DISPATCH, dispatch_hop_label

        db = sqlite_in_memory
        db.save_candidate("cand-1", state="REQUESTED_ARTIFACTS")
        hop = dispatch_hop_label(
            CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"],
            "craft_get_rubric",
        )
        db.save_candidate("cand-1", state=hop)
        row = db.get_candidate("cand-1")
        assert row is not None
        assert row["state"] == hop

    def test_rejects_unknown_hop_label(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="REQUESTED_ARTIFACTS")
        with pytest.raises(ValueError, match="Invalid candidate state"):
            sqlite_in_memory.save_candidate(
                "cand-1", state="REQUESTED_ARTIFACTS.not_a_task",
            )

    def test_insert_and_merge_update(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_data={"bio": "a"})
        db.save_candidate("cand-1", state="INTAKE_INITIATED", candidate_data={"summary": "b"}, merge=True)
        row = db.get_candidate("cand-1")
        assert row is not None
        assert row["state"] == "INTAKE_INITIATED"
        assert row["candidate_data"]["bio"] == "a"
        assert row["candidate_data"]["summary"] == "b"

    def test_overwrite_candidate_data(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_data={"bio": "a"})
        db.save_candidate("cand-1", candidate_data={"summary": "only"}, merge=False)
        row = db.get_candidate("cand-1")
        assert row is not None
        assert row["candidate_data"] == {"summary": "only"}

    def test_save_candidate_no_longer_takes_legacy_api_key(self, sqlite_in_memory) -> None:
        # AST-1878 / AST-1901: per-server keys live in candidate.api_keys; no save path writes the legacy column.
        with pytest.raises(TypeError):
            sqlite_in_memory.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_api_key="secret-key")


class TestAst1417SaveCandidateHopLabelPersist:
    """AST-1417 bug-repro: save_candidate persists REQUESTED_ARTIFACTS.<hop> (AST-1416)."""

    def test_update_persists_requested_artifacts_hop_label(self, sqlite_in_memory) -> None:
        from src.utils.config import CANDIDATE_STAGE_DISPATCH, dispatch_hop_label

        trigger = CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]
        hop = dispatch_hop_label(trigger, "craft_get_rubric")
        db = sqlite_in_memory
        db.save_candidate("cand-1417", state=trigger, candidate_data={})
        db.save_candidate("cand-1417", state=hop)
        row = db.get_candidate("cand-1417")
        assert row is not None
        assert row["state"] == hop


# Branches: blank id; missing row; list all.
class TestGetCandidate:
    def test_returns_none_for_blank_id(self, sqlite_in_memory) -> None:
        assert sqlite_in_memory.get_candidate("") is None

    def test_returns_none_when_missing(self, sqlite_in_memory) -> None:
        assert sqlite_in_memory.get_candidate("missing") is None


class TestListCandidates:
    def test_returns_saved_rows(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="NEW_CANDIDATE")
        sqlite_in_memory.save_candidate("cand-2", state="INTAKE_INITIATED")
        ids = {row["astral_candidate_id"] for row in sqlite_in_memory.list_candidates()}
        assert ids == {"cand-1", "cand-2"}


# Branches: status write (set, replace, append, NOT SET kept, duplicate, blank id, bad status,
# missing candidate); legacy ciphertext left until that server is edited; malformed column;
# legacy singular column unread; schema; hard-delete.
class TestAst1901CandidateApiKeysArray:
    """AST-1901 column + AST-2251 status records. api_keys is not ciphertext."""

    @pytest.fixture
    def db(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("ASTRAL_RAILWAY_TOKEN", raising=False)
        sqlite_in_memory.save_candidate("cand-1", state="NEW_CANDIDATE")
        return sqlite_in_memory

    @staticmethod
    def _sql(db, sql: str, params: tuple = ()) -> list:
        conn = db._get_connection()
        try:
            rows = conn.execute(sql, params).fetchall()
            conn.commit()
            return rows
        finally:
            conn.close()

    def _raw(self, db, cid: str = "cand-1"):
        cell = self._sql(db, "SELECT api_keys FROM candidate WHERE astral_candidate_id = ?", (cid,))[0][0]
        if not cell:
            return []
        return json.loads(cell)

    def test_status_write_never_encrypts(self, db, monkeypatch: pytest.MonkeyPatch) -> None:
        def _boom(plaintext: str) -> str:
            raise AssertionError("encrypt_value")
        monkeypatch.setattr(db, "encrypt_value", _boom)
        db.update_candidate_api_keys("cand-1", [
            {"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
            {"server": "openrouter", "status": "NOT SET", "expires_at": None},
        ])
        raw = self._raw(db)
        assert raw == [
            {"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
            {"server": "openrouter", "status": "NOT SET", "expires_at": None},
        ]
        assert all("key" not in e for e in raw)
        row = db.get_candidate("cand-1")
        assert row["candidate_secret_status"]["kimi"]["status"] == "SET"
        assert "candidate_api_key" not in row
        assert "api_keys" not in row

    def test_list_rows_carry_status(self, db) -> None:
        db.update_candidate_api_keys("cand-1", [
            {"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
        ])
        (row,) = db.list_candidates()
        assert row["candidate_secret_status"]["kimi"]["expires_at"] == "2999-01-01 00:00:00"
        assert {"candidate_api_key", "api_keys"}.isdisjoint(row)

    def test_candidate_without_keys_has_empty_map(self, db) -> None:
        assert self._raw(db) == []
        assert db.get_candidate("cand-1")["candidate_api_keys"] == {}
        assert db.get_candidate("cand-1")["candidate_secret_status"] == {}

    def test_legacy_column_value_is_never_exposed(self, db) -> None:
        # Column is unread. A value there must not become candidate_api_keys.
        self._sql(
            db,
            "UPDATE candidate SET candidate_api_key = ? WHERE astral_candidate_id = ?",
            ("legacy-blob", "cand-1"),
        )
        row = db.get_candidate("cand-1")
        assert "candidate_api_key" not in row
        assert row["candidate_api_keys"] == {}

    def test_edit_replaces_in_place_and_appends(self, db) -> None:
        db.update_candidate_api_keys("cand-1", [
            {"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
            {"server": "openrouter", "status": "SET", "expires_at": "2999-01-02 00:00:00"},
        ])
        db.update_candidate_api_keys("cand-1", [
            {"server": "kimi", "status": "SET", "expires_at": "2999-06-01 00:00:00"},
            {"server": "deepseek", "status": "NOT SET", "expires_at": None},
        ])
        assert [e["server"] for e in self._raw(db)] == ["kimi", "openrouter", "deepseek"]
        assert self._raw(db)[0]["expires_at"] == "2999-06-01 00:00:00"
        assert self._raw(db)[1]["status"] == "SET"

    def test_clear_keeps_not_set_row(self, db) -> None:
        db.update_candidate_api_keys("cand-1", [
            {"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
            {"server": "openrouter", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
        ])
        db.update_candidate_api_keys("cand-1", [
            {"server": "kimi", "status": "NOT SET", "expires_at": None},
        ])
        raw = self._raw(db)
        assert [e["server"] for e in raw] == ["kimi", "openrouter"]
        assert raw[0] == {"server": "kimi", "status": "NOT SET", "expires_at": None}
        assert raw[1]["status"] == "SET"

    def test_untouched_legacy_ciphertext_survives_another_servers_edit(self, db) -> None:
        self._sql(
            db,
            "UPDATE candidate SET api_keys = ? WHERE astral_candidate_id = ?",
            (json.dumps([{"server": "kimi", "key": "cipher-kimi"}]), "cand-1"),
        )
        db.update_candidate_api_keys("cand-1", [
            {"server": "openrouter", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
        ])
        raw = self._raw(db)
        assert raw[0] == {"server": "kimi", "key": "cipher-kimi"}
        assert raw[1]["server"] == "openrouter"
        assert "key" not in raw[1]

    def test_duplicate_server_rejected_and_nothing_written(self, db) -> None:
        with pytest.raises(ValueError, match="Duplicate api_keys entry for server 'kimi'"):
            db.update_candidate_api_keys("cand-1", [
                {"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"},
                {"server": "kimi", "status": "NOT SET", "expires_at": None},
            ])
        assert self._raw(db) == []

    @pytest.mark.parametrize(
        ("cid", "entries", "exc", "match"),
        [
            ("  ", [{"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"}], ValueError, "candidate_id is required"),
            ("cand-1", [{"server": "kimi", "key": "sk"}], ValueError, "Invalid api_keys status"),
            ("ghost", [{"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"}], LookupError, "Candidate not found: ghost"),
        ],
    )
    def test_update_rejects_bad_input(self, db, cid: str, entries: list, exc: type, match: str) -> None:
        with pytest.raises(exc, match=match):
            db.update_candidate_api_keys(cid, entries)
        assert self._raw(db) == []

    def test_malformed_column_reads_as_empty(self, db) -> None:
        set_col = "UPDATE candidate SET api_keys = ? WHERE astral_candidate_id = ?"
        self._sql(db, set_col, ("not json", "cand-1"))
        assert db.get_candidate("cand-1")["candidate_api_keys"] == {}
        assert db.get_candidate("cand-1")["candidate_secret_status"] == {}
        self._sql(db, set_col, (json.dumps([{"server": "kimi"}, "x", {"key": "only"}, {"nope": 1}]), "cand-1"))
        row = db.get_candidate("cand-1")
        assert row["candidate_secret_status"] == {}
        assert row["candidate_api_keys"] == {}

    def test_required_metadata_columns_unchanged(self, db) -> None:
        cols = {r[1] for r in self._sql(db, "PRAGMA table_info(candidate)")}
        for name in (
            "state", "state_history", "state_changed_at", "batch_id", "batch_created_at",
            "created_at", "updated_at",
        ):
            assert name in cols

    def test_schema_setup_adds_column_and_drops_candidate_key_table(self, db, monkeypatch: pytest.MonkeyPatch) -> None:
        # Existing pre-AST-1901 database: legacy candidate table without api_keys + a candidate_key table.
        self._sql(db, "DROP TABLE candidate")
        self._sql(db, "CREATE TABLE candidate (astral_candidate_id TEXT PRIMARY KEY, state TEXT, candidate_api_key TEXT)")
        self._sql(db, "CREATE TABLE candidate_key (candidate_id TEXT, server_id TEXT, api_key TEXT)")
        monkeypatch.setattr(db, "_candidate_schema_ensured", False)
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
        finally:
            conn.close()
        assert self._sql(db, "SELECT name FROM sqlite_master WHERE name = 'candidate_key'") == []
        assert "api_keys" in {r[1] for r in self._sql(db, "PRAGMA table_info(candidate)")}

    def test_fresh_schema_has_api_keys_column_and_no_candidate_key_table(self, db) -> None:
        assert "api_keys" in {r[1] for r in self._sql(db, "PRAGMA table_info(candidate)")}
        assert self._sql(db, "SELECT name FROM sqlite_master WHERE name = 'candidate_key'") == []

    def test_retired_candidate_key_helpers_are_gone(self, db) -> None:
        for name in ("_ensure_candidate_key_table", "_candidate_key_map", "set_candidate_server_key",
                     "clear_candidate_server_key", "list_candidate_server_keys"):
            assert not hasattr(db, name), name

    def test_hard_delete_takes_keys_with_the_row(self, db) -> None:
        db.update_candidate_api_keys("cand-1", [{"server": "kimi", "status": "SET", "expires_at": "2999-01-01 00:00:00"}])
        counts = db.hard_delete_candidate("cand-1")
        assert "candidate_key" not in counts
        assert counts["candidate"] == 1
        # A re-created candidate with the same id must not inherit the deleted person's keys.
        db.save_candidate("cand-1", state="NEW_CANDIDATE")
        assert db.get_candidate("cand-1")["candidate_api_keys"] == {}


# Branches: candidate.last_email_check column + stamp helper (AST-1134).
class TestAst1134LastEmailCheck:
    """AST-1134: last_email_check schema + update_candidate_last_email_check."""

    def test_fresh_schema_has_nullable_column(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
            cols = {r[1]: r for r in conn.execute("PRAGMA table_info(candidate)").fetchall()}
            assert "last_email_check" in cols
            assert cols["last_email_check"][3] == 0  # nullable
        finally:
            conn.close()

    def test_stamp_sets_when_and_default_now(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c1134", state="NEW_CANDIDATE")
        assert db.get_candidate("c1134").get("last_email_check") is None
        db.update_candidate_last_email_check("c1134", when="2026-08-02 12:00:00")
        assert db.get_candidate("c1134")["last_email_check"] == "2026-08-02 12:00:00"
        db.update_candidate_last_email_check("c1134")
        stamp = db.get_candidate("c1134")["last_email_check"]
        assert stamp and stamp != "2026-08-02 12:00:00"

    def test_stamp_raises_blank_and_missing(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match="candidate_id is required"):
            db.update_candidate_last_email_check("")
        with pytest.raises(LookupError, match="Candidate not found"):
            db.update_candidate_last_email_check("missing-cand")


class TestAst971CandidateStateHistoryColumn:
    """AST-971: state_history column — parse, persist, preserve-when-omitted."""

    def test_insert_defaults_empty_history(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c971", state="NEW_CANDIDATE")
        row = db.get_candidate("c971")
        assert row["state_history"] == []

    def test_insert_persists_history_list(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        hist = [{"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "2026-01-01 00:00:00", "batch_id": None}]
        db.save_candidate("c971", state="NEW_CANDIDATE", state_history=hist)
        row = db.get_candidate("c971")
        assert row["state_history"] == hist

    def test_update_preserves_history_when_omitted(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        hist = [{"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None}]
        db.save_candidate("c971", state="NEW_CANDIDATE", state_history=hist)
        db.save_candidate("c971", state="INTAKE_INITIATED")
        row = db.get_candidate("c971")
        assert row["state"] == "INTAKE_INITIATED"
        assert row["state_history"] == hist

    def test_update_overwrites_history_when_provided(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c971",
            state="NEW_CANDIDATE",
            state_history=[{"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None}],
        )
        nxt = [
            {"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None},
            {"from_state": "NEW_CANDIDATE", "to_state": "INTAKE_INITIATED", "timestamp": "t1", "batch_id": None},
        ]
        db.save_candidate("c971", state="INTAKE_INITIATED", state_history=nxt)
        assert db.get_candidate("c971")["state_history"] == nxt

    def test_invalid_json_parses_to_empty_list(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c971", state="NEW_CANDIDATE")
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE candidate SET state_history = ? WHERE astral_candidate_id = ?",
                ("not-json", "c971"),
            )
            conn.commit()
        finally:
            conn.close()
        assert db.get_candidate("c971")["state_history"] == []


class TestAst973LegacyCandidateMigration:
    """AST-973: hard_delete + migrate phases A/B/C."""

    def _force_state(self, db, cid: str, state: str, *, candidate_data: str | None = None, state_changed_at: str | None = None) -> None:
        """Bypass save_candidate validation so legacy rows can be staged for migrate."""
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
            cols = "astral_candidate_id, state, candidate_data, state_changed_at, updated_at, created_at"
            # Upsert: delete then insert minimal row
            conn.execute("DELETE FROM candidate WHERE astral_candidate_id = ?", (cid,))
            cd = candidate_data if candidate_data is not None else "{}"
            sca = state_changed_at or "2020-01-01 00:00:00"
            now = "2026-07-23 00:00:00"
            conn.execute(
                f"INSERT INTO candidate ({cols}) VALUES (?, ?, ?, ?, ?, ?)",
                (cid, state, cd, sca, now, now),
            )
            conn.commit()
        finally:
            conn.close()

    def test_hard_delete_removes_satellites(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c973", state="ACTIVE_SEARCH", candidate_data={})
        db.save_dispatch_task(
            candidate_id="c973",
            task_key="evaluate_jd",
            min_count=1,
            trigger_state="JD_READY",
        )
        db.sync_company_search_terms("c973", ["fintech"])
        counts = db.hard_delete_candidate("c973")
        assert counts["candidate"] == 1
        assert counts["dispatch_task"] >= 1
        assert counts["company_search_terms"] >= 1
        assert db.get_candidate("c973") is None
        assert db.list_dispatch_tasks_for_candidate("c973") == []

    def test_phase_b_remaps_legacy_preserves_state_changed_at(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        stamped = "2019-06-01 12:00:00"
        self._force_state(db, "legacy", "LIVE_PROMPTS", state_changed_at=stamped)
        self._force_state(db, "newish", "NEW", state_changed_at=stamped)
        self._force_state(db, "weird", "TOTALLY_UNKNOWN", state_changed_at=stamped)
        out = db.migrate_legacy_candidate_states(dry_run=False, phases="BC")
        assert out["states_remapped"] >= 3
        assert any(x["astral_candidate_id"] == "weird" for x in out["states_unknown_to_new_candidate"])
        assert db.get_candidate("legacy")["state"] == "ACTIVE_SEARCH"
        assert db.get_candidate("newish")["state"] == "NEW_CANDIDATE"
        assert db.get_candidate("weird")["state"] == "NEW_CANDIDATE"
        # Preserve aging clock
        conn = db._get_connection()
        try:
            row = conn.execute(
                "SELECT state_changed_at FROM candidate WHERE astral_candidate_id = ?",
                ("legacy",),
            ).fetchone()
            assert row[0] == stamped
        finally:
            conn.close()
        # Idempotent
        out2 = db.migrate_legacy_candidate_states(dry_run=False, phases="BC")
        assert out2["states_remapped"] == 0

    def test_phase_a_hard_deletes_pre_cutover_deleted_only(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        import json
        self._force_state(db, "pre", "DELETED", candidate_data="{}")
        self._force_state(
            db,
            "post",
            "DELETED",
            candidate_data=json.dumps({"lifecycle": {"reap_started_at": "2026-01-01T00:00:00Z"}}),
        )
        dry = db.migrate_legacy_candidate_states(dry_run=True, phases="A")
        assert dry["deleted_hard_pre_cutover"] == 1
        # Dry-run must not delete — check raw
        conn = db._get_connection()
        try:
            ids = {r[0] for r in conn.execute("SELECT astral_candidate_id FROM candidate").fetchall()}
        finally:
            conn.close()
        assert "pre" in ids and "post" in ids
        live = db.migrate_legacy_candidate_states(dry_run=False, phases="A")
        assert live["deleted_hard_pre_cutover"] == 1
        conn = db._get_connection()
        try:
            ids = {r[0] for r in conn.execute("SELECT astral_candidate_id FROM candidate").fetchall()}
        finally:
            conn.close()
        assert "pre" not in ids
        assert "post" in ids

    def test_phase_c_remaps_candidate_triggers_not_company_new(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c973c", state="ACTIVE_SEARCH", candidate_data={})
        conn = db._get_connection()
        try:
            db._ensure_dispatch_task_schema(conn)
            # Candidate legacy trigger LIVE_PROMPTS → ACTIVE_SEARCH
            conn.execute(
                "INSERT INTO dispatch_task "
                "(candidate_id, task_key, entity_type, trigger_state, min_count, auto_mode, "
                "batch_size, freq_hrs, sort_by, batch_call_mode, updated_at) "
                "VALUES (?, 'craft_resume_base', 'candidate', 'LIVE_PROMPTS', 1, 0, 1, 0, "
                "'updated_at', 0, datetime('now'))",
                ("c973c",),
            )
            # Company NEW must stay (job/company registry)
            conn.execute(
                "INSERT INTO dispatch_task "
                "(candidate_id, task_key, entity_type, trigger_state, min_count, auto_mode, "
                "batch_size, freq_hrs, sort_by, batch_call_mode, updated_at) "
                "VALUES (?, 'evaluate_jd', 'company', 'NEW', 1, 0, 1, 0, "
                "'updated_at', 0, datetime('now'))",
                ("c973c",),
            )
            # Candidate NEW → NEW_CANDIDATE
            conn.execute(
                "INSERT INTO dispatch_task "
                "(candidate_id, task_key, entity_type, trigger_state, min_count, auto_mode, "
                "batch_size, freq_hrs, sort_by, batch_call_mode, updated_at) "
                "VALUES (?, 'bootstrap_candidate_context', 'candidate', 'NEW', 1, 0, 1, 0, "
                "'updated_at', 0, datetime('now'))",
                ("c973c",),
            )
            conn.commit()
        finally:
            conn.close()
        out = db.migrate_legacy_candidate_states(dry_run=False, phases="BC")
        assert out["dispatch_triggers_remapped"] >= 2
        rows = {
            (r["task_key"], r["trigger_state"], r.get("entity_type"))
            for r in db.list_dispatch_tasks_for_candidate("c973c")
        }
        assert ("craft_resume_base", "ACTIVE_SEARCH", "candidate") in rows
        assert ("evaluate_jd", "NEW", "company") in rows
        assert ("bootstrap_candidate_context", "NEW_CANDIDATE", "candidate") in rows

    def test_ensure_runs_bc_not_phase_a(self, sqlite_in_memory) -> None:
        """Schema ensure must not hard-delete pre-cutover DELETED."""
        db = sqlite_in_memory
        self._force_state(db, "keep_deleted", "DELETED", candidate_data="{}")
        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
        finally:
            conn.close()
        conn = db._get_connection()
        try:
            ids = {r[0] for r in conn.execute("SELECT astral_candidate_id FROM candidate").fetchall()}
        finally:
            conn.close()
        assert "keep_deleted" in ids


class TestAst1258CandidateBatchClaim:
    """AST-1258: candidate batch_id columns + pool claim → get → clear (job/company parity)."""

    def test_schema_has_nullable_batch_columns(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
            cols = {r[1]: r for r in conn.execute("PRAGMA table_info(candidate)").fetchall()}
            assert "batch_id" in cols
            assert "batch_created_at" in cols
            assert cols["batch_id"][3] == 0  # nullable
            assert cols["batch_created_at"][3] == 0
        finally:
            conn.close()

    def test_save_leaves_batch_unclaimed(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c1258u", state="REQUESTED_ARTIFACTS", candidate_data={})
        row = db.get_candidate("c1258u")
        assert row is not None
        assert not row.get("batch_id")

    def test_claim_get_clear_multi_row_pool(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c1258a", state="REQUESTED_ARTIFACTS", candidate_data={})
        db.save_candidate("c1258b", state="REQUESTED_ARTIFACTS", candidate_data={})
        db.save_candidate("c1258c", state="ACTIVE_SEARCH", candidate_data={})  # wrong state
        n = db.claim_candidate_batch("craft_get_rubric-test-uuid", "REQUESTED_ARTIFACTS", 2)
        assert n == 2
        rows = db.get_candidate_batch("craft_get_rubric-test-uuid")
        assert {r["astral_candidate_id"] for r in rows} == {"c1258a", "c1258b"}
        for r in rows:
            assert r["batch_id"] == "craft_get_rubric-test-uuid"
            assert r.get("batch_created_at")
        # Second concurrent claim cannot steal locked rows
        n2 = db.claim_candidate_batch("other-batch-uuid", "REQUESTED_ARTIFACTS", 2)
        assert n2 == 0
        assert db.get_candidate_batch("other-batch-uuid") == []
        # Clear releases all rows in the batch
        cleared = db.clear_candidate_batch("craft_get_rubric-test-uuid")
        assert cleared == 2
        for cid in ("c1258a", "c1258b"):
            row = db.get_candidate(cid)
            assert not row.get("batch_id")
            assert not row.get("batch_created_at")
        # Pool is claimable again after clear
        n3 = db.claim_candidate_batch("reclaim-uuid", "REQUESTED_ARTIFACTS", 2)
        assert n3 == 2

    def test_claim_unions_retry_states(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c1258p", state="REQUESTED_ARTIFACTS", candidate_data={})
        db.save_candidate("c1258r", state="REQUESTED_ARTIFACTS_RETRY", candidate_data={})
        n = db.claim_candidate_batch(
            "batch-1258-union",
            "REQUESTED_ARTIFACTS",
            10,
            states=["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY"],
        )
        assert n == 2
        ids = {r["astral_candidate_id"] for r in db.get_candidate_batch("batch-1258-union")}
        assert ids == {"c1258p", "c1258r"}



class TestAst1502EnsureLeavesLiveCandidateContent:
    """AST-1502 bug-repro (gap for AST-1497): ensure must not run content migrates on boot."""

    def test_ensure_candidate_schema_leaves_artifacts_ready_without_content_migrates(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        db = sqlite_in_memory
        # Live operator row (plan ## Repro): ARTIFACTS_READY must survive schema ensure.
        db.save_candidate(
            "somerset",
            state="ARTIFACTS_READY",
            candidate_data={
                "contact": {"first": "Susan", "last": "Somerset"},
                "context": {"bio_summary": "ops"},
                "artifacts": {"base_resume": {"professional_summary": "ready"}},
            },
        )
        before = db.get_candidate("somerset")
        assert before is not None
        assert before["state"] == "ARTIFACTS_READY"

        content_calls: list[str] = []
        monkeypatch.setattr(
            db,
            "_migrate_candidate_data_structure",
            lambda _c: content_calls.append("data_structure"),
        )
        monkeypatch.setattr(
            db,
            "_migrate_pronoun_preference_backfill",
            lambda _c: content_calls.append("pronoun_backfill"),
        )
        monkeypatch.setattr(
            db,
            "_migrate_context_arrays_to_text",
            lambda _c: content_calls.append("context_arrays"),
        )
        monkeypatch.setattr(
            db,
            "_migrate_candidate_library_ast1014",
            lambda _c: content_calls.append("library_ast1014"),
        )
        monkeypatch.setattr(
            db,
            "_legacy_candidate_migrate_conn",
            lambda *_a, **_k: content_calls.append("legacy_migrate") or {},
        )

        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
        finally:
            conn.close()

        after = db.get_candidate("somerset")
        assert after is not None
        assert after["state"] == "ARTIFACTS_READY"
        # Kill-switch: content migrates must not ride inside schema ensure (AST-1497).
        assert content_calls == []
