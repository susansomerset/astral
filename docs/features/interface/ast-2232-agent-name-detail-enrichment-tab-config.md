# AST-2232 — Agent name, detail enrichment, tab config (Updates to recommended job modal)

- **Linear:** [AST-2232](https://linear.app/astralcareermatch/issue/AST-2232) · parent [AST-2226](https://linear.app/astralcareermatch/issue/AST-2226)
- **Publish ref:** `origin/sub/AST-2226/AST-2232-agent-name-detail-enrichment-tab-config`
- **Assignee:** Katherine

Seed `agent_name` on every agent row, wire it through repo-JSON + `get_entity_agent_story`, enrich `GET /api/jobs/<id>` with company identity / website / lifecycle dates / `can_apply`, and move Job Description onto its own config top tab (drop Summary `raw_jd`). Backend and config only — siblings AST-2226 #2 (header) and #3 (modal panes) consume the payload.

## UAT fitness

- **AC restored:** Parent AST-2226 functional scope items this child owns: (6) every agent carries `agent_name`; (7) detail exposes `company_name` and company website for the header; (8) lifecycle dates — discovered = `created_at`, recommended = first `RECOMMENDED` in `state_history`, applied = first `CANDIDATE_APPLIED` or absent; (11) Job Description top tab between Analysis and Summary with `raw_jd` removed from Summary; plus child AC 12 — detail includes server-gated `can_skip` and `can_apply`.
- **Correct outcome:** Discussion consumers can read `agent_name` on story entries; Recommended report detail JSON carries real `company_name` (not short_name alone), `company_website`, lifecycle timestamps, and Applied legality; opening the modal lands on Analysis with Job Description available as its own tab (siblings render chrome/panes).
- **Sibling check:** #2 (header) and #3 (modal panes) still only need presentational/wiring work — field names below are the contract. Verified by leaving React / App.css / JobAnalysisReportModal untouched in Files Changed.
- **Not sufficient:** Removing an exception or returning 200 without the new fields / tab order is not done.
- **Wrong fix rejected:** Deriving header company label from `job.company` / `short_name` alone; putting JD only under Summary; computing `can_apply` in the UI from an ad-hoc state list instead of `job_state_admits_transition(..., "CANDIDATE_APPLIED")`.

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

| File | Kind of change Scope allows |
|------|-----------------------------|
| `data/admin/agent.json` | **modified** — add `agent_name` per seeded agent (both Estelle ids → `Estelle`) |
| `src/utils/config.py` | **modified** — `REPO_ADMIN_JSON_CONFIG` agent columns include `agent_name`; `JOBS_RECOMMENDED_REPORT_TOP_TABS` inserts `job_description` between `analysis` and `summary`; Summary sections drop `raw_jd` |
| `src/data/database.py` | **modified** — agent repo-JSON import/export and agent read/update accept and return `agent_name` |
| `src/core/agent.py` | **modified** — `get_entity_agent_story` attaches `agent_name` from the task's agent row when non-empty (parallel to `task_name`) |
| `src/core/tracker.py` | **modified** — Applied prior-state admission (mirroring Skip via existing `job_state_admits_transition`); helpers for discovered / recommended / applied timestamps |
| `src/ui/api/api_jobs.py` | **modified** — detail adds `company_name`, company website URL, lifecycle dates, `can_apply` (keeps `can_skip`) via `get_company`; no new unauthenticated surface |

Every **Files Changed** row and every Stage step names only those files / that kind of change. No React, no `api_admin.py`, no App.css.

## Canon Scope (id-only at plan)

Ticket Citations: `stat.logging.debug`, `stat.logging.error`, `stat.logging.info.api`.

No **patterns** are cited. Per plan-child §0a / canon-index § Who reads what: statutes stay **id-only** until build-child §8. Builder must expand the three logging statutes before coding call/response `logger.debug` / error paths on new `get_company` and lifecycle helper call sites in `api_jobs.py` / `tracker.py` / `agent.py` when those sites already log peer calls the same way.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent.json` | Add non-empty `agent_name` on every row; each row's keys exactly match updated `REPO_ADMIN_JSON_CONFIG` agent columns | data seed |
| `src/utils/config.py` | Add `agent_name` to agent repo columns; insert `job_description` tab; remove Summary `raw_jd` | utils |
| `src/data/database.py` | Schema ensure + public read/write/export paths for `agent_name` | data |
| `src/core/agent.py` | Attach `agent_name` on story entries when set | core |
| `src/core/tracker.py` | Lifecycle date helpers; Applied admission reused via existing `job_state_admits_transition` | core |
| `src/ui/api/api_jobs.py` | Detail enrichment: company fields, lifecycle dates, `can_apply` | ui |

**Out of scope:** `RecommendedJobReportHeader.tsx`, `App.css`, `JobAnalysisReportModal.tsx`, `JobDiscussionPane.tsx`, `recommendedJobReport.tsx`, `api_admin.py`, `tests/` / bible (Betty).

**Sibling consume contract (#2 / #3 — do not implement here):**

| Field / config | Shape | UI use |
|----------------|-------|--------|
| `agent_story[].agent_name` | optional string | Discussion header `<agent_name>'s <task_name> @ …` |
| `company_name` | string or null | Header label (never short_name alone) |
| `company_website` | string or null | `<a target="_blank">` on its own line under job link |
| `discovered_at` | string or null (= job `created_at`) | Date strip |
| `recommended_at` | string or null | Date strip |
| `applied_at` | string or null | Date strip only when non-null |
| `can_apply` | bool | Applied button legality |
| `can_skip` | bool (already present) | Skip button legality |
| `JOBS_RECOMMENDED_REPORT_TOP_TABS` | analysis → **job_description** → summary → … | Top tabs; first entry remains default (Analysis) |
| Summary sections | no `raw_jd` | JD only on Job Description tab |

---

## Stage 1: Config — agent_name column + Job Description tab

**Done when:** `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` includes `"agent_name"`; `JOBS_RECOMMENDED_REPORT_TOP_TABS` order is analysis, job_description, summary, artifacts, discussion, meteorite; `JOBS_RECOMMENDED_REPORT_SUMMARY_SECTIONS` has no `raw_jd` entry. No seed/DB/API behavior change yet.

1. In `src/utils/config.py`, in `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` (tuple currently ending with `"updated_at"`), insert `"agent_name"` immediately after `"agent_id"` so the tuple begins `("agent_id", "agent_name", "content", …)`. Comment: `# AST-2232: display name for Discussion headers`.
2. In `src/utils/config.py`, replace `JOBS_RECOMMENDED_REPORT_TOP_TABS` with:
   ```python
   JOBS_RECOMMENDED_REPORT_TOP_TABS = [
       {"tab_id": "analysis", "nav_label": "Analysis"},
       {"tab_id": "job_description", "nav_label": "Job Description"},
       {"tab_id": "summary", "nav_label": "Summary"},
       {"tab_id": "artifacts", "nav_label": "Artifacts"},
       {"tab_id": "discussion", "nav_label": "Discussion"},
       {"tab_id": "meteorite", "nav_label": "Meteorite"},
   ]
   ```
   Update the comment above it to include `AST-2232` and note that the first entry remains the default tab.
3. In `src/utils/config.py`, in `JOBS_RECOMMENDED_REPORT_SUMMARY_SECTIONS`, **delete** the entire `{"section_id": "raw_jd", ...}` dict. Leave the other four sections unchanged.
4. Do **not** touch `build_state_ui_manifest()` / `"report_top_tabs"` / `"report_summary_sections"` wiring — they already `list()` these constants.
5. `python3 -m py_compile src/utils/config.py`.
6. Commit: `code(AST-2232): config — agent_name column, Job Description tab, drop raw_jd`. Publish per build-child.

⚠️ **Decision:** `agent_name` sits right after `agent_id` in the columns tuple (identity then display name) rather than at the end — keeps export/import human-readable and matches how `task_name` sits near identity on `agent_task`.

---

## Stage 2: Seed — `agent_name` on every `data/admin/agent.json` row

**Done when:** Every object in `data/admin/agent.json` has a non-empty string `agent_name` per the map below, and `set(row.keys())` equals `set(REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"])` for every row (so `_validate_agent_repo_json_rows` would accept a revert).

1. In `data/admin/agent.json`, for each row set `agent_name` as follows (both Estelle agent_ids share `Estelle`):

   | `agent_id` | `agent_name` |
   |------------|--------------|
   | `job_analyst_grace` | `Grace` |
   | `ats_expert_atlas` | `Atlas` |
   | `content_writer_judith` | `Judith` |
   | `web_scraper_laslo` | `Laslo` |
   | `principal_recruiter_estelle` | `Estelle` |
   | `college_intern_ruth` | `Ruth` |
   | `contact_recruiter_estelle` | `Estelle` |
   | `antagonist_kent` | `Kent` |
   | `fact_checker_marta` | `Marta` |
   | `job_filter_lucy` | `Lucy` |

2. After inserting `agent_name`, rewrite each row so its keys are **exactly** the Stage 1 columns tuple (order may follow the tuple). Today's checked-in rows also carry `brain_setting` and `mode`, which are **not** in `REPO_ADMIN_JSON_CONFIG` agent columns and would fail `_validate_agent_repo_json_rows` on revert — **drop those two keys** from every seed row in this same edit. Do not invent replacement columns for them.
3. Do not change `content`, `model_id`, settings, or `updated_at` values except as required to keep valid JSON.
4. Sanity: `python3 -c` that loads `REPO_ADMIN_JSON_CONFIG` + the file and asserts every row's key set equals the columns set and every `agent_name` is non-empty.
5. Commit: `code(AST-2232): seed agent_name on admin agent.json`. Publish per build-child.

⚠️ **Decision:** Dropping `brain_setting` / `mode` from the seed is required for the columns contract after Stage 1; those keys are already outside REPO_ADMIN columns and are not named in this ticket's Scope as columns to add. If dropping them is blocked by a concurrent ticket, stop and comment on parent AST-2226 — do not add them to `REPO_ADMIN_JSON_CONFIG`.

---

## Stage 3: Database — persist and expose `agent_name`

**Done when:** Fresh and existing DBs have an `agent` column `agent_name TEXT`; `get_agent` / `list_agents` return it; `save_agent` / `update_agent` / repo-JSON apply+export read and write it; header inventory mentions `agent_name`.

1. In `src/data/database.py` module docstring table inventory for `agent`, append `agent_name TEXT` (display string; AST-2232) next to the other agent columns.
2. In `_ensure_agent_schema`, add `("agent_name", "TEXT")` to the `ALTER TABLE agent ADD COLUMN` loop list (same pattern as `model_id` / settings). On the `CREATE TABLE agent` branch (empty DB), include `agent_name TEXT` after `agent_id`.
3. Extend `_AGENT_PUBLIC_COLUMNS` so `agent_name` appears immediately after `agent_id` (mirror Stage 1 column order for the identity pair). Keep settings + `updated_at` as today.
4. In `save_agent`, add optional kw-only `agent_name: Optional[str] = None`. On INSERT, store `"" if agent_name is None else str(agent_name)` (or the stripped string — empty allowed at write time; seed always non-empty). On UPDATE, when `agent_name is not None`, set the column (same None-means-leave-alone rule as `max_tokens`).
5. Add `"agent_name"` to `_UPDATE_AGENT_ALLOWED`.
6. In `list_agents` SQL `SELECT`, include `agent_name` with the other public columns (after `agent_id`).
7. Confirm repo-JSON paths need **no special-case code**: `_agent_repo_json_columns()` already reads `REPO_ADMIN_JSON_CONFIG`, so export/apply/validate pick up `agent_name` once Stage 1 landed. If a hardcoded column list still omits it, fix that list to use `_agent_repo_json_columns()` / `_AGENT_PUBLIC_COLUMNS` rather than inventing a parallel tuple.
8. `python3 -m py_compile src/data/database.py`.
9. Commit: `code(AST-2232): database agent_name column + read/write`. Publish per build-child.

⚠️ **Decision:** `agent_name` is plain TEXT, not an `AGENT_SETTING_COLUMNS` entry — it is display metadata, never sent to the LLM provider. Keep it off `_AGENT_SETTING_TYPES` / settings type checks.

⚠️ **Decision:** `api_admin.py` is **out of Scope**. Admin PUT will not yet accept `agent_name` in the body; `get_agent` still **returns** it once public columns include it. Seed + Revert to file is the write path this ticket owns. Do not edit `api_admin.py`.

---

## Stage 4: Core — story `agent_name` + lifecycle helpers + Applied admission

**Done when:** `get_entity_agent_story` entries include `agent_name` when the task's agent row has a non-empty value; tracker exposes helpers that return discovered / recommended / applied timestamps; `job_state_admits_transition(state, "CANDIDATE_APPLIED")` is the Applied legality query (no duplicate matcher).

1. In `src/core/agent.py` `get_entity_agent_story`, immediately after the existing `task_name` attach block (~lines that call `get_agent_task` and set `entry["task_name"]`), attach `agent_name` the same way:
   - Resolve `agent_id` from `(get_agent_task(task_key) or {}).get("agent_id")` (reuse the task row already fetched for `task_name` — do not call `get_agent_task` twice; bind one `task_row`).
   - `agent_row = get_agent(agent_id) if agent_id else None` — import / use the same `get_agent` already available in this module (or `database.get_agent` if that is the local pattern).
   - `agent_name = ((agent_row or {}).get("agent_name") or "").strip()`
   - If `agent_name`: `entry["agent_name"] = agent_name`
   - Omit the key when blank (parallel to `task_name`).
2. In `src/core/tracker.py`, near `job_state_admits_transition`, add three public helpers (AST-2232):

   ```python
   def job_discovered_at(job: Dict[str, Any]) -> Optional[str]:
       """Date discovered = job.created_at (AST-2232)."""
       value = job.get("created_at")
       if value is None:
           return None
       text = str(value).strip()
       return text or None

   def job_first_state_history_at(job: Dict[str, Any], to_state: str) -> Optional[str]:
       """Timestamp of the first state_history entry whose to_state equals to_state (AST-2232)."""
       target = (to_state or "").strip()
       if not target:
           return None
       for entry in job.get("state_history") or []:
           if not isinstance(entry, dict):
               continue
           if (entry.get("to_state") or "").strip() != target:
               continue
           ts = entry.get("timestamp")
           if ts is None:
               return None
           text = str(ts).strip()
           return text or None
       return None

   def job_recommended_at(job: Dict[str, Any]) -> Optional[str]:
       """First RECOMMENDED timestamp in state_history (AST-2232)."""
       return job_first_state_history_at(job, "RECOMMENDED")

   def job_applied_at(job: Dict[str, Any]) -> Optional[str]:
       """First CANDIDATE_APPLIED timestamp in state_history, or None (AST-2232)."""
       return job_first_state_history_at(job, "CANDIDATE_APPLIED")
   ```

   Place them directly after `job_state_admits_transition`. Import `Optional` / `Dict` / `Any` only if not already imported.
3. Do **not** add a second prior-state matcher. Applied admission is `job_state_admits_transition(current, "CANDIDATE_APPLIED")` — same function Skip already uses (AST-1872). Stage 5 calls it.
4. `python3 -m py_compile src/core/agent.py src/core/tracker.py`.
5. Commit: `code(AST-2232): story agent_name + job lifecycle helpers`. Publish per build-child.

⚠️ **Decision:** Three named helpers plus a shared `job_first_state_history_at` (rather than one opaque dict return) match Scope's "helpers that return discovered / recommended / applied" wording and keep detail wiring one call each.

⚠️ **Decision:** First matching `state_history` entry wins (chronological list order as stored). Do not scan reversed; do not prefer `state_changed_at`.

---

## Stage 5: API — job detail enrichment

**Done when:** `GET /api/jobs/<astral_job_id>` (existing `@require_auth` `detail`) includes `company_name`, `company_website`, `discovered_at`, `recommended_at`, `applied_at`, and `can_apply`, and still includes `can_skip`. No new routes. Missing company → null company fields (never invent from short_name). Never-applied → `applied_at` is JSON `null`.

1. In `src/ui/api/api_jobs.py`, extend the `from src.core.tracker import (...)` block with: `get_company`, `job_applied_at`, `job_discovered_at`, `job_recommended_at` (and keep `job_state_admits_transition`). Use alphabetical order consistent with the existing import list.
2. In `detail()`, immediately after the existing `can_skip` assignment, add:
   ```python
   # AST-2232: Applied legality — same prior-state admission as Skip
   job["can_apply"] = job_state_admits_transition(
       job.get("state") or "", "CANDIDATE_APPLIED"
   )
   ```
3. Still in `detail()`, after `can_apply` (and before artifact hydration is fine), attach company + lifecycle fields:
   ```python
   # AST-2232: company identity + website for Recommended report header (siblings render)
   company_key = (job.get("company_id") or job.get("company") or "").strip()
   company_row = None
   if company_key:
       logger.debug("Calling get_company: [short_name=%s]", company_key)
       company_row = get_company(company_key)
       logger.debug("Response from get_company: %s", company_row)
   job["company_name"] = (
       ((company_row or {}).get("company_name") or "").strip() or None
   )
   job["company_website"] = (
       ((company_row or {}).get("company_website") or "").strip() or None
   )
   job["discovered_at"] = job_discovered_at(job)
   job["recommended_at"] = job_recommended_at(job)
   job["applied_at"] = job_applied_at(job)
   ```
4. Do **not** fall back `company_name` to `company_key` / short_name when the company row is missing or `company_name` is blank — leave JSON `null` (AC: fail = short_name shown as the only company label from this payload).
5. Do **not** add routes, remove `@require_auth`, or change `skip_job` / candidate-action Applied POST handlers.
6. `python3 -m py_compile src/ui/api/api_jobs.py`.
7. Hand sanity (not committed): for a RECOMMENDED job with a company row, detail JSON shows non-null `company_name` distinct from `company_id`, `can_apply` true, `can_skip` true, `discovered_at` equal to `created_at`, and `applied_at` null when never applied. If any assert fails, stop and comment on parent AST-2226.
8. Commit: `code(AST-2232): job detail company, lifecycle dates, can_apply`. Publish per build-child.

⚠️ **Decision (website field name):** Response key is **`company_website`** (company table column), not `website` — matches list/roster vocabulary siblings already know.

⚠️ **Decision (lifecycle field names):** **`discovered_at` / `recommended_at` / `applied_at`** — ISO/DB timestamp strings as stored; React (#2) formats `m/d/yy`. `discovered_at` is an explicit alias of `created_at` so the header strip does not special-case the job column name.

---

## Test fallout (Betty — qa-child; engineer does not touch `tests/`)

- Config tests that pin `JOBS_RECOMMENDED_REPORT_TOP_TABS` / Summary sections / agent repo columns.
- Agent repo-JSON / `get_agent` / story `task_name` suites — extend for `agent_name`.
- Job detail / `can_skip` suites — add `can_apply`, company fields, lifecycle dates.
- Manifest `report_top_tabs` order assertions (Analysis first, then Job Description).

## Execution contract

Binding. Execute steps in order, stages in order. Do not add files outside Files Changed. Do not edit React or `api_admin.py`. When a referenced line, name, or signature has drifted, or Stage 5 step 7 fails, stop and comment on parent AST-2226:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage is one commit on the epic worktree, published to
`origin/sub/AST-2226/AST-2232-agent-name-detail-enrichment-tab-config` before the next stage starts.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

```text
[plan-rubric]
**Ticket:** AST-2232
**Overall:** APPROVED
**Corpus:** 65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91 (tree `canon/` at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `origin/sub/AST-2226/AST-2232-agent-name-detail-enrichment-tab-config` @ `ea17ea6c516b8682c71d7d8eec47678f6c51e4a0`

## Canon scores

stat.logging.debug | A | |
stat.logging.error | A | |
stat.logging.info.api | A | |

## Traceability

AC 8 → Stages 1–4; AC 9 → Stage 5 (`company_name`, `company_website`, `created_at` on payload — header `m/d/yy` / `<a target="_blank">` N/A sibling #2); AC 10 → Stages 4–5 (`discovered_at` / `recommended_at` / `applied_at` — header strip N/A #2); AC 11 → Stage 1 (tab order + drop `raw_jd` — modal default tab / JD pane expanded N/A #3); AC 12 → Stage 5 (`can_apply` + existing `can_skip`). Parent functional items 6–8, 11 (server/config slice) and child Boundaries satisfied; parent AC 9–16 UI chrome/panes explicitly out of scope.

## Findings

**acceptable** — Explicit scope gate, UAT fitness (correct outcome vs symptom-only), sibling contract table, and execution stop comment match parent AST-2226 partition; five ordered stages with one commit each are executable against current `config.py` tab list (no `job_description` yet) and `detail()` already setting `can_skip` via `job_state_admits_transition`.

**acceptable** — Stage 5 `get_company` Calling/Response joints align with existing `detail()` meteorite debug pattern; `get_entity_agent_story` try/except unchanged (warning, not new error handler); GET detail still correctly omits `stat.logging.info.api` progress lines.

**discuss** — Canon Scope carries only the three logging statutes; this plan also edits `REPO_ADMIN_JSON_CONFIG`, `database.py`, and `api_jobs` imports — `astral.config.config-source-of-truth`, `astral.layers.import-direction`, and `astral.standards.in-scope-only` plainly govern but are not on the frozen list (Archie may amend at Discussion; not scored here).

**discuss** — Stage 2 drops `brain_setting` / `mode` from seed rows outside REPO_ADMIN columns; plan documents the revert-validation rationale and stop gate — worth Susan awareness if anything still read those keys from file-only seed.

**discuss** — Stage 5 import list names `get_company` from `tracker` while `api_jobs.py` today imports `get_company` from `src.core.roster`; either delegate is valid — builder should avoid duplicate/conflicting imports.

**Definition fidelity (R6):** Files Changed and stages stay inside ticket `## Scope`; no React/App.css/modal files. Estimate confirm present. Plan Discuss rounds on thread: 0.

context_tokens≈38000
```

## Review

- **Publish ref:** `origin/sub/AST-2226/AST-2232-agent-name-detail-enrichment-tab-config`
- **Tip:** `98cab23162b2477fefd11ad18bbda6653b154de9` (product @ `c54e581bbb8665548e94045354baade04c7e0ea0`)
- **Stages landed:** 1 config · 2 seed · 3 database · 4 story + lifecycle helpers · 5 detail enrichment
