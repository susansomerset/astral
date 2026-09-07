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

## Radia review

# Radia code review — AST-1602

**Publish ref:** `origin/sub/AST-1601/AST-1602-retire-job-body-replica-config-authority` @ `a5cca41c93cda3046cf3b2d44e3b09e25fbaa940`  
**Diff baseline:** `origin/dev...origin/sub/AST-1601/AST-1602-retire-job-body-replica-config-authority` (4 files: `src/utils/config.py`, `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`, issue doc)

---

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1602  
**Publish ref:** a5cca41c93cda3046cf3b2d44e3b09e25fbaa940  
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent/confidence paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task/delegation changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release batch helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity-agent-responses paths |
| astral.config.config-source-of-truth | scoped | conforms | finalize catalog binding moved onto `TASK_CONFIG.artifact_key`; parallel map deleted |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env usage |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact dirs |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch/run-next changes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no seed-auto paths |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | issue doc add is pipeline artifact, not product scope |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty path; no Betty src/features commits in diff |
| astral.git.engineer-test-tree-ban | scoped | conforms | test/bible edits arrive via `merge-tests(AST-1602)` Betty SHA, not engineer product commits |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render-verdict paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API auth paths |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | utils-only product diff |
| astral.layers.import-direction | scoped | not-applicable | no import graph changes in diff |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI paths |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed table paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog overrides |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed boot paths |
| astral.seed.define-approved | scoped | not-applicable | no define/seed paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | no database/migration changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug-contract emission added |
| astral.standards.dry-and-focused-functions | scoped | conforms | map deletion + derivation inline; no duplicate SoT |
| astral.standards.in-scope-only | scoped | conforms | product diff confined to `config.py`; test/bible via Betty pipeline; agent left for AST-1603 per plan |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging changes |
| astral.standards.names-not-ticket-ids | scoped | conforms | symbols/descriptions use domain names, not ticket ids as runtime identifiers |
| astral.standards.no-cross-contamination | scoped | not-applicable | single-module config authority move |
| astral.standards.no-hardcoded-sets | scoped | conforms | editable leaves derived from `TASK_CONFIG.artifact_key`; hardcoded assert tuple is validation not SoT |
| astral.standards.public-then-helpers | scoped | not-applicable | no new helper surface |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transition logic |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job-state enforcement changes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/daisy-chain paths |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no UI naming paths |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no gunicorn/server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single `merge-tests(AST-1602): origin/tests 0b3f9ea4…` on publish tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `merge-tests` / `docs` commits follow vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | child work on `sub/AST-1601/…`, not direct-to-dev product |
| orch.git.ftr-sub-topology | universal | conforms | correct sub-under-parent topology |
| orch.git.merge-on-checkout | universal | conforms | no merge/checkout violations evident |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear stage commits on sub |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1601 epic worktree pattern |
| orch.git.three-permanent-branches | universal | conforms | no extra permanent branches introduced |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | config authority split already decided in parent plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match plan text; pin map untouched |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to diff substance |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed as required |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | manifest + revised 1099/1590 tests + bible land on Betty path |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada remains assignee; review is recommend-only |
| orch.roles.pre-commit-path-bans | universal | conforms | no hook-ban path violations in diff |

**Straggler:** Joan `[plan-rubric] APPROVED` attached; no Excluded statute list in artifact — nothing to straggle.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | Extends `TASK_CONFIG` with `artifact_key`; retires parallel `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` map — matches approved solution shape |
| none formally cited in plan ## Patterns to reuse | — | Joan considered `patt.artifact.manage-catalog` (draft, not approved catalog entry); directionally aligned but not scored as catalog pattern |

## Plan adherence

Stages 1–2 landed exactly as specified:

- `TASK_CONFIG["finalize_job_resume"]["artifact_key"] == "job.artifacts.job_resume"` and `finalize_cover_letter` → `"job.artifacts.cover_letter"`, mirroring `craft_resume_base`.
- `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` block and intersection assert deleted; zero hits in `config.py`.
- `JOB_EDITABLE_ARTIFACT_TYPES` re-derived from ordered finalize task keys via `.rsplit(".", 1)[-1]`.
- Post-`ARTIFACT_CONFIG` asserts rewritten to bind via `TASK_CONFIG.artifact_key`.
- `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` unchanged (`propose_application_responses` → `proposed_answers` only).
- No `ARTIFACT_CONFIG` entries added for sibling blobs; new `TestAst1602…::test_sibling_blobs_stay_out_of_artifact_config` locks that.
- No `agent.py` / `tracker.py` edits — correct per explicit scope gate and AST-1603 boundary.
- Estimate **2** footprint matches: one config module, config-only authority move plus Betty test/bible hygiene.

Component manifest from bible runs green on config-only paths (config module imports cleanly; manifest does not import `agent`).

## Frame diff

- **Before:** finalize hop → catalog key binding lived in parallel `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`; editable leaf types derived from that map’s values.
- **After:** finalize hops carry `artifact_key` on their `TASK_CONFIG` rows (candidate pilot shape); editable leaf types derive from those task keys; startup asserts enforce TASK_CONFIG ↔ ARTIFACT_CONFIG binding.
- **Still deferred:** production `agent.py` body-replica consumer still references deleted symbol until AST-1603.

## Findings

### discuss

- **Location:** `src/core/agent.py` L78, L3049 (out of diff; downstream of config delete)  
  **Finding:** `ImportError: cannot import name 'JOB_ARTIFACT_BODY_REPLICA_BY_TASK' from 'src.utils.config'` on `from src.core import agent`. Config-only component tests pass because they import `config` directly; any path loading `agent` is broken until AST-1603.  
  **Recommendation:** Not fix-now on this ticket — plan Stage 2 §5 and Joan acceptable finding document the deliberate intermediate tree. **Do not rollup/merge this sub to ftr expecting a green agent import** until AST-1603 lands. Chuckles/datt should preserve blockedBy order AST-1602 → AST-1603.

### advisory

- **Location:** `docs/test-bible/utils/config.md` L3640–3641  
  **Finding:** AST-1602 manifest block still has `Bible shasum (publish tip): *(filled after publish)*` while the immediately preceding AST-1596 block at L3601 has a filled sha.  
  **Recommendation:** Betty/Chuckles fill on next bible publish pass — not blocking config correctness.

- **Location:** `docs/test-bible/core/agent.md` (unchanged in this diff)  
  **Finding:** Still documents finalize hops using `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`. Stale relative to config truth.  
  **Recommendation:** AST-1603 bible sweep when agent call sites rewire; manifest already says not to include agent body-replica tests on AST-1602 manifest.

- **Location:** Plan Stage 2 §5 wording  
  **Finding:** Plan says `tracker.py` still imports the deleted symbol; repo grep shows **only** `agent.py` references it. Minor plan imprecision, no tracker impact observed.

### fix-now

(none)

## What's solid

- Config edits are a faithful, minimal execution of Joan-approved Stages 1–2.
- Startup assert block cleanly replaces body-replica authority with TASK_CONFIG binding without touching JAR tab asserts or `proposed_answers` non-catalog guard.
- Betty revised obsolete 1099/1590 tests and added focused `TestAst1602RetireJobBodyReplicaConfigAuthority` coverage aligned with the new SoT.
- Pin map isolation preserved — finalize tasks explicitly excluded from `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK`.

## Recommended actions (downstream — not Radia)

1. **Chuckles:** append this artifact to issue doc; post slim upshot; move to Review Posted; route **resolve-child only if Susan wants the discuss item treated as actionable** — otherwise **PROCEED to User Testing** on config slice with explicit note that epic rollup requires AST-1603 before agent import safety.
2. **AST-1603 implementer:** remove `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` import/usage from `agent.py`; refresh `docs/test-bible/core/agent.md`.
3. **Betty:** fill AST-1602 bible shasum placeholder at publish tip.

context_tokens≈85000
