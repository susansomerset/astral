# AST-1550 — Discussion tab config + story task_name

**Linear:** [AST-1550](https://linear.app/astralcareermatch/issue/AST-1550/discussion-tab-config-story-task-name-add-discussion-tab-to-recommended)  
**Parent:** [AST-1541 — Add "Discussion" tab to Recommended Job modal](https://linear.app/astralcareermatch/issue/AST-1541/add-discussion-tab-to-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-1541/AST-1550-discussion-tab-config-story-task-name`

Register **Discussion** on `JOBS_RECOMMENDED_REPORT_TOP_TABS` (immediately after Artifacts), expose an ordered nine-hop Discussion section list (keys + `task_name` labels, all `default_expanded: false`) on the recommended-report UI manifest, and enrich `get_entity_agent_story` entries with `task_name` from the live `agent_task` row. Does **not** own the React Discussion pane (sibling AST-1551 / child #2).

---

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

- `src/utils/config.py` — Discussion top tab + hop-order source
- `src/ui/api/api_system.py` — manifest Discussion sections
- `src/core/agent.py` — `task_name` on story entries

Every **Files Changed** row and every Stage step names only those files / that kind of change. No React, no `api_jobs.py`, no Job Detail Agent Story UI, no artifact generation.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Append Discussion to `JOBS_RECOMMENDED_REPORT_TOP_TABS`; add public hop-order walk from `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"]` via live `agent_task.run_next` | utils |
| `src/ui/api/api_system.py` | On `GET /api/state_ui_manifest`, attach `jobs.recommended.report_discussion_sections` (nine section defs from the walk + `task_name` / `task_key` labels, `default_expanded: false`) | ui |
| `src/core/agent.py` | In `get_entity_agent_story`, attach `task_name` from the current `agent_task` row when non-empty | core |

**Out of scope:** `JobAnalysisReportModal.tsx` / `JobDiscussionPane.tsx` / `App.css` / `AgentStoryTab.tsx` (sibling #2); Job Detail / Company Detail Agent Story behavior; artifact generation; Analysis / Summary bodies; `tests/` / bible (Betty).

**Sibling consume contract (AST-1551 — do not implement here):**

| Manifest / API field | Shape | UI use |
|----------------------|-------|--------|
| `jobs.recommended.report_top_tabs` | includes `{tab_id: "discussion", nav_label: "Discussion"}` after Artifacts | top-tab chrome (already driven by `report_top_tabs`) |
| `jobs.recommended.report_discussion_sections` | `[{section_id, nav_label, default_expanded}, …]` length 9 | Discussion pane section list |
| `agent_story[].task_name` | optional string | header label when present; else `task_key` |

---

## Stage 1: Config — Discussion top tab + hop-order walk

**Done when:** `JOBS_RECOMMENDED_REPORT_TOP_TABS` ends with Summary → Analysis → Artifacts → **Discussion**; a public config helper returns the live BUILD_ARTIFACTS daisy-chain task_keys starting at `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"]` (`contemplate_job`) and ending when `run_next` is empty (today: nine keys through `propose_application_responses`). No API or story behavior change yet.

1. In `src/utils/config.py`, immediately after the existing Artifacts entry in `JOBS_RECOMMENDED_REPORT_TOP_TABS`, append:

   ```python
   {"tab_id": "discussion", "nav_label": "Discussion"},
   ```

   Do **not** reorder Summary / Analysis / Artifacts. Comment the block as AST-1550 (Discussion after Artifacts).

2. In `src/utils/config.py`, near the other BUILD_ARTIFACTS / `resume_artifact_chain` helpers (after `is_build_artifacts_in_progress` / the `_rac` assert block is fine — same concern area), add a **public** function:

   ```python
   def build_artifacts_discussion_hop_task_keys() -> list[str]:
       """Live run_next walk for Recommended Job Report Discussion sections (AST-1550).

       Starts at BUILD_CONFIG['resume_artifact_chain']['first_task_key'] (contemplate_job).
       Follows current agent_task.run_next until empty. Cycle → RuntimeError.
       Does not include anticipate_scan (not on this chain).
       """
   ```

   Implementation rules (literal):

   - Late-import `get_agent_task` from `src.data.database` inside the function (same pattern as `_agent_task_parents_with_run_next` — utils must not import data at module load).
   - `start = (BUILD_CONFIG.get("resume_artifact_chain") or {}).get("first_task_key")` stripped; if empty, return `[]`.
   - Walk: append key → read `(get_agent_task(key) or {}).get("run_next")` stripped → next key; stop when next is empty.
   - If a key repeats, `raise RuntimeError(f"build_artifacts discussion run_next cycle at {key!r}")` (same discipline as `_walk_requested_artifacts_chain_task_keys` in `candidate.py`).
   - Do **not** hardcode the nine task_key strings in a list. Do **not** add a parallel `hop_task_keys` array under `BUILD_CONFIG["resume_artifact_chain"]` (that list was retired; membership is live `run_next`).

⚠️ **Decision:** Walk from `first_task_key` via live `run_next` rather than a static nine-key list — satisfies `astral.standards.no-hardcoded-sets` / parent Technical scope. Starting at `resume_artifact_chain.first_task_key` excludes `anticipate_scan` without naming it. Terminal is empty `run_next` (today `propose_application_responses`); do not special-case that key unless the walk would otherwise continue past it.

---

## Stage 2: api_system — attach Discussion section defs on the recommended manifest

**Done when:** `GET /api/state_ui_manifest` includes `jobs.recommended.report_discussion_sections` as an ordered list of nine `{section_id, nav_label, default_expanded: false}` objects where `section_id` is the hop `task_key` and `nav_label` is that hop’s `agent_task.task_name` when non-empty, else `task_key`. Walk/DB failure degrades to `[]` with a warning (rest of manifest still 200). Discussion already appears in `report_top_tabs` via Stage 1’s `list(JOBS_RECOMMENDED_REPORT_TOP_TABS)` inside `build_state_ui_manifest()` — do not duplicate the top-tab entry here.

1. In `src/ui/api/api_system.py`, import `build_artifacts_discussion_hop_task_keys` from `src.utils.config` (add to the existing config import block).

2. Import `get_agent_task` from `src.data.database` (UI → data is allowed; `api_admin` already uses it). Prefer a top-level import next to other data/core imports, or a late import inside the try block if that keeps the module header cleaner — either is fine; pick one and stay consistent with nearby code in this file.

3. In `state_ui_manifest()`, after `manifest = build_state_ui_manifest()` and **before** `return jsonify(manifest)`, attach Discussion sections. Mirror the AST-1253 soft-fail pattern used for `artifacts_chain_*` on the same endpoint:

   ```python
   try:
       sections = []
       for task_key in build_artifacts_discussion_hop_task_keys():
           row = get_agent_task(task_key) or {}
           name = (row.get("task_name") or "").strip()
           sections.append({
               "section_id": task_key,
               "nav_label": name or task_key,
               "default_expanded": False,
           })
       manifest.setdefault("jobs", {}).setdefault("recommended", {})[
           "report_discussion_sections"
       ] = sections
   except Exception as exc:
       _log.warning("discussion sections manifest walk failed: %s", exc)
       manifest.setdefault("jobs", {}).setdefault("recommended", {})[
           "report_discussion_sections"
       ] = []
   ```

4. Do **not** put `report_discussion_sections` inside `build_state_ui_manifest()` in config — ticket Scope assigns manifest Discussion sections to `api_system.py` (live `task_name` at request time, same reason AST-1253 enriches outside the pure config builder).

5. Do **not** change frontend TypeScript types in this ticket (sibling #2 / Katherine). Backend key name is exactly `report_discussion_sections`.

⚠️ **Decision:** Soft-fail to `[]` on walk failure so a broken `agent_task` chain cannot 500 the whole state-UI manifest (matches AST-1253). Healthy DB today yields exactly nine sections; Betty owns asserting that count.

---

## Stage 3: agent — `task_name` on `get_entity_agent_story` entries

**Done when:** Each enriched story entry from `get_entity_agent_story` includes `task_name` when the current `agent_task` row for that entry’s `task_key` has a non-empty `task_name`; when blank/missing, the key is **omitted** (UI falls back to `task_key`). Applies to job / company / candidate stories alike (additive field; Agent Story tabs unchanged). No change to block filtering, scored-task enrichment, or soft-fail behavior.

1. In `src/core/agent.py`, inside `get_entity_agent_story`, in the loop that builds each `entry` (after `task_key = e.get("task_key", "")` is known, and when assembling `entry = {**e, "blocks": blocks}` / before `enriched.append(entry)`):

   - Call `get_agent_task(task_key)` (already imported at module top from `src.data.database`).
   - `name = ((get_agent_task(task_key) or {}).get("task_name") or "").strip()`
   - If `name`: set `entry["task_name"] = name`.
   - If not `name`: do **not** set `task_name` to `""` — omit the key.

2. Prefer a single `get_agent_task` call per entry (reuse the row if you already fetch it for something else in the same iteration — today you do not). Do **not** batch-load all tasks unless an existing helper already does that; N is small (latest-per-task refs).

3. Do **not** change `_filter_response_block`, scored `vector_grades` / `rubric_artifact` attachment, or the soft-fail paths around `list_entity_latest_agent_refs` / `get_agent_data`.

⚠️ **Decision:** Omit empty `task_name` rather than sending `""` — matches parent Technical (“empty → omit / UI falls back to `task_key`”) and keeps payloads clean for siblings that check truthiness.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name`.
- Do not add files, modules, or frontend edits not listed above.
- Ambiguity / drift → comment on **parent** AST-1541 with the Stage blocked template; stop.

---

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1550
**Overall:** APPROVED
**Publish ref:** `sub/AST-1541/AST-1550-discussion-tab-config-story-task-name` @ `6a05e07e893fa93469e42cb0547da4b277711981`

## Traceability
AC1 → Stage 1 (`JOBS_RECOMMENDED_REPORT_TOP_TABS` → `build_state_ui_manifest` `report_top_tabs`); AC2 → Stages 2–3 (`report_discussion_sections` manifest labels + `get_entity_agent_story` `task_name` enrichment). Parent AC2/4–7 N/A — sibling AST-1551 (React pane / RESPONSE bodies).

## Findings

### acceptable — `astral.standards.utils-data-late-import-only` vs in-tree precedent
**Location:** Stage 1 (`build_artifacts_discussion_hop_task_keys` late-imports `get_agent_task` in `config.py`)
**Finding:** Statute text forbids utils→data late-import outside `logging.py`; the same file already uses that pattern in `_agent_task_parents_with_run_next` / `dispatch_chain_row_matches_job`. Parent Component/Technical scope assigns the hop walk to `config.py`; core’s `_current_agent_task_run_next` is not importable from utils.
**Recommendation:** Proceed as planned — matches parent definition and existing config chain helpers. Not a plan defect.

context_tokens≈52000
```

---

## Self-Assessment

**Scope:** `Single-Component` — config top tab + hop walk, api_system Discussion sections, agent story `task_name`; no React pane.

**Conf:** `High` — live `run_next` walk mirrors AST-1253; nine hops verified against DB; additive `task_name` field.

**Risk:** `Low` — soft-fail empty sections if walk fails; empty `task_name` omitted (UI falls back to `task_key`).

---

## Review

**Built:** `origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name` @ `7b103e5a6be93581bff8a1d6f69d2df77281d497`

Stages 1–3: Discussion on `JOBS_RECOMMENDED_REPORT_TOP_TABS`; `build_artifacts_discussion_hop_task_keys`; `report_discussion_sections` on `state_ui_manifest`; `task_name` on `get_entity_agent_story`. Tests deferred to Betty.
