# AST-1277 — Strip pass_threshold; verdict uses dispatch score_floor

**Linear:** [AST-1277](https://linear.app/astralcareermatch/issue/AST-1277/strip-pass-threshold-verdict-uses-dispatch-score-floor-remove-pass)  
**Parent:** [AST-1275](https://linear.app/astralcareermatch/issue/AST-1275/remove-pass-threshold-from-task-config) — Remove "pass_threshold" from task_config  
**Publish ref:** `sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor`

Remove every `TASK_CONFIG` `pass_threshold` key (roster consult, meteorite aliases, and `prefilter_company`). Scored soft-fail / pass after a run reads `score_floor` from the candidate’s matching `dispatch_task` row — explicit `0` means no numeric soft-fail; dealbreaker and technical-error paths stay. Does not own admin Score Floor dropdown (AST-1278) or statute/Code Rules retirement (AST-1279).

## Post-land floor expectations

Parent keeps NULL→`1.0` for **claim**; this child applies the **same** normalizer to **verdict** soft-fail (sole numeric floor). Roster `grade_do` / `grade_get` / `grade_like` dispatch rows are not seed-catalogued with an explicit floor (unlike `METEORITE_DISPATCH_TASKS` at `0.0`), so on the day this lands those hops soft-fail against **`1.0`**, not today’s TASK_CONFIG `6.0`, until Susan sets floors in admin (AST-1278 makes `0` selectable). **No row backfill in this ticket.** UAT / Susan action before expecting historical-6.0 behavior: set each candidate’s scored consult dispatch `score_floor` to the intended value (commonly `6.0` for roster GDL; `0` for always-pass numeric, e.g. prefilter / meteorite).

**Law sequencing (accepted):** `astral.config.pass-threshold-vs-score-floor` is still `status: active` and forbids feeding `score_floor` into the verdict path. Parent AC4 retires it in AST-1279, which this child **blocks**, so the tree contradicts that statute in the interval between landings. Parent authority accepts the interval; this child does not rewrite Code Rules or retire the statute.

**Pattern citations:** `pattern.dispatch.score-floor` is not yet under `canon/patterns/**` (AST-1279). Conform to the parent’s plain-language rule until that pattern lands. Parent citation `astral.patterns.render-verdict-orchestrates-consult` is retired; live id is `astral.idioms.render-verdict-orchestrates-consult` — not this child’s to fix in Linear text.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Delete all `pass_threshold` keys from `TASK_CONFIG`; add `effective_dispatch_score_floor` (NULL→1.0, keep explicit `0`); add `dispatch_row_task_key` (consult/catalog key → `dispatch_task.task_key`, prefilter only) | utils |
| `src/core/consult.py` | Resolve floor from candidate dispatch row via tracker helper + row key map; scored `_apply_render_verdict_decoded_job` uses it; rename `_render_score` threshold arg to `score_floor`; stop reading artifact/`pass_threshold` fallbacks | core |
| `src/core/roster.py` | Prefilter scored soft-fail uses the same dispatch `score_floor` (not hardcoded `0.0`); pass consult key `prefilter_company` into the helper (helper maps to dispatch key `prefilter`) | core |
| `src/core/dispatcher.py` | Claim-path floor assignment calls `effective_dispatch_score_floor` (same NULL/`0` rules; no behavior invent) | core |

**Out of files (do not touch):** `docs/ASTRAL_CODE_RULES.md` / statutes / pattern catalog (AST-1279); admin Score Floor UI (`AdminScheduledActions.tsx`, AST-1278); `tests/` and `docs/test-bible/**` (Betty); binary qualify/evaluate paths that discard `_render_score` state and only need an informational score (keep calling `_render_score` with literal `0.0` so state is unused-pass — those paths are not soft-fail consumers).

## Stages

### Stage 1: Strip TASK_CONFIG thresholds + shared floor helpers

**Done when:** `rg '"pass_threshold"' src/utils/config.py` returns no matches. `effective_dispatch_score_floor(None) == 1.0`, `effective_dispatch_score_floor(0) == 0.0`, `effective_dispatch_score_floor(0.0) == 0.0`, and `effective_dispatch_score_floor(6) == 6.0`. `dispatch_row_task_key("prefilter_company") == "prefilter"`, `dispatch_row_task_key("prefilter") == "prefilter"`, and `dispatch_row_task_key("grade_do") == "grade_do"` (meteorite aliases identity). Dispatcher job-claim floor assignment uses `effective_dispatch_score_floor` (same numeric outcomes as today’s inline ternary for scored rows).

1. In `src/utils/config.py`, delete the `"pass_threshold": …` entry from each of these `TASK_CONFIG` blocks only (leave every other key in those blocks untouched):
   - `prefilter_company` (currently `0.0`)
   - `grade_do`, `grade_get`, `grade_like` (currently `6.0`)
   - `meteorite_grade_do`, `meteorite_grade_get`, `meteorite_like` (currently `6.0`)
   Confirm with search: no remaining `"pass_threshold"` string under `src/utils/config.py`.

2. In `src/utils/config.py`, immediately after `dispatch_score_floor_option_labels` (near the existing score-floor helpers ~line 2907), add:

   ```python
   def effective_dispatch_score_floor(raw_score_floor: Optional[float]) -> float:
       """Normalize dispatch_task.score_floor for claim + scored soft-fail.

       Explicit 0 / 0.0 is valid (no numeric soft-fail / no claim exclusion by floor).
       NULL / missing → 1.0 (same claim rule dispatcher already applies on scored rows).
       """
       if raw_score_floor is None:
           return 1.0
       return float(raw_score_floor)
   ```

   Import `Optional` is already available in this module. Do not change `DISPATCH_SCORE_FLOOR_VALUES` or admin option labels (AST-1278).

3. In `src/utils/config.py`, next to `dispatch_task_grouping_catalog_key` (~line 2991; that helper maps dispatch→catalog), add the inverse used for row lookup:

   ```python
   def dispatch_row_task_key(task_key: str) -> str:
       """Map consult/catalog task_key to dispatch_task.task_key when they differ.

       ROSTER_CONFIG['prefilter']['task_key'] (`prefilter_company`) and the bare
       dispatch key `prefilter` both resolve to `prefilter` (AST-823 migrated rows).
       All other keys (including meteorite_grade_* aliases) are identity.
       """
       tk = (task_key or "").strip()
       if tk == "prefilter" or tk == ROSTER_CONFIG["prefilter"]["task_key"]:
           return "prefilter"
       return tk
   ```

   Do **not** invent other renames; prefilter is the only consult≠dispatch key pair this ticket needs.

4. In `src/core/dispatcher.py`, import `effective_dispatch_score_floor` from `src.utils.config`. Replace the scored job-claim floor line that currently does:

   ```python
   floor = float(task.get("score_floor")) if (is_scored and task.get("score_floor") is not None) else (1.0 if is_scored else None)
   ```

   with:

   ```python
   floor = effective_dispatch_score_floor(task.get("score_floor")) if is_scored else None
   ```

   Do **not** change the company-claim floor line (`float(task["score_floor"]) if … else None`) — company claim already treats NULL as ungated; that path is outside this ticket’s scored-verdict contract.

   ⚠️ **Decision:** Shared normalizer lives in `config.py` next to other dispatch score-floor helpers so claim and verdict cannot drift. Explicit `0` must not collapse to `1.0` (parent boundary: `0` distinct from NULL).

### Stage 2: Scored verdict + prefilter read dispatch score_floor

**Done when:** A scored job consult (`grading_mode == "scored"`) soft-fails when computed score `<` that candidate’s matching `dispatch_task.score_floor`, passes when `>=`, and with `score_floor == 0` never soft-fails on the numeric comparison (F2 dealbreaker and technical error paths unchanged). `_apply_render_verdict_decoded_job` does not read `cfg["pass_threshold"]` or `{rubric_key}_threshold` artifacts. Prefilter soft-fail looks up the dispatch row with `task_key == "prefilter"` (via `dispatch_row_task_key`), so an explicit `0` on that row is reachable. `rg pass_threshold src/` returns no matches.

1. In `src/core/consult.py`, add a helper (place with other private helpers near `_candidate_id_from_ctx` / before `_render_score`):

   ```python
   def _dispatch_score_floor_for_task(
       candidate_id: str,
       task_key: str,
       trigger_state: Optional[str] = None,
   ) -> float:
   ```

   Behavior (literal):
   - `cid = (candidate_id or "").strip()`; `raw_tk = (task_key or "").strip()`; `dispatch_tk = dispatch_row_task_key(raw_tk)`.
   - If `cid` empty or `dispatch_tk` empty → return `effective_dispatch_score_floor(None)` (i.e. `1.0`).
   - `ts = (trigger_state or "").strip()` or `None` if blank.
   - Call **`tracker.list_dispatch_tasks_for_candidate(cid, trigger_state=ts)`** when `ts` is not None; otherwise `tracker.list_dispatch_tasks_for_candidate(cid)`. Do **not** re-implement trigger / compound hop-label matching in consult — the tracker helper already uses `parse_dispatch_hop_label`.
   - From that list, keep rows whose `(row.get("task_key") or "").strip() == dispatch_tk`.
   - If `ts` was set and that filter yields zero rows, **fall back once**: `tracker.list_dispatch_tasks_for_candidate(cid)` (no trigger filter), then the same `task_key == dispatch_tk` keep.
   - If still zero matching rows → return `effective_dispatch_score_floor(None)`.
   - If one or more matching rows → use the **first** element of that filtered list. That first element is the **newest** row (`id DESC`): `tracker.list_dispatch_tasks_for_candidate` walks `database.list_dispatch_tasks()` which is `ORDER BY id DESC`. Do **not** claim `id ASC` and do **not** call `database.list_dispatch_tasks_for_candidate` from consult (core stays on the tracker wrapper).
   - Return `effective_dispatch_score_floor(chosen.get("score_floor"))`.

   Import `effective_dispatch_score_floor` and `dispatch_row_task_key` from `src.utils.config` in the existing config import block.

   ⚠️ **Decision — lookup over ctx injection:** Resolve from the DB row at verdict time rather than requiring dispatcher to stuff `score_floor` into `ctx`. Ad-hoc / single-job `render_verdict` has no claim context; the dispatch row is the sole authority. Missing row → NULL normalization (`1.0`), not a hard raise, so CLI/ad-hoc does not brick.

   ⚠️ **Decision — drop artifact `{rubric}_threshold` override:** Parent makes `dispatch_task.score_floor` the sole numeric floor. Stop reading `artifacts.get(f"{rubric_key}_threshold", …)`. Do not resurrect a TASK_CONFIG or artifact threshold. (No UI writer for those keys remains in `src/`.)

   ⚠️ **Decision — newest-row tie-break:** When multiple same-`task_key` rows remain after trigger preference / fallback, take the first tracker-returned match (= newest `id`). Prefer always passing `trigger_state=` from the job’s current state so multi-row collision is rare; compound hop labels are handled by the tracker helper, not by exact string equality in consult.

2. In `_render_score`, rename the parameter `pass_threshold: float` to `score_floor: float`. Update the three debug/detail strings and the comparison to use `score_floor` (same `score < score_floor` → `fail_state` math). Keep F2 dealbreaker branch first; keep score persistence/`pass_state` return shape identical.

3. In `_apply_render_verdict_decoded_job`, in the `mode == "scored"` branch, replace:

   ```python
   artifacts = (ctx or {}).get("candidate_data", {}).get("artifacts", {})
   threshold = artifacts.get(f"{rubric_key}_threshold", cfg.get("pass_threshold", 6.0))
   …
   to_state, score = _render_score(cfg, rubric_criteria, grades, float(threshold))
   ```

   with (same control flow otherwise):
   - `candidate_id = _candidate_id_from_ctx(ctx)` — if empty, also try `str((tracker.get_job(astral_job_id) or {}).get("astral_candidate_id") or (tracker.get_job(astral_job_id) or {}).get("candidate_id") or "")` so single-job paths without ctx still resolve.
   - `job_row = tracker.get_job(astral_job_id) or {}` (binary branch already loads a job row — reuse one fetch if already present in that function; do not double-fetch unnecessarily).
   - `floor = _dispatch_score_floor_for_task(candidate_id, dispatch_task_key, (job_row.get("state") or None))` — `dispatch_task_key` may be a consult or dispatch string; the helper maps via `dispatch_row_task_key` (identity for `grade_*` / `meteorite_grade_*`).
   - `to_state, score = _render_score(cfg, rubric_criteria, grades, floor)`
   - Keep `_require_complete_grade_set` before `_render_score` as today.

4. In `src/core/roster.py` `_apply_prefilter_decoded_company_outcome`, replace the informational-only score block that calls `_render_score(..., 0.0)` so soft-fail participates in the outcome:
   - Resolve `floor = _dispatch_score_floor_for_task(candidate_id, "prefilter_company")` (import the helper from `src.core.consult` alongside the existing `_render_score` import). The helper’s `dispatch_row_task_key` maps `prefilter_company` → dispatch row key **`prefilter`** — do **not** query for `task_key == "prefilter_company"` (those rows were migrated away in AST-823).
   - Keep the existing `_render_pass_fail("prefilter_company", grades)` call for X / no-confidence / empty-grade rules that `_render_score` does not cover.
   - When `verdict_state == cfg["pass_state"]` and `rubric_list` is non-empty: call `score_state, score = _render_score(task_cfg, rubric_list, grades, floor)`. Set `prefilter_score = float(score)` when `score is not None`. If `score_state == cfg["fail_state"]`, set `verdict_state = cfg["fail_state"]` **before** the decomposed/legacy `new_state` branching so numeric soft-fail parks as fail (same as dealbreaker fail). When `floor == 0.0`, `_render_score` never soft-fails on the numeric compare (dealbreaker inside `_render_score` still can).
   - Do not add a new `pass_threshold` (or alias name) on `TASK_CONFIG["prefilter_company"]`.

   ⚠️ **Decision — prefilter NULL floor:** Same normalizer as job consult (`NULL`→`1.0`). Historical `pass_threshold: 0.0` meant always-pass numeric; after this change, always-pass requires an explicit `score_floor` of `0` on the candidate’s **`prefilter`** dispatch row (AST-1278 makes `0` selectable). Do not special-case prefilter to treat NULL as `0`.

5. Leave binary qualify/evaluate call sites that do `_, score = _render_score(..., 0.0)` unchanged (informational score only; verdict remains `_render_pass_fail`). Update the module docstring line in `consult.py` that mentions “thresholds” from TASK_CONFIG so it says soft-fail floor comes from `dispatch_task.score_floor` (one-line docstring honesty — not a Code Rules edit).

6. Repo check before stage commit: `rg 'pass_threshold' src/` must return no matches. If any remain outside the planned files, **stop** and comment on the parent — do not expand scope.

## Self-Assessment

**Scope:** `Single-Component` — config strip plus consult/roster scored soft-fail wiring (and a one-line dispatcher DRY reuse of the normalizer); no UI, no statutes, no test-tree.

**Conf:** `Medium` — TASK_CONFIG key enumeration and claim normalizer are solid; round-1 caught a real consult≠dispatch key miss on prefilter and an inverted list-order claim, both now pinned in Stage 1–2.

**Risk:** `Medium` — wrong floor lookup or NULL→1.0 changes who soft-fails vs historical `pass_threshold` 6.0/0.0 (see Post-land floor expectations); dealbreaker/error paths are intentionally untouched but a bad floor still parks jobs in fail states.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Shared `effective_dispatch_score_floor`; trigger filtering delegated to `tracker.list_dispatch_tasks_for_candidate(..., trigger_state=)` (no parallel hop-label parser in consult); `dispatch_row_task_key` is the single consult↔dispatch rename point.
- **§2.1 config SoT:** Deletes resurrected task-config thresholds; floors read from dispatch rows / normalizer — does **not** rewrite the outdated §2.1 pass-threshold subsection (AST-1279). Active statute `astral.config.pass-threshold-vs-score-floor` is contradicted in the land interval by parent order (see Post-land / Law sequencing).
- **§2.4 batch / §2.6 states:** Claim-process-release and pass/fail/error state **names** unchanged; only the numeric compare source changes.
- **§2.7 / `astral.idioms.render-verdict-orchestrates-consult`:** Still orchestrates; scored branch swaps floor source only.
- **§3.3 imports:** `consult` → `tracker` + `config`; `roster` → `consult` helpers (existing pattern); no new `ui`/`external` edges; no direct `database.list_dispatch_tasks_for_candidate` from consult.
- **§3.5 naming:** `score_floor` / `effective_dispatch_score_floor` / `dispatch_row_task_key` match existing dispatch vocabulary.
- **Test-tree ban:** No `tests/` or bible edits in this plan.

## Revisions

Revision 1 — 2026-08-08  
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric REVISE) — fix-now wrong prefilter dispatch lookup key (`prefilter_company` vs `prefilter`); fix-now inverted tie-break order claim (`id ASC` vs tracker/`list_dispatch_tasks` `id DESC`); discuss NULL→1.0 verdict semantics / Susan floor action; discuss active-law interval vs AST-1279; discuss DRY trigger match via tracker helper; discuss pattern citation status.  
Changes: Added `dispatch_row_task_key`; Stage 2 lookup uses tracker `trigger_state=` + newest-first tie-break; prefilter resolves through that map to dispatch key `prefilter`; documented post-land floor expectations and accepted statute-interval contradiction; Conf → Medium; self-review updated for DRY / idiom id.
