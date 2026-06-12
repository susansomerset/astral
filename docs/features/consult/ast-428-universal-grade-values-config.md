# AST-428 — Universal grade values config

**Linear:** [AST-428](https://linear.app/astralcareermatch/issue/AST-428/replace-per-vector-grade-scores-with-universal-grade-values-per-vector)  
**Parent:** [AST-358](https://linear.app/astralcareermatch/issue/AST-358/replace-per-vector-grade-scores-with-universal-grade-values-per-vector)  
**Feature ref:** `sub/AST-358/AST-428-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-universal-grade-values-config`

Stand up the **config layer** for AST-358’s three-knob consult scoring: universal letter grades (`GRADE_VALUES`), display baseline `RUBRIC_TOTAL`, and removal of per-vector `grade_scores` from `TASK_CONFIG`. **AST-357** (`CONFIDENCE_MULTIPLIERS`) and **AST-359** (`consult_importance` / `importance_multiplier`) already exist — do not duplicate them. **Sibling AST-429** rewrites `_render_score`; this ticket must **not** change scoring math.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/utils/config.py` | Add `GRADE_VALUES`, `RUBRIC_TOTAL`; optional `grade_value(letter)` helper; move legacy quality map here | utils |
| `src/utils/config.py` | `craft_job_resume` `vectors`: `name` only — drop all `grade_scores` | utils |
| `src/core/consult.py` | Remove module-level `GRADE_QUALITY`; import legacy map from config (same numeric ratios until AST-429) | core |
| `tests/component/utils/test_config.py` | Assert `GRADE_VALUES` / `RUBRIC_TOTAL` shape (new small test class) | tests |

---

## Stage 1 — `GRADE_VALUES` and `RUBRIC_TOTAL`

**Done when:** Config exports universal letter map and rubric display total; values match parent AST-358 spec.

1. In `src/utils/config.py`, immediately after `CONFIDENCE_MULTIPLIERS` / `CONFIDENCE_DESCRIPTIONS` (consult constants block ~line 476), add:
   - `GRADE_VALUES: Dict[str, int] = {"A": 7, "B": 6, "C": 3, "D": 0}` — **only** A–D; **F** and **X** are not keys (control flow in consult).
   - `RUBRIC_TOTAL: int = 3000` — cosmetic baseline for normalization (AST-429).
2. Add `def grade_value(letter: str) -> int:` that uppercases, looks up `GRADE_VALUES`, raises `ValueError` for unknown letters (used by AST-429; safe to add now).
3. Add `MAX_GRADE_VALUE: int = max(GRADE_VALUES.values())` (or compute inline in AST-429 only — prefer module constant for one import site).
4. `python3 -m py_compile src/utils/config.py`.

⚠️ **Decision:** Use parent’s example integers exactly (`A=7…D=0`). Do not tune to match old `GRADE_QUALITY` ratios — AST-429 owns the new formula.

---

## Stage 2 — Remove per-vector `grade_scores` from `TASK_CONFIG`

**Done when:** `craft_job_resume` vectors list has `name` only; `grade_get` / `grade_do` / `grade_like` remain unchanged (they already have no inline `grade_scores`).

1. In `TASK_CONFIG["craft_job_resume"]["vectors"]`, replace each `{"name": "…", "grade_scores": {…}}` with `{"name": "…"}` for all 12 vectors (MISSION … GUT).
2. Grep `src/` for `"grade_scores"` — expect **zero** hits outside comments/docs after this stage. If other tasks still embed tables, remove per ticket scope (only `craft_job_resume` per Linear).
3. `python3 -m py_compile src/utils/config.py`.

---

## Stage 3 — Retire `GRADE_QUALITY` from `consult.py` (no scoring rewrite)

**Done when:** `consult.py` has no module-level `GRADE_QUALITY`; `_render_score` behavior unchanged on existing tests.

1. In `src/utils/config.py`, add **`GRADE_QUALITY_LEGACY`** with the **exact** current ratios: `{"A": 1.0, "B": 0.7, "C": 0.35, "D": 0.07}` — temporary until AST-429 deletes it.
2. In `src/core/consult.py`:
   - Delete module-level `GRADE_QUALITY`.
   - Import `GRADE_QUALITY_LEGACY as GRADE_QUALITY` (or import and alias at use site) so `_render_score` line `q = GRADE_QUALITY.get(letter, 0.0)` is unchanged.
   - Update the file header comment (~line 73) to state positional weights + legacy quality curve remain until AST-429.
3. Run: `python3 -m py_compile src/core/consult.py src/utils/config.py`.
4. Run: `python3 -m pytest tests/component/core/test_consult.py::TestRenderScore -q` — must stay green (no math change).

---

## Stage 4 — Config tests

**Done when:** One pytest asserts public constants.

1. In `tests/component/utils/test_config.py`, add `class TestGradeValuesConfig` with `test_grade_values_and_rubric_total` — assert keys A–D, `GRADE_VALUES["A"] == 7`, `RUBRIC_TOTAL == 3000`, `grade_value("b") == 6`.
2. Run full file or new class only; green before commit.

---

## Self-Assessment

**Scope — `Single-Component`**  
Touches `config.py`, a thin import change in `consult.py`, and one test module — no `_render_score` rewrite.

**Conf — `high`**  
Straightforward config extraction; AST-357/359 already landed.

**Risk — `Medium`**  
Wrong constant placement could confuse AST-429; mitigated by keeping legacy quality map and green `TestRenderScore`.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §2.1 config | `GRADE_VALUES` / `RUBRIC_TOTAL` live only in `config.py`. |
| §3.3 | `config.py` does not import core. |
| §1.3 DRY | No duplicate multiplier tables. |

No conflicts flagged.

## Review stub (build-astral) — 2026-05-17

**Branch:** `sub/AST-358/AST-428-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-universal-grade-values-config`  
**Shipped:** `GRADE_VALUES`, `RUBRIC_TOTAL`, `grade_value()`, `MAX_GRADE_VALUE`; `craft_job_resume` vectors name-only; `GRADE_QUALITY_LEGACY` import in `consult.py` (scoring unchanged). `TestGradeValuesConfig` + `TestRenderScore` green.

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-358/AST-428-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-universal-grade-values-config` (no `origin/ftr/AST-428`; sub-issue under AST-358).

### What's solid

| Area | Notes |
|------|--------|
| Acceptance | `GRADE_VALUES` A=7/B=6/C=3/D=0; `RUBRIC_TOTAL=3000`; `craft_job_resume` vectors are `name` only; no `grade_scores` in any `.py` on tip. |
| Boundaries | `_render_score` body unchanged; `GRADE_QUALITY` module dict removed, `GRADE_QUALITY_LEGACY` imported as alias; no `consult_importance` / confidence table duplication. |
| API | `grade_value()` normalizes and raises on unknown letters; `MAX_GRADE_VALUE` derived from map. |
| Tests / bible | `TestGradeValuesConfig`; **ASTRAL_TEST_BIBLE** §7.13i. |
| Scope | Matches plan Self-Assessment (`scope-Single-Component`). |

### Issues

| Severity | Item |
|----------|------|
| **fix-now** | 0 |
| **discuss** | 1 — `grade_value()` raises on F/X (not in `GRADE_VALUES`); correct for this ticket; **AST-429** should define fail/unknown letter handling when wiring importance scoring. |
| **advisory** | 1 — `docs/ASTRAL_CODE_RULES.md` §1 still mentions `grade_scores` on vectors; engineer correctly did not drive-by edit; consider a small doc follow-up when AST-429 lands. |

### Recommended actions

| Action | Owner |
|--------|--------|
| Cherry-pick doc commit onto `dev-ada` and re-publish to sub branch | Ada |
| AST-429: use `grade_value()` + importance; retire `GRADE_QUALITY_LEGACY` in `_render_score` | Ada (sibling ticket) |

## Resolution (resolve-astral) — 2026-05-17

**Radia:** 0 fix-now · 1 discuss · 1 advisory — no product commits required on AST-428.

| Item | Outcome |
|------|---------|
| fix-now | None — config layer accepted as shipped (`f2b3347a` + bible `67049556`). |
| discuss (`grade_value` / F–X) | No change here; **AST-429** defines scored-path F halt and X/conf-1 exclusion (landed on sibling sub). |
| advisory (`ASTRAL_CODE_RULES` §1 `grade_scores`) | Deferred per review — update when AST-358 family completes, not a drive-by on this ticket. |

**Doc:** Radia review section cherry-picked via merge of `origin/sub/…-universal-grade-values-config` (`0c358d7b`). **Parent:** AST-358 — ready for **prep-uat** when all siblings are **User Testing** or **Done**.
