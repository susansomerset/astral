<!-- linear-archive: AST-1152 archived 2026-08-07 -->

## Linear archive (AST-1152)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1152/stop-title-pattern-screening-on-meteorite-track-do-not-validate-titles  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1151 — Do not validate titles on meteorites  
**Blocked by / blocks / related:** parent: AST-1151; blocks: AST-1153

### Description

## What this implements

Owns ensuring meteorite jobs never run roster title-pattern validation and never divert to INVALID_TITLE / title-screen fail for pattern mismatch; candidate submission is the title qualification. Leaves the `qualify_meteorite` short/blank title content gate unchanged. Does not own GDL grading or email ingest.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — qualify_job_listings / qualify_meteorite keep claim→process→release; title-screen peel + re-home only
- [X] `pattern.state.entity-state-transitions` — meteorite-company NEW → METEORITE_NEW; no INVALID_TITLE / VALID_TITLE for meteorite companies
- [X] `pattern.config.config-block` — METEORITE_CONFIG short_name_prefix + job_create_state; TASK_CONFIG qualify_meteorite content-gate mins unchanged
- [X] `astral.state.job-prior-states-enforced` — re-home via tracker.transition_job_state to unrestricted METEORITE_NEW
- [X] `astral.state.core-decides-transitions` — core owns skip / re-home; no data-layer title decisions
- [X] `astral.config.config-source-of-truth` — prefix and landing state from METEORITE_CONFIG (no hardcoded meteorite- at call sites)
- [X] `astral.standards.no-cross-contamination` — roster NEW title-screen unchanged for non-meteorite companies; meteorites not fed into roster AI qualify
- [X] `astral.standards.in-scope-only` — no GDL / email-ingest / UI bulk-retry drive-by

## Considered but excluded

* `astral.agent.do-task-delegation` — no new do_task / assemble path; qualify_meteorite AI path untouched
* `astral.agent.grade-vector-validation` / `astral.agent.confidence-bounds` — no grades on this ticket
* `astral.dispatch.run-next-is-chain-authority` — no dispatch_task / run_next changes
* Jobs Skipped `bulk_retry_to_state` / `src/ui/**` — UI retry may still set NEW; Stage 3 re-home heals without manifest change
* Board ingest `title_matchers` / `ingest_jobs` in `process_gazer_batch` — roster board scrapes only
* AST-1153 proof/lock coverage — sibling owns observable tests

## Acceptance criteria

- [X] A meteorite job that would fail candidate title-pattern matching on the roster path is not rejected for that reason and remains eligible for meteorite qualify → analysis when it has a usable title and other content gates pass.
- [X] No meteorite job is transitioned to INVALID_TITLE (or any roster title-screen fail state) by title-pattern screening.
- [X] A meteorite whose extract has a short or blank title still fails the existing content gate to METEORITE_FAILED_QUALIFY (unchanged policy).
- [X] Roster NEW jobs still receive the existing title-pattern screen (pass → continue qualify; fail → INVALID_TITLE) with no behavioral change from this epic.

## Boundaries

Does not own GDL grading or email ingest. Does not remove or relax the qualify_meteorite short/blank title content gate. Does not change roster qualify_job_listings title screening for non-meteorite NEW jobs. Sibling #2 owns proof/lock coverage.

## Notes for planning

Candidate submission is the title qualification. Keep short/blank title content gate. Happy-path qualify_meteorite already omits validate_title_batch; harden contamination when meteorite-company rows appear as NEW.

## Git branch (authoritative)

`sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track`

### Comments

#### radia — 2026-08-03T01:20:02.720Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1152
**Publish ref:** 4b8850e699e9c3938b21d2d587da6868cec588dc
**Overall:** DISCUSS

## Plan adherence

- Stage 1–3 implemented as written: `is_meteorite_company` (meteorite.py), `validate_title_batch` meteorite skip (gazer.py), `qualify_job_listings` re-home + `qualify_meteorite` content-gate comment (consult.py) — all match the plan's literal sequence.
- `ai_jobs` filter and `qualify_meteorite` content gates untouched, per plan's explicit "do not widen" decisions.
- One literal drift from the plan's Stage 3 snippet (see Discuss below) — otherwise no reorder/skip/expand.

**Discuss:** `orch.pipeline.plan-is-bible` — plan's literal snippet hardcodes `index=1, total=1` in the meteorite re-home loop; shipped code uses `index=mi, total=len(meteorite_new)` via `enumerate`. The shipped version is correct (plan's literal code would have violated `astral.standards.debug-contract-gated`'s per-index-header rule on a multi-job batch), but the divergence wasn't escalated/noted per plan-is-bible — flagging so future Review sections call out beneficial drift explicitly rather than fixing silently.

## Pattern conformance

`pattern.batch.entity-claim-process-release`, `pattern.state.entity-state-transitions`, `pattern.config.config-block` (cited in description) — conforms; claim→process→release and config-sourced landing state unchanged.

## Frame diff

(none)

**What's solid:**

- `is_meteorite_company` sources `METEORITE_CONFIG["short_name_prefix"]` only — no hardcoded `"meteorite-"` at call sites.
- Debug instrumentation on both the `validate_title_batch` skip and the re-home loop matches the file's established per-index contract exactly (`func=`, universal `index N/M`, `identifier=`, `outcome=`).
- Re-home uses `tracker.transition_job_state` into unrestricted `METEORITE_NEW` (not `save_job`) — job-prior-states-enforced / core-decides-transitions hold.
- `merge-tests(AST-1152)` pulling in AST-1147 bible/test rows is expected `orch.git.betty-merge-tests-one-sha` mechanics (shared `origin/tests` SHA), not scope creep — the `code(AST-1152)` commit itself only touches `src/core/{consult,gazer,meteorite}.py`.

Full active-set sweep (65 statutes: 18 universal + 47 scoped) scored in-session — 33 scoped statutes matched this diff and conformed, 14 not-applicable (ui/scripts/utils-only or dispatcher/seed-specific predicates untouched here), 18 universal conformed except the plan-is-bible discuss item above. No Joan plan-rubric verdict attached to this ticket — no straggler check possible.

context_tokens≈9

— Radia

#### betty — 2026-08-03T01:06:33.172Z
[check-linear]

Cleared `[qa-handoff]`: monkeypatched `_rubric_criteria_for_cfg` on three `TestQualifyJobListings` rows; dropped obsolete artifacts-only rubric ctx. Bible AST-1152 broken/obsolete note updated. Manifest command unchanged.

`origin/sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track` @ `4b8850e6` (`merge-tests(AST-1152): origin/tests 3f6d415a8e9b7c73dec9714c1b45a9b304206ced`)

Bible: `docs/test-bible/core/consult.md` shasum `0aaa5eeda72048dcf21433a8b50205eb89d2de85`

Assignee → Ada for `test-child`.

— Betty

#### ada — 2026-08-03T01:04:43.661Z
[qa-handoff]
@Betty White

Manifest command red on 3 `TestQualifyJobListings` cases — **test/fixture defect**, not AST-1152 product.

```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle \
  tests/component/core/test_gazer.py::TestValidateTitleBatch \
  tests/component/core/test_gazer.py::TestValidateTitleBatchDebugPaths \
  tests/component/core/test_consult.py::TestAst1062QualifyMeteorite \
  tests/component/core/test_consult.py::TestQualifyJobListings \
  -q
```

**Result:** 13 passed, 3 failed:
- `TestQualifyJobListings::test_fails_short_title_and_relative_link`
- `TestQualifyJobListings::test_saves_fail_state_without_metadata`
- `TestQualifyJobListings::test_rejects_short_titles_on_passing_grades`

**Why test/manifest:** All three use `state=VALID_TITLE` + `company="co"` (never hit AST-1152 meteorite re-home / title-screen peel). They pass rubric only via `ctx["candidate_data"]["artifacts"]["joblist_rubric"]` and do **not** monkeypatch `_rubric_criteria_for_cfg`. Product `_rubric_criteria_for_cfg` is table-backed (AST-723) and returns `[]` without `astral_candidate_id` → `_run_batch_consult` logs `grade reason hydration failed: rubric criteria missing or empty` and returns `passed=0/failed=0`. Sibling in the same class (`test_runs_debug_and_passing_job_path`) **passes** because it monkeypatches `_rubric_criteria_for_cfg`.

**Ask:** Align those three fixtures with the monkeypatch (or candidate_id + table rubric) used by the passing sibling; drop obsolete artifacts-only rubric wiring. AST-1152 title-screen / meteorite paths unchanged.

Tip run against: `origin/sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track` @ `8f5fd177`

#### betty — 2026-08-03T01:02:40.817Z
1. `tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle` — roster `NEW` still runs inline `validate_title_batch`
2. `tests/component/core/test_gazer.py::TestValidateTitleBatch` + `::TestValidateTitleBatchDebugPaths` — roster pattern pass/fail → `VALID_TITLE` / `INVALID_TITLE`
3. `tests/component/core/test_consult.py::TestAst1062QualifyMeteorite` — short/blank title content gate → `METEORITE_FAILED_QUALIFY` unchanged
4. `tests/component/core/test_consult.py::TestQualifyJobListings` — qualify path after title screen

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle \
  tests/component/core/test_gazer.py::TestValidateTitleBatch \
  tests/component/core/test_gazer.py::TestValidateTitleBatchDebugPaths \
  tests/component/core/test_consult.py::TestAst1062QualifyMeteorite \
  tests/component/core/test_consult.py::TestQualifyJobListings \
  -q
```

No new tests this pass — plan + sibling **AST-1153** own meteorite skip / re-home / pattern-mismatch proof. No broken existing suites (fixtures omit `meteorite-*` company). No integration scenario drift.

`origin/sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track` @ `8f5fd177` (`merge-tests(AST-1152): origin/tests 176cf97825e73b88c240c8ea2ff2c68c220ac2e7`)

Bible: `docs/test-bible/core/consult.md` shasum `1b436f43e9ade4e35722aec9841d8be1d0385ab4`

— Betty

#### joan — 2026-08-03T00:56:44.069Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1152
**Overall:** APPROVED
**Publish ref tip:** `c97f0bb3` on `origin/sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track`

## Traceability

AC1→S2–S3; AC2→S2 (skip, no VALID/INVALID_TITLE) + S3 (re-home before screen); AC3→S3.5 (qualify_meteorite content gate untouched); AC4→S2.3–2.4 + S3.3–3.4 (roster `NEW` still enters `validate_title_batch`, `ai_jobs` filter unchanged). No orphan stage — S1 is the shared `is_meteorite_company` predicate consumed by S2/S3.

## Findings

**discuss — Stage 3 re-home debug header (`src/core/consult.py`).** The re-home loop emits `logger.debug_index(index=1, total=1, …)` per job, so N re-homed jobs each log `index 1/1`. ASTRAL_CODE_RULES §1.5.1 style D wants a universal `index N/M` per batch item; `enumerate(meteorite_new, start=1)` with `total=len(meteorite_new)` would keep the header scannable. Gating itself is correct (`if debug:`), so `astral.standards.debug-contract-gated` scores needs-discussion, not violates. Non-blocking.

**acceptable — verified against tip, not taken on faith:**
- Stage 3's quoted "replace this block" anchor matches `consult.py` L1453–1464 exactly, so the literal edit applies cleanly.
- Stage 2's skip uses `ji` / `job_total` / `_gazer_job_identifier` / `_log`, all in scope inside `validate_title_batch`; `from src.core.meteorite import …` already exists at `gazer.py:40`.
- `METEORITE_NEW` is `prior_states: None`, so `NEW` → `METEORITE_NEW` via `tracker.transition_job_state` is legal and history-recording (`astral.state.job-prior-states-enforced` conforms).
- New module-level `consult → meteorite` import does not cycle: `meteorite → candidate → dispatcher`, and both `dispatcher` (L381) and `candidate` (L1305) import `consult` lazily inside functions.
- `validate_title_batch` has exactly one caller (`consult.py`), so the Stage 2 skip cannot strand a roster job in `NEW` via some other call site.
- `short_name_prefix` / `job_create_state` are read from `METEORITE_CONFIG`; no new literals (`astral.config.config-source-of-truth` conforms).
- Roster path, `ai_jobs` filter, `GAZER_CONFIG["validate_title"]` states, and `qualify_meteorite` thresholds all explicitly unchanged (`astral.standards.no-cross-contamination`, `astral.standards.in-scope-only` conform).
- `is_meteorite_company` is domain-named, so `astral.standards.names-not-ticket-ids` conforms — the `AST-1152` strings are comments/docstring, not identifiers.
- Self-assessment (Single-Component / high / Medium) is honest; the Medium-risk mitigations named (config prefix identity, re-home before the AI slice, explicit ban on widening `ai_jobs`) are specific.

Statute scoring (48 considered — 18 universal + 30 scoped; 17 excluded) ran in-session per R7 slim-artifact rules; no `violates`.

context_tokens≈78000

— Joan

#### ada — 2026-08-03T00:50:28.576Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track/docs/features/meteorite/ast-1152-stop-title-pattern-screening-on-meteorite-track.md

Tip: `c97f0bb3` on `origin/sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track`

**Scope:** Single-Component — `meteorite.is_meteorite_company`, `validate_title_batch` skip, `qualify_job_listings` re-home meteorite-company NEW → METEORITE_NEW; qualify_meteorite content gate unchanged.

**Conf:** high — happy path already omits title patterns (AST-1062); remaining hole is meteorite-company rows forced into NEW (e.g. bulk retry) hitting roster title screen → INVALID_TITLE on empty raw_job_listing.

**Risk:** Medium — wrong prefix predicate could skip roster screening or leave meteorites stuck; mitigated by METEORITE_CONFIG prefix + explicit re-home before AI slice; plan forbids widening ai_jobs to meteorites.

---

# AST-1152 — Stop title-pattern screening on meteorite track

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1152/stop-title-pattern-screening-on-meteorite-track-do-not-validate-titles  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1151/do-not-validate-titles-on-meteorites  

**Publish ref (origin):** `sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track`  
**Parent integration ref:** `ftr/AST-1151-do-not-validate-titles-on-meteorites`

Candidates submit meteorites they already chose for analysis — that submission is the title qualification. Roster title-pattern screening (`contact.title_patterns` → `validate_title_batch` → `VALID_TITLE` / `INVALID_TITLE`) must never run on the meteorite track. This ticket hardens that separation: `qualify_meteorite` stays free of title-pattern screening (content short/blank title gate unchanged), and any meteorite-company job that wrongly appears on the roster `NEW` title-screen path is re-homed to the meteorite track instead of being pattern-rejected. Does **not** own GDL grading, email ingest, or sibling proof coverage (AST-1153).

**Diagnosis (code tip — no runtime spike required):**

1. **Happy path already skips title patterns:** `qualify_meteorite` (AST-1062) never calls `validate_title_batch`; create lands jobs in `METEORITE_CONFIG["job_create_state"]` (`METEORITE_NEW`). Content gates (`min_job_title_length`, link, jd chars) still map to `METEORITE_FAILED_QUALIFY`.
2. **Contamination path still open:** Roster `qualify_job_listings` runs `validate_title_batch` on every claimed job with `state == "NEW"`, with no meteorite-company exclusion. Jobs Skipped bulk retry forces `to_state: "NEW"` via `save_job` (bypasses priors). A meteorite-company row forced into `NEW` is then title-screened; meteorite jobs typically lack `raw_job_listing`, so with non-empty `title_patterns` they fail → `INVALID_TITLE` — exactly the parent AC violation.
3. **Defensive gap:** `validate_title_batch` itself has no meteorite-company guard; any caller can divert a meteorite-company job onto roster title-screen outcomes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | Add `is_meteorite_company(short_name)` using `METEORITE_CONFIG["short_name_prefix"]` | core |
| `src/core/gazer.py` | `validate_title_batch` skips meteorite-company jobs (no `VALID_TITLE` / `INVALID_TITLE`) | core |
| `src/core/consult.py` | `qualify_job_listings`: re-home meteorite-company `NEW` → `job_create_state`; only roster `NEW` enters `validate_title_batch`; confirm `qualify_meteorite` still has no title-screen call | core |

No config key changes (reuse `short_name_prefix` + `job_create_state`). No UI / bulk_retry retarget (re-home heals contamination). No gazer board ingest / `ingest_jobs` title_matchers change (roster board path only). No `tests/` / bible (Betty / AST-1153).

---

## Stage 1: Shared meteorite-company predicate

**Done when:** `is_meteorite_company` is importable from `src.core.meteorite`, returns True iff `short_name` starts with `METEORITE_CONFIG["short_name_prefix"]`, and False for empty/None/non-meteorite companies. No call-site wiring yet.

1. In `src/core/meteorite.py`, after the imports / before `ensure_meteorite_company`, add:

```python
def is_meteorite_company(short_name: Optional[str]) -> bool:
    """True when company short_name is on the meteorite placeholder track (AST-1152)."""
    prefix = METEORITE_CONFIG["short_name_prefix"]
    return bool(short_name) and str(short_name).startswith(prefix)
```

2. Ensure `Optional` is already imported from `typing` (it is — keep that import).

⚠️ **Decision — company prefix, not state prefix alone:** Contamination lands meteorite rows in roster `NEW` (state no longer `METEORITE_*`). Company `meteorite-<candidate_id>` is the durable track signal; `METEORITE_CONFIG["short_name_prefix"]` stays the single source (no hardcoded `"meteorite-"` string at call sites).

---

## Stage 2: Harden `validate_title_batch` against meteorite companies

**Done when:** A job whose `company` is a meteorite short_name passed into `validate_title_batch` is not transitioned to `VALID_TITLE` or `INVALID_TITLE`, is not counted in `passed`/`failed`, and roster (non-meteorite) `NEW` jobs still pattern-screen exactly as today. `python3 -m py_compile src/core/gazer.py src/core/meteorite.py` succeeds.

1. In `src/core/gazer.py`, extend the existing `from src.core.meteorite import create_meteorite_job` import to also import `is_meteorite_company`.

2. Inside `validate_title_batch`, at the start of the per-job loop (after resolving `aid`), before reading `raw_job_listing` / applying patterns:

```python
        if is_meteorite_company(job.get("company")):
            if debug:
                _log.debug_index(
                    func="gazer.validate_title_batch",
                    index=ji,
                    total=job_total,
                    identifier=_gazer_job_identifier(job),
                    outcome="skipped — meteorite company (no title-pattern screen)",
                )
            continue
```

3. Do **not** change `GAZER_CONFIG["validate_title"]` pass/fail states, pattern compilation, or permissive-empty-patterns behavior for roster jobs.

4. Do **not** change board-ingest `title_matchers` / `ingest_jobs` filtering in `process_gazer_batch` (roster board scrapes only — out of meteorite track).

⚠️ **Decision — skip, do not force VALID_TITLE:** Forcing `VALID_TITLE` would put meteorite rows onto the roster qualify AI path. Skip leaves state alone; Stage 3 re-homes onto `METEORITE_NEW` before this batch function sees them in the normal consult path. The skip is defense in depth for any other caller.

---

## Stage 3: Re-home meteorite-company `NEW` in `qualify_job_listings`; keep `qualify_meteorite` title-screen-free

**Done when:** In a `qualify_job_listings` batch, every claimed job with `state == "NEW"` and meteorite company is transitioned to `METEORITE_CONFIG["job_create_state"]` (`METEORITE_NEW`) via `tracker.transition_job_state`, is excluded from `validate_title_batch`, and does not enter the roster AI qualify slice (`VALID_TITLE` / `VALID_TITLE_RETRY` / `NEW_RETRY`). Non-meteorite `NEW` jobs still run `validate_title_batch` unchanged (pass → continue qualify; fail → `INVALID_TITLE`). `qualify_meteorite` still does not call `validate_title_batch` and still fails short/blank titles to `cfg["fail_state"]` (`METEORITE_FAILED_QUALIFY`). `python3 -m py_compile src/core/consult.py` succeeds.

1. In `src/core/consult.py`, add `METEORITE_CONFIG` to the existing `src.utils.config` import list.

2. Add a module-level import: `from src.core.meteorite import is_meteorite_company` (core→core; meteorite does not import consult).

3. In `qualify_job_listings`, replace the title-screen block that currently does:

```python
    title_screen_failed = 0
    if any((j.get("state") or "") == "NEW" for j in jobs):
        from src.core.gazer import validate_title_batch

        new_jobs = [j for j in jobs if (j.get("state") or "") == "NEW"]
        tr = await validate_title_batch(batch_id, new_jobs, ctx or {}, debug=debug)
        title_screen_failed = int(tr.get("failed", 0))
        for j in jobs:
            if (j.get("state") or "") == "NEW":
                fresh = tracker.get_job(j["astral_job_id"])
                if fresh:
                    j["state"] = fresh.get("state")
```

with this literal sequence:

```python
    title_screen_failed = 0
    if any((j.get("state") or "") == "NEW" for j in jobs):
        from src.core.gazer import validate_title_batch

        new_jobs = [j for j in jobs if (j.get("state") or "") == "NEW"]
        meteorite_new = [j for j in new_jobs if is_meteorite_company(j.get("company"))]
        roster_new = [j for j in new_jobs if not is_meteorite_company(j.get("company"))]
        # AST-1152: candidate submission is title qualification — never pattern-screen meteorites.
        meteorite_landing = METEORITE_CONFIG["job_create_state"]
        for j in meteorite_new:
            aid = j["astral_job_id"]
            tracker.transition_job_state([aid], meteorite_landing)
            if debug:
                logger.debug_index(
                    func="consult.qualify_job_listings",
                    index=1,
                    total=1,
                    identifier=_consult_job_identifier(j),
                    outcome=f"re-home meteorite NEW -> {meteorite_landing}",
                )
        if roster_new:
            tr = await validate_title_batch(batch_id, roster_new, ctx or {}, debug=debug)
            title_screen_failed = int(tr.get("failed", 0))
        for j in jobs:
            if (j.get("state") or "") == "NEW" or is_meteorite_company(j.get("company")):
                fresh = tracker.get_job(j["astral_job_id"])
                if fresh:
                    j["state"] = fresh.get("state")
```

4. Leave the existing `ai_jobs` filter unchanged:

```python
    ai_jobs = [
        j for j in jobs
        if (j.get("state") or "") in ("VALID_TITLE", "VALID_TITLE_RETRY", "NEW_RETRY")
    ]
```

Re-homed meteorite rows are `METEORITE_NEW` after refresh and therefore drop out of this roster AI slice (eligible for the next `qualify_meteorite` dispatch claim).

5. In `qualify_meteorite`, **do not** add a `validate_title_batch` call. Keep the existing content gates (`company_job_id`, `len(job_title) < min_job_title_length`, http `job_link`, `min_jd_chars`) → `cfg["fail_state"]`. Optionally add a one-line comment above the title length gate: `# AST-1152: length/blank content gate only — not roster title-pattern screening.` Do not change gate thresholds or fail/pass states.

⚠️ **Decision — re-home inside qualify_job_listings, not Jobs Skipped UI:** Bulk retry may still send meteorite rows to `NEW`; the next roster qualify claim self-heals onto `METEORITE_NEW` without changing `bulk_retry_to_state` or frontend. That keeps this ticket off UI/manifest scope and avoids changing roster retry for non-meteorite skipped jobs.

⚠️ **Decision — use `tracker.transition_job_state`, not `save_job`:** `METEORITE_NEW` has `prior_states: None` (unrestricted entry), so `NEW` → `METEORITE_NEW` is legal and records history. Matches `astral.state.core-decides-transitions` / job prior enforcement.

⚠️ **Decision — do not widen `ai_jobs` to include meteorites:** Meteorite qualify owns Ruth enrich; stuffing meteorites into roster `qualify_job_listings` AI would violate `astral.standards.no-cross-contamination`.

**Done when (recheck):**

- Meteorite-company job in `NEW` with a title that would fail `title_patterns`, claimed by `qualify_job_listings` → state becomes `METEORITE_NEW`, never `INVALID_TITLE`, not run through roster AI qualify.
- Roster non-meteorite `NEW` job that fails patterns → still `INVALID_TITLE`.
- `qualify_meteorite` batch with usable extract (title ≥ `min_job_title_length`, http link, jd chars) → can still reach `METEORITE_QUALIFIED` regardless of candidate `title_patterns`.
- `qualify_meteorite` with blank/short title → still `METEORITE_FAILED_QUALIFY`.

---

## Out of scope (do not implement)

- AST-1153 proof/lock tests and bible updates (Hedy / Betty).
- Changing `GAZER_CONFIG["validate_title"]` states or retiring `validate_title` for roster.
- Changing `qualify_meteorite` `min_job_title_length` / `min_jd_chars` thresholds or fail policy.
- Jobs Skipped `bulk_retry_to_state` / frontend retry UX (healed by Stage 3 re-home).
- Board ingest `title_matchers` on `ingest_jobs` / `process_gazer_batch`.
- GDL (`evaluate_jd` / grade_*) / Recommended UI / email ingest (`gaze_email`, Manage Email).
- New `METEORITE_*` states.

---

## Self-Assessment

**Scope:** `Single-Component` — three core modules (`meteorite.py` predicate, `gazer.py` defensive skip, `consult.py` re-home + confirm qualify_meteorite); no config/UI/data layer edits.

**Conf:** `high` — happy-path qualify already omits title patterns; contamination vector (meteorite company + `NEW` + `validate_title_batch`) is concrete; prefix and landing state already live in `METEORITE_CONFIG`.

**Risk:** `Medium` — wrong company predicate could skip title screen for a real roster company (mitigated by config prefix identity) or leave meteorites stuck in `NEW` without re-home (mitigated by Stage 3 transition before AI filter). Mistakenly feeding meteorites into roster AI qualify would cross-contaminate — plan explicitly forbids widening `ai_jobs`.

---

## Self-review vs ASTRAL_CODE_RULES

- **§2.4 / `pattern.batch.entity-claim-process-release`:** Claim→process→release shapes for both qualify tasks unchanged; only pre-AI title-screen partitioning + re-home.
- **§2.6 / `astral.state.job-prior-states-enforced` + `astral.state.core-decides-transitions`:** Re-home uses `tracker.transition_job_state` to unrestricted `METEORITE_NEW`; no `INVALID_TITLE` for meteorite companies; core owns the decision.
- **§2.1 / `astral.config.config-source-of-truth` + `pattern.config.config-block`:** Prefix and landing state from `METEORITE_CONFIG`; no new hardcoded thresholds; content-gate mins stay in `TASK_CONFIG["qualify_meteorite"]`.
- **§1.1 / `astral.standards.no-cross-contamination`:** Roster title-screen behavior for non-meteorite `NEW` unchanged; meteorites not pushed into roster AI qualify.
- **§1.1 / `astral.standards.in-scope-only`:** No GDL / email-ingest / UI bulk-retry drive-by.
- **§1.3 DRY:** Single `is_meteorite_company` helper; both call sites import it.
- **§1.5.1 debug contract:** New debug lines only under existing `debug` flags / Style D helpers.
- **§3.3 import direction:** core→core (`meteorite`) and existing utils config import — allowed.

No plan conflicts requiring `conf-!!-NONE`.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1151/AST-1152-stop-title-pattern-screening-on-meteorite-track`  
**Plan path:** `docs/features/meteorite/ast-1152-stop-title-pattern-screening-on-meteorite-track.md`

**Built tip:** `bba9bcb66b7350278b5df8e251ed132632589f7c` (`bba9bcb6`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `bba9bcb6` | `is_meteorite_company`; `validate_title_batch` skip; re-home meteorite-company NEW → METEORITE_NEW; qualify_meteorite content gate comment |

---

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1` — **Publish ref tip:** `4b8850e699e9c3938b21d2d587da6868cec588dc` — **Overall:** DISCUSS

**What's solid:**

- `is_meteorite_company` reads `METEORITE_CONFIG["short_name_prefix"]` only — no hardcoded `"meteorite-"` at call sites, matches the plan's explicit decision.
- `validate_title_batch` skip and `qualify_job_listings` re-home both use the established per-index debug contract (`_log.set_debug_flag(True)` / `logger.set_debug_flag(True)` + `debug_index` with `func=` / universal `index N/M` / `identifier=` / `outcome=`) — matches surrounding style exactly.
- Re-home uses `tracker.transition_job_state` (not `save_job`) into unrestricted `METEORITE_NEW`, so job-prior-states-enforced / core-decides-transitions hold.
- `ai_jobs` filter untouched — meteorites are not widened into roster AI qualify (no-cross-contamination holds).
- `merge-tests(AST-1152)` brings in one `origin/tests` SHA; the AST-1147 bible/test rows riding along are that shared branch's other queued content, not scope creep from this ticket — engineer's `code(AST-1152)` commit only touches `src/core/{consult,gazer,meteorite}.py`, test-tree edits stay on Betty's `test(...)` / `merge-tests(...)` commits.

**Discuss:**

- `orch.pipeline.plan-is-bible` — the plan's literal Stage 3 snippet hardcodes `index=1, total=1` inside the `for j in meteorite_new:` loop; the shipped code instead uses `for mi, j in enumerate(meteorite_new, start=1): ... index=mi, total=len(meteorite_new)`. This is a correct fix (the plan's literal snippet would have mis-numbered a multi-job re-home batch under `astral.standards.debug-contract-gated`'s per-index-header rule), but it's a silent drift from the plan's literal code rather than an escalated one — worth a one-line note in the Review section next time so plan-is-bible fidelity stays visible.

**Full-set sweep:** all 65 active statutes (18 universal + 47 scoped) scored in-session; 33 scoped statutes matched the diff (core + docs layers, add/modify) and conformed, 14 not-applicable (ui/scripts/utils-only or seed/dispatcher-specific predicates not touched by this diff), 18 universal all conformed except the plan-is-bible discuss item above. No Joan plan-rubric verdict attached to this ticket — nothing to straggler-check against.

**Pattern conformance:** `pattern.batch.entity-claim-process-release`, `pattern.state.entity-state-transitions`, `pattern.config.config-block` (all cited in description) — conforms; claim→process→release and config-sourced landing state unchanged.

context_tokens≈9

— Radia

---

## Resolution

**Date:** 2026-08-03  
**Radia tip:** `4b8850e6` · **Overall:** DISCUSS (no fix-now)

| Item | Disposition |
|------|-------------|
| Discuss — `orch.pipeline.plan-is-bible` Stage 3 debug `index=1, total=1` vs shipped `enumerate` / `index=mi, total=len(meteorite_new)` | **Keep shipped code.** Enumerate matches §1.5.1 Style D and Joan’s earlier non-blocking plan note; plan literal would mis-number multi-job re-homes. Drift recorded here for plan-is-bible fidelity — no product change. |

No product or test-tree edits this resolve pass.
