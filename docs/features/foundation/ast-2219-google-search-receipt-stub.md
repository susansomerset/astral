# AST-2219 — Google search calls and receipt stub

- **Linear:** [AST-2219](https://linear.app/astralcareermatch/issue/AST-2219)
- **Parent:** [AST-2215](https://linear.app/astralcareermatch/issue/AST-2215) — Add task `fetch_timesheet`
- **Publish ref:** `sub/AST-2215/AST-2219-google-search-receipt-stub`

After AST-2217 / AST-2218: each Google CSE query writes one `DISPATCH_SEARCH` `service_timesheet` row (via the existing `record_search_timesheet_entry`), `google_cse.get_receipt` is the zero stub (receipt cost empty), and the fetch runner routes / key-gates `google_cse` so those rows can stub-receipt. Does **not** own provision, OpenRouter billed receipts, daemon retirement, or contact ledger wrapping.

## Explicit scope gate

Files and change kinds match this ticket’s amended **## Scope** (includes `timesheets.py` after Chuckles cleared `[scope-gate]`). Test / bible paths are Betty (`qa-child`); engineer commits product only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/google_cse.py` | Zero-stub `get_receipt`; `search_google_cse` returns hits + call_start / call_stop / hit_count | external |
| `src/core/timesheets.py` | Route `google_cse` in `_get_receipt_fn`; key exception for search provider; optional entity on `record_search_timesheet_entry` | core |
| `src/core/roster.py` | Both CSE call sites record through `record_search_timesheet_entry` using returned timing + entity | core |
| `tests/component/external/test_google_cse.py`, `docs/test-bible/external/google_cse.md` | Betty | test/bible |
| `tests/component/core/test_roster.py`, `docs/test-bible/core/roster.md` | Betty | test/bible |
| `tests/component/core/test_timesheets.py`, `docs/test-bible/core/timesheets.md` | Betty | test/bible |

## Stage 1: `google_cse` return shape + zero-stub `get_receipt`

**Done when:** `get_receipt(["x","y"], key)` returns two dicts whose keys are exactly `TIMESHEET_RECEIPT_FIELDS`, tokens/status filled, `platform_cost is None`, no HTTP; `search_google_cse` returns a structured result with `hits`, `call_start`, `call_stop`, `hit_count` (and early/empty paths still fill timing).

1. In `src/external/google_cse.py`, add a `TypedDict` (name flexible, e.g. `GoogleCseSearchResult`) with keys:
   - `hits: list[GoogleCseHit]`
   - `call_start: str` (UTC ISO)
   - `call_stop: str` (UTC ISO, ≥ start)
   - `hit_count: int` (equal to `len(hits)` after any max_results trim)

2. Change `search_google_cse` return type from `list[GoogleCseHit]` to that TypedDict. Capture `call_start` at function entry (`datetime.now(timezone.utc).isoformat()`); set `call_stop` on every exit path (success, empty items, max-results trim, pagination break). Prefer one helper that builds `{hits, call_start, call_stop, hit_count}` so early `return hits[:max_results]` sites do not forget timing.

3. Update `__all__` to export `get_receipt` and the result TypedDict (keep `GoogleCseHit`, `search_google_cse`).

4. Add `get_receipt(external_ids: list[str], api_key: str) -> list[dict]` matching AST-2217 Anthropic stub: one row per id, keys exactly `TIMESHEET_RECEIPT_FIELDS`, token fields `0`, `platform_cost=None`, `completion_status="stub"`, no network, `api_key` ignored. Docstring: zero stub until search pricing exists (AST-2215).

⚠️ **Decision:** Structured return object (not a bare list + side channel). Only in-repo product callers of `search_google_cse` are the two `roster.py` sites (Scope); both are updated in Stage 3. Tests that call CSE are Betty’s.

## Stage 2: Timesheets — route, key exception, entity on recorder

**Done when:** `_get_receipt_fn(TIMESHEET_SEARCH_SERVER_ID)` returns `google_cse.get_receipt`; `run_fetch_timesheet` does **not** skip `google_cse` for missing candidate API key (calls stub with `""`); `record_search_timesheet_entry(..., entity_type=..., entity_id=...)` persists those columns.

1. In `src/core/timesheets.py` `record_search_timesheet_entry`, add optional kwargs `entity_type: Optional[str] = None`, `entity_id: Optional[str] = None` and pass them into `record_timesheet_entry` (replace the hard-coded `None`s). Defaults keep prior behavior for any existing callers/tests.

2. In `_get_receipt_fn`, before the llm_compat fallback:

```python
if provider == TIMESHEET_SEARCH_SERVER_ID:  # "google_cse"
    from src.external.google_cse import get_receipt
    return get_receipt
```

3. In `run_fetch_timesheet`’s per-provider loop, when resolving the key: if `provider == TIMESHEET_SEARCH_SERVER_ID`, set `key = ""` (or `_api_key_for_server(...) or ""`) and **do not** `continue` on missing candidate key. All other providers keep the existing warning + skip. Stub ignores the key; shared `get_receipt(ids, key)` signature stays.

⚠️ **Decision:** Key exception is provider-specific only — do not weaken the candidate-key gate for LLM servers. Empty string satisfies the call signature without inventing a fake CSE secret in `candidate_api_keys`.

**Boundaries (this stage):** Do not change OpenRouter / Anthropic / llm_compat routing, claim/`finally` logic, provision, or config.

## Stage 3: Roster — both CSE sites record search rows

**Done when:** After a successful `search_google_cse` in either site, one `DISPATCH_SEARCH` row exists for the candidate + current `batch_id` with `response_item_count == hit_count`, all token/`calc_cost_*` zero, and entity filled per site; existing `logger.debug` Calling/Response lines remain (`stat.logging.debug`); skipped-website path (no CSE call) records nothing.

1. Import `record_search_timesheet_entry` from `src.core.timesheets` in `src/core/roster.py`.

2. **`resolve_company_website`** (CSE call ~692):
   - Unpack `result = search_google_cse(...)` → `hits = result["hits"]` (rest of function keeps using `hits` as today).
   - After a successful return from CSE (including zero hits), call:

```python
record_search_timesheet_entry(
    candidate_id=(entity.get("candidate_id") or "").strip() or None,
    batch_id=log_batch_id.get(),
    hit_count=result["hit_count"],
    call_start=result["call_start"],
    call_stop=result["call_stop"],
    entity_type="company",
    entity_id=short_name,
)
```

   - On `RuntimeError` / `ValueError` from CSE: do **not** record (no completed call). Keep existing warn + failure return.
   - Early skip when `company_website` already set: no CSE, no timesheet row.

3. **`run_inflow_discovery_batch`** (CSE call ~804, per term):
   - Same unpack; after each successful CSE (including zero hits for that term), record:

```python
record_search_timesheet_entry(
    candidate_id=candidate_id,
    batch_id=batch_id,
    hit_count=result["hit_count"],
    call_start=result["call_start"],
    call_stop=result["call_stop"],
    entity_type="candidate",
    entity_id=candidate_id,
)
```

   - On per-term CSE exception: no record for that term (existing continue path).

⚠️ **Decision:** Record on zero-hit successes too — the query is still a billable/attributable call (tokens 0, item count 0). Matches “each Google search query writes one row.”

## Boundaries

- No `dispatcher.py` / OpenRouter billed path / contact ledger / config registries.
- No daemon reconcile work.
- Engineer does not commit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review (build)

**Built @ `781924332`** — `origin/sub/AST-2215/AST-2219-google-search-receipt-stub` (`781924332421f6adced65dc897183d53262e3c40`)

- Stage 1: `GoogleCseSearchResult` + structured `search_google_cse` return; zero-stub `get_receipt` (`platform_cost=None`).
- Stage 2: `_get_receipt_fn` routes `google_cse`; fetch runner key exception for search provider; optional entity on `record_search_timesheet_entry`.
- Stage 3: both roster CSE sites unpack result and record `DISPATCH_SEARCH` (resolve skips record when `log_batch_id` unset).
- Out of scope: OpenRouter/daemon/provision (2218), contact ledger (2220). Betty owns test/bible in Scope.

## Joan validate


```text
[plan-rubric]
**Ticket:** AST-2219
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2215/AST-2219-google-search-receipt-stub` @ `c082b82936ab2c7d9d172b71c07039335fcf2239`

## Canon scores

stat.logging.debug | A | | 

## Traceability

Child AC 10 → Stages 1–3 (CSE record + stub `get_receipt` + runner route); parent AC 1–9,11 → N/A (#1/#2/#4); Stage 2 depends on AST-2218 runner (not re-owned here); stages map to parent FS 7 + Technical scope CSE recording.

## Findings

### acceptable — Scope gate (`timesheets.py`)

- **Severity:** acceptable
- **Location:** `[scope-gate]`; Stage 2; ticket `## Scope`
- **Finding:** Without `google_cse` routing and key skip, `DISPATCH_SEARCH` rows never stub-receipt and batches stall in `FETCHING`/`NEW`; amended Scope + Stage 2 match the gate ask.
- **Recommendation:** None.

### discuss — Build ordering (#1 + #2 before #3)

- **Severity:** discuss
- **Location:** Preamble; Stages 2–3
- **Finding:** Plan assumes `record_search_timesheet_entry`, `TIMESHEET_SEARCH_SERVER_ID`, `run_fetch_timesheet`, and registries from AST-2217/2218.
- **Recommendation:** Integrate on ftr after siblings merge; Betty AC10 is the primary child check.

### discuss — `batch_id` when `log_batch_id` unset

- **Severity:** discuss
- **Location:** Stage 3 `resolve_company_website` (`batch_id=log_batch_id.get()`)
- **Finding:** Parent AC10 is “inside a batch”; plan does not say skip record when `batch_id` is `None`.
- **Recommendation:** Engineer/Betty: only call `record_search_timesheet_entry` when `batch_id` is truthy, or document intentional no-op — avoids orphan rows if a CSE hop runs outside a claim.

### discuss — Assignee not Joan (process)

- **Severity:** discuss
- **Location:** Linear assignee Katherine Johnson
- **Finding:** validate-plan gate expects Joan at spawn; review run per Chuckles spawn prompt.
- **Recommendation:** Chuckles handoff only; no plan change.

### acceptable — CSE layer stays log-free

- **Severity:** acceptable
- **Location:** `google_cse.py` module contract; Stage 1
- **Finding:** Debug stays on roster Calling/Response joints; no new `google_cse` logging — matches external-layer rule and sole canon id.
- **Recommendation:** None.

### acceptable — Zero-hit searches still recorded

- **Severity:** acceptable
- **Location:** Stage 3 decisions
- **Finding:** Aligns with parent “each Google search query writes one row” and AC10 item count semantics.
- **Recommendation:** None.

context_tokens≈48000
```

## Radia review

```text
[code-rubric]
**Ticket:** AST-2219
**Publish ref:** `16e3b32500c4fabbe67adaacfb400997824a5be7` (`origin/sub/AST-2215/AST-2219-google-search-receipt-stub`)
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Overall:** CLEAN

## Canon scores

stat.logging.debug | A | |

## Column diff vs plan stage

(aligned) — Joan: A @ plan tip `c082b82936ab2c7d9d172b71c07039335fcf2239`; build lands Stages 1–3 through tip `16e3b3250` (+ Betty tests/bibles).

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling stack in three-dot diff:** vs `origin/dev`, diff includes AST-2217 / 2218 / 2220 product, tests, and plan docs (expected before epic lands on `dev`). AST-2219-owned product commits (`035cec931`…`781924332`): `google_cse.py`, `timesheets.py`, `roster.py` only (+91 / −22 lines).
- **Joan `batch_id` discuss — addressed on resolve path:** `resolve_company_website` records only when `log_batch_id.get()` is truthy (comment cites AC10 / avoid orphans). `run_inflow_discovery_batch` always records after successful CSE — `batch_id` is a required function argument there, so orphans are not expected in normal dispatch.
- **Build ordering:** Depends on AST-2217/2218 (`record_search_timesheet_entry`, `TIMESHEET_SEARCH_SERVER_ID`, `run_fetch_timesheet`); satisfied on this publish ref.
- **Canon Scope:** single frozen id `stat.logging.debug`; `google_cse` correctly stays log-free per external-layer contract; debug remains on roster Calling/Response joints.

## What's solid

- **Stage 1:** `GoogleCseSearchResult` + `_search_result` on all successful exit paths; `get_receipt` zero-stub with exact `TIMESHEET_RECEIPT_FIELDS`, `platform_cost=None`, `completion_status="stub"`, no HTTP; `__all__` updated.
- **Stage 2:** `_get_receipt_fn` routes `TIMESHEET_SEARCH_SERVER_ID` → `google_cse.get_receipt`; `run_fetch_timesheet` uses empty key for CSE without skip-on-missing-key; optional `entity_type` / `entity_id` on `record_search_timesheet_entry`.
- **Stage 3:** Both CSE sites unpack `result["hits"]`; record `DISPATCH_SEARCH` with timing and entity attribution; CSE failures do not record; early website skip unchanged.
- **Boundaries:** No dispatcher/OpenRouter/daemon/contact/config registry edits in 2219 commits.
- **Tests (Betty, Tests Passed):** `test_google_cse` AST-2219 stub/shape; `test_roster` AC10 recording + no-record when batch unset on resolve.

## Recommended actions (Chuckles / downstream — not executed by Radia)

- Append artifact; `docs(AST-2219): Radia review — clean`; push; post slim upshot `--as radia`; **Review Posted** → User Testing.

context_tokens≈38000
```

