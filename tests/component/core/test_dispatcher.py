"""Component tests for src/core/dispatcher.py (AST-393)."""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core import dispatcher as dispatcher_mod
from src.utils import config as cfg


@pytest.fixture(autouse=True)
def _clear_task_registry() -> None:
    original_tick = dispatcher_mod._tick_thread
    dispatcher_mod._tick_thread = None
    with dispatcher_mod._registry_lock:
        dispatcher_mod._task_registry.clear()
    yield
    dispatcher_mod._tick_thread = original_tick
    with dispatcher_mod._registry_lock:
        dispatcher_mod._task_registry.clear()


def _run_one_tick(monkeypatch: pytest.MonkeyPatch) -> None:
    # Raise StopIteration from a plain callable — generator.throw(StopIteration) becomes
    # RuntimeError under PEP 479 (breaks tick-loop tests on 3.9+).
    def _wait_breaks_tick_loop(timeout: object = None) -> None:
        raise StopIteration

    monkeypatch.setattr(dispatcher_mod._tick_event, "wait", _wait_breaks_tick_loop)
    monkeypatch.setattr(dispatcher_mod._tick_event, "clear", MagicMock())


class TestDispatchWrappers:
    def test_list_dispatch_ledger_enriches_costs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod,
            "_db_list_dispatch_ledger",
            lambda **kwargs: [{"batch_id": "batch-1"}, {"batch_id": None}],
        )
        monkeypatch.setattr(dispatcher_mod, "_db_sum_cost_by_batch", lambda batch_ids: {"batch-1": 2.5})
        rows = dispatcher_mod.list_dispatch_ledger()
        assert rows[0]["total_cost"] == 2.5
        assert rows[1]["total_cost"] == 0.0

    def test_ast571_ledger_total_cost_matches_timesheet_sum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Execution History display uses sum_cost_by_batch (calc_cost_* sum) — AST-571."""
        monkeypatch.setattr(
            dispatcher_mod,
            "_db_list_dispatch_ledger",
            lambda **kwargs: [{"batch_id": "draft_job_resume-f017d456-6ccb-4f90-82cc-364e1ec92c9f"}],
        )
        monkeypatch.setattr(
            dispatcher_mod,
            "_db_sum_cost_by_batch",
            lambda batch_ids: {"draft_job_resume-f017d456-6ccb-4f90-82cc-364e1ec92c9f": 0.044939528},
        )
        rows = dispatcher_mod.list_dispatch_ledger()
        assert rows[0]["total_cost"] == pytest.approx(0.044939528)

    def test_list_dispatch_ledger_skips_cost_lookup_without_batch_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod,
            "_db_list_dispatch_ledger",
            lambda **kwargs: [{"batch_id": None}],
        )
        summed = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_db_sum_cost_by_batch", summed)
        rows = dispatcher_mod.list_dispatch_ledger()
        summed.assert_not_called()
        assert rows[0]["total_cost"] == 0.0

    def test_thin_wrappers_delegate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod, "_db_get_dispatch_ledger", lambda batch_id: {"batch_id": batch_id})
        monkeypatch.setattr(dispatcher_mod, "_db_list_log_entries", lambda **kwargs: ["log"])
        monkeypatch.setattr(dispatcher_mod, "_db_save_dispatch_task", lambda *args, **kwargs: 7)
        monkeypatch.setattr(dispatcher_mod, "_db_get_dispatch_task", lambda task_id: {"id": task_id})
        monkeypatch.setattr(dispatcher_mod, "_db_list_dispatch_tasks", lambda: ["task"])
        update = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", update)
        assert dispatcher_mod.get_dispatch_ledger("batch-1")["batch_id"] == "batch-1"
        assert dispatcher_mod.list_log_entries(batch_id="batch-1") == ["log"]
        assert dispatcher_mod.save_dispatch_task("key", "cand") == 7
        assert dispatcher_mod.get_dispatch_task(3)["id"] == 3
        assert dispatcher_mod.list_dispatch_tasks() == ["task"]
        dispatcher_mod.update_dispatch_task(3, enabled=True)
        update.assert_called_once_with(3, enabled=True)


class TestScoredHelpers:
    def test_task_key_scored_uses_agent_task(self) -> None:
        assert dispatcher_mod._task_key_scored("evaluate_jd") is True
        assert dispatcher_mod._task_key_scored("missing_task") is False

    def test_trigger_state_scored_checks_consult_states(self) -> None:
        assert dispatcher_mod._trigger_state_scored(None, "evaluate_jd") is False
        assert dispatcher_mod._trigger_state_scored("JD_READY_RETRY", "evaluate_jd") is False
        assert dispatcher_mod._trigger_state_scored("PASSED_JD", "evaluate_jd") is True
        assert dispatcher_mod._trigger_state_scored("WATCH", "evaluate_jd") is False


class TestWarmThenGather:
    @pytest.mark.asyncio
    async def test_returns_empty_for_no_entities(self) -> None:
        assert await dispatcher_mod._warm_then_gather(AsyncMock(), [], dispatcher_mod._SUMMARY_ZERO) == []

    @pytest.mark.asyncio
    async def test_returns_single_result_without_delay(self, monkeypatch: pytest.MonkeyPatch) -> None:
        one = AsyncMock(return_value={"total_processed": 1})
        assert await dispatcher_mod._warm_then_gather(one, ["a"], dispatcher_mod._SUMMARY_ZERO) == [{"total_processed": 1}]
        one.assert_awaited_once_with("a")

    @pytest.mark.asyncio
    async def test_gathers_remaining_entities(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.asyncio, "sleep", AsyncMock())
        one = AsyncMock(side_effect=[{"total_processed": 1}, {"total_processed": 2}])
        out = await dispatcher_mod._warm_then_gather(one, ["a", "b"], dispatcher_mod._SUMMARY_ZERO)
        assert out == [{"total_processed": 1}, {"total_processed": 2}]

    @pytest.mark.asyncio
    async def test_converts_gather_exceptions_to_error_summary(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.asyncio, "sleep", AsyncMock())
        one = AsyncMock(side_effect=[{"total_processed": 1}, RuntimeError("boom")])
        out = await dispatcher_mod._warm_then_gather(one, ["a", "b"], dispatcher_mod._SUMMARY_ZERO)
        assert out[1]["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_skips_delay_when_cache_warm_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(dispatcher_mod.ASTRAL_CONFIG)
        cfg["cache_warm_delay_seconds"] = 0
        monkeypatch.setattr(dispatcher_mod, "ASTRAL_CONFIG", cfg)
        sleep = AsyncMock()
        monkeypatch.setattr(dispatcher_mod.asyncio, "sleep", sleep)
        one = AsyncMock(side_effect=[{"total_processed": 1}, {"total_processed": 2}])
        out = await dispatcher_mod._warm_then_gather(one, ["a", "b"], dispatcher_mod._SUMMARY_ZERO)
        assert out == [{"total_processed": 1}, {"total_processed": 2}]
        sleep.assert_not_awaited()


@pytest.fixture
def batch_id() -> str:
    token = dispatcher_mod.log_batch_id.set("batch-test")
    try:
        yield "batch-test"
    finally:
        dispatcher_mod.log_batch_id.reset(token)


class TestRunUnified:
    @pytest.mark.asyncio
    async def test_skips_when_network_unreachable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: False)
        out = await dispatcher_mod._run_unified({"task_key": "evaluate_jd"}, {}, False)
        assert out == dispatcher_mod._SUMMARY_ZERO

    @pytest.mark.asyncio
    async def test_claims_jobs_and_clears_batch(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"astral_job_id": "job-1"}]))
        clear = MagicMock()
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "job",
            "trigger_state": "JD_READY",
            "task_key": "evaluate_jd",
            "batch_size": 2,
            "batch_call_mode": 1,
            "score_floor": 0.5,
        }
        out = await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, True)
        assert out["total_processed"] == 1
        claim.assert_called_once()
        clear.assert_called_once_with(batch_id)
        run.assert_awaited_once()
        assert run.await_args.kwargs["dispatch_task_key"] == "evaluate_jd"

    @pytest.mark.asyncio
    async def test_ast534_forwards_dispatch_task_key_to_consult(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str,
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(
            return_value=(
                batch_id,
                [{"astral_job_id": "job-534", "state": cfg.BUILD_ARTIFACTS_BASE_STATE}],
            ),
        )
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "job",
            "trigger_state": cfg.BUILD_ARTIFACTS_BASE_STATE,
            "task_key": "anticipate_scan",
            "batch_call_mode": 0,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert run.await_args.kwargs["dispatch_task_key"] == "anticipate_scan"

    @pytest.mark.asyncio
    async def test_ast849_post_claim_filter_skips_row_mismatch(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str,
    ) -> None:
        """AST-849: claimed jobs filtered by dispatch_chain_row_matches_job before consult."""
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(
            return_value=(
                batch_id,
                [{"astral_job_id": "job-x", "state": "RECOMMENDED"}],
            ),
        )
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        run = AsyncMock()
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "job",
            "trigger_state": cfg.BUILD_ARTIFACTS_BASE_STATE,
            "task_key": "contemplate_job",
            "batch_call_mode": 0,
        }
        out = await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert out == dispatcher_mod._SUMMARY_ZERO
        claim.assert_called_once()
        run.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_claims_companies_and_runs_per_entity(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"short_name": "co"}]))
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr(dispatcher_mod, "_warm_then_gather", AsyncMock(return_value=[run.return_value]))
        task = {
            "entity_type": "company",
            "trigger_state": "WATCH",
            "task_key": "gaze",
            "batch_size": 1,
            "batch_call_mode": 0,
            "freq_hrs": 4,
            "sort_by": "last_scan_at",
        }
        out = await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert out["total_processed"] == 1
        clear.assert_called_once_with(batch_id)



    @pytest.mark.asyncio
    async def test_ast505_candidate_entity_routes_ctx_without_company_clear(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        clear_co = MagicMock()
        clear_job = MagicMock()
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear_co)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear_job)
        consult_out = {"total_processed": 1, "total_passed": 2, "total_failed": 0, "total_errors": 0}
        run = AsyncMock(return_value=consult_out)
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        ctx = {"astral_candidate_id": "c505", "state": "LIVE_PROMPTS", "candidate_data": {}}
        task = {
            "entity_type": "candidate",
            "trigger_state": "LIVE_PROMPTS",
            "task_key": "inflow_discovery",
            "batch_call_mode": 0,
        }
        out = await dispatcher_mod._run_unified(task, ctx, False)
        assert out == consult_out
        clear_co.assert_not_called()
        clear_job.assert_not_called()
        run.assert_awaited_once_with(
            "candidate", "LIVE_PROMPTS", [ctx], batch_id, ctx, False, dispatch_task_key="inflow_discovery",
        )

    @pytest.mark.asyncio
    async def test_ast506_inflow_resolve_claims_empty_website_only(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"short_name": "no_site", "state": "NEW"}]))
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "company",
            "trigger_state": "NEW",
            "task_key": "inflow_resolve_website",
            "batch_call_mode": 0,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "c506"}, False)
        claim.assert_called_once()
        assert claim.call_args.kwargs["require_empty_website"] is True

    @pytest.mark.asyncio
    async def test_ast508_prefilter_passed_dispatch_passes_score_floor(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"short_name": "inflow_co", "state": "PREFILTER_PASSED"}]))
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "company",
            "trigger_state": "PREFILTER_PASSED",
            "task_key": "fetch_job_pages",
            "batch_call_mode": 0,
            "score_floor": 7.0,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "c508"}, False)
        claim.assert_called_once()
        assert claim.call_args.kwargs["score_floor"] == 7.0
        assert claim.call_args.kwargs.get("require_empty_website") is False

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_entities_claimed(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", MagicMock(return_value=(batch_id, [])))
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        out = await dispatcher_mod._run_unified(
            {
                "entity_type": "job",
                "trigger_state": "JD_READY",
                "task_key": "evaluate_jd",
                "batch_call_mode": 1,
                "batch_size": 10,
            },
            {},
            True,
        )
        assert out == dispatcher_mod._SUMMARY_ZERO

    @pytest.mark.asyncio
    async def test_returns_zero_without_debug_logging(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", MagicMock(return_value=(batch_id, [])))
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        out = await dispatcher_mod._run_unified(
            {
                "entity_type": "job",
                "trigger_state": "JD_READY",
                "task_key": "evaluate_jd",
                "batch_call_mode": 1,
                "batch_size": 10,
            },
            {},
            False,
        )
        assert out == dispatcher_mod._SUMMARY_ZERO

    @pytest.mark.asyncio
    async def test_uses_default_score_floor_for_scored_states(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"astral_job_id": "job-1"}]))
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        monkeypatch.setattr("src.core.consult.run_consult_task", AsyncMock(return_value=dispatcher_mod._SUMMARY_ZERO))
        task = {
            "entity_type": "job",
            "trigger_state": "PASSED_JD",
            "task_key": "grade_do",
            "batch_call_mode": 1,
            "batch_size": 10,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert claim.call_args.kwargs["score_floor"] == 1.0

    @pytest.mark.asyncio
    async def test_qualify_valid_title_claim_without_score_floor(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        """AST-586: VALID_TITLE jobs lack latest_score — claim must not apply score_floor."""
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"astral_job_id": "job-1"}]))
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        monkeypatch.setattr("src.core.consult.run_consult_task", AsyncMock(return_value=dispatcher_mod._SUMMARY_ZERO))
        task = {
            "entity_type": "job",
            "trigger_state": "NEW",
            "task_key": "qualify_job_listings",
            "batch_call_mode": 1,
            "batch_size": 10,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        claim.assert_called_once()
        assert claim.call_args.kwargs["score_floor"] is None

    @pytest.mark.asyncio
    async def test_ast641_primary_job_trigger_passes_union_claim_states(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, []))
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        monkeypatch.setattr("src.core.consult.run_consult_task", AsyncMock(return_value=dispatcher_mod._SUMMARY_ZERO))
        task = {
            "entity_type": "job",
            "trigger_state": "NEW",
            "task_key": "qualify_job_listings",
            "batch_call_mode": 1,
            "batch_size": 10,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert claim.call_args.kwargs["states"] == ["NEW"]

    @pytest.mark.asyncio
    async def test_ast641_retry_only_job_trigger_single_claim_state(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, []))
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        monkeypatch.setattr("src.core.consult.run_consult_task", AsyncMock(return_value=dispatcher_mod._SUMMARY_ZERO))
        task = {
            "entity_type": "job",
            "trigger_state": "VALID_TITLE_RETRY",
            "task_key": "qualify_job_listings",
            "batch_call_mode": 1,
            "batch_size": 10,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert claim.call_args.kwargs["states"] == ["VALID_TITLE_RETRY"]

    @pytest.mark.asyncio
    async def test_ast641_company_prefilter_passes_union_claim_states(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, []))
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", MagicMock())
        monkeypatch.setattr("src.core.consult.run_consult_task", AsyncMock(return_value=dispatcher_mod._SUMMARY_ZERO))
        task = {
            "entity_type": "company",
            "trigger_state": "HOMEPAGE_READY",
            "task_key": "prefilter",
            "batch_call_mode": 1,
            "batch_size": 10,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert claim.call_args.kwargs["states"] == ["HOMEPAGE_READY"]

    @pytest.mark.asyncio
    async def test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        """batch_call_mode=1 → one ``run_consult_task`` await with the full claimed job list (not per-entity gather)."""
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        entities = [{"astral_job_id": "job-a"}, {"astral_job_id": "job-b"}]
        claim = MagicMock(return_value=(batch_id, entities))
        clear = MagicMock()
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear)
        run = AsyncMock(
            return_value={"total_processed": 2, "total_passed": 2, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "job",
            "trigger_state": "JD_READY",
            "task_key": "evaluate_jd",
            "batch_size": 2,
            "batch_call_mode": 1,
        }
        out = await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert out["total_processed"] == 2
        run.assert_awaited_once()
        assert run.await_args.kwargs["dispatch_task_key"] == "evaluate_jd"
        passed_entities = run.await_args.args[2]
        assert len(passed_entities) == 2
        assert {e["astral_job_id"] for e in passed_entities} == {"job-a", "job-b"}

    @pytest.mark.asyncio
    async def test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        """eligible > batch_size → K chunks; chunk 0 completes, one cache-warm sleep, then chunks 1…K−1 in gather."""
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "count_eligible_for_dispatch_task",
            MagicMock(return_value=2000),
        )
        chunk_sz = 500
        entities = [{"astral_job_id": f"j{i:04d}"} for i in range(2000)]
        claim = MagicMock(return_value=(batch_id, entities))
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())

        seq: List[Tuple[str, Any]] = []
        lens: List[Tuple[Optional[int], int]] = []

        async def run_capture(
            entity_type: str,
            input_state: str,
            ents: List[Dict[str, Any]],
            bid_arg: str,
            ctx_arg: Dict[str, Any],
            debug: bool,
            batch_chunk_index: Optional[int] = None,
            dispatch_task_key: str = "",
        ) -> Dict[str, int]:
            seq.append(("consult_enter", batch_chunk_index))
            lens.append((batch_chunk_index, len(ents)))
            seq.append(("consult_exit", batch_chunk_index))
            return {
                "total_processed": len(ents),
                "total_passed": len(ents),
                "total_failed": 0,
                "total_errors": 0,
            }

        monkeypatch.setattr("src.core.consult.run_consult_task", run_capture)

        delay = 0.41
        cfg = dict(dispatcher_mod.ASTRAL_CONFIG)
        cfg["cache_warm_delay_seconds"] = delay
        monkeypatch.setattr(dispatcher_mod, "ASTRAL_CONFIG", cfg)

        async def track_sleep(sec: float) -> None:
            seq.append(("sleep", sec))

        sleep_spy = AsyncMock(side_effect=track_sleep)
        monkeypatch.setattr(dispatcher_mod.asyncio, "sleep", sleep_spy)

        task = {
            "entity_type": "job",
            "trigger_state": "JD_READY",
            "task_key": "evaluate_jd",
            "batch_size": chunk_sz,
            "batch_call_mode": 1,
            "id": 999,
        }
        out = await dispatcher_mod._run_unified(task, {"astral_candidate_id": "c1"}, False)

        assert out["total_processed"] == 2000
        assert lens == [(i, chunk_sz) for i in range(4)]
        ix0e = seq.index(("consult_enter", 0))
        ix0x = seq.index(("consult_exit", 0))
        ixs = seq.index(("sleep", delay))
        assert ix0e < ix0x < ixs
        for ci in range(1, 4):
            assert seq.index(("consult_enter", ci)) > ixs
        sleep_spy.assert_awaited_once()
        assert claim.call_args.kwargs.get("claim_cap") == 2000

    @pytest.mark.asyncio
    async def test_ast502_two_chunks_skips_sleep_when_delay_zero(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        """Same splitter; cache_warm_delay_seconds=0 must not await asyncio.sleep."""
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "count_eligible_for_dispatch_task",
            MagicMock(return_value=4),
        )
        entities = [{"astral_job_id": f"j{i}"} for i in range(4)]
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", MagicMock(return_value=(batch_id, entities)))
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())

        run = AsyncMock(
            return_value={"total_processed": 2, "total_passed": 2, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr("src.core.consult.run_consult_task", run)

        cfg = dict(dispatcher_mod.ASTRAL_CONFIG)
        cfg["cache_warm_delay_seconds"] = 0
        monkeypatch.setattr(dispatcher_mod, "ASTRAL_CONFIG", cfg)
        sleep_spy = AsyncMock()
        monkeypatch.setattr(dispatcher_mod.asyncio, "sleep", sleep_spy)

        task = {
            "entity_type": "job",
            "trigger_state": "VALID_TITLE",
            "task_key": "qualify_job_listings",
            "batch_size": 2,
            "batch_call_mode": 1,
            "id": 1001,
        }
        ctx = {"astral_candidate_id": "c1"}
        out = await dispatcher_mod._run_unified(task, ctx, False)

        assert out["total_processed"] == 4
        assert run.await_count == 2
        sleep_spy.assert_not_awaited()
        assert run.call_args_list[0].kwargs["batch_chunk_index"] == 0
        assert run.call_args_list[1].kwargs["batch_chunk_index"] == 1
        assert len(run.call_args_list[0].args[2]) == 2
        assert len(run.call_args_list[1].args[2]) == 2

    @pytest.mark.asyncio
    async def test_runs_per_entity_consult_calls(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", MagicMock(return_value=(batch_id, [{"astral_job_id": "job-1"}])))
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        monkeypatch.setattr(dispatcher_mod.asyncio, "sleep", AsyncMock())
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "job",
            "trigger_state": "JD_READY",
            "task_key": "evaluate_jd",
            "batch_call_mode": 0,
        }
        out = await dispatcher_mod._run_unified(task, {}, False)
        assert out["total_processed"] == 1
        run.assert_awaited_once()


class TestCircuitBreaker:
    def test_disables_task_after_zero_progress_runs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_recent_ledger_summaries",
            lambda task_key, candidate_id, n: [{"total_passed": 0, "total_failed": 0}] * 3,
        )
        update = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", update)
        dispatcher_mod._check_circuit_breaker("evaluate_jd", "cand-1", 9, False)
        update.assert_called_once_with(9, enabled=False)

    def test_ignores_short_history(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_recent_ledger_summaries",
            lambda task_key, candidate_id, n: [{"total_passed": 0, "total_failed": 0}],
        )
        update = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", update)
        dispatcher_mod._check_circuit_breaker("evaluate_jd", "cand-1", 9, False)
        update.assert_not_called()

    def test_keeps_enabled_when_recent_runs_show_progress(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_recent_ledger_summaries",
            lambda task_key, candidate_id, n: [
                {"total_passed": 0, "total_failed": 0},
                {"total_passed": 1, "total_failed": 0},
                {"total_passed": 0, "total_failed": 0},
            ],
        )
        update = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", update)
        dispatcher_mod._check_circuit_breaker("evaluate_jd", "cand-1", 9, False)
        update.assert_not_called()


class TestRunTask:
    @pytest.mark.asyncio
    async def test_delegates_to_unified_runner(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "_run_unified", AsyncMock(return_value={"total_processed": 2, "total_passed": 2, "total_failed": 0, "total_errors": 0}))
        out = await dispatcher_mod._run_task({"task_key": "evaluate_jd", "batch_size": 2}, {}, True)
        assert out["total_processed"] == 2

    @pytest.mark.asyncio
    async def test_runs_without_debug_logging(self, monkeypatch: pytest.MonkeyPatch, batch_id: str) -> None:
        monkeypatch.setattr(dispatcher_mod, "_run_unified", AsyncMock(return_value=dispatcher_mod._SUMMARY_ZERO))
        out = await dispatcher_mod._run_task({"task_key": "evaluate_jd", "batch_size": 2}, {}, False)
        assert out == dispatcher_mod._SUMMARY_ZERO


class TestRegistryControls:
    def test_run_task_rejects_duplicate_or_missing_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[1] = {"thread": MagicMock(is_alive=MagicMock(return_value=True))}
        assert dispatcher_mod.run_task(1) is False
        monkeypatch.setattr(dispatcher_mod.database, "get_dispatch_task", lambda task_id: None)
        assert dispatcher_mod.run_task(2) is False

    def test_run_task_starts_daemon_thread(self, monkeypatch: pytest.MonkeyPatch) -> None:
        started: list[threading.Thread] = []

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self._target = target
                self._args = args
                self.daemon = daemon
                self.name = name

            def start(self) -> None:
                started.append(self)

            def is_alive(self) -> bool:
                return False

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "id": task_id,
                "task_key": "evaluate_jd",
                "entity_type": "job",
                "trigger_state": "JD_READY",
                "candidate_id": "cand-1",
            },
        )
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 3)
        assert dispatcher_mod.run_task(5) is True
        assert started

    def test_drain_and_cancel_report_registry_state(self) -> None:
        assert dispatcher_mod.drain_task(1)["reason"] == "not_running"
        assert dispatcher_mod.cancel_task(1)["reason"] == "not_running"
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[2] = {
                "task_key": "evaluate_jd",
                "candidate_id": "cand-1",
                "drain": False,
            }
        assert dispatcher_mod.drain_task(2)["draining"] is True
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[3] = {
                "task_key": "evaluate_jd",
                "candidate_id": "cand-1",
                "loop": None,
                "asyncio_task": None,
            }
        assert dispatcher_mod.cancel_task(3)["reason"] == "not_yet_ready"

    def test_cancel_all_and_status_all(self) -> None:
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[4] = {
                "thread": MagicMock(is_alive=MagicMock(return_value=True)),
                "drain": False,
                "task_key": "evaluate_jd",
                "candidate_id": "cand-1",
                "is_auto": True,
            }
        assert dispatcher_mod.cancel_all_tasks()[0]["reason"] == "not_yet_ready"
        assert dispatcher_mod.task_status_all()[4]["running"] is True

    def test_run_task_zero_available_without_entity_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self.daemon = daemon
                self.name = name

            def start(self) -> None:
                return None

            def is_alive(self) -> bool:
                return False

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_dispatch_task",
            lambda task_id: {"id": task_id, "task_key": "evaluate_jd", "candidate_id": "cand-1"},
        )
        counted = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", counted)
        assert dispatcher_mod.run_task(8) is True
        counted.assert_not_called()

    def test_cancel_task_reports_already_done(self) -> None:
        loop = MagicMock()
        asyncio_task = MagicMock()
        asyncio_task.done.return_value = True
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[6] = {
                "task_key": "evaluate_jd",
                "candidate_id": "cand-1",
                "loop": loop,
                "asyncio_task": asyncio_task,
            }
        assert dispatcher_mod.cancel_task(6)["reason"] == "already_done"

    def test_cancel_task_sends_cancellation(self) -> None:
        loop = MagicMock()
        asyncio_task = MagicMock()
        asyncio_task.done.return_value = False
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[7] = {
                "task_key": "evaluate_jd",
                "candidate_id": "cand-1",
                "loop": loop,
                "asyncio_task": asyncio_task,
            }
        out = dispatcher_mod.cancel_task(7)
        assert out["killed"] is True
        loop.call_soon_threadsafe.assert_called_once_with(asyncio_task.cancel)


class TestNowIso:
    def test_returns_utc_timestamp(self) -> None:
        assert len(dispatcher_mod._now_iso()) == 19


def test_current_agent_task_run_next_missing_agent_task_row(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.core import agent as agent_mod

    monkeypatch.setattr(agent_mod, "get_agent_task", lambda _task_key: None)
    assert agent_mod._current_agent_task_run_next("gaze") == ""
    assert agent_mod._current_agent_task_run_next("recheck_no_openings") == ""


class TestDispatchOne:
    @pytest.mark.asyncio
    async def test_skips_without_candidate_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "get_candidate", lambda candidate_id: None)
        await dispatcher_mod._dispatch_one({"id": 1, "task_key": "evaluate_jd", "candidate_id": "cand-1"})

    @pytest.mark.asyncio
    async def test_skips_without_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        await dispatcher_mod._dispatch_one({"id": 1, "task_key": "evaluate_jd", "candidate_id": "cand-1"})

    @pytest.mark.asyncio
    async def test_run_next_chain_skips_dispatch_level_ledger(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import agent as agent_mod

        monkeypatch.setattr(
            dispatcher_mod,
            "_current_agent_task_run_next",
            lambda task_key: "contemplate_job",
        )
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock())
        task = {"id": 20, "task_key": "anticipate_scan", "candidate_id": "cand-1", "auto_mode": 0}
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[20] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        save_ledger.assert_not_called()
        assert dispatcher_mod.log_batch_id.get() is None

    @pytest.mark.asyncio
    async def test_completes_click_dispatch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        breaker = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", breaker)
        loop = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", loop)
        task = {"id": 2, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 0, "skip_cache": 1}
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[2] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        loop.assert_awaited_once()
        assert loop.await_args.args[0]["skip_cache"] is True
        assert dispatcher_mod.log_batch_id.get() is None
        breaker.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_dispatch_uses_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", MagicMock())
        wait_for = AsyncMock(side_effect=asyncio.TimeoutError())
        monkeypatch.setattr(dispatcher_mod.asyncio, "wait_for", wait_for)
        task = {"id": 3, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 1}
        await dispatcher_mod._dispatch_one(task)
        wait_for.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cancelled_dispatch_marks_interrupted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        update_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", update_ledger)
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=asyncio.CancelledError()))
        task = {"id": 4, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 0}
        await dispatcher_mod._dispatch_one(task)
        assert update_ledger.call_args.kwargs["status"] == "INTERRUPTED"

    @pytest.mark.asyncio
    async def test_failed_dispatch_records_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        update_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", update_ledger)
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=RuntimeError("boom")))
        task = {"id": 5, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 0}
        await dispatcher_mod._dispatch_one(task)
        assert update_ledger.call_args.kwargs["status"] == "FAILED"

    @pytest.mark.asyncio
    async def test_auto_run_error_on_auto_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=2.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        alert = MagicMock()
        monkeypatch.setattr(dispatcher_mod.monitor, "auto_run_error", alert)

        async def _bump(ctx, task, task_key, batch_id, accumulated):
            accumulated["total_errors"] = 1

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_bump))
        task = {"id": 6, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 1}
        await dispatcher_mod._dispatch_one(task)
        alert.assert_called_once()
        assert alert.call_args.args[4] == "cand-1"

    @pytest.mark.asyncio
    async def test_ledger_write_failure_is_logged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock(side_effect=RuntimeError("ledger")))
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=1.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock())
        task = {"id": 7, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 0}
        await dispatcher_mod._dispatch_one(task)

    @pytest.mark.asyncio
    async def test_last_run_update_failure_is_logged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=3.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock(side_effect=RuntimeError("task row")))

        async def _process(ctx, task, task_key, batch_id, accumulated):
            accumulated["total_processed"] = 2

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_process))
        task = {"id": 8, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 0}
        await dispatcher_mod._dispatch_one(task)


class TestAst841DispatchTerminalLogging:
    """AST-841: terminal ERROR/WARNING app_log lines align ledger status with log severities."""

    @pytest.mark.asyncio
    async def test_interrupted_dispatch_emits_terminal_error_log(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(
            dispatcher_mod.database,
            "save_dispatch_ledger",
            MagicMock(return_value=99),
        )
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=asyncio.CancelledError()))
        task = {"id": 41, "task_key": "inflow_discovery", "candidate_id": "cand-1", "auto_mode": 0}
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[41] = {"asyncio_task": None}
        with caplog.at_level("ERROR", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one(task)
        assert any(
            "batch finished INTERRUPTED" in r.message and "inflow_discovery" in r.message
            for r in caplog.records
        )

    @pytest.mark.asyncio
    async def test_completed_with_errors_emits_terminal_warning_log(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "key"},
        )
        monkeypatch.setattr(
            dispatcher_mod.database,
            "save_dispatch_ledger",
            MagicMock(return_value=100),
        )
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", MagicMock())

        async def _bump(ctx, task, task_key, batch_id, accumulated, dispatch_ledger_id=None):
            accumulated["total_errors"] = 2
            accumulated["total_processed"] = 5

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_bump))
        task = {"id": 42, "task_key": "inflow_discovery", "candidate_id": "cand-1", "auto_mode": 0}
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[42] = {"asyncio_task": None}
        with caplog.at_level("WARNING", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one(task)
        assert any(
            "batch finished COMPLETED with errors" in r.message
            and "errors=2" in r.message
            and "inflow_discovery" in r.message
            for r in caplog.records
        )


class TestRunDispatchLoop:
    @pytest.mark.asyncio
    async def test_skips_when_queue_below_min_count(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 0)
        run = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {"id": 1, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY", "auto_mode": 1, "min_count": 2}
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "batch-1", accumulated, None)
        run.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_stops_after_drain_flag(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 5)
        monkeypatch.setattr(dispatcher_mod, "_run_task", AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}))
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[9] = {"drain": True}
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {"id": 9, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY", "auto_mode": 1, "min_count": 1}
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "batch-1", accumulated, None)
        assert accumulated["total_processed"] == 0

    @pytest.mark.asyncio
    async def test_stops_when_batch_processes_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 5)
        monkeypatch.setattr(dispatcher_mod, "_run_task", AsyncMock(return_value=dispatcher_mod._SUMMARY_ZERO))
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {"id": 10, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY", "auto_mode": 0, "min_count": 1}
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "batch-1", accumulated, None)
        assert accumulated["total_processed"] == 0

    @pytest.mark.asyncio
    async def test_honours_max_runs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 5)
        monkeypatch.setattr(
            dispatcher_mod,
            "_run_task",
            AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}),
        )
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {
            "id": 11,
            "task_key": "evaluate_jd",
            "entity_type": "job",
            "trigger_state": "JD_READY",
            "auto_mode": 1,
            "min_count": 1,
            "max_runs": 2,
        }
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "batch-1", accumulated, None)
        assert accumulated["total_processed"] == 2

    @pytest.mark.asyncio
    async def test_stops_after_first_run_when_max_runs_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 5)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {"id": 12, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY", "auto_mode": 1, "min_count": 1, "max_runs": None}
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "batch-1", accumulated, None)
        run.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_continues_when_max_runs_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        counts = iter([5, 5, 0])
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: next(counts))
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {"id": 13, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY", "auto_mode": 1, "min_count": 1, "max_runs": 0}
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "batch-1", accumulated, None)
        assert run.await_count == 2

    @pytest.mark.asyncio
    async def test_logs_stop_after_prior_runs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        counts = iter([5, 0])
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: next(counts))
        monkeypatch.setattr(
            dispatcher_mod,
            "_run_task",
            AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}),
        )
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {"id": 14, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY", "auto_mode": 1, "min_count": 1, "max_runs": 0}
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "batch-1", accumulated, None)
        assert accumulated["total_processed"] == 1


class TestAst802InflowDiscoveryDebug:
    @pytest.mark.asyncio
    async def test_skip_emits_eligibility_reason_when_debug_true(
        self, monkeypatch: pytest.MonkeyPatch, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        db.save_candidate("c802", state="NEW", candidate_data={})
        log = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "logger", log)
        run = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {
            "id": 802,
            "task_key": "inflow_discovery",
            "entity_type": "candidate",
            "trigger_state": "LIVE_PROMPTS",
            "candidate_id": "c802",
            "auto_mode": 1,
            "min_count": 1,
            "debug": True,
        }
        await dispatcher_mod._run_dispatch_loop({}, task, "inflow_discovery", "batch-802", accumulated, None)
        run.assert_not_awaited()
        details = [str(c.args[0]) for c in log.debug_detail.call_args_list]
        assert any("eligibility:" in d for d in details)


class TestAst814InflowDiscoveryDebug:
    @pytest.mark.asyncio
    async def test_skip_cites_freq_hrs_when_all_terms_fresh(
        self, monkeypatch: pytest.MonkeyPatch, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        db.save_candidate("c814", state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms("c814", ["term"])
        db.update_company_search_term_last_scan_at("c814", "term")
        log = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "logger", log)
        run = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {
            "id": 814,
            "task_key": "inflow_discovery",
            "entity_type": "candidate",
            "trigger_state": "LIVE_PROMPTS",
            "candidate_id": "c814",
            "auto_mode": 1,
            "min_count": 1,
            "freq_hrs": 168,
            "debug": True,
        }
        await dispatcher_mod._run_dispatch_loop({}, task, "inflow_discovery", "batch-814", accumulated, None)
        run.assert_not_awaited()
        details = [str(c.args[0]) for c in log.debug_detail.call_args_list]
        assert any("freq_hrs=168" in d for d in details)
        assert not any("scan_interval_hours" in d for d in details)


class TestTaskThreadTarget:
    def test_cleans_registry_after_loop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        loop = MagicMock()
        loop.run_until_complete = MagicMock()
        loop.close = MagicMock()
        monkeypatch.setattr(dispatcher_mod.asyncio, "new_event_loop", lambda: loop)
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[15] = {}
        dispatcher_mod._task_thread_target(15, {"task_key": "evaluate_jd"})
        assert 15 not in dispatcher_mod._task_registry
        loop.close.assert_called_once()
        loop.run_until_complete.assert_called_once()

    def test_skips_loop_assignment_without_registry_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        loop = MagicMock()
        loop.run_until_complete = MagicMock()
        loop.close = MagicMock()
        monkeypatch.setattr(dispatcher_mod.asyncio, "new_event_loop", lambda: loop)
        dispatcher_mod._task_thread_target(16, {"task_key": "evaluate_jd"})
        loop.close.assert_called_once()


class TestScheduler:
    def test_start_scheduler_is_idempotent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        thread = MagicMock()
        thread.is_alive.return_value = True
        dispatcher_mod._tick_thread = thread
        created = MagicMock()
        monkeypatch.setattr(dispatcher_mod.threading, "Thread", created)
        dispatcher_mod.start_scheduler()
        created.assert_not_called()

    def test_start_scheduler_marks_stale_ledgers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dispatcher_mod._tick_thread = None
        stale = MagicMock(return_value=2)
        monkeypatch.setattr(dispatcher_mod.database, "mark_stale_ledger_interrupted", stale)
        started: list[threading.Thread] = []

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self._target = target
                self.daemon = daemon
                self.name = name

            def start(self) -> None:
                started.append(self)

            def is_alive(self) -> bool:
                return True

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        dispatcher_mod.start_scheduler()
        stale.assert_called_once()
        assert started

    def test_start_scheduler_skips_stale_warning_when_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dispatcher_mod._tick_thread = None
        stale = MagicMock(return_value=0)
        monkeypatch.setattr(dispatcher_mod.database, "mark_stale_ledger_interrupted", stale)

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self.daemon = daemon

            def start(self) -> None:
                return None

            def is_alive(self) -> bool:
                return False

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        dispatcher_mod.start_scheduler()
        stale.assert_called_once()

    def test_tick_loop_spawns_due_auto_tasks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = [{"id": 20}, {"id": 21}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        spawned: list[int] = []
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id: spawned.append(task_id) or True)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == [20, 21]

    def test_tick_loop_skips_running_and_full_slots(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = [{"id": 30}, {"id": 31}, {"id": 32}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[30] = {"is_auto": True}
        spawned: list[int] = []
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id: spawned.append(task_id) or True)
        cfg = dict(dispatcher_mod.ASTRAL_CONFIG)
        cfg["max_auto_threads"] = 2
        monkeypatch.setattr(dispatcher_mod, "ASTRAL_CONFIG", cfg)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == [31]

    def test_tick_loop_ignores_failed_spawn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = [{"id": 40}, {"id": 41}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        spawned: list[int] = []
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id: spawned.append(task_id) or False)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == [40, 41]

    def test_tick_loop_stops_when_spawn_slots_are_exhausted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = [{"id": 52}, {"id": 53}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        spawned: list[int] = []
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id: spawned.append(task_id) or True)
        cfg = dict(dispatcher_mod.ASTRAL_CONFIG)
        cfg["max_auto_threads"] = 1
        monkeypatch.setattr(dispatcher_mod, "ASTRAL_CONFIG", cfg)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == [52]

    def test_tick_loop_skips_when_auto_slots_full(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = [{"id": 50}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[51] = {"is_auto": True}
        spawned: list[int] = []
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id: spawned.append(task_id) or True)
        cfg = dict(dispatcher_mod.ASTRAL_CONFIG)
        cfg["max_auto_threads"] = 1
        monkeypatch.setattr(dispatcher_mod, "ASTRAL_CONFIG", cfg)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == []

    def test_tick_loop_calls_clear_after_wait_then_stops(self, monkeypatch: pytest.MonkeyPatch) -> None:
        wait_calls: list[int] = []

        def wait_then_stop(timeout=None):
            wait_calls.append(1)
            if len(wait_calls) >= 2:
                raise StopIteration
            return None

        monkeypatch.setattr(dispatcher_mod._tick_event, "wait", wait_then_stop)
        clear = MagicMock()
        monkeypatch.setattr(dispatcher_mod._tick_event, "clear", clear)
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: [])
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        clear.assert_called()
        assert len(wait_calls) == 2

    def test_tick_loop_swallows_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", MagicMock(side_effect=RuntimeError("tick")))
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()


class TestAst875SetCandidateDispatchTasksFromTemplate:
    """AST-875: core set-from-template orchestration; no run_task side effects."""

    def test_set_from_template_happy_path_and_idempotent(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        monkeypatch.setattr(dispatcher_mod, "database", db)
        monkeypatch.setattr(dispatcher_mod, "template_candidate_id", lambda: "tmpl")
        run = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "run_task", run, raising=False)

        db.save_candidate("tmpl", state="LIVE_PROMPTS", candidate_data={})
        db.save_candidate("tgt", state="LIVE_PROMPTS", candidate_data={})
        db.save_dispatch_task(
            "tmpl", "fetch_website", min_count=2, trigger_state="WEBSITE_FOUND", auto_mode=True, batch_size=4,
        )
        db.save_dispatch_task(
            "tgt", "evaluate_jd", min_count=1, trigger_state="JD_READY",
        )

        out = dispatcher_mod.set_candidate_dispatch_tasks_from_template("tgt")
        assert out["candidate_id"] == "tgt"
        assert out["template_candidate_id"] == "tmpl"
        assert out["inserted"] == 1
        assert out["updated"] == 0
        assert out["deleted"] == 1
        assert out["count"] == 1
        rows = db.list_dispatch_tasks_for_candidate("tgt")
        assert len(rows) == 1
        assert rows[0]["task_key"] == "fetch_website"
        assert rows[0]["auto_mode"] in (1, True)
        assert rows[0]["last_run_at"] is None
        assert rows[0]["batch_id"] is None
        run.assert_not_called()

        out2 = dispatcher_mod.set_candidate_dispatch_tasks_from_template("tgt")
        assert out2["inserted"] == 0 and out2["updated"] == 1 and out2["deleted"] == 0
        run.assert_not_called()

    def test_missing_candidates_and_blank_target(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        monkeypatch.setattr(dispatcher_mod, "database", db)
        monkeypatch.setattr(dispatcher_mod, "template_candidate_id", lambda: "tmpl")
        with pytest.raises(ValueError, match="candidate_id is required"):
            dispatcher_mod.set_candidate_dispatch_tasks_from_template("  ")
        with pytest.raises(LookupError, match="Template candidate not found"):
            dispatcher_mod.set_candidate_dispatch_tasks_from_template("tgt")
        db.save_candidate("tmpl", state="LIVE_PROMPTS", candidate_data={})
        with pytest.raises(LookupError, match="Candidate not found"):
            dispatcher_mod.set_candidate_dispatch_tasks_from_template("tgt")
