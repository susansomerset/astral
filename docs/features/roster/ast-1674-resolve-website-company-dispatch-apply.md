# AST-1674 — resolve_website company dispatch apply

**Linear:** https://linear.app/astralcareermatch/issue/AST-1674  
**Parent:** [AST-1670](https://linear.app/astralcareermatch/issue/AST-1670) — Split inflow website resolve into CSE fetch + find_company_website dispatch  
**Publish ref:** `sub/AST-1670/AST-1674-resolve-website-company-dispatch-apply`

After AST-1672 (SSOT) and AST-1673 (CSE persist → `WEBSITE_REVIEW`): claimable company SA `resolve_website` on `WEBSITE_REVIEW` loads persisted CSE hits, rebuilds the existing `0|slug|` + `1|title|url|snippet` live_content shape, runs `do_task` as hop identity `find_company_website` (via `TASK_CONFIG["resolve_website"]["agent_task"]`), and lands `WEBSITE_FOUND` (URL written) or `NO_WEBSITE`. Does not re-own CSE search, registry SSOT, or claim/eligibility filters.

**Canon Scope (frozen at plan):** `patt.entity.batch-processing`, `patt.entity.batch-criteria`, `stat.logging.info.entity`, `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`  
**Corpus note (plan-time):** patterns read in full; logging statutes read for placement (entity id-pipe / ContextVar debug / warn-who-why / error+traceback). No claim-criteria or dispatcher completion-line changes in this ticket.

## Explicit scope gate

Ticket **## Scope** names: `src/core/roster.py`, `src/core/consult.py`. Every Files Changed row and stage step stays inside those two files. No `src/utils/config.py` (AST-1672). No CSE search / discovery land / claim SQL / `require_empty_website` (AST-1673). No Somerset `dispatch_tasks` inserts (parent ops gate).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | New `resolve_website_company` apply runner; `run_company_task` routes `WEBSITE_REVIEW` → it | core |
| `src/core/consult.py` | Explicit `resolve_website` company branch (AI hop, not fallthrough-only) | core |

## Stage 1: `resolve_website_company` apply runner

**Done when:** A company in `WEBSITE_REVIEW` with a non-empty `company_data[hit_list_data_key]` list can run through load → live_content → `do_task(find_company_website)` → `update_company(company_website=…)` + `WEBSITE_FOUND`, or decline/empty website → `NO_WEBSITE`, with no CSE call and no edits outside this function’s write path.

1. In `src/core/roster.py`, add `async def resolve_website_company(short_name, entity, ctx=None, debug=False) -> Dict[str, Any]` immediately **after** `resolve_company_website` (CSE fetch hop) and **before** `run_inflow_discovery_batch`. Docstring: `resolve_website` AI apply — load persisted CSE hits → `find_company_website` → `WEBSITE_FOUND` | `NO_WEBSITE`.
2. Resolve config locals (do not invent new keys):
   - `hit_key = INFLOW_CONFIG["resolve"]["hit_list_data_key"]` (`inflow_resolve_website_hits`)
   - `sa_cfg = TASK_CONFIG["resolve_website"]`
   - `agent_task_key = sa_cfg["agent_task"]` → must be `"find_company_website"`
   - `pass_state = sa_cfg["pass_state"]` → `"WEBSITE_FOUND"`
   - `fail_state = sa_cfg["fail_state"]` → `"NO_WEBSITE"`
3. `log = logger; log.set_debug_flag(debug)` (same debug helper pattern as `resolve_company_website` / `vet_inflow_discovery_company`).
4. **Load hits** from `(entity.get("company_data") or {}).get(hit_key)`. Accept only a non-empty `list`. If missing, not a list, or empty:
   - `logger.warning("[%s] resolve_website_company: missing or empty %s", short_name, hit_key)` (`stat.logging.warning`)
   - Return `{"success": False, "state": None, "error": f"missing or empty {hit_key}"}` — **do not** transition state (leaves `WEBSITE_REVIEW` for retry / ops; AI decline is the only soft path to `NO_WEBSITE`).
5. **Build live_content** exactly as the pre-AST-1673 inline block (slug row + 1-based hits):

```python
lines = [f"0|{short_name}|"]
for i, hit in enumerate(hits):
    snip = (hit.get("snippet") or "")[:500]
    lines.append(f"{i + 1}|{hit.get('title', '')}|{hit.get('url', '')}|{snip}")
live_content = "\n".join(lines)
```

   Hit dict keys are the CSE shape persisted by AST-1673 (`title`, `url`, `snippet`, …). Do not re-query CSE.

6. Debug (ContextVar-gated via existing helpers — `stat.logging.debug`): `debug_index` with `func="roster.resolve_website_company"`, `outcome=f"vet {agent_task_key} {len(hits)} hit(s)"`, then `debug_detail_block(live_content)`.
7. Call:

```python
api_result = await do_task(
    task_key=agent_task_key,  # find_company_website — agent identity, not SA key
    live_content=live_content,
    index=short_name,
    ctx=ctx,
    debug=debug,
)
```

⚠️ **Decision:** Pass `task_key=TASK_CONFIG["resolve_website"]["agent_task"]` (`find_company_website`), not `"resolve_website"`. Prompts / `agent_task` rows live under `find_company_website`; the SA key is dispatch/claim identity only (parent AC 6 + AST-1672 SSOT). Matches the deleted pre-split `do_task(cfg["ai_task_key"])` call.

8. If `not api_result.get("success")`: debug index `outcome="find_company_website task failed"` + detail `error=…`; return `{"success": False, "state": None, "error": api_result.get("error") or "task failed"}` — **no** state transition (hard task failure stays claimable on `WEBSITE_REVIEW`).
9. Parse: `parsed = api_result.get("parsed_response") or {}`; `website = (parsed.get("website") or "").strip()`.
10. **Decline / empty website:** if `not parsed.get("task_success") or not website`:
    - Debug outcome `NO_WEBSITE — task_success false or empty website`
    - `transition_company_state(short_name, fail_state)`
    - Always-on entity info (`stat.logging.info.entity`):

```python
logger.info(
    "%s | company %s: %s (batch: %s)",
    short_name,
    "resolve_website",
    f"-> {fail_state}",
    (entity.get("batch_id") or "-"),
)
```

    - Return `{"success": True, "state": fail_state, "error": None}`.
11. **Success:** `update_company(short_name, company_website=website)`; `transition_company_state(short_name, pass_state)`; entity info line with `f"website={website!r} -> {pass_state}"`; debug outcome `recorded WEBSITE_FOUND website=…`; return `{"success": True, "state": pass_state, "error": None}`.
12. Do **not** clear `hit_list_data_key` after apply (out of scope). Do **not** call `search_google_cse`. Do **not** import new modules — `do_task`, `update_company`, `transition_company_state`, `INFLOW_CONFIG`, `TASK_CONFIG`, `logger` are already imported / available in `roster.py`.

⚠️ **Decision:** Function name `resolve_website_company` (SA key + entity), parallel to `vet_inflow_discovery_company`. Keep `resolve_company_website` as the CSE-only fetch name from AST-1673 — do not rename it.

## Stage 2: `run_company_task` + consult routing

**Done when:** Dispatch with `dispatch_task_key=resolve_website` and `input_state=WEBSITE_REVIEW` reaches `resolve_website_company` from both `run_company_task` and `consult.run_consult_task`, and rollup treats `WEBSITE_FOUND` / `NO_WEBSITE` as completed terminals (`total_passed`) while hard errors stay `total_errors`.

1. In `run_company_task`, add an `elif input_state == "WEBSITE_REVIEW":` block **immediately after** the `DISCOVERED` block (before the `WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` branch):
   - `tk = (dispatch_task_key or "").strip()`
   - If `tk != "resolve_website"`: `logger.warning("run_company_task: WEBSITE_REVIEW expects resolve_website, got %s", tk)` and return `{**zero, "total_errors": 1}`
   - Else: `r = await resolve_website_company(short_name, entity, ctx=ctx, debug=debug)`
   - If `r.get("error")`: return `{**zero, "total_errors": 1}`
   - `terminal_ok = (TASK_CONFIG["resolve_website"]["pass_state"], TASK_CONFIG["resolve_website"]["fail_state"])`
   - If `r.get("state") in terminal_ok`: `{**zero, "total_passed": 1}`; else `{**zero, "total_failed": 1}`
2. Ensure `TASK_CONFIG` is already imported in `roster.py` (it is via the existing config import block). If a local import is needed inside the branch only, mirror the `DISCOVERED` block’s use of module-level `INFLOW_CONFIG` / `TASK_CONFIG` — prefer module-level.
3. In `src/core/consult.py` `run_consult_task` company section, **after** the `INFLOW_CONFIG["resolve"]["task_key"]` (`inflow_resolve_website`) branch and **before** `prefilter` / `vet_inflow_discovery`, add an explicit AI-hop branch:

```python
if task_key == "resolve_website":
    from src.utils.config import TASK_CONFIG
    terminal_ok = (
        TASK_CONFIG["resolve_website"]["pass_state"],
        TASK_CONFIG["resolve_website"]["fail_state"],
    )
    passed = failed = errors = 0
    for entity in entities:
        r = await roster.resolve_website_company(
            entity.get("short_name", ""), entity, ctx=ctx, debug=debug,
        )
        if r.get("error"):
            errors += 1
        elif r.get("state") in terminal_ok:
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

⚠️ **Decision:** Explicit consult loop (same shape as the CSE fetch branch) rather than relying on the `entities[0]` fallthrough to `run_company_task`. Ticket requires both paths; the explicit branch keeps multi-entity batches correct if dispatcher ever hands more than one row.

4. Do **not** add Somerset / `dispatch_tasks` rows. Do **not** change dispatcher claim filters or database eligibility helpers.

## Estimate

Confirm Chuckles estimate: 2 — agree

Lift of the deleted AI block from pre-AST-1673 `resolve_company_website` plus two routing branches; SSOT and hit persist already on tip from AST-1672 / AST-1673.
