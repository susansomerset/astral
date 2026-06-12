# AST-429 — Importance-based scoring engine

**Linear:** [AST-429](https://linear.app/astralcareermatch/issue/AST-429/replace-per-vector-grade-scores-with-universal-grade-values-per-vector)  
**Parent:** [AST-358](https://linear.app/astralcareermatch/issue/AST-358/replace-per-vector-grade-scores-with-universal-grade-values-per-vector)  
**Feature ref:** `sub/AST-358/AST-429-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-importance-based-scoring-engine`  
**Depends on:** [AST-428](https://linear.app/astralcareermatch/issue/AST-428) (`GRADE_VALUES`, `RUBRIC_TOTAL` on `origin/dev` or merged sub branch)

Rewrite consult **scored** grading to AST-358’s three-knob model: equal base share per counted vector, universal grade density × confidence, per-vector importance from rubric artifact rows. Remove positional `_rubric_to_weights`. Preserve F halt, X / conf-1 / F1 exclusions (AST-357). Return **0–10** via `rubric_score / RUBRIC_TOTAL * 10` for `pass_threshold` comparison.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/core/consult.py` | Replace `_render_score` math; remove `_rubric_to_weights`; add `_importance_for_label`; update call sites | core |
| `src/utils/config.py` | Remove `GRADE_QUALITY_LEGACY` after consult migrates; export helpers used by consult | utils |
| `tests/component/core/test_consult.py` | Replace positional-weight tests; add AST-358 formula cases | tests |

---

## Stage 1 — Importance lookup from rubric criteria

**Done when:** Helper returns multiplier per vector label using artifact `importance` (default 5).

1. In `src/core/consult.py`, add:

```python
def _importance_for_label(rubric_criteria: list, vector_label: str) -> float:
```

- Match `vector_label` to `item["label"]` with same `_strip_code` normalization as `_render_score`.
- Read `item.get("importance")`; if missing, use `ASTRAL_CONFIG["consult_importance"]["default_vector_importance"]` (5).
- Return `importance_multiplier(int(n))` from `src.utils.config`.
- Raise `ValueError` if label not found (same strictness as missing vector today).

2. `python3 -m py_compile src/core/consult.py`.

⚠️ **Decision:** Importance comes from **artifact row** (`label` + `importance`), not list order — UI sort is cosmetic per AST-359.

---

## Stage 2 — New `_render_score` implementation

**Done when:** Formula matches parent AST-358; F2+ → `(fail_state, None)`; counted vectors exclude X, conf 1, F1 via existing `_effective_no_signal_for_score`.

1. Change signature to:

```python
def _render_score(
    consult_cfg: dict,
    rubric_criteria: list,
    grades: list,
    pass_threshold: float,
) -> Tuple[str, Optional[float]]:
```

Remove `vector_weights: Dict[str, int]` parameter.

2. **F dealbreaker** — keep existing block (F with confidence ≥ 2).

3. **Expected vectors** — build `expected_labels = {_strip_code(item["label"]) for item in rubric_criteria if item.get("label")}`; same missing/extra validation as today (compare to `grades` vectors after `_strip_code`).

4. **Counted set V** — iterate grades; skip rows where `_effective_no_signal_for_score(g)`; let `V = len(counted_rows)`. If `V == 0`, set `rubric_score = 0.0` and **skip** the per-row loop (do **not** return `fail_state` early). Then normalize `score = 0.0` and run the usual `score < pass_threshold` comparison — preserves informational paths with `pass_threshold == 0.0` (`test_render_score_with_only_no_signal_rows`).

5. For each counted row `g`:
   - `letter = g["grade"]` (not F — F2+ already returned)
   - `conf = g["confidence"]` — validate int; `m = CONFIDENCE_MULTIPLIERS[conf]`
   - `gv = grade_value(letter)` from config
   - `density = (gv / MAX_GRADE_VALUE) * m`
   - `base = RUBRIC_TOTAL / V`
   - `imp = _importance_for_label(rubric_criteria, g["vector"])`
   - `contrib = base * density * imp`
   - accumulate `rubric_score += contrib`

6. **Normalize:** `score = (rubric_score / RUBRIC_TOTAL) * 10.0` (float). Compare `score < pass_threshold` → fail else pass. **Do not** cap raw sum at `RUBRIC_TOTAL` before normalize (parent allows sum > total).

7. Debug logging: update `_render_score` debug lines to log `base`, `density`, `imp`, `contrib` (not positional `w`, `q`).

8. Delete `_rubric_to_weights` and the comment about list order (~lines 76–83).

9. Remove `GRADE_QUALITY_LEGACY` usage; delete from `config.py` if unused.

10. `python3 -m py_compile src/core/consult.py src/utils/config.py`.

---

## Stage 3 — Call sites

**Done when:** All scored paths pass `rubric_criteria` into `_render_score`; no `_rubric_to_weights` references.

1. **`_process_one_job_response`** (~line 378): replace `vector_weights = _rubric_to_weights(...)` and `_render_score(cfg, vector_weights, …)` with `_render_score(cfg, rubric_criteria, grades, float(threshold))`.

2. **Batch consult paths** (~lines 560, 641): replace `_vector_weights = _rubric_to_weights(rubric_list) if rubric_list else {}` and guards `if _vector_weights` with `if rubric_list` (or `if rubric_criteria`); call `_render_score(cfg, rubric_list, grades, 0.0)`.

3. Grep `consult.py` and repo for `_rubric_to_weights` — zero hits.

4. Update `src/core/agent.py` comment (~line 106) if it mentions `_rubric_to_weights` / positional weights — one-line note: importance-based scoring (AST-429).

---

## Stage 4 — Tests

**Done when:** `tests/component/core/test_consult.py` reflects new math; green manifest for Betty after Code Complete.

1. **Remove or rewrite** `TestRubricHelpers.test_derives_weights_and_strips_codes` — drop `_rubric_to_weights` assertion; keep `_strip_code` test only.

2. **Rewrite `TestRenderScore`** cases:
   - Dealbreaker F2+ unchanged.
   - **Single vector:** rubric `[{"label": "Fit", "importance": 10}]`, grade A conf 5 → compute expected score by hand with `GRADE_VALUES`, `RUBRIC_TOTAL`, multipliers; assert `pass_state` and `score` ≈ expected (use `pytest.approx`).
   - **X excluded:** two-vector rubric, one row X conf 0 → only one vector in V.
   - **Conf 1 excluded:** row A conf 1 → not counted (V=0 or other row required).
   - **Importance floor:** same grades, importance 1 vs 10 → higher importance yields higher score.
   - Unknown/missing vector errors unchanged.

3. Update any test that builds `weights = {"Fit": 1}` to pass minimal `rubric_criteria=[{"label": "Fit", "importance": 5}]`.

4. Run: `python3 -m pytest tests/component/core/test_consult.py -q`.

5. Document Betty manifest in build comment (class-qualified node ids).

---

## Stage 5 — Cleanup

**Done when:** No legacy quality curve; consult header accurate.

1. Remove `GRADE_QUALITY_LEGACY` from `config.py`.
2. Update `consult.py` module docstring (lines 7–8) to describe importance + universal grade values.
3. Final `py_compile` + full `test_consult.py` run.

---

## Self-Assessment

**Scope — `scope-MAJOR-CHANGE`**  
Rewrites core scoring path and test suite; touches all consult scored entry points.

**Conf — `Medium`**  
Formula is specified but hand-tests must match; depends on AST-428 constants.

**Risk — `HIGH`**  
Wrong normalization or V counting changes pass/fail for live jobs; requires thorough component tests.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §2.1 | Grade/importance numbers from `config.py` / `ASTRAL_CONFIG` only. |
| §2.6 | Scoring does not transition job states. |
| §3.3 | consult imports config/utils only. |
| §1.3 | Delete `_rubric_to_weights` rather than parallel weight path. |

No `!!-NONE` conflicts.

---

## Revisions

**Revision 1 — 2026-05-17**  
Driven by: Chuckles plan review (fix-now on `V == 0`).  
Changes: Stage 2 step 4 — all-no-signal rows yield `score = 0.0` then threshold compare, not short-circuit `fail_state`.

---

## Radia / discuss (non-blocking)

Parent review may note duplicate `run_*_artifact_chain` helpers — **out of scope** (consult scoring only).

## Review stub (build-astral) — 2026-05-17

**Branch:** `sub/AST-358/AST-429-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-importance-based-scoring-engine`  
**Shipped:** `_importance_for_label`, AST-358 `_render_score` (no `_rubric_to_weights`); `GRADE_QUALITY_LEGACY` removed; scored call sites pass `rubric_criteria`. Normalized score can exceed 10.0 when importance multipliers &gt; 1. Betty manifest: `tests/component/core/test_consult.py` (`TestRenderScore`, `TestRenderScoreBranches`, `TestRubricHelpers`, `test_render_score_with_only_no_signal_rows`).

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-358/AST-429-replace-per-vector-grade-scores-with-universal-grade-values-per-vector-importance-multiplier-importance-based-scoring-engine` (no `origin/ftr/AST-429`; AST-358 sub-issue). Branch also carries **AST-428** config (`GRADE_VALUES`, name-only vectors) stacked for integration.

### What's solid

| Area | Notes |
|------|--------|
| Formula | `base = RUBRIC_TOTAL/V`, density from `grade_value` × `CONFIDENCE_MULTIPLIERS`, importance via `_importance_for_label` / `importance_multiplier()`; normalized `(rubric_score/RUBRIC_TOTAL)*10`. |
| AST-357 | F conf≥2 → `(fail_state, None)`; X and conf-1 excluded from V via `_effective_no_signal_for_score`; F conf-1 excluded by conf==1 path. |
| Cleanup | `_rubric_to_weights` and `GRADE_QUALITY` removed; all `_render_score` call sites pass `rubric_criteria`. |
| Edge cases | V==0 → score 0.0 then threshold compare (`test_render_score_with_only_no_signal_rows`). |
| Tests | `test_consult.py` updated for importance math, X exclusion, F2+ fail; bible §7.13j. |

### Issues

| Severity | Item |
|----------|------|
| **fix-now** | 0 |
| **discuss** | 1 — Normalized score is **not capped at 10** (e.g. single A@conf5 importance 10 → **~20.0** in tests). Matches parent formula allowing raw sum > `RUBRIC_TOTAL`; Susan should confirm existing `pass_threshold` values in `CONSULT_CONFIG` still make sense in UAT. |
| **discuss** | 2 — Diff vs `origin/dev` includes **AST-428** config/doc (`ast-428-*.md`, `qualify_job_listings` vectors) on the same sub branch; expected for stacked children, but UAT merge should treat 428+429 together under **AST-358**. |
| **advisory** | Docstring mentions “F1” while implementation excludes any **conf==1** row (broader than F-only) — correct for AST-357; optional comment tweak only. |

### Recommended actions

| Action | Owner |
|--------|--------|
| Cherry-pick doc commit onto `dev-ada` | Ada |
| UAT: spot-check scored consult pass/fail with real rubrics and thresholds | Susan |
| `resolve-astral` only if discuss items need code changes | Ada |

## Resolution (resolve-astral) — 2026-05-17

**Radia:** 0 fix-now · 2 discuss · 1 advisory.

| Item | Outcome |
|------|---------|
| fix-now | None — scoring engine accepted as shipped. |
| discuss (score &gt; 10) | No cap added — matches AST-358 / Chuckles plan review; **Susan UAT** should confirm `pass_threshold` in `CONSULT_CONFIG` still behaves as intended. |
| discuss (428+429 stack) | Documented — sub branch intentionally stacks **AST-428** config; **prep-uat** merges siblings under parent **AST-358**. **AST-428** already **User Testing**. |
| advisory (`_effective_no_signal_for_score` docstring) | Docstring clarified: excludes literal **X** or **confidence 1** (not “F1” only). |

**Doc:** Radia review merged from `origin/sub/…` (`3145e013`). **Parent AST-358** — ready for **prep-uat** when all children **User Testing** or **Done**.
