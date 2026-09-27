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
| Ada | engineer | `/home/susan/.cursor/chats/1455e88c7dd6c45ad05cd7610e9f8231/43ae5743-b955-4005-8968-d46be29d901d/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/43d31f32-ec85-4464-b8dc-5a028b4a3304/store.db` |
| Radia | review | `/home/susan/.cursor/chats/1455e88c7dd6c45ad05cd7610e9f8231/1c630dcc-dea8-4614-ab3e-c8b87b7fdeb8/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1804 (parent) | ftr/AST-1804-fetch-avail-retry |
| AST-1805 | sub/AST-1804/AST-1805-fetch-avail-retry |
| AST-1806 | sub/AST-1804/AST-1806-retry-registry-purge |
| AST-1807 | sub/AST-1804/AST-1807-implicit-retry-tests |
| AST-1808 | sub/AST-1804/AST-1808-purge-retry-tests |

**Epic worktree:** `astral-AST-1804/` — one active sub checked out at a time.

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


## Review-fix findings (AST-1802)

## Fix-specific checks

**`[bug-repro]`:** OK — Betty qa-fix manifest names `test_get_new_company_batch_states_allows_registry_absent_companion` as the repro gate. Body pins **To-be** concretely: guard `"HOMEPAGE_READY_RETRY" not in COMPANY_STATES`, live pairing `states=["HOMEPAGE_READY","HOMEPAGE_READY_RETRY"]`, no `ValueError`, and `claim_company_batch` kwargs `states` forwarded unchanged. Would fail pre–AST-1801 (multi-state registry loop); passes with AST-1801 product (on ftr per merge ancestry). Tracker/candidate mirrors assert absent `{primary}_RETRY` + `states=` forward — same contract, not tautological.

**`## What must still hold`:** OK
- **AST-1801 contract** encoded in new cases + bible § AST-1802 · AST-1801; no `src/` edits.
- **AST-1798 / `dispatch_claim_states`:** untouched; no cross-name companion asserts added.
- **Single-state reject:** `test_get_new_company_batch_rejects_unknown_state` unchanged in diff (still in manifest).
- **No registry seeding:** tests assert companions absent from `COMPANY_STATES` / `JOB_STATES` / `CANDIDATE_STATES`; no config/registry diffs.

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on gap ticket (same pattern as AST-1799 / AST-1801). Joan fix-board OK only.  
  **Recommendation:** No Canon Scope amendment required.

### advisory

- **Location:** `test_roster.py::TestBatchApi::test_get_new_company_batch_states_allows_registry_absent_companion`  
  **Finding:** No `[bug-repro]` docstring/first-line tag (unlike e.g. AST-1724 roster case); Betty labels it in the qa-fix manifest only. Machinery that greps `[bug-repro]` may miss it.  
  **Recommendation:** Optional bible/docstring hygiene later; not fix-now — assertions satisfy repro-first intent.

- **Location:** `test_roster.py` absent-companion case  
  **Finding:** Asserts companion ∉ registry but not explicitly `HOMEPAGE_READY in COMPANY_STATES` (plan repro assumes primary is valid). Low risk given `states=` path and live repro state.  
  **Recommendation:** None for resolve-child.

## What's solid

- Plan-fix § Proposed change (1)–(4) delivered: roster + tracker + candidate mirrors, bible table + run command; item (5) boundaries honored (no `src/`, no `dispatch_claim_states` edits).
- Scope gate: tests + `docs/test-bible/core/roster.md` + feature-doc plan patch only — aligns with `astral.git.betty-no-src-or-features` / engineer test-tree ban (Betty `merge-tests` path).
- Closes AST-1801 `[board-betty] TESTS: REVISE` bar; mirrors AST-1799 gap pattern for AST-1798.
- Estimate **2** fits footprint.
- Parent **AST-1800** In Progress; diff base `origin/ftr/AST-1800-claim-union-no-registry-validate` — **normal** parent shape.

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1800 In Progress) | → **Review Posted** → append artifact + `docs(AST-1802): Radia review — clean` on publish ref → post slim upshot `--as radia` → §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |

## Bug: AST-1805 — `_RETRY` as implicit substate (no explicit `_RETRY` registry states; validators accept `{base}_RETRY`)

Parent AST-1804 (orphaned mini-parent). Binding rule (Susan, AST-1804): *"There should be NO explicit _RETRY state in config. It is an implicit substate for exactly this purpose. Always query for _RETRY when claiming a batch with the base state, but don't validate the full RETRY string."*

### As-is
- The entity registries declare **18 explicit `*_RETRY` keys**: 13 in `JOB_STATES`, 3 in `COMPANY_STATES`, 2 in `CANDIDATE_STATES`. **~60 `prior_states` entries** name them. `config.py` also carries ~40 more `"X_RETRY"` literals, in `retry_state` / `error_state` / `retry_trigger_state` / `pass_states` / `fetch_job_pages_trigger_states`, `IN_REVIEW_STATES`, `JOBS_IN_REVIEW_UI_SECTIONS`, `JOBS_IN_REVIEW_GRADE_FIELD`, `JOBS_UI_STATE_RUBRIC_OVERRIDE`, `inflight_hide_states`, and `company_state_transitions`. Outside config there are literals in `consult._INPUT_STATE_TO_TASK`, `consult.py:1858`, and `roster.py:886`.
- Validators accept a `_RETRY` state only when its **full string** is a registry key:
  - `tracker.transition_job_state` → `validate_value(_JOB_STATE_LIST, …)` + `JOB_STATES[to]["prior_states"]`
  - `roster.transition_company_state` → `validate_value(_COMPANY_STATE_LIST, …)`
  - `candidate.transition_candidate_state` / `_candidate_prior_states` → `CANDIDATE_STATES[to]`
  - `config.is_valid_job_batch_claim_state` / `is_valid_candidate_batch_claim_state`
  - `config._dispatch_sort_by_for`
  - `api_admin` dispatch-row trigger validation (`registry_ts not in registry`, two sites)
  - the candidate `retry_state` assert (`config.py` ~1976)
- Claim/count (`dispatch_claim_states`) already pairs `[base, base_RETRY]` without registry lookup (AST-1798/AST-1800). Only the modelling and validation are explicit.

### To-be
- Registries hold **bases only**. `{base}_RETRY` is valid wherever `{base}` is registered. Validators check the base, never the full `_RETRY` string.
- Prior rules for retries are **derived from the base** (rule below). There are no `*_RETRY` entries in `prior_states`.
- Every remaining reference to a retry substate in config is built from its base via `retry_of("<BASE>")`. There are no `"X_RETRY"` string literals in config.
- Claim is unchanged: `dispatch_claim_states(ts)` → `[ts, f"{ts}_RETRY"]`.

### Repro
Deterministic against current config (`python3` in the worktree, tip `51d4f793`):
```python
from src.utils.config import JOB_STATES, COMPANY_STATES, CANDIDATE_STATES
[k for r in (JOB_STATES, COMPANY_STATES, CANDIDATE_STATES) for k in r if k.endswith("_RETRY")]
# → 18 keys (VALID_TITLE_RETRY … METEORITE_PASSED_LIKE_RETRY, WEBSITE_FOUND_RETRY,
#   JOBLIST_IDENTIFIED_RETRY, PREFILTER_PASSED_RETRY, REQUESTED_RESUME_RETRY, REQUESTED_ARTIFACTS_RETRY)
"PASSED_GET_RETRY" in JOB_STATES   # False — yet dispatch_claim_states("PASSED_GET","job") claims it
from src.core import tracker
tracker.transition_job_state([<job in PASSED_DO>], "PASSED_GET_RETRY")
# → ValueError "not in allowed list" (full string validated; base PASSED_GET is registered)
```

### Root cause
Retry was modelled as **explicit registry states** (AST-630/898/1155/1338 era). Claim moved to suffix-always pairing (AST-1798), but the registries, prior tables, and transition validators still treat every `*_RETRY` as a separately declared state. The two models disagree: claim counts retries that validators can only accept when explicitly declared.

### Derived prior rule (verified)
Let `R = registry`, `feeders(B) = {B} ∪ {S ∈ R : R[S].retry_state == retry_of(B)}`. This covers cross-base routing: `VALID_TITLE → NEW_RETRY`, `HOMEPAGE_READY → WEBSITE_FOUND_RETRY`.
- **Into `retry_of(B)`**: effective priors = `feeders(B) ∪ {retry_of(B)}`, where `retry_of(B)` covers re-entry (candidate `REQUESTED_*_RETRY`, company `WFR → WFR`).
- **Into base `T`** with `R[T].prior_states = P` (`None` stays `None`): effective priors = `P ∪ {retry_of(p) : p ∈ P} ∪ {R[p].retry_state : p ∈ P, set} ∪ {retry_of(T)}`, where `retry_of(T)` covers the retry draining back to its base (candidate `REQUESTED_RESUME_RETRY → REQUESTED_RESUME`).

I checked this rule by script against every explicit edge in today's `JOB_STATES` and `CANDIDATE_STATES`, and it reproduces **all** of them. `FAILED_JOBLIST ← NEW_RETRY` is covered via `VALID_TITLE.retry_state`. **Loosening (accepted):**
- It allows `retry_of(p)` edges for bases that never route into retry today, e.g. `BOT_BLOCKED_RETRY → PASSED_JOBLIST`. No writer produces those states.
- It allows `retry_of(T) → T` self-drain for job bases, e.g. `JD_READY_RETRY → JD_READY`.

Company transitions: `transition_company_state` has no prior gate, and `ASTRAL_CONFIG["company_state_transitions"]` has **no consumer** in `src/`. Only literal cleanup applies there.

### Estimate & split
Honest size: **8 points**. That's over 5, so this splits into two sibling children. Stage A is behavior-neutral (retry keys still present) and Stage B is a mechanical purge on top of it. Chuckles files Stage B as a sibling under AST-1804, **blockedBy AST-1805**.

| Child | Stage | Est |
|-------|-------|-----|
| **AST-1805** (this ticket) | A — implicit-retry helpers + every validator resolves through the base | 3 |
| **new sibling** (`AST-1804` child, e.g. `fix: purge explicit _RETRY registry keys and literals`) | B — delete registry keys, strip retry priors, derive every literal via `retry_of` | 5 |

### Proposed change — Stage A (AST-1805)

**A1. `src/utils/config.py` — new helpers, defined above `TASK_CONFIG` (line ~198) so Stage B can use `retry_of` inside every dict:**
```python
RETRY_SUFFIX = "_RETRY"

def retry_of(base: str) -> str:
    """Implicit retry substate name for a registered base state."""
    return f"{base}{RETRY_SUFFIX}"

def retry_base(state: Optional[str]) -> Optional[str]:
    """Base of an implicit retry substate, or None when state has no _RETRY suffix."""
    s = (state or "").strip()
    return s[: -len(RETRY_SUFFIX)] if s.endswith(RETRY_SUFFIX) and len(s) > len(RETRY_SUFFIX) else None

def registered_base(registry: Dict[str, Any], state: Optional[str]) -> Optional[str]:
    """Registry key that owns state: itself, or the base of {base}_RETRY. Never validates the full retry string."""

def is_registered_state(registry: Dict[str, Any], state: Optional[str]) -> bool:
    return registered_base(registry, state) is not None

def state_prior_states(registry: Dict[str, Any], to_state: str) -> Optional[List[str]]:
    """Effective prior_states per the derived prior rule above (retry targets always derived, even if a legacy key exists)."""
```
- `registered_base` returns `s` when `s in registry`, else `retry_base(s)` when that base is in the registry, else `None`.
- `state_prior_states` raises `KeyError` when `to_state` is not registered. Retry targets **always** use the derived rule, even while legacy keys still exist, so Stage A exercises the derivation and Stage B's key deletion changes nothing.
- `dispatch_claim_states` is **untouched** (AST-1798 boundary).

**A2. Validators — each swaps a full-string membership check for `is_registered_state` / `registered_base`, and each `…["prior_states"]` read for `state_prior_states`:**
- `src/core/tracker.py`
  - `transition_job_state`: replace `validate_value(_JOB_STATE_LIST, to_state)` with `if not is_registered_state(JOB_STATES, to_state): raise ValueError(f"Value {to_state!r} not in allowed list: {_JOB_STATE_LIST}")`. The message text stays the same. `prior_states = state_prior_states(JOB_STATES, to_state)`.
  - `legal_job_successor_states`: use `state_prior_states(JOB_STATES, name)` per key.
  - `_job_state_matches_prior`: unchanged, because the expansion happens in the prior list.
- `src/core/roster.py` `transition_company_state`: same replacement as tracker, against `COMPANY_STATES` / `_COMPANY_STATE_LIST`.
- `src/core/candidate.py`
  - `_candidate_prior_states`: `if not is_registered_state(CANDIDATE_STATES, to_state): raise ValueError(...)`, then `return state_prior_states(CANDIDATE_STATES, to_state)`.
  - `transition_candidate_state`: use `not is_registered_state(CANDIDATE_STATES, to_state)` in place of `not in CANDIDATE_STATES`.
  - `run_requested_artifacts_dispatch` bare-trigger guard (~3670): same swap.
- `src/utils/config.py`
  - `is_valid_job_batch_claim_state` / `is_valid_candidate_batch_claim_state`: use `registered_base(...) is not None` in place of `s in REG`.
  - `_dispatch_sort_by_for`: job branch uses `not is_registered_state(JOB_STATES, trigger_state)`; company branch reads `COMPANY_STATES.get(registered_base(COMPANY_STATES, trigger_state) or trigger_state)`. Base and retry `batch_criteria` are identical today.
  - Candidate `retry_state` assert (~1976): `is_registered_state(CANDIDATE_STATES, _retry)`.
- `src/ui/api/api_admin.py` dispatch-task trigger validation, both sites (mailbox candidate branch and the general branch): `if not is_registered_state(registry, registry_ts)`. `state_options` needs no code change; it lists bases once Stage B lands.
- **Must NOT resolve through the base** (retry-of-retry routes to terminal): `consult._consult_batch_fail_dest`, `roster._prefilter_batch_fail_dest`, `candidate._requested_stage_failure_target`, `gazer` retry checks. They keep their direct `REG.get(st, {}).get("retry_state")` / equality reads.
- Verify only, no change: `database.count_eligible_for_dispatch_task` / `_state_in_sql` (no registry validation) and `dispatcher._run_unified` (uses `dispatch_claim_states`).

### Proposed change — Stage B (sibling, blockedBy AST-1805)
Mechanical rule for `src/utils/config.py`, with zero behavior change given Stage A:
1. **Delete** the 18 `*_RETRY` registry keys (13 `JOB_STATES`, 3 `COMPANY_STATES`, 2 `CANDIDATE_STATES`).
2. **Remove** every `*_RETRY` entry from every `prior_states` list, since they're now derived by `state_prior_states`.
3. **Replace** every remaining `"X_RETRY"` string literal with `retry_of("X")`. That covers:
   - registry `retry_state` fields;
   - task-config `retry_state` / `error_state` / `retry_trigger_state` / `pass_states` / `fetch_job_pages_trigger_states` (~840, 905, 1208, 1281, 1318, 2046, 2062–2073, 2260, 2266);
   - the UI lists `IN_REVIEW_STATES`, `JOBS_IN_REVIEW_UI_SECTIONS`, `JOBS_IN_REVIEW_GRADE_FIELD`, `JOBS_UI_STATE_RUBRIC_OVERRIDE`, and `inflight_hide_states`;
   - the `company_state_transitions` pairs.
   Cross-base mappings keep their explicit key (e.g. `retry_of("NEW"): "joblist_grades"`). Do **not** derive those maps by comprehension from base keys: `NEW` has no grade field, but `NEW_RETRY` does.
4. Asserts that check retry names against a registry switch to `is_registered_state`: the `grade_field` assert (~4197) and the `inflight_hide_states` assert (~4186).
5. `src/core/consult.py`:
   - `_INPUT_STATE_TO_TASK` drops its 6 retry literals and adds `_INPUT_STATE_TO_TASK.update({retry_of(k): v for k, v in list(_INPUT_STATE_TO_TASK.items())})`. Every retry maps the same as its base today, and this is a legacy map with no `src/` consumer.
   - Line ~1858: the tuple becomes `("VALID_TITLE", retry_of("VALID_TITLE"), retry_of("NEW"))`.
6. `src/core/roster.py` ~886: the tuple becomes `("WEBSITE_FOUND", retry_of("WEBSITE_FOUND"))`.
7. `grep -n '_RETRY"' src/utils/config.py` must return no state literals. Only the `RETRY_SUFFIX` definition and docstrings remain.

### Blast radius
- **Admin**
  - `state_options` loses 18 retry entries once Stage B lands, so admin trigger dropdowns show bases only.
  - Existing dispatch rows with a `*_RETRY` trigger still validate via `is_registered_state`.
- **Jobs UI**
  - `legal_next_states` (via `api_jobs` → `legal_job_successor_states`) stops offering retry targets once keys are gone, because it iterates registry keys. Manual moves into retry are no longer offered.
  - In Review retry buckets stay, via `retry_of` entries.
- **Transition gates loosen slightly** per the derived rule (never-produced retry states, plus job self-drain `X_RETRY → X`).
- **Tests (Betty's)** that assert retry keys exist in the registries, assert explicit `prior_states` contents, or equality-check `state_options` / registry key lists will break in Stage B. `tests/component/core/test_consult.py` `_INPUT_STATE_TO_TASK` retry asserts stay green (derived keys). Expect fix-board **TESTS: REVISE** → gap sibling.
- **Shared modules:** `tracker`, `roster`, `candidate`, `api_admin`, and `config` claim/sort helpers. `dispatcher` and `database` are unchanged.

### What must still hold
- AST-641 / AST-1798: a primary claims and counts `[ts, f"{ts}_RETRY"]`; a retry-only row claims `[ts]`; Available and claim use the same list. `dispatch_claim_states` is byte-identical.
- AST-1800: the `states=` claim path does not registry-validate the companion.
- AST-892: `fetch_website` excludes prefilter second-strike `WEBSITE_FOUND_RETRY` rows with homepage text (claim and count).
- AST-642 routing: a primary failure goes to its retry holding state; a failure while in `*_RETRY` goes to terminal/error. There is no new routing into retry substates.
- Every transition legal today stays legal (verified by the derived-rule script above).
- Config still imports cleanly, with all module asserts passing, after each stage.


## Fix-board Joan findings (AST-1805) — AST-1805 (Stage A only)

**Ticket:** AST-1805 · parent AST-1804 · publish ref `origin/sub/AST-1804/AST-1805-fetch-avail-retry`  
**Read:** `plan-fix` § Bug: AST-1805 (As-is / To-be / Repro / Root cause / Proposed change Stage A / Blast radius / What must still hold); roster skim from `canon/statutes/README.md` + overlapping active directives; Susan binding rule on implicit `_RETRY`.

**The one question:** Does Stage A’s proposed product change conflict with or require updating any directive in force?

**Answer:** No. Stage A closes the gap between today’s explicit-registry validators and canon that already treats `_RETRY` as a suffix substate, not a separate registry instance.

### Overlap review (not R1–R7)

| Directive | Overlap | vs Stage A |
|-----------|---------|------------|
| **`patt.task.dispatch-retry`** | Retry suffix, claim union, validation via base | **Aligns.** Arc 1–2: no separate retry instance; suffixed states need not be registry keys; validation uses the non-suffixed root. Stage A’s `registered_base` / `is_registered_state` and derived priors implement that. `dispatch_claim_states` stays byte-identical (AST-641 / AST-1798). |
| **`astral.batch.claim-process-release`** | Claim → process → release | **Unchanged shape.** Blast radius names shared modules; dispatcher/database unchanged. |
| **`astral.dispatch.entity-state-bound`** | `trigger_state` must be a real claim/dispatch state | **Aligns** once validators accept `{base}_RETRY` via registered base (Susan rule). “Real state” reads as dispatch-valid for that entity registry, not “must be a literal dict key.” |
| **`astral.state.job-prior-states-enforced`** | Prior gating on job transitions | **Still holds.** Tracker uses `state_prior_states` instead of raw `JOB_STATES[to]["prior_states"]`; plan verifies derived rule reproduces today’s edges (accepted loosening documented in plan-fix, not a new precedent). |
| **`astral.config.config-source-of-truth`** | Helpers in `config.py` | **Conforming.** `RETRY_SUFFIX`, `retry_of`, `retry_base`, `registered_base`, `state_prior_states` live in the registry module as planned. |
| **`astral.standards.in-scope-only`** | Touch named layers only | **Conforming.** Stage A scopes validators + config helpers; explicitly excludes fail-routing paths that must keep direct `retry_state` reads. |

**Out of scope for this pass (AST-1806):** purging 18 explicit keys and ~40 `"X_RETRY"` literals is Stage B; that is mechanical follow-on, not a canon amendment requirement for Stage A. Remaining explicit keys during Stage A are legacy surface until the sibling lands; they do not override `patt.task.dispatch-retry`’s “no separate instance” model.

**ESCALATE bar:** Susan’s AST-1804 binding rule already decides architecture (implicit substate, claim always base+suffix, never validate full `_RETRY` string). Derived-prior loosening is accepted in the plan-fix patch. No ambiguous statute intent that needs Archie before `make-fix`.

**F3 (`validate-plan` fix mode):** Not triggered from this board pass.

---


## Review-fix findings (AST-1805)

**`[bug-repro]`:** not applicable — `[board-betty] TESTS: REVISE` on sibling **AST-1807**; qa-fix did not run; no `[bug-repro]` on tip (spawn prompt confirmed). Same product-only + gap-sibling split as AST-1798 / AST-1801 / AST-1802.

**`## What must still hold`:** OK  
- **AST-641 / AST-1798:** `dispatch_claim_states` has no hunks in the ftr…sub diff; suffix-always pairing unchanged.  
- **AST-1800:** `dispatcher.py`, `database.py`, and multi-state claim wrappers untouched — `states=` relaxation not regressed.  
- **AST-892:** `fetch_website_prefilter_second_strike_filter` / gazer claim filter paths not in diff.  
- **AST-642 routing:** Plan § “must NOT resolve through the base” fail-dest paths (`consult`, `gazer`, roster/candidate failure targets) unchanged; only validator / prior expansion paths updated.  
- **Transition legality:** Stage A intentionally applies derived priors via `state_prior_states` (accepted loosening in plan-fix); no evidence in diff of removed enforcement gates beyond that plan.  
- **Config load:** Module asserts updated (`retry_state` assert uses `is_registered_state`); helpers placed above `TASK_CONFIG` as planned.

## Canon scores

(no frozen canon list on Linear Description — fix-lane pattern; zero ids locked at Plan Approved; scored set empty)

## Column diff vs plan stage

no plan-stage scores attached (F3 validate-plan fix mode not triggered; Joan fix-board `[board-joan] CANON: OK` only)

## Frame diff

(none)

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on bug ticket. Joan fix-board overlap table cites `patt.task.dispatch-retry`, `astral.batch.claim-process-release`, `astral.dispatch.entity-state-bound`, `astral.state.job-prior-states-enforced`, `astral.config.config-source-of-truth`, `astral.standards.in-scope-only` informally only — same process pattern as AST-1798 / AST-1801 / AST-1802.  
  **Recommendation:** No in-flight Canon Scope amendment required unless Archie wants Radia comparability on every fix-lane bug; product aligns with board narrative.

- **Location:** `[board-betty] TESTS: REVISE` / sibling **AST-1807**  
  **Finding:** No component test on this tip pins `transition_job_state` → `{base}_RETRY`, derived-prior helpers, or per-validator `{base}_RETRY` branches Betty named. Expected on Stage A product tip; AST-1807 owns repro-first coverage.  
  **Recommendation:** Chuckles: **Docs-Acceptance** on AST-1805 (mirror AST-1801). Do not block product UT on AST-1807; land AST-1807 before expecting new implicit-retry contracts green on ftr.

### advisory

- **Location:** Linear `## Component scope` vs diff  
  **Finding:** Description still lists `consult.py` / `gazer.py` as modified; Stage A plan and tip touch only `config.py`, `tracker.py`, `roster.py`, `candidate.py`, `api_admin.py` (+ plan doc). Matches Stage A split (“no deletions yet”; fail-dest paths unchanged).  
  **Recommendation:** Optional Description hygiene when AST-1806 lands; not fix-now.

- **Location:** Board-cited law (informal, not frozen)  
  **Finding:** Diff implements Arc 1–2 of `patt.task.dispatch-retry`: `registered_base` / `is_registered_state` resolve `{base}_RETRY` through the base; `dispatch_claim_states` untouched; fail-routing still uses direct `retry_state` reads where plan forbade base resolution.  
  **Recommendation:** None for resolve-child.

## Notes (informal board overlap — not scored)

| Directive | vs Stage A diff |
|-----------|-----------------|
| `patt.task.dispatch-retry` | Aligns — validators + derived priors; claim helper unchanged. |
| `astral.batch.claim-process-release` | Unchanged claim/SQL/dispatcher shape in diff. |
| `astral.dispatch.entity-state-bound` | Admin + batch claim validators accept implicit retries via base. |
| `astral.state.job-prior-states-enforced` | Still enforced via `state_prior_states` + `_job_state_matches_prior`. |
| `astral.config.config-source-of-truth` | Helpers live in `config.py` as specified. |
| `astral.standards.in-scope-only` | Diff stays inside Stage A file set; no registry purge (AST-1806 scope). |

## What's solid

- Diff isolates plan-fix § Proposed change — Stage A (A1 helpers + A2 validators): `retry_of` / `retry_base` / `registered_base` / `is_registered_state` / `state_prior_states`; `transition_*` and admin trigger checks; batch-claim and `_dispatch_sort_by_for` company branch via `registered_base`.  
- Susan binding rule honored: no explicit `_RETRY` registry purge on this tip; validation resolves through base, not full retry string membership.  
- Boundaries honored: `dispatch_claim_states` byte-identical; no `consult`/`gazer`/`dispatcher`/`database` product edits.  
- Plan fidelity: Stage A only — 18 explicit keys remain; derived priors exercised even while legacy keys exist (Stage B safe).  
- Estimate **3** fits footprint (five `src/` modules + plan-fix patch).  
- Parent **AST-1804** with `origin/ftr/AST-1804-fetch-avail-retry` present — **normal** fix-lane parent shape (not orphaned merge-to-dev).

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1804; diff base `origin/ftr/AST-1804-fetch-avail-retry`) | → **Review Posted** → append artifact + `docs(AST-1805): Radia review — clean` on publish ref → post slim upshot `--as radia` → §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |
| — | Sibling **AST-1807** | Parallel: close Betty `TESTS: REVISE` bar (test/bible only). **AST-1806** remains blocked until UT on Stage A. |

**Chuckles note:** `[board-betty] TESTS: REVISE` owned by sibling gap **AST-1807**. Product tip docs-acceptance — no merge-tests on AST-1805. Chuckles verified 195 baseline failures parity (zero new / zero fixed) — not re-litigated here.

**Docs-Acceptance (AST-1805):** product tip only; `[board-betty] TESTS: REVISE` is owned by gap sibling AST-1807. No merge-tests on this tip. Touched-area suites: 195 failures on origin/dev and on the tip, identical sets (verified by Chuckles).


## Bug: AST-1806 — purge explicit `_RETRY` states from entity-state registries (Stage B of AST-1805)

Parent AST-1804. Stacks on AST-1805 (Stage A, merged on `ftr/AST-1804-fetch-avail-retry`): validators already resolve `{base}_RETRY` through the base via `is_registered_state` / `registered_base` / `state_prior_states`. Susan's binding rule: *no explicit `_RETRY` state in config.*

### As-is
- `config.py` still declares 18 `*_RETRY` registry keys:
  - `JOB_STATES` (13): ~2543–2615
  - `COMPANY_STATES` (3): 1269, 1280, 1282
  - `CANDIDATE_STATES` (2): 1349, 1386
- `*_RETRY` entries still sit in `prior_states` lists across `JOB_STATES` (~2545–2613) and `CANDIDATE_STATES` (1343, 1354, 1360, 1375, 1391, 1397).
- There are ~45 more `"X_RETRY"` string literals in config (inventory under **Proposed change**).
- Code literals outside config: `consult._INPUT_STATE_TO_TASK` (6 entries), `consult.py` ~1858, `roster.py` ~886.
- These consumers look up a runtime state directly by its full key, so they depend on the explicit keys existing:
  - `roster.claim_company_batch` (~1419)
  - `database.save_company` (~1127)
  - `candidate.check_context_complete` (~2459)
  - `candidate._requested_stage_failure_target` (~3611)
  - `api_system._progress_rank` (~46)
- Carried from AST-1805: `_requested_stage_failure_target(bare_trigger, …)` indexes `CANDIDATE_STATES[primary]["retry_state"]`. A **retry-only** candidate dispatch row (`REQUESTED_*_RETRY` trigger) already raises `KeyError` there, because the legacy retry keys carry no `retry_state` / `error_state`.

### To-be
- The three registries hold **bases only**, and no `prior_states` list names a `*_RETRY`: `state_prior_states` derives them.
- Every remaining retry reference in config is written as `retry_of("<BASE>")`. No `"X_RETRY"` state literal remains in config, consult, or roster code.
- Consumers that look up a runtime state resolve through `registered_base`, so behavior is identical.
- A retry-only candidate row routes its failure to `error_state` (AST-642: failing while on retry goes to terminal) instead of raising `KeyError`.
- Claim is unchanged: `dispatch_claim_states`, AST-1800 `states=`, and the AST-892 filter all stay as they are.

### Repro
```python
from src.utils.config import JOB_STATES, COMPANY_STATES, CANDIDATE_STATES
sum(k.endswith("_RETRY") for r in (JOB_STATES, COMPANY_STATES, CANDIDATE_STATES) for k in r)  # → 18 (want 0)
# KeyError carry-over (today, retry-only candidate row):
from src.core.candidate import _requested_stage_failure_target
_requested_stage_failure_target("REQUESTED_ARTIFACTS_RETRY", "REQUESTED_ARTIFACTS_RETRY")  # → KeyError 'retry_state'
```

### Root cause
Stage A made the explicit keys redundant for validation, but the data is still declared, and five consumers still depend on the retry key existing because they look up the runtime state directly.

### Proposed change

**Gate first — the purge only proceeds if this passes before and after the deletion.** Run this in the worktree (`~/astral-tests/.venv/bin/python`) once on the pre-change tip and once after steps B1–B2. The two snapshots must be **identical**. A dry run in memory (keys and retry priors stripped from copies) already gives **0 diffs** across 110 job / 62 company / 38 candidate targets.
```python
import src.utils.config as C
def snap(R):
    bases = [k for k in R if not k.endswith(C.RETRY_SUFFIX)]
    out = {}
    for t in bases + [C.retry_of(b) for b in bases]:
        P = C.state_prior_states(R, t)
        out[t] = None if P is None else frozenset(p for p in P if not p.endswith("_RETRY_RETRY"))
    return out
{n: snap(getattr(C, n)) for n in ("JOB_STATES", "COMPANY_STATES", "CANDIDATE_STATES")}
```
Any diff means stop and don't publish; comment the diff on the ticket.

**B1. `src/utils/config.py` — registries**
- Delete the 18 keys: `VALID_TITLE_RETRY`, `NEW_RETRY`, `JD_READY_RETRY`, `PASSED_JD_RETRY`, `PASSED_DO_RETRY`, `CULTURE_READY_RETRY`, `PASSED_LIKE_RETRY`, `METEORITE_{NEW,QUALIFIED,PASSED_JD,PASSED_DO,PASSED_GET,PASSED_LIKE}_RETRY`, `WEBSITE_FOUND_RETRY`, `JOBLIST_IDENTIFIED_RETRY`, `PREFILTER_PASSED_RETRY`, `REQUESTED_RESUME_RETRY`, `REQUESTED_ARTIFACTS_RETRY`. Move each deleted key's trailing `# …` comment (e.g. "grade_do incomplete-grade holding (AST-1155)") onto its base's line as `# retry_of: …` so the history stays.
- Remove every `*_RETRY` element from every `prior_states` list: job ~2545–2613, candidate 1343, 1360, 1375, 1397. The two retry-key entries at 1354/1391 go away with their keys.
- Registry `retry_state` values become `retry_of("<BASE>")`, keeping cross-base values as-is: `VALID_TITLE` → `retry_of("NEW")`, and `HOMEPAGE_READY` (1272) → `retry_of("WEBSITE_FOUND")`.

**B2. `src/utils/config.py` — other literals → `retry_of("<BASE>")`**, same value, only the spelling changes:
- Task configs:
  - `error_state` 904 (`PASSED_LIKE`), 969 (`METEORITE_PASSED_LIKE`)
  - `retry_state` 2110, 2127, 2137, 2324
  - `pass_states` 2126
  - `retry_trigger_state` 2135
  - `fetch_job_pages_trigger_states` 2330
- `IN_REVIEW_STATES` 3563–3569, and the `JOBS_IN_REVIEW_UI_SECTIONS` `"state"` values 3995–4020 (labels unchanged).
- Keys of `JOBS_IN_REVIEW_GRADE_FIELD` 4114–4133 and `JOBS_UI_STATE_RUBRIC_OVERRIDE` 4158. Keep the explicit keys: `NEW_RETRY → joblist_grades` is cross-base, so no comprehension.
- `inflight_hide_states` 4249.
- `company_state_transitions` pairs 4557–4616.
- Docstrings/comments that mention a retry by name (e.g. 3643 `WEBSITE_FOUND_RETRY`) stay as prose.

**B3. `src/utils/config.py` — asserts that would fail once keys are gone**
- ~6559 TASK_CONFIG outcome assert: `assert is_registered_state(JOB_STATES, _outcome.strip())`. Required because `analysis_upshot` / `meteorite_upshot` `error_state` is a retry.
- ~4251 `inflight_hide_states` and ~4262 `grade_field` asserts: `all(is_registered_state(REG, s) …)`.
- ~2040 candidate `retry_state` assert: already `is_registered_state` (AST-1805).

**B4. Consumers that look up a runtime state directly — resolve through the base** (each is a one-expression change):
- `src/core/roster.py`
  - `claim_company_batch` (~1419): the single-state gate becomes `if states is None and not is_registered_state(COMPANY_STATES, state): raise ValueError(<same message>)`, and `state_config = COMPANY_STATES.get(registered_base(COMPANY_STATES, state) or state, {})`. Base and retry `batch_criteria` are identical today.
  - ~886: `input_state in ("WEBSITE_FOUND", retry_of("WEBSITE_FOUND"))`.
- `src/data/database.py` `save_company` (~1127): `if not is_registered_state(COMPANY_STATES, state): raise ValueError(<same message>)`. Needed because `roster._parse_dispatch_failure_state` saves `JOBLIST_IDENTIFIED_RETRY` through `_save_company` (~1122). Import `is_registered_state` from config.
- `src/core/candidate.py`
  - `check_context_complete` (~2459): `CANDIDATE_STATES.get(registered_base(CANDIDATE_STATES, current_state) or "")`. Retry ranks equal their base (4 / 6).
  - `_requested_stage_failure_target` (~3611), the carried fix. Resolve first, compare against the resolved base:
    ```python
    primary = registered_base(CANDIDATE_STATES, primary_state) or primary_state
    cfg = CANDIDATE_STATES[primary]
    if current_state == primary:
        return cfg["retry_state"]
    return cfg["error_state"]
    ```
    A retry-only row gives `current == REQUESTED_*_RETRY` ≠ primary, so it returns `error_state`, never `retry` (no retry loop).
- `src/core/consult.py`
  - `_INPUT_STATE_TO_TASK`: delete the 6 retry entries; right after the dict add `_INPUT_STATE_TO_TASK.update({retry_of(k): v for k, v in list(_INPUT_STATE_TO_TASK.items())})`. Every retry maps like its base; this is a legacy map with no `src/` consumer.
  - ~1858: the tuple becomes `("VALID_TITLE", retry_of("VALID_TITLE"), retry_of("NEW"))`.
- **`src/ui/api/api_system.py` `_progress_rank` (~46): `CANDIDATE_STATES.get(registered_base(CANDIDATE_STATES, state) or "")`.** This file was added to the ticket's `## Scope` after the `[scope-gate]` on AST-1806. Without it, a candidate in `REQUESTED_*_RETRY` drops from rank 4 / 6 to −1, and nav gating (`_is_at_or_past`) closes items.
- **Must stay direct** (retry of retry goes to terminal; don't resolve through the base): `consult._consult_batch_fail_dest` (~1526), `roster._prefilter_batch_fail_dest` (~1871), `candidate.age_stale_candidate_states` (~2482, no stale on retry either way), and the `gazer` `cfg["retry_state"]` reads. `dispatcher` / `database` claim/count are verify only.

**B5. Done check:** `rg -n '"[A-Z_]+_RETRY"' src/utils/config.py src/core/consult.py src/core/roster.py` returns nothing. Config imports cleanly, and the gate snapshot is identical.

### Estimate
**5**: one mechanical config pass (B1–B3), 7 one-line consumer edits (B4), and the gate script. Stays within the ≤5 the ticket asked for; no further split.

### Blast radius
- **Admin / UI key lists** (`api_admin` `state_options`, `api_candidate` state list, `tracker._JOB_STATE_LIST` / `roster._COMPANY_STATE_LIST` error text) lose the 18 retry names.
- **`legal_job_successor_states`** stops offering retry targets for manual Jobs moves (accepted in AST-1805's blast radius).
- **In Review** retry buckets, grade/rubric columns, and task routing are unchanged (same strings via `retry_of`).
- **Tests (Betty / AST-1807)** will break wherever they assert retry keys exist in the registries, explicit `prior_states` contents, full `state_options` lists, or `_requested_stage_failure_target` raising for a retry primary. `test_consult` `_INPUT_STATE_TO_TASK` retry asserts stay green.
- **Shared modules:** `config`, `roster`, `candidate`, `consult`, `database` (`save_company` gate only), and `api_system` (`_progress_rank` only).

### What must still hold
- AST-641 / AST-1798 / AST-1800: claim/count lists are byte-identical, and the AST-892 second-strike filter is unchanged.
- AST-642: a primary failure goes to retry holding; a failure while in retry goes to terminal/error. No new routing into retry substates.
- Every legal transition today stays legal: the gate snapshot is identical before and after.
- Candidate `progress_rank` for `REQUESTED_*_RETRY` stays 4 / 6 everywhere it's read.
- Config imports with every module assert passing.

### Board-joan findings (AST-1806)

## Fix-board Joan pass — AST-1806

**Ticket:** AST-1806 (Stage B purge) · parent AST-1804 · publish ref `origin/sub/AST-1804/AST-1806-retry-registry-purge` (@ `9e5bc738+`)  
**Read:** `plan-fix` § Bug: AST-1806 (As-is / To-be / Repro / Root cause / Proposed change B1–B5 / Blast radius / What must still hold); fix-board § Joan pass; active corpus skim (`patt.task.dispatch-retry`, `astral.state.job-prior-states-enforced`, `astral.dispatch.entity-state-bound`, `astral.batch.claim-process-release`, `astral.config.config-source-of-truth`); grep for explicit `_RETRY` / registry-key requirements in `canon/statutes` and `canon/directives/active`.

**The one question:** Does this product purge conflict with or **require** updating any directive in force?

**Answer:** No mandatory canon work for this board pass. The purge **implements** canon that already treats `_RETRY` as an implicit suffix substate, not a separate registry instance. Susan’s AST-1804 rule matches **`patt.task.dispatch-retry`** Arc 1–2 (no separate retry instance; validation via registered base; claim union unchanged).

### Your explicit sub-questions

**Any statute naming explicit `_RETRY` registry states?**  
**No.** Active statutes in `canon/statutes` do not require 18 `*_RETRY` dict keys or `"X_RETRY"` literals in `JOB_STATES` / `COMPANY_STATES` / `CANDIDATE_STATES`. Stale **product/docs** (e.g. archived AST-641 “companion exists in registry”, bible rows) are not in-force directives; AST-1806 does not amend them in this ticket.

**`JOB_STATES.prior_states` wording in `astral.state.job-prior-states-enforced`?**  
The Statement says transitions enforce **`JOB_STATES.prior_states` via tracker**. After AST-1805, enforcement already goes through **`state_prior_states`**; AST-1806 only removes redundant explicit retry keys and retry-named entries from config lists. The **invariant** (illegal jumps raise; priors gate transitions) is unchanged; the gate snapshot in the plan is meant to prove effective priors are identical.  

That wording is **imprecise as config documentation** (priors for retry targets are derived, not only literal list fields), but it was already imprecise after Stage A. It does **not** contradict the purge: the statute describes the enforcement outcome, not “every allowed edge must appear literally in `prior_states`.” No **conflict** and no **blocking** canon edit—same read Joan used for AST-1805 Stage A.

**Optional housekeeping (not fix-board REVISE):** Archie could later tighten `astral.state.job-prior-states-enforced` and/or **`astral.dispatch.entity-state-bound`** (“real state” = registered base or implicit `{base}_RETRY`) for Radia/comparability. That is F3/clarity, not a prerequisite to `make-fix` here.

### Overlap table (Stage B)

| Directive | vs AST-1806 purge |
|-----------|-------------------|
| **`patt.task.dispatch-retry`** | **Conforming.** Arc 1: no separate registry instance; Arc 2: suffixed states need not be registry keys; B1–B2 remove the legacy contradiction. |
| **`astral.dispatch.entity-state-bound`** | **Conforming** with AST-1805 validators + B4 `registered_base` reads; trigger/claim states stay honest. |
| **`astral.batch.claim-process-release`** / AST-641 / AST-1798 / AST-1800 | **Unchanged** claim/count paths per plan. |
| **`astral.config.config-source-of-truth`** | **Conforming.** `retry_of` / helpers stay in `config.py`; mechanical literal → `retry_of("BASE")` is SSOT, not scatter. |
| **`stat.config.derive-dont-restate`** (corpus roster) | **Improved conformity**, not a required statute edit—fewer duplicated `"X_RETRY"` literals. |
| **AST-642 routing** | B4 `_requested_stage_failure_target` fix aligns retry-only rows with terminal-on-retry; no new retry loop—pattern Arc 4, not new precedent. |

**ESCALATE:** Not warranted. Susan’s binding rule, gate script, and accepted blast radius (UI key lists, `legal_job_successor_states`) are bounded product choices, not ambiguous statute intent.

**F3 (`validate-plan` fix mode):** Not triggered from this board pass.

---

**Machine-readable upshot (Chuckles posts `--as joan`):**

```
[board-joan]  CANON: OK
```

**Stdout:**

```text
[board-joan]  CANON: OK
AST-1806 board-joan done — CANON: OK.
```

context_tokens≈32000

### Review-fix findings (AST-1806)

[code-rubric]
**Ticket:** AST-1806  
**Publish ref:** cfcf3c273512386e6b2fcd9c2e059b158229b4fb  
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3  
**Overall:** CLEAN

## Fix-specific checks

**`[bug-repro]`:** not applicable — `[board-betty] TESTS: REVISE` routed to sibling **AST-1808**; qa-fix did not run; no `[bug-repro]` on tip (spawn prompt confirmed). Product-only + gap-sibling split matches AST-1805 / AST-1801 pattern.

**`## What must still hold`:** OK  
- **AST-641 / AST-1798 / AST-1800:** `dispatch_claim_states` has no hunks in the ftr…sub diff; `dispatcher.py` unchanged; multi-state claim wrappers on ftr already AST-1800/1805 shape — not regressed by Stage B.  
- **AST-892:** No diff hunks on `fetch_website_prefilter_second_strike_filter` / gazer claim filter paths in this range.  
- **AST-642 routing:** `_consult_batch_fail_dest`, `_prefilter_batch_fail_dest`, and gazer direct `retry_state` reads unchanged in diff; `_requested_stage_failure_target` now resolves primary via `registered_base` so retry-only rows land on `error_state` (plan carried fix). Fail-dest paths remain direct full-string lookups as required by plan B4.  
- **Prior / transition legality:** Plan gate (identical `state_prior_states` snapshots pre/post purge) asserted at make-fix; diff implements B1–B2 deletion + derived priors only — no contradicting product change in diff.  
- **Candidate progress_rank:** `check_context_complete` and `api_system._progress_rank` use `registered_base` — matches plan B4 and amended scope.  
- **Config load:** Asserts updated to `is_registered_state` where purge would break raw-key checks (inflight_hide, grade_field, TASK_CONFIG outcome).

## Canon scores

(no frozen canon list on Linear Description — fix-lane pattern; zero ids locked at Plan Approved; scored set empty)

## Column diff vs plan stage

no plan-stage scores attached (F3 validate-plan fix mode not triggered; Joan fix-board `[board-joan] CANON: OK` only)

## Frame diff

(none)

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on bug ticket. Joan fix-board cites `patt.task.dispatch-retry`, entity-state-bound, config-source-of-truth, job-prior-states-enforced, claim-process-release informally — same process pattern as AST-1805 / AST-1801.  
  **Recommendation:** No in-flight Canon Scope amendment required unless Archie wants comparability on every fix-lane bug; purge aligns with Susan’s implicit-substate rule and board narrative.

- **Location:** `[board-betty] TESTS: REVISE` / sibling **AST-1808**  
  **Finding:** Betty-flagged `test_config.py` raw-registry / explicit-prior asserts break on this tip by design (14 expected failures per Ada test-fix vs ftr `65e3ca6f`); B4 consumer fixes and gate snapshot have no tests yet. No `tests/` changes on this tip — correct ownership split.  
  **Recommendation:** Chuckles: **Docs-Acceptance** on AST-1806 (mirror AST-1805). Do not block product UT on AST-1808; land AST-1808 before expecting purge + consumer contracts green on ftr.

### advisory

- **Location:** `src/core/consult.py` `_consult_batch_fail_dest` (unchanged; post-purge behavior)  
  **Finding:** Retry-holding job states no longer have registry dict entries; routing for `*_RETRY` failures leans on `JOB_STATES.get(st)` miss plus `st == error_state` terminal branch (e.g. analysis_upshot). Plan explicitly kept fail-dest direct; strings unchanged via `retry_of`.  
  **Recommendation:** AST-1808 repro tests should pin this path; not fix-now on product tip.

- **Location:** Plan fidelity — scope gate  
  **Finding:** `[scope-gate]` caught missing `api_system.py`; Chuckles amended scope; tip includes `_progress_rank` fix — regression closed.  
  **Recommendation:** None for resolve-child.

## Notes (informal board overlap — not scored)

| Directive | vs Stage B diff |
|-----------|-----------------|
| `patt.task.dispatch-retry` | Registries bases-only; retry names via `retry_of`; claim helper untouched. |
| `astral.config.config-source-of-truth` | Mechanical literal → `retry_of` in `config.py`; helpers from AST-1805 reused. |
| `astral.state.job-prior-states-enforced` | Enforcement still via `state_prior_states` (on ftr from AST-1805); explicit retry priors stripped. |
| `astral.dispatch.entity-state-bound` | Runtime states validated/resolved via `registered_base` / `is_registered_state` in B4 sites. |
| `astral.batch.claim-process-release` | Claim SQL/dispatcher unchanged; `save_company` gate widened for implicit retry saves only. |
| `astral.standards.in-scope-only` | Diff matches plan B1–B5 file set (+ scope-amended `api_system.py`); no `tests/` edits. |

## What's solid

- **B1/B2 delivered:** Remote tip shows **0** explicit `*_RETRY` registry dict keys; B5-style `rg '"…_RETRY"'` on `config.py` / `consult.py` / `roster.py` clean (prose/docstrings only).  
- **B3 asserts:** TASK_CONFIG outcome, inflight_hide, grade_field use `is_registered_state`.  
- **B4 consumers:** roster `claim_company_batch` + WEBSITE_FOUND branch, `database.save_company`, candidate rank + `_requested_stage_failure_target`, consult map derive + qualify filter tuple — match plan snippets.  
- **Boundaries:** `gazer`, `dispatcher`, `api_admin`, `tracker` product files untouched in diff; fail-dest functions not “resolved through base.”  
- **Stacking:** Diff base `origin/ftr/AST-1804-fetch-avail-retry` includes merged AST-1805 validators — Stage B builds on Stage A correctly.  
- **Estimate 5** fits footprint (~300 LOC mechanical config + seven consumer touchpoints + plan doc).  
- Parent **AST-1804** — **normal** fix-lane shape.

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1804; diff base `origin/ftr/AST-1804-fetch-avail-retry`) | → **Review Posted** → append artifact + `docs(AST-1806): Radia review — clean` on publish ref → post slim upshot `--as radia` → §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |
| — | Sibling **AST-1808** | Parallel: close Betty `TESTS: REVISE` bar (test/bible only). **merge-child** can roll AST-1806 onto ftr after UT. |

**Chuckles note:** `[board-betty] TESTS: REVISE` owned by **AST-1808**. Product tip docs-acceptance — no merge-tests on AST-1806. Ada’s 14 `test_config` breaks + 4 baseline fixes are expected purge fallout; Chuckles re-verifies parity independently — not re-litigated here beyond ownership split.

context_tokens≈38000

```
[code-rubric] PROCEED (Commit: cfcf3c273512386e6b2fcd9c2e059b158229b4fb) Registry purge clean
```

## Bug: AST-1807 — gap: tests + bible for implicit `_RETRY` helpers and validator acceptance (AST-1805)

Parent AST-1804. Test-gap sibling from fix-board `[board-betty] TESTS: REVISE` on AST-1805. **Betty lands everything here (qa-fix); engineers do not edit `tests/` or `docs/test-bible/**`.** No product `src/` change.

### As-is
AST-1805 (`d088edfd`, merged on `ftr/AST-1804-fetch-avail-retry`) added five config helpers (`retry_of`, `retry_base`, `registered_base`, `is_registered_state`, `state_prior_states`) and a `{base}_RETRY` acceptance branch in eight validators:
- `tracker.transition_job_state`
- `roster.transition_company_state`
- `candidate.transition_candidate_state` / `_candidate_prior_states`
- `config.is_valid_job_batch_claim_state` / `is_valid_candidate_batch_claim_state`
- `config._dispatch_sort_by_for` (job and company)
- the two `api_admin._dispatch_task_key_trigger_error` sites (mailbox candidate branch and general branch)

None of these branches has a component test or a bible row.

### To-be
Every helper and every acceptance branch has a component test. For each validator, a registered `{base}_RETRY` is accepted, while an unregistered base with the suffix (`NOPE_RETRY`) is still rejected. There is one repro test that is red on the pre-fix tree (`9f6536ce`) and green on `ftr`. The five bible pages named in scope each get an AST-1807 section.

### Repro
**Correction to the ticket and to § Bug: AST-1805 Repro:** the repro transition is **`PASSED_GET → PASSED_GET_RETRY`**, not `PASSED_DO → PASSED_GET_RETRY`. Under AST-1805's derived rule, `state_prior_states(JOB_STATES, "PASSED_GET_RETRY") == ["PASSED_GET", "PASSED_GET_RETRY"]`, so `PASSED_DO → PASSED_GET_RETRY` correctly still raises `Invalid transition` after the fix. That becomes the negative companion test.

Probed on both trees (this pass, `~/astral-tests/.venv/bin/python`):

| Call | Pre-fix `9f6536ce` | `ftr` (AST-1805) |
|---|---|---|
| `transition_job_state` from `PASSED_GET` → `PASSED_GET_RETRY` | `ValueError: Value 'PASSED_GET_RETRY' not in allowed list` | saves `state="PASSED_GET_RETRY"` |
| from `PASSED_DO` → `PASSED_GET_RETRY` | `ValueError … not in allowed list` | `ValueError: Invalid transition: PASSED_DO -> PASSED_GET_RETRY` |

### Root cause
The fix-board flagged that AST-1805's new helpers and branches landed without coverage. There is no product defect here.

### Proposed change
All expected values below were probed on `ftr` tip `65e3ca6f`. Every "pre-fix" value was probed with the five AST-1805 product files checked out at `9f6536ce`. Use the existing fixture idioms in each file (`monkeypatch` on `database.get_job` / `save_job`, `roster_mod.get_company` / `update_company`, `candidate_mod.database.get_candidate` / `save_candidate`).

**T1. `tests/component/utils/test_config.py` — new `class TestAst1807ImplicitRetryHelpers`**
- `retry_of("PASSED_GET") == "PASSED_GET_RETRY"`.
- `retry_base`: `"PASSED_GET_RETRY"` → `"PASSED_GET"`; `" PASSED_GET_RETRY "` → `"PASSED_GET"` (strips); `"PASSED_GET"` → `None`; `"_RETRY"` → `None`; `None` → `None`.
- `registered_base(JOB_STATES, …)`: `"PASSED_GET"` → `"PASSED_GET"`; `"PASSED_GET_RETRY"` → `"PASSED_GET"`; `"NOPE_RETRY"` → `None`. `is_registered_state` mirrors this (True, True, False).
- `state_prior_states`, the derived-prior rule:
  - `(JOB_STATES, "NEW_RETRY") == ["NEW", "NEW_RETRY", "VALID_TITLE"]` (cross-base feeder: `VALID_TITLE.retry_state`).
  - `(COMPANY_STATES, "WEBSITE_FOUND_RETRY") == ["WEBSITE_FOUND", "WEBSITE_FOUND_RETRY", "HOMEPAGE_READY"]` (cross-base feeder: `HOMEPAGE_READY.retry_state`).
  - `(JOB_STATES, "PASSED_GET_RETRY") == ["PASSED_GET", "PASSED_GET_RETRY"]`.
  - Self-drain: `"JD_READY_RETRY" in state_prior_states(JOB_STATES, "JD_READY")`, and `"REQUESTED_RESUME_RETRY" in state_prior_states(CANDIDATE_STATES, "REQUESTED_RESUME")`.
  - Unrestricted stays unrestricted: `state_prior_states(JOB_STATES, "NEW") is None`.
  - `pytest.raises(KeyError, match="unregistered state")` for both `"NOPE"` and `"NOPE_RETRY"`.
- **Do not** touch `TestAst… ` asserts on raw `JOB_STATES[…]["prior_states"]` / explicit `*_RETRY` keys (~3080–3110). Those flip with AST-1806.

**T2. `tests/component/utils/test_config.py` — new `class TestAst1807ImplicitRetryConfigValidators`**
- `is_valid_job_batch_claim_state("PASSED_GET_RETRY") is True`; `("NOPE_RETRY") is False`. Pre-fix: False / False.
- `is_valid_candidate_batch_claim_state("RESUME_READY_RETRY") is True`; `("NOPE_RETRY") is False`. Pre-fix: False / False.
- `_dispatch_sort_by_for("job", "PASSED_JOBLIST_RETRY") == "updated_at"`. Pre-fix: `KeyError "unknown job trigger_state"`.
- `_dispatch_sort_by_for("job", "NOPE_RETRY")` raises `KeyError`, match `"unknown job trigger_state"`.
- `_dispatch_sort_by_for("company", "TO_WATCH_RETRY") == "updated_at"`, resolved from the base's `batch_criteria`. Pre-fix: `KeyError "missing batch_criteria"`.

**T3. `tests/component/core/test_tracker.py` — extend `TestTransitionJobState` (or new `TestAst1807ImplicitRetryJobTransition`)**
- **Repro (`[bug-repro]`):** `get_job` returns `{"state": "PASSED_GET", "state_history": []}`. `transition_job_state(["job-1"], "PASSED_GET_RETRY")` saves `state="PASSED_GET_RETRY"`, and history's last `to_state == "PASSED_GET_RETRY"`. Red on `9f6536ce` (`not in allowed list`).
- Negative: from `PASSED_DO` → `PASSED_GET_RETRY` raises `ValueError`, match `"Invalid transition"`.
- Unregistered: `transition_job_state(["job-1"], "NOPE_RETRY")` raises `ValueError`, match `"not in allowed list"` (message text preserved).

**T4. `tests/component/core/test_roster.py` — extend `TestTransitionCompanyState`**
- `transition_company_state("acme", "PREFILTER_FAILED_RETRY")` calls `update_company` with `state="PREFILTER_FAILED_RETRY"`. This is an unregistered retry of a registered base. Pre-fix: `ValueError`.
- `"NOPE_RETRY"` raises `ValueError`, match `"not in allowed list"`.

**T5. `tests/component/core/test_candidate.py` — extend `TestTransitionCandidateState`**
- From `RESUME_READY` → `RESUME_READY_RETRY` saves `state="RESUME_READY_RETRY"`. Pre-fix: `ValueError "Unknown candidate state"`.
- From `NEW_CANDIDATE` → `RESUME_READY_RETRY` raises `IllegalCandidateTransition` (the derived prior gate still enforces).
- `→ "NOPE_RETRY"` raises `ValueError`, match `"Unknown candidate state"`.

**T6. `tests/component/ui/api/test_api_admin.py` — extend the class holding `test_dispatch_task_key_trigger_error_helper` (~947)**
- General branch: `_dispatch_task_key_trigger_error("fetch_jd", "PASSED_JOBLIST_RETRY") is None`. Pre-fix returns `"task_key 'fetch_jd' (job) is not valid for trigger_state 'PASSED_JOBLIST_RETRY'"`. `("fetch_jd", "NOPE_RETRY")` returns that same error shape for `'NOPE_RETRY'`.
- Mailbox candidate branch: `_dispatch_task_key_trigger_error("stage_email_meteorite", "RESUME_READY_RETRY") is None`. Pre-fix returns an error. `("stage_email_meteorite", "NOPE_RETRY")` returns `"task_key 'stage_email_meteorite' (candidate) is not valid for trigger_state 'NOPE_RETRY'"`.

**T7. Bible — add an `### AST-1807 · AST-1805 (implicit _RETRY substate)` section** (the format of recent entries, e.g. `config.md` § AST-1788) to each page, with a table naming source → test class/nodes, `**Broken / obsolete:** none`, `**Integration:** none — do not invent`, and the narrowed `run_component_tests.sh` command:
- `docs/test-bible/utils/config.md`: T1, T2
- `docs/test-bible/core/tracker.md`: T3 (mark the repro node `[bug-repro]`)
- `docs/test-bible/core/roster.md`: T4
- `docs/test-bible/core/candidate.md`: T5
- `docs/test-bible/ui/api/api_admin.md`: T6

**Red→green check for Betty:** check out the five product files at `9f6536ce`:
```bash
git checkout 9f6536ce -- src/utils/config.py src/core/tracker.py src/core/roster.py src/core/candidate.py src/ui/api/api_admin.py
```
The T3 repro and every "Pre-fix" row above must fail (T1 fails on import-level `AttributeError`, since the helpers don't exist yet). Restore with `git checkout HEAD -- <same files>`, and everything must pass. Use `~/astral-tests/.venv/bin/python -m pytest` (that venv has `asyncpg`).

### Estimate
**3**: roughly 30 assertions across 4 test files plus 5 bible sections, all read-only against the existing product.

### Blast radius
- Test-tree and bible only.
- Nothing asserts on the purged state of the registries: these tests use unregistered retries (`PASSED_GET_RETRY`, `PREFILTER_FAILED_RETRY`, `RESUME_READY_RETRY`, `TO_WATCH_RETRY`, `PASSED_JOBLIST_RETRY`) and helper outputs that are identical before and after AST-1806. The exception is `NEW_RETRY` / `WEBSITE_FOUND_RETRY` priors; AST-1806's gate proves those are unchanged. So the suite stays green through the purge.
- The 123 pre-existing failures in these files (identical pre/post AST-1805; see the AST-1805 Tests Passed comment) are out of scope here.

### What must still hold
- `NOPE_RETRY` (unregistered base) is rejected by every validator; the fix does not validate the suffix alone.
- Derived priors still gate: `PASSED_DO → PASSED_GET_RETRY` and `NEW_CANDIDATE → RESUME_READY_RETRY` are rejected.
- The AST-1806-flipping asserts in `test_config.py` (~3080–3110) are untouched.
- Fail-destination must-not-resolve coverage already in `test_consult` / `test_roster` is untouched.

### Board-joan findings (AST-1807)

## Fix-board Joan pass — AST-1807

**Ticket:** AST-1807 (gap) · parent AST-1804 · publish ref `origin/sub/AST-1804/AST-1807-implicit-retry-tests`  
**Read:** `plan-fix` § Bug: AST-1807 (As-is / To-be / Repro / Root cause / Proposed change T1–T7 / Blast radius / What must still hold); fix-board § Joan pass; roster skim (`patt.task.dispatch-retry`, `astral.state.job-prior-states-enforced`, `astral.batch.claim-process-release`, `astral.dispatch.entity-state-bound`, `astral.config.config-source-of-truth`, `astral.standards.in-scope-only`).

**Scope of this pass:** Tests + `docs/test-bible/**` only. **No product `src/` edits.** AST-1805 behavior is assumed on `ftr`; this ticket locks it in component tests and bible rows.

**The one question:** Does the proposed change conflict with or require updating any directive in force?

**Answer:** No. This is documentation and regression coverage for product behavior that already matches active canon (especially **`patt.task.dispatch-retry`**: suffix substate, claim union unchanged elsewhere, validation via registered base). The plan explicitly avoids registry-purge assertions that AST-1806 will flip (~3080–3110 in `test_config.py`) and avoids inventing integration scenarios.

| Area | Assessment |
|------|------------|
| **Proposed change (T1–T7)** | Asserts helpers and validator branches Betty listed; negative cases preserve “suffix alone is not enough” (`NOPE_RETRY`) and derived-prior gates (`PASSED_DO → PASSED_GET_RETRY`). That matches Susan’s AST-1804 binding rule and the pattern’s Arc 1–2, without restating new product policy. |
| **Blast radius** | Test-tree + bible only; no statute/pattern text touched. |
| **Canon gap vs product gap** | Any tension between literal `JOB_STATES.prior_states` wording in **`astral.state.job-prior-states-enforced`** and derived `state_prior_states` was introduced by AST-1805 product, not by this test gap. Locking behavior in tests does not *require* a canon amendment to proceed (optional clarity edit remains F3 material on the product ticket if Archie wants it, not fix-board on AST-1807). |
| **ESCALATE bar** | No new precedent, no ambiguous architectural call — repro documents pre-fix vs `ftr` only. |

**F3 (`validate-plan` fix mode):** Not triggered from this board pass.

**Precedent:** Same shape as AST-1802 in this feature doc — test/bible-only gap, **CANON: OK**.

---

**Machine-readable upshot (Chuckles posts `--as joan`):**

```
[board-joan]  CANON: OK
```

**Stdout:**

```text
[board-joan]  CANON: OK
AST-1807 board-joan done — CANON: OK.
```

context_tokens≈24000

### Review-fix findings (AST-1807)

[code-rubric]
**Ticket:** AST-1807  
**Publish ref:** e398249244438d8913319b09bd33042125d794be  
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3  
**Overall:** CLEAN

## Fix-specific checks

**`[bug-repro]`:** OK  
- **Node:** `tests/component/core/test_tracker.py::TestTransitionJobState::test_ast1807_bug_repro_base_to_implicit_retry` — first-line comment tags `[bug-repro] AST-1807 / AST-1805`.  
- **Body pins To-be:** job in `PASSED_GET`, target `PASSED_GET_RETRY`; asserts `save_job` receives `state="PASSED_GET_RETRY"` and history `to_state == "PASSED_GET_RETRY"`. That is the corrected plan repro (not the obsolete `PASSED_DO → PASSED_GET_RETRY` path, which correctly stays illegal and is covered by `test_ast1807_derived_priors_still_gate_retry`).  
- **Pre-fix contract:** would fail on pre–AST-1805 product with `ValueError` / `not in allowed list` (full-string registry validation) — matches plan § Repro and Betty’s `[bug-repro]` handoff; not tautological (exercises real `transition_job_state`, not helper mirrors).  
- **Companion negatives in same class:** `NOPE_RETRY` → `not in allowed list`; derived-prior gate `PASSED_DO → PASSED_GET_RETRY` → `Invalid transition` — satisfy plan “suffix alone not enough” and **What must still hold**.

**`## What must still hold`:** OK  
- **`NOPE_RETRY` rejected:** asserted in T1 helpers, T2 batch/sort validators, T3–T6 validator tests.  
- **Derived priors still gate:** tracker + candidate negative cases in diff.  
- **AST-1806-flipping `test_config.py` ~3080–3110:** no hunks in that region (append-only at ~6942).  
- **Fail-dest / consult coverage:** no edits to `test_consult` fail-dest tests in diff.  
- **No `src/`:** zero lines under `src/` in ftr…sub diff.

## Canon scores

(no frozen canon list on Linear Description — gap-ticket pattern; zero ids locked at Plan Approved; scored set empty)

## Column diff vs plan stage

no plan-stage scores attached (F3 not triggered; Joan fix-board `[board-joan] CANON: OK` only)

## Frame diff

(none)

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on gap ticket (same pattern as AST-1802 / AST-1808 / AST-1805 product tips). Joan board OK only.  
  **Recommendation:** No Canon Scope amendment required; tests lock AST-1805 behavior that already matches `patt.task.dispatch-retry` Arc 1–2.

- **Location:** Plan-fix § Proposed change header vs landing path  
  **Finding:** Plan states engineers do not edit `tests/` (Betty qa-fix ownership); Betty landed `[bug-repro]` + manifest @ `6d47880e`, then `merge-tests` / Ada test-fix @ `e3982492` — normal fix-lane gap shape (same family as AST-1802).  
  **Recommendation:** None for resolve-child.

### advisory

- **Location:** Betty `[bug-repro]` thread vs Ada test-fix  
  **Finding:** Betty cited “35/35 pass”; Ada manifest lists **18/18** nodes for `### AST-1807` — count mismatch only; both agree repro red→green and manifest green on tip with AST-1806 on branch.  
  **Recommendation:** Optional thread hygiene; not fix-now.

- **Location:** Tip commit message  
  **Finding:** HEAD `e3982492` is `sync(ftr)` (AST-1806 merged on branch); test/bible payload lives in `d72c8c7b` + `merge-tests` — review substance is the ftr…sub diff, not the sync commit alone.  
  **Recommendation:** Chuckles doc append uses tip SHA `e3982492` as publish ref under review.

## Notes (informal board overlap — not scored)

| Directive | vs test/bible diff |
|-----------|-------------------|
| `patt.task.dispatch-retry` | Tests assert implicit `{base}_RETRY` via base + derived priors; no claim-shape edits. |
| `astral.state.job-prior-states-enforced` | Negative transitions prove priors still gate; does not rewrite raw `prior_states` tables (AST-1808). |
| `astral.dispatch.entity-state-bound` | Admin trigger tests accept registered-base retries. |
| `astral.config.config-source-of-truth` | Helper/validator tests target `config.py` API only. |
| `astral.standards.in-scope-only` | Tests + bible + plan doc only; no product drift. |

## What's solid

- **T1–T2:** `TestAst1807ImplicitRetryHelpers` + `TestAst1807ImplicitRetryConfigValidators` — values match plan (feeders, self-drain, `NEW` unrestricted, KeyError on unregistered, batch/sort validators).  
- **T3–T6:** Tracker repro + negatives; roster `PREFILTER_FAILED_RETRY`; candidate `RESUME_READY_RETRY` + prior gate; admin both trigger branches — all present in diff.  
- **T7:** Five bible pages include `### AST-1807 · AST-1805` with tables, **Broken / obsolete:** none, narrowed `run_component_tests.sh` commands; tracker marks repro node explicitly.  
- **AST-1805 board bar:** Closes Betty `TESTS: REVISE` on **AST-1805** (not AST-1808 purge rewrites). Probe retries documented as never registry keys — compatible with AST-1806 purge on merged ftr.  
- **Estimate 3** fits (~385 LOC tests/bible/plan).  
- **Parent AST-1804** — normal fix-lane shape; diff base includes AST-1805 (+ ftr now carries AST-1806 per sync).

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1804; diff base `origin/ftr/AST-1804-fetch-avail-retry`) | → **Review Posted** → append artifact + `docs(AST-1807): Radia review — clean` on publish ref → post slim upshot `--as radia` → §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |
| — | **AST-1805** | Docs-Acceptance on product can close once this lands (Betty REVISE for helpers/validators satisfied here). |
| — | **AST-1808** | Separate purge test gap — do not conflate. |

**Chuckles note:** `[bug-repro]` present and substantive. Ada’s 18/18 manifest green with AST-1806 merged on tip — aligns with spawn prompt; baseline 195-debt parity out of scope.

context_tokens≈42000

```
[code-rubric] PROCEED (Commit: e398249244438d8913319b09bd33042125d794be) Implicit retry tests OK
```

## Bug: AST-1808 — gap: tests for explicit `_RETRY` registry purge (AST-1806)

Parent AST-1804. Test-gap sibling of AST-1806, from fix-board `[board-betty] TESTS: REVISE`. **Test tree and bible only; Betty lands it (qa-fix).** No `src/` change: product is AST-1806 (`origin/sub/AST-1804/AST-1806-retry-registry-purge` @ `cfcf3c27`, Tests Passed; not yet on ftr). AST-1807 owns the AST-1805 helper/validator-acceptance tests; don't duplicate them.

### As-is
- On the AST-1806 tip, 14 `tests/component/utils/test_config.py` cases fail, and none of them is a product failure. Each one reads a raw registry: a `*_RETRY` key lookup, `"X_RETRY" in REGISTRY`, or an exact `prior_states` list that still names a `*_RETRY` (AST-1806 test-fix, base ftr `65e3ca6f` vs tip).
- None of the AST-1806 resolve-via-base sites has a test: `_requested_stage_failure_target` on a retry-only row, `roster.get_new_company_batch` single-state retry claim, `check_context_complete` / `_progress_rank` retry rank, `database.save_company` retry save.
- Nothing pins "zero explicit `_RETRY` keys" or the gate-snapshot identity.

### To-be
- All 14 asserts express the same intent through the implicit-substate surface: `is_registered_state` / `registered_base` for membership, `state_prior_states` for effective priors, and key absence for the purged entries. Raw `prior_states` equality asserts keep checking the **declared** base-only list.
- A repro test fails on the pre-purge tree and passes on the AST-1806 tip.
- New cases cover each B4 consumer and pin the gate snapshot.

### Repro
`[bug-repro]` node (new): `tests/component/utils/test_config.py::TestAst1808RetryRegistryPurge::test_no_explicit_retry_keys_in_entity_registries`
```python
for name in ("JOB_STATES", "COMPANY_STATES", "CANDIDATE_STATES"):
    reg = getattr(cfg, name)
    assert not [k for k in reg if k.endswith(cfg.RETRY_SUFFIX)], name
    assert not [(k, p) for k, v in reg.items() for p in (v.get("prior_states") or []) if p.endswith(cfg.RETRY_SUFFIX)], name
```
The first assert is red on ftr `65e3ca6f` (18 keys) and green on AST-1806 `cfcf3c27` (0). Verify red→green against **AST-1806's product files**; ftr alone stays red until merge-child lands AST-1806.

### Root cause
The AST-1806 purge deletes the 18 keys and strips the retry priors by design (Susan's AST-1804 rule). These tests pinned the old explicit-key data shape rather than the behavior.

### Proposed change
All values below were checked against the AST-1806 tip (`state_prior_states`, `is_registered_state`, `dispatch_claim_states` probes).

**T1. Rewrite the 14 breaks in `tests/component/utils/test_config.py`.** Line numbers are on ftr `65e3ca6f`. Keep every non-retry assert in each case as-is.

The 7 listed in the ticket Scope:
- **1439 AST-874 `test_job_states_and_like_priors`:**
  - `PASSED_LIKE` / `FAILED_LIKE` / `FAILED_TECHNICAL_LIKE`: raw `prior_states == ["CULTURE_READY"]`.
  - Add `"CULTURE_READY_RETRY" in state_prior_states(JOB_STATES, t)` for each.
- **2267 AST-898 `test_registry_retry_pointers_and_drain`:**
  - Keep the `NEW` / `VALID_TITLE` `retry_state == "NEW_RETRY"` lines.
  - Replace the `JOB_STATES["NEW_RETRY"]` / `["VALID_TITLE_RETRY"]` reads with `"NEW_RETRY" not in JOB_STATES and "VALID_TITLE_RETRY" not in JOB_STATES`.
  - `set(state_prior_states(JOB_STATES, "NEW_RETRY")) == {"NEW", "NEW_RETRY", "VALID_TITLE"}`.
  - `"NEW_RETRY"` ∈ derived priors of `PASSED_JOBLIST` and `FAILED_JOBLIST`.
- **2308 AST-1339 `test_registry_retry_pointer_no_nested`:**
  - Keep `METEORITE_NEW.retry_state == "METEORITE_NEW_RETRY"`.
  - `"METEORITE_NEW_RETRY" not in JOB_STATES`.
  - `set(state_prior_states(JOB_STATES, "METEORITE_NEW_RETRY")) == {"METEORITE_NEW", "METEORITE_NEW_RETRY"}`.
- **2605 AST-1253 `test_requested_artifacts_priors_include_regenerate_states`:**
  - Read `priors = state_prior_states(CANDIDATE_STATES, "REQUESTED_ARTIFACTS")`; the loop is unchanged.
  - Keep `"REQUESTED_ARTIFACTS_ERROR" not in priors`.
- **3061 AST-1053 `test_job_states_priors`:**
  - Each exact raw list drops its `*_RETRY` element, e.g. `METEORITE_QUALIFIED == ["METEORITE_NEW", "METEORITE_FAILED_JD", "METEORITE_ERROR_EVALUATE_JD"]`, `METEORITE_FAILED_JD == ["METEORITE_QUALIFIED"]`.
  - For each, add the dropped retry ∈ `state_prior_states(JOB_STATES, t)`.
  - `METEORITE_PASSED_LIKE_RETRY`: key absent; derived `{"METEORITE_PASSED_LIKE", "METEORITE_PASSED_LIKE_RETRY"}`.
  - `PASSED_LIKE`: as in the 1439 case.
- **3169 AST-1053 `test_non_meteorite_gdl_and_recommended_untouched`:**
  - The `PASSED_SCORE_GATED_STATES` loop is unchanged (it is membership in a list, not in a registry).
  - `"PASSED_LIKE_RETRY"` ∈ `state_prior_states(JOB_STATES, "RECOMMENDED")`.
  - `PASSED_JD` raw `== ["JD_READY", "FAILED_DO", "FAILED_TECHNICAL_DO"]`, plus `"JD_READY_RETRY"` ∈ derived.
- **3448 AST-1195 `test_bot_blocked_registry_and_skipped_ui`:** `BOT_BLOCKED` raw `== ["PASSED_JOBLIST", "METEORITE_NEW"]`, plus `"METEORITE_NEW_RETRY"` ∈ derived.

The 7 the ticket Scope missed (same file, same kind of rewrite; flagged on AST-1808 22:32):
- **1306 AST-721 `test_parse_states_and_transitions`:** `is_registered_state(COMPANY_STATES, "JOBLIST_IDENTIFIED_RETRY")` and `"JOBLIST_IDENTIFIED_RETRY" not in COMPANY_STATES`. The transition-pair asserts are unchanged (still true via `retry_of`).
- **1340 AST-720 `test_selection_states_and_transitions`:** same pattern for `PREFILTER_PASSED_RETRY`; transitions unchanged.
- **1524 AST-507 `test_company_states_and_transitions`:** same pattern for `WEBSITE_FOUND_RETRY`. `ROSTER_CONFIG["prefilter"]["retry_state"] == "WEBSITE_FOUND_RETRY"` is unchanged.
- **2643 AST-1375 `test_inflight_hide_states_exact_membership`:** the exact-list assert is unchanged. `all(s in CANDIDATE_STATES …)` becomes `all(is_registered_state(CANDIDATE_STATES, s) …)`.
- **3475 AST-1197 `test_task_config_email_and_bot_knobs`:** `"METEORITE_NEW_RETRY"` ∈ `state_prior_states(JOB_STATES, "BOT_BLOCKED")`.
- **3661 AST-1055 `test_recommended_priors_include_meteorite_like_states`:** read `priors = state_prior_states(JOB_STATES, "RECOMMENDED")`; all four membership asserts are unchanged.
- **4763 AST-1155 `test_retry_state_and_dispatch_claim_companions`:**
  - `holding in JOB_STATES` becomes `holding not in JOB_STATES and registered_base(JOB_STATES, holding) == primary`.
  - Drop `"retry_state" not in JOB_STATES[holding]`, which is subsumed by key absence.
  - Both `dispatch_claim_states` asserts are unchanged (verified: `[primary, holding]` / `[holding]`).

**T2. New class `TestAst1808RetryRegistryPurge` in `tests/component/utils/test_config.py`:**
- The `[bug-repro]` test (**Repro** above).
- `test_prior_snapshot_pinned`: fixture `tests/fixtures/ast1806_prior_snapshot.json`, generated once by the AST-1806 gate script on ftr `65e3ca6f` (the pre-purge tree), stored as `{registry: {target: sorted list | null}}` over bases plus `retry_of(bases)` from the pre-purge registries. The test rebuilds the same map from the current config, with bases = the current keys, and asserts `set()` equality per target (None ↔ null). **Explicit decision for Betty:** this is a checked-in fixture, because the pre-purge tree can't be recomputed after the purge.

**T3. New consumer coverage (component, monkeypatched, no DB writes beyond the existing fixtures):**
- **`tests/component/core/test_candidate.py`:**
  - `_requested_stage_failure_target(retry_of(b), retry_of(b)) == CANDIDATE_STATES[b]["error_state"]` for `b in ("REQUESTED_RESUME", "REQUESTED_ARTIFACTS")`, with no KeyError.
  - The base-on-base case still returns `retry_state`.
  - `check_context_complete` with `database.get_candidate` patched to state `REQUESTED_ARTIFACTS_RETRY` returns the same result as the base.
- **`tests/component/core/test_roster.py` `TestBatchApi`:**
  - `get_new_company_batch("WEBSITE_FOUND_RETRY", context="roster")`, with `claim_company_batch` / `get_company_batch` patched, raises no `ValueError`, and `claim.call_args` `sort_by` equals the base's `batch_criteria` `sort_by`.
  - `"NOPE_RETRY"` still raises.
- **`tests/component/data/database/test_companies.py`:** `save_company(..., state="JOBLIST_IDENTIFIED_RETRY")` succeeds on the existing test DB fixture, and `state="NOPE_RETRY"` raises `ValueError` (`Invalid state`).
- **`tests/component/ui/api/test_api_system.py`:** `_progress_rank(retry_of(b)) == _progress_rank(b)` for both requested bases (4 / 6), and `_progress_rank("NOPE_RETRY") == -1`.

**T4. Bible:** add a `### AST-1808` block (same shape as `### AST-1807`) to `docs/test-bible/utils/config.md`, `core/roster.md`, `core/candidate.md`, `data/database.md`, `ui/api/api_system.md`. List the 14 rewritten cases under **Broken / obsolete → revised**.

### Blast radius
- Test tree only: `test_config.py` (14 rewrites plus the new class), `test_candidate.py`, `test_roster.py`, `test_companies.py`, `test_api_system.py`, one new fixture JSON, and 5 bible pages.
- These tests are green only once AST-1806 is on ftr. Run qa-fix against AST-1806 product files, same as AST-1807's red-on-dev / green-on-ftr check.
- The AST-1807 cases (`TestAst1807*`, probe retries never registry keys) are untouched.

### What must still hold
- No `src/` edits.
- Every rewritten case keeps its original non-retry asserts; only the retry-key/prior reads change.
- Derived-prior asserts use `in` / `set` membership, never exact derived-list equality. The derived set deliberately includes retry-of-priors and self-drain (AST-1805 rule), which AST-1807 owns.
- AST-641 / AST-1798 / AST-1800 claim asserts (`dispatch_claim_states`) are unchanged.

### Board-joan findings (AST-1808)

## Fix-board Joan pass — AST-1808

**Ticket:** AST-1808 (test gap) · parent AST-1804 · publish ref `origin/sub/AST-1804/AST-1808-purge-retry-tests`  
**Read:** `plan-fix` § Bug: AST-1808 (As-is / To-be / Repro / Root cause / Proposed change T1–T4 / Blast radius / What must still hold); fix-board § Joan pass; roster skim (`patt.task.dispatch-retry`, `astral.state.job-prior-states-enforced`, `astral.dispatch.entity-state-bound`, `astral.batch.claim-process-release`, `astral.config.config-source-of-truth`).

**Scope:** Test tree + `docs/test-bible/**` + one pinned JSON fixture only. **No `src/` edits.** Product assumption: AST-1806 purge on the tree under test.

**The one question:** Does this proposed change conflict with or require updating any directive in force?

**Answer:** No. This ticket re-expresses tests and bible rows so they lock **Susan’s implicit `_RETRY` model** and AST-1806 behavior already aligned with **`patt.task.dispatch-retry`** (Arc 1: no separate registry instance; Arc 2: validation via base). It does not introduce new product policy or carve-outs.

| Area | Assessment |
|------|------------|
| **T1 rewrites (14 cases)** | Move from raw `*_RETRY` keys / literal `prior_states` lists to `is_registered_state`, `registered_base`, `state_prior_states`, and key absence. That matches in-force retry law; it does not require amending statutes that still say `JOB_STATES.prior_states` in shorthand (enforcement outcome unchanged—same point as AST-1806 board OK). |
| **T2 repro + snapshot fixture** | `[bug-repro]` pins zero explicit retry keys; snapshot pins pre/post gate identity. Documentation of product contract, not a canon corpus change. |
| **T3 consumer tests** | Cover B4 sites (`_requested_stage_failure_target`, claim, `save_company`, `_progress_rank`) in terms of implicit substates and AST-642 terminal-on-retry—consistent with active pattern, not a new precedent. |
| **T4 bible** | Test-bible hygiene only. |
| **Boundary with AST-1807** | Plan avoids duplicating full derived-prior equality work; uses membership/`in` where appropriate—no canon tension. |

**ESCALATE:** Not warranted—no architectural ambiguity; Susan rule and AST-1806 plan already decided the model.

**F3 (`validate-plan` fix mode):** Not triggered from this board pass.

**Precedent:** Same shape as AST-1807 / AST-1802—test/bible-only gap, **CANON: OK**.

---

**Machine-readable upshot (Chuckles posts `--as joan`):**

```
[board-joan]  CANON: OK
```

**Stdout:**

```text
[board-joan]  CANON: OK
AST-1808 board-joan done — CANON: OK.
```

context_tokens≈35000

### Review-fix findings (AST-1808)

[code-rubric]
**Ticket:** AST-1808  
**Publish ref:** 0435671d644a4ab4e9e3217c7035f3b6fe59ae28  
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3  
**Overall:** CLEAN

## Fix-specific checks

**`[bug-repro]`:** OK  
- **Node:** `tests/component/utils/test_config.py::TestAst1808RetryRegistryPurge::test_no_explicit_retry_keys_in_entity_registries` — comment tags `[bug-repro] AST-1808`.  
- **Body matches plan § Repro:** for each of `JOB_STATES`, `COMPANY_STATES`, `CANDIDATE_STATES`, asserts no registry key ending in `RETRY_SUFFIX` and no `prior_states` entry ending in `RETRY_SUFFIX`. That pins Susan’s “no explicit `_RETRY` in config” after AST-1806 — not tautological (would fail with 18 keys on pre-purge `65e3ca6f`; green on purged tree).  
- **Companion T2:** `test_prior_snapshot_pinned` uses checked-in fixture + **`_RETRY_RETRY` strip on both sides** (comment + compare line match Betty’s design note and AST-1806 gate script behavior).  
- **Consult pin (Radia ask on AST-1806):** `test_consult_fail_dest_for_retry_job_states` asserts primary → holding via `_PAIRS`, holding → terminal `err`, and `PASSED_LIKE_RETRY` / `PASSED_LIKE_RETRY` → `FAILED_TECHNICAL` — concrete post-purge routing when retry keys are absent from `JOB_STATES`.

**`## What must still hold`:** OK  
- **No `src/`:** zero `src/` hunks in ftr…sub diff.  
- **14 rewrites:** diff touches `test_config.py` at the Betty + Ada line sites; pattern is key absence + `is_registered_state` / `registered_base` / `state_prior_states` with `in` / `set` for derived priors (e.g. AST-1155 companions, AST-898 feeders) while raw `prior_states` lists drop explicit retry names.  
- **AST-1807 preserved:** `TestAst1807*` block in `test_config.py` is append-only relative to AST-1807 work; AST-1808 adds after it.  
- **`dispatch_claim_states`:** AST-1155 rewrite keeps both companion asserts unchanged.  
- **Fail-dest tests elsewhere:** no edits to `test_consult.py` AST-642 matrix in this diff; new consult coverage lives in `TestAst1808RetryRegistryPurge` only.

## Canon scores

(no frozen canon list on Linear Description — gap-ticket pattern; zero ids locked at Plan Approved; scored set empty)

## Column diff vs plan stage

no plan-stage scores attached (F3 not triggered; Joan fix-board `[board-joan] CANON: OK` only)

## Frame diff

(none)

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list on gap ticket (same pattern as AST-1807 / AST-1802). Joan board OK only.  
  **Recommendation:** No Canon Scope amendment required; tests lock AST-1806 purge aligned with `patt.task.dispatch-retry`.

- **Location:** Plan T3 / T4 vs landed artifact — `save_company`  
  **Finding:** Plan named new `tests/component/data/database/test_companies.py`; Betty documented **`.cursorignore` `data/`** blocks agent edits — bible **`### AST-1808`** in `config.md` points `save_company` retry acceptance at existing **`test_dispatch_tasks.py`** anchors (×4 `WEBSITE_FOUND_RETRY` saves). No new DB-layer test node; coverage is indirect but documented.  
  **Recommendation:** Accept as known gap (spawn prompt acknowledged); optional follow-up if Susan wants a dedicated `JOBLIST_IDENTIFIED_RETRY` save assert outside blocked paths — not fix-now on this tip.

- **Location:** Plan T4 — `docs/test-bible/data/database.md`  
  **Finding:** Board listed five bible pages including `data/database.md`; landed **`### AST-1808`** blocks are in `utils/config`, `core/roster`, `core/candidate`, `ui/api/api_system` (save_company row lives under config § AST-1808).  
  **Recommendation:** Optional bible file split later; not a product or repro blocker.

### advisory

- **Location:** `git diff` three-dot base  
  **Finding:** Git warns **multiple merge bases** (`2a419fbf`); ftr…sub diff can include hunks already on `origin/ftr` (e.g. duplicate-looking `+ast1807_*` in `test_candidate.py` when merge-base lags ftr tip). Review substance is AST-1808 commits (`5a1becb6` / `e0c39e85` / `merge-tests`).  
  **Recommendation:** Chuckles use publish ref `0435671d` + manifest, not raw diff line count alone.

- **Location:** Manifest **42/45** (spawn: **3** pre-existing also red on `65e3ca6f`)  
  **Finding:** Bible documents additional pre-existing failures (`test_count_eligible_homepage_ready_unions_wfr`, other `test_config` debt). Matches fix-lane “manifest green for AST-1808 scope, baseline debt out of scope.”  
  **Recommendation:** Do not block UT on unrelated reds; Chuckles parity check as noted.

- **Location:** `test_consult_fail_dest_for_retry_job_states`  
  **Finding:** Post-purge, holding states have no registry row; test encodes current `_consult_batch_fail_dest` behavior (direct `get(st)` + terminal paths). Matches AST-1806 Radia advisory on fail-dest — now locked in tests.  
  **Recommendation:** None for resolve-child.

## Notes (informal board overlap — not scored)

| Directive | vs test/bible diff |
|-----------|-------------------|
| `patt.task.dispatch-retry` | Zero explicit keys repro + implicit-state consumer tests. |
| `astral.state.job-prior-states-enforced` | Rewrites separate declared vs derived priors; snapshot pins gate identity. |
| `astral.config.config-source-of-truth` | Fixture + helper-derived asserts only. |
| `astral.standards.in-scope-only` | Tests, bible, fixture JSON, plan doc — no product. |

## What's solid

- **T1:** Fourteen purge-break sites rewritten in `test_config.py` (Betty’s seven + Ada’s seven), including AST-721/720/507, AST-898/1339, AST-1053/1055, AST-1155 companions, inflight hide `is_registered_state`, etc.  
- **T2:** `TestAst1808RetryRegistryPurge` with repro + pinned `tests/component/utils/fixtures/ast1806_prior_snapshot.json` (936 lines) + consult fail-dest matrix.  
- **T3:** `TestAst1808RetryResolvesViaBase` (candidate), `test_ast1808_single_state_retry_claims_with_base_criteria` (roster), `TestAst1808ProgressRankRetry` (api_system).  
- **T4:** Bible sections with **Broken / obsolete → revised** list, repro node, manifest command, pre-existing failure callout.  
- **Boundary with AST-1807:** Derived-prior **equality** tests stay in `TestAst1807*`; AST-1808 uses membership/`set` for purge rewrites — matches plan.  
- **Estimate ~3** fits (~1.6k LOC tests/bible/fixture/plan).  
- Closes Betty **`TESTS: REVISE`** on **AST-1806** product tip.

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal (AST-1804; diff base `origin/ftr/AST-1804-fetch-avail-retry`) | → **Review Posted** → append artifact + `docs(AST-1808): Radia review — clean` on publish ref → post slim upshot `--as radia` → §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |
| — | **AST-1806** | Product docs-acceptance closes once this lands (Betty REVISE bar for purge tests). |

**Chuckles note:** `[bug-repro]` present and substantive. Manifest 42/45 with three known pre-existing failures — align with Ada/Betty threads; do not merge-block AST-1806 UT on unrelated baseline.

context_tokens≈45000

```
[code-rubric] PROCEED (Commit: 0435671d644a4ab4e9e3217c7035f3b6fe59ae28) Purge test gap clean
```

## Bug: AST-1810 — fetch_website counts and claims every `WEBSITE_FOUND_RETRY` row (drop the AST-892 `homepage_text` exclusion)

Parent AST-1804 (UAT batch; AST-1805–1808 shipped to dev). Susan (verbatim): *"The deliberate exception is a bug. Please remove the exception and include the RETRY rows regardless of homepage text."* The ticket's To-be adds: *"Any other exceptions are also removed."*

### As-is
- fetch_website's trigger is `WEBSITE_FOUND`. It claims `dispatch_claim_states("WEBSITE_FOUND", "company") == ["WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"]`.
- Three places carve out `WEBSITE_FOUND_RETRY` rows with non-empty `company_data.homepage_text` (AST-892, "prefilter second strike"):
  1. **Count:** `database.count_eligible_for_dispatch_task` (~8989) sends fetch_website to its own helper, `count_companies_eligible_for_fetch_website` (~9041), which adds `AND NOT (state = ? AND homepage_text non-empty)`.
  2. **Claim:** `dispatcher._run_unified` (~749) passes `exclude_prefilter_second_strike=(dispatch_task_key == "fetch_website")`. `roster.get_new_company_batch` (~1397/1430) passes it through `database.claim_company_batch` (~226/246) to `set_company_batch` (~984/1025), which adds the same `NOT (…)` clause.
  3. **Handler:** `gazer.fetch_website_batch` (~527–541). If an already-claimed row is `WEBSITE_FOUND_RETRY` with `homepage_text`, it does `skipped += 1; return`: no scrape, no transition, not counted in `total`.
- The clause keys come from `config.fetch_website_prefilter_second_strike_filter()` (~3610). Comments at config ~1268 and ~2308 describe the "dual ownership".

### To-be
- fetch_website's Avail count and its claim both take **every** unclaimed `WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` row, whatever `homepage_text` holds, and the two stay in step.
- The handler scrapes every claimed row: no second-strike skip.
- The count uses the same generic company path as every other company task: `count_entities_in_state(entity_type, state, candidate_id, states=claim_states)`.

### Repro
There's no live-DB repro: the local `astral.db` has 0 companies and no fetch_website dispatch row (probed read-only). The code-level repro is the existing pinned test, which is green today and pins the exclusion:
- `tests/component/data/database/test_dispatch_tasks.py` ~1197 (AST-892 class).
- It seeds one `WEBSITE_FOUND_RETRY` row with `homepage_text`, one without, and one `WEBSITE_FOUND`.
- Today: the fetch_website count is 2, the claim is 2 (`{"retry", "fresh"}`), and the second-strike row is left out. To-be: count and claim are both 3.
- Handler: `tests/component/core/test_gazer.py` ~423 `test_skips_wfr_when_homepage_text_present` asserts `skipped == 1` and no scrape. To-be: the row is scraped.

### Root cause
AST-892 split `WEBSITE_FOUND_RETRY` into two owners by `homepage_text` (fetch_website for empty rows, prefilter for rows with text) and enforced the split in the count, the claim and the handler. Susan ruled the split itself is the bug: under AST-1804, `{base}_RETRY` is an implicit substate of `WEBSITE_FOUND`, so fetch_website owns all of it.

### Proposed change

**P1. `src/data/database.py`**
- `count_eligible_for_dispatch_task` (~8989): delete the `if (task_key or "").strip() == "fetch_website": return count_companies_eligible_for_fetch_website(...)` branch. fetch_website then falls through to the existing score-floor check (its row has no `score_floor`) and on to `count_entities_in_state(..., states=claim_states)`, like every other company task.
- Delete `count_companies_eligible_for_fetch_website` (~9041–9068).
- `set_company_batch`: delete the `exclude_prefilter_second_strike` parameter and its `if exclude_prefilter_second_strike:` block (~1025–1033).
- `claim_company_batch`: delete the `exclude_prefilter_second_strike` parameter, its docstring line (~232) and the passthrough (~246).
- Drop `fetch_website_prefilter_second_strike_filter` from the config import (~109).

**P2. `src/core/dispatcher.py`** `_run_unified` (~749): delete the `exclude_prefilter_second_strike=(dispatch_task_key == "fetch_website"),` kwarg.

**P3. `src/core/roster.py`** `get_new_company_batch`: delete the `exclude_prefilter_second_strike` parameter (~1397) and the passthrough (~1430).

**P4. `src/utils/config.py`**
- Delete `fetch_website_prefilter_second_strike_filter` (~3610–3619). After P1 it has no `src/` caller.
- Reword the two AST-892 comments to say there is a single owner:
  - ~1268: `# retry_of("WEBSITE_FOUND"): fetch_website scrape retry for every row (AST-1810; AST-892 split removed).`
  - ~2308: `# Shared retry holding; fetch_website claims all of it (AST-1810).`

**P5. `src/core/gazer.py`** `fetch_website_batch` (~527–541): delete the second-strike skip block, and remove `skipped` from the counter set if nothing else increments it. Keep the returned dict shape `{"passed", "failed", "errors", "skipped", "total"}` with `skipped` fixed at 0, so `consult`'s work-only total mapping is unchanged. Update the docstring (~494–498) to drop the AST-892 skip wording.
- **Outside the amended scope:** `gazer.py` is in AST-1804's Component scope only "if it transitions to a literal `*_RETRY`". Without P5, P1–P3 claim the rows and the handler skips them. They are then released unprocessed and reclaimed on every run: a hot loop, and the To-be doesn't hold. See `[scope-gate]` on AST-1810.

**Re-fetching prefilter second-strike rows (knowingly overwriting `homepage_text`):**
- These rows reach `WEBSITE_FOUND_RETRY` from `HOMEPAGE_READY` on a prefilter technical failure (`COMPANY_STATES["HOMEPAGE_READY"]["retry_state"]`).
- fetch_website now re-scrapes them. On pass, `save_company_data(short_name, {"homepage_text": …, "nav_links": …})` **merges**: only `homepage_text` (and `nav_links` when the new scrape found any) are replaced. `prefilter_score`, `prefilter_company_notes`, `possible_joblist_links` and the rest are kept. The row then goes to `HOMEPAGE_READY`, and prefilter runs on fresh text.
- On an infra error while on the retry, the row goes to `CANNOT_READ_WEBSITE` (`_fetch_website_fail_destination`: retry re-fail → terminal); a site error also goes to `CANNOT_READ_WEBSITE`. This is accepted per Susan's ruling; no code guards the overwrite.
- **Flagged, not changed (no limit added without Susan's approval):**
  - `HOMEPAGE_READY` →(prefilter technical fail)→ `WEBSITE_FOUND_RETRY` →(fetch_website pass)→ `HOMEPAGE_READY` can repeat for as long as prefilter keeps failing technically and the scrape keeps succeeding.
  - Under AST-1798 suffix-always, prefilter's `HOMEPAGE_READY` row claims `HOMEPAGE_READY(_RETRY)`, not `WEBSITE_FOUND_RETRY`. So the old second-strike → `ERROR_PREFILTER` exit only fires if an admin-created retry-only prefilter row on `WEBSITE_FOUND_RETRY` claims the row first.
  - Bounding the cycle is a product decision for Susan.

**Other count/claim differences reviewed for "any other exceptions".** Neither is fetch_website-specific, so both are **not changed** and flagged for Susan:
- **Meteorite placeholders:** `set_company_batch` always skips `short_name LIKE 'meteorite-%'` (AST-1041), but `count_entities_in_state` doesn't, for every company task. Local DB: 0 meteorite rows in `WEBSITE_FOUND*`.
- **Scan interval:** the dispatcher turns a company row's `freq_hrs > 0` into a claim-only `scan_interval_hours` (a gaze cadence knob), and count ignores it. It only applies to fetch_website if its dispatch row has `freq_hrs` set.
- `require_empty_website` (resolve only) and `score_floor` (fetch_website isn't scored) don't apply.

### Blast radius
- **Product:** P1–P5 as listed. Nothing else in `src/` reads the flag or the helper (grep: only these sites).
  - `roster.prefilter_company_batch`'s not-ready branch (~2086–2096) still leaves `WEBSITE_FOUND_RETRY` rows without text for fetch_website.
  - `_prefilter_batch_fail_dest` still routes a retry re-fail to `error_state`. Both unchanged.
- **Ownership:** a retry-only prefilter dispatch row on `WEBSITE_FOUND_RETRY`, if one exists, now competes with fetch_website for the same rows. Whoever claims first wins; batch claim is atomic, so there's no double-processing.
- **Tests that pin AST-892 (Betty; the engineer does not edit them):**
  - `test_dispatch_tasks.py` ~1197–1300: `test_count_excludes_second_strike_includes_scrape_retry` (count becomes 3), `test_claim_skips_second_strike_keeps_bare_wfr` (the kwarg is gone; claim is 3), `test_prefilter_claim_still_takes_second_strike` (drop the kwarg; the prefilter claim is unchanged).
  - `test_gazer.py` ~423–500: `test_skips_wfr_when_homepage_text_present` and `test_mixed_skip_and_scrape_excludes_skips_from_total` flip to scrape.
  - `test_config.py` ~2181 helper test: delete it.
  - `test_roster.py` ~329: the `exclude_prefilter_second_strike=False` call-kwarg assert goes.
  - `test_consult.py` ~1864 (work-only total → `total_processed=0`): still valid in shape; review.
- **Bible:** `docs/test-bible/{data/database/dispatch_tasks,core/gazer,core/roster,core/consult,utils/config}.md` AST-892 rows.
- **Canon:** grep of `canon/` for second-strike / AST-892 / `homepage_text` finds nothing, so there's no directive to amend.

### What must still hold
- AST-641 / AST-1798: `dispatch_claim_states("WEBSITE_FOUND", "company")` is unchanged, and count and claim use the same `claim_states`.
- AST-1800 / AST-1801: a multi-state claim is still not registry-gated.
- AST-1041: meteorite placeholders are still never claimed.
- AST-642 routing: fetch_website infra fail on base → retry; re-fail on retry → `CANNOT_READ_WEBSITE`. Prefilter's retry re-fail → `ERROR_PREFILTER`.
- `save_company_data` merge semantics: re-fetching never wipes prefilter-owned `company_data` keys.
- The `fetch_website_batch` return dict keeps its keys, so `consult`'s total mapping is unchanged.
