# AST-1053 — Meteorite GDL parallel job states

**Linear:** [AST-1053](https://linear.app/astralcareermatch/issue/AST-1053/meteorite-gdl-parallel-job-states-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`

Register a **parallel meteorite GDL job-state track** in `JOB_STATES` (entry **METEORITE_NEW**, then **METEORITE_PASSED_JD → DO → GET → LIKE**, plus fail / technical-fail / upshot-retry siblings) and wire those states into the existing Jobs **In Review** / **Skipped** UI manifests so they are visible. Does **not** own dispatch rows, agent_task prompts, Create landing retarget, or the Recommended Meteorites section.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add meteorite `JOB_STATES` keys + priors; extend `IN_REVIEW_STATES` / `SKIPPED_STATES` / `JOBS_IN_REVIEW_UI_SECTIONS` / `JOBS_SKIPPED_*` / grade-field maps | utils |

## Stage 1: Parallel meteorite `JOB_STATES` + Jobs UI manifests

**Done when:** All meteorite GDL states exist in `JOB_STATES` with legal `prior_states`; In Review / Skipped manifests list them; no dispatch / create / Recommended changes.

1. In `src/utils/config.py`, inside `JOB_STATES` (after the existing GDL block that ends around `FAILED_TECHNICAL_LIKE` / before `ERROR_QUALIFY_JOB_LISTINGS` is fine — keep keys contiguous with a short comment header), add:

```python
# AST-1052 / AST-1053: parallel meteorite GDL track (no CULTURE_READY hop).
# Entry METEORITE_NEW is unrestricted (create landing — sibling AST-1056).
"METEORITE_NEW":                  {"prior_states": None},
"METEORITE_PASSED_JD":            {"prior_states": ["METEORITE_NEW"]},
"METEORITE_FAILED_JD":            {"prior_states": ["METEORITE_NEW"]},
"METEORITE_ERROR_EVALUATE_JD":    {"prior_states": ["METEORITE_NEW"]},
"METEORITE_PASSED_DO":            {"prior_states": ["METEORITE_PASSED_JD"]},
"METEORITE_FAILED_DO":            {"prior_states": ["METEORITE_PASSED_JD"]},
"METEORITE_FAILED_TECHNICAL_DO":  {"prior_states": ["METEORITE_PASSED_JD"]},
"METEORITE_PASSED_GET":           {"prior_states": ["METEORITE_PASSED_DO"]},
"METEORITE_FAILED_GET":           {"prior_states": ["METEORITE_PASSED_DO"]},
"METEORITE_FAILED_TECHNICAL_GET": {"prior_states": ["METEORITE_PASSED_DO"]},
# LIKE claimed from METEORITE_PASSED_GET (no CULTURE_READY) — sibling AST-1054/1055.
"METEORITE_PASSED_LIKE":          {"prior_states": ["METEORITE_PASSED_GET"]},
"METEORITE_FAILED_LIKE":          {"prior_states": ["METEORITE_PASSED_GET"]},
"METEORITE_FAILED_TECHNICAL_LIKE":{"prior_states": ["METEORITE_PASSED_GET"]},
# Upshot technical-hold after meteorite LIKE (mirrors PASSED_LIKE_RETRY) — sibling AST-1055.
"METEORITE_PASSED_LIKE_RETRY":    {"prior_states": ["METEORITE_PASSED_LIKE"]},
```

⚠️ **Decision — `prior_states: None` on `METEORITE_NEW`:** Lawful unrestricted entry for Create (sibling AST-1056), mirroring `NEW` rather than expanding `JD_READY` or inventing a carve-out on this ticket. Do **not** change `METEORITE_CONFIG["job_create_state"]` here (still `JD_READY` until AST-1056).

⚠️ **Decision — no `METEORITE_*_RETRY` holding states except `METEORITE_PASSED_LIKE_RETRY`:** Parent AC lists pass + fail/technical siblings only; LIKE upshot needs the retry hold to mirror `PASSED_LIKE_RETRY`. Do **not** add `METEORITE_NEW_RETRY` / scrape-fail siblings / culture states.

⚠️ **Decision — do not extend `RECOMMENDED` / `RECOMMENDED_JOB_STATES` priors:** Meteorite post-upshot membership is AST-1057. Mixing `METEORITE_PASSED_LIKE` into normal `RECOMMENDED` priors would violate parent Boundaries.

⚠️ **Decision — do not add meteorite keys to `PASSED_SCORE_GATED_STATES`:** Score-floor claim wiring is AST-1054 (`score_floor` 0 on meteorite dispatch rows). Leaving the frozenset unchanged keeps non-meteorite claim/UI floor behavior identical.

2. Extend ordered Jobs UI lists (same file) so Jobs In Review / Skipped stay config-driven:

- **`IN_REVIEW_STATES`:** append  
  `"METEORITE_NEW", "METEORITE_PASSED_JD", "METEORITE_PASSED_DO", "METEORITE_PASSED_GET", "METEORITE_PASSED_LIKE", "METEORITE_PASSED_LIKE_RETRY"`.
- **`SKIPPED_STATES`:** append  
  `"METEORITE_FAILED_JD", "METEORITE_ERROR_EVALUATE_JD", "METEORITE_FAILED_DO", "METEORITE_FAILED_TECHNICAL_DO", "METEORITE_FAILED_GET", "METEORITE_FAILED_TECHNICAL_GET", "METEORITE_FAILED_LIKE", "METEORITE_FAILED_TECHNICAL_LIKE"`.
- **`JOBS_IN_REVIEW_UI_SECTIONS`:** append rows (labels):
  - `METEORITE_NEW` → `"Meteorite New"`
  - `METEORITE_PASSED_JD` → `"Meteorite Passed JD"`
  - `METEORITE_PASSED_DO` → `"Meteorite Passed DO"`
  - `METEORITE_PASSED_GET` → `"Meteorite Passed GET"`
  - `METEORITE_PASSED_LIKE` → `"Meteorite Passed LIKE"`
  - `METEORITE_PASSED_LIKE_RETRY` → `"Meteorite LIKE upshot (retry)"`
- **`JOBS_SKIPPED_SECTION_ORDER`:** prepend meteorite fails near the matching normal fails (group with LIKE/GET/DO/JD technical pairs), e.g. after the normal LIKE pair insert the meteorite LIKE pair, etc. — keep order stable and readable; every new skipped state must appear exactly once.
- **`JOBS_SKIPPED_SECTION_LABELS`:** add human labels for each new skipped state (mirror naming: `"Meteorite Failed JD"`, `"Meteorite Error Evaluate JD"`, `"Meteorite Failed DO"`, …).
- **`JOBS_IN_REVIEW_GRADE_FIELD`:** map  
  `METEORITE_PASSED_JD` → `jd_grades`,  
  `METEORITE_PASSED_DO` → `do_grades`,  
  `METEORITE_PASSED_GET` → `get_grades`,  
  `METEORITE_PASSED_LIKE` / `METEORITE_PASSED_LIKE_RETRY` → `like_grades`.  
  (`METEORITE_NEW` needs no grade blob yet.)
- **`JOBS_SKIPPED_GRADE_FIELD`:** map  
  `METEORITE_FAILED_JD` → `jd_grades`,  
  `METEORITE_FAILED_DO` → `do_grades`,  
  `METEORITE_FAILED_GET` → `get_grades`,  
  `METEORITE_FAILED_LIKE` → `like_grades`.  
  (Technical / error states may omit grade fields — same as normal `FAILED_TECHNICAL_*` / `ERROR_EVALUATE_JD` today.)

3. Do **not** edit `TASK_CONFIG` / `DISPATCH_*` / `METEORITE_CONFIG` create defaults / Recommended section lists / frontend TS state enums (manifest is config-driven via `build_state_ui_manifest`). Do **not** edit `tests/` or bible.

**Done when (recheck):** `from src.utils.config import JOB_STATES` loads; every new key is present with the priors above; `METEORITE_NEW` has `prior_states is None`; no `CULTURE_READY` / `NEED_*` meteorite keys; `IN_REVIEW_STATES` / `SKIPPED_STATES` / UI section lists include the new keys; `RECOMMENDED` priors and `PASSED_SCORE_GATED_STATES` unchanged; `python3 -m py_compile src/utils/config.py` succeeds.

## Out of scope (do not implement here)

- Meteorite dispatch_task rows / `score_floor` 0 (AST-1054).
- `meteorite_like` / meteorite upshot agent_task bodies (AST-1055).
- Retarget Create / `METEORITE_CONFIG["job_create_state"]` → `METEORITE_NEW` (AST-1056).
- Recommended page Meteorites section (AST-1057).
- Changing non-meteorite GDL states, culture hop, or score-floor frozenset membership.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — one file (`config.py`); state registry + Jobs UI manifests only.

**Conf:** `high` — mirrors existing GDL prior graph and In Review / Skipped list patterns; no core/UI code paths required for registration.

**Risk:** `Medium` — wrong priors would block sibling transitions or legalize illegal hops; mitigated by explicit prior table matching the parent chain and leaving `RECOMMENDED` / score-gated sets untouched.

## Rules self-review

- **§2.1 / no-hardcoded-sets:** State names only in `JOB_STATES` + existing UI list constants.
- **§2.6 / job-prior-states-enforced:** Every new state has explicit `prior_states` (or `None` for entry).
- **config-source-of-truth:** UI labels/sections read from the same config maps.
- **In-scope only:** No dispatch / prompts / create / Recommended section.

## Review (build stub)

**Publish ref:** 
**Plan path:** 

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 |  | JOB_STATES meteorite GDL track + In Review/Skipped UI manifests |

**Tip:**  on 

