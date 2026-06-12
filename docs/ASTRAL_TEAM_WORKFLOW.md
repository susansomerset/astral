# Astral team — workflow (index)

This file is a **one-page map**. **Executable procedures** live in global Cursor skills under **`~/.cursor/skills/`**: **`orientation-astral`**, **`check-linear`**, **`plan-astral`**, **`build-astral`**, **`qa-astral`**, **`test-astral`**, **`review-astral`**, **`resolve-astral`**, plus Chuckles’ **`define-linear`**, **`dispatch-linear`**, **`validate-plan`**, **`rollcall`**. **`docs/ASTRAL_CODE_RULES.md`** is the architecture contract.

**`.cursor/skills/`** is **not** in this repository (**`origin/dev`** has only **`.cursor/settings.json`**, gitignored locally). Use the canonical skill names in the table above only (**`check-linear`**, **`test-astral`**, **`qa-astral`**, etc.). Removed aliases: **`check-astral`**, **`astral-test`**, **`astral-qa-plan`**. Delete stale copies under agent worktrees (e.g. **`0-agent-orientation`**, **`1-check-linear`**, **`astral-check-linear`**).

**Per-skill step lists** live only in global skills—do not mirror long checklists in this file.

**Project scope:** **`orientation-astral`** establishes which **Linear program** this chat is working in when Susan names it (or asks if she didn’t). Planning / build / test / review skills stay **project-scoped**—use that session **project** filter for queues and discovery unless Susan gives a single explicit ticket id. **Tester** (`qa-astral`) uses a **wider** lens for *test design* judgment. **`test-astral`** is run by the **engineer** on **`Tests Ready`**, same project filter. **Reviewer** (`review-astral`) is **stateless** per program.

---

## Git and branches

**Branch law** (worktrees, `dev` / `dev-<agent>`, **`ftr/<ticket-id>`** on `origin` only, cherry-pick publish, reading plans without checking out feature branches) is defined **only** in the global skill **`~/.cursor/skills/orientation-astral/SKILL.md`** — **§ Branch law**. Agents read that during **`orientation-astral`**; it is **not** duplicated here because these rules are team-wide, not repo-specific.

**Integration line discipline** (merge **`origin/dev`** then **`origin/<publish-ref>`** before **`test-astral`**; never push **`dev-<agent>`** to **`origin/dev`**; prep-uat harness gate; no hard reset on integration branches) lives in the same skill — **§ Integration line discipline**. Susan owns **`origin/dev`**; engineers own ticket publish refs.

**Local debug / spike output** (Playwright captures, scratch JSON): repo-root **`debug/spikes/<issue-id>/…`** only — never repo-root **`artifacts/`**; spike deliverables are **not** committed under **`docs/features/`** (attach on Linear). See **`orientation-astral`** § Local debug and spike output and **`docs/ASTRAL_CODE_RULES.md`** §3.6.

**Local UI dev:** repo-root **`launch.sh`** — Flask **`:5001`** + Vite **`:5173`**. Tracked; **do not delete** in merges (`land-ftr` / `push-dev`). Restore from git if missing. Details: **`orientation-astral`** § Local dev — `launch.sh`.

---

## Roles (short)

| Role | Who | Notes |
|------|-----|--------|
| **Architect** | Susan | Scope, approval, **`dev` → PR → `main`**. |
| **Engineer** | Ada, Hedy, Katherine | Same assignee for the ticket through resolve; work in **`astral-<agent>`**. |
| **Tester** | Betty | **`qa-astral`**; inbox via **`check-linear`**; owns **test-tree** commits; may think repo-wide for *risk*; **`list_issues`** still project-scoped unless Susan says otherwise. |
| **Reviewer** | Radia | **`review-astral`** on **`Tests Passed`**; stateless across Linear programs. |
| **Coordinator** | Chuckles | **`define-linear`**, **`dispatch-linear`**, **`review-plan`**, **`rollcall`** — **never** Linear **assignee**; see those skills. |

---

## Test ownership

**Betty** (`qa-astral`) is the only role that commits under **`tests/`**, **`scripts/test_*.py`**, **`scripts/testing/`**, and **`docs/ASTRAL_TEST_BIBLE.md`** (new coverage, revisions, harness, bible).

**Engineers** (`build-astral`, `test-astral`, `resolve-astral`): **product** (and plan docs when the skill says so) only. If the manifest fails and you believe the **test** is wrong, or resolve needs a test change: **`[qa-handoff]`** as the **first line** of a Linear comment — **do not** patch test-tree paths yourself. Betty picks up **`Tests Ready`** + **`[qa-handoff]`** and **`Review Posted`** + **`[qa-handoff]`** (see **`qa-astral`** §1 **C**).

---

## Orientation

Follow **`~/.cursor/skills/orientation-astral/SKILL.md`** in full before other pipeline skills. That procedure loads this document and **`docs/ASTRAL_CODE_RULES.md`**, establishes **`<session-linear-project>`** (asks Susan if needed), runs a **project survey** (Linear project description, issues in that project, skim **`docs/features/<folder>/`** per **plan-astral** folder mapping), verifies **Linear MCP** identity, records token/subagent habits, and teaches **§ Branch law** (`ftr/<ticket-id>`, `dev-<agent>`, cherry-pick publish). Orientation does not by itself produce a ticket commit; follow-up edits belong in the owning skill (usually **plan-astral** or the architect).

## Linear status → skill (happy path)

| Linear status | Typical actor | Next skill / action |
|---------------|----------------|---------------------|
| Backlog | Susan + Chuckles | **`define-linear`** until definition is ready; Susan moves to **Todo** when approved for planning. |
| Todo | Engineer | **`plan-astral`** → **Plan Ready** |
| Plan Ready | Chuckles + Susan | **`validate-plan`** → **Plan Approved** (engineer stays assignee) |
| Plan Approved | Engineer | **`build-astral`** → **Code Complete** |
| Code Complete | Betty | **`qa-astral`** → **Tests Ready** |
| Tests Ready | Engineer | **`test-astral`** → **Tests Passed** |
| Tests Passed | Radia | **`review-astral`** → **Review Posted** |
| Review Posted | Engineer | **`resolve-astral`** → **User Testing** (child keeps engineer **assignee**) |
| User Testing (child) | Engineer | Ready for **`prep-uat`** rollup; **assignee** stays implementer |
| User Testing (parent) | Susan | **`prep-uat`** assigns Susan; merge **`origin/ftr/<parent>`** into local **`dev`**, exercise |
| PR Ready | Susan sets **parent** → Chuckles **`finish-up`** | Land **`origin/ftr/<parent-segment>`** on **`origin/dev`**; **parent + children** → **PR Ready** (children keep engineer **assignee**) |
| Done | Susan | Close **parent** in Linear (work on **`origin/dev`**) |

**Parent epics:** **`dispatch-linear`** moves children to **Todo** and parent to **In Progress**; parent **assignee** stays **Susan** (or coordinator), **not** Chuckles. Rollup when all children reach **Review Posted** per **`rollcall`**.

---

## CALL SUSAN

Product, priority, and cross-feature contracts: **@susan** in Linear. Do not build on missing decisions.
