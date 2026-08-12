# AST-1036 — Simple Resume Parse function

<!-- linear-archive: AST-1036 archived 2026-08-05 -->

## Linear archive (AST-1036)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1036/simple-resume-parse-function  
**Status at archive:** Archive  
**Project:** Astral Administrator  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Session Resume Paste is a stop-gap Admin workbench until the full resume generation pipeline ships. Today Parse still runs Judith’s full `craft_resume_base` hop — expensive “think and rewrite” work for what is really rote paste→JSON shaping. This epic swaps that hop to Ruth (Little brain) with a much simpler parse prompt so Susan can keep using Paste → Parse → Open HTML without burning big-brain tokens on translation.

## Functional scope

* **Dedicated simple parse task.** Introduce a Ruth-owned agent task whose job is only to map pasted resume text into the existing session-resume JSON contract (structure + content fields the Paste screen and Open HTML already consume). The prompt instructs mechanical field placement — not rewrite, enrichment, LinkedIn synthesis, or “improve the resume.”
* **Session Resume Parse uses Ruth.** The Admin Session Resume Paste Parse path invokes that Ruth/Little task instead of Judith’s craft-base task. Success and failure responses stay compatible with the current paste screen and Open HTML flow (no candidate bind, no durable artifact write).
* **Paste-faithful mechanical rules stay in the simple prompt.** Rules already proven on this screen — preserve `__` / `~~` markers, competency bullet joins (not pipes), title vs tagline placement, and `<no bullet>` lead markers — remain explicit parse instructions so Open HTML quality does not regress when leaving Judith’s craft prompt.
* **Candidate craft path unchanged.** Candidate-bound resume craft / generation that uses Judith `craft_resume_base` keeps using that task and persona. This epic only changes the Admin session stop-gap path.
* **Observability.** Admin session parse continues to record cost/ledger visibility for the hop. When `debug=True`, the parse hop logs Style D found|recorded detail (index headers plus DEBUG_DETAIL_PREFIX working lines; long payloads truncated per Code Rules) — not only pass/fail.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — new task definition and response schema live in `TASK_CONFIG` / repo agent_task seed; no inline magic sets.
  * `pattern.ui.admin-endpoint` — keep the existing Admin parse route thin; core owns the task swap; `@require_admin` / auth shape unchanged.
  * `pattern.layers.import-discipline` — UI calls Admin API; core calls `do_task`; no layer skipping.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — task key, schema, and brain/persona wiring from config + admin agent_task rows.
  * `astral.agent.do-task-delegation` — session parse still reaches the model only via `do_task`.
  * `astral.patterns.require-auth-on-protected-endpoints` — Admin parse remains auth-gated.
  * `astral.layers.ui-config-driven-business-logic` — React stays a caller; task choice is core/config.
  * `astral.layers.import-direction` — honor layer import direction on touched files.
  * `astral.standards.in-scope-only` — do not retouch unrelated craft/generation surfaces.
  * `astral.standards.debug-contract-gated` — Style D only when `debug=True` on touched backend debug paths.
  * `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — keep the session-parse entry focused; extract only if the wire forces it.
  * `astral.standards.no-hardcoded-sets` — no new inline enum/sets for task keys or schema.
  * `astral.standards.logging-via-utils` — logging through utils logger helpers.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child.

## Boundaries

* Does **not** replace or re-persona Judith `craft_resume_base` for candidate artifact generation / Manage Tasks craft flows.
* Does **not** implement the full resume generation pipeline this screen is bridging toward.
* Does **not** change Open HTML builder behavior, paste-page chrome, or session localStorage keys unless a tiny contract tweak is required to keep Parse→HTML working (prefer zero UI change).
* Does **not** change Session Cover Letter or other Admin session tools.
* Does **not** invent a new free-form JSON shape that breaks Open HTML or “View Parsed JSON.”
* Does **not** weaken paste-faithful mechanical rules already expected on this stop-gap screen.
* Adjacent in flight: Artifacts UAT children still tuning Judith craft-base prompts (e.g. under [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies)) — those remain craft-base work; this epic moves **session** parse off that task onto Ruth.

## Acceptance criteria

1. From Admin **Session Resume Paste**, Parse runs a Ruth (Little) task — not Judith craft-base — and still returns structure-keyed JSON the screen already understands.
2. A successful Parse → Open HTML path still works without binding to the selected candidate and without writing candidate/job artifacts for the paste.
3. Dispatch/cost ledger for the Admin session-parse hop still records the run against the session sentinel path (same operational visibility Susan has today).
4. Paste-faithful mechanics remain observable on a known fixture: `__` / `~~` survive into content for HTML expand; competencies are not pipe-joined; specialty/keyword text lands in tagline (not mashed into title); `<no bullet>` leads remain lead markers for HTML.
5. Candidate-bound `craft_resume_base` / Judith craft behavior is unchanged when exercised outside this Admin session path.
6. With debug on, the session-parse hop emits Style D index + detail (found|recorded), not summary-only noise; with debug off, no new debug-contract lines.

## Dependencies and blockers

none.

Related context (not blockers): [AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf) / [AST-987](https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf) (session parse API + paste page, Done); [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) family (Judith craft-base / render UAT — parallel, session path will stop depending on craft-base).

## Open questions

none.

## Proposed child tickets

#### 1!: **Ruth simple session-resume parse task - Ada**

Add the dedicated Little/Ruth agent task and `TASK_CONFIG` entry for paste→JSON only (mechanical field mapping; no craft/translate). Seed the repo agent_task so Manage Tasks / startup apply pick it up. Same response contract the session paste path already expects. Does **not** wire Admin Session Resume Parse yet — that is #2. Does **not** change Judith `craft_resume_base`.

**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.agent.do-task-delegation`; `astral.standards.no-hardcoded-sets`.

#### 2: **Wire Session Resume Parse to Ruth task - Ada**

After #1: point Admin session resume parse (core + thin Admin route contract) at the new Ruth task instead of `craft_resume_base`. Preserve no-persist / no-candidate-bind behavior, ledger visibility, and Style D debug on the hop. Leave candidate craft on Judith. Prefer no Paste UI change.

**Citations:** `pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-1036](https://linear.app/astralcareermatch/issue/AST-1036/simple-resume-parse-function) (parent) | ftr/ast-1036-simple-resume-parse-function |
| [AST-1037](https://linear.app/astralcareermatch/issue/AST-1037/ruth-simple-session-resume-parse-task-simple-resume-parse-function) | sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task |
| [AST-1038](https://linear.app/astralcareermatch/issue/AST-1038/wire-session-resume-parse-to-ruth-task-simple-resume-parse-function) | sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task |

**Epic worktree:** `astral-AST-1036/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/b7db5ad694e6820d489686b5e4f4c45f/63822cd9-a3e7-40e1-8d25-96adcec75c48/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/58edbffa-5f49-48ec-a370-227fc628a86b/store.db` |
| Radia | review | `/home/susan/.cursor/chats/b7db5ad694e6820d489686b5e4f4c45f/e2ba1705-2de2-4475-aea3-4f9425915936/store.db` |

---

## Original brief

Let's replace the AI call on the Session Resume Parse screen to a similar but MUCH SIMPLER prompt that sends text to Ruth (little brain) to parse the text into JSON, not think through and translate.  This screen is a stop-gap measure until we have the full generation pipeline completed.  Let's not waste big-brain tokens on rote translation to JSON.

### Comments

#### chuckles — 2026-07-29T15:40:43.611Z
[thread-missing] Ada Team chat `4d3fdf0b-0cce-401f-851c-3e1d8306d50c` collided with this epic's sub-chuck drone session. Reminted Ada → `63822cd9-a3e7-40e1-8d25-96adcec75c48`; Betty → `58edbffa-5f49-48ec-a370-227fc628a86b` (was sharing Radia's UUID). Updated ## Team.

— Chuckles

#### chuckles — 2026-07-29T15:11:36.484Z
[thread-missing] Ada Team row: history UUIDs had no store.db on this host — minted `d199ecbd-8077-4beb-961e-625e0eecb96e` under epic workspace hash `b7db5ad694e6820d489686b5e4f4c45f`. Look path: `/home/susan/.cursor/chats/b7db5ad694e6820d489686b5e4f4c45f/d199ecbd-8077-4beb-961e-625e0eecb96e/store.db`.

[thread-missing] Betty Team row: no history mention — minted `7e25baa3-0842-4c1e-8d94-2265e4c3df20` under astral-tests hash `2d0fa47271e47a831e103b336fb3fbc8`.

[thread-orphan] Radia Team row: relocated `e2ba1705-2de2-4475-aea3-4f9425915936` from main hash → epic hash `b7db5ad694e6820d489686b5e4f4c45f` (same UUID).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
