# AST-1602: Retire job body-replica config authority

**Linear:** [AST-1602](https://linear.app/astralcareermatch/issue/AST-1602)
**Parent:** [AST-1601](https://linear.app/astralcareermatch/issue/AST-1601) — Rip out job-specific artifact pin helpers; match candidate catalog pattern
**Publish ref:** `sub/AST-1601/AST-1602-retire-job-body-replica-config-authority`

Config-only slice: put `artifact_key` on the two job finalize `TASK_CONFIG` rows (same shape as `craft_resume_base`), delete `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` and every assert/derivation that treats it as SoT, and re-derive `JOB_EDITABLE_ARTIFACT_TYPES` from those task `artifact_key` values. Leaves `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` / `proposed_answers` alone. Does **not** rewire `agent.py` or `tracker.py` — that is [AST-1603](https://linear.app/astralcareermatch/issue/AST-1603) (blocked by this ticket).

## Explicit scope gate

Ticket **## Scope** names only `src/utils/config.py`. Every Files Changed row and every Stage step stays inside that file. No agent/tracker call-site edits, no cataloging of `proposed_answers` / `notes` / `resume_content` / `application_responses`, no new `ARTIFACT_CONFIG` keys.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `artifact_key` on finalize TASK_CONFIG rows; delete body-replica map + asserts; re-derive `JOB_EDITABLE_ARTIFACT_TYPES` from task `artifact_key` values | utils |

## Stages

## Stage 1: TASK_CONFIG artifact_key on finalize hops

**Done when:** `TASK_CONFIG["finalize_job_resume"]["artifact_key"] == "job.artifacts.job_resume"` and `TASK_CONFIG["finalize_cover_letter"]["artifact_key"] == "job.artifacts.cover_letter"`, each key present in `ARTIFACT_CONFIG`. Body-replica map still exists until Stage 2.

1. In `src/utils/config.py`, on the `"finalize_job_resume"` entry inside `TASK_CONFIG` (currently ends with `"error_state": ERROR_BUILD_ARTIFACTS_STATE` and no `artifact_key`), add:
   ```python
   "artifact_key": "job.artifacts.job_resume",
   ```
   Place it after `"error_state"` (or immediately before the closing `},` of that dict), mirroring the `"artifact_key": "candidate.artifacts.base_resume"` field on `"craft_resume_base"`.
2. In the same file, on the `"finalize_cover_letter"` entry inside `TASK_CONFIG` (currently ends with `"trigger_state": None` and no `artifact_key`), add:
   ```python
   "artifact_key": "job.artifacts.cover_letter",
   ```
   Same placement rule as step 1.

⚠️ **Decision:** Literal catalog keys on the two TASK_CONFIG rows (not a helper lookup). Matches `craft_resume_base` and parent Technical scope (`job.artifacts.job_resume` / `job.artifacts.cover_letter`).

## Stage 2: Delete body-replica map; re-derive editable leaf types

**Done when:** `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` is gone from `config.py`; `JOB_EDITABLE_ARTIFACT_TYPES` still equals `("job_resume", "cover_letter")` derived from the two finalize task `artifact_key` values; `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` unchanged; startup asserts no longer name the deleted map.

1. In `src/utils/config.py`, delete the entire block that defines and asserts the body-replica map (today ~AST-1548 / AST-1590 comment through the intersection assert):
   ```python
   # AST-1548 / AST-1590: finalize hops → catalog keys (leaf types derived for table I/O).
   JOB_ARTIFACT_BODY_REPLICA_BY_TASK = {
       "finalize_job_resume": "job.artifacts.job_resume",
       "finalize_cover_letter": "job.artifacts.cover_letter",
   }
   assert not (
       set(JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK) & set(JOB_ARTIFACT_BODY_REPLICA_BY_TASK)
   )
   ```
   Leave `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` (the `propose_application_responses` → `proposed_answers` map) exactly as it is.
2. Replace the `JOB_EDITABLE_ARTIFACT_TYPES` derivation that currently reads `JOB_ARTIFACT_BODY_REPLICA_BY_TASK.values()` with derivation from the two finalize task `artifact_key` values, preserving leaf order `job_resume` then `cover_letter`:
   ```python
   # AST-1556 / AST-1602: editable job catalog leaf types from TASK_CONFIG.artifact_key (not body-replica).
   JOB_EDITABLE_ARTIFACT_TYPES = tuple(
       TASK_CONFIG[task_key]["artifact_key"].rsplit(".", 1)[-1]
       for task_key in ("finalize_job_resume", "finalize_cover_letter")
   )
   ```
   Keep `JOB_ARTIFACT_ENTITY_TYPE = "job"` on the next line unchanged.
3. In the post-`ARTIFACT_CONFIG` startup assert block (today the three asserts that name `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` immediately after `_cl` / cover_letter catalog asserts), delete those body-replica asserts and replace them with TASK_CONFIG / ARTIFACT_CONFIG binding asserts:
   ```python
   # Finalize hops bind to catalog keys via TASK_CONFIG.artifact_key (AST-1602).
   assert TASK_CONFIG["finalize_job_resume"]["artifact_key"] == "job.artifacts.job_resume"
   assert TASK_CONFIG["finalize_job_resume"]["artifact_key"] in ARTIFACT_CONFIG
   assert TASK_CONFIG["finalize_cover_letter"]["artifact_key"] == "job.artifacts.cover_letter"
   assert TASK_CONFIG["finalize_cover_letter"]["artifact_key"] in ARTIFACT_CONFIG

   # Editable leaf types are exactly the catalog job-key leaves (order = finalize task keys above).
   assert JOB_EDITABLE_ARTIFACT_TYPES == ("job_resume", "cover_letter")
   assert all(
       ARTIFACT_CONFIG[TASK_CONFIG[task_key]["artifact_key"]]["entity_type"]
       == JOB_ARTIFACT_ENTITY_TYPE
       for task_key in ("finalize_job_resume", "finalize_cover_letter")
   )
   ```
   Do **not** change the JAR tab leaf asserts (`_jar_by_id["artifact_resume"]` / `artifact_cover` / `artifact_application`) or the `proposed_answers` non-catalog assert that follow.
4. Grep `src/utils/config.py` for `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` — zero hits must remain (including comments that still treat the map as SoT). Module docstring does not currently name the map; do not add it.
5. Do **not** edit `src/core/agent.py` or `src/core/tracker.py`. After this stage, those modules still import / call `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` until AST-1603 removes those call sites. That intermediate import break on agent load is expected under blockedBy (#1 → #2); this ticket’s Boundaries forbid fixing it here.

⚠️ **Decision:** Derive `JOB_EDITABLE_ARTIFACT_TYPES` from the two finalize `TASK_CONFIG` `artifact_key` values (ordered task-key tuple), not from a scan of all `ARTIFACT_CONFIG` job keys. Rationale: (a) `JOB_EDITABLE_ARTIFACT_TYPES` is defined before `ARTIFACT_CONFIG` in this file, so catalog scan would require moving the constant; (b) parent Technical scope allows “those `artifact_key` values **or** ARTIFACT_CONFIG job-scoped keys” — task keys are the authority this epic is installing; (c) fixed order `("finalize_job_resume", "finalize_cover_letter")` keeps today’s `("job_resume", "cover_letter")` tuple for tracker table I/O.

⚠️ **Decision:** Ticket AC #2’s “no production caller imports it” clause is split across children by Boundaries: this child deletes the config symbol; AST-1603 removes agent/tracker imports and branches. Do not leave a shim alias in config.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1601/AST-1602-retire-job-body-replica-config-authority`.
- Do not add files, touch agent/tracker, or invent `ARTIFACT_CONFIG` entries for non-catalog blobs.
- If a step is ambiguous or the codebase drifted — stop, comment on **parent** AST-1601 with the Stage N blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1602
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1601/AST-1602-retire-job-body-replica-config-authority` @ `0951955c93a4b308bff7ca6f22a42eb2c8a72ecd`

## Traceability
- **AC1** → Stage 1 (`artifact_key` on `finalize_job_resume` / `finalize_cover_letter`, each ∈ `ARTIFACT_CONFIG`).
- **AC2** → Stage 2 (delete `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` + body-replica asserts from `config.py`; import/caller clause deferred to AST-1603 per Boundaries + Stage 2 decision note).
- **AC3** → Stage 2 step 1 (`JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` untouched).
- **AC4** → Explicit scope gate + Execution contract (no new `ARTIFACT_CONFIG` entries for non-catalog blobs).
- **Parent AC3–5** → N/A — agent land, pin-key vocabulary, and `get_job_current` hydrate are AST-1603 scope.

## Findings

### acceptable
- **Location:** Stage 2 step 5 — transient `agent.py` import break until AST-1603  
  **Finding:** Deleting the config symbol while production still imports it yields a deliberate intermediate broken tree.  
  **Recommendation:** Keep as documented; rollup order should land AST-1603 (or test-tree updates) before expecting green epic-wide import.

- **Location:** Child AC #2 wording vs Boundaries  
  **Finding:** Ticket AC couples “symbol gone” with “no production caller imports it”; plan correctly splits delivery across children.  
  **Recommendation:** No plan change required — decision block is explicit.

- **Location:** Plan structure — no `## Self-Assessment`  
  **Finding:** Section absent (estimate-2 config-only slice; peer plans AST-1590/1592 also omit).  
  **Recommendation:** Optional `minor` self-assessment if engineer wants parity with larger tracker plans; not blocking.

### discuss
- **Location:** `tests/component/utils/test_config.py` (not in Files Changed)  
  **Finding:** Manifest rows still assert `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`; will flip red after Stage 2 until Betty revises bible/manifest on Tests Ready.  
  **Recommendation:** Engineer need not expand scope; flag for qa-child manifest sweep — not a plan defect.

**Considered (in-session):** Universal `orch.*` statutes — all `conforms`. Scoped: `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only` — `conforms`. Cited `pattern.config.config-block` — matches solution shape. Cited `patt.artifact.manage-catalog` (draft directive) — plan retires parallel map in favor of `TASK_CONFIG.artifact_key`, consistent with catalog authority. Codebase anchors verified: `craft_resume_base` already carries `artifact_key`; finalize rows lack it today; body-replica block ~L3237–3249; post-`ARTIFACT_CONFIG` asserts ~L5835–5846 match Stage 2 targets.

context_tokens≈52000

## Review (build)

**Built @ `4ac6d1ef`** — `origin/sub/AST-1601/AST-1602-retire-job-body-replica-config-authority`

Stages 1–2 landed: finalize TASK_CONFIG `artifact_key` rows; `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` deleted; `JOB_EDITABLE_ARTIFACT_TYPES` derived from those keys; pin map untouched. Agent/tracker call sites remain until AST-1603. Test path remains Betty `qa-child`.
