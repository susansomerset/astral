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

---

## Bug: AST-1881 — Reality Check as a persisted default prefilter vector (like QC/GC); drop duplicate prompt section

**Parent bug:** [AST-1876](https://linear.app/astralcareermatch/issue/AST-1876) (orphaned mini-parent, `ftr/AST-1876-prefilter-rc-default-vector` off `origin/dev`)  
**Publish ref:** `origin/sub/AST-1876/AST-1881-prefilter-rc-default-vector`  
**Pattern precedent:** AST-1085 / AST-1077 (`_merge_embedded_evaluate_jd_criteria`, `docs/features/interface/ast-1085-wire-constants-evaluate-jd.md`).

### As-is

Reality Check is defined twice in the rendered `prefilter_company` prompt: once as a hand-written `### Reality Check - Is this the website for a company…` block (A/B/C/D/F company-site scale) in the `cache_prompt`, and again inside `{$RUBRIC_VECTORS}` from `EMBEDDED_COMPANY_PREFILTER_CRITERIA` (generic "real vs fraudulent" A–F/X scale). The model grades both, emits `000|RCA5|RCA5|…`, and the AST-1513 duplicate-code guard in `agent._decode_payload` rejects the whole payload. Batch `prefilter_company-6e5f321d-…` errored 50 of 50. RC is only merged in memory by `rubric_criteria_for_task` and never stored in `rubric_vector`, unlike QC/GC.

### To-be

RC is defined once, as a default prefilter rubric vector maintained exactly like QC/GC: the `config.py` constant is merged on rubric save, craft persist, craft generate and read for owner `prefilter_company` / artifact `company_prefilter` / task `craft_prefilter_rubric`, and stored in `rubric_vector`. Its content is the company-site scale (the deleted prompt block's A/B/C/D/F plus X = couldn't read the page). The prompt's hand-written section is gone; each encoded line carries exactly one `RC` segment.

### Repro

Data-shape fixture (no DB seed; prompt + decode):

1. `prefilter_company` `cache_prompt` from `data/admin/agent_task.json` as shipped on `origin/dev` — contains both `### Reality Check - Is this the website…` and `{$RUBRIC_VECTORS}`.
2. `rubric_criteria_for_task(cid, "prefilter_company")` for a candidate whose `rubric_vector` rows are `MP` + `US` only → returns `[RC(embedded), MP, US]`, so `{$RUBRIC_VECTORS}` renders a second Reality Check.
3. Model response line `000|RCA5|RCA5|MPB3|USA3|…` → `_decode_payload` raises duplicate vector code `RC`; the batch errors every company.
4. Post-fix expectation: the rendered prompt contains exactly one Reality Check definition (from `{$RUBRIC_VECTORS}`); `list_rubric_vectors(cid, "prefilter_company", current_only=True)` includes an `RC` row after the candidate's next prefilter rubric save or craft persist.

### Root cause

AST-707 added `EMBEDDED_COMPANY_PREFILTER_CRITERIA` as a read-time-only merge (now inline in `rubric_criteria_for_task`, `src/core/candidate.py` ~1509–1520) and left the prompt's hand-written Reality Check block in place (AST-707 Stage 1 step 1 read the prompt copy but never removed it). Result: two RC definitions with different scales in one prompt. Also, unlike QC/GC (merged in `apply_rubric_vectors_save` ~1551, `_persist_craft_dispatch_success` ~3603, craft generate ~4003), RC never reaches `rubric_vector`.

### Proposed change

**1. `src/utils/config.py` — `EMBEDDED_COMPANY_PREFILTER_CRITERIA` (~2409–2438).** Keep `code` `"RC"`, `label` `"Reality Check"`, `importance` `8`. Replace the header comment and the `content` / `grade_descriptions` with the company-site scale:

```python
# AST-707 / AST-1881: default company_prefilter vector — merged on save / craft persist /
# craft generate / read (embedded wins on code) and stored in rubric_vector, like QC/GC.
EMBEDDED_COMPANY_PREFILTER_CRITERIA: tuple[dict, ...] = (
    {
        "code": "RC",
        "label": "Reality Check",
        "importance": 8,
        "content": (
            "Reality Check — Is this the website for a company that the candidate might work at?\n"
            "A == It is a typical website with content about products or services, a link to a careers page, etc.\n"
            "B == It is an elaborate website that isn't clearly a company website, but at least it's about the company, such as a VC portfolio page.\n"
            "C == It is a social media site for the company, but not their website. Links might still be found to job openings from here.\n"
            "D == This is a company website, but it doesn't look like the expected website for this company.\n"
            "F == This is obviously not a company website, someone got confused in their previous research identifying the company.\n"
            "X == could not read the page (bot blocked or other network issue)"
        ),
        "grade_descriptions": [
            {"grade": "A", "description": "It is a typical website with content about products or services, a link to a careers page, etc."},
            {"grade": "B", "description": "It is an elaborate website that isn't clearly a company website, but at least it's about the company, such as a VC portfolio page."},
            {"grade": "C", "description": "It is a social media site for the company, but not their website. Links might still be found to job openings from here."},
            {"grade": "D", "description": "This is a company website, but it doesn't look like the expected website for this company."},
            {"grade": "F", "description": "This is obviously not a company website, someone got confused in their previous research identifying the company."},
            {"grade": "X", "description": "could not read the page (bot blocked or other network issue)"},
        ],
    },
)
```

⚠️ **Decision:** `{$FIRST_NAME}` from the prompt block becomes "the candidate". Rubric vector content is not relied on to resolve tokens. No `E` row: the company-site scale defines no E, and nothing in `src/` gates on RC letters (grep: `"RC"` / `Reality Check` appear only in this constant).

**2. `src/core/candidate.py` — new helper, immediately after `_merge_embedded_evaluate_jd_criteria` (~1500):**

```python
def _merge_embedded_company_prefilter_criteria(criteria: list) -> list:
    """Prepend EMBEDDED_COMPANY_PREFILTER_CRITERIA; embedded wins on duplicate code (AST-707 / AST-1881)."""
    embedded_codes = {
        str(c.get("code")).strip().upper()
        for c in EMBEDDED_COMPANY_PREFILTER_CRITERIA
        if isinstance(c, dict) and c.get("code")
    }
    tail = [
        c
        for c in (criteria or [])
        if isinstance(c, dict)
        and str(c.get("code") or "").strip().upper() not in embedded_codes
    ]
    return list(EMBEDDED_COMPANY_PREFILTER_CRITERIA) + tail
```

⚠️ **Decision:** **Prepend** (RC first), not append like QC/GC. This keeps today's read-time order and the `000|RC…|…` line shape. Only the persistence lifecycle mirrors QC/GC.

**3. `src/core/candidate.py` — call the helper on the same four paths as QC/GC:**

- **Read — `rubric_criteria_for_task` (~1509–1520):** replace the inline `if owner_task_key == "prefilter_company":` block body with `return _merge_embedded_company_prefilter_criteria(criteria)`. The read-time merge stays; it covers candidates that have no stored RC row yet.
- **Save — `apply_rubric_vectors_save` (~1548–1552):** that's where QC/GC are merged on save. The ticket names `normalize_rubric_artifacts_on_save`, but that function only validates and never merges. After the existing QC/GC `if`, add:
  ```python
        # AST-1881: restore RC on save (prepend; embedded wins on code), like QC/GC.
        if owner == "prefilter_company":
            val = _merge_embedded_company_prefilter_criteria(val)
  ```
  Leave `normalize_rubric_artifacts_on_save` unchanged, same as QC/GC.
- **Craft persist — `_persist_craft_dispatch_success` (~3601–3604):** after the QC/GC `if`, add:
  ```python
        # AST-1881: craft_prefilter_rubric persist restores RC before sync.
        elif artifact_key == "company_prefilter":
            criteria = _merge_embedded_company_prefilter_criteria(criteria)
  ```
- **Craft generate — generate response/stash (~4001–4007):** after the QC/GC block, add:
  ```python
            # AST-1881: prepend RC into craft_prefilter_rubric generate response/stash.
            elif task_key == "craft_prefilter_rubric" and isinstance(parsed_response, dict):
                crit = parsed_response.get("criteria")
                if isinstance(crit, list):
                    parsed_response["criteria"] = _merge_embedded_company_prefilter_criteria(crit)
                    criteria_count = len(parsed_response["criteria"])
  ```

**4. `data/admin/agent_task.json` — `prefilter_company` row, `cache_prompt` only.** Delete the hand-written block from `### Reality Check - Is this the website for a company that {$FIRST_NAME} might work at?` through the `F == This is obviously not a company website, …identifying the company.` line and its trailing blank line, so the rubric section reads `**Your Rubric for evaluation:**\n\n{$RUBRIC_VECTORS}\n\n### POSSIBLE_JOBLIST_LINKS`. Replace it as raw text on the JSON-escaped substring; do not reserialize the file, so the rest of the diff stays one hunk. Verify with `json.load` that the file parses and that the `prefilter_company` row's `cache_prompt` no longer contains `Reality Check` while `{$RUBRIC_VECTORS}` is still present. Leave every other row and field alone, including the "Use the rubric's A/B/C/D/F/X definitions" ground rule.

**5. Existing candidates — how RC gets stored (planning call).** RC is stored **on the candidate's next prefilter rubric save or `craft_prefilter_rubric` persist**. There's no explicit backfill script. In the meantime the read-time merge in `rubric_criteria_for_task` keeps `{$RUBRIC_VECTORS}` and hydration correct, because embedded wins on code either way, so the prompt is identical before and after a candidate's row lands. A backfill would need a `scripts/` file, which is outside this ticket's scope. If Susan wants every candidate stored immediately, that's a follow-up ticket.

**6. Rollout (operator, not code).** The `agent_task` DB rows are the live prompt. `data/admin/agent_task.json` is a seed, and automatic startup apply is disabled under the AST-1492 kill-switch (`stat.seed.agent-tables-in-repo-json`). After deploy, Susan applies `prefilter_company` with Manage Tasks → **Revert to file**, or deletes the same block in Manage Tasks. Until she does, the live prompt still carries the duplicate block and batches keep failing.

### Blast radius

- `rubric_criteria_for_task` feeds the `{$RUBRIC_VECTORS}` token resolver (`rubric_criteria_for_token`), `hydrate_rubric_artifacts_for_response` (Artifacts UI already shows RC via the read merge), and prefilter batch decode labels and grade-reason hydration. The list shape and order are unchanged; only RC's text changes.
- **Candidate Rubric UI:** edits a user makes to the RC row get overwritten by the constant on save. This is the same as QC/GC today and is intended ("maintained the same way").
- **Shared dict objects:** like the QC/GC helper, the merge returns the constant's own dicts. In craft persist, `normalize_rubric_artifacts_on_save` then rewrites `grade_descriptions` / `importance` on them in place. The values written are identical (the content parses to the same six rows; importance 8 normalizes to 8). This mirrors QC/GC exactly. Copying the dicts would diverge from the precedent, so it's left out unless Susan asks for it.
- **Tests (Betty):** `tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig` and any test asserting the old RC prose or an `E` row will need an update. So will any test that asserts the `prefilter_company` prompt text or that `apply_rubric_vectors_save` / craft persist writes only artifact rows for `prefilter_company`.
- **AST-724 vector feedback:** RC now gets a `rubric_vector` row. Whether prefilter feedback capture then picks it up is a side effect, not a goal of this ticket.
- **Hot file:** in-flight `ftr/AST-1862-recommended-job-modal-changes` edits a different block of `src/utils/config.py`. Expect a clean merge.

### What must still hold

- The AST-1513 duplicate-code guard in `_decode_payload` / `_require_complete_grade_set` is untouched, and duplicate codes are still rejected.
- QC/GC merge behavior (`_merge_embedded_evaluate_jd_criteria` and its four call sites) is unchanged.
- AST-707: prefilter hydration still resolves RC for candidates with no stored RC row (read-time merge), and embedded wins on duplicate code.
- `_assert_unique_rubric_codes` still passes: the helper dedupes by code, so a stored RC plus the embedded RC yields one row.
- No new limits, caps, retries, tables or fields.

## Joan fix-board — AST-1881

Read the AST-1881 plan-fix patch on `origin/sub/AST-1876/AST-1881-prefilter-rc-default-vector` (As-is → What must still hold). `docs/canon-index.md` is not on that ref; roster overlap was checked via `canon/directives/active/*` and draft statutes cited by the AST-1085 embedded-vector precedent (`pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.agent.grade-vector-validation`, `astral.seed.agent-tables-in-repo-json`).

**Triage question:** Does the proposed change conflict with or require updating any in-force directive?

**Answer:** No. The plan completes the QC/GC lifecycle for RC (config constant, merge on read/save/craft paths, seed prompt dedupe), keeps grades in `{A,B,C,D,F,X}`, leaves AST-1513 duplicate-code enforcement intact, and uses repo `agent_task.json` plus operator Revert-to-file rollout—aligned with seed and config-block law. Prepend-vs-append is an owner-specific implementation choice already called out in plan; it does not contradict the evaluate_jd append precedent as a global rule. No new carve-out, statute rewrite, or Archie-only precedent gap.

```
BEGIN-VERDICT
[board-joan]  CANON: OK
END-VERDICT
```

```text
AST-1881 board-joan done — CANON: OK.
```

## Radia review — AST-1881

[code-rubric]

**Ticket:** AST-1881  
**Publish ref:** `2b1f6e1acd5a4cf9f768164abedd290d3c536105` (`origin/sub/AST-1876/AST-1881-prefilter-rc-default-vector`)  
**Diff base:** `origin/ftr/AST-1876-prefilter-rc-default-vector...origin/sub/AST-1876/AST-1881-prefilter-rc-default-vector` (4 files: `data/admin/agent_task.json`, `src/utils/config.py`, `src/core/candidate.py`, plan-fix append in feature doc — **no** `tests/**` / `src/core/agent.py` / `src/core/consult.py`)  
**Corpus:** `e1f2699fad` (local `canon/` via `canon_clerk index`; `docs/canon-index.md` absent on sub tip — same shape as Joan fix-board)  
**Overall:** CLEAN  

## Fix-specific checks

| Check | Verdict |
|-------|---------|
| `[bug-repro]` | **not applicable — clean board opt-out** — fix-board `TESTS: REVISE` became sibling **AST-1882**; no `[bug-repro]` on this ticket (per spawn brief; repro assertion not scored here). |
| `## What must still hold` | **OK** — see below. |

### What must still hold (§5.2)

1. **AST-1513 duplicate-code guard** — `_decode_payload` / `_require_complete_grade_set` not in diff; `src/core/agent.py` unchanged on tip. Duplicate `RC` rejection remains the intended fix *target*, not a regression.  
2. **QC/GC merge** — `_merge_embedded_evaluate_jd_criteria` definition and existing `evaluate_jd` / `evaluate_meteorite` branches unchanged; diff only adds parallel `elif` arms for `prefilter_company` / `company_prefilter` / `craft_prefilter_rubric`.  
3. **AST-707 read-time RC** — `rubric_criteria_for_task` still prepends embedded RC via `_merge_embedded_company_prefilter_criteria` (refactor of prior inline merge); roster/consult/agent token paths use `rubric_criteria_for_task` — hydration/`{$RUBRIC_VECTORS}` still get RC when DB rows lack RC.  
4. **`_assert_unique_rubric_codes`** — merge strips artifact rows whose codes collide with embedded before persist; merged lists are single RC + tail — compatible with normalize’s duplicate-code check on craft persist (normalize → apply merge → sync).  
5. **No new limits/caps/retries/tables/fields** — diff respects boundary.  

## Canon scores

**Process gap:** AST-1881 Linear description has **no frozen Canon Scope list** (Plan Approved append-only ids). Per `review-child` §5 / fix-lane precedent (e.g. AST-702, AST-897), **`## Canon scores` table omitted** — do not treat `[board-joan] CANON: OK` as per-id plan-stage grades.

**Qualitative alignment** (Joan fix-board cited ids only, not scored as formal rows): embedded RC lifecycle mirrors AST-1085 QC/GC pattern; config-block edit is in-place `EMBEDDED_COMPANY_PREFILTER_CRITERIA`; seed prompt dedupe in `agent_task.json` with operator Revert-to-file rollout called out in plan; grade letters `{A,B,C,D,F,X}` for RC; decode guard untouched. No off-list statute violations spotted in the isolated fix diff.

## Column diff vs plan stage

`no plan-stage scores attached` — Joan **fix-board** `CANON: OK` only; no `validate-plan` per-directive column on the bug ticket.

## Frame diff

- [ ] **Operator:** After deploy, apply `prefilter_company` prompt dedupe on **live** `agent_task` (Manage Tasks → Revert to file or manual delete of duplicate Reality Check block) — plan §6; until then live DB can still double-define RC despite repo seed fix.

## Plan fidelity

| Plan-fix item | Diff |
|---------------|------|
| RC prose → company-site scale + X; drop generic E scale | ✓ `config.py` |
| `_merge_embedded_company_prefilter_criteria` + read/save/craft persist/craft generate | ✓ `candidate.py` (save on **`apply_rubric_vectors_save`**, matching plan-fix — not `normalize_rubric_artifacts_on_save`, consistent with QC/GC) |
| Remove hand-written Reality Check block from `prefilter_company` `cache_prompt` | ✓ `agent_task.json`; `json.load` OK; no `### Reality Check` header; `{$RUBRIC_VECTORS}` retained |
| Tests/bible | Deferred to **AST-1882** (expected; no test carry in this diff) |

## Non-canon findings

**fix-now:** none  

**discuss:** none  

**advisory:**

- Linear **Technical scope** still says “modify `normalize_rubric_artifacts_on_save`” for RC merge; authoritative plan-fix and shipped code use **`apply_rubric_vectors_save`** (QC/GC precedent). Wording drift only — implementation matches plan-fix.  
- **Sibling gap AST-1882:** `TestAst707EmbeddedPrefilterConfig` / prompt assertions updated there; product tip is intentionally ahead of bible on RC prose until sibling lands.  
- **Parent shape:** orphaned mini-parent **AST-1876** — on clean review Chuckles merges **`sub/.../AST-1881-...` straight to `origin/dev`** (no `merge-child` / `prep-uat`).

## What's solid

Focused fix diff: one prompt dedupe, one config constant refresh, one merge helper wired on the four QC/GC-parity paths; preserves AST-1513 enforcement and batch decode contract while eliminating double RC definition at the source.

## Chuckles — post-review branching

| Gate | Parent | Next |
|------|--------|------|
| **PROCEED** (this review) | **Orphaned AST-1876** | **Review Posted** → clean-review shortcut → **User Testing** (skip `resolve-child`) → then finish-up-style merge **sub → `origin/dev`**. |

---

**Slim upshot (Chuckles posts `--as radia`):**

```
[code-rubric] PROCEED (Commit: 2b1f6e1a) RC persist + prompt dedupe OK
```

`context_tokens≈` (approximate session cost not instrumented here)

#### Chuckles disposition (AST-1881)

Clean review: Review Posted → User Testing via the clean-review shortcut (resolve-child skipped). Merged into the mini-parent ftr (orphaned bug with its own ftr — merge-child, then prep-uat/finish-up per fix-intake bug-fix; not a direct sub → dev).

Docs-acceptance on this tip: no test-tree delivery here — tests and bible land on gap sibling AST-1882.

Operator step after deploy: Manage Tasks → Revert to file on `prefilter_company` (live DB prompt still carries the duplicate Reality Check block until then).
