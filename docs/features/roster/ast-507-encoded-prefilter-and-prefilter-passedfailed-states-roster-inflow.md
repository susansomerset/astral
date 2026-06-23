<!-- linear-archive: AST-507 archived 2026-06-15 -->

## Linear archive (AST-507)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-507/encoded-prefilter-and-prefilter-passedfailed-states-roster-inflow  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-490 — Roster inflow  
**Blocked by / blocks / related:** parent: AST-490; blocks: AST-508

### Description

## What this implements

Phase 3 of roster inflow: update **prefilter_company** to **encoded rubric** output (token-efficient); **dealbreaker F → PREFILTER_FAILED**; all else → **PREFILTER_PASSED** with persisted rubric score. Add **PREFILTER_PASSED** / **PREFILTER_FAILED** company states and config transitions.

## Acceptance criteria

8. Phase 3 prefilter uses encoded rubric output; dealbreaker F → **PREFILTER_FAILED**; otherwise → **PREFILTER_PASSED** with rubric score stored — regardless of non-dealbreaker grades.

## Boundaries

* Phase 4 locate dispatch integration — sibling Hedy ticket.
* Does not change **IMPORTED** / legacy **WEBSITE_FOUND → TO_WATCH** path for manual imports unless definition requires shared prefilter task only.
* Requires **craft_company_prefilter** artifact on candidate.

## Notes for planning

* Follow existing `grades_encoded` output_type pattern (qualify_job_listings class).
* [roster.py](<http://roster.py>) prefilter pass logic: dealbreaker-only F failure.
* Flag Susan if plan needs new columns.

## Git branch (authoritative)

`sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states`

### Comments

#### radia — 2026-05-28T00:03:49.004Z
**Review** — `origin/dev`…`origin/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states` · code `19f97fe6` · doc `06531e7b`

Plan doc: `docs/features/roster/ast-507-encoded-prefilter-and-prefilter-passedfailed-states-roster-inflow.md` (## Review)

**Solid (§2.1 / §2.6 / AC #8)**
- `grades_encoded` + `_flatten_prefilter_parsed`; dealbreaker F2+ via `_render_pass_fail`; `prefilter_score` on pass via `_render_score`.
- **PREFILTER_PASSED** / **PREFILTER_FAILED** states + transitions; legacy **TO_WATCH** / **IGNORE** via `state_history` (**NEW → WEBSITE_FOUND**).
- `decision` treats **PREFILTER_PASSED** like **TO_WATCH** for culture-link save; shape/score errors → **PREFILTER_UNKNOWN**.

**Advisory only (no fix-now)**
- Publish ref includes sibling bible §7.13zf–7.13zg and `TestAst504CompanySearchTermsConfig` — narrow future child publishes when possible.
- `_fetch_prefilter_notes` uses empty `vector_labels` (no ctx); fine with current mocks; revisit if live decode requires rubric labels on coat-check.

Ada: no code changes requested — proceed toward UAT on parent branch when siblings allow.

#### betty — 2026-05-27T23:55:39.859Z
**Publish ref:** `origin/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states` @ `a76cde78`

**`docs/ASTRAL_TEST_BIBLE.md` SHA256 (on publish ref):** `8ee520f59faeb11b3722b180be2780c58209c46bf1c6f29656091c28159b28a6`

**QA test manifest**

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig tests/component/core/test_roster.py::TestPrefilterCompany::test_pass_and_fail_grades_persist_data tests/component/core/test_roster.py::TestAst507EncodedPrefilter tests/component/core/test_roster.py::TestRunCompanyTask::test_prefilter_pass_and_fail`

**Coverage notes (§7.13zh):** Encoded `jobs[0].grades` shape; dealbreaker **F** with confidence ≥ 2 → **PREFILTER_FAILED** on inflow (`NEW → WEBSITE_FOUND` history); legacy empty history → **TO_WATCH** / **IGNORE**; **F1** on one vector with another vector confidence > 1 → pass (not dealbreaker); **`prefilter_score`** on legacy pass path; **`run_company_task`** counts **PREFILTER_PASSED** in `pass_states`.

**Prerequisite:** **`craft_company_prefilter`** on candidate before dispatch (per plan).

#### ada — 2026-05-27T23:42:24.509Z
Plan doc: [ast-507-encoded-prefilter-and-prefilter-passedfailed-states-roster-inflow.md](https://github.com/susansomerset/astral/blob/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states/docs/features/roster/ast-507-encoded-prefilter-and-prefilter-passedfailed-states-roster-inflow.md) (`dec0d7ac` on `origin/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states`).

**Scope:** `scope-Single-Component` — config state registry + `prefilter_company` / `run_company_task` in `roster.py` and targeted tests only.

**Conf:** `conf-Medium` — `grades_encoded` decode returns `jobs[0]`; roster adapter + `state_history` inflow vs legacy split must match parent AC without absorbing **AST-508** locate work.

**Risk:** `risk-Medium` — shared prefilter on **WEBSITE_FOUND**; wrong branch sends manual roster to **PREFILTER_*** or inflow to **TO_WATCH**; dealbreaker regression affects downstream spend.

**Susan flag (no new column this ticket):** Rubric score → `company_data.prefilter_score`. SQL `score_floor` on company batch claim (**AST-508**) may need `company.latest_score` — approve separately if required.

---

# Encoded prefilter and PREFILTER PASSED/FAILED states (Roster inflow)

**Linear:** [AST-507](https://linear.app/astralcareermatch/issue/AST-507/encoded-prefilter-and-prefilter-passedfailed-states-roster-inflow)  
**Parent:** [AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow) (context only — do not implement sibling phases here)  
**Publish ref:** `sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states`  
**Summary:** Switch `prefilter_company` to compact **grades_encoded** output, grade with **dealbreaker-only** `F` (confidence ≥ 2), persist a **0–10 rubric score**, and route inflow companies to **PREFILTER_PASSED** / **PREFILTER_FAILED** while keeping the manual **WEBSITE_FOUND → TO_WATCH / IGNORE** path via an explicit state-history branch.

**Depends on:** **AST-506** (companies reach **WEBSITE_FOUND** from inflow). **craft_company_prefilter** artifact must exist on the candidate before dispatch runs.

**Out of scope (sibling tickets):** Phase 4 locate/parse dispatch (**AST-508**), discovery ingest (**AST-505**), website resolution (**AST-506**), new company **NEW** ingest columns, admin UI for inflow states.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `PREFILTER_PASSED` / `PREFILTER_FAILED` in `COMPANY_STATES`; transitions; `TASK_CONFIG["prefilter_company"]` encoded + scored orch; `ROSTER_CONFIG["prefilter"]` inflow vs legacy state keys | utils |
| `src/core/roster.py` | `prefilter_company` encoded decode adapter, dealbreaker pass/fail, score persist, inflow vs legacy state mapping; `run_company_task` pass_states; `_fetch_prefilter_notes` parity | core |
| `src/core/consult.py` | *(read-only import)* `_render_pass_fail`, `_render_score`, `_rubric_criteria_from_cd` | core |
| `tests/component/core/test_roster.py` | Prefilter pass/fail/score/encoded-shape tests | tests |
| `tests/component/utils/test_config.py` | Assert new company states and transitions present | tests |

**No new DB columns in this ticket.** Rubric score is stored in `company_data.prefilter_score` (float). If **AST-508** needs SQL `score_floor` on company batch claim, Susan must approve a follow-up column (e.g. `company.latest_score`) — flag in Linear comment when plan is posted.

---

## Stage 1: Config — states, transitions, task encoding

**Done when:** `COMPANY_STATES` includes **PREFILTER_PASSED** and **PREFILTER_FAILED**; `ASTRAL_CONFIG["company_state_transitions"]` allows **WEBSITE_FOUND → PREFILTER_PASSED|FAILED** (and existing **PREFILTER_UNKNOWN**); `TASK_CONFIG["prefilter_company"]` uses **grades_encoded** + scored orchestration; `ROSTER_CONFIG["prefilter"]` names inflow and legacy target states.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, add:
   - `"PREFILTER_PASSED": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}}` — same batch shape as **WEBSITE_FOUND** / **TO_WATCH** today so dispatch can claim passed companies later (**AST-508** wires `find_job_page` trigger).
   - `"PREFILTER_FAILED": {}` — terminal for inflow rejects (no batch criteria).

2. In `ASTRAL_CONFIG["company_state_transitions"]`, append (do not remove existing tuples):
   - `("WEBSITE_FOUND", "PREFILTER_PASSED")`
   - `("WEBSITE_FOUND", "PREFILTER_FAILED")`
   Keep `("WEBSITE_FOUND", "TO_WATCH")`, `("WEBSITE_FOUND", "IGNORE")`, `("WEBSITE_FOUND", "PREFILTER_UNKNOWN")` for legacy manual path.

3. In `TASK_CONFIG["prefilter_company"]`:
   - Set `"response_format": "json"` (unchanged envelope).
   - Set `"output_type": "grades_encoded"`.
   - Set `"scored": True`, `"rubric_artifact": "company_prefilter"`, `"pass_threshold": 0.0` (no numeric pass/fail threshold at prefilter — dealbreaker logic only; score is informational for **AST-508** `score_floor`).
   - Set `"pass_state": "PREFILTER_PASSED"`, `"fail_state": "PREFILTER_FAILED"` (used by `_render_pass_fail` / `_render_score` from `consult.py`).
   - Remove `"grading_mode": "binary"` (superseded by consult renderers).
   - Replace `response_schema` with decode-aligned shape:
     ```python
     "response_schema": {
         "jobs": {
             "type": "list", "required": True,
             "items_schema": {
                 "grades": {
                     "type": "list", "required": True,
                     "items_schema": {
                         "vector": {"type": "str", "required": True},
                         "grade": {"type": "str", "required": True},
                         "confidence": {"type": "int", "required": True},
                     },
                 },
                 "possible_job_links": {"type": "list", "required": False},
                 "culture_links_to_explore": {"type": "list", "required": False},
             },
         },
     }
     ```
     ⚠️ **Decision:** `_decode_payload` for `grades_encoded` always returns `{"jobs": [{"grades": [...]}]}` (see `agent.py`). Schema matches post-decode validation; roster flattens `jobs[0]` in Stage 2. **possible_job_links** / **culture_links_to_explore** are optional — encoded lines may omit them; roster defaults to `[]` when absent (legacy **TO_WATCH** locate still works when present).

4. In `ROSTER_CONFIG["prefilter"]`, set inflow targets and legacy aliases:
   - `"pass_state": "PREFILTER_PASSED"`
   - `"fail_state": "PREFILTER_FAILED"`
   - `"pass_states": ["PREFILTER_PASSED", "TO_WATCH"]` — `run_company_task` counts inflow pass and legacy pass as success.
   - `"legacy_pass_state": "TO_WATCH"`
   - `"legacy_fail_state": "IGNORE"`
   - `"legacy_pass_states": ["TO_WATCH"]` — optional mirror for tests/docs.
   Keep `"input_state": "WEBSITE_FOUND"`, `"unknown_state"`, `"error_state"` unchanged.

5. Do **not** change `dispatch_tasks` seed row for `"prefilter"` in this ticket (still `trigger_state: WEBSITE_FOUND`). **AST-508** adds **PREFILTER_PASSED** locate rows.

---

## Stage 2: Core — `prefilter_company` encoded grades, dealbreaker, score, dual state targets

**Done when:** `prefilter_company` calls `do_task` with `batch_entities` + `vector_labels`, decodes grades via encoded pipeline, fails only on dealbreaker `F` (confidence ≥ 2), stores `prefilter_score` on pass, and maps to **PREFILTER_*** or **TO_WATCH/IGNORE** based on inflow history.

1. At top of `src/core/roster.py`, add imports from `src/core/consult`:
   - `_render_pass_fail`
   - `_render_score`
   - `_rubric_criteria_from_cd`

2. Add helper `_vector_labels_from_ctx(ctx: Optional[Dict]) -> Dict[str, str]` in `roster.py` (inline, ~8 lines):
   - `cd = (ctx or {}).get("candidate_data") or {}`
   - `criteria = _rubric_criteria_from_cd(cd, "company_prefilter")`
   - Return `{item["code"]: item["label"] for item in criteria if item.get("code") and item.get("label")}`.

3. Add helper `_flatten_prefilter_parsed(parsed: Any) -> Dict[str, Any]`:
   - If `parsed` is dict with `"jobs"` list and `jobs[0]` is dict, return `jobs[0]`.
   - If `parsed` is dict with `"grades"` list at top level (test mocks / legacy), return `parsed`.
   - Raise `ValueError("prefilter_company: unrecognised parsed_response shape")`.

4. Add helper `_company_used_inflow_prefilter(short_name: str) -> bool`:
   - `company = get_company(short_name)`; if missing, return `False`.
   - Walk `company.get("state_history") or []` **newest-first**; return `True` on first entry where `to_state == "WEBSITE_FOUND"` and `from_state == "NEW"`.
   - If no such entry, return `False` (manual / legacy **IMPORTED** path → legacy states).

5. In `prefilter_company`, before `do_task`, build `task_ctx`:
   ```python
   task_ctx = {
       **(ctx or {}),
       "batch_entities": [{"astral_job_id": short_name}],
       "batch_size": 1,
       "vector_labels": _vector_labels_from_ctx(ctx),
   }
   ```
   Pass `ctx=task_ctx` into `do_task(...)`.

6. Replace Step 4 pass/fail block (lines ~436–444 today) with:
   - `flat = _flatten_prefilter_parsed(api_result.get("parsed_response"))`
   - `grades = flat.get("grades") or []`
   - `rubric_list = _rubric_criteria_from_cd((ctx or {}).get("candidate_data") or {}, "company_prefilter")`
   - `verdict_state = _render_pass_fail("prefilter_company", grades)` → **PREFILTER_PASSED** or **PREFILTER_FAILED**
   - If `_company_used_inflow_prefilter(short_name)`: `new_state = verdict_state`
   - Else (legacy): `new_state = ROSTER_CONFIG["prefilter"]["legacy_pass_state"]` if `verdict_state == cfg["pass_state"]` else `ROSTER_CONFIG["prefilter"]["legacy_fail_state"]`
   - `decision = "TO_WATCH"` when `new_state` in (`TO_WATCH`, `PREFILTER_PASSED`); else `"IGNORE"` (keep existing `decision` semantics for downstream culture-link save guard).

7. Score persistence (pass path only, after verdict is pass):
   - If `verdict_state == cfg["pass_state"]` and `rubric_list`:
     - `_, score = _render_score("prefilter_company", grades, rubric_list, pass_threshold=0.0)`
     - Add to `data_to_save`: `"prefilter_score": float(score)` (score may be `0.0`; still store).
   - On `_render_score` `ValueError`, treat like agent failure → `PREFILTER_UNKNOWN` (same as missing parsed_response).

8. Notes string: keep `" | ".join(...)` from grades **only when** `g.get("reason")` is truthy; encoded grades may lack `reason` until hydration — if all reasons empty, set `prefilter_company_notes` to `""` (do not fabricate).

9. `possible_job_links` / `culture_links_to_explore`: read from `flat` with `.get(..., [])`; persist as today when non-empty; culture links only when `decision == "TO_WATCH"` (unchanged guard — legacy path).

10. In `run_company_task`, for `input_state == "WEBSITE_FOUND"`: keep calling `prefilter_company`; success when `result.get("state") in ROSTER_CONFIG["prefilter"]["pass_states"]` (**PREFILTER_PASSED** or legacy **TO_WATCH**).

---

## Stage 3: Coat-check handler and tests

**Done when:** `_fetch_prefilter_notes` uses the same ctx/body as `prefilter_company`; component tests cover dealbreaker-only F, encoded `jobs[0]` shape, inflow vs legacy states, and config keys.

1. In `_fetch_prefilter_notes` (`roster.py` ~1059+), mirror Stage 2 `task_ctx` (batch_entities, vector_labels) on the `do_task` call; reuse `_flatten_prefilter_parsed` for grades extraction.

2. In `tests/component/utils/test_config.py`, add assertions:
   - `"PREFILTER_PASSED"` and `"PREFILTER_FAILED"` in `COMPANY_STATES`.
   - `("WEBSITE_FOUND", "PREFILTER_PASSED")` and `("WEBSITE_FOUND", "PREFILTER_FAILED")` in `ASTRAL_CONFIG["company_state_transitions"]`.
   - `TASK_CONFIG["prefilter_company"]["output_type"] == "grades_encoded"`.

3. In `tests/component/core/test_roster.py`, update `test_pass_and_fail_grades_persist_data`:
   - Mock `parsed_response` as encoded decode shape: `{"jobs": [{"grades": [{"grade": "F", "vector": "fit", "confidence": 2, "reason": "nope"}]}]}` for fail (dealbreaker).
   - Pass case: `confidence: 5`, grade `A`; mock `get_company` state_history with `from_state: NEW`, `to_state: WEBSITE_FOUND` for inflow branch → expect **PREFILTER_PASSED** and `prefilter_score` in `save_company_data` call.
   - Add test: grade `F` with `confidence: 1` (F1 / no-signal) → **PREFILTER_PASSED** (not fail).
   - Add test: same pass grades, empty state_history → **TO_WATCH** (legacy).

4. Run before publish (build-astral gate):
   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_roster.py \
     tests/component/utils/test_config.py
   ```

---

## Self-Assessment

**Scope:** `Single-Component` — Touches `config.py` state registry, one task config entry, and the `prefilter_company` / `run_company_task` path in `roster.py` plus focused tests; no dispatcher or UI work.

**Conf:** `Medium` — Reusing `grades_encoded` + consult renderers is established, but adapting `jobs[0]` decode output to roster persistence and splitting inflow vs legacy states via `state_history` needs careful execution; prompt/DB task rows may still describe JSON grades until Susan refreshes Manage Tasks copy.

**Risk:** `Medium` — Wrong inflow detection would send manual companies to **PREFILTER_*** or inflow companies to **TO_WATCH**; dealbreaker regression would over- or under-filter before job locate.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_render_pass_fail` / `_render_score` from `consult.py` instead of duplicating F2+ logic. |
| §2.1 config | States, transitions, task encoding, and roster targets live in `config.py`. |
| §2.4 batch | No change to claim/clear; still uses existing `prefilter` dispatch row. |
| §2.6 state machine | New transitions appended; legacy tuples retained. |
| §3.3 imports | `roster` → `consult` for render helpers only (no `database` import from core). |
| §3.5 naming | States `PREFILTER_PASSED` / `PREFILTER_FAILED` match parent epic AC #8. |

No `conf-!!-NONE` conflicts.

---

## Execution contract (developer)

- Execute stages in order; one commit per stage on `dev-ada`, then cherry-pick to `origin/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states`.
- Requires **craft_company_prefilter** on candidate; if missing, `do_task` token resolution fails — stop and comment on **AST-507** (not parent).
- Do not add **AST-508** locate dispatch or **company.latest_score** column unless Susan approves after reading the plan comment.
- Blocking questions → comment on **AST-507** with 🛑 format from `plan-astral`.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states`  
**Product commits:** `8e10c3f1` (config — PREFILTER states, transitions, encoded `prefilter_company` task), `19f97fe6` (core — encoded decode, dealbreaker pass/fail, score persist, inflow vs legacy routing, coat-check parity)

## Review

**Reviewer:** Radia · **Diff:** `origin/dev`…`origin/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states` · **Code tip:** `19f97fe6` · **Doc commit:** (this section)

### What's solid

- **Plan fidelity (AC #8):** `prefilter_company` uses `grades_encoded` decode shape (`jobs[0].grades`), dealbreaker-only **F** with confidence ≥ 2 via shared `_render_pass_fail`, and persists **`prefilter_score`** on pass via `_render_score` — non-dealbreaker grades do not fail the company.
- **§2.1 / §2.6 config:** `PREFILTER_PASSED` / `PREFILTER_FAILED` in `COMPANY_STATES`, transitions appended without removing legacy **TO_WATCH** / **IGNORE** / **PREFILTER_UNKNOWN** tuples; `ROSTER_CONFIG["prefilter"]` dual targets with `pass_states` for `run_company_task`.
- **Inflow vs legacy routing:** `_company_used_inflow_prefilter` (newest-first **NEW → WEBSITE_FOUND** in `state_history`) maps inflow to **PREFILTER_*** and manual path to **TO_WATCH** / **IGNORE**; `decision == "TO_WATCH"` guard correctly includes **PREFILTER_PASSED** so culture links persist on inflow pass.
- **§1.3 DRY:** Reuses consult renderers instead of duplicating F2+ / scored math; shape errors and score `ValueError` route to **PREFILTER_UNKNOWN** like missing parse.
- **Tests:** `TestAst507EncodedPrefilter` covers F2 fail, F1 pass (multi-vector), legacy empty history; config assertions and coat-check mocks updated to encoded envelope.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **advisory** | `tests/component/utils/test_config.py`, `docs/ASTRAL_TEST_BIBLE.md` | Publish ref bundles **AST-504** config tests and bible §7.13zf–7.13zg (siblings **AST-501–504**) alongside §7.13zh. Not AST-507 product scope; harmless if those siblings are already on `origin/dev`, but future publishes should keep child manifests narrow. |
| **advisory** | `src/core/roster.py` `_fetch_prefilter_notes` | Coat-check `do_task` uses `_vector_labels_from_ctx(None)` → empty labels. Dispatch path passes rubric-derived labels. Acceptable today (tests mock API; failures return `None`), but if live encoded prefilter ever requires labels for decode, coat-check should load candidate rubric the same way as `prefilter_company`. |
| **advisory** | `src/core/roster.py` imports | Private consult helpers (`_render_pass_fail`, `_render_score`, `_rubric_criteria_from_cd`) — justified by plan self-review and avoids duplicated grading logic. Consider a small public roster/consult facade later if import surface grows. |

No **fix-now** or **discuss** items on the happy path.

### Recommended actions

| Action | Owner | Notes |
| --- | --- | --- |
| Cherry-pick doc commit onto `dev-ada` and re-publish | Ada | After `resolve-astral` if any discuss items appear on siblings; none required here. |
| Proceed to **resolve-astral** (none) then UAT on parent branch | Ada | No code changes requested from this review. |
| **AST-508** locate dispatch | Hedy | Wire **PREFILTER_PASSED** trigger; `prefilter_score` already persisted for future `score_floor`. |

## Resolution — 2026-05-27

- Radia **`review-astral`**: **advisory** only (publish ref bundles sibling bible §7.13zf–7.13zg; coat-check empty `vector_labels`; private consult imports). **No fix-now** or **discuss** — no product changes in this pass.
- Radia doc commit **`06531e7b`** already on **`dev-ada`** via **`origin/sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states`** attach.
- **§9a** dry-runs vs **`origin/dev`** and **`origin/ftr/AST-490-roster-inflow`** clean before **`User Testing`**.
