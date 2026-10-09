# AST-1909 — Manage Task modal: no Model dropdown of config-driven model keys

<!-- linear-archive: AST-1909 archived 2026-10-08 -->

## Linear archive (AST-1909)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1851 — Support OpenRouter API models for agent work  
**Blocked by / blocks / related:** parent: AST-1851

### Description

Susan's UAT comment on [AST-1851](https://linear.app/astralcareermatch/issue/AST-1851/support-openrouter-api-models-for-agent-work) (verbatim, 2026-10-01T00:12:46Z):

> \[bug\] I cannot select the model from a dropdown list of config-driven model keys in the Manage Task modal.

## As-is / to-be

* **As-is:** The Manage Task modal (`src/ui/frontend/src/pages/AdminTaskPrompts.tsx`) shows the model only as read-only text (`model_code`), and the list's "Model" column shows `agent_id`. The config-driven model picker (`GET /api/admin/agents/models`) exists only in Manage Agents (`AdminAgentPrompts.tsx`).
* **To-be:** The Manage Task modal has a Model dropdown filled from the config model catalog keys (`LLM_MODEL_CONFIG`), and saving the task persists the selection.

Open for plan-fix: whether the task-modal selection writes the task's agent `model_id` (today's per-agent design) or a task-level model. Ask Susan in `[plan-discuss]` rather than guess.

## Suggested engineer

Ada ([AST-1880](https://linear.app/astralcareermatch/issue/AST-1880/admin-model-brain-pickers-per-platform-keys-invalid-on-missing-key) built the admin model pickers and the `/agents/models` route).

### Comments

#### chuckles — 2026-10-01T00:36:19.168Z
[merge-child] blocked: `origin/sub/AST-1851/AST-1909-manage-task-model-dropdown` carries another epic's work. @susan

Betty's `merge-tests(AST-1909)` (`0995f7033`, origin/tests `58098c74c`) brought in 11 commits, not just her one test commit. A parallel AST-1908 pass reset the shared `astral-tests` worktree mid-run. The extras are AST-1902 epic commits that are not on `origin/dev`: `7479f320a code(AST-1904)` (`src/core/builder.py`), `2c760d1ac test(AST-1905)` (`test_builder.py`, `docs/test-bible/core/builder.md`), AST-1904/1905 docs, `fa334f155 sync(ftr): ftr/AST-1902…`, and `42dcc9c73 sync(dev)`. If `merge-child` runs, all of that lands on `ftr/AST-1851-support-openrouter-api-models`.

The AST-1909 fix itself is done and clean: plan, fix-board (TESTS: REVISE → repro, CANON: OK), make-fix `9c7591ea9`, test-fix 29/29, Radia PROCEED. It is at User Testing. Git law forbids cherry-pick and force-push, so I can't strip the extras myself.

How should I proceed? Options: merge as-is (AST-1902 rides along into the AST-1851 PR); have Ada and Betty add revert commits on the sub for the AST-1902 product/test changes (risks a revert-of-revert when AST-1902 lands); or reseed a fresh sub from ftr and re-land AST-1909 there. Once you decide, assign this bug to Chuckles.

#### radia — 2026-10-01T00:36:03.426Z
[code-rubric] PROCEED (Commit: 9c7591ea9) task modal catalog picks

#### ada — 2026-10-01T00:31:15.432Z
`origin/sub/AST-1851/AST-1909-manage-task-model-dropdown` @ `9c7591ea9` · code complete

#### betty — 2026-10-01T00:28:49.524Z
[bug-repro]
`origin/sub/AST-1851/AST-1909-manage-task-model-dropdown` @ `0995f7033` · repro lands red, awaits fix

#### joan — 2026-10-01T00:22:21.883Z
[board-joan]  CANON: OK

#### betty — 2026-10-01T00:21:56.385Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md (AdminTaskPrompts) — broken tests + missing repro coverage — `test_AdminTaskPrompts.test.tsx` mocks every call via `installBaseApiMocks`, which throws "Unhandled api" on any URL it doesn't route. None of its handlers (main mockApi, load-failure, AST-513, AST-783, AST-739 describe, revert, run_next) serve the new mount `GET /api/admin/agents/models` or the edit-time `GET /api/admin/agents/<id>`, so the fix breaks the existing suite unless those routes get defaults. No test covers the repro: the Model and Brain size selects filled from the catalog in `order`, the size kept or reset on a model change, the "Applies to agent … used by N task(s)" hint, the disabled "— no agent —" state, task PUT then agent PUT `{model_id, brain_setting}` only when changed, and an agent-PUT 400 going to the error toast.

#### ada — 2026-10-01T00:20:58.888Z
`origin/sub/AST-1851/AST-1909-manage-task-model-dropdown` @ `9d71763a1` · scope cleared, plan ready

#### chuckles — 2026-10-01T00:20:02.242Z
[scope-gate] resolved — `AdminTaskPrompts.tsx` added to AST-1851 Component/Technical scope (per-agent `model_id`, no task-level model, frontend only). Resuming plan-fix.

#### ada — 2026-10-01T00:19:21.817Z
[scope-gate] `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` is not in AST-1851's Component scope, and this fix lives entirely in that file.

- **Scope today:** the parent's admin UI lines are "`AdminAgentPrompts.tsx` — model select + model-scoped brain-size select", "`AdminManageCandidates.tsx` — one key field per catalog server", "`AdminScheduledActions.tsx` …", and "`AdminSessionResumePaste.tsx` …". Functional scope 8 ("Admin surfaces") names only Manage Agents and Manage Candidates. Nothing covers the Manage Task modal.
- **Needed change (frontend only, no backend):** the Manage Task modal gets Model + Brain size selects from `GET /api/admin/agents/models`. Saving writes the **task's agent** `model_id` + `brain_setting` via the existing `PUT /api/admin/agents/<id>`. This is the same per-agent design and routes AST-1880 shipped, so it is a small omission, not a new approach.
- **Open question settled by the parent:** the model is per agent (Purpose, Functional scope 1, and the brief: "the agent table should point to the model"). There is no task-level model, so no `[plan-discuss]` is needed. The modal shows a "used by N tasks" hint, because the agent change applies to every task on that agent.
- **Ask:** add `src/ui/frontend/src/pages/AdminTaskPrompts.tsx — Manage Task modal: model + brain-size selects for the task's agent (catalog-driven)` to AST-1851's Component/Technical scope. After amending, assign this bug to Chuckles. The plan is complete at bd96c338b.

---

_Implementation detail may live in git history on `origin/dev`._
