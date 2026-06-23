# Sunset boards in Code Rules, test bible, and feature docs (Sunset Astral Boards)

**Parent:** [AST-757](https://linear.app/astralcareermatch/issue/AST-757/sunset-astral-boards)  
**Publish ref:** `sub/AST-757/AST-767-sunset-boards-documentation`

**Summary:** Document the Astral Boards sunset in **`docs/ASTRAL_CODE_RULES.md`** (rationale + both revival SHAs), retire active boards manifest sections in the monolith and decomposed **`docs/test-bible/**`**, and reframe **`docs/features/boards/`** as a historical archive. Docs-only — no `src/`, `tests/`, or `scripts/spikes/` edits.

**Prerequisite (on ftr @ `ad5d683`):** Siblings **AST-765** (product removal) and **AST-766** (schema drop) shipped; Betty retired board-only tests on those subs.

**Revival SHAs (authoritative):**

| Label | SHA | Notes |
|-------|-----|-------|
| Pre-removal `dev` tip at dispatch | `8d9b01e5e75ace9c04c32711488430503075e0c3` | Parent **Description** + **AST-765** plan |
| First removal commit | `e8fe8143f7b0b73a703238af1c31a39252b65992` | `code(AST-765): delete boards modules and unregister API` — equivalent `f64c3c0` on AST-765 republish line |

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/ASTRAL_CODE_RULES.md` | Add **§3.7 Sunset — Astral Boards** | docs |
| `docs/ASTRAL_TEST_BIBLE.md` | Retire §7.13q/r/s/v/za/zzu active manifests; add consolidated sunset pointer; trim board refs in §7.13w | docs |
| `docs/test-bible/core/dispatcher.md` | Replace AST-458 active spine with sunset historical note; consolidate AST-765 → AST-757 sunset | docs |
| `docs/test-bible/core/consult.md` | Consolidate AST-765 sunset; remove active board routing rows in historical blocks | docs |
| `docs/test-bible/core/gazer.md` | Consolidate AST-765 sunset | docs |
| `docs/test-bible/core/tracker.md` | Consolidate AST-765 sunset; retire board-sourced manifest block | docs |
| `docs/test-bible/external/playwright.md` | Consolidate AST-765 sunset | docs |
| `docs/test-bible/utils/config.md` | Consolidate AST-765 sunset | docs |
| `docs/test-bible/frontend/root.md` | Mark AST-649 block historical; point to Code Rules | docs |
| `docs/test-bible/frontend/pages.md` | Retire AST-521 board-search craft rows (historical one-liner) | docs |
| `docs/test-bible/data/database/dispatch_tasks.md` | Keep AST-766 manifest; add sunset cross-ref | docs |
| `docs/test-bible/dev/cleanup_duplicate_and_board_gaze_jobs.md` | Update board-prefix note (literal `__board__`, not `BOARDS_CONFIG`) | docs |
| `docs/features/boards/README.md` | Archive preamble — sunset framing, link to Code Rules §3.7 | docs |

**Not in engineer commits:** `src/**`, `tests/**`, `scripts/spikes/**`.

---

## Stage 1: Code Rules sunset section

**Done when:** `docs/ASTRAL_CODE_RULES.md` contains **§3.7 Sunset — Astral Boards** immediately after **§3.6** (before **§4**); section includes roster/CSE rationale, both SHAs in a table, revival `git show`/`git diff` hints, pointers to archived `docs/features/boards/` and test-bible sunset notes.

1. Insert new **§3.7** after the `---` following §3.6 (~line 482):

   - **Heading:** `### 3.7 Sunset — Astral Boards (AST-757)`
   - **Body:** Boards channel sunset; superseded by Google CSE roster cultivation; epic siblings **AST-765**–**766** removed product + schema; **AST-767** retires active bible manifests.
   - **SHA table:** pre-removal `8d9b01e5e75ace9c04c32711488430503075e0c3`; first removal `e8fe8143f7b0b73a703238af1c31a39252b65992` (note equivalent `f64c3c0` on AST-765 line).
   - **Revival:** `git diff 8d9b01e5..e8fe814` for removal start; `git show 8d9b01e5:<path>` for last product files.
   - **Archive pointers:** `docs/features/boards/`; no active test obligations — monolith §7.13 boards (sunset) + decomposed bible sunset stubs.

2. Grep `ASTRAL_CODE_RULES.md` for `BOARD_CONFIG`, `gaze_board`, `board_search` — expect zero (sunset section may name them historically only).

---

## Stage 2: Monolith test bible consolidation

**Done when:** §7.13q, §7.13r, §7.13s, §7.13v, §7.13za, and §7.13zzu no longer list active component-test manifests; each replaced with a **RETIRED (AST-757)** stub pointing to **§3.7** and `docs/features/boards/`; §7.13w no longer references live board registry / `TestProcessGazeBoardBatch` / `test_board_sourced_qualify_evaluate` as active coverage.

1. Add consolidated header before §7.13q (or replace §7.13q opening):

   ```markdown
   ## 7.13 boards channel (SUNSET — AST-757)

   **No active manifest.** Astral Boards removed (**AST-765** product, **AST-766** schema). Revival SHAs and rationale: **`docs/ASTRAL_CODE_RULES.md` §3.7**. Historical plans: **`docs/features/boards/`**. Retired monolith subsections below are archive index only.
   ```

2. Replace body of **§7.13q**, **§7.13r**, **§7.13s**, **§7.13v**, **§7.13za**, **§7.13zzu** — keep section headings (for monolith grep / retired map) but replace manifest tables and narrowed runs with:

   `**RETIRED (AST-757):** No component-test obligations. See Code Rules §3.7.`

3. In **§7.13w** (~lines 340–353):
   - Remove table row **`TestBoardRegistryAst457`** / board registry layout.
   - Remove **`TestProcessGazeBoardBatch`** / **`§7.13q`** sentence from consult/gazer row.
   - Remove **`test_board_sourced_qualify_evaluate.py`** row (board-sourced pipeline).
   - Remove manifest sentence referencing board integration gaps.

---

## Stage 3: Decomposed test-bible sunset stubs

**Done when:** Each listed decomposed file has no active boards manifest tables implying live coverage; AST-458-style spine blocks replaced with AST-757 sunset historical notes pointing to Code Rules §3.7.

1. **`docs/test-bible/core/dispatcher.md`:** Replace **### AST-458 · AST-471 · AST-379** block (lines 13–29) with historical sunset stub. Replace **### AST-765 · AST-757** body with single sunset paragraph + link to Code Rules §3.7 (remove narrowed run implying boards work).

2. **`docs/test-bible/core/consult.md`:** Replace top board-related rows in historical **AST-467** block if present; consolidate **### AST-765 · AST-757** to sunset pointer (remove epic manifest listing board tests).

3. **`docs/test-bible/core/gazer.md`:** Remove **`TestProcessGazeBoardBatch`** from AST-544 table if still listed as live; consolidate **AST-765** section to sunset pointer.

4. **`docs/test-bible/core/tracker.md`:** Replace board-sourced **AST-419** active manifest block with RETIRED stub; consolidate **AST-765** section.

5. **`docs/test-bible/external/playwright.md`:** Consolidate **AST-765** to sunset pointer.

6. **`docs/test-bible/utils/config.md`:** Consolidate **AST-765** to sunset pointer.

7. **`docs/test-bible/frontend/root.md`:** Mark **AST-649** block as historical (UI retired; backend removed AST-765); point to Code Rules §3.7.

8. **`docs/test-bible/frontend/pages.md`:** Replace **AST-521** board-search craft table row with historical one-liner (craft generate removed with boards module).

9. **`docs/test-bible/data/database/dispatch_tasks.md`:** Add one-line cross-ref at top of **AST-766** block: prior board integration retired; active test is schema sunset only.

10. **`docs/test-bible/dev/cleanup_duplicate_and_board_gaze_jobs.md`:** In reuse note (~line 11), replace `BOARDS_CONFIG["ingest"]["placeholder_company_prefix"]` with literal **`__board__`** prefix (AST-765 removed config).

---

## Stage 4: Feature docs archive preamble

**Done when:** `docs/features/boards/README.md` opens with sunset/archive framing; no language implying active production board-channel work.

1. Replace README title and opening paragraph:

   - Title: `# Astral Boards (historical archive — SUNSET AST-757)`
   - Lead: This folder preserves design history only; boards channel removed from product. See **`docs/ASTRAL_CODE_RULES.md` §3.7** for rationale and revival SHAs.

2. Keep spikes table (§3.6 alignment) — still accurate for historical spike CLIs under `scripts/spikes/`.

3. Remove "production board-channel work only" language.

---

## Stage 5: Verification

**Done when:** Grep shows no active manifest language implying live boards coverage outside sunset stubs.

1. Run:

   ```bash
   rg -n 'test_board_search_integration|test_board_ingest|TestProcessGazeBoardBatch|TestBoardRegistryAst457|test_board_sourced|/api/boards|claim_board_search' docs/ASTRAL_TEST_BIBLE.md docs/test-bible/
   ```

   Expect hits only inside **RETIRED**, **SUNSET**, **historical**, or Code Rules cross-ref context — not as active manifest obligations.

2. Confirm **§3.7** present in `ASTRAL_CODE_RULES.md` with both SHAs.

3. Post **Code Complete** Linear comment: Betty may trim any remaining historical rows on next qa pass; no `tests/` changes in this ticket.

---

## Self-Assessment

**Scope:** `Single-Component` — Documentation-only across Code Rules, monolith bible, decomposed test-bible, and boards feature README; no product or test tree.

**Conf:** `high` — SHAs and file targets fixed by parent epic and AST-765/766 sibling plans; pattern is replace active manifests with sunset stubs + §3.7 anchor.

**Risk:** `low` — Doc-only; worst case is a missed boards manifest row implying live tests ( caught by Stage 5 grep).

---

## ASTRAL_CODE_RULES review

| Rule | Assessment |
|------|------------|
| §3.6 spikes | README keeps spike path guidance; no change to `scripts/spikes/` |
| §1 scope | Sunset section is explicit out-of-scope documentation for removed channel |
| DRY | Single §3.7 anchor; bible stubs point there rather than duplicating SHAs |

No conflicts requiring escalation.

---

## Radia review (2026-06-23)

**Diff:** `origin/dev...origin/sub/AST-757/AST-767-sunset-boards-documentation` @ `2d0050a`  
**Product commit reviewed:** `a62c6a7` (docs only)

### What’s solid

| Area | Notes |
|------|-------|
| Plan Stages 1–5 | **§3.7** added after §3.6 with both revival SHAs, `git diff`/`git show` hints, archive pointers; monolith §7.13 consolidated header + **RETIRED** stubs for §7.13q/r/s/v/za/zzu; §7.13w board registry/gaze/board-sourced rows removed; decomposed bible sunset stubs in dispatcher, consult, gazer, tracker, playwright, config, frontend root/pages, dispatch_tasks, cleanup script doc (`__board__` literal). |
| Stage 5 grep | Remaining hits only in **RETIRED** / **historical** / §3.7 cross-ref context (`dispatch_tasks.md`, `frontend/root.md`). |
| Scope | No `src/`, `tests/`, or `scripts/spikes/` in `a62c6a7`; `docs/features/boards/README.md` reframed as historical archive. |
| Betty | `merge-tests(AST-767)` at tip — bible README sunset pointer; no doc regressions. |

### Issues

None **fix-now**.

### Advisory

Three-dot diff vs `origin/dev` includes **AST-765** / **AST-766** product + test removal (expected epic stacking). AST-767 doc surface is `a62c6a7` only.

### Recommended actions

Ada → **resolve-child** — no changes required.

---

## Resolution (2026-06-23)

**Review:** Radia clean — no fix-now, discuss, or doc/product changes.

**§9a:** `origin/sub/AST-757/AST-767-sunset-boards-documentation` merges cleanly into `origin/dev` and `origin/ftr/AST-757-sunset-astral-boards`.

**Shipped @ resolve:** docs-only @ `05ac119`; Betty `merge-tests` @ `654d553`; test pass = Stage 5 acceptance grep (no pytest manifest).
