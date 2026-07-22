<!-- linear-archive: AST-726 archived 2026-07-22 -->

## Linear archive (AST-726)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-726/latest-only-rubric-writes-and-modal-dedup-store-only-the-latest-rubric  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-717 — Store only the latest rubric results in <entity>_data  
**Blocked by / blocks / related:** parent: AST-717; blocks: AST-727

### Description

## What this implements

When rubric-backed consult or prefilter steps rerun on a job or company, replace — do not accumulate — that phase's outcome on the entity data blob (grades, score, notes). Keep one latest `agent_responses` entry per `task_key` so entity modals show a single tab per consult phase. Preserve full per-run history in `agent_data`.

## Acceptance criteria

* Running the same scored consult phase twice on one job leaves a single current grades payload for that phase on the job's data blob, matching the second run; associated score and notes fields for that phase match the second run only.
* agent_data still contains distinct blocks for both runs after the scenario above.
* The job entity modal shows one navigable result for that consult phase (e.g. one consult_get entry), not multiple tabs for reruns of the same phase.
* Recommended Job Report JD / DO / GET / LIKE tabs display grades from the latest run only.
* Re-running company prefilter replaces prefilter grades/score/notes on company_data without accumulation; the company entity modal shows one current prefilter result.
* Dispatch eligibility that depends on latest consult score reflects the most recent scored run after a rerun.
* No regression: first-time runs still persist outcomes and populate entity modals as they do today.

## Boundaries

* Does not ship the one-time backfill script (sibling ticket).
* Does not change rubric authoring, runtime rubric validation (AST-378), or debug logging (AST-538).

## Notes for planning

* Primary surfaces: consult verdict persistence, roster prefilter saves, `append_agent_response` / `get_entity_agent_story`, job and company entity modals.
* Dedup key for modal navigation: one latest entry per `task_key`.
* Config-driven task keys and grades fields per ASTRAL_CODE_RULES §2.1.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-717-store-only-latest-rubric-results-in-entity-data`, child `sub/AST-717/<child-segment>`.

### Comments

#### radia — 2026-06-18T02:36:47.450Z
### Review vs `origin/dev` (`cfa2ad8`)

**Diff:** `origin/dev...origin/sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup`

**Plan fidelity:** Stages 1–4 delivered — upsert by `task_key`, latest-only rubric fields on job/company blobs, `get_entity_agent_story` dedupe + company `vector_grades`, `prefilter_company` `grades_key`, §2.4.1 rules update. Self-Assessment scope/conf match diff footprint.

**Layer / batch (§3, §2.4, §2.6):** No new cross-layer imports; claim/clear and transition paths unchanged; only post-success entity snapshot writes.

**fix-now:** none.

**discuss:** Write-path upsert appends the replaced ref at array tail — rerunning one scored phase can reorder modal tabs when other keys appeared earlier in the stored array (one entry per key still holds; cosmetic).

**advisory:** `qualify_job_listings` fail path omits `joblist_score` when score is non-numeric (test documents intent); stale score could linger if a job passed joblist then fails on rerun — unlike prefilter which clears via explicit `None`. Legacy `agent_responses` rows with empty `task_key` are skipped by read dedupe; new writes fail loud — **AST-727** backfill scope.

**Doc:** `docs/features/roster/ast-726-latest-only-rubric-writes-and-modal-dedup.md` § Radia review.

**Handoff:** Hedy → **resolve-child** (no code changes required unless Susan wants tab-order stability or joblist fail score clear in this epic).

#### betty — 2026-06-18T02:33:11.348Z
## QA test manifest (AST-726)

**Publish:** `origin/sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup` @ `53a4547` (`merge-tests(AST-726): origin/tests 581eac3`)

**Existing coverage reused:** `TestEntityAgentStory`, `TestRenderVerdict` (notes path), AST-507 prefilter score regressions — extended, not replaced.

**New / revised tests:**

1. **Entity ref upsert** — `tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert`
2. **Consult latest-only job blob fields** — `tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes`
3. **Roster story dedup + company vector_grades + prefilter score clear** — `tests/component/core/test_roster.py::TestAst726LatestOnlyRosterStory`
4. **Config `grades_key`** — `tests/component/utils/test_config.py::TestAst726PrefilterGradesKey`

**Narrowed run (test-child pass criterion — pytest green, not zero-arg harness / branch-lock gate):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes \
  tests/component/core/test_roster.py::TestAst726LatestOnlyRosterStory \
  tests/component/utils/test_config.py::TestAst726PrefilterGradesKey \
  -q
```

**Bible shasums (`origin/sub/...`):**
- `docs/test-bible/core/consult.md`: `16f3950e184ae7c391b8f269655f0a04eb71e934fdb919fb7950642609da9b70`
- `docs/test-bible/core/roster.md`: `d6790025a5ccc166d251c4d00c29fc8bbc5db80e99dc397c566cbb32eae34e92`
- `docs/test-bible/data/database/agent_responses.md`: `53c7eb1556fe557f75b50bebe1ce57b5efe1336beeb1f0a664185c3b5ef78e46`
- `docs/test-bible/utils/config.md`: `7fe60ac206228a74c080a8108e8016d13c1974f644e5500e305935d60e313429`

**Notes:** No frontend changes on this ticket — §6c routed-page manifest N/A. Fail-path `qualify_job_listings` omits `joblist_score` when F-grade yields no numeric score (expected). Read-path dedup covers legacy duplicate refs until sibling **AST-727** backfill.

#### hedy — 2026-06-18T02:23:38.803Z
Plan: `docs/features/roster/ast-726-latest-only-rubric-writes-and-modal-dedup.md`

https://github.com/susansomerset/astral/blob/sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup/docs/features/roster/ast-726-latest-only-rubric-writes-and-modal-dedup.md

**Self-assessment**
- **Scope:** Single-Component — data-layer `append_agent_response` upsert, consult/roster rubric outcome saves, and `get_entity_agent_story` dedup; no UI files.
- **Conf:** high — existing merge-replace and config keys are mapped; upsert pattern is straightforward.
- **Risk:** Medium — wrong task_key dedup could hide non-rubric tabs; mitigated by key-scoped replace only.

---

# Latest-only rubric writes and modal dedup (Store only the latest rubric results in `<entity>_data`)

**Linear:** [AST-726](https://linear.app/astralcareermatch/issue/AST-726/latest-only-rubric-writes-and-modal-dedup-store-only-the-latest-rubric-results-in)  
**Parent:** [AST-717](https://linear.app/astralcareermatch/issue/AST-717/store-only-the-latest-rubric-results-in-entity-data) (context only — backfill is **AST-727**)  
**Publish ref:** `sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup`

**Summary:** When a rubric-backed consult or company prefilter step reruns on a job or company, replace — do not accumulate — that phase's outcome on the entity working snapshot (`job_data` / `company_data` grades, score, notes) and keep **one** `agent_responses` ref per `task_key` so entity modals and the Recommended Job Report show a single current result per phase. Full per-run prompt/response blocks stay in `agent_data` (unchanged).

**Out of scope (sibling / parent):** one-time backfill script (**AST-727**); rubric authoring; runtime rubric validation (**AST-378**); debug logging (**AST-538**).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `append_agent_response`: upsert by `task_key` instead of blind append | data |
| `src/core/tracker.py` | Docstring on `append_agent_response` delegate — latest-only semantics | core |
| `src/core/consult.py` | `_apply_render_verdict_decoded_job`: always persist `{prefix}_notes` (clear when empty); audit batch save paths for scored phases | core |
| `src/core/roster.py` | `_apply_prefilter_decoded_company_outcome`: always persist `prefilter_score` / clear score when absent; `get_entity_agent_story`: dedupe by `task_key`, read grades from correct entity blob | core |
| `src/utils/config.py` | `TASK_CONFIG["prefilter_company"]`: add `grades_key: "prefilter_grades"` | utils |
| `docs/ASTRAL_CODE_RULES.md` | §2.4.1: document latest-only upsert on entity `agent_responses` | docs |

**No frontend changes.** `JobDetailModal`, `CompanyDetailModal`, and `JobAnalysisReportModal` consume API payloads; server-side dedup + replace is sufficient.

**No test edits in this ticket** — Betty owns manifest/bible updates in **qa-child**.

---

## Stage 1: Entity `agent_responses` upsert by `task_key`

**Done when:** Calling `append_agent_response` twice for the same `(entity_type, entity_id, task_key)` leaves **one** array element (the second entry), with no duplicate `task_key` values; `agent_data` rows from both runs remain queryable by block id.

1. In `src/data/database.py`, locate **`append_agent_response(entity_type, entity_id, entry)`** (see AST-486 plan reference ~line 3564). Read the current fetch-parse-save loop.

2. Before persisting, read the entity row's parsed `agent_responses` list (default `[]`). Let `new_key = (entry.get("task_key") or "").strip()`. If `new_key` is empty, **raise `ValueError("append_agent_response: entry missing task_key")`** — callers always set `task_key` on `agent_ref` today; fail loud rather than append untagged rows.

3. Build the updated list:
   - Remove every existing element whose `(e.get("task_key") or "").strip() == new_key`.
   - Append `entry` at the **end** (preserves chronological ordering for non-rubric tasks; latest rubric ref is last among its key).

4. Save the entity row with the rebuilt list. Do **not** delete or mutate `agent_data` rows referenced by removed refs.

5. In `src/core/tracker.py`, update the one-line docstring on **`append_agent_response`** to state: *upserts by `task_key` — latest ref wins; full history remains in `agent_data`.*

6. Grep callers — **do not add new call sites**; existing paths are sufficient once data layer upserts:
   - `src/core/agent.py` (~1983) — single-entity `do_task`
   - `src/core/consult.py` `_run_batch_consult` (~1172)
   - `src/core/roster.py` `_run_batch_company_prefilter` (~1621)

⚠️ **Decision:** Upsert lives in **`database.append_agent_response`** (single write path) rather than a parallel `upsert_*` helper — all three core callers already funnel here via `tracker.append_agent_response` or direct import in `agent.py`. **`add_agent_response_entry`** (audit helper in `agent.py` `_store_agent_response`) writes to **`agent_data`** only; leave it unchanged.

---

## Stage 2: Latest-only rubric outcome fields on entity blobs

**Done when:** Re-running a scored consult phase on one job overwrites `{prefix}_grades`, `{prefix}_score`, and `{prefix}_notes` to match the second run only (including clearing notes when the second run has none); re-running company prefilter overwrites `prefilter_grades`, `prefilter_score`, and `prefilter_company_notes`; `latest_score` column reflects the most recent scored transition.

### 2a — Encoded consult DO/GET/LIKE (`_apply_render_verdict_decoded_job`)

1. In `src/core/consult.py`, function **`_apply_render_verdict_decoded_job`** (~794–849), change notes persistence:
   - Today: `if notes_tail: save_data[f"{prefix}_notes"] = notes_tail`
   - Replace with: **`save_data[f"{prefix}_notes"] = notes_tail`** always (empty string when `notes_tail` is falsy) so a rerun without tail text clears stale notes.

2. Leave grades/score writes as-is (`save_data[f"{prefix}_grades"] = grades`; score keys when numeric). `tracker.save_job_data` merge already replaces top-level keys.

3. Confirm **`_transition_job_state_for_task`** still receives the new score on reruns — no change expected; scored reruns must update `job.latest_score` via existing `transition_job_state(..., score=...)`.

### 2b — Batch qualify / evaluate paths

1. **`qualify_job_listings` `process()`** (~1285–1316): after computing `score = _score_from_grades()`, when saving passing/failing rows, add **`joblist_score`** when `_task_config_scored("qualify_job_listings")` and normalized score is not `None` (mirror `evaluate_jd` pattern at ~1419–1422). Use **`_latest_score_value(score)`** before persist.

2. **`evaluate_jd` `process()`** (~1411–1432): already saves `jd_grades` + optional `jd_score` — no structural change. Verify notes are N/A for this phase (no `{prefix}_notes` key today).

3. **`_consult_scored_dispatch_batch_encoded`** already delegates persistence to **`_apply_render_verdict_decoded_job`** — covered by 2a.

### 2c — Company prefilter persistence

1. In `src/core/roster.py`, **`_apply_prefilter_decoded_company_outcome`** (~1256–1326):
   - Today: `prefilter_score` is set only when `verdict_state == cfg["pass_state"] and rubric_list`.
   - Change to **always include `prefilter_score` in `data_to_save`**: when score is computed, set `float(score)`; when not computed on this run, set **`None`** (JSON null) so merge clears a stale score from a prior pass-state run.
   - `prefilter_grades` and `prefilter_company_notes` already overwrite each run — keep; ensure `prefilter_company_notes` is **`""`** when `notes` is empty (not omitted).

2. Do **not** change routing fields (`possible_joblist_links`, `nav_links`, etc.) beyond what this function already writes — scope is rubric outcome keys only.

⚠️ **Decision:** Explicit **`None` / `""` clears** on rerun rather than a one-time backfill — aligns with AC before **AST-727** runs on legacy rows; read-path dedup (Stage 3) covers duplicate `agent_responses` until backfill.

---

## Stage 3: Modal / API story — one entry per `task_key`

**Done when:** `get_entity_agent_story` returns at most one enriched entry per distinct `task_key` (latest `created_at` wins); company prefilter tabs attach `vector_grades` from `company_data.prefilter_grades`; job scored tabs still read from `job_data` via `TASK_CONFIG[task_key].grades_key`.

1. In `src/core/roster.py`, add helper **`_dedupe_agent_responses_latest(entries: list) -> list`** above `get_entity_agent_story`:
   - Input: raw `agent_responses` list from entity column.
   - For each entry, key = `(entry.get("task_key") or "").strip()`; skip entries with empty key.
   - Keep the entry with the **max** `created_at` string per key (`created_at` format today: `"YYYY-MM-DD HH:MM:SS"` — string compare is safe).
   - Return deduped list sorted in **original array order** (first-seen key order among survivors) so unrelated task tabs stay stable.

2. In **`get_entity_agent_story`**, replace `entries = entity.get("agent_responses") or []` with **`entries = _dedupe_agent_responses_latest(entity.get("agent_responses") or [])`**.

3. Fix grades blob selection for scored tasks (~2860–2863):
   - Replace `entity.get("job_data", {})` with:
     ```python
     data_blob = entity.get("job_data") if entity.get("astral_job_id") else entity.get("company_data")
     data_blob = data_blob if isinstance(data_blob, dict) else {}
     ```
   - Set `entry["vector_grades"] = data_blob.get(grades_key) if grades_key else None`.

4. In `src/utils/config.py`, inside **`TASK_CONFIG["prefilter_company"]`**, add **`"grades_key": "prefilter_grades"`** next to `"scored": True` (same pattern as `qualify_job_listings` / `evaluate_jd`).

5. **Do not** change `JobDetailModal.tsx`, `CompanyDetailModal.tsx`, or `JobAnalysisReportModal.tsx` — they already render one side tab per `agent_story` entry; deduped API output satisfies AC.

⚠️ **Decision:** Read-path dedup **plus** write-path upsert — write path fixes new reruns; read path makes modals correct on legacy duplicate rows until **AST-727** backfill runs.

---

## Stage 4: Rules doc + verification gate

**Done when:** `ASTRAL_CODE_RULES.md` §2.4.1 describes upsert semantics; compile check passes on touched modules.

1. In `docs/ASTRAL_CODE_RULES.md` §2.4.1 Entity Agent Responses, change "appends a lightweight reference entry" to **upserts by `task_key` (latest wins)**. Add one sentence: *Historical blocks remain in `agent_data`; only the entity-row ref array is latest-only per phase.*

2. Run **`python -m compileall src/core/consult.py src/core/roster.py src/core/tracker.py src/utils/config.py`** (or project-standard compile gate) — must pass before **Code Complete**.

3. Manual verification checklist (for **test-child** / UAT notes — not automated in this ticket):
   - Run same scored consult phase twice on one job → one `consult_get` (or equivalent) tab in job modal; `job_data.get_grades` match second run; two distinct RESPONSE blocks still in `agent_data`.
   - Recommended Job Report JD/DO/GET/LIKE tabs show second-run grade dots only.
   - Re-run company prefilter → one `prefilter_company` tab; `prefilter_grades` / notes match second run.
   - Dispatch claim with `score_floor` after rerun uses updated `latest_score`.

---

## Execution contract

Binding per **plan-child**: execute stages **1 → 2 → 3 → 4** in order; **one commit per stage** on epic worktree during **build-child**, then publish each commit to **`origin/sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup`**. Do not implement **AST-727** backfill. Do not edit `tests/` or `docs/test-bible/**`. On ambiguity — **`🛑 Stage N blocked`** comment on **AST-717** parent per plan-child format; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — touches data persistence (`append_agent_response`), consult/roster verdict save paths, and roster entity-story shaping; no UI files.

**Conf:** `high` — upsert + merge-replace patterns exist; callers and config keys are enumerated in codebase today.

**Risk:** `Medium` — incorrect upsert could drop non-rubric agent story tabs if `task_key` dedup is too aggressive; mitigated by deduping only matching keys and preserving unrelated entries.

---

## Self-review against ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single upsert in `database.append_agent_response`; shared `_dedupe_agent_responses_latest` for read path; consult prefilter reuse existing save helpers. |
| §2.1 config | `grades_key` added on `prefilter_company`; scored phase keys remain in existing `TASK_CONFIG` entries. |
| §2.4 batch | Batch claim/clear unchanged; only post-success entity snapshot writes change. |
| §2.6 state machine | Transitions unchanged; `latest_score` still via `transition_job_state`. |
| §3.3 imports | No new cross-layer imports; data layer change consumed through existing tracker/agent paths. |
| §3.5 naming | Keep `append_agent_response` name (behavior change documented) — avoids churn across core call sites. |

No unresolved conflicts.

---

## Review

**Branch:** `origin/sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup`  
**Diff baseline:** `origin/dev`  
**Review tip:** `53a4547`

**Built:** Stages 1–4 — `append_agent_response` upsert by `task_key`; latest-only rubric outcome fields on job/company blobs; `get_entity_agent_story` dedupe + company `vector_grades`; `prefilter_company` `grades_key`; §2.4.1 rules update.

### Radia review (AST-726)

| | |
|---|---|
| **What's solid** | Plan stages 1–4 match diff: `database.append_agent_response` upsert + `ValueError` on missing `task_key`; consult notes always persisted (empty clears stale); `qualify_job_listings` `joblist_score` on scored pass; prefilter `prefilter_score`/`prefilter_company_notes` always written (`None`/`""` clears); `_dedupe_agent_responses_latest` + company `vector_grades` from `company_data`; `grades_key` on `prefilter_company`; §2.4.1 rules updated. Layer/batch rules clean — no new cross-layer imports; transitions unchanged. Betty manifest covers upsert, dedupe, notes clear, prefilter score clear. |
| **Issues** | None **fix-now**. |
| **Discuss** | Write-path upsert appends replaced `task_key` at array tail — rerunning one phase can reorder modal tabs when other keys were listed earlier (read-path dedupe preserves post-write array order; cosmetic only). |
| **Advisory** | `qualify_job_listings` fail path omits `joblist_score` when score is non-numeric (test documents intent); stale score could linger if a job passed joblist then fails on rerun — prefilter explicitly clears via `None`; align in a follow-up only if UAT shows confusion. Legacy `agent_responses` rows with empty `task_key` are skipped by dedupe (new writes fail loud); **AST-727** backfill scope. |
| **Recommended actions** | Hedy: **resolve-child** — no code changes required unless Susan wants tab-order stability or joblist fail score clear in this epic. |

---

## Resolution

**Date:** 2026-06-18  
**Resolved by:** Hedy (resolve-child)

Radia posted **no fix-now** items. Discuss (upsert tail-append tab reorder) and advisory (`qualify_job_listings` fail-path score clear, legacy empty `task_key` rows) accepted as documented — out of scope for this ticket; **AST-727** owns legacy backfill.

**§9a dry-run:** `origin/sub/AST-717/AST-726-latest-only-rubric-writes-and-modal-dedup` @ `cfa2ad8` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-717-store-only-latest-rubric-results-in-entity-data`**.

**Product changes in resolve:** none — review clean.
