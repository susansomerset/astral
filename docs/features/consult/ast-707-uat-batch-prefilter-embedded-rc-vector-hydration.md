<!-- linear-archive: AST-707 archived 2026-06-23 -->

## Linear archive (AST-707)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-707/uat-batch-prefilter-hydration-fails-on-embedded-rc-vector  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-700 — prefilter as batch process  
**Blocked by / blocks / related:** parent: AST-700; related: AST-700

### Description

## What failed

Batch **prefilter** on **HOMEPAGE_READY** companies: LLM returns valid encoded payload with **RC** grades (e.g. `000|RCD3|MPB3|USA3|...`), but grade-reason hydration errors `No rubric criterion matching vector 'RC'`. All companies transition to **WEBSITE_FOUND_RETRY**; batch summary shows `total_errors=10`.

Susan fixed candidate **company_prefilter** rubric for MP/US vectors; **RC** (Reality Check) is an embedded rubric vector in [**config.py**](<http://config.py>) that applies on every call regardless of candidate artifact.

## Expected

Hydration resolves **RC** (and other embedded/global rubric vectors defined in [**config.py**](<http://config.py>)) before failing on candidate artifact criteria. Batch prefilter completes with per-company pass/fail outcomes per today's prefilter semantics.

## Repro

1. Ensure candidate **company_prefilter** artifact has MP/US (and other non-embedded) vector codes configured.
2. Run dispatch **prefilter** batch on 10 **HOMEPAGE_READY** companies.
3. Observe LLM success + encoded lines containing **RC** grades.
4. Observe `grade reason hydration failed: No rubric criterion matching vector 'RC'` and all companies → **WEBSITE_FOUND_RETRY**.

## Parent AC (quoted inline)

> 3. Multiple companies in **HOMEPAGE_READY** can be claimed in one dispatch batch and evaluated in a **single** agent call; each company receives an independent pass/fail outcome and state transition matching today's prefilter semantics.

## Boundaries

* This bug does **not** change: fetch_website scrape phase, dispatch_tasks migration (AST-703), or encoded link decode contract.
* Add embedded vector registry in [**config.py**](<http://config.py>) (importance, code, title, rubric options) and extend hydration lookup to consult it — do not require Susan to duplicate RC in every candidate artifact.

### Comments

#### hedy — 2026-06-16T19:10:34.377Z
## Radia review (FIX-UAT retroactive) — `origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration`

**Git:** publish ref ≡ `origin/dev` @ `e2ac4afb` (`merge-tests`); product diff **`eb5a38b1..c4a25ee1`** (`config.py` + `consult.py`).

### Plan fidelity

| Stage | Verdict |
|-------|---------|
| 1 — `EMBEDDED_COMPANY_PREFILTER_CRITERIA` in `config.py` | ✓ RC row with code, label, importance 8, content, A–F `grade_descriptions` |
| 2 — merge in `_rubric_criteria_from_cd`; code-aware `_lookup_rubric_reason_for_grade` + `_importance_for_label` | ✓ embedded prepends artifact; dedupe by code; label **or** code match |
| 3 — Betty batch regression | ✓ manifest + `TestAst707EmbeddedRcBatchHydration` on `origin/tests` @ `bc6469de` |

Self-assessment (**Single-Component**, **high** conf, **Medium** risk) matches the diff footprint. Boundaries respected — no roster/dispatch/decode contract changes.

### ASTRAL_CODE_RULES

| Check | Result |
|-------|--------|
| §1.3 DRY / §2.1 config | ✓ single registry + one merge site |
| §2.4 batch / §2.6 transitions | ✓ criteria source only; no claim/clear or state-machine edits |
| §3.3 layer | ✓ core → utils only |
| B1 lazy import (`consult.py` ~117) | **Advisory:** function-scoped `EMBEDDED_*` import could move to the existing top-level `config` import block — not blocking |
| D2 silent failure / E1 print / §5f debug | N/A — untouched |

### Code quality

Focused UAT fix: addresses root cause (artifact-only rubric list + label-only lookup when decode emits raw `"RC"`). Merge order (embedded wins on duplicate code) matches plan decision.

**fix-now:** none

**discuss:** none

**Advisory:** Stage 1 plan asked for Manage Tasks RC prose when available; shipped literals match plan fallback — fine for UAT; optional follow-up to sync copy from live prompt DB.

**Status:** left at **User Testing** (FIX-UAT fast path — retroactive sign-off only; no `Review Posted` regression).

— Radia

#### betty — 2026-06-16T19:08:22.722Z
Bible shasum correction (`origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration` @ `e2ac4afb`):

- `docs/test-bible/core/consult.md`: `932a247341537d5638138be65e85e0bd9edb7e6b`
- `docs/test-bible/core/roster.md`: `a3903e98718e45ca67acbc326c5ea0075c8ad977`
- `docs/test-bible/utils/config.md`: `e2187edce09d88f4fba2051c19bbb37a3ef2e895`

— Betty

#### betty — 2026-06-16T19:07:51.673Z
## QA test manifest (AST-707)

**Publish ref:** `origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration` @ `e2ac4afb` (`merge-tests(AST-707): origin/tests bc6469de`)

### 1. Existing coverage (bible-backed)

| # | Area | Run |
|---|------|-----|
| 1 | **AST-603** prefilter hydration baseline | `tests/component/core/test_roster.py::TestAst603ConsultParityHydration` |
| 2 | **AST-702** batch runner smoke | `tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch::test_batch_pass_and_fail_counts` |

### 2. New / revised tests (this pass)

| # | Area | Run |
|---|------|-----|
| 3 | Embedded **RC** registry | `tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig` |
| 4 | **`_rubric_criteria_from_cd`** prepends embedded **RC**; dedupes artifact **RC** | `tests/component/core/test_consult.py::TestRubricHelpers::test_merges_embedded_rc_for_company_prefilter` |
| 5 | Hydration by **code** when artifact omits **RC** | `tests/component/core/test_consult.py::TestRubricHelpers::test_hydrates_rc_by_code_without_artifact_row` |
| 6 | **`_lookup_rubric_reason_for_grade`** code match | `tests/component/core/test_consult.py::TestRubricLookup::test_matches_criterion_by_code` |
| 7 | **`_importance_for_label`** code match | `tests/component/core/test_consult.py::TestImportanceForLabelBranches::test_importance_matches_by_code` |
| 8 | Batch prefilter UAT repro — artifact **MP/US** only, post-decode **Reality Check** grades, no mass **WEBSITE_FOUND_RETRY** | `tests/component/core/test_roster.py::TestAst707EmbeddedRcBatchHydration::test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact` |

### 3. Narrowed run (manifest)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig \
  tests/component/core/test_consult.py::TestRubricHelpers::test_merges_embedded_rc_for_company_prefilter \
  tests/component/core/test_consult.py::TestRubricHelpers::test_hydrates_rc_by_code_without_artifact_row \
  tests/component/core/test_consult.py::TestRubricLookup::test_matches_criterion_by_code \
  tests/component/core/test_consult.py::TestImportanceForLabelBranches::test_importance_matches_by_code \
  tests/component/core/test_roster.py::TestAst707EmbeddedRcBatchHydration::test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact
```

### Bible shasum (`origin/sub/…` @ `e2ac4afb`)

- `docs/test-bible/core/consult.md`: `932a247341537d5638138be65e85e0bd9edb7e6b`
- `docs/test-bible/core/roster.md`: `a3903e98718e45ca67acbc326c5ea0075c8ad977`
- `docs/test-bible/utils/config.md`: `e2187edce09d88f4fba2051c19bbb37a3ef2e895`

— Betty

#### hedy — 2026-06-16T19:03:31.894Z
**Plan doc:** [`docs/features/consult/ast-707-uat-batch-prefilter-embedded-rc-vector-hydration.md`](https://github.com/susansomerset/astral/blob/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration/docs/features/consult/ast-707-uat-batch-prefilter-embedded-rc-vector-hydration.md) @ `e5451597`

**Self-assessment**
- **Scope:** Single-Component — `config.py` embedded RC registry + `consult.py` merge in `_rubric_criteria_from_cd` and label/code-aware hydration lookup; roster inherits existing helper calls.
- **Conf:** high — UAT error names missing `RC`; root cause is artifact-only rubric list + label-only `_lookup_rubric_reason_for_grade` when decode emits raw code.
- **Risk:** Medium — prefilter hydration and `_render_score` on every company batch; wrong merge still mass-retries, but localized and REPL/UAT verifiable.

**Stages:** (1) `EMBEDDED_COMPANY_PREFILTER_CRITERIA` with full A–F grade rows; (2) merge + code-aware lookup; (3) Betty batch regression when artifact lacks RC.

#### hedy — 2026-06-16T19:01:56.986Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration/docs/features/consult/ast-707-uat-batch-prefilter-embedded-rc-vector-hydration.md

**Scope:** Single-Component — config embedded RC registry, consult merge/lookup helpers, roster prefilter rubric wiring.

**Conf:** high — UAT names failing vector RC; batch hydration uses artifact-only criteria and label-only lookup; Susan direction is explicit.

**Risk:** Medium — prefilter hydration/scoring hot path; wrong merge still mass-retries batches, but localized and manually verifiable.

---

# UAT: batch prefilter hydration fails on embedded RC vector

**Linear:** [AST-707](https://linear.app/astralcareermatch/issue/AST-707/uat-batch-prefilter-hydration-fails-on-embedded-rc-vector)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process) (AC #3 reference only — batch prefilter per-company outcomes)  
**Publish ref:** `origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration`

Susan UAT: batch **prefilter** on **HOMEPAGE_READY** companies succeeds at the LLM layer (`000|RCD3|MPB3|USA3|…`), but `_run_batch_company_prefilter` fails grade-reason hydration with `No rubric criterion matching vector 'RC'`, transitions every company to **WEBSITE_FOUND_RETRY**, and reports `total_errors=10`. **RC** (Reality Check) is a **global embedded vector** on every `prefilter_company` call — not stored in candidate `company_prefilter` artifacts. Hydration and decode `vector_labels` today use candidate artifact criteria only.

**Root cause (current code on `origin/ftr/AST-700-prefilter-as-batch-process`):**

1. `_vector_labels_from_ctx` builds `{code: label}` from `_rubric_criteria_from_cd(..., "company_prefilter")` only — when RC is absent from the artifact, `_decode_payload` leaves `grades[].vector` as the raw code `"RC"`.
2. `_run_batch_company_prefilter`, `_apply_prefilter_decoded_company_outcome`, and `_fetch_prefilter_notes` pass artifact-only `rubric_list` into `_hydrate_grade_reasons_from_rubric` / `_hydrate_response_jobs_grade_reasons`.
3. `_lookup_rubric_reason_for_grade` matches criterion **label** only (not **code**), so hydration fails when the grade row carries `"RC"` instead of `"Reality Check"`.
4. `_render_score` would fail similarly on missing **Reality Check** in **`expected`** if hydration were bypassed.

**Out of scope:** `fetch_website` scrape phase, dispatch_tasks migration (**AST-703**), encoded link decode contract (**AST-697**), rubric prompt copy refresh, admin UI, new DB columns.

**Related (context only):** [AST-603](ast-603-consult-parity-hydration-for-prefilter-company.md); [AST-702](ast-702-batch-prefilter-evaluate-phase.md).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** — canonical **RC** criterion row | utils |
| `src/core/consult.py` | Merge embedded criteria in **`_rubric_criteria_from_cd`** when **`rubric_key == "company_prefilter"`**; extend **`_lookup_rubric_reason_for_grade`** and **`_importance_for_label`** to match **label or code** | core |

**Tests (Betty — qa-child):** Engineer does **not** edit `tests/` or bible. Post **`[qa-handoff]`** if manifest omits regression below.

| File | Change | Layer |
|------|--------|-------|
| `tests/component/core/test_roster.py` | Regression: artifact without **RC** + encoded **`RCD3`** batch path → hydration succeeds, not mass **WEBSITE_FOUND_RETRY** | tests |

---

## Stage 1: Embedded RC registry in config

**Done when:** **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** exists in **`config.py`** with a complete **RC** row (code, label, importance, content, **A–F** **`grade_descriptions`**).

1. **Before editing config**, on epic worktree, read Manage Tasks → **`prefilter_company`** → current `user_prompt` / `cache_prompt` and locate the **Reality Check (RC)** vector block (grade table + descriptions). Use that prose for **`content`** and **`grade_descriptions`** when present. If the block is missing or ambiguous, use the literals in step 2 and post a Linear comment on **AST-707** noting prompt copy was unavailable — do **not** block build on prompt DB access failure.

2. In **`src/utils/config.py`**, immediately **after** **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** (~1035), add:

   ```python
   # AST-707: embedded company_prefilter vectors — merged before candidate artifact criteria (embedded wins on code).
   EMBEDDED_COMPANY_PREFILTER_CRITERIA: tuple[dict, ...] = (
       {
           "code": "RC",
           "label": "Reality Check",
           "importance": 8,
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

   Replace **`content`** / **`grade_descriptions`** with Manage Tasks copy from step 1 when available (every letter the prompt defines must have a row).

3. Do **not** add **RC** to candidate-save validation as a required artifact row — embedded rows are not stored in **`candidate_data`**.

4. Do **not** change **`TASK_CONFIG`**, **`TOKEN_SOURCES`**, or encoded decode grammar in this stage.

   ⚠️ **Decision:** Single embedded vector **RC** only for this ticket. Future globals append to **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`**; do not scatter RC literals in roster/agent.

---

## Stage 2: Merge embedded criteria + code-aware hydration lookup

**Done when:** All callers of **`_rubric_criteria_from_cd(..., "company_prefilter")`** receive embedded + artifact criteria; **`_vector_labels_from_ctx`** includes **`RC`**; hydration and **`_render_score`** succeed when artifact lacks **RC** but grades carry **`"RC"`** or **`"Reality Check"`**.

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
               str(c.get("code")).strip().upper()
               for c in EMBEDDED_COMPANY_PREFILTER_CRITERIA
               if isinstance(c, dict) and c.get("code")
           }
           tail = [
               c
               for c in artifact
               if isinstance(c, dict) and str(c.get("code") or "").strip().upper() not in embedded_codes
           ]
           return list(EMBEDDED_COMPANY_PREFILTER_CRITERIA) + tail
       return artifact
   ```

   Do **not** add a parallel merge helper in **`roster.py`** — **`_vector_labels_from_ctx`**, batch runner, and coat-check paths already call **`_rubric_criteria_from_cd`**.

2. In **`_lookup_rubric_reason_for_grade`** (~125–129), treat a criterion row as matching when **either** stripped **`label`** **or** uppercased **`code`** equals **`target`** (after **`_strip_code`** on the grade's vector string). Keep existing grade-description resolution unchanged once matched.

3. In **`_importance_for_label`** (~465–469), apply the same label-or-code match so **`_render_score`** works when **`grades[].vector`** is **`"RC"`** or **`"Reality Check"`**.

4. Do **not** change **`fetch_website`**, **`database.py`** AST-703 migration, or **`agent._decode_payload`** segment grammar.

5. Manual verification (Python REPL — do **not** commit):

   ```python
   from src.core.consult import _rubric_criteria_from_cd, _hydrate_grade_reasons_from_rubric
   cd = {"artifacts": {"company_prefilter": [
       {"code": "MP", "label": "Mission & Product", "importance": 5,
        "grade_descriptions": [{"grade": "B", "description": "ok mp"}]},
       {"code": "US", "label": "US Presence", "importance": 3,
        "grade_descriptions": [{"grade": "A", "description": "us ok"}]},
   ]}}
   rubric = _rubric_criteria_from_cd(cd, "company_prefilter")
   assert rubric[0]["code"] == "RC"
   grades = [{"vector": "RC", "grade": "D", "confidence": 3},
             {"vector": "Mission & Product", "grade": "B", "confidence": 3}]
   _hydrate_grade_reasons_from_rubric(grades, rubric)
   assert all(g.get("reason") for g in grades)
   ```

6. Manual verification (UAT repro): candidate artifact with **MP/US** only, dispatch **prefilter** batch on **HOMEPAGE_READY** companies; confirm no `[prefilter_company_batch] grade reason hydration failed`; companies reach pass/fail outcomes, not wholesale **WEBSITE_FOUND_RETRY**.

   ⚠️ **Decision:** Embedded criteria **prepend** artifact rows; on duplicate **`code`**, embedded wins. Code-aware lookup is belt-and-suspenders when decode still emits raw **`"RC"`** before **`vector_labels`** refresh.

---

## Stage 3: Regression test (Betty)

**Done when:** Test fails on pre-fix code and passes after Stages 1–2.

1. Betty adds **`test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact`** in **`tests/component/core/test_roster.py`**:
   - **`ctx`** with **`company_prefilter`** **MP** + **US** only (no **RC**).
   - Mock **`do_task`** returning encoded batch response with **`RCD3`** (or grades with **`vector: "RC"`**).
   - Assert batch prefilter does **not** mass-transition to **WEBSITE_FOUND_RETRY** on hydration failure.

Engineer: post **`[qa-handoff]`** on AST-707 if Betty's manifest omits this case.

---

## Self-Assessment

### Scope — **Single-Component**

Two production modules: config registry plus consult merge/lookup tweaks; roster inherits via existing **`_rubric_criteria_from_cd`** calls — no roster edits.

### Conf — **high**

UAT log names failing vector **`RC`**; batch path and label-only lookup confirmed in source; ticket direction (config-held embedded vectors) is explicit.

### Risk — **Medium**

Touches prefilter hydration and **`_render_score`** for every company prefilter run; wrong merge or lookup would still mass-retry batches, but change is localized and manually verifiable.

---

## Plan vs ASTRAL_CODE_RULES cross-check

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single merge in **`_rubric_criteria_from_cd`** + config list — no roster-local RC literals. |
| §2.1 config | Embedded **RC** lives in **`config.py`**; artifact rows stay candidate-owned. |
| §2.4 batch | Batch runner unchanged except criteria source — claim/decode/outcome flow preserved. |
| §2.6 state machine | No new states; fixes incorrect **WEBSITE_FOUND_RETRY** mass transition on hydration failure. |
| §3.3 imports | Lazy import of **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** inside **`company_prefilter`** branch. |

No conflicts requiring **`!!-NONE`**.

---

## Review stub

- `code(AST-707): embedded RC registry and prefilter hydration merge` @ `c4a25ee1` — `origin/sub/AST-700/AST-707-uat-batch-prefilter-embedded-rc-vector-hydration`
