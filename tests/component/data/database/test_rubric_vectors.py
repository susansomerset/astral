"""rubric_vector + vector_feedback table cluster (AST-722)."""

from __future__ import annotations

import re

import pytest

from src.utils import rubric_text


class TestRubricVectorSchema:
    def test_insert_list_count_round_trip(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("prefilter_company", agent_id="a1", user_prompt="p")
        task_uuid = db.get_current_agent_task_uuid("prefilter_company")
        assert task_uuid

        fp = rubric_text.rubric_vector_content_fingerprint("RC", "content here")
        uuid = db.insert_rubric_vector_row(
            candidate_id="cand-1",
            task_key="prefilter_company",
            task_key_uuid=task_uuid,
            code="RC",
            label="Reality Check",
            content="content here",
            importance=5,
            content_fingerprint=fp,
        )
        assert uuid

        rows = db.list_rubric_vectors("cand-1", "prefilter_company")
        assert len(rows) == 1
        assert rows[0]["code"] == "RC"
        assert rows[0]["current"] == 1
        assert rows[0]["content_fingerprint"] == fp
        assert db.count_rubric_vectors_for_candidate_task("cand-1", "prefilter_company") == 1

    def test_list_and_count_empty_inputs(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.list_rubric_vectors("", "prefilter_company") == []
        assert db.count_rubric_vectors_for_candidate_task("cand-1", "") == 0

    def test_vector_feedback_table_ensures_on_connection(self, seeded_db) -> None:
        db = seeded_db
        conn = db._get_connection()
        try:
            db._ensure_vector_feedback_table(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='vector_feedback'"
            ).fetchone()
            assert row[0] == 1
        finally:
            conn.close()


class TestPurgeLegacyRubricArtifacts:
    def test_removes_only_rubric_keys_preserves_other_artifacts(self, seeded_db) -> None:
        db = seeded_db
        artifacts = {
            "company_prefilter": [{"code": "RC", "content": "x", "importance": 5}],
            "base_resume": "keep me",
            "do_rubric": [{"code": "D1", "content": "y", "importance": 3}],
        }
        db.save_candidate("cand-1", state="NEW", candidate_data={"artifacts": artifacts})

        removed = db.purge_legacy_rubric_artifact_keys("cand-1")
        assert "company_prefilter" in removed
        assert "do_rubric" in removed
        assert "base_resume" not in removed

        cand = db.get_candidate("cand-1")
        arts = cand["candidate_data"]["artifacts"]
        assert "base_resume" in arts
        assert "company_prefilter" not in arts
        assert "do_rubric" not in arts

    def test_no_op_when_no_artifacts(self, seeded_db) -> None:
        assert seeded_db.purge_legacy_rubric_artifact_keys("cand-1") == []


class TestFeedbackBlockType:
    def test_save_agent_data_accepts_feedback_block(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        result = db.save_agent_data(
            "id-1",
            "candidate",
            "prefilter_company",
            "batch-722",
            "FEEDBACK",
            "payload",
        )
        assert result["inserted"] is True
        assert result["outcome"] == "new_content"
        rows = db.get_agent_data_by_batch("batch-722", block_type="FEEDBACK")
        assert len(rows) == 1


# Backfill script integration (real SQLite — AST-722 migration path).
import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_BACKFILL_SCRIPT = _REPO_ROOT / "scripts/migrations/backfill_rubric_vectors.py"


def _load_backfill_module():
    spec = importlib.util.spec_from_file_location("backfill_rubric_vectors", _BACKFILL_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_backfill = _load_backfill_module()


class TestBackfillRubricVectorsIntegration:
    def test_dry_run_reports_without_insert(self, seeded_db, capsys) -> None:
        db = seeded_db
        db.save_agent_task("prefilter_company", agent_id="a1", user_prompt="p")
        db.save_candidate(
            "cand-1",
            state="NEW",
            candidate_data={
                "artifacts": {
                    "company_prefilter": [
                        {"code": "RC", "label": "RC", "content": "text", "importance": 5}
                    ]
                }
            },
        )

        counts = _backfill.backfill_candidate_rubric_vectors("cand-1", dry_run=True)

        assert counts["would_insert"] == 1
        assert counts["vectors_inserted"] == 0
        assert db.count_rubric_vectors_for_candidate_task("cand-1", "prefilter_company") == 0
        assert "would insert" in capsys.readouterr().out

    def test_live_backfill_inserts_vectors(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("prefilter_company", agent_id="a1", user_prompt="p")
        db.save_candidate(
            "cand-1",
            state="NEW",
            candidate_data={
                "artifacts": {
                    "company_prefilter": [
                        {"code": "RC", "label": "RC", "content": "text", "importance": 5}
                    ]
                }
            },
        )

        counts = _backfill.backfill_candidate_rubric_vectors("cand-1", dry_run=False)

        assert counts["vectors_inserted"] == 1
        rows = db.list_rubric_vectors("cand-1", "prefilter_company")
        assert len(rows) == 1
        assert rows[0]["code"] == "RC"

    def test_idempotent_skip_when_vectors_exist(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("prefilter_company", agent_id="a1", user_prompt="p")
        task_uuid = db.get_current_agent_task_uuid("prefilter_company")
        db.insert_rubric_vector_row(
            candidate_id="cand-1",
            task_key="prefilter_company",
            task_key_uuid=task_uuid,
            code="RC",
            label="RC",
            content="existing",
            importance=5,
            content_fingerprint="fp",
        )
        db.save_candidate(
            "cand-1",
            state="NEW",
            candidate_data={
                "artifacts": {
                    "company_prefilter": [
                        {"code": "RC", "label": "RC", "content": "text", "importance": 5}
                    ]
                }
            },
        )

        counts = _backfill.backfill_candidate_rubric_vectors("cand-1", dry_run=False)

        assert counts["skipped_existing"] == 1
        assert db.count_rubric_vectors_for_candidate_task("cand-1", "prefilter_company") == 1

    def test_purge_script_dry_run_and_live(self, seeded_db, capsys) -> None:
        db = seeded_db
        db.save_candidate(
            "cand-1",
            state="NEW",
            candidate_data={
                "artifacts": {
                    "do_rubric": [{"code": "D1", "content": "y", "importance": 3}],
                    "base_resume": "keep",
                }
            },
        )

        dry = _backfill.purge_rubric_artifacts(["cand-1"], dry_run=True)
        assert dry["keys_removed"] == 1
        assert "do_rubric" in db.get_candidate("cand-1")["candidate_data"]["artifacts"]

        live = _backfill.purge_rubric_artifacts(["cand-1"], dry_run=False)
        assert live["keys_removed"] == 1
        arts = db.get_candidate("cand-1")["candidate_data"]["artifacts"]
        assert "do_rubric" not in arts
        assert arts["base_resume"] == "keep"


class TestAst723SyncRubricVectors:
    def test_importance_only_update_keeps_uuid(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("qualify_job_listings", agent_id="a1", user_prompt="p")
        criteria = [{"code": "CR", "label": "fit", "content": "Grade A", "importance": 5}]
        db.sync_rubric_vectors_from_criteria("cand-1", "qualify_job_listings", criteria)
        rows1 = db.list_rubric_vectors("cand-1", "qualify_job_listings")
        uuid1 = rows1[0]["rubric_vector_uuid"]
        criteria[0]["importance"] = 8
        db.sync_rubric_vectors_from_criteria("cand-1", "qualify_job_listings", criteria)
        rows2 = db.list_rubric_vectors("cand-1", "qualify_job_listings")
        assert len(rows2) == 1
        assert rows2[0]["rubric_vector_uuid"] == uuid1
        assert rows2[0]["importance"] == 8

    def test_fingerprint_change_retires_and_inserts_new_row(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "Get", "content": "v1", "importance": 5}],
        )
        uuid1 = db.list_rubric_vectors("cand-1", "grade_get")[0]["rubric_vector_uuid"]
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "Get", "content": "v2", "importance": 5}],
        )
        current = db.list_rubric_vectors("cand-1", "grade_get")
        assert len(current) == 1
        assert current[0]["rubric_vector_uuid"] != uuid1
        assert current[0]["content"] == "v2"
        assert db.count_rubric_vectors_for_candidate_task("cand-1", "grade_get", current_only=False) == 2

    def test_removed_code_retires_row(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_do", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_do",
            [
                {"code": "AA", "label": "A", "content": "a", "importance": 5},
                {"code": "BB", "label": "B", "content": "b", "importance": 5},
            ],
        )
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_do",
            [{"code": "AA", "label": "A", "content": "a", "importance": 5}],
        )
        current = db.list_rubric_vectors("cand-1", "grade_do")
        assert [r["code"] for r in current] == ["AA"]
        assert db.count_rubric_vectors_for_candidate_task("cand-1", "grade_do", current_only=False) == 2



# AST-2008 Step 2: two current rows sharing a code (legacy somerset TP/TP). Branch: code already in
# current_by_code -> retire the later row (rowid order) instead of overwriting the earlier one.
class TestAst2008SyncRetiresDuplicateCurrentRows:
    def _seed(self, db, task_uuid: str, label: str, content: str) -> str:
        return db.insert_rubric_vector_row(
            candidate_id="somerset", task_key="grade_do", task_key_uuid=task_uuid, code="TP", label=label,
            content=content, importance=5,
            content_fingerprint=rubric_text.rubric_vector_content_fingerprint(label, content),
        )

    def test_later_duplicate_row_retired_on_next_sync(self, seeded_db) -> None:
        # Repro 3 - today the dict keeps r2, so r1 is never matched and r2 is re-inserted: TP, TP, TX.
        db = seeded_db
        db.save_agent_task("grade_do", agent_id="a1", user_prompt="p")
        task_uuid = db.get_current_agent_task_uuid("grade_do")
        r1 = self._seed(db, task_uuid, "Hands-On Technical Partnership", "partner body")
        r2 = self._seed(db, task_uuid, "Speaking Truth to Power", "truth body")
        db.sync_rubric_vectors_from_criteria(
            "somerset",
            "grade_do",
            [
                {"code": "TP", "label": "Hands-On Technical Partnership", "content": "partner body", "importance": 7},
                {"code": "TX", "label": "Speaking Truth to Power", "content": "truth body", "importance": 5},
            ],
        )
        current = {r["code"]: r for r in db.list_rubric_vectors("somerset", "grade_do", current_only=True)}
        assert sorted(current) == ["TP", "TX"]
        assert current["TP"]["rubric_vector_uuid"] == r1
        assert current["TP"]["importance"] == 7
        all_rows = {r["rubric_vector_uuid"]: r for r in db.list_rubric_vectors("somerset", "grade_do", current_only=False)}
        assert all_rows[r2]["current"] == 0
        assert len(all_rows) == 3

class TestAst723RubricTokenMigration:
    def test_replaces_legacy_rubric_tokens_on_agent_task(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="Rubric: {$GET_RUBRIC}")
        assert "{$GET_RUBRIC}" in db.get_agent_task("grade_get")["user_prompt"]
        db._ast723_rubric_token_migration_applied = False
        conn = db._get_connection()
        try:
            db._apply_ast723_rubric_vectors_token_migration(conn)
        finally:
            conn.close()
        row = db.get_agent_task("grade_get")
        assert "{$RUBRIC_VECTORS}" in row["user_prompt"]
        assert "AST-723_RUBRIC_VECTORS_TOKEN" in row["user_prompt"]


class TestAst724VectorFeedbackRows:
    def test_list_rubric_vector_uuid_by_code(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "GA", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        mapping = db.list_rubric_vector_uuid_by_code("cand-1", "grade_get")
        assert "GA" in mapping
        rows = db.list_rubric_vectors("cand-1", "grade_get")
        assert mapping["GA"] == rows[0]["rubric_vector_uuid"]

    def test_insert_vector_feedback_rows_writes_three_types_per_vector(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "GA", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        uuid = db.list_rubric_vectors("cand-1", "grade_get")[0]["rubric_vector_uuid"]
        db.insert_vector_feedback_rows(
            [{"rubric_vector_uuid": uuid, "code": "GA", "relevance": "A", "clarity": "O", "verdict": "K"}],
            candidate_id="cand-1",
            batch_id="batch-724",
            task_key="grade_get",
            batch_size=1,
        )
        conn = db._get_connection()
        try:
            rows = conn.execute(
                """SELECT feedback_type, value FROM vector_feedback
                   WHERE batch_id = ? ORDER BY feedback_type""",
                ("batch-724",),
            ).fetchall()
            assert [(r[0], r[1]) for r in rows] == [("clarity", "O"), ("relevance", "A"), ("verdict", "K")]
        finally:
            conn.close()

    def test_store_feedback_block_persists_feedback_agent_data(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        fb_id = db.store_feedback_block(
            "candidate",
            "grade_get",
            "batch-fb",
            '{"vector_reviews": ["bad"]}',
            index="0",
        )
        rows = db.get_agent_data_by_batch("batch-fb", block_type="FEEDBACK")
        assert len(rows) == 1
        assert rows[0]["agent_data_id"] == fb_id


class TestAst725ListVectorFeedback:
    def _seed_vector_and_feedback(self, db, *, task_key: str, batch_id: str) -> str:
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "GA", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        uuid = db.list_rubric_vectors("cand-1", "grade_get")[0]["rubric_vector_uuid"]
        db.insert_vector_feedback_rows(
            [{"rubric_vector_uuid": uuid, "code": "GA", "relevance": "A", "clarity": "O", "verdict": "K"}],
            candidate_id="cand-1",
            batch_id=batch_id,
            task_key=task_key,
            batch_size=1,
        )
        return uuid

    def test_owner_task_key_expands_to_consumer_and_craft_run_keys(self, seeded_db) -> None:
        db = seeded_db
        self._seed_vector_and_feedback(db, task_key="grade_get", batch_id="batch-725a")
        self._seed_vector_and_feedback(db, task_key="craft_get_rubric", batch_id="batch-725b")
        rows = db.list_vector_feedback(candidate_id="cand-1", owner_task_key="grade_get")
        batch_ids = {r["batch_id"] for r in rows}
        assert batch_ids == {"batch-725a", "batch-725b"}

    def test_filters_batch_id_and_vector_code(self, seeded_db) -> None:
        db = seeded_db
        self._seed_vector_and_feedback(db, task_key="grade_get", batch_id="batch-725-filter")
        rows = db.list_vector_feedback(
            candidate_id="cand-1",
            batch_id="batch-725-filter",
            vector_code="ga",
        )
        assert len(rows) == 3
        assert all(r["vector_code"] == "GA" for r in rows)


class TestAst725AggregateVectorFeedback:
    def test_per_vector_distributions_and_zero_feedback_vectors(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [
                {"code": "GA", "label": "GA", "content": "a\nA = one", "importance": 8},
                {"code": "GB", "label": "GB", "content": "b\nA = one", "importance": 5},
            ],
        )
        uuid1 = db.list_rubric_vectors("cand-1", "grade_get")[0]["rubric_vector_uuid"]
        db.insert_vector_feedback_rows(
            [{"rubric_vector_uuid": uuid1, "code": "GA", "relevance": "A", "clarity": "O", "verdict": "K"}],
            candidate_id="cand-1",
            batch_id="batch-725-sum",
            task_key="grade_get",
            batch_size=1,
        )
        summary = db.aggregate_vector_feedback_by_vector("cand-1", "grade_get")
        assert len(summary) == 2
        g1 = next(r for r in summary if r["code"] == "GA")
        g2 = next(r for r in summary if r["code"] == "GB")
        assert g1["feedback_row_count"] == 3
        assert g1["batch_count"] == 1
        assert "A:" in g1["relevance_dist"]
        assert g2["feedback_row_count"] == 0
        assert g2["batch_count"] == 0

class TestAst809VectorFeedbackBatchMetadata:
    def test_insert_requires_batch_id(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "GA", "content": "body\nA = one", "importance": 5}],
        )
        uuid = db.list_rubric_vectors("cand-1", "grade_get")[0]["rubric_vector_uuid"]
        db.insert_vector_feedback_rows(
            [{"rubric_vector_uuid": uuid, "code": "GA", "relevance": "A", "clarity": "O", "verdict": "K"}],
            candidate_id="cand-1",
            batch_id="",
            task_key="grade_get",
            batch_size=3,
        )
        assert db.list_vector_feedback(candidate_id="cand-1") == []

    def test_insert_persists_batch_size_and_completed_at(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "GA", "content": "body\nA = one", "importance": 5}],
        )
        uuid = db.list_rubric_vectors("cand-1", "grade_get")[0]["rubric_vector_uuid"]
        completed = "2026-06-25 10:00:00"
        db.insert_vector_feedback_rows(
            [{"rubric_vector_uuid": uuid, "code": "GA", "relevance": "A", "clarity": "O", "verdict": "K"}],
            candidate_id="cand-1",
            batch_id="batch-809",
            task_key="grade_get",
            batch_size=4,
            completed_at=completed,
        )
        rows = db.list_vector_feedback(candidate_id="cand-1", batch_id="batch-809")
        assert len(rows) == 3
        assert all(r["batch_size"] == 4 for r in rows)
        assert all(r["completed_at"] == completed for r in rows)
        assert all(r["created_at"] == completed for r in rows)


class TestAst808ListVectorFeedbackContent:
    def test_list_includes_vector_content_and_importance(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "GA", "label": "GA label", "content": "Criterion text\nA = one", "importance": 7}],
        )
        uuid = db.list_rubric_vectors("cand-1", "grade_get")[0]["rubric_vector_uuid"]
        db.insert_vector_feedback_rows(
            [{"rubric_vector_uuid": uuid, "code": "GA", "relevance": "A", "clarity": "O", "verdict": "K"}],
            candidate_id="cand-1",
            batch_id="batch-808",
            task_key="grade_get",
            batch_size=1,
        )
        rows = db.list_vector_feedback(candidate_id="cand-1", batch_id="batch-808")
        assert len(rows) == 3
        assert rows[0]["vector_content"] == "Criterion text\nA = one"
        assert rows[0]["vector_importance"] == 7
        assert rows[0]["vector_label"] == "GA label"


# AST-2066 Branches: list_rubric_vectors code= filter (case-insensitive, chronological) vs code=None
# (ORDER BY code); set_current_rubric_vector moves one criterion only (AC6) + carries live importance
# (COALESCE hit) / keeps own importance when no other current row (COALESCE miss); cross-code + unknown
# uuid raise with no change; blank args raise.
class TestAst2066RubricCriterionVersions:
    _TASK = "grade_do"

    def _seed(self, db) -> dict:
        # VA: A then B (two blurs = fingerprint retire+insert); VB untouched.
        db.save_agent_task(self._TASK, agent_id="a1", user_prompt="p")
        v02 = {"code": "VB", "label": "Other", "content": "keep", "importance": 3}
        db.sync_rubric_vectors_from_criteria(
            "cand-1", self._TASK, [{"code": "VA", "label": "L", "content": "A", "importance": 5}, v02]
        )
        db.sync_rubric_vectors_from_criteria(
            "cand-1", self._TASK, [{"code": "VA", "label": "L", "content": "B", "importance": 8}, v02]
        )
        hist = db.list_rubric_vectors("cand-1", self._TASK, current_only=False, code="VA")
        cur = {r["code"]: r["rubric_vector_uuid"] for r in db.list_rubric_vectors("cand-1", self._TASK)}
        return {"a": hist[0]["rubric_vector_uuid"], "b": hist[1]["rubric_vector_uuid"], "v02": cur["VB"]}

    def _current(self, db) -> dict:
        return {r["code"]: r for r in db.list_rubric_vectors("cand-1", self._TASK)}

    def test_code_filter_lists_one_criterion_oldest_first(self, seeded_db) -> None:
        db = seeded_db
        ids = self._seed(db)
        hist = db.list_rubric_vectors("cand-1", self._TASK, current_only=False, code=" va ")
        assert [r["rubric_vector_uuid"] for r in hist] == [ids["a"], ids["b"]]
        assert [r["content"] for r in hist] == ["A", "B"]
        # code=None keeps the existing ORDER BY code listing across codes.
        assert [r["code"] for r in db.list_rubric_vectors("cand-1", self._TASK)] == ["VA", "VB"]

    def test_set_current_moves_one_criterion_and_carries_importance(self, seeded_db) -> None:
        # AC6: VA back to A; VB unchanged; one current per code; live importance (8) carried.
        db = seeded_db
        ids = self._seed(db)
        assert db.set_current_rubric_vector("cand-1", self._TASK, "va", ids["a"]) == ids["a"]
        cur = self._current(db)
        assert cur["VA"]["rubric_vector_uuid"] == ids["a"]
        assert cur["VA"]["content"] == "A"
        assert cur["VA"]["importance"] == 8
        assert cur["VB"]["rubric_vector_uuid"] == ids["v02"]
        all_rows = db.list_rubric_vectors("cand-1", self._TASK, current_only=False)
        for code in ("VA", "VB"):
            assert sum(1 for r in all_rows if r["code"] == code and r["current"] == 1) == 1

    def test_reset_already_current_keeps_own_importance(self, seeded_db) -> None:
        db = seeded_db
        ids = self._seed(db)
        assert db.set_current_rubric_vector("cand-1", self._TASK, "VA", ids["b"]) == ids["b"]
        assert self._current(db)["VA"]["importance"] == 8

    def test_cross_code_and_unknown_uuid_raise_without_change(self, seeded_db) -> None:
        db = seeded_db
        ids = self._seed(db)
        before = db.list_rubric_vectors("cand-1", self._TASK, current_only=False)
        with pytest.raises(ValueError, match="is not a version of"):
            db.set_current_rubric_vector("cand-1", self._TASK, "VA", ids["v02"])
        with pytest.raises(ValueError, match="is not a version of"):
            db.set_current_rubric_vector("cand-1", self._TASK, "VA", "no-such-uuid")
        assert db.list_rubric_vectors("cand-1", self._TASK, current_only=False) == before

    @pytest.mark.parametrize(
        "args",
        [("", "grade_do", "VA", "u"), ("cand-1", "", "VA", "u"), ("cand-1", "grade_do", " ", "u"), ("cand-1", "grade_do", "VA", "")],
    )
    def test_blank_args_raise(self, seeded_db, args) -> None:
        with pytest.raises(ValueError, match="required"):
            seeded_db.set_current_rubric_vector(*args)


# AST-2126 (AST-2127 tests): sync stores only codes agent._GRADE_SEG can decode — [A-Z]{2} after
# strip().upper(). Branches: invalid code (blank / V01 / one letter / digit / three letters) → ValueError,
# no V{idx} fallback, nothing committed for the owner (a valid earlier criterion in the same call included);
# lowercase valid code → stored uppercased.
class TestAst2126SyncRejectsUndecodableCodes:
    _TASK = "grade_do"

    @pytest.mark.parametrize("code", ["V01", "", "A", "G1", "CLR"])
    def test_invalid_code_raises_and_writes_nothing(self, seeded_db, code: str) -> None:
        db = seeded_db
        db.save_agent_task(self._TASK, agent_id="a1", user_prompt="p")
        crit = [
            {"code": "TP", "label": "Valid first", "content": "ok", "importance": 5},
            {"code": code, "label": "Bad", "content": "x", "importance": 5},
        ]
        with pytest.raises(ValueError, match=f"criterion 2 code {re.escape(repr(code))} is not two letters A-Z"):
            db.sync_rubric_vectors_from_criteria("cand-1", self._TASK, crit)
        assert db.list_rubric_vectors("cand-1", self._TASK) == []

    def test_lowercase_code_stored_uppercased(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task(self._TASK, agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1", self._TASK, [{"code": " tp", "label": "Truth", "content": "x", "importance": 5}]
        )
        assert [r["code"] for r in db.list_rubric_vectors("cand-1", self._TASK)] == ["TP"]
