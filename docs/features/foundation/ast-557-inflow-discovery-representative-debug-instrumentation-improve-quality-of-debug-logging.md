<!-- linear-archive: AST-557 archived 2026-06-15 -->

## Linear archive (AST-557)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-557/inflow-discovery-representative-debug-instrumentation-improve-quality  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-538 — Improve Quality of Debug Logging  
**Blocked by / blocks / related:** parent: AST-538

### Description

## What this implements

Dispatcher + roster inflow_discovery / vet_inflow_discovery per-index debug (found + recorded).

## Acceptance criteria

2,4 from parent.

## Boundaries

Uses shared helper from contract child; not full component backfill.

## Git branch (authoritative)

Per orientation-astral: parent `ftr/ast-538-improve-quality-of-debug-logging`, child `sub/AST-538/<child-id>-<slug>`.

### Comments

#### betty — 2026-06-03T03:27:13.422Z
**Betty — bible rollup reconcile (AST-557)**

Replaced **`docs/ASTRAL_TEST_BIBLE.md`** on **`origin/sub/AST-538/AST-557-inflow-discovery-representative-debug`** with **`origin/ftr/ast-538-improve-quality-of-debug-logging` @ `50716857`** + **§7.13zu** only (after **§7.13zt**). Removed stray **§7.13zr** / **§7.13zv** / **§7.13zw** tails that were not on parent ftr. Product/tests on sub unchanged.

- **Publish tip:** `2e89defe`
- **Bible shasum:** `a8cf19b4f2b062a46c7b7c322bff3780e7e58c8158714872ef9cdfbec3577b82`
- **Status:** User Testing unchanged (rollup fix only)

— Betty

#### betty — 2026-06-03T03:25:29.800Z
**Rollup bible reconcile (Betty)** — `origin/sub/AST-538/AST-557-inflow-discovery-representative-debug` @ `140eb825`

- Merged **`origin/ftr/ast-538-improve-quality-of-debug-logging`** into **`dev-betty`**; published bible-only **`docs(AST-557): reconcile bible §7.13zu for ftr rollup`**.
- **§7.13zs** (**AST-554** + **AST-556** row) and **§7.13zt** (**AST-555**) match **`ftr/ast-538`**; **§7.13zu** holds **AST-557** manifest (no **AST-557** row under **§7.13zs**).
- **`docs/ASTRAL_TEST_BIBLE.md` shasum:** `11a4d31cb4e38bfe3e0b01d601b3834afd13535e4da97e32a131b03bca4e8027`

Status unchanged (**User Testing**). Joan **`rollup-child`** for **AST-557** can retry.

#### radia — 2026-06-03T03:19:36.488Z
**Review** — `origin/dev...origin/sub/AST-538/AST-557-inflow-discovery-representative-debug` (product @ `4be2af40`; Radia doc @ `fc291360` on publish ref).

**fix-now:** none.

**discuss**
- `src/core/roster.py` — `run_inflow_discovery_batch`: after the term loop, `if not all_hits` returns with no contract header when CSE ran but dedupe left zero hits (plan Stage 1.4 allows skipping vet). Optional: one `debug_index` with outcome `no deduped hits after CSE` when `debug=True` — not blocking.

**advisory**
- `src/core/agent.py` (unchanged in this diff): `vet_inflow_discovery` still uses legacy `do_task` debug paths, not §1.5.1 contract headers — matches plan out-of-scope / later backfill.
- Plan doc: `docs/features/foundation/ast-557-inflow-discovery-representative-debug-instrumentation-improve-quality-of-debug-logging.md` § Review (Radia) on publish ref.

**§1.5.1 / plan (solid)**
- `roster.run_inflow_discovery_batch`: `set_debug_flag(debug)`; per-term `debug_index` + hit `debug_detail` (20-hit cap); vet block `debug_detail_block`; per-row ingest outcomes; batch summary detail; `do_task(..., debug=debug)`.
- `dispatcher._run_unified` / `_run_task`: contract lines only when `task_key == inflow_discovery` and `debug=True`; other tasks keep grandfather `[DEBUG]`.
- No contract emission paths when `debug=False` on touched branches.

**resolve-astral:** no code changes required from this review.

#### betty — 2026-06-03T03:13:21.270Z
## QA test manifest

**Publish:** `origin/sub/AST-538/AST-557-inflow-discovery-representative-debug` @ `4be2af40`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `26576b04d50fe0588312a5bc8fd6fe4fd9a4ee60` (**§7.13zs** — **AST-557** row)

**Classification:** Existing coverage (bible-backed). Parent **AST-538** AC 7 + plan Stage 3 forbid Betty log-string tests for this child; **AST-554** owns helper gating/truncation tests.

1. `.venv/bin/python -m pytest tests/component/core/test_roster.py::TestAst505InflowDiscovery -q`
2. `.venv/bin/python -m pytest tests/component/core/test_dispatcher.py -k "inflow or ast505" -q`
3. `.venv/bin/python -m pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q` (blocker **AST-554** regression)

**Susan UAT (plan Stage 3 — not automated):** `debug=True` with ≥2 stale terms → term/vet/row contract trace; `debug=False` → no `index N/M` contract headers on dispatcher + roster paths (parent AC 2/4).

#### hedy — 2026-06-03T00:39:49.825Z
Plan: `docs/features/foundation/ast-557-inflow-discovery-representative-debug-instrumentation-improve-quality-of-debug-logging.md`

https://github.com/susansomerset/astral/blob/sub/AST-538/AST-557-inflow-discovery-representative-debug/docs/features/foundation/ast-557-inflow-discovery-representative-debug-instrumentation-improve-quality-of-debug-logging.md

Published @ `5272a5b6` on `origin/sub/AST-538/AST-557-inflow-discovery-representative-debug`.

**Scope:** `Single-Component` — `run_inflow_discovery_batch` plus dispatcher `_run_task` / `_run_unified` branches gated on `inflow_discovery` and `debug=True` only.

**Conf:** `high` — AST-554 contract helpers are on the line; term loop, vet `do_task(debug=)`, and row ingest mapping are explicit in the plan.

**Risk:** `Medium` — Dispatcher is shared, but changes are task-key- and debug-gated; AC 4 spot-check is Stage 3 in the plan.

---

# AST-557 — inflow_discovery representative debug instrumentation (Improve Quality of Debug Logging)

- **Linear (this ticket):** [AST-557](https://linear.app/astralcareermatch/issue/AST-557/inflow-discovery-representative-debug-instrumentation-improve-quality-of)
- **Parent:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)
- **Publish ref:** `origin/sub/AST-538/AST-557-inflow-discovery-representative-debug` (child of AST-538; not Linear `gitBranchName`)
- **Depends on:** [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — `debug_index` / `debug_detail` / `debug_detail_block` in `src/utils/logging.py` and §1.5.1 in `docs/ASTRAL_CODE_RULES.md` must be on the integration line before build.

## Summary

Instrument the **representative** `inflow_discovery` dispatch path and **`run_inflow_discovery_batch`** / **`vet_inflow_discovery`** handoff so that when `debug=True`, Susan sees **per-index** CSE discovery results and **per-row ingest outcomes** (found + recorded), not only batch `summary={...}`. Satisfies parent acceptance criteria **2** (UAT-grade trace) and **4** (no new contract lines when `debug=False`). Does **not** backfill other components, migrate unrelated `[DEBUG]` lines, or add Betty log-string tests.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| `logging.py` / Code Rules contract | **AST-554** (done) |
| Agent Ad Hoc nav rename | **AST-555** |
| `review-astral` fix-now rubric | **AST-556** |
| Global `do_task` `[DEBUG]` → contract migration | Later backfill children |
| `ingest_new_companies` signature change | Log ingest outcomes from caller loop only |
| Other dispatch `task_key`s' `[DEBUG]` lines | Grandfather until those files are touched |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | `run_inflow_discovery_batch`: contract debug per search term, vet bundle, vet row, ingest outcome; pass `debug` into `do_task` | core |
| `src/core/dispatcher.py` | `_run_task` / `_run_unified`: contract debug when `task_key == inflow_discovery` only; leave other tasks' `[DEBUG]` grandfathered | core |

## Stage 1: Roster — `run_inflow_discovery_batch` (`src/core/roster.py`)

**Done when:** With `debug=True`, a multi-term discovery run logs one **index N/M** header per stale search term (CSE hits under ` | ` detail), one vet summary block, one **index N/M** header per vet result row (outcome + recorded fields), and a final batch summary line; with `debug=False`, no new `debug_index` / `debug_detail` / `debug_detail_block` lines (existing WARNING/ERROR unchanged).

1. At the top of `run_inflow_discovery_batch`, after `candidate_id` and `cfg` are resolved, add:

```python
log = logger
log.set_debug_flag(debug)
```

Use module `logger` (`get_logger(__name__)`) — do not shadow with a new `get_logger` call.

2. When `debug` and `not terms`, before the existing `logger.warning(...)` return, emit:

```python
log.debug_index(
    func="roster.run_inflow_discovery_batch",
    index=1,
    total=1,
    identifier=candidate_id,
    outcome="no stale search terms",
)
```

3. Replace the `for term in terms:` loop body instrumentation:

   - Before the loop: `term_total = len(terms)`.
   - At loop start (1-based index): `term_i` from `enumerate(terms, start=1)`.
   - Before `search_google_cse`: no header yet if you prefer outcome-after-search; **instead** call `log.debug_index` **after** CSE completes (success or except) so `outcome` is accurate:

     - **CSE success:** `outcome=f"{len(hits)} hit(s)"` where `hits` is the list returned for this term only (before dedupe into `all_hits`).
     - **CSE except:** `outcome=f"CSE failed: {exc!s}"` (same exception path as today; still `errors += 1`; `continue`).

     Use `identifier=term` (the search string). `func="roster.run_inflow_discovery_batch"`, `index=term_i`, `total=term_total`.

   - After a successful CSE (inside `try`, after `hits = search_google_cse(...)`):

     - `log.debug_detail(f"search_term={term!r} raw_hits={len(hits)}")`
     - For each hit in `hits` (not deduped global list), up to **20** hits: `log.debug_detail(f"hit title={hit.get('title','')!r} url={hit.get('url','')!r}")`. If `len(hits) > 20`, one more `log.debug_detail(f"... {len(hits) - 20} more hits omitted from log")` — **do not** add a new config constant; inline `20` with comment "UAT cap per term".

   - After `update_company_search_term_last_scan_at` on success path, `log.debug_detail("last_scan_at bumped")`.

4. After the term loop, when building `live_content` for vet:

   - If `not all_hits`: skip vet logging block; return as today.
   - If `debug`:
     - `log.debug_index(func="roster.run_inflow_discovery_batch", index=1, total=1, identifier=candidate_id, outcome=f"vet {cfg['vet_task_key']} {len(all_hits)} deduped hit(s)")`
     - `log.debug_detail_block(live_content)` — uses truncation per §1.5.1.

5. Change the `do_task` call to pass through debug:

```python
api_result = await do_task(
    task_key=cfg["vet_task_key"],
    live_content=live_content,
    index=candidate_id,
    ctx=task_ctx,
    debug=debug,
)
```

6. After `do_task` returns:

   - If `debug` and not `api_result.get("success")`: `log.debug_index(..., index=1, total=1, identifier=candidate_id, outcome="vet task failed")` then existing error return.
   - If `debug` and `rows` is not a list: `log.debug_detail("vet parsed_response missing results list")` then existing return.

7. Replace the `for row in rows:` ingest loop with indexed contract logging:

   - `row_total = len([r for r in rows if isinstance(r, dict)])` — if zero, skip row headers.
   - `row_i = 0` before loop; increment only for `dict` rows.
   - For each dict `row`:
     - Compute `action`, `slug`, `site`, `hi` (hit_index) same as today.
     - Determine `outcome` string **before** mutating counters:
       - `action == "ignore"` → `"ignored"`
       - `action != "slug"` → `"skipped unknown action"`
       - empty slug → `"skipped empty slug"`
       - else compute `ingest_ok = ingest_new_companies(...)` (call unchanged)
       - if `ingest_ok`: `outcome=f"recorded state={'WEBSITE_FOUND' if site else 'NEW'} website={site or ''}"`
       - else: `outcome="not recorded (duplicate slug, other candidate, invalid slug, or duplicate URL)"`
     - `log.debug_index(func="roster.run_inflow_discovery_batch", index=row_i, total=row_total, identifier=slug or f"hit_index={hi}", outcome=outcome)`
     - `log.debug_detail(f"action={action!r} hit_index={row.get('hit_index')!r} website={site!r}")` when `debug` (redundant guard ok).
     - Then apply existing `ingested` / `skipped` / `errors` counter logic unchanged.

8. Before the final `return { total_processed: 1, ... }`, when `debug`:

```python
log.debug_detail(
    f"batch summary total_processed=1 total_passed={ingested} "
    f"total_failed={skipped} total_errors={errors} terms={term_total} deduped_hits={len(all_hits)}"
)
```

⚠️ **Decision:** Per-index for **search terms** and **vet result rows** — not one index per deduped hit in `all_hits` — matches Susan's 95-term example (operational unit = term + vet row). Deduped hit listing appears once in the vet `debug_detail_block`.

⚠️ **Decision:** Cap per-term hit detail at 20 lines to avoid console floods; full payload still visible via `debug_detail_block(live_content)` before vet.

## Stage 2: Dispatcher — `inflow_discovery` only (`src/core/dispatcher.py`)

**Done when:** For `task_key == "inflow_discovery"` and `debug=True`, `_run_task` and `_run_unified` use contract helpers instead of `logger.info("[DEBUG] …")`; for `debug=False` or any other `task_key`, behavior and log volume unchanged from today.

1. Near imports, add:

```python
from src.utils.config import INFLOW_CONFIG
_INFLOW_DISCOVERY_KEY = INFLOW_CONFIG["discovery"]["task_key"]
```

(If `INFLOW_CONFIG` is already imported in this file, reuse — do not duplicate import.)

2. In `_run_unified`, at function entry after `logger` is available, when `debug`:

```python
if debug and (task.get("task_key") or "").strip() == _INFLOW_DISCOVERY_KEY:
    logger.set_debug_flag(True)
```

3. Replace the block at lines ~227–240 (no entities / claimed entities) **only when** `debug and task_key == inflow_discovery`:

   - No entities: `logger.debug_index(func="dispatcher._run_unified", index=1, total=1, identifier=f"{entity_type}/{input_state}", outcome="no entities claimed")` then `return s`.
   - Has entities: `logger.debug_index(..., outcome=f"claimed {len(entities)} entity/entities")` plus `logger.debug_detail(f"batch_id={bid} batch_call_mode={batch_call_mode} dispatch batch_size={limit!r}")`.

   For **other** `task_key`s, keep existing `logger.info("[DEBUG] _run_unified[...]")` lines unchanged (grandfather).

4. In `_run_task`, replace the two `[DEBUG]` lines (~331–336) **only when** `debug and (task.get("task_key") or "").strip() == _INFLOW_DISCOVERY_KEY`:

   - Start: `logger.debug_index(func="dispatcher._run_task", index=1, total=1, identifier=task.get("task_key") or "", outcome="running")` and `logger.debug_detail(f"batch_size={task.get('batch_size')} batch_id={bid}")`.
   - End: `logger.debug_detail(f"runner returned summary={summary}")` — do **not** duplicate as a second header; summary is working detail per §1.5.1.

   Other tasks: keep `[DEBUG]` `_run_task` lines.

5. Do **not** add `set_debug_flag(False)` at exit — flag is per-call on shared module logger; `run_inflow_discovery_batch` sets its own flag from its `debug` parameter.

## Stage 3: Manual verification (build agent / Susan UAT)

**Done when:** Susan (or build agent with note in Linear) confirms spot-check for AC 4.

1. Run one `inflow_discovery` dispatch with `debug=False` (normal AUTO or manual without debug): grep log output — **no** lines matching `index \d+/\d+` from contract headers and **no** new ` | ` detail lines from this ticket's edits.
2. Run one `inflow_discovery` with `debug=True` and ≥2 stale terms: console shows term headers, vet block, row headers, batch summary detail.

(No new automated tests in AST-557 — parent forbids Betty log-string tests; optional manual note only.)

## Self-Assessment

**Scope:** `Single-Component` — Touches only `roster.run_inflow_discovery_batch` and narrow `dispatcher` branches gated on `inflow_discovery` + `debug`.

**Conf:** `high` — AST-554 helpers and §1.5.1 are on the line; loop structure and `do_task(debug=)` passthrough are straightforward.

**Risk:** `Medium` — Dispatcher is shared infrastructure, but edits are guarded by `task_key` and `debug`; wrong guard could affect other tasks or add noise when `debug=False`.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_PrefixedLogger` helpers; no duplicate truncation logic |
| §2.1 config | Reads `INFLOW_CONFIG["discovery"]` keys; no new magic numbers except inline 20-hit cap |
| §2.4 batch | Per-term and per-row indices match batch loops |
| §3.3 imports | `INFLOW_CONFIG` import at top of dispatcher if added |
| §3.5 naming | `func=` strings use `roster.*` / `dispatcher.*` prefixes |
| §1.5.1 | All contract emission gated on `debug=True`; grandfather other `[DEBUG]` |

No conflicts requiring `conf-!!-NONE`.

## Execution contract

- Stages **1 → 2 → 3** in order; one commit per stage on `dev-hedy`, then `git-store-code-commit` per **build-astral**.
- Blocking questions → parent **AST-538** with 🛑 format from **plan-astral**.

## Review (build stub)

**Built:** `origin/sub/AST-538/AST-557-inflow-discovery-representative-debug` @ `00da9ef3`.

**Stages delivered:**
- Stage 1: `run_inflow_discovery_batch` contract debug (per-term CSE, vet block, per-row ingest, `do_task(debug=)`) — `15a126b7`.
- Stage 2: `dispatcher._run_unified` / `_run_task` gated on `inflow_discovery` + `debug` — `00da9ef3`.

**Stage 3 (manual):** Susan UAT — `debug=False` no contract headers; `debug=True` with ≥2 stale terms shows term/vet/row trace. No Betty log-string tests per parent.
## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-538/AST-557-inflow-discovery-representative-debug` — `src/core/dispatcher.py`, `src/core/roster.py`, plan doc, test bible manifest.

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Stages 1–2 match the approved plan; scope stays dispatcher + roster for `inflow_discovery` only. |
| §1.5.1 / AST-538 | Per-term `index N/M` + ` \| ` hit lines; vet bundle via `debug_detail_block`; per-row ingest outcomes; batch summary detail; `do_task(..., debug=debug)`. |
| Dispatcher guards | `_INFLOW_DISCOVERY_KEY` gates contract emission; other tasks keep grandfather `[DEBUG]` lines. |
| `debug=False` | Contract helpers only run under `if debug` / `set_debug_flag(debug)`; no new contract paths when debug is off. |
| Layers / D2 | No new UI/data imports; existing WARNING/ERROR paths unchanged. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `roster.run_inflow_discovery_batch` — `if not all_hits` early return | When terms run but dedupe yields zero hits, vet is skipped with no contract header (plan Stage 1.4 allows skip). Optional UAT clarity: one `debug_index` with outcome `no deduped hits after CSE` before return. Not blocking. |
| **advisory** | `src/core/agent.py` (unchanged) | `vet_inflow_discovery` still uses legacy `do_task` debug paths, not contract headers — deferred per plan out-of-scope table. |

### Recommended actions

| Priority | Action |
|----------|--------|
| — | **resolve-astral:** none required (no fix-now). |
| Optional | Susan UAT Stage 3: confirm `debug=False` grep and multi-term `debug=True` trace per plan. |
| Optional | If empty-dedupe runs are common in UAT, add one debug header on the `not all_hits` path (discuss above). |

## Resolution (2026-06-02)

**Review:** Radia @ `fc291360` on `origin/sub/AST-538/AST-557-inflow-discovery-representative-debug` — **no fix-now** items.

**Changes vs review:** None required. Product @ `4be2af40` unchanged. Discuss item (optional `debug_index` on empty dedupe after CSE) deferred — plan Stage 1.4 already allows skipping vet without header; not blocking UAT.

**Verification:** Betty manifest (12 + 2 + 13 pytest) green on `dev-hedy` after attach. §9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-538-improve-quality-of-debug-logging`.

**UAT:** Susan Stage 3 — `debug=False` no contract headers; `debug=True` with ≥2 stale terms shows term/vet/row trace (parent AC 2/4).
