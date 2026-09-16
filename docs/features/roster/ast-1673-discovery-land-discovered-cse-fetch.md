# AST-1673 — Discovery land DISCOVERED + CSE fetch hop

**Linear:** https://linear.app/astralcareermatch/issue/AST-1673  
**Parent:** [AST-1670](https://linear.app/astralcareermatch/issue/AST-1670) — Split inflow website resolve into CSE fetch + find_company_website dispatch  
**Publish ref:** `sub/AST-1670/AST-1673-discovery-land-discovered-cse-fetch`

After AST-1672 (registry SSOT on tip): discovery records land `DISCOVERED`; `inflow_resolve_website` becomes a CSE-only fetch hop that persists hits and waits on `WEBSITE_REVIEW` (or `NO_WEBSITE` on zero hits) with no `do_task`; claim/eligibility empty-website filtering applies only to that hop on `DISCOVERED`. Does not implement `resolve_website` AI apply (AST-1674).

**Canon Scope (frozen at plan):** `patt.entity.batch-processing`, `patt.entity.batch-criteria`, `stat.logging.info.entity`, `stat.logging.info.dispatcher`, `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`  
**Corpus note (plan-time):** patterns read in full; logging statutes read for placement (entity id-pipe / dispatcher candidate-pipe / warn-who-why / debug ContextVar / error+traceback). No new dispatcher completion lines planned — only claim-criteria tweak.

## Explicit scope gate

Ticket **## Scope** names: `src/core/roster.py`, `src/core/consult.py`, `src/core/dispatcher.py`, `src/data/database.py`. Every Files Changed row and stage step stays inside those four files. No `src/utils/config.py` edits (AST-1672). No `resolve_website` apply runner / AI `do_task(find_company_website)` (AST-1674). No Somerset `dispatch_tasks` inserts (parent ops gate).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | Discovery land `DISCOVERED`; CSE-only `resolve_company_website`; `run_company_task` routes vet/resolve off `DISCOVERED` | core |
| `src/core/consult.py` | Explicit `inflow_resolve_website` fetch-hop branch (sibling to `fetch_website`) | core |
| `src/core/dispatcher.py` | `require_empty_website` only when task is `inflow_resolve_website` **and** trigger is `DISCOVERED` | core |
| `src/data/database.py` | Resolve (+ vet) eligibility helpers retarget `NEW` → `DISCOVERED` | data |

## Stage 1: Discovery land DISCOVERED

**Done when:** `record_inflow_discovery_hit` inserts companies with `state` equal to `INFLOW_CONFIG["discovery"]["land_state"]` (`DISCOVERED` per AST-1672 SSOT), not the literal `"NEW"`. Success messages say `DISCOVERED`.

1. In `src/core/roster.py` `record_inflow_discovery_hit`, change `save_company(..., state="NEW", ...)` to `state=INFLOW_CONFIG["discovery"]["land_state"]` (import already present via module-level `INFLOW_CONFIG`).
2. Update the function docstring: "Record one CSE hit as a NEW company…" → "…as a company in discovery `land_state` (DISCOVERED)…".
3. Update the two success return strings from `recorded NEW slug=…` to `recorded DISCOVERED slug=…` (keep term/`slug` formatting unchanged).
4. In `run_inflow_discovery_batch` docstring, change "record deduped hits as NEW" → "record deduped hits as DISCOVERED (`land_state`)".

⚠️ **Decision:** Read land state from `INFLOW_CONFIG["discovery"]["land_state"]` rather than hard-coding `"DISCOVERED"`, so the write stays coupled to AST-1672 SSOT.

## Stage 2: CSE-only `resolve_company_website` + `run_company_task` DISCOVERED routing

**Done when:** `resolve_company_website` has no `do_task(` call; ≥1 CSE hit persists under `hit_list_data_key` and transitions to `WEBSITE_REVIEW`; zero hits → `NO_WEBSITE`; `run_company_task` routes vet vs resolve on `DISCOVERED` by `dispatch_task_key` and no longer routes resolve (or vet) off `NEW`.

1. Rewrite `resolve_company_website` docstring to: CSE-only fetch hop for `inflow_resolve_website` → persist hits → `WEBSITE_REVIEW` | `NO_WEBSITE`; never calls `do_task`.
2. Keep the early skip when `company_website` is already set (defensive; claim filter should exclude these): return `{"success": True, "state": "WEBSITE_FOUND", "error": None}` without CSE — same as today.
3. Keep CSE search block unchanged (`query = f"{name} official website"`, `max_results` / `date_restrict_days` from `INFLOW_CONFIG["resolve"]`, debug hit dump capped at 20). On `(RuntimeError, ValueError)`: `logger.warning("[%s] resolve_company_website: CSE failed: %s", …)` and return `{"success": False, "state": None, "error": str(exc)}` — no state transition.
4. **Zero hits:** `transition_company_state(short_name, cfg["fail_state"])` (`NO_WEBSITE`); return success with that state. Do **not** call `do_task` / `find_company_website`.
5. **≥1 hit:**  
   a. `save_company_data(short_name, {cfg["hit_list_data_key"]: hits})` where `hits` is the list of CSE hit dicts returned by `search_google_cse` (keys as today: `title`, `url`, `snippet`, etc. — JSON-serializable as stored).  
   b. `transition_company_state(short_name, cfg["pass_state"])` (`WEBSITE_REVIEW`).  
   c. Emit one always-on entity info line (`stat.logging.info.entity`) after the persist + transition — not gated on `debug`, no CSE hit dump on this line:

```python
logger.info(
    "%s | company %s: %s (batch: %s)",
    short_name,
    "inflow_resolve_website",
    f"{len(hits)} hits -> {cfg['pass_state']}",
    (entity.get("batch_id") or "-"),
)
```

   d. Return `{"success": True, "state": cfg["pass_state"], "error": None}`.  
   e. **Delete** the entire live_content / `do_task(cfg["ai_task_key"])` / parse-website / `update_company` / `WEBSITE_FOUND` block (lines that currently follow the zero-hit branch through end of function).
6. Debug path after ≥1 hit: `debug_index` outcome must **not** reference `cfg["ai_task_key"]` (key removed by AST-1672). Use e.g. `outcome=f"persist {len(hits)} CSE hit(s) -> {cfg['pass_state']}"` and optionally `debug_detail` the hit count / first few URLs (ContextVar-gated via existing debug helpers). Keep CSE hit dumps on debug only — not on the entity info line in step 5c.
7. In `run_company_task`, **replace** the `if input_state == "NEW":` inflow block with `if input_state == "DISCOVERED":` that keeps the same `dispatch_task_key` branch structure:
   - `tk == INFLOW_CONFIG["vet"]["task_key"]` → `vet_inflow_discovery_company(...)`
   - `tk == INFLOW_CONFIG["resolve"]["task_key"]` → `resolve_company_website(...)`
   - else → `logger.warning` naming both task keys and return `total_errors: 1`
8. Update `terminal_ok` for that block to:

```python
terminal_ok = (
    INFLOW_CONFIG["vet"]["pass_state"],
    INFLOW_CONFIG["vet"]["fail_state"],
    INFLOW_CONFIG["resolve"]["pass_state"],  # WEBSITE_REVIEW
    INFLOW_CONFIG["resolve"]["fail_state"],  # NO_WEBSITE
)
```

   Treat `r.get("state") in terminal_ok` as `total_passed: 1`; otherwise `total_failed: 1` (same control flow as today). CSE hard-fail (`error` set) stays `total_errors: 1`.
9. **Do not** leave a `NEW` branch that still calls resolve or vet. If `input_state == "NEW"` is reached with an inflow task key, fall through to the existing unhandled-state warning at the bottom of `run_company_task` (or add an explicit one-line warning that inflow no longer runs on `NEW`) — do not invent a new recovery path for legacy `NEW` rows.

⚠️ **Decision:** Persist raw CSE hit dicts under `hit_list_data_key`. AST-1674 owns rebuilding the `0|slug|` + `1|title|url|snippet` live_content shape for `find_company_website`. Do not write live_content strings into company_data here.

⚠️ **Decision:** Removing `do_task` from this hop will leave `ai_task_key` references gone (already deleted from config). Import of `do_task` at module top stays — still used by vet / prefilter / other roster paths.

## Stage 3: Consult fetch-hop route + claim / eligibility cutover

**Done when:** `run_consult_task` routes `inflow_resolve_website` like `fetch_website` (explicit branch, not silent fallthrough); dispatcher applies `require_empty_website` only for that task on `DISCOVERED`; database resolve Avail counts `DISCOVERED` + empty website (still excluding discovery-blurb rows); vet Avail counts `DISCOVERED` + blurb so discovery land does not orphan vet.

1. In `src/core/consult.py` `run_consult_task` company section, **after** the `fetch_website` / `fetch_job_pages` branches (and before or after `vet_inflow_discovery` — either is fine), add:

```python
if task_key == INFLOW_CONFIG["resolve"]["task_key"]:  # inflow_resolve_website
    # Align with run_company_task terminal_ok: zero-hit NO_WEBSITE is a completed
    # terminal fetch outcome (pass count), not a batch failure.
    resolve_terminal_ok = (
        INFLOW_CONFIG["resolve"]["pass_state"],   # WEBSITE_REVIEW
        INFLOW_CONFIG["resolve"]["fail_state"],   # NO_WEBSITE
        "WEBSITE_FOUND",  # defensive early skip when website already set
    )
    passed = failed = errors = 0
    for entity in entities:
        r = await roster.resolve_company_website(
            entity.get("short_name", ""), entity, ctx=ctx, debug=debug,
        )
        if r.get("error"):
            errors += 1
        elif r.get("state") in resolve_terminal_ok:
            passed += 1
        else:
            failed += 1
    total = len(entities)
    return {
        "total_processed": total,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }
```

   Import `INFLOW_CONFIG` at the top of that block if not already imported in-function (mirror how discovery uses it later in the same function).

⚠️ **Decision:** Per-entity loop matches `batch_call_mode=0` warm_then_gather (dispatcher already passes `[e]`). Same function as `run_company_task` calls — no separate batch helper required in Files Changed.

⚠️ **Decision (Joan fix-now):** Consult rollup must match Stage 2 `terminal_ok` — `fail_state` (`NO_WEBSITE`) increments `passed`, not `failed`. Parent AC5 is a terminal fetch outcome; dispatch fail counts are reserved for CSE hard-errors (`error` set).

2. In `src/core/dispatcher.py` company claim path, change:

```python
require_empty_website=(task.get("task_key") == resolve_key),
```

to:

```python
require_empty_website=(
    task.get("task_key") == resolve_key
    and (input_state or "").strip()
    == INFLOW_CONFIG["resolve"]["dispatch_trigger_state"]  # DISCOVERED
),
```

   Keep `resolve_key = INFLOW_CONFIG["resolve"]["task_key"]` as today. This satisfies AC6: empty-website filter is never applied when claiming `NEW` (or any non-`DISCOVERED` trigger).

3. In `src/data/database.py` `count_company_new_without_website`:
   - Change docstring to say unclaimed **DISCOVERED** companies with empty `company_website` for `inflow_resolve_website` (still excludes rows that carry `inflow_discovery_blurb` — AST-776 partition vs vet).
   - Change SQL `state = 'NEW'` → `state = 'DISCOVERED'` (literal matching `INFLOW_CONFIG["resolve"]["dispatch_trigger_state"]`; do not import config into the SQL string builder if the file already uses literals for these helpers — keep the same style as the existing `'NEW'` literal, just retarget).
   - **Rename** the function to `count_company_discovered_without_website` and update the single caller in `count_eligible_for_dispatch_task` (`task_key == INFLOW_CONFIG["resolve"]["task_key"]` branch). Leave a one-line comment at the old name site is unnecessary — update the call site only; do not keep a deprecated alias.

4. In `src/data/database.py` `count_company_new_pending_inflow_vet`:
   - Change docstring to **DISCOVERED** + discovery blurb pending `vet_inflow_discovery`.
   - Change SQL `state = 'NEW'` → `state = 'DISCOVERED'`.
   - **Rename** to `count_company_discovered_pending_inflow_vet` and update the `count_eligible_for_dispatch_task` vet branch caller.

⚠️ **Decision:** Vet eligibility retarget is required so Stage 1 discovery land does not leave vet Avail stuck at 0 on `NEW`. Ticket Scope names resolve helpers explicitly; vet helper is the same NEW→DISCOVERED cutover kind and is in the same file / same `count_eligible` switch — include it. Do **not** add a blurb filter to `set_company_batch` claim SQL (not in Scope; Avail helpers keep the AST-776 partition).

5. Confirm `set_company_batch` / `claim_company_batch` `require_empty_website` SQL predicate is unchanged (`company_website IS NULL OR TRIM = ''`) — only the dispatcher gate that sets the flag changes. No other callers of `require_empty_website=True` should exist outside dispatcher resolve; if a stray caller appears during build, stop and comment on AST-1670.

## Out of scope (do not touch)

- `src/utils/config.py` — **AST-1672** (already on tip)
- `resolve_website` apply / live_content rebuild / `do_task(find_company_website)` — **AST-1674**
- Somerset / candidate `dispatch_tasks` row inserts — parent ops gate
- Inventing `NEW` → … recovery for legacy rows

## Execution contract

- Stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1670/AST-1673-discovery-land-discovered-cse-fetch`.
- Do not add files outside the Files Changed table.
- If `INFLOW_CONFIG["resolve"]` still has `ai_task_key` or lacks `hit_list_data_key` / `pass_state` on the build tip — stop; re-sync with AST-1672 tip (dependency). Do not re-add config keys here.
- Ambiguity / drift → comment on **AST-1670** with the Stage blocked template.

## Acceptance mapping

| AC | Plan |
|----|------|
| 3 — no `do_task` in CSE fetch runner | Stage 2 steps 1–5 |
| 4 — ≥1 hit → `WEBSITE_REVIEW` + non-empty hit list in company_data | Stage 2 step 5 |
| 5 — zero hits → `NO_WEBSITE`, no AI hop | Stage 2 step 4 |
| 6 — `require_empty_website` not on `NEW`; only resolve/`DISCOVERED` | Stage 3 steps 2–3 |
| Parent AC1 land `DISCOVERED` (roster write) | Stage 1 |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

Revision 1 — 2026-09-16  
Driven by: Joan `[plan-rubric]` REVISE — fix-now consult `NO_WEBSITE` rollup vs `terminal_ok`; discuss entity info on persist/transition  
Changes:
- Stage 3 step 1: consult branch counts `pass_state`, `fail_state`, and defensive `WEBSITE_FOUND` as `passed` (shared `resolve_terminal_ok`); CSE `error` → `errors` only.
- Stage 2 step 5c: add `stat.logging.info.entity` id-pipe line on successful hit persist → `WEBSITE_REVIEW` (hit count + target state + batch); CSE dumps stay debug-only.

## Joan validate

[plan-rubric]
**Ticket:** AST-1673
**Overall:** REVISE
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1670/AST-1673-discovery-land-discovered-cse-fetch` @ `8e0365a3472bd862068ff36c330ac08593fc0ed7`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| stat.logging.info.entity | C | 1 | Stage 2 step 5 persist/transition has no id-pipe `logger.info` on the new primary success path |
| stat.logging.info.dispatcher | X | | no dispatch completion-line changes; claim gate only |
| stat.logging.debug | B | | continues existing roster `debug_index`/`debug_detail` helpers (unconverted file) |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Traceability

3→S2.1–5 (delete `do_task` block) | 4→S2.5a–b (`save_company_data` + `WEBSITE_REVIEW`) | 5→S2.4 (`fail_state`/`NO_WEBSITE`, no AI) | 6→S3.2–3 (dispatcher + DB eligibility) | parent AC1→S1 (`land_state` write); parent AC2/6/7–9→N/A (AST-1672 config / AST-1674 apply / ops gate)

## Findings

### fix-now

- **Severity:** fix-now
- **Location:** Stage 3 step 1 (`run_consult_task` `inflow_resolve_website` branch)
- **Finding:** Proposed rollup counts `NO_WEBSITE` (`fail_state`) as `failed += 1`, but Stage 2 step 8 `run_company_task` `terminal_ok` treats `INFLOW_CONFIG["resolve"]["fail_state"]` as a completed pass (`total_passed: 1`). Dispatcher always calls `run_consult_task` (not `run_company_task` directly), so zero-hit companies would surface as dispatch **fail** counts despite `success: True` — contradicting parent AC5 intent (terminal fetch outcome, not batch failure).
- **Recommendation:** Align consult counting with `terminal_ok`: treat `pass_state`, `fail_state`, and defensive `WEBSITE_FOUND` early-skip as `passed` (or share one `terminal_ok` tuple in both paths). Remove the comment that zero-hit is a “failed outcome for summary counts.”

### discuss

- **Severity:** discuss
- **Location:** Stage 2 step 5
- **Finding:** `stat.logging.info.entity` — persist + `WEBSITE_REVIEW` transition is new expected progress with no planned id-pipe info line (`<id> | company <event>: <detail> (batch: …)`). Parent Architectural definition cites this statute for fetch outcomes.
- **Recommendation:** Add one entity info line on successful persist/transition (hit count + target state); keep CSE hit dumps on debug only.

### acceptable

- **Severity:** acceptable
- **Location:** Stage 3 steps 3–4 (vet eligibility rename)
- **Finding:** Vet `count_company_*` retarget is slightly beyond the ticket Scope sentence (resolve helpers only) but necessary so Stage 1 `DISCOVERED` land does not orphan vet Avail.
- **Recommendation:** Keep as planned; same-file NEW→DISCOVERED cutover is coherent.

- **Severity:** acceptable
- **Location:** Dependency / tip
- **Finding:** AST-1672 SSOT is ancestor of this publish ref (`DISCOVERED`, `land_state`, `hit_list_data_key`, no `ai_task_key`).
- **Recommendation:** None — dependency satisfied.

context_tokens≈58000

## Joan validate (round 2)

[plan-rubric]
**Ticket:** AST-1673
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1670/AST-1673-discovery-land-discovered-cse-fetch` @ `063072d84c3c3170ccc71ffccb164b8b07e9cc70`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.info.dispatcher | X | | no dispatch completion-line changes; claim gate only |
| stat.logging.debug | B | | continues existing roster `debug_index`/`debug_detail` helpers (unconverted file) |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Traceability

3→S2.1–5e (delete `do_task` block) | 4→S2.5a–c (`save_company_data` + transition + entity info) | 5→S2.4 (`fail_state`/`NO_WEBSITE`, no AI) | 6→S3.2–3 (dispatcher + DB eligibility) | parent AC1→S1 (`land_state` write); parent AC2/6/7–9→N/A (AST-1672 config / AST-1674 apply / ops gate)

## Findings

### acceptable

- **Severity:** acceptable
- **Location:** Plan Discuss round 1 → Revision 1
- **Finding:** Prior fix-now (consult `NO_WEBSITE` rollup vs `terminal_ok`) and discuss (entity info on persist) are addressed in Stage 3 step 1 `resolve_terminal_ok` and Stage 2 step 5c id-pipe `logger.info` (matches statute Do example shape).
- **Recommendation:** None — proceed to build.

- **Severity:** acceptable
- **Location:** Stage 2 step 4 vs step 5c
- **Finding:** Zero-hit `NO_WEBSITE` path has no planned entity info line; ≥1-hit path does. Asymmetric but consistent with warning-on-CSE-failure / debug-on-detail pattern; not blocking.
- **Recommendation:** Optional at build: one info line on zero-hit terminal if operators want symmetric grep; warning/debug may suffice.

- **Severity:** acceptable
- **Location:** Stage 3 steps 3–4
- **Finding:** Vet eligibility retarget remains slightly beyond Scope sentence but required for `DISCOVERED` land coherence.
- **Recommendation:** Keep as planned.

context_tokens≈65000

## Build

**Publish tip:** `origin/sub/AST-1670/AST-1673-discovery-land-discovered-cse-fetch` @ `c1a6bca0`

| Stage | Commit |
|-------|--------|
| 1 — discovery land DISCOVERED | `423cfd05` |
| 2 — CSE-only resolve + DISCOVERED routing | `806b9e90` |
| 3 — consult route + claim eligibility | `c1a6bca0` |

## Review

(pending Radia)
