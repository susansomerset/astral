# AST-1365 — Ideal Day library + token

**Linear:** [AST-1365](https://linear.app/astralcareermatch/issue/AST-1365/ideal-day-library-token-add-ideal-day-to-the-set-of-candidate-context)
**Parent:** [AST-1360](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc) — Add `ideal_day` to the set of candidate context (strengths, priorities, etc.)
**Publish ref:** `sub/AST-1360/AST-1365-ideal-day-library-token`

Add `ideal_day` as a first-class candidate **context** library key (peer of strengths / priorities / deal_breakers / backstory): register it in `CANDIDATE_LIBRARY_CONFIG`, expose `{$IDEAL_DAY}` via `TOKEN_SOURCES`, drive the context completeness gate from a config-owned key list that includes Ideal Day, and document the field in `CANDIDATE_DATA_MODEL.md`. Persistence already deep-merges `candidate_data.context.*` through `save_candidate_data` — no new save API. This ticket does **not** own Candidate nav/UI (AST-1366), Topic Menu informs / Estelle allowlists (AST-1367), or JD/DO/LIKE craft prompt text (AST-1368).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `ideal_day` to `CANDIDATE_LIBRARY_CONFIG["context_keys"]`; add `context_completeness_keys` (five gated prose keys incl. `ideal_day`) with ⊆ `context_keys` asserts; add `TOKEN_SOURCES["IDEAL_DAY"]` | utils |
| `src/core/candidate.py` | `check_context_complete` reads completeness keys from `CANDIDATE_LIBRARY_CONFIG` (remove module `_CONTEXT_TEXT_KEYS`); update docstring | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `context.ideal_day` / `{$IDEAL_DAY}` / Gate=Yes; fix “four context fields” wording | docs |

**Out of scope (do not touch):**

| File / area | Owner |
|-------------|--------|
| `NAV_CONFIG`, `routes.tsx`, `CandidateIdealDay.tsx` / `ContextTextPage` wiring | AST-1366 |
| `TOPIC_MENU_CONFIG["informs"]`, `TOPIC_MENU_GEN_CONFIG` packet/patch allowlists | AST-1367 |
| `data/admin/agent_task.json` / craft rubric prompt bodies for JD/DO/LIKE | AST-1368 |
| `DATA_SHAPES` Profile detail | N/A — strengths/priorities/deal_breakers/backstory are **not** Profile shape fields today (dedicated context pages); Ideal Day follows that pattern under AST-1366 |
| `INTAKE_CONFIG["build_field_paths"]`, `TASK_CONFIG` intake/bootstrap schemas | Parent: no new intake interview phase for Ideal Day |
| Migrations / backfill of existing candidates | Parent: empty until edited or Topic Menu writes |

## Stages

### Stage 1: Config vocabulary, completeness keys, token

**Done when:** `ideal_day` is in `CANDIDATE_LIBRARY_CONFIG["context_keys"]`; `CANDIDATE_LIBRARY_CONFIG["context_completeness_keys"]` is exactly the five gated keys including `ideal_day` and each is asserted ⊆ `context_keys`; `TOKEN_SOURCES["IDEAL_DAY"]` points at `context.ideal_day`; importing `src.utils.config` still succeeds (existing Topic Menu / preamble asserts unchanged).

1. In `src/utils/config.py`, inside `CANDIDATE_LIBRARY_CONFIG`, extend `context_keys` so `ideal_day` sits with the other gated prose peers — insert **`"ideal_day"` immediately after `"deal_breakers"`** in the existing tuple (before `"writing_preferences"`):

```python
"context_keys": (
    "bio_summary", "backstory", "strengths", "priorities", "deal_breakers",
    "ideal_day",
    "writing_preferences", "hopes", "interests", "concerns",
    "raw_resume", "raw_profile", "raw_sample",
),
```

2. Still inside `CANDIDATE_LIBRARY_CONFIG`, add a new key **after** `context_key_remap` (before `name_columns`):

```python
"context_completeness_keys": (
    "strengths",
    "priorities",
    "deal_breakers",
    "backstory",
    "ideal_day",
),
```

   ⚠️ **Decision:** Completeness key list lives in `CANDIDATE_LIBRARY_CONFIG` (not a module constant in `candidate.py`) so `astral.standards.no-hardcoded-sets` / `astral.config.config-source-of-truth` hold. Order matches today’s `_CONTEXT_TEXT_KEYS` with `ideal_day` appended — gate iteration order is not product-visible.

3. Immediately after the `CANDIDATE_LIBRARY_CONFIG = { ... }` block (before `COVER_FROM_BLOCK_CONFIG`), add load-time asserts:

```python
assert len(CANDIDATE_LIBRARY_CONFIG["context_completeness_keys"]) == len(
    set(CANDIDATE_LIBRARY_CONFIG["context_completeness_keys"])
)
for _ck in CANDIDATE_LIBRARY_CONFIG["context_completeness_keys"]:
    assert _ck in CANDIDATE_LIBRARY_CONFIG["context_keys"], _ck
```

4. Do **not** change `TOPIC_MENU_CONFIG["informs"]`, the equality assert that locks that tuple, or the loop `for _ctx in ("strengths", "priorities", "deal_breakers", "backstory")` that only checks those informs homes ⊆ `context_keys`. AST-1367 owns adding `ideal_day` to informs; once this stage lands, `ideal_day` is already a valid library home for that sibling.

5. Do **not** change `TOPIC_MENU_GEN_CONFIG["packet_context_keys"]` / `patchable_context_keys` (AST-1367).

6. In `TOKEN_SOURCES`, in the `# context (candidate-provided, unaltered)` cluster, add immediately after `"BACKSTORY"`:

```python
"IDEAL_DAY":            {"source": "candidate", "path": "context.ideal_day"},
```

   Same shape as `STRENGTHS` / `PRIORITIES` / `DEAL_BREAKERS` / `BACKSTORY`. Unset path already resolves to empty string via existing `resolve_tokens` + `_value_to_str` (AC2).

7. Do **not** add Ideal Day to `NAV_CONFIG`, `DATA_SHAPES`, `INTAKE_CONFIG["build_field_paths"]`, or any `TASK_CONFIG` response_schema.

### Stage 2: Completeness gate + data-model doc

**Done when:** `check_context_complete` requires non-empty stripped `context.ideal_day` in addition to the previous four keys (unless progress_rank already ≥ `ALL_TOPICS_READY`); module no longer defines `_CONTEXT_TEXT_KEYS`; `CANDIDATE_DATA_MODEL.md` lists Ideal Day as a gated context key with token `{$IDEAL_DAY}`.

1. In `src/core/candidate.py`, delete:

```python
_CONTEXT_TEXT_KEYS = ("strengths", "priorities", "deal_breakers", "backstory")
```

2. Update `check_context_complete` docstring from “all four context text fields” to reference config, e.g. “all `CANDIDATE_LIBRARY_CONFIG['context_completeness_keys']` are non-empty (no state write).”

3. Replace the gate loop body so it iterates config:

```python
ctx = (candidate.get("candidate_data") or {}).get("context", {})
if not isinstance(ctx, dict):
    ctx = {}
for key in CANDIDATE_LIBRARY_CONFIG["context_completeness_keys"]:
    if not (ctx.get(key) or "").strip():
        return False
return True
```

   Keep the existing progress_rank short-circuit (`rank >= ALL_TOPICS_READY`) unchanged and **before** the context loop. `CANDIDATE_LIBRARY_CONFIG` is already imported in this module.

4. Do **not** change `save_candidate_data` — merge already persists arbitrary `context` keys. AC1 is satisfied when a caller (admin API / future Ideal Day page) POSTs `{ "context": { "ideal_day": "<prose>" } }` and GET returns it; vocabulary + gate are this ticket’s product surface.

5. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under **context (candidate-provided prose + raw sources)**:

   - Add a table row after `context.backstory` (or after `context.deal_breakers` if grouping gated peers):  
     `| \`context.ideal_day\` | \`{$IDEAL_DAY}\` | Yes | Ideal workday prose |`
   - Change the later sentence that says `check_context_complete()` reports whether **the four** context fields are populated to say **the gated** context fields (`CANDIDATE_LIBRARY_CONFIG["context_completeness_keys"]`, including Ideal Day) — still **no** state write.

6. Do **not** edit archived plan docs (`ast-217-*`, `ast-218-*`, `ast-1014-*`).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1365
**Overall:** APPROVED
**Publish ref:** `sub/AST-1360/AST-1365-ideal-day-library-token` @ `30e71a61fc979894fd693df5692f865c18355c00`

## Traceability
AC1→Stage 2 (persist/read via existing `save_candidate_data` + PUT `/api/candidates/<id>/data`); AC2→Stage 1 `TOKEN_SOURCES["IDEAL_DAY"]` → `context.ideal_day`; AC3→Stage 1 `context_completeness_keys` + Stage 2 `check_context_complete` config loop.

### Findings

**acceptable** — Stage 2 AC1 says “POST”; live API is PUT merge on `/api/candidates/<id>/data`. Semantics match; wording only.

**acceptable** — Deleting `_CONTEXT_TEXT_KEYS` will break `tests/component/core/test_candidate.py` (`TestCheckContextCompleteExtended`); plan omits test touch. Expected at `test-child` / Betty manifest — not a plan defect for this child’s stated files.

**acceptable** — Linear assignee is Ada (not Joan) at fetch time; Chuckles seeded this spawn — no plan impact.

context_tokens≈42000

## Review (build stub)

**Built:** `astral-AST-1360` @ `d190d916` on `origin/sub/AST-1360/AST-1365-ideal-day-library-token`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `30e71a61` | Plan doc |
| 1 | `5caa4ebf` | `ideal_day` in library + `context_completeness_keys` + `{$IDEAL_DAY}` |
| 2 | `d190d916` | `check_context_complete` from config + data-model row |

**Verify:** `python3 -m py_compile` on `src/utils/config.py`, `src/core/candidate.py` — pass; import + `resolve_tokens` empty/set Ideal Day — pass.

**Note for Betty:** Joan flagged `tests/component/core/test_candidate.py` (`TestCheckContextCompleteExtended`) will need the fifth key once Ideal Day is gated; no test-tree edits in this build.

## Radia review

# Radia review — AST-1365

**Ticket:** AST-1365  
**Parent:** AST-1360  
**Publish ref:** `origin/sub/AST-1360/AST-1365-ideal-day-library-token` @ `0437d9c87e1d8bb65396db78d86b1f171305fa06`  
**Diff baseline:** `origin/dev...origin/sub/AST-1360/AST-1365-ideal-day-library-token` (8 files, +350/−8)  
**Status gate:** Tests Passed (spawn prompt; trusted)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1365  
**Publish ref:** `0437d9c87e1d8bb65396db78d86b1f171305fa06`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent/grade payload changes |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` / agent routing changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no rubric vector / grading changes |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch claim paths touched |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no dispatcher claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no agent-response persistence |
| `astral.config.config-source-of-truth` | scoped | conforms | `context_completeness_keys` + `IDEAL_DAY` token live in `config.py`; gate reads config |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env wiring |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact paths |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed changes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run-next / chain edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | `docs/features/candidate/ast-1365-ideal-day-library-token.md` present |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge is test-tree only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | product commits touch `src/` only; tests land via `merge-tests` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no `external/` changes |
| `astral.layers.import-direction` | scoped | conforms | `core`→`utils.config` only; no new layer bends |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/` changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | no UI layer changes |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth surface changes |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON edits |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog conflict |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed hot-path changes |
| `astral.seed.define-approved` | scoped | not-applicable | no DEFINE seed work |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator-row seeding |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no `data/` layer changes |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no schema/migration |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug logging added |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | small, focused gate refactor |
| `astral.standards.in-scope-only` | scoped | conforms | no NAV/TOPIC_MENU/craft/agent_task smuggling; explicit boundary test |
| `astral.standards.logging-via-utils` | scoped | conforms | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | domain key `ideal_day`; ticket id only in comment carve-out |
| `astral.standards.no-cross-contamination` | scoped | conforms | sibling-owned surfaces untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | `_CONTEXT_TEXT_KEYS` removed; config is source |
| `astral.standards.public-then-helpers` | scoped | conforms | public `check_context_complete` unchanged contract |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils→data late imports |
| `astral.state.core-decides-transitions` | scoped | conforms | gate still read-only (no state write) |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state machine |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run loop changes |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend files |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI files |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | tip is `merge-tests(AST-1365)` @ tests SHA |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `docs` / `test` / `merge-tests` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub-branch topology respected |
| `orch.git.ftr-sub-topology` | universal | conforms | child `sub/AST-1360/...` |
| `orch.git.merge-on-checkout` | universal | conforms | no rebase/force signals in diff |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commit stack |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/...` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1360 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs `origin/dev` only |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches staged plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a to code |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test + bible updates via Betty merge |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | n/a |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada assignee; review-only pass |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path commits in product commits |

**Active set count:** 64 rows (per `canon/statutes/README.md` harvested table). No `violates` or `needs-discussion` rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan / Joan artifact cite no `canon/patterns/**` ids |

## Plan adherence

Implementation matches Joan **APPROVED** plan (stages 1–2) on tip `0437d9c8`:

- `ideal_day` inserted after `deal_breakers` in `context_keys`.
- `context_completeness_keys` tuple + load-time uniqueness/subset asserts added.
- `TOKEN_SOURCES["IDEAL_DAY"]` → `context.ideal_day` after `BACKSTORY`.
- `_CONTEXT_TEXT_KEYS` removed; `check_context_complete` iterates config keys with `isinstance(ctx, dict)` guard; `progress_rank` short-circuit preserved.
- `CANDIDATE_DATA_MODEL.md` row + gated-field wording updated.
- Out-of-scope surfaces correctly untouched (`TOPIC_MENU_CONFIG["informs"]`, NAV, craft prompts, intake schemas).

**Estimate (2):** Footprint matches — two `src/` modules, one data-model doc, Betty test merge. No scope inflation.

**Cross-ticket boundaries:** `TestAst1365IdealDayLibraryToken::test_topic_menu_informs_exclude_ideal_day_until_sibling` locks AST-1367 boundary. No AST-1366/1368 leakage.

**Test manifest:** Betty bible entries + component tests align with qa-child manifest (`TestAst1365IdealDayLibraryToken`, revised `TestCheckContextCompleteExtended`, `TestAst1365IdealDayLibrary`). `merge-tests` commit present at tip.

**Joan straggler (C4):** Plan-rubric verdict attached (APPROVED); no Excluded-statute list in artifact — nothing to straggle.

## Findings

### fix-now

*(none)*

### discuss

*(none)*

### advisory

- **UAT / parent epic:** Candidates who previously satisfied the four legacy gated keys but have no `context.ideal_day` will now fail `check_context_complete` until Ideal Day is filled (via future AST-1366 UI or existing PUT merge). Plan + parent explicitly accept empty-until-edited — not a defect; worth noting for Susan’s UAT on AST-1360.

## What’s solid

- Config-driven completeness list with load-time asserts prevents silent drift (`astral.standards.no-hardcoded-sets` + `astral.config.config-source-of-truth`).
- Token resolution follows existing peer pattern; empty → `""` verified in tests.
- Defensive `ctx` dict guard is a small hardening beyond prior code.
- Explicit sibling-boundary test prevents accidental Topic Menu informs expansion.

## Frame diff

(none) — product diff matches plan frame; test/bible additions are pipeline-owned (Betty) and anticipated by Joan’s “tests will break” note.

## Notes

- Joan plan-rubric verdict attached; no Excluded statutes listed.
- §5f / §5g not triggered (no debug surfaces, no LLM external modules).
- C7 artifact complete.

context_tokens≈38000

---
