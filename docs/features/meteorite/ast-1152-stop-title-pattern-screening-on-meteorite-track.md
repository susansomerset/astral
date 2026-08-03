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
