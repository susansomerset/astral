"""Component tests for src/core/dispatcher.py (AST-393)."""

from __future__ import annotations

import asyncio
import threading
from contextlib import asynccontextmanager
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


@pytest.fixture
def real_server_gate() -> None:
    """AST-1944 opt-out: request this fixture to run the real task_llm_server_id_or_none resolver.
    A fixture, not a marker — pytest.ini runs --strict-markers."""
    return None


@pytest.fixture(autouse=True)
def _task_server_anthropic(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """AST-1879 / AST-1944: skip gate resolves the task agent's server via task_llm_server_id_or_none —
    pin it so candidate stubs carrying candidate_api_keys["anthropic"] reach dispatch without a seeded
    agent_task row. Tests requesting real_server_gate keep the real resolver."""
    # Return before setattr so the repro also runs on pre-AST-1944 trees (attribute absent there).
    if "real_server_gate" in request.fixturenames:
        return
    monkeypatch.setattr(dispatcher_mod, "task_llm_server_id_or_none", lambda task_key: "anthropic")


def _run_one_tick(monkeypatch: pytest.MonkeyPatch) -> None:
    # Raise StopIteration from a plain callable — generator.throw(StopIteration) becomes
    # RuntimeError under PEP 479 (breaks tick-loop tests on 3.9+).
    def _wait_breaks_tick_loop(timeout: object = None) -> None:
        raise StopIteration

    monkeypatch.setattr(dispatcher_mod._tick_event, "wait", _wait_breaks_tick_loop)
    monkeypatch.setattr(dispatcher_mod._tick_event, "clear", MagicMock())
    # AST-972: tick ages waiting stages before get_due_tasks — keep unit ticks DB-free
    monkeypatch.setattr(
        "src.core.candidate.age_stale_candidate_states",
        MagicMock(return_value=0),
    )
    # AST-1022: tick Style D AUTO-off side path lists stage rows — keep unit ticks DB-free
    monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: [])
    # AST-1022: tick Style D AUTO-off side path lists stage rows — keep unit ticks DB-free
    monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: [])


def _stub_scheduler_boot_provisions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep start_scheduler unit tests DB-free across legacy provision / AST-1252 retire hooks.

    AST-1500 / AST-1496: start_scheduler must not call dispatch_task provision/ensure writers;
    stubs remain so older tip shapes and wrapper-retire tests stay DB-free.
    """
    monkeypatch.setattr(
        dispatcher_mod,
        "provision_meteorite_dispatch_tasks",
        MagicMock(return_value={"template_candidate_id": "tmpl", "candidates_touched": 0}),
    )
    if hasattr(dispatcher_mod, "retire_candidate_requested_wrapper_dispatch_tasks"):
        monkeypatch.setattr(
            dispatcher_mod,
            "retire_candidate_requested_wrapper_dispatch_tasks",
            MagicMock(
                return_value={
                    "template_candidate_id": "tmpl",
                    "candidates_scanned": 0,
                    "retired": 0,
                }
            ),
        )
    _gaze = MagicMock(
        return_value={
            "task_key": "meteorite_email",
            "retired_null": 0,
            "candidates_touched": 0,
            "added": 0,
            "skipped": 0,
            "skipped_missing_config": 0,
        }
    )
    if hasattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks"):
        monkeypatch.setattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks", _gaze)
    if hasattr(dispatcher_mod, "ensure_fetch_email_dispatch_task"):
        monkeypatch.setattr(
            dispatcher_mod,
            "ensure_fetch_email_dispatch_task",
            MagicMock(
                return_value={
                    "task_key": "fetch_email",
                    "added": 0,
                    "skipped": 0,
                    "skipped_missing_config": 0,
                }
            ),
        )
    # AST-1623: UPDATE-only ingress/notify entity_type correction on boot.
    if hasattr(dispatcher_mod, "correct_meteorite_ingress_dispatch_entity_types"):
        monkeypatch.setattr(
            dispatcher_mod,
            "correct_meteorite_ingress_dispatch_entity_types",
            MagicMock(return_value={"scanned": 0, "updated": 0, "task_keys": []}),
        )


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
    async def test_ast2025_fetch_relative_jd_claims_trigger_state_and_releases_on_error(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str,
    ) -> None:
        # AC6: claim by RELATIVE_JOB_LINK only; lock released even when the runner raises.
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"astral_job_id": "job-r", "state": "RELATIVE_JOB_LINK"}]))
        clear = MagicMock()
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", claim)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear)
        run = AsyncMock(side_effect=RuntimeError("runner boom"))
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "job",
            "trigger_state": cfg._dispatch_trigger_state_for_task_key("fetch_relative_jd"),
            "task_key": "fetch_relative_jd",
            "batch_call_mode": 1,
        }
        with pytest.raises(RuntimeError, match="runner boom"):
            await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert claim.call_args.args[0] == "RELATIVE_JOB_LINK"
        assert claim.call_args.kwargs["candidate_id"] == "cand-1"
        # Base + its derived retry holding only — no other job state is claimable.
        assert claim.call_args.kwargs["states"] == ["RELATIVE_JOB_LINK", "RELATIVE_JOB_LINK_RETRY"]
        clear.assert_called_once_with(batch_id)
        assert run.await_args.kwargs["dispatch_task_key"] == "fetch_relative_jd"

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
    async def test_ast891_parse_job_list_full_batch_despite_batch_call_mode_zero(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str,
    ) -> None:
        """AST-891: parse_job_list always full-list consult — never _warm_then_gather fan-out."""
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        companies = [{"short_name": "co-a"}, {"short_name": "co-b"}]
        claim = MagicMock(return_value=(batch_id, companies))
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        run = AsyncMock(
            return_value={"total_processed": 2, "total_passed": 2, "total_failed": 0, "total_errors": 0},
        )
        warm = AsyncMock()
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        monkeypatch.setattr(dispatcher_mod, "_warm_then_gather", warm)
        task = {
            "entity_type": "company",
            "trigger_state": "JOBLIST_IDENTIFIED",
            "task_key": "parse_job_list",
            "batch_size": 20,
            "batch_call_mode": 0,
        }
        out = await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert out["total_processed"] == 2
        run.assert_awaited_once()
        assert run.await_args.args[2] == companies
        assert run.await_args.kwargs["dispatch_task_key"] == "parse_job_list"
        warm.assert_not_awaited()
        clear.assert_called_once_with(batch_id)

    @pytest.mark.asyncio
    async def test_ast505_candidate_entity_claims_without_company_clear(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        # AST-1259: pool claim via get_new_candidate_batch; clear_candidate_batch in finally (not job/company).
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claimed = [{"astral_candidate_id": "c505", "state": "ACTIVE_SEARCH", "candidate_data": {}}]
        claim = MagicMock(return_value=(batch_id, claimed))
        clear_cand = MagicMock()
        clear_co = MagicMock()
        clear_job = MagicMock()
        monkeypatch.setattr("src.core.candidate.get_new_candidate_batch", claim)
        monkeypatch.setattr("src.core.candidate.clear_candidate_batch", clear_cand)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear_co)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear_job)
        consult_out = {"total_processed": 1, "total_passed": 2, "total_failed": 0, "total_errors": 0}
        run = AsyncMock(return_value=consult_out)
        monkeypatch.setattr("src.core.consult.run_consult_task", run)

        async def _immediate_warm(one_fn, entities, zero):
            return [await one_fn(e) for e in entities]

        monkeypatch.setattr(dispatcher_mod, "_warm_then_gather", _immediate_warm)
        ctx = {"astral_candidate_id": "c505", "state": "ACTIVE_SEARCH", "candidate_data": {}}
        task = {
            "entity_type": "candidate",
            "trigger_state": "ACTIVE_SEARCH",
            "task_key": "inflow_discovery",
            "batch_size": 1,
            "batch_call_mode": 0,
        }
        out = await dispatcher_mod._run_unified(task, ctx, False)
        assert out == consult_out
        claim.assert_called_once()
        clear_cand.assert_called_once_with(batch_id)
        clear_co.assert_not_called()
        clear_job.assert_not_called()
        run.assert_awaited_once_with(
            "candidate", "ACTIVE_SEARCH", claimed, batch_id, ctx, False, dispatch_task_key="inflow_discovery",
        )

    @pytest.mark.asyncio
    async def test_ast506_inflow_resolve_claims_empty_website_only(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        # AST-1673: empty-website filter only when resolve claims DISCOVERED.
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, [{"short_name": "no_site", "state": "DISCOVERED"}]))
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        task = {
            "entity_type": "company",
            "trigger_state": "DISCOVERED",
            "task_key": "inflow_resolve_website",
            "batch_call_mode": 0,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "c506"}, False)
        claim.assert_called_once()
        assert claim.call_args.kwargs["require_empty_website"] is True

    @pytest.mark.asyncio
    async def test_ast1673_inflow_resolve_on_new_skips_empty_website_filter(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        # AC6: require_empty_website never applied when claiming NEW for resolve.
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, []))
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        monkeypatch.setattr(
            "src.core.consult.run_consult_task",
            AsyncMock(return_value={"total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0}),
        )
        task = {
            "entity_type": "company",
            "trigger_state": "NEW",
            "task_key": "inflow_resolve_website",
            "batch_call_mode": 0,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "c1673"}, False)
        claim.assert_called_once()
        assert claim.call_args.kwargs.get("require_empty_website") is False

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
        # AST-898: NEW.retry_state → NEW_RETRY companions on primary qualify row
        assert claim.call_args.kwargs["states"] == ["NEW", "NEW_RETRY"]

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
            "task_key": "prefilter_company",
            "batch_call_mode": 1,
            "batch_size": 10,
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "cand-1"}, False)
        assert claim.call_args.kwargs["states"] == ["HOMEPAGE_READY", "WEBSITE_FOUND_RETRY"]

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

    # AST-1847 / AST-1848: ctx["dispatch_partial"] — fresh copy per run, popped on normal
    # return, left in place on cancel (timeout branch folds it); finally still clears the batch.
    @staticmethod
    def _ast1847_company_claim(monkeypatch: pytest.MonkeyPatch, batch_id: str) -> Tuple[MagicMock, Dict[str, Any]]:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        monkeypatch.setattr(
            "src.core.roster.get_new_company_batch",
            MagicMock(return_value=(batch_id, [{"short_name": "co-1", "state": "JOBLIST_IDENTIFIED"}])),
        )
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        task = {
            "entity_type": "company",
            "trigger_state": "JOBLIST_IDENTIFIED",
            "task_key": "parse_job_list",
            "batch_call_mode": 1,
        }
        return clear, task

    @pytest.mark.asyncio
    async def test_ast1847_sets_fresh_dispatch_partial_and_pops_on_return(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str,
    ) -> None:
        _clear, task = self._ast1847_company_claim(monkeypatch, batch_id)
        # Stale partial from a prior run must not leak into this one.
        ctx = {
            "astral_candidate_id": "cand-1",
            "dispatch_partial": {"total_processed": 9, "total_passed": 9, "total_failed": 0, "total_errors": 0},
        }
        seen: Dict[str, Any] = {}

        async def _seen(*_a, **_k):
            seen["partial"] = dict(ctx["dispatch_partial"])
            seen["is_zero_const"] = ctx["dispatch_partial"] is dispatcher_mod._SUMMARY_ZERO
            return {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}

        monkeypatch.setattr("src.core.consult.run_consult_task", AsyncMock(side_effect=_seen))
        out = await dispatcher_mod._run_unified(task, ctx, False)
        assert seen["partial"] == dispatcher_mod._SUMMARY_ZERO
        # Copy, so the module constant is never mutated by batch runners.
        assert seen["is_zero_const"] is False
        assert "dispatch_partial" not in ctx
        assert out["total_processed"] == 1

    @pytest.mark.asyncio
    async def test_ast1847_cancel_keeps_dispatch_partial_and_clears_batch(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str,
    ) -> None:
        clear, task = self._ast1847_company_claim(monkeypatch, batch_id)
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}

        async def _tally_then_cancel(*_a, **_k):
            ctx["dispatch_partial"]["total_processed"] += 1
            ctx["dispatch_partial"]["total_passed"] += 1
            raise asyncio.CancelledError()

        monkeypatch.setattr("src.core.consult.run_consult_task", AsyncMock(side_effect=_tally_then_cancel))
        with pytest.raises(asyncio.CancelledError):
            await dispatcher_mod._run_unified(task, ctx, False)
        # Pop is on the normal-return path only; cancel leaves the partial for the timeout fold-in.
        assert ctx["dispatch_partial"] == {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        clear.assert_called_once_with(batch_id)


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
    async def test_skips_without_candidate_context(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "get_candidate", lambda candidate_id: None)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        with caplog.at_level("WARNING", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one({"id": 1, "task_key": "evaluate_jd", "candidate_id": "cand-1"})
        save_ledger.assert_not_called()
        assert any(
            "cand-1 | dispatch evaluate_jd skipped — no candidate or anthropic API key" in r.getMessage()
            and "This task is not starting" in r.getMessage()
            for r in caplog.records
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "keys",
        [
            None,
            {},
            # AST-1879 AC 7: another platform's key does not open the gate.
            {"kimi": "sk-kimi", "deepseek": "sk-ds"},
            {"anthropic": ""},
        ],
    )
    async def test_skips_without_task_servers_api_key(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, keys: Any
    ) -> None:
        row: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        if keys is not None:
            row["candidate_api_keys"] = keys
        monkeypatch.setattr(dispatcher_mod.database, "get_candidate", lambda candidate_id: row)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        with caplog.at_level("WARNING", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one({"id": 1, "task_key": "evaluate_jd", "candidate_id": "cand-1"})
        save_ledger.assert_not_called()
        assert any("skipped — no candidate or anthropic API key" in r.getMessage() for r in caplog.records)

    @pytest.mark.asyncio
    async def test_gate_reads_key_for_task_agents_server(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        # AST-1879 / AST-1944: the gate asks task_llm_server_id_or_none(task_key) which server to check.
        seen: List[str] = []

        def _server(task_key: str) -> str:
            seen.append(task_key)
            return "kimi"

        monkeypatch.setattr(dispatcher_mod, "task_llm_server_id_or_none", _server)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "sk-ant"}},
        )
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        with caplog.at_level("WARNING", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one({"id": 1, "task_key": "evaluate_jd", "candidate_id": "cand-1"})
        assert seen == ["evaluate_jd"]
        save_ledger.assert_not_called()
        assert any("no candidate or kimi API key" in r.getMessage() for r in caplog.records)

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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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

    # AST-1988: unified entity run stamps log_candidate_id beside log_batch_id and clears both in finally.
    # Branches: loop ok → stamped mid-run, cleared; loop raises → still cleared; run_next chain → neither stamped here.
    def _ast1988_run(self, monkeypatch: pytest.MonkeyPatch, task_id: int, loop_side_effect) -> list:
        # test_completes_click_dispatch patch set; the loop mock records (batch, candidate) mid-run.
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", MagicMock())
        seen: list = []

        async def _loop(*_a, **_k):
            seen.append((dispatcher_mod.log_batch_id.get(), dispatcher_mod.log_candidate_id.get()))
            if loop_side_effect is not None:
                raise loop_side_effect

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_loop))
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[task_id] = {"asyncio_task": None}
        return seen

    async def _ast1988_dispatch(self, task: Dict[str, Any]) -> None:
        # Start both vars at None (tokens) so a leak elsewhere can't green the post-run checks.
        tb = dispatcher_mod.log_batch_id.set(None)
        tc = dispatcher_mod.log_candidate_id.set(None)
        try:
            await dispatcher_mod._dispatch_one(task)
            assert dispatcher_mod.log_batch_id.get() is None
            assert dispatcher_mod.log_candidate_id.get() is None
        finally:
            dispatcher_mod.log_candidate_id.reset(tc)
            dispatcher_mod.log_batch_id.reset(tb)

    @pytest.mark.asyncio
    async def test_ast1988_unified_run_stamps_candidate_with_batch_and_clears(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        seen = self._ast1988_run(monkeypatch, 1988, None)
        await self._ast1988_dispatch({"id": 1988, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 0})
        assert len(seen) == 1
        assert seen[0][0].startswith("evaluate_jd-")
        assert seen[0][1] == "cand-1"

    @pytest.mark.asyncio
    async def test_ast1988_failed_run_still_clears_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        seen = self._ast1988_run(monkeypatch, 19881, RuntimeError("boom"))
        await self._ast1988_dispatch({"id": 19881, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 0})
        assert len(seen) == 1
        assert seen[0][1] == "cand-1"

    @pytest.mark.asyncio
    async def test_ast1988_run_next_chain_leaves_candidate_unset_like_batch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Same chain setup as test_run_next_chain_skips_dispatch_level_ledger: the agent hop opener owns the stamp.
        monkeypatch.setattr(dispatcher_mod, "_current_agent_task_run_next", lambda task_key: "contemplate_job")
        seen = self._ast1988_run(monkeypatch, 19882, None)
        await self._ast1988_dispatch(
            {"id": 19882, "task_key": "anticipate_scan", "candidate_id": "cand-1", "auto_mode": 0}
        )
        assert seen == [(None, None)]

    @pytest.mark.asyncio
    async def test_auto_run_error_on_auto_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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


@pytest.mark.usefixtures("real_server_gate")
class TestAst1944NonLlmGate:
    """AST-1944: real resolver on the skip gate — patch the agent data layer, never the resolver.

    agent_mod.get_agent_task / get_agent feed _resolve_task_prompts, task_llm_server_id(_or_none),
    and _current_agent_task_run_next (dispatcher imports those from agent, so module globals apply).
    """

    @staticmethod
    def _data(
        monkeypatch: pytest.MonkeyPatch, rows: Dict[str, Dict[str, Any]], agents: Dict[str, Dict[str, Any]]
    ) -> None:
        from src.core import agent as agent_mod

        monkeypatch.setattr(agent_mod, "get_agent_task", lambda k: rows.get(k))
        monkeypatch.setattr(agent_mod, "get_agent", lambda i: agents.get(i))

    @staticmethod
    def _scaffold(monkeypatch: pytest.MonkeyPatch, candidate: Optional[Dict[str, Any]]) -> Tuple[AsyncMock, MagicMock]:
        # Same dispatch scaffolding as TestDispatchOne.test_completes_click_dispatch.
        monkeypatch.setattr(dispatcher_mod.database, "get_candidate", lambda candidate_id: candidate)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", MagicMock())
        loop = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", loop)
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[44] = {"asyncio_task": None}
        return loop, save_ledger

    _TASK = {"id": 44, "task_key": "fetch_jd", "candidate_id": "cand-1", "auto_mode": 0}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "rows",
        [
            # "telescope" sentinel — agents has no telescope row, so the strict path raises first.
            {"fetch_jd": {"task_key": "fetch_jd", "agent_id": "telescope", "current": 1}},
            {"fetch_jd": {"task_key": "fetch_jd", "agent_id": "", "current": 1}},
            # AST-537 invariant: no agent_task row at all.
            {},
        ],
        ids=["telescope", "empty_agent_id", "no_row"],
    )
    async def test_non_llm_key_reaches_handler_without_any_api_key(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, rows: Dict[str, Any]
    ) -> None:
        # [bug-repro] AST-1944: red on origin/dev (strict resolver raises out of _dispatch_one), green after fix.
        self._data(monkeypatch, rows, {})
        loop, _ = self._scaffold(monkeypatch, {"astral_candidate_id": "cand-1", "candidate_api_keys": {}})
        with caplog.at_level("WARNING", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one(dict(self._TASK))
        loop.assert_awaited_once()
        assert not any("skipped — no candidate" in r.getMessage() for r in caplog.records)

    @pytest.mark.asyncio
    async def test_non_llm_key_missing_candidate_still_skipped(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        self._data(monkeypatch, {"fetch_jd": {"task_key": "fetch_jd", "agent_id": "telescope", "current": 1}}, {})
        loop, save_ledger = self._scaffold(monkeypatch, None)
        with caplog.at_level("WARNING", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one(dict(self._TASK))
        loop.assert_not_awaited()
        save_ledger.assert_not_called()
        # No server for a non-LLM key — the warning's server slot prints None (AST-1944 plan).
        assert any(
            "cand-1 | dispatch fetch_jd skipped — no candidate or None API key" in r.getMessage()
            for r in caplog.records
        )

    @pytest.mark.asyncio
    async def test_llm_key_without_server_key_still_skipped(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        # AST-1879 holds on the real resolver: deepseek-v4-pro → server "deepseek"; an anthropic key does not count.
        # AST-1956: plain-settings row shape (no brain_setting / mode).
        self._data(
            monkeypatch,
            {"evaluate_jd": {"task_key": "evaluate_jd", "agent_id": "a1", "current": 1}},
            {"a1": {"agent_id": "a1", "model_id": "deepseek-v4-pro", "temperature": 0.2}},
        )
        loop, save_ledger = self._scaffold(monkeypatch, {"astral_candidate_id": "cand-1", "candidate_api_keys": {"anthropic": "sk-ant"}})
        with caplog.at_level("WARNING", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one({**self._TASK, "task_key": "evaluate_jd"})
        loop.assert_not_awaited()
        save_ledger.assert_not_called()
        assert any(
            "cand-1 | dispatch evaluate_jd skipped — no candidate or deepseek API key" in r.getMessage()
            for r in caplog.records
        )

    @pytest.mark.asyncio
    async def test_unknown_real_agent_still_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # A misconfigured LLM task stays loud — no silent gate bypass.
        self._data(monkeypatch, {"evaluate_jd": {"task_key": "evaluate_jd", "agent_id": "ghost", "current": 1}}, {})
        loop, _ = self._scaffold(monkeypatch, {"astral_candidate_id": "cand-1", "candidate_api_keys": {"anthropic": "sk-ant"}})
        with pytest.raises(ValueError, match="Agent 'ghost'"):
            await dispatcher_mod._dispatch_one({**self._TASK, "task_key": "evaluate_jd"})
        loop.assert_not_awaited()


class TestAst841DispatchTerminalLogging:
    """AST-841: terminal ERROR/WARNING app_log lines align ledger status with log severities."""

    @pytest.mark.asyncio
    async def test_interrupted_dispatch_emits_terminal_error_log(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
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


class TestAst1847TimeoutPartialCounts:
    """AST-1847 / AST-1848: dispatch timeout keeps finished companies' counts in ledger + log."""

    @staticmethod
    def _stub_dispatch_one(monkeypatch: pytest.MonkeyPatch, task_id: int, timeout_s: float) -> MagicMock:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        update_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", update_ledger)
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", MagicMock())
        monkeypatch.setattr(dispatcher_mod.monitor, "auto_run_error", MagicMock())
        # Sub-second timeout only triggers the cancel; nothing asserts on elapsed time.
        monkeypatch.setitem(dispatcher_mod.ASTRAL_CONFIG, "dispatch_timeout_seconds", timeout_s)
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[task_id] = {"asyncio_task": None}
        return update_ledger

    @pytest.mark.asyncio
    async def test_parse_job_list_timeout_ledger_and_log_carry_partial_counts(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
    ) -> None:
        # bug-repro: real _dispatch_one → _run_dispatch_loop → _run_task → _run_unified →
        # consult.run_consult_task → roster.parse_job_list_batch; only claim, browser and the
        # per-company dispatch are faked, so the ctx reference must survive consult.
        from src.core import roster as roster_mod
        from src.utils.config import ROSTER_CONFIG

        update_ledger = self._stub_dispatch_one(monkeypatch, 1847, 0.2)
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        # No run_next chain → this dispatch owns the ledger row.
        monkeypatch.setattr(dispatcher_mod, "_current_agent_task_run_next", lambda _tk: None)
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda _t: 4)
        companies = [{"short_name": n, "state": "JOBLIST_IDENTIFIED"} for n in ("a", "b", "c", "d")]
        claimed: List[str] = []

        def _claim(*_a, **k):
            claimed.append(k["batch_id"])
            return k["batch_id"], companies

        monkeypatch.setattr("src.core.roster.get_new_company_batch", _claim)
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)

        @asynccontextmanager
        async def _batch():
            yield MagicMock()

        monkeypatch.setattr(roster_mod, "create_batch_browser_session", _batch)
        monkeypatch.setattr(roster_mod, "get_company", lambda _sn: {})
        parse_cfg = ROSTER_CONFIG["parse_job_list"]

        async def _dispatch(company, batch_id, ctx, debug, batch_session=None):
            name = company["short_name"]
            if name in ("a", "b"):
                return {"state": parse_cfg["pass_state"]}
            if name == "c":
                return {"state": parse_cfg["retry_state"]}
            await asyncio.sleep(3600)  # d: still in flight when the dispatch timeout fires

        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", _dispatch)
        task = {
            "id": 1847,
            "task_key": "parse_job_list",
            "candidate_id": "cand-1",
            "entity_type": "company",
            "trigger_state": "JOBLIST_IDENTIFIED",
            "auto_mode": 1,
            "batch_call_mode": 1,
            "max_runs": 1,
        }
        with caplog.at_level("ERROR", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one(task)

        kw = update_ledger.call_args.kwargs
        assert kw["status"] == "INTERRUPTED"
        # a, b passed; c retried (processed, not error); d cancelled → uncounted; errors=1 is the timeout.
        assert (kw["total_processed"], kw["total_passed"], kw["total_failed"], kw["total_errors"]) == (3, 2, 0, 1)
        assert any(
            "dispatch timeout after" in r.message and "processed=3 passed=2 failed=0 errors=1" in r.message
            for r in caplog.records
        )
        # AST-891 AC2: _run_unified finally still releases the claim on cancel.
        assert len(claimed) == 1
        clear.assert_called_once_with(claimed[0])

    @pytest.mark.asyncio
    async def test_timeout_folds_partial_on_top_of_prior_runs(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
    ) -> None:
        update_ledger = self._stub_dispatch_one(monkeypatch, 1848, 0.05)
        captured: Dict[str, Any] = {}

        async def _hang(ctx, task, task_key, batch_id, accumulated, dispatch_ledger_id=None):
            captured["ctx"] = ctx
            # Completed prior runs already in accumulated; in-flight run's partial on ctx.
            accumulated.update(total_processed=5, total_passed=4, total_failed=0, total_errors=1)
            ctx["dispatch_partial"] = {"total_processed": 2, "total_passed": 1, "total_failed": 0, "total_errors": 1}
            await asyncio.sleep(3600)

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_hang))
        task = {"id": 1848, "task_key": "evaluate_jd", "candidate_id": "cand-1", "auto_mode": 1}
        with caplog.at_level("ERROR", logger="src.core.dispatcher"):
            await dispatcher_mod._dispatch_one(task)

        kw = update_ledger.call_args.kwargs
        # errors = 1 prior + 1 partial + 1 timeout
        assert (kw["total_processed"], kw["total_passed"], kw["total_failed"], kw["total_errors"]) == (7, 5, 0, 3)
        # +1 timeout lands before the log line, so log == ledger.
        assert any("processed=7 passed=5 failed=0 errors=3" in r.message for r in caplog.records)
        assert "dispatch_partial" not in captured["ctx"]


# Branches: first balance refusal marks ctx["provider_balance_outage"]; per-entity + chunk paths
# skip remaining work; loop stops after the outage run; AUTO → INTERRUPTED + outage alert (no
# auto_run_error, no breaker); CLICK → INTERRUPTED, no alert; ordinary errors never mark ctx.
class TestAst1867ProviderBalanceOutage:
    """AST-1867 / AST-1870: provider balance refusal reported as one batch-level outage."""

    _FC = "provider_balance_refusal"
    _REFUSAL_ERR = "Error code: 402 - Insufficient Balance"

    @staticmethod
    def _edges(monkeypatch: pytest.MonkeyPatch, task_id: int) -> Dict[str, MagicMock]:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
        )
        # a run_next chain would suppress the ledger id and with it the alert
        monkeypatch.setattr(dispatcher_mod, "_current_agent_task_run_next", lambda _tk: None)
        mocks = {
            "save_dispatch_ledger": MagicMock(),
            "update_dispatch_ledger": MagicMock(),
            "breaker": MagicMock(),
            "auto_run_error": MagicMock(),
            "provider_balance_outage": MagicMock(),
        }
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", mocks["save_dispatch_ledger"])
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", mocks["update_dispatch_ledger"])
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        # patched, never called: TestCircuitBreaker carries unrelated arity drift
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", mocks["breaker"])
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        monkeypatch.setitem(dispatcher_mod.ASTRAL_CONFIG, "cache_warm_delay_seconds", 0)
        monkeypatch.setattr(dispatcher_mod.monitor, "auto_run_error", mocks["auto_run_error"])
        # raising=False: pre-fix monitor has no such attribute — repro must fail on asserts, not setup
        monkeypatch.setattr(
            dispatcher_mod.monitor, "provider_balance_outage", mocks["provider_balance_outage"], raising=False,
        )
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[task_id] = {"asyncio_task": None}
        return mocks

    @staticmethod
    def _claim_companies(monkeypatch: pytest.MonkeyPatch, n: int) -> Dict[str, MagicMock]:
        companies = [
            {"short_name": f"co{i}", "state": "PJL_READY", "company_website": f"https://co{i}"}
            for i in range(n)
        ]
        claim = MagicMock(return_value=("bid-1867", companies))
        clear = MagicMock()
        monkeypatch.setattr("src.core.roster.get_new_company_batch", claim)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear)
        return {"claim": claim, "clear": clear}

    @pytest.mark.asyncio
    async def test_bug_repro_balance_refusal_one_call_interrupted_outage_alert(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # [bug-repro] pre-fix: every company calls the provider on every run (3 × 3 = 9), run
        # ends COMPLETED with errors, auto_run_error fires, breaker is consulted.
        # Real stack: _dispatch_one → _run_dispatch_loop → _run_task → _run_unified →
        # consult.run_consult_task → roster.run_company_task; only the AST-1842 held return is faked.
        from src.core import roster as roster_mod

        edges = self._edges(monkeypatch, 1867)
        # held companies stay eligible — only the outage stop can end the loop early
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda _t: 24)
        claimed = self._claim_companies(monkeypatch, 3)
        select = AsyncMock(
            return_value={
                "state": "PJL_READY",
                "response_type": "SELECT_FAILED",
                "error": self._REFUSAL_ERR,
                "failure_class": self._FC,
                "state_held": True,
            }
        )
        monkeypatch.setattr(roster_mod, "run_select_job_page_dispatch", select)
        task = {
            "id": 1867,
            "task_key": "select_job_page",
            "candidate_id": "cand-1",
            "entity_type": "company",
            "trigger_state": "PJL_READY",
            "batch_call_mode": 0,
            "batch_size": 3,
            "auto_mode": 1,
            # bounds the pre-fix run; 0 (unlimited) would never end there
            "max_runs": 3,
        }
        await dispatcher_mod._dispatch_one(task)

        assert select.await_count == 1
        assert claimed["claim"].call_count == 1
        claimed["clear"].assert_called_once_with("bid-1867")
        kw = edges["update_dispatch_ledger"].call_args.kwargs
        assert kw["status"] == "INTERRUPTED"
        assert (kw["total_processed"], kw["total_errors"]) == (1, 0)
        edges["auto_run_error"].assert_not_called()
        edges["provider_balance_outage"].assert_called_once()
        args = edges["provider_balance_outage"].call_args.args
        assert args[0] == "select_job_page"
        assert args[1].startswith("select_job_page-")
        assert args[3] == {"error": self._REFUSAL_ERR, "held": 1}
        assert args[4] == "cand-1"
        edges["breaker"].assert_not_called()

    @pytest.mark.asyncio
    async def test_run_unified_per_entity_skips_after_refusal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._edges(monkeypatch, 18672)
        claimed = self._claim_companies(monkeypatch, 3)
        consult = AsyncMock(
            return_value={
                "total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0,
                "total_held": 1, "failure_class": self._FC, "error": self._REFUSAL_ERR,
            }
        )
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 18672, "task_key": "select_job_page", "entity_type": "company",
            "trigger_state": "PJL_READY", "batch_call_mode": 0, "batch_size": 3,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        out = await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 1
        # held / failure_class stay off the summary — update_dispatch_ledger rejects unknown keys
        assert out == {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}
        assert ctx["provider_balance_outage"] == {"error": self._REFUSAL_ERR, "held": 1}
        claimed["clear"].assert_called_once_with("bid-1867")

    @pytest.mark.asyncio
    async def test_run_unified_chunk_split_skips_tail_after_head_refusal(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._edges(monkeypatch, 18673)
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda _t: 3)
        jobs = [{"astral_job_id": f"j{i}", "state": "JD_READY"} for i in range(3)]
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", MagicMock(return_value=("bid-j", jobs)))
        monkeypatch.setattr("src.core.tracker.clear_job_batch", MagicMock())
        consult = AsyncMock(
            return_value={
                "total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1,
                "failure_class": self._FC, "error": self._REFUSAL_ERR,
            }
        )
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 18673, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY",
            "batch_call_mode": 1, "batch_size": 1, "score_floor": 0.5,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        await dispatcher_mod._run_unified(task, ctx, False)

        # head chunk refused → both tail chunks skipped
        assert consult.await_count == 1
        # consult envelopes carry no total_held
        assert ctx["provider_balance_outage"]["held"] == 0

    @pytest.mark.asyncio
    async def test_run_unified_ordinary_error_does_not_skip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._edges(monkeypatch, 18674)
        self._claim_companies(monkeypatch, 3)
        consult = AsyncMock(return_value={"total_processed": 1, "total_errors": 1, "error": "boom"})
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 18674, "task_key": "select_job_page", "entity_type": "company",
            "trigger_state": "PJL_READY", "batch_call_mode": 0, "batch_size": 3,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        out = await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 3
        assert "provider_balance_outage" not in ctx
        assert out["total_errors"] == 3

    @pytest.mark.asyncio
    async def test_run_dispatch_loop_stops_after_outage_run(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # finite eligibility so the pre-fix loop (no outage stop) still terminates
        monkeypatch.setattr(
            dispatcher_mod.database, "count_eligible_for_dispatch_task", MagicMock(side_effect=[24, 24, 24, 0]),
        )
        update_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", update_ledger)

        async def _run(task, ctx, debug):
            ctx["provider_balance_outage"] = {"error": self._REFUSAL_ERR, "held": 1}
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}

        run_task = AsyncMock(side_effect=_run)
        monkeypatch.setattr(dispatcher_mod, "_run_task", run_task)
        # max_runs 0 = unlimited: only the outage stop (or drained eligibility) ends the loop
        task = {"id": 18675, "task_key": "select_job_page", "entity_type": "company", "auto_mode": 1, "max_runs": 0}
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        accumulated = {"total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0}
        await dispatcher_mod._run_dispatch_loop(ctx, task, "select_job_page", "bid", accumulated, "bid")

        assert run_task.await_count == 1
        # mid-run ledger write happens before the stop
        update_ledger.assert_called_once_with(
            "bid", total_processed=1, total_passed=0, total_failed=0, total_errors=0,
        )

    @pytest.mark.asyncio
    async def test_dispatch_one_click_outage_interrupted_no_alert(self, monkeypatch: pytest.MonkeyPatch) -> None:
        edges = self._edges(monkeypatch, 18676)

        async def _loop(ctx, task, task_key, batch_id, accumulated, dispatch_ledger_id):
            ctx["provider_balance_outage"] = {"error": self._REFUSAL_ERR, "held": 1}
            accumulated["total_processed"] = 1

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_loop))
        task = {"id": 18676, "task_key": "select_job_page", "candidate_id": "cand-1", "auto_mode": 0}
        await dispatcher_mod._dispatch_one(task)

        assert edges["update_dispatch_ledger"].call_args.kwargs["status"] == "INTERRUPTED"
        # alerts stay AUTO-only
        edges["provider_balance_outage"].assert_not_called()
        edges["auto_run_error"].assert_not_called()
        edges["breaker"].assert_not_called()


# AST-2010 branches: first exhausted-429 result marks ctx["provider_rate_limit_outage"] at all three
# _run_unified call sites (per-entity, chunk, full batch); remaining work skipped; loop stops after
# the run; ledger FAILED (wins over balance INTERRUPTED), breaker skipped; untagged 429 never marks ctx.
class TestAst2010ProviderRateLimitOutage:
    """AST-2010: OpenRouter 429 still refused after retries stops the batch; ledger FAILED."""

    _FC = "provider_rate_limit"
    _ERR = "Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error'}}"
    _edges = staticmethod(TestAst1867ProviderBalanceOutage._edges)
    _claim_companies = staticmethod(TestAst1867ProviderBalanceOutage._claim_companies)

    def _summary(self, **extra: Any) -> Dict[str, Any]:
        return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1, **extra}

    @staticmethod
    def _claim_jobs(monkeypatch: pytest.MonkeyPatch, n: int, state: str) -> MagicMock:
        jobs = [{"astral_job_id": f"j{i}", "state": state} for i in range(n)]
        monkeypatch.setattr("src.core.tracker.get_new_job_batch", MagicMock(return_value=("bid-2010", jobs)))
        clear = MagicMock()
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear)
        return clear

    @pytest.mark.asyncio
    async def test_bug_repro_rate_limit_stops_batch_ledger_failed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # [bug-repro] AST-2009: 2-entity meteorite_like, per-entity warm-then-gather. Pre-fix: every
        # entity is sent on every run (2 × 3 = 6) and the ledger finishes COMPLETED.
        edges = self._edges(monkeypatch, 2010)
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda _t: 24)
        clear = self._claim_jobs(monkeypatch, 2, "LIKE_READY")
        consult = AsyncMock(return_value=self._summary(failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 2010, "task_key": "meteorite_like", "candidate_id": "cand-1", "entity_type": "job",
            "trigger_state": "LIKE_READY", "batch_call_mode": 0, "batch_size": 2, "auto_mode": 1, "max_runs": 3,
        }
        await dispatcher_mod._dispatch_one(task)

        # warm entity exhausted → gather entity never sent, no second run
        assert consult.await_count == 1
        clear.assert_called_once_with("bid-2010")
        kw = edges["update_dispatch_ledger"].call_args.kwargs
        assert kw["status"] == "FAILED"
        assert (kw["total_processed"], kw["total_errors"]) == (1, 1)
        edges["provider_balance_outage"].assert_not_called()
        edges["breaker"].assert_not_called()

    @pytest.mark.asyncio
    async def test_run_unified_per_entity_skips_after_rate_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._edges(monkeypatch, 20102)
        claimed = self._claim_companies(monkeypatch, 3)
        consult = AsyncMock(return_value=self._summary(failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 20102, "task_key": "select_job_page", "entity_type": "company",
            "trigger_state": "PJL_READY", "batch_call_mode": 0, "batch_size": 3,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        out = await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 1
        # failure_class / error stay off the summary — update_dispatch_ledger rejects unknown keys
        assert out == {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}
        assert ctx["provider_rate_limit_outage"] == {"error": self._ERR}
        assert "provider_balance_outage" not in ctx
        claimed["clear"].assert_called_once_with("bid-1867")

    @pytest.mark.asyncio
    async def test_run_unified_chunk_split_skips_tail_after_head_rate_limit(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._edges(monkeypatch, 20103)
        self._claim_jobs(monkeypatch, 3, "JD_READY")
        consult = AsyncMock(return_value=self._summary(failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 20103, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY",
            "batch_call_mode": 1, "batch_size": 1, "score_floor": 0.5,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 1
        assert ctx["provider_rate_limit_outage"] == {"error": self._ERR}

    @pytest.mark.asyncio
    async def test_run_unified_full_batch_marks_rate_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._edges(monkeypatch, 20104)
        self._claim_jobs(monkeypatch, 2, "JD_READY")
        consult = AsyncMock(return_value=self._summary(failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        # batch_size ≥ claimed → one consult call for the whole batch (no chunk split)
        task = {
            "id": 20104, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY",
            "batch_call_mode": 1, "batch_size": 5, "score_floor": 0.5,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 1
        assert ctx["provider_rate_limit_outage"] == {"error": self._ERR}

    @pytest.mark.asyncio
    async def test_run_unified_untagged_429_does_not_skip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # DeepSeek / Kimi exhausted 429 arrives untagged — today's behavior, every entity still sent
        self._edges(monkeypatch, 20105)
        self._claim_companies(monkeypatch, 3)
        consult = AsyncMock(return_value=self._summary(error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 20105, "task_key": "select_job_page", "entity_type": "company",
            "trigger_state": "PJL_READY", "batch_call_mode": 0, "batch_size": 3,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        out = await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 3
        assert "provider_rate_limit_outage" not in ctx
        assert out["total_errors"] == 3

    @pytest.mark.asyncio
    async def test_run_dispatch_loop_stops_after_rate_limit_run(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database, "count_eligible_for_dispatch_task", MagicMock(side_effect=[24, 24, 24, 0]),
        )
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())

        async def _run(task, ctx, debug):
            ctx["provider_rate_limit_outage"] = {"error": self._ERR}
            return self._summary()

        run_task = AsyncMock(side_effect=_run)
        monkeypatch.setattr(dispatcher_mod, "_run_task", run_task)
        task = {"id": 20106, "task_key": "meteorite_like", "entity_type": "job", "auto_mode": 1, "max_runs": 0}
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        await dispatcher_mod._run_dispatch_loop({"astral_candidate_id": "cand-1"}, task, "meteorite_like", "bid", accumulated, "bid")

        assert run_task.await_count == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("with_balance", [False, True])
    async def test_dispatch_one_rate_limit_outage_failed(
        self, monkeypatch: pytest.MonkeyPatch, with_balance: bool,
    ) -> None:
        edges = self._edges(monkeypatch, 20107)

        async def _loop(ctx, task, task_key, batch_id, accumulated, dispatch_ledger_id):
            ctx["provider_rate_limit_outage"] = {"error": self._ERR}
            if with_balance:
                ctx["provider_balance_outage"] = {"error": "Error code: 402 - Insufficient Balance", "held": 1}
            accumulated["total_processed"] = 1

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_loop))
        task = {"id": 20107, "task_key": "meteorite_like", "candidate_id": "cand-1", "auto_mode": 1}
        await dispatcher_mod._dispatch_one(task)

        # FAILED wins over the balance outage's INTERRUPTED
        assert edges["update_dispatch_ledger"].call_args.kwargs["status"] == "FAILED"
        edges["breaker"].assert_not_called()


# AST-2098 branches: first failed-host-probe result marks ctx["provider_probe_outage"] {"error", "held"} at
# all three _run_unified call sites; remaining work skipped; loop stops after the run; ledger INTERRUPTED,
# no alert, no auto_run_error, breaker skipped; rate limit's FAILED wins. Literals only (no AST-2098
# imports) so the repro fails by assertion on the pre-fix tree.
class TestAst2098ProviderProbeOutage:
    """AST-2098: a failed host probe is a no-op run — entities held, run stopped, next round probes again."""

    _FC = "provider_probe_failure"
    _ERR = "Host probe failed: Probe response named no provider: {'message': 'No endpoints found'}"
    _edges = staticmethod(TestAst1867ProviderBalanceOutage._edges)
    _claim_companies = staticmethod(TestAst1867ProviderBalanceOutage._claim_companies)
    _claim_jobs = staticmethod(TestAst2010ProviderRateLimitOutage._claim_jobs)

    @staticmethod
    def _held(**extra: Any) -> Dict[str, Any]:
        return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0, "total_held": 1, **extra}

    @pytest.mark.asyncio
    async def test_bug_repro_probe_failure_holds_batch_interrupted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # [bug-repro] AST-2016 incident shape: 2-job meteorite_grade_get, per-entity warm-then-gather, max_runs 3.
        # Pre-fix the dispatcher ignores the tag: every job is sent every run (2 × 3 = 6), ledger COMPLETED.
        edges = self._edges(monkeypatch, 2098)
        # held jobs stay eligible — only the outage stop can end the loop early
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda _t: 24)
        clear = self._claim_jobs(monkeypatch, 2, "METEORITE_PASSED_DO")
        consult = AsyncMock(return_value=self._held(failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 2098, "task_key": "meteorite_grade_get", "candidate_id": "cand-1", "entity_type": "job",
            "trigger_state": "METEORITE_PASSED_DO", "batch_call_mode": 0, "batch_size": 2, "auto_mode": 1,
            "max_runs": 3,
        }
        await dispatcher_mod._dispatch_one(task)

        # warm entity held → gather entity never sent, no second run; claim released
        assert consult.await_count == 1
        clear.assert_called_once_with("bid-2010")
        kw = edges["update_dispatch_ledger"].call_args.kwargs
        assert kw["status"] == "INTERRUPTED"
        assert (kw["total_processed"], kw["total_errors"]) == (1, 0)
        edges["breaker"].assert_not_called()
        edges["auto_run_error"].assert_not_called()
        edges["provider_balance_outage"].assert_not_called()

    @pytest.mark.asyncio
    async def test_run_unified_per_entity_skips_after_probe_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._edges(monkeypatch, 20982)
        claimed = self._claim_companies(monkeypatch, 3)
        consult = AsyncMock(return_value=self._held(failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 20982, "task_key": "select_job_page", "entity_type": "company",
            "trigger_state": "PJL_READY", "batch_call_mode": 0, "batch_size": 3,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        out = await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 1
        # held / failure_class stay off the summary — update_dispatch_ledger rejects unknown keys
        assert out == {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}
        assert ctx["provider_probe_outage"] == {"error": self._ERR, "held": 1}
        assert "provider_balance_outage" not in ctx and "provider_rate_limit_outage" not in ctx
        claimed["clear"].assert_called_once_with("bid-1867")

    @pytest.mark.asyncio
    async def test_run_unified_chunk_split_skips_tail_after_head_probe_failure(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._edges(monkeypatch, 20983)
        self._claim_jobs(monkeypatch, 3, "JD_READY")
        consult = AsyncMock(return_value=self._held(failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        task = {
            "id": 20983, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY",
            "batch_call_mode": 1, "batch_size": 1, "score_floor": 0.5,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        await dispatcher_mod._run_unified(task, ctx, False)

        # head chunk held → both tail chunks skipped
        assert consult.await_count == 1
        assert ctx["provider_probe_outage"] == {"error": self._ERR, "held": 1}

    @pytest.mark.asyncio
    async def test_run_unified_full_batch_marks_probe_outage(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._edges(monkeypatch, 20984)
        self._claim_jobs(monkeypatch, 2, "JD_READY")
        consult = AsyncMock(return_value=self._held(total_held=2, failure_class=self._FC, error=self._ERR))
        monkeypatch.setattr("src.core.consult.run_consult_task", consult)
        # batch_size ≥ claimed → one consult call for the whole batch (no chunk split)
        task = {
            "id": 20984, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY",
            "batch_call_mode": 1, "batch_size": 5, "score_floor": 0.5,
        }
        ctx: Dict[str, Any] = {"astral_candidate_id": "cand-1"}
        await dispatcher_mod._run_unified(task, ctx, False)

        assert consult.await_count == 1
        assert ctx["provider_probe_outage"] == {"error": self._ERR, "held": 2}

    @pytest.mark.asyncio
    async def test_run_dispatch_loop_stops_after_probe_outage_run(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # finite eligibility so the pre-fix loop (no outage stop) still terminates
        monkeypatch.setattr(
            dispatcher_mod.database, "count_eligible_for_dispatch_task", MagicMock(side_effect=[24, 24, 24, 0]),
        )
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())

        async def _run(task, ctx, debug):
            ctx["provider_probe_outage"] = {"error": self._ERR, "held": 1}
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}

        run_task = AsyncMock(side_effect=_run)
        monkeypatch.setattr(dispatcher_mod, "_run_task", run_task)
        # max_runs 0 = unlimited: only the outage stop (or drained eligibility) ends the loop
        task = {"id": 20985, "task_key": "meteorite_grade_get", "entity_type": "job", "auto_mode": 1, "max_runs": 0}
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        await dispatcher_mod._run_dispatch_loop(
            {"astral_candidate_id": "cand-1"}, task, "meteorite_grade_get", "bid", accumulated, "bid",
        )

        assert run_task.await_count == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("with_rate_limit", "status"), [(False, "INTERRUPTED"), (True, "FAILED")])
    async def test_dispatch_one_probe_outage_status(
        self, monkeypatch: pytest.MonkeyPatch, with_rate_limit: bool, status: str,
    ) -> None:
        edges = self._edges(monkeypatch, 20986)

        async def _loop(ctx, task, task_key, batch_id, accumulated, dispatch_ledger_id):
            ctx["provider_probe_outage"] = {"error": self._ERR, "held": 1}
            if with_rate_limit:
                ctx["provider_rate_limit_outage"] = {"error": "Error code: 429 - rate limited"}
            accumulated["total_processed"] = 1

        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock(side_effect=_loop))
        task = {"id": 20986, "task_key": "meteorite_grade_get", "candidate_id": "cand-1", "auto_mode": 1}
        await dispatcher_mod._dispatch_one(task)

        # rate limit's FAILED wins over the probe outage's INTERRUPTED
        assert edges["update_dispatch_ledger"].call_args.kwargs["status"] == status
        # no probe alert (AST-2098 Boundary); a no-op run never trips auto_run_error or the breaker
        edges["provider_balance_outage"].assert_not_called()
        edges["auto_run_error"].assert_not_called()
        edges["breaker"].assert_not_called()


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
        db.save_candidate("c802", state="NEW_CANDIDATE", candidate_data={})
        log = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "logger", log)
        run = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        accumulated = dict(dispatcher_mod._SUMMARY_ZERO)
        task = {
            "id": 802,
            "task_key": "inflow_discovery",
            "entity_type": "candidate",
            "trigger_state": "ACTIVE_SEARCH",
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
        db.save_candidate("c814", state="ACTIVE_SEARCH", candidate_data={})
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
            "trigger_state": "ACTIVE_SEARCH",
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
        _stub_scheduler_boot_provisions(monkeypatch)
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
        _stub_scheduler_boot_provisions(monkeypatch)

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
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id, **_kw: spawned.append(task_id) or True)
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
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id, **_kw: spawned.append(task_id) or True)
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
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id, **_kw: spawned.append(task_id) or False)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == [40, 41]

    def test_tick_loop_stops_when_spawn_slots_are_exhausted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = [{"id": 52}, {"id": 53}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        spawned: list[int] = []
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id, **_kw: spawned.append(task_id) or True)
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
        monkeypatch.setattr(dispatcher_mod, "run_task", lambda task_id, **_kw: spawned.append(task_id) or True)
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
        monkeypatch.setattr(
            "src.core.candidate.age_stale_candidate_states",
            MagicMock(return_value=0),
        )
        monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: [])
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

        db.save_candidate("tmpl", state="ACTIVE_SEARCH", candidate_data={})
        db.save_candidate("tgt", state="ACTIVE_SEARCH", candidate_data={})
        db.save_dispatch_task(
            "tmpl", "qualify_job_listings", min_count=2, trigger_state="NEW", auto_mode=True, batch_size=4,
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
        assert rows[0]["task_key"] == "qualify_job_listings"
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
        db.save_candidate("tmpl", state="ACTIVE_SEARCH", candidate_data={})
        with pytest.raises(LookupError, match="Candidate not found"):
            dispatcher_mod.set_candidate_dispatch_tasks_from_template("tgt")


class TestAst1259CandidatePoolClaim:
    """AST-1259: dispatcher candidate pool claim → per-entity process → clear (empty + finally)."""

    @pytest.mark.asyncio
    async def test_claim_honors_batch_size_and_claim_states(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        rows = [
            {"astral_candidate_id": "c1259a", "state": "REQUESTED_ARTIFACTS"},
            {"astral_candidate_id": "c1259b", "state": "REQUESTED_ARTIFACTS_RETRY"},
        ]
        claim = MagicMock(return_value=(batch_id, rows))
        clear = MagicMock()
        monkeypatch.setattr("src.core.candidate.get_new_candidate_batch", claim)
        monkeypatch.setattr("src.core.candidate.clear_candidate_batch", clear)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)

        async def _immediate_warm(one_fn, entities, zero):
            return [await one_fn(e) for e in entities]

        monkeypatch.setattr(dispatcher_mod, "_warm_then_gather", _immediate_warm)
        task = {
            "entity_type": "candidate",
            "trigger_state": "REQUESTED_ARTIFACTS",
            "task_key": "craft_get_rubric",
            "batch_size": 2,
            "batch_call_mode": 1,  # forced False for candidate — still per-entity
        }
        await dispatcher_mod._run_unified(task, {"astral_candidate_id": "owner"}, False)
        claim.assert_called_once()
        assert claim.call_args.args[0] == "REQUESTED_ARTIFACTS"
        assert claim.call_args.kwargs["limit"] == 2
        assert claim.call_args.kwargs["batch_id"] == batch_id
        assert claim.call_args.kwargs["states"] == cfg.dispatch_claim_states(
            "REQUESTED_ARTIFACTS", "candidate"
        )
        assert run.await_count == 2
        assert run.await_args_list[0].args[2] == [rows[0]]
        assert run.await_args_list[1].args[2] == [rows[1]]
        clear.assert_called_once_with(batch_id)

    @pytest.mark.asyncio
    async def test_empty_batch_clears_candidate_batch(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claim = MagicMock(return_value=(batch_id, []))
        clear = MagicMock()
        monkeypatch.setattr("src.core.candidate.get_new_candidate_batch", claim)
        monkeypatch.setattr("src.core.candidate.clear_candidate_batch", clear)
        run = AsyncMock()
        monkeypatch.setattr("src.core.consult.run_consult_task", run)
        clear_job = MagicMock()
        clear_co = MagicMock()
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear_job)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear_co)
        task = {
            "entity_type": "candidate",
            "trigger_state": "REQUESTED_ARTIFACTS",
            "task_key": "craft_get_rubric",
            "batch_size": 5,
        }
        out = await dispatcher_mod._run_unified(task, {"astral_candidate_id": "c"}, False)
        assert out == dispatcher_mod._SUMMARY_ZERO
        run.assert_not_awaited()
        clear.assert_called_once_with(batch_id)
        clear_job.assert_not_called()
        clear_co.assert_not_called()

    @pytest.mark.asyncio
    async def test_finally_clears_and_skips_job_company_clear(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        rows = [{"astral_candidate_id": "c1259f", "state": "REQUESTED_ARTIFACTS"}]
        claim = MagicMock(return_value=(batch_id, rows))
        clear = MagicMock()
        clear_job = MagicMock()
        clear_co = MagicMock()
        monkeypatch.setattr("src.core.candidate.get_new_candidate_batch", claim)
        monkeypatch.setattr("src.core.candidate.clear_candidate_batch", clear)
        monkeypatch.setattr("src.core.tracker.clear_job_batch", clear_job)
        monkeypatch.setattr("src.core.roster.clear_company_batch", clear_co)
        run = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        monkeypatch.setattr("src.core.consult.run_consult_task", run)

        async def _immediate_warm(one_fn, entities, zero):
            return [await one_fn(e) for e in entities]

        monkeypatch.setattr(dispatcher_mod, "_warm_then_gather", _immediate_warm)
        await dispatcher_mod._run_unified(
            {
                "entity_type": "candidate",
                "trigger_state": "REQUESTED_ARTIFACTS",
                "task_key": "craft_get_rubric",
                "batch_size": 1,
            },
            {"astral_candidate_id": "c"},
            False,
        )
        clear.assert_called_once_with(batch_id)
        clear_job.assert_not_called()
        clear_co.assert_not_called()


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "retire_candidate_requested_wrapper_dispatch_tasks"),
    reason="AST-1252 wrapper retire not on this publish tip",
)

class TestAst972CandidateStageDispatch:
    """AST-972 → AST-1252: retire wrappers; claim gate; tick aging; scheduler retire hook."""

    def test_retire_wrapper_rows_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows_by_cid = {
            "tmpl": [
                {"id": 1, "task_key": "candidate_requested_resume"},
                {"id": 2, "task_key": "craft_get_rubric"},
            ],
            "c2": [
                {"id": 3, "task_key": "candidate_requested_artifacts"},
                {"id": 4, "task_key": "meteorite_email"},
            ],
        }
        deleted: list[int] = []
        monkeypatch.setattr(dispatcher_mod, "template_candidate_id", lambda: "tmpl")
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_candidate_ids_with_dispatch_tasks",
            lambda: ["tmpl", "c2"],
        )
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks_for_candidate",
            lambda cid: list(rows_by_cid.get(cid, [])),
        )
        monkeypatch.setattr(
            dispatcher_mod,
            "delete_dispatch_task",
            lambda tid: deleted.append(int(tid)),
        )
        out = dispatcher_mod.retire_candidate_requested_wrapper_dispatch_tasks()
        assert out["retired"] == 2
        assert sorted(deleted) == [1, 3]
        assert out["candidates_scanned"] == 2

    def test_retire_requires_template_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod, "template_candidate_id", lambda: "")
        with pytest.raises(ValueError, match="template_candidate_id"):
            dispatcher_mod.retire_candidate_requested_wrapper_dispatch_tasks()

    @pytest.mark.asyncio
    async def test_run_unified_candidate_claim_gate(
        self, monkeypatch: pytest.MonkeyPatch, batch_id: str
    ) -> None:
        # AST-1259: gate is pool claim (empty → no consult; claimed row → per-entity consult).
        monkeypatch.setattr(dispatcher_mod, "check_internet_reachable", lambda: True)
        claimed = {"astral_candidate_id": "c1", "state": "REQUESTED_ARTIFACTS"}
        claim = MagicMock(side_effect=[(batch_id, []), (batch_id, [claimed])])
        clear = MagicMock()
        monkeypatch.setattr("src.core.candidate.get_new_candidate_batch", claim)
        monkeypatch.setattr("src.core.candidate.clear_candidate_batch", clear)
        run = AsyncMock(return_value=dict(dispatcher_mod._SUMMARY_ZERO))
        monkeypatch.setattr("src.core.consult.run_consult_task", run)

        async def _immediate_warm(one_fn, entities, zero):
            return [await one_fn(e) for e in entities]

        monkeypatch.setattr(dispatcher_mod, "_warm_then_gather", _immediate_warm)
        task = {
            "id": 1,
            "task_key": "craft_get_rubric",
            "trigger_state": "REQUESTED_ARTIFACTS",
            "entity_type": "candidate",
            "batch_size": 1,
            "batch_call_mode": 0,
        }
        ctx = {"astral_candidate_id": "c1", "state": "ACTIVE_SEARCH"}
        await dispatcher_mod._run_unified(task, ctx, False)
        run.assert_not_called()
        clear.assert_called_with(batch_id)
        clear.reset_mock()
        out = await dispatcher_mod._run_unified(task, ctx, False)
        assert out == dispatcher_mod._SUMMARY_ZERO
        run.assert_awaited_once()
        assert run.await_args.args[0] == "candidate"
        assert run.await_args.args[1] == "REQUESTED_ARTIFACTS"
        assert run.await_args.args[2] == [claimed]
        assert run.await_args.kwargs["dispatch_task_key"] == "craft_get_rubric"
        clear.assert_called_once_with(batch_id)

    def test_tick_loop_invokes_stale_aging(self, monkeypatch: pytest.MonkeyPatch) -> None:
        aged = MagicMock(return_value=0)
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: [])
        _run_one_tick(monkeypatch)
        monkeypatch.setattr("src.core.candidate.age_stale_candidate_states", aged)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        aged.assert_called_once_with()

    def test_start_scheduler_invokes_wrapper_retire(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dispatcher_mod._tick_thread = None
        monkeypatch.setattr(dispatcher_mod.database, "mark_stale_ledger_interrupted", MagicMock(return_value=0))
        retire = MagicMock(
            return_value={
                "template_candidate_id": "tmpl",
                "candidates_scanned": 1,
                "retired": 2,
            }
        )
        monkeypatch.setattr(dispatcher_mod, "retire_candidate_requested_wrapper_dispatch_tasks", retire)

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self.daemon = daemon

            def start(self) -> None:
                return None

            def is_alive(self) -> bool:
                return False

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        monkeypatch.setattr(
            dispatcher_mod,
            "provision_meteorite_dispatch_tasks",
            MagicMock(return_value={"template_candidate_id": "tmpl", "candidates_touched": 0}),
        )
        _stub = MagicMock(
            return_value={
                "task_key": "meteorite_email",
                "retired_null": 0,
                "candidates_touched": 0,
                "added": 0,
                "skipped": 0,
                "skipped_missing_config": 0,
            }
        )
        if hasattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks"):
            monkeypatch.setattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks", _stub)
        if hasattr(dispatcher_mod, "ensure_fetch_email_dispatch_task"):
            monkeypatch.setattr(
                dispatcher_mod,
                "ensure_fetch_email_dispatch_task",
                MagicMock(
                    return_value={
                        "task_key": "fetch_email",
                        "added": 0,
                        "skipped": 0,
                        "skipped_missing_config": 0,
                    }
                ),
            )
        dispatcher_mod.start_scheduler()
        retire.assert_called_once_with()


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "ensure_meteorite_dispatch_tasks"),
    reason="AST-1054 meteorite dispatch provision not on this publish tip",
)
class TestAst1054MeteoriteDispatchProvision:
    """AST-1054: ensure/provision meteorite GDL dispatch rows; twins skip without TASK_CONFIG."""

    def test_ensure_inserts_shared_gdl_and_twins_per_task_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        existing: list[dict] = []
        saves: list[dict] = []
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks_for_candidate",
            lambda cid: list(existing),
        )

        def _save(**kwargs):
            saves.append(kwargs)
            existing.append(
                {"task_key": kwargs["task_key"], "trigger_state": kwargs["trigger_state"], "id": len(existing) + 1}
            )

        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_task", _save)
        monkeypatch.setattr(dispatcher_mod, "delete_dispatch_task", MagicMock())
        twins_present = {"meteorite_like", "meteorite_upshot"} <= set(dispatcher_mod.TASK_CONFIG)
        qualify_present = "qualify_meteorite" in dispatcher_mod.TASK_CONFIG
        # Base GDL = 3; +qualify (AST-1060) = 4; +twins = 6.
        expect_add = (6 if twins_present else 4) if qualify_present else (5 if twins_present else 3)
        expect_missing = 0 if twins_present else 2
        first = dispatcher_mod.ensure_meteorite_dispatch_tasks("c1")
        assert first["added"] == expect_add and first["skipped_missing_config"] == expect_missing
        assert first["skipped"] == 0
        assert first.get("retired", 0) == 0
        by_key = {s["task_key"]: s for s in saves}
        # Twin GDL entry: evaluate_meteorite@METEORITE_QUALIFIED (not evaluate_jd).
        assert "evaluate_meteorite" in dispatcher_mod.TASK_CONFIG
        assert by_key["evaluate_meteorite"]["trigger_state"] == "METEORITE_QUALIFIED"
        assert by_key["evaluate_meteorite"]["score_floor"] is None
        assert "evaluate_jd" not in by_key
        assert by_key["meteorite_grade_do"]["score_floor"] == 0.0
        assert by_key["meteorite_grade_get"]["score_floor"] == 0.0
        assert by_key["meteorite_grade_do"]["trigger_state"] == "METEORITE_PASSED_JD"
        assert by_key["meteorite_grade_get"]["trigger_state"] == "METEORITE_PASSED_DO"
        assert "grade_do" not in by_key
        assert "grade_get" not in by_key
        if qualify_present:
            assert by_key["qualify_meteorite"]["trigger_state"] == "METEORITE_NEW"
            assert by_key["qualify_meteorite"]["score_floor"] is None
        if twins_present:
            assert by_key["meteorite_like"]["score_floor"] == 0.0
            assert by_key["meteorite_upshot"]["batch_size"] == 1
        else:
            assert "meteorite_like" not in by_key
        second = dispatcher_mod.ensure_meteorite_dispatch_tasks("c1")
        assert second["added"] == 0 and second["skipped"] == expect_add
        assert second["skipped_missing_config"] == expect_missing
        assert second.get("retired", 0) == 0

    def test_ensure_inserts_twins_when_task_config_present(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        existing: list[dict] = []
        saves: list[dict] = []
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks_for_candidate",
            lambda cid: list(existing),
        )

        def _save(**kwargs):
            saves.append(kwargs)
            existing.append(
                {"task_key": kwargs["task_key"], "trigger_state": kwargs["trigger_state"], "id": len(existing) + 1}
            )

        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_task", _save)
        monkeypatch.setattr(dispatcher_mod, "delete_dispatch_task", MagicMock())
        patched = dict(dispatcher_mod.TASK_CONFIG)
        patched["meteorite_like"] = {"agent_task": "meteorite_like"}
        patched["meteorite_upshot"] = {"agent_task": "meteorite_upshot"}
        monkeypatch.setattr(dispatcher_mod, "TASK_CONFIG", patched)
        out = dispatcher_mod.ensure_meteorite_dispatch_tasks("c1")
        qualify_present = "qualify_meteorite" in patched
        expect_add = 6 if qualify_present else 5
        assert out["added"] == expect_add and out["skipped_missing_config"] == 0
        by_key = {s["task_key"]: s for s in saves}
        assert by_key["meteorite_like"]["trigger_state"] == "METEORITE_PASSED_GET"
        assert by_key["meteorite_like"]["score_floor"] == 0.0
        assert by_key["meteorite_upshot"]["trigger_state"] == "METEORITE_PASSED_LIKE"
        assert by_key["meteorite_upshot"]["score_floor"] == 0.0
        assert by_key["meteorite_upshot"]["batch_size"] == 1

    def test_ensure_retires_evaluate_jd_on_meteorite_triggers_when_twin_present(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1209: delete evaluate_jd@METEORITE_* when twin present; keep evaluate_jd@JD_READY."""
        if "evaluate_meteorite" not in dispatcher_mod.TASK_CONFIG:
            pytest.skip("evaluate_meteorite twin not on this tip")
        existing = [
            {"id": 10, "task_key": "evaluate_jd", "trigger_state": "METEORITE_NEW"},
            {"id": 11, "task_key": "evaluate_jd", "trigger_state": "METEORITE_QUALIFIED"},
            {"id": 12, "task_key": "evaluate_jd", "trigger_state": "JD_READY"},
        ]
        saves: list[dict] = []
        deleted: list[int] = []
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks_for_candidate",
            lambda cid: list(existing),
        )

        def _save(**kwargs):
            saves.append(kwargs)
            existing.append(
                {
                    "id": 100 + len(saves),
                    "task_key": kwargs["task_key"],
                    "trigger_state": kwargs["trigger_state"],
                }
            )

        def _delete(row_id: int) -> None:
            deleted.append(row_id)
            existing[:] = [r for r in existing if int(r["id"]) != int(row_id)]

        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_task", _save)
        monkeypatch.setattr(dispatcher_mod, "delete_dispatch_task", _delete)
        out = dispatcher_mod.ensure_meteorite_dispatch_tasks("c1")
        assert out["retired"] == 2
        assert set(deleted) == {10, 11}
        assert any(
            s["task_key"] == "evaluate_meteorite" and s["trigger_state"] == "METEORITE_QUALIFIED"
            for s in saves
        )
        assert any(r["task_key"] == "evaluate_jd" and r["trigger_state"] == "JD_READY" for r in existing)
        assert not any(
            r["task_key"] == "evaluate_jd" and str(r["trigger_state"]).startswith("METEORITE_")
            for r in existing
        )

    def test_ensure_retires_shared_key_meteorite_do_get_when_aliases_present(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1222: drop grade_do@METEORITE_PASSED_JD / grade_get@METEORITE_PASSED_DO once aliases exist."""
        if "meteorite_grade_do" not in dispatcher_mod.TASK_CONFIG:
            pytest.skip("AST-1222 alias TASK_CONFIG not on tip")
        existing = [
            {"id": 30, "task_key": "grade_do", "trigger_state": "METEORITE_PASSED_JD"},
            {"id": 31, "task_key": "grade_get", "trigger_state": "METEORITE_PASSED_DO"},
            {"id": 32, "task_key": "grade_do", "trigger_state": "PASSED_JD"},
            {"id": 33, "task_key": "grade_get", "trigger_state": "PASSED_DO"},
        ]
        saves: list[dict] = []
        deleted: list[int] = []

        def _save(**kwargs):
            saves.append(kwargs)
            existing.append(
                {
                    "task_key": kwargs["task_key"],
                    "trigger_state": kwargs["trigger_state"],
                    "id": 100 + len(existing),
                }
            )

        def _delete(row_id: int) -> None:
            deleted.append(row_id)
            existing[:] = [r for r in existing if int(r["id"]) != int(row_id)]

        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks_for_candidate",
            lambda cid: list(existing),
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_task", _save)
        monkeypatch.setattr(dispatcher_mod, "delete_dispatch_task", _delete)
        out = dispatcher_mod.ensure_meteorite_dispatch_tasks("c1")
        assert out["retired"] >= 2
        assert set(deleted) >= {30, 31}
        assert 32 not in deleted and 33 not in deleted
        assert any(
            s["task_key"] == "meteorite_grade_do" and s["trigger_state"] == "METEORITE_PASSED_JD"
            for s in saves
        )
        assert any(
            s["task_key"] == "meteorite_grade_get" and s["trigger_state"] == "METEORITE_PASSED_DO"
            for s in saves
        )
        assert any(r["task_key"] == "grade_do" and r["trigger_state"] == "PASSED_JD" for r in existing)
        assert any(r["task_key"] == "grade_get" and r["trigger_state"] == "PASSED_DO" for r in existing)
        assert not any(
            r["task_key"] == "grade_do" and r["trigger_state"] == "METEORITE_PASSED_JD"
            for r in existing
        )

    def test_ensure_skips_retire_when_twin_absent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1209: never strip evaluate_jd@METEORITE_* if twin row cannot be inserted."""
        existing = [
            {"id": 20, "task_key": "evaluate_jd", "trigger_state": "METEORITE_QUALIFIED"},
            {"id": 21, "task_key": "evaluate_jd", "trigger_state": "JD_READY"},
        ]
        deleted: list[int] = []
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks_for_candidate",
            lambda cid: list(existing),
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_task", MagicMock())
        monkeypatch.setattr(
            dispatcher_mod,
            "delete_dispatch_task",
            lambda row_id: deleted.append(row_id),
        )
        # Drop twin from TASK_CONFIG so insert loop skips it (skipped_missing_config).
        patched = {
            k: v for k, v in dispatcher_mod.TASK_CONFIG.items() if k != "evaluate_meteorite"
        }
        monkeypatch.setattr(dispatcher_mod, "TASK_CONFIG", patched)
        out = dispatcher_mod.ensure_meteorite_dispatch_tasks("c1")
        assert out["retired"] == 0
        assert deleted == []
        assert any(
            r["task_key"] == "evaluate_jd" and r["trigger_state"] == "METEORITE_QUALIFIED"
            for r in existing
        )
        assert any(r["task_key"] == "evaluate_jd" and r["trigger_state"] == "JD_READY" for r in existing)

    def test_provision_touches_scheduled_candidates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod, "template_candidate_id", lambda: "tmpl")
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid},
        )
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_candidate_ids_with_dispatch_tasks",
            lambda: ["tmpl", "c2"],
        )
        calls: list[str] = []

        def _ensure(cid):
            calls.append(cid)
            return {
                "candidate_id": cid,
                "added": 0,
                "skipped": 3,
                "skipped_missing_config": 2,
                "retired": 0,
            }

        monkeypatch.setattr(dispatcher_mod, "ensure_meteorite_dispatch_tasks", _ensure)
        out = dispatcher_mod.provision_meteorite_dispatch_tasks()
        assert calls[0] == "tmpl"
        assert "tmpl" in calls and "c2" in calls
        assert out["candidates_touched"] == 2
        # Template ensure + loop over ["tmpl","c2"] → 3 ensures × stub 2 = 6.
        assert out["skipped_missing_config"] == 6
        assert out.get("retired", 0) == 0

    def test_start_scheduler_does_not_invoke_meteorite_provision(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """[bug-repro] AST-1500 — restart must not auto-write dispatch_task via meteorite provision."""
        dispatcher_mod._tick_thread = None
        monkeypatch.setattr(
            dispatcher_mod.database, "mark_stale_ledger_interrupted", MagicMock(return_value=0)
        )
        # start_scheduler boot order: meteorite → AST-1252 wrapper retire → gaze.
        mprovision = MagicMock(
            return_value={
                "template_candidate_id": "tmpl",
                "candidates_touched": 1,
                "added": 3,
                "skipped": 0,
                "skipped_missing_config": 2,
            }
        )
        monkeypatch.setattr(dispatcher_mod, "provision_meteorite_dispatch_tasks", mprovision)
        monkeypatch.setattr(
            dispatcher_mod,
            "retire_candidate_requested_wrapper_dispatch_tasks",
            MagicMock(
                return_value={
                    "template_candidate_id": "tmpl",
                    "candidates_scanned": 0,
                    "retired": 0,
                }
            ),
        )
        _stub = MagicMock(
            return_value={
                "task_key": "meteorite_email",
                "retired_null": 0,
                "candidates_touched": 0,
                "added": 0,
                "skipped": 0,
                "skipped_missing_config": 0,
            }
        )
        if hasattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks"):
            monkeypatch.setattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks", _stub)
        elif hasattr(dispatcher_mod, "provision_meteorite_email_dispatch_task"):
            monkeypatch.setattr(dispatcher_mod, "provision_meteorite_email_dispatch_task", _stub)
        fetch_ensure = MagicMock(
            return_value={
                "task_key": "fetch_email",
                "added": 0,
                "skipped": 0,
                "skipped_missing_config": 0,
            }
        )
        if hasattr(dispatcher_mod, "ensure_fetch_email_dispatch_task"):
            monkeypatch.setattr(dispatcher_mod, "ensure_fetch_email_dispatch_task", fetch_ensure)

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self.daemon = daemon

            def start(self) -> None:
                return None

            def is_alive(self) -> bool:
                return False

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        dispatcher_mod.start_scheduler()
        mprovision.assert_not_called()
        if hasattr(dispatcher_mod, "ensure_fetch_email_dispatch_task"):
            fetch_ensure.assert_not_called()


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks"),
    reason="AST-1466 meteorite_email provision not on this publish tip",
)
class TestAst1134MeteoriteEmailDispatchProvision:
    """AST-1134: per-candidate ensure; retire null shell; coverage over every candidate."""

    def test_ensure_adds_then_skips(self, monkeypatch: pytest.MonkeyPatch) -> None:
        existing: list[dict] = []
        saves: list[dict] = []
        tk = dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]
        # Mailbox key is intentionally absent from live TASK_CONFIG; stub it for ensure insert path.
        monkeypatch.setitem(dispatcher_mod.TASK_CONFIG, tk, {"task_key": tk})
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks_for_candidate",
            lambda cid: [r for r in existing if r.get("candidate_id") == cid],
        )

        def _save(**kwargs):
            saves.append(kwargs)
            row = {
                "id": 41,
                "task_key": kwargs["task_key"],
                "candidate_id": kwargs.get("candidate_id"),
            }
            existing.append(row)
            return 41

        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_task", _save)
        first = dispatcher_mod.ensure_meteorite_email_dispatch_task("cand-a")
        assert first["added"] == 1 and first["skipped"] == 0
        assert first["candidate_id"] == "cand-a"
        assert first["id"] == 41
        assert saves[0]["candidate_id"] == "cand-a"
        assert saves[0]["task_key"] == tk
        assert saves[0]["auto_mode"] is False
        assert saves[0]["entity_type"] is None
        assert saves[0]["trigger_state"] is None
        second = dispatcher_mod.ensure_meteorite_email_dispatch_task("cand-a")
        assert second["added"] == 0 and second["skipped"] == 1
        assert second["id"] == 41
        assert len(saves) == 1

    def test_ensure_requires_candidate_id(self) -> None:
        with pytest.raises(ValueError, match="candidate_id is required"):
            dispatcher_mod.ensure_meteorite_email_dispatch_task("")
        with pytest.raises(ValueError, match="candidate_id is required"):
            dispatcher_mod.ensure_meteorite_email_dispatch_task("   ")

    def test_ensure_skips_missing_task_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod, "TASK_CONFIG", {})
        out = dispatcher_mod.ensure_meteorite_email_dispatch_task("cand-a")
        assert out["skipped_missing_config"] == 1
        assert out["added"] == 0 and out["skipped"] == 0
        assert out["candidate_id"] == "cand-a"

    def test_provision_retires_null_and_covers_candidates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        deleted: list[int] = []
        rewritten: list[tuple[int, str]] = []
        ensured: list[str] = []
        tk = dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]
        prior = "meteorite" + "_email"
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_dispatch_tasks",
            lambda: [
                {"id": 1, "task_key": tk, "candidate_id": None},
                {"id": 2, "task_key": tk, "candidate_id": "keep"},
                {"id": 3, "task_key": "evaluate_jd", "candidate_id": None},
                {"id": 4, "task_key": prior, "candidate_id": "rewrite-me"},
                {"id": 5, "task_key": prior, "candidate_id": None},
            ],
        )
        monkeypatch.setattr(
            dispatcher_mod.database,
            "delete_dispatch_task",
            lambda tid: deleted.append(int(tid)),
        )
        monkeypatch.setattr(
            dispatcher_mod,
            "_db_update_dispatch_task",
            lambda tid, **kw: rewritten.append((int(tid), str(kw.get("task_key") or ""))),
        )
        monkeypatch.setattr(
            dispatcher_mod.database,
            "list_candidates",
            lambda: [
                {"astral_candidate_id": "c1"},
                {"astral_candidate_id": "c2"},
                {"astral_candidate_id": ""},
            ],
        )

        def _ensure(cid: str):
            ensured.append(cid)
            return {
                "candidate_id": cid,
                "task_key": tk,
                "added": 1 if cid == "c1" else 0,
                "skipped": 0 if cid == "c1" else 1,
                "skipped_missing_config": 0,
                "id": 10,
            }

        monkeypatch.setattr(dispatcher_mod, "ensure_meteorite_email_dispatch_task", _ensure)
        out = dispatcher_mod.provision_meteorite_email_dispatch_tasks()
        assert deleted == [1, 5]
        assert rewritten == [(4, tk)]
        assert ensured == ["c1", "c2"]
        assert out["retired_null"] == 2
        assert out["rewritten"] == 1
        assert out["candidates_touched"] == 2
        assert out["added"] == 1
        assert out["skipped"] == 1
        assert out["skipped_missing_config"] == 0

    def test_start_scheduler_does_not_invoke_gaze_provision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """[bug-repro] AST-1500 — restart must not auto-write dispatch_task via meteorite_email provision."""
        dispatcher_mod._tick_thread = None
        monkeypatch.setattr(
            dispatcher_mod.database, "mark_stale_ledger_interrupted", MagicMock(return_value=0)
        )
        monkeypatch.setattr(
            dispatcher_mod,
            "provision_meteorite_dispatch_tasks",
            MagicMock(return_value={"template_candidate_id": "tmpl", "candidates_touched": 0}),
        )
        monkeypatch.setattr(
            dispatcher_mod,
            "retire_candidate_requested_wrapper_dispatch_tasks",
            MagicMock(
                return_value={
                    "template_candidate_id": "tmpl",
                    "candidates_scanned": 0,
                    "retired": 0,
                }
            ),
        )
        gprovision = MagicMock(
            return_value={
                "task_key": "meteorite_email",
                "retired_null": 1,
                "candidates_touched": 2,
                "added": 1,
                "skipped": 1,
                "skipped_missing_config": 0,
            }
        )
        monkeypatch.setattr(dispatcher_mod, "provision_meteorite_email_dispatch_tasks", gprovision)
        fetch_ensure = MagicMock(
            return_value={
                "task_key": "fetch_email",
                "added": 0,
                "skipped": 0,
                "skipped_missing_config": 0,
            }
        )
        if hasattr(dispatcher_mod, "ensure_fetch_email_dispatch_task"):
            monkeypatch.setattr(dispatcher_mod, "ensure_fetch_email_dispatch_task", fetch_ensure)

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self.daemon = daemon

            def start(self) -> None:
                return None

            def is_alive(self) -> bool:
                return False

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        dispatcher_mod.start_scheduler()
        gprovision.assert_not_called()
        if hasattr(dispatcher_mod, "ensure_fetch_email_dispatch_task"):
            fetch_ensure.assert_not_called()


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "_debug_log_auto_off_stage_skips"),
    reason="AST-1022 product not on this publish tip",
)
class TestAst1022HonorAutoOffStageDispatch:
    """AST-1022 → AST-1252: stage AUTO-off Style D uses craft_get_rubric stage key."""

    def test_stage_auto_mode_false_in_config(self) -> None:
        arts = cfg.CANDIDATE_STAGE_DISPATCH["requested_artifacts"]
        assert arts["auto_mode"] is False
        assert arts["task_key"] == "craft_get_rubric"

    def test_debug_log_auto_off_stage_skips_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            {
                "id": 1,
                "task_key": "craft_get_rubric",
                "auto_mode": 0,
                "debug": 1,
                "entity_type": "candidate",
                "trigger_state": "REQUESTED_ARTIFACTS",
                "candidate_id": "c1",
                "min_count": 1,
            },
            {
                "id": 3,
                "task_key": "evaluate_jd",
                "auto_mode": 0,
                "debug": 1,
                "entity_type": "job",
                "trigger_state": "JD_READY",
                "candidate_id": "c1",
                "min_count": 1,
            },
            {
                "id": 6,
                "task_key": "candidate_requested_artifacts",
                "auto_mode": 0,
                "debug": 1,
                "entity_type": "candidate",
                "trigger_state": "REQUESTED_ARTIFACTS",
                "candidate_id": "c4",
                "min_count": 1,
            },
        ]
        monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "count_eligible_for_dispatch_task",
            lambda task: 1,
        )
        log = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "logger", log)
        run = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "run_task", run)
        dispatcher_mod._debug_log_auto_off_stage_skips()
        run.assert_not_called()
        log.set_debug_flag.assert_called_once_with(True)
        assert log.debug_index.call_count == 1
        assert log.debug_index.call_args.kwargs["identifier"] == "craft_get_rubric"

    def test_debug_log_skips_when_below_min_count(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            {
                "id": 9,
                "task_key": "craft_get_rubric",
                "auto_mode": 0,
                "debug": 1,
                "entity_type": "candidate",
                "trigger_state": "REQUESTED_ARTIFACTS",
                "candidate_id": "c1",
                "min_count": 2,
            },
        ]
        monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "count_eligible_for_dispatch_task",
            lambda task: 1,
        )
        log = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "logger", log)
        dispatcher_mod._debug_log_auto_off_stage_skips()
        log.set_debug_flag.assert_not_called()

    def test_tick_loop_calls_auto_off_debug_helper_before_spawn(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        due = [{"id": 20}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        order: list[str] = []

        def _dbg() -> None:
            order.append("debug")

        def _run(task_id: int, **_kw: object) -> bool:
            order.append(f"run:{task_id}")
            return True

        monkeypatch.setattr(dispatcher_mod, "_debug_log_auto_off_stage_skips", _dbg)
        monkeypatch.setattr(dispatcher_mod, "run_task", _run)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert order == ["debug", "run:20"]


# Branches: qualify_meteorite in chunk-exhaust set with listing qualify (AST-1062).
class TestAst1062QualifyMeteoriteChunkExhaust:
    def test_chunk_exhaust_includes_qualify_meteorite(self) -> None:
        import pytest
        from src.core import dispatcher as dispatcher_mod

        keys = dispatcher_mod._CHUNK_EXHAUST_CONSULT_JOB_KEYS
        assert "qualify_job_listings" in keys
        if "qualify_meteorite" not in keys:
            pytest.skip("AST-1062 qualify_meteorite chunk-exhaust not on this tip")
        assert "qualify_meteorite" in keys


@pytest.mark.skipif(
    "meteorite_grade_do" not in getattr(cfg, "TASK_CONFIG", {}),
    reason="AST-1221 alias exhaust keys not on this publish tip",
)
class TestAst1221AliasChunkExhaust:
    """AST-1221: meteorite_grade_do/get join chunk-exhaust consult set."""

    def test_chunk_exhaust_includes_meteorite_grade_aliases(self) -> None:
        from src.core import dispatcher as dispatcher_mod

        keys = dispatcher_mod._CHUNK_EXHAUST_CONSULT_JOB_KEYS
        assert "grade_do" in keys and "grade_get" in keys
        assert "meteorite_grade_do" in keys
        assert "meteorite_grade_get" in keys


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "METEORITE_EMAIL_MAILBOX_CONFIG"),
    reason="AST-1466 meteorite_email wiring not on this publish tip",
)
class TestAst1090GazeEmailDispatchOne:
    """AST-1090 / AST-1134 / AST-1467: _dispatch_one routes meteorite_email; ledger uses bound row cid."""

    @pytest.mark.asyncio
    async def test_calls_runner_with_bound_ledger_cid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.core import inbox as inbox_mod

        get_cand = MagicMock(side_effect=AssertionError("must not load candidate"))
        monkeypatch.setattr(dispatcher_mod.database, "get_candidate", get_cand)
        runner = AsyncMock(
            return_value={
                "total_processed": 2,
                "total_passed": 2,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(inbox_mod, "check_email", runner)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        upd = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", upd)
        loop = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", loop)
        task = {
            "id": 90,
            "task_key": dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"],
            "candidate_id": "cand-bound",
            "auto_mode": 1,
            "debug": 0,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[90] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        runner.assert_awaited_once()
        loop.assert_not_called()
        get_cand.assert_not_called()
        assert upd.called
        assert save_ledger.called
        # save_dispatch_ledger(batch_id, task_key, candidate_id, …) — bound row cid.
        assert save_ledger.call_args.args[2] == "cand-bound"

    @pytest.mark.asyncio
    async def test_skips_unbound_candidate_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import inbox as inbox_mod

        runner = AsyncMock()
        monkeypatch.setattr(inbox_mod, "check_email", runner)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        task = {
            "id": 91,
            "task_key": dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"],
            "candidate_id": None,
            "auto_mode": 0,
            "debug": 0,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[91] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        runner.assert_not_awaited()
        save_ledger.assert_not_called()


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "_is_meteorite_ingress_transition_task_key"),
    reason="AST-1560 meteorite ingress dispatch branch not on this publish tip",
)
class TestAst1560IngressTransitionDispatchOne:
    """AST-1560 / AST-1774: _dispatch_one routes stage/scrape/check_unique/land transition runners."""

    @pytest.mark.asyncio
    async def test_routes_stage_runner_with_entity_batch_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.core import meteorite as meteorite_mod

        monkeypatch.setattr(meteorite_mod, "run_stage_meteorite", AsyncMock())
        monkeypatch.setattr(meteorite_mod, "run_scrape_meteorite", AsyncMock())
        monkeypatch.setattr(meteorite_mod, "run_land_meteorite", AsyncMock())
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        loop = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", loop)
        tk = dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG["stage_task_key"]
        task = {
            "id": 1560,
            "task_key": tk,
            "candidate_id": None,
            "auto_mode": 1,
            "debug": 0,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[1560] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        # Tip: ingress custom branch mints entity_batch_id then drives via _run_dispatch_loop.
        loop.assert_awaited_once()
        assert task["entity_batch_id"].startswith(f"{tk}-")
        save_ledger.assert_called_once()
        assert save_ledger.call_args.args[1] == tk

    @pytest.mark.asyncio
    async def test_click_loops_to_max_runs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import meteorite as meteorite_mod

        runner = AsyncMock(
            return_value={
                "total_processed": 1,
                "total_passed": 1,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(meteorite_mod, "run_land_meteorite", runner)
        monkeypatch.setattr(meteorite_mod, "run_scrape_meteorite", AsyncMock())
        monkeypatch.setattr(meteorite_mod, "run_stage_meteorite", AsyncMock())
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 5)
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        tk = dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"]
        task = {
            "id": 15602,
            "task_key": tk,
            "candidate_id": "somerset",
            "auto_mode": 0,
            "debug": 0,
            "max_runs": 2,
            "_ui_initiated": True,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[15602] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        assert runner.await_count == 2

    @pytest.mark.asyncio
    async def test_routes_check_unique_runner_with_entity_batch_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1774: check_unique_meteorite joins the ingress transition branch."""
        if "check_unique_task_key" not in dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG:
            pytest.skip("AST-1773 check_unique_task_key not on this tip")

        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        loop = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", loop)
        tk = dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"]
        assert dispatcher_mod._is_meteorite_ingress_transition_task_key(tk)
        assert (
            dispatcher_mod._meteorite_ingress_runner(tk).__name__
            == "run_check_unique_meteorite"
        )
        task = {
            "id": 1774,
            "task_key": tk,
            "candidate_id": None,
            "auto_mode": 1,
            "debug": 0,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[1774] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        loop.assert_awaited_once()
        assert task["entity_batch_id"].startswith(f"{tk}-")
        save_ledger.assert_called_once()
        assert save_ledger.call_args.args[1] == tk

    def test_ensure_ingress_includes_check_unique(self, sqlite_in_memory) -> None:
        """AST-1774: provision inserts check_unique twin beside stage/scrape/land."""
        if "check_unique_task_key" not in dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG:
            pytest.skip("AST-1773 check_unique_task_key not on this tip")
        if not hasattr(dispatcher_mod, "ensure_meteorite_ingress_dispatch_tasks"):
            pytest.skip("ensure_meteorite_ingress_dispatch_tasks not on this tip")
        db = sqlite_in_memory
        cid = "cand-cu-prov"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "P"})
        stats = dispatcher_mod.ensure_meteorite_ingress_dispatch_tasks(cid)
        assert stats["added"] >= 1
        rows = db.list_dispatch_tasks_for_candidate(cid)
        by_key = {(r.get("task_key") or "").strip(): r for r in rows}
        ingress = dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG
        assert ingress["check_unique_task_key"] in by_key
        assert by_key[ingress["check_unique_task_key"]]["trigger_state"] == (
            ingress["check_unique_trigger_state"]
        )


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "_is_meteorite_bot_blocked_notify_task_key"),
    reason="AST-1561 bot_blocked notify dispatch branch not on this publish tip",
)
class TestAst1561BotBlockedNotifyDispatchOne:
    """AST-1561: _dispatch_one routes notify runner with entity_batch_id."""

    @pytest.mark.asyncio
    async def test_routes_notify_runner_with_entity_batch_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.core import meteorite as meteorite_mod

        runner = AsyncMock(
            return_value={
                "total_processed": 1,
                "total_passed": 1,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(meteorite_mod, "run_notify_meteorite_bot_blocked", runner)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        loop = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", loop)
        tk = dispatcher_mod.METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["task_key"]
        task = {
            "id": 1561,
            "task_key": tk,
            "candidate_id": None,
            "auto_mode": 1,
            "debug": 0,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[1561] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        runner.assert_awaited_once()
        assert runner.await_args.args[0]["entity_batch_id"].startswith(f"{tk}-")
        loop.assert_not_called()
        save_ledger.assert_called_once()
        assert save_ledger.call_args.args[1] == tk


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "_is_meteorite_retention_task_key"),
    reason="AST-1562 retention dispatch branch not on this publish tip",
)
class TestAst1562RetentionDispatchOne:
    """AST-1562: _dispatch_one routes retention runner with entity_batch_id."""

    @pytest.mark.asyncio
    async def test_routes_retention_runner_with_entity_batch_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.core import meteorite as meteorite_mod

        runner = AsyncMock(
            return_value={
                "total_processed": 2,
                "total_passed": 2,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(meteorite_mod, "run_meteorite_retention", runner)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        loop = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", loop)
        tk = dispatcher_mod.METEORITE_RETENTION_CONFIG["task_key"]
        task = {
            "id": 1562,
            "task_key": tk,
            "candidate_id": None,
            "auto_mode": 1,
            "debug": 0,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[1562] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        runner.assert_awaited_once()
        assert runner.await_args.args[0]["entity_batch_id"].startswith(f"{tk}-")
        loop.assert_not_called()
        save_ledger.assert_called_once()
        assert save_ledger.call_args.args[1] == tk


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "_meteorite_email_due_tasks"),
    reason="AST-1135 gaze due merge not on this publish tip",
)
class TestAst1135GazeEmailDueTasks:
    """AST-1135: AUTO gaze due from live bind Avail + freq gate."""

    def test_due_when_avail_and_freq_allow(self, monkeypatch: pytest.MonkeyPatch) -> None:
        tk = dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]
        rows = [
            {
                "id": 1,
                "task_key": tk,
                "candidate_id": "A",
                "auto_mode": 1,
                "min_count": 1,
                "freq_hrs": 0,
            },
            {
                "id": 2,
                "task_key": tk,
                "candidate_id": "B",
                "auto_mode": 1,
                "min_count": 2,
                "freq_hrs": 0,
            },
            {
                "id": 3,
                "task_key": tk,
                "candidate_id": "C",
                "auto_mode": 0,
                "min_count": 1,
                "freq_hrs": 0,
            },
            {
                "id": 4,
                "task_key": "evaluate_jd",
                "candidate_id": "A",
                "auto_mode": 1,
                "min_count": 1,
            },
        ]
        monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(
            "src.core.inbox.count_inbox_bound_by_candidate",
            lambda **kwargs: {"A": 3, "B": 1},
        )
        monkeypatch.setattr(dispatcher_mod.database, "dispatch_task_freq_allows", lambda t: True)
        due = dispatcher_mod._meteorite_email_due_tasks()
        assert [t["id"] for t in due] == [1]
        assert due[0]["available_count"] == 3

    def test_freq_blocks_and_inbox_error_returns_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        tk = dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]
        rows = [
            {
                "id": 7,
                "task_key": tk,
                "candidate_id": "A",
                "auto_mode": 1,
                "min_count": 1,
                "freq_hrs": 24,
            }
        ]
        monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(
            "src.core.inbox.count_inbox_bound_by_candidate",
            lambda **kwargs: {"A": 5},
        )
        monkeypatch.setattr(dispatcher_mod.database, "dispatch_task_freq_allows", lambda t: False)
        assert dispatcher_mod._meteorite_email_due_tasks() == []

        monkeypatch.setattr(
            "src.core.inbox.count_inbox_bound_by_candidate",
            MagicMock(side_effect=RuntimeError("gmail down")),
        )
        monkeypatch.setattr(dispatcher_mod.database, "dispatch_task_freq_allows", lambda t: True)
        assert dispatcher_mod._meteorite_email_due_tasks() == []

    def test_run_task_enriches_gaze_available_count(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        tk = dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]
        task = {
            "id": 55,
            "task_key": tk,
            "candidate_id": "cand-x",
            "entity_type": None,
            "trigger_state": None,
            "auto_mode": 0,
            "debug": 0,
        }
        monkeypatch.setattr(dispatcher_mod.database, "get_dispatch_task", lambda tid: dict(task))
        monkeypatch.setattr(
            "src.core.inbox.count_inbox_messages_bound_to_candidate",
            lambda cid, **kwargs: 4 if cid == "cand-x" else 0,
        )
        captured: list[dict] = []

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                captured.append(args[1] if len(args) > 1 else {})

            def start(self) -> None:
                return None

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        assert dispatcher_mod.run_task(55, ui_initiated=True) is True
        assert captured[0]["available_count"] == 4


@pytest.mark.skipif(
    not hasattr(dispatcher_mod, "correct_meteorite_ingress_dispatch_entity_types"),
    reason="AST-1623 meteorite entity_type correction not on this publish tip",
)
class TestAst1623MeteoriteLedgerAndBackfill:
    """AST-1623: ingress/notify ledger entity_type=meteorite + NULL→meteorite correction."""

    @pytest.mark.asyncio
    async def test_ingress_ledger_entity_type_meteorite(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import meteorite as meteorite_mod

        runner = AsyncMock(
            return_value={
                "total_processed": 1,
                "total_passed": 1,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(meteorite_mod, "run_stage_meteorite", runner)
        monkeypatch.setattr(meteorite_mod, "run_scrape_meteorite", AsyncMock())
        monkeypatch.setattr(meteorite_mod, "run_land_meteorite", AsyncMock())
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock())
        tk = dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG["stage_task_key"]
        task = {"id": 1623, "task_key": tk, "candidate_id": None, "auto_mode": 1, "debug": 0}
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[1623] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        assert save_ledger.call_args.kwargs.get("entity_type") == "meteorite"

    @pytest.mark.asyncio
    async def test_notify_ledger_entity_type_meteorite(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import meteorite as meteorite_mod

        runner = AsyncMock(
            return_value={
                "total_processed": 1,
                "total_passed": 1,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(meteorite_mod, "run_notify_meteorite_bot_blocked", runner)
        save_ledger = MagicMock()
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", save_ledger)
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_run_dispatch_loop", AsyncMock())
        tk = dispatcher_mod.METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["task_key"]
        task = {"id": 16231, "task_key": tk, "candidate_id": None, "auto_mode": 1, "debug": 0}
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[16231] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        assert save_ledger.call_args.kwargs.get("entity_type") == "meteorite"

    def test_correct_null_entity_type_ingress_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ingress = dispatcher_mod.METEORITE_INGRESS_DISPATCH_CONFIG
        notify_tk = dispatcher_mod.METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["task_key"]
        rows = [
            {"id": 1, "task_key": ingress["stage_task_key"], "entity_type": None},
            {"id": 2, "task_key": ingress["scrape_task_key"], "entity_type": ""},
            {"id": 3, "task_key": ingress["land_task_key"], "entity_type": "meteorite"},
            {"id": 4, "task_key": notify_tk, "entity_type": None},
            {"id": 5, "task_key": "meteorite_retention", "entity_type": None},
            {"id": 6, "task_key": "grade_do", "entity_type": None},
        ]
        monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: rows)
        updates: list[tuple[int, dict]] = []

        def _upd(tid: int, **kwargs):
            updates.append((int(tid), dict(kwargs)))

        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", _upd)
        out = dispatcher_mod.correct_meteorite_ingress_dispatch_entity_types()
        assert out["scanned"] == 6
        assert out["updated"] == 3
        assert sorted(updates) == [
            (1, {"entity_type": "meteorite"}),
            (2, {"entity_type": "meteorite"}),
            (4, {"entity_type": "meteorite"}),
        ]
        # Second call: already-corrected rows are no-ops.
        rows[0]["entity_type"] = "meteorite"
        rows[1]["entity_type"] = "meteorite"
        rows[3]["entity_type"] = "meteorite"
        updates.clear()
        out2 = dispatcher_mod.correct_meteorite_ingress_dispatch_entity_types()
        assert out2["updated"] == 0
        assert updates == []

    def test_start_scheduler_invokes_entity_type_correction(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dispatcher_mod._tick_thread = None
        monkeypatch.setattr(dispatcher_mod.database, "mark_stale_ledger_interrupted", MagicMock(return_value=0))
        _stub_scheduler_boot_provisions(monkeypatch)
        corr = MagicMock(return_value={"scanned": 2, "updated": 1, "task_keys": ["stage_meteorite"]})
        monkeypatch.setattr(dispatcher_mod, "correct_meteorite_ingress_dispatch_entity_types", corr)

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                self.daemon = daemon

            def start(self) -> None:
                return None

            def is_alive(self) -> bool:
                return False

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        dispatcher_mod.start_scheduler()
        corr.assert_called_once_with()


# Branches: mailbox sweep-due mark / sweep-not-due skip / freq gate on sweep / normal row unmarked;
# tick passes _scheduled_sweep to run_task + logs sweep-due (marked vs unmarked);
# run_task stores the flag; _run_dispatch_loop one batch min 1 for flagged AUTO; debug forcing UI-only.
@pytest.mark.skipif(
    not hasattr(dispatcher_mod.database, "dispatch_task_sweep_due"),
    reason="AST-1829 scheduled sweep not on this publish tip",
)
class TestAst1829ScheduledSweep:
    """AST-1829: sweep_hrs scheduled sweep — mailbox due, tick spawn flag, one-batch loop."""

    @staticmethod
    def _ago(hours: float) -> str:
        from datetime import datetime, timedelta, timezone

        return (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

    def _mailbox_rows(self, **overrides: Any) -> List[Dict[str, Any]]:
        tk = dispatcher_mod.METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]
        row = {
            "id": 1829,
            "task_key": tk,
            "candidate_id": "A",
            "auto_mode": 1,
            "min_count": 5,
            "freq_hrs": 0,
            "sweep_hrs": 1,
            "last_run_at": self._ago(2),
        }
        row.update(overrides)
        return [row]

    def _mailbox_due(self, monkeypatch: pytest.MonkeyPatch, rows, bound, freq_ok: bool = True):
        monkeypatch.setattr(dispatcher_mod.database, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr("src.core.inbox.count_inbox_bound_by_candidate", lambda **kwargs: bound)
        monkeypatch.setattr(dispatcher_mod.database, "dispatch_task_freq_allows", lambda t: freq_ok)
        # sweep-due helper is real (row data only, no DB)
        return dispatcher_mod._meteorite_email_due_tasks()

    # AC 9: bound Avail 2 < min_count 5, sweep due, freq allows → due, marked sweep
    def test_mailbox_sweep_due_marked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = self._mailbox_due(monkeypatch, self._mailbox_rows(), {"A": 2})
        assert [t["id"] for t in due] == [1829]
        assert due[0]["_scheduled_sweep"] is True
        assert due[0]["available_count"] == 2

    # AC 9: freq_allows false gates the sweep branch too
    def test_mailbox_sweep_blocked_by_freq(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert self._mailbox_due(monkeypatch, self._mailbox_rows(), {"A": 2}, freq_ok=False) == []

    # AC 3 / 4 / 5 on the mailbox path: inside interval, no interval, zero Avail → not due
    @pytest.mark.parametrize(
        "overrides,bound",
        [
            ({"last_run_at": "RECENT"}, {"A": 2}),
            ({"sweep_hrs": None}, {"A": 2}),
            ({"sweep_hrs": 0}, {"A": 2}),
            ({}, {}),
        ],
        ids=["inside_interval", "sweep_null", "sweep_zero", "zero_avail"],
    )
    def test_mailbox_sweep_not_due(self, monkeypatch: pytest.MonkeyPatch, overrides, bound) -> None:
        if overrides.get("last_run_at") == "RECENT":
            overrides = {"last_run_at": self._ago(10 / 60)}
        assert self._mailbox_due(monkeypatch, self._mailbox_rows(**overrides), bound) == []

    # AC 7 on the mailbox path: Avail >= min_count → due, not marked
    def test_mailbox_full_batch_unmarked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = self._mailbox_due(monkeypatch, self._mailbox_rows(), {"A": 5})
        assert [t["id"] for t in due] == [1829]
        assert not due[0].get("_scheduled_sweep")

    # Tick: marked row spawns with scheduled_sweep=True and logs once; unmarked row spawns False
    def test_tick_passes_sweep_flag_and_logs_sweep_due(self, monkeypatch: pytest.MonkeyPatch) -> None:
        due = [{"id": 60, "_scheduled_sweep": True, "task_key": "evaluate_jd"}, {"id": 61}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        calls: list[tuple] = []
        monkeypatch.setattr(
            dispatcher_mod,
            "run_task",
            lambda task_id, **kw: calls.append((task_id, kw)) or True,
        )
        log = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "logger", log)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert calls == [(60, {"scheduled_sweep": True}), (61, {"scheduled_sweep": False})]
        sweep_lines = [c for c in log.debug.call_args_list if str(c.args[0]).startswith("sweep due")]
        assert len(sweep_lines) == 1
        assert sweep_lines[0].args[1] == 60

    # run_task: flag lands on the thread's task dict (row is re-read, so it must be passed in)
    @pytest.mark.parametrize("flag", [True, False])
    def test_run_task_stores_scheduled_sweep(self, monkeypatch: pytest.MonkeyPatch, flag: bool) -> None:
        captured: list[dict] = []

        class _Thread:
            def __init__(self, target=None, args=(), kwargs=None, daemon=False, name=None):
                captured.append(args[1])

            def start(self) -> None:
                return None

        monkeypatch.setattr(dispatcher_mod.threading, "Thread", _Thread)
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_dispatch_task",
            lambda task_id: {"id": task_id, "task_key": "evaluate_jd", "candidate_id": "cand-1"},
        )
        kwargs = {"scheduled_sweep": True} if flag else {}
        assert dispatcher_mod.run_task(1829, **kwargs) is True
        assert captured[0]["_scheduled_sweep"] is flag
        assert captured[0]["_ui_initiated"] is False

    # AC 7: normal AUTO row below min_count (no sweep flag) still skips
    @pytest.mark.asyncio
    async def test_loop_unflagged_auto_below_min_skips(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 3)
        run = AsyncMock()
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        task = {"id": 1829, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY",
                "auto_mode": 1, "min_count": 10, "max_runs": 0, "_scheduled_sweep": False}
        await dispatcher_mod._run_dispatch_loop({}, task, "evaluate_jd", "b", dict(dispatcher_mod._SUMMARY_ZERO), None)
        run.assert_not_awaited()

    # AC 8 + AC 10: tick-spawned sweep (Avail 3 < min 10, max_runs 0) → exactly one batch,
    # last_run_at stamped, log_debug stays False on a local deploy; ui_initiated contrast forces True.
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "flag_key,expect_debug",
        [("_scheduled_sweep", False), ("_ui_initiated", True)],
        ids=["scheduled_sweep", "ui_sweep_contrast"],
    )
    async def test_sweep_one_batch_no_min_gate_and_debug(
        self, monkeypatch: pytest.MonkeyPatch, flag_key: str, expect_debug: bool
    ) -> None:
        monkeypatch.setattr(
            dispatcher_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_keys": {"anthropic": "key"}},
        )
        monkeypatch.setattr(dispatcher_mod.database, "save_dispatch_ledger", MagicMock(return_value=1829))
        monkeypatch.setattr(dispatcher_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(dispatcher_mod, "flush_log_buffer", MagicMock())
        monkeypatch.setattr(dispatcher_mod, "_check_circuit_breaker", MagicMock())
        stamp = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "_db_update_dispatch_task", stamp)
        monkeypatch.setattr(dispatcher_mod, "is_local_deploy_env", lambda: True)
        monkeypatch.setattr(dispatcher_mod.database, "count_eligible_for_dispatch_task", lambda task: 3)
        seen_debug: list[bool] = []

        async def _one_batch(*args: Any, **kwargs: Any) -> Dict[str, int]:
            seen_debug.append(bool(dispatcher_mod.log_debug.get()))
            return {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}

        run = AsyncMock(side_effect=_one_batch)
        monkeypatch.setattr(dispatcher_mod, "_run_task", run)
        task = {
            "id": 1829, "task_key": "evaluate_jd", "entity_type": "job", "trigger_state": "JD_READY",
            "candidate_id": "cand-1", "auto_mode": 1, "min_count": 10, "max_runs": 0, "debug": 0,
            flag_key: True,
        }
        with dispatcher_mod._registry_lock:
            dispatcher_mod._task_registry[1829] = {"asyncio_task": None}
        await dispatcher_mod._dispatch_one(task)
        assert run.await_count == 1
        assert seen_debug == [expect_debug]
        assert any("last_run_at" in c.kwargs for c in stamp.call_args_list)


# Branches: get_auto_thread_cap override set / unset; set_auto_thread_cap type reject / range reject / accept;
# _tick_loop slot math reads the live cap every tick (raise between ticks, lower below running count).
class TestAst1916AutoThreadCap:
    """AST-1916: runtime AUTO-thread cap — bounded setter, live read in _tick_loop, never cancels."""

    @pytest.fixture(autouse=True)
    def _reset_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # monkeypatch restores the module global at teardown even after set_auto_thread_cap writes it,
        # so no override leaks into the cfg["max_auto_threads"]-driven TestScheduler tick tests.
        monkeypatch.setattr(dispatcher_mod, "_auto_thread_cap_override", None)

    @staticmethod
    def _registering_run_task(monkeypatch: pytest.MonkeyPatch) -> List[int]:
        # Spawned ids land in the registry as AUTO so the next tick counts them as running.
        spawned: List[int] = []

        def _run(task_id: int, **_kw: Any) -> bool:
            spawned.append(task_id)
            with dispatcher_mod._registry_lock:
                dispatcher_mod._task_registry[task_id] = {"is_auto": True}
            return True

        monkeypatch.setattr(dispatcher_mod, "run_task", _run)
        return spawned

    def test_getter_falls_back_to_config_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(dispatcher_mod.ASTRAL_CONFIG, "max_auto_threads", 5)
        assert dispatcher_mod.get_auto_thread_cap() == 5

    @pytest.mark.parametrize("value", [1, 7, 100], ids=["min", "mid", "max"])
    def test_setter_accepts_in_range_and_getter_reports_it(self, value: int) -> None:
        assert dispatcher_mod.set_auto_thread_cap(value) == value
        assert dispatcher_mod.get_auto_thread_cap() == value

    # bool is an int subclass and 5.0 / "5" are numeric — the strict type() check must reject them all.
    @pytest.mark.parametrize(
        "value",
        [0, 101, -1, "abc", 2.5, True, None, "5", 5.0],
        ids=["zero", "over_max", "negative", "str", "float", "bool", "none", "numeric_str", "whole_float"],
    )
    def test_setter_rejects_and_keeps_prior_cap(self, value: Any) -> None:
        dispatcher_mod.set_auto_thread_cap(7)
        with pytest.raises(ValueError, match="whole number between 1 and 100"):
            dispatcher_mod.set_auto_thread_cap(value)
        assert dispatcher_mod.get_auto_thread_cap() == 7

    def test_setter_bounds_come_from_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 8: moving the config bounds moves the accepted range (nothing hardcoded in the setter).
        monkeypatch.setitem(dispatcher_mod.ASTRAL_CONFIG, "max_auto_threads_min", 2)
        monkeypatch.setitem(dispatcher_mod.ASTRAL_CONFIG, "max_auto_threads_max", 4)
        with pytest.raises(ValueError, match="between 2 and 4"):
            dispatcher_mod.set_auto_thread_cap(1)
        with pytest.raises(ValueError, match="between 2 and 4"):
            dispatcher_mod.set_auto_thread_cap(5)
        assert dispatcher_mod.set_auto_thread_cap(4) == 4

    def test_tick_honours_raised_cap_on_next_tick(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 5 / 6: cap 1 on tick 1, raised to 3 during the sleep → tick 2 fills to 3, no restart.
        due = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: due)
        monkeypatch.setattr(dispatcher_mod, "_meteorite_email_due_tasks", lambda: [])
        spawned = self._registering_run_task(monkeypatch)
        _run_one_tick(monkeypatch)
        dispatcher_mod.set_auto_thread_cap(1)
        waits: List[int] = []

        def _raise_cap_then_stop(timeout: object = None) -> None:
            waits.append(1)
            if len(waits) == 1:
                dispatcher_mod.set_auto_thread_cap(3)
                return
            raise StopIteration

        monkeypatch.setattr(dispatcher_mod._tick_event, "wait", _raise_cap_then_stop)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == [1, 2, 3]

    def test_lowering_below_running_spawns_none_and_cancels_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 7: 3 AUTO running, cap lowered to 1 → no spawn, registry untouched, nothing cancelled.
        monkeypatch.setattr(dispatcher_mod.database, "get_due_tasks", lambda: [{"id": 9}])
        monkeypatch.setattr(dispatcher_mod, "_meteorite_email_due_tasks", lambda: [])
        with dispatcher_mod._registry_lock:
            for tid in (1, 2, 3):
                dispatcher_mod._task_registry[tid] = {"is_auto": True}
        cancel = MagicMock()
        monkeypatch.setattr(dispatcher_mod, "cancel_task", cancel)
        monkeypatch.setattr(dispatcher_mod, "cancel_all_tasks", cancel)
        spawned = self._registering_run_task(monkeypatch)
        dispatcher_mod.set_auto_thread_cap(1)
        _run_one_tick(monkeypatch)
        with pytest.raises(StopIteration):
            dispatcher_mod._tick_loop()
        assert spawned == []
        assert sorted(dispatcher_mod._task_registry) == [1, 2, 3]
        cancel.assert_not_called()
