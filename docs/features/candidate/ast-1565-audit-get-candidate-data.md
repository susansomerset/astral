# AST-1565 — Audit get_candidate_data

<!-- linear-archive: AST-1565 archived 2026-09-09 -->

## Linear archive (AST-1565)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1565/audit-get-candidate-data  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. **Clarify the two access paths** (read-only reconnaissance):
   * **Contact-task path:** Estelle/contact agent emits `~~/get_candidate_data [optional.dotted.path]~~` markup in `reply` → `parse_contact_task_markup` → `run_contact_task_dispatch` → `contact_task_get_candidate_data` in `src/core/tracker.py` (registered in `CONTACT_TASK_CONFIG`, AST-1515/1518). Handler loads via `candidate.get_candidate()` and optionally walks a dotted path or attaches `agent_story`.
   * **Direct-context path:** Callers pass `candidate_data` (or a full candidate raft as `ctx`) into `do_task` / agent token resolution without invoking the contact task — e.g. `contact.process_estelle_turn` pre-loads `candidate_data` from `get_candidate()` and passes it to `do_task` (`src/core/contact.py` ~1122–1137). Agent helpers in `src/core/agent.py` (`_token_view_for_do_task`, `is_candidate_token_view`) merge `ctx` vs explicit `candidate_data`.
2. **Inventory** `get_candidate_data` **usage** — grep for the task key and handler:
   * `get_candidate_data`, `contact_task_get_candidate_data`, `~~/get_candidate_data`
   * Expected: config registration (`src/utils/config.py`), handler + tests (`tracker.py`, `test_tracker.py`), feature docs — **no production markup callers yet** (agent must emit markup at runtime). Note any prompt/config text that instructs Estelle to use the task.
3. **Inventory direct** `candidate_data` **consumers** — grep `src/` (then tests for contrast only):
   * `.get("candidate_data")`, `candidate_data=`, `save_candidate_data`, `get_candidate(` followed by blob access
   * Group by module: `candidate.py`, `contact.py`, `agent.py`, `consult.py`, `builder.py`, `meteorite.py`, `gazer.py`, `intake.py`, `api_*`, `config.py` token resolution
   * Skip pure DB/migration scripts unless they read blob fields for runtime behavior
4. **Classify each file/site** into one of:
   * **A** — Uses contact-task dispatch (`get_candidate_data` markup path)
   * **B** — Loads candidate row / blob directly (`get_candidate`, `.get("candidate_data")`)
   * **C** — Receives pre-hydrated `candidate_data` on agent context (`do_task`, token resolution)
   * **D** — Writes blob (`save_candidate_data`, `save_candidate`)
   * **E** — Frontend/API passes or displays blob slices (React context, API serializers)
5. **Assess fidelity** — For contact-adjacent flows (Estelle turn, contact skills, land meteorite follow-up): does the code assume blob is already on context when the contact-task path would be the canonical read? Flag mismatches (e.g. agent told to use `~~/get_candidate_data~~` but turn context already injects the blob; or code reads paths the task would expose but never routes through dispatch).
6. **Produce deliverable** — Markdown table: `file | access pattern | what fields/paths | why | faithful to get_candidate_data? (Y/N/NA)`. Post as a Linear comment on this ticket (or link a `docs/` note if Susan prefers — ask in comment if unclear). **No code changes.**

## Done when

* Every `src/` module that reads or writes `candidate_data` content appears in the table with a one-line summary.
* Contact-task path vs direct-context path is documented with concrete file:line references.
* Gaps/mismatches called out explicitly (where direct access bypasses or duplicates what `get_candidate_data` would return).
* Deliverable posted; ticket remains read-only audit (no commits).

## Risks / open questions

* Susan's brief names `get_candidate_data` **in** `candidate.py` — no such function exists today; the registered contact task handler is `contact_task_get_candidate_data` in `tracker.py`. Treat the brief as the contact-task key unless Susan clarifies a different symbol.
* Runtime markup usage won't appear in static grep — check agent prompts, `CONTACT_ESTELLE_CONFIG`, and live Slack threads if needed.
* "Context object" may mean (a) Slack conversation context, (b) `candidate_data.context` library section, or (c) agent `ctx` raft — classify each site explicitly in the table.

---

## Original brief

Perform an audit of the codebase to determine how faithfully the get_candidate_data function in [candidate.py](<http://candidate.py>) is called, versus assuming the data is available on the context object directly.

Do not change code.

Make a list of files that use content from candidate_data for any reason and a brief summary of how and why.

### Comments

#### chuckles — 2026-09-01T16:25:49.743Z
# AST-1565 — `get_candidate_data` vs direct `candidate_data` access audit

## Symbol note

Susan's brief references **`get_candidate_data` in `candidate.py`** — that function does not exist. The registered contact-task key **`get_candidate_data`** maps to **`contact_task_get_candidate_data`** in **`src/core/tracker.py`** (`CONTACT_TASK_CONFIG`, AST-1515/1518). This audit uses that handler as the canonical "get_candidate_data" path.

## Two access paths

| Path | Flow | Primary files |
|------|------|---------------|
| **Contact-task (A)** | Agent emits `~~/get_candidate_data [optional.dotted.path]~~` → `parse_contact_task_markup` → `run_contact_task_dispatch` → `contact_task_get_candidate_data` → `get_candidate()` + optional path walk or full row + `agent_story` | `contact.py:867–977`, `tracker.py:1717–1802`, `config.py:4764–4768` |
| **Direct-context (B/C)** | Caller loads row via `get_candidate()` / `database.get_candidate()`, extracts inner blob (or `build_candidate_token_view`), passes to `do_task` / token resolution / business logic without contact-task dispatch | Widespread — see table below |

**Static grep:** zero production call sites emit `~~/get_candidate_data~~` markup. Usage is runtime-only when Estelle's reply includes the task. Config + tests + handler are the only compile-time references.

## Fidelity assessment (contact-adjacent)

**Estelle turn (`contact.process_estelle_turn`, ~1122–1190):**

1. **Before** markup dispatch: loads `candidate_data` from `get_candidate(astral_candidate_id)` and passes it to `do_task` for token resolution (pattern **C**).
2. Turn context **lists** `get_candidate_data` among available contact tasks (~1090) so the agent *can* request it.
3. **After** markup dispatch: task results (including any `get_candidate_data` output) are JSON-serialized into follow-up `live_content`; the **same pre-loaded** `candidate_data` dict is passed again to the follow-up `do_task` (~1181).

**Mismatch / design intent:**

- **Not faithful in the strict sense:** the primary turn never *needs* `~~/get_candidate_data~~` for token resolution — the blob is already on the agent context. The contact task is redundant for library fields (`contact`, `context`, `artifacts`) already in `build_candidate_token_view`.
- **Meaningful delta when task *is* used:** full-row fetch (empty param) adds **`agent_story`** and returns the raw DB row shape (name columns + nested `candidate_data` + meta keys like `topic_menu`, `lifecycle`). Direct path uses **`build_candidate_token_view`** which flattens library blobs and **excludes meta + agent_story** (`candidate.py:88–102`, `agent.py:410–437`).
- **Dotted-path param:** walks **only** inner `candidate_data` — not top-level name columns. Same data source as direct access, different API surface for the agent follow-up turn.
- **Verdict:** Architecture is **dual-path by design** — context injection for tokens, contact task for agent-initiated reads (especially full row / agent_story / meta). Low runtime fidelity to calling the task because pre-injection makes it optional, not because callers bypass a required gate.

---

## File inventory (`src/`)

| File | Pattern | Fields / paths | Why | Faithful to `get_candidate_data`? |
|------|---------|----------------|-----|-----------------------------------|
| `src/utils/config.py` | B, config | `CONTACT_TASK_CONFIG` registration; `resolve_tokens` walks `candidate_data` paths; `TOPIC_MENU`/`SURFER` meta keys; contact skill ACL paths | Token catalog + contact task registry | **NA** — defines the task, doesn't call it |
| `src/core/tracker.py` | A (handler), B | Handler: full row or dotted `candidate_data` path + `agent_story`. Elsewhere: `_candidate_data_for_job` loads blob via `get_candidate` for job resume/cover | Contact task implementation + job artifact prep | **Y** for handler; **N** for `_candidate_data_for_job` (direct load) |
| `src/core/contact.py` | A, B, C, D | Dispatch infra; Estelle pre-loads blob → `do_task`; skill saves via `save_candidate_data`; Slack resolve reads `contact.slack_user_id` | Contact turn loop, ACL writes, prospect create | **N** — primary path pre-injects blob; task is optional second step |
| `src/core/candidate.py` | B, D | `get_candidate`, `save_candidate_data`, `build_candidate_token_view`; reads/writes all library + meta sections | Core CRUD + token view builder | **N** — canonical direct DB access layer |
| `src/core/agent.py` | B, C | `_token_view_for_do_task`: load by id, full row ctx, or raw blob; `do_task` token resolution | All agent tasks | **N** — never routes through contact dispatch |
| `src/core/consult.py` | C | Passes `ctx["candidate_data"]` into sub-tasks; `_candidate_data_for_job` via tracker | Consult chains / prefilter | **N** |
| `src/core/builder.py` | B, C | `_coerce_candidate_blob`; reads `artifacts.base_resume`, `context.raw_sample`, resume structure | Resume/cover HTML build | **N** |
| `src/core/meteorite.py` | B | `get_candidate` for email bind, land paths; `_resolve_slack_dm_channel` reads `contact.slack_user_id` | Meteorite intake + Slack DM | **N** |
| `src/core/gazer.py` | C | Accepts `candidate_data` dict or inner blob from ctx | Gazer scrape contact task context | **N** |
| `src/core/intake.py` | B, D | Reads/writes `context`, `intakes_old` via `get_candidate` + `save_candidate_data` | Intake chat persistence | **N** |
| `src/core/dispatcher.py` | B | `database.get_candidate` for dispatch template copy | Batch dispatch setup | **N** |
| `src/core/roster.py` | B | `get_candidate` for rubric criteria in roster flows | Job roster agent context | **N** |
| `src/ui/api/api_candidate.py` | B, D, E | CRUD API: returns/merges full `candidate_data`; profile/context/artifacts endpoints | Frontend candidate editor | **N** |
| `src/ui/api/api_admin.py` | B, E | `build_candidate_token_view` for preview/token count; admin agent screens | Admin tooling | **N** |
| `src/ui/api/api_inbox.py` | B | Resolves email paths against row + `candidate_data` (`CANDIDATE_LOOKUP_CONFIG`) | Inbox candidate filter | **N** |
| `src/ui/api/api_intake.py` | B | Existence checks via `get_candidate` | Intake API gate | **N** |
| `src/ui/api/api_surfer.py` | B | Existence checks via `get_candidate` | Surfer consent API gate | **N** |
| `src/ui/api/api_system.py` | B | `get_candidate` for system endpoints | System API | **N** |

## Frontend (`src/ui/frontend/`)

| File | Pattern | Summary | Faithful? |
|------|---------|---------|-----------|
| `contexts/CandidateContext.tsx` | E | Holds selected candidate + `candidate_data` from API | **N** |
| `components/ContextTextPage.tsx` | E | Edits `candidate_data.context.*` prose fields | **N** |
| `components/ProfileTextPage.tsx` | E | Edits contact / profile-adjacent blob fields | **N** |
| `components/ArtifactEditor.tsx` | E | Edits artifact rubric/resume sections | **N** |
| `components/JobAnalysisReportModal.tsx` | E | Displays job analysis using candidate context from API | **N** |
| `components/AgentAnalysisHeader.tsx` | E | Shows candidate-linked agent analysis header | **N** |
| `components/Time.tsx` | E | Reads candidate timezone from blob | **N** |
| `lib/artifactBlobHasContent.ts` | E | Utility: non-empty check on artifact blob slices | **N** |
| `pages/CandidateProfile.tsx` | E | Profile page CRUD on blob sections | **N** |
| `pages/CandidateIntake.tsx` | E | Intake UI reads candidate state/blob | **N** |
| `pages/AdminManageCandidates.tsx` | E | Admin list/detail on candidate rows | **N** |
| `pages/AdminAnthropicAdHoc.tsx` | E | Ad-hoc agent with candidate_data from API | **N** |
| `pages/AdminPerformanceMonitor.tsx` | E | Perf monitor scoped to candidate | **N** |
| `pages/ArtifactsCompanySearchTerms.tsx` | E | Artifacts page for company search terms | **N** |

Frontend/API layers never invoke the Slack contact-task path — expected (**NA** for contact-task fidelity).

## Tests (contrast only)

| File | Notes |
|------|-------|
| `tests/component/core/test_tracker.py` | Exercises `contact_task_get_candidate_data` handler directly |
| `tests/component/utils/test_config.py` | Asserts `get_candidate_data` in `CONTACT_TASK_CONFIG` |
| `tests/component/core/test_contact.py` | Contact turn + dispatch integration |
| `tests/component/core/test_candidate.py` | Blob CRUD + token view |
| Other `test_*.py` with `candidate_data` | Fixture/mocking for APIs and UI — mirror production direct-access patterns |

## Summary

- **13 Python modules** under `src/` touch `candidate_data` content; **14 frontend files** display or edit it.
- **`get_candidate_data` contact task** is implemented and wired, but **no static caller** uses it — only runtime Estelle markup.
- **Every non-contact-task consumer** loads via `get_candidate()` / API / pre-hydrated context (**pattern B/C**). This is consistent across agent, builder, consult, intake, meteorite, tracker job helpers, and UI.
- **Key gap:** Estelle turns inject the blob before the agent can call `~~/get_candidate_data~~`, and token resolution uses the flattened view without `agent_story`. The contact task remains the only path to expose full row + agent_story to the agent via markup follow-up.

**No code changes** — audit only.

---

_Implementation detail may live in git history on `origin/dev`._
