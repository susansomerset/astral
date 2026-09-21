# AST-1078 — Small bug: Headers for Job Lists

<!-- linear-archive: AST-1078 archived 2026-08-07 -->

## Linear archive (AST-1078)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1078/small-bug-headers-for-job-lists  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Job list tables that show per-vector grade columns must stay compact enough to scan. Full vector labels as column headers widen the table and defeat the shared compact-header contract from AST-437. This epic restores two-letter vector codes as the visible headers, with the full vector name available on hover, so Skipped / In Review (and any sibling list using the same column builder) remain readable after the AST-1059 rubric-hydration work. While touching that display path, grade-dot (matrix) hover text must also surface rubric criterion text plus a parenthetical confidence description so Susan can read a cell without opening the job.

## Functional scope

* Grade-column headers on Jobs list tables that paint per-vector grades show the **two-letter vector code** only (not the full vector label).
* Hovering a grade-column header shows the **full vector name** (existing compact tooltip shape: label with importance, e.g. `Employment Type (8)` — same AST-437 contract).
* When a column has no stored vector `code` (grades-only / pre-snapshot rows), the UI still resolves a compact two-letter header — never leaves the full vector string in the `<th>` text.
* Skipped and In Review list tables stay consistent with each other for header text vs tooltip (same compact code + tooltip behavior).
* Hovering a **grade-dot / matrix icon** (the letter cell next to confidence bullets) shows the **rubric text** for that grade (job reason when present, otherwise the criterion grade description) **and** a **parenthetical description of the confidence rating** for that cell.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (canon UI catalog only has `pattern.ui.admin-endpoint`; compact job-list header/tooltip behavior lives in the AST-437 shared `JobListRubricColumn` contract, not a named pattern id).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` (touch only job-list header/column/grade-dot display surfaces); `astral.standards.dry-and-focused-functions` (fix shared column/tooltip helpers once; do not fork per page); `astral.ui.frontend-file-placement` (frontend lib + Jobs list pages); `astral.layers.ui-config-driven-business-logic` (codes/labels/confidence come from job payload — no new hardcoded vector name sets); `astral.docs.features-single-file-per-ticket` (one plan doc per child).

## Boundaries

* Does **not** change rubric artifact editors, analysis-report headers, or Admin Vector Feedback hydration.
* Does **not** change Score columns, group-by-aligned-rubric partitioning, or job-carried `*_rubric` snapshot writes (AST-1063/1064 stay as landed).
* Does **not** redesign Recommended Jobs list phase-score columns (those are not per-vector grade headers).
* Does **not** invent new vector codes in config or backfill historical `*_rubric` snapshots.
* Does **not** redesign the visual ConfidenceBullets glyph itself beyond what is needed so its meaning appears in the grade-dot hover text.
* Must not break sorting/matching of grades to columns (identity keys stay usable even when display header is compact).

## Acceptance criteria

1. On Skipped and In Review Jobs list sections that show per-vector grade columns, each grade `<th>` visible text is a two-letter (or short) vector **code**, not the full vector label.
2. Hovering that `<th>` shows a tooltip with the full vector name (label; importance retained per AST-437).
3. For a group whose jobs only have grades (no job-carried `*_rubric`), headers are still compact codes — e.g. a vector like `Technical (TE)` does **not** appear as the full string in the header cell.
4. Skipped and In Review both show compact codes in the header cell (no page still rendering the long label while the other shows the code).
5. Grade dots still align under the correct columns; sorting by a grade column still works.
6. Hovering a grade-dot on Skipped and In Review shows rubric criterion text for that letter (reason when present, else grade description) **and** a parenthetical confidence description when confidence is present on the cell.

## Dependencies and blockers

none. ([AST-1059](https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages) / [AST-1063](https://linear.app/astralcareermatch/issue/AST-1063/job-carried-rubric-hydration-for-list-columns-issue-with-the-rubric) / [AST-1064](https://linear.app/astralcareermatch/issue/AST-1064/group-by-aligned-rubric-jobs-list-tables-issue-with-the-rubric-grade) are Done; this is a follow-on display fix on that stack.)

## Open questions

none.

## Proposed child tickets

#### 1: **Compact vector codes and grade-dot tooltips on job lists - Katherine**

One UI slice: shared job-list rubric column builder always emits compact `headerCode` (including grades-only fallback); Skipped / In Review render that compact code in the header cell with the full-name tooltip; grade-dot hover includes rubric text plus parenthetical confidence. Does **not** own rubric snapshot writes, grouping, or Recommended phase-score layout.
**Citations:** `astral.standards.dry-and-focused-functions`; `astral.ui.frontend-file-placement`; `astral.standards.in-scope-only`.

**Monolith check:** Functional scope bullets are one inseparable display contract (builder + both list pages + grade-dot hover) — single child intentional.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-1078](https://linear.app/astralcareermatch/issue/AST-1078/small-bug-headers-for-job-lists) (parent) | ftr/AST-1078-headers-for-job-lists |
| [AST-1086](https://linear.app/astralcareermatch/issue/AST-1086/compact-vector-codes-and-grade-dot-tooltips-on-job-lists-small-bug) | sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips |

**Epic worktree:** `astral-AST-1078/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/76bd7e6193cbd12e5d5db1c6e922b0c1/3a96093d-30b6-45bf-93e6-190c0dae9a78/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/e7d725cb-da4c-4747-871f-7a4a849f7455/store.db` |
| Radia | review | `/home/susan/.cursor/chats/76bd7e6193cbd12e5d5db1c6e922b0c1/f8658bda-ea58-433c-8041-1c20336d09c9/store.db` |

---

## Original brief

When displaying the job lists by header, use the two-letter vector code as the column header and tooltip them with the full vector name, so that the table can display in a compact display.

### Comments

#### chuckles — 2026-07-31T00:38:38.911Z
[refresh-ftr] blocked: CONFLICT files while merging `origin/dev` into `origin/ftr/AST-1078-headers-for-job-lists` (attempt 1/3):

**@Betty White** (bible / test-tree):
- `docs/test-bible/utils/config.md`
- `tests/component/utils/test_config.py`
- `data/merge_ticket_log.json` (take a coherent merge of both sides — keep all landed parent ids)

Resolve on a worktree with `origin/ftr/AST-1078-headers-for-job-lists` + merge `origin/dev`, commit, push to `origin/ftr/AST-1078-headers-for-job-lists`. Then Chuckles will re-run refresh-ftr.

— Chuckles

#### chuckles — 2026-07-31T00:13:02.854Z
[check-linear] In Progress — grade-dot tooltips (rubric text + parenthetical confidence) already in epic scope / AC; shipping on the open child.

— Chuckles

#### susan — 2026-07-30T16:54:11.911Z
@chuckles While we are in there, let's make sure the tooltip for the icons in the matrix do popups of the rubric text as well as a parenthetical description of the confidence rating.

---

_Implementation detail may live in git history on `origin/dev`._
