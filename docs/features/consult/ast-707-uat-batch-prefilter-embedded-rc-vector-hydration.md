# UAT: batch prefilter hydration fails on embedded RC vector

**Linear:** [AST-707](https://linear.app/astralcareermatch/issue/AST-707/uat-batch-prefilter-hydration-fails-on-embedded-rc-vector)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process) (AC #3 reference only — batch prefilter per-company outcomes)  
**Publish ref:** `origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration`

Susan UAT: batch **prefilter** on **HOMEPAGE_READY** companies succeeds at the LLM layer (`000|RCD3|MPB3|USA3|…`), but `_run_batch_company_prefilter` fails grade-reason hydration with `No rubric criterion matching vector 'RC'`, transitions every company to **WEBSITE_FOUND_RETRY**, and reports `total_errors=10`. **RC** (Reality Check) is a **global embedded vector** on every `prefilter_company` call — not stored in candidate `company_prefilter` artifacts. Hydration and decode `vector_labels` today use candidate artifact criteria only.

**Root cause (current code on `origin/ftr/AST-700-prefilter-as-batch-process`):**

1. `_vector_labels_from_ctx` builds `{code: label}` from `_rubric_criteria_from_cd(..., "company_prefilter")` only — when RC is absent from the artifact, `_decode_payload` leaves `grades[].vector` as the raw code `"RC"`.
2. `_run_batch_company_prefilter`, `_apply_prefilter_decoded_company_outcome`, and `_fetch_prefilter_notes` pass artifact-only `rubric_list` into `_hydrate_grade_reasons_from_rubric` / `_hydrate_response_jobs_grade_reasons`.
3. `_lookup_rubric_reason_for_grade` matches criterion **label** only (not **code**), so even a decoded label mismatch fails when the grade row carries `"RC"`.

**Out of scope:** `fetch_website` scrape phase, dispatch_tasks migration (**AST-703**), encoded link decode contract (**AST-697**), rubric prompt copy, admin UI, new DB columns.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `EMBEDDED_PREFILTER_RUBRIC_VECTORS` registry (RC criterion row) | utils |
| `src/core/consult.py` | Merge helper + code-aware rubric lookup for hydration/scoring | core |
| `src/core/roster.py` | Use merged criteria + merged `vector_labels` on all prefilter paths | core |

Betty may add a batch-prefilter hydration regression row in **astral-tests** (artifact without RC, encoded line with `RC*`) — engineer does **not** edit `tests/` or the bible.

---

## Stage 1: Embedded RC registry + merged rubric criteria

**Done when:** `EMBEDDED_PREFILTER_RUBRIC_VECTORS` exists in config with a complete RC criterion row; `_company_prefilter_rubric_criteria(cd)` returns embedded vectors prepended to artifact criteria (dedupe by `code`); `_lookup_rubric_reason_for_grade` and `_importance_for_label` resolve rows by **label or code**; `_vector_labels_from_ctx` includes embedded codes; all four roster prefilter call sites use the merged helper instead of raw `_rubric_criteria_from_cd(..., "company_prefilter")`.

1. **Before editing config**, on epic worktree, read Manage Tasks → **`prefilter_company`** → current `user_prompt` / `cache_prompt` and locate the **Reality Check (RC)** vector block (grade table + descriptions). That prompt text is canonical for embedded RC prose. If the block is missing or ambiguous, stop with 🛑 on **AST-700** — do not invent grade copy.

2. In `src/utils/config.py`, after `RUBRIC_CRITERIA_ARTIFACT_KEYS` (~1035), add:

   ```python
   # AST-707: global prefilter vectors — always graded; not duplicated in candidate artifacts.
   EMBEDDED_PREFILTER_RUBRIC_VECTORS: List[Dict[str, Any]] = [
       {
           "code": "RC",
           "label": "Reality Check",
           "importance": 8,
           "content": "<Reality Check rubric body copied from prefilter_company Manage Tasks prompt>",
           "grade_descriptions": [
               # One {"grade": "<letter>", "description": "<line from prompt grade table>"} per A–F
               # populated from step 1 — every letter the prompt defines must have a row
           ],
       },
   ]
   ```

   ⚠️ **Decision:** Single embedded vector **RC** only for this ticket. Future globals append to this list; do not scatter literals in roster/consult.

3. In `src/core/consult.py`, add:

   ```python
   def _company_prefilter_rubric_criteria(cd: dict) -> list:
       from src.utils.config import EMBEDDED_PREFILTER_RUBRIC_VECTORS
       artifact = _rubric_criteria_from_cd(cd, "company_prefilter")
       embedded_codes = {str(v.get("code") or "").upper() for v in EMBEDDED_PREFILTER_RUBRIC_VECTORS if v.get("code")}
       merged = list(EMBEDDED_PREFILTER_RUBRIC_VECTORS)
       for row in artifact:
           if str(row.get("code") or "").upper() in embedded_codes:
               continue
           merged.append(row)
       return merged
   ```

4. In `_lookup_rubric_reason_for_grade` (~121–146), when iterating `rubric_criteria`, treat a row as matching when **either** stripped `label` **or** uppercased `code` equals `target` (after `_strip_code` on the grade's vector string). Keep existing grade-description resolution unchanged once matched.

5. In `_importance_for_label` (~462–475), apply the same label-or-code match so `_render_score` works when `grades[].vector` is `"RC"` or `"Reality Check"`.

6. In `src/core/roster.py`, update `_vector_labels_from_ctx` to build labels from `_company_prefilter_rubric_criteria(cd)` instead of `_rubric_criteria_from_cd(cd, "company_prefilter")`.

7. In `src/core/roster.py`, replace artifact-only rubric fetches with `_company_prefilter_rubric_criteria((ctx or {}).get("candidate_data") or {})` at:
   - `_apply_prefilter_decoded_company_outcome` (~1060)
   - `_run_batch_company_prefilter` (~1281) — both `rubric_list` and rely on updated `_vector_labels_from_ctx` for `task_ctx["vector_labels"]`
   - `_fetch_prefilter_notes` (~2233) — use merged list from `cd` built there

8. Manual verification on epic worktree (Python REPL — do **not** commit):

   ```python
   from src.core.consult import _company_prefilter_rubric_criteria, _hydrate_grade_reasons_from_rubric
   cd = {"artifacts": {"company_prefilter": [
       {"code": "MP", "label": "Mission & Product", "importance": 5,
        "grade_descriptions": [{"grade": "B", "description": "ok mp"}]},
       {"code": "US", "label": "US Presence", "importance": 3,
        "grade_descriptions": [{"grade": "A", "description": "us ok"}]},
   ]}}
   rubric = _company_prefilter_rubric_criteria(cd)
   assert rubric[0]["code"] == "RC"
   grades = [{"vector": "RC", "grade": "D", "confidence": 3},
             {"vector": "Mission & Product", "grade": "B", "confidence": 3}]
   _hydrate_grade_reasons_from_rubric(grades, rubric)
   assert all(g.get("reason") for g in grades)
   ```

9. Manual verification (UAT repro path): with candidate artifact containing MP/US but **no RC**, run dispatch **prefilter** batch on **HOMEPAGE_READY** companies; confirm log shows no `[prefilter_company_batch] grade reason hydration failed`; companies reach **PREFILTER_PASSED** / **PREFILTER_FAILED** (or inflow equivalents), not wholesale **WEBSITE_FOUND_RETRY**.

---

## Execution contract

- Execute Stage 1 only; **one `code(AST-707)` commit** on epic worktree, then publish to **`origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration`** via `git push origin HEAD:sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration`.
- Do **not** edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`.
- Blocking ambiguity (missing RC prompt block, grade-table mismatch) → 🛑 comment on **AST-700** per plan-child execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — One config registry, two consult helpers/lookup tweaks, and roster prefilter rubric wiring; no dispatcher, data layer, or UI.

**Conf:** `high` — UAT log names the failing vector (`RC`); batch path and `_lookup_rubric_reason_for_grade` label-only match are confirmed in source; Susan's direction (config-held embedded vectors) is explicit in the ticket.

**Risk:** `Medium` — Touches prefilter hydration and scored `_render_score` for every company prefilter run; wrong merge or lookup would still mass-retry batches, but change is localized and manually verifiable with artifact-minus-RC fixture.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `_company_prefilter_rubric_criteria` + config list — no roster-local RC literals. |
| §2.1 config | Embedded RC lives in `config.py`; artifact rows stay candidate-owned. |
| §2.4 batch | Batch prefilter runner unchanged except criteria source — claim/decode/outcome flow preserved. |
| §2.6 state machine | No new states; fixes incorrect **WEBSITE_FOUND_RETRY** mass transition on hydration failure. |
| §3.3 imports | Keep existing roster pattern (`from src.core.consult import …` at function scope). |
| §3.5 naming | `EMBEDDED_PREFILTER_RUBRIC_VECTORS` / `_company_prefilter_rubric_criteria` match existing rubric naming. |

No conflicts requiring `!!-NONE`.
