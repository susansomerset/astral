# UAT: batch prefilter hydration fails on embedded RC vector

**Linear:** [AST-707](https://linear.app/astralcareermatch/issue/AST-707/uat-batch-prefilter-hydration-fails-on-embedded-rc-vector)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process)  
**Publish ref:** `origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration`

Batch **prefilter** on **HOMEPAGE_READY** companies: the LLM returns valid encoded lines (`000|RCD3|MPB3|USA3|...`), but **`_hydrate_response_jobs_grade_reasons`** raises **`No rubric criterion matching vector 'RC'`** (or **`'Reality Check'`** when labels resolve). Every company transitions to **WEBSITE_FOUND_RETRY** with **`total_errors=10`**. Susan removed **RC** from the candidate **`company_prefilter`** artifact (MP/US remain there); **Reality Check** must live in **`config.py`** as an embedded criterion merged at hydration/decode time. This ticket adds that registry and a single merge point — no fetch_website, AST-703 migration, or encoded decode contract changes.

**Root cause (verified in code):**

1. **`_rubric_criteria_from_cd(cd, "company_prefilter")`** reads **only** `candidate_data.artifacts.company_prefilter` (~108–114 in `consult.py`).
2. **`_vector_labels_from_ctx`** builds **`vector_labels`** from that same artifact-only list (~949–953 in `roster.py`). When **RC** is absent, **`_decode_payload`** falls back to code as vector name (`vector_labels.get(code, code)` → **`"RC"`**).
3. **`_lookup_rubric_reason_for_grade`** matches **`grades[].vector`** against criterion **`label`**, not **`code`** (~121–146). Missing embedded **RC** → hydration **`ValueError`** → batch failure path (~1316–1320 in `roster.py`).
4. **`_render_score`** would fail similarly on missing **Reality Check** in **`expected`** if hydration were bypassed (~494–505).

**Related (context only):** [AST-603](ast-603-consult-parity-hydration-for-prefilter-company.md) established hydration; [AST-702](ast-702-batch-prefilter-evaluate-phase.md) batch runner calls the same helpers.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** — canonical **RC** criterion row (code, label, importance, content, grade_descriptions A–F) | utils |
| `src/core/consult.py` | Merge embedded criteria into **`_rubric_criteria_from_cd`** when **`rubric_key == "company_prefilter"`** (embedded wins on duplicate **`code`**) | core |

**Tests (Betty — qa-child):** Engineer does **not** edit `tests/` or bible. Post **`[qa-handoff]`** if manifest omits regression below.

| File | Change | Layer |
|------|--------|-------|
| `tests/component/core/test_roster.py` | Regression: candidate artifact **without** RC + encoded **`RCD3`** batch response → hydration succeeds, per-company pass/fail (not all **WEBSITE_FOUND_RETRY**) | tests |

---

## Stage 1: Embedded RC registry in config

**Done when:** **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** is importable from **`config.py`**, contains exactly one **RC** row matching artifact criterion shape, and full **A–F** **`grade_descriptions`** so **`RCD3`** (and any letter) hydrates without **`ValueError`**.

1. In **`src/utils/config.py`**, immediately **after** the **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** assignment (~1035), add:

   ```python
   # AST-707: embedded company_prefilter vectors — merged before candidate artifact criteria (embedded wins on code).
   EMBEDDED_COMPANY_PREFILTER_CRITERIA: tuple[dict, ...] = (
       {
           "code": "RC",
           "label": "Reality Check",
           "importance": 5,
           "content": (
               "Reality Check — assess whether the company is real and operating as represented.\n"
               "A = clearly real and verifiable\n"
               "B = appears real with minor gaps\n"
               "C = mixed signals; legitimacy uncertain\n"
               "D = significant doubt about reality or representation\n"
               "E = strong evidence of misrepresentation\n"
               "F = not a real company or clearly fraudulent"
           ),
           "grade_descriptions": [
               {"grade": "A", "description": "Company is clearly real, active, and independently verifiable."},
               {"grade": "B", "description": "Company appears real with minor verification gaps."},
               {"grade": "C", "description": "Mixed signals; legitimacy uncertain."},
               {"grade": "D", "description": "Significant doubt the company is real or operating as represented."},
               {"grade": "E", "description": "Strong evidence of misrepresentation or shell entity."},
               {"grade": "F", "description": "Not a real company or clearly fraudulent."},
           ],
       },
   )
   ```

2. Do **not** add **RC** to **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** validation expectations for candidate save — embedded rows are not stored in **`candidate_data`**.

3. Do **not** change **`TASK_CONFIG`**, **`TOKEN_SOURCES`**, **`output_types`**, or **`prefilter_company`** orchestration keys in this stage.

   ⚠️ **Decision:** **RC** prose above is the canonical embedded hydration source (config-as-truth §2.1). Susan may edit **`content`** / **`grade_descriptions`** in **`config.py`** later without touching candidate artifacts; do **not** require duplicate **RC** rows in **Manage Tasks → Company Watch Criteria**.

---

## Stage 2: Merge embedded criteria at lookup time

**Done when:** All prefilter paths that call **`_rubric_criteria_from_cd(..., "company_prefilter")`** receive **embedded + artifact** criteria; **`_vector_labels_from_ctx`**, batch hydration (**`_run_batch_company_prefilter`** ~1281–1316), **`_apply_prefilter_decoded_company_outcome`** (~1060–1081), and **`_fetch_prefilter_notes`** (~2233) work when artifact lacks **RC** but encoded response includes **`RC*`** segments.

1. In **`src/core/consult.py`**, replace **`_rubric_criteria_from_cd`** (~108–114) with:

   ```python
   def _rubric_criteria_from_cd(cd: dict, rubric_key: Optional[str]) -> list:
       if not rubric_key:
           return []
       raw = (cd or {}).get("artifacts", {}).get(rubric_key)
       if isinstance(raw, list):
           artifact = raw
       else:
           artifact = (raw or {}).get("criteria") or []
       if rubric_key == "company_prefilter":
           from src.utils.config import EMBEDDED_COMPANY_PREFILTER_CRITERIA

           embedded_codes = {
               str(c.get("code")).strip()
               for c in EMBEDDED_COMPANY_PREFILTER_CRITERIA
               if isinstance(c, dict) and c.get("code")
           }
           tail = [
               c
               for c in artifact
               if isinstance(c, dict) and str(c.get("code") or "").strip() not in embedded_codes
           ]
           return list(EMBEDDED_COMPANY_PREFILTER_CRITERIA) + tail
       return artifact
   ```

2. Do **not** add a second merge helper in **`roster.py`** — **`_vector_labels_from_ctx`** already calls **`_rubric_criteria_from_cd`**; merged criteria automatically populate **`vector_labels["RC"] = "Reality Check"`** for **`_decode_payload`**.

3. Do **not** change **`_lookup_rubric_reason_for_grade`**, **`_hydrate_grade_reasons_from_rubric`**, **`_render_score`**, **`fetch_website`**, **`database.py`** AST-703 migration, or **`agent._decode_payload`** segment grammar.

4. Manual verification on epic worktree (Susan repro):
   - Candidate **`company_prefilter`** artifact with **MP** + **US** only (no **RC** row).
   - Run dispatch **prefilter** batch on **HOMEPAGE_READY** companies (or unit-test equivalent with mocked **`do_task`** returning **`000|RCD3|MPB3|USA3|...`** per row).
   - Confirm log has **no** `[prefilter_company_batch] grade reason hydration failed: No rubric criterion matching vector`.
   - Confirm companies receive independent **PREFILTER_PASSED** / **PREFILTER_FAILED** / legacy outcomes — **not** uniform **WEBSITE_FOUND_RETRY**.

   ⚠️ **Decision:** Embedded criteria **prepend** artifact criteria; on duplicate **`code`**, embedded row wins (artifact **RC** row ignored if Susan leaves a stale copy). Future embedded vectors append to **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** only — no per-call-site lists.

---

## Stage 3: Regression test (Betty)

**Done when:** Test fails on pre-fix code (artifact without **RC**, encoded **RC** grade) and passes after Stages 1–2.

1. Betty adds **`test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact`** (or adjacent **AST-603** / batch prefilter class) in **`tests/component/core/test_roster.py`**:
   - Build **`ctx`** with **`company_prefilter`** criteria **MP** + **US** only (no **RC**).
   - Mock **`do_task`** success with **`parsed_response.jobs`** containing encoded grades decoded to **`Reality Check` / D / 3** (via normal decode path with **`vector_labels`** from ctx).
   - Assert **`_run_batch_company_prefilter`** (or **`prefilter_company_batch`**) does **not** route all rows to **`WEBSITE_FOUND_RETRY`** via hydration failure; assert at least one row reaches a pass/fail outcome state.

Engineer: if Betty's **test-child** manifest omits this case, post **`[qa-handoff]`** on AST-707 citing this stage.

---

## Self-Assessment

### Scope — **Single-Component**

Two production files: one config constant block and one merge in **`_rubric_criteria_from_cd`**; all prefilter hydration/decode/score callers inherit via existing helper.

### Conf — **high**

Failure path traced to artifact-only rubric list + missing **`vector_labels["RC"]`**; fix matches ticket boundaries and existing AST-603 hydration pattern.

### Risk — **Medium**

Wrong merge order or incomplete **A–F** **`grade_descriptions`** would still fail batch hydration or produce empty **`prefilter_company_notes`** for some grades; contained to company prefilter — job consult rubrics unchanged.

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§2.1 config-as-truth:** Embedded **RC** lives as literals in **`config.py`**; not env vars, not duplicated in candidate artifact.
- **§1.3 DRY:** Single merge in **`_rubric_criteria_from_cd`** — no parallel lists in **`roster.py`** / **`agent.py`**.
- **§2.4 batch processing:** Batch runner unchanged except inputs to existing hydration helpers.
- **§2.6 state machine:** No new transitions — fixes erroneous **WEBSITE_FOUND_RETRY** routing on hydration errors.
- **§3.3 imports:** Lazy import of **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** inside **`company_prefilter`** branch avoids circular import at module load (same pattern as other consult config pulls).

No conflicts requiring plan revision.
