# AST-1403 — Update Adhoc Agent to mirror new task structure

**Component:** agent  
**Children:** AST-1411, AST-1412, AST-1413  
**Linear archived:** AST-1403 2026-09-09; AST-1411 2026-09-09; AST-1412 2026-09-09; AST-1413 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-16 21:43 | AST-1411 | docs | `acf80f984` | plan — ad hoc seven-segment resolve assemble persist |
| 2026-08-16 21:46 | AST-1411 | docs | `42cedceb2` | Joan validate — seven-segment backend wiring |
| 2026-08-16 21:48 | AST-1411 | code | `a576dea81` | resolve seven adhoc segments on preview |
| 2026-08-16 21:50 | AST-1411 | docs | `803d535c3` | review stub — seven-segment adhoc backend |
| 2026-08-16 21:50 | AST-1411 | code | `e2795bec2` | assemble persist seven-segment adhoc test |
| 2026-08-16 22:04 | AST-1411 | test | `0cf26ca1f` | seven-segment Ad Hoc preview/test coverage |
| 2026-08-16 22:05 | AST-1411 | merge-tests | `11477b6c6` | origin/tests 0cf26ca1fdb6790fa9a8ad443d022c9140b9c0b6 |
| 2026-08-16 22:11 | AST-1411 | docs | `57682a6c9` | Radia review — clean |
| 2026-08-16 22:24 | AST-1412 | docs | `1bab7d00f` | plan — Ad Hoc seven-segment editors and save |
| 2026-08-16 22:27 | AST-1412 | docs | `9dbf08ba2` | Joan validate — seven-segment editor UI |
| 2026-08-16 22:32 | AST-1412 | code | `cfac04267` | Preview and Test send seven segments |
| 2026-08-16 22:32 | AST-1412 | code | `7f697deb9` | seven-segment Ad Hoc editors and save |
| 2026-08-16 22:33 | AST-1412 | docs | `c8b4682d3` | review stub |
| 2026-08-16 22:37 | AST-1411 | docs | `46858a9df` | Radia review — AST-1411 on publish ref |
| 2026-08-16 22:40 | AST-1412 | merge-tests | `79ed28a22` | origin/tests f14ad7a644c450638026d9cbf7f587ba583b86cb |
| 2026-08-16 22:40 | AST-1412 | test | `f14ad7a64` | seven-segment Ad Hoc editors and save coverage |
| 2026-08-16 22:43 | AST-1411 | revert | `cb045a882` | seven-segment Ad Hoc preview/test coverage" |
| 2026-08-16 22:47 | AST-1412 | docs | `88d28a9eb` | Radia review — clean |
| 2026-08-16 22:50 | AST-1412 | resolve | `bfd233792` | — clean |
| 2026-08-16 22:56 | AST-1403 | merge | `169df389f` | origin/ftr/AST-1403-update-adhoc-agent-to-mirror-new-task-struct |
| 2026-08-16 22:56 | AST-1412 | merge | `169df389f` | origin/ftr/AST-1403-update-adhoc-agent-to-mirror-new-task-struct |
| 2026-08-16 23:06 | AST-1413 | docs | `a65cf3e34` | plan — Ad Hoc preview modal and agent_data panes |
| 2026-08-16 23:10 | AST-1413 | docs | `50388ff9e` | Joan validate — preview modal plus panes |
| 2026-08-16 23:17 | AST-1413 | code | `31889c26c` | Ad Hoc Preview Prompt opens scrollable modal |
| 2026-08-16 23:19 | AST-1413 | code | `56bac7971` | show agent_data panes after Ad Hoc Test |
| 2026-08-16 23:20 | AST-1413 | docs | `d2d63f2ff` | review stub |
| 2026-08-16 23:26 | AST-1413 | merge-tests | `7290f7c48` | origin/tests e09f7f485a055985c01c20a0b8185486bb24032b |
| 2026-08-16 23:26 | AST-1413 | test | `e09f7f485` | Ad Hoc preview modal and agent_data panes |
| 2026-08-16 23:33 | AST-1413 | docs | `68885cf4f` | Radia review — preview modal and panes |
| 2026-09-09 17:53 | AST-1411 | docs | `8524bf4f9` | archive Linear issue content |
| 2026-09-09 17:53 | AST-1412 | docs | `9d580bebf` | archive Linear issue content |
| 2026-09-09 17:53 | AST-1413 | docs | `807417f85` | archive Linear issue content |
| 2026-09-09 18:04 | AST-1403 | docs | `8f574b759` | archive Linear issue content |

## Epic — AST-1403

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1403/update-adhoc-agent-to-mirror-new-task-structure · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: High / 8_

### Purpose

The Agent Ad Hoc workbench still authors prompts as the old three-slot layout (User / Cache / NoCache), while Manage Tasks and production `do_task` already use the seven-segment model (System, Cache A–D, No Cache, User). Operators cannot edit or save the new slots from Ad Hoc, Preview sits inline at the bottom of the page, and the Test result is a dumped text pane instead of the same agent_data block tabs used everywhere else. This epic brings Ad Hoc to parity with the current task structure so a workbench round-trip — load, edit, preview, test, save, inspect stored blocks — matches what production stores and what Execution History already shows.

### Functional scope

* **Seven-segment editors.** Agent Ad Hoc prompt inputs match Manage Tasks: System Prompt, Cache Block A, Cache Block B, Cache Block C, Cache Block D, No Cache Block, User Prompt. Loading a task fills every segment from that task’s saved content. Empty System at Preview and Test follows the same production rule as Manage Tasks: an empty System segment is filled from the selected agent’s content. Live content is not an editor; it still comes from the selected entity and appears in Preview when an entity is chosen.
* **Save maps to the real columns.** Save As writes each editor into the matching `agent_task` segment (System → system, Cache A → cache A, B–D → cache B–D, No Cache → no-cache, User → user). Overwrite confirmation treats any of the seven segments as existing content. Saving does not invent extra columns or remap Cache A into B–D.
* **Preview Prompt is a modal.** Preview Prompt opens a scrollable modal (same family as Manage Tasks preview), not an inline block at the bottom of the page. The modal shows the resolved seven segments plus live content, with empty slots visible as empty.
* **Test shows agent_data panes.** After Test, the workbench shows the standard agent_data tabbed panes (System, Cache A–D, No Cache, Task, Response — same order and meaning as Execution History). A dumped response text block at the bottom of the page is not the inspection surface. Timesheet/cost for that run remains visible with those panes.
* **Ad hoc Test persists complete blocks.** A workbench Test stores prompt and response blocks in `agent_data` for that run: System, each non-empty Cache A–D, No Cache (including live content when present), Task (user), and Response. Empty segments are omitted. Preview does not write `agent_data`. When `debug=True`, the store path logs what was **found** and what was **recorded** per block (index header, block type, outcome, identifier) using the AST-538 contract (`|` detail prefix; long payloads truncated 15 / omitted / 15). When `debug=False`, no new debug-contract lines.

### Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — Ad Hoc preview/test/save stay thin admin routes; segment resolve and persist stay out of React.
  * `pattern.ui.shared-button-roles` — Preview, Test, Save As, modal dismiss keep the shared labeled-button roles (Preview is secondary; Test is the commit).
  * `pattern.ui.icon-control` — modal close uses the shared icon-control, not a one-off × style.
  * `pattern.layers.import-discipline` — UI calls core/admin helpers; core writes `agent_data`; no UI → data.
  * `pattern.config.config-block` — `BLOCK_TYPES` remains the source of truth for stored block names and display order.
* **New patterns proposed** — none. This is Ad Hoc catching up to the AST-453 seven-segment model and the existing Execution History agent_data panes.
* **Applicable statutes**
  * Universal set (`tier: universal`, `status: active`) — product epic.
  * `astral.agent.do-task-delegation` — production hops stay on `do_task`; Ad Hoc remains the workbench runner (`run_adhoc` / workbench wrapper), but its segment assembly and `agent_data` writes must match the seven-segment helper production already uses. Do not fold Test into `do_task` (that would impose production schema validation on the workbench; AST-1394 already forbids overlaying type errors on a successful Test).
  * `astral.config.config-source-of-truth` — block types and task segment names from config, not a parallel Ad Hoc enum.
  * `astral.standards.debug-contract-gated` — store/debug lines only when `debug=True`.
  * `astral.standards.dry-and-focused-functions` — reuse seven-segment assemble/store and the existing agent_data pane component; do not fork a second block model.
  * `astral.standards.no-hardcoded-sets` — display order follows `BLOCK_TYPES`, not a page-local list that drifts.
  * `astral.layers.import-direction` / `astral.layers.ui-config-driven-business-logic` — token resolve and persist in core/API; React renders.
  * `astral.standards.in-scope-only` / `astral.standards.database-header-inventory` — no new tables; existing `agent_task` seven columns and `agent_data` only.
  * `astral.patterns.require-auth-on-protected-endpoints` — admin Ad Hoc routes stay authenticated.
  * `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — Ad Hoc page and shared modal/pane components stay in the established UI layout.
  * `astral.standards.logging-via-utils` / `astral.standards.data-raises-caller-logs` — data layer still raises; core logs store failures.

### Boundaries

* Does **not** change Manage Tasks, production `do_task` assembly, dispatch, or `run_next` chain tokens.
* Does **not** add or rename `agent_task` columns (Cache A remains the existing cache slot; B–D already exist).
* Does **not** re-do AST-1392 / AST-1393 / AST-1394 (success body stringify and Test overlay). Those stay landed; this epic is the remaining seven-segment + inspection gap.
* Does **not** send Ad Hoc Test through `do_task` schema/grade validation. A successful provider reply still displays; persist still stores text.
* Does **not** author prompt copy for any product task, and does not change seed rows.
* Does **not** replace Execution History; it reuses the same agent_data tabbed panes on the workbench after Test.
* Must **not** break: pure ad hoc (no task key), entity picker / batch-first-N, token resolve, timesheets, Execution History rows with `adhoc-<task_key>`, Preview-does-not-ledger.

### Acceptance criteria

1. With a task that has distinct text in System and Cache A–D, loading it on Agent Ad Hoc shows each segment in the matching editor. Save As to that task (or another) and reload in Manage Tasks shows the same seven strings in the same slots.
2. A task whose only cache content is in Cache B (Cache A empty) round-trips through Ad Hoc load → Save As without moving that text into Cache A.
3. Preview Prompt opens a scrollable modal. The page body does not grow an inline resolved-preview block. The modal has tabs for System, Cache A–D, No Cache, User, and Live Content; resolved text matches what Test will send for those slots.
4. After a successful Test, the workbench shows agent_data tabs for that run (System, each stored Cache A–D, No Cache, Task, Response). Response is the stored Response block, not a separate dumped pane. Preview alone does not create or refresh those panes from a new batch.
5. For a Test whose editors have System + Cache A + Cache C + User populated (B and D empty), `agent_data` for that batch contains SYSTEM, CACHE_A, CACHE_C, TASK, and RESPONSE, and does not contain empty CACHE_B or CACHE_D rows. Opening the same batch from Execution History shows the same blocks.
6. Empty System in the editors still sends the selected agent’s content at Preview and Test (production fallback); Save As with empty System leaves `system_prompt` empty on the row.
7. When `debug=True` on a Test that stores multiple blocks, logs show a per-block index header plus found → recorded detail; when `debug=False`, that Test adds no new debug-contract lines.

### Dependencies and blockers

* **AST-453 / AST-454 / AST-456** (Done) — seven-segment `agent_task` persistence and Manage Tasks UI. This epic consumes that shape; it does not re-specify it.
* **AST-514 / AST-515** (Done) — Ad Hoc Test already writes ledger + `agent_data`; this epic completes the missing slots and the workbench inspection surface.
* **AST-1392 / AST-1393 / AST-1394** (Done) — RESPONSE stringify for object payloads. Do not regress.
* **AST-1290 / AST-1294** (User Testing) — html_links completeness; no shared scope.

none blocking start.

### Open questions

none

### Proposed child tickets


##### 1!!!: **Ad Hoc seven-segment resolve, assemble, persist - Ada**

Own the backend path: preview and test accept all seven segments; token-resolve each; assemble and send Cache A–D as separate cached blocks (empty omitted); workbench Test stores those blocks plus No Cache / Task / Response; Test response includes enough identity for the workbench to load that run’s agent_data panes. Save As already has columns — this child must not drop B–D on the way through preview/test/store. Does **not** own React editors, the preview modal, or the on-page agent_data panes (those are #2 / #3).
**Citations:** `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.config.config-source-of-truth`, `astral.standards.dry-and-focused-functions`
**Estimate: 5**

##### 2!: **Ad Hoc seven-segment editors and save - Hedy**

After #1. Agent Ad Hoc editors match Manage Tasks’ seven segments; fetch-from-task and Save As read/write all seven columns; overwrite/has-content treats any populated segment as content; Preview and Test requests send all seven fields. Does **not** own the preview modal chrome or the post-Test agent_data panes (#3).
**Citations:** `pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.ui.frontend-file-placement`, `astral.standards.no-hardcoded-sets`
**Estimate: 3**

##### 3: **Ad Hoc preview modal and agent_data panes - Katherine**

After #2. Preview Prompt opens the shared scrollable modal with seven-segment + live-content tabs (no inline preview at the bottom). After Test, the workbench shows the same agent_data tabbed panes as Execution History for that run (including timesheet/cost already shown there). Does **not** change how blocks are stored (#1) or which editors exist (#2).
**Citations:** `pattern.ui.shared-button-roles`, `pattern.ui.icon-control`, `pattern.config.config-block`, `astral.ui.frontend-file-placement`, `astral.standards.dry-and-focused-functions`
**Estimate: 2**

---

### Original brief

Currently the Adhoc Agent does not support System, Cache A, etc..
he
Please update it so that the inputs are identical, and saving the task to the agent_tasks table correctly puts the content blocks where they should go.

Also please make the "Preview Prompt" a scrollable modal popup, rather than displaying at the bottom of the screen, and instead, display our standard tabbed panes of agent_data for the ad hoc response.

Confirm that the agent_data is successfully saved from ad hoc calls, as well (I was having some spotty coverage when testing earlier).

#### Comments


##### chuckles — 2026-08-17T06:11:36.326Z

AST-1413 STALE(dev+88) — @Katherine Johnson refresh sub/* (merge origin/dev + origin/ftr/AST-1403-update-adhoc-agent-to-mirror-new-task-structure) then republish.

##### chuckles — 2026-08-17T05:55:29.982Z

AST-1412 REVIEW — merge-child blocked; recalling Hedy for `Merge remote-tracking branch` on the sub tip.

##### chuckles — 2026-08-17T04:44:30.078Z

AST-1411 estimate 5→3 — wiring onto existing seven-segment assemble/store helpers

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1411 — Ad Hoc seven-segment resolve, assemble, persist

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1411/ad-hoc-seven-segment-resolve-assemble-persist-update-adhoc-agent-to · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1403; blocks: AST-1412_

#### What this implements

Own the backend path: preview and test accept all seven segments; token-resolve each; assemble and send Cache A–D as separate cached blocks (empty omitted); workbench Test stores those blocks plus No Cache / Task / Response; Test response includes enough identity for the workbench to load that run’s agent_data panes. Save As already has columns — this child must not drop B–D on the way through preview/test/store. Does **not** own React editors, the preview modal, or the on-page agent_data panes (those are #2 / #3).

#### Citations

`pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.config.config-source-of-truth`, `astral.standards.dry-and-focused-functions`

#### Acceptance criteria

- [X] 5. For a Test whose editors have System + Cache A + Cache C + User populated (B and D empty), `agent_data` for that batch contains SYSTEM, CACHE_A, CACHE_C, TASK, and RESPONSE, and does not contain empty CACHE_B or CACHE_D rows. Opening the same batch from Execution History shows the same blocks.
- [X] 6. Empty System in the editors still sends the selected agent’s content at Preview and Test (production fallback); Save As with empty System leaves `system_prompt` empty on the row.
- [X] 7. When `debug=True` on a Test that stores multiple blocks, logs show a per-block index header plus found → recorded detail; when `debug=False`, that Test adds no new debug-contract lines.

(Parent AC 3–4 modal/panes belong to later siblings. This child supplies the preview/test payload shape and stored blocks those siblings display.)

#### Boundaries

- [X] Does **not** own React editors, the preview modal, or the on-page agent_data panes (siblings #2 / #3).
- [X] Does **not** change Manage Tasks, production `do_task` assembly, dispatch, or `run_next`.
- [X] Does **not** re-do AST-1392 / AST-1393 / AST-1394 success-body stringify.

#### Notes for planning

Reuse the seven-segment assemble/store helper production already uses. Empty cache slots omitted. When `debug=True`, found → recorded per stored block (AST-538). Estimate: 5

#### QA test manifest

**Publish:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `11477b6c6664e3f60c9fe23519e86e40d6b0f5c7`

**Bible shasums** (on publish ref):

* `docs/test-bible/core/agent.md` `090e04d0088f720b5433d78f4476ab816aeb8542`
* `docs/test-bible/ui/api/api_admin.md` `f0912468fc3fa9d50db062364a0383f44bf69e8f`

1. Existing workbench ledger + `batch_id` / four-slot store kwargs: `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`
2. RESPONSE stringify regression: `tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody`
3. Seven-segment persist / assemble / Style D: `tests/component/core/test_agent.py::TestAst1411AdhocSevenSegment`
4. Existing preview/test envelopes (revised mocks): `tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test`
5. Preview still ledger-free: `tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_does_not_create_dispatch_ledger`
6. Stringify HTTP regression: `tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText`
7. Seven-segment resolve/preview + Test identity: `tests/component/ui/api/test_api_admin.py::TestAst1411AdhocSevenSegment`
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody \
  tests/component/core/test_agent.py::TestAst1411AdhocSevenSegment \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_does_not_create_dispatch_ledger \
  tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText \
  tests/component/ui/api/test_api_admin.py::TestAst1411AdhocSevenSegment \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

##### Comments


###### radia — 2026-08-17T05:11:04.595Z

[code-rubric] PROCEED (Commit: 11477b6c) seven-segment adhoc wired

###### betty — 2026-08-17T05:06:16.607Z

`origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `11477b6c6664e3f60c9fe23519e86e40d6b0f5c7` · seven-segment workbench tests

###### ada — 2026-08-17T04:50:57.434Z

`origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `803d535c34aa93c33c6448cc6e0c75001105c55c`

Betty: `_store_prompt_blocks` debug is Style D index + found→recorded (replaces `agent_data_write` on prompt blocks only).

###### joan — 2026-08-17T04:46:57.170Z

[plan-rubric] PROCEED (Commit: acf80f98) seven-segment backend wiring

###### ada — 2026-08-17T04:43:31.613Z

`origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `acf80f98461d696f7a421a177df9198945357780` · seven-segment workbench plan

---

#### Stage 1: Resolve seven segments and Preview payload

**Done when:** `POST /api/admin/adhoc/preview` with `system_prompt`, `cache_prompt`, `cache_prompt_c`, and `user_prompt` populated (B and D omitted or `""`) returns JSON whose `system` is the token-resolved system (agent `content` when `system_prompt` is empty/whitespace), `cache` / `cache_a` equal the resolved Cache A text, `cache_c` equals the resolved Cache C text, `cache_b` and `cache_d` are `""`, `user` / `nocache` / `live_content` unchanged in meaning. Preview still does not write `agent_data` or a ledger row. `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, in `_resolve_adhoc`, keep agent/model/candidate/task_key_uuid/`_chain_context` / `resolved_task_system` as they are. Change **only** the prompt-resolution block that currently reads:
```python
       _cc = _chain_context(agent, cd, task_key, jc)
       agent_task_for_system = (
           {"system_prompt": ""} if agent_task_row is None and task_key == "adhoc" else (agent_task_row or {})
       )
       return {
           "system": resolved_task_system(agent, agent_task_for_system, cd, task_key, _cc, jc),
           "user": resolve_tokens(body.get("user_prompt", ""), cd, task_key, _cc, jc),
           "cache": resolve_tokens(body.get("cache_prompt", ""), cd, task_key, _cc, jc),
           "nocache": resolve_tokens(body.get("nocache_prompt", ""), cd, task_key, _cc, jc),
           ...
       }, None
```

   to:
```python
       _cc = _chain_context(agent, cd, task_key, jc)
       if "system_prompt" in body:
           # Editor sent the field (sibling #2): empty → agent content via resolved_task_system.
           agent_task_for_system = {"system_prompt": body.get("system_prompt") or ""}
       else:
           # Key omitted (today’s three-slot UI): keep DB task system, then agent content.
           agent_task_for_system = (
               {"system_prompt": ""} if agent_task_row is None and task_key == "adhoc" else (agent_task_row or {})
           )
       cache_a = resolve_tokens(body.get("cache_prompt", "") or "", cd, task_key, _cc, jc)
       cache_b = resolve_tokens(body.get("cache_prompt_b", "") or "", cd, task_key, _cc, jc)
       cache_c = resolve_tokens(body.get("cache_prompt_c", "") or "", cd, task_key, _cc, jc)
       cache_d = resolve_tokens(body.get("cache_prompt_d", "") or "", cd, task_key, _cc, jc)
       return {
           "system": resolved_task_system(agent, agent_task_for_system, cd, task_key, _cc, jc),
           "user": resolve_tokens(body.get("user_prompt", ""), cd, task_key, _cc, jc),
           "cache": cache_a,
           "cache_a": cache_a,
           "cache_b": cache_b,
           "cache_c": cache_c,
           "cache_d": cache_d,
           "nocache": resolve_tokens(body.get("nocache_prompt", ""), cd, task_key, _cc, jc),
           "model_code": model_code,
           "tier_meta": tier_meta,
           "temperature": temperature,
           "max_tokens": max_tokens,
           "candidate_id": candidate_id or None,
           "task_key_uuid": task_key_uuid,
           "api_key_override": api_key_override,
       }, None
```

   Request field names are the Manage Tasks / `PUT /tasks/<task_key>` names: `system_prompt`, `user_prompt`, `cache_prompt` (A), `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`. Do **not** invent `cache_a` on the request body.

2. In `adhoc_preview`, replace the `jsonify({...})` keys so the payload is:
```python
       return jsonify({
           "system": resolved["system"],
           "user": resolved["user"],
           "cache": resolved["cache"],
           "cache_a": resolved["cache_a"],
           "cache_b": resolved["cache_b"],
           "cache_c": resolved["cache_c"],
           "cache_d": resolved["cache_d"],
           "nocache": resolved["nocache"],
           "live_content": live_content,
       })
```

   Always include `cache_a`–`cache_d` (empty string when that slot resolved empty) so sibling #3 can show empty tabs. Keep `cache` as the Cache A alias so today’s Preview tab (`PreviewKey = "cache"`) still reads A. Do **not** call `save_agent_data` / ledger helpers from Preview.

3. Do **not** change `PUT /api/admin/tasks/<task_key>` (`update_task`). `save_agent_task(..., system_prompt=None)` means leave the column; `system_prompt=""` writes empty. Empty System on Save As must **not** copy agent `content` into `system_prompt`. That path is already correct if the key is present with `""`.

⚠️ **Decision:** `"system_prompt" in body` vs omitted. Production fallback is empty **segment** → agent `content` (`resolved_task_system`). Sibling #2 will send the key (including `""`). Until then the current page omits the key; treating omit as today’s DB-row system avoids Preview/Test dropping a loaded task’s saved system during the #1-only window. Empty string in the body never falls back to the DB task row — only to agent `content`.

⚠️ **Decision:** Reuse `resolved_task_system` for the system slot rather than a second fallback. Token resolve for A–D is the same `resolve_tokens(..., _cc, jc)` already used for Cache A.

#### Stage 2: Assemble Cache A–D, persist, Test identity, store debug

**Done when:** A workbench Test whose resolved segments are System + Cache A + Cache C + User (B and D empty, no nocache, no live) calls `_assemble_blocks_seven_segment` with four cache slots (B and D empty/omitted by that helper) and `_store_prompt_blocks(..., caches_resolved_four=(A, "", C, ""))`, so `agent_data` for that `batch_id` contains `SYSTEM`, `CACHE_A`, `CACHE_C`, `TASK`, and `RESPONSE` and does **not** contain `CACHE_B` or `CACHE_D` rows. `POST /api/admin/adhoc/test` HTTP 200 includes `batch_id` equal to the ledger id (`adhoc-<task_key>-<uuid>`). HTTP 500 `success: false` (soft provider failure that still returns a result dict) also includes that `batch_id`. The AST-1393 stringify + `_caller_response_blob` success store is unchanged. When `debug=True`, each stored **prompt** block emits one Style D index header plus found → recorded detail (payload truncated via `debug_detail_block`); when `debug=False`, this store path adds no new debug-contract lines. `python3 -m py_compile src/core/agent.py src/ui/api/api_admin.py` passes.

1. In `src/core/agent.py`, extend `run_adhoc` with three optional kwargs immediately after `cache_content` (defaults `None`): `cache_content_b`, `cache_content_c`, `cache_content_d`. Replace the `_assemble_blocks(...)` call with `_assemble_blocks_seven_segment`:
```python
       system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens = _assemble_blocks_seven_segment(
           system_content=system_content,
           user_content=user_content,
           caches_resolved_four=(cache_content, cache_content_b, cache_content_c, cache_content_d),
           nocache_content=nocache_content,
           live_content=live_content,
           model_code=model_code,
           skip_cache=False,
       )
```

   Leave `send_to_anthropic` / `send_to_deepseek` arguments unchanged. Do **not** delete `_assemble_blocks` (legacy wrapper still used elsewhere / tests). Existing `run_adhoc(..., cache_content="...")` callers stay valid: B/C/D default `None` and the seven-segment helper skips empty slots.

2. In `run_adhoc_workbench_test`, add the same three optional kwargs (`cache_content_b`, `cache_content_c`, `cache_content_d`, default `None`) after `cache_content`. Pass them through to `run_adhoc`. Replace the `_store_prompt_blocks` call that currently uses `cache_content=cache_content or None` with the production four-slot interface (**do not** also pass `cache_content=` — that raises `TypeError`):
```python
           _store_prompt_blocks(
               entity_type=entity_type,
               task_key=workbench_task_key,
               batch_id=batch_id,
               system_content=system_content,
               caches_resolved_four=(
                   cache_content or "",
                   cache_content_b or "",
                   cache_content_c or "",
                   cache_content_d or "",
               ),
               nocache_content=nocache_content,
               user_content=user_content,
               live_content=live_content,
               debug=debug,
           )
```

   Empty/whitespace cache slots are omitted inside `_store_prompt_blocks` (`if blob and blob.strip()`). Live content, when present, still stores a `NO_CACHE` row — same as production. Do **not** skip the `SYSTEM` row.

3. Still in `run_adhoc_workbench_test`, immediately before `return result` (the single successful-return at the end of the `try`, after ledger COMPLETED/FAILED update), set `result["batch_id"] = batch_id`. Do **not** add `batch_id` on the exception path that `raise`s after marking FAILED. Do **not** edit the AST-1393 success stringify block (`_caller_response_blob` / `debug_index` `outcome="serialized store"` / `_store_response_block`).

4. In `src/ui/api/api_admin.py` `adhoc_test`, pass the four resolved caches into `run_adhoc_workbench_test`. Use `.get` so existing tests that monkeypatch `_resolve_adhoc` with only `cache` / `nocache` do not KeyError:
```python
           result = asyncio.run(run_adhoc_workbench_test(
               workbench_task_key=task_key,
               candidate_id=resolved["candidate_id"],
               entity_id=entity_id or None,
               system_content=resolved["system"],
               user_content=resolved["user"],
               cache_content=resolved.get("cache") or None,
               cache_content_b=resolved.get("cache_b") or None,
               cache_content_c=resolved.get("cache_c") or None,
               cache_content_d=resolved.get("cache_d") or None,
               nocache_content=resolved.get("nocache") or None,
               live_content=live_content,
               response_format=task_response_format,
               model_code=resolved["model_code"],
               tier_meta=resolved.get("tier_meta"),
               temperature=resolved["temperature"],
               max_tokens=resolved["max_tokens"],
               api_key_override=resolved["api_key_override"],
               task_key_uuid=resolved["task_key_uuid"],
               debug=ui_llm_debug(),
           ))
```

5. In the same `adhoc_test`, after `if not result.get("success"):` keep HTTP 500, but include `batch_id` when present:
```python
       if not result.get("success"):
           err_body = {"success": False, "error": result.get("error", "Unknown error")}
           if result.get("batch_id"):
               err_body["batch_id"] = result["batch_id"]
           return jsonify(err_body), 500
```

   On the success `jsonify`, add `batch_id`:
```python
       return jsonify({
           "success": True,
           "response_text": response_text,
           "hydrated": hydrated,
           "timesheet": timesheet,
           "batch_id": result.get("batch_id"),
       })
```

   Leave `_caller_response_blob` extraction, encoded `_decode_payload`, `@require_admin`, and the exception→500 branch unchanged. Do **not** add schema/grade validation. Sibling #3 loads panes via existing `GET /api/agent_data/<batch_id>` (`api_system.py`) — do not add a new route.

6. In `_store_prompt_blocks`, keep the dual `caches_resolved_four` / `cache_content` contract and the skip-empty rules. Change the save loop so both paths collect `(block_type, content)` first, then save. Replace the inner `if debug: dbg.debug_detail("agent_data_write ...")` with Style D **per stored prompt block**:

   After building the list of segments to write (SYSTEM always; then A-only **or** A–D; then optional NO_CACHE / live NO_CACHE / TASK — same membership as today), loop `enumerate(segments, start=1)` with `total = len(segments)`. Inside `_save` after `save_agent_data`, when `debug` is True:
```python
           dbg = get_logger(__name__, debug_flag=True)
           outcome = result.get("outcome")
           dbg.debug_index(
               func="_store_prompt_blocks",
               index=index,
               total=total,
               identifier=f"{block_type}:{result.get('agent_data_id') or agent_data_id}",
               outcome=str(outcome) if outcome is not None else "saved",
           )
           dbg.debug_detail(f"found block_type={block_type} chars={len(content)}")
           dbg.debug_detail_block(content)
           dbg.debug_detail(
               f"recorded outcome={outcome} agent_data_id={result.get('agent_data_id')} "
               f"ref_agent_data_id={result.get('ref_agent_data_id')!r}"
           )
```

   Pass `index` and `total` into `_save`. When `debug=False`, emit none of those lines (no `debug_index` / `debug_detail` / `debug_detail_block`). Do **not** change `_store_response_block` (AST-977 `agent_data_write` + AST-1393 serialize found→recorded stay as-is). Do **not** add `logger.info("[DEBUG] …")`. `debug_detail_block` already truncates long payloads (15 / omitted / 15).

⚠️ **Decision:** Workbench store always uses `caches_resolved_four=`, never the legacy `cache_content=` branch, so Cache B–D cannot be dropped on the way through Test. `run_adhoc` still accepts `cache_content` as slot A for existing callers.

⚠️ **Decision:** Style D lives in the shared `_store_prompt_blocks` helper (the store production already uses) rather than a workbench-only logger. `do_task` assembly is untouched; `do_task` already calls this helper with `caches_resolved_four`. Debug lines remain gated on the existing `debug` flag.

⚠️ **Decision:** Test identity is `batch_id` only. That is the key `GET /api/agent_data/<batch_id>` already uses. Do not add a second Ad Hoc agent_data endpoint.

#### Execution contract

- Execute stages in order. One commit per stage on this epic worktree, then `git push origin HEAD:sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist`.
- Do not add files, config blocks, routes, or React editors not listed above.
- Do not fold Ad Hoc Test into `do_task` (schema/grade validation stays off the workbench).
- If a referenced helper signature has drifted, stop and comment on **AST-1403** with the Stage N blocked template — do not improvise.

#### Estimate

Confirm Chuckles estimate: 5 — revise to 3 because this is wiring Ad Hoc onto existing `_assemble_blocks_seven_segment` / `_store_prompt_blocks(caches_resolved_four=)` / `resolved_task_system`; no schema, no React, no new tables.

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1411
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `acf80f98461d696f7a421a177df9198945357780`

#### Traceability

AC5→Stage 2 (four-slot `caches_resolved_four` assemble/store; omit empty CACHE_B/D); AC6→Stage 1 (`system_prompt` in body → agent fallback; omit key → DB task system) + Stage 2 (Preview/Test send resolved system); AC7→Stage 2 step 6 (Style D `debug_index`/`debug_detail` per stored prompt block, gated on `debug`).

#### Findings

**acceptable** — Stage 2 step 6 refactors shared `_store_prompt_blocks` debug emission (not workbench-only). Intentional: parent functional scope requires found→recorded per block on the store path; reuses the production helper rather than forking.

**acceptable** — No explicit Self-Assessment conf block; stages + Done-when criteria are specific enough for this wiring-only scope.

context_tokens≈32000

[plan-rubric] PROCEED (Commit: acf80f98) seven-segment backend wiring

---

#### Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist`
**Product commits:** `a576dea8` (Stage 1 — seven-segment `_resolve_adhoc` + Preview keys), `e2795bec` (Stage 2 — `_assemble_blocks_seven_segment` / `caches_resolved_four` store, Test `batch_id`, Style D on `_store_prompt_blocks`)

React editors, preview modal, panes, Save As PUT, `do_task` assembly, and AST-1393 stringify left untouched.

#### Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1411
**Publish ref:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `11477b6c6664e3f60c9fe23519e86e40d6b0f5c7`
**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` (14 files; product: `src/core/agent.py`, `src/ui/api/api_admin.py`; plus Betty `merge-tests` / test-bible / `tests/**`)

**Status gate:** Spawn prompt `Tests Passed` — trusted.

**Joan:** plan-rubric APPROVED attached; no Excluded statute list — no straggler callouts.

#### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No confidence/scoring paths touched |
| astral.agent.do-task-delegation | scoped | conforms | Ad Hoc still delegates I/O to externals; no new inline provider calls |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade/vector validation touched |
| astral.batch.batch-id-first | scoped | conforms | Workbench still sets `log_batch_id` before store; `batch_id` returned on soft-fail |
| astral.batch.batch-id-format | scoped | conforms | Existing `adhoc-{task_key}-{uuid}` ledger id unchanged |
| astral.batch.claim-process-release | scoped | not-applicable | No batch claim/clear helpers changed |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No latest-response selection logic changed |
| astral.config.config-source-of-truth | scoped | not-applicable | No config surface changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug/artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike/debug-dir paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | `dispatcher.py` / seed paths untouched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No `run_next` / chain authority changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `ast-1411-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Product `src/**` commits are engineer (`code(AST-1411)`); test/bible via Betty |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits limited to `src/`; test tree is Betty lane |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No new core→external assembly or I/O |
| astral.layers.import-direction | scoped | conforms | No new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | API resolves tokens/server-side; no hardcoded UI state |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Empty CACHE_B/D omitted via `strip()`; intentional per plan |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render/consult orchestration |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` unchanged on preview/test |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | Seed/admin-json paths untouched |
| astral.seed.archie-catalog-wins | scoped | not-applicable | Dispatcher/catalog paths untouched |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No seed hot-path changes |
| astral.seed.define-approved | scoped | not-applicable | No define/seed approval flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row seed logic |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer logging added |
| astral.standards.database-header-inventory | scoped | not-applicable | No `src/data/**` changes |
| astral.standards.debug-contract-gated | scoped | conforms | Style D index/found/recorded gated on `debug=True`; no `[DEBUG]` info spam |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses production helpers; segment-collect refactor is bounded |
| astral.standards.in-scope-only | scoped | conforms | Product diff limited to planned `agent.py` / `api_admin.py` wiring |
| astral.standards.logging-via-utils | scoped | conforms | Debug via `get_logger(..., debug_flag=True)` |
| astral.standards.names-not-ticket-ids | scoped | conforms | No ticket-id symbol names in product code |
| astral.standards.no-cross-contamination | scoped | conforms | Ad Hoc wiring only; `do_task` assembly untouched |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new hardcoded business sets |
| astral.standards.public-then-helpers | scoped | conforms | Changes stay in existing public entrypoints/helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No `src/utils/**` changes |
| astral.state.core-decides-transitions | scoped | not-applicable | No job/roster transition logic |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job prior-state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No daisy-chain run logic |
| astral.ui.frontend-file-placement | scoped | not-applicable | No `src/ui/frontend/**` product changes |
| astral.ui.naming-conventions | scoped | conforms | Preview keys follow existing `cache_prompt_*` naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No worker/config deployment changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip `merge-tests(AST-1411): origin/tests 0cf26ca1` present |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests` vocabulary on branch |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish ref; diff vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | Child `sub/AST-1403/AST-1411-...` topology |
| orch.git.merge-on-checkout | universal | conforms | No merge/rebase violations in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No forbidden git ops in artifact |
| orch.git.no-dev-agent-branches | universal | conforms | Publish on `sub/*`, not agent-named dev branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1403` worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch classes introduced |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Plan decisions documented; no new product forks |
| orch.pipeline.plan-is-bible | universal | conforms | Implementation matches staged plan Done-when |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code diff |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed per pipeline |
| orch.roles.archie-approves-statutes | universal | conforms | No canon statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible changes on Betty commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee; review recommend-only |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-ban evidence in diff |

**Active set scored:** 65 / 65

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan/parent cite no catalog patterns |

#### Plan adherence

Stage 1 and Stage 2 match the issue doc Done-when criteria:

- **`_resolve_adhoc`:** token-resolves A–D; `system_prompt in body` vs omitted behavior matches the documented decision; Preview returns `cache` alias plus `cache_a`–`cache_d`.
- **`run_adhoc` / `run_adhoc_workbench_test`:** `_assemble_blocks_seven_segment` with four slots; workbench store uses `caches_resolved_four=` only (no legacy `cache_content=`).
- **`adhoc_test`:** forwards four caches via `.get`; returns `batch_id` on HTTP 200 and soft-fail 500; exception path that re-raises still omits `batch_id` (plan step 3).
- **`_store_prompt_blocks`:** segment collect → per-block Style D (`debug_index` N/M, found, `debug_detail_block`, recorded) when `debug=True`; quiet when `debug=False`.
- **Out of scope respected:** no React, no Save As PUT, no `do_task` / AST-1393 stringify edits, no new routes.

**Estimate (3):** footprint fits — two product files, wiring onto existing helpers.

Betty coverage (`TestAst1411*`, revised `TestAst515*`, `test_api_admin.py`) aligns with manifest intent in `docs/test-bible/core/agent.md` and `docs/test-bible/ui/api/api_admin.md`.

#### Findings


##### fix-now

(none)

##### discuss

(none)

##### advisory

- **Publish-ref cargo:** branch tip includes Betty `test(AST-1408)` frontend cases via `merge-tests` — not AST-1411 product scope; expected for Tests Passed. Downstream `merge-child` should treat as tests-line alignment, not #1411 feature scope.
- **Shared helper blast radius:** `_store_prompt_blocks` Style D applies to production `do_task` store path too — Joan/plan marked acceptable; operators will see new per-block debug on production store when `debug=True`.

#### What's solid

- Clean wiring onto existing `_assemble_blocks_seven_segment` / `_store_prompt_blocks(caches_resolved_four=)` / `resolved_task_system` — no parallel Ad Hoc store fork.
- Empty cache omission and SYSTEM-always-store semantics preserved.
- `batch_id` identity for sibling #3 (`GET /api/agent_data/<batch_id>`) is correct on success and provider soft-fail.
- Style D test (`test_store_prompt_blocks_style_d_debug_gated`) asserts both `debug=True` emission and `debug=False` quiet.

#### Frame diff

| Planned | Landed |
|---------|--------|
| `api_admin.py` — seven-segment resolve + Preview keys + Test forward/`batch_id` | Matches (`a576dea8`) |
| `agent.py` — assemble/store/batch_id/Style D | Matches (`e2795bec`) |
| No frontend / Save As / `do_task` / AST-1393 block | Confirmed absent from product diff |
| Tests (Betty) | Present via `0cf26ca1` + `merge-tests` (includes AST-1408 frontend tests on tests line) |

#### Recommended actions (downstream — not executed here)

- Chuckles: append this artifact to issue doc, `docs()` commit on sub-branch, post slim upshot `--as radia`, move to **Review Posted**.
- datt: **PROCEED** → User Testing (no `resolve-child` needed).

context_tokens≈38000

---

[code-rubric] PROCEED (Commit: 11477b6c) seven-segment adhoc wired

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/api/api_admin.py` | `_resolve_adhoc` token-resolves all seven body segments; Pre | `e2795bec2` `a576dea81` |
| ✓ | `src/core/agent.py` | `run_adhoc` / `run_adhoc_workbench_test` assemble and store  | `e2795bec2` |
| | _tests_ | — | 2 file(s) |

### AST-1412 — Ad Hoc seven-segment editors and save

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1412/ad-hoc-seven-segment-editors-and-save-update-adhoc-agent-to-mirror-new · Status at archive: Archive · Project: Astral Agent · Assignee: hedy · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1403; blocks: AST-1413_

#### What this implements

After #1. Agent Ad Hoc editors match Manage Tasks’ seven segments; fetch-from-task and Save As read/write all seven columns; overwrite/has-content treats any populated segment as content; Preview and Test requests send all seven fields. Does **not** own the preview modal chrome or the post-Test agent_data panes (#3).

#### Citations

`pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.ui.frontend-file-placement`, `astral.standards.no-hardcoded-sets`

#### Acceptance criteria

- [X] With a task that has distinct text in System and Cache A–D, loading it on Agent Ad Hoc shows each segment in the matching editor. Save As to that task (or another) and reload in Manage Tasks shows the same seven strings in the same slots.
- [X] A task whose only cache content is in Cache B (Cache A empty) round-trips through Ad Hoc load → Save As without moving that text into Cache A.
- [X] Empty System in the editors still sends the selected agent’s content at Preview and Test (production fallback); Save As with empty System leaves `system_prompt` empty on the row.

#### Boundaries

- [X] Does **not** own the preview modal chrome or the post-Test agent_data panes (sibling #3). Does **not** own backend assemble/store (sibling #1). Does **not** change Manage Tasks.

#### Notes for planning

After #1. Seven editors matching Manage Tasks; Save As maps System / Cache A–D / No Cache / User to the existing `agent_task` columns. Estimate: 3

#### QA test manifest

**Publish:** `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` @ `79ed28a22566689192785d782878c9f3e072e10f`

**Bible shasums** (on publish ref):

* `docs/test-bible/frontend/pages.md` `63f89f403f15d5917ac03d98372c4a4492e103ec`
* `docs/test-bible/ui/api/api_admin.md` `bcbba9961fe6fb39a99c561d053a4ef6c3d1fce5`

1. Routed Agent Ad Hoc page (§6c) — seven tabs, Cache-B isolation, Preview/Test/Save As seven keys, overwrite ●: `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`
2. `_enrich_tasks` seven `*_len` (Cache-B-only): `tests/component/ui/api/test_api_admin.py::TestAst1412EnrichTaskLens`
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx

./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1412EnrichTaskLens \
  -q
```

**Pass criterion:** Vitest + `TestAst1412EnrichTaskLens` green — not zero-arg harness / branch-lock gate.

##### Comments


###### chuckles — 2026-08-17T05:55:28.974Z

[merge-child] blocked: validate-sub-log — git pull merge on sub (`c374594a Merge remote-tracking branch 'origin/ftr/AST-1403-update-adhoc-agent-to-mirror-new-task-structure'`). @Hedy Lamarr — rewrite that merge off the publish tip (`git fetch && git merge origin/ftr/AST-1403-update-adhoc-agent-to-mirror-new-task-structure -m "merge(AST-1412): origin/ftr/AST-1403-update-adhoc-agent-to-mirror-new-task-structure"`), force-with-lease push `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` only, stay User Testing.

###### hedy — 2026-08-17T05:54:01.411Z

`origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` @ `c374594a` · §9a clean · ftr dry-run clean

###### radia — 2026-08-17T05:47:57.154Z

[code-rubric] PROCEED (Commit: 79ed28a2) seven-segment editors wired

###### betty — 2026-08-17T05:41:59.090Z

`origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` @ `79ed28a22566689192785d782878c9f3e072e10f` · seven-segment editor tests

###### joan — 2026-08-17T05:27:48.130Z

[plan-rubric] PROCEED (Commit: 1bab7d00) seven-segment editor UI

###### hedy — 2026-08-17T05:24:34.057Z

`origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` @ `1bab7d00` · seven-segment editor plan

---

#### Stage 1: Seven editors, fetch, Save As, overwrite lens

**Done when:** Selecting a task whose GET `/api/admin/tasks/<task_key>` has distinct text in `system_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, and `user_prompt` fills seven Ad Hoc tabs labeled exactly like Manage Tasks (System Prompt, Cache Block A–D, No Cache Block, User Prompt) with those strings in those slots. A task whose only cache content is `cache_prompt_b` loads into Cache Block B with Cache Block A empty. Save As PUT sends all seven keys (including `system_prompt: ""` when that editor is empty) and does **not** omit B–D. Save As is enabled when any of the seven editors has non-whitespace content. Overwrite confirm and the Save As ● mark fire when **any** of the seven list `*_len` values is `> 0`, including Cache-B-only (A empty). `python3 -m py_compile src/ui/api/api_admin.py` and `cd src/ui/frontend && npx tsc -b --noEmit` pass.

1. In `src/ui/api/api_admin.py`, in `_enrich_tasks`, the `rows.append({...})` dict currently drops the char-count columns that `database.list_candidate_tasks()` already selects (`user_prompt_len`, `cache_prompt_len`, `cache_prompt_b_len`, `cache_prompt_c_len`, `cache_prompt_d_len`, `nocache_prompt_len`, `system_prompt_len`). Add those seven keys onto the appended dict (same `int(... or 0)` pattern already used for `len_a` / `len_b` above in this function):
```python
               "user_prompt_len":       int(t.get("user_prompt_len") or 0),
               "cache_prompt_len":      int(t.get("cache_prompt_len") or 0),
               "cache_prompt_b_len":    int(t.get("cache_prompt_b_len") or 0),
               "cache_prompt_c_len":    int(t.get("cache_prompt_c_len") or 0),
               "cache_prompt_d_len":    int(t.get("cache_prompt_d_len") or 0),
               "nocache_prompt_len":    int(t.get("nocache_prompt_len") or 0),
               "system_prompt_len":     int(t.get("system_prompt_len") or 0),
```

   Place them immediately after `"updated_at": t.get("updated_at"),` and before `**_grouping_from_agent_task_row(t, task_key)`. Do **not** change token fields, grouping, or Manage Tasks columns. Extra JSON keys are unused by `AdminTaskPrompts.tsx`.

2. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, replace the three-slot editor types/constants with Manage Tasks’ seven-segment edit keys and labels (same strings as `EDIT_PANEL_LABELS` / `VALID_EDIT_TAB_KEYS` in `AdminTaskPrompts.tsx`). Keep the existing inline **preview** tab type (`PreviewKey`) and `PREVIEW_TABS` unchanged (sibling #3 owns seven-tab preview chrome).

   Replace:
```ts
   type TabKey = "user" | "cache" | "nocache"
```

   and `const TABS: { key: TabKey; label: string }[] = [ ... User / Cache / NoCache ... ]`

   with:
```ts
   type TabKey = "system" | "cache" | "cache_b" | "cache_c" | "cache_d" | "nocache" | "user"

   const TABS: { key: TabKey; label: string }[] = [
     { key: "system",  label: "System Prompt" },
     { key: "cache",   label: "Cache Block A" },
     { key: "cache_b", label: "Cache Block B" },
     { key: "cache_c", label: "Cache Block C" },
     { key: "cache_d", label: "Cache Block D" },
     { key: "nocache", label: "No Cache Block" },
     { key: "user",    label: "User Prompt" },
   ]
```

   Tab order is System → Cache A–D → No Cache → User (same order as Manage Tasks accordion). Do **not** switch Ad Hoc from `TabBar` to `CollapsiblePanel`.

3. Extend `TaskSummary` with the seven lens (keep `task_key`):
```ts
   interface TaskSummary {
     task_key: string
     user_prompt_len?: number
     cache_prompt_len?: number
     cache_prompt_b_len?: number
     cache_prompt_c_len?: number
     cache_prompt_d_len?: number
     nocache_prompt_len?: number
     system_prompt_len?: number
   }
```

   Add a file-local helper (next to `byteSize`) used by Save As ● and overwrite:
```ts
   function taskHasExistingPrompts(t: TaskSummary): boolean {
     return (
       (t.system_prompt_len || 0) > 0 ||
       (t.user_prompt_len || 0) > 0 ||
       (t.cache_prompt_len || 0) > 0 ||
       (t.cache_prompt_b_len || 0) > 0 ||
       (t.cache_prompt_c_len || 0) > 0 ||
       (t.cache_prompt_d_len || 0) > 0 ||
       (t.nocache_prompt_len || 0) > 0
     )
   }
```

4. Keep `useLocalStorage` key `adhoc:cachePrompt` as **Cache A**. Add four more persisted editors (do **not** rename the existing three keys):
```ts
   const [systemPrompt, setSystemPrompt] = useLocalStorage<string>(`${LS}systemPrompt`, "")
   const [cachePromptB, setCachePromptB] = useLocalStorage<string>(`${LS}cachePromptB`, "")
   const [cachePromptC, setCachePromptC] = useLocalStorage<string>(`${LS}cachePromptC`, "")
   const [cachePromptD, setCachePromptD] = useLocalStorage<string>(`${LS}cachePromptD`, "")
```

   Keep `userPrompt` / `cachePrompt` / `nocachePrompt` / `activeTab` as they are (`activeTab` default remains `"user"`). Restored `"cache"` still means Cache A.

5. Add this helper inside the component (after the localStorage hooks, before `handlePreview`) so Save As / Preview / Test cannot drift field names. Request names are the Manage Tasks / `PUT /tasks/<task_key>` names — **not** `cache_a` on the request body (sibling #1 contract):
```ts
   function editorSegmentBody() {
     return {
       system_prompt: systemPrompt,
       user_prompt: userPrompt,
       cache_prompt: cachePrompt,
       cache_prompt_b: cachePromptB,
       cache_prompt_c: cachePromptC,
       cache_prompt_d: cachePromptD,
       nocache_prompt: nocachePrompt,
     }
   }
```

   Always include every key, including `""`. Omitting `system_prompt` is forbidden: sibling #1 treats a missing key as “use the DB task row,” and `save_agent_task(..., system_prompt=None)` means leave the column.

6. Replace `hasContent` with:
```ts
   const hasContent = [systemPrompt, userPrompt, cachePrompt, cachePromptB, cachePromptC, cachePromptD, nocachePrompt]
     .some(s => s.trim())
```

7. In the task-key `useEffect` fetch-confirm branch, replace `if (userPrompt || cachePrompt || nocachePrompt)` with the same seven strings (truthy, matching today’s three-slot confirm — whitespace counts as content for the replace banner).

8. In `doFetchFrom`, after `r.json()`, set all seven editors from the GET task row (`|| ""` when missing):
```ts
         setSystemPrompt(data.system_prompt || "")
         setUserPrompt(data.user_prompt || "")
         setCachePrompt(data.cache_prompt || "")
         setCachePromptB(data.cache_prompt_b || "")
         setCachePromptC(data.cache_prompt_c || "")
         setCachePromptD(data.cache_prompt_d || "")
         setNocachePrompt(data.nocache_prompt || "")
```

   Do **not** copy `cache_prompt_b` into `cachePrompt`. Do **not** fetch or write `run_next` / grouping / `agent_id` from this GET into the editors.

9. In `handleSaveAs`, replace the three-len `existing` check with `taskHasExistingPrompts(task)` (guard `task` the same way: `const task = tasks.find(...)`; `existing` is true only when `task` is found **and** `taskHasExistingPrompts(task)`). In the Save As dropdown row, replace the inline three-len `hasExisting` with `taskHasExistingPrompts(t)` (same ● suffix and gold color as today).

10. In `doSaveAs`, replace the PUT JSON body with:
```ts
      body: JSON.stringify({ agent_id: agentId || undefined, ...editorSegmentBody() }),
```

    Do **not** send `run_next`, `task_group_*`, or `task_name`. Empty System must be present as `system_prompt: ""` so PUT writes empty (`sp = body["system_prompt"]` when the key is in the body) and does **not** copy agent `content` into the row.

11. Replace the three-tab `TokenTextarea` switch with one textarea per `TABS` key. Placeholders and rows:

    | `activeTab` | placeholder | `rows` |
    |-------------|-------------|---------|
    | `system` | `Empty = use assigned agent content. {$SELECTED_AGENT} injects the agent system prompt at runtime.` | 16 |
    | `cache` | `Cache block A (ephemeral cached at API when non-empty).` | 22 |
    | `cache_b` | `Cache block B (optional).` | 22 |
    | `cache_c` | `Cache block C (optional).` | 22 |
    | `cache_d` | `Cache block D (optional).` | 22 |
    | `nocache` | `No-cache segment (dynamic context; not cached at API).` | 22 |
    | `user` | `User prompt content...` | 16 |

    Bind `value` / `onChange` to the matching state (`cache` → `cachePrompt` / `setCachePrompt`, `cache_b` → `cachePromptB` / `setCachePromptB`, …). Keep `className="dep-input"` and `tokens={tokenList}`.

12. Do **not** change Preview Prompt / ▶ Test button classes (`btn secondary` / `btn primary`), Save As (`btn secondary`), or confirm Yes/Cancel (`btn danger` / `btn secondary`). Do **not** restyle `.tabbed-ta-bar`. Do **not** edit the inline “Resolved Prompt Preview” block or the Test Response `<pre>` in this stage.

⚠️ **Decision:** Pass the existing `list_candidate_tasks` `*_len` columns through `_enrich_tasks` rather than GET-on-click for overwrite. The list query already has per-segment lengths; enrichment currently drops them, so today’s three-len check never sees Cache B–D (or System) on the real `/api/admin/tasks` payload. Spreading the seven ints onto the list JSON does not change Manage Tasks UI. Token fields (`system_prompt_tokens`) are the wrong signal — they include agent-content fallback and would false-positive overwrite on every tasked row.

⚠️ **Decision:** Keep Ad Hoc on `TabBar` (seven tabs) instead of copying Manage Tasks’ `CollapsiblePanel` accordion. Parent AC is segment parity (labels + columns), not chrome. Accordion would be an unplanned layout rewrite; sibling #3 already owns preview chrome.

⚠️ **Decision:** Duplicate Manage Tasks label strings in this page rather than a new shared module. Extracting labels would add a file or touch `AdminTaskPrompts.tsx` (out of scope). Editor tab keys are UI labels, not a `BLOCK_TYPES` / config enum (`BLOCK_TYPES` includes TASK / RESPONSE / FEEDBACK, which are not editors).

#### Stage 2: Preview and Test send all seven fields

**Done when:** `POST /api/admin/adhoc/preview` and `POST /api/admin/adhoc/test` JSON bodies include `system_prompt`, `user_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, and `nocache_prompt` on every call (empty string when that editor is empty). Cache B text is sent as `cache_prompt_b` only, not copied into `cache_prompt`. Empty System still sends `"system_prompt": ""` so sibling #1’s `"system_prompt" in body` path uses `resolved_task_system` (agent content) instead of the DB task row. The inline preview tabs and Test Response dump stay as they are (sibling #3). `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `handlePreview`, replace the three prompt fields in the `JSON.stringify({...})` object with a spread of `editorSegmentBody()` (keep `agent_id`, `task_key`, `entity_id`, `entity_ids`, `candidate_id` exactly as they are). Resulting prompt keys must be those seven names — do **not** send `cache_a`.

2. In `handleTest`, the same spread: replace `user_prompt` / `cache_prompt` / `nocache_prompt` with `...editorSegmentBody()`. Do **not** add `debug`. Do **not** read or display `batch_id` from the Test JSON (sibling #3 loads agent_data panes from that identity).

3. Leave `PREVIEW_TABS` as System / Cache / NoCache / User / Live Content. Sibling #1 keeps Preview JSON key `cache` as the Cache A alias, so today’s Cache preview tab still shows A. Do **not** add Cache B–D preview tabs here. Do **not** convert the inline preview into a modal. Do **not** replace the Test Response `<pre>` with agent_data panes.

4. Do **not** edit `tests/` or `docs/test-bible/**`. Existing Vitest cases that type “User prompt content...” and POST three prompt fields will need Betty’s manifest; if they fail because placeholders/body keys changed, `[qa-handoff]` — do not patch the test tree.

⚠️ **Decision:** Always send all seven keys (including `""`) rather than omitting empty ones. Sibling #1: omitted `system_prompt` means “use the DB task system until #2 lands”; empty string means production fallback to agent content at Preview/Test and empty column on Save As. Omitting `cache_prompt_b` on PUT would leave the column untouched (`None` = no write) and could not clear B.

#### Estimate

Confirm Chuckles estimate: 3 — agree

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1412
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` @ `1bab7d00f97c398089dddec934bcaa84f6ff404f`

#### Traceability

AC1→Stage 1 (seven editors, fetch/save all seven columns, seven-len overwrite ●); AC2→Stage 1 steps 8–10 (`cache_prompt_b` isolated, no slide into A); AC3→Stage 1 step 10 + Stage 2 (`system_prompt: ""` on Save/Preview/Test; sibling #1 resolves agent fallback).

#### Findings

**acceptable** — Duplicated Manage Tasks label strings instead of a shared module; plan documents why (`AdminTaskPrompts.tsx` out of scope).

**acceptable** — `_enrich_tasks` additive `*_len` passthrough on shared `/api/admin/tasks`; backward-compatible, correct lens for Cache-B-only overwrite.

**acceptable** — Stage 2 Preview/Test contract depends on AST-1411 `"system_prompt" in body` behavior; ticket ordering “after #1” matches dispatch.

context_tokens≈48000

#### Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save`
**Product commits:** `7f697deb` (Stage 1 — seven-segment editors and save), `cfac0426` (Stage 2 — Preview/Test send seven fields)

#### Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1412
**Publish ref:** `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` @ `79ed28a22566689192785d782878c9f3e072e10f`
**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save` (19 files; product: `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`; plus Betty `merge-tests` / test-bible / `tests/**`)

**Status gate:** Spawn prompt `Tests Passed` — trusted.

**Relations:** `blockedBy AST-1411` — frontend seven-key contract is correct; epic merge must land #1 backend before Preview/Test resolve B–D server-side. Not a defect in this diff.

**Joan:** plan-rubric APPROVED attached; no Excluded statute list — no straggler callouts.

#### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No confidence/scoring paths touched |
| astral.agent.do-task-delegation | scoped | not-applicable | No `src/core/**` changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade/vector validation touched |
| astral.batch.batch-id-first | scoped | not-applicable | No batch/ledger paths touched |
| astral.batch.batch-id-format | scoped | not-applicable | No `batch_id` construction |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/clear helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No response-selection logic |
| astral.config.config-source-of-truth | scoped | not-applicable | No config surface changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug/artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike/debug-dir paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | Dispatcher/seed paths untouched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No `run_next` changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `ast-1412-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Product `src/**` is engineer `code(AST-1412)` only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits limited to `src/`; test tree is Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No core/external changes |
| astral.layers.import-direction | scoped | conforms | UI-only edits; no new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Duplicated editor labels per plan; segment body from editor state, not hardcoded job state |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check handlers |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render/consult orchestration |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | Ad Hoc routes unchanged; list/tasks enrichment behind existing admin API |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | Seed/admin-json paths untouched |
| astral.seed.archie-catalog-wins | scoped | not-applicable | Dispatcher/catalog paths untouched |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No seed hot-path changes |
| astral.seed.define-approved | scoped | not-applicable | No define/seed approval flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row seed logic |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No data-layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | No `src/data/**` changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | No backend debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | `editorSegmentBody` / `taskHasExistingPrompts` centralize contract; `editors` map avoids seven copy-paste textareas |
| astral.standards.in-scope-only | scoped | conforms | Product limited to planned `_enrich_tasks` passthrough + Ad Hoc page |
| astral.standards.logging-via-utils | scoped | not-applicable | No runtime logging changes |
| astral.standards.names-not-ticket-ids | scoped | conforms | API field names match Manage Tasks / PUT contract |
| astral.standards.no-cross-contamination | scoped | conforms | `AdminTaskPrompts.tsx`, `agent.py`, Save As handler untouched |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new hardcoded business sets |
| astral.standards.public-then-helpers | scoped | conforms | File-local helpers beside component; no API surface churn |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No `src/utils/**` changes |
| astral.state.core-decides-transitions | scoped | not-applicable | No job/roster transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job prior-state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No daisy-chain run logic |
| astral.ui.frontend-file-placement | scoped | conforms | Changes stay in `pages/AdminAnthropicAdHoc.tsx` |
| astral.ui.naming-conventions | scoped | conforms | `cache_prompt_b` API / `cachePromptB` state follow existing A-pattern |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No worker/deployment changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip `merge-tests(AST-1412): origin/tests f14ad7a6` present |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests` on branch |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish ref; diff vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | Child `sub/AST-1403/AST-1412-...` topology |
| orch.git.merge-on-checkout | universal | conforms | No merge/rebase violations in artifact |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | Publish on `sub/*` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1403` worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch classes |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Label duplication / TabBar decisions documented in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Implementation matches staged Done-when |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code diff |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No canon statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible on Betty commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy assignee; review recommend-only |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-ban evidence in diff |

**Active set scored:** 65 / 65

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan cites no catalog patterns |

#### Plan adherence

**Stage 1** — matches Done-when:

- `_enrich_tasks` passes all seven `*_len` ints after `updated_at`, before grouping spread.
- Seven `TabBar` editors with Manage Tasks label strings and tab order (System → A–D → No Cache → User).
- `TaskSummary` + `taskHasExistingPrompts` cover Cache-B-only ● / overwrite.
- Four new `useLocalStorage` keys; `adhoc:cachePrompt` remains Cache A.
- `doFetchFrom` loads all seven columns without sliding B→A.
- `doSaveAs` PUT spreads `editorSegmentBody()`; always includes `system_prompt: ""` when empty.
- `hasContent` spans all seven editors; fetch-confirm checks all seven strings.
- Preview chrome / Test `<pre>` / `PREVIEW_TABS` unchanged.

**Stage 2** — matches Done-when:

- `handlePreview` / `handleTest` spread `editorSegmentBody()` (seven keys, no `cache_a`, no `debug`, no `batch_id` read).

**Out of scope respected:** no `AdminTaskPrompts.tsx`, no `agent.py`, no preview modal / agent_data panes, no shared label module.

**Estimate (3):** footprint fits — two product files, UI wiring only.

Betty coverage (`TestAst1412*` Vitest, `TestAst1412EnrichTaskLens` HTTP) aligns with `docs/test-bible/frontend/pages.md` and `docs/test-bible/ui/api/api_admin.md`.

#### Findings


##### fix-now

(none)

##### discuss

(none)

##### advisory

- **Epic ordering:** `blockedBy AST-1411` — this branch’s product diff vs `origin/dev` does not include #1 `_resolve_adhoc` backend; seven-key POST bodies are correct for when #1 is on `ftr`. `merge-child` must respect `blockedBy` order.
- **Publish-ref cargo:** `merge-tests` carries Betty commits for AST-1408, AST-1409, AST-1411 tests alongside AST-1412 — expected for Tests Passed; not #1412 product scope.
- **Label duplication:** editor labels duplicated from `AdminTaskPrompts.tsx` per plan — if Manage Tasks labels change later, both pages need manual sync (Joan marked acceptable).

#### What's solid

- `editorSegmentBody()` single source prevents Preview / Test / Save As field drift.
- Cache-B-only round-trip isolated (`cache_prompt_b` never slides into `cache_prompt`).
- Empty System always sent as `""` — correct for #1 `"system_prompt" in body` semantics and PUT empty-column write.
- `_enrich_tasks` additive JSON is backward-compatible for Manage Tasks.
- Vitest asserts all seven keys on preview/test/PUT and Cache-B-only ● marker.

#### Frame diff

| Planned | Landed |
|---------|--------|
| `api_admin.py` — seven `*_len` passthrough on `_enrich_tasks` | Matches (`7f697deb`) |
| `AdminAnthropicAdHoc.tsx` — seven editors, fetch, Save As, overwrite lens | Matches (`7f697deb`) |
| Preview/Test spread `editorSegmentBody()` | Matches (`cfac0426`) |
| No Manage Tasks / `agent.py` / preview modal / shared module | Confirmed absent |
| Tests (Betty) | `f14ad7a6` + `merge-tests` |

#### Recommended actions (downstream — not executed here)

- Chuckles: append artifact to issue doc, `docs()` commit on sub-branch, post slim upshot `--as radia`, move to **Review Posted**.
- datt: **PROCEED** → User Testing (no `resolve-child` needed).
- `merge-child`: roll up after AST-1411 per `blockedBy`.

context_tokens≈42000

#### Resolution (Hedy)

**Date:** 2026-08-17
**Review ref:** Radia @ `88d28a9e` — **fix-now:** none; **discuss:** none

No product changes. Advisory (blockedBy AST-1411, merge-tests cargo, duplicated Manage Tasks labels) is merge-child / already accepted in plan — not a code fix. §9a dry-run into `origin/dev` recorded at publish; `origin/ftr/AST-1403` not on origin yet.

**Verdict:** Ready for **User Testing**.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/api/api_admin.py` | Pass through the seven `*_len` fields `list_candidate_tasks` | `7f697deb9` |
| ✓ | `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Seven editors matching Manage Tasks labels/fields; fetch and | `cfac04267` `7f697deb9` |
| | _tests_ | — | 2 file(s) |

### AST-1413 — Ad Hoc preview modal and agent_data panes

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1413/ad-hoc-preview-modal-and-agent-data-panes-update-adhoc-agent-to-mirror · Status at archive: Archive · Project: Astral Agent · Assignee: katherine · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1403_

#### What this implements

After #2. Preview Prompt opens the shared scrollable modal with seven-segment + live-content tabs (no inline preview at the bottom). After Test, the workbench shows the same agent_data tabbed panes as Execution History for that run (including timesheet/cost already shown there). Does **not** change how blocks are stored (#1) or which editors exist (#2).

#### Citations

`pattern.ui.shared-button-roles`, `pattern.ui.icon-control`, `pattern.config.config-block`, `astral.ui.frontend-file-placement`, `astral.standards.dry-and-focused-functions`

#### Acceptance criteria

- [X] 3. Preview Prompt opens a scrollable modal. The page body does not grow an inline resolved-preview block. The modal has tabs for System, Cache A–D, No Cache, User, and Live Content; resolved text matches what Test will send for those slots.
- [X] 4. After a successful Test, the workbench shows agent_data tabs for that run (System, each stored Cache A–D, No Cache, Task, Response). Response is the stored Response block, not a separate dumped pane. Preview alone does not create or refresh those panes from a new batch.

#### Boundaries

- [X] Does **not** change how blocks are stored (sibling #1) or which editors exist (sibling #2). Does **not** replace Execution History; it reuses the same agent_data tabbed panes on the workbench after Test.

#### Notes for planning

After #2. Preview is the modal; post-Test inspection is the standard agent_data panes. Estimate: 2

#### QA test manifest

**Publish:** `origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes` @ `7290f7c486442935912b5d5a5f8c116ce3811f46`

**Bible shasums** (on publish ref):

* `docs/test-bible/frontend/pages.md` `6ea74a0d50ef3cd7609f416460337c66d05516be`

1. Routed Agent Ad Hoc page (§6c) — Preview modal, post-Test panes, AST-1394 chrome retarget: `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`
2. Execution History modal wrapper (extract regression): `tests/component/frontend/components/test_BatchAgentDataModal.test.tsx`
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

##### Comments


###### radia — 2026-08-17T06:33:27.858Z

[code-rubric] PROCEED (Commit: 7290f7c4) preview modal and panes

###### betty — 2026-08-17T06:26:48.670Z

`origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes` @ `7290f7c486442935912b5d5a5f8c116ce3811f46` · preview modal pane tests

###### joan — 2026-08-17T06:10:20.452Z

[plan-rubric] PROCEED (Commit: a65cf3e3) preview modal plus panes

###### katherine — 2026-08-17T06:07:15.687Z

`origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes` @ `a65cf3e34b3f5c26085176267399924a9945d2b1` · preview modal plus panes

---

#### Stage 1: Preview Prompt is a scrollable modal

**Done when:** Clicking Preview Prompt (after a 200 from `POST /api/admin/adhoc/preview`) opens `Modal` from `src/ui/frontend/src/components/Modal.tsx`. The page body does **not** contain the “Resolved Prompt Preview” heading or an inline preview `<pre>`. The modal `TabBar` has exactly these tabs, in this order: System, Cache A, Cache B, Cache C, Cache D, No Cache, User, Live Content. Empty slots render `(empty)`. Cache A text is `cache_a` from the JSON, falling back to `cache`. Closing the modal (header `icon-control` × or footer Cancel) hides it and does **not** call `GET /api/agent_data/...`. Preview Prompt / ▶ Test / Save As button classes are unchanged. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, add:
```ts
   import Modal from "../components/Modal"
```

   next to the existing `TabBar` / `TokenTextarea` imports.

2. Replace `type PreviewKey` and `PREVIEW_TABS` with:
```ts
   type PreviewKey = "system" | "cache_a" | "cache_b" | "cache_c" | "cache_d" | "nocache" | "user" | "live_content"

   const PREVIEW_TABS: { key: PreviewKey; label: string }[] = [
     { key: "system",       label: "System" },
     { key: "cache_a",      label: "Cache A" },
     { key: "cache_b",      label: "Cache B" },
     { key: "cache_c",      label: "Cache C" },
     { key: "cache_d",      label: "Cache D" },
     { key: "nocache",      label: "No Cache" },
     { key: "user",         label: "User" },
     { key: "live_content", label: "Live Content" },
   ]
```

   Delete `type PreviewData = Record<PreviewKey, string>`.

3. Add this file-local helper immediately after `taskHasExistingPrompts` (same shape as `previewField` in `AdminTaskPrompts.tsx`; do **not** import from that page):
```ts
   function previewField(tab: PreviewKey, data: Record<string, unknown> | null): string {
     if (!data) return ""
     const txt = (k: string): string => (typeof data[k] === "string" ? (data[k] as string) : "")
     switch (tab) {
       case "cache_a":
         return txt("cache_a") || txt("cache")
       default:
         return txt(tab)
     }
   }
```

4. Change preview state: `previewData` type becomes `Record<string, unknown> | null`. Add `const [previewOpen, setPreviewOpen] = useState(false)` next to `previewTab`. Keep `previewTab` default `"system"`.

5. In `handlePreview`, keep the POST body (`agent_id`, `task_key`, `entity_id` / `entity_ids`, `...editorSegmentBody()`, `candidate_id`) unchanged. Replace the success `.then(data => { setPreviewData(data as PreviewData); setPreviewTab("system") })` with:
```ts
         .then(data => {
           setPreviewData(data)
           setPreviewTab("system")
           setPreviewOpen(true)
         })
```

   Do **not** call `api("/api/agent_data/...")` here. Do **not** clear Test state (`response` / `timesheet` still exist in this stage).

6. Delete `byteSize` and `previewTabsWithSize` (modal tabs match Manage Tasks: labels only, no byte-size suffix).

7. Delete the entire JSX block `{previewData && ( … Resolved Prompt Preview … )}`. In its place, immediately before `<Toast … />`, add:
```tsx
         <Modal
           open={previewOpen}
           onClose={() => setPreviewOpen(false)}
           title={taskKey ? `Preview: ${taskKey}` : "Preview"}
         >
           <TabBar tabs={PREVIEW_TABS} active={previewTab} onChange={key => setPreviewTab(key)} />
           <pre style={{
             marginTop: 12, padding: 12, borderRadius: 4,
             background: "var(--bg-deep)", border: "1px solid var(--border)",
             color: "var(--text-primary)", fontFamily: "monospace", fontSize: 12,
             whiteSpace: "pre-wrap", wordBreak: "break-word",
             maxHeight: 500, overflow: "auto",
           }}>
             {previewField(previewTab, previewData) || "(empty)"}
           </pre>
         </Modal>
```

   Do **not** pass `size="wide"`. Do **not** pass `showFooter={false}` (Manage Tasks preview keeps the default Cancel footer). Close is the existing `Modal` `icon-control` × — do not add a second close button. Do **not** change Preview Prompt (`btn secondary`) / ▶ Test (`btn primary`) / Save As (`btn secondary`).

8. Leave the Response `<pre>` dump in this stage. Do **not** edit `TABS`, `editors`, `editorSegmentBody`, fetch/Save As, or entity picker.

⚠️ **Decision:** Same `Modal` family as Manage Tasks preview (default card width, header ×, Cancel footer, `TabBar` + scrollable `<pre maxHeight: 500>`), not `size="wide"`. Parent AC names the preview tabs System / Cache A–D / No Cache / User / Live Content — use those short labels, not Manage Tasks’ “System Prompt” / “Cache Block A” editor strings. Live Content is Ad Hoc–only (Manage Tasks preview has no live-content slot).

⚠️ **Decision:** Duplicate `previewField` here rather than sharing with `AdminTaskPrompts.tsx`. That page is out of scope; Cache A still needs the `cache_a` || `cache` alias sibling #1 kept on the Preview JSON.

#### Stage 2: After Test, workbench shows Execution History agent_data panes

**Done when:** A successful `POST /api/admin/adhoc/test` (HTTP 200, `success: true`, non-empty string `batch_id`) renders `BatchAgentDataPanes` on the workbench for that `batch_id` (tabs in `BLOCK_TYPE_ORDER` for stored blocks, including SYSTEM / each stored CACHE_A–D / NO_CACHE / TASK / RESPONSE, plus the existing Tokens & Cost summary). There is no Response `<pre>` dump and no Ad Hoc timesheet header next to it. Preview Prompt does not set, clear, or refetch `testBatchId`. Execution History still opens `BatchAgentDataModal` (wide modal) with the same pane body. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/BatchAgentDataModal.tsx`, keep `BLOCK_TYPE_ORDER`, fetch URLs, timesheet math, FEEDBACK hydrate, and CSS class names. Split as follows.

   Add:
```ts
   interface PanesProps {
     batchId: string
     candidateId?: string
     className?: string
   }
```

   Move the current `BatchAgentDataModal` function body (all hooks + the inner `<div className="batch-agent-data-wrapper">…</div>`) into:
```ts
   export function BatchAgentDataPanes({ batchId, candidateId, className }: PanesProps) {
```

   Drop the `if (!batchId) return` early-out in the fetch effect (`batchId` is now a required string). Change the wrapper to:
```tsx
       <div className={className ? `batch-agent-data-wrapper ${className}` : "batch-agent-data-wrapper"}>
```

   The default export becomes only the Execution History chrome:
```tsx
   export default function BatchAgentDataModal({ batchId, candidateId, onClose }: Props) {
     return (
       <Modal open={!!batchId} onClose={onClose} title={batchId ?? ""} size="wide">
         {batchId ? <BatchAgentDataPanes batchId={batchId} candidateId={candidateId} /> : null}
       </Modal>
     )
   }
```

   Do **not** change `AdminPerformanceMonitor.tsx` or `AdminVectorFeedback.tsx` imports (they keep the default Modal). Do **not** change `size="wide"` on that wrapper. Do **not** add FEEDBACK-omit logic for Ad Hoc — reuse the pane as-is.

2. In `src/ui/frontend/src/App.css`, immediately after the `.batch-agent-data-wrapper { … }` block (before `.batch-agent-data-body`), add:
```css
   .batch-agent-data-wrapper--page {
     height: 560px;
     padding: 0;
     margin-top: 20px;
   }
```

   Do **not** change `.batch-agent-data-wrapper` itself (Execution History wide modal still fills `modal-body`). The page class is a sized parent so `flex: 1; min-height: 0` on `.batch-agent-data-textarea` is not a 0-height box; 560px matches the previous dump’s visible area (`maxHeight: 600` minus the Response header). Do **not** truncate `block_data`.

3. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, add:
```ts
   import { BatchAgentDataPanes } from "../components/BatchAgentDataModal"
```

4. Delete `response` and `timesheet` state. Add `const [testBatchId, setTestBatchId] = useState<string | null>(null)`. Delete `responseBodyToText` and `formatResponse`.

5. Replace `handleTest` success/error handling. Keep the POST body unchanged (still `...editorSegmentBody()`, no `debug`). At the start of `handleTest`, after the agent-id guard:
```ts
       setTesting(true)
       setTestBatchId(null)
```

   Replace the `.then(data => { if (data.success) { setResponse… } … })` / `.catch(e => setResponse…)` with:
```ts
         .then(data => {
           if (data.success) {
             const id = typeof data.batch_id === "string" ? data.batch_id.trim() : ""
             if (id) setTestBatchId(id)
             else setToast({ text: "Test succeeded without batch_id", variant: "error" })
           } else {
             setToast({ text: data.error || "Unknown error", variant: "error" })
           }
         })
         .catch(e => setToast({ text: e.message, variant: "error" }))
```

   HTTP 500 (including sibling #1 soft-fail that still returns `batch_id`) stays on the existing `if (!r.ok) throw` path — toast only; do **not** load panes. Do **not** display `response_text`.

6. `handlePreview` must not read or write `testBatchId`.

7. Delete the entire JSX `{response !== null && ( … Response … )}` block and the disabled hydrated-output comment. After the prompt editor tabs (and after the Stage 1 Preview `Modal`), render:
```tsx
         {testBatchId && (
           <BatchAgentDataPanes
             batchId={testBatchId}
             candidateId={selectedId || undefined}
             className="batch-agent-data-wrapper--page"
           />
         )}
```

   `BatchAgentDataPanes` already GETs `/api/agent_data/<batch_id>` and `/api/admin/timesheets?batch_id=…` — do not add a parallel fetch on the page.

⚠️ **Decision:** Panes are **inline on the workbench** (they replace the dump at the bottom). Preview is the modal. Opening Execution History’s `BatchAgentDataModal` after Test would hide inspection in a second popup and contradict “on the workbench.” Reuse is the extracted pane body, not a second copy of tab/order/cost logic.

⚠️ **Decision:** Named export from the existing modal file rather than a new `components/*.tsx`. Placement stays `src/components/` (flat); one extra file is not required.

⚠️ **Decision:** Only HTTP 200 + `success` + non-empty `batch_id` mounts panes (parent AC4: after a **successful** Test). Soft-fail 500 may still have stored blocks — operator inspects those from Execution History, not from this dump replacement.

#### Execution contract

- Execute stages in order. One commit per stage on this epic worktree, then `git push origin HEAD:sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes`.
- Do not add files, routes, config blocks, or editor tabs not listed above.
- Do not fold Test into `do_task`. Do not persist on Preview.
- If `TABS` is still three-slot, or Preview JSON lacks `cache_a`–`cache_d`, or Test JSON lacks `batch_id`, stop and comment on **AST-1403** with the Stage N blocked template — do not improvise.

#### Estimate

Confirm Chuckles estimate: 2 — agree

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1413
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes` @ `a65cf3e34b3f5c26085176267399924a9945d2b1`

#### Traceability

AC3→Stage 1 (Preview `Modal`, eight resolved tabs incl. Live Content, no inline preview block, `cache_a`||`cache` alias); AC4→Stage 2 (`BatchAgentDataPanes` inline after HTTP 200 + `success` + `batch_id`; Response `<pre>` removed; Preview does not touch `testBatchId`).

#### Findings

**acceptable** — Short preview tab labels (“Cache A”) vs Manage Tasks editor strings; matches parent AC3 wording and is documented.

**acceptable** — `BatchAgentDataPanes` named export refactor in existing `BatchAgentDataModal.tsx`; default wide `Modal` wrapper preserved for Execution History / Vector Feedback consumers.

**acceptable** — HTTP 500 / soft-fail with `batch_id` does not mount workbench panes; operator uses Execution History — consistent with AC4 “after a successful Test.”

context_tokens≈62000

[plan-rubric] PROCEED (Commit: a65cf3e3) preview modal plus panes

#### Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes`
**Product commits:** `31889c26` (Stage 1 — Preview Prompt `Modal` with eight resolved tabs), `56bac797` (Stage 2 — `BatchAgentDataPanes` inline after Test; Response dump removed)

#### Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1413
**Publish ref:** `origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes` @ `7290f7c486442935912b5d5a5f8c116ce3811f46`
**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes` (10 files). **AST-1413 product commits** (`31889c26`, `56bac797`) touch only `AdminAnthropicAdHoc.tsx`, `BatchAgentDataModal.tsx`, `App.css`. Cumulative diff vs `origin/dev` also carries sibling **#1/#2** `agent.py` / `api_admin.py` / editor wiring from epic `ftr` merge — not introduced by #1413 commits.

**Status gate:** Spawn prompt `Tests Passed` — trusted.

**Joan:** plan-rubric APPROVED attached; no Excluded statute list — no straggler callouts.

#### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No confidence/scoring in #1413 commits |
| astral.agent.do-task-delegation | scoped | not-applicable | No `src/core/**` in #1413 commits |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade/vector validation |
| astral.batch.batch-id-first | scoped | not-applicable | UI consumes `batch_id`; does not construct it |
| astral.batch.batch-id-format | scoped | not-applicable | No batch_id construction |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/clear helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | Pane reuse; no selection logic change |
| astral.config.config-source-of-truth | scoped | not-applicable | No config changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug/artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike/debug-dir paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | Dispatcher untouched in #1413 |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No `run_next` changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `ast-1413-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Product `src/**` is engineer `code(AST-1413)` only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits UI-only; test tree is Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No core/external in #1413 commits |
| astral.layers.import-direction | scoped | conforms | UI imports only; named export from existing modal file |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Preview/panes driven by API payloads; no hardcoded job state |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check handlers |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render/consult orchestration |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | Existing `api()` auth paths unchanged |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | Seed paths untouched |
| astral.seed.archie-catalog-wins | scoped | not-applicable | Catalog paths untouched |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No seed hot-path changes |
| astral.seed.define-approved | scoped | not-applicable | No define/seed approval flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row seed logic |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No data-layer changes in #1413 |
| astral.standards.database-header-inventory | scoped | not-applicable | No `src/data/**` changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | No backend debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | `BatchAgentDataPanes` extract reuses pane logic; `previewField` local helper |
| astral.standards.in-scope-only | scoped | conforms | #1413 commits limited to three planned UI files |
| astral.standards.logging-via-utils | scoped | not-applicable | No runtime logging changes |
| astral.standards.names-not-ticket-ids | scoped | conforms | No ticket-id symbol names |
| astral.standards.no-cross-contamination | scoped | conforms | `AdminTaskPrompts`, `AdminPerformanceMonitor`, `Modal.tsx` untouched |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new hardcoded business sets |
| astral.standards.public-then-helpers | scoped | conforms | Named export + file-local `previewField` |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No `src/utils/**` changes |
| astral.state.core-decides-transitions | scoped | not-applicable | No job/roster transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job prior-state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No daisy-chain run logic |
| astral.ui.frontend-file-placement | scoped | conforms | Changes in `pages/` + existing `components/BatchAgentDataModal.tsx` |
| astral.ui.naming-conventions | scoped | conforms | `BatchAgentDataPanes`, `batch-agent-data-wrapper--page` follow conventions |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No worker/deployment changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip `merge-tests(AST-1413): origin/tests e09f7f48` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests` on branch |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish ref; diff vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | Child `sub/AST-1403/AST-1413-...` on epic stack |
| orch.git.merge-on-checkout | universal | conforms | `sync(dev)` + `merge(AST-1412)` present; no rebase violations |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | Publish on `sub/*` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1403` worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch classes |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Modal vs inline / 500 panes decisions documented |
| orch.pipeline.plan-is-bible | universal | conforms | Stages match Done-when |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code diff |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No canon statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `test(AST-1413)` + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee; review recommend-only |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-ban evidence |

**Active set scored:** 65 / 65

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan cites no catalog patterns |

#### Plan adherence

**Stage 1** — matches Done-when:

- Preview opens `Modal` (default width, Cancel footer, no `size="wide"`).
- Eight `PREVIEW_TABS` in plan order; `(empty)` for blank slots; `previewField` uses `cache_a` || `cache` alias.
- Inline “Resolved Prompt Preview” removed; `previewOpen` gated; Preview does not `GET /api/agent_data/...`.
- `byteSize` / `previewTabsWithSize` removed.

**Stage 2** — matches Done-when:

- `BatchAgentDataPanes` named export; default `BatchAgentDataModal` wide wrapper preserved for `AdminPerformanceMonitor` / `AdminVectorFeedback`.
- `.batch-agent-data-wrapper--page` added (560px) without altering base wrapper.
- `response` / `timesheet` / Response `<pre>` removed; `testBatchId` set on HTTP 200 + `success` + non-empty `batch_id`.
- `setTestBatchId(null)` at Test start; HTTP 500 stays on `!r.ok` throw → toast only (no panes).
- `handlePreview` does not read/write `testBatchId`.
- Inline `BatchAgentDataPanes` after editor + preview modal.

**Out of scope respected (#1413 commits):** no `agent.py`, no `api_admin.py`, no new component file, no `Modal.tsx` edits, no Manage Tasks changes.

**Estimate (2):** footprint fits — UI refactor + CSS hook.

Betty `AST-1413:*` Vitest cases cover modal tabs, pane mount, preview isolation, missing `batch_id` toast.

#### Findings


##### fix-now

(none)

##### discuss

(none)

##### advisory

- **Cumulative diff vs `origin/dev`:** branch tip includes sibling **#1/#2** backend and editor changes not yet on `dev` — expected epic stacking via `merge(AST-1412)`; #1413 engineer commits remain scoped to three UI files.
- **HTTP 500 + `batch_id`:** plan-accepted — soft-fail does not mount workbench panes; operator uses Execution History. No Vitest case for 500 path (optional Betty follow-up, not blocking).
- **`previewField` duplication:** mirrors `AdminTaskPrompts` per plan; label drift risk if Manage Tasks preview helper changes later (Joan marked acceptable).

#### What's solid

- Clean split: preview = modal, post-Test = inline `BatchAgentDataPanes` (not a second popup).
- Execution History consumers unchanged (default export + `size="wide"`).
- Preview modal verified not to fetch `agent_data`; successful Test panes fetch once.
- Cache A alias + empty-slot `(empty)` behavior tested.

#### Frame diff

| Planned (#1413 commits) | Landed |
|-------------------------|--------|
| Preview → `Modal` + eight tabs | `31889c26` |
| `BatchAgentDataPanes` export + inline after Test | `56bac797` |
| `.batch-agent-data-wrapper--page` | `56bac797` |
| No `agent.py` / `api_admin.py` / new files | Confirmed on #1413 commits |
| Sibling #2 editors (pre-flight) | Present via `merge(AST-1412)` before #1413 work |

#### Recommended actions (downstream — not executed here)

- Chuckles: append artifact to issue doc, `docs()` commit on sub-branch, post slim upshot `--as radia`, move to **Review Posted**.
- datt: **PROCEED** → User Testing (no `resolve-child` needed).
- `merge-child`: roll up #1413 after siblings per epic `blockedBy` / ftr order.

context_tokens≈45000

[code-rubric] PROCEED (Commit: 7290f7c4) preview modal and panes

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Preview → `Modal` with eight resolved tabs; after Test, inli | `56bac7971` `31889c26c` |
| ✓ | `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | Export pane body as `BatchAgentDataPanes`; default export st | `56bac7971` |
| ✓ | `src/ui/frontend/src/App.css` | Add `.batch-agent-data-wrapper--page` so the existing flex t | `56bac7971` |
| | _tests_ | — | 1 file(s) |
