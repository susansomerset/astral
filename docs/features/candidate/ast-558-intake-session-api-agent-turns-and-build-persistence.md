<!-- linear-archive: AST-558 archived 2026-06-23 -->

## Linear archive (AST-558)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-558/intake-session-api-agent-turns-and-build-persistence-candidate-intake  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-539 — Candidate Intake Chat Session  
**Blocked by / blocks / related:** parent: AST-539; blocks: AST-559

### Description

## What this implements

Backend for Estelle-led candidate intake: session store with resume-after-close, three user-message modes (`initiate_candidate`, `candidate_response`, `build_request`), config-driven Estelle calls with cache reuse, interview-turn JSON validation (`ready_to_build`, `assistant_message`), one `build_request` per session with persistence of all seven output areas via existing candidate save/normalization (including company search terms table sync), source material fields on candidate context, execution history recording per model call.

## Acceptance criteria

 2. Each user reply advances the thread via `assistant_message`; Estelle responses include `ready_to_build`; **Generate Profile** is disabled until the latest response has `ready_to_build: true`.
 3. While `ready_to_build: true`, the user can still send `candidate_response` turns and Estelle may ask further clarifications before generate is pressed.
 4. **Generate Profile** sends `build_request` and persists all seven output areas as flat text strings verifiable on existing candidate UI/API.
 5. Company search terms from build appear in the Company Search Terms experience and are consumed by roster inflow the same as manually entered terms.
 6. Title patterns from build are stored on the candidate profile and participate in gazer title filtering the same as manually entered patterns.
 7. After a successful build in a session, **Generate Profile** cannot be fired again in that same modal session; opening a new session allows a new build.
 8. Pasted resume, cover, and LinkedIn source texts remain on the candidate record after the session.
 9. If the candidate already satisfies `check_context_complete` after build, the existing **CONTEXT_READY** transition occurs through current core logic (no duplicate state-machine invention).
10. Estelle agent settings (model, prompts) are loaded from admin config; changing Estelle in Manage Tasks changes intake behavior without code deploy.
11. Closing and reopening the same intake session resumes the conversation (not a blank session).
12. Each intake model call appears in **Execution History** with prompt/logging parity to other agent exchanges; observable from Admin without new Intake-modal cost UI.
13. Post-build, `parse_candidate_resume` **/** `craft_resume_base` **are not auto-invoked** — user performs those steps separately when ready.

## Boundaries

Does not implement Intake modal UI or nav (sibling Katherine ticket). Does not draft prompt text files on parent (Chuckles attachment). Does not auto-invoke post-build resume craft.

## Notes for planning

Expose stable API contract for UI: session CRUD, turn endpoint, build endpoint. Follow AST-202 Estelle/Manage Tasks patterns. Company search terms via AST-490 table sync. Session persistence = transcript + cache reload pattern like ad hoc multi-turn.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent **ftr/ast-539-candidate-intake-chat-session**, child **sub/AST-539/<child-id>-intake-session-api** (slug at dispatch).

### Comments

#### radia — 2026-06-03T00:26:34.407Z
**Review** (`origin/dev...origin/sub/AST-539/AST-558-intake-session-api` @ `470c01e5`, product tip before doc: `470c01e5`)

**What's solid**
- REST contract + DTO flags match plan Stage 3 and parent **AST-539** AC 2–4, 7, 11 (`src/core/intake.py`, `src/ui/api/api_intake.py`).
- §3.3: UI → core only; core uses `do_task`, `save_candidate_data`, `sync_company_search_terms_from_text`, `check_context_complete` — no new state machine.
- §2.4: `intake-{task_key}` ledger per turn; `prompt_snapshot` + `agent.py` `intake_*` snapshot hook for resume-after-close.
- Build: seven-path whitelist, one build per session (tested), no auto `parse_candidate_resume` / `craft_resume_base`.
- Component tests: `tests/component/core/test_intake.py`, `tests/component/ui/api/test_api_intake.py` (bible §7.13zr).

**discuss**
- `post_intake_build` does not check `last_ready_to_build` — only ACTIVE + not BUILT. UI (**AST-559**) gates Generate Profile; confirm if API should **400** when not ready.
- `POST /sessions` leaves prior ACTIVE rows; `GET /active` returns newest — Katherine should hold `session_id` or use `/active`.

**advisory**
- `INTAKE_CONFIG["estelle_agent_id"]` unused — Estelle via Manage Tasks `agent_task` rows; seed three `intake_*` keys before live UAT.

**fix-now:** none — Ada may **resolve-astral** on happy path.

**Doc:** `docs/features/candidate/ast-558-intake-session-api-agent-turns-and-build-persistence.md` § Radia review (2026-06-03); published `590d4736` on publish ref (`dev-radia` source `582dfe08`).

#### betty — 2026-06-03T00:22:51.435Z
[check-linear]

**[qa-handoff] cleared** — manifest items 1–2 now exit 0 on narrowed harness.

- **Harness:** `run_component_tests.sh` runs Vitest only with zero args; trailing pytest paths (manifest 1–2) are pytest-only.
- **Tests:** `test_AdminManageCandidates.test.tsx` — **AST-511** (canceled) middle-name cases **`it.skip`**.
- **Bible:** §7.13zr + Appendix A note; shasum on publish ref: `2872f983227332a8af63877968c2605d8859dfba7757de82963d0f2845942621`
- **Publish:** `origin/sub/AST-539/AST-558-intake-session-api` @ `470c01e5`

**Manifest (unchanged commands, now green):**

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_intake.py`
2. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_intake.py`

Reassigned **Ada** for **`test-astral`** — stay **Tests Ready**.

#### ada — 2026-06-03T00:13:38.756Z
[qa-handoff]

@Betty White — Re-verified on `dev-ada` after merges (`origin/dev`, `origin/ftr/ast-539-candidate-intake-chat-session`, `origin/sub/AST-539/AST-558-intake-session-api` @ `e043f447`). Blocker unchanged from prior handoff.

**Manifest items 1–2:** pytest green on both paths; `run_component_tests.sh` still exits **1** after full Vitest tail (`test_AdminManageCandidates.test.tsx` — **Middle Name** / `profile.middle`; **AST-510** / **AST-511** canceled, no `middle` in product).

**Direct pytest (repro):**
```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py tests/component/ui/api/test_api_intake.py -q
```
→ **17 passed**.

Please update manifest or test tree so items 1–2 exit 0 (e.g. skip/remove AST-511 middle-name Vitest cases, pytest-only gate per §7.13zr, or harness change). Reassign **Ada** when green.

#### ada — 2026-06-03T00:11:33.393Z
[qa-handoff]

@Betty White — manifest **pytest** is green; **`run_component_tests.sh`** exits **1** on the harness Vitest tail only.

**Commands (Betty manifest):**
1. `./scripts/testing/run_component_tests.sh tests/component/core/test_intake.py` → pytest **9 passed**; then full Vitest runs.
2. Same pattern for `tests/component/ui/api/test_api_intake.py`.

**Direct pytest (publish tip on `dev-ada` after merges):**
```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py tests/component/ui/api/test_api_intake.py -q
```
→ **17 passed** in 0.26s.

**Vitest failures (not in AST-558 manifest):**
- `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` — expects **Middle Name** label and `profile.middle` in POST body.
- **AST-511** is **Canceled**; `AdminManageCandidates.tsx` has no middle field on `origin/sub/AST-539/AST-558-intake-session-api`, `origin/ftr/ast-539-candidate-intake-chat-session`, or local tree after merges.

**Why this is test/harness, not AST-558 product:** Bible §7.13zr manifest is intake backend only (no UI). Bible §565 documents that narrowed `run_component_tests.sh` still runs **full** Vitest; tail is red due to **canceled AST-511** specs, not `test_intake.py` / `test_api_intake.py`.

**Ask:** Update manifest or test tree so engineer gate for **AST-558** is reproducible green (e.g. drop/skip AST-511 middle-name Vitest cases, or document pytest-only gate for this child). Reassign **Ada** when `run_component_tests.sh` items 1–2 exit 0.

**Refs:** `origin/sub/AST-539/AST-558-intake-session-api` @ `e043f447` (matches Betty SHA).

#### betty — 2026-06-02T22:58:06.096Z
**QA test manifest** (`origin/sub/AST-539/AST-558-intake-session-api` @ `e043f447`)

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_intake.py`
2. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_intake.py`

**Coverage:** new component tests for session lifecycle, turn validation, build persistence (company search terms sync + `check_context_complete`), ledger `intake-{task_key}` prefix, and REST contract/auth/error paths. No UI tests — **AST-559** owns the modal.

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` §7.13zr; shasum on publish ref: `33cb9eeb884cb566f6950441ff8ef278ce7c5a94`

**UAT note (from build):** Seed `intake_initiate_candidate`, `intake_candidate_response`, and `intake_build_request` in Manage Tasks (`agent_id` = `X00_estelle_recruiter`) before live Estelle intake calls.

#### ada — 2026-06-02T22:31:51.387Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-539/AST-558-intake-session-api/docs/features/candidate/ast-558-intake-session-api-agent-turns-and-build-persistence.md

**Scope:** MAJOR-CHANGE — New `candidate_intake_session` table, `src/core/intake.py`, `api_intake.py`, three `TASK_CONFIG` intake tasks, and a small `agent.py` snapshot hook for multi-turn cache resume.

**Conf:** Medium — Reuses `do_task`, dispatch ledger, and AST-524 search-term sync; new pieces are session store + cache snapshot wiring.

**Risk:** Medium — Build persistence touches candidate context/profile and `check_context_complete`; mitigated by whitelisted build keys and no new state-machine logic.

Published to `origin/sub/AST-539/AST-558-intake-session-api` @ `acdc8074`.

---

# AST-558 — Intake session API, agent turns, and build persistence

**Linear:** https://linear.app/astralcareermatch/issue/AST-558/intake-session-api-agent-turns-and-build-persistence-candidate-intake  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session  
**Feature ref:** `sub/AST-539/AST-558-intake-session-api` (origin only)  
**Sibling (out of scope):** [AST-559](https://linear.app/astralcareermatch/issue/AST-559/intake-chat-modal-and-candidate-navigation-candidate-intake-chat-session) — Katherine owns Intake modal UI and nav.

## Summary

Backend for Estelle-led candidate intake: a **`candidate_intake_session`** store (resume-after-close), REST API for session CRUD and turns, three config-driven **`do_task`** keys bound to agent **`X00_estelle_recruiter`**, interview-turn JSON validation (`ready_to_build`, `assistant_message`), one **`build_request`** per session with persistence of seven output areas through existing **`save_candidate_data`** / **`sync_company_search_terms_from_text`** / **`check_context_complete`**, and **Execution History** parity via **`dispatch_ledger`** + **`agent_data`** (same pattern as **`run_candidate_artifact_generation`** / **AST-515**). Does **not** implement modal UI, nav, or prompt prose (parent **AST-539** attachments + Manage Tasks).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `INTAKE_CONFIG` (agent id, build field whitelist); three `TASK_CONFIG` entries | utils |
| `src/data/database.py` | Header inventory; `candidate_intake_session` table + CRUD | data |
| `src/core/intake.py` | Session lifecycle, turn/build orchestration, persistence, cache snapshot | core |
| `src/ui/api/api_intake.py` | REST contract for Katherine (**AST-559**) | ui |
| `src/ui/server.py` | `register_blueprint(intake_bp)` | ui |
| `tests/component/core/test_intake.py` | Session, turn validation, build persistence | tests |
| `tests/component/ui/api/test_api_intake.py` | HTTP contract + auth | tests |

**Out of scope:** `src/ui/frontend/**`, `NAV_CONFIG`, prompt text in repo, `parse_candidate_resume` / `craft_resume_base` auto-run.

---

## API contract (stable for AST-559)

All routes under **`/api/candidates/<candidate_id>/intake`**, `@require_auth`, JSON bodies.

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/sessions` | Create session; persist source materials; run **`intake_initiate_candidate`** |
| `GET` | `/sessions/<session_id>` | Resume session (transcript, flags, status) |
| `GET` | `/sessions/active` | Return newest **`ACTIVE`** session for candidate, or **`404`** |
| `POST` | `/sessions/<session_id>/turns` | **`candidate_response`** turn |
| `POST` | `/sessions/<session_id>/build` | **`intake_build_request`** once per session |

### `POST /sessions` body

```json
{
  "starting_resume_text": "required non-empty string",
  "sample_cover_text": "optional string",
  "linkedin_profile_text": "optional string"
}
```

**Response `201`:**

```json
{
  "session_id": "uuid",
  "status": "ACTIVE",
  "transcript": [
    {"role": "assistant", "text": "...", "ready_to_build": false}
  ],
  "ready_to_build": false,
  "can_build": false,
  "build_completed": false,
  "batch_id": "intake-intake_initiate_candidate-..."
}
```

### `POST /sessions/<id>/turns` body

```json
{"message": "user reply text — required non-empty"}
```

**Response `200`:** same shape as create (full transcript + flags + latest **`batch_id`**).

### `POST /sessions/<id>/build` body

`{}` or omitted.

**Response `200`:**

```json
{
  "session_id": "...",
  "status": "BUILT",
  "build_completed": true,
  "can_build": false,
  "ready_to_build": true,
  "batch_id": "...",
  "persisted_fields": ["context.bio_summary", "..."]
}
```

**Errors (consistent JSON `{"error": "..."}`):**

- **`400`** — validation (empty message, session not **`ACTIVE`**, build already done, model JSON invalid)
- **`404`** — candidate or session missing
- **`500`** — agent/DB failure after ledger opened (include **`batch_id`** when available)

**Flags:**

- **`ready_to_build`** — from latest assistant turn (interview tasks only)
- **`can_build`** — `ready_to_build && status === "ACTIVE"` (UI enables Generate Profile)
- **`build_completed`** — `status === "BUILT"`

---

## Stage 1: Config and data layer

**Done when:** `INTAKE_CONFIG` and three `TASK_CONFIG` rows exist; `candidate_intake_session` table CRUD works in isolation; no API yet.

1. In **`src/utils/config.py`**, after **`CANDIDATE_STATES`** (or adjacent candidate blocks), add **`INTAKE_CONFIG`**:

   ```python
   INTAKE_CONFIG = {
       "estelle_agent_id": "X00_estelle_recruiter",
       "session_status_active": "ACTIVE",
       "session_status_built": "BUILT",
       "build_field_paths": [
           "context.bio_summary",
           "context.backstory",
           "context.strengths",
           "context.priorities",
           "context.deal_breakers",
           "profile.title_patterns",
           "company_search_terms",
       ],
   }
   ```

   - **`company_search_terms`** is the build JSON key (not `artifacts.company_search_terms`); maps to **`sync_company_search_terms_from_text`** (AST-524).

2. In **`TASK_CONFIG`**, add three entries (sequential **`phase`** string **`"A. Candidate Intake"`**, **`entity_type`**: **`"candidate"`**, **`requires_candidate_key`**: **`True`**, **`trigger_state`**: **`None`**):

   **`intake_initiate_candidate`**

   ```python
   "response_schema": {
       "ready_to_build": {"type": "bool", "required": True},
       "assistant_message": {"type": "str", "required": True},
   },
   "response_format": "json",
   "context_format": "intake_{index}",
   ```

   **`intake_candidate_response`** — same **`response_schema`** as initiate.

   **`intake_build_request`**

   ```python
   "response_schema": {
       "context.bio_summary": {"type": "str", "required": True},
       "context.backstory": {"type": "str", "required": True},
       "context.strengths": {"type": "str", "required": True},
       "context.priorities": {"type": "str", "required": True},
       "context.deal_breakers": {"type": "str", "required": True},
       "profile.title_patterns": {"type": "str", "required": True},
       "company_search_terms": {"type": "str", "required": True},
   },
   "response_format": "json",
   "context_format": "intake_build_{index}",
   ```

3. In **`src/data/database.py`** header inventory, add:

   ```
   - candidate_intake_session — Per-candidate Estelle intake chat (intake_session_id TEXT PK, candidate_id,
     status ACTIVE|BUILT, transcript JSON, prompt_snapshot JSON, last_ready_to_build INTEGER, built_at TIMESTAMP,
     created_at, updated_at). Resume-after-close (AST-558).
   ```

4. Implement **`_ensure_candidate_intake_session_table(conn)`** with:

   ```sql
   CREATE TABLE candidate_intake_session (
       intake_session_id TEXT PRIMARY KEY,
       candidate_id TEXT NOT NULL,
       status TEXT NOT NULL,
       transcript TEXT NOT NULL,
       prompt_snapshot TEXT,
       last_ready_to_build INTEGER NOT NULL DEFAULT 0,
       built_at TIMESTAMP,
       created_at TIMESTAMP NOT NULL,
       updated_at TIMESTAMP NOT NULL
   );
   CREATE INDEX idx_intake_session_candidate ON candidate_intake_session (candidate_id);
   ```

5. Implement CRUD (follow **`board_search`** / **`company_search_terms`** style — JSON serialize in Python):

   - **`create_intake_session(intake_session_id, candidate_id, transcript, prompt_snapshot=None) -> None`** — insert **`status=ACTIVE`**, empty transcript `[]` if not passed.
   - **`get_intake_session(intake_session_id) -> Optional[dict]`** — parse **`transcript`**, **`prompt_snapshot`** JSON.
   - **`update_intake_session(intake_session_id, *, transcript, prompt_snapshot, last_ready_to_build, status, built_at) -> None`** — touch **`updated_at`**.
   - **`get_active_intake_session(candidate_id) -> Optional[dict]`** — latest **`ACTIVE`** by **`created_at DESC`**, limit 1.

⚠️ **Decision:** Store **transcript** and **prompt_snapshot** as JSON **TEXT** columns (SQLite pattern used elsewhere) rather than normalizing messages — resume reload is acceptable per parent; keeps session layer thin.

---

## Stage 2: Core intake orchestration

**Done when:** `src/core/intake.py` can create a session, run three turn types with ledger + `do_task`, snapshot cache after each turn, apply build once, and call **`check_context_complete`**; no Flask routes yet.

1. Create **`src/core/intake.py`** (header: layer **core → data, agent, candidate, utils**; no **ui** imports).

2. Constants from **`INTAKE_CONFIG`**; import **`do_task`**, **`compute_batch_cost`**, **`get_agent_data_by_batch`** (or existing block fetch used by admin), **`log_batch_id`**, **`save_dispatch_ledger`**, **`update_dispatch_ledger`**.

3. **`_persist_source_materials(candidate_id, starting_resume_text, sample_cover_text, linkedin_profile_text) -> None`**

   - Require **`starting_resume_text.strip()`** non-empty; else **`ValueError("starting_resume_text is required")`**.
   - **`save_candidate_data(candidate_id, {"context": {"starting_resume_text": ..., "sample_cover_text": optional or "", "linkedin_profile_text": optional or ""}}, merge=True)`** — keys match **CANDIDATE_DATA_MODEL** (`context.starting_resume_text`, `context.sample_cover_text`, `context.linkedin_profile_text`).

4. **`_ledger_task_key(task_key: str) -> str`**: return **`f"intake-{task_key}"`** (Execution History Task column).

5. **`async def _run_intake_task(candidate_id: str, task_key: str, live_content: str, *, prompt_snapshot: Optional[dict]) -> dict`**

   - Mirror **`run_candidate_artifact_generation`** ledger pattern: **`batch_id = f"{_ledger_task_key(task_key)}-{uuid.uuid4()}"`**, **`save_dispatch_ledger`**, **`log_batch_id.set`**, **`try/finally`** clear batch id.
   - Build **`ctx`** from **`get_candidate(candidate_id)`** (import **`get_candidate`** from **`candidate`**).
   - If **`prompt_snapshot`** is non-empty dict, pass **`ctx["intake_prompt_snapshot"] = prompt_snapshot`** (new key consumed only in intake assembly — see step 6).
   - **`result = await do_task(task_key=..., live_content=live_content, index=candidate_id, ctx=ctx)`**.
   - Close ledger **COMPLETED** / **FAILED** with **`compute_batch_cost`**.
   - Return **`{"success", "parsed_response", "error", "batch_id"}`**.

6. In **`src/core/agent.py`**, minimal hook for cache resume (single guarded branch — do **not** refactor **`do_task`**):

   - After **`_resolve_task_prompts`**, if **`ctx.get("intake_prompt_snapshot")`** and **`task_key.startswith("intake_")`**: when assembling cache slots, use snapshot strings for **`system_content`** / **`rca`–`rcd`** / **`nocache_content`** instead of re-resolving those segments from empty task prompts on follow-up turns. **Still** resolve **`user_content`** and **`live_content`** from tokens + caller **`live_content`** each turn.

   ⚠️ **Decision:** Snapshot override lives in **`agent.py`** behind **`intake_`** prefix + **`intake_prompt_snapshot`** ctx flag — avoids duplicating Anthropic send path in **`intake.py`**.

7. **`def _snapshot_from_batch(batch_id: str) -> dict`**

   - **`get_agent_data_by_batch(batch_id)`**; build dict **`{"system": ..., "cache_a": ..., "cache_b": ..., "cache_c": ..., "cache_d": ..., "nocache": ...}`** from stored block **content** fields (empty string if block missing). Used after first successful turn.

8. **`def _validate_interview_turn(parsed: dict) -> dict`**

   - Require dict; **`ready_to_build`** bool; **`assistant_message`** non-empty stripped str.
   - Return **`{"ready_to_build": bool, "assistant_message": str}`**.

9. **`def _append_transcript(transcript: list, *, role, text, ready_to_build=None, mode=None) -> list`**

   - User entries: **`{"role":"user","text":...,"mode":"candidate_response"|"initiate_candidate"}`**.
   - Assistant: **`{"role":"assistant","text":...,"ready_to_build": bool}`**.

10. **`def _live_content_for_turn(mode: str, message: str, transcript: list) -> str`**

    - **`initiate_candidate`**: **`live_content`** = message arg (API layer passes formatted payload — see Stage 3).
    - **`candidate_response`**: JSON string **`{"mode":"candidate_response","user_message": message}`** (Manage Tasks templates instruct Estelle to read mode).
    - **`build_request`**: literal **`{"mode":"build_request"}`** or fixed string **`build_request`** per Chuckles parent templates — use **`json.dumps({"mode": "build_request"})`** in code.

11. **`async def create_intake_session_and_start(...) -> dict`**

    - Generate **`intake_session_id = str(uuid.uuid4())`**.
    - **`_persist_source_materials`**.
    - **`create_intake_session`** with empty transcript.
    - Run **`_run_intake_task(..., task_key="intake_initiate_candidate", live_content=formatted initiate payload)`** where initiate payload includes source texts (plain text sections, not token substitution in API — core formats):

      ```
      RESUME:
      {starting_resume_text}

      COVER LETTER SAMPLE:
      {sample_cover_text or "(none)"}

      LINKEDIN:
      {linkedin_profile_text or "(none)"}
      ```

    - On failure: raise or return error with **`batch_id`**.
    - Validate interview turn; update session transcript + **`last_ready_to_build`** + **`prompt_snapshot`** from **`_snapshot_from_batch`**.
    - Return session DTO for API.

12. **`async def post_intake_turn(intake_session_id, message: str) -> dict`**

    - Load session; require **`ACTIVE`**; reject if **`message.strip()`** empty.
    - Append user line to transcript (copy list before mutate).
    - **`_run_intake_task`** with **`intake_candidate_response`**, snapshot from session, live content from step 10.
    - Append assistant line; update DB.

13. **`def _apply_build_payload(candidate_id: str, parsed: dict) -> list[str]`**

    - Whitelist keys = **`INTAKE_CONFIG["build_field_paths"]`** only; reject unknown keys **`ValueError`**.
    - Each value non-empty stripped str.
    - Build nested dict for **`save_candidate_data`**: dot-path split — e.g. **`context.bio_summary`** → **`{"context": {"bio_summary": v}}`** deep-merge.
    - For **`company_search_terms`**: call **`sync_company_search_terms_from_text(candidate_id, text)`** — do **not** leave key in artifacts blob.
    - **`save_candidate_data`** merge.
    - Call **`check_context_complete(candidate_id)`** (existing — no new transition logic).
    - Return list of persisted path strings.

14. **`async def post_intake_build(intake_session_id: str) -> dict`**

    - Session **`ACTIVE`** only; if **`built_at`** set or **`status == BUILT`**, **`ValueError("build already completed for this session")`**.
    - **`_run_intake_task`** **`intake_build_request`** with snapshot + build live content.
    - **`_apply_build_payload`**; set session **`status=BUILT`**, **`built_at=now`**, **`build_completed`** semantics.
    - **Do not** call **`parse_candidate_resume`** or **`craft_resume_base`**.

15. **`def get_intake_session_dto(row: dict) -> dict`** — map DB row to API flags (**§ API contract**).

⚠️ **Decision:** **`agent_task`** rows for the three **`intake_*`** keys are **not** seeded in code — Susan/Chuckles load prompts via **Manage Tasks** (`agent_id` = **`X00_estelle_recruiter`**). **build-astral** Stage 0 comment on **AST-558**: confirm three tasks exist before UAT; missing row → clear **`do_task`** error.

---

## Stage 3: UI API and server registration

**Done when:** All five endpoints work behind auth; Katherine can integrate against OpenAPI-shaped responses above.

1. Create **`src/ui/api/api_intake.py`** — **`intake_bp = Blueprint("intake", __name__, url_prefix="/api/candidates")`** with routes nested under **`/<candidate_id>/intake/...`**.

2. Each handler: verify candidate exists (**`get_candidate`**); map **`ValueError`** → **400**, missing → **404**; agent failures → **500** with **`batch_id`** when present.

3. **`POST .../sessions`**: call **`asyncio.run(create_intake_session_and_start(...))`** — same async pattern as **`api_candidate.generate_artifact`**.

4. **`GET .../sessions/<session_id>`** and **`GET .../sessions/active`**: return **`get_intake_session_dto`**; no model call.

5. **`POST .../turns`** and **`POST .../build`**: async core calls.

6. In **`src/ui/server.py`**, add:

   ```python
   from ui.api.api_intake import intake_bp
   app.register_blueprint(intake_bp)
   ```

   (after **`candidate_bp`**).

7. Optional query param **`debug=true`** on turn/build routes only: pass **`debug=True`** into **`do_task`** when present (AST-538 backend contract); **no** extra logging in React (out of scope).

---

## Stage 4: Component tests

**Done when:** Tests pass locally; manifest handoff for Betty cites these paths.

1. **`tests/component/core/test_intake.py`**

   - Fixture candidate + mock **`do_task`** (patch at **`src.core.intake.do_task`**).
   - Create session persists context source fields.
   - Turn appends transcript; **`ready_to_build`** propagates.
   - Second **`post_intake_build`** on same session raises / 400 path.
   - Build calls **`sync_company_search_terms`** (patch **`database.sync_company_search_terms`**) and **`save_candidate_data`** with expected nested keys.
   - **`check_context_complete`** invoked after build (patch assert call).

2. **`tests/component/ui/api/test_api_intake.py`**

   - Flask test client with auth fixture (mirror **`test_api_candidate`**).
   - **`POST /sessions`** **201** shape; **`GET /sessions/active`**; build blocked when not ready (mock core).

---

## ASTRAL_CODE_RULES self-review

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Reuses **`run_candidate_artifact_generation`** / ledger pattern; **`_apply_build_payload`** uses existing **`save_candidate_data`** + **`sync_company_search_terms_from_text`** |
| §2.1 config | **`INTAKE_CONFIG`**, **`TASK_CONFIG`** schemas; Estelle id not hardcoded in UI |
| §2.2 do_task | All model calls via **`do_task`** + DB **`agent_task`** |
| §2.4 batch | **`batch_id`** per turn; ledger **`intake-{task_key}`** |
| §2.6 state | **`check_context_complete`** only — no new candidate transitions |
| §3.3 imports | **core/intake** → data, agent, candidate; **ui** → core only |
| §3.5 naming | snake_case API JSON; table **`candidate_intake_session`** |

No conflicts requiring **`conf-!!-NONE`**.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New SQLite table, core module, Flask blueprint, `agent.py` snapshot hook, and three `TASK_CONFIG` entries across data, core, utils, and UI layers.

**Conf:** `Medium` — Ledger/`do_task`/company-search sync patterns are established (AST-515, AST-524), but multi-turn cache snapshot + `agent.py` intake branch is new integration surface.

**Risk:** `Medium` — Incorrect build persistence or search-term sync could affect roster inflow and `CONTEXT_READY` gating; mitigated by whitelisting build keys and reusing `check_context_complete` without new state-machine code.

---

## Review (build)

| Field | Value |
|-------|-------|
| Publish ref | `origin/sub/AST-539/AST-558-intake-session-api` |
| Tip SHA | `04de72cc` |
| Built | 2026-06-02 (Ada / build-astral) |

**UAT note:** Seed `intake_initiate_candidate`, `intake_candidate_response`, and `intake_build_request` in Manage Tasks (`agent_id` = `X00_estelle_recruiter`) before live Estelle intake calls; missing rows surface as `do_task` errors.

**Tests:** Component tests in Stage 4 deferred to Betty (`qa-astral`); build-astral test-tree ban.
