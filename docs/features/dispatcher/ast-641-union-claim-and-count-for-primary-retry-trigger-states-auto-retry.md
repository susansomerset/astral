<!-- linear-archive: AST-641 archived 2026-06-23 -->

## Linear archive (AST-641)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-641/union-claim-and-count-for-primary-retry-trigger-states-auto-retry  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-630 — Auto retry  
**Blocked by / blocks / related:** parent: AST-630; blocks: AST-642

### Description

## What this implements

When a Scheduled Action row’s `trigger_state` is a primary job or company state (not already ending in `_RETRY`), eligible-entity counting and batch claim include entities in both that state and `trigger_state + "_RETRY"` when the suffix state exists in config. Retry-only rows continue to claim only the retry state. Existing dispatch row rules (candidate scope, sort, batch size, score-floor gating, company scan intervals) apply uniformly across the combined set.

## Acceptance criteria

* A Scheduled Action with `trigger_state` `VALID_TITLE` and `task_key` `qualify_job_listings` shows an **Available** count equal to eligible jobs in `VALID_TITLE` plus eligible jobs in `VALID_TITLE_RETRY` (scoped to candidate and existing floor rules).
* Running that row claims jobs from both states in one dispatch pass (subject to `batch_size` / chunk rules).
* The same primary + `_RETRY` union behavior works for `JD_READY` / `JD_READY_RETRY` (`evaluate_jd`) and for company prefilter (`WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` on `prefilter`).
* A row with `trigger_state` `VALID_TITLE_RETRY` claims only `VALID_TITLE_RETRY` jobs.
* Rows that intentionally target only a retry state (legacy seed or manual rows) behave as today — no regression in run or count.

## Boundaries

* Does **not** change per-entity retry vs error routing inside batch consult — sibling ticket owns `consult.py` mixed-state batches.
* Does **not** create or seed new `dispatch_task` rows.
* Does **not** alter score-floor semantics for `*_RETRY` trigger rows.

## Notes for planning

* Config registry: `JOB_STATES`, `COMPANY_STATES` / `ROSTER_CONFIG` prefilter `retry_state`.
* Touch paths: data claim/count, `tracker.get_new_job_batch`, company batch claim, `dispatcher._run_unified` input, `api_admin` available_count (likely via shared count helper).
* `dispatch_claim_uses_score_floor`: primary trigger rows keep current gating; `*_RETRY` states remain non–score-gated at claim.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-630-auto-retry`, child `sub/AST-630/<child-segment>`. Created at dispatch-parent.

### Comments

#### hedy — 2026-06-14T20:27:02.226Z
**Review (Radia)** — `origin/dev...origin/sub/AST-630/AST-641-union-claim-count` @ `378af6e4` (product); doc @ `a053a5cc`

### fix-now
None.

### discuss
None.

### advisory
- Plan Execution contract named `test_api_admin.py`; bible §7.13zzo covers **Available** via `count_eligible_for_dispatch_task` data-layer tests instead — acceptable (admin has no separate count path).
- `database.py`: `_state_in_sql` is defined below early claim callers; runtime-safe; reorder optional for readability only.

### What's solid (rules)
- **§2.1 / §2.4:** `dispatch_claim_states` + `_state_in_sql`; count/claim share resolved list; score floor still keyed off row `trigger_state`.
- **§2.6 / §5d:** No consult/transition edits; AST-642 boundary held.
- **§1.5.1:** `claim_states` in `_run_unified` `debug_detail` only when `debug=True`.

Plan doc: `docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md` — **Review (Radia)** section.

**Verdict:** Clean — ready for `resolve-child`.

#### betty — 2026-06-14T20:24:22.757Z
## QA test manifest (Tests Ready)

**Publish ref:** `origin/sub/AST-630/AST-641-union-claim-count` @ `378af6e4` (`merge-tests(AST-641): origin/tests 9a9996ec`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `f4f2e7e83f3dab62782299f4f0c5f56134d00ee8edfcdfff9fb75f5080bdc145` (§7.13zzo)

Run from repo root after `git fetch origin` and checkout publish ref (merge `origin/ftr/ast-630-auto-retry` per merge-on-checkout):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst641DispatchClaimStates \
  tests/component/data/database/test_dispatch_tasks.py::TestAst641UnionClaimCount \
  tests/component/core/test_dispatcher.py -k ast641
```

### Manifest

1. **`tests/component/utils/test_config.py::TestAst641DispatchClaimStates`** — `dispatch_claim_states` primary vs retry-only vs missing companion; job (`VALID_TITLE`, `JD_READY`) and company (`WEBSITE_FOUND`) pairs.
2. **`tests/component/data/database/test_dispatch_tasks.py::TestAst641UnionClaimCount`**
   - Primary `VALID_TITLE` row: `count_eligible_for_dispatch_task` sums primary + retry jobs; `claim_job_batch` with `states=` claims both.
   - Retry-only `VALID_TITLE_RETRY` row: count single retry state only.
   - Company `WEBSITE_FOUND` prefilter: count + `claim_company_batch` union with `WEBSITE_FOUND_RETRY`.
   - Scored `PASSED_LIKE` primary: one `score_floor` across primary + `PASSED_LIKE_RETRY` pool (regression guard).
3. **`tests/component/core/test_dispatcher.py`** — `test_ast641_primary_job_trigger_passes_union_claim_states`, `test_ast641_retry_only_job_trigger_single_claim_state`, `test_ast641_company_prefilter_passes_union_claim_states` — `_run_unified` passes resolved `states=` into batch helpers.

**Existing coverage (no separate manifest line):** admin Available count flows through shared `count_eligible_for_dispatch_task` once data layer is fixed — no new `test_api_admin.py` cases required this ticket.

**Out of scope (AST-642):** consult mixed-state routing — not asserted here.

#### hedy — 2026-06-14T19:18:44.267Z
Plan: [`docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md`](https://github.com/susansomerset/astral/blob/sub/AST-630/AST-641-union-claim-count/docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md)

**Self-assessment**
- **Scope:** `Single-Component` — config `dispatch_claim_states`, data-layer claim/count IN clauses, thin tracker/roster/dispatcher plumbing; no consult or UI.
- **Conf:** `high` — extends existing batch claim/count and AST-586 score-floor split with a registry-driven state list.
- **Risk:** `Medium` — claim/count mismatch would affect dispatch eligibility, but consult routing stays on AST-642.

Three stages: (1) config helper, (2) database multi-state SQL, (3) core wrappers + dispatcher wiring. Betty covers union vs retry-only AC in component tests at Code Complete.

---

# Union claim and count for primary + _RETRY trigger states (Auto retry — AST-641)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-641/union-claim-and-count-for-primary-retry-trigger-states-auto-retry  
**Parent:** https://linear.app/astralcareermatch/issue/AST-630/auto-retry  

**Publish ref (origin):** `sub/AST-630/AST-641-union-claim-count`  
**Parent integration ref:** `ftr/ast-630-auto-retry`  

When a Scheduled Action row’s `trigger_state` is a **primary** job or company state (does not end with `_RETRY`), eligible-entity **count** and batch **claim** include entities in both that state and its companion `trigger_state + "_RETRY"` when the companion exists in the product registry (`JOB_STATES` / `COMPANY_STATES`). Retry-only rows continue to claim and count **only** the retry state. Score-floor gating (`dispatch_claim_uses_score_floor`) and all other dispatch row rules (candidate scope, sort, batch size, scan intervals) apply uniformly across the combined set. Per-entity retry-vs-error routing inside consult is **AST-642** — out of scope here.

**Verified (plan time):** `claim_job_batch`, `set_company_batch`, and `count_eligible_for_dispatch_task` filter on a single `state = ?`. `dispatcher._run_unified` passes `task["trigger_state"]` verbatim into `get_new_job_batch` / `get_new_company_batch`. Admin **Available** uses `database.count_eligible_for_dispatch_task(row)` in `api_admin.py` — no separate count path.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `dispatch_claim_states(trigger_state, entity_type) -> List[str]` | utils |
| `src/data/database.py` | Multi-state IN clause in `claim_job_batch`, `set_company_batch` / `claim_company_batch`, `count_eligible_for_dispatch_task`, and shared count helpers | data |
| `src/core/tracker.py` | `get_new_job_batch`: optional `states` kw-only param → `claim_job_batch` | core |
| `src/core/roster.py` | `get_new_company_batch`: optional `states` kw-only param → `claim_company_batch` | core |
| `src/core/dispatcher.py` | Resolve `claim_states` before job/company claim; pass into batch helpers | core |

**Not in scope:** `src/core/consult.py` (AST-642), `api_admin.py` (counts via shared helper once data layer fixed), React admin UI, dispatch_task seeding, `JOB_STATES` / transition registry edits.

**Tests (Betty at Code Complete — engineer does not edit `tests/` in build):** extend `tests/component/core/test_dispatcher.py`, `tests/component/ui/api/test_api_admin.py`, and data-layer claim/count coverage for union vs retry-only rows per AC below.

---

## Stage 1: Config helper — resolve claim state set

**Done when:** `dispatch_claim_states` returns the correct 1- or 2-state lists for primary vs retry triggers and job vs company entity types; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, immediately after `dispatch_claim_uses_score_floor` (~1189), add:

   ```python
   def dispatch_claim_states(trigger_state: Optional[str], entity_type: str) -> List[str]:
       """States a dispatch row claims and counts (primary + companion *_RETRY when configured)."""
       if trigger_state is None:
           return []
       ts = str(trigger_state).strip()
       if not ts:
           return []
       if ts.endswith("_RETRY"):
           return [ts]
       companion = f"{ts}_RETRY"
       if entity_type == "job" and companion in JOB_STATES:
           return [ts, companion]
       if entity_type == "company" and companion in COMPANY_STATES:
           return [ts, companion]
       return [ts]
   ```

2. Run:

   ```bash
   python3 -m py_compile src/utils/config.py
   ```

⚠️ **Decision:** Companion detection uses the **`trigger_state + "_RETRY"`** suffix convention with registry membership (`JOB_STATES` / `COMPANY_STATES`), matching parent epic wording and existing pairs (`VALID_TITLE`/`VALID_TITLE_RETRY`, `JD_READY`/`JD_READY_RETRY`, `WEBSITE_FOUND`/`WEBSITE_FOUND_RETRY`). No scan of `ROSTER_CONFIG` at runtime — registry keys are the source of truth for “suffix state exists in config.”

---

## Stage 2: Data layer — multi-state claim and count SQL

**Done when:** `count_eligible_for_dispatch_task` sums eligible rows across the resolved state set for job and company tasks; `claim_job_batch` and `claim_company_batch` claim from the same combined pool with identical filters and sort; retry-only trigger rows behave as today (single state); `python3 -m py_compile src/data/database.py` passes.

1. In `src/data/database.py`, import `dispatch_claim_states` from `src.utils.config` alongside existing config imports (~76).

2. Add a private helper near the count/claim functions (~5250):

   ```python
   def _state_in_sql(states: List[str]) -> tuple[str, List[Any]]:
       """Return ('state IN (?,?)', [s0, s1]) or ('state = ?', [s0]) for non-empty states."""
       if not states:
           raise ValueError("states must be non-empty")
       if len(states) == 1:
           return "state = ?", [states[0]]
       placeholders = ",".join("?" for _ in states)
       return f"state IN ({placeholders})", list(states)
   ```

3. In `claim_job_batch` (~1384):
   - Add keyword-only parameter: `*, states: Optional[List[str]] = None`.
   - At function entry: `claim_states = states if states is not None else [state]`.
   - Replace the subquery predicate `WHERE state = ?` with `WHERE {_state_in_sql(claim_states)[0]}` and bind `_state_in_sql(claim_states)[1]` in params **before** `candidate_filter` / `score_filter` params (preserve existing param order after state bind: batch_id, now, then state(s), then candidate_id, score_floor, limit).

4. In `set_company_batch` (~743), claim branch (`clear=False`):
   - Add keyword-only `*, states: Optional[List[str]] = None`.
   - Resolve `claim_states = states if states is not None else [state]` (require `state` when `states` is None, same as today).
   - Replace `where_base = "state = ? AND ..."` with `f"{_state_in_sql(claim_states)[0]} AND (batch_id IS NULL OR batch_id = '')"` and bind state params first in `params` after `[batch_id, ...]` — match existing param assembly order.

5. In `claim_company_batch` (~164), add `*, states: Optional[List[str]] = None` and pass through to `set_company_batch(..., states=states)`.

6. In `count_entities_in_state` (~5375), add optional `states: Optional[List[str]] = None`:
   - When `states` is provided, use `_state_in_sql(states)` instead of `state = ?` in both company and job COUNT queries.
   - When `states` is None, keep current single-`state` behavior (backward compat for any direct callers).

7. In `count_eligible_for_dispatch_task` (~5257):
   - After parsing `entity_type`, `state`, `candidate_id`, compute:
     ```python
     claim_states = dispatch_claim_states(state, entity_type)
     ```
   - If `claim_states` is empty, return `0`.
   - **Job branch with score floor** (~5335): replace `WHERE state = ?` with `_state_in_sql(claim_states)` in the COUNT SQL.
   - **Job branch default** (final `return count_entities_in_state(...)`): call `count_entities_in_state(entity_type, state, candidate_id, states=claim_states)`.
   - **Company branch** (all paths that filter on `state = ?`, including `count_companies_in_state_with_score_floor` call sites and stale-scan COUNT ~5290): pass `claim_states` into count helpers — either add `states=` to `count_companies_in_state_with_score_floor` or inline `_state_in_sql(claim_states)` in those COUNT queries so WEBSITE_FOUND rows count WEBSITE_FOUND + WEBSITE_FOUND_RETRY.
   - **Do not change** `entity_type == "candidate"`, `board_search`, or `inflow_resolve_website` branches — they do not use `trigger_state` retry union.

8. Run:

   ```bash
   python3 -m py_compile src/data/database.py
   ```

⚠️ **Decision:** Score-floor gating stays keyed off the **dispatch row’s** `trigger_state` via existing `dispatch_claim_uses_score_floor(state)` — not per claimed entity state. Primary rows (`VALID_TITLE`, `JD_READY`, `WEBSITE_FOUND`) remain non–score-gated at claim; `*_RETRY` trigger rows remain non–score-gated; `PASSED_*` scored rows apply one floor across the combined primary+retry pool when both exist in registry.

---

## Stage 3: Core batch wrappers and dispatcher wiring

**Done when:** `dispatcher._run_unified` claims jobs and companies using `dispatch_claim_states(input_state, entity_type)`; `claim_cap` for AST-502 chunk exhaustion still matches post-union `count_eligible_for_dispatch_task`; direct `get_new_job_batch("NEW", ...)` test callers unchanged (single state unless `states=` passed); `python3 -m py_compile` passes on touched core files.

1. In `src/core/tracker.py`, `get_new_job_batch` (~542):
   - Add keyword-only `*, states: Optional[List[str]] = None`.
   - When `states` is None: `validate_value(_JOB_STATE_LIST, state)` (unchanged).
   - When `states` is provided: `for s in states: validate_value(_JOB_STATE_LIST, s)` — do **not** call `dispatch_claim_states` here (dispatcher owns resolution).
   - Pass `states=states` through to `database.claim_job_batch(...)`.

2. In `src/core/roster.py`, `get_new_company_batch` (~888):
   - Add keyword-only `*, states: Optional[List[str]] = None`.
   - When `states` is None: existing allowed-state check on `state`.
   - When `states` is provided: validate each state is in `COMPANY_STATES`.
   - For `batch_criteria` lookup (`state_config = COMPANY_STATES.get(state, {})` ~909): keep using the **dispatch row trigger_state** (`state` argument), not the companion retry state — sort/limit defaults come from the row’s configured input trigger.
   - Pass `states=states` to `claim_company_batch(...)`.

3. In `src/core/dispatcher.py`, `_run_unified` job branch (~239):
   - Import `dispatch_claim_states` from `src.utils.config`.
   - Before `get_new_job_batch(...)`:
     ```python
     claim_states = dispatch_claim_states(input_state, "job")
     ```
   - Pass `states=claim_states` into `get_new_job_batch(input_state, ..., states=claim_states)`.
   - Leave `claim_cap = database.count_eligible_for_dispatch_task(task)` unchanged — count helper now includes union.

4. In `_run_unified` company `else` branch (~259):
   - `claim_states = dispatch_claim_states(input_state, "company")`
   - Pass `states=claim_states` into `get_new_company_batch(input_state, ..., states=claim_states)`.

5. In `_run_unified` debug_detail lines that log `input_state`, append `claim_states={claim_states!r}` when `debug=True` (both job and company branches) — no behavior change.

6. Run:

   ```bash
   python3 -m py_compile src/core/tracker.py src/core/roster.py src/core/dispatcher.py
   ```

---

## Execution contract reminders

- **AST-642** owns consult routing when a batch mixes primary and retry entities — do not edit `consult.py` in this ticket.
- Retry-only dispatch rows (`VALID_TITLE_RETRY`, etc.) must claim/count **only** that retry state — verified by `dispatch_claim_states` suffix guard.
- Do not seed or delete `dispatch_task` rows.
- Betty’s tests should cover at minimum:
  - `VALID_TITLE` + `qualify_job_listings`: available count = eligible VALID_TITLE + VALID_TITLE_RETRY (mock or fixture DB).
  - `VALID_TITLE_RETRY` row: count/claim only retry state.
  - `WEBSITE_FOUND` prefilter company row: union with `WEBSITE_FOUND_RETRY`.
  - Scored primary row with companion in registry: floor applied once across combined pool (regression guard).

---

## Self-Assessment

**Scope:** `Single-Component` — touches config helper, data-layer claim/count SQL, and thin core/dispatcher plumbing; no UI or consult changes.

**Conf:** `high` — extends existing batch claim/count pattern with a registry-driven state list; call sites and score-floor split are already established (AST-586/617).

**Risk:** `Medium` — wrong IN-clause or count/claim mismatch would starve or double-run dispatch batches, but blast radius is isolated to claim/count paths and sibling AST-642 handles consult outcomes.

---

## ASTRAL_CODE_RULES self-review

| Rule | Compliance |
|------|------------|
| §1.3 DRY | Single `dispatch_claim_states` + `_state_in_sql`; count and claim share the same resolved list |
| §2.1 Config as source of truth | Companion states validated against `JOB_STATES` / `COMPANY_STATES` only |
| §2.4 Batch processing | `batch_id` first unchanged; claim/get/clear pattern preserved |
| §2.6 State machine | No transition edits |
| §3.3 Imports | Config helper in utils; data imports config; core imports data |
| §3.5 Naming | Follows existing `dispatch_claim_*` prefix |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `sub/AST-630/AST-641-union-claim-count` @ `394dfdd7`
**Scope:** `dispatch_claim_states` config helper; multi-state claim/count in data layer; dispatcher/tracker/roster wiring.
**Betty:** extend `test_dispatcher.py`, `test_api_admin.py`, data-layer claim/count tests per Execution contract.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-630/AST-641-union-claim-count` @ `378af6e4`
**Reviewed:** 2026-06-14

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–3 land as specified: `dispatch_claim_states` in config; `_state_in_sql` + multi-state claim/count in `database.py`; optional `states=` on tracker/roster batch helpers; dispatcher resolves and passes union before claim. |
| AC coverage | Betty manifest: primary job/company union count+claim, retry-only single state, scored `PASSED_LIKE` floor across union (`TestAst641UnionClaimCount`, dispatcher `test_ast641_*`, config helper tests). |
| §2.1 / §2.4 | Companion states from `JOB_STATES` / `COMPANY_STATES` registry; `batch_id`-first claim/get/clear unchanged; score-floor gating still keyed off dispatch row `trigger_state` via `dispatch_claim_uses_score_floor`. |
| §2.6 / §5d | No transition or consult changes; AST-642 boundary respected. |
| §1.3 DRY | Single resolver + SQL helper shared by count and claim paths. |
| §1.5.1 debug | `claim_states` appended to `_run_unified` `debug_detail` only on debug path — no contract emission when `debug=False`. |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| advisory | Plan Execution contract vs bible §7.13zzo | Plan listed `test_api_admin.py`; manifest covers admin **Available** indirectly via `count_eligible_for_dispatch_task` data-layer tests — sufficient for this ticket. |
| advisory | `database.py` `_state_in_sql` placement | Helper defined after early claim functions that call it — valid at runtime (call-time binding); optional reorder only if readability matters. |

### Recommended actions

| Priority | Action |
|----------|--------|
| resolve-child | No fix-now — ship as reviewed; optional UAT: Scheduled Actions **Available** for `VALID_TITLE` / `WEBSITE_FOUND` rows shows primary+retry union in staging. |

**Verdict:** Approve for `resolve-child` — clean pass.

---

## Resolution

**Resolved:** 2026-06-14  
**Publish ref:** `origin/sub/AST-630/AST-641-union-claim-count` @ `a053a5cc`

Radia **Review Posted** (2026-06-14): **fix-now** none, **discuss** none. Advisory items (admin count covered via data-layer tests; `_state_in_sql` placement) — no product changes required.

**Shipped:** `dispatch_claim_states` config helper; `_state_in_sql` + multi-state claim/count in `database.py`; optional `states=` on tracker/roster batch helpers; dispatcher union wiring. Betty manifest green (14 tests). §9a dry-run clean into `origin/dev` and `origin/ftr/ast-630-auto-retry`.

---

## Bug: AST-1798 — strict `_RETRY` suffix claim pairing (no `retry_state` companion)

Orphaned mini-parent: AST-1797. No ancestor box checked; this section patches the historical home of `dispatch_claim_states` (AST-641). Scope gate: AST-1798 `## Scope` / Component + Technical scope only.

### As-is

A company (or any entity) dispatch row with `trigger_state=HOMEPAGE_READY` claims and counts `['HOMEPAGE_READY', 'WEBSITE_FOUND_RETRY']` because `dispatch_claim_states` prefers `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"]` when that key is in the registry, then falls back to `{ts}_RETRY` only if that companion key exists in the registry. Live tip matches that preference. The only other live cross-name claim pair is job `VALID_TITLE` → `NEW_RETRY` (AST-898 `retry_state`).

### To-be

For every `dispatch_task` / every `entity_type`, claim/count companions are **only** the trigger plus the literal suffix `trigger_state + "_RETRY"`, whether or not that companion key exists in the entity registry. Do not validate suffix content against the registry and do not error when the suffix key is absent. `HOMEPAGE_READY` therefore claims `['HOMEPAGE_READY', 'HOMEPAGE_READY_RETRY']` — never `WEBSITE_FOUND_RETRY` via config. Registry `retry_state` may still describe failure **routing** destinations; it must not drive claim grouping. No exceptions by entity type or task key.

### Repro

```python
from src.utils import config as cfg

# Broken today (tip):
assert cfg.dispatch_claim_states("HOMEPAGE_READY", "company") == [
    "HOMEPAGE_READY",
    "WEBSITE_FOUND_RETRY",
]
# Also broken cross-name (AST-898 retry_state used for claim):
assert cfg.dispatch_claim_states("VALID_TITLE", "job") == [
    "VALID_TITLE",
    "NEW_RETRY",
]

# Expected after fix:
assert cfg.dispatch_claim_states("HOMEPAGE_READY", "company") == [
    "HOMEPAGE_READY",
    "HOMEPAGE_READY_RETRY",
]
assert cfg.dispatch_claim_states("VALID_TITLE", "job") == [
    "VALID_TITLE",
    "VALID_TITLE_RETRY",
]
# Missing companion key is fine (no error); still append suffix:
assert "HOMEPAGE_READY_RETRY" not in cfg.COMPANY_STATES
assert cfg.dispatch_claim_states("HOMEPAGE_READY", "company")[1] == "HOMEPAGE_READY_RETRY"
```

Optional live check: Admin Available / claim for a `prefilter` row with `trigger_state=HOMEPAGE_READY` must not include companies in `WEBSITE_FOUND_RETRY`.

### Root cause

`dispatch_claim_states` (AST-882) prefers `registry[ts]["retry_state"]` when present-and-in-registry over the `{ts}_RETRY` name, and otherwise only appends `{ts}_RETRY` when that key is also in the registry. That turns failure-routing config into claim grouping and drops suffix companions that have no registry entry.

### Proposed change

1. **`src/utils/config.py` — `dispatch_claim_states`** (only product edit required for the pairing rule):
   - Keep: `None` / blank → `[]`; already ends with `_RETRY` → `[ts]` only.
   - Remove the branch that returns `[ts, registry[ts].retry_state]` when `retry_state` is a non-empty string in the registry.
   - Remove the `if companion in registry` gate.
   - For every non-`_RETRY` primary, always return `[ts, f"{ts}_RETRY"]` for all entity types (`job` / `company` / `candidate` / `meteorite` / unknown). Do not look up registry for claim companions at all.
   - Keep the `entity_type` parameter (callers unchanged); it no longer selects a registry for companion resolution.
   - Rewrite the docstring: suffix-only pairing; `retry_state` is not used here.
   - Do **not** change `JOB_STATES` / `COMPANY_STATES` / etc. `retry_state` field values (routing stays).

2. **`src/data/database.py` and claim callers** — **no change expected**. `_state_in_sql` already accepts an arbitrary non-empty string list and does not validate membership in the entity registry. Confirm during make-fix that no claim/count path rejects `{ts}_RETRY` absent from the registry; if one does, strip that validation only (do not invent cross-name companions). Out of scope: scrape ownership of `WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` on `fetch_website`.

3. **`tests/component/utils/test_config.py`** (Betty / make-fix as owned — named here because Scope lists it): flip assertions that encode the broken preference:
   - `TestAst882DispatchClaimStates`: `HOMEPAGE_READY` → `['HOMEPAGE_READY', 'HOMEPAGE_READY_RETRY']` (never `WEBSITE_FOUND_RETRY`); keep `WEBSITE_FOUND` → `['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']`.
   - `TestAst641DispatchClaimStates` / AST-898 claim asserts: `VALID_TITLE` → `['VALID_TITLE', 'VALID_TITLE_RETRY']` (not `NEW_RETRY`); primaries with no registry companion key (e.g. company `NEW`, meteorite primaries) → always `[ts, f"{ts}_RETRY"]`.
   - Any other claim-state assert that equals a non-suffix `retry_state` companion must use the suffix form.

### Blast radius

- **Claim/count only:** Available counts and batch claims for primary rows stop unioning cross-named `retry_state` destinations. Concrete live flips: `HOMEPAGE_READY` drops `WEBSITE_FOUND_RETRY`; `VALID_TITLE` drops `NEW_RETRY` and picks up `VALID_TITLE_RETRY` (key already in `JOB_STATES`).
- **Routing unchanged:** prefilter / qualify failure paths that write `retry_state` destinations keep using registry `retry_state` outside this helper.
- **Absent suffix keys:** SQL `IN` for a never-written state (e.g. `HOMEPAGE_READY_RETRY`) matches zero rows — no error; that is intentional.
- **Shared consumers:** `count_eligible_for_dispatch_task`, claim_*_batch paths, dispatcher `_run_unified` debug `claim_states` — all via this helper; no separate pairing logic to fork.
- **Tests** that encode AST-882 / AST-898 cross-name claim expectations will fail until updated (listed above). Integration scenarios that assumed `HOMEPAGE_READY` unions WFR for prefilter Available need the same expectation flip if present.

### What must still hold

- Already-`*_RETRY` trigger rows still claim only that single state (AST-641 AC).
- Primaries whose suffix already matches their `retry_state` (e.g. `JD_READY` → `JD_READY_RETRY`, `WEBSITE_FOUND` → `WEBSITE_FOUND_RETRY`, candidate `REQUESTED_*`) keep the same two-state list — behavior unchanged for those rows.
- Score-floor gating still keyed off the dispatch row’s `trigger_state` via `dispatch_claim_uses_score_floor`, not off companion states (AST-641).
- `fetch_website` ownership / second-strike filter for `WEBSITE_FOUND_RETRY` vs homepage-ready WFR is untouched (AST-882 / AST-892 boundary).
- Registry `retry_state` / `error_state` continue to drive failure routing writes; only claim grouping stops reading them.
- No new company/job states required; do not seed `HOMEPAGE_READY_RETRY` as part of this bug unless a later ticket asks.


## Fix-board Joan findings (AST-1798)

**Triage notes**

Read the AST-1798 `plan-fix` patch on `origin/sub/AST-1797/AST-1798-retry-suffix-claim` and skimmed overlapping roster directives (`patt.task.dispatch-retry`, `astral.dispatch.entity-state-bound`, `astral.batch.claim-process-release`, `patt.task.daisy-chain`).

The proposed change restores suffix-only claim pairing in `dispatch_claim_states` and drops AST-882’s registry `retry_state` preference for claim grouping. That aligns with active canon rather than fighting it:

- **`patt.task.dispatch-retry`** — Arc 1–3: retry is `{trigger}_RETRY`; claim expands to trigger + suffixed companion; suffix states need not exist in the registry. Cross-name pairing (`HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY`, `VALID_TITLE` → `NEW_RETRY`) is what this bug introduced; the fix corrects it.
- **`astral.dispatch.entity-state-bound`** — claim helpers should reflect what the row actually claims; suffix-only pairing makes `trigger_state` honest.
- **`astral.batch.claim-process-release`** / **`patt.task.daisy-chain`** — unchanged claim→process→release shape; only the state-set membership changes.

No statute or pattern update, carve-out, or Archie gate needed. Registry `retry_state` stays for failure routing (AST-882/702); only claim grouping stops reading it, which canon already expects. F3 `validate-plan` fix mode not triggered from this board pass.
[AST-1797 | AST-1798] Joan/validate fix-board - complete 7b757bfd model=composer-2.5 - (52s) > OK


## Review-fix findings (AST-1798)

## Fix-specific checks

**`[bug-repro]`:** not applicable — product-only tip; board `TESTS: REVISE` explicitly deferred to sibling **AST-1799** (Plan Ready). Issue Description and plan-fix both mark `tests/component/utils/test_config.py` out of scope on this tip. No qa-fix thread on AST-1798; intentional docs-acceptance split (AST-1794/AST-1795 precedent).

**`## What must still hold`:** OK
- `*_RETRY`-only triggers → single-state list preserved (`endswith("_RETRY")` branch unchanged).
- Suffix-matched primaries (`JD_READY`, `WEBSITE_FOUND`, `NEW` job, candidate `REQUESTED_*`) → same two-state lists under suffix-only rule.
- `dispatch_claim_uses_score_floor` untouched; score-floor still keyed on row `trigger_state`.
- `fetch_website_prefilter_second_strike_filter` / AST-892 boundary untouched.
- Registry `retry_state` / routing fields unchanged; only claim grouping stops reading them.
- No new registry states seeded.

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on the bug ticket. Joan fix-board informal OK only. Process observation for Archie — not blocking; product aligns with board-cited dispatch-retry law.  
  **Recommendation:** No in-flight Canon Scope amendment required unless Archie wants Radia comparability on fix-lane bugs.

- **Location:** `[board-betty] TESTS: REVISE` / sibling **AST-1799** (Plan Ready)  
  **Finding:** Claim test classes on tip still encode cross-name companions (`HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY`, etc.). Expected on a product-only tip; AST-1799 owns the flip.  
  **Recommendation:** Chuckles: document **Docs-Acceptance** on AST-1798 (mirror AST-1794). Do not merge-tests on this tip. Land AST-1799 before expecting full `test_config.py` claim suite green on ftr.

### advisory

- **Location:** `tests/component/utils/test_config.py` (tip, unchanged on AST-1798 diff)  
  **Finding:** `TestAst882DispatchClaimStates` / `TestAst641DispatchClaimStates` / `TestAst898NewRetryQualifyHolding` would fail if run against `8721f208` product. test-fix manifest likely excluded them or ran pre-code SHA; not a product defect on this tip.

## What's solid

- Diff isolates exactly plan-fix § Proposed change (1): `dispatch_claim_states` suffix-only, registry branch removed, `entity_type` kept for call-site compat, docstring updated.
- `src/data/database.py` unchanged; `_state_in_sql` accepts arbitrary state strings — no registry membership gate (plan item 2 confirmed).
- Registry `retry_state` values untouched — routing vs claim separation restored.
- Estimate **3** fits footprint (one helper, docs-only plan-fix + board append).

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1797 In Progress; diff base `origin/ftr/AST-1797-retry-suffix-claim`) | → **Review Posted** → append artifact + `docs(AST-1798): Radia review — clean` on publish ref → post slim upshot `--as radia` → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |
| — | Sibling **AST-1799** | Parallel track: close `TESTS: REVISE` bar (test/bible only). ftr rollup should not assume full claim-suite green until AST-1799 lands. |

`

**Chuckles note:** `[board-betty] TESTS: REVISE` owned by sibling gap AST-1799. Product tip docs-acceptance — no merge-tests on AST-1798.



## Docs-Acceptance (AST-1798)

Test-tree / claim-assert flips owned by sibling gap AST-1799 (fix-board TESTS: REVISE). No merge-tests on this tip.

## Bug: AST-1799 — gap: tests/bible suffix-always claim asserts

Sibling test gap for AST-1798 (`[board-betty] TESTS: REVISE`). Product pairing lands on AST-1798; this ticket is **test/bible only**. Scope gate: AST-1799 `## Scope` (Component + Technical). Same plan-doc home as the claim helper (AST-641).

### As-is

`tests/component/utils/test_config.py` claim classes still encode registry-`retry_state` / membership-gated companions: `TestAst882DispatchClaimStates` expects `HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY` and `VALID_TITLE` → `NEW_RETRY`; `TestAst641DispatchClaimStates` expects `VALID_TITLE` → `NEW_RETRY` and companion-less primaries (`NEW` company, `INVALID_TITLE`) → single-state; `TestAst898NewRetryQualifyHolding` expects `VALID_TITLE` → `NEW_RETRY`. `docs/test-bible/utils/config.md` § AST-641 / AST-882 / AST-898 documents that same broken claim contract.

### To-be

Those claim asserts and the bible match AST-1798 suffix-always pairing: primary → always `[ts, f"{ts}_RETRY"]`; already-`*_RETRY` → `[ts]` only; never cross-name claim unions from `retry_state`. Registry `retry_state` field asserts (routing) stay unchanged.

### Repro

Against a tree with AST-1798 product landed (`dispatch_claim_states` suffix-always) and this gap **not** applied:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst882DispatchClaimStates \
  tests/component/utils/test_config.py::TestAst641DispatchClaimStates \
  tests/component/utils/test_config.py::TestAst898NewRetryQualifyHolding \
  -q
```

Expect red on `HOMEPAGE_READY` / `VALID_TITLE` / companion-less primary claim asserts. Pre-fix product + current asserts: green for the old cross-name contract (Betty board finding).

### Root cause

AST-882 / AST-898 taught the component suite and bible that claim companions follow registry `retry_state` (and AST-641 gated on companion ∈ registry). AST-1798 restores suffix-only claim pairing; tests and bible were not updated on that tip (`TESTS: REVISE` → this gap).

### Proposed change

1. **`tests/component/utils/test_config.py`** — flip **claim-state** asserts only (do not change `JOB_STATES`/`COMPANY_STATES` `retry_state` field asserts, transition tables, or fail-dest matrices):
   - **`TestAst882DispatchClaimStates`**: docstring → suffix-always (not “prefer retry_state”). `HOMEPAGE_READY` → `["HOMEPAGE_READY", "HOMEPAGE_READY_RETRY"]` (never `WEBSITE_FOUND_RETRY`). Keep `WEBSITE_FOUND` → `["WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"]`. `VALID_TITLE` → `["VALID_TITLE", "VALID_TITLE_RETRY"]`.
   - **`TestAst641DispatchClaimStates`**: `VALID_TITLE` → `["VALID_TITLE", "VALID_TITLE_RETRY"]` (drop AST-898 cross-name comment). Company `NEW` → `["NEW", "NEW_RETRY"]`; job `INVALID_TITLE` → `["INVALID_TITLE", "INVALID_TITLE_RETRY"]`. Keep retry-only single-state and `JD_READY` / `WEBSITE_FOUND` suffix pairs (already correct).
   - **`TestAst898NewRetryQualifyHolding`**: claim asserts — `VALID_TITLE` → `["VALID_TITLE", "VALID_TITLE_RETRY"]`; keep `NEW` → `["NEW", "NEW_RETRY"]` and retry-only singles. Leave `JOB_STATES["VALID_TITLE"]["retry_state"] == "NEW_RETRY"` and consult fail-dest → `NEW_RETRY` (routing, not claim).
   - **Sibling claim asserts in the same file** that still encode the old gate (same Scope “any sibling claim asserts”): e.g. candidate `ACTIVE_SEARCH` single-state → always append `_RETRY`; meteorite primaries in `test_dispatch_claim_states_meteorite` → always `[ts, f"{ts}_RETRY"]`. Do not invent new test classes beyond flipping these claim expectations.

2. **`docs/test-bible/utils/config.md`** — revise claim-contract prose only:
   - **§ AST-641 · AST-642 · AST-630**: primary rows always count/claim `trigger` + `trigger+"_RETRY"` whether or not the companion key exists in the registry (drop “when that companion exists”).
   - **§ AST-882 · AST-881**: replace “prefers registry `retry_state`… HOMEPAGE_READY claims WEBSITE_FOUND_RETRY” with suffix-always: `HOMEPAGE_READY` → `HOMEPAGE_READY_RETRY`; note `retry_state` remains for failure routing. Update the HOMEPAGE_READY claim-list row accordingly.
   - **§ AST-898 · AST-895**: keep `NEW`/`VALID_TITLE` **registry** `retry_state` → `NEW_RETRY` for routing; change primary **claim** language so `VALID_TITLE` claims `VALID_TITLE_RETRY` (not `NEW_RETRY`). `NEW` claim `["NEW","NEW_RETRY"]` stays (suffix matches).

3. **Out of scope (AST-1798 / other tickets):** no `src/` product edits; do not change `docs/test-bible/core/roster.md` / `gazer.md` / `dispatch_tasks.md` unless a separate board finding names them — Betty’s REVISE named `utils/config.md` + these claim classes.

### Blast radius

- Component suite for utils/config claim helpers goes green against AST-1798 product once flipped; stays red against pre-fix product for the HOMEPAGE_READY / VALID_TITLE cases (desired).
- Routing / transition / fail-dest tests that still assert `retry_state == WEBSITE_FOUND_RETRY` or `VALID_TITLE.retry_state == NEW_RETRY` remain valid and must not be “fixed” into suffix form.
- Downstream data/dispatcher tests that hard-code old claim unions (e.g. `TestAst882HomepageReadyClaimsWfr` if still present) are **not** in this ticket’s Scope — leave them; file a follow-up only if Betty’s board expands.

### What must still hold

- Retry-only trigger rows still assert single-state claim lists.
- Primaries whose suffix already matched `retry_state` (`JD_READY`, `WEBSITE_FOUND`, `NEW` job, candidate `REQUESTED_*`) keep the same two-state claim lists.
- AST-898 registry holding and consult fail-dest to `NEW_RETRY` remain documented and tested as routing, not claim.
- AST-1798 product contract: no cross-name claim companions; companion need not exist in registry.

**test(AST-1799) confirmation:** `TestAst882DispatchClaimStates` / `TestAst641DispatchClaimStates` / `TestAst898NewRetryQualifyHolding` — 12 passed (suffix-always; `HOMEPAGE_READY` never `WEBSITE_FOUND_RETRY`).

**Triage notes**

AST-1799 is test/bible-only (gap from Betty’s AST-1798 `TESTS: REVISE`). Scope: flip `TestAst882` / `TestAst641` / `TestAst898` claim asserts and `docs/test-bible/utils/config.md` claim-contract prose to suffix-always pairing; no `src/` edits; registry `retry_state` routing asserts stay.

No active statute or pattern needs a change:

- **`patt.task.dispatch-retry`** — claim is trigger + `{trigger}_RETRY`; routing via config `retry_state` is separate. The plan keeps that split (claim asserts flip; fail-dest / registry `retry_state` asserts unchanged).
- **`astral.dispatch.entity-state-bound`** / **`astral.batch.claim-process-release`** — not touched; bible alignment with AST-1798 product supports them.
- Test bible is not canon; updating it to match suffix-only claim law is documentation, not a directive amendment.

No F3 `validate-plan` fix mode from this board pass.
[AST-1797 | AST-1799] Joan/validate fix-board - complete 78c1bebf model=composer-2.5 - (15s) > OK


## Review-fix findings (AST-1799)

## Fix-specific checks

**`[bug-repro]`:** OK — no dedicated `[bug-repro]` tag (board `TESTS: OK`; qa-fix not spawned). Flipped assert bodies in `TestAst882DispatchClaimStates`, `TestAst641DispatchClaimStates`, and `TestAst898NewRetryQualifyHolding` pin concrete suffix-always To-be values (`HOMEPAGE_READY` → `HOMEPAGE_READY_RETRY`, `VALID_TITLE` → `VALID_TITLE_RETRY`, companion-less primaries → `[ts, f"{ts}_RETRY"]`). They would fail against pre-AST-1798 product and pass on current `dispatch_claim_states` — satisfies plan-fix repro intent.

**`## What must still hold`:** OK
- Retry-only rows (`VALID_TITLE_RETRY`, `NEW_RETRY`) still single-state.
- Unchanged suffix pairs (`JD_READY`, `WEBSITE_FOUND`, `NEW` job, `REQUESTED_*`) preserved.
- AST-898 registry `retry_state`, UI sections, and `consult_batch_fail_dest` → `NEW_RETRY` untouched (routing, not claim).
- AST-1798 suffix-only product contract reflected in claim asserts; no `src/` edits on this tip.

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on gap ticket (same pattern as AST-1798). Joan fix-board informal OK only.  
  **Recommendation:** No in-flight Canon Scope amendment required.

### advisory

- **Location:** `tests/component/core/test_dispatcher.py` `test_ast641_company_prefilter_passes_union_claim_states`  
  **Finding:** Still asserts `states == ["HOMEPAGE_READY", "WEBSITE_FOUND_RETRY"]` — red against AST-1798 product. Plan-fix § Blast radius explicitly leaves downstream dispatcher tests out of AST-1799 scope.  
  **Recommendation:** File follow-up or fold into a later dispatcher test sweep before assuming full `test_dispatcher.py` green on ftr; not a fix-now on this tip.

- **Location:** `docs/test-bible/utils/config.md` § AST-641 manifest table  
  **Finding:** Prose updated to suffix-always, but manifest row still cites `tests/component/core/test_dispatcher.py` **`test_ast641_*`** — that test encodes the old union.  
  **Recommendation:** Optional bible hygiene in a follow-up; not blocking AST-1799 scope.

## What's solid

- Diff is test/bible only — no `src/` changes; scope gate honored.
- Plan-fix § Proposed change (1)–(2) fully delivered: TestAst882/641/898 flipped; sibling `ACTIVE_SEARCH` and meteorite claim asserts flipped; bible § AST-641 / AST-882 / AST-898 prose updated with routing vs claim split.
- Routing asserts in `TestAst898NewRetryQualifyHolding` (`retry_state`, fail-dest matrix) correctly left unchanged.
- Closes AST-1798 `[board-betty] TESTS: REVISE` bar; ftr base already carries AST-1798 product (`8721f208`).
- Estimate **2** fits footprint.

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1797 In Progress; diff base `origin/ftr/AST-1797-retry-suffix-claim`) | → **Review Posted** → append artifact + `docs(AST-1799): Radia review — clean` on publish ref → post slim upshot `--as radia` → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |

With AST-1799 landed, the AST-1798 docs-acceptance split is closed for the Betty-flagged claim classes. Advisory: `test_dispatcher.py::test_ast641_company_prefilter_passes_union_claim_states` may still red on broader runs until a follow-up flips it.

`

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/5a3773ac45ef22d5543e2b022b1fbc98/3ed1ed8b-cfbb-4d08-939a-e00238cce690/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/1129750e-d200-47dd-b89a-3d15ae4d989d/store.db` |
| Radia | review | `/home/susan/.cursor/chats/5a3773ac45ef22d5543e2b022b1fbc98/2f036639-2d41-4513-bd5e-622fb417f1d8/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1797 (parent) | ftr/AST-1797-retry-suffix-claim |
| AST-1798 | sub/AST-1797/AST-1798-retry-suffix-claim |
| AST-1799 | sub/AST-1797/AST-1799-retry-suffix-claim-tests |

**Epic worktree:** `astral-AST-1797/` — one active sub checked out at a time.

---

## Bug: AST-1801 — claim union must not registry-validate companion states

Orphaned mini-parent: AST-1800 (no ancestor box checked). This section patches the historical home of union claim / AST-1798. Scope gate: AST-1801 `## Scope` / Component + Technical scope only (`roster` / `tracker` / `candidate` claim helpers).

### As-is

`prefilter_company` with `trigger_state=HOMEPAGE_READY` resolves `claim_states=["HOMEPAGE_READY","HOMEPAGE_READY_RETRY"]` via AST-1798 suffix-always `dispatch_claim_states`, then `get_new_company_batch(..., states=claim_states)` raises `ValueError: state must be one of [...], got 'HOMEPAGE_READY_RETRY'` because the multi-state branch requires every list member ∈ `COMPANY_STATES`. Dispatcher truncates the batch; the hop fails. The companion key is intentionally absent from the registry (AST-1798 / AST-641: do not seed synthetic `_RETRY` keys).

### To-be

When `states=` is provided, claim helpers pass the union through to SQL without registry-membership checks on list members. `HOMEPAGE_READY` may claim `['HOMEPAGE_READY','HOMEPAGE_READY_RETRY']` even when `HOMEPAGE_READY_RETRY` ∉ `COMPANY_STATES`; zero matching rows for an unused companion is fine. When `states` is `None`, the single primary `state` argument remains registry-validated. Data validation stays upstream of claim; do not add synthetic companions to any entity-state registry.

### Repro

Against current tip (AST-1798 product landed; this fix not applied):

```python
from src.utils import config as cfg
from src.core.roster import get_new_company_batch

assert cfg.dispatch_claim_states("HOMEPAGE_READY", "company") == [
    "HOMEPAGE_READY",
    "HOMEPAGE_READY_RETRY",
]
assert "HOMEPAGE_READY_RETRY" not in cfg.COMPANY_STATES

# Raises today (matches live log 2026-09-25 20:43:15):
get_new_company_batch(
    "HOMEPAGE_READY",
    limit=1,
    candidate_id="abrams",
    batch_id="repro-ast-1801",
    states=["HOMEPAGE_READY", "HOMEPAGE_READY_RETRY"],
)
# ValueError: state must be one of [...], got 'HOMEPAGE_READY_RETRY'
```

After fix: same call returns `(batch_id, companies)` with no ValueError (companies may be empty if no rows match either state).

### Root cause

AST-641 Stage 3 wired optional `states=` on claim wrappers and **validated every list member against the entity registry**. AST-1798 made claim pairing suffix-always and explicitly allowed companions absent from the registry, but left those wrapper loops in place. The raise site on the live log is `roster.get_new_company_batch` (~1412–1414); `tracker.get_new_job_batch` and `candidate.get_new_candidate_batch` share the same multi-state registry gate.

### Proposed change

1. **`src/core/roster.py` — `get_new_company_batch`** (~1408–1414):
   - Keep: when `states is None`, raise if `state` ∉ `COMPANY_STATES` (single-state callers stay bound).
   - Change: when `states` is provided, **do not** loop `for s in states` against `COMPANY_STATES` — pass `states` through to `claim_company_batch` unchanged.
   - Leave `state_config = COMPANY_STATES.get(state, {})` for batch_criteria (trigger-state keyed; empty dict if absent is fine).

2. **`src/core/tracker.py` — `get_new_job_batch`** (~1510–1514):
   - Keep: when `states is None`, call `_assert_valid_job_batch_claim_state(state)`.
   - Change: when `states` is provided, **do not** call `_assert_valid_job_batch_claim_state` on each member — pass `states` through to `database.claim_job_batch`.

3. **`src/core/candidate.py` — `get_new_candidate_batch`** (~1971–1979):
   - Keep: when `states is None`, validate `state` via `is_valid_candidate_batch_claim_state`.
   - Change: when `states` is provided, **do not** loop registry/`is_valid_candidate_batch_claim_state` on each member — pass `states` through to `database.claim_candidate_batch`.

4. **Out of scope / boundaries:** do **not** add `HOMEPAGE_READY_RETRY` (or other synthetic companions) to `COMPANY_STATES` / `JOB_STATES` / `CANDIDATE_STATES`. Do **not** change `dispatch_claim_states` (already suffix-always on AST-1798). Do **not** change data-layer `_state_in_sql` / claim SQL (already accepts arbitrary non-empty string lists). Smoke: `prefilter_company` with `HOMEPAGE_READY` + union claim completes without the ValueError.

### Blast radius

- **Claim path only:** multi-state dispatch claims (primary + `_RETRY` via `_run_unified`) stop failing when a companion key is absent from the registry. Live flip: `prefilter_company` / `HOMEPAGE_READY` no longer truncates on `HOMEPAGE_READY_RETRY`.
- **Single-state callers** (`get_new_*_batch(state, ...)` without `states=`) unchanged — still registry-gated.
- **SQL:** unused companion still matches zero rows — no error, no inventing rows.
- **Shared consumers:** dispatcher already passes `claim_states` from `dispatch_claim_states`; no change to pairing or score-floor gating.
- **Tests** that assert the multi-state ValueError for registry-absent companions (if any) would flip; AST-1798 plan item 2 already expected claim paths not to reject absent `{ts}_RETRY`. Betty owns test-tree flips if the board asks.

### What must still hold

- AST-1798 suffix-always pairing: primary → `[ts, f"{ts}_RETRY"]`; already-`*_RETRY` → `[ts]` only; no cross-name `retry_state` claim unions.
- Retry-only trigger rows still claim a single state (AST-641 AC).
- Score-floor gating still keyed off the dispatch row’s `trigger_state` via `dispatch_claim_uses_score_floor` (AST-641).
- Registry `retry_state` / `error_state` continue to drive failure **routing** writes; claim helpers still must not invent registry keys.
- `batch_id`-first claim → get → clear shape unchanged (`astral.batch.claim-process-release`).
- Direct single-state claim callers (tests / non-dispatch paths) still reject unknown primary `state` values when `states` is omitted.


## Fix-board Joan findings (AST-1801)

**Verdict: CANON: OK** — Dropping multi-state registry gates on `get_new_company_batch` / `get_new_job_batch` / `get_new_candidate_batch` when `states=` is set matches `patt.task.dispatch-retry` (companion need not exist in registry). Single-state callers stay registry-bound. No statute update; F3 not triggered.


## Review-fix findings (AST-1801)

## Fix-specific checks

**`[bug-repro]`:** not applicable — `[board-betty] TESTS: REVISE` defers absent-companion claim coverage to sibling **AST-1802** (gap ticket in plan doc). No qa-fix spawn / no `[bug-repro]` in diff. Same intentional product-only + docs-acceptance split as **AST-1798** / **AST-1791**.

**`## What must still hold`:** OK
- **AST-1798 suffix-always pairing:** `dispatch_claim_states` untouched in diff; only wrapper validation relaxed.
- **Retry-only rows single-state:** no change to dispatch pairing or `endswith("_RETRY")` logic.
- **Score-floor gating:** `dispatch_claim_uses_score_floor` / dispatcher call sites unchanged.
- **Registry `retry_state` / routing:** no registry or routing writes in diff.
- **`astral.batch.claim-process-release` shape:** `claim_*_batch` → `get_*_batch` → return unchanged; only pre-claim registry loops removed when `states=` set.
- **Single-state callers (`states is None`):** roster / tracker / candidate still registry-gate primary `state` (diff keeps `if states is None` branches only).

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on bug ticket. Joan fix-board cites `patt.task.dispatch-retry` informally only. Process observation for Archie — not blocking; product matches board-cited dispatch-retry law (same pattern as AST-1798 / AST-1799).  
  **Recommendation:** No in-flight Canon Scope amendment required unless Archie wants Radia comparability on every fix-lane bug.

- **Location:** `[board-betty] TESTS: REVISE` / sibling **AST-1802** (Plan Ready per plan doc)  
  **Finding:** No component test on this tip pins `get_new_*_batch(..., states=[primary, {primary}_RETRY])` with companion ∉ registry. Expected on product-only tip; AST-1802 owns repro-first flip + bible.  
  **Recommendation:** Chuckles: mark **Docs-Acceptance** on AST-1801 (mirror AST-1798). Do not block product UT on AST-1802; land AST-1802 before expecting roster/tracker/candidate absent-companion cases green on ftr.

### advisory

- **Location:** Board-cited law (informal, not frozen) — `patt.task.dispatch-retry`, `astral.dispatch.entity-state-bound`, `astral.batch.claim-process-release`  
  **Finding:** Diff aligns with Joan fix-board narrative: companions may be absent from registry at claim time; single-state path stays bound; claim→get shape preserved.  
  **Recommendation:** None for resolve-child.

## What's solid

- Diff isolates plan-fix § Proposed change (1)–(3): removes multi-state registry `for s in states` loops in `roster.get_new_company_batch`, `tracker.get_new_job_batch`, `candidate.get_new_candidate_batch`; inline comments cite AST-1801 / AST-1798.
- Scope gate honored: only scoped `src/core/{roster,tracker,candidate}.py` + plan-fix patch on `ast-641-…` feature doc; no registry seeding, no `dispatch_claim_states` / `database.py` edits.
- Plan fidelity: matches **To-be** (union passes through when `states=` set; `states is None` still validates primary).
- Estimate **3** fits footprint (three mirrored helpers + plan doc).
- Parent **AST-1800** In Progress with `origin/ftr/AST-1800-claim-union-no-registry-validate` present — **normal** fix-lane parent shape (not `ORPHANED — target dev`).

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1800 In Progress; diff base `origin/ftr/AST-1800-claim-union-no-registry-validate`) | → **Review Posted** → append artifact + `docs(AST-1801): Radia review — clean` on publish ref → post slim upshot `--as radia` → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |
| — | Sibling **AST-1802** | Parallel: close Betty `TESTS: REVISE` bar (test/bible only). |

**Chuckles note:** `[board-betty] TESTS: REVISE` owned by sibling gap AST-1802. Product tip docs-acceptance — no merge-tests on AST-1801.



## Docs-Acceptance (AST-1801)

Test-tree / absent-companion claim asserts owned by sibling gap AST-1802 (fix-board TESTS: REVISE). No merge-tests on this tip.

## Bug: AST-1802 — gap: claim-union absent-companion registry tests (AST-1801 board)

Sibling test gap for AST-1801 (`[board-betty] TESTS: REVISE`). Product fix (drop multi-state registry gates on claim helpers) lands on AST-1801; this ticket is **test/bible only**. Scope gate: AST-1802 `## Scope` (Component + Technical). Same plan-doc home as union claim / AST-1798 / AST-1801 (`ast-641-…`).

### As-is

`tests/component/core/test_roster.py::TestBatchApi` covers single-state reject (`test_get_new_company_batch_rejects_unknown_state`) and happy-path claim with `states=None`, but has **no** case that `get_new_company_batch(..., states=["HOMEPAGE_READY","HOMEPAGE_READY_RETRY"])` completes without `ValueError` when `HOMEPAGE_READY_RETRY` ∉ `COMPANY_STATES` (the live prefilter_company repro). `docs/test-bible/core/roster.md` has no entry for that multi-state / absent-companion contract. Job/candidate batch suites similarly lack an absent-companion multi-state case (candidate already passes in-registry `REQUESTED_ARTIFACTS_RETRY`; tracker multi-state case uses legacy hop labels, not a missing `_RETRY` key).

### To-be

Roster (required) and job/candidate (mirrors — product changed all three on AST-1801) claim tests assert: when `states=` includes a companion absent from the entity registry, the wrapper does **not** raise the registry `ValueError` / `not in allowed list` and still forwards `states=` to the claim mock. Single-state unknown primary still raises. Bible `docs/test-bible/core/roster.md` names the new coverage (and points at tracker/candidate mirrors if landed).

### Repro

Against a tree with AST-1801 product **not** applied (multi-state registry loop still present) and this gap **not** applied — the new asserts below are red:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestBatchApi -k 'absent_companion or rejects_unknown' \
  -q
```

Concrete contract (must fail pre-AST-1801, pass after):

```python
assert "HOMEPAGE_READY_RETRY" not in COMPANY_STATES
# Pre-fix: ValueError("… got 'HOMEPAGE_READY_RETRY'")
get_new_company_batch(
    "HOMEPAGE_READY",
    batch_id="ast-1802",
    states=["HOMEPAGE_READY", "HOMEPAGE_READY_RETRY"],
)
```

### Root cause

AST-1801 removes the multi-state registry gate that caused the live hop failure. Betty’s board found **missing coverage** — no test/bible line that pins “companion need not ∈ registry when `states=` is provided” — so the gap owns the flip (same pattern as AST-1799 for AST-1798).

### Proposed change

1. **`tests/component/core/test_roster.py` — `TestBatchApi`** (required):
   - Add a case (name e.g. `test_get_new_company_batch_states_allows_registry_absent_companion`) that monkeypatches `claim_company_batch` / `get_company_batch`, calls `get_new_company_batch("HOMEPAGE_READY", batch_id=…, states=["HOMEPAGE_READY","HOMEPAGE_READY_RETRY"])`, asserts **no** `ValueError`, and that `claim_company_batch` was invoked with `states=["HOMEPAGE_READY","HOMEPAGE_READY_RETRY"]`. Guard/assert `"HOMEPAGE_READY_RETRY" not in COMPANY_STATES` so the case stays honest if someone later seeds the key.
   - Keep `test_get_new_company_batch_rejects_unknown_state` unchanged (single-state reject still raises when `states` is omitted).

2. **`tests/component/core/test_tracker.py` — `TestBatchApi`** (mirror — in Scope “if needed”; land it):
   - Add a multi-state case with a primary ∈ `JOB_STATES` whose `{primary}_RETRY` is **absent** (e.g. `INVALID_TITLE` + `INVALID_TITLE_RETRY`), monkeypatch claim/get, assert no registry `ValueError` / `not in allowed list`, `states=` forwarded. Do not weaken existing single-state / hop reject cases.

3. **`tests/component/core/test_candidate.py` — `TestAst1259CandidateBatchApi`** (mirror — same):
   - Add a multi-state case with a primary ∈ `CANDIDATE_STATES` whose `{primary}_RETRY` is absent (e.g. `ACTIVE_SEARCH` / `PROSPECT` + fabricated `{primary}_RETRY` if that suffix key is missing), monkeypatch claim/get, assert no registry raise, `states=` forwarded. Leave existing in-registry `REQUESTED_ARTIFACTS_RETRY` claim case as-is.

4. **`docs/test-bible/core/roster.md`** — add an **AST-1802 · AST-1801** section: multi-state claim with registry-absent companion must not raise; single-state unknown primary still rejects; name the new roster test node id(s); briefly note tracker/candidate mirror node ids if present. No other bible pages unless a later board expands.

5. **Out of scope:** no `src/` product edits (AST-1801); do not seed `HOMEPAGE_READY_RETRY` into registries; do not change `dispatch_claim_states` asserts (those are AST-1799).

### Blast radius

- New/revised component cases go **red** against pre-AST-1801 product (desired repro-first) and **green** once AST-1801 product is on the tree (or after merge into ftr).
- Existing single-state reject and happy-path claim tests must stay green.
- No product blast; bible is documentation of the AST-1801 contract only.

### What must still hold

- AST-1801 product contract: when `states=` is provided, claim helpers do not registry-validate list members; when `states` is None, primary `state` stays registry-bound.
- AST-1798 suffix-always pairing unchanged; do not re-assert cross-name `retry_state` companions.
- Single-state unknown primary still raises on roster / job / candidate claim helpers.
- No synthetic `_RETRY` keys added to `COMPANY_STATES` / `JOB_STATES` / `CANDIDATE_STATES` as part of this gap.


## Fix-board Joan findings (AST-1802)

**Verdict: CANON: OK** — Test/bible-only gap locking absent-companion claim contract; no product or canon edits.
