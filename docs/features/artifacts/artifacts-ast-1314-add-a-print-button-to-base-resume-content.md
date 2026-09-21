# AST-1314 — Add a Print button to Base Resume Content
**Component:** artifacts  
**Children:** AST-1337, AST-1341, AST-1342  
**Linear archived:** AST-1314 2026-08-31; AST-1337 2026-08-31; AST-1341 2026-08-31; AST-1342 2026-08-31

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-12 07:56 | AST-1337 | docs | `a4e72815b` | docs(AST-1337): plan — print control on base resume content |
| 2026-08-12 07:59 | AST-1337 | docs | `f2eb10098` | docs(AST-1337): Joan validate — plan approved |
| 2026-08-12 08:02 | AST-1337 | docs | `3719b06b0` | docs(AST-1337): review stub after base resume Print build |
| 2026-08-12 08:02 | AST-1337 | code | `c4f30b515` | code(AST-1337): Print control on Base Resume Content |
| 2026-08-12 08:05 | AST-1337 | test | `2dc40a0c4` | test(AST-1337): Base Resume Content Print validate-then-blob |
| 2026-08-12 08:05 | AST-1337 | merge-tests | `63ba62d5b` | merge-tests(AST-1337): origin/tests 2dc40a0c452b3afa8a86dcfce375aa4d75c30893 |
| 2026-08-12 08:08 | AST-1337 | docs | `91410146e` | docs(AST-1337): Radia review — clean |
| 2026-08-12 16:19 | AST-1342 | docs | `af39043a1` | docs(AST-1342): plan-fix — Print next to Regenerate |
| 2026-08-12 16:21 | AST-1341 | docs | `c7a29266e` | docs(AST-1341): plan-fix — Print false-missing base_resume |
| 2026-08-12 16:21 | AST-1342 | test | `2f0a86889` / `bf9d6fca6` | test(AST-1342): bug-repro — Print in dep-actions next to Regenerate |
| 2026-08-12 16:23 | AST-1342 | code | `5af26e827` | code(AST-1342): Print next to Regenerate in dep-actions |
| 2026-08-12 16:24 | AST-1341 | test | `a750e4424` / `d777d7048` | test(AST-1341): bug-repro — list-shaped base_resume print |
| 2026-08-12 16:26 | AST-1341 | code | `1abf0e4e7` | code(AST-1341): ingest list-shaped base_resume for Print |
| 2026-08-12 16:27 | AST-1342 | merge-tests | `5ac37297f` | merge-tests(AST-1342): origin/tests 2f0a8688 (clean rebuild onto ftr) |
| 2026-08-12 16:27 | AST-1342 | docs | `79391f38e` | docs(AST-1342): Radia review — clean after ftr rebase |
| 2026-08-12 16:29 | AST-1341 | docs | `e2a38d240` | docs(AST-1341): Radia review-fix — clean rebuild notes |
| 2026-08-12 16:30 | AST-1341 | merge-tests | `8445c7929` | merge-tests(AST-1341): origin/tests a750e4424e2767dfb24232fab3db218fb340d94e |
| 2026-08-12 18:45 | AST-1314 | merge-child | `978435c53` | merge-child(): refresh-ftr — origin/dev into ftr/AST-1314 (1341 ingest + 1350/1351 experience) |
| 2026-08-14 11:37 | AST-1314 | docs | `38cb7ba87` | docs(AST-1314): mirror epic registry Threads |
| 2026-08-31 14:13 | AST-1337 | docs | `3b3f4863e` | docs(AST-1337): archive Linear issue content |
| 2026-08-31 14:13 | AST-1341 | docs | `cfcd38f50` | docs(AST-1341): archive Linear issue content |
| 2026-08-31 14:13 | AST-1342 | docs | `b14556ba5` | docs(AST-1342): archive Linear issue content |
| 2026-08-31 14:17 | AST-1314 | docs | `23089908e` | docs(AST-1314): archive Linear issue content |

_The `refresh-ftr` merge-child note (2026-08-12 18:45) mentions AST-1350/1351 in its parenthetical — those belong to a different family (F22, AST-1345) and merely rode along on the same `origin/dev` refresh; no product content from that family is part of this one. One row of unrelated cross-ticket noise excluded from the table above: `test(AST-1489): bug-repro — print-before-PUT page-break auto-persist` (2026-08-26, a later F29 family commit whose body cites AST-1337 as a related pattern). AST-1341 and AST-1342 each went through one `[merge-child] blocked` cycle — their sub-branches had been contaminated with unrelated meteorite/AST-dev history, and Chuckles mechanically rebuilt each clean onto `origin/ftr/AST-1314` via cherry-pick of only that ticket's `docs()`/`test()`/`code()` commits (documented in each ticket's own Radia review-fix note below) — not a product defect. One inbound reference from outside this folder was found and left as-is (not edited): `docs/features/interface/ast-1274-restore-recommended-job-detail-open.md` cites `docs/features/artifacts/ast-1337-print-control-on-base-resume-content.md` by path inside a Radia review finding, documenting that an unrelated AST-1355 sub-branch improperly carried AST-1341/1342 product/plan-fix content in its diff — a historical citation of a scope violation, not a live navigation link, so it is reported here rather than retargeted._

## Epic — AST-1314
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1314/add-a-print-button-to-base-resume-content · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Medium / 2 · Blocked by / blocks / related: —_

### Purpose

Operators author and save a candidate's Base Resume Content, but they cannot open a print-ready HTML preview from that page the way they already can from Admin Session Resume Paste. This epic adds a Print control on Base Resume Content so Susan can verify structure, section formats, accent, and body content via browser Print → PDF before relying on job-tailored Print Resume elsewhere.

### Functional scope

* With a candidate selected on Artifacts → Base Resume Content, a Print control is available when that candidate has printable base resume content.
* Activating Print opens a new browser tab with print-ready HTML rendered from the selected candidate's saved base resume content and resume structure — the same operator outcome as Session Resume Paste's Open HTML flow. No job id is required.
* Failed or empty HTML never opens a blank/broken tab as if success occurred; the Base Resume Content page surfaces a clear error instead.
* Print uses last-saved candidate base resume content and structure (not an unsaved in-editor draft buffer).

### Architectural definition

* **Patterns to reuse** — `pattern.ui.shared-button-roles` (Print is a neutral alternate labeled control: `btn` + `secondary`, not a one-off style); Session Resume Paste's established Open-HTML → new-tab operator flow (error-check response before opening a tab). Prefer the existing authenticated candidate base HTML surface (`/candidate/resume/base` + `build_base_resume`) as the candidate-bound sibling to Admin Session Resume Paste's in-memory HTML path — do not invent a third emit pipeline.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.idioms.require-auth-on-protected-endpoints`; `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`.

### Boundaries

* Does **not** change Admin Session Resume Paste, its parse API, or admin-only `POST /api/admin/session_resume/html`.
* Does **not** change job Print Resume / Print Cover Letter on the Recommended Job Report.
* Does **not** generate server-side PDF; operator uses browser Print → PDF from the HTML tab.
* Does **not** print unsaved editor buffer state; Save first, then Print.
* Does **not** own craft/parse hops, structure catalog changes, or Highlights-required work (AST-1326 and children).
* Does **not** alter cover-letter emit or Session Cover Letter.

### Acceptance criteria

1. On Base Resume Content with a selected candidate that has saved printable base resume content, Susan can activate Print and get a new tab of print-ready HTML for that candidate's base resume (structure order, section titles/formats, accent as already emitted by the base-resume builder).
2. Susan can use the browser's Print → PDF from that tab without needing a job id or leaving Artifacts for Session Resume Paste.
3. With no candidate selected, or when base resume content is missing/unusable, Print is unavailable or fails with a clear on-page error — and no blank HTML tab opens.
4. A failed HTML response never opens a success-looking blank/broken tab.
5. Job Print Resume / Print Cover Letter and Session Resume Paste behavior are unchanged.

### Dependencies and blockers

none. Candidate base HTML emit (`build_base_resume` / `/candidate/resume/base`) and format-aware section emit (AST-1304) already exist. AST-1326 (Highlights required) is adjacent authoring work, not a blocker for Print.

### Open questions

none

### Proposed child tickets

**1: Print control on Base Resume Content — Katherine** — Wire a Print control on Artifacts → Base Resume Content for the selected candidate. On success, open print-ready HTML in a new tab using the same operator flow as Session Resume Paste Open HTML (validate response, then open tab; no blank tab on failure). Source is the candidate's saved base resume content via the existing candidate-bound base HTML path — not Admin session paste and not job-tailored resume routes. Does **not** own emit pipeline changes beyond wiring, Session Resume Paste, or job Print controls.
**Citations:** `pattern.ui.shared-button-roles`; `astral.idioms.require-auth-on-protected-endpoints`; `astral.ui.frontend-file-placement`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`
**Estimate: 2**

Monolith check: Functional scope has four bullets but one inseparable UI wire to an existing emit surface — single child intentional.

### Original brief

Use the same method as is used in the Session Resume Paste, but use the candidate's base resume content.

#### Comments

##### susan — 2026-08-12T17:40:17.616Z
\[bug\]

Clicking the button while looking at the base_resume I'm looking at generates an error:

```
Astral error diagnostic
timestamp: 2026-08-12T17:40:04.654Z
message: Candidate missing artifacts.base_resume
route: /artifacts/base_resume_content
astral_candidate_id: abrams
```

##### susan — 2026-08-12T17:46:30.383Z
\[bug\]

When adding buttons to a page, or any UI additions or changes, consider in the planning process the appropriate location, if not specified, to make that change or to put that button. In this case, the button was placed at the top of the screen, unstyled like the others, etc.

Meanwhile, put the Print button next to the Regenerate button, please.

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree only carries the `merge-child()` refresh-ftr commit and the epic-registry Threads mirror / `docs(AST-1314)` archive commits. Implementation landed entirely via the sub-issue below and its two UAT bug tickets._

## Sub-issues

### AST-1337 — Print control on Base Resume Content
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1337/print-control-on-base-resume-content-add-a-print-button-to-base-resume · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1314_

#### What this implements

Wire a Print control on Artifacts → Base Resume Content for the selected candidate. On success, open print-ready HTML in a new tab using the same operator flow as Session Resume Paste Open HTML (validate response, then open tab; no blank tab on failure). Source is the candidate's saved base resume content via the existing candidate-bound base HTML path — not Admin session paste and not job-tailored resume routes.

#### Acceptance criteria

- [X] 1. On Base Resume Content with a selected candidate that has saved printable base resume content, Susan can activate Print and get a new tab of print-ready HTML for that candidate's base resume.
- [X] 2. Susan can use the browser's Print → PDF from that tab without needing a job id or leaving Artifacts for Session Resume Paste.
- [X] 3. With no candidate selected, or when base resume content is missing/unusable, Print is unavailable or fails with a clear on-page error — and no blank HTML tab opens.
- [X] 4. A failed HTML response never opens a success-looking blank/broken tab.
- [X] 5. Job Print Resume / Print Cover Letter and Session Resume Paste behavior are unchanged.

#### Boundaries

Does not own emit pipeline changes beyond wiring. Does not change Session Resume Paste or job Print Resume / Print Cover Letter. Does not print unsaved editor buffer. Does not own Highlights-required work (AST-1326).

#### Notes for planning

Reuse `/candidate/resume/base` + `build_base_resume` (or equivalent authenticated candidate base HTML) with Session-style validate-then-open-tab UX. Print = `btn secondary`.

#### UAT fitness (plan doc)

**AC restored** (all five, verbatim from the ticket — see Acceptance criteria above). **Correct outcome:** from Base Resume Content, Print yields a usable print-ready HTML tab for the **selected candidate's saved** base resume (same emit path as `/candidate/resume/base`), then browser Print → PDF works — not merely "no error toast." **Sibling check:** this epic has a single proposed child; adjacent Highlights work (AST-1326) is out of scope. **Not sufficient:** removing a stacktrace/exception/5xx alone is not done. **Wrong fix rejected:** `window.open("/candidate/resume/base?candidate_id=…")` like job Print — can open a tab before the body is known (JSON 404 / empty / SPA miss looks like a broken success tab); parent requires Session-style validate-then-open. Also rejected: calling Admin `POST /api/admin/session_resume/html` or reading the in-editor dirty buffer — wrong source and out of boundaries.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Add Print (`btn secondary`): auth-fetch `GET /candidate/resume/base?candidate_id=…`, validate, open blob tab; on-page error + toast; disable when no candidate / in-flight | ui |

**Do not touch:** `AdminSessionResumePaste.tsx`, `AdminSessionCoverLetter.tsx`, `JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx`, `api_resume_html.py`, `api_admin.py` session HTML, `builder.py`, `ArtifactEditor.tsx` (shared Generate/Save chrome — Print stays page-local at this stage), `routes.tsx`, vite proxy, `tests/**`, `docs/test-bible/**`.

#### Stage 1 — Print control + validate-then-open tab

`handlePrint` mirrors `AdminSessionResumePaste.handleOpenHtml`: guards on `!selectedId || printing`; fetches via the shared `api()` helper (Bearer auth) against `GET /candidate/resume/base?candidate_id=…`; on `!r.ok` parses a JSON `error` string (else `HTTP {status}`), sets on-page error + toast, returns **without** opening a tab; on empty response text, same error-without-tab path; only on success builds a `Blob`/`URL.createObjectURL` and `window.open(blobUrl, "_blank", "noopener,noreferrer")`, with a popup-blocked toast fallback and a 60s `revokeObjectURL`. Label **Print** / in-flight **Opening…**, class `btn secondary`, disabled when `!selectedId || printing`, placed in a small action row above `<ArtifactEditor>`.

⚠️ **Decision:** Validate-then-blob via `api()` + `GET /candidate/resume/base`, not `window.open` of the HTML URL directly — matches Session Open HTML and parent AC 3–4; reuses the existing `@require_auth` route + `build_base_resume`, no new endpoint. ⚠️ **Decision:** Do not preflight by reading ArtifactEditor tab state or the unsaved buffer — Print always hits saved candidate content on the server (Save first, then Print); missing content surfaces as 404/empty with on-page error and no tab. ⚠️ **Decision:** Keep Print page-local at this stage — do not add a header slot to `ArtifactEditor` (would touch every ArtifactEditor consumer); place a small action row above the editor instead. (This decision is explicitly reversed by AST-1342 below.)

#### Plan review — Joan, APPROVED

**acceptable** — deliberate Session mirror (DRY): `handlePrint` closely mirrors `AdminSessionResumePaste.handleOpenHtml` (~40 lines); acceptable since the parent requires Session-style validate-then-open and the plan keeps scope to one page file, naming the mirror explicitly. Optional future extract to `lib/` only if a third call site appears.

#### QA test manifest — Betty

Gaps (new): `AST-1337: Print disabled with no candidate; success opens blob tab (§6c)`; `AST-1337: Print error and empty HTML never open a tab` (§6c routed page), both in `test_ArtifactsBaseResumeContent.test.tsx`. Existing coverage (structure/accent/AST-1306/AST-1323/AST-1325) left alone. No broken/obsolete. No existing integration scenario asserted Base Resume Content Print.

#### Radia review — code-rubric.v1, CLEAN

Full 64-statute active-set sweep (registry states 65; corpus scored from README + universal block): all conforms/not-applicable, no violations. **Plan adherence:** validate-then-blob mirrors `AdminSessionResumePaste.handleOpenHtml` exactly (fetch → `!r.ok` JSON-error parse → empty-body guard → blob URL + `window.open` → popup-blocked toast → 60s revoke); source is `GET /candidate/resume/base?candidate_id=…` (saved server content, not editor buffer or admin POST); placement above `ArtifactEditor`, no header slot; Session Paste / job Print routes / `api_resume_html.py` / `builder.py` untouched. Estimate 2 matches footprint.

**Advisory (not blocking):** stale `printError` on candidate switch — not cleared when `selectedId` changes, so a failed Print for candidate A may still show A's error after switching to B until the next Print attempt; low severity, optional `setPrintError(null)` in the `selectedId` effect. **Advisory:** on popup-blocked (`!win`), only the toast fires, no `printError` line — same as Session Paste, acceptable.

**What's solid:** Session mirror correctly wired to the existing `@require_auth` route; error paths never call `window.open`; `btn secondary` + disabled rule match plan and `pattern.ui.shared-button-roles`; no scope smuggling from Session/job Print siblings.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `ArtifactsBaseResumeContent.tsx` | Print control, validate-then-blob | `c4f30b515` — +63 |
| | _tests_ | Print disabled/success/error-no-tab coverage | `2dc40a0c4`; bible `docs/test-bible/frontend/pages.md` § AST-1337 @ `35d501e624da7d2bb22f8eee8e92fca3f5c7d44e` |

### AST-1341 — Print false-missing artifacts.base_resume
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1341/print-base-resume-content-errors-candidate-missing-artifactsbase-resume · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1314_

#### As-is

On Base Resume Content for candidate `abrams`, Print fails with `Candidate missing artifacts.base_resume` (error toast / click-to-copy diagnostic) instead of opening print-ready HTML, even while the operator is viewing that candidate's base resume content in the editor.

#### To-be

Print opens print-ready HTML for the selected candidate's saved base resume when the editor can already show that content. If there is truly nothing printable, show a clear content-missing message (on-page + toast) that does **not** read like an internal hard crash — and still open no blank tab.

#### Repro

Candidate whose saved `artifacts.base_resume` is a non-empty **list** of `{label, content}` rows (or another shape the Base Resume Content editor already maps into section tabs): section bodies are visible in the editor, but clicking Print fails with `Candidate missing artifacts.base_resume` and no HTML tab.

```json
{
  "artifacts": {
    "base_resume": [
      { "label": "Summary", "content": "Visible in editor" },
      { "label": "Skills", "content": "Also visible" }
    ],
    "resume_structure": { "sections": {} }
  }
}
```

`GET /api/candidates/<id>` + ArtifactEditor `mapFixedFieldsFromRaw` shows the list; current `build_base_resume` rejects it because `not isinstance(br, dict)`.

#### Root cause

`build_base_resume` in `src/core/builder.py` loaded raw `artifacts.base_resume` and failed closed with `Candidate missing artifacts.base_resume` unless it was already a **non-empty dict**. Base Resume Content's editor (and the candidate PUT path) already accept list **or** dict via `ingest_legacy_label_content_base_resume` / `mapFixedFieldsFromRaw`. Print never ran that ingest, so saved list-shaped (or title-keyed-until-ingest) content the operator was looking at was treated as "missing." The internal key-path error string then surfaced through the error toast diagnostic bundle and looked like a crash.

#### Proposed change

Scope: make Print succeed for the same saved shapes the Base Resume Content page already displays. Do not print the unsaved editor buffer. Do not change Session Resume Paste or job Print routes.

In `build_base_resume`: after coercing the candidate blob, resolve structure via `resolve_resume_structure(cd)`; if raw `artifacts.base_resume` is a list or dict, normalize it with the **same** helper the PUT path uses — `ingest_legacy_label_content_base_resume(raw, structure)` — and use the returned `(content, structure)` pair for the rest of the emit so legacy-label extras stay aligned with PUT; if raw is missing/wrong type, treat as empty content but keep the resolved structure. Replace the old `isinstance(br, dict) or not br` gate with a printable-content check on `content` **after** ingest (`if not content:`), raising a new operator-facing error `"No printable base resume content for this candidate"` — the old `Candidate missing artifacts.base_resume` string is retired for this path. Continue the existing emit (`filter_content_to_resume_structure`, contact apply, markers, `_emit_html_document`) unchanged aside from consuming the ingested content/structure. `api_resume_html.py`'s `@require_auth` route stays a thin wrapper still mapping `ValueError` → 404 JSON. On the frontend, `handlePrint`'s error path recognizes the new operator sentence and surfaces it as on-page error + toast without attaching a diagnostics/stacktrace bundle for this expected empty case; other HTTP failures keep today's behavior.

⚠️ **Decision:** Fix at `build_base_resume` with `ingest_legacy_label_content_base_resume` (same contract as candidate PUT), not by teaching the React Print handler to POST editor tabs or call Admin session HTML. Rejected: printing the dirty unsaved buffer (parent boundary). Rejected: only renaming the error without running ingest (would leave list-shaped abrams broken).

#### Blast radius

`build_base_resume` is also used only by `GET /candidate/resume/base` for this Print path — job `build_resume` already has its own base_resume fallback via `_is_nonempty_resume_dict` and does not use this gate. Candidates with list-shaped or title-keyed saved `base_resume` that the editor already shows start printing (intended). Truly empty/missing base resume: message text changes.

#### Radia review-fix — REVIEW → Chuckles rebuild, then PROCEED

**fix-now (Chuckles mechanical — done):** the sub had been contaminated with unrelated meteorite + AST-1342 test history. Rebuilt `origin/sub/AST-1314/AST-1341-…` from `origin/ftr/AST-1314-…` + cherry-picked only this ticket's `docs(AST-1341)` / `test(AST-1341)` / `code(AST-1341)` commits. **Product:** PROCEED after the clean rebuild — `build_base_resume` list ingest + operator error copy; Betty bug-repro on list-shaped print. **Advisory:** empty-content gate is plan-minimum; bug-repro comment tag format advisory only.

#### What must still hold

AST-1337 AC1–5 (validate-then-blob; no blank tab on failure; auth GET; `btn secondary`; Session/job Print unchanged; saved content only). `ingest_legacy_label_content_base_resume` / PUT normalize contract unchanged (Print calls it read-only). No new emit pipeline; no Admin `session_resume/html` for this page.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/builder.py` | `build_base_resume` list/dict ingest via `ingest_legacy_label_content_base_resume`; new operator error string | `1abf0e4e7` (with page TSX) — +19/-5 across two files |
| ✓ | `ArtifactsBaseResumeContent.tsx` | Frontend recognizes new error sentence, no diagnostics bundle for the empty case | `1abf0e4e7` — see above |
| | _tests_ | list-shaped base_resume print bug-repro | `a750e4424`/`d777d7048`; bible per Betty manifest |

### AST-1342 — Print button placement: put next to Regenerate (match page chrome)
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1342/print-button-placement-put-next-to-regenerate-match-page-chrome · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1314_

#### As-is

Print is rendered in a standalone row above `<ArtifactEditor>` on Base Resume Content, separate from the page's `dep-header` / `dep-actions` chrome where Generate/Regenerate lives — so it looks orphaned and not of the same control family as the other primary actions.

#### To-be

Print sits in the Base Resume Content header action row **next to** the Generate/Regenerate control (same `dep-actions` strip), still `btn secondary`, still validate-then-blob Print behavior from AST-1337.

#### Root cause

AST-1337 Stage 1 deliberately kept Print page-local and rejected an ArtifactEditor header slot (to avoid touching every ArtifactEditor consumer). That placement choice is the defect relative to UAT chrome expectations: Regenerate is inside `ArtifactEditor`'s `dep-actions`, so a page-level row above the editor cannot sit "next to" it.

#### Proposed change

Placement/styling delta only — do not change Print fetch/validate/blob logic, labels, disable rules, toast, or error copy. `ArtifactEditor.tsx` gains an optional `headerActions?: React.ReactNode` prop, rendered in the existing `dep-actions` div immediately after the Generate/Regenerate block and before the Cancel/Save-or-status-span branch — so Print sits next to Regenerate when both show, and still appears when Generate is hidden. Other ArtifactEditor call sites omit the prop → no visual change for them. `ArtifactsBaseResumeContent.tsx` removes the standalone Print wrapper div and instead passes the Print button as `headerActions` into `<ArtifactEditor>`; the on-page `printError` block stays above the editor (unchanged styling) so failed Print still surfaces without opening a tab.

⚠️ **Decision:** Optional `headerActions` slot on ArtifactEditor (not a base_resume-only special case inside the editor) — reverses the AST-1337 "no ArtifactEditor slot" decision for placement only; Print behavior stays owned by the page. Rejected: CSS repositioning the orphan row. Rejected: hardcoding Print inside ArtifactEditor.

#### Blast radius

`ArtifactEditor` is shared by other artifact pages; the opt-in prop defaults off so it must not alter Generate/Save paths for those consumers. Betty's AST-1337 §6c cases querying Print by role/name should still find the button after the move.

#### Radia review-fix — REVIEW → Chuckles rebuild, then CLEAN

**fix-now (resolved):** publish-ref scope contamination (meteorite/dev history bleeding onto the sub) — fixed by force-with-lease rewrite onto the `ftr` tip, cherry-picking only plan/test/code for this ticket. **Discuss:** none. **Advisory:** no-candidate Print visibility is now absent entirely (ArtifactEditor early return) versus the prior "disabled but visible" state — Betty's suite accepts either; the plan had specified disabled-but-visible. Not corrected — accepted as a minor UX variance.

#### What must still hold

AST-1337 AC1–5: Print still opens print-ready HTML via auth `GET /candidate/resume/base?candidate_id=…` + validate-then-blob; no blank tab on failure; on-page error + toast; disabled with no candidate; Session/job Print unchanged; prints saved base resume only. Print remains `btn secondary`.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `ArtifactEditor.tsx` | `headerActions` prop rendered in `dep-actions` | `5af26e827` (with page TSX) — +16/-11 across two files |
| ✓ | `ArtifactsBaseResumeContent.tsx` | Remove standalone Print row; pass Print as `headerActions` | `5af26e827` — see above |
| | _tests_ | Print in dep-actions next to Regenerate bug-repro | `2f0a86889`/`bf9d6fca6`; bible per Betty manifest |
