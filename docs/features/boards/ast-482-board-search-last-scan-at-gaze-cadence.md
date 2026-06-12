# Board search `last_scan_at` gaze cadence (Design data flow for Astral Boards)

- **Linear:** [AST-482](https://linear.app/astralcareermatch/issue/AST-482/board-search-last-scan-at-gaze-cadence-design-data-flow-for-astral-boards)
- **Parent:** [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards)
- **Feature ref (origin):** `sub/AST-379/AST-482-board-search-last-scan-at-gaze-cadence`

## Summary

Adds nullable **`last_scan_at`** on **`board_search`**, configures **`scan_interval_hours`** beside existing **`gaze_board`** gaze settings (**mirror company `WATCH` / `gaze`**), narrows **`claim_board_search_batch`** and **`count_eligible_for_dispatch_task`** with the **same staleness predicate** as **`set_company_batch` / `claim_company_batch`**, orders claims by **`last_scan_at`** (seed + DB migration), and bumps **`last_scan_at` only after a successful `run_board_search_gaze`** ingest (**no bump** on **`process_gaze_board_batch`** **`except`** / failure paths). **`updated_at`** is **not** updated when only **`last_scan_at`** advances (scan cadence vs user edits).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Under **`BOARDS_CONFIG["gaze_board"]`**, add **`scan_interval_hours: 24`** (literal, mirrors **`COMPANY_STATES["WATCH"]["batch_criteria"]["scan_interval_hours"]`** intent). Preserve existing **`batch_size`** et al.; do **not** remove unused **`claim_status`** / **`running_status`** keys in this ticket (no cleanup scope). | utils |
| `src/data/database.py` | (1) Header inventory: **`board_search`** lists **`last_scan_at`**. (2) **`BOARD_SEARCH_BATCH_SORT_COLUMNS`** frozenset: at least **`last_scan_at`**, **`updated_at`**, **`created_at`**; **`claim_board_search_batch`** **`ORDER BY`** uses **`sort_by`** only when in whitelist else **`ORDER BY rowid`**. (3) **`_ensure_board_search_table`**: **`ALTER TABLE board_search ADD COLUMN last_scan_at TIMESTAMP`** if missing (idempotent); add **`last_scan_at`** on greenfield **`CREATE TABLE`**. (4) **`_DISPATCH_TASK_SEED["gaze_board"]["sort_by"]`** → **`last_scan_at`**. (5) **`_ensure_dispatch_tasks_schema`**: **`UPDATE dispatch_task SET sort_by = 'last_scan_at' WHERE task_key = 'gaze_board' AND sort_by = 'updated_at'`** (same block as **`gaze`** migration ~L4150). (6) **`claim_board_search_batch`**: add **`scan_interval_hours`**, **`sort_by`** optional args; stale clause matches **`set_company_batch`** (see `database.py` L711–713). (7) **`count_eligible_for_dispatch_task`** branch **`board_search`**: **`freq_hrs` > 0** uses **`freq_hrs`**, else **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`**; **`WHERE`** staleness identical to claim. (8) **`update_board_search_last_scan_at`** — sets **`last_scan_at`** only. | data |
| `src/core/dispatcher.py` | In **`entity_type == "board_search"`** block: **`eff_scan`** from **`task["freq_hrs"]`** vs **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`** (default **24** if missing); pass **`scan_interval_hours`** and the same **`sort_by`** string already computed at **`_run_unified`** entry (trimmed **`task`** **`sort_by`**, same pattern as **`sort_override`** on company **`gaze`**). | core |
| `src/core/gazer.py` | After successful **`await run_board_search_gaze`** in **`process_gaze_board_batch`** **`try`**, call **`update_board_search_last_scan_at(sid)`**; **`except`** path unchanged (**no bump**). | core |
| `tests/component/data/database/test_board_search_integration.py` | Tests: stale vs fresh **`last_scan_at`**, **`NULL`**, **`freq_hrs` override** parity with **`count_eligible`** (extend **`TestClaimBoardSearchSqlShape`** or new class). | tests |
| `tests/component/core/test_gazer.py` | Success ⇒ **`last_scan_at`** set; exception path ⇒ **`last_scan_at`** unchanged. | tests |
| `tests/component/core/test_dispatcher.py` | Monkeypatch **`claim_board_search_batch`**; assert **`scan_interval_hours`** and **`sort_by`** kwargs. | tests |
| `tests/component/utils/test_config.py` | Adjust only if assertions pin **`gaze_board` sort_by`; expect **`last_scan_at`**. | tests |
| `docs/ASTRAL_TEST_BIBLE.md` | New or extended **§7.13** row for **`AST-482`** + test names. | docs |

Spike/playwright output stays under **`debug/spikes/`** only (**gitignored**).

## Stage 1: Schema + config + dispatch seed parity

**Done when:** Fresh and migrated DBs have **`last_scan_at`** nullable on **`board_search`**; **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"] == 24`**; **`_DISPATCH_TASK_SEED["gaze_board"]["sort_by"]`** is **`last_scan_at`**; **`_ensure_dispatch_tasks_schema`** migrates **`updated_at`** → **`last_scan_at`** on existing **`dispatch_task`** rows **`task_key = 'gaze_board'`** once at startup (**same staging as gaze **`sort_by`** migration**).

1. **`config.py`**: add **`scan_interval_hours: 24`** inside **`BOARDS_CONFIG["gaze_board"]`**.
2. **`database.py`** header inventory: **`board_search`** line documents **`last_scan_at`** scan cadence (not claim lock).
3. **`_ensure_board_search_table`**: **`PRAGMA table_info`**; if **`last_scan_at` not in cols**, **`ALTER TABLE board_search ADD COLUMN last_scan_at TIMESTAMP`**; **`commit`** when needed.
4. New installs: **`CREATE TABLE board_search (...)` column list adds **`last_scan_at TIMESTAMP`** (nullable — omit **NOT NULL**).
5. **`BOARD_SEARCH_BATCH_SORT_COLUMNS`** **`frozenset`** + docstring.
6. **`_DISPATCH_TASK_SEED["gaze_board"]["sort_by"]`** → **`"last_scan_at"`**.
7. After existing **`UPDATE dispatch_task ... gaze ...`** (**~L4151**): add **`UPDATE dispatch_task SET sort_by = 'last_scan_at' WHERE task_key = 'gaze_board' AND sort_by = 'updated_at'`** + **`conn.commit()`**.

⚠️ **Decision:** **`update_board_search_last_scan_at`** does **not** bump **`updated_at`** (ticket: cadence ≠ edits); **`batch_id`** claim **still updates `updated_at`** as today.

## Stage 2: Claim + eligibility + dispatcher wiring

**Done when:** Claim returns only **ACTIVE**, clear **`batch_id`**, and staleness rows; **`count_eligible_for_dispatch_task`** uses the **same** **`WHERE`** for **`freq_hrs` vs `scan_interval_hours`** as claim.

8. **`claim_board_search_batch`**: implement **`scan_interval_hours`** and **`sort_by`** as in **Files Changed** table; whitelist **`ORDER BY`** column (**`ASC NULLS FIRST`** for **`last_scan_at`**).
9. **`count_eligible_for_dispatch_task`** (**`board_search`** branch): staleness **`AND`** mirrors **`claim`**; **`hours`** string binding follows **`WATCH`** path (**`database.py`** ~4318-4331).
10. **`dispatcher._run_unified`** **`board_search`**: **`eff_scan`** from **`freq_hrs`** vs **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`** (default **24**); pass **`scan_interval_hours`** + trimmed **`sort_by`** into **`claim_board_search_batch`**.

⚠️ **Decision:** **`eff_scan`** mirrors company **`gaze`**: **`freq_hrs > 0`** overrides **`BOARDS_CONFIG`** interval ( **`dispatcher`** company **`scan_override`** path ~L175).

## Stage 3: Success-path bump after ingest

**Done when:** Component tests prove **`last_scan_at`** is set only when **`run_board_search_gaze`** returns without **`process_gaze_board_batch`** entering **`except`**; **`ERROR`** **`state`** leaves **`last_scan_at`** unchanged.

11. **`database.update_board_search_last_scan_at`** — single-row **`UPDATE`** of **`last_scan_at`** only.
12. **`gazer.process_gaze_board_batch`**: after **`run_board_search_gaze`** succeeds inside **`try`**, call **`update_board_search_last_scan_at(sid)`** before **`set_board_search_state`** (order flexible).

⚠️ **Decision:** **`board_search_run.completed_at`** stays audit-only — **never** the claim **`WHERE`** (per ticket boundaries).

## Stage 4: Tests + **`ASTRAL_TEST_BIBLE`**

**Done when:** New/updated tests listed in **Files Changed** pass in CI; **`ASTRAL_TEST_BIBLE`** **§7.13** cites **`AST-482`** coverage + file/class names (**§7.12** rituals if required for **100 %** bookkeeping).

13. **`test_board_search_integration.py`**, **`test_gazer.py`**, **`test_dispatcher.py`**, **`test_config.py`** per table.
14. **`ASTRAL_TEST_BIBLE.md`**: add **§7.13** subsection (or extend **§7.13q**/r**) for **`last_scan_at`** **`gaze_board`** cadence + test pointers.

## Execution contract

If **`SQLite` `ALTER`** or **`sort_by` whitelist** cannot handle legacy DB **`sort_by`**, **STOP** and comment on **AST-482** (plan-astral escalation).

## Self-Assessment

### Scope

**Single-Component** — **`database`**, **`dispatcher`**, **`gazer`**, **`config`**, Boards tests + bible (no UI; **`board_search`** **`state`** semantics unchanged).

### Conf

**high** — Mirrors company **`last_scan_at`**, **`scan_interval_hours`**, and **`count_eligible`** (**`database.py`** + **`dispatcher.py`**).

### Risk

**Medium** — Incorrect **`hours`** parity or **`ORDER BY`** would either starve **`gaze_board`** (**over-throttle**) or re-hit boards every tick (**under-throttle**) — regressions confined to Boards dispatch + admin counts.

---

## Rules cross-check (§§1.3–3.5)

| Rule | Fit |
|------|-----|
| **§1.3 DRY** | Staleness **`AND`** duplicated **verbatim** in **`claim`** and **`count`** (⚠️ **Decision:** inline, no helper — matches **AST-459** parity style). |
| **§2.1 config** | **`scan_interval_hours`** on **`BOARDS_CONFIG["gaze_board"]`**; **`freq_hrs`** on **`dispatch_task`** overrides when **> 0**. |
| **§2.4 batch** | **`batch_id`** claim/clear unchanged; **`last_scan_at`** is separate from locking. |
| **§2.6 state** | No **`state`** workflow edits (**AST-471** **`ACTIVE`** / **`INACTIVE`** / **`ERROR`**). |
| **§3.3 imports** | **`database`** already imports **`BOARDS_CONFIG`**; **`gazer`** adds **`update_board_search_last_scan_at`** import only. |
| **§3.5 naming** | **`update_board_search_last_scan_at`** parallel **`update_company_last_scan_at`**. |

---

## Review stub (build — **AST-482**)

| Field | Value |
|-------|--------|
| **`dev-hedy`** (implementation) | `3bb1cd8f498db42663165efb857514683a0c1146` |
| **`origin` publish branch** | `sub/AST-379/AST-482-board-search-last-scan-at-gaze-cadence` |

## Review

**Radia (`linear-radia`) vs `origin/dev`…`origin/sub/AST-379/AST-482-board-search-last-scan-at-gaze-cadence`**, tip **`8944bf86b2733582ada8d2b95213365dae157a09`**.

### What’s solid

- Acceptance criteria mapped: **`last_scan_at`** DDL (idempotent + rebuild path), **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`**, staleness **`AND`** wired in **`claim_board_search_batch`** and **`count_eligible_for_dispatch_task`**, **`_run_unified`** passes **`freq_hrs` / config**‑aligned **`scan_interval_hours`** plus **`sort_by`**, **`_DISPATCH_TASK_SEED`** + migration for **`sort_by`**, **`update_board_search_last_scan_at`** on success‑only ingest path (**`except`** unchanged), **`ASTRAL_TEST_BIBLE`** §**7.13za** (+ §**7.13q** row touch for cadence coverage).
- **ASTRAL_CODE_RULES** fit: **`scan_interval_hours`** as config literal; batch claim → process → release unchanged (**§2.4**); **`ORDER BY`** whitelist (**`BOARD_SEARCH_BATCH_SORT_COLUMNS`**); **`gazer`** only adds **`data`** import (**§3.3**); **`run_board_search_gaze`** returns success dict or raises (no silent “failed but bumped” slice without **`except`** being avoided).
- **Tests** exercise fresh vs **`NULL`/stale** claim, **`count_eligible`** parity, **`freq_hrs`** tightening vs claim, dispatcher kwargs, config default **24**, and gaze bump only on the successful **`bs-1`** row in **`TestProcessGazeBoardBatch`**.

### Issues

| Severity | Area | Notes |
|----------|------|-------|
| **discuss** | **`docs/ASTRAL_TEST_BIBLE.md`** boundary | **`§7.13y`** / **`§7.13z`** document AST‑478 lineage (**AST‑479**–**481**), not **AST‑482**. Fine if Susan chose a bible batch on this integration tip—otherwise peels cleaner on **`resolve-astral`** if those sections arrive from **`origin/dev`** or sibling publish branches (**review-astral §5d**). |

### Recommended actions

| Priority | Owner | Action |
|----------|-------|--------|
| optional | Chuckles | Confirm whether **`§7.13y`/`§7.13z`** on this Boards child publish is deliberate bible catch‑up vs **AST‑478**/`dev` lineage; relocate or annotate to keep ticket cherries narrow. |

**Review doc commit**: follow `review-astral` §6 (this section). **Cherry-pick-only** merge handoff.

---

## Resolution

**Date:** 2026-05-24 (resolve-astral, **Hedy** / `linear-hedy`). **Linear:** [AST-482](https://linear.app/astralcareermatch/issue/AST-482) (**Review Posted → User Testing**).

### Vs Radia’s review (`review-astral`)

- **fix-now:** No product or plan-doc corrections required (**0** items).
- **discuss (`ASTRAL_TEST_BIBLE` §7.13y/z vs §7.13za):** **Closed — intentional.** Boards publish tip **`8944bf86`** includes Betty’s QA manifest and bible updates where **`§7.13za`** carries **AST‑482** cadence coverage; **`§7.13y`** / **`§7.13z`** are sibling **AST‑478** lineage on the same integration surface (confirmed with Chuckles/Susan backlog batching intent). **`resolve-astral`** cherries for this ticket stay **narrowly** **`feat(AST-482):`**, **`docs(AST-482):`**, **`test(AST-482):`**, Radia appendix **`docs(AST-482): Radia review`**, plus this **`docs(AST-482): Resolution`** hop — no bible peel needed.
- **advisory:** None.

### Shipped refs

- **`origin/sub/AST-379/AST-482-board-search-last-scan-at-gaze-cadence`:** product **`8944bf86`**; Radia appendix plan commit **`c4c36876`**; Resolution doc commit (**this append**).

