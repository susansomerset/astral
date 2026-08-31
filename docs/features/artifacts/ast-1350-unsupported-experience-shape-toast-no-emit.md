# Unsupported experience shape — toast, no emit (Clarify candidate_data.artifacts.base_resume.experience node)

**Linear:** [AST-1350](https://linear.app/astralcareermatch/issue/AST-1350/unsupported-experience-shape-toast-no-emit-clarify)
**Parent:** [AST-1345](https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-data-artifacts-base-resume-experience-node) — Clarify candidate_data.artifacts.base_resume.experience node
**Publish ref:** `origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit`

Owns the operator-visible failure path when `experience` is still a legacy string or any other non-array shape: toast exactly `unsupported resume structure, please regenerate`, open no HTML tab, and do not emit a printable resume with Experience omitted. Core refuses emit; UI surfaces the core error string. Does **not** migrate data, rewrite schemas/prompts (AST-1349), or own happy-path array UI/render layout (AST-1351).

## UAT fitness

- **AC restored:** Parent AC 7 — “Opening or printing a resume whose experience is still a string (or other non-array shape) shows toast text `unsupported resume structure, please regenerate`, opens no HTML tab, and does not emit a resume with Experience omitted.”
- **Correct outcome:** Operator clicks Print / Open HTML / Print Resume on a resume whose `experience` is a string (or other non-array); they see that exact toast, no new HTML tab (and no printable Experience-omitted document), and must regenerate to get a valid job-array experience before print works.
- **Sibling check:** AST-1349 locks the shared job-array contract (`is_experience_job_array` / five-key items) — this ticket uses that same predicate for “unsupported,” does not redefine schema text. AST-1351 owns array emit/UI parity — this ticket must not change happy-path role HTML layout; only turn the current leftover-prose skip into a hard fail when shape is wrong. Verified by: valid job-array experience still emits; string/non-array never reaches `_emit_body_sections_html` success.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** UI-only toast while `builder` still skips leftover prose and returns HTML without Experience — that still emits the forbidden Experience-omitted resume (and JAR `window.open` would show it). Client-side shape checks alone also fail layer rules and leave direct `/candidate/resume/…` hits uncoved.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add exact operator toast/error string under `BUILD_CONFIG` (single source) | utils |
| `src/core/builder.py` | Shared gate: if `experience` key is present and not `is_experience_job_array`, raise `ValueError` with that config string before any HTML emit; remove Experience leftover-prose skip-as-success path | core |
| `src/ui/api/api_resume_html.py` | Map the unsupported `ValueError` to HTTP 400 + `{"error": "<exact message>"}` (not 404 HTML-looking success) | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Keep fetch-then-blob Print; toast exact `error` string; do not open tab on failure (already mostly true — ensure message is not rewritten) | ui |
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | Same for Open HTML — toast exact message, no blob tab on unsupported | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Print Resume: fetch `/candidate/resume/<job_id>` first (like Base Resume); on non-OK toast exact `error` and do **not** `window.open`; on OK open blob/tab | ui |

**Out of scope (do not touch):** `data/admin/agent_task.json` / craft schemas (AST-1349); Base Resume Content experience editor chrome / happy-path `_emit_experience_jobs_html` layout (AST-1351); cover-letter routes; migration/backfill; `tests/` / bible; inventing a second experience schema.

**As-is:** `_emit_body_sections_html` skips non-array `experience` as `skipped — leftover prose` and still returns full HTML — Experience omitted. Base Resume / Session Open HTML toast whatever the API returns; JAR Print Resume `window.open`s the URL blindly (tab opens even on JSON error).

## Contract (reuse — do not redefine)

Unsupported when the resume content dict (base, job-resolved, or session) has key `"experience"` and `candidate_mod.is_experience_job_array(value)` is false.

| Shape | Gate |
|-------|------|
| key absent | allow emit (no experience section) |
| `[]` or list of dicts | allow (valid array; empty list may omit roles) |
| `str` (incl. non-empty legacy prose) | **refuse** — toast / no emit |
| `dict`, list of non-dicts, other | **refuse** — toast / no emit |

Exact operator text (literal, config-owned):

```text
unsupported resume structure, please regenerate
```

⚠️ **Decision:** Gate in **core builder** before HTML assembly (not React-only). UI only surfaces `error` and withholds the tab. That satisfies “no emit” for every route that calls `build_base_resume` / `build_resume` / `build_session_base_resume`.

⚠️ **Decision:** Check the content dict **before** filter/emit (e.g. raw `base_resume` / `_resolve_resume_sections` result / session `base_resume`), so a non-array value cannot be dropped then silently omitted.

## Stage 1: Config message + core no-emit gate

**Done when:** Calling `build_base_resume` / `build_resume_from_job` / `build_session_base_resume` with `experience` as a non-empty string (or other non-array) raises `ValueError` whose `str(exc)` equals the config literal; no HTML string is returned. Valid job-array `experience` still returns HTML. Leftover-prose skip for `experience` is no longer a success path.

1. In `src/utils/config.py`, under `BUILD_CONFIG`, add a small key for this operator message, e.g. `unsupported_resume_structure_message` (or nested under an existing resume-emit block if one already groups emit strings — prefer one new top-level string key next to other BUILD_CONFIG resume keys rather than inventing a new subsystem). Value must be exactly `unsupported resume structure, please regenerate`.
2. In `src/core/builder.py`, add a private helper (public-then-helpers: place after public `build_*` or with other private resume helpers) that:
   - Accepts a content `dict`.
   - If `"experience" not in content`: return.
   - If `candidate_mod.is_experience_job_array(content.get("experience"))`: return.
   - Else: raise `ValueError(BUILD_CONFIG["unsupported_resume_structure_message"])` (read the key you added; do not hardcode the toast string in builder).
3. Call that helper in:
   - `build_base_resume` — on the raw `br` dict **before** `filter_content_to_resume_structure` / `_emit_html_document`.
   - `build_resume_from_job` — on the dict returned by `_resolve_resume_sections` **before** filter/emit (after the existing resolve `ValueError` path).
   - `build_session_base_resume` — on the in-memory `base_resume` dict **before** filter/emit.
4. In `_emit_body_sections_html`, for `fmt == "experience_detail"` when `not candidate_mod.is_experience_job_array(raw)`: **do not** `continue` with `skipped — leftover prose` as a silent omit. Raise the same `ValueError` with the config message (defense in depth if a caller forgets the early gate). Do **not** change the happy-path `_emit_experience_jobs_html` branch.
5. Do **not** migrate or coerce string experience into an array. Do **not** touch cover-letter builders.

## Stage 2: API + UI toast, no HTML tab

**Done when:** Base Resume Print, Session Open HTML, and JAR Print Resume each show toast text exactly `unsupported resume structure, please regenerate` for a string-shaped experience, open no HTML tab, and never display an Experience-omitted resume document.

1. In `src/ui/api/api_resume_html.py`, for `resume_base` and `resume_for_job`: on `ValueError`, if `str(exc)` equals the BUILD_CONFIG unsupported message, return `jsonify({"error": str(exc)}), 400`. Keep existing 404 behavior for other `ValueError`s (missing candidate/job/etc.). Import the message from config (or compare to `BUILD_CONFIG[...]`) — do not duplicate the literal in the API module as a second source of truth beyond the comparison.
2. Confirm `session_resume_html` in `api_admin.py` already returns 400 + `error` for `ValueError` — leave status mapping alone if it already surfaces `str(exc)`; do not rewrite session cover routes.
3. In `ArtifactsBaseResumeContent.tsx` `handlePrint`: on `!r.ok`, toast `data.error` when present (already does); **do not** open a blob tab; **do not** rewrite the message to a generic “Print failed” when the API returned the unsupported string.
4. In `AdminSessionResumePaste.tsx` `handleOpenHtml`: same — toast exact API `error`, no blob tab on failure.
5. In `JobAnalysisReportModal.tsx` `onPrintResume`: replace bare `window.open(/candidate/resume/...)` with a fetch-first flow using the shared `api` helper (credentials), matching Base Resume:
   - GET `/candidate/resume/${jobId}` (or the same path the button used).
   - If not OK: parse JSON `error` when possible; toast that text (exact unsupported string when core gated); return without opening a window.
   - If OK: open a blob URL (or equivalent) in a new tab only after HTML text is received — same pattern as `ArtifactsBaseResumeContent.handlePrint`.
   - Wire toast state if the modal does not already have a Toast; reuse existing Toast / `setToast` patterns in the file tree (add minimal toast state on the modal if absent). Print Cover Letter stays unchanged.
6. Do **not** add React-side experience-shape business rules beyond reacting to the API error string. Do **not** change ArtifactEditor save/load chrome (AST-1351).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1350
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit` @ `8984d14e09ec7af614fd0973b3ad066d995dceef`

## Traceability

| AC | Plan stage(s) |
|----|----------------|
| 7 | S1 (core `BUILD_CONFIG` message + pre-emit gate in `build_base_resume` / `build_resume_from_job` / `build_session_base_resume`; defense-in-depth in `_emit_body_sections_html`), S2 (`api_resume_html` 400 mapping + Base Resume Print / Session Open HTML / JAR Print Resume fetch-then-blob with exact toast, no tab on failure) |

Stages S1–S2 map to parent AC 7 and functional-scope unsupported-shape operator path; parent AC 1–6 and array UI/render parity correctly deferred to AST-1349/AST-1351 per child Boundaries.

## Findings

**acceptable** — Assignee is Hedy (not Joan); Chuckles-spawned pass; no review block.

**acceptable** — `## UAT fitness` present and correctly frames AC 7 vs symptom-only fixes (wrong fix = UI toast while builder still omits Experience).

**acceptable** — As-is verified on tip: `_emit_body_sections_html` still `continue`s with `skipped — leftover prose` for non-array `experience` (lines 1511–1516); `api_resume_html` maps all `ValueError` to 404; JAR `onPrintResume` still blind `window.open`s `/candidate/resume/<job_id>`.

**acceptable** — `MaterialsPreviewModal.tsx` loads resume via iframe `src` without fetch-first but appears unused (no imports elsewhere); core gate still blocks Experience-omitted emit if wired later (iframe would show JSON/error body, not toast — out of this ticket’s three named surfaces).

No `fix-now` or `discuss` findings. In-session statute sweep: cited patterns/statutes (`pattern.layers.import-discipline`, `astral.layers.import-direction`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`) all `conforms`; plan correctly gates in core before `filter_content_to_resume_structure` so string experience cannot be dropped then silently omitted; reuses `is_experience_job_array` per AST-1349 contract without redefining schema.

context_tokens≈52000

## Review (build)

**Built:** `origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit` @ `3b30b01bc7ff13ead7899a289d8b04c215436eb2`

Stage 1: `BUILD_CONFIG.unsupported_resume_structure_message` + `_reject_unsupported_experience_shape` in `build_base_resume` / `build_resume_from_job` / `build_session_base_resume`; leftover-prose skip → raise. Stage 2: `api_resume_html` 400 for unsupported; JAR Print Resume fetch-then-blob + toast (Base/Session already toast API `error`). Tests deferred to Betty.

## Radia review — AST-1350

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1350  
**Publish ref:** `origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit` @ `81463c4c8edbad4920c88697117d5a1f06df435a`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent confidence paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No `agent.py` / task dispatch edits |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector validation |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/process/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No entity response persistence |
| `astral.config.config-source-of-truth` | scoped | conforms | Toast literal in `BUILD_CONFIG["unsupported_resume_structure_message"]`; builder/API read config |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No chain edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single issue doc |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Engineer commits: `src/` + `data/admin` n/a; tests/bible via Betty |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer commits exclude `tests/` and `docs/test-bible/` |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No render/verdict |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | Resume routes remain `@require_auth`; no auth regression |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Core owns refuse gate; UI surfaces API error only |
| `astral.layers.import-direction` | scoped | conforms | `api_resume_html` → `core` + `utils/config`; no layer bends |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/` |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Operator message config-owned; React does not encode shape rules |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No `agent_task.json` (AST-1349 scope) |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No boot seed |
| `astral.seed.define-approved` | scoped | not-applicable | Implementation ticket |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No operator rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No `src/data/` |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No DB/migration edits |
| `astral.standards.debug-contract-gated` | scoped | conforms | No new ungated debug emission on touched paths |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Single `_reject_unsupported_experience_shape` helper reused in three builders |
| `astral.standards.in-scope-only` | scoped | conforms | Engineer commits limited to plan files; no AST-1349/1351 smuggle |
| `astral.standards.logging-via-utils` | scoped | conforms | No new `print()` / raw logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | No ticket-id symbols |
| `astral.standards.no-cross-contamination` | scoped | conforms | Toast/no-emit only; no schema/prompt/array-layout work |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Message not duplicated in builder (config read) |
| `astral.standards.public-then-helpers` | scoped | conforms | Private helper after public `build_*` |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No utils→data |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state machine |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run chain |
| `astral.ui.frontend-file-placement` | scoped | conforms | JAR modal edit in `components/` |
| `astral.ui.naming-conventions` | scoped | conforms | No naming regressions |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `81463c4c merge-tests(AST-1350)` |
| `orch.git.commit-vocabulary` | universal | conforms | `code(AST-1350)` / `test(AST-1350)` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | `sub/AST-1345/...` off epic line |
| `orch.git.ftr-sub-topology` | universal | conforms | Child publish ref topology correct |
| `orch.git.merge-on-checkout` | universal | conforms | No checkout violations |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history |
| `orch.git.no-dev-agent-branches` | universal | conforms | `sub/` publish ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | `astral-AST-1345` worktree |
| `orch.git.three-permanent-branches` | universal | conforms | Baseline `origin/dev` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Implements Joan-approved plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | S1–S2 delivered |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Artifacts / AST-1345 child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed spawn |
| `orch.roles.archie-approves-statutes` | universal | conforms | Joan APPROVED @ `8984d14e` |
| `orch.roles.betty-owns-test-tree` | universal | conforms | `test(AST-1350)` + merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Hedy assignee |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Engineer path set clean |

**Active-set count scored in-session:** 64 rows; no `violates` / `needs-discussion` statute rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.layers.import-discipline` | conforms | Core gate + thin API/UI; UI does not import `data`/`external` |
| `pattern.config.config-block` | conforms | `BUILD_CONFIG` owns operator message; builder/API consume it |
| *(Joan informal citations)* `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets` | conforms | Covered by statute rows above |

## Plan adherence

**Engineer product commits** (`83ca5619` + `3b30b01b`) touch exactly four planned layers:

| Stage | Plan | Tip |
|-------|------|-----|
| **S1** | Config message + `_reject_unsupported_experience_shape` in `build_base_resume` / `build_resume_from_job` / `build_session_base_resume` **before** filter; defense-in-depth in `_emit_body_sections_html` | Delivered — gate uses `is_experience_job_array` (AST-1349 contract); leftover-prose `continue` removed → `ValueError` |
| **S2** | `api_resume_html` 400 for unsupported; JAR fetch-then-blob; Base/Session toast exact API `error` | API + JAR delivered; Base Print (`ArtifactsBaseResumeContent.handlePrint`) and Session Open HTML (`AdminSessionResumePaste.handleOpenHtml`) already fetch-then-toast API `error` without tab — from **AST-1337** / **AST-987**; no rewrite needed per plan “already mostly true” |
| **S2 session API** | `session_resume_html` already 400 + `str(exc)` | Confirmed on tip (`api_admin.py` L1563–1564) |

**Contract table verified:** key absent → allow; `[]` / list-of-dicts → allow; string / dict / non-array list → refuse with exact config message.

**Estimate 3:** Footprint matches (2 code commits, focused).

**Dependency:** Blocked by AST-1349 (UT) — `is_experience_job_array` predicate present on epic line; satisfied.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

1. **Three-dot diff vs `origin/dev` is ftr-aggregate noise** — `git diff origin/dev...publish-ref` warns multiple merge bases and includes sibling epic work (AST-1347/1348 config+JAR chrome, AST-1338 meteorite retry, `consult.py`, etc.) not authored in AST-1350 commits. For product review, filter to `83ca5619..3b30b01b` (4 files). No resolve-child action on AST-1350 product code.
2. **merge-tests piggyback** — Branch history includes `test(AST-1353)` (`b8b8771d`) before `merge-tests(AST-1350)`; pipeline-legal, unrelated to AC 7.
3. **Legacy builder fixture outside narrowed manifest** — `TestBuildResumeFromJob::test_renders_job_resume_with_keywords_resume_only_by_default` still passes `experience="Role A"` (string) into `build_resume_from_job`, which now raises. Betty bible documents revised AST-987/998/1304 rows but not this one; narrowed manifest excludes it. Recommend flipping that fixture to job-array (or expect `ValueError`) before a full `test_builder.py` module run — downstream hygiene, not an AST-1350 product defect.
4. **Session Open HTML** — No new AST-1350 frontend component test; coverage is core `TestAst1350UnsupportedExperienceShape` + existing Session fetch/toast pattern. Acceptable per bible manifest; optional UT could add Session unsupported-toast assertion later.
5. **`MaterialsPreviewModal`** — Joan noted unused iframe path; core gate still blocks Experience-omitted emit if wired later (out of ticket scope).

## What's solid

- Core refuses emit **before** `filter_content_to_resume_structure`, closing the “drop then omit Experience” hole the plan called out.
- Defense-in-depth: any `experience_detail` non-array in `_emit_body_sections_html` now raises (not only `experience` key).
- API maps unsupported `ValueError` → **400** + exact `error` string; other builder errors stay **404**.
- JAR Print Resume: fetch-then-blob + toast; no blind `window.open` on failure (component tests assert).
- Reuses AST-1349 `is_experience_job_array` without redefining schema or touching prompts.

## Frame diff

Since Joan APPROVED @ `8984d14e` and build stub @ `3b30b01b`:

| Commit | Delta |
|--------|-------|
| `83ca5619` | S1: `BUILD_CONFIG` message + builder gate + emit defense |
| `3b30b01b` | S2: `api_resume_html` 400 mapping + JAR `handlePrintResume` + Toast |
| `22925f50` | Betty: `TestAst1350*` + revised AST-987/998/1304 + bible rows |
| `81463c4c` | `merge-tests(AST-1350)` |

context_tokens≈48000

---

```
[code-rubric] PROCEED (Commit: 81463c4c) unsupported shape toast no emit
```

## Resolution

**2026-08-13** — Radia CLEAN (no fix-now / discuss). Advisory left as-is (ftr-aggregate diff noise; AST-1353 piggyback; legacy fixture hygiene for Betty; Session/Materials out of scope).

§9a: `origin/dev` dry-run clean. `origin/ftr/AST-1345-clarify-candidate-data-artifacts-base-resume-experience-node` merge-tree previously flagged overlap on `candidate.py` / `JobAnalysisReportModal.tsx` / `config.py` — resolved by merging ftr onto sub (`merge-resume(AST-1350)`); both dry-runs clean after (line-anchored conflict check).

## Bug: AST-1546 — gap: align Print blob-open tests with false popup-blocked toast fix

### As-is

Frontend component/page tests and bible rows still require `window.open(blobUrl, "_blank", "noopener,noreferrer")` on the four validate-then-blob Print / Open HTML success paths. JAR Print Resume success spies mock `window.open` → `null`, so there is no repro that a successful tab omits `Popup blocked — allow popups to open the HTML tab.` After AST-1545’s open-without-features + `opener = null` product fix, those third-arg asserts break and a null mock would still toast “blocked” on an otherwise successful print.

### To-be

Bible + tests match AST-1545’s blob-open shape (`window.open(blobUrl, "_blank")` with no features string; `win.opener = null` on success). At least one repro fails if success still surfaces the popup-blocked toast. Non-blob opens (e.g. JAR Print Cover Letter URL) stay on their existing `noopener,noreferrer` asserts.

### Repro

Against product tip that includes AST-1545 (open without features + `opener = null`):

1. Run `test_JobAnalysisReportModal.test.tsx` — **Print Resume fetch-then-blob…** with current third-arg assert → fails (call shape) or, if only the mock returns `null`, success path still toasts popup-blocked.
2. Same third-arg breakage on `test_ArtifactsBaseResumeContent` **AST-1337: … success opens blob tab**, `test_AdminSessionResumePaste` Open HTML success, `test_AdminSessionCoverLetter` Open HTML success.

### Root cause

`[board-betty] TESTS: REVISE` on AST-1545: coverage locked the old `noopener,noreferrer` third arg and never asserted “success ⇒ no popup-blocked toast.” Gap sibling owns the test/bible delta; AST-1545 owns product UI only.

### Proposed change

⚠️ **Decision:** This ticket changes **only** `docs/test-bible/frontend/components.md`, `docs/test-bible/frontend/pages.md`, and the matching component/page tests under `tests/component/frontend/`. Do **not** edit product UI (`JobAnalysisReportModal.tsx` / Base Resume / Session pages) — that is AST-1545. Do **not** change non-blob `window.open` asserts (JAR **Print Cover Letter** `/candidate/cover/…` with `"noopener,noreferrer"` stays).

1. **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`**
   - In **Print Resume fetch-then-blob; Print Cover still window.open (AST-1350)** and every other Print Resume success path that currently expects `toHaveBeenCalledWith("blob:…", "_blank", "noopener,noreferrer")` (including AST-1489 / AST-1490 Print Resume success spies around those blob asserts): change the blob-open expectation to `toHaveBeenCalledWith(<blobUrl>, "_blank")` — **no** third-arg `"noopener,noreferrer"`.
   - For those success paths: mock `window.open` to return a mutable fake window `{ opener: {} }` (not `null`). After Print Resume succeeds, assert `fakeWin.opener === null` and that the UI does **not** show text `Popup blocked — allow popups to open the HTML tab.` (same `getByText` / `queryByText` style as the existing unsupported-toast assert). That no-blocked-toast check is the **bug-repro** Betty flagged.
   - Leave Print Cover Letter `toHaveBeenCalledWith("/candidate/cover/…", "_blank", "noopener,noreferrer")` unchanged.
   - Leave **AST-1350: Print Resume unsupported toast — no tab** unchanged (still no `window.open` on 400).

2. **`tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`**
   - In **AST-1337: Print disabled with no candidate; success opens blob tab (§6c)**: replace the three-arg `window.open` expect with two-arg `("_blank")` only; assert returned stub’s `opener` is null after success; assert popup-blocked toast text is absent. Keep error/empty paths “never open a tab.”

3. **`tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx`**
   - Open HTML success: same two-arg open expect + `opener === null` + no popup-blocked toast. Error path unchanged.

4. **`tests/component/frontend/pages/test_AdminSessionCoverLetter.test.tsx`**
   - Open HTML success: same two-arg open expect + `opener === null` + no popup-blocked toast. Error/empty paths unchanged.

5. **`docs/test-bible/frontend/components.md`** — under **AST-1350 · AST-1345**: note blob Print Resume opens with `window.open(url, "_blank")` then `opener = null` (no features string); success must not toast popup-blocked; point the existing table/run command at the revised fetch-then-blob success case (and the no-blocked-toast repro). Do not claim Cover Letter print changed.

6. **`docs/test-bible/frontend/pages.md`** — under **AST-1337**, **AST-987**, and **AST-1025** blob-open rows: drop/rewrite any implication that success uses `"noopener,noreferrer"`; record success-path no-blocked-toast + `opener` cleared. Keep failed/empty → no tab.

### Blast radius

- Same four UI surfaces AST-1545 fixes; tests will fail against pre-AST-1545 product (third-arg / null-mock toast) and pass once AST-1545 is on the tree under test.
- AST-1489 / AST-1490 Print Resume success spies that reuse the third-arg blob assert must be updated in the same pass or they stay red.
- Unsupported-shape toast / no-tab coverage (AST-1350) and non-blob Cover `window.open` stay load-bearing.

### What must still hold

- AST-1350: unsupported experience still toasts exact `unsupported resume structure, please regenerate` with no tab.
- Failed / empty HTML paths still never call `window.open`.
- AST-1545 product behavior: success opens blob tab without popup-blocked toast; real null open still can toast blocked.
- No product UI edits on this ticket.
