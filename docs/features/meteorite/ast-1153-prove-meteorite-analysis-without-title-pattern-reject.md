# AST-1153 — Prove meteorite analysis without title-pattern reject

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1153/prove-meteorite-analysis-without-title-pattern-reject-do-not-validate  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1151/do-not-validate-titles-on-meteorites  

**Publish ref (origin):** `sub/AST-1151/AST-1153-prove-meteorite-analysis-without-title-pattern-reject`  
**Parent integration ref:** `ftr/AST-1151-do-not-validate-titles-on-meteorites`  
**Blocked-by (satisfied):** AST-1152 — User Testing; product on parent ftr tip.

After AST-1152, meteorite-company jobs skip roster title-pattern screening (re-home `NEW` → `METEORITE_NEW`; `validate_title_batch` skips meteorite companies; `qualify_meteorite` never calls `validate_title_batch`). This ticket **locks Archie’s decision** with observable proof: a meteorite whose listing title would fail `contact.title_patterns` still reaches meteorite qualify/analysis eligibility when content gates pass; short/blank title still content-fails to `METEORITE_FAILED_QUALIFY`; roster NEW title screening is unchanged. Does **not** invent ingest paths, own the AST-1152 peel, or change GDL scoring.

⚠️ **Decision — product already shipped on AST-1152; this ticket owns the proof contract, not a second peel:** Betty’s AST-1152 bible section deferred three gaps to AST-1153 (`docs/test-bible/core/consult.md` § AST-1152). Engineer build stacks this publish ref on parent ftr, verifies the shipped symbols, and leaves **no new `src/` behavior**. Permanent component coverage is Betty (`qa-child`) from the Proof matrix below; engineer never edits `tests/` / `docs/test-bible/**`.

---

## Prerequisite (build-child § sync)

Before Stage 1, run:

```bash
~/.cursor/scripts/git/sync-child.sh \
  sub/AST-1151/AST-1153-prove-meteorite-analysis-without-title-pattern-reject \
  --ftr AST-1151-do-not-validate-titles-on-meteorites \
  --worktree /home/susan/astral-AST-1151/
```

Use the **full** parent segment from the epic registry (`parent_ftr`), not bare `AST-1151` — `origin/ftr/AST-1151` does not exist; short `--ftr AST-1151` silently skips the parent merge.

**Done when (preflight):** `HEAD` contains AST-1152 product (`is_meteorite_company` in `src/core/meteorite.py`; meteorite re-home in `qualify_job_listings`; meteorite skip in `validate_title_batch`). If any symbol is missing after sync, **stop** and comment on AST-1153 — do not re-implement AST-1152.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/meteorite/ast-1153-prove-meteorite-analysis-without-title-pattern-reject.md` | Plan + build Review stub after verify | docs |

**No `src/` edits** on the happy path. **No** `tests/` / `docs/test-bible/**` (Betty). **No** new ingest / GDL / UI paths.

If Stage 1 discovers a product gap vs the Proof matrix (e.g. meteorite-company `NEW` still reaches `INVALID_TITLE`), **stop** — comment on the Linear **parent** with the Stage-blocked format; do not silently re-open AST-1152 scope.

---

## Proof matrix (binding for Betty `qa-child`)

Betty materializes these as component tests (and bible rows under `docs/test-bible/core/consult.md` / `docs/test-bible/core/gazer.md` as she judges). Engineer does **not** write them. Each row is one observable lock.

### P1 — Meteorite-company `NEW` re-home (never `INVALID_TITLE`)

**Call:** `consult.qualify_job_listings` with a claimed job:

- `state == "NEW"`
- `company` starts with `METEORITE_CONFIG["short_name_prefix"]` (e.g. `meteorite-cand-proof`)
- `job_data.raw_job_listing` is a string that **fails** a non-empty `ctx.candidate_data.contact.title_patterns` regex (e.g. patterns `^Engineer` and listing `"Janitor Wanted"`)

**Expect:**

1. `tracker.transition_job_state([aid], METEORITE_CONFIG["job_create_state"])` invoked for that aid (`METEORITE_NEW`).
2. `validate_title_batch` is **not** awaited with that meteorite job in its jobs list (either not called, or called only with roster `NEW` peers).
3. Final job state after refresh is **not** `INVALID_TITLE` / `VALID_TITLE`.
4. Job is **not** included in the roster AI qualify slice (`VALID_TITLE` / `VALID_TITLE_RETRY` / `NEW_RETRY`).

**Reuse:** extend `TestQualifyJobListings` / new `TestAst1153…` class in `tests/component/core/test_consult.py` — Betty chooses class name.

### P2 — `validate_title_batch` skips meteorite companies

**Call:** `gazer.validate_title_batch` with one job whose `company` is meteorite-prefixed and `raw_job_listing` would fail the same title_patterns as P1.

**Expect:**

1. No `transition_job_state` to `VALID_TITLE` or `INVALID_TITLE` for that aid.
2. Return counts: that job is **not** in `passed` or `failed` (skip / continue path).
3. A second roster (non-meteorite) job in the same batch still pattern-screens as today.

**Reuse:** extend `TestValidateTitleBatch` in `tests/component/core/test_gazer.py`.

### P3 — Pattern-mismatch title still eligible for `qualify_meteorite` when content gates pass

**Call:** `consult.qualify_meteorite` with:

- job on meteorite company, `state` `METEORITE_NEW` (or whatever claim state the tip uses)
- `ctx` with `title_patterns` that would reject the AI `job_title` on the roster path (e.g. patterns `^Nurse` and AI title `"Senior Platform Engineer"`)
- AI/`do_task` response that **passes** content gates: non-empty `company_job_id` (or UUID-resolvable http `job_link`), `len(job_title) >= TASK_CONFIG["qualify_meteorite"]["min_job_title_length"]`, http `job_link`, `len(jd_text) >= min_jd_chars`

**Expect:**

1. Pass path: `initialize_job` + transition to `TASK_CONFIG["qualify_meteorite"]["pass_state"]` (`METEORITE_QUALIFIED`).
2. No call to `validate_title_batch` from `qualify_meteorite`.
3. No transition to `INVALID_TITLE`.

**Reuse:** extend `TestAst1062QualifyMeteorite` (add a pattern-mismatch ctx row; do not weaken existing content-gate rows).

### P4 — Short/blank title still content-fails (unchanged policy)

**Call:** existing `TestAst1062QualifyMeteorite` content-gate cases (blank/`ab` title → `METEORITE_FAILED_QUALIFY`).

**Expect:** still fail to `cfg["fail_state"]`; thresholds still from `TASK_CONFIG["qualify_meteorite"]` (`min_job_title_length`, `min_jd_chars`). **No threshold change.**

**Betty action:** keep these rows on the AST-1153 manifest; do not delete or soften.

### P5 — Roster NEW title screen unchanged

**Call:** existing `TestAst797QualifyInlineValidateTitle` + `TestValidateTitleBatch` roster fail → `INVALID_TITLE`.

**Expect:** non-meteorite `NEW` still runs inline `validate_title_batch`; pattern fail → `INVALID_TITLE`; pass continues to roster AI qualify.

**Betty action:** keep on manifest; add a regression assert that a non-meteorite company with failing patterns still hits `INVALID_TITLE` if not already explicit beside P1.

### Manifest shape (Betty publishes)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle \
  tests/component/core/test_gazer.py::TestValidateTitleBatch \
  tests/component/core/test_consult.py::TestAst1062QualifyMeteorite \
  tests/component/core/test_consult.py::<P1 class> \
  tests/component/core/test_gazer.py::<P2 method(s)> \
  -q
```

Exact node ids are Betty’s once classes land. Integration: **do not invent** new `tests/integration/` scenarios (same posture as AST-1152 bible).

---

## UAT observation recipe (parent AC — Archie)

No new ingest. Use an existing candidate-submitted meteorite path (Manage Email land / Create under meteorite company — AST-1130 children already own those). On staging after prep-uat:

1. Candidate with non-empty `contact.title_patterns` that would reject a chosen listing title on the roster path.
2. Land/create a meteorite job whose extract title fails those patterns but passes content gates (usable title length, http link, JD chars).
3. Run `qualify_meteorite` (dispatch / admin task). **Observe:** job reaches `METEORITE_QUALIFIED` (or continues on meteorite GDL track) — **not** `INVALID_TITLE`.
4. Optionally force a meteorite-company row into roster `NEW` (Jobs Skipped bulk retry) and run `qualify_job_listings`. **Observe:** re-home to `METEORITE_NEW`, not `INVALID_TITLE`.
5. Control: short/blank title extract → `METEORITE_FAILED_QUALIFY`.
6. Control: roster (non-meteorite) `NEW` with failing patterns → still `INVALID_TITLE`.

Spike captures (if used) stay under gitignored `debug/spikes/AST-1153/` only — never commit spike output.

---

## Stage 1: Stack on parent ftr and verify AST-1152 product

**Done when:** Publish-ref tip includes AST-1152 product; the four static checks below pass; `python3 -m py_compile src/core/meteorite.py src/core/gazer.py src/core/consult.py` succeeds; **no** `src/` diff introduced by this stage.

1. Sync per Prerequisite (full `--ftr` segment). Confirm merge-clean gate exit 0.
2. Verify by reading tip sources (no runtime DB required):
   - `src/core/meteorite.py` defines `is_meteorite_company` using `METEORITE_CONFIG["short_name_prefix"]` only (no hardcoded `"meteorite-"` at call sites).
   - `src/core/gazer.py` `validate_title_batch` continues early when `is_meteorite_company(job.get("company"))`.
   - `src/core/consult.py` `qualify_job_listings` partitions `meteorite_new` / `roster_new`, re-homes via `tracker.transition_job_state` to `METEORITE_CONFIG["job_create_state"]`, and only passes `roster_new` into `validate_title_batch`.
   - `src/core/consult.py` `qualify_meteorite` has **no** `validate_title_batch` call; short/blank title still maps to `cfg["fail_state"]` via `min_job_title_length`.
3. `python3 -m py_compile src/core/meteorite.py src/core/gazer.py src/core/consult.py`.
4. Do **not** edit product code. Do **not** edit `tests/` or bible.

**Commit message (only if this stage produced a merge commit that is not yet on `origin/<publish-ref>`):** merge commits from sync are fine; do not invent a no-op product commit. If tip already matches ftr + prior plan and Stage 1 is verify-only, proceed to Stage 2 without a Stage 1 commit.

---

## Stage 2: Lock Review stub on the plan (Code Complete handoff)

**Done when:** Plan file on `origin/<publish-ref>` has a `## Review (build stub)` section recording the verified tip SHA, that P1–P5 are ready for Betty, and that no `src/` delta was required. Linear → Code Complete after publish (build-child ritual).

1. Append `## Review (build stub)` with:
   - Publish ref tip SHA after Stage 1
   - Confirmation: no `src/` files changed for AST-1153
   - Pointer: Proof matrix P1–P5 + UAT recipe above
   - Note: Betty fills AST-1152 deferred gaps; engineer test-tree ban holds
2. Commit: `code(AST-1153): lock proof matrix for title-pattern skip` (docs-only Review stub is the stage artifact — message stays `code()` because this is the build stage completion, not a re-plan).
3. Push `git push origin HEAD:sub/AST-1151/AST-1153-prove-meteorite-analysis-without-title-pattern-reject`.

⚠️ **Decision — `code()` commit may be docs-only:** Happy path has no product peel left; the build deliverable is the verified stack + locked proof contract for Betty/UAT. Inventing a `src/` change to “have a code commit” would violate `astral.standards.in-scope-only`.

---

## Out of scope (do not implement)

- Re-implementing or widening AST-1152 peel / `is_meteorite_company` logic.
- Changing `qualify_meteorite` content-gate thresholds or fail/pass states.
- Roster `qualify_job_listings` title-screen behavior for non-meteorite companies.
- GDL (`evaluate_jd` / grade_*) / Recommended UI.
- New email ingest / Manage Email / Playwright create paths.
- New `METEORITE_*` states.
- Engineer-authored `tests/` or `docs/test-bible/**` commits.
- New integration scenarios under `tests/integration/`.

---

## Self-Assessment

**Scope:** `minor` — docs-only build on the happy path; product peel already on AST-1152 / parent ftr; proof contract binds Betty’s deferred gaps.

**Conf:** `high` — AST-1152 product and bible gap list are concrete; P1–P5 map 1:1 to parent ACs and Betty’s deferred rows; no open product decisions.

**Risk:** `low` — no new product behavior; residual risk is Betty missing a matrix row (mitigated by explicit P1–P5 + manifest shape) or sync using short `--ftr AST-1151` and silently omitting parent tip (mitigated by Prerequisite full segment).

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.1 / `astral.standards.in-scope-only`:** No GDL / ingest / threshold drive-by; no invented product peel.
- **§1.1 / `astral.standards.no-cross-contamination`:** P5 locks roster title screen unchanged; P1–P3 keep meteorites off roster title-screen outcomes.
- **§2.6 / `pattern.state.entity-state-transitions`:** Proof asserts meteorite track states (`METEORITE_NEW` / `METEORITE_QUALIFIED` / `METEORITE_FAILED_QUALIFY`) and forbids `INVALID_TITLE` for meteorite companies.
- **§2.1 / config source of truth:** Thresholds and landing state read from existing `TASK_CONFIG` / `METEORITE_CONFIG` — plan does not hardcode apply values beyond naming the keys.
- **§3.6 spikes:** UAT/spike output under `debug/spikes/AST-1153/` only if used; not committed.
- **Test ownership:** Engineer ban on `tests/` / bible honored; Proof matrix is instructions for Betty, not an engineer test commit.

No plan conflicts requiring `conf-!!-NONE`.
