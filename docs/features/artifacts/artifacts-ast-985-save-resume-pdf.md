# AST-985 — Save resume pdf
**Component:** artifacts  
**Children:** AST-986, AST-987
**Linear archived:** AST-985 2026-08-05; AST-986 2026-08-05; AST-987 2026-08-05

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-07-27 14:51 | AST-986 | docs | `60dce7a39` | docs(AST-986): plan — session parse API no persist no candidate bind |
| 2026-07-27 14:54 | AST-987 | docs | `16fdddac9` | docs(AST-987): plan — Admin Session Resume Paste page + HTML new tab |
| 2026-07-27 15:03 | AST-986 | code | `9c49edbc2` | code(AST-986): Admin POST /api/admin/session_resume/parse |
| 2026-07-27 15:03 | AST-986 | code | `b655a55ca` | code(AST-986): session resume parse core — no persist no candidate bind |
| 2026-07-27 15:03 | AST-986 | docs | `f4c034c52` | docs(AST-986): build review stub |
| 2026-07-27 15:04 | AST-987 | code | `e62c136de` | code(AST-987): session base resume HTML builder — no candidate bind |
| 2026-07-27 15:05 | AST-987 | code | `2c8c8e1b4` | code(AST-987): Admin Session Resume Paste page + nav |
| 2026-07-27 15:05 | AST-987 | code | `bb7a68ae1` | code(AST-987): Admin POST /api/admin/session_resume/html |
| 2026-07-27 15:06 | AST-987 | docs | `b32b8259e` | docs(AST-987): build review stub |
| 2026-07-27 15:10 | AST-986 | merge-tests | `066bbe625` | merge-tests(AST-986): origin/tests 172d84787 |
| 2026-07-27 15:10 | AST-986 | test | `172d84787` | test(AST-986): session resume parse — no persist, no candidate bind |
| 2026-07-27 15:13 | AST-987 | test | `1e242cdc4` | test(AST-987): Session Resume Paste page + session HTML builder/API |
| 2026-07-27 15:13 | AST-987 | test | `65623e4bd` | test(AST-987): Session Resume Paste page + session HTML builder/API |
| 2026-07-27 15:20 | AST-986 | docs | `6d1f8db08` | docs(AST-986): Radia review — findings |
| 2026-07-27 15:21 | AST-986 | resolve | `152499122` | resolve(AST-986): — clean |
| 2026-07-27 15:22 | AST-987 | docs | `18188d0e0` | docs(AST-987): Radia review — findings |
| 2026-07-27 15:24 | AST-987 | resolve | `0c6a6cbad` | resolve(AST-987): — clean |
| 2026-07-27 15:25 | AST-986 | plan | `fa7c5950d` | plan(AST-986): — sequence label for merge-child gate |
| 2026-07-27 15:28 | AST-987 | plan | `036921d5b` | plan(AST-987): — sequence label for merge-child gate |
| 2026-07-27 15:29 | AST-987 | merge-tests | `8e82fc788` | merge-tests(AST-987): origin/tests 1e242cd |
| 2026-07-27 15:30 | AST-985 | prep-uat | `b5abe04f3` | prep-uat(ast-985): rebuild merge ticket log |
| 2026-08-05 14:52 | AST-986 | docs | `0b92d4add` | docs(AST-986): archive Linear issue content |
| 2026-08-05 14:52 | AST-987 | docs | `c56365648` | docs(AST-987): archive Linear issue content |
| 2026-08-05 14:57 | AST-985 | docs | `51699e779` | docs(AST-985): archive Linear issue content |

## Epic — AST-985
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Purpose

Susan needs a fast, job-independent way to turn pasted resume text into Astral's structured resume JSON and see the familiar HTML layout in a new browser tab — without wiring a job, without writing the candidate database yet. This is an Admin convenience tool tightly coupled to the existing resume structure and HTML builder work already shipped in Artifacts, with a simpler paste-first input path. Session retention (same idea as Admin Data Management SQL history) keeps the working paste/parse state across navigation in the browser so UAT and iteration are not lost on every page leave. The HTML tab's job is user Print → PDF (same as today's resume HTML routes) — not a server-generated PDF file.

### Functional scope

* **Admin paste workbench:** A dedicated Admin screen with a text area where Susan pastes a full resume text block and triggers parse. Nav lives under **Admin** (alongside Data Management and other admin tools).
* **Parse to resume JSON (detached from candidate selector):** The pasted text is parsed into the same structure-keyed resume JSON shape Astral already uses for resume artifacts (section catalog + section content), reusing the existing craft/parse pipeline and **default** resume-structure contract. It does **not** bind to the currently selected candidate for accent, contact, profile, or stored structure — contact/header and sections come from the paste/parse result. Future job binding is out of scope for this epic.
* **Render HTML and open new tab:** Parsed JSON is rendered through the existing resume HTML builder into an HTML document (in-memory / response is fine) and opened in a new browser tab for review; Susan prints that tab to PDF herself.
* **Session retention (no DB write):** Paste text and the latest successful parse result are retained in the browser the same way Admin Data Management retains SQL command history — available after leaving and returning to the tool. Nothing is written to candidate or job artifact storage in this epic.
* **Job-independent:** Flow does not require or attach a job id; it must not enter BUILD_ARTIFACTS, job `resume_content`, or Recommended Job Report paths.

#### UI inventory (new vs reused)

| Kind | Screen / component | Role in this epic |
| -- | -- | -- |
| **New** | Session Resume Paste page under **Admin** nav | Paste textarea, Parse action, status/errors, trigger "open rendered HTML" |
| **New** | Session-scoped storage for this tool's paste + last parse (mirror Data Management SQL history pattern) | Retain working state without DB |
| **Reused** | Existing `craft_resume_base` / parse-to-structure pipeline (same JSON contract as Base Resume Content generate) | Produce structure + content JSON from pasted text |
| **Reused** | Base resume HTML builder + authenticated HTML resume response pattern (`/candidate/resume/base` family), adapted for session/in-memory JSON without selected-candidate binding | Turn JSON into the known HTML layout |
| **Reused** | New-tab open pattern already used for Print Resume / materials preview | Display rendered HTML outside the SPA chrome |
| **Reused** | Toast (and ordinary form controls) | Success/error feedback |
| **Not used** | Base Resume Content page / ArtifactEditor section tabs | Those edit persisted candidate `base_resume`; this tool is paste → parse → preview only |
| **Not used** | Candidate selector as input to parse/render | Explicitly detached this epic |
| **Not used** | Job Analysis Report, Materials Preview modal, job resume/cover HTML routes | Job-scoped; out of scope |

### Boundaries

* **No database persistence** of paste text, parsed JSON, or HTML onto the candidate or any job — browser session retention only for this epic.
* **No selected-candidate binding** — does not read or write the selected candidate's profile, accent, or `artifacts.*` for this flow.
* **No job coupling** — does not create, select, or tailor against a job; does not write `job_data.artifacts.resume_content`. Future job binding is deferred.
* **Does not replace Base Resume Content** — persisted structure/content editing and Generate-on-candidate remain on the existing Artifacts page; this tool does not become the new system of record.
* **Does not change Manage Tasks prompts, TASK_CONFIG registry shape, or dispatch chains.**
* **No server-side PDF generation** — HTML in a new tab; user Print → PDF.
* **No cover letter** path in this epic.
* **No new top-level** `artifacts/` **directory** (Code Rules) — plans stay under `docs/features/artifacts/`.
* **Must not break** Base Resume Content, `/candidate/resume/base`, job resume/cover HTML routes, Admin Data Management session history, or other Admin nav items.

### Acceptance criteria

1. From the new **Admin** tool screen, Susan can paste resume text and run Parse; on success she receives structure-keyed resume JSON consistent with the existing base-resume parse contract (not a free-form blob).
2. Parse and HTML render succeed **without** depending on which candidate is selected in the app chrome (detached from the selector).
3. After a successful parse, a control opens a new browser tab showing HTML rendered with the existing resume HTML layout; Susan can Print → PDF from that tab; no job id is required.
4. Closing and reopening the tool screen within the same browser session restores the last pasted text and last successful parse result (Data Management–style retention); a full browser clear of site data wipes them.
5. Completing the flow does not create or update candidate `artifacts.base_resume` / `artifacts.resume_structure`, job artifacts, or any other durable store for this paste.
6. The UI inventory above is reflected in the shipped UX: new Admin paste page + session retention; reused parse pipeline, HTML builder/route family, and new-tab open — not ArtifactEditor, JAR materials preview, or selected-candidate inputs.
7. A failed parse surfaces a clear error on the paste screen and does not open a blank/broken HTML tab as if success occurred.

### Dependencies and blockers

none. Foundations already on `dev`: structure-aligned resume JSON (**AST-477** / **AST-517–519**), base resume HTML builder + `/candidate/resume/base` (**AST-298** family), Base Resume Content / craft path (**AST-519** / **AST-616**), session localStorage pattern on Admin Data Management.

### Open questions

none.

### Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Session parse API (no persist, no candidate bind) | Backend: accept pasted resume text, run the existing parse-to-structure pipeline against the **default** structure contract, return structure-keyed JSON **without** reading/writing the selected candidate or any job artifacts; debug-capable on the parse hop per AST-538 when debug is on. Does not own UI or HTML tab. | Ada | — |
| 2 | Admin Session Resume Paste page + HTML new tab | New Admin nav page + session retention for paste + last parse; call #1; open rendered HTML in a new tab via reused builder/HTML route family fed by session/in-memory JSON (no selected-candidate bind, no DB). Does not own parse agent prompts. | Katherine | after #1 |

**New pattern:** Session-scoped resume draft (Admin paste → parse JSON → HTML preview with browser retention, no durable artifact write, no candidate selector bind) — introduced by #1+#2; later job binding or "save to candidate" can reuse the same JSON contract without redoing parse/render.

**Monolith check:** Functional scope has 5 capabilities; 2 children split backend non-persist/detached parse from Admin UI/session/HTML open (layers + agents differ).

### Original brief

Very simple:

I want a text input screen where I can paste a resume text block.

The block is parsed into a resume json.

The resume json is then rendered into an html file (potentially just in memory)

A new tab opens to display the rendered html.

this should reuse all the work we have done already in artifacts, simplifying the input process slightly. These resumes are not related to any job. This is a candidate tool that is tightly coupled with our resume structure.

call out the new and reused ui screens and ui components. The resume does not need to be saved to the database at this time, but should be retained in the user session like we do for database commands.

#### Comments

##### chuckles — 2026-07-27T21:41:43.886Z
@susan

1. PDF vs HTML — title says PDF; brief is HTML new tab + no DB. Confirm UAT is browser Print → PDF from the HTML tab (same as today's resume HTML), not a server `.pdf` download?
2. Selected candidate binding — use currently selected candidate for accent/contact/structure defaults (results still session-only), or fully detached from the selector?
3. Nav placement — Candidate or Artifacts?

_(Decisions taken forward into the definition: HTML new tab + browser Print → PDF, no server PDF; fully detached from the selector; nav under Admin.)_

### Files changed (plan vs actual)

_No product commit trail on the parent — the one `prep-uat(ast-985)` commit rebuilds the merge ticket log; implementation landed via AST-986 (parse) and AST-987 (HTML + UI)._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-986 — Session parse API (no persist, no candidate bind)
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-985; blocks: AST-987_

#### What this implements

Backend: accept pasted resume text, run the existing parse-to-structure pipeline against the **default** structure contract, return structure-keyed JSON **without** reading/writing the selected candidate or any job artifacts; debug-capable on the parse hop per AST-538 when debug is on. Does not own UI or HTML tab.

#### Acceptance criteria

1. Admin paste + Parse → structure-keyed resume JSON consistent with the base-resume parse contract (not a free-form blob).
2. Parse succeeds **without** depending on which candidate is selected (detached from the selector).
3. Does not create/update candidate `artifacts.base_resume` / `artifacts.resume_structure`, job artifacts, or any other durable store for this paste.
4. A failed parse surfaces a clear error and does not open a blank/broken HTML tab as if success occurred.

#### Boundaries

* Does not own the Admin paste page, nav, session retention, or new-tab HTML open — sibling AST-987.
* Does not bind to the selected candidate or any job.
* Does not change Manage Tasks prompts or TASK_CONFIG registry shape beyond what is required to invoke the existing parse path in a non-persist mode.
* Does not generate server-side PDF.

#### Notes for planning

* Reuse `craft_resume_base` / parse-to-structure pipeline; default resume-structure contract (no selected-candidate structure/accent/profile).
* Debug Style D on touched `debug=` surfaces per AST-538 / Code Rules.
* UI is Katherine's sibling; expose a clear API contract she can call.

#### API contract (for AST-987)

**`POST /api/admin/session_resume/parse`**
- Auth: `@require_admin` (same as other Admin tools).
- Request JSON: `{ "resume_text": "<pasted full resume text>" }` — required; after strip, must be non-empty.
- Success **200**:
  ```json
  {
    "success": true,
    "resume_structure": { "sections": { "...": { "id", "title", "enabled", "order", "job_agent_editable" } } },
    "base_resume": { "<section_id>": "<string content>", "...": "..." },
    "parsed_response": { "...": "full craft_resume_base agent JSON" },
    "batch_id": "<ledger batch id or null>",
    "timesheet": {}
  }
  ```
  - `resume_structure` / `base_resume` come from `split_craft_resume_base_payload(parsed)` — same shape Base Resume Content persists under `artifacts.*`, but **response-only**.
  - `base_resume` keys are enabled section ids from the resolved structure (default catalog when the model omits/invalidates structure).
- Client errors **400**: `{ "success": false, "error": "<clear message>" }`.
- Server / agent failures **500**: `{ "success": false, "error": "<clear message>", "batch_id": "..." }` — never imply success; Katherine must not open an HTML tab on non-success.

**Detached rules (hard):**
- Do **not** read Flask/session candidate selector, `request` candidate id, or `database.get_candidate` for this flow.
- Do **not** call `database.save_candidate`, `_persist_craft_dispatch_success`, or job artifact writers.
- Synthetic `ctx` must **omit** `astral_candidate_id` so `do_task` does not overlay company_search_terms / candidate API key from a real row.

#### Stage 1: Core session parse (no persist)

**Done when:** `run_session_resume_parse` accepts paste text, invokes `craft_resume_base` with default structure + synthetic ctx, returns `(body, status)` matching the success/error shapes above, and a grep of the function shows no `get_candidate` / `save_candidate`.

1. In `src/core/candidate.py`, add public function `run_session_resume_parse(resume_text: str, *, debug: bool = False) -> Tuple[Dict[str, Any], int]` near `run_candidate_artifact_generation` / `parse_candidate_resume`.
2. Validate input: if `resume_text` is not a `str` or `not resume_text.strip()`, return `({"success": False, "error": "resume_text is required"}, 400)` — do not call `do_task`.
3. Build synthetic token ctx (**no** `astral_candidate_id` key):
   ```python
   structure = default_resume_structure()
   paste = resume_text.strip()
   ctx = {
       "candidate_data": {
           "context": {"starting_resume_text": paste},
           "artifacts": {"resume_structure": structure},
       },
   }
   ```
   ⚠️ **Decision:** Satisfy `TASK_CONFIG["craft_resume_base"]["requires_candidate_key"]` with an in-memory `candidate_data` dict only — do **not** flip `requires_candidate_key` or change the response_schema. Default structure comes from `default_resume_structure()` / `RESUME_STRUCTURE_DEFAULT`, not from any selected candidate's `artifacts.resume_structure`.
4. Ledger + batch (mirror UI generate cost trail without binding a real candidate):
   - `ledger_task_key = "user-session-parse-resume"`; `batch_id = f"{ledger_task_key}-{uuid.uuid4()}"`
   - `database.save_dispatch_ledger(batch_id, ledger_task_key, "session", started_at, entity_type=None, batch_size=1)` then `log_batch_id.set(batch_id)`.
   - ⚠️ **Decision:** Ledger `candidate_id="session"` is a sentinel for Admin cost visibility — **not** an `astral_candidate_id`. Do not resolve or create a candidate row for it.
5. Set debug flag: `logger.set_debug_flag(debug)`. When `debug=True`, Style D: one `debug_index` header for the parse hop (`func="run_session_resume_parse"`, `index=1`, `total=1`, identifier=`batch_id` or `"session"`, outcome success/fail) plus `debug_detail` / `debug_detail_block` — no new ungated `[DEBUG]` info lines (§1.5.1).
6. Call `asyncio.run(do_task(task_key="craft_resume_base", live_content=paste, index=batch_id, ctx=ctx, debug=debug))` inside try/except.
   - ⚠️ **Decision:** Pass `index=batch_id` (session-scoped), **not** a real candidate id. `craft_resume_base` has `entity_type: None`, so `_store_agent_response` skips entity `agent_responses` mutation; agent_data blocks key off the session batch id, never a live candidate.
7. On exception or `not result.get("success")`: update ledger `FAILED` (when batch opened), return 500 body with `success: false` and `error` from exception / `result["error"]` / `"do_task returned None"`.
8. On success: `parsed = result["parsed_response"]`; require `isinstance(parsed, dict)` else 500. Call `structure_out, content = split_craft_resume_base_payload(parsed)`. Update ledger `COMPLETED` + `compute_batch_cost`. Return 200 body with `success`, `resume_structure=structure_out`, `base_resume=content`, `parsed_response=parsed`, `batch_id`, `timesheet=result.get("timesheet", {})`.
9. **Forbidden in this function:** `database.get_candidate`, `database.save_candidate`, `_persist_craft_dispatch_success`, `_stash_pending_craft_generation`, job/tracker artifact writers. Do not reuse `run_candidate_artifact_generation` or `parse_candidate_resume` (both persist `craft_resume_base` today).
10. `finally`: `flush_log_buffer()`; `log_batch_id.set(None)`.

#### Stage 2: Admin API route

**Done when:** `POST /api/admin/session_resume/parse` is registered on `admin_bp`, requires admin auth, validates JSON, delegates to `run_session_resume_parse`, and returns its `(body, status)` unchanged; `py_compile` clean.

1. In `src/ui/api/api_admin.py`, import `run_session_resume_parse` from `src.core.candidate` (keep ui → core only).
2. Add route:
   ```python
   @admin_bp.route("/session_resume/parse", methods=["POST"])
   @require_admin
   def session_resume_parse():
       body = request.get_json(silent=True) or {}
       resume_text = body.get("resume_text")
       result_body, status = run_session_resume_parse(
           resume_text if isinstance(resume_text, str) else "",
           debug=ui_llm_debug(),
       )
       return jsonify(result_body), status
   ```
   - Pass `""` when `resume_text` is missing/non-string so core owns the single validation home.
3. Do **not** register a new blueprint or touch `server.py`. Do **not** add NAV_CONFIG entries or frontend files (AST-987).

**Self-Assessment:** Single-Component — one core orchestrator beside existing craft helpers plus one Admin POST route; no schema/registry/UI surface. Conf high — reuses `do_task("craft_resume_base")`, `default_resume_structure()`, `split_craft_resume_base_payload`; only new behavior is synthetic ctx + skipping persist. Risk Medium — a mistaken `astral_candidate_id` or reuse of `run_candidate_artifact_generation` would write `artifacts.base_resume` / `resume_structure` on a real candidate; the plan forbids those paths and uses a session ledger sentinel.

##### Comments

###### joan — 2026-07-27T21:57:52.606Z (plan-rubric.v1)
**Overall: APPROVED.** Traceability: parent AC 1/2/5/7 map to Stages 1–2 (`run_session_resume_parse` + `POST /api/admin/session_resume/parse`); AC 3/4/6 are sibling AST-987. All 48 in-scope statutes **conforms**.

**discuss** — Stage 1 ledger key `user-session-parse-resume` is a custom string beside `_ledger_task_key_for_ui_generate` (`user-{task_key}`). Distinct key is fine for session cost visibility; at build time keep it intentional (do not silently collide with recover-by-ledger for real candidates).

**discuss** — With `requires_candidate_key` + `index=batch_id`, `_effective_entity_type` resolves to `candidate` for agent_data storage while raw TASK_CONFIG `entity_type: None` still skips `_store_agent_response`. Plan already notes this; confirm `craft_resume_base` does not trip caller-token hydration against the session batch id (expected: no).

**acceptable** — Self-assessment Conf high / Risk Medium matches synthetic-ctx + persist-avoidance complexity. No fix-now findings; R1–R6 pass.

###### betty — 2026-07-27T22:10:38.492Z (QA test manifest)
Publish: `origin/sub/AST-985/AST-986-…` @ `066bbe6` (`merge-tests(AST-986): origin/tests 172d84787`).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst986SessionResumeParse \
  tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi \
  -q
```

1. **Core** — `TestAst986SessionResumeParse`: 400 empty/non-str; ledger `user-session-parse-resume` + sentinel `session`; fail/exception/non-dict → 500; success splits payload; **no** `get_candidate`/`save_candidate`; ctx omits `astral_candidate_id`; debug Style D on/off.
2. **Admin API** — `TestAst986SessionResumeParseApi`: `@require_admin` 403; empty/non-str/`get_json` miss → core 400; success forwards `ui_llm_debug`; 500 passthrough.

Broken / obsolete: none. Bible (publish tip): `docs/test-bible/core/candidate.md` `7085d81843db74c45f0e263fa00e187f011105e8`.

###### radia — 2026-07-27T22:20:23.065Z (code-rubric.v1)
**Overall: DISCUSS** (procedural straggler only). Stages 1–2 match plan: synthetic default-structure ctx (no `astral_candidate_id`), response-only `split_craft_resume_base_payload`, ledger sentinel `session`, `@require_admin` Admin POST. AST-987 UI/HTML boundary held. All in-scope statutes **conforms**.

**discuss** — straggler — Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time; the three-dot review tip brings `docs/features/**` + `tests/**`/`docs/test-bible/**` back in scope. Sweep scores all three **conforms** (single plan file; Betty owns tests). No product fix required.

**What's solid:** no `get_candidate`/`save_candidate` in `run_session_resume_parse`; `craft_resume_base` `entity_type: None`; debug Style D gated, `debug_detail_block` truncates; Betty manifest + `merge-tests(AST-986)` on tip.

#### Resolution (Ada / resolve-child) — 2026-07-27

Review tip `6d1f8db` (Radia `docs(AST-986): Radia review — findings`). fix-now: none. Discuss: C4 straggler acknowledged — Radia scored **conforms**, no product action; left as-is (no plan-wording churn without Archie ask). Product delta this resolve: none — clean resolve.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/candidate.py` | Add `run_session_resume_parse(resume_text, *, debug=False)` — synthetic default-structure ctx, `do_task("craft_resume_base")`, split payload, **never** `save_candidate` / `get_candidate` | `b655a55ca` |
| ✓ | `src/ui/api/api_admin.py` | Add `POST /api/admin/session_resume/parse` (`@require_admin`) — validate body, call core, return JSON contract | `9c49edbc2` |
| | _tests_ | core parse (no persist/bind) + Admin API contract | `172d84787` — `test_candidate.py` / `test_api_admin.py` + test-bible (Betty) |

### AST-987 — Admin Session Resume Paste page + HTML new tab
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-985; blockedBy: AST-986_

#### What this implements

New Admin nav page + session retention for paste + last parse; call the session parse API sibling; open rendered HTML in a new tab via reused builder/HTML route family fed by session/in-memory JSON (no selected-candidate bind, no DB). Does not own parse agent prompts.

#### Acceptance criteria

Same seven ACs as the parent (Susan pastes + Parse → structure-keyed JSON; detached from selector; a control opens HTML new tab for Print → PDF, no job id; session retention of paste + last successful parse, cleared by site-data wipe; no durable candidate/job artifact writes; UI inventory reflected; failed parse shows a clear error and never opens a blank/broken HTML tab). The parse backend is owned by AST-986 (blockedBy) and consumed at Stage 3.

#### Boundaries

* Does not own the non-persist parse backend — sibling AST-986.
* Does not bind to the selected candidate or any job.
* Does not change Manage Tasks prompts or TASK_CONFIG registry shape.
* Does not generate server-side PDF — HTML new tab; user Print → PDF.

#### Notes for planning

* Nav under **Admin**. Session retention mirrors Admin Data Management SQL history (`localStorage`).
* Reuse Toast and new-tab open pattern from Print Resume / materials preview.
* Depends on AST-986 API contract.

#### Approach notes (Katherine)

HTML via `POST /api/admin/session_resume/html` → blob URL new tab (session JSON too large for GET `/candidate/resume/*`); contact/header from paste section strings, not selected-candidate profile.

#### Stage 1: Session HTML builder (core, no candidate bind)

**Done when:** `build_session_base_resume` returns print-oriented HTML from in-memory structure + content dicts; a grep of the function shows no `get_candidate`, `database.`, or `candidate_id`; empty/invalid inputs raise `ValueError` with clear messages.

1. In `src/core/builder.py`, add public function `build_session_base_resume(resume_structure: dict, base_resume: dict, *, debug: bool = False) -> str` immediately after `build_base_resume`.
2. Validate inputs before any emit: non-`dict` structure or missing `sections` dict → `ValueError("resume_structure with sections is required")`; non-nonempty-`dict` `base_resume` → `ValueError("base_resume content is required")`.
3. Build a **synthetic** in-memory candidate blob only (never load a row):
   ```python
   cd = {"artifacts": {"resume_structure": resume_structure, "base_resume": base_resume}, "profile": {}}
   ```
   ⚠️ **Decision:** Detach from selected candidate by constructing `cd` entirely from the request payload. Do **not** call `candidate_mod.get_candidate` or read Flask/session candidate id.
4. Mirror `build_base_resume` emit steps on `cd`: `resolve_resume_structure` → `filter_content_to_resume_structure` → **do not** call `_apply_profile_to_render_dict` (contact/header must come from paste/parse section strings `candidate_name` / `candidate_title` / `candidate_contact_detail`, not a profile row) → `_merge_effective_style(cd)` (accent from session `resume_structure` / default `BUILD_CONFIG` only) → `_apply_resume_text_markers` → `_structure_ordered_body_ids` → `resume_section_titles` → `_emit_html_document(..., include_cover=False)`.
5. Style D header (`func="builder.build_session_base_resume"`, `index=1`, `total=1`, identifier=`"session"`, outcome success) plus detail lines for enabled sections / html_chars — gated on `debug=True` (§1.5.1).
6. Return `html_out`. Do not write any candidate/job artifact.

#### Stage 2: Admin session HTML route

**Done when:** `POST /api/admin/session_resume/html` is registered on `admin_bp`, requires admin auth, returns `text/html` on valid body and JSON `{success:false,error}` on bad input / `ValueError`; `py_compile` clean.

Route body validates `resume_structure` / `base_resume` are objects (else 400), calls `build_session_base_resume(..., debug=ui_llm_debug())`, maps `ValueError` → 400, returns `Response(html, mimetype="text/html; charset=utf-8")`. No new blueprint; `/candidate/resume/base` and job resume/cover routes untouched.

⚠️ **Decision:** HTML lives under `/api/admin/session_resume/html` next to the parse sibling (admin-gated), not as a GET on `/candidate/resume/*`. Session JSON is too large for a Print-Resume-style GET URL; the page POSTs via `api()` (Bearer) then opens a blob URL — same builder family, adapted for in-memory JSON without server-side session cache.

#### Stage 3: Admin nav + Session Resume Paste page

**Done when:** Admin nav shows **Session Resume Paste**; `/admin/session_resume_paste` renders inside `AdminRoute`; paste + last successful parse restore after leave/return via `localStorage`; Parse calls AST-986; Open HTML only after a successful parse and only when the HTML POST succeeds; failed parse shows a clear error and never opens a tab; page does not read `useCandidate().selectedId` for parse/HTML.

1. `NAV_CONFIG` Admin `items`: add `{"label": "Session Resume Paste", "path": "/admin/session_resume_paste"}` after **Data Management**.
2. `routes.tsx`: import `SessionResumePaste` from `./pages/AdminSessionResumePaste`; child route `{ path: "admin/session_resume_paste", element: <AdminRoute><SessionResumePaste /></AdminRoute> }` next to `admin/data_management`.
3. `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — default-export `SessionResumePaste`.
4. **localStorage retention** (reuse `useLocalStorage`): key `session_resume:paste_text` (`string`, default `""`, bound to the textarea); key `session_resume:last_parse` (`{resume_structure, base_resume} | null`, default `null`, set **only** on successful parse, **not** cleared on failed parse). Clearing site data wipes both.
5. **UI layout** (reuse `AdminDataManagement.tsx` classes / tokens — `dep-btn`, `dep-input`, CSS vars): title `Session Resume Paste`; helper line stating the tool does not use the selected candidate and does not save to the database; `<textarea className="dep-input">` (monospace, ~16 rows, `spellCheck={false}`); **Parse** (disabled when paste empty or parsing) and **Open HTML** (disabled when `lastParse` null or opening/parsing); inline error `<p>`; `<Toast>`.
6. **Parse handler** (`POST /api/admin/session_resume/parse`): on `!r.ok` or `data.success !== true`, set error from `data.error` / `HTTP <status>`, Toast `error`, return **without** updating `lastParse` or opening a tab; on success require object `resume_structure` + `base_resume`, `setLastParse(...)`, Toast success, clear inline error.
   ⚠️ **Decision:** Do **not** auto-open the HTML tab on parse success — AC requires a **control** that opens the tab; the Open HTML button is that control (avoids popup-blocker failures masking parse success).
7. **Open HTML handler** (`POST /api/admin/session_resume/html`): guard `if (!lastParse) return`; POST `lastParse`; on `!r.ok` Toast error and **do not** open a tab; on ok `await r.text()`, empty → Toast error; else `URL.createObjectURL(new Blob([html], {type:"text/html;charset=utf-8"}))` → `window.open(blobUrl, "_blank", "noopener,noreferrer")` (null → "Popup blocked" Toast), `setTimeout(revokeObjectURL, 60_000)`.
   ⚠️ **Decision:** Blob URL after authenticated POST (not `window.open("/candidate/resume/...")`) because session JSON is request-bodied and must not depend on selected-candidate query params or server-side draft storage.
8. **Hard UI bans:** no `useCandidate` for parse/HTML inputs; no navigation to Base Resume Content / ArtifactEditor / Materials Preview / job print routes; no POST to candidate generate/persist artifact endpoints.

**Self-Assessment:** Single-Component — one builder helper, one admin HTML POST, nav/route wiring, one Admin page; no schema/registry/persist path changes. Conf high — reuses `build_base_resume` emit helpers, `@require_admin` + `api()`, `useLocalStorage`, and the AST-986 parse contract. Risk Medium — wrong wiring could call candidate-bound `/candidate/resume/base` or persist craft generate; plan forbids those paths and keeps contact fields on paste JSON only; build blocked until AST-986's parse route is on the epic `ftr` line.

##### Comments

###### joan — 2026-07-27T22:00:12.729Z (plan-rubric.v1)
**Overall: APPROVED.** Stages 1–3 map to all seven parent ACs (parse backend owned by AST-986, blockedBy, consumed at Stage 3). All in-scope statutes **conforms**.

**discuss** — Retention uses `useLocalStorage` (Ad Hoc pattern) rather than Data Management's raw `HISTORY_KEY` helper. Parent asks for Data Management–*style* browser retention; this still satisfies AC4. Keep keys namespaced (`session_resume:*`) as planned.

**acceptable** — Conf high / Risk Medium matches candidate-bound print-route footgun + AST-986 ftr dependency. Skipping `_apply_profile_to_render_dict` is the right detach move vs `build_base_resume`. No fix-now findings; R1–R6 pass.

###### betty — 2026-07-27T22:14:18.107Z (QA test manifest)
Publish: `origin/sub/AST-985/AST-987-…` @ `cbe3cbf` (`merge-tests(AST-987): origin/tests 1e242cdc4`).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume \
  tests/component/ui/api/test_api_admin.py::TestAst987SessionResumeHtmlApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx
```

1. **Builder** — `TestAst987BuildSessionBaseResume`: invalid structure/empty content → `ValueError`; success HTML from in-memory payload; **no** `get_candidate`; debug on/off.
2. **Admin HTML API** — `TestAst987SessionResumeHtmlApi`: `@require_admin` 403; bad body / builder `ValueError` → 400; success `text/html` + `ui_llm_debug`.
3. **Page (§6c)** — `test_AdminSessionResumePaste.test.tsx`: render + Parse success enables Open HTML (no auto-tab); parse fail error / no tab; Open HTML blob URL; HTML error / no tab; localStorage restore.

Broken / obsolete: none. Bible (publish tip): `docs/test-bible/frontend/pages.md` `6b2de34d1263352795ec6c284512a7964e1b441f`.

###### radia — 2026-07-27T22:22:48.566Z (code-rubric.v1)
**Overall: DISCUSS** (procedural straggler only). Stages 1–3 match plan: `build_session_base_resume` (synthetic `cd`, no `get_candidate` / no profile overlay), `POST /api/admin/session_resume/html` (`@require_admin`), Admin page + `NAV_CONFIG` + `AdminRoute`, `useLocalStorage` keys `session_resume:*`, Open HTML only after successful parse + successful HTML POST via blob URL. AST-986 parse consumed only; no TASK_CONFIG / persist / candidate print-route reuse. All in-scope statutes **conforms**.

**discuss** — straggler — same Joan plan-time exclusions vs three-dot tip; all score **conforms**. No product action.

#### Resolution — 2026-07-27

Radia tip `e95ffa8` (`docs(AST-987): Radia review — findings`). fix-now: none. discuss (stragglers): acknowledged — Joan's plan-rubric exclusions scored **conforms** on the three-dot tip; no product or plan-stage change. advisory: none. Product delta this resolve: none (clean).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | Add `build_session_base_resume(resume_structure, base_resume, *, debug=False) -> str` — same HTML emit path as `build_base_resume`, zero `get_candidate` / DB | `e62c136de` |
| ✓ | `src/ui/api/api_admin.py` | Add `POST /api/admin/session_resume/html` (`@require_admin`) — validate JSON body, return `text/html` or JSON error | `bb7a68ae1` |
| ✓ | `src/utils/config.py` | Add Admin `NAV_CONFIG` item for Session Resume Paste | `2c8c8e1b4` |
| ✓ | `src/ui/frontend/src/routes.tsx` | Register `/admin/session_resume_paste` under `AdminRoute` | `2c8c8e1b4` |
| ✓ | `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | New page: paste textarea, Parse, Open HTML, Toast, `useLocalStorage` retention | `2c8c8e1b4` |
| | _tests_ | builder + Admin HTML API + page (§6c) | `1e242cdc4` — `test_builder.py` / `test_api_admin.py` / `test_AdminSessionResumePaste.test.tsx` + test-bible (Betty) |
