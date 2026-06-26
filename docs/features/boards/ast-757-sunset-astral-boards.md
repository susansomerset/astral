# AST-757 — Sunset Astral Boards

<!-- linear-archive: AST-757 archived 2026-06-23 -->

## Linear archive (AST-757)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-757/sunset-astral-boards  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The boards channel (candidate-defined saved searches on adopted external job boards) was built and partially shipped, but Susan has decided roster cultivation via Google CSE is the durable job-discovery path. UI for board searches was already retired (**AST-648** / **AST-649**); backend modules, config, dispatch paths, database schema, tests, and bible sections remain and still influence design and maintenance. This epic removes that remaining surface entirely so boards no longer appear in config, APIs, dispatch, tests, or documentation as live product scope — while preserving enough repo history (commit SHAs + archived docs) to revive the idea later if needed.

## Functional scope

* **Remove boards product code:** Delete or excise all boards-channel implementation in `src/` — core boards module, boards REST API, board-specific config blocks and helpers, `gaze_board` and related dispatch/consult/gazer/tracker/playwright paths, admin hidden-key shims that exist only for boards, and server route registration for boards APIs. Company-centric gazer and roster flows must remain intact.
* **Remove boards database usage:** Drop or migrate away the `board_search` table and any job/company columns or sentinel values used only for board-sourced ingest (e.g. board-search FK, placeholder board companies). No runtime code may read or write board-search rows after this ships. No production data purge or migration — treat board-sourced rows as if they never existed; schema/code removal only.
* **Retire boards tests:** Remove component and integration tests whose sole purpose is boards behavior; update shared fixtures/conftest that exist only for boards. Full component test suite must pass without boards coverage.
* **Update test bible:** Remove or consolidate all active boards manifest sections (§7.13q–§7.13zzu and decomposed bible files under `docs/test-bible/` that exist only for boards). Any retained historical mention must point to the sunset note in Code Rules, not imply live coverage.
* **Document the sunset in Code Rules:** Add an explicit section to `docs/ASTRAL_CODE_RULES.md` stating that Astral Boards was sunset, why (roster/CSE superseded it), and **two authoritative commit SHAs on** `dev`: (1) the `dev` tip SHA at **dispatch** (last commit before removal work merges), and (2) the SHA of the **first removal commit** on the epic branch — so a future revival can diff or checkout either point.
* **Archive boards feature docs:** Preserve boards design history under `docs/features/boards/` in read-only form (linear-archive markers / sunset preamble) so spikes and **AST-379** lineage remain discoverable without implying active product scope.
* **Preserve spike CLIs only:** Keep board-related spike helper scripts under `scripts/spikes/` as unreferenced historical CLIs per Code Rules §3.6; they must not live under `src/`.

## Boundaries

* Does **not** change Google CSE roster cultivation, company-centric job ingest, qualify/evaluate consult pipeline, or any non-boards dispatch tasks.
* Does **not** revive, redesign, or partially re-enable boards UX or APIs — full removal only.
* Does **not** remove generic job-page scanning language in company/roster context; only the boards **channel** (saved board searches, board config registry, board-sourced job ingest) is in scope.
* Does **not** require deleting gitignored spike captures under `debug/spikes/` (already local-only).
* Does **not** delete or migrate production/staging board-sourced job or company rows — out of scope; pretend the data never existed.
* Does **not** remove `scripts/spikes/` board spike CLIs — historical R&D scripts stay; only `src/` boards product code goes.
* Must **not** break unrelated admin, candidate, or scheduler surfaces — verify `gaze_board` and board task keys are gone from schedulable/admin catalogs without regressing company or consult dispatch.
* Per Code Rules config-as-truth: removed enums, task keys, and nav entries must not leave orphaned references in `TASK_CONFIG`, dispatch seeds, or `ENTITY_TYPES`.

## Acceptance criteria

1. Grep-equivalent product check: no `BOARD_CONFIG`, `BOARDS_CONFIG`, `board_search` entity dispatch, `gaze_board` task key, or `/api/boards` routes under `src/` on the epic publish ref.
2. Database schema on a fresh migrate/ensure reflects removal of board-only tables/columns; no application layer imports board-search DDL helpers.
3. `docs/ASTRAL_CODE_RULES.md` contains a **Sunset — Astral Boards** (or equivalent) section with rationale and **both** recorded SHAs: pre-removal `dev` tip at dispatch and first removal commit on the epic branch.
4. `docs/ASTRAL_TEST_BIBLE.md` and decomposed bible files contain no boards manifests that imply active test obligations; Betty's component suite is green on the publish ref.
5. `docs/features/boards/` remains as historical archive only (clear sunset/archive framing at folder or index level).
6. Admin Scheduled Actions and nav config show no board-search or `gaze_board` entries (extends **AST-649** completeness to backend removal).
7. No board-specific component tests remain except any explicitly marked historical fixtures tied to the archive doc — default is delete.
8. Board spike CLIs remain under `scripts/spikes/` only; no boards implementation remains under `src/`.

## Dependencies and blockers

* **AST-648** / **AST-649** (Done) — board search UI already removed; this epic completes backend and docs cleanup they intentionally left dormant.
* none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-757 (parent) | ftr/AST-757-sunset-astral-boards |
| AST-765 | sub/AST-757/AST-765-remove-boards-src-and-board-only-tests |
| AST-766 | sub/AST-757/AST-766-drop-board-search-schema |
| AST-767 | sub/AST-757/AST-767-sunset-boards-documentation |

**Pre-removal** `dev` **SHA (dispatch):** `8d9b01e5e75ace9c04c32711488430503075e0c3`

**Epic worktree:** `astral-AST-757/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |

---

## Original brief

At one time, I had envisioned doing board scrapes for job searches for our candidates, but I have since realized that our Google CSE roster cultivation approach is a much stronger approach.

I would like us to archive the astral boards feature completely so that it does not continue to be a "hangnail" in our design considerations.  I think this would also need an update to the test bible and an explicit note in the astral_code_rules to explain its removal and which commit SHA had the last boards code on it in case we ever need to revive it.

### Comments

#### chuckles — 2026-06-23T19:04:34.210Z
@susan Open questions before dispatch:

1. **Production data:** Should board-sourced jobs and placeholder board companies already in live/staging databases be **deleted**, **left orphaned**, or **migrated** to a neutral state — or is schema/code removal sufficient with no data purge?
2. **`scripts/spikes/` board spike CLIs:** Delete with the epic, or keep as unreferenced historical scripts under Code Rules §3.6?
3. **Last-boards SHA capture:** Record the **`dev` tip SHA at dispatch** (before removal work merges), at **first removal commit**, or via an explicit **`git tag`** you choose at prep-UAT?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
