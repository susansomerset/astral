# AST-1775 — Ruth duplicate-review invoke + DUPLICATE map

**Linear:** [AST-1775](https://linear.app/astralcareermatch/issue/AST-1775/ruth-duplicate-review-invoke-duplicate-map-meteorite-state-check-unique)  
**Parent:** [AST-1762](https://linear.app/astralcareermatch/issue/AST-1762/meteorite-state-check-unique-before-landed) — Meteorite state CHECK_UNIQUE before LANDED  
**Publish ref:** `sub/AST-1762/AST-1775-ruth-duplicate-review-invoke-duplicate-map`

Owns Ruth invoke inside the check-unique peer paths for AST-1762: when `_review_duplicate_meteorite_hook` is called with SQL title+employer peers or null-field multi-LANDED peers, build full-content payloads, call `do_task` for `review_duplicate_meteorite`, and map `duplicate` → `DUPLICATE` (record LANDED peer id) / `not_duplicate` → `READY`. Does **not** re-edit stage prompts or registry (**AST-1773**), does **not** own SQL unique→READY or peer detection (**AST-1774**), and does **not** change `run_land_meteorite`.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` — **modified** — Ruth invoke + outcome map on SQL-match and null-field multi-peer paths only; does not own SQL unique→READY (#2) or config/catalog (#1).

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / explicit boundaries):**

- `src/utils/config.py`, `data/admin/agent_task.json`, `data/admin/dispatch_task.json` — **AST-1773** (already on epic line after sync)
- Peer detection, unique→`READY`, stage/scrape→`CHECK_UNIQUE` writers, dispatcher route — **AST-1774** (already on epic line; this ticket only fills the hook body)
- New `database.py` columns or `_UPDATE_METEORITE_ALLOWED` changes — not named in Scope
- `apply_paste` and any other direct `READY` writers
- Changing `run_land_meteorite` claim set (`READY` + `BOT_BLOCKED`) or `land_trigger_state`

**Depends on:** **AST-1773** symbols (`REVIEW_DUPLICATE_METEORITE_CONFIG`, `TASK_CONFIG["review_duplicate_meteorite"]`, `DUPLICATE` / `CHECK_UNIQUE` in `METEORITE_STATES`) and **AST-1774** hook call sites + stub signature `_review_duplicate_meteorite_hook(row, peers, *, batch_id, debug=False)`. After `sync-child.sh` with `--ftr AST-1762-meteorite-state-check-unique-before-landed`, if the stub or config symbols are missing on HEAD, **stop** and comment on AST-1775 (do not re-implement siblings).

**AC partition (this ticket):** Parent AC7 (null peers → Ruth with full content), AC8 (SQL peers → Ruth → `DUPLICATE`|`READY` with peer id recorded), AC9 (land gate unchanged — inspect only). Parent AC1–6, AC10 → N/A (siblings).

**Canon Scope (read at plan):**

- `patt.entity.batch-processing` — full (process only claimed rows under the runner’s `batch_id`; Ruth `do_task` rides the existing claim batch via `log_batch_id` / agent_data; do not mint a second claim)
- `stat.logging.info.entity` — full (row transitions `CHECK_UNIQUE` → `DUPLICATE` / `READY` use `_meteorite_state_info`)
- `stat.logging.debug` — full (do_task call/response + peer/payload detail stay `logger.debug`, ungated at call site)

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | Fill `_review_duplicate_meteorite_hook`: full-content live payload, `do_task` duplicate-review, outcome → `DUPLICATE`/`READY` (+ peer id on duplicate); import `REVIEW_DUPLICATE_METEORITE_CONFIG`; update module docstring peer-path sentence | core |

## Stage 1: Ruth invoke + DUPLICATE|READY map inside the hook

**Done when:** Calling `_review_duplicate_meteorite_hook` with a CHECK_UNIQUE subject and ≥1 LANDED peers runs `review_duplicate_meteorite` with full subject + peer content; `duplicate` writes `DUPLICATE` with peer id on the row and an entity state info line; `not_duplicate` writes `READY` with an entity state info line; do_task failure / invalid outcome / unvalidated peer id leave the row in `CHECK_UNIQUE` (no auto-terminal); `run_land_meteorite` still claims only `READY`/`BOT_BLOCKED`; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `src/core/meteorite.py` imports from `src.utils.config`, add `REVIEW_DUPLICATE_METEORITE_CONFIG` alongside the existing meteorite ingress imports.

2. Immediately above `_review_duplicate_meteorite_hook`, add a payload builder (same module — Scope allows only this file):

```python
def _review_duplicate_live_content(
    subject: Dict[str, Any], peers: List[Dict[str, Any]]
) -> str:
    """Full CHECK_UNIQUE + LANDED peer bodies for Ruth (AC7/AC8 — not title/employer equality)."""
    def _block(label: str, row: Dict[str, Any]) -> str:
        rid = row.get("id")
        title = _nonempty_strip(row.get("job_title"))
        employer = _nonempty_strip(row.get("employer_name"))
        link = _nonempty_strip(row.get("link"))
        body = row.get("content") if isinstance(row.get("content"), str) else ""
        return (
            f"{label}\n"
            f"id: {rid}\n"
            f"job_title: {title}\n"
            f"employer_name: {employer}\n"
            f"link: {link}\n"
            f"CONTENT:\n{body}"
        )

    parts = [_block("CHECK_UNIQUE:", subject)]
    for peer in peers:
        parts.append(_block(f"LANDED peer id={peer.get('id')}:", peer))
    return "\n\n".join(parts)
```

3. Replace the stub body of `_review_duplicate_meteorite_hook` (keep the same signature AST-1774 defined — callers already pass `row`, `peers`, `batch_id=`, `debug=`). New docstring:

```python
async def _review_duplicate_meteorite_hook(
    row: Dict[str, Any],
    peers: List[Dict[str, Any]],
    *,
    batch_id: str,
    debug: bool = False,
) -> None:
    """Ruth duplicate-review invoke + DUPLICATE|READY map (AST-1775).

    Called only from run_check_unique_meteorite peer paths (SQL or null multi-peer).
    """
```

4. Inside the hook, implement (binding order):

   a. **Guards:** `row_id = int(row["id"])`; `cid = str(row.get("candidate_id") or "").strip()`; if `not peers`, log debug and **return** leaving `CHECK_UNIQUE` (caller should not hit this; do not auto-`READY`).

   b. **Payload:** `live_content = _review_duplicate_live_content(row, peers)`.

   c. **do_task:** late-import `from src.core.agent import do_task` (same pattern as `_classify_stage_blob` / land enrich). Read `task_key = REVIEW_DUPLICATE_METEORITE_CONFIG["task_key"]` and `peer_key = REVIEW_DUPLICATE_METEORITE_CONFIG["peer_id_response_key"]`. Build:

   ```python
   task_ctx: Dict[str, Any] = {"astral_candidate_id": cid}
   do_index = f"{task_key}_{row_id}_{batch_id}"
   token = _hold_log_batch(batch_id)
   try:
       logger.debug(
           "Calling agent.do_task: [task_key=%s, index=%s, peer_ids=%s]",
           task_key, do_index, [p.get("id") for p in peers],
       )
       result = await do_task(
           task_key=task_key,
           live_content=live_content,
           index=do_index,
           ctx=task_ctx,
           debug=debug,
       )
       logger.debug("Response from agent.do_task: %s", result)
   finally:
       if token is not None:
           log_batch_id.reset(token)
   ```

   d. **do_task failure:** if `not result.get("success")`, `_warn_item(cid, f"review_duplicate_meteorite failed: {result.get('error') or 'do_task failed'}", "This row stays CHECK_UNIQUE for retry")` and **return** (leave `CHECK_UNIQUE`).

   e. **Parse outcome:** `parsed = result.get("parsed_response") if isinstance(result.get("parsed_response"), dict) else {}`; `outcome = (parsed.get("outcome") or "").strip() if isinstance(parsed.get("outcome"), str) else ""`. Allowed set = `set(REVIEW_DUPLICATE_METEORITE_CONFIG["outcomes"])` (`duplicate` / `not_duplicate`). If outcome not in that set, warn with `_warn_item` and **return** (leave `CHECK_UNIQUE`).

   f. **`not_duplicate`:** `update_meteorite(row_id, state="READY")`; `_meteorite_state_info(row_id, "READY", from_state="CHECK_UNIQUE")`; return.

   g. **`duplicate`:** read raw peer id from `parsed.get(peer_key)`; coerce to stripped string (`str(raw).strip()` if raw is not None else `""`). Build `allowed_peer_ids = {str(int(p["id"])) for p in peers if p.get("id") is not None}`. If peer id empty **or** not in `allowed_peer_ids`, warn (`invalid/missing peer_meteorite_id`) and **return** (leave `CHECK_UNIQUE` — never invent a peer). Otherwise:

   ```python
   update_meteorite(
       row_id,
       state="DUPLICATE",
       error=f"duplicate_of:{peer_id}",
   )
   _meteorite_state_info(row_id, "DUPLICATE", from_state="CHECK_UNIQUE")
   ```

5. Update the module docstring ingress sentence so peer paths are described: after unique hop → `READY`, peer Ruth path → `DUPLICATE` | `READY` (land remains `READY` → `LANDED`).

6. **Inspect only (no edit):** confirm `run_land_meteorite` still uses `land_states = ["READY", "BOT_BLOCKED"]` and does not claim `CHECK_UNIQUE` or `DUPLICATE`. Confirm `run_check_unique_meteorite` unique branch and peer call sites are unchanged (this stage only fills the hook body).

7. Compile: `python3 -m py_compile src/core/meteorite.py`.

⚠️ **Decision — peer id on `error`:** Scope forbids new data-layer columns. Persist Ruth’s validated LANDED peer id as `error=f"duplicate_of:{peer_id}"` on the `DUPLICATE` transition (allowed by `_UPDATE_METEORITE_ALLOWED`). Agent_data from `do_task` still holds the full response; the `error` string is the row-level handle for later cleanup / rescue epics. Do **not** overload `astral_job_id` / `classify_outcome` / `source_ref`.

⚠️ **Decision — failure stays CHECK_UNIQUE:** do_task miss, invalid outcome, or unvalidated peer id must not auto-`READY` or auto-`DUPLICATE` (parent AC7/AC8 fail conditions). Leaving `CHECK_UNIQUE` lets the hop retry on the next claim.

⚠️ **Decision — do not remint claim batch_id:** Pass the runner’s claim `batch_id` into `_hold_log_batch` / do_task index so Ruth agent_data joins the uniqueness hop audit trail (`patt.entity.batch-processing`). Do not call `claim_meteorite_batch` from the hook.

⚠️ **Decision — live_content shape:** Label blocks `CHECK_UNIQUE:` then `LANDED peer id=<id>:` with `job_title` / `employer_name` / `link` / full `CONTENT` — matches catalog prompts (“full content”, not title/employer string equality). Peer list is whatever AST-1774 already selected (SQL or null multi-peer); do not re-filter.

**AC check after this stage:** Parent AC7, AC8, AC9.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1775
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `sub/AST-1762/AST-1775-ruth-duplicate-review-invoke-duplicate-map` @ `72e3501591d98df2783230f34c011b5691f7c7cf`

## Canon scores

patt.entity.batch-processing | A |
stat.logging.info.entity | A |
stat.logging.debug | A |

## Traceability

AC7 → Stage 1 steps 2–4 (`_review_duplicate_live_content` CHECK_UNIQUE + LANDED peer blocks with full `CONTENT`; hook invoked from AST-1774 null multi-peer path unchanged); AC8 → Stage 1 steps 4c–g (`do_task` `review_duplicate_meteorite`; validated `peer_meteorite_id` → `DUPLICATE` + `error=duplicate_of:<id>`; `not_duplicate` → `READY`; failure/invalid outcome/unvalidated peer leaves `CHECK_UNIQUE`); AC9 → Stage 1 step 6 inspect-only (`run_land_meteorite` still `READY`/`BOT_BLOCKED` only). Parent AC1–6, AC10 → N/A (AST-1773 registry/catalog; AST-1774 SQL/unique→READY/dispatcher per plan **AC partition**).

## Findings

### acceptable — No `## Self-assessment` block
- **Severity:** acceptable
- **Location:** Plan structure — Estimate confirm only
- **Finding:** Estimate confirm present; no conf/risk paragraph like some sibling plans.
- **Recommendation:** Optional polish; stages carry done-when gates and four explicit ⚠️ decisions.

### acceptable — Peer id persisted on `error`
- **Severity:** acceptable
- **Location:** Stage 1 step 4g / ⚠️ Decision — peer id on `error`
- **Finding:** AC8 asks to record LANDED peer id; plan stores `duplicate_of:{peer_id}` in `error` because Scope forbids new columns — `error` is in `_UPDATE_METEORITE_ALLOWED`.
- **Recommendation:** Accept for this epic; rescue/cleanup epics can key off the prefix if needed.

context_tokens≈52000

## Review

- **Commit:** `edf50a4c8b7e3edf57bfd1264eeee9346896ecf3`
- **Publish ref:** `sub/AST-1762/AST-1775-ruth-duplicate-review-invoke-duplicate-map`
