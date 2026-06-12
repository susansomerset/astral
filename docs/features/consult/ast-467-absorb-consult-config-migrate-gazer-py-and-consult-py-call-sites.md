# AST-467 — Absorb CONSULT_CONFIG: migrate gazer.py and consult.py call sites

**Parent:** [AST-376](https://linear.app/astralcareermatch/issue/AST-376)  
**Linear:** [AST-467](https://linear.app/astralcareermatch/issue/AST-467/absorb-consult-config-migrate-gazerpy-and-consultpy-call-sites)  
**Publish ref (origin only):** `sub/AST-376/AST-467-absorb-consult-config-migrate-gazer-py-and-consult-py-call-sites`

## Summary

After **AST-466** lands `GAZER_CONFIG` and merges per-task orchestration into `TASK_CONFIG`, this ticket removes all runtime use of `CONSULT_CONFIG` from `gazer.py` and `consult.py`. Gazer reads only `GAZER_CONFIG` for `validate_title` and `scrape_jd` transitions. Consult reads orchestration (pass/fail/error states, thresholds, rubric keys, batch metadata) from `TASK_CONFIG`.

**Dispatch vs orchestration keys:** `qualify_job_listings` and `evaluate_jd` use the **same** string for dispatch and for their `TASK_CONFIG[...]` slice. For **consult** batch work, dispatch and job-level task keys remain `consult_do`, `consult_get`, and `consult_like`, but **orchestration lives under** `TASK_CONFIG["grade_do"]`, `TASK_CONFIG["grade_get"]`, and `TASK_CONFIG["grade_like"]` — there are no `consult_*` top-level orchestration entries after **AST-466**. Implementation must map `consult_*` → `grade_*` explicitly (same indirection the **AST-466** shim already documents via `agent_task` / helpers if shipped); **do not** assume `TASK_CONFIG["consult_do"]` exists.

Tests that patch or assert via `CONSULT_CONFIG` are updated to patch/assert the **grade** keys in `TASK_CONFIG` (and `GAZER_CONFIG` for gazer-owned tasks). Behavior of title validate, qualify, scrape JD, evaluate JD, and consult do/get/like must stay identical for the same config values.

**Prerequisite (hard):** Do not start **build-astral** until **AST-466** is merged onto the integration line you are building from (so `GAZER_CONFIG` and extended `TASK_CONFIG` exist). Linear lists **AST-466** as blocking **AST-467**; if orchestration fields are missing or named differently than below, stop and comment on **AST-467** — do not invent schema.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gazer.py` | Drop `CONSULT_CONFIG`; use `GAZER_CONFIG` for `validate_title` and `scrape_jd` pass/fail states; remove redundant inner import | core |
| `src/core/consult.py` | Drop `CONSULT_CONFIG`; read orchestration from `TASK_CONFIG` for all former `CONSULT_CONFIG` lookups; update module docstring and comments that name `CONSULT_CONFIG` | core |
| `tests/component/core/test_consult.py` | Replace imports and `monkeypatch.setitem` targets from `CONSULT_CONFIG` to `TASK_CONFIG` (same task keys); keep assertions logically identical | tests |

---

## Stage 1: `gazer.py` — `GAZER_CONFIG` only

**Done when:** `src/core/gazer.py` contains no identifier `CONSULT_CONFIG`; `validate_title_batch` and `scrape_jd_batch` resolve pass/fail states from `GAZER_CONFIG`; `python3 -m py_compile src/core/gazer.py` succeeds.

1. In `src/core/gazer.py`, change the top-level import from `CONSULT_CONFIG` to `GAZER_CONFIG` alongside existing `ROSTER_CONFIG`, `TRACKER_CONFIG`.
2. In `scrape_jd_batch`, delete the duplicate inner `from src.utils.config import CONSULT_CONFIG` and the erroneous assignment `pass_state = TRACKER_CONFIG` used only as a comment placeholder. Set `pass_state = GAZER_CONFIG["scrape_jd"]["pass_state"]` and `fail_state = GAZER_CONFIG["scrape_jd"]["fail_state"]` (same string values as today’s `CONSULT_CONFIG["scrape_jd"]` after AST-466 moves them).
3. In `validate_title_batch`, replace `task_cfg = CONSULT_CONFIG["validate_title"]` with `task_cfg = GAZER_CONFIG["validate_title"]`; keep `pass_state` / `fail_state` reads unchanged.
4. Run `python3 -m py_compile src/core/gazer.py`.

⚠️ **Decision:** JD scrape error routing continues to use module-local `_JD_ERROR_STATES` + `TRACKER_CONFIG` classifier — only the **success** and **generic fail** states come from `GAZER_CONFIG["scrape_jd"]`, matching current split of responsibilities.

---

## Stage 2: `consult.py` — `TASK_CONFIG` orchestration

**Done when:** `src/core/consult.py` contains no identifier `CONSULT_CONFIG`; every former `CONSULT_CONFIG[...]` access resolves orchestration via `TASK_CONFIG[...]` using the **correct orchestration key** per row below (`qualify_*` / `evaluate_*` = same key; `consult_*` = matching `grade_*`); `python3 -m py_compile src/core/consult.py` succeeds.

| Dispatch / caller task key (unchanged at call sites) | `TASK_CONFIG` key holding orchestration |
|-----------------------------------------------------|----------------------------------------|
| `qualify_job_listings` | `qualify_job_listings` |
| `evaluate_jd` | `evaluate_jd` |
| `consult_do` | `grade_do` |
| `consult_get` | `grade_get` |
| `consult_like` | `grade_like` |

1. In imports, remove `CONSULT_CONFIG` from `src.utils.config` import list; keep `TASK_CONFIG` (already imported).
2. Update the file header comment: replace the bullet that says `render_verdict` looks up `CONSULT_CONFIG` with wording that it reads per-task orchestration from `TASK_CONFIG` (and `agent_task` for the Anthropic task key).
3. Update the comment above `_INPUT_STATE_TO_TASK` to say it maps `input_state` → dispatch **task key**. Note that **`consult_*` dispatch keys still appear in tracker/job rows**, while orchestration for those flows is read from `TASK_CONFIG[grade_*]` (see table above — avoid implying `TASK_CONFIG[input_state]` is always valid).

4. In `_render_pass_fail`, replace `cfg = CONSULT_CONFIG[task_key]` with `cfg = TASK_CONFIG[_orchestration_key(task_key)]` where `_orchestration_key` is either (**a**) a tiny module-local map `consult_*`→`grade_*` plus identity for `qualify_job_listings` / `evaluate_jd`, or (**b**) a **documented helper from `config.py`** if **AST-466** exports one — **preferred if present** so dispatch↔grade indirection stays single-sourced with the shim.

5. In `render_verdict`, resolve orchestration dict with the same `_orchestration_key(task_type)` (or **`config`** helper): for `consult_do` / `consult_get` / `consult_like`, `cfg = TASK_CONFIG["grade_do"|"grade_get"|"grade_like"]` respectively — **never** `TASK_CONFIG["consult_do"]`. Keep `agent_task = cfg["agent_task"]`, `error_state`, `requires_company`, `rubric_artifact`, `pass_threshold`, `save_prefix`, and scored/binary branching identical.
6. On failure paths that currently say `consult_config[{task_type}]`, change the string to `task_config/orchestration` wording only in user-facing error text — use the **orchestration** key in the bracket (e.g. `f"TASK_CONFIG[{_orchestration_key(task_type)}] missing rubric_artifact"`).
7. In `_run_batch_consult`, replace `cfg = CONSULT_CONFIG[task_key]` with `cfg = TASK_CONFIG[_orchestration_key(task_key)]` (consult batches still **dispatch** as `consult_*`; orchestration rows are `grade_*`).
8. In `qualify_job_listings`, replace `cfg = CONSULT_CONFIG[task_key]` with `cfg = TASK_CONFIG[task_key]`.
9. In `evaluate_jd_batch`, replace `cfg = CONSULT_CONFIG[task_key]` with `cfg = TASK_CONFIG[task_key]`.
10. In `run_consult_task`, for `task_key in ("consult_do", "consult_get", "consult_like")`, replace `cfg = CONSULT_CONFIG[task_key]` with `cfg = TASK_CONFIG[_orchestration_key(task_key)]` (same mapping as steps 4–5) for pass/fail summary normalization after `render_verdict` — still **do not** index `TASK_CONFIG` by bare `consult_*`.
11. Run `python3 -m py_compile src/core/consult.py`.

⚠️ **Decision:** Prefer a **documented** `config.py` helper for **dispatch key → orchestration key** if **AST-466** ships one; otherwise keep a single module-local `_orchestration_key()` (or equivalent map) so `TASK_CONFIG[...]` is never indexed with a non-existent `consult_*` orchestration key.

⚠️ **Decision:** `_render_score` keeps its parameter name `consult_cfg`; it remains a plain dict carrying `pass_state` / `fail_state` — callers pass `TASK_CONFIG[...]` slices / full entries as today.

---

## Stage 3: Tests — `test_consult.py`

**Done when:** `tests/component/core/test_consult.py` does not import or reference `CONSULT_CONFIG`; tests patch/assert `TASK_CONFIG` at the **orchestration** keys used by production (`grade_*` for consult flows); targeted pytest for this file passes.

1. Replace `from src.utils.config import ... CONSULT_CONFIG ...` with `TASK_CONFIG` (and add `GAZER_CONFIG` only if a test asserts gazer config — unlikely in this file).
2. Replace `CONSULT_CONFIG`/monkeypatch entries so orchestration slices live under **`TASK_CONFIG["grade_do"]`**, **`grade_get`**, **`grade_like`** for consult scenarios; **`qualify_job_listings`** / **`evaluate_jd`** remain keyed by those same names.

3. For assertions that compared results to `CONSULT_CONFIG["qualify_job_listings"]["fail_state"]` etc., source from `TASK_CONFIG["qualify_job_listings"]` unchanged. For former `consult_do` orch assertions, compare against **`TASK_CONFIG["grade_do"]`** fields (matching production lookup).
4. Run: `python3 -m pytest tests/component/core/test_consult.py -q` (or the project’s standard test entrypoint if different).

⚠️ **Decision:** Ticket acceptance criteria require test updates here. If **build-astral**’s test-tree policy conflicts with an explicit ticket AC, escalate on **AST-467** before skipping test edits.

---

## Stage 4: Gazer tests and smoke

**Done when:** No test under `tests/` references `CONSULT_CONFIG` for code paths owned by this ticket; `test_gazer.py` still passes (it does not import `CONSULT_CONFIG` today — confirm with `rg CONSULT_CONFIG tests/component/core/test_gazer.py` and fix only if a future upstream change added it).

1. Run `rg CONSULT_CONFIG tests/component/core/test_gazer.py` — if zero matches, no file change required for gazer tests.
2. Run `python3 -m pytest tests/component/core/test_gazer.py tests/component/core/test_consult.py -q`.
3. Run dispatch-related consult tests if present in the repo (same directory or `tests/component/core/test_dispatcher.py` if it imports these modules) — **only** if failures point at `CONSULT_CONFIG` in `gazer`/`consult` call paths; do not expand scope to **AST-468** (`dispatcher.py` / `database.py` / `api_admin.py`).

---

## Self-Assessment

**Scope:** `Single-Component` — Touches two core modules plus `test_consult.py`; all changes are config lookup rewiring, not new product features.

**Conf:** `Medium` — Behavior is deterministic once **AST-466**’s `TASK_CONFIG` / `GAZER_CONFIG` shape is on disk; residual risk is a subtle mismatch between moved keys and call-site expectations.

**Risk:** `Medium` — Incorrect pass/fail state or threshold source would corrupt job state transitions and dispatch summaries; mitigation is bytecode compile, pytest for consult/gazer, and parity review against pre-migration state strings.

---

## Plan vs `ASTRAL_CODE_RULES.md`

- **§1.3 DRY:** Prefer **AST-466** helpers if shipped; otherwise single dict source `TASK_CONFIG` / `GAZER_CONFIG` without parallel inline state literals.
- **§2.1 Config:** Orchestration stays in `config.py`; core only reads — no new hardcoded state sets in `gazer.py` / `consult.py`.
- **§2.4 / §2.6:** Batch IDs and transitions unchanged — only where transition target strings are resolved.
- **§3.3 Imports:** Core may import `utils.config`; no new cross-layer violations.

---

## Revisions

- **Plan validation (Chuckles, AST-467 thread):** Document explicit **`consult_*` → `TASK_CONFIG["grade_*"]`** indirection; removed incorrect assumption that `TASK_CONFIG["consult_do"]` exists. Updated Stage 2 steps **4–5, 10** and Stage 3 test migration notes accordingly.

---

## Review stub (build agent)

Built by Hedy Lamarr.

- **Publish ref:** `origin/sub/AST-376/AST-467-absorb-consult-config-migrate-gazer-py-and-consult-py-call-sites`
- **Integration line:** **`dev-hedy`** (`astral-hedy`). AST-466 sub-branch merged first per Susan/Chuckles orchestrator override (`origin/sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields`).
- **Implementation commits:** `6ad97e691fd354f7596c7f1b3cbd657b0c6856d8` (feat); review stub appendix in following `docs(AST-467)` commit on `dev-hedy`.
Handoff (**build-astral §7:** no test edits in this pass): **`test_consult.py`** (and any consult tests patching **`CONSULT_CONFIG`** for **`consult.py`** orchestration lookups) need migration to **`TASK_CONFIG["grade_*"]`** / **`monkeypatch.setitem`** on the merged **`_consult_orchestration`** sources — **`qa-astral`** (**Betty**) per Stage 3 in this plan.

## Review

**Radia · `linear-radia` · 2026-05-23**  
**Baseline / diff:** `git diff origin/dev...origin/sub/AST-376/AST-467-absorb-consult-config-migrate-gazer-py-and-consult-py-call-sites` (three-dot). **Publish tip:** `13c8c9e7224bf297d741932a8cb928fa17fc8ab1`.

### What’s solid

- **`gazer.py` / `consult.py`:** No remaining `CONSULT_CONFIG` identifier in either module (acceptance criterion met). `GAZER_CONFIG` for validate/scrape JD success-fail transitions; `TASK_CONFIG` via `_consult_orchestration` for qualify/evaluate and `consult_*` → `grade_*` mapping matches the validated plan (# Revisions section).
- **`_consult_orchestration`:** Merging `{**TASK_CONFIG[grade_*], "agent_task": agent_key}` matches current `TASK_CONFIG["grade_*"]` shape (those rows omit a top-level `agent_task`; `agent_key` resolves `do_task` correctly).
- **`tests/component/core/test_consult.py`:** Patches and assertions moved to **`TASK_CONFIG["grade_do"]`** / **`qualify_job_listings`** as production does — consistent with staged migration notes.

### Issues

| Sev | Bucket | Finding |
|-----|--------|---------|
| — | Advisory | **`run_consult_task` → `process_gaze_board_batch`:** Nested `from src.core.gazer import …` likely cycle-break justified; **`ASTRAL_CODE_RULES` §B1 / review-astral §5a** prefers a **one-line** comment stating lazy import purpose. |
| Discuss | Footprint vs ticket | **`origin/dev...` tip diff** includes **`database.py`**, **`tracker.py`**, **`api_admin.py`**, **`agent.py`**, broad **`config.py`**, **`test_tracker`**, **`test_agent`**, etc. **AST-467** Linear boundaries say **dispatcher / database / api_admin → AST-468** and config schema **AST-466**. Confirm merge/parent intent (integration line stacking) vs ticket narrative so UAT/sign-off scope stays clear. |
| Discuss | Plan fidelity | **`render_verdict`** rubric-missing branch: message uses **`TASK_CONFIG orchestration[{task_type}]`** while **`task_type`** is still **dispatch key** (**`consult_*`**) in some callers; Stage 2 step 6 in this doc suggested **`TASK_CONFIG[{orchestration key}]`** in the bracket for clarity. Operational only — consider aligning text with **`_consult_orchestration(task_type)`’s resolved key**. |
| Discuss | **`process_gaze_board_batch`** | Broad **`except Exception`** with surfaced **`failure` outcome + `set_board_search_status(..., "error")`** — not silent (**§D2**-tolerable trajectory). Optional future narrow if churn warrants. |

**Fix-now count:** **0** (routing to **Review Posted**).

### Recommended actions

- Engineers: optional **`resolve-astral`** tweaks for **Discuss** rows (comments / error-string clarity); confirm epic owns **boards / DB / admin** deltas on this ref relative to **AST-467**.

---

## Resolution · Hedy Lamarr · 2026-05-23

**`resolve-astral`** (post-**`Review Posted`**) vs **`docs(AST-467): Radia review — TASK_CONFIG orchestration migration`** (`4660dea946c0557f7dabe76f9e03c6256e9f8d4a`).

| Radia bucket | Outcome |
|-------------|---------|
| **Fix-now** | No product changes needed (count **0**); publish ref already carries Radia doc at above SHA. |
| **Advisory** · lazy **`process_gaze_board_batch`** import | Landed **`src/core/consult.py`** one-line comment before the nested import (**`consult.py`** only). |
| **Discuss** | No code or copy changes under **AST-467 alone** — epic **AST-376** / **`prep-uat`** owns footprint narrative and optional **`render_verdict`** message tightening. |

**Parent:** **[AST-376](https://linear.app/astralcareermatch/issue/AST-376)** — branch tip after push is **`fix(AST-467):`** resolve (**`prep-uat`** handoff cites that SHA).
