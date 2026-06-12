<!-- linear-archive: AST-351 archived 2026-06-03 -->

## Linear archive (AST-351)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-351/convert-consult-to-use-encoded-responses  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** betty  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

We need to use encoded responses for the consult stages, because the analysis in the first two stages are wasted if the third stage fails.  If all three pass, we can run a complete analysis on the job description with Estelle and build the report that way for the candidate to peruse.

Now that we are moving to a pure grading-rubric for most of consult work, I would like to start using the rubric's grade description text as the "Reason", for all the consult runs (qualify, evaluate, do, get, like).

Our grades are formatted mostly consistently in the text block, so I think we can use regex to parse it from the text when the save happens.

So, for each vector, I want BOTH, a single text file that asks the prompt for the vector, AND a "normalized" array of grades and descriptions, so that we can programmatically reference the rubric grades without having to parse at runtime, but hte user can still do a copy/paste and work with the text.  

Let's use the parsing logic as a validation, assuming that the grades are the last part of the text, and the grades are line-break-delimited and formatted as {grade}{separator}{description}, and if there are not at least TWO lines of grades, then throw a validation error when the content is saved and don't overwrite the original array, if any.

{separator} can be "{whitespace}={whitespace}", "{whitespace}=={whitespace}", or "{whitespace}:{whitespace}" where whitespace is optional.

NOTE: This change will require changes to the task prompts in the database, and Susan will do those as needed.

### Comments

#### susan — 2026-05-06T20:55:48.950Z
Review feedback resolved. Branch `chuckles/ast-351-convert-consult_-to-use-encoded-responses` is ready for testing. Commit: `0861726e`

— Betty

#### susan — 2026-05-06T20:31:06.451Z
**Code review (Radia)** — local feature ref **`chuckles/ast-351-convert-consult_-to-use-encoded-responses`** missing (`git rev-parse` failed). Reviewed **local `dev`** range **`1c4b5dd6^..18bbf486`** (`feat(ast-351): encoded consult…` + `chore(ast-351): append review stub`).

**Counts:** fix-now **0** · discuss **2** · advisory **1**

**What’s solid:** Encoded-grade / rubric-reason pipeline lands in **core** (`consult.py`, `candidate.py`), **`src/utils/rubric_text.py`**, and **`TASK_CONFIG` / `CONSULT_CONFIG`** updates with UI/API touchpoints — matches ticket direction (normalized arrays + text, validation on save). **§1.2 / §2.1** layering looks respected from the file list.

**Discuss:** (1) **`CONSULT_CONFIG` / `TASK_CONFIG` churn** — confirm every consult step that reads grades tolerates the new encoded shape in production DBs Susan migrates separately (ticket note). (2) **`api_candidate.py` + `ArtifactEditor.tsx`** — thin wiring; sanity-check round-trip with encoded payload sizes.

**Advisory:** Large diff across config + core; worth a focused regression pass on **qualify / evaluate / get / do / like** after DB prompt migration.

New doc on branch path in diff: `docs/features/consult/ast-351-convert-consult-to-use-encoded-responses.md` — not appended from this pass (no local feature ref).

— Radia

#### susan — 2026-05-06T20:16:55.433Z
**Radia — review blocked (no branch to diff)**

Linear lists `gitBranchName` `chuckles/ast-351-convert-consult_-to-use-encoded-responses`, but that ref is **not** on `origin` here, so no checkout / diff was possible.

**State:** left **Code Complete**.

— Radia

---

# AST-351 — Convert consult_* to use encoded responses

Linear: **AST-351** · Project: Astral Dispatcher (Linear) · Doc: `docs/features/consult/` · Blocked-by label: **AST-357** (grade confidence — already implemented on `dev`; treat Linear dependency as satisfied for implementation planning.)

---

## Product notes (clarified post-ticket)

The Linear ticket already asked for rubric grade description text as the **Reason** on all five consult paths (qualify, evaluate, do, get, like). This doc spells out two details that were easy to under-specify in the ticket:

1. **Replace, not supplement:** At runtime, `grades[].reason` is **always** the rubric line’s **description** for that vector + letter — **not** model freeform analysis. **Separate:** optional **line tail** for do/get/like (product note **4** below) is stored as **`{prefix}_notes`** on `job_data`, not in `grades[].reason`.
2. **Duplicate into `job_data`:** Canonical definitions stay in `candidate_data` artifacts (text + normalized `grade_descriptions`). When consult results are persisted on the **job** row (`{prefix}_grades` via `tracker.save_job_data`), each stored grade row should still carry **`reason` = that same description** so job JSON is self-contained for UI, dispatch sorting context, and debugging—**intentional duplication** so callers are not forced to join back to the candidate rubric for every read.

3. **Schema parity (locked):** `grade_do`, `grade_get`, and `grade_like` drop the **fat JSON** job-artifact shape (`dealbreakers`, `ja_notes`, `job_summary`, `overall_assessment`, `clarifications`, `critical_keywords`, `ats_concerns`, etc.). **Grade segments** on the wire use the **same compact segment grammar as `evaluate_jd`** (`pos|{code}{grade}{conf}|...`). **`CONSULT_CONFIG`:** remove legacy **`save_fields`** from `consult_do` and `consult_get` (no more persisting those blobs from the model JSON).

4. **Optional short notes tail (in scope for AST-351):** Add **`output_type` `grades_encoded_notes`**. **Clarify `grades_encoded_meta`:** On **qualify**, the **grade segments are listing-specific too** — each decoded line is one **job listing** in the batch (`pos` maps to that row); rubric codes grade **that listing**. The **`_meta`** part is what’s structurally different after the segments: non-grade chunks follow a **fixed listing schema** (`company_job_id`, `job_title`, `job_link`, then `key:value` → `job_data`). **`grades_encoded_notes`** is for **do / get / like** (one line per **JD consult** row, `pos=000`): **same segment grammar** for grades, but any **non-segment** tail is **only** rejoined into **`job["notes"]`** — no listing-ID columns, no `job_data` key:value tail. **`{$OUTPUT_INSTRUCTIONS}`** describe grades **plus** that optional freeform tail. **No tail** → **no error**; **`{prefix}_notes`** omitted when absent. **Cost control:** prompts may omit the tail. **Never** overload **`grades_encoded_meta`** for do/get/like notes — wrong **post-segment** field mapping even though both types are “grades on a wire line.”

5. **Multi-line batch later (no decoder refactor):** `_decode_payload` already processes **multiple lines**, one **`pos`** per line (same core loop as **evaluate** and **qualify**). If we later send **many JDs in one do (or get / like) call**, the model can return **N lines** with **`pos` 0…N−1**, each with its **own optional `notes` tail** at the end of that line. **`grades_encoded_notes`** stays one implementation: per line, segments → `grades`, remainder → **`notes`** for **that** decoded job row. **No second encoder design** — only call-site work (`batch_entities` length N, orchestration to score/save per `astral_job_id`). **AST-351** can still ship **`render_verdict`** one-job-first; the wire format is already batch-ready.

---

## Plan

### 1. Schema and persistence surface (locked)

- **`TASK_CONFIG`:** For `grade_do`, `grade_get`, `grade_like`, replace the fat JSON `response_schema` with the **post-decode** shape: `jobs` list, each job `astral_job_id` + `grades` (`vector`, `grade`, `confidence` from decode; **`reason` from rubric** per §6) + **optional** string field **`notes`** when the wire line included a tail.
- **`output_type`:** **`grades_encoded_notes`** — **new** entry under `ASTRAL_CONFIG["output_types"]` with `payload_instructions` for grades + optional tail; distinct from **`grades_encoded_meta`** (see product note **4**).
- **`CONSULT_CONFIG`:** Remove **`save_fields`** from `consult_do` / `consult_get`. Optionally document that **`{save_prefix}_notes`** is populated by `render_verdict` when decode yields non-empty `notes` (convention over new config keys unless you prefer an explicit `notes_job_data_key`).
- **`render_verdict`:** After flattening `jobs[0]` → grades + hydration, if `job.get("notes")` is non-empty after strip, `save_data[f"{prefix}_notes"] = that string`. No legacy `save_fields` copy from old JSON.

---

### 2. Switch `grade_do`, `grade_get`, `grade_like` to compact encoded payloads (`TASK_CONFIG` + DB prompts)

**Today:** `response_format: json`, full `response_schema` with `grades[].reason` and many optional narrative fields.

**Target:** Same outer JSON envelope (`agent_performance` + `agent_payload`), **`agent_payload`** a **compact string** decoded by `_decode_payload` using **`grades_encoded_notes`** (grade segment rules identical to **`grades_encoded`** / evaluate; optional **notes** tail per §3).

**Config (`src/utils/config.py`):**

- Register **`grades_encoded_notes`** in `output_types` and point the three agent tasks at it.
- Keep `grading_mode: scored`, `grades_key`, `rubric_artifact`; slim `response_schema` to the decoded shape (including optional per-job `notes` if schema validation should carry it — align with how other encoded tasks validate after decode).
- Extend **`stringify_response_schema()`** with an example line **with** optional tail for this type.

**Database (Susan-owned per issue):** Update `agent_task` rows — remove fat JSON field expectations; **optionally** mention a **very short** optional tail after grades, **or omit** that instruction entirely to control cost — decoder accepts both (empty tail = success).

---

### 3. Encoder layout — `grades_encoded_notes` (grades + optional tail)

**Implement in `src/core/agent.py` (`_decode_payload`):** Branch when `output_type` is the new key (or delegate from existing `_encoded` hook):

- **Same** as `grades_encoded` for: line split, `pos`, `batch_entities` → `astral_job_id`, classifying `fields[1:]` into grade segments vs non-segments via `_GRADE_SEG`.
- **Difference from `_meta`:** After grade segments, non-segment chunks are **not** interpreted as `company_job_id` / title / link / `key:value` listing fields; rejoin them as **`job["notes"]`** only (`"|".join(meta).strip()`). Empty after strip → omit **`notes`** / `None` — **never** fail validation for “no tail.”
- **Rejoin:** If the model puts `|` inside the blurb, split-then-rejoin preserves the intended text.

**Line cardinality:** One non-empty input line → one `jobs[]` entry (same as evaluate/qualify). **`render_verdict` (MVP):** one line, **`pos=0`**, `batch_entities=[job]`. **Future:** N JDs → N lines, **`batch_entities`** of length N — decoder unchanged (see product note **5**).

---

### 4. Thread `batch_entities` + `vector_labels` into `render_verdict` → `do_task`

`_run_batch_consult` already builds `task_ctx` with `batch_entities`, `vector_labels`, and `batch_size` for decode + label hydration.

**`render_verdict`** (`src/core/consult.py`) currently calls `do_task(..., ctx=ctx)` without that batch context. For encoded consult:

- Build `vector_labels` from the same rubric resolution as `_run_batch_consult` (`rubric_artifact` → criteria list with `code` + `label`).
- Set `batch_entities` to a **one-element list** `[job]` for MVP (same dict `get_job` returns, ensuring `astral_job_id` is present). **Later batching:** same mechanism as `_run_batch_consult` — pass **N jobs**, no change to **`grades_encoded_notes`** decode.
- Merge into `ctx` (copy dict if needed) before `do_task`.

---

### 5. Normalize `parsed_response` for `render_verdict` after decode

Decoded encoded tasks return top-level **`jobs`**, not **`grades`**.

**`render_verdict`** today does `grades = parsed.get("grades")` and copies **`save_fields`** from top-level `parsed` (removed per §1).

**Change:** After a successful `do_task`, if `parsed` has `jobs` with exactly one entry matching `astral_job_id`, set **`grades`** from that entry’s `grades` list. If the decoded job includes **`notes`**, persist **`{prefix}_notes`** per §1 when non-empty. No other agent-payload fields for these tasks.

Scoring (`_render_score`) and `{prefix}_grades` persistence use the grade list once **`reason`** is hydrated per §6.

---

### 6. Populate `reason` from rubric — universal for all consult; persist on the job row

**Scope (universal):** qualify_job_listings, evaluate_jd, consult_do, consult_get, consult_like — same rule everywhere consult grades are produced and saved.

**Semantics:** For each grade row, **`reason` is the rubric’s human-authored description for that grade letter** on that vector (from normalized `grade_descriptions` / parsed trailing block). This **replaces** any historical pattern where the model wrote freeform text into `reason`. After hydration, downstream code (`_render_pass_fail`, `_render_score`, UI, exports) always sees `reason` as that description.

**Source of truth on save (step 7):** each rubric vector tab stores human-editable `content` plus a **normalized** array, e.g. `[{"grade":"A","description":"..."}, ...]`, built by parsing the trailing “grade table” in `content`.

**When to hydrate:** Immediately after decode (or equivalent assembly of `grades` for that job), **before** `_render_pass_fail` / `_render_score` and **before** `tracker.save_job_data(..., {prefix}_grades=...)`. For each grade row (vector label + letter after code→label hydration), set `reason` to the matching description. **Strict default:** if `(vector, grade)` has no description row, treat as validation failure (same severity as missing vector)—do not persist partial grades for that job for that step.

**Where to implement:** Prefer **`consult.py`** and one shared helper (e.g. `_hydrate_grade_reasons_from_rubric(grades, rubric_criteria)`) so `agent.py` stays unaware of candidate artifact layout. Core reads normalized arrays from `ctx["candidate_data"].artifacts[rubric_key]`; utils holds pure parse helpers for **writing** validation only (step 7).

**Batch qualify / evaluate:** After `_decode_payload` builds each job’s `grades`, run the same helper before `process_fn` / per-job saves so `joblist_grades` / `jd_grades` (and any intermediate structures) already carry `reason` before state transitions and `save_job_data`.

**Per-job do / get / like:** `render_verdict` path: hydrate `grades` before `save_data` is built so `{prefix}_grades` on the job row always includes **`grade`, `confidence`, `vector`, and `reason`** (description copy) for every consult stage.

---

### 7. Rubric save validation + dual storage (text + normalized array)

**Requirement:** For each vector (each rubric criterion entry: prompt text + parsed grades), keep:

1. **Single text blob** — the prompt / instructions the author edits (existing tab `content` in `ArtifactEditor` / artifact array shape).
2. **Normalized array** — `[{ "grade": "A"|"B"|..., "description": "..." }, ...]` for programmatic lookup.

**Parsing rules (validation on save):**

- Grade block is the **last** part of the text: trailing lines only, each line one grade row.
- Line format: `{grade}{separator}{description}` where `separator` is `\s*=\s*`, `\s*==\s*`, or `\s*:\s*` (regex).
- **At least two** such lines; otherwise **raise validation error**, do **not** overwrite the prior artifact array for that key (merge must reject the bad rubric slice and return 400 to the client with a clear message).

**Where to implement validation:**

- **Not** in thin `save_candidate_data` alone (docstring: pure persistence). Add **`src/core/candidate.py`** (or a dedicated `src/core/rubric_validation.py` if file size matters) a function such as  
  `validate_candidate_artifact_overlay(existing_candidate_data: dict, incoming: dict) -> None`  
  that raises `ValueError` with a user-safe message when `incoming["artifacts"]` touches registered rubric keys.
- **`src/ui/api/api_candidate.py`** `update_candidate_data`: call validator before `save_candidate_data`; return `400` + JSON error on failure.

**Registry of keys to validate:** Derive from config — e.g. union of `CONSULT_CONFIG[*]["rubric_artifact"]` values plus any other artifact keys that use the same editor pattern, **centralized in `config.py`** as a single constant (satisfies “no hardcoded sets” in §1.4 / §2.1).

**Storage shape:** Extend each rubric criterion object with a field such as `grade_descriptions: [...]` (name bikesheddable) alongside `label`, `content`, `code`. On successful parse, write both updated `content` and `grade_descriptions`. **Index by vector id:** continue using array order with stable `code` / `label` per item (existing convention); no new “unindexed list” anti-pattern.

**Parser implementation:** New **pure** helpers under `src/utils/` (e.g. `src/utils/rubric_text.py`: `parse_trailing_grade_block(text: str) -> list[dict]`, `split_body_and_grade_block(text: str) -> tuple[str, list[dict]]`) with unit tests in `scripts/` or `tests/` if the repo adds a test package — otherwise minimal `if __name__` guard is discouraged; prefer a tiny pytest file if Susan approves test layout.

---

### 8. Frontend (`ArtifactEditor` / rubric pages)

- On save response **400**, show toast with server message; **do not** clear local state in a way that loses the user’s text (editor already has dirty/snapshot behavior — verify failure path leaves prior server state intact).
- Optionally surface read-only **parsed grade rows** under each tab for sanity check (nice-to-have; not required for MVP if API errors are clear).

Files: `src/ui/frontend/src/components/ArtifactEditor.tsx` and any rubric-specific pages if they bypass the shared editor.

---

### 9. Admin / ad-hoc / `api_admin` decode preview

Decode preview paths must handle **`grades_encoded_notes`** the same way as runtime decode (optional `notes` tail). Show an example line **with** and **without** tail in docs or admin UI help text if useful.

---

### 10. Docs and migrations

- **`docs/ASTRAL_CODE_RULES.md`**: If `render_verdict` + encoded consult becomes the canonical pattern, add a short bullet under §2.7 pointing to this doc.
- **Optional one-time script** for backfilling `grade_descriptions` from existing `content` (best-effort regex); run only with Susan’s approval — validation on save already prevents *new* bad states.

---

### 11. Compliance check (ASTRAL_CODE_RULES)

| Rule | How this plan complies |
|------|-------------------------|
| §3.3 Layers | UI calls core validator; core uses utils for pure parse; `agent.py` gains decode branch only (no `candidate_data`); rubric reason hydration stays in `consult.py`. |
| §2.1 Config SOT | Rubric artifact key list and `valid_grades` already in config; reuse for parser allowed letters. |
| §2.4 Batch / batch_id | No change to claim/process/release; `render_verdict` still one job per dispatch invocation; `batch_id` still from `do_task` / logging. |
| §2.6 States | Still only `CONSULT_CONFIG` + `tracker.transition_job_state`; no new states. |
| §1.3 DRY | Shared grade-segment parsing with `grades_encoded`; consult-notes type adds one tail branch; `hydrate_grade_reasons` + `parse_trailing_grade_block` unchanged for rubric saves. |
| §3.5 Naming | snake_case for new Python helpers and API errors; React unchanged except messages. |

---

### 12. Cross-check vs `docs/ASTRAL_CODE_RULES.md` (ready for implementation)

**Aligned (no conflict)**

| Rules section | Notes |
|----------------|--------|
| **§2.1 Config SOT** | `TASK_CONFIG`, `CONSULT_CONFIG`, `ASTRAL_CONFIG["output_types"]`, optional rubric-key frozenset — all in `config.py`. |
| **§2.2 do_task** | Consult still orchestrates via `do_task`; no change to “core does not assemble Anthropic params.” |
| **§2.3.2 Confidence** | Encoded segment already carries conf digit; `_render_pass_fail` / `_render_score` unchanged in intent. |
| **§2.4 Batch / batch_id** | MVP: one job per `render_verdict`, existing `batch_id` from `do_task`. Future N-line decode does not bypass claim/process/release when wired through dispatch. |
| **§2.6 States** | Still `CONSULT_CONFIG` + `tracker.transition_job_state` only. |
| **§2.7 render_verdict** | Same 9-step spine; extend step 7 mentally to “grades + score **and optional `{prefix}_notes`**”. Update `ASTRAL_CODE_RULES` §2.7 when implementing (see §10). |
| **§3.3 Imports** | Utils parser pure; core validates + hydrates; `agent.py` decode only; UI → core for candidate artifact validation. |
| **§1.5 Errors** | API `400` on bad rubric merge; core/domain `ValueError`; data layer raises — unchanged pattern. |

**Verify during implementation (not blockers, but check)**

| Topic | Rule / pattern | Action |
|--------|----------------|--------|
| **§2.3.1 `vectors`** | If `TASK_CONFIG` keeps `vectors`, `do_task` still runs letter/vector-name validation against that list. | Either keep `vectors` in sync with rubric codes **or** document removal and rely on rubric + `_render_score` only — pick one and match `agent.py` validation. |
| **§1.1 `database.py`** | New **tables** need header inventory update. | No new tables expected; `job_data` JSON blob keys only — confirm `tracker.save_job_data` / merge rules accept **`do_notes`**, **`get_notes`**, **`like_notes`** without a whitelist gap. |
| **§2.8 Coat-check** | `TRACKER_CONFIG["job_data_keys"]` maps coat-check fetchers. | **`{prefix}_notes`** are **writes from consult**, not lazy fetch — do **not** register as coat-check keys unless there is an on-demand fetcher (there isn’t). |
| **§3.2 UI + config** | Job/candidate shaping for list/detail often via `DATA_SHAPES` / API resolution. | If any **Jobs** UI should show the new notes columns, add **config-driven** field defs and resolve in **`src/ui/api/`** — avoid hardcoding in React. Optional for MVP if nothing displays notes yet. |
| **§1.3 DRY / helpers** | Public first, helpers grouped in `agent.py` / `consult.py`. | When adding `_decode_payload` branch, extract shared “split segments vs meta” if duplication with `_meta` grows. |

**Doc debt (already in plan §10)**

- After shipping, add a short **§2.7** bullet in `ASTRAL_CODE_RULES.md` for encoded consult + optional notes + pointer to this feature doc.

---

## Files Changed (summary)

| File | Action |
|------|--------|
| `docs/features/consult/ast-351-convert-consult-to-use-encoded-responses.md` | **Create** (this plan; later: review + resolution sections). |
| `src/utils/config.py` | **Modify** — `TASK_CONFIG` for `grade_do` / `grade_get` / `grade_like` (schema + `output_type: grades_encoded_notes`); new **`ASTRAL_CONFIG["output_types"]`** entry; **remove** `save_fields` from `CONSULT_CONFIG` `consult_do` / `consult_get`; optional `RUBRIC_ARTIFACT_KEYS` (or equivalent) for save validation. |
| `src/core/agent.py` | **Modify** — `_decode_payload` (or helper): branch for **`grades_encoded_notes`**; optional `notes` on job dict; empty tail = success, no `notes` key or null. |
| `src/core/consult.py` | **Modify** — `render_verdict`: `batch_entities` / `vector_labels` in `ctx`; flatten `jobs[]` → `grades`; persist **`{prefix}_notes`** when present; **remove** legacy `save_fields` loop; reason hydration per §6. |
| `src/utils/rubric_text.py` (or `formatting.py`) | **Create / modify** — trailing grade block parse + validation helpers. |
| `src/core/candidate.py` | **Modify** — new validation entry for artifact saves (or adjacent module). |
| `src/ui/api/api_candidate.py` | **Modify** — call validator before `save_candidate_data`. |
| `src/ui/api/api_admin.py` | **Modify** — decode preview for new `output_type` if applicable. |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | **Modify** — error handling for 400 on save; optional UI for normalized rows. |
| `agent_task` table (DB) | **Data** — prompt text for affected tasks (Susan). |
| Tests | **Add** if project standard allows — parser edge cases (separators, `<2` lines, trailing whitespace). |

---

*Plan only — no implementation in this step. Iterate after review.*

---

## Review

**Diff reviewed (Radia, 2026-05-06):** `origin/dev` range **`1c4b5dd6^..18bbf486`** (`feat(ast-351): encoded consult…` + `chore(ast-351): append review stub`). Feature ref was absent in review environment; findings from tree.

**Counts:** fix-now **0** · discuss **2** · advisory **1**

### What’s solid

- Encoded-grade / rubric-reason pipeline in **core** (`consult.py`, `candidate.py`), **`src/utils/rubric_text.py`**, and **`TASK_CONFIG` / `CONSULT_CONFIG`** with UI/API touchpoints — matches ticket (normalized arrays + text, validation on save). **§1.2 / §2.1** layering respected from file list.

### Issues (none blocking code in resolve pass)

| Severity | Topic | Notes |
|----------|--------|--------|
| Discuss | **`CONSULT_CONFIG` / `TASK_CONFIG` churn** | Confirm every consult step that reads grades tolerates the new encoded shape after Susan migrates prompts in DB (ticket note). |
| Discuss | **`api_candidate.py` + `ArtifactEditor.tsx`** | Thin wiring — sanity-check round-trip with encoded payload sizes in **Testing**. |
| Advisory | Large diff across config + core | Focused regression pass on **qualify / evaluate / get / do / like** after DB prompt migration. |

---

## Resolution

**Date:** 2026-05-06 — Betty (`f-resolve-linear`)

- **Radia:** fix-now **0** — no additional code changes in this resolve pass; implementation already landed on **`dev`** (**`1c4b5dd6`**, **`18bbf486`**).
- **Discuss / advisory:** Rolled into **Testing** checklist: DB prompt migration (**Susan**), API/UI round-trip, consult-stage regression pass.
- **Build:** `python3 -m compileall -q src` before this doc commit (no Python edits here).

— Betty
