<!-- linear-archive: AST-1116 archived 2026-08-07 -->

## Linear archive (AST-1116)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1116/uat-cover-letter-preview-fails-field-definitions-for-cover-letter  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data  
**Blocked by / blocks / related:** parent: AST-1091

### Description

## What this implements

JAR Cover Letter preview loads field definitions for `cover_letter` and shows hop body content resolved from the pinned `job_data.artifacts.cover_letter` `agent_data_id` (via existing agent_data read + display hydrate).

## In scope

- [X] `astral.config.config-source-of-truth` — field defs only in `DATA_SHAPES["candidates"]["detail"]["cover_letter"]`
- [X] `astral.layers.ui-config-driven-business-logic` — tab keeps config `shapes_key: cover_letter`
- [X] `astral.layers.import-direction` — FE via shapes API; normalize in core hydrate
- [X] `astral.patterns.coat-check-never-store-empty` — hydrate overlay only; no empty writes
- [X] `astral.batch.entity-agent-responses-latest-only` — pin stays id; body from `agent_data`
- [X] `astral.standards.in-scope-only` — Cover Letter field defs + hydrate normalize only
- [X] `astral.standards.dry-and-focused-functions` — reuse `normalize_cover_letter_artifact`

## Considered but excluded

- [X] Pin write / `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` — AST-1099
- [X] Print HTML / Materials print routes — AST-1117
- [X] TASK_CONFIG `persist_in` — parent forbids
- [X] Setting `shapes_key` to None / swallowing `shapeError` — wrong fix
- [X] Unrelated JAR tabs / Job Resume structure mode — excluded
- [X] `tests/` / `docs/test-bible/**` — Betty
- [X] `astral.standards.database-header-inventory` — no `src/data/**` in Files Changed
- [X] `astral.layers.scripts-exempt-from-layer-rules` — no `scripts/**`

## Acceptance criteria

- [X] Cover Letter UAT preview no longer shows `Failed to load field definitions for "cover_letter".`
- [X] With pin present after `finalize_cover_letter`, preview shows Subject / Letter / signature tabs populated from resolved hop body (re_line/body aliases normalized on display hydrate).
- [X] Pin-on-job contract (AST-1099) and pin→body resolve (AST-1100) still hold; no full cover JSON forced onto the job as the pin replacement.

## Boundaries

Does not change pin write, Print HTML (AST-1117), TASK_CONFIG `persist_in`, or unrelated JAR chrome.

## Notes for planning

Hypothesis: missing `DATA_SHAPES.candidates.detail.cover_letter`; ArtifactEditor treats empty defs as hard failure before pin-resolved body can render.

## Git branch (authoritative)

Per parent **## Git**: `sub/AST-1091/AST-1116-cover-letter-field-defs`.

## What failed

Previewing the Cover Letter artifact on the recommended/JAR UAT surface shows:

`Failed to load field definitions for "cover_letter".`

## Expected

Cover Letter preview loads field tabs and body content resolved from the pinned `job_data.artifacts.cover_letter` `agent_data_id` (via existing agent_data read paths).

## Repro

1. Open a recommended job that has completed the cover-letter hop (pin present on `job_data.artifacts.cover_letter`).
2. Open the Cover Letter artifact / preview tab.
3. Observe the red error: Failed to load field definitions for "cover_letter".

## Parent AC (quoted inline)

> After a successful `finalize_cover_letter` hop (chain may continue), `job_data.artifacts.cover_letter` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.

> A full successful daisy-chain that ran those three hops leaves all three pointer keys set; UAT surfaces that show Job Resume / Cover Letter / suggested answers resolve content via those ids without a manual PUT of the response body.

## Diagnosis

* **Hypothesis:** Cover Letter tab sets `shapesKey` to `cover_letter`, but `DATA_SHAPES.candidates.detail` has no `cover_letter` field-def list — ArtifactEditor treats empty defs as hard failure before pin-resolved body can render.
* **Correct outcome:** Cover Letter UAT preview shows the hop content (and editable field tabs if that surface is meant to edit) via the pin, not a field-definitions error.
* **Wrong fix to avoid:** Swallow `shapeError` and show a blank editor; put the full cover JSON back on `job_data.artifacts`; invent unrelated DATA_SHAPES keys without aligning `JOBS_RECOMMENDED_ARTIFACT_TABS.shapes_key` / ArtifactEditor contract; catch-all hide the error.
* **Related siblings / contracts:** AST-1100 (resolve pin → body for UAT surfaces); AST-1099 (pin write). Pin-on-job contract must still hold.

## Original brief

UAT bug filed by Chuckles from fix-uat.

### Comments

#### radia — 2026-08-01T00:47:11.186Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1116
**Publish ref:** `origin/sub/AST-1091/AST-1116-cover-letter-field-defs` @ `0acf29aa` (code `e550a2c8`; merge-tests `0b5724a6`)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1116)` → `72ccddd5` |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | Publish forward on origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1091/AST-1116-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in ticket commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1116 history |
| orch.git.no-dev-agent-branches | universal | conforms | Child sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in astral-AST-1091 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis locked; no open product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 implemented as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty test + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer path was Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Assignee left with Katherine |
| orch.roles.pre-commit-path-bans | universal | conforms | Doc-only Radia commit; engineer off bans |
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence path touched |
| astral.agent.do-task-delegation | scoped | conforms | No do_task bypass |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector changes |
| astral.batch.batch-id-first | scoped | conforms | No claim/batch API changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No claim/release changes |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Pin stays id; body from agent_data; normalize is overlay |
| astral.config.config-source-of-truth | scoped | conforms | Field defs only in `DATA_SHAPES` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/threshold changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no `artifacts/**` / spikes paths |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | No parallel run_next membership/shadow list |
| astral.dispatch.seed-auto-false | scoped | conforms | Config touch is DATA_SHAPES only; no seed auto_mode |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1116-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty did not edit src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commit left tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core normalize only; no external I/O |
| astral.layers.import-direction | scoped | conforms | FE via shapes API; normalize stays in core |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Tab keeps config `shapes_key: cover_letter` |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Hydrate overlay only; no empty writes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult changes |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | no `src/ui/**` in ticket change set |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | No agent-table seed / admin JSON changes |
| astral.seed.archie-catalog-wins | scoped | conforms | No dispatcher catalog seed changes |
| astral.seed.boot-only-not-hot-path | scoped | conforms | Display hydrate only; no new boot seed path |
| astral.seed.define-approved | scoped | conforms | No product seed invented |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | No dispatch_task reconcile |
| astral.seed.other-via-coverage-join | scoped | conforms | No coverage-join seed work |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer calls |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses `normalize_cover_letter_artifact` |
| astral.standards.in-scope-only | scoped | conforms | Cover field defs + hydrate normalize only |
| astral.standards.logging-via-utils | scoped | conforms | No new logging surface |
| astral.standards.names-not-ticket-ids | scoped | conforms | Ticket ids only in comments (carve-out) |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in utils/core (+ Betty tests) |
| astral.standards.no-hardcoded-sets | scoped | conforms | Field keys align with existing cover spine |
| astral.standards.public-then-helpers | scoped | conforms | Normalize call on existing public hydrate |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state changes |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No daisy-chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | no `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | conforms | Config touch is DATA_SHAPES only |

## Pattern conformance

| cited | verdict |
|-------|---------|
| astral.config.config-source-of-truth | conforms |
| astral.layers.ui-config-driven-business-logic | conforms |
| astral.layers.import-direction | conforms |
| astral.patterns.coat-check-never-store-empty | conforms |
| astral.batch.entity-agent-responses-latest-only | conforms |
| astral.standards.in-scope-only | conforms |
| astral.standards.dry-and-focused-functions | conforms |

## Plan adherence

FIX-UAT Stages 1–2 match: `DATA_SHAPES` cover_letter defs + post-loop hydrate normalize. Self-Assessment Single-Component / high / Medium fits. Pin write (AST-1099), resolve entry (AST-1100), Print HTML (AST-1117) untouched. Wrong fixes rejected.

## Findings

None.

## Notes

- FIX-UAT mode. `no plan-rubric verdict attached` — not a block (C4).
- Change set for applies_when + product judgment: AST-1116 commits on publish tip. Active statutes = 65.
- Docs append @ `0acf29aa`.

context_tokens≈38000

— Radia

#### betty — 2026-08-01T00:44:16.080Z
## QA test manifest

`origin/sub/AST-1091/AST-1116-cover-letter-field-defs` @ `0b5724a6` (`merge-tests(AST-1116): origin/tests 72ccddd5847a618393655f6908fb0019b5980bae`)

### 1. Existing coverage (bible-backed)

- Pin write / resolve path remains AST-1099 / AST-1100 suites.
- `normalize_cover_letter_artifact` / `TestAst309CoverLetterArtifact` still cover the shared normalizer.

### 2. Broken / obsolete (revised this pass)

1. `TestAst1100ResolveHydrateJobArtifactPins::test_hydrate_replaces_pin_strings_leaves_legacy_dicts` — partial `{"Subject": "keep"}` now expects Subject/Letter/signature spine after hydrate normalize.

### 3. Gaps (new this pass)

1. `tests/component/utils/test_config.py::TestAst1116CoverLetterDataShapes`
2. `tests/component/core/test_tracker.py::TestAst1116HydrateCoverLetterNormalize`
3. `tests/component/ui/api/test_api_system.py::TestAst1116ShapesCoverLetter`

**Bible shasums** (on publish tip):
- `docs/test-bible/core/tracker.md` `adfd43a56baf8421ff44088622b595ba8a9b0b5c`
- `docs/test-bible/utils/config.md` `aee9790f7cb685c4036ed8e0de7d3b47ea28a8f4`

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1116CoverLetterDataShapes \
  tests/component/core/test_tracker.py::TestAst1116HydrateCoverLetterNormalize \
  tests/component/core/test_tracker.py::TestAst1100ResolveHydrateJobArtifactPins \
  tests/component/ui/api/test_api_system.py::TestAst1116ShapesCoverLetter \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

#### katherine — 2026-08-01T00:38:23.652Z
Plan published on `origin/sub/AST-1091/AST-1116-cover-letter-field-defs` @ `ac63308c`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1091/AST-1116-cover-letter-field-defs/docs/features/artifacts/ast-1116-cover-letter-field-defs.md

**Approach:** Add `DATA_SHAPES.candidates.detail.cover_letter` (Subject / Letter / signature) so ArtifactEditor stops hard-failing; normalize pin-resolved cover bodies in display hydrate via existing `normalize_cover_letter_artifact` so hop `re_line`/`body` fill those tabs.

**Self-assessment**
- **Scope — Single-Component:** config field defs + tracker hydrate normalize for Cover Letter UAT tab only.
- **Conf — high:** empty `detail.cover_letter` is the proven failure; reuses shapes API + cover normalize helper.
- **Risk — Medium:** wrong field keys → blank tabs after error clears; hydrate normalize could mask raw RESPONSE shape for other GET overlay consumers.

---

# AST-1116 — UAT: Cover Letter preview fails field definitions for cover_letter

**Linear:** [AST-1116](https://linear.app/astralcareermatch/issue/AST-1116/uat-cover-letter-preview-fails-field-definitions-for-cover-letter)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved) (AC reference only)

**Publish ref:** `origin/sub/AST-1091/AST-1116-cover-letter-field-defs`

JAR Cover Letter tab passes `shapes_key: "cover_letter"` into `ArtifactEditor`, which loads `/api/shapes/candidates` and hard-fails when `detail.cover_letter` is missing or empty. Add the field-def list and normalize pin-resolved cover bodies onto the Subject/Letter spine so preview shows hop content.

## UAT fitness

- **AC restored:** After a successful `finalize_cover_letter` hop (chain may continue), `job_data.artifacts.cover_letter` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`. — and — A full successful daisy-chain that ran those three hops leaves all three pointer keys set; UAT surfaces that show Job Resume / Cover Letter / suggested answers resolve content via those ids without a manual PUT of the response body.
- **Correct outcome:** Cover Letter UAT preview shows the hop content (and editable field tabs) via the pin, not a field-definitions error.
- **Sibling check:** AST-1099 pin write and AST-1100 pin→body hydrate stay intact — this ticket only adds `DATA_SHAPES` field defs + cover normalize on display hydrate; does not change pin keys or GET hydrate entry points. Verified by not touching `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK`, `resolve_job_artifact_agent_data_body`, or job GET wiring beyond the existing hydrate call path.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Swallowing `shapeError` / blank editor; putting full cover JSON back on `job_data.artifacts` as the pin replacement strategy; inventing unrelated `DATA_SHAPES` keys without aligning `JOBS_RECOMMENDED_ARTIFACT_TABS.shapes_key`; setting `shapes_key` to `None` so raw dict tabs appear without defs (loses fixed Subject/Letter tabs and breaks edit/save contract).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `DATA_SHAPES["candidates"]["detail"]["cover_letter"]` field-def list (Subject / Letter / signature) | utils |
| `src/core/tracker.py` | In `hydrate_job_artifacts_for_display`, when resolved/left `cover_letter` value is a dict, replace with `normalize_cover_letter_artifact(...)` (display overlay only; no `save_job_data`) | core |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| Pin write / `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` | AST-1099 |
| Print HTML / Materials print routes | AST-1117 |
| TASK_CONFIG `persist_in` | parent forbids |
| Unrelated JAR tabs / Job Resume `use_resume_structure` | excluded |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: Config — DATA_SHAPES cover_letter field defs

**Done when:** `GET /api/shapes/candidates` JSON includes non-empty `detail.cover_letter` with three fields keyed `Subject`, `Letter`, `signature`; `JOBS_RECOMMENDED_ARTIFACT_TABS` cover row still has `shapes_key: "cover_letter"`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside `DATA_SHAPES["candidates"]["detail"]`, immediately after the `"base_resume_structure"` list (before the closing of the `detail` dict), add:

```python
            # AST-1116: ArtifactEditor fixed tabs for JAR Cover Letter (shapes_key=cover_letter).
            # Keys match BUILD_CONFIG["artifact_shapes"]["cover_letter"] + normalize_cover_letter_artifact.
            "cover_letter": [
                {"key": "Subject", "label": "Subject", "type": "str"},
                {"key": "Letter", "label": "Letter", "type": "str"},
                {"key": "signature", "label": "Signature", "type": "str"},
            ],
```

2. Do **not** change `JOBS_RECOMMENDED_ARTIFACT_TABS` (keep `artifact_key` / `shapes_key` as `"cover_letter"`).
3. Do **not** add other `DATA_SHAPES` keys or invent a parallel shapes API.

⚠️ **Decision:** Field keys are `Subject` / `Letter` / `signature` (canonical job cover spine), not hop RESPONSE `re_line` / `body`. Hop aliases are mapped in Stage 2 via existing `normalize_cover_letter_artifact` so fixed tabs fill after pin hydrate and after human PUT (which already normalizes on save).

## Stage 2: Tracker — normalize cover body on display hydrate

**Done when:** After `hydrate_job_artifacts_for_display`, a pin string on `cover_letter` that resolves to `{re_line, body, signature}` (or Subject/Letter) becomes `{Subject, Letter, signature}` in the returned overlay dict; stored pins on disk are unchanged; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py` `hydrate_job_artifacts_for_display`, after the existing pin-resolve loop (or inside it when applying a resolved body for `cover_letter`), ensure the display value for key `"cover_letter"` is normalized when it is a `dict`:

```python
    # After pin resolve loop (and also if cover_letter was already a body dict):
    cover = out.get("cover_letter")
    if isinstance(cover, dict):
        out["cover_letter"] = normalize_cover_letter_artifact(cover)
```

2. Place the normalize step **after** the pin-key loop so both (a) freshly resolved pin bodies and (b) legacy body dicts already under `cover_letter` get Subject/Letter keys for ArtifactEditor.
3. Do **not** call `save_job_data` / `save_job_artifact_cover_letter` from hydrate.
4. Do **not** change `resolve_job_artifact_agent_data_body` itself.

## Self-Assessment

**Scope — Single-Component:** `DATA_SHAPES` cover field defs in config + one normalize line in tracker display hydrate for the Cover Letter UAT tab.

**Conf — high:** Failure mode is proven (`shapes.detail.cover_letter` empty → `shapeError`); fix reuses `normalize_cover_letter_artifact` and the existing `shapes_key` / `/api/shapes/candidates` contract.

**Risk — Medium:** Wrong field keys leave tabs blank after the error clears; hydrate normalize bugs could mask raw RESPONSE shape for other consumers of the GET overlay (JAR is the intended consumer).

## Code rules check

| Rule | Notes |
|------|-------|
| §2.1 / `astral.config.config-source-of-truth` | Field defs live only in `DATA_SHAPES` |
| §3.3 / `astral.layers.import-direction` | No UI→data; FE still reads shapes API; normalize stays in core |
| `astral.patterns.coat-check-never-store-empty` | Hydrate still does not write; normalize is overlay-only |
| `astral.standards.in-scope-only` | Cover Letter field defs + hydrate normalize only |
| `astral.batch.entity-agent-responses-latest-only` | Pin remains id; body still from `agent_data` |
| `astral.layers.ui-config-driven-business-logic` | Tab still driven by config `shapes_key` |

## Review

**Branch:** `sub/AST-1091/AST-1116-cover-letter-field-defs`  
**Code:** `e550a2c8`  
**Publish tip reviewed:** `0b5724a6` (`merge-tests(AST-1116)`)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1116  
**Overall:** CLEAN

### What’s solid
- `DATA_SHAPES.candidates.detail.cover_letter` Subject/Letter/signature matches ArtifactEditor `shapes_key` and `normalize_cover_letter_artifact`.
- Display hydrate normalizes cover dict after pin resolve; overlay only (no save); pin id contract untouched.
- Tab still `shapes_key: cover_letter`; wrong-fix paths (swallow shapeError / clear shapes_key) not taken.
- Betty one-SHA merge-tests; engineer stayed off tests/bible.

### Issues
None fix-now / discuss.

### Recommended actions
- Engineer: resolve-child → User Testing (no product fixes).

### Notes
- FIX-UAT child. `no plan-rubric verdict attached` — not a block.
- Statute applies_when + product judgment used AST-1116 commit change set. Active statutes = 65.

context_tokens≈38000

— Radia

## Resolution

**Date:** 2026-08-01  
**Publish tip before resolve:** `0acf29aa` (Radia `docs(AST-1116)` on merge-tests `0b5724a6` / code `e550a2c8`)

- **fix-now:** none — Radia overall CLEAN.
- **discuss / advisory:** none.

## Bug: AST-1499 — Fix cover letter content edit hydrate on job details

Orphaned-bug mini-parent **AST-1491** (fresh `ftr` off `origin/dev`). Ancestor plan above (AST-1116 field defs + hydrate normalize) stays; this block is the fix delta only. Do not re-parent under AST-1116.

### As-is

On the job details (JAR) Cover Letter artifact tabs, Subject / Letter / Signature open as empty text blocks, so the operator cannot see or edit the letter. Print Cover Letter for the same job still renders letter content.

### To-be

Opening Cover Letter content on the job details page shows the same letter body Print uses (Subject / Letter / Signature populated from the job's cover-letter artifact after display hydrate), and the operator can edit and Save those fields. Print still renders after the hydrate/edit path.

### Repro

Fixture-shaped (no SQL seed — file/JSON persistence):

1. Job with `job_data.artifacts.cover_letter` set to a finalize pin string whose `agent_data` RESPONSE body is a cover hop payload Print accepts (nonempty `re_line`/`body` or `Subject`/`Letter` after the same field map Print uses) — **or** the live UAT job Susan used when filing AST-1491.
2. Confirm Print Cover Letter for that job returns HTML with visible letter body (not the "No cover letter content" error).
3. `GET /api/jobs/<astral_job_id>` and inspect `job_data.artifacts.cover_letter` after `hydrate_job_artifacts_for_display`.
4. Open JAR → Cover Letter artifact tabs (`shapes_key=cover_letter` / `ArtifactEditor` + `jobPersistence`).

**Broken observation (any one):** hydrated value is still a pin **string**, or a dict whose `Subject`/`Letter`/`signature` are all `""`, while Print still shows a letter. Editor tabs bind empty placeholders.

**Passing observation after fix:** hydrated `cover_letter` is `{"Subject": "<nonempty or empty>", "Letter": "<nonempty>", "signature": "..."}` with at least one nonempty body field matching Print's letter; tabs show that text; Save PUT round-trips the spine; Print still works.

### Root cause

JAR Cover Letter tabs bind only a **dict** of Subject / Letter / signature from `GET /api/jobs` after `hydrate_job_artifacts_for_display`. Print does **not** use that overlay — `builder._resolve_cover_letter` re-reads on-disk `artifacts.cover_letter` (nonempty dict → pin resolve via `resolve_job_artifact_agent_data_body` → else candidate `context.raw_sample`).

Two gaps leave the editor empty while Print still renders:

1. **Pin string / empty spine on the GET overlay.** After AST-1480, `ArtifactEditor.mapFixedFieldsFromRaw` rejects non-object pin strings (avoids garbage). If hydrate leaves the pin string (resolve miss) or installs `normalize_cover_letter_artifact(...)` → all-empty Subject/Letter/signature (unconditional normalize on any dict, including blank or alias-mismatched hop bodies), the tabs stay empty placeholders.
2. **Divergent read rules vs Print.** Hydrate pin-resolves then always normalizes a dict; it does not share Print's `_cover_letter_nonempty` / `_cover_letter_fields_for_read` gate, does not unwrap a nested cover hop body the way `job_resume` uses `_resume_payload_body`, and must not overwrite a usable pin with an empty normalized dict (`coat-check-never-store-empty` on the display overlay). Print can still emit HTML from a successful pin read or from `raw_sample` for the same job.

AST-1116 already added `DATA_SHAPES...cover_letter` and flat normalize-after-pin; this bug is the remaining hydrate↔Print↔editor contract hole, not missing field defs.

### Proposed change

Implement only inside Explicit scope (tracker primary; FE / api_jobs / builder only if the step-0 probe says so).

**0. Probe (make-fix, before editing product code)** — on a job that Prints a letter, compare:
- on-disk `artifacts.cover_letter` (pin string vs dict),
- `hydrate_job_artifacts_for_display(...)` result,
- what `_resolve_cover_letter` returns (and whether source is pin/dict vs `raw_sample`).

Branch on the probe (do not guess):

| Probe result | Fix path |
|--------------|----------|
| Pin/dict has printable fields but hydrate overlay is pin string or all-empty Subject/Letter | **A — tracker hydrate** (default) |
| Hydrate overlay already nonempty Subject/Letter/signature but tabs still empty | **B — ArtifactEditor** mapping only |
| Detail skips / drops hydrate for the cover slot | **C — api_jobs.detail** attach only |
| Print letter is **only** `raw_sample` (job slot empty/unusable) | **Stop / `[scope-gate]`** — do **not** silently copy sample onto the job artifact overlay without Susan; AC text says job cover-letter artifact. Comment `[scope-gate]` naming the sample-only finding. |

**A — `src/core/tracker.py` (expected happy path)**

1. Add a focused public helper used by hydrate (name e.g. `cover_letter_artifact_for_display(raw) -> Optional[Dict[str, str]]`):
   - If `raw` is a nonempty pin string: `body = resolve_job_artifact_agent_data_body(raw)`; if not a `dict`, return `None` (leave pin in place — no empty overwrite).
   - If `raw` / `body` is a `dict`: if top-level normalize would be all-empty, try **one** nested unwrap when a single nested dict carries cover keys (`Subject`/`re_line`/`Letter`/`body`/`signature`) — same intent as job_resume `_resume_payload_body`, cover-shaped only; do not invent new key names.
   - `normalized = normalize_cover_letter_artifact(...)`.
   - Return `normalized` only if any of `Subject` / `Letter` / `signature` is nonempty; else `None`.
2. In `hydrate_job_artifacts_for_display`, **replace** the current unconditional block:
   ```python
   cover = out.get("cover_letter")
   if isinstance(cover, dict):
       out["cover_letter"] = normalize_cover_letter_artifact(cover)
   ```
   with: after the pin-key loop, `display = cover_letter_artifact_for_display(out.get("cover_letter"))`; if `display is not None`, set `out["cover_letter"] = display`; if `None`, do **not** replace a pin string with an empty Subject/Letter/signature dict.
3. Optional DRY (in scope): extract shared nonempty field map with `builder._cover_letter_fields_for_read` / `_cover_letter_nonempty` so Print and hydrate cannot drift — builder keeps emit `re_line`/`body`; hydrate still exposes Subject/Letter/signature via `normalize_cover_letter_artifact`. Do **not** change print CSS / Somerset emit layout unless required for the shared read helper.

**B — `src/ui/frontend/src/components/ArtifactEditor.tsx` (only if probe says API is already good)**

- In `applyJobArtifactResponse` / `mapFixedFieldsFromRaw` for `shapesKey` cover / `jobPersistence.artifactKey === "cover_letter"`: bind Subject/Letter/signature from the hydrated dict (accept `re_line`→Subject and `body`→Letter only if server normalize was skipped). Do not re-introduce pin-string-as-tab-content.

**C — `src/ui/api/api_jobs.py` (only if probe says detail mishandles attach)**

- Keep calling `hydrate_job_artifacts_for_display` and attaching `job_data.artifacts`; fix only a missed call / wrong artifacts source — no new persistence.

**Out of scope:** print HTML/CSS redesign; resume structure-mode behavior except shared hydrate consistency; writing empty cover dicts; replacing pin-on-job with full cover JSON as the stored pin; new plan doc; `tests/` / bible (Betty).

### Blast radius

- **GET `/api/jobs/<id>`** overlay shape for `artifacts.cover_letter` (JAR ArtifactEditor + any other consumer of hydrated job detail).
- **Print** if shared read helper is extracted from `builder._resolve_cover_letter` / `_cover_letter_fields_for_read` — emit keys must remain `re_line`/`body`/`signature` for Somerset map.
- **Save PUT** `/api/jobs/.../artifacts/cover_letter` — still expects Subject/Letter/signature spine (`save_job_artifact_cover_letter` / normalize on write); hydrate must not force empty overlays that operators then Save over a good pin.
- **Siblings / contracts:** AST-1099 pin write, AST-1100 pin→body resolve, AST-1116 field defs + flat normalize — must still hold; pin stays id on disk.
- **FE:** AST-1480 pin-string reject remains; cover tabs rely on nonempty hydrated dict.
- **Tests:** AST-1116 hydrate normalize + AST-1100 pin suites; Betty may extend for nested/empty-overwrite cases after Plan Ready board.

### What must still hold

- Pin-on-job: `job_data.artifacts.cover_letter` on disk remains the RESPONSE `agent_data_id` string after finalize (AST-1099); hydrate is overlay-only — no `save_job_data` from hydrate.
- Pin→body resolve entry (`resolve_job_artifact_agent_data_body`) unchanged in contract (AST-1100).
- `DATA_SHAPES.candidates.detail.cover_letter` Subject / Letter / signature field defs remain; tab keeps `shapes_key: "cover_letter"` (AST-1116).
- Never store / overlay an all-empty cover dict in place of a usable pin (`astral.patterns.coat-check-never-store-empty`).
- Print Cover Letter still renders for jobs that printed before the fix.
- Operator Save still persists Subject/Letter/signature and reload shows saved values.
- No change to resume structure-mode editing or unrelated JAR tabs beyond cover_letter fixed fields.

## Radia review (AST-1499)

Clean review. Product hydrate fix; [bug-repro] / docs-acceptance for tests lives on sibling AST-1504.

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1499
**Publish ref:** `origin/sub/AST-1491/AST-1499-fix-cover-letter-content-edit-hydrate` @ `435cd11ac21a4e92cfcd3c85177f22a315a59819`
**Diff base:** `origin/ftr/AST-1491-cover-letter-content-does-not-appear-for-editing...origin/sub/AST-1491/AST-1499-fix-cover-letter-content-edit-hydrate`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No agent confidence / grading changes in `tracker.py` hydrate path |
| astral.agent.do-task-delegation | scoped | conforms | No AI delegation; display hydrate only |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector logic touched |
| astral.batch.batch-id-first | scoped | conforms | No batch claim API signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id formatting |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release lifecycle edits |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Pin string on disk unchanged; overlay-only hydrate |
| astral.config.config-source-of-truth | scoped | conforms | No new field defs or config drift; reuses existing normalize/resolve |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets or env reads added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No `artifacts/**` path in diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan-fix patch in existing feature doc, not a spike |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | No dispatch chain edits |
| astral.dispatch.seed-auto-false | scoped | not-applicable | Diff paths exclude `dispatcher.py` / `config.py` seed targets |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Bug patch appended to existing `ast-1116-cover-letter-field-defs.md` |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty role path-ban; engineer product commit |
| astral.git.engineer-test-tree-ban | scoped | conforms | No `tests/` or test-bible paths in diff |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | `cover_letter_artifact_for_display` returns `None` on empty; hydrate never overlays all-empty Subject/Letter/signature |
| astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | No consult/render_verdict changes |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No `src/ui/**` in diff |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core-only change; no external I/O introduced |
| astral.layers.import-direction | scoped | conforms | No layer violations; reuses in-module resolve/normalize |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` in diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | Diff layers `{core, docs}` — no `ui` layer |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | `tracker.py` not in seed path list |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No dispatcher/config/admin seed paths |
| astral.seed.boot-only-not-hot-path | scoped | conforms | Hydrate helper is display hot-path overlay, not boot/seed |
| astral.seed.define-approved | scoped | conforms | Fix implementation only; not a define ticket |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No dispatcher/data seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No dispatcher/data seed paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer exception swallowing |
| astral.standards.database-header-inventory | scoped | not-applicable | No `src/data/**` in diff |
| astral.standards.debug-contract-gated | scoped | conforms | `debug` kwarg forwarded to resolve helper |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses `normalize_cover_letter_artifact` / `resolve_job_artifact_agent_data_body`; focused public helper |
| astral.standards.in-scope-only | scoped | conforms | Path A tracker hydrate only; no FE/api_jobs/builder edits |
| astral.standards.logging-via-utils | scoped | conforms | No ad-hoc logging; existing debug_detail contract |
| astral.standards.names-not-ticket-ids | scoped | conforms | Domain names in API; ticket id only in AST comment |
| astral.standards.no-cross-contamination | scoped | conforms | Cover-letter hydrate scoped; resume/proposed_answers paths untouched |
| astral.standards.no-hardcoded-sets | scoped | conforms | `_COVER_LETTER_FIELD_KEYS` mirrors existing alias set (Subject/re_line/Letter/body/signature) |
| astral.standards.public-then-helpers | scoped | conforms | `cover_letter_artifact_for_display` public; `_cover_letter_*` helpers private |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No `src/utils/**` in diff |
| astral.state.core-decides-transitions | scoped | conforms | No state transition logic |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state machine edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch-run daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | No `src/ui/frontend/**` in diff |
| astral.ui.naming-conventions | scoped | not-applicable | No `src/ui/**` in diff |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No ui/scripts worker config in diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single product commit on sub; test gap routed to sibling |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1499): …` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward on `origin/sub/...` stacked on ftr |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1491/AST-1499-…` on live mini-parent ftr |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in ticket commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None observed |
| orch.git.no-dev-agent-branches | universal | conforms | Standard sub branch only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in `astral-AST-1491` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No scope-gate / raw_sample copy; path A only |
| orch.pipeline.plan-is-bible | universal | conforms | Implementation matches plan-fix Path A |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-ticket fix-lane review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed per spawn prompt |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Engineer did not commit tests; Betty REVISE → AST-1504 |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Katherine assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No role-path-ban violations in diff |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| astral.patterns.coat-check-never-store-empty | conforms | Cited in plan-fix `## What must still hold`; behavior delivered via `astral.idioms.coat-check-never-store-empty` (idiom supersedes retired pattern catalog entry) |

## Plan adherence

Path **A — tracker hydrate** implemented as proposed. `cover_letter_artifact_for_display` pin-resolves, optionally unwraps one nested hop envelope (`agent_payload` / `cover_letter` / single ambiguous nested dict), normalizes to Subject/Letter/signature, and returns `None` when all fields empty. `hydrate_job_artifacts_for_display` skips cover in the generic pin loop and applies the helper only when nonempty — fixing the AST-1116 unconditional normalize that installed empty tabs while Print still rendered. Optional DRY with `builder._cover_letter_fields_for_read` explicitly deferred (plan marked optional). Paths B/C correctly not taken. No `save_job_data` from hydrate. `builder._resolve_cover_letter` / print emit untouched.

**C6 judgment aids (§5a–§5g):** imports/layers clean; `None` return is explicit contract not silent failure; debug forwarded; no UI/config/batch/external concerns in diff.

**C4 stragglers:** `no plan-rubric verdict attached` — not a block.

## Fix-specific checks

**[bug-repro]:** not applicable — `[board-betty] TESTS: REVISE` routed repro to sibling **AST-1504**; no `[bug-repro]` expected on this ticket per board opt-out design.

**`## What must still hold`:** OK

| hold item | verdict |
|-----------|---------|
| Pin-on-job disk string; hydrate overlay-only, no `save_job_data` | OK — helper/hydrate read-only |
| `resolve_job_artifact_agent_data_body` contract unchanged | OK — called, not modified |
| AST-1116 DATA_SHAPES / `shapes_key: cover_letter` | OK — no shape or FE edits |
| Never overlay all-empty dict over usable pin | OK — core fix |
| Print still renders pre-fix jobs | OK — builder print path not in diff |
| Operator Save round-trip | OK — `save_job_artifact_cover_letter` unchanged |
| No resume structure-mode / unrelated JAR tab changes | OK — cover slot only |

## Findings

- **fix-now:** none
- **discuss:** none
- **advisory:** Plan-fix prose still cites retired pattern id `astral.patterns.coat-check-never-store-empty`; idiom statute is the live check. Optional DRY with builder read helpers left for a follow-up if Print/hydrate drift becomes a concern.

## What's solid

Surgical fix at the right layer: one public helper, pin-loop skip prevents double-resolve, nonempty gate closes the hydrate↔editor gap without touching disk pins or print emit. Existing AST-1116 hydrate tests remain compatible (nonempty pin/dict paths unchanged).

## Frame diff

(none)

## Chuckles branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal (AST-1491 ftr live) | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped) |
