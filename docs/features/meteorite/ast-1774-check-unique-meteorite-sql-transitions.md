# AST-1774 — check_unique_meteorite SQL + transitions

**Linear:** [AST-1774](https://linear.app/astralcareermatch/issue/AST-1774/check-unique-meteorite-sql-transitions-meteorite-state-check-unique)  
**Parent:** [AST-1762](https://linear.app/astralcareermatch/issue/AST-1762/meteorite-state-check-unique-before-landed) — Meteorite state CHECK_UNIQUE before LANDED  
**Publish ref:** `sub/AST-1762/AST-1774-check-unique-meteorite-sql-transitions`

Owns the uniqueness-gate **runners** for AST-1762: retarget `run_stage_meteorite` / `run_scrape_meteorite` landable success to `CHECK_UNIQUE` (leave `apply_paste` and other READY writers untouched), implement `run_check_unique_meteorite` (claim → SQL title+employer match among same-candidate `LANDED` → unique promote to `READY`; detect null-field multi-peer case; delegate Ruth via a hook stub for **AST-1775**), and register the hop on the meteorite ingress dispatcher route. Does **not** own Ruth `do_task` / outcome map (**AST-1775**), config/catalog (**AST-1773**), or `apply_paste`.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` — **modified** `run_stage_meteorite` / `run_scrape_meteorite` landable success → `CHECK_UNIQUE` (not `apply_paste`).
- `src/core/meteorite.py` — **new** `run_check_unique_meteorite` — claim batch; SQL match by title + `employer_name` among same-candidate `LANDED`; no peers → `READY`; detect null-field multi-peer case and delegate Ruth hook; unique SQL path → `READY`.
- `src/core/dispatcher.py` — **modified** — route `check_unique_meteorite`.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / explicit boundaries):**

- `src/utils/config.py`, `data/admin/agent_task.json`, `data/admin/dispatch_task.json` — **AST-1773** (already on epic line after sync)
- Ruth `do_task` / duplicate → `DUPLICATE` / not-duplicate → `READY` inside the peer paths — **AST-1775** (fills the hook this ticket defines)
- `apply_paste` and any other direct `READY` writers outside stage/scrape landable success
- Changing `run_land_meteorite` claim set (`READY` + `BOT_BLOCKED`) or `land_trigger_state`
- New `database.py` claim/query APIs — use existing `list_meteorites_for_candidate` / `get_meteorite` / claim helpers already imported or importable from `src.data.database`

**Depends on:** **AST-1773** on the epic line (`CHECK_UNIQUE` / `DUPLICATE` in `METEORITE_STATES`, `METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"]` / `check_unique_trigger_state`, scrape `"ok"` → `CHECK_UNIQUE`, `REVIEW_DUPLICATE_METEORITE_CONFIG`). After `sync-child.sh`, if those symbols are missing on HEAD, **stop** and comment on AST-1774 (do not re-implement registry here).

**AC partition (this ticket):** Parent AC3 (stage/scrape → `CHECK_UNIQUE` only), AC5 (SQL match keys), AC6 (unique → `READY`), AC9 (land gate unchanged). Parent AC7 / AC8 (Ruth invoke + `DUPLICATE` map) → **AST-1775** (this ticket only detects peers and calls the hook).

**Canon Scope (read at plan):**

- `patt.entity.batch-processing` — full (claim under one `batch_id`, process only claimed rows, `clear_meteorite_batch` in `finally`)
- `patt.entity.batch-criteria` — full (claim state / limit from `dispatch_task` / `METEORITE_INGRESS_DISPATCH_CONFIG`, not literals invented in the runner beyond reading config keys)
- `astral.batch.claim-process-release` — full (meteorite is an `ENTITY_TYPES` claim queue)
- `stat.logging.info.entity` — full (row transitions use `_meteorite_state_info` / entity progress lines)
- `stat.logging.info.dispatcher` — id-only (dispatcher completion line already owned by existing `_log_dispatch_task_completed`; this ticket does not rewrite that helper — only ensures the new task key routes through the same ingress branch)

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | Retarget stage/scrape landable success → `CHECK_UNIQUE`; add peer-match helpers + Ruth hook stub; add `run_check_unique_meteorite` claim/process/release runner | core |
| `src/core/dispatcher.py` | Register `check_unique_meteorite` on ingress transition key set + runner map; add the same key to `ensure_meteorite_ingress_dispatch_tasks` entries (provision twin of stage/scrape/land) | core |

## Stage 1: Stage/scrape landable success → `CHECK_UNIQUE`

**Done when:** Text-source stage success and scrape `"ok"` success write `CHECK_UNIQUE` (not `READY`); `apply_paste` still writes `READY`; `run_land_meteorite` still claims `READY`/`BOT_BLOCKED` only; module docstring / runner docstrings mention the uniqueness hop; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `src/core/meteorite.py` module docstring (top), update the ingress sentence so stage/scrape landable success is described as → `CHECK_UNIQUE` (not straight to `READY`); land remains `READY` → `LANDED`.

2. In `run_stage_meteorite`:
   - Update the docstring to `NEW → SCRAPE_LINK | CHECK_UNIQUE` (AST-1560 / AST-1774).
   - On the `text_source_ref_outcomes` success arm only (the arm that currently does `update_meteorite(row_id, state="READY")` then `_meteorite_state_info(..., "READY", from_state="NEW")`), change both the state write and the info line to `"CHECK_UNIQUE"`.
   - Do **not** change URL→`SCRAPE_LINK`, skip/error arms, or any other writer in this function.

3. In `run_scrape_meteorite`:
   - Update the docstring to `SCRAPE_LINK → CHECK_UNIQUE | BOT_BLOCKED | LINK_EXPIRED | SCRAPE_ERROR`.
   - On the `page_status == "ok" and visible_text.strip()` success arm, set `state` from `status_map["ok"]` (already `"CHECK_UNIQUE"` after AST-1773) instead of the hardcoded `"READY"` literal; pass that same value to `_meteorite_state_info(..., from_state="SCRAPE_LINK")`.
   - Leave blocked / closed / missing / soft-fail arms unchanged (they already use `status_map` or error states).

4. Confirm by inspection (no edit): `apply_paste` still ends `state="READY"`; `run_land_meteorite` still uses `land_states = ["READY", "BOT_BLOCKED"]` and `cfg["land_trigger_state"]` (`READY`).

⚠️ **Decision — scrape success via `status_map["ok"]`:** Use the config map AST-1773 already retargeted (`"ok": "CHECK_UNIQUE"`) rather than a second hardcoded `"CHECK_UNIQUE"` literal, so stage literal + scrape map stay the SSOT pair without inventing a new config key for stage.

**AC check after this stage:** Parent AC3, AC9 (land untouched).

## Stage 2: Peer helpers + Ruth hook stub + `run_check_unique_meteorite`

**Done when:** `run_check_unique_meteorite` claims `CHECK_UNIQUE`, promotes unique rows to `READY` with entity info lines, calls the Ruth hook (no auto-`DUPLICATE` / no auto-`READY`) when title+employer SQL peers exist or the null-field multi-peer case fires, releases the batch in `finally`, and never matches on email ids / message ids / JD text; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. Add import: `list_meteorites_for_candidate` from `src.data.database` (alongside existing meteorite list helpers).

2. Immediately above the dispatch transition runners section (near `_ZERO_SUMMARY`), add helpers:

```python
def _nonempty_strip(value: Any) -> str:
    return (str(value) if value is not None else "").strip()


def _landed_peers_for_candidate(candidate_id: str, *, exclude_id: int) -> List[Dict[str, Any]]:
    """Same-candidate LANDED rows only — exclude the CHECK_UNIQUE subject id."""
    peers = []
    for row in list_meteorites_for_candidate(candidate_id):
        if int(row["id"]) == int(exclude_id):
            continue
        if (row.get("state") or "").strip() != "LANDED":
            continue
        peers.append(row)
    return peers


def _title_employer_sql_peers(subject: Dict[str, Any], landed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Equal non-empty job_title + employer_name only (not email/message ids, not JD text)."""
    title = _nonempty_strip(subject.get("job_title"))
    employer = _nonempty_strip(subject.get("employer_name"))
    if not title or not employer:
        return []
    matched = []
    for peer in landed:
        if _nonempty_strip(peer.get("job_title")) != title:
            continue
        if _nonempty_strip(peer.get("employer_name")) != employer:
            continue
        matched.append(peer)
    return matched


def _null_field_multi_peers(subject: Dict[str, Any], landed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """When subject title and/or employer is empty, LANDED peers that also have null title and/or null employer."""
    sub_title = _nonempty_strip(subject.get("job_title"))
    sub_employer = _nonempty_strip(subject.get("employer_name"))
    if sub_title and sub_employer:
        return []
    nullish = [
        p for p in landed
        if not _nonempty_strip(p.get("job_title")) or not _nonempty_strip(p.get("employer_name"))
    ]
    # Parent AC7: multiple LANDED rows — need ≥2 to trigger Ruth; else unique path.
    return nullish if len(nullish) >= 2 else []
```

3. Add the Ruth hook stub that **AST-1775** will replace/fill (same module, same name — do not put invoke logic here):

```python
async def _review_duplicate_meteorite_hook(
    row: Dict[str, Any],
    peers: List[Dict[str, Any]],
    *,
    batch_id: str,
    debug: bool = False,
) -> None:
    """Peer path entry for AST-1775 (Ruth invoke + DUPLICATE|READY map).

    Stub: leave row in CHECK_UNIQUE — do not auto-READY or auto-DUPLICATE.
    """
    _ = batch_id, debug
    logger.debug(
        "review_duplicate_meteorite hook stub: meteorite_id=%s peer_ids=%s (AST-1775 owns invoke)",
        row.get("id"),
        [p.get("id") for p in peers],
    )
```

4. Implement `run_check_unique_meteorite` immediately after `run_scrape_meteorite` (before `run_land_meteorite`), mirroring stage/scrape claim shape:

```python
@_with_log_debug
async def run_check_unique_meteorite(task: Dict[str, Any], *, debug: bool = False) -> Dict[str, int]:
    """Dispatch runner: CHECK_UNIQUE → READY (unique) | Ruth hook (peers) (AST-1774)."""
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")
    entity_candidate_id = str((task or {}).get("candidate_id") or "").strip()
    if not entity_candidate_id:
        raise ValueError("candidate_id is required")

    summary = dict(_ZERO_SUMMARY)
    trigger = cfg["check_unique_trigger_state"]
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s, candidate_id=%s]",
        batch_id, trigger, batch_size, entity_candidate_id,
    )
    claim_meteorite_batch(batch_id, trigger, limit=batch_size, candidate_id=entity_candidate_id)
    rows = get_meteorite_batch(batch_id)
    logger.debug("Response from get_meteorite_batch: %s", rows)
    if not rows:
        return summary

    logger.debug("Beginning check_unique meteorite loop on %s items", len(rows))
    try:
        for row in rows:
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            try:
                landed = _landed_peers_for_candidate(cid, exclude_id=row_id)
                sql_peers = _title_employer_sql_peers(row, landed)
                if sql_peers:
                    await _review_duplicate_meteorite_hook(
                        row, sql_peers, batch_id=batch_id, debug=debug,
                    )
                    summary["total_passed"] += 1
                    continue
                null_peers = _null_field_multi_peers(row, landed)
                if null_peers:
                    await _review_duplicate_meteorite_hook(
                        row, null_peers, batch_id=batch_id, debug=debug,
                    )
                    summary["total_passed"] += 1
                    continue
                update_meteorite(row_id, state="READY")
                _meteorite_state_info(row_id, "READY", from_state="CHECK_UNIQUE")
                summary["total_passed"] += 1
            except Exception as exc:
                summary["total_errors"] += 1
                logger.exception(
                    "%s | meteorite %s run_check_unique_meteorite\n  %s: %s\n  Continuing to the next row",
                    cid, row_id, type(exc).__name__, exc,
                )
    finally:
        logger.debug("End check_unique meteorite loop after %s items", summary["total_processed"])
        clear_meteorite_batch(batch_id)
    return summary
```

5. Match order (binding): **title+employer SQL peers first**; else **null-field multi-peer**; else **unique → READY**. Never compare `source_id`, email ids, message ids, or `content` / JD text for equality.

⚠️ **Decision — peer list via `list_meteorites_for_candidate`:** Filter `LANDED` in-process rather than a new `database.py` query — Scope does not name data-layer files; existing helper already scopes by `candidate_id`.

⚠️ **Decision — hook stub leaves `CHECK_UNIQUE`:** Parent AC7/AC8 require Ruth before terminal transitions; AST-1775 owns invoke/map. Auto-`READY` or auto-`DUPLICATE` on peer paths would violate the partition. Stub logs debug only and leaves state so unique→READY still ships under this ticket.

⚠️ **Decision — null multi-peer threshold ≥2:** Parent wording is “multiple LANDED rows”; a single nullish LANDED peer is not enough to force Ruth — promote unique → `READY` instead.

⚠️ **Decision — string equality:** Strip whitespace only; case-sensitive. Parent says “equal”, not case-fold.

**AC check after this stage:** Parent AC5, AC6. Hook presence satisfies the “delegate Ruth hook” Scope line without owning AC7/AC8 outcomes.

## Stage 3: Dispatcher route (+ ingress ensure entry)

**Done when:** `_is_meteorite_ingress_transition_task_key("check_unique_meteorite")` is true; `_meteorite_ingress_runner` returns `run_check_unique_meteorite` for that key; `ensure_meteorite_ingress_dispatch_tasks` can insert the check-unique row for a candidate the same way as stage/scrape/land; `python3 -m py_compile src/core/dispatcher.py src/core/meteorite.py` succeeds.

1. In `src/core/dispatcher.py` `_is_meteorite_ingress_transition_task_key`, add `METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"]` to the membership tuple (with stage/scrape/land).

2. In `_meteorite_ingress_runner`:
   - Late-import `run_check_unique_meteorite` alongside the three existing runners.
   - Add map entry: `METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"]: run_check_unique_meteorite`.

3. In `ensure_meteorite_ingress_dispatch_tasks`, extend `entries` with:

```python
(ingress["check_unique_task_key"], ingress["check_unique_trigger_state"], ingress["batch_size"]),
```

   placed with the other ingress transition keys (before or after land — order among the four is not load-bearing). Update the function docstring from “stage/scrape/land/notify” to include check_unique.

⚠️ **Decision — ensure entry in this ticket:** Scope says “route `check_unique_meteorite` … like other ingress transition keys.” The other three transition keys are both runner-mapped **and** listed in `ensure_meteorite_ingress_dispatch_tasks`. AST-1773 seeded SEED_CONFIG SQL; without the ensure twin, candidates provisioned only via ensure would never get the hop. No new file; still `dispatcher.py` only.

**AC check after this stage:** Parent AC9 still holds (land route untouched). Dispatch completion logging stays on the existing ingress branch (`stat.logging.info.dispatcher` id-only).

## Estimate

Confirm Chuckles estimate: 5 — agree

## Review (build stub)

**Publish ref:** `origin/sub/AST-1762/AST-1774-check-unique-meteorite-sql-transitions`
**Plan path:** `docs/features/meteorite/ast-1774-check-unique-meteorite-sql-transitions.md`

**Built tip:** `b0df9ebe8b8d32e01c7d19d6c30d7ed2b609ec63` (`b0df9ebe`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `b0df9ebe` | stage/scrape → CHECK_UNIQUE; `run_check_unique_meteorite` + Ruth hook stub; dispatcher route + ensure entry |

## Joan validate

[plan-rubric]
**Ticket:** AST-1774
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `sub/AST-1762/AST-1774-check-unique-meteorite-sql-transitions` @ `ee50f95f102cbccea49e6bebbc901b9659d7d747`

## Canon scores

patt.entity.batch-processing | A |
patt.entity.batch-criteria | A |
astral.batch.claim-process-release | A |
stat.logging.info.entity | A |
stat.logging.info.dispatcher | A |

## Traceability

AC3 → Stage 1 steps 2–3 (stage `text_source_ref_outcomes` + scrape `ok` arm → `CHECK_UNIQUE`; `apply_paste` / `run_land_meteorite` inspect-only unchanged); AC4 → Stage 2 steps 2–3, 5 (`_landed_peers_for_candidate` LANDED-only; `_title_employer_sql_peers` same-candidate equal non-empty `job_title` + `employer_name`; explicit ban on email/message/JD equality); AC5 → Stage 2 step 4 else-branch (`update_meteorite` → `READY` + `_meteorite_state_info` from `CHECK_UNIQUE`); AC6 → Stage 1 step 4 + Stage 3 (land runner/claim set untouched; `CHECK_UNIQUE` routed as ingress transition only). Parent AC1–2, AC4, AC7–8, AC10 → N/A (AST-1773 registry/prompts; AST-1775 Ruth invoke/map per plan **AC partition**).

## Findings

### acceptable — No `## Self-assessment` block
- **Severity:** acceptable
- **Location:** Plan structure — Estimate confirm only
- **Finding:** Prior meteorite plans sometimes carry a self-assessment paragraph; this plan stops at estimate confirm.
- **Recommendation:** Optional polish for plan-child parity; not blocking — stages carry done-when gates and explicit ⚠️ decisions.

context_tokens≈42000
