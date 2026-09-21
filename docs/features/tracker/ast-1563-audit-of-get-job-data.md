# AST-1563 — Audit of get_job_data

<!-- linear-archive: AST-1563 archived 2026-09-09 -->

## Linear archive (AST-1563)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1563/audit-of-get-job-data  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. **Map the two** `get_job_data` **surfaces** — distinguish async coat-check `tracker.get_job_data(job, key)` (JD self-heal via gazer) from sync contact-task handler `contact_task_get_job_data(candidate_id, job_id)` registered in `CONTACT_TASK_CONFIG`. Document signatures, call paths, and what each returns.
2. **Inventory coat-check callers vs direct** `job_data` **reads** — ripgrep `src/` and `tests/` for:
   * `await tracker.get_job_data(` / `tracker.get_job_data(`
   * `job["job_data"]`, `job.get("job_data")`, nested key access (`job_description`, grades, artifacts, etc.)
   * `save_job_data` writers (context for read patterns)
     Classify each site: faithful coat-check, justified direct read (e.g. batch paths where JD already guaranteed), or potential end-run. Note `docs/ASTRAL_CODE_RULES.md` coat-check statute as the bar.
3. **Trace context assembly at dispatch** — follow the inbound path Susan cares about (Contact Estelle turn is the primary dispatch surface):
   * `contact.run_contact_estelle_turn` → `load_slack_conversation_context` → `live_content` string assembly (ACL, contact tasks, conversation, latest inbound)
   * `do_task(..., live_content=..., candidate_data=...)` in `agent.py` — how prompt slots hydrate from `candidate_data` / caller tokens; what job objects (if any) are on the context dict vs only in `live_content` text
   * Post-turn: `parse_contact_task_markup` → `run_contact_task_dispatch` → handler results folded into follow-up `live_content`
     Also skim consult/gazer dispatch entrypoints if they assemble job-bearing context differently.
4. **Produce the job_data consumer file list** — every file under `src/` (and note test-only mirrors) that reads or writes `job_data` content, one line each: file, keys/fields touched, why (UI display, consult grading, coat-check, contact hydration, meteorite land, artifacts, etc.).
5. **Write findings** — append a structured audit section to this ticket (comment or linked doc if large): coat-check fidelity summary table, context-assembly narrative with function names, full file list. **No product code changes.**

## Done when

* Execution plan above is complete and findings are posted on AST-1563.
* Coat-check vs direct-access inventory covers all `src/` call sites with a clear faithful / justified / questionable classification.
* Context assembly at dispatch is documented from Slack/event ingress through `do_task` (and contact-task follow-up turn when markup present).
* File list of `job_data` consumers exists with brief per-file rationale.
* No commits to product code.

## Risks / open questions

* **Scope of "context object"** — Susan's brief may mean Contact Estelle's `live_content` + `candidate_data` raft only, or all dispatch paths (consult batch, gazer, UI API). Plan covers Contact first; consult/gazer noted if time — confirm with Susan if a wider sweep is required.
* `contact_task_get_job_data` **deliberately bypasses async coat-check** (AST-1518 boundary) — audit must treat that as intentional, not a violation.
* **Frontend reads** — `src/ui/frontend/` consumes job payloads from API responses (already lifted from `job_data` server-side); include in file list but distinguish from core coat-check layer.

---

## Original brief

Perform an audit of the codebase to determine how faithfully the get_job_data function in [tracker.py](<http://tracker.py>) is called, versus assuming the data is available on the context object directly.

Do not change code.

separately, describe how the context object is assembled at the time of dispatch before it is passed through to the core component.

Make a list of files that use content from job_data for any reason and a brief summary of how and why.

### Comments

#### chuckles — 2026-09-01T16:23:34.067Z
# AST-1563 audit findings

## 1. Two `get_job_data` surfaces

| Surface | Location | Signature | Behavior |
|---------|----------|-----------|----------|
| **Coat-check (async)** | `tracker.get_job_data(job, key)` | `(job: dict, key: str) → Any` | Reads `job["job_data"][key]`; for `job_description` only, self-heals via `gazer.fetch_jd_batch` when missing/short. Sole registered coat-check key per `ASTRAL_CODE_RULES` §2.8. |
| **Contact-task handler (sync)** | `tracker.contact_task_get_job_data(candidate_id, job_id)` | `(str, str, *, debug) → dict` | Loads row via `get_job(jid)` (DB + artifact overlay), checks `_job_owned_by_candidate`, returns `_contact_task_hydrate_job(job)` with `agent_story`. **Does not** call async coat-check (AST-1518 boundary — stored data + hydration only). |

Registered in `CONTACT_TASK_CONFIG["get_job_data"]` → handler dotted path `src.core.tracker.contact_task_get_job_data`.

---

## 2. Coat-check fidelity: `get_job_data` vs direct `job_data` access

### Production callers of async `tracker.get_job_data`

| File | Function | Classification |
|------|----------|----------------|
| `src/core/consult.py:838` | `_prep_live_content` | **Faithful** — canonical pre-agent JD path; also used by `render_verdict`, batch encoded consult, `analysis_upshot`. |

**Only one production call site** for the async coat-check function in `src/`.

### Direct `job_data` reads in `src/` — classification

| File | Usage | Classification |
|------|-------|----------------|
| `consult.py` | `_prep_analysis_upshot_live_content` reads `raw_job_listing`, DO/GET/LIKE grades after `_prep_live_content` | **Justified** — JD already coat-checked in same call chain |
| `consult.py` | `build_job_token_context` reads `job_description` + phase keys for `VISIBLE_JD` / analysis phase tokens | **Mixed** — job row comes from `ctx.batch_entities` / `get_job`; JD may be stale if caller skipped `_prep_live_content`, but token path is parallel to live_content not a JD end-run for agent scoring |
| `consult.py` | `_jd_ready_for_evaluate`, `evaluate_jd_batch` not-ready branch, batch listing/JD length checks | **Justified** — readiness gates / metadata; batch docstring expects gazer-scraped JD already in blob |
| `consult.py` | `qualify_job_listings` raw listing char counts | **Justified** — `raw_job_listing` is not a coat-check key |
| `tracker.py` | Internal artifact/candidate_results helpers, `get_job_data` itself, `get_job` overlay | **Internal** — tracker layer owns the blob |
| `tracker.py` | `contact_task_get_job_*` via `get_job` + hydrate | **Intentional bypass** (contact read boundary) |
| `gazer.py` | Writes `job["job_data"][jd_key]` after scrape | **Writer/fetch layer** — populates blob for downstream reads |
| `meteorite.py` | Dedupe compare JD length / employer on recorded row | **Justified** — compare stored snapshots |
| `builder.py` | `build_*_from_job` reads artifacts, cover letter, keywords from in-memory job | **Justified** — caller supplies loaded job row; no agent/scrape trigger |
| `agent.py` | Decode path builds ephemeral `job["job_data"]` from AI meta; `_job_row_from_ctx` defaults empty dict | **Write/decode** — not a read end-run |
| `agent.py` | Entity story hydration uses `entity.get("job_data")` | **Justified** — presentation of stored entity |
| `api_jobs.py` | `_flatten_grades` lifts grades/scores/rubrics to top level for API | **UI read layer** — no fetch |
| `api_jobs.py` | Artifact overlay merge on detail read | **UI read layer** |
| `api_admin.py` | Admin job inspection | **UI read layer** |

### Summary

- The **coat-check statute is narrowly honored for JD before agent calls**: every consult agent path that needs JD text goes through `_prep_live_content` → `get_job_data`.
- **Widespread direct `job_data` access** exists for: (a) non-coat-check keys (`raw_job_listing`, grades, artifacts), (b) batch readiness gates assuming prior gazer write, (c) UI flattening, (d) contact-task stored reads, (e) job-scoped prompt tokens in `build_job_token_context`.
- **No production caller** outside `consult._prep_live_content` invokes async `get_job_data` — the function is under-used relative to direct blob access, but the critical agent-facing JD path is faithful.
- **Potential gap (informational, not flagged as bug):** `build_job_token_context` reads `job_description` directly from the job row for `{$VISIBLE_JD}` and phase tokens without invoking coat-check. In practice `render_verdict` coat-checks JD into `live_content` first and passes the same `job_row` in `batch_entities`; if JD were missing, `_prep_live_content` would fail before `do_task`. Token view could show empty JD while live_content succeeded only if row mutated between calls (unlikely).

---

## 3. Context assembly at dispatch

### A. Contact Estelle (`run_contact_estelle_turn`) — primary conversational dispatch

```
Slack event
  → load_slack_conversation_context(channel, thread_ts)   # cached Slack history
  → assemble live_content string:
       channel / thread_ts / astral_candidate_id / candidate_state
       ## Available Contact skills (ACL)
       ## Available contact tasks (markup)
       ## Land meteorite (job scraps)
       ## Conversation (trimmed messages)
       ## Latest inbound
  → candidate_data = get_candidate(...).candidate_data inner dict (or {})
  → do_task(CONTACT_ESTELLE task_key, live_content=..., candidate_data=..., store_agent_data=True)
  → parse_contact_task_markup(reply) → run_contact_task_dispatch(markup_spans)
       → contact_task_get_job_data loads job via get_job (no coat-check)
       → results appended as JSON in follow-up live_content
  → optional second do_task (same-event follow-up turn) when markup present
  → run_contact_skill for skill_calls ACL paths
```

**Job objects are not on the dispatch context dict.** Job data enters only when Estelle emits `~~/get_job_data <job_id>~~` markup and the handler result is serialized into the follow-up turn's `live_content` text.

### B. Dispatcher → consult batch / render_verdict

```
dispatcher._dispatch_one
  → ctx = database.get_candidate(candidate_id)   # full candidate raft (+ api key, flags)
  → ctx["entity_batch_id"] = ...
  → entity loader fetches job rows (list_jobs / get_job) — each row includes job_data blob from DB
  → consult batch helpers / render_verdict(astral_job_id, ctx=ctx)
       → job = tracker.get_job(id)
       → live_content = await _prep_live_content(job, company)  # coat-check JD here
       → task_ctx = {**ctx, batch_entities: [job_row], vector_labels, batch_size: 1}
       → do_task(agent_task, live_content=..., index=astral_job_id, ctx=task_ctx)
```

### C. Inside `do_task` (core component)

| Input | Role |
|-------|------|
| `live_content` | NO_CACHE prompt segment (TASK block) — JD text lives here for consult |
| `ctx` | Candidate raft: `astral_candidate_id`, `candidate_api_key`, optional `batch_entities`, `job`, `vector_labels`, dispatch chain keys |
| `candidate_data` / `_token_view_for_do_task(ctx, ...)` | Candidate-scoped prompt tokens (name columns, resume structure, etc.) |
| `_job_context_for_call(ctx, index, cd)` | When exactly one job in scope: `build_job_token_context(_job_row_from_ctx(...))` → `{$VISIBLE_JD}`, phase tokens, resume catalog — reads **directly from job row's job_data** |
| `index` | Entity id (e.g. `astral_job_id`) for audit + decode position mapping |

**Context object = `ctx` dict + assembled prompt segments**, not a single typed object. Job-bearing data splits across: (1) `live_content` string for agent-visible JD/website text, (2) `ctx.batch_entities` / `ctx.job` for decode and job tokens, (3) persisted `job_data` blob on each entity row from DB.

---

## 4. Files using `job_data` content (`src/`)

| File | How / why |
|------|-----------|
| `src/utils/config.py` | Schema keys, `CONTACT_TASK_CONFIG`, `TRACKER_CONFIG["job_data_keys"]`, meteorite employer key — configuration only |
| `src/core/tracker.py` | SoT read/write helpers, coat-check, artifact merge, contact-task hydration, ingest/initialize |
| `src/core/consult.py` | Grading pipeline read/write (grades, scores, rubrics, analysis_upshot), live_content prep, token context, batch gates |
| `src/core/gazer.py` | JD scrape writes to `job_data`; batch fetch reads/writes |
| `src/core/meteorite.py` | Land/dedupe compares stored JD and employer fields |
| `src/core/builder.py` | Resume/cover HTML from in-memory job artifacts and keywords |
| `src/core/agent.py` | Job row from ctx for tokens; decode writes meta into job_data; entity story reads blob |
| `src/core/contact.py` | Indirect — dispatches to contact_task handlers that load jobs |
| `src/core/roster.py` | Comment mirror of tracker pattern (company_data, not job_data) |
| `src/ui/api/api_jobs.py` | Flatten grades/rubrics for SPA; artifact overlay; save proposed answers |
| `src/ui/api/api_admin.py` | Admin job listing inspection |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Display analysis_upshot, artifacts, JD from API payload |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | JD presence/display |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Job artifact edit response handling |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Report rendering from flattened + job_data fields |
| `src/ui/frontend/src/lib/analysisUpshot.ts` | Parse persisted analysis_upshot JSON shape |

**Test mirrors:** `tests/component/core/test_tracker.py`, `test_consult.py`, `test_contact.py`, `test_gazer.py`, `test_meteorite.py`, `test_builder.py`, `test_agent.py`, `tests/component/ui/api/test_api_jobs.py`, `test_api_admin.py`, frontend component tests — exercise same access patterns.

**Scripts (non-product):** `scripts/gen_ast382_src_review.py`, `scripts/migrations/backfill_collapse_blank_lines.py`, `scripts/spikes/ast445_evaluate_jd_batch_trace.py`, `scripts/migrate_encoded_agent_data.py`.

---

No code changes made (per brief).

---

_Implementation detail may live in git history on `origin/dev`._
