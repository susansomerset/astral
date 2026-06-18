"""rubric_vector + vector_feedback table cluster (AST-722)."""

from __future__ import annotations

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
        assert db.save_agent_data(
            "id-1",
            "candidate",
            "prefilter_company",
            "batch-722",
            "FEEDBACK",
            "payload",
        ) is True
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
