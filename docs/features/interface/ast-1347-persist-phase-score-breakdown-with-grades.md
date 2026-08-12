# Persist phase score breakdown with grades

**Linear:** [AST-1347](https://linear.app/astralcareermatch/issue/AST-1347/persist-phase-score-breakdown-with-grades-add-rubric-score-to-analysis)  
**Parent:** [AST-1346 — Add rubric score to analysis header](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header)  
**Publish ref (origin):** `sub/AST-1346/AST-1347-persist-phase-score-breakdown`  
**Parent integration ref:** `ftr/AST-1346-add-rubric-score-to-analysis-header`  
**Blocks:** [AST-1348](https://linear.app/astralcareermatch/issue/AST-1348/analysis-header-score-title-chrome-add-rubric-score-to-analysis) (header chrome reads stored trio; derive-at-read when absent)

Compute **earned / possible / max** with the same per-vector contribution math already used at grade time (`_render_score` in `consult.py`), persist that trio on `job_data` beside the phase’s grades and 0–10 `{prefix}_score` at score-save time, and lift the fields on job list/detail payloads. Does **not** own Analysis header title chrome (AST-1348). Does **not** change 0–10 `{prefix}_score` semantics, pass/fail, Recommended list phase-score columns, or dispatch soft-fail. Does **not** backfill historical jobs or implement read-time derive (sibling).

Parent brief example numbers (`137 out of 150 possible (320 max total)`) are **format-only** — real values come from current contribution math (`RUBRIC_TOTAL`, grade density, importance, confidence).

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree `/home/susan/astral-AST-1346`: run  
   `~/.cursor/scripts/git/sync-child.sh sub/AST-1346/AST-1347-persist-phase-score-breakdown --ftr AST-1346 --worktree /home/susan/astral-AST-1346/`  
   and require exit 0. (`origin/ftr/AST-1346-…` may still be unpublished — sync-child skips missing ftr; that is OK until Chuckles publishes parent ftr.)
2. Do **not** implement AST-1348 header chrome on this ref.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add breakdown key suffix + field-name tuple for the persisted trio shape | utils |
| `src/core/consult.py` | Extract contribution breakdown helper; reuse from `_render_score`; persist `{prefix}_score_breakdown` on Analysis-phase score saves (jd / do / get / like) | core |
| `src/ui/api/api_jobs.py` | Lift `{jd,do,get,like}_score_breakdown` in `_flatten_grades` (list + detail) | ui |

**Out of scope:** React / Analysis header title chrome (AST-1348); read-time derive when trio absent (AST-1348); `joblist_*` qualify path; Recommended list Score column UI; changing `{prefix}_score` / `latest_score` / score_floor behavior; historical backfill; `tests/` / bible (Betty).

**Contract for AST-1348 (consume only — do not implement here):**

| Phase | Grades key | 0–10 score key (unchanged) | New breakdown key |
|-------|------------|----------------------------|-------------------|
| JD | `jd_grades` | `jd_score` | `jd_score_breakdown` |
| DO | `do_grades` | `do_score` | `do_score_breakdown` |
| GET | `get_grades` | `get_score` | `get_score_breakdown` |
| LIKE | `like_grades` | `like_score` | `like_score_breakdown` |

Naming: `{save_prefix}_score_breakdown` (parallel to `{save_prefix}_score` / `{save_prefix}_rubric` from AST-1063).

Each breakdown value is a **dict**:

```python
{
  "earned": float,    # sum of contributions for counted (non-no-signal) vectors
  "possible": float,  # max attainable among counted vectors only
  "max": float,       # max attainable if every analysis-time vector had full signal
}
```

- Absent key = pre-AST-1347 job (sibling derives at read).
- Do **not** write the key when that phase has no scorable numeric score (same gate as writing `{prefix}_score` — e.g. F2 dealbreaker path that stores no score).

**QA note (Betty):** After land, assert a fresh scored write for jd/do/get/like persists `*_score_breakdown` with the three floats beside grades/score/rubric; assert F2 / unscored path omits the key; assert `_flatten_grades` lifts it; assert `*_score` / list phase-score / soft-fail unchanged. Historical fixture: key absent.

---

## Stage 1: Config constants for breakdown shape

**Done when:** `config.py` exposes a single suffix and the three dict field names used by consult + API; no product behavior change yet.

1. In `src/utils/config.py`, near `GRADE_VALUES` / `RUBRIC_TOTAL` / `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS` (scoring / jobs-UI block — pick the scoring constants area beside `RUBRIC_TOTAL`), add:

   ```python
   # AST-1347 — job_data phase contribution breakdown beside {prefix}_score
   PHASE_SCORE_BREAKDOWN_KEY_SUFFIX = "score_breakdown"  # → f"{prefix}_score_breakdown"
   PHASE_SCORE_BREAKDOWN_FIELDS = ("earned", "possible", "max")
   ```

2. Do **not** add these fields to `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS` (list Score columns stay 0–10 only — parent AC6 / child AC4).

⚠️ **Decision:** Nested `{prefix}_score_breakdown` object rather than three top-level floats — keeps the trio atomic for sibling chrome and avoids proliferating flatten keys beyond one per phase.

---

## Stage 2: Contribution breakdown helper + wire into `_render_score`

**Done when:** A pure helper returns `{earned, possible, max}` using the same contribution formula `_render_score` uses today; `_render_score`’s 0–10 result is numerically unchanged for the same inputs (earned drives normalization); F2 dealbreaker still returns `(fail_state, None)` with no breakdown call required by callers.

1. In `src/core/consult.py`, immediately above `_render_score`, add:

   ```python
   def _phase_score_breakdown(
       rubric_criteria: list,
       grades: list,
   ) -> dict:
       """Earned / possible / max contribution totals (AST-1347).

       Uses the same per-vector math as _render_score (base × density × importance).
       No-signal rows (_effective_no_signal_for_score) are excluded from earned and
       possible (and from the counted denominator). Max uses full grade-set capacity
       (every vector, including no-signal slots) at density 1.0.
       """
   ```

2. Behavior (exact — do not invent a second formula):

   - Caller must already have enforced a complete grade set (`_require_complete_grade_set`) when used from `_render_score` / score-save paths. The helper itself does **not** re-check completeness and does **not** apply F2 dealbreaker logic.
   - `counted = [g for g in grades if not _effective_no_signal_for_score(g)]` (same predicate as today).
   - `n_all = len(grades)`; `n_counted = len(counted)`.
   - `base_counted = float(RUBRIC_TOTAL) / n_counted` when `n_counted > 0`, else unused for earned/possible loops.
   - `base_all = float(RUBRIC_TOTAL) / n_all` when `n_all > 0`, else `0.0`.
   - For each counted grade `g`:
     - Resolve `conf` / `m` / `gv` / `density` / `imp` exactly as `_render_score` does today (`CONFIDENCE_MULTIPLIERS`, `grade_value`, `MAX_GRADE_VALUE`, `_importance_for_label`). Same `ValueError`s on bad confidence.
     - `earned += base_counted * density * imp`
     - `possible += base_counted * 1.0 * imp`  (full signal = density 1.0, i.e. A × confidence multiplier 1.0)
   - When `n_counted == 0`: `earned = 0.0`, `possible = 0.0` (same as today’s empty counted path before normalization).
   - For **every** grade row in `grades` (including no-signal):  
     `max_total += base_all * 1.0 * _importance_for_label(rubric_criteria, g["vector"])`  
     When `n_all == 0`: `max_total = 0.0`.
   - Return `{"earned": earned, "possible": possible, "max": max_total}` using exactly the keys in `PHASE_SCORE_BREAKDOWN_FIELDS` (import those names from config; build the dict with those keys — do not hardcode alternate spellings).

3. Refactor `_render_score` scored path (after F2 early-return and `_require_complete_grade_set`):

   - Call `breakdown = _phase_score_breakdown(rubric_criteria, grades)`.
   - Set `rubric_score = breakdown["earned"]` (or `breakdown[PHASE_SCORE_BREAKDOWN_FIELDS[0]]` if indexing by the config tuple — prefer the `"earned"` key via the config constant’s first element or a local bind `earned_key = PHASE_SCORE_BREAKDOWN_FIELDS[0]`).
   - Keep `score = (rubric_score / float(RUBRIC_TOTAL)) * 10.0` and the existing score_floor / pass-state branches unchanged.
   - Keep existing `debug_detail` contribution logging: either move the per-vector debug lines into `_phase_score_breakdown` (gated the same way — only when the logger debug flag is already on / existing pattern) **or** retain a thin loop in `_render_score` that only logs. Prefer moving the math+debug into the helper so there is one loop. Do **not** change debug contract semantics (still only when debug is on via existing helpers).
   - `_render_score` return type stays `Tuple[str, Optional[float]]` — do **not** change callers to receive the breakdown from `_render_score`. Callers that need the trio call `_phase_score_breakdown` separately (cheap; same inputs) **or** compute once in the save path after a successful numeric score (see Stage 3). Prefer: compute once in the save path after `_render_score` returns a non-`None` score, calling `_phase_score_breakdown` again — two passes is OK at plan fidelity; if the implementer wants a single pass, they may have `_render_score` stash nothing and still call the helper twice, **or** extract an internal `_render_score_with_breakdown` used only by the two save sites — **allowed optimization inside Stage 2/3 as long as public `_render_score` signature and 0–10 results are unchanged**. Default instruction: call `_phase_score_breakdown` from `_render_score` for earned, and again at persist sites when writing the key (clear, small duplication).

⚠️ **Decision:** Max uses `base_all = RUBRIC_TOTAL / len(grades)` while earned/possible use `base_counted = RUBRIC_TOTAL / len(counted)` — matches parent wording that no-signal rows leave the possible denominator but still count toward max capacity. Do **not** keep a single base for all three totals.

⚠️ **Decision:** Full-signal density is exactly `1.0` (A + confidence multiplier 1.0), not a second config table — same ceiling already implied by `MAX_GRADE_VALUE` and `CONFIDENCE_MULTIPLIERS[5]`.

---

## Stage 3: Persist breakdown on Analysis-phase score saves

**Done when:** Fresh scored writes for **jd / do / get / like** store `{prefix}_score_breakdown` beside grades/score/rubric when `{prefix}_score` is written; dealbreaker / unscored paths omit the key; `joblist_*` qualify path is untouched; 0–10 score and transitions unchanged.

1. **`_apply_render_verdict_decoded_job`** (do / get / like and meteorite variants that share this path):

   - After the existing block that may set `save_data[f"{prefix}_score"]`, if that key was set on `save_data` in this call, also set:

     ```python
     save_data[f"{prefix}_{PHASE_SCORE_BREAKDOWN_KEY_SUFFIX}"] = _phase_score_breakdown(
         rubric_criteria, grades
     )
     ```

   - Use the same `rubric_criteria` and `grades` already in hand for scoring (job-carried rubric law — analysis-time criteria, not a live re-fetch after score).
   - If `{prefix}_score` was **not** written (binary mode, F2 → `score is None`, etc.), do **not** write the breakdown key.
   - Keep existing `{prefix}_rubric` / notes / transition behavior.

2. **`evaluate_jd_batch` `process`**:

   - Same rule: when `jd_score` is written onto `save_data`, also write `jd_score_breakdown` via `_phase_score_breakdown(rubric_list, grades)`.
   - When `jd_score` is omitted (e.g. F2 → `score is None`), omit breakdown.

3. **Do not** modify `qualify_job_listings` / `joblist_*` saves — not an Analysis-tab phase for this epic.

4. **Do not** backfill historical `job_data`.

5. **Do not** change `_transition_job_state_for_task`, score_floor soft-fail, or `{prefix}_score` numeric values.

---

## Stage 4: API flatten lift

**Done when:** List and detail job JSON expose `jd_score_breakdown`, `do_score_breakdown`, `get_score_breakdown`, `like_score_breakdown` when present on `job_data`, via the same `_flatten_grades` path used for grades/scores/rubrics. Recommended list still returns unchanged `*_score` fields for phase-score columns.

1. In `src/ui/api/api_jobs.py` `_flatten_grades`, extend the existing key loop to also lift:

   ```text
   jd_score_breakdown, do_score_breakdown, get_score_breakdown, like_score_breakdown
   ```

   Prefer building those four strings from prefixes `("jd", "do", "get", "like")` + `PHASE_SCORE_BREAKDOWN_KEY_SUFFIX` imported from config (avoids a second hardcoded parallel list). If importing that constant into `api_jobs` is awkward for the existing import style, adding the four literal keys beside the current `*_rubric` entries is acceptable **only if** they match the config suffix exactly — document the match in a one-line comment `# AST-1347: {prefix}_score_breakdown`.

2. Do **not** compute or invent breakdowns in the API when absent (sibling derive).
3. Do **not** alter `latest_score` / `joblist_score` fallback behavior.
4. Detail route already uses `_flatten_grades` — no second path.

⚠️ **Decision:** Lift on API (not React digging `job_data`) — same import-direction pattern as AST-1063.

---

## Stage 5: Manual smoke (builder)

**Done when:** A throwaway call shows a scored phase write persists the trio and flatten lifts it; an F2-style unscored path omits it; `*_score` values match pre-change expectations for a fixed grade fixture.

1. Optional gitignored spike under `debug/spikes/AST-1347/` that:
   - Builds a small rubric + grades mix (some X / conf-1, some letter grades).
   - Calls `_phase_score_breakdown` and `_render_score` and prints earned/possible/max + 0–10 score.
   - Confirms `score ≈ (earned / RUBRIC_TOTAL) * 10`.
2. Do not commit spike output. No React work.

---

## Self-Assessment

**Scope:** `Single-Component` — consult score-save + config constants + `api_jobs` flatten; no header UI.

**Conf:** `Medium` — write sites are the same two Analysis paths as AST-1063’s jd/verdict saves; math is a structured extract of existing `_render_score`, but max-vs-possible denominator split is new product surface for the sibling.

**Risk:** `Medium` — wrong denominator for max/possible would mis-label header chrome later; missing a save site leaves that phase without stored trio (sibling can still derive). Mitigated by binding helper to `_render_score` earned path and mirroring the `{prefix}_score` write gate.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One breakdown helper; `_render_score` reuses earned; two persist call sites (verdict + evaluate_jd).
- **§1.4 / §2.1 config:** Breakdown field names + key suffix live in `config.py`; grade/confidence/importance constants unchanged.
- **§2.3 grade / confidence:** No change to valid grade set or no-signal rules — reuse `_effective_no_signal_for_score`.
- **§2.7 render_verdict:** Persist beside existing save_prefix grades/score/rubric write; orchestration untouched.
- **§3.3 import-direction:** API lifts stored keys only; does not import consult or recompute.
- **Job-carried rubric law (AST-1063):** Breakdown uses the same analysis-time `rubric_criteria` / `rubric_list` already used for scoring in that save — never live candidate rubric at read in this ticket.

---

## Estimate

Confirm Chuckles estimate: 3 — agree

---

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1347
**Overall:** APPROVED
**Publish ref:** `sub/AST-1346/AST-1347-persist-phase-score-breakdown` @ `d405dad3852eadabb06f5ccb93f50743ea6d46b3`

## Traceability
AC3 → Stages 2–3 (`_phase_score_breakdown` extract + persist `{prefix}_score_breakdown` on jd/do/get/like score-save paths in `_apply_render_verdict_decoded_job` and `evaluate_jd_batch`); AC4 → Stage 1 (explicit exclusion from `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS`), Stages 3–4 (no `{prefix}_score` / `latest_score` / score_floor / soft-fail changes; API lift only).

## Findings

### acceptable — Stage 2/3 double `_phase_score_breakdown` call
**Location:** Stage 2 refactor + Stage 3 persist sites  
**Finding:** Plan allows calling the helper twice (once inside `_render_score` for earned, again at persist) for clarity; small duplicate loop at save time.  
**Recommendation:** Accept as written; optional single-pass internal helper is implementer optimization only — must not change `_render_score` signature or 0–10 output.

### discuss — all-no-signal edge (`n_counted == 0`)
**Location:** Stage 2 `_phase_score_breakdown` behavior  
**Finding:** When every vector is no-signal, plan sets `earned=possible=0.0` while `_render_score` may still emit numeric `0.0` and persist `{prefix}_score`, so breakdown may show `0/0` with a non-zero `max`.  
**Recommendation:** Persist behavior matches existing score-save gate; AST-1348 owns whether header suffix appears — no plan change required here.

**R6 checklist:** Definition fidelity ✓ (child scope matches AST-1347 description; header chrome / derive-at-read correctly deferred to AST-1348). Layer imports ✓ (`core`→utils; `ui/api` lifts stored keys only, no consult import). Config ✓ (suffix + field tuple in `config.py`). File placement ✓ (no new dirs). Patterns ✓ (`pattern.config.config-block`; import-direction lift mirrors AST-1063 rubric/score flatten). DRY ✓ (single helper bound to existing `_render_score` math). Boundaries ✓ (no React, no qualify/joblist path, no backfill, no 0–10 semantic change). Self-assessment ✓ (Medium conf honest; save sites and max/possible denominator split called out).

**Statute pass (in-session):** Universal orch set — conforms (plan-is-bible, git topology via prerequisite gate, Betty owns tests). Scoped applies — `astral.layers.import-direction`, `astral.config.config-source-of-truth`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.standards.dry-and-focused-functions`, `astral.agent.grade-vector-validation`, `astral.idioms.render-verdict-orchestrates-consult`, `astral.docs.features-single-file-per-ticket` — all **conforms**. No R3 `violates`; no R5 gaps on child AC 3–4.

**Procedural (Chuckles):** Ticket status `Plan Ready` ✓; assignee is Ada (not Joan) — Chuckles should assign Joan before spawn in future; validation proceeded per spawn command.

context_tokens≈32000
```
