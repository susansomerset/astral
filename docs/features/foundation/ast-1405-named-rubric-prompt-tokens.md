# AST-1405 — Named rubric prompt tokens

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1405/named-rubric-prompt-tokens-reintroduce-the-specific-rubric-tokens
**Parent:** [AST-1404](https://linear.app/astralcareermatch/issue/AST-1404/reintroduce-the-specific-rubric-tokens) — Reintroduce the specific rubric tokens
**Publish ref:** `sub/AST-1404/AST-1405-named-rubric-prompt-tokens`

Register five named prompt tokens on the existing `TOKEN_SOURCES` registry, pin each to a fixed rubric owner, and resolve them through the same `rubric_criteria_for_token` / `_value_to_str` path `{$RUBRIC_VECTORS}` already uses. Pickers already list `TOKEN_SOURCES` keys — no UI list. `{$RUBRIC_VECTORS}` stays task-derived. Seed prompt bodies are not rewritten.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add five `TOKEN_SOURCES` rows with `source: rubric` + `owner_task_key` pin; teach `resolve_tokens` rubric branch to honor the pin and to silence missing-candidate warnings for pinned names (AST-1396 contract) | utils |

**Out of scope (do not touch):**

| File / area | Why |
|-------------|-----|
| `data/admin/agent_task.json` / seed prompt bodies | Ticket + parent: tokens become available; Susan inserts them |
| Frontend pickers (`TokenTextarea`, Manage Agents / Manage Tasks pages) | `/agents/meta/tokens` → `get_manage_agents_tokens()`; `/tasks/meta/tokens` → `get_tokens()` — both already derive from `TOKEN_SOURCES` |
| `src/core/candidate.py` `rubric_criteria_for_token` / `rubric_criteria_for_task` | Existing current-vector read path; named tokens call it with a pinned owner |
| `src/core/agent.py` `do_task` assembly | Substitution already goes through `resolve_tokens` |
| Rubric storage, craft, scoring, Artifacts, vector-feedback injection | Parent boundaries |
| `JOB_TOKEN_CONFIG` / `ANALYSIS_*` tokens | Different surface (job-scoped consult analysis text) |
| `tests/` / bible | Betty. Existing `TestAst723RubricVectorsToken.test_legacy_per_artifact_rubric_tokens_removed` currently asserts `GET_RUBRIC` / `DO_RUBRIC` / `LIKE_RUBRIC` are **absent** — that assertion is invalidated by this ticket; Betty revises it. Engineer does not patch tests. |

## Owner pins (authoritative)

Pin values are existing consumer `task_key`s from `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` — do not invent new owner strings, do not pin craft_* keys, do not pin meteorite or job-list owners.

| Token name | `owner_task_key` | Artifact key (do not put this on the registry row) |
|------------|------------------|-----------------------------------------------------|
| `GET_RUBRIC` | `grade_get` | `get_rubric` |
| `DO_RUBRIC` | `grade_do` | `do_rubric` |
| `LIKE_RUBRIC` | `grade_like` | `like_rubric` |
| `JD_RUBRIC` | `evaluate_jd` | `jobdesc_rubric` — **not** `evaluate_meteorite` / `meteorite_jobdesc_rubric` |
| `PREFILTER_RUBRIC` | `prefilter_company` | `company_prefilter` — new name; do **not** also register `COMPANY_PREFILTER` |

Do **not** register: `JOBLIST_RUBRIC`, `COMPANY_PREFILTER`, `JOBDESC_RUBRIC`.

`RUBRIC_VECTORS` stays `{"source": "rubric"}` with **no** `owner_task_key` — owner remains `rubric_owner_task_key(task_key)` (running-task owner).

⚠️ **Decision:** Spec pin key is `owner_task_key` (not `rubric_owner_task_key`). `rubric_owner_task_key` is already the function that maps a *running* task to its owner. The registry field is a fixed pin, not that lookup. Rejected: a second dict of named tokens outside `TOKEN_SOURCES` (would violate `astral.standards.no-hardcoded-sets` / config-as-source-of-truth). Rejected: `source: "named_rubric"` (parent: small extension of existing `source: rubric`, no new catalog shape).

## Stages

### Stage 1: Register pins and resolve them

**Done when:** `get_tokens()` and `get_manage_agents_tokens()` include the five names and exclude the three forbidden legacy names; `resolve_tokens("{$GET_RUBRIC}", cd, "grade_like")` with a candidate that has GET vectors substitutes GET (not LIKE); `{$RUBRIC_VECTORS}` on `grade_like` still substitutes LIKE; Ad Hoc-style `resolve_tokens("{$GET_RUBRIC}", {}, "adhoc")` returns `""` and does not log a missing-candidate / unresolved warning.

1. In `src/utils/config.py` `TOKEN_SOURCES`, immediately after the `RUBRIC_VECTORS` row, insert these five entries (keep `RUBRIC_VECTORS` itself unchanged except the comment on that row may stay). Do not reorder other keys.

```python
    # Resolved from rubric_vector rows for active task owner (AST-723).
    "RUBRIC_VECTORS":       {"source": "rubric"},
    # AST-1405: named pins — same serialize path as RUBRIC_VECTORS; owner is the pin, not the running task.
    "GET_RUBRIC":           {"source": "rubric", "owner_task_key": "grade_get"},
    "DO_RUBRIC":            {"source": "rubric", "owner_task_key": "grade_do"},
    "LIKE_RUBRIC":          {"source": "rubric", "owner_task_key": "grade_like"},
    "JD_RUBRIC":            {"source": "rubric", "owner_task_key": "evaluate_jd"},
    "PREFILTER_RUBRIC":     {"source": "rubric", "owner_task_key": "prefilter_company"},
```

2. In the same file, the `TOKEN_SOURCES` block header currently says adding a new token is one registry entry with no code change. After this stage, that remains true for a *sixth* named rubric token (add a row with `source: rubric` + `owner_task_key`). Leave the header; do not add a parallel named-token list.

3. In `resolve_tokens` `_replace`, replace **only** the `if spec["source"] == "rubric":` branch. Keep the late import of `rubric_criteria_for_token` (existing utils → core cycle break). Exact replacement:

```python
        if spec["source"] == "rubric":
            from src.core.candidate import rubric_criteria_for_token

            pinned = spec.get("owner_task_key")
            owner = pinned or rubric_owner_task_key(task_key)
            if not owner:
                _log.warning("Token {$%s} unresolved — task %r has no rubric owner", name, task_key)
                return ""
            cid = (candidate_data or {}).get("_astral_candidate_id") or ""
            if not cid:
                # AST-1405 / AST-1396: pinned names with no candidate in context (cd == {})
                # are expected empty — do not spam missing-id warnings. Unpinned
                # RUBRIC_VECTORS keeps the existing missing-id warning.
                if pinned and not candidate_data:
                    return ""
                _log.warning("Token {$%s} unresolved — missing candidate id (task=%s)", name, task_key)
                return ""
            return _value_to_str(rubric_criteria_for_token(cid, owner))
```

4. Do **not** change the candidate / config / output_type / chain / job / pronoun branches. Do **not** add a `warn_empty` kwarg. Do **not** skip substitution (leaving `{$GET_RUBRIC}` literal would flip `_enrich_tasks` `task_ready` via leftover-`{$…}` regex — same AST-1396 constraint).

5. Do **not** warn when a candidate is present and the pinned rubric list is empty — `_value_to_str([])` already returns `""`; `RUBRIC_VECTORS` already behaves that way. AC2 forbids an empty stub **when vectors exist**, not when they do not.

⚠️ **Decision:** Silence the missing-cid warning for **pinned** names only, and only when `candidate_data` is falsy (`{}` from `_enrich_tasks("")` and `_resolve_adhoc` with no candidate). Truthy token views that lack `_astral_candidate_id` still warn. `{$RUBRIC_VECTORS}` warning behavior is unchanged (AC4). Rejected: silencing all rubric warnings; rejected: gating on missing cid alone without the `pinned` check (would quiet `RUBRIC_VECTORS` on Ad Hoc load of owner tasks).

6. Hand-verify (no test-tree edits) after the change, from the epic worktree:

```bash
python3 - <<'PY'
from src.utils.config import TOKEN_SOURCES, get_tokens, get_manage_agents_tokens, resolve_tokens, rubric_owner_task_key

named = ("GET_RUBRIC", "DO_RUBRIC", "LIKE_RUBRIC", "JD_RUBRIC", "PREFILTER_RUBRIC")
forbidden = ("JOBLIST_RUBRIC", "COMPANY_PREFILTER", "JOBDESC_RUBRIC")
for n in named:
    assert TOKEN_SOURCES[n]["source"] == "rubric"
    assert TOKEN_SOURCES[n]["owner_task_key"]
    assert n in get_tokens()
    assert n in get_manage_agents_tokens()
for n in forbidden:
    assert n not in TOKEN_SOURCES
assert TOKEN_SOURCES["RUBRIC_VECTORS"] == {"source": "rubric"}
assert rubric_owner_task_key("grade_like") == "grade_like"
# Pin independence: named GET owner is grade_get even when the running task is LIKE.
assert TOKEN_SOURCES["GET_RUBRIC"]["owner_task_key"] == "grade_get"
# No-candidate silence: empty cd, pinned name → empty string (warnings checked by not exploding).
assert resolve_tokens("{$GET_RUBRIC}", {}, "adhoc") == ""
assert resolve_tokens("{$RUBRIC_VECTORS}", {}, "adhoc") == ""
print("ast-1405 registry ok")
PY
```

If any assert fails, **stop** and comment on **parent AST-1404** with the Stage-blocked format — do not invent a second registry or change picker APIs.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.** No fix-on-the-fly.
- Completes the stage on the epic worktree, commits, and publishes to `origin/sub/AST-1404/AST-1405-named-rubric-prompt-tokens`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1405
**Overall:** APPROVED
**Publish ref:** `sub/AST-1404/AST-1405-named-rubric-prompt-tokens` @ `ba66a4c7d1cf73960035e77553483bfde6fc8834`

## Traceability
AC1–6 → Stage 1 (`TOKEN_SOURCES` five pinned `source: rubric` rows + `resolve_tokens` rubric-branch pin/`owner_task_key` + AST-1396 silence for falsy `candidate_data` only).

## Findings

### acceptable
- **Location:** Stage 1 hand-verify snippet  
  **Finding:** Inline assert block checks registry membership and no-candidate silence but not live `resolve_tokens(..., cd, "grade_like")` pin-independence with a populated candidate.  
  **Recommendation:** Engineer may run the Stage “Done when” REPL check before publish; not a plan gap — implementation steps are exact.

- **Location:** Plan doc (no formal self-assessment block)  
  **Finding:** No conf/risk axes section; scope is single-file `utils` registry extension with explicit decisions and out-of-scope table.  
  **Recommendation:** Acceptable for estimate 3; no `!!-NONE` escalation trigger.

**Considered (in-session):** Universal orch.* pipeline/git/roles statutes — all `conforms` (plan-only pass; engineer assignee restored after approval). Scoped: `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.standards.utils-data-late-import-only` — `conforms` (names/pins in `TOKEN_SOURCES`; explicit boundaries; preserves late `rubric_criteria_for_token` import). `astral.layers.ui-config-driven-business-logic` — `conforms` (pickers already derive from registry via `get_tokens` / `get_manage_agents_tokens`; no parallel UI list). Parent-cited `astral.agent.do-task-delegation` — `conforms` by boundary (no `core/` edits; substitution stays on existing `resolve_tokens` / `do_task` path). Remaining scoped astral.* corpus — excluded (layer/path/change_type mismatch on `utils`-only footprint) or `conforms` where considered. Pattern `pattern.config.config-block` — matches solution shape.

context_tokens≈18500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1404/AST-1405-named-rubric-prompt-tokens`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `ba66a4c7` | Plan doc |
| Joan | `f58ea6b7` | validate APPROVED |
| 1 | `310f5e72` | Five named `TOKEN_SOURCES` pins; `resolve_tokens` honors pin and AST-1396 silence |

**Built:** `src/utils/config.py` only.
**Tip:** `310f5e72` (product); this stub follows on the same publish ref.

## Radia review

`[code-rubric] revision=2`
**Rubric:** code-rubric.v2
**Ticket:** AST-1405
**Publish ref:** `origin/sub/AST-1404/AST-1405-named-rubric-prompt-tokens` @ `82ac3ca836d08126616ebc8a6910141ac2fb11b6`
**Overall:** CLEAN

**Diff baseline:** `git diff origin/dev...origin/sub/AST-1404/AST-1405-named-rubric-prompt-tokens`
**Change set:** layers `utils`, `docs`; paths `src/utils/config.py`, `docs/features/foundation/ast-1405-named-rubric-prompt-tokens.md`, `docs/test-bible/utils/config.md`, `tests/component/utils/test_config.py`; change_types `add` + `modify`
**Product commit:** `310f5e72` (`src/utils/config.py` only) — engineer test-tree ban respected
**Test commit:** `c4433157` + merge `82ac3ca8` (Betty lane)

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/**` diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no `src/core/**` diff; substitution stays on existing `resolve_tokens` path |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grading/vector validation logic changed |
| astral.batch.batch-id-first | scoped | not-applicable | no batch/dispatch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch id emission |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch response paths |
| astral.config.config-source-of-truth | scoped | conforms | five pins added to `TOKEN_SOURCES`; no scattered literals |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no artifact/debug dir changes |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch/seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run-next/chain authority changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | plan/review at `docs/features/foundation/ast-1405-named-rubric-prompt-tokens.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commit touches tests + bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | product commit `310f5e72` is `src/utils/config.py` only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no core/external boundary edits |
| astral.layers.import-direction | scoped | conforms | no new cross-layer imports; preserves existing late `rubric_criteria_for_token` import in rubric branch |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | pickers already derive from `TOKEN_SOURCES` via `get_tokens` / `get_manage_agents_tokens`; no parallel UI list |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth handlers |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON edits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog/seed conflicts |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | hot-path token resolve unchanged structurally |
| astral.seed.define-approved | scoped | not-applicable | no define/seed workflow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed row lifecycle |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `src/data/**` changes |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migration changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | no `debug=` contract surfaces |
| astral.standards.dry-and-focused-functions | scoped | conforms | minimal branch extension; no new helpers |
| astral.standards.in-scope-only | scoped | conforms | single-file product change; out-of-scope areas untouched |
| astral.standards.logging-via-utils | scoped | conforms | uses existing `_log`; warning semantics match plan |
| astral.standards.names-not-ticket-ids | scoped | conforms | token names are domain names, not ticket ids |
| astral.standards.no-cross-contamination | scoped | conforms | rubric branch only; other token sources untouched |
| astral.standards.no-hardcoded-sets | scoped | conforms | pins live in `TOKEN_SOURCES`, not inline elsewhere |
| astral.standards.public-then-helpers | scoped | conforms | registry + existing `resolve_tokens` path |
| astral.standards.utils-data-late-import-only | scoped | conforms | no new utils→data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine edits |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state transitions |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/daisy-chain paths |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no UI naming surfaces |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server/worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1405)` lands Betty SHA on publish ref |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub publish ref; no reverse merges in diff |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1404/AST-1405-…` topology |
| orch.git.merge-on-checkout | universal | conforms | no checkout/merge violations in review scope |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear commit stack |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches in diff |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1404` worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | seed prompt rewrite explicitly deferred to Susan |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches Stage 1 steps |
| orch.pipeline.project-scoped-queues | universal | conforms | single-child review scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child gate satisfied |
| orch.roles.archie-approves-statutes | universal | conforms | active corpus used |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada remains assignee through review |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Sweep count:** 64 active rows from `canon/statutes/README.md` § Harvested corpus (registry cites 65; table matches README listing).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | five named rows extend `TOKEN_SOURCES`; pins use existing `rubric_criteria_for_token` path; no second registry |

Joan plan-rubric cited this pattern in-session; no additional pattern ids in plan/parent Architectural definition.

## Plan adherence

Stage 1 executed as written:

- Five `TOKEN_SOURCES` rows immediately after `RUBRIC_VECTORS` with correct `owner_task_key` pins (`grade_get`, `grade_do`, `grade_like`, `evaluate_jd`, `prefilter_company`).
- Forbidden names (`JOBLIST_RUBRIC`, `COMPANY_PREFILTER`, `JOBDESC_RUBRIC`) absent.
- `RUBRIC_VECTORS` remains `{"source": "rubric"}` unpinned.
- `resolve_tokens` rubric branch honors pin vs running-task owner; AST-1396 silence only for `pinned and not candidate_data`.
- Out-of-scope respected: no seed prompts, no UI, no `candidate.py` / `agent.py` edits.

**Estimate (3):** footprint matches — one utils file product + Betty tests/bible.

**QA manifest:** Betty’s `TestAst1405NamedRubricPromptTokens` (4 cases) + revised `TestAst723RubricVectorsToken` align with `docs/test-bible/utils/config.md` § AST-1405 manifest.

**Joan straggler (C4):** plan-rubric APPROVED @ `f58ea6b7`; no formal Excluded table — in-session exclusions were utils-footprint predicates; no straggler on code diff.

## Findings

### fix-now
(none)

### discuss
(none)

### advisory
- **Pre-existing layer bend:** `resolve_tokens` rubric branch retains late `from src.core.candidate import rubric_criteria_for_token` (AST-723 cycle break). Not introduced here; plan documents it. No action unless a future ticket centralizes utils→core rubric reads.
- **UAT follow-up (parent scope):** Susan still inserts tokens into seed prompt bodies per plan out-of-scope — expected downstream of this child.

## What’s solid
- Pin independence is clear: `{$GET_RUBRIC}` on `grade_like` resolves `grade_get`; `{$RUBRIC_VECTORS}` stays task-derived.
- Warning contract is precise: empty `{}` silences pinned names only; truthy view without `_astral_candidate_id` still warns; unpinned `RUBRIC_VECTORS` on `grade_like` still warns.
- Engineer/test lane separation is clean (`310f5e72` vs `c4433157`).

## Frame diff

| Planned (product) | Actual |
|-------------------|--------|
| `src/utils/config.py` only | `310f5e72` — `src/utils/config.py` only ✓ |
| No tests (Betty) | `c4433157` — tests + bible ✓ |
| No seed/UI/core | none in diff ✓ |

context_tokens≈42000

