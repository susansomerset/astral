# Astral team — workflow (index)

This file is a **one-page map**. **Executable procedures** live in global Cursor skills under **`~/.cursor/skills/`**: **`orientation`**, **`check-linear`**, **`plan-child`**, **`build-child`**, **`qa-child`**, **`test-child`**, **`review-child`**, **`resolve-child`**, plus Chuckles’ **`define-parent`**, **`dispatch-parent`**, **`rollcall`**, and Joan’s **`validate-plan`**. **`docs/ASTRAL_CODE_RULES.md`** is the architecture contract.

**`.cursor/skills/`** is **not** in this repository (**`origin/dev`** has only **`.cursor/settings.json`**, gitignored locally). Use the canonical skill names in the table above only (**`check-linear`**, **`test-child`**, **`qa-child`**, etc.). Removed aliases: **`check-astral`**, **`astral-test`**, **`astral-qa-plan`**. Delete stale copies under agent worktrees (e.g. **`0-agent-orientation`**, **`1-check-linear`**, **`astral-check-linear`**).

**Per-skill step lists** live only in global skills—do not mirror long checklists in this file.

**Project scope:** **`orientation`** establishes which **Linear program** this chat is working in when Susan names it (or asks if she didn’t). Planning / build / test / review skills stay **project-scoped**—use that session **project** filter for queues and discovery unless Susan gives a single explicit ticket id. **Tester** (`qa-child`) uses a **wider** lens for *test design* judgment. **`test-child`** is run by the **engineer** on **`Tests Ready`**, same project filter. **Reviewer** (`review-child`) is **stateless** per program.

---

## Git and branches

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `team-git-and-branches-pointers`

**Branch law** (worktrees, `dev` / `epic worktree`, **`ftr/<ticket-id>`** on `origin` only, direct commits on sub, reading plans without checking out feature branches) is defined **only** in the global skill **`~/.cursor/skills/orientation/SKILL.md`** — **§ Branch law**. Agents read that during **`orientation`**; it is **not** duplicated here because these rules are team-wide, not repo-specific.

**Integration line discipline** (merge **`origin/dev`** then **`origin/<publish-ref>`** before **`test-child`**; never push **`epic worktree`** to **`origin/dev`**; prep-uat harness gate; no hard reset on integration branches) lives in the same skill — **§ Integration line discipline**. Susan owns **`origin/dev`**; engineers own ticket publish refs.

**Local debug / spike output** (Playwright captures, scratch JSON): repo-root **`debug/spikes/<issue-id>/…`** only — never repo-root **`artifacts/`**; spike deliverables are **not** committed under **`docs/features/`** (attach on Linear). See **`orientation`** § Local debug and spike output and **`docs/ASTRAL_CODE_RULES.md`** §3.6.

**Local UI dev:** repo-root **`launch.sh`** — Flask **`:5001`** + Vite **`:5173`**. Tracked; **do not delete** in merges (`prep-uat` / `finish-up`). Restore from git if missing. Details: **`orientation`** § Local dev — `launch.sh`.

---

## Roles (short)

**Statute:** `orch.roles.chuckles-never-ticket-assignee`
**Statute:** `orch.roles.engineer-assignee-through-resolve`

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `team-roles-table-detail`

| Role | Who | Notes |
|------|-----|--------|
| **Architect** | Archie | Scope, approval, **`dev` → PR → `main`**. Linear: Susan / `@susan`; see `team-chuckles/agents/identity-table.md`. |
| **Engineer** | Ada, Hedy, Katherine | Same assignee for the ticket through resolve; work in **`astral-<agent>`**. |
| **Tester** | Betty | **`qa-child`**; inbox via **`check-linear`**; owns **test-tree** commits; may think repo-wide for *risk*; **`list_issues`** still project-scoped unless Archie says otherwise. |
| **Reviewer** | Radia | **`review-child`** on **`Tests Passed`**; stateless across Linear programs. |
| **Coordinator** | Chuckles | **`define-parent`**, **`dispatch-parent`**, **`rollcall`**, spawns Joan for **`validate-plan`** — **never** Linear **assignee**; see those skills. |
| **Statute validator** | Joan | **`validate-plan`** on **Plan Ready** / **Plan Discuss**; no git authority. |

---

## Test ownership

**Statute:** `orch.roles.betty-owns-test-tree`
**Statute:** `astral.git.engineer-test-tree-ban`

**Betty** (`qa-child`) is the only role that commits under **`tests/`**, **`scripts/test_*.py`**, **`scripts/testing/`**, and **`docs/test-bible/**`** (new coverage, revisions, harness, bible). The monolith **`docs/ASTRAL_TEST_BIBLE.md`** remains Betty-owned until AST-598 retirement after Radia review.

**Engineers** (`build-child`, `test-child`, `resolve-child`): **product** (and plan docs when the skill says so) only. If the manifest fails and you believe the **test** is wrong, or resolve needs a test change: **`[qa-handoff]`** as the **first line** of a Linear comment — **do not** patch test-tree paths yourself. Betty picks up **`Tests Ready`** + **`[qa-handoff]`** and **`Review Posted`** + **`[qa-handoff]`** (see **`qa-child`** §1 **C**).

---

## Orientation

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `team-orientation-pointer`

Follow **`~/.cursor/skills/orientation/SKILL.md`** in full before other pipeline skills. That procedure loads this document and **`docs/ASTRAL_CODE_RULES.md`**, establishes **`<session-linear-project>`** (asks Archie if needed), runs a **project survey** (Linear project description, issues in that project, skim **`docs/features/<folder>/`** per **plan-child** folder mapping), verifies **Linear MCP** identity, records token/subagent habits, and teaches **§ Branch law** (`ftr/<ticket-id>`, `epic worktree`, direct commits on sub). Orientation does not by itself produce a ticket commit; follow-up edits belong in the owning skill (usually **plan-child** or the architect).

## Linear status → skill (happy path)

**Statute:** `orch.pipeline.status-gates-skill-entry`
**Statute:** `orch.pipeline.project-scoped-queues`
**Statute:** `orch.pipeline.plan-is-bible`

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `team-happy-path-table`

| Linear status | Typical actor | Next skill / action |
|---------------|----------------|---------------------|
| Backlog | Archie + Chuckles | **`define-parent`** until definition is ready; Archie moves to **Todo** when approved for planning (Linear: Susan). |
| Todo | Engineer | **`plan-child`** → **Plan Ready** |
| Plan Ready | Joan (Chuckles assigns/spawns) | **`validate-plan`** → **Plan Approved** (APPROVED) or **Plan Discuss** (REVISE); Joan briefly assignee during the pass, then engineer |
| Plan Discuss | Joan + engineer | tagged discuss loop (`validate-plan` / plan reply); cap 2 → Escalate (Linear: Susan); exit Plan Approved or Todo |
| Plan Approved | Engineer | **`build-child`** → **Code Complete** |
| Code Complete | Betty | **`qa-child`** → **Tests Ready** |
| Tests Ready | Engineer | **`test-child`** → **Tests Passed** |
| Tests Passed | Radia | **`review-child`** → **Review Posted** |
| Review Posted | Engineer | **`resolve-child`** → **User Testing** (child keeps engineer **assignee**) |
| User Testing (child) | Engineer | Ready for **`prep-uat`** rollup; **assignee** stays implementer |
| User Testing (parent) | Susan | **`prep-uat`** assigns Susan; merge **`origin/ftr/<parent>`** into local **`dev`**, exercise |
| PR Ready | Archie sets **parent** (Linear: Susan) → Chuckles **`finish-up`** | Land **`origin/ftr/<parent-segment>`** on **`origin/dev`** (PR + ref cleanup per **finish-up**); move **parent + shipped children** → **Done** (children keep engineer **assignee**) |
| Done | Archie | Close **parent** in Linear (work on **`origin/dev`**) |

**Parent epics:** **`dispatch-parent`** moves children to **Todo** and parent to **In Progress**; parent **assignee** stays **Susan** (or coordinator), **not** Chuckles. Rollup when all children reach **Review Posted** per **`rollcall`**.

---

## CALL ARCHIE

**Statute:** `orch.pipeline.call-susan-for-product-decisions`

**Archie** is the public architect alias (`team-chuckles/agents/identity-table.md`). Product, priority, and cross-feature contracts: **@susan** in Linear. Do not build on missing decisions.
