# AST-1603: Agent + tracker land via TASK_CONFIG.artifact_key

**Linear:** [AST-1603](https://linear.app/astralcareermatch/issue/AST-1603)
**Parent:** [AST-1601](https://linear.app/astralcareermatch/issue/AST-1601) — Rip out job-specific artifact pin helpers; match candidate catalog pattern
**Publish ref:** `sub/AST-1601/AST-1603-agent-tracker-land-via-task-config-artifact-key`

After [AST-1602](https://linear.app/astralcareermatch/issue/AST-1602) (config authority on `TASK_CONFIG.artifact_key`), rewire `do_task` finalize land to read that key and call `save_job_artifact`; drop the deleted `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` import/branch; privatize the job-only replica-prepare helper; strip `job_resume` / `cover_letter` from pin-key vocabulary. Keep `proposed_answers` pin resolve and generic catalog write/current-read. Does not touch config registration, does not catalog `proposed_answers`.

## Explicit scope gate

Ticket **## Scope** names only `src/core/agent.py` and `src/core/tracker.py`. Every Files Changed row and every Stage step stays inside those two files. No `config.py` edits (sibling #1 owns that). No coat-check. No new body-validation gates. No cataloging of `proposed_answers` / `notes` / `resume_content` / `application_responses`. No new type-specific public save for `job_resume` / `cover_letter`.

**Prerequisite:** `sync-child.sh` with `--ftr AST-1601-rip-job-artifact-pin-helpers-match-candidate` already carries AST-1602 — `TASK_CONFIG["finalize_job_resume"]["artifact_key"]` / `finalize_cover_letter` set, `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` gone from `config.py`. If that symbol still exists at build start, stop and comment on the parent — do not re-implement config work here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Privatize `prepare_job_replica_body` → `_prepare_job_replica_body`; shrink `_JOB_ARTIFACT_PIN_KEYS` to `proposed_answers` only; hydrate pin-resolve loop follows | core |
| `src/core/agent.py` | Remove `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` import/branch; land via `TASK_CONFIG` `artifact_key` → `_prepare_job_replica_body` + `save_job_artifact`; keep pin + draft-notes + candidate-craft paths | core |

## Stages

## Stage 1: Tracker — privatize prepare; strip catalog keys from pin vocabulary

**Done when:** `prepare_job_replica_body` is no longer a public name (only `_prepare_job_replica_body`); `_JOB_ARTIFACT_PIN_KEYS` is exactly `("proposed_answers",)`; hydrate still overlays `job_resume` / `cover_letter` from `get_job_current` and still pin-resolves `proposed_answers`; `save_job_artifact` / `get_job_current` / `pin_job_artifact_agent_data_id` unchanged.

1. In `src/core/tracker.py`, rename `prepare_job_replica_body` → `_prepare_job_replica_body` (same signature and body). Keep it among helpers below the public catalog write/read / pin APIs. Update the docstring to: private helper that unwraps a finalize hop payload for a job catalog key; returns `None` if no landable body (AST-1592 / AST-1603).
2. After the rename, `src/core/tracker.py` must not define or re-export a public `prepare_job_replica_body` (no alias). `src/core/agent.py` may still import the old public name until Stage 2 — land Stage 2 in the same build session immediately after so the broken import window is one commit only.
3. Change `_JOB_ARTIFACT_PIN_KEYS = ("job_resume", "cover_letter", "proposed_answers")` to:
   ```python
   _JOB_ARTIFACT_PIN_KEYS = ("proposed_answers",)
   ```
4. In `hydrate_job_artifacts_for_display`, keep the `get_job_current` overlay for `job.artifacts.job_resume` / `job.artifacts.cover_letter` unchanged. Simplify the pin-resolve loop: delete the `if key in ("job_resume", "cover_letter"): continue` branch (those keys are no longer in `_JOB_ARTIFACT_PIN_KEYS`). Loop body for `proposed_answers` stays: string pin → `resolve_job_artifact_agent_data_body` → replace value when body is not None.
5. Do **not** add a new type-specific public save for job_resume / cover_letter. Do **not** change `save_job_artifact`, `get_job_current`, or `pin_job_artifact_agent_data_id` signatures/behavior.

⚠️ **Decision:** Privatize prepare rather than leave it public. Scope allows either; `astral.standards.public-then-helpers` prefers no leftover public type-wired peer once the parallel map is gone. Agent is the sole production caller (lazy import of the private name in Stage 2). Betty revises component patches that still mock/import the public name under `qa-child` — engineer does not edit `tests/`.

## Stage 2: Agent finalize land via TASK_CONFIG.artifact_key

**Done when:** `src/core/agent.py` has zero references to `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`; on successful `finalize_job_resume` / `finalize_cover_letter` with a job `index`, `do_task` reads `TASK_CONFIG[task_key]["artifact_key"]`, calls `_prepare_job_replica_body` then `save_job_artifact(index, catalog_key, body)`; `propose_application_responses` pin path and candidate craft persist path are unchanged in behavior.

1. In `src/core/agent.py`, remove `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` from the `src.utils.config` import list (keep `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` and `TASK_CONFIG`).
2. In `do_task`, replace the body-replica block that today starts with `replica_slot = JOB_ARTIFACT_BODY_REPLICA_BY_TASK.get(task_key)` and the paired `if result.get("success") and replica_slot:` / `elif pin_slot …` structure with:
   ```python
   pin_slot = JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK.get(task_key)
   task_cfg = TASK_CONFIG.get(task_key) or {}
   catalog_key = task_cfg.get("artifact_key")
   # Job catalog land via TASK_CONFIG.artifact_key (AST-1603). Candidate craft
   # uses a separate persist_candidate_craft_hops gate below — do not share this branch.
   if (
       result.get("success")
       and task_cfg.get("entity_type") == "job"
       and isinstance(catalog_key, str)
       and catalog_key.strip()
   ):
       if index:
           # Body land uses in-memory parsed — do not gate on resp_id (AST-1600).
           # Lazy import breaks agent↔tracker cycle (consult imports agent).
           try:
               from src.core.tracker import (
                   _prepare_job_replica_body,
                   save_job_artifact,
               )

               body = _prepare_job_replica_body(
                   catalog_key, parsed, astral_job_id=index
               )
               if body is None:
                   logger.warning(
                       "persist_job_artifact_catalog skipped task=%s index=%s "
                       "key=%s reason=prepare_empty",
                       task_key,
                       index,
                       catalog_key,
                   )
               else:
                   landed = save_job_artifact(index, catalog_key, body)
                   if landed is None:
                       logger.warning(
                           "persist_job_artifact_catalog skipped task=%s index=%s "
                           "key=%s reason=save_skipped_empty",
                           task_key,
                           index,
                           catalog_key,
                       )
           except Exception as persist_err:
               logger.error(
                   "persist_job_artifact_catalog failed task=%s index=%s err=%s",
                   task_key,
                   index,
                   persist_err,
               )
       elif debug:
           _do_task_debug_logger(debug).debug_detail(
               f"artifact_catalog key={catalog_key} skipped reason=missing_index"
           )
   elif pin_slot and result.get("success"):
       # unchanged proposed_answers pin branch (resp_id gate, debug skip reasons)
       ...
   ```
   Keep the existing `elif pin_slot` body exactly as today (lazy import `pin_job_artifact_agent_data_id`, `index and resp_id` gate, debug skip reasons). Do not edit the `draft_job_resume` notes block or the `persist_candidate_craft_hops` candidate block that follow.
3. Grep `src/core/agent.py` for `JOB_ARTIFACT_BODY_REPLICA` and the public name `prepare_job_replica_body` — zero hits. Grep `src/` for `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` — zero production hits. Debug skip lines stay Style D / `debug=True` gated (`astral.standards.debug-contract-gated`).

⚠️ **Decision:** Gate job catalog land on `entity_type == "job"` **and** non-empty `artifact_key`, not on `artifact_key` alone. Candidate tasks (`craft_resume_base`, etc.) also carry `artifact_key`; sharing the branch would mis-route a candidate index into `save_job_artifact`. Ticket wording is job-finalize land; the entity_type gate is the concrete form of that boundary.

## Estimate

Confirm Chuckles estimate: 3 — agree
