# Design data flow for Astral Boards: gaze_board enabled flag and user deeplink URLs

- **Linear:** [AST-459](https://linear.app/astralcareermatch/issue/AST-459/design-data-flow-for-astral-boards-gaze_board-enabled-flag-and-user-deeplink-urls)
- **Parent:** [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards)
- **Feature ref (origin):** `sub/AST-379/AST-459-design-data-flow-for-astral-boards-gaze-board-enabled-flag-and-user-deeplink-urls`
- **Depends on:** Shipped **[AST-418](ast-418-design-data-flow-for-astral-boards-gaze-board-dispatch-and-gazer-batch.md)** (`run_board_search_gaze`, `claim_board_search_batch`, **`board_search.status`** semantics). Requires **AST-458** **`enabled`** column + **`search_mode`** + **`deeplink_url`** persisted and domain-validated at save — **implement after or coordinate** if Katherine needs parallel API contract stubs; **`build-astral`** MUST NOT land **459** persistence changes (description boundary).

## Summary

Periodic **`gaze_board`** batches must: **(1)** claim only **`board_search`** rows the user left **enabled**, while keeping operational **`status`** (`active`|`running`|`error`) independent as today; **(2)** during **`run_board_search_gaze`**, if the saved row is in **deeplink mode**, **`page.goto`** the **stored user URL** exactly (already domain-checked at save — **458**); if in **criteria** mode, keep param-synthesis behavior from **`board_search_deeplink(page, profile_entry_url, query_params)`** per **418**. No ingest fork changes (**AST-417**), no UI.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Narrow WHERE inside **`claim_board_search_batch`** and the **`board_search`** branch of **`count_eligible_for_dispatch_task`** to require **`enabled` truthy semantics** aligned with **`458`** (**`enabled IS NULL`** treated as **`1`** historically if ALTER missed — ⚠️ **Decision:** ALTER should have made column NOT NULL default 1; both use **`AND COALESCE(enabled, 1) = 1`** for safety ONCE then simplify to **`enabled = 1`** once confident). Comment above SQL states user vs batch dimensions. | data |
| `src/core/boards.py` | **`run_board_search_gaze`**: branch on row **`search_mode`** (fallback `"criteria"` when column absent pre-migrate read — ⚠️ **Decision:** AST-459 build assumes **`458` merged**: mode always present). Deeplink branch uses stored URL → Playwright **`board_search_deeplink`** overload behavior (Stage 2). | core |

No **`config.py`** change unless **`BOARDS_CONFIG["gaze_board"]`** gains a readability flag documenting claim filter (**optional**, default skip extra config noise — ⚠️ **Decision:** omit new config constants; claim filter is deterministic SQL commentary only).

Spike/playwright captures under **`debug/spikes/AST-459/`** only if manual validation needed (**gitignored**).

## Stage 1: Claim path filters user-disabled rows

**Done when:** DB integration path never claims rows with **`enabled = 0`**, assuming migration from **458**.

1. In **`database.claim_board_search_batch`**, append predicate **`AND COALESCE(enabled, 1) = 1`** to both the SELECT IDs leg and transactional UPDATE targeting those IDs (preserve existing **`status`/batch predicates** verbatim).
2. Document inline: **`status`** predicates remain **lifecycle** only; **`enabled`** predicates are **UX persistence**.

## Stage 2: Gaze scrape uses stored deeplink when mode says so

**Done when:** For **`search_mode == "deeplink"`** (string compare), Playwright navigates full user URL **without** injecting criteria query params.

3. **`run_board_search_gaze`** (after profile validation + scrape_mode **`deep_link`** check identical to baseline):
    - **`mode = row.get("search_mode") or "criteria"`**.
    - If **`mode == "deeplink"`**:
       - **`stored = (row.get("deeplink_url") or "").strip()`** — empty → **`ValueError("missing deeplink URL for deeplink-mode board_search")`** (should not happen post-458 POST/PATCH guards; escalate if raised because data drift).
       - **`async with`** browser context unchanged.
       - Call **`await board_search_deeplink(page, stored_url, None)`**.
       - **Do not rebuild** URLs from **`profile["entry_url"]`** for navigation target (different from **`criteria`** branch below).
    - Else (**criteria** classical path):
       - Keep today’s behavior: **`query_params`** from **`criteria`** keys **`title_query`**, **`work_mode`**, **`max_listing_age`**, **`entry_url`** from **`profile`**, **`board_search_deeplink(page, entry_url, query_params)`**.
    - Subsequent **`extract_board_listings` → `ingest_board_listings`** unchanged for both branches (**AST-417** contract preserved).

⚠️ **Decision:** **`board_search_deeplink`** reused for **criteria** synthesis **and** user URL navigation so cookie-dismiss / timeout behavior stays centralized; **`query_params` empty dict** ⇒ function already **goto** canonical URL unchanged (`playwright.board_search_deeplink` § lines 2296–2311 baseline).

## Stage 3: Status + error symmetry

**Done when:** Rows stay **`running`/`active`/`error`** exactly like **418** aside from exclusion from claim when **`enabled=false`**.

4. Do **not** automatically flip **`enabled`** when **`status`** becomes **`error`** — user disables via API only (**458** boundary).
5. **`process_gaze_board_batch`** / **`set_board_search_status`** callers remain unchanged — **`enabled`** is never written here unless future ticket says so(**out of scope**).

## Execution contract

- **Pre-req drift:** If **458** naming differs (**`board_search_mode` vs key `mode`**) the builder maps using **whatever keys `_parse_board_search_row`** actually exposes (`search_mode` per **458 plan** literal). STOP if mismatch surfaces during **build**.
- Escalations if **`board_search`** row violates mutual exclusivity invariants — **`build` stops** Linear parent comment (**AST-379** if cross-child) per execution contract (**plan-astral**).

## Self-Assessment

### Scope

**minor** — Surgical SQL WHERE addition + branching inside **`run_board_search_gaze`**.

### Conf

**high** — AST-418 path well understood; deltas are narrow and localized.

### Risk

**Medium** — Mis-checked claim filter could suppress all board searches (**enabled typo**) or resurrect disabled batches; reversible via migration + regression focus on claim SQL.

---

## Rules cross-check

- **§2.4 batch locking:** **`batch_id` / `clear_board_search_batch`** untouched.
- **§2.6 state machines:** Operational **`status`** still three-state semantics (extend only via existing **418**).
- **§3.3 imports:** **`boards` → `playwright`, `tracker`, `database`** remains valid.
- **Tests:** Betty shipped **`ASTRAL_TEST_BIBLE`** **§7.13r** + component coverage (`TestClaimBoardSearchSqlShape`, `TestRunBoardSearchGazeAst459`, related harness entries) on **`ftr/AST-459`** — see **Review** table.

---

## Review

**Radia** — `review-astral`, diff `origin/dev...origin/ftr/AST-459`, tip **`80402612e44d13aff106c24fe9f7a5b228933c73`**. Scope for this pass: **AST-459** acceptance criteria (enabled filter on claim, deeplink vs criteria navigation in `run_board_search_gaze`, independence of batch **status**). Epic-wide siblings on the same branch were not re-reviewed here.

### What’s solid

- **`claim_board_search_batch`** adds **`AND COALESCE(enabled, 1) = 1`** with an inline note separating user **enabled** from lifecycle **status** — matches AC (skip disabled, NULL-safe).
- **`run_board_search_gaze`** branches on **`search_mode`**: deeplink uses stored **`deeplink_url`** and passes **`None`** for query params so **`board_search_deeplink`** does not synthesize criteria; criteria path keeps **`entry_url`** + param subset. Empty deeplink raises **`ValueError`** as planned.
- **Tests/Bible:** `TestClaimBoardSearchSqlShape::test_claim_skips_user_disabled_board_search_ast459` and `TestRunBoardSearchGazeAst459` cover claim + gaze branches; **§7.13r** in `docs/ASTRAL_TEST_BIBLE.md` matches implementation.
- **Self-Assessment (**Scope / Conf / Risk**)** aligns with Linear labels (**scope-minor**, **conf-high**, **risk-Medium**).

### Issues

| Severity | Topic | Finding |
|----------|-------|-----------|
| **discuss** | Dispatch eligibility vs claim | **`count_eligible_for_dispatch_task`** for **`entity_type=board_search`** counts idle rows by **status**/batch only and does **not** apply **`COALESCE(enabled,1)=1`**. **`claim_board_search_batch`** does. If the scheduler/UI relies on this count, it may over-report work while claims return fewer rows — consider aligning the WHERE clause with claim unless disabled rows are intentionally included in “inventory” counts. |
| **discuss** | **§1.2 / B1** imports | **`extract_board_listings`** and **`run_board_search_gaze`** use function-scoped `from src.external…` / `src.core…` imports without the short justification comment expected for non-top-level imports (see **`ASTRAL_CODE_RULES.md`** §1.2 and **`review-astral`** §5a). Acceptable only with a bounded comment (lazy/cycle/heavy-dep) or hoisting after cycle check — neither is documented in-diff. |

### Recommended actions

| Item | Owner | Note |
|------|-------|------|
| Eligibility **`COUNT`** vs claim | Implementer / Susan | Confirm product intent; if counts should mirror claimable gaze work, add the same **`enabled`** predicate to the **`board_search`** branch of **`count_eligible_for_dispatch_task`**. |
| Import placement / comments | Implementer | Add one-line rationale per function-scoped import (or hoist) under **§1.2**. |
| Plan hygiene | Advisory | **Rules cross-check** still says no tests landed; **`ASTRAL_TEST_BIBLE`** **§7.13r** and component tests contradict — update when next editing this plan doc. |

**Counts:** **0 fix-now**, **2 discuss**, **1 advisory** (doc drift only).

---

## Resolution

**2026-05-23 — Hedy (`resolve-astral`, post-Radia `review-astral`)**

- **Discuss — dispatch count vs claim:** **`count_eligible_for_dispatch_task`** **`board_search`** branch now includes **`AND COALESCE(enabled, 1) = 1`**, matching **`claim_board_search_batch`**, so scheduler / admin **`available_count`** reflects rows that can actually be claimed for **`gaze_board`**.
- **Discuss — §1.2 function-scoped imports:** **`extract_board_listings`** and **`run_board_search_gaze`** document why imports are local (REST-only paths vs scrape; **`boards` ↔ `gazer`/`tracker`** lazy edges + Playwright deferral).
- **Advisory — Rules cross-check:** Rephrased to reference Betty tests and bible **§7.13r** (see **Rules cross-check** bullet above).

**Refs:** Radia Linear comment AST-459; diff review tip **`80402612`**; follow-up implementation commit on **`origin/ftr/AST-459`** (see Linear “Review feedback resolved” comment for hash).
