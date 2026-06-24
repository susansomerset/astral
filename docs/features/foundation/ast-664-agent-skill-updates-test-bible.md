<!-- linear-archive: AST-664 archived 2026-06-23 -->

## Linear archive (AST-664)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-664/agent-skill-updates-for-test-bible-tree-restructure-astral-test  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-598 — Restructure ASTRAL_TEST_BIBLE.md into per-component bible files  
**Blocked by / blocks / related:** parent: AST-598

### Description

## What this implements

Update `~/.cursor/skills/` (`qa-child`, `test-child`, `build-child`, `review-child`, `resolve-child`, `dispatch-parent`, `check-linear`, `do-all-the-things`) and `~/.cursor/agents/betty-AGENTS.md` so manifest contract, engineer ban paths, rollup/shasum instructions, and read-only review pointers use `docs/test-bible/` instead of the monolith. Engineer pre-commit blocks `docs/test-bible/**`.

## Acceptance criteria

5. Agent skills and `betty-AGENTS.md` updated; engineer pre-commit blocks `docs/test-bible/**`.
6. After sibling migration lands, active workflow docs/skills do not instruct agents to edit `docs/ASTRAL_TEST_BIBLE.md`.

## Boundaries

* Does not perform bible content migration — sibling **Per-component test bible migration** ticket (Betty).
* Skills live outside the product repo; publish via engineer workflow on `sub/*`.
* Blocked until Betty migration branch has `docs/test-bible/` tree on `origin/ftr/`.

## Notes for planning

See Chuckles `[check-linear]` comment on parent AST-598 for the file checklist. Pair with Betty migration landing on `ftr`.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-598-restructure-astral_test_biblemd-into-per-component-bible`, child `sub/AST-598/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-15T05:58:42.690Z
**Review** — `origin/dev...origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` @ `d5a55d2d` (post-review doc: tip after push)

### What's solid

- Eight global skills + four agent handoffs + `~/.cursor/hooks/pre-commit/engineer.sh`: manifest contract, engineer bans, rollup/shasum, and read-only review pointers use **`docs/test-bible/**`**; transitional monolith ban retained.
- **`qa-child`**: sole writer is the tree; **`### AST-NNN`** manifest registry; per-path shasum; no instruction to append new manifests to **`docs/ASTRAL_TEST_BIBLE.md`**.
- **`build-child` / `test-child` / `resolve-child`** + engineer **AGENTS.md**: ban **`docs/test-bible/**`** alongside monolith; hook blocks **`docs/test-bible/*`**.
- **`review-child`**, **dispatch-parent**, **check-linear**, **do-all-the-things**: README + component file pointers / skip lists updated.
- Betty manifest in **`docs/test-bible/README.md` § AST-664**: narrowed **`tests/component`** smoke documented correctly (workflow-only; skip zero-arg **LOCKED_AT_100** gate).
- **`test_api_admin.py`** **`run_task`** mock (**ui_initiated**) — Betty **AST-653** handoff; matches manifest.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| advisory | Branch diff vs plan “repo plan only” | Diff includes **AST-663** tree + Betty **merge-tests** + workflow doc pointer updates from **`ftr`** integration — expected on **`sub/*`**, not **AST-664** engineer product scope. |
| advisory | **`.gitignore`** `/AGENTS.md` | **AST-663** root-anchor fix; consistent, out of **AST-664** record. |

**fix-now:** none  
**discuss:** none

### Recommended actions

- **Ada:** **resolve-child** — no product changes; acknowledge and advance when ready.
- **AST-598 parent:** monolith retirement remains a separate Radia gate after siblings land.

Plan review section: `docs/features/foundation/ast-664-agent-skill-updates-test-bible.md` (Radia doc commit on publish ref).

#### betty — 2026-06-15T05:55:03.353Z
`[check-linear]`

Cleared Ada's **`[qa-handoff]`** — narrowed workflow manifest: **do not** run zero-arg harness ( **`LOCKED_AT_100`** gate fails on **`sub/*`** replay unrelated to AST-664).

**Manifest delta (item 1):** `./scripts/testing/run_component_tests.sh tests/component` — pytest green is pass criterion; skips **`$# == 0`** coverage gate + Vitest tail. Item 2 (plan audit) unchanged.

**Publish:** `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` @ **`d5a55d2d`** (`merge-tests(AST-664): origin/tests 5aed6dc8`).

**Bible shasum:** `docs/test-bible/README.md` → `c426e8f50aabc49d8be2c2331a8252522b1c2743`

Assignee → **Ada** for **`test-child`** re-run. Status stays **Tests Ready**.

#### ada — 2026-06-15T05:53:35.737Z
`[qa-handoff]`

**Re-run** on `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` @ **`db3a2593`** after Betty **`ui_initiated`** fix.

**Manifest item 1** — `./scripts/testing/run_component_tests.sh` (zero args):

- **pytest:** **1528 passed**, 2 skipped — **green** (including `TestDispatchTasks::test_scheduler_and_run_controls`)
- **Harness exit 1:** `check_per_file_coverage.py` — 14 `LOCKED_AT_100` files below 100% branch (e.g. `config.py` 93.5%, `roster.py` 79.5%). **`HEAD` is not contained in `origin/ftr/*`**, so **`ASTRAL_FTR_COVERAGE_INTEGRATION`** does not apply per `run_component_tests.sh` / README §7.12b.
- Vitest tail never runs (script `set -e` after coverage gate).

**Why test/manifest, not product:** AST-664 has no `src/**` commits. Zero-arg full harness + branch-lock gate is documented as unreliable on **`sub/*`** until locks regain 100% (see `docs/test-bible/utils/config.md` **AST-483** note). Workflow-only ticket should not require restoring all `LOCKED_AT_100` files.

**Manifest item 2 (plan audit):** **OK** — Implementation record lists eight skills + four agent handoffs + hook verification.

**Ask:** Revise **Tests Ready** manifest to a **narrowed** command that skips the `$# == 0` coverage gate (e.g. pytest-only smoke or the single fixed node), **or** explicitly accept **pytest green** as pass criterion for this workflow child. Republish + reassign Ada.

@Betty White

#### betty — 2026-06-15T05:51:12.395Z
`[check-linear]`

Cleared Ada's **`[qa-handoff]`** — **`TestDispatchTasks::test_scheduler_and_run_controls`** mock now accepts **`ui_initiated`** (**AST-653** / `origin/dev` product; unrelated to AST-664 workflow scope).

**Fix:** `tests/component/ui/api/test_api_admin.py` — `run_task` monkeypatch `lambda task_id, ui_initiated=False: True`; README **`### AST-664`** block notes handoff revision.

**Publish:** `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` @ **`db3a2593`** (`merge-tests(AST-664): origin/tests 7776dc3c`). Single **`merge-tests`** on sub (rewound before first delivery).

**Bible shasum:** `docs/test-bible/README.md` → `d0c11906a043a016ce29f9cf81fdcdfb3c0a6475`

Assignee → **Ada** for **`test-child`** re-run. Status stays **Tests Ready**.

#### ada — 2026-06-15T05:47:54.366Z
`[qa-handoff]`

**Manifest item 1** — `./scripts/testing/run_component_tests.sh` (zero args) on `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` @ `3b51dd71`:

**Result:** 1527 passed, 2 skipped, **1 failed**

```
FAILED tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls
TypeError: ...<lambda>() got an unexpected keyword argument 'ui_initiated'
```

**Why test/manifest, not AST-664 product:** This child has **no** `src/**` or `tests/**` commits (plan + bible manifest only). Product on `origin/dev` calls `run_task(task_id, ui_initiated=True)` in `api_admin.py:1201` (**AST-653**). The test still monkeypatches `run_task` with `lambda task_id: True` — mock does not accept `ui_initiated`.

**Plan audit (item 2):** Implementation record in `docs/features/foundation/ast-664-agent-skill-updates-test-bible.md` lists all eight skills + four agent handoffs + hook verification — spot-check OK.

**Ask:** Update the mock in `test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls` (or narrow manifest to exclude this unrelated failure if full harness is intentionally out of scope for workflow-only tickets). Republish `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` and reassign Ada.

@Betty White

#### betty — 2026-06-15T05:46:21.187Z
## QA test manifest (AST-664 — global skills / workflow)

**Publish:** `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` @ `3b51dd71` (`merge-tests(AST-664): origin/tests 36935ab1`)

**Bible shasum:** `docs/test-bible/README.md` → `a373d1ed70a7458b52b7caae030e1a989e80c33b`

**Scope delivered (Betty):** `### AST-664` manifest block in `docs/test-bible/README.md` — manifest-only; global skill/agent/hook updates documented in plan **Implementation record** (outside repo git).

**Manifest (test-child):**

1. **`./scripts/testing/run_component_tests.sh`** — full harness regression (zero args); no product or test-tree changes on this ticket.
2. **Plan audit:** Confirm **Implementation record** in `docs/features/foundation/ast-664-agent-skill-updates-test-bible.md` lists all eight skills + four agent handoffs + hook verification (read-only spot-check acceptable).

**Existing coverage (bible-backed):** No new pytest/Vitest files — workflow-only ticket per plan boundaries.

**Broken / obsolete tests:** None expected.

**Notes:** Engineer **`test()`** commit on publish ref should be **`test(AST-664): …`** if any product fix is needed (unlikely). If manifest or hook verification fails, **`[qa-handoff]`** → Betty.

#### hedy — 2026-06-15T05:38:59.753Z
Plan: [`docs/features/foundation/ast-664-agent-skill-updates-test-bible.md`](https://github.com/susansomerset/astral/blob/sub/AST-598/AST-664-agent-skill-updates-test-bible/docs/features/foundation/ast-664-agent-skill-updates-test-bible.md) @ `5acc8190`

Seven build stages: (1) **`qa-child`** manifest/rollup/shasum → **`docs/test-bible/**`** + `### AST-NNN`; (2) **`betty-AGENTS.md`**; (3) engineer bans in **`build-child`**, **`test-child`**, **`resolve-child`**; (4) **`review-child`** read-only pointers; (5) **`dispatch-parent`**, **`check-linear`**, **`do-all-the-things`**; (6) verify engineer hook + **`ada`/`hedy`/`katherine` AGENTS** ban lines; (7) publish + Implementation record. Path mirror table in plan. Depends on **AST-663** tree on **`ftr`** (present).

**Scope:** `scope-Single-Component` — global skills/agents/hook only; no product or bible content.

**Conf:** `conf-high` — Chuckles parent checklist + **AST-598** AC #5 fix the contract; **AST-663** already landed the tree.

**Risk:** `risk-Medium` — stale monolith references would break Betty/engineer handoffs or reintroduce bible merge conflicts under the new tree.

---

# AST-664 — Agent skill updates for test-bible tree

- **Linear (this ticket):** [AST-664](https://linear.app/astralcareermatch/issue/AST-664/agent-skill-updates-for-test-bible-tree-restructure-astral-test)
- **Parent:** [AST-598](https://linear.app/astralcareermatch/issue/AST-598/restructure-astral-test-biblemd-into-per-component-bible-files)
- **Publish ref:** `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` (child of AST-598; not Linear `gitBranchName`)

## Summary

Update global Cursor skills and Betty’s AGENTS handoff so the **per-component test bible tree** (`docs/test-bible/**`) is the sole workflow authority for manifests, engineer bans, rollup/shasum verification, and read-only review context — replacing instructions that still point at the monolith `docs/ASTRAL_TEST_BIBLE.md`. Confirm the engineer pre-commit hook blocks `docs/test-bible/**`. No product code, no bible content migration (sibling **AST-663**), no edits under `tests/`.

## Dependency note

**AST-663** (`blockedBy` in Linear) delivered the `docs/test-bible/` tree on **`origin/ftr/ast-598-restructure-astral_test_biblemd-into-per-component-bible`**. Before **build-child**, verify that ref contains `docs/test-bible/README.md` and the layer index. The monolith may still exist until Radia retires it; skills must treat **`docs/test-bible/**`** as canonical for new manifest work while allowing transitional mentions of the monolith only as “retired / do not edit.”

## Path resolution helper (use in all skills)

When a skill needs “which bible file for this test or module,” apply this mirror (also documented in `docs/test-bible/README.md`):

| Test path pattern | Bible path |
| --- | --- |
| `tests/component/<layer>/test_<module>.py` | `docs/test-bible/<layer>/<module>.md` |
| `tests/component/data/database/test_<cluster>.py` | `docs/test-bible/data/database/<cluster>.md` |
| `tests/component/ui/api/test_api_<name>.py` | `docs/test-bible/ui/api/api_<name>.md` |
| `tests/component/frontend/<folder>/test_*.tsx` | `docs/test-bible/frontend/<folder>.md` (folder-level, not per file) |
| Cross-cutting standards (§2, §6, §6c, §7.12, appendix) | `docs/test-bible/README.md` |

**Manifest headers:** Ticket blocks use `### AST-NNN` inside the component bible file(s) for modules that ticket touched — **not** monolith `§7.13z*` numbering.

## Out of scope (explicit)

| Item | Owner |
| --- | --- |
| Bible content split / migration | **AST-663** (Betty) |
| `docs/ASTRAL_TEAM_WORKFLOW.md`, `docs/ASTRAL_GIT_WORKFLOW.md` repo edits | **AST-663** (already on `ftr`) |
| Deleting `docs/ASTRAL_TEST_BIBLE.md` | **AST-598** after Radia gate |
| Historical `docs/features/**` plan mentions of monolith | Opportunistic only — do not bulk-edit |

## Files Changed (planned)

| File | Change | Layer |
| --- | --- | --- |
| `~/.cursor/skills/qa-child/SKILL.md` | Manifest contract → `docs/test-bible/**`; rollup/shasum; drop §7.13z* | global skill |
| `~/.cursor/agents/betty-AGENTS.md` | Ownership + session read path | global agent |
| `~/.cursor/skills/build-child/SKILL.md` | Engineer test-tree ban paths | global skill |
| `~/.cursor/skills/test-child/SKILL.md` | Ban + context read paths | global skill |
| `~/.cursor/skills/resolve-child/SKILL.md` | Pre-commit diff guard paths | global skill |
| `~/.cursor/skills/review-child/SKILL.md` | Read-only bible pointers | global skill |
| `~/.cursor/skills/dispatch-parent/SKILL.md` | Hot-file / orientation read list | global skill |
| `~/.cursor/skills/check-linear/SKILL.md` | Merge-conflict example path | global skill |
| `~/.cursor/skills/do-all-the-things/SKILL.md` | Resume skip list + FIX-UAT bible gate | global skill |
| `~/.cursor/agents/ada-AGENTS.md` | Workspace guard ban line (match build-child) | global agent |
| `~/.cursor/agents/hedy-AGENTS.md` | Same | global agent |
| `~/.cursor/agents/katherine-AGENTS.md` | Same | global agent |
| `~/.cursor/hooks/pre-commit/engineer.sh` | Verify `docs/test-bible/*` blocked (add if missing) | global hook |
| `docs/features/foundation/ast-664-agent-skill-updates-test-bible.md` | This plan + Implementation record | docs (repo) |

**No** `src/**`, `tests/**`, or `docs/test-bible/**` edits in **AST-664** commits.

## Stage 1: `qa-child` — sole authority and manifest contract

**Done when:** `~/.cursor/skills/qa-child/SKILL.md` names **`docs/test-bible/**`** as Betty’s sole bible write surface; manifest steps cite **file paths + pytest node ids** and `### AST-NNN` blocks; rollup/shasum/land-preflight sections reference per-component files; no instruction tells Betty to append new manifests to `docs/ASTRAL_TEST_BIBLE.md`.

1. In the YAML **`description:`** front matter (lines 3–8), replace **`ASTRAL_TEST_BIBLE`** with **`docs/test-bible/**`** (per-component tree mirroring `tests/component/`).

2. In **§ intro paragraph** (line ~13 “sole authority on **`docs/ASTRAL_TEST_BIBLE.md`**”): Replace with sole authority on **`docs/test-bible/**`** — the per-component tree mirroring **`tests/component/`**. Betty edits **only** the component file(s) for modules this ticket touches plus **`docs/test-bible/README.md`** when cross-cutting standards change.

3. Replace every remaining **`docs/ASTRAL_TEST_BIBLE.md`** reference in the skill using this mapping:
   - **Authority / read-before-manifest:** → **`docs/test-bible/README.md`** for standards + grep/read the component file(s) from the **Path resolution helper** for modules in the plan diff.
   - **Engineer ban cross-ref:** → **`docs/test-bible/**`** (engineers never commit bible files).
   - **§6c UI manifest rules:** → **`docs/test-bible/README.md` §6c** (not monolith §6c).
   - **§7.13z* registry / epic § layout:** → Before adding a manifest block, read existing **`### AST-NNN`** headings in the target component file(s) on **`origin/ftr/<parent-segment>`** — do not duplicate the same ticket block; prefer one **`### AST-NNN`** per child in the file for the primary test module.
   - **Rollup conflict routing:** → If rollup conflicts **only** under **`docs/test-bible/**`**, **`@Betty`** re-runs **`qa-child`**: merge **`origin/ftr/<parent-segment>`**, keep rolled **`### AST-NNN`** blocks, append this child’s block only in the correct component file(s).
   - **shasum verify (§ Test Bible Verify):** → When bible changed this pass, for **each** touched path under **`docs/test-bible/`**, record **`git show origin/<publish-ref>:<path> | shasum`** in the Linear manifest comment (one line per file, or a single line listing paths + combined note if only README moved).
   - **§3 FIX-UAT full re-read gate:** → Full tree re-read **only** if **`docs/test-bible/**`** changed on **`origin/ftr/<parent-segment>`** since this parent’s last qa pass; otherwise grep manifest-relevant sections in README + touched component files and the bug plan delta only.
   - **§6 manifest bullet “from ASTRAL_TEST_BIBLE”:** → “from **`docs/test-bible/`** component file(s) and the repo”.
   - **§7 git add paths:** → **`git add`** test-tree paths **plus** **`docs/test-bible/**`** paths Betty updated (not **`docs/ASTRAL_TEST_BIBLE.md`** unless AST-598 retirement pass explicitly retires the monolith — out of scope here).
   - **§10 Linear comment shasum:** → Same per-path shasum rule as Verify bullet above.

4. In **§ Test Bible — sole authority** rules list (items 1, 3, 7, Land preflight, Chuckles `@Betty` paragraph): replace monolith filename with **`docs/test-bible/**`** and per-component rollup wording from step 3.

5. Remove **§7.13z* registry** heading text; replace section title with **`### AST-NNN manifest registry`** and body from step 3 epic § layout bullet.

6. Add one short subsection after **§6 Design the manifest** (before **§ Test Bible**):

   **`#### Component file selection (AST-598)`**

   > For each manifest line, name the pytest path. Map to bible file via the mirror table in **`docs/test-bible/README.md`** (see this plan **Path resolution helper**). Append new **`### AST-NNN`** blocks only inside those component files. Standards-only updates (§6c, branch locks, harness appendix) go in **`docs/test-bible/README.md`** once — not duplicated in every component file.

7. Do **not** change Betty git surface, **`merge-tests()`** mechanics, **`astral-tests`** worktree rules, or Linear status gates.

⚠️ **Decision:** During monolith retirement transition, **`qa-child`** may still *read* the monolith on old branches for historical context, but must **never instruct Betty to write** new manifests to **`docs/ASTRAL_TEST_BIBLE.md`**.

## Stage 2: `betty-AGENTS.md`

**Done when:** Betty’s handoff doc points at the tree and README; no “read monolith at session start” without tree path.

1. In **`~/.cursor/agents/betty-AGENTS.md`**, line 3: change **`docs/ASTRAL_TEST_BIBLE.md`** → **`docs/test-bible/**`** (per-component test bible; Betty sole writer).

2. Line 28 **Standards**: Replace **`Read docs/ASTRAL_TEST_BIBLE.md at session start`** with **`Read docs/test-bible/README.md at session start; open component file(s) per ticket using the mirror in README § Tree layout`**.

3. **Test ownership** (if present elsewhere): engineers do not commit **`docs/test-bible/**`**.

## Stage 3: Engineer skills — test-tree ban paths

**Done when:** **`build-child`**, **`test-child`**, and **`resolve-child`** ban **`docs/test-bible/**`** alongside the transitional monolith ban; context reads point at tree + README.

### 3a. `build-child/SKILL.md`

1. In **§7 Test-tree ban** (line ~115): extend the ban list to:

   **`tests/`**, **`scripts/test_*.py`**, **`scripts/testing/`**, **`docs/ASTRAL_TEST_BIBLE.md`**, **`docs/test-bible/**`**.

   Add one sentence: **Betty** owns all bible paths under **`docs/test-bible/**`** at **Code Complete** (`qa-child`).

### 3b. `test-child/SKILL.md`

1. **§2 Test-tree ban** (line ~14): same path list as **3a**.

2. **§3 Load the run book** (line ~55): Replace monolith-only read with:

   > **`docs/test-bible/README.md`** and the component bible file(s) for manifest modules — context for why Betty chose paths; do **not** override her manifest silently.

3. **§5 git** (line ~78): Replace **`ASTRAL_TEST_BIBLE.md`** in merge bullet with **`docs/test-bible/**`** (Betty publishes tests + bible to **`sub/*`**).

### 3c. `resolve-child/SKILL.md`

1. **§9 pre-commit diff guard** (line ~104): extend to:

   **`tests/`**, **`scripts/test_*.py`**, **`scripts/testing/`**, **`docs/ASTRAL_TEST_BIBLE.md`**, **`docs/test-bible/**`**.

## Stage 4: `review-child` — read-only pointers

**Done when:** Review skill tells Radia to read README + relevant component file(s), not the monolith as primary.

1. **§3 Read the rules** (line ~47): Replace optional monolith read with:

   > **`docs/test-bible/README.md`** for standards; **`docs/test-bible/<layer>/<module>.md`** (per **Path resolution helper**) for coverage intent matching the ticket manifest or diff — **read-only**; Betty owns edits via **`qa-child`**.

2. **§ Reviewer scope** intro (line ~21): replace **`docs/ASTRAL_TEST_BIBLE.md`** in the list with **`docs/test-bible/**`**.

## Stage 5: Orchestration skills — `dispatch-parent`, `check-linear`, `do-all-the-things`

**Done when:** Dispatch hot-file list, check-linear conflict example, and do-all-the-things resume/FIX-UAT gates use tree paths.

### 5a. `dispatch-parent/SKILL.md`

1. **Hot files** list (line ~96): replace **`docs/ASTRAL_TEST_BIBLE.md`** with **`docs/test-bible/**`**.

### 5b. `check-linear/SKILL.md`

1. **§4 routine comment example** (line ~288): replace example conflict path:

   **`docs/test-bible/core/dispatcher.md (@Betty White)`** (illustrative per-component path; any **`docs/test-bible/**`** file is Betty-owned).

### 5c. `do-all-the-things/SKILL.md`

1. **resume-spawn template** (lines ~121, ~153): replace **`ASTRAL_TEST_BIBLE`** in the “Do NOT re-read” list with **`docs/test-bible/`** (tree).

2. **§4f FIX-UAT qa-child note** (line ~414): replace bible full re-read condition with:

   > bible full re-read only if **`docs/test-bible/**`** changed on **`origin/ftr/<parent>`** since last qa on this parent

## Stage 6: Engineer AGENTS + pre-commit hook verification

**Done when:** Engineer personas and hook match skill ban paths; no repo commit required if hook already correct.

1. Read **`~/.cursor/hooks/pre-commit/engineer.sh`**. The **`case`** statement must include **`docs/test-bible/*)`** alongside **`docs/ASTRAL_TEST_BIBLE.md`**. If missing, add **`docs/test-bible/*)`** to the same blocked branch (do **not** remove monolith block until AST-598 deletes the file).

2. In **`~/.cursor/agents/ada-AGENTS.md`**, **`hedy-AGENTS.md`**, **`katherine-AGENTS.md`**: update workspace guard line 3–4 equivalent to:

   **`Never commit to tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**` — pre-commit hook enforces.**

3. **Verification (no pytest):** From **`astral-AST-598`**, run:

   ```bash
   git diff --cached --name-only >/dev/null  # ensure clean staging
   echo 'docs/test-bible/core/agent.md' | GIT_INDEX_FILE=/dev/null \
     bash -c 'source ~/.cursor/hooks/pre-commit/engineer.sh' 2>&1 || true
   ```

   Manually stage a dummy path test if needed: `git add -N docs/test-bible/README.md 2>/dev/null; git diff --cached --name-only | head -1` — confirm hook prints **`engineer hook: blocked path`**. Reset: `git reset HEAD docs/test-bible/README.md 2>/dev/null`.

⚠️ **Decision:** Hook and **`~/.cursor/agents/*`** live outside **`astral`** git; **Implementation record** below mirrors verification output for UAT.

## Stage 7: Repo plan publish and implementation record

**Done when:** Plan on **`origin/sub/AST-598/AST-664-agent-skill-updates-test-bible`**; Linear **Plan Ready** with labels and GitHub link.

1. On **`astral-AST-598`** epic worktree, implement **Stages 1–6** on global paths first.

2. Append **`## Implementation record`** to the bottom of **this** plan file listing each global file touched and a one-line summary of what changed (auditable mirror for Susan/Chuckles — same pattern as **AST-556**).

3. Commit **only** `docs/features/foundation/ast-664-agent-skill-updates-test-bible.md` on epic worktree:

   **`docs(AST-664): plan — agent skill updates for test-bible tree`**

   If **build-child** already ran Stages 1–6, use instead:

   **`code(AST-664): agent skill updates for test-bible tree`**

   with Implementation record populated.

4. Publish:

   ```bash
   git push origin HEAD:sub/AST-598/AST-664-agent-skill-updates-test-bible
   ```

5. Confirm **`git log origin/sub/AST-598/AST-664-agent-skill-updates-test-bible -1 --oneline`**.

## Self-Assessment

**Scope:** `scope-Single-Component` — Global workflow skills and agent handoff files only; no `src/` or test corpus.

**Conf:** `conf-high` — Parent **AST-598** definition and Chuckles **[check-linear] file checklist** on the parent fix the target paths and contract; **AST-663** tree is on **`ftr`**.

**Risk:** `risk-Medium` — Stale monolith references in skills would mis-route Betty manifests or let engineers commit bible files; wrong rollup wording could recreate merge pain under **`docs/test-bible/**`**.

## ASTRAL_CODE_RULES self-review

- **§1.3 DRY:** Path mirror table defined once in this plan and referenced from **`qa-child`** — no duplicate mirror prose in every skill.
- **§2.1 config / §2.4 batch / §2.6 state machine:** Not applicable — no product code.
- **§3.3 imports / §3.5 naming:** Not applicable.
- **§3.6 debug/spikes:** Not applicable.
- **No conflicts** with code rules; workflow-only change.

## Implementation record

**Built 2026-06-14** on `astral-AST-598`. Global skills/agents/hook updated (not in astral git except this plan):

| File | Change |
| --- | --- |
| `~/.cursor/skills/qa-child/SKILL.md` | Sole authority → `docs/test-bible/**`; `### AST-NNN` manifest blocks; per-path shasum; Component file selection subsection; rollup/conflict routing for per-component files |
| `~/.cursor/agents/betty-AGENTS.md` | Ownership + README session read path |
| `~/.cursor/skills/build-child/SKILL.md` | Test-tree ban includes `docs/test-bible/**` |
| `~/.cursor/skills/test-child/SKILL.md` | Ban + README/component read + merge bullet |
| `~/.cursor/skills/resolve-child/SKILL.md` | Pre-commit diff guard includes `docs/test-bible/**` |
| `~/.cursor/skills/review-child/SKILL.md` | Read-only README + component file pointers |
| `~/.cursor/skills/dispatch-parent/SKILL.md` | Hot files → `docs/test-bible/**` |
| `~/.cursor/skills/check-linear/SKILL.md` | Conflict example → `docs/test-bible/core/dispatcher.md` |
| `~/.cursor/skills/do-all-the-things/SKILL.md` | Resume skip list + FIX-UAT bible gate |
| `~/.cursor/agents/ada-AGENTS.md` | Workspace guard ban line |
| `~/.cursor/agents/hedy-AGENTS.md` | Same |
| `~/.cursor/agents/katherine-AGENTS.md` | Same |
| `~/.cursor/hooks/pre-commit/engineer.sh` | Already had `docs/test-bible/*` — verified blocks staged `docs/test-bible/README.md` (hook exit 1) |

**Repo commit:** plan doc + Implementation record only; no `src/**`, `tests/**`, or `docs/test-bible/**` edits.

## Review

| Field | Value |
|-------|-------|
| **Branch** | `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` |
| **Build commit** | `d5a55d2d` (tip after `merge-tests(AST-664)`) |
| **Reviewer** | Radia (`review-child` after Tests Passed) |
| **Diff baseline** | `origin/dev...origin/sub/AST-598/AST-664-agent-skill-updates-test-bible` |

### What's solid

- All eight global skills + four agent handoffs + `engineer.sh` hook align with parent **AST-598** AC #5–6 and Chuckles parent checklist.
- `qa-child` sole authority is **`docs/test-bible/**`**; no instruction to append new manifests to the monolith; **`### AST-NNN`** registry and per-path shasum contract present.
- Engineer ban paths list **`docs/test-bible/**`** alongside transitional **`docs/ASTRAL_TEST_BIBLE.md`** in **build-child**, **test-child**, **resolve-child**, and engineer **AGENTS.md** files; hook blocks **`docs/test-bible/*`** (verified in Implementation record).
- **review-child**, **dispatch-parent**, **check-linear**, **do-all-the-things** read/skip paths point at the tree + **README.md**.
- Betty manifest block in **`docs/test-bible/README.md`** correctly documents narrowed **`tests/component`** smoke (skips zero-arg **LOCKED_AT_100** gate for workflow-only child).
- **`test_api_admin.py`** **`run_task`** mock fix (**AST-653** handoff) is Betty-owned and matches manifest.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **advisory** | Branch diff vs plan “repo commit plan only” | Three-dot diff includes **AST-663** tree, workflow doc pointer updates, and Betty **merge-tests** commits — expected on integrated **`sub/*`** after **`ftr`** merge; not engineer scope creep on **AST-664** product path. |
| **advisory** | **`.gitignore`** `/AGENTS.md` | Anchors ignore to repo root (**AST-663**); good hygiene, outside **AST-664** Implementation record. |

**fix-now:** none  
**discuss:** none

### Recommended actions

| Action | Owner |
| --- | --- |
| **resolve-child** — no product changes required | Ada |
| Parent **AST-598** — retire monolith after all siblings **User Testing** | Radia gate (separate pass) |

## Resolution

**Resolved 2026-06-14** on `astral-AST-598` @ `origin/sub/AST-598/AST-664-agent-skill-updates-test-bible`.

| Item | Outcome |
| --- | --- |
| **fix-now** | None — Radia review confirmed global skills/agents/hook + Betty manifest align with **AST-598** AC #5–6. |
| **discuss** | None. |
| **advisory** | **AST-663** / **ftr** noise on **`sub/*` diff** and **`.gitignore`** `/AGENTS.md` — acknowledged; out of **AST-664** engineer scope. |
| **Product / repo** | No **`src/**`** changes. Plan doc carries Implementation record + Review (Radia **`1918f4cd`**). Global skill edits remain on workstation per Implementation record. |
| **§9a dry-run** | `origin/sub/…/AST-664-…` merges cleanly into **`origin/dev`** and **`origin/ftr/ast-598-restructure-astral_test_biblemd-into-per-component-bible`**. |

**Linear:** **User Testing** — assignee **Ada** (implementer unchanged).
