# AST-1270 — Nested draft_job_resume contract (prompt + normalize/validate)

**Linear:** https://linear.app/astralcareermatch/issue/AST-1270/nested-draft-job-resume-contract-prompt-normalizevalidate-draft-job  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong  
**Publish ref:** `sub/AST-1268/AST-1270-nested-draft-job-resume-contract`

`draft_job_resume` already asks Judith for a nested envelope (`agent_payload.resume` + sibling `deviations`), but runtime normalize/validate still treats the outer key `resume` as a catalog section id and whitelists via `resolve_resume_structure` / enabled catalog ids. This ticket unwraps `agent_payload.resume` before section checks, switches the whitelist to the candidate’s current `artifacts.base_resume` section keys, allows `deviations` as sibling metadata (no retention work), and keeps the Manage Tasks seed on that nested shape with no flat-only or “experience must be a string” contradiction. Does **not** own deviations persistence (**AST-1271**), debug whitelist trail (**AST-1272**), HTML chrome, or AST-1201 / AST-1205.

## Diagnosis (why the nested sample fails today)

Verified against `normalize_draft_job_resume_agent_payload` / `validate_draft_job_resume_payload` in `src/core/candidate.py` and the parent brief sample:

1. Manage Tasks seed (`data/admin/agent_task.json` → `draft_job_resume.user_prompt`) already shows nested `agent_payload.resume` + `deviations` — prompt and validator disagree; the model followed the prompt.
2. Normalize’s nest loop promotes children from `content` / `section_content` / `base_resume` only (`_CRAFT_RESUME_CONTENT_DICT_KEYS`). It does **not** unwrap `resume`, so `resume` remains a top-level `agent_payload` key.
3. Validate iterates every non-metadata key on `agent_payload` against `enabled_resume_section_ids(resolve_resume_structure(cd))`. `resume` is not a section id → `Unknown resume section key 'resume' (not in candidate catalog: …)` — exact parent failure.
4. Whitelist source is structure catalog (default when `artifacts.resume_structure` is missing), not `artifacts.base_resume` keys. Parent contract: whitelist = current base resume section keys so candidates without a persisted structure blob still validate when base keys match.
5. `_DRAFT_JOB_RESUME_METADATA_KEYS` is a module frozenset and does not include `deviations`. Even after unwrap, `deviations` would be treated as an unknown section unless allowlisted as metadata.
6. `_resume_payload_body` in `tracker.py` walks flat `agent_payload` string/experience keys only. After a correct unwrap, persist gates see section bodies; without unwrap (or if a caller feeds raw nested JSON), nested bodies are invisible and a `deviations` list is skipped only because it is not a string — harden by preferring `.resume` when present so resume parsers never treat envelope keys as section content.

⚠️ **Decision:** Nested envelope is authoritative. Normalize **pops** `agent_payload[nested_resume_key]` when it is a dict and merges its entries onto `agent_payload` before section validation. Flat payloads (no nest key) remain accepted for AST-594-era callers. Whitelist = keys of `artifacts.base_resume` that are members of `RESUME_STRUCTURE_KNOWN_SECTION_IDS` (drops `accent_color` and other non-section junk). Nest key name, metadata key set (including `deviations`), and the existing `resume_section_payload` flag live on `TASK_CONFIG["draft_job_resume"]` — no new inline frozensets in core.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | On `TASK_CONFIG["draft_job_resume"]`: nest unwrap key + payload metadata keys (incl. `deviations`) | utils |
| `src/core/candidate.py` | Unwrap nested resume; whitelist from `base_resume` keys; read metadata/nest names from TASK_CONFIG | core |
| `src/core/tracker.py` | `_resume_payload_body`: when nested resume dict present, take section bodies from it only | core |
| `data/admin/agent_task.json` | Align `draft_job_resume` user_prompt nested example; experience matches base value types | data seed |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Persist / retain `deviations` as hop or artifact metadata | AST-1271 |
| Style D debug whitelist / unwrap / accept-reject trail | AST-1272 |
| HTML builders / cover-letter hops / craft-base parse | out of epic |
| AST-1201 base-resume daisy chain / AST-1205 approve artifacts | related, not this child |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: TASK_CONFIG nest + metadata contract

**Done when:** `TASK_CONFIG["draft_job_resume"]` declares the nest key and metadata key set used by normalize/validate. No behavior change yet until Stage 2 reads them.

1. In `src/utils/config.py`, inside `TASK_CONFIG["draft_job_resume"]` (keep existing `response_schema`, `response_format`, `resume_section_payload`, entity/chain fields), add:

   ```python
   "nested_resume_key": "resume",
   "payload_metadata_keys": (
       "astral_job_id",
       "company",
       "title",
       "task_success",
       "deviations",
   ),
   ```

2. Do **not** put section id lists, base_resume paths, or prompt prose in this stage. Do **not** add a second config block for the same literals.

3. Leave `_DRAFT_JOB_RESUME_METADATA_KEYS` in `candidate.py` untouched until Stage 2 replaces reads with TASK_CONFIG (avoid a half-migrated dual source).

## Stage 2: Normalize unwrap + base_resume whitelist + deviations metadata

**Done when:** The parent nested sample shape validates when `resume` section keys ⊆ that candidate’s `artifacts.base_resume` known section keys and values are well-typed (experience prose string **or** job array). `resume` is never reported as an unknown section key after normalize. True unknown keys **inside** `resume` still fail with a clear unknown-key message. Candidates with no persisted `artifacts.resume_structure` still pass when base_resume keys match. `deviations` is skipped as metadata (not validated as a section). Flat (no nest) payloads still validate against the same base_resume whitelist.

1. In `src/core/candidate.py`, add a small helper (public or module-private — place with the other draft helpers, public-then-helpers order):

   ```python
   def draft_job_resume_allowed_section_keys(candidate_data: dict) -> list[str]:
       """Section keys from artifacts.base_resume ∩ RESUME_STRUCTURE_KNOWN_SECTION_IDS."""
   ```

   Implementation rules:
   - Read `candidate_data["artifacts"]["base_resume"]`; non-dict / missing → return `[]`.
   - Return sorted keys where `key in RESUME_STRUCTURE_KNOWN_SECTION_IDS` (import/use the existing config tuple — do not copy a parallel section-id tuple).
   - Do **not** call `resolve_resume_structure` / `enabled_resume_section_ids` for this whitelist.

2. Change `normalize_draft_job_resume_agent_payload(parsed)`:
   - Resolve `task_cfg = TASK_CONFIG["draft_job_resume"]`, `nest_key = task_cfg["nested_resume_key"]`, `meta = set(task_cfg["payload_metadata_keys"])`.
   - Resolve `inner` as today (`agent_payload` dict or the parsed dict itself).
   - **Unwrap:** if `inner.get(nest_key)` is a `dict`, `block = inner.pop(nest_key)` then for each `(sid, val)` in `block.items()`, set `inner[sid] = val` (resume body wins on key clash with a pre-existing top-level section key).
   - If `inner.get(nest_key)` is present and **not** a dict, leave it in place — Stage 2 validate will fail it as an unknown/disallowed key (or add an explicit error string in validate: `f"{nest_key!r} must be an object of resume sections"` when the key remains and is not a dict). Prefer the explicit error in `validate_draft_job_resume_payload` after normalize.
   - Keep existing `resume_structure` flatten, `_CRAFT_RESUME_CONTENT_DICT_KEYS` promote, coercions, and `_apply_draft_job_resume_section_aliases` — but when skipping metadata keys in those loops, use `meta` from TASK_CONFIG (include `deviations`), not the old module frozenset.
   - Remove the module-level `_DRAFT_JOB_RESUME_METADATA_KEYS` frozenset once all reads use TASK_CONFIG (delete the constant; do not leave a stale duplicate). Keep `_DRAFT_JOB_RESUME_CONSULT_KEYS` as today unless it already lives in config (leave consult reject set as-is for this ticket).

3. Change `validate_draft_job_resume_payload(parsed, candidate_data)`:
   - Call normalize first (unchanged order).
   - Resolve `inner` / `payload` as today.
   - After normalize, if `nest_key` is still in `payload` and is not a dict: return `f"{nest_key!r} must be an object of resume sections"`.
   - `allowed = set(draft_job_resume_allowed_section_keys(candidate_data))`.
   - If `not allowed`: return `"candidate has no base_resume section keys"` (replace the old “no enabled resume sections” path for this validator).
   - For each `key, val` in `payload.items()`:
     - Skip if `key in meta` or `key == "resume_structure"`.
     - Keep consult-key rejection via `_DRAFT_JOB_RESUME_CONSULT_KEYS`.
     - If `key not in allowed`: return `f"Unknown resume section key '{key}' (not in candidate base_resume keys: {sorted(allowed)})"`.
     - Keep existing experience job-array **or** prose string typing rules (AST-997 / AST-594) and other section string coercion.
   - Keep `pin_experience_job_facts_from_base(payload, candidate_data)` at the end.
   - Do **not** drop or persist `deviations` — leave the value on the payload for AST-1271.

4. Do **not** add Style D debug logging here (AST-1272). Do **not** change `do_task` call sites beyond what already invokes these helpers (`resume_section_payload` path stays).

## Stage 3: Resume body path ignores envelope keys

**Done when:** `_resume_payload_body` returns only section bodies from the nested `resume` object when that object is present; `deviations` and the nest key itself never appear as section content. Flat already-unwrapped payloads behave as today.

1. In `src/core/tracker.py`, update `_resume_payload_body(parsed)`:
   - Resolve `body` from `agent_payload` or `parsed` as today.
   - Read `nest_key = TASK_CONFIG["draft_job_resume"]["nested_resume_key"]`.
   - If `body.get(nest_key)` is a `dict`, set `body = body[nest_key]` for section extraction only (do not mutate the original parsed object).
   - Build `out` as today: string values + experience job arrays only.
   - Do **not** copy `deviations` or other metadata into `out`.

2. No changes to `save_job_artifact_resume_content` filtering beyond what the updated body helper feeds. No HTML/builder edits.

## Stage 4: Manage Tasks seed — nested contract only

**Done when:** Repo seed `data/admin/agent_task.json` row `task_key == "draft_job_resume"` instructs the nested `agent_payload.resume` + `deviations` shape; there is no flat-only envelope example; experience wording matches base value types (string or job array), not “must be a single string.”

1. Edit only the `draft_job_resume` row’s `user_prompt` JSON example / surrounding sentences:
   - Keep the nested envelope:
     ```text
     "agent_payload": {
       "resume": { ...exactly the same keys and value types as the provided base resume... },
       "deviations": ["instruction skipped and why"]
     }
     ```
   - Replace the clause `experience remains a single string formatted like the base` with wording that experience (and every other key) keeps the **same value type as the provided base resume** (prose string or job array for `experience`).
   - Do **not** add a second example where section keys sit flat on `agent_payload` without `resume`.
   - Keep existing instruction bullets (claims trace to materials, deviations for skipped brief items, writing instructions, etc.) unless a sentence contradicts the nested contract — then fix that sentence only.
   - Do **not** edit other task_key rows in this ticket.

2. Repo admin JSON is applied at startup (`apply_repo_admin_json_at_startup`); no separate DB migration script.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, publishes to `origin/sub/AST-1268/AST-1270-nested-draft-job-resume-contract`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — `TASK_CONFIG` literals + `candidate.py` draft normalize/validate + thin `_resume_payload_body` harden + one Manage Tasks seed row.

**Conf:** `high` — Failure mode is reproduced by the parent sample against current normalize/validate; fix is unwrap + whitelist source swap + metadata allowlist, reusing existing experience typing.

**Risk:** `Medium` — Wrong whitelist (e.g. still requiring resume_structure, or including non-section base keys) would reject valid drafts or accept junk keys; botched unwrap would leave `resume` as a section key and keep the parent outage.

## Code rules check

- §1.3 DRY: one unwrap path in normalize; whitelist helper shared by validate; tracker reads the same nest key from TASK_CONFIG.
- §1.4 / §2.1 / `astral.standards.no-hardcoded-sets` / `pattern.config.config-block`: nest key + metadata keys on `TASK_CONFIG["draft_job_resume"]`; section id universe stays `RESUME_STRUCTURE_KNOWN_SECTION_IDS`.
- §2.2 / `astral.agent.do-task-delegation`: no new Anthropic call shape; `do_task` keeps calling existing normalize/validate hooks.
- §1.5.1: no new debug-contract lines (AST-1272).
- §3.3 imports: core → utils only for config; no ui/data import changes.
- Boundaries: no deviations retention, no debug trail, no test-tree edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1268/AST-1270-nested-draft-job-resume-contract`  
**Tip:** `9ef3f920`

Stages landed: TASK_CONFIG nest/metadata → unwrap + `base_resume` whitelist → `_resume_payload_body` nest prefer → Manage Tasks seed wording.

## Radia review — code-rubric.v2

`[code-rubric] revision=2`
**Overall:** DISCUSS
**Diff:** `origin/dev...origin/sub/AST-1268/AST-1270-nested-draft-job-resume-contract` (product files: `src/utils/config.py`, `src/core/candidate.py`, `src/core/tracker.py`, `data/admin/agent_task.json` — matches plan Files Changed exactly)

### Statutes checked (full active set, in-session)

`id | tier | verdict | one-line`

- `orch.roles.betty-owns-test-tree | universal | conforms | test()/merge-tests commits own tests/ + docs/test-bible/**; no engineer code() commit touches them`
- `orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes/** changed`
- `orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee is Ada (engineer), not Chuckles`
- `orch.roles.pre-commit-path-bans | universal | conforms | each commit stayed in its role's lane`
- `orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Tests Passed`
- `orch.git.three-permanent-branches | universal | conforms | no new permanent branch`
- `orch.git.flow-direction-inviolable | universal | conforms | tests→sub via merge-tests, dev→sub merge only`
- `orch.git.no-cherry-pick-rebase-force | universal | conforms | no rebase/force-push/cherry-pick in the commit sequence`
- `orch.git.betty-merge-tests-one-sha | universal | conforms | exactly one merge-tests(AST-1270) commit, SHA a07a3db9`
- `orch.git.merge-on-checkout | universal | conforms | sub carries ftr ancestry; no stale-seed evidence`
- `orch.git.one-epic-worktree-per-parent | universal | conforms | single astral-AST-1268/ worktree`
- `orch.git.ftr-sub-topology | universal | conforms | sub/AST-1268/AST-1270-… naming, Chuckles-created`
- `orch.git.commit-vocabulary | universal | conforms | docs()/code()/test()/merge-tests() only`
- `orch.git.no-dev-agent-branches | universal | conforms | no dev-<agent> branch`
- `orch.pipeline.call-susan-for-product-decisions | universal | needs-discussion | Joan's plan-rubric flagged the base_resume-hard-fail behavior (no persisted structure + no base_resume) as a product call needing Susan confirmation; no Susan comment found — build proceeded on Joan's "defensible" read without escalation`
- `orch.pipeline.status-gates-skill-entry | universal | conforms | stateHistory shows in-order Todo→…→Tests Passed`
- `orch.pipeline.project-scoped-queues | universal | conforms | explicit-id review, no queue behavior`
- `orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4 executed in order, no skip/reorder/expand`
- `astral.agent.do-task-delegation | scoped | conforms | no new do_task call assembly`
- `astral.agent.grade-vector-validation | scoped | conforms | vector validation untouched`
- `astral.agent.confidence-bounds | scoped | conforms | confidence handling untouched`
- `astral.batch.claim-process-release | scoped | conforms | claim/process/release untouched`
- `astral.batch.batch-id-first | scoped | conforms | no new batch APIs`
- `astral.batch.entity-agent-responses-latest-only | scoped | conforms | agent_data write path untouched`
- `astral.batch.batch-id-format | scoped | conforms | batch_id construction untouched`
- `astral.config.config-source-of-truth | scoped | conforms | nest key + metadata keys land on TASK_CONFIG (cited pattern.config.config-block)`
- `astral.config.pass-threshold-vs-score-floor | scoped | conforms | pass_threshold/score_floor untouched`
- `astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals added`
- `astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no artifacts/** or scripts/spikes/** paths in diff`
- `astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features addition is the proper plan doc, not spike notes`
- `astral.dispatch.run-next-is-chain-authority | scoped | conforms | new TASK_CONFIG keys are payload contract, not a run_next-shadowing membership set`
- `astral.dispatch.seed-auto-false | scoped | conforms | no dispatch_task/auto_mode touched`
- `astral.docs.features-single-file-per-ticket | scoped | conforms | one file, docs/features/artifacts/ast-1270-…md`
- `astral.git.betty-no-src-or-features | scoped | conforms | Betty's commits touch only tests/ + docs/test-bible/**`
- `astral.git.engineer-test-tree-ban | scoped | conforms | engineer code() commits never touch tests/ or docs/test-bible`
- `astral.idioms.coat-check-never-store-empty | scoped | conforms | no coat-check handler touched`
- `astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | render_verdict/consult path untouched`
- `astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no src/ui/** changes`
- `astral.layers.core-vs-external-bright-line | scoped | conforms | no I/O added to core`
- `astral.layers.import-direction | scoped | conforms | TASK_CONFIG import is core→utils; no new cross-layer import`
- `astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** changes`
- `astral.layers.ui-config-driven-business-logic | scoped | conforms | no UI files touched`
- `astral.seed.agent-tables-in-repo-json | scoped | conforms | agent_task.json stays non-empty; targeted wording edit only`
- `astral.seed.archie-catalog-wins | scoped | conforms | change committed to repo JSON, not a live-DB-only edit`
- `astral.seed.boot-only-not-hot-path | scoped | conforms | TASK_CONFIG addition is a static dict literal, no new hot-path seed code`
- `astral.seed.define-approved | scoped | conforms | parent Architectural definition names the nest/metadata config need + cites pattern.config.config-block`
- `astral.seed.operator-rows-stay-deleted | scoped | conforms | no dispatch_task insert/reconcile logic touched`
- `astral.seed.other-via-coverage-join | scoped | conforms | no new seed/provision path added`
- `astral.standards.database-header-inventory | scoped | not-applicable | no src/data/** changes`
- `astral.standards.data-raises-caller-logs | scoped | conforms | validate/normalize keep returning Optional[str]; no new raise/log`
- `astral.standards.debug-contract-gated | scoped | conforms | no new debug=True surface; Style D trail explicitly deferred to AST-1272`
- `astral.standards.dry-and-focused-functions | scoped | conforms | one unwrap path in normalize; one whitelist helper shared by validate`
- `astral.standards.in-scope-only | scoped | conforms | diff = exactly the plan's 4 Files Changed`
- `astral.standards.logging-via-utils | scoped | conforms | no new logging added`
- `astral.standards.names-not-ticket-ids | scoped | conforms | draft_job_resume_allowed_section_keys is domain language`
- `astral.standards.no-cross-contamination | scoped | conforms | no out-of-layer import added`
- `astral.standards.no-hardcoded-sets | scoped | conforms | _DRAFT_JOB_RESUME_METADATA_KEYS frozenset deleted, replaced by TASK_CONFIG; no new inline set added`
- `astral.standards.public-then-helpers | scoped | conforms | new public helper grouped with public draft helpers; private alias helper relocated after the public validate fn`
- `astral.standards.utils-data-late-import-only | scoped | conforms | config.py edit is dict literals only, no utils→data import`
- `astral.state.core-decides-transitions | scoped | conforms | no transition logic touched`
- `astral.state.job-prior-states-enforced | scoped | conforms | no job state transition touched`
- `astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch run-loop touched`
- `astral.ui.frontend-file-placement | scoped | not-applicable | no src/ui/frontend/** changes`
- `astral.ui.naming-conventions | scoped | not-applicable | no src/ui/** changes`
- `astral.ui.single-gunicorn-worker | scoped | conforms | config.py edit unrelated to worker/scheduler settings`

**Straggler (C4):** Joan's plan-rubric.v1 verdict (attached, APPROVED) reports counts only ("9 scoped excluded") without itemized ids — no itemized Excluded list to cross-check against this sweep's `not-applicable` rows. No contradiction identified.

### Pattern conformance

`id | verdict | one-line`

- `pattern.config.config-block | conforms | TASK_CONFIG["draft_job_resume"] extended with nest key + metadata keys; old inline frozenset deleted, not duplicated`

### Findings

**discuss** — `orch.pipeline.call-susan-for-product-decisions` / plan Stage 2 step 3. Joan's plan-rubric already flagged this: a candidate with no persisted `artifacts.resume_structure` **and** no `artifacts.base_resume` now hard-fails (`"candidate has no base_resume section keys"`) instead of falling back to the 10-id default catalog. Defensible (a hop that tailors the base resume is meaningless without one), but it's a behavior flip decided inside the plan rather than confirmed by Susan. Recommend a short Linear confirmation before this reaches production traffic.

**discuss** — `src/core/tracker.py` persist path (carried from Joan's plan-rubric, still true on the built diff). `validate_draft_job_resume_payload` now whitelists via `base_resume` keys ∩ `RESUME_STRUCTURE_KNOWN_SECTION_IDS`, while `persist_job_artifact_from_parsed` still filters through `filter_content_to_resume_structure(body, resolve_resume_structure(cd))` (enabled catalog ids). A candidate with a persisted structure that disables a section could now validate a section that then silently drops at persist. Harmless while the default catalog enables all 10 known ids; worth a QA watch note since it's a live divergence, not a hypothetical.

**discuss** — merge hygiene, not a product defect. `origin/sub/AST-1268/AST-1270-nested-draft-job-resume-contract`'s previous tip (`ee481251`) carried `docs/test-bible/core/repo_admin_json.md` + `tests/component/core/test_repo_admin_json.py` changes for **AST-1269** (a sibling of parent **AST-1184**, unrelated to AST-1268) via the shared `origin/tests` branch — that content predated and diverged from `origin/dev`'s own (separately resolved) AST-1269 landing. Ran the epic worktree's merge-clean gate (`git merge origin/dev`) before this docs() commit per review-child §4; the merge resolved cleanly with no conflicts and the AST-1269 divergence is gone from the tip this review publishes. No product code in `src/` was affected either way — verified identical across both tips.

### What's solid

Implementation follows Stages 1–4 exactly: `TASK_CONFIG["draft_job_resume"]` carries the nest key + metadata keys (including `deviations`); `normalize_draft_job_resume_agent_payload` unwraps before the legacy flatten/promote/alias logic; `validate_draft_job_resume_payload` whitelists against `base_resume` ∩ `RESUME_STRUCTURE_KNOWN_SECTION_IDS` and gives a clear error when the nest key survives as a non-dict; `_resume_payload_body` prefers the nested body so `deviations` never leaks into resume content; the Manage Tasks seed wording fix is surgical. `no-hardcoded-sets` conformance is a clean textbook example — one frozenset deleted, zero added.

context_tokens≈145000
— Radia

## Resolution

**Date:** 2026-08-08  
**Review:** `[code-rubric] revision=2` Overall DISCUSS @ `e748483d` — zero **fix-now**.

| Finding | Disposition |
|---------|-------------|
| **discuss** — hard-fail when truthy candidate has no `artifacts.base_resume` section keys | **Accepted as planned.** Plan Decision + Stage 2 step 3: whitelist = `base_resume` ∩ known section ids; empty whitelist → `"candidate has no base_resume section keys"`. Matches parent Functional scope (draft whitelist is base_resume keys, not structure fallback). No product change. Susan can reverse on parent UAT if the flip is wrong. |
| **discuss** — validate (`base_resume`) vs persist (`resolve_resume_structure` enabled catalog) divergence | **Out of scope this child** (Boundaries / siblings). Documented for AST-1271 / AST-1272 / future watch. No product change. |
| **discuss** — AST-1269 test-tree content via `origin/tests` | **Already cleared** on tip by Radia's merge-clean gate before `docs(AST-1270)`. No further action. |

No product code changes in resolve. Commit: `resolve(AST-1270): — clean`.
