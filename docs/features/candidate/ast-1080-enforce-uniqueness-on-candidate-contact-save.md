<!-- linear-archive: AST-1080 archived 2026-08-11 -->

## Linear archive (AST-1080)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1080/enforce-uniqueness-on-candidate-contact-save-verify-unique-contact  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1045 — Verify unique contact info  
**Blocked by / blocks / related:** parent: AST-1045

### Description

## What this implements

On the candidate contact save path: apply within-candidate dedupe and cross-candidate uniqueness per the config contract sibling; hard-fail collisions (toast-ready clear domain error for callers); emit Style D debug on touched `debug=True` paths. After AST-1079. Does **not** own config vocabulary (AST-1079), library schema (AST-1014), or Profile/Admin contact UI (AST-1065).

## Acceptance criteria

- [X] 1. Saving contact data for a candidate that would duplicate a uniqueness-scoped contact value already held by a **different** candidate is refused (hard-fail); the other candidate’s data is unchanged.
- [X] 2. Saving contact data that contains within-candidate duplicates among uniqueness-scoped values avoids adding the same contact info twice for that candidate (no residual duplicate list entries / dual-field copies for scoped fields).
- [X] 3. A refused uniqueness save surfaces a clear error to the save caller suitable for UI/API display (toast); success path still persists normalized contact as today.
- [X] 4. Touched backend `debug=True` uniqueness/save paths emit per-step found/recorded Style D lines (index header + `|` detail; long content truncated).
- [X] 5. After enforcement, two live candidates cannot both hold the same uniqueness-scoped email going forward.

## Boundaries

- [X] Does **not** own config vocabulary (AST-1079).
- [X] Does **not** own library schema (AST-1014).
- [X] Does **not** own Profile/Admin contact UI (AST-1065).
- [X] Does **not** silently merge candidate records on collision.

## In scope

- [X] new contact uniqueness gate on save (proposed) — `_enforce_contact_uniqueness` in `src/core/candidate.py` on `save_candidate_data` / initiate paths
- [X] `astral.standards.data-raises-caller-logs` — core raises toast-ready `ValueError`; UI already surfaces
- [X] `astral.standards.debug-contract-gated` — Style D on uniqueness steps when `debug=True`
- [X] `astral.layers.import-direction` — gate in core; reads `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` from utils
- [X] `astral.layers.core-vs-external-bright-line` — no external I/O in uniqueness gate
- [X] `astral.standards.no-hardcoded-sets` — path/compare vocabulary only from AST-1079 config
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/candidate/ast-1080-enforce-uniqueness-on-candidate-contact-save.md`

## Considered but excluded

- [X] `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` vocabulary — AST-1079 (`src/utils/config.py`)
- [X] Contact library schema / name columns — AST-1014
- [X] Profile / Admin contact UI / toast component redesign — AST-1065 (`src/ui/`)
- [X] `get_candidate_id_for_query` match-semantics rework — AST-1047 (Done); this ticket only scans live candidates for collisions
- [X] Legacy duplicate cleanup / migration — parent OQ#4 locked “there won’t be duplicates”
- [X] Batch claim/process, candidate state machine, dispatcher — N/A

## Notes for planning

After #1 (AST-1079). Hard-fail on cross-candidate collision. All contact info in uniqueness scope per parent open answers.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1045-verify-unique-contact-info`, child `sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T00:23:07.240Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending tip ancestry includes `39cb7ffa Merge remote-tracking branch 'origin/dev' into sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save` (from publish-ref refresh). validate-sub-log refuses that shape.

@Ada Lovelace — rebuild `origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save` so AST-1080 commits sit on current `origin/ftr/AST-1045-verify-unique-contact-info` (and absorb `origin/dev` via ftr, not a `Merge remote-tracking branch 'origin/dev'` commit). Keep plan/code/merge-tests/test/docs/resolve sequence. Force-with-lease republish only if history rewrite is required.

— Chuckles

#### radia — 2026-07-31T00:21:25.758Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1080
**Publish ref:** `6ebd64574c2590f396d508064fb1972486fb2b26` (`origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save`)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save` — paths: `src/core/candidate.py` (modify), `src/utils/config.py` (modify; AST-1079 ancestry), `docs/features/candidate/ast-1080-….md` (add), `docs/features/candidate/ast-1079-….md` (add; ancestry), `docs/test-bible/core/candidate.md` (modify), `tests/component/core/test_candidate.py` (modify). Layers: `core`, `utils`, `docs`. Change types: `add`, `modify`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No graded-confidence / consult work |
| astral.agent.do-task-delegation | scoped | conforms | No do_task / agent_task changes |
| astral.agent.grade-vector-validation | scoped | conforms | No grade validation work |
| astral.batch.batch-id-first | scoped | conforms | No batch claim API changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id work |
| astral.batch.claim-process-release | scoped | conforms | No batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | scoped | conforms | Paths/compare only from AST-1079 config; no new hardcoded sets |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths {artifacts/**,scripts/spikes/**} no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs only; no spike notes under docs/features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file per ticket under docs/features/candidate/ |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only test-tree + merge-tests |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` only `src/core/candidate.py`; Betty owns tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Gate in core; no external I/O |
| astral.layers.import-direction | scoped | conforms | Core → utils config + existing database; no UI |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ {core,utils,docs}=∅ |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI; toast via existing API ValueError→400 |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers {ui} ∩ {core,utils,docs}=∅ |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core raises toast-ready ValueError; data not inventing uniqueness |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} ∩ {core,utils,docs}=∅ |
| astral.standards.debug-contract-gated | scoped | conforms | Style D index/detail only when debug=True on save gate |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shared token collect/compare; one enforce helper for save+initiate |
| astral.standards.in-scope-only | scoped | conforms | This ticket’s code() is candidate.py only; config ancestry is AST-1079 |
| astral.standards.logging-via-utils | scoped | conforms | get_logger + truncate_debug_content; no stdlib logger |
| astral.standards.no-cross-contamination | scoped | conforms | Stays on candidate contact write path |
| astral.standards.no-hardcoded-sets | scoped | conforms | Uniqueness vocabulary only from CANDIDATE_CONTACT_UNIQUENESS_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | Helpers placed after normalize_contact_urls matching file org |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data import (config ancestry only) |
| astral.state.core-decides-transitions | scoped | conforms | No candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job-state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers {ui} ∩ {core,utils,docs}=∅ |
| astral.ui.naming-conventions | scoped | not-applicable | layers {ui} ∩ {core,utils,docs}=∅ |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single merge-tests(AST-1080) SHA lands Betty tip |
| orch.git.commit-vocabulary | universal | conforms | plan/docs/code/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Publish only to origin/sub/AST-1045/AST-1080-… |
| orch.git.ftr-sub-topology | universal | conforms | Matches parent Git table child ref |
| orch.git.merge-on-checkout | universal | conforms | Worktree merge of origin/ftr clean before docs() |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None on publish tip |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub/AST-1045/AST-1080-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree astral-AST-1045 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Collapse vs hard-fail cite locked parent OQs |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches Stage 1 helpers + wire points |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test() + merge-tests only on test-tree paths |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer Ada stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role hooks respected on publish path |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| contact uniqueness gate on save (proposed) | conforms | `_enforce_contact_uniqueness` on save + initiate paths |

Active `astral.patterns.*` covered in statutes table.

## Plan adherence

Stage 1 delivered as planned: helpers after `normalize_contact_urls`; within collapse + cross hard-fail; toast-ready `ValueError` shape; Style D on `save_candidate_data(debug=True)`; initiate/prospect gated with `debug=False`; proposed-contact inline merge + `blob["contact"] = proposed` per plan (no private `_deep_merge`). Self-Assessment **Single-Component / high / Medium** matches footprint. Boundaries held vs AST-1079 / AST-1065 / AST-1014. No `conf-!!-NONE`.

## Findings

**discuss (straggler):** Joan plan-rubric Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.utils-data-late-import-only`, `astral.ui.single-gunicorn-worker` (plan Files Changed = core only). Three-dot vs `origin/dev` (docs/features + Betty test-tree + AST-1079 `config.py` ancestry) puts them in scope. All six score **conforms** — no product fix.

No fix-now.

## What’s solid

Config-driven token collection; within-candidate collapse before cross scan; raise before persist; Style D uses `debug_index` / `debug_detail` / `truncate_debug_content` under `func=enforce_contact_uniqueness`.

## Notes

Joan plan-rubric verdict attached (APPROVED). Joan’s non-blocking discusses (inline merge parity; `list_candidates` scan cost) remain acceptable — implementation matches the plan’s prescribed inline merge comment.

context_tokens≈48000

#### betty — 2026-07-31T00:17:20.980Z
## QA test manifest

`origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save` @ `24fe2c56` (`merge-tests(AST-1080): origin/tests 30daab9a`).

1. `tests/component/core/test_candidate.py::TestAst1080ContactUniqueness` — within-candidate collapse (reply email / websites); cross-candidate casefold hard-fail; same-candidate keep; initiate collision; Style D debug outcomes

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1080ContactUniqueness \
  -q
```

**Bible sha256** (`git show origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save:docs/test-bible/core/candidate.md`):
- `docs/test-bible/core/candidate.md` `068ca45dc364db9a6020687f848d13868229c00514b36a0b91af482bedd4d339`

— Betty

#### joan — 2026-07-31T00:07:11.504Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1080
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 cross-candidate collision hard-fail; other unchanged | Stage 1 — `_find_cross_candidate_contact_collision` + `ValueError`; no persist after raise |
| AC2 within-candidate avoid duplicate contact info | Stage 1 — `_dedupe_contact_within` collapse (not hard-fail) |
| AC3 fields/compare in config | N/A — boundary (AST-1079); this child only reads `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` |
| AC4 clear error to save caller (toast) | Stage 1 — toast-ready `ValueError` message; API→400 pattern cited |
| AC5 Style D debug on touched uniqueness/save paths | Stage 1 — `_enforce_contact_uniqueness` Style D when `debug=True` on `save_candidate_data` |
| AC6 two live candidates cannot share uniqueness-scoped email going forward | Stage 1 — cross-candidate gate on save + initiate paths |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 helpers + wire save/initiate | Purpose/Functional scope uniqueness gate on save; new pattern “contact uniqueness gate on save”; child AC1–5; parent OQ#2 collapse / OQ#3 hard-fail |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Sub publish path only |
| orch.git.flow-direction-inviolable | conforms | Publish origin/sub/… only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1045/AST-1080-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1045 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Collapse vs hard-fail cite locked parent OQs |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed + Done-when + Decisions |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits; Betty owns formal tests |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded consult confidence work |
| astral.agent.do-task-delegation | conforms | No do_task / agent_task changes |
| astral.agent.grade-vector-validation | conforms | No grade validation work |
| astral.batch.batch-id-first | conforms | No batch claim API changes |
| astral.batch.batch-id-format | conforms | No batch_id work |
| astral.batch.claim-process-release | conforms | No batch processing |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | conforms | Paths/compare only from AST-1079 config; no new hardcoded sets |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Gate in core; no external I/O |
| astral.layers.import-direction | conforms | Core → utils config + database; no UI |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.standards.data-raises-caller-logs | conforms | Core raises `ValueError`; UI/API surfaces; data not inventing uniqueness |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` on save gate |
| astral.standards.dry-and-focused-functions | conforms | Shared token collect/compare; wire initiate+save via one enforce helper |
| astral.standards.in-scope-only | conforms | candidate.py only; config/UI/schema/legacy cleanup excluded |
| astral.standards.logging-via-utils | conforms | Uses existing get_logger / truncate_debug_content |
| astral.standards.no-cross-contamination | conforms | Stays on candidate contact write path |
| astral.standards.no-hardcoded-sets | conforms | Uniqueness vocabulary only from config |
| astral.standards.public-then-helpers | conforms | Helpers placed after existing `normalize_contact_urls` matching file org |
| astral.state.core-decides-transitions | conforms | No candidate state transitions |
| astral.state.job-prior-states-enforced | conforms | No job-state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch daisy-chain |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {core} empty
- astral.layers.ui-config-driven-business-logic — layers ∩ plan {core} empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan {core} empty
- astral.standards.database-header-inventory — layers ∩ plan {core} empty
- astral.standards.utils-data-late-import-only — layers ∩ plan {core} empty
- astral.ui.frontend-file-placement — layers ∩ plan {core} empty
- astral.ui.naming-conventions — layers ∩ plan {core} empty
- astral.ui.single-gunicorn-worker — layers ∩ plan {core} empty

## Findings

None fix-now.

**discuss (non-blocking):** `save_candidate_data` rebuilds proposed contact with an inline merge instead of `database._deep_merge` (private). Plan requires matching overwrite/list-replace semantics — engineer must keep that parity or stop on parent if the live merge helper diverges.

**discuss (non-blocking):** Cross-candidate check scans all live candidates via `list_candidates` — same family as existing lookup scans; acceptable for this epic; not a plan defect.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium honest; initiate paths gated with `debug=False` (no debug kwarg today) while Style D is on `save_candidate_data(debug=True)`.

**R6:** Definition fidelity pass (enforce only). Layer/import pass. Config consume-only pass. Within=collapse / cross=hard-fail matches OQs. No UI/schema/legacy cleanup creep.

context_tokens≈42000

— Joan

#### ada — 2026-07-31T00:04:47.922Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save/docs/features/candidate/ast-1080-enforce-uniqueness-on-candidate-contact-save.md

`origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save` @ `6311223e`

**Scope:** Single-Component — uniqueness gate helpers + wire into `save_candidate_data` / `initiate_candidate` / `initiate_prospect_candidate` in `src/core/candidate.py` only.

**Conf:** high — AST-1079 config is on ftr; API already maps `ValueError` → 400; `list_candidates` + path resolve patterns exist from lookup.

**Risk:** Medium — collapse/collision mistakes can block good saves or miss cross-candidate leaks; limited to contact write paths.

---

# AST-1080 — Enforce uniqueness on candidate contact save

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1080/enforce-uniqueness-on-candidate-contact-save-verify-unique-contact  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info  

**Publish ref (origin):** `sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save`  
**Parent integration ref:** `ftr/AST-1045-verify-unique-contact-info`

On the candidate contact **save** path, apply within-candidate dedupe and cross-candidate uniqueness using `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` (AST-1079): collapse duplicate identity tokens inside one candidate’s contact blob, hard-fail when a token is already held by a different live candidate, raise a toast-ready `ValueError`, and emit Style D debug when `debug=True`. Does **not** change the config vocabulary, library schema, or Profile/Admin UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Import uniqueness config; add private uniqueness helpers; call gate from `save_candidate_data`, `initiate_candidate`, and `initiate_prospect_candidate` after URL normalize / before DB write; Style D on touched debug paths | core |

---

## Stage 1: Uniqueness helpers + wire into contact write paths

**Done when:** Saving contact via `save_candidate_data` (and create via `initiate_candidate` / `initiate_prospect_candidate`) dedupes within-candidate uniqueness tokens in the contact blob, refuses cross-candidate collisions with a clear `ValueError` (existing API → HTTP 400 / toast), leaves the other candidate unchanged, and emits Style D found/recorded lines when `debug=True`. No config.py / UI / data-layer schema edits.

1. In `src/core/candidate.py`, add `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` to the existing `from src.utils.config import (...)` list. Update the module docstring **In-scope** line to mention contact uniqueness enforcement on save (AST-1080) next to `save_candidate_data`.

2. Add private helpers **below** `normalize_contact_urls` and **above** `save_candidate_data` (public-then-helpers: keep public functions first; place new helpers with the other contact helpers near `normalize_contact_urls`, or at the bottom helper section if that file already groups helpers after publics — **match existing file organization**: `normalize_contact_urls` is already among early helpers; add the new helpers immediately after it).

   **`_uniqueness_compare_token(raw: Any, mode: str) -> str`**
   - If `raw` is not a `str`, return `""`.
   - Strip whitespace; if empty, return `""`.
   - If `mode == "casefold"`: return `stripped.casefold()`.
   - If `mode == "exact"`: return `stripped`.
   - Otherwise treat as `"casefold"` (defensive; config asserts only those two modes).

   **`_iter_uniqueness_path_values(source: Dict[str, Any], dotted_path: str) -> list[str]`**
   - Resolve values for one config path against either a full candidate row (has `candidate_data`) **or** a bare contact dict wrapped as `{"candidate_data": {"contact": contact}}` / a synthetic row.
   - Reuse `_lookup_path_value` for scalar/email/slack string paths (it already strips; callers still run compare-token).
   - For `list_paths` entries (`contact.websites`): walk `candidate_data.contact.websites` (or contact.websites on a contact-only view). If the value is a `list`, yield each element that is a non-empty `str` after strip; if a single `str`, yield that one; ignore other types.
   - Return a list of raw stripped strings (not yet casefold/exact compared).

   **`_collect_uniqueness_tokens_from_candidate(candidate: Dict[str, Any]) -> list[tuple[str, str]]`**
   - Read `CANDIDATE_CONTACT_UNIQUENESS_CONFIG`.
   - Emit `(compare_token, path)` for every non-empty token from:
     - each path in `email_paths` with `compare["email"]`
     - each path in `scalar_paths` with `compare["scalar"]`
     - each path in `list_paths` with `compare["list"]` (one token per list entry)
     - each path in `slack_user_id_paths` with `compare["slack_user_id"]`
   - Skip empty compare tokens.
   - Deterministic path order: email_paths, then scalar_paths, then list_paths (list index order), then slack_user_id_paths.

   **`_collect_uniqueness_tokens_from_contact(contact: Dict[str, Any]) -> list[tuple[str, str]]`**
   - Build a synthetic candidate row `{"candidate_data": {"contact": contact}}` and call `_collect_uniqueness_tokens_from_candidate`. (Write-side proposed contact has no transitional `profile.*`; those paths simply resolve empty — correct.)

   **`_dedupe_contact_within(contact: dict) -> list[str]`** (mutates `contact` in place)
   - Parent OQ#2: avoid adding the same contact info twice for one candidate — **collapse**, do not hard-fail.
   - Walk uniqueness paths in the same order as `_collect_uniqueness_tokens_from_candidate` against this contact.
   - Keep a `seen: set[str]` of compare tokens already retained.
   - For scalar/email/slack paths (`contact.<key>` only — skip paths that do not start with `contact.`): if the field’s compare token is non-empty and already in `seen`, set that field to `""` and append a short note like `cleared contact.reply_email (duplicate)`; else if non-empty, add to `seen`.
   - For `contact.websites` when it is a `list`: rebuild the list keeping first occurrence of each non-empty compare token; drop later duplicates and any entry whose token was already seen from an earlier scalar/email field; assign the rebuilt list back; note removals.
   - Return the list of human-readable notes (may be empty). Do **not** invent phone digit normalization or extra URL canonicalization beyond what `normalize_contact_urls` already did.

   **`_find_cross_candidate_contact_collision(candidate_id: str, contact: dict) -> Optional[tuple[str, str, str]]`**
   - Tokens from `_collect_uniqueness_tokens_from_contact(contact)`.
   - For each other row in `list_candidates(include_deleted=False)` whose `astral_candidate_id` ≠ `candidate_id` (string strip compare): collect tokens via `_collect_uniqueness_tokens_from_candidate` (includes transitional `profile.*` email paths on the other row).
   - If any compare token overlaps, return `(token_display, path, other_candidate_id)` where `token_display` is a truncated raw-ish form suitable for errors (use the colliding stripped value from **this** contact’s path, not the other candidate’s id in the user message — see step 3).
   - Else return `None`.

   **`_enforce_contact_uniqueness(candidate_id: str, contact: dict, *, debug: bool = False) -> None`**
   - Assumes `contact` is a `dict` already passed through `normalize_contact_urls`.
   - If `debug`: `logger.set_debug_flag(True)` is the caller’s job when they already set it; still emit Style D under this function when `debug` is True.
   - Step A — within-candidate: `notes = _dedupe_contact_within(contact)`. If `debug`: one `debug_index` with `func="enforce_contact_uniqueness"`, `identifier=candidate_id`, `outcome="recorded|within_dedupe"` (or `found|within_clean` when notes empty), and `debug_detail` lines for notes / token counts (truncate long payloads with `truncate_debug_content`).
   - Step B — cross-candidate: `hit = _find_cross_candidate_contact_collision(candidate_id, contact)`. If hit: if `debug`, emit `debug_index` with `outcome="found|cross_collision"` and detail including `path`, truncated value, and `other_candidate_id`. Then **`raise ValueError`** with exactly this message shape (toast-ready, no other candidate id in the user string):

     ```text
     This contact info is already used by another candidate ({value}).
     ```

     where `{value}` is the colliding stripped value truncated to **80** characters if longer. Do **not** persist after this raise.
   - If no collision and `debug`: `debug_index` with `outcome="recorded|cross_clear"`.

⚠️ **Decision — gate lives in core on write paths, not in UI or data:** Parent architecture + citations require core validation; `api_candidate` already maps exceptions to `{"error": str(e)}` 400 (toast-ready). Data layer stays raise-only / no log.

⚠️ **Decision — within = collapse, cross = hard-fail:** Locked parent OQs #2 and #3. Collapse prefers earlier paths in config order; websites list keeps first unique entries.

⚠️ **Decision — shared helper for initiate + save:** Create paths (`initiate_candidate`, `initiate_prospect_candidate`) also write contact blobs today; collisions on create must hard-fail the same way. Do not leave a bypass around `save_candidate_data`.

3. Wire **`save_candidate_data`** after `normalize_contact_urls(contact)` and **before** building debug `steps` / calling `database.save_candidate`:

   ```python
   contact = blob.get("contact")
   if isinstance(contact, dict):
       normalize_contact_urls(contact)
       # Proposed contact after merge (merge=True) or replace payload (merge=False).
       if not replace:
           existing = database.get_candidate(candidate_id) or {}
           existing_cd = existing.get("candidate_data") or {}
           if not isinstance(existing_cd, dict):
               existing_cd = {}
           existing_contact = existing_cd.get("contact")
           if isinstance(existing_contact, dict):
               proposed = copy.deepcopy(existing_contact)
               # Same semantics as database._deep_merge for one contact overlay:
               for k, v in contact.items():
                   if (
                       k in proposed
                       and isinstance(proposed[k], dict)
                       and isinstance(v, dict)
                   ):
                       # nested dict rare under contact; still recurse shallowly
                       inner = copy.deepcopy(proposed[k])
                       for ik, iv in v.items():
                           inner[ik] = iv
                       proposed[k] = inner
                   else:
                       proposed[k] = v
           else:
               proposed = copy.deepcopy(contact)
       else:
           proposed = copy.deepcopy(contact)
       _enforce_contact_uniqueness(candidate_id, proposed, debug=debug)
       blob["contact"] = proposed  # persist deduped contact
   ```

   Use `copy` (already imported). Do **not** call `database._deep_merge` from core (private). The inline merge above must match deep-merge overwrite rules for contact’s flat keys + list replace for `websites`.

   If `contact` is not a dict (missing / wrong type), skip the gate (unchanged behavior).

4. Wire **`initiate_candidate`** and **`initiate_prospect_candidate`** after `normalize_contact_urls(contact)` and **before** `database.save_candidate`:

   ```python
   if isinstance(contact, dict):
       normalize_contact_urls(contact)
       _enforce_contact_uniqueness(astral_candidate_id, contact, debug=False)
   ```

   No `debug=` param on these create APIs today — pass `debug=False`. Do not expand their signatures.

5. Do **not** edit `src/utils/config.py`, `src/data/database.py`, UI/React, or Profile/Admin toast components (AST-1065). Do **not** silently merge two candidate records. Do **not** add legacy duplicate cleanup / migration. Do **not** change `get_candidate_id_for_query` match semantics.

**Done when (recheck):** Manual or REPL-level checks (Betty owns formal tests):

- Same email (case-insensitive) on candidate B’s save while A holds it → `ValueError` with the message above; A unchanged.
- `contact_email` and `reply_email` set to the same address on one save → reply cleared (or later path cleared), save succeeds, one retained value.
- Duplicate strings in `websites` → list collapsed; save succeeds.
- `debug=True` on `save_candidate_data` with contact changes → Style D index headers + `|` detail for within/cross steps (and existing library-write lines still work).

---

## Self-Assessment

**Scope:** `Single-Component` — `src/core/candidate.py` only; reads AST-1079 config; no UI/data schema.

**Conf:** `high` — config contract shipped; write path and API `ValueError`→400 pattern already exist; lookup already scans `list_candidates` for path values.

**Risk:** `Medium` — wrong collapse/collision logic can block legitimate saves or miss cross-candidate leaks; limited to contact write paths.

---

## Code Rules check (§8)

| Rule | Result |
|------|--------|
| §1.3 DRY | Token collection / compare shared; path vocabulary only from `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` |
| §1.4 no-hardcoded-sets | No inline unique-field lists in core |
| §2.1 config source of truth | Compare modes + paths from config |
| §1.5.1 debug-contract-gated | Style D only when `debug=True` on touched save gate |
| §2.4 batch / §2.6 state | N/A |
| §3.3 imports | Core → utils config + existing database; no UI/external |
| data-raises-caller-logs | Core raises `ValueError`; UI already logs/surfaces |

No conflicts requiring `conf-!!-NONE`.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-1080 |
| Publish ref | `origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save` |
| Built | `a80e51c5c3e233afea30d0b73331072e8f0f2535` |
| Notes | Stage 1 — within collapse + cross hard-fail on `save_candidate_data` / initiate paths via AST-1079 config. |

### Radia — code-rubric.v1

`[code-rubric] revision=1` · **Overall:** DISCUSS (stragglers only; product CLEAN)

**What’s solid**
- Gate matches Stage 1: config-driven tokens, within collapse, cross `ValueError` toast shape, Style D on `save_candidate_data(debug=True)`, initiate paths gated with `debug=False`.
- Proposed-contact merge + `blob["contact"] = proposed` follows plan (no private `_deep_merge` call).
- Engineer `code()` = `src/core/candidate.py` only; Betty owns test-tree.

**Issues**
- **discuss (straggler):** Joan excluded docs/features + test-tree + utils-adjacent path statutes at plan time; three-dot vs `origin/dev` (incl. AST-1079 ancestry) brings them in scope. All score **conforms** — no product fix.

**Recommended actions**
- Ada: no code change for stragglers; `resolve-child` → User Testing unless a discuss thread is opened.

## Resolution

**Date:** 2026-07-31  
**Review tip:** `6ebd6457` (`docs(AST-1080): Radia review — contact uniqueness gate`)  
**Outcome:** clean — no fix-now; no product or config changes.

| Finding | Disposition |
| -- | -- |
| discuss (straggler) — Joan excluded docs/test-tree/utils-adjacent statutes at plan time; three-dot scores conforms | Accepted as documented; no code change |
| Joan non-blocking discusses (inline merge parity; list_candidates scan) | Left as planned; implementation matches plan |
