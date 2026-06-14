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
