# AST-1491 — Cover Letter content does not appear for editing
**Component:** artifacts  
**Children:** AST-1499, AST-1504  
**Linear archived:** AST-1491 2026-09-09; AST-1499 2026-09-09; AST-1504 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-26 08:45 | AST-1499 | docs | `26733bb4d` | plan-fix — cover letter JAR hydrate parity |
| 2026-08-26 08:59 | AST-1499 | code | `435cd11ac` | nonempty cover letter hydrate for JAR edit |
| 2026-08-26 09:00 | AST-1504 | test | `447d82f57` | bug-repro — cover letter hydrate nested unwrap / empty-spine gate |
| 2026-08-26 09:08 | AST-1499/1504 | docs | `ba7c6604b` | Radia review — nonempty cover hydrate (docs-acceptance; repro on AST-1504) |
| 2026-08-26 09:17 | AST-1504 | test | `595ccaca9` | strengthen pin leave-on-miss red-first (non-cover body) |
| 2026-08-26 09:22 | AST-1499/1504 | docs | `85fbd6e0e` | Radia review path — test-only gap (docs-acceptance; product AST-1499) |
| 2026-08-26 09:22 | AST-1504 | test | `c88b5de35` | bug-repro — cover letter hydrate nested unwrap / empty-spine / pin leave-on-miss |
| 2026-08-26 09:24 | AST-1499/1504 | code/docs | `79e76e9aa` | docs-acceptance — test-only gap; product is AST-1499 |
| 2026-08-26 09:24 | AST-1504 | docs | `541fa33ae` | plan — test-gap cover letter hydrate display repro |
| 2026-08-28 22:27 | AST-1491 | docs | `fcad25ca6` | mirror epic registry Threads |
| 2026-09-09 17:58 | AST-1499 | docs | `28c732593` | archive Linear issue content |
| 2026-09-09 17:59 | AST-1504 | docs | `7362dd1b9` | archive Linear issue content |
| 2026-09-09 18:07 | AST-1491 | docs | `f6115a467` | archive Linear issue content |

_AST-1499's plan-fix and full build/review narrative is not in its own thin ticket doc — per its "Notes for planning," it explicitly patches the pre-existing **AST-1116** feature doc ("plan-fix: never create a new plan doc") rather than authoring a new one. AST-1116 (archived 2026-08-07) is itself an older, separate ticket under a different parent epic (AST-1091 — "Job resume artifact, cover letter and suggested responses is not saved in job_data"), which is **not** part of this session's Phase-1 archival list and is therefore left in place, unrenamed. The AST-1499 (and referenced AST-1504) content embedded in that doc is reproduced in full below, cited to its source, per this session's embedded-bug convention — this is its real family._

## Epic — AST-1491
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1491/cover-letter-content-does-not-appear-for-editing · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Report (Susan)

When I print a cover letter, I see content, but when I click on the Cover letter content sections on the job details page, the text blocks are empty, so I can't edit the content.

### As-is

On the job details (JAR) page, Cover Letter content sections (Subject / Letter / Signature) open with empty text blocks, so the operator cannot see or edit the letter. Print Cover Letter for the same job still renders letter content.

### To-be

Opening Cover Letter content on the job details page shows the same letter body that Print uses (Subject / Letter / Signature populated from the job's cover-letter artifact), and the operator can edit and save those fields.

### Proposed steps

1. On a job that prints a non-empty cover letter, compare `GET /api/jobs/<id>` `job_data.artifacts.cover_letter` after `hydrate_job_artifacts_for_display` with what `builder._resolve_cover_letter` uses for Print — confirm whether the editor path gets a pin string, an empty Subject/Letter/signature dict, or a nested hop body that `normalize_cover_letter_artifact` flattens to blanks.
2. Fix the failing path so ArtifactEditor's `shapes_key=cover_letter` load receives a non-empty Subject/Letter/signature dict (likely in `hydrate_job_artifacts_for_display` / pin unwrap before normalize, or in `ArtifactEditor.applyJobArtifactResponse` / `mapFixedFieldsFromRaw` if the API already returns the right blob and the client drops it).
3. Re-check Print still resolves content; Confirm Save PUT still writes the Subject/Letter/signature spine.

### Component scope

* `src/core/tracker.py` — modified: display hydrate / normalize for `artifacts.cover_letter` so JAR GET leaves Subject/Letter/signature bodies the editor can bind (same contract AST-1116/AST-1100 intended).
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — modified only if client load/mapping for `shapesKey=cover_letter` + `jobPersistence` is what blanks tabs after a good hydrate (e.g. pin-string reject or key map miss).
* `src/ui/api/api_jobs.py` — modified only if job detail stops calling or mishandles `hydrate_job_artifacts_for_display` for the cover slot.
* `src/core/builder.py` — read/align only if Print and hydrate need a shared unwrap; do not change print CSS or emit layout unless required for parity of field read.

### Technical scope

* `src/core/tracker.py` — modified function(s): `hydrate_job_artifacts_for_display` and/or `normalize_cover_letter_artifact` (and possibly pin-body unwrap before normalize) so a printable cover pin or dict becomes a Subject/Letter/signature dict for display; no empty overwrite of a usable pin.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — modified function(s): `applyJobArtifactResponse` / `mapFixedFieldsFromRaw` (and load effect only if needed) so fixed cover fields populate from the hydrated blob instead of staying empty placeholders.
* `src/ui/api/api_jobs.py` — modified function only if `detail` must change how artifacts are attached after hydrate.
* `src/core/builder.py` — optional shared helper extract from `_resolve_cover_letter` / `_cover_letter_fields_for_read` if hydrate should reuse the same nonempty read rules as Print.

### Ancestor candidates

- [X] AST-1116 — Cover letter field defs + JAR hydrate normalize (`DATA_SHAPES` cover_letter + `normalize_cover_letter_artifact`); closest shipped work for empty Cover Letter tabs vs resolved body
- [ ] AST-1100 — Resolve pinned `agent_data_id` bodies for UAT surfaces including `cover_letter` on job GET
- [ ] AST-1091 — Parent epic: job resume / cover letter / suggested responses persisted as job_data artifact pins
- [ ] AST-1480 (under AST-1459) — Same ArtifactEditor "sections visible, bodies empty" failure class for resume structure mode; shared component, different mode (`shapesKey` cover vs structure resume)

#### Comments

_No comments on the parent itself._

### Files changed (plan vs actual)

_No direct product commit trail on the parent beyond the epic-registry Threads mirror and archive-docs commits. Implementation landed via the two sub-issues below, both as a plan-fix patch on the pre-existing AST-1116 doc rather than new plan docs of their own._

## Sub-issues

### AST-1499 — Fix cover letter content edit hydrate on job details
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1499/fix-cover-letter-content-edit-hydrate-on-job-details-cover-letter · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1491_

#### What this implements (own ticket doc)

Restore JAR Cover Letter content sections so Subject / Letter / Signature show the same letter body Print uses, and the operator can edit and save them. Orphaned-bug fix under mini-parent AST-1491. Approved ancestor (archived): AST-1116 — use its feature doc for plan-fix context only; do not re-parent under it.

**Acceptance criteria:** on a job whose Print Cover Letter shows non-empty letter content, opening Cover Letter content on the job details page shows Subject / Letter / Signature populated (not empty placeholders); operator can edit those fields and Save, reload still shows the saved values; Print Cover Letter still renders the letter after the editor hydrate/fix; no change to resume structure-mode editing or unrelated JAR tabs beyond cover_letter fixed fields.

**Board:** Joan `[board-joan] CANON: OK`. Betty `[board-betty] TESTS: REVISE` — "docs/test-bible/core/tracker.md (AST-1116 hydrate) — missing coverage — repro gaps (pin leave-on-miss / nested hop unwrap / nonempty gate vs empty Subject·Letter·signature overwrite) not exercised by `TestAst1116HydrateCoverLetterNormalize`; Blast radius expects Betty extend before make-fix" — routed to sibling AST-1504 rather than run inline.

#### As-is / To-be / Root cause / Proposed change _(embedded build narrative, sourced from `ast-1116-cover-letter-field-defs.md` § "Bug: AST-1499 — Fix cover letter content edit hydrate on job details")_

Orphaned-bug mini-parent **AST-1491** (fresh `ftr` off `origin/dev`). AST-1116's ancestor plan (field defs + flat normalize) stays; this block is the fix delta only — explicitly not re-parented under AST-1116.

**As-is:** On the job details (JAR) Cover Letter artifact tabs, Subject / Letter / Signature open as empty text blocks, so the operator cannot see or edit the letter. Print Cover Letter for the same job still renders letter content.

**To-be:** Opening Cover Letter content on the job details page shows the same letter body Print uses (Subject / Letter / Signature populated from the job's cover-letter artifact after display hydrate), and the operator can edit and Save those fields. Print still renders after the hydrate/edit path.

**Repro** (fixture-shaped, no SQL seed):
1. Job with `job_data.artifacts.cover_letter` set to a finalize pin string whose `agent_data` RESPONSE body is a cover hop payload Print accepts (nonempty `re_line`/`body` or `Subject`/`Letter` after the same field map Print uses) — or the live UAT job Susan used when filing AST-1491.
2. Confirm Print Cover Letter for that job returns HTML with visible letter body (not the "No cover letter content" error).
3. `GET /api/jobs/<astral_job_id>` and inspect `job_data.artifacts.cover_letter` after `hydrate_job_artifacts_for_display`.
4. Open JAR → Cover Letter artifact tabs (`shapes_key=cover_letter` / `ArtifactEditor` + `jobPersistence`).

**Broken observation (any one):** hydrated value is still a pin **string**, or a dict whose `Subject`/`Letter`/`signature` are all `""`, while Print still shows a letter. Editor tabs bind empty placeholders.

**Passing observation after fix:** hydrated `cover_letter` is `{"Subject": "<nonempty or empty>", "Letter": "<nonempty>", "signature": "..."}` with at least one nonempty body field matching Print's letter; tabs show that text; Save PUT round-trips the spine; Print still works.

**Root cause:** JAR Cover Letter tabs bind only a **dict** of Subject / Letter / signature from `GET /api/jobs` after `hydrate_job_artifacts_for_display`. Print does **not** use that overlay — `builder._resolve_cover_letter` re-reads on-disk `artifacts.cover_letter` (nonempty dict → pin resolve via `resolve_job_artifact_agent_data_body` → else candidate `context.raw_sample`). Two gaps leave the editor empty while Print still renders: (1) **pin string / empty spine on the GET overlay** — after AST-1480, `ArtifactEditor.mapFixedFieldsFromRaw` rejects non-object pin strings; if hydrate leaves the pin string (resolve miss) or installs `normalize_cover_letter_artifact(...)` → all-empty Subject/Letter/signature (unconditional normalize on any dict, including blank or alias-mismatched hop bodies), the tabs stay empty placeholders; (2) **divergent read rules vs Print** — hydrate pin-resolves then always normalizes a dict; it does not share Print's `_cover_letter_nonempty` / `_cover_letter_fields_for_read` gate, does not unwrap a nested cover hop body the way `job_resume` uses `_resume_payload_body`, and must not overwrite a usable pin with an empty normalized dict (`coat-check-never-store-empty` on the display overlay). AST-1116 already added `DATA_SHAPES...cover_letter` and flat normalize-after-pin; this bug is the remaining hydrate↔Print↔editor contract hole, not missing field defs.

**Proposed change (probe-gated, Path A landed):** a step-0 probe on a job that Prints a letter compares on-disk `artifacts.cover_letter`, the `hydrate_job_artifacts_for_display(...)` result, and what `_resolve_cover_letter` returns, then branches: **A — tracker hydrate** (default, landed) if the pin/dict has printable fields but the hydrate overlay is a pin string or all-empty; **B — ArtifactEditor mapping only** if the hydrate overlay is already nonempty but tabs still empty; **C — api_jobs.detail attach only** if detail skips/drops hydrate for the cover slot; **Stop / `[scope-gate]`** if Print's letter is only `raw_sample` (do not silently copy sample onto the job artifact overlay without Susan).

**Path A — `src/core/tracker.py` (as built):** add a focused public helper `cover_letter_artifact_for_display(raw) -> Optional[Dict[str, str]]`: if `raw` is a nonempty pin string, resolve via `resolve_job_artifact_agent_data_body(raw)`, return `None` (leave pin in place) if not a dict; if a dict, try **one** nested unwrap when a single nested dict carries cover keys (mirroring job_resume's `_resume_payload_body`, cover-shaped only, no new key names); normalize via `normalize_cover_letter_artifact(...)`; return the normalized dict only if `Subject`/`Letter`/`signature` has any nonempty value, else `None`. In `hydrate_job_artifacts_for_display`, replace the AST-1116 unconditional normalize-on-dict block with a call to the helper after the pin-key loop — set `out["cover_letter"]` only when the helper returns non-`None`; never replace a pin string with an empty spine. Optional DRY (deferred) — share a nonempty field map with `builder._cover_letter_fields_for_read` / `_cover_letter_nonempty` so Print and hydrate cannot drift.

#### Radia review — code-rubric.v2, CLEAN

Full statute sweep conforms/not-applicable. Plan adherence: Path A implemented exactly as proposed — helper pin-resolves, optionally unwraps one nested hop envelope, normalizes, returns `None` when all-empty; hydrate skips cover in the generic pin loop and applies the helper only when nonempty, fixing AST-1116's unconditional normalize. Paths B/C correctly not taken; no `save_job_data` from hydrate; `builder._resolve_cover_letter` / print emit untouched. `[bug-repro]` not applicable on this ticket — Betty's REVISE routed repro coverage to sibling AST-1504 by design. **"What must still hold" table:** all seven items (pin-on-job disk string / overlay-only hydrate; `resolve_job_artifact_agent_data_body` contract; AST-1116 DATA_SHAPES/shapes_key; never overlay all-empty dict over a usable pin; Print still renders pre-fix jobs; operator Save round-trip; no resume-structure/unrelated-tab changes) verified OK.

**advisory** — plan-fix prose still cites the retired pattern id `astral.patterns.coat-check-never-store-empty`; the live check is the `astral.idioms.coat-check-never-store-empty` idiom statute (behavior delivered either way). **advisory** — optional DRY with builder read helpers left for a follow-up if Print/hydrate drift becomes a concern.

#### What's solid

Surgical fix at the right layer: one public helper, pin-loop skip prevents double-resolve, nonempty gate closes the hydrate↔editor gap without touching disk pins or print emit. Existing AST-1116 hydrate tests remain compatible (nonempty pin/dict paths unchanged).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/tracker.py` | `cover_letter_artifact_for_display` helper; skip-then-conditionally-overlay in `hydrate_job_artifacts_for_display` | `435cd11ac` — +51/-4 |
| | _tests_ | routed to sibling AST-1504 (docs-acceptance on this ticket) | — |

### AST-1504 — Gap: cover letter hydrate empty-overwrite / nested unwrap tests
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1504/gap-cover-letter-hydrate-empty-overwrite-nested-unwrap-tests-cover · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1491_

#### What this implements

Test-gap sibling of AST-1499 (orphaned-bug fix-board `TESTS: REVISE` — not run inline on the fix child). Lands repro coverage for cover-letter display hydrate gaps Betty named so Subject/Letter/signature empty-overwrite / nested hop unwrap / pin leave-on-miss cannot regress without a red test. Does **not** implement the product hydrate fix (AST-1499); does not expand into a bible sweep beyond the named gap.

#### Board brief (from AST-1499)

> [board-betty] TESTS: REVISE
> What: docs/test-bible/core/tracker.md (AST-1116 hydrate) — missing coverage — repro gaps (pin leave-on-miss / nested hop unwrap / nonempty gate vs empty Subject·Letter·signature overwrite) not exercised by `TestAst1116HydrateCoverLetterNormalize`; Blast radius expects Betty extend before make-fix.

#### Acceptance criteria

`TestAst1504CoverLetterHydrateDisplayGaps` covers nested unwrap, empty-spine gate, and pin leave-on-miss; pin leave-on-miss is red-first (resolve `{"unrelated": "meta"}` → assert overlay keeps `"pin-cover"`, per a Radia fix-now); manifest green on tip with AST-1499 product present; does not implement the product fix.

#### QA test manifest

`tests/component/core/test_tracker.py::TestAst1504CoverLetterHydrateDisplayGaps` (bug-repro: nested unwrap + empty-spine gate + pin leave-on-miss; pin leave-on-miss red-first via `::test_hydrate_leaves_pin_when_resolve_misses`). Bible: `docs/test-bible/core/tracker.md` → shasum `c8285aa02050af9d72bc033f0f062fbba8499a1d`. Publish: `origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `b5847de3` ← `origin/tests` `595ccaca`.

#### Build narrative — a Radia fix-now on the *test itself*, strengthened mid-flight

##### chuckles — 2026-08-26T15:56:31.825Z
Test-gap sibling of AST-1499. Betty's board on AST-1499:

[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md (AST-1116 hydrate) — missing coverage — repro gaps (pin leave-on-miss / nested hop unwrap / nonempty gate vs empty Subject·Letter·signature overwrite) not exercised by TestAst1116HydrateCoverLetterNormalize; Blast radius expects Betty extend before make-fix.

qa-fix runs here (orphaned-bug REVISE is not inline on the fix child). Use that brief.

##### betty — 2026-08-26T16:03:25.009Z
[bug-repro]
`origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `85ee1c89` · repro lands red, awaits fix

##### katherine — 2026-08-26T16:10:09.839Z
`origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `4ff9654b` · [bug-repro] green (3 passed)

##### radia — 2026-08-26T16:12:44.367Z
[code-rubric] REVIEW (Commit: 4ff9654b) Pin-miss repro not red-first

##### katherine — 2026-08-26T16:14:00.664Z
[qa-handoff]
@Betty White

Radia fix-now on AST-1504 (Review Posted → resolve): `TestAst1504CoverLetterHydrateDisplayGaps::test_hydrate_leaves_pin_when_resolve_misses` is green on **pre-AST-1499** product (resolve `None` already left the pin before the fix). It is not a red→green [bug-repro] gate.

**Please strengthen or reclassify on astral-tests, then merge-tests(AST-1504) to** `origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests`:

Preferred strengthen (Radia's example): change that node so resolve returns a **nonempty non-cover** body (e.g. `{"unrelated": "meta"}`) and assert the overlay keeps the pin string `"pin-cover"` — pre-fix installed empty Subject/Letter/signature spine (or the raw body); post-AST-1499 leaves the pin. That makes pin leave-on-miss red-first.

Alternatively: drop/reclassify that node out of the [bug-repro] red→green set (nested unwrap + empty-spine gate nodes already carry the gate) and update `docs/test-bible/core/tracker.md` AST-1504 accordingly.

Do **not** rewrite foreign AST-1493/AST-1500 history; keep AST-1504-owned test commit clean.

When landed: reassign Katherine; she re-syncs and advances User Testing.

##### betty — 2026-08-26T16:18:33.502Z
[qa-handoff]
Pin leave-on-miss strengthened (Radia fix-now).

`test_hydrate_leaves_pin_when_resolve_misses` now resolves `{"unrelated": "meta"}` and asserts overlay keeps `"pin-cover"` — red on pre-AST-1499 (empty spine); green after AST-1499 helper. Bible AST-1504 updated.

`origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `b5847de3` · merge-tests ← `origin/tests` `595ccaca`

Stay Review Posted — reassigned Katherine to finish resolve → User Testing. Epic worktree synced to sub tip.

#### Resolution

Radia's fix-now — the pin-leave-on-miss test wasn't actually red-first (it passed even on pre-fix product, since a `None` resolve already left the pin untouched before AST-1499 existed) — was addressed by strengthening the repro to resolve a nonempty **non-cover** body instead, which genuinely fails pre-fix (installs an empty spine or raw body) and passes post-fix (leaves the pin). Verified return pass: all three nodes red on pre-AST-1499 product; pin-miss green on post-AST-1499. Resolve §9a clean (dev + ftr).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `tests/component/core/test_tracker.py` + `docs/test-bible/core/tracker.md` | `TestAst1504CoverLetterHydrateDisplayGaps` — nested unwrap, empty-spine gate, pin leave-on-miss (strengthened to be genuinely red-first) | `447d82f57` (initial, 79 insertions) → `c88b5de35` / `595ccaca9` (strengthened, 80 insertions) |
