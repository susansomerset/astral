# AST-598 — Restructure ASTRAL_TEST_BIBLE.md into per-component bible files

<!-- linear-archive: AST-598 archived 2026-06-23 -->

## Linear archive (AST-598)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-598/restructure-astral-test-biblemd-into-per-component-bible-files  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The test bible is a single ~1,800-line markdown file that every Betty `qa-child` pass appends to. When sibling `sub/*` branches merge through `ftr/*`, those append-only edits collide in one file — repeated merge pain, rollup `@Betty` cycles, and no clean ownership boundary per ticket. Splitting the bible into a directory tree aligned with `tests/component/` gives Betty a natural edit surface per component area, reduces cross-branch conflicts, makes stale manifest rows easier to spot, and lets Radia scope bible compliance reviews to the files a ticket actually touched. This is documentation and workflow structure only; it does not change product behavior or test assertions.

## Functional scope

* **Tree layout:** Replace `docs/ASTRAL_TEST_BIBLE.md` with `docs/test-bible/` mirroring `tests/component/` layer folders (`core/`, `data/`, `external/`, `utils/`, `ui/`, `frontend/`, `dev/`). Extend Susan's draft list to a **full mirror**: every Python test module under `tests/component/` gets a matching bible file (e.g. `test_gazer.py` → `core/gazer.md`; `test_boards.py` → `core/boards.md`; not only the eight core modules in the original sketch).
* **Standards vs component content (not integration testing):** Some monolith sections are **process rules for all component tests**, not coverage for one module — e.g. where tests live, Python vs frontend branch-coverage policy, Betty's routed-page manifest rules, the shared branch-lock list, and harness appendix notes. These are **not** integration tests (`tests/integration/` stays a placeholder). They live once in `docs/test-bible/README.md` (index + standards). Component files hold only that module's coverage map, fixture notes, and ticket manifest blocks.
* **Ticket manifest blocks:** Relocate each former §7.13* block into the component bible file(s) for the tests it references. **Drop §7.13 numbering**; use `### AST-NNN` headers instead. Append new manifests only inside the file(s) for modules that ticket touched — same append habit, smaller blast radius.
* `data/database` **clusters:** Mirror the existing cluster split: one bible file per cluster under `docs/test-bible/data/database/` (matching each `tests/component/data/database/test_<cluster>.py`), plus a short `data/database.md` index for cluster conventions and `data/fixtures.md` for shared SQLite conftest notes. Avoid a single large `database.md` that recreates monolith merge pain.
* `frontend/` **shape:** Mirror `tests/component/frontend/` subfolders with **folder-level bible files** (`pages.md`, `components.md`, `lib.md`, `hooks.md`, `contexts.md`, plus a small root file for App/routes-level tests). Each file uses `### AST-NNN` sections per ticket — not one giant frontend file, not dozens of one-line files.
* **Entry point:** `docs/test-bible/README.md` links every layer folder, states Betty ownership, explains standards vs component files, and optionally maps retired monolith § ids to new paths for one release.
* **Repo workflow updates:** Update `docs/ASTRAL_TEAM_WORKFLOW.md`, `docs/ASTRAL_GIT_WORKFLOW.md`, pre-commit hooks, and script comments that still name the monolith so they reference `docs/test-bible/**`.
* **Agent skill updates (separate child at dispatch):** Susan confirmed skill files need their own sub-issue. Update `~/.cursor/skills/` (`qa-child`, `test-child`, `build-child`, `review-child`, `resolve-child`, `dispatch-parent`, `check-linear`, `do-all-the-things`) and `~/.cursor/agents/betty-AGENTS.md` so manifest contract, engineer ban paths, rollup/shasum instructions, and read-only review pointers use `docs/test-bible/` instead of the monolith. Blocked on or paired with the repo migration child.
* **Monolith retirement:** Delete `docs/ASTRAL_TEST_BIBLE.md` only after Betty's migration is complete **and Radia's review-child** confirms the tree is navigable and content-complete.
* **Ownership unchanged:** Betty remains sole writer of bible content on publish refs; engineers still do not commit bible files.

## Boundaries

* **No product code** under `src/` and no changes to test assertions under `tests/` except hook/script path strings.
* **No semantic rewrite** of manifest rows — split, relocate, re-header; do not merge or prune ticket history unless content is duplicate after split.
* **No change** to Betty's publish workflow (`origin/sub/*`, Joan `store-qa-commit`, Chuckles `merge-child` rollup) beyond which file paths Betty edits and rollup merging per-component files instead of one blob.
* **No integration-test program.**
* **Does not** bulk-fix historical markdown defects except incidental cleanup during migration.
* **Must not break** in-flight epics without a coordinated quiet window on Betty's integration line.

## Acceptance criteria

1. Searchable equivalence: every monolith section appears somewhere under `docs/test-bible/` (spot-check: README standards block includes routed-page manifest rules and branch-lock list; three `### AST-NNN` blocks from different layers present in the correct component files).
2. Full mirror: each `tests/component/**/test_*.py` and each frontend `test_*` module has a documented home under matching `docs/test-bible/` paths per structure decisions above.
3. `docs/test-bible/README.md` is sufficient for an agent to find the right component file without the deleted monolith.
4. `docs/ASTRAL_TEAM_WORKFLOW.md` and `docs/ASTRAL_GIT_WORKFLOW.md` reference `docs/test-bible/`, not the monolith, as canonical.
5. Agent skills and `betty-AGENTS.md` updated per the skill-update child; engineer pre-commit blocks `docs/test-bible/**`.
6. **Radia review-child** on Betty's migration branch documents completeness before monolith delete.
7. After deletion, active workflow docs/skills do not instruct agents to edit `docs/ASTRAL_TEST_BIBLE.md` (historical plan docs may mention it in passing).

## Dependencies and blockers

* **Coordination:** Open `sub/*` branches may still edit the monolith until migration lands on Betty's integration line.
* **none** for definition approval and dispatch planning.

## Open questions

none.

---

## Original brief

**Summary:** The current single `ASTRAL_TEST_BIBLE.md` is a chronological append log that creates merge conflicts whenever two sub branches touch overlapping test sections. Replace it with a tree of per-component bible files mirroring the `tests/component/` directory structure.

**Motivation:**

* Merge conflicts on the bible are a recurring source of branch spaghetti
* A single file gives Betty no natural scope boundary per ticket
* Obsolete tests are hard to identify when buried in a chronological log
* Per-component files make Radia's compliance review easier to scope

**Proposed structure:**

```
docs/test-bible/
  core/
    agent.md
    builder.md
    candidate.md
    consult.md
    dispatcher.md
    intake.md
    roster.md
    tracker.md
  data/
    database.md
  external/
    anthropic.md
    deepseek.md
  ui/
    api/
      api_admin.md
      api_candidate.md
      api_jobs.md
      api_resume_html.md
  utils/
    config.md
```

**Acceptance:**

* All content from `ASTRAL_TEST_BIBLE.md` migrated into the appropriate per-component file
* `ASTRAL_TEST_BIBLE.md` deleted
* All agent skills that reference the bible updated to point to the relevant per-component file
* Radia confirms the new structure in a review pass before the old file is deleted

**Assigned to:** Betty **Scope:** Docs/structure only — no product code changes

### Comments

#### chuckles — 2026-06-15T02:07:05.478Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-598 (parent) | ftr/ast-598-restructure-astral_test_biblemd-into-per-component-bible |
| AST-663 | sub/AST-598/AST-663-per-component-test-bible-migration |
| AST-664 | sub/AST-598/AST-664-agent-skill-updates-test-bible |

**Epic worktree:** `astral-AST-598/` — one active sub checked out at a time.

**Parent:** AST-598

AST-664 blockedBy AST-663 (Review Posted).

— Chuckles

#### chuckles — 2026-06-15T01:49:07.722Z
[fix-uat] blocked — @susan

**Your question:** No — nothing from AST-598 is on `origin/dev` yet. There is no `origin/ftr/AST-598*` and no `sub/AST-598/*`; the monolith `docs/ASTRAL_TEST_BIBLE.md` is still canonical on `origin/dev` and `origin/tests`.

**Why fix-uat can't run:** This epic was never dispatched (no children, no integration branch). I can't file Bug children or seed `sub/*` without `origin/ftr/<parent-segment>` per dispatch §8c.

**Pick one:**
1. Move parent back to **Todo**, assign Chuckles → **dispatch-parent** (Betty migration + skill-update child), then normal UAT cycle; or
2. Reply here with concrete **UAT:** failures if you tested something else — I'll file bugs once `ftr` exists.

— Chuckles

#### susan — 2026-06-15T01:47:31.858Z
@chuckles Chuckles, can you confirm if the feature has already been commited to dev origin?  if not, let me know here.

#### chuckles — 2026-06-15T01:44:21.305Z
@susan — finish-up blocked: no `origin/ftr/AST-598*` branch (and no `sub/*`); monolith bible still on `origin/dev`/`origin/tests`. PR Ready with nothing to land — dispatch + Betty migration first, or move parent back if premature.

— Chuckles

#### chuckles — 2026-06-15T00:08:29.306Z
@susan — six open questions in Description need your call before dispatch:

1. File granularity: full mirror of every tested component area, or only the draft subset with catch-all layer files?
2. Cross-cutting sections (§2, §6, §6c, §7.12, Appendix A): single index/README vs per-layer duplication?
3. §7.13 ticket-append blocks: keep chronological § numbering inside component files, or reorganize by module?
4. `data/database`: one `database.md` vs per-cluster files mirroring `tests/component/data/database/`?
5. `frontend/`: full subtree mirror vs fewer grouped files?
6. Radia gate: dedicated review-child on migration branch, or your Linear sign-off on this parent?

— Chuckles

#### susan — 2026-06-14T23:22:24.131Z
Okay, you'll need to create a subissue to handle those changes as well.

#### chuckles — 2026-06-14T23:04:40.510Z
[check-linear] **Skill / workflow files to update when `docs/test-bible/` lands**

**Must change (manifest contract):**
- **`~/.cursor/skills/qa-child/SKILL.md`** — sole authority becomes **`docs/test-bible/**`** (mirror `tests/component/`); Betty edits only the component file(s) touched by the ticket; manifest cites **file paths + test node ids** (drop monolith **`§7.13z*`** numbering); **`ftr/` rollup** merges per-component files instead of one blob; shasum line lists changed bible paths.
- **`~/.cursor/agents/betty-AGENTS.md`** — same path + ownership wording.

**Ban / read-only pointers (path swap):**
- **`build-child`**, **`test-child`**, **`resolve-child`** — engineer test-tree ban: **`docs/test-bible/**`** replaces **`docs/ASTRAL_TEST_BIBLE.md`**.
- **`review-child`** — read-only context → relevant component bible file(s).
- **`do-all-the-things`** — resume prompts / FIX-UAT bible re-read gate → tree path.
- **`dispatch-parent`** — orientation read list.
- **`check-linear`** — merge-conflict routing example paths.

**Repo docs / hooks (Betty ticket, but list for completeness):**
- **`docs/ASTRAL_GIT_WORKFLOW.md`**, **`docs/ASTRAL_TEAM_WORKFLOW.md`** — Betty ownership + engineer ban rows.
- **`scripts/testing/run_component_tests.sh`**, **`check_frontend_coverage.py`** — comments referencing **`§6b`** → new location (likely **`docs/test-bible/README.md`** or **`ui/frontend.md`**).
- **Pre-commit hook** on **`astral-tests`** (if it blocks **`ASTRAL_TEST_BIBLE.md`**) → **`docs/test-bible/**`**.

**Suggested add-on in AST-598:** **`docs/test-bible/README.md`** — index + “which file for which layer”; optional one-release mapping from old **`§`** ids.

**Out of scope for skills:** plan docs under **`docs/features/**`** (historical); update opportunistically only.

— Chuckles

#### susan — 2026-06-14T02:12:25.467Z
@chuckles When this is implemented, what will need to change in the skill files to support the new manifest?

---

_Implementation detail may live in git history on `origin/dev`._
