# AST-1601 — Rip out job-specific artifact pin helpers; match candidate catalog pattern

<!-- linear-archive: AST-1601 archived 2026-09-22 -->

## Linear archive (AST-1601)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1601/rip-out-job-specific-artifact-pin-helpers-match-candidate-catalog  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1588

### Description

## Purpose

[AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) registered `job.artifacts.job_resume` / `job.artifacts.cover_letter` and table SoT, but left a parallel job-only pin / body-replica vocabulary (`JOB_ARTIFACT_BODY_REPLICA_BY_TASK`, leftover pin-key peers, type-wired prepare helpers) that diverges from how candidate lands catalog artifacts (`TASK_CONFIG.artifact_key` → generic entity id + catalog key write/read). This epic removes that parallel authority so job resume and cover letter follow the same candidate-shaped catalog contract — no job-only pin vocabulary for those keys.

## Functional scope

1. **Config authority matches candidate** — Finalize hops that land job resume / cover letter declare their catalog key on `TASK_CONFIG` the same way `craft_resume_base` does (`artifact_key`). The parallel `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` map is retired as authority. Editable leaf types for those catalog keys are derived from `ARTIFACT_CONFIG` / task `artifact_key` values, not from a body-replica peer map.
2. **Agent land matches candidate** — On successful finalize hops, `do_task` reads `TASK_CONFIG[task].artifact_key` and calls the existing generic job catalog write (`save_job_artifact`) with entity id + catalog key + prepared body — same shape as candidate craft persist via `save_candidate_data`. No branch that looks up a job-only body-replica map.
3. **Tracker drops pin/type-wired peers for catalog keys** — Residual helpers and pin-key lists that still treat `job_resume` / `cover_letter` as agent_data pin slots (or require a job-only replica prepare public surface) are removed or collapsed under the generic write/current-read path. Display hydrate for those keys stays on `get_job_current` by catalog key.
4. **Explicit non-goals** — Do not revert [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) catalog registration, artifacts-table SoT, or `save_job_artifact` / `get_job_current`. Do not promote `proposed_answers` / `notes` / `resume_content` / `application_responses` into `ARTIFACT_CONFIG`. The `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` → `pin_job_artifact_agent_data_id` path for `proposed_answers` stays until that key is catalogued (separate epic). No coat-check. No new body-validation gates. No rename of entity-scoped public functions into one cross-entity API.

## Component scope

* `src/utils/config.py` — **modified** — add `artifact_key` on `finalize_job_resume` / `finalize_cover_letter` TASK_CONFIG entries; delete `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` and its asserts; re-derive `JOB_EDITABLE_ARTIFACT_TYPES` (or equivalent) from catalog / task `artifact_key` values; leave `proposed_answers` pin map untouched.
* `src/core/agent.py` — **modified** — finalize land uses `TASK_CONFIG` `artifact_key` → `save_job_artifact`; remove imports/branches on `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`.
* `src/core/tracker.py` — **modified** — remove or privatize job-only replica-prepare peer (`prepare_job_replica_body`) so land does not depend on a parallel public helper; strip `job_resume` / `cover_letter` from pin-key vocabulary (`_JOB_ARTIFACT_PIN_KEYS` and peers); keep proposed_answers pin resolve; keep generic `save_job_artifact` / `get_job_current`.

## Technical scope

* `src/utils/config.py` — Set `artifact_key` to `job.artifacts.job_resume` / `job.artifacts.cover_letter` on the two finalize TASK_CONFIG rows (mirroring `craft_resume_base`). Delete `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` and every assert/derivation that treats it as SoT. Derive editable job catalog leaf types from those `artifact_key` values (or from `ARTIFACT_CONFIG` job-scoped keys that are operator-editable). Keep `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` for `propose_application_responses` only.
* `src/core/agent.py` — Replace body-replica map lookup with `TASK_CONFIG.get(task_key, {}).get("artifact_key")`; when present and hop succeeds with index, prepare body then `save_job_artifact(index, artifact_key, body)`. Proposed_answers pin branch unchanged. Debug skips stay Style D / debug-gated.
* `src/core/tracker.py` — Body prepare for finalize land either moves beside the generic write as a private helper or stays callable without being a job-only public peer required by a parallel map. `_JOB_ARTIFACT_PIN_KEYS` (or successor) lists only remaining pin slots (`proposed_answers`); hydrate continues overlaying catalog currents for the two keys via `get_job_current`. No new type-specific public save for job_resume / cover_letter.

## Architectural definition

**Patterns to reuse**

* `pattern.config.config-block` — task/catalog authority lives in named config blocks, not ad hoc maps beside them. [link](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>)
* `patt.artifact.manage-catalog` — catalog keys remain the sole key authority; callers resolve via catalog + generic write/read. [link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — agent land replicates into operative rows via the generic write, not agent_data pins for these keys. [link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — display/consumers keep current-read by catalog key. [link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)

**New patterns proposed**

* none

**Applicable statutes**

* `astral.config.config-source-of-truth` — TASK_CONFIG / ARTIFACT_CONFIG are SoT for keys and task→artifact binding. [link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — do not reintroduce inline job-only key sets once body-replica map is gone. [link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.dry-and-focused-functions` — collapse parallel prepare/land paths. [link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
* `astral.standards.public-then-helpers` — no leftover public type-wired peers for catalog keys. [link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.public-then-helpers.md>)
* `astral.standards.in-scope-only` — do not expand into proposed_answers catalog work or coat-check. [link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — agent↔tracker lazy imports stay legal; no new layer violations. [link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.standards.debug-contract-gated` — any land/skip debug lines remain `debug=True` gated. [link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)

## Acceptance criteria

1. `TASK_CONFIG["finalize_job_resume"]` and `TASK_CONFIG["finalize_cover_letter"]` each expose `artifact_key` equal to the matching `ARTIFACT_CONFIG` key.
2. `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` does not exist in config (and no production caller imports it).
3. Successful finalize hops persist bodies only via `save_job_artifact(entity_id, catalog_key, body)` driven by `TASK_CONFIG` `artifact_key` — same calling shape candidate uses for catalog str-path save.
4. No production pin write or pin-key list treats `job_resume` or `cover_letter` as agent_data pin slots.
5. `get_job_current` / hydrate for those two keys still serves display from the artifacts table ([AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) SoT preserved).
6. `proposed_answers` pin path (`JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` + `pin_job_artifact_agent_data_id`) still works unchanged.
7. Sibling non-catalog blobs (`notes`, `resume_content`, `application_responses`) are not added to `ARTIFACT_CONFIG`.

## Open questions

none

## Proposed child tickets

#### 1!: **Retire job body-replica config authority - Ada**

Owns config-only alignment: put `artifact_key` on the two finalize TASK_CONFIG rows, delete `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` and its asserts, derive editable job catalog leaf types from catalog / `artifact_key` values. Does not rewire agent or tracker call sites (sibling #2). Blocks #2.
**Citations:** `pattern.config.config-block`; `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`
**Scope:** `src/utils/config.py` — **modified** — add `artifact_key` on `finalize_job_resume` / `finalize_cover_letter` TASK_CONFIG entries; delete `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` and its asserts; re-derive `JOB_EDITABLE_ARTIFACT_TYPES` (or equivalent) from catalog / task `artifact_key` values; leave `proposed_answers` pin map untouched. `src/utils/config.py` — Set `artifact_key` to `job.artifacts.job_resume` / `job.artifacts.cover_letter` on the two finalize TASK_CONFIG rows (mirroring `craft_resume_base`). Delete `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` and every assert/derivation that treats it as SoT. Derive editable job catalog leaf types from those `artifact_key` values (or from `ARTIFACT_CONFIG` job-scoped keys that are operator-editable). Keep `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` for `propose_application_responses` only.
**Estimate: 2**

#### 2: **Agent + tracker land via TASK_CONFIG.artifact_key - Hedy**

After #1: rewire `do_task` finalize land to `TASK_CONFIG.artifact_key` → `save_job_artifact`; remove body-replica map branches; collapse/remove `prepare_job_replica_body` as a required public peer; strip `job_resume` / `cover_letter` from pin-key vocabulary; keep proposed_answers pin resolve and generic catalog write/read. Does not re-own config registration (#1). Does not catalog `proposed_answers`.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `astral.standards.dry-and-focused-functions`; `astral.standards.public-then-helpers`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`; `astral.standards.in-scope-only`
**Scope:** `src/core/agent.py` — **modified** — finalize land uses `TASK_CONFIG` `artifact_key` → `save_job_artifact`; remove imports/branches on `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`. `src/core/tracker.py` — **modified** — remove or privatize job-only replica-prepare peer (`prepare_job_replica_body`) so land does not depend on a parallel public helper; strip `job_resume` / `cover_letter` from pin-key vocabulary (`_JOB_ARTIFACT_PIN_KEYS` and peers); keep proposed_answers pin resolve; keep generic `save_job_artifact` / `get_job_current`. `src/core/agent.py` — Replace body-replica map lookup with `TASK_CONFIG.get(task_key, {}).get("artifact_key")`; when present and hop succeeds with index, prepare body then `save_job_artifact(index, artifact_key, body)`. Proposed_answers pin branch unchanged. Debug skips stay Style D / debug-gated. `src/core/tracker.py` — Body prepare for finalize land either moves beside the generic write as a private helper or stays callable without being a job-only public peer required by a parallel map. `_JOB_ARTIFACT_PIN_KEYS` (or successor) lists only remaining pin slots (`proposed_answers`); hydrate continues overlaying catalog currents for the two keys via `get_job_current`. No new type-specific public save for job_resume / cover_letter.
**Estimate: 3**

---

## Original brief

## Purpose

Rip out job-specific artifact pin / type-wired helpers left by [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) (e.g. `JOB_ARTIFACT_AGENT_DATA_PIN` and peers) so job resume / cover letter follow the **same** candidate catalog pattern — generic entity id + catalog key, no job-only pin vocabulary.

## Related

Related to [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588). Susan: [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) was supposed to be an identical pattern to candidate; remaining job-specific functions are contrary to the new artifact patterns.

## As-is

[AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) landed catalog keys and table paths, but product still carries job-specific pin/helper surfaces that diverge from candidate's generic catalog contract.

## To-be

Those job-specific helpers are removed or collapsed to the shared candidate-shaped catalog write/read path; no parallel job-only pin authority.

### Comments

#### chuckles — 2026-09-07T00:26:26.288Z
AST-1602 REVIEW — Radia: config slice clean; deliberate agent import break until AST-1603 (discuss only, no fix-now).

---

_Implementation detail may live in git history on `origin/dev`._
