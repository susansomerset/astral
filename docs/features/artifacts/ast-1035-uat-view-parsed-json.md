<!-- linear-archive: AST-1035 archived 2026-08-05 -->

## Linear archive (AST-1035)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1035/uat-view-parsed-json-button-on-session-resume-paste  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019

### Description

## What failed

Session Resume Paste has Parse and Open HTML, but no way to inspect the parsed resume JSON between those steps. Susan cannot tell whether a remaining UAT gap is in the parse/JSON structure or in the HTML renderer.

## Expected

A **View Parsed JSON** control between Parse and Open HTML that shows the current parsed resume JSON (post-Parse) so UAT can separate structure vs render issues.

## Repro

1. Open Session Resume Paste.
2. Paste a resume fixture and click Parse.
3. Observe controls: there is no View Parsed JSON between Parse and Open HTML.
4. Open HTML alone does not expose the intermediate JSON for debugging.

## Parent AC (quoted inline)

> Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on "close enough."
> Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No "close enough."

Susan confirmed this debug affordance is **in scope for AST-1019** (under-defined original specification): add View Parsed JSON between Parse and Open HTML.

## Diagnosis

* **Hypothesis:** Session Resume Paste UI only surfaces Parse → Open HTML; the in-memory/session parse result is not inspectable, so remaining format gaps cannot be attributed to JSON vs renderer.
* **Correct outcome:** After Parse, Susan can click View Parsed JSON and see the structured resume JSON used for Open HTML (read-only display is enough).
* **Wrong fix to avoid:** Dumping JSON into the resume HTML body; changing renderer contracts to "fix" missing fields; persisting session paste to the candidate DB; inventing new resume sections.
* **Related siblings / contracts:** AST-1020/1021 (render cosmetics); prior UAT bugs AST-1027–1030 (emit/markers); must not break AST-985/986/987 Session Resume Paste → Open HTML.

## Boundaries

* This bug does **not** change: golden stylesheet, marker/`__`/`~~` emit rules, meta/title contracts, cover-letter HTML, or candidate DB persistence.
* "Button exists" alone is not done — View Parsed JSON must show the same parse payload Open HTML consumes.

### Comments

#### radia — 2026-07-29T14:58:03.843Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1035
**Publish ref:** c0be4044e1ecc70a4af57dd46dc650785e510086
**Overall:** CLEAN

Diff basis: required `origin/dev...origin/sub/AST-1019/AST-1035-uat-view-parsed-json` reports **multiple merge bases** (noisy three-dot). Product review uses AST-1035 commits + `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies...HEAD` for the real child delta. Product @ `5f920814` / merge-tests tip `91d25515` + this `docs()` append.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1035): origin/tests 3538ee6e` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish to child `origin/sub/…` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019; ftr..sub is AST-1035 vocab only |
| orch.git.merge-on-checkout | universal | conforms | No alternate merge inventiveness |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Susan scoped debug affordance into AST-1019; no fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 Modal + `lastParse` Done-when matches tip |
| orch.pipeline.project-scoped-queues | universal | conforms | Single Artifacts bug child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Reviewed from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test` + `merge-tests`; Ada avoided test tree |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer product path is TSX page + plan |
| astral.agent.confidence-bounds | scoped | not-applicable | layers/paths miss — no `src/core/**` / config |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths miss — no batch/data/core |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths miss — no batch/data/core |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths miss — no batch/data/core |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths miss — no batch/data/core |
| astral.config.config-source-of-truth | scoped | conforms | No new config; UI reads existing `lastParse` only |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | paths miss — no scored config/core/data |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env; frontend page only |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss — no repo-root `artifacts/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/`; no spike pollution |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1035-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only tests/bible (+ merge-tests) |
| astral.git.engineer-test-tree-ban | scoped | conforms | Ada code/docs omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths miss — no `src/core/**` / external |
| astral.layers.import-direction | scoped | conforms | UI imports Modal/Toast/api/hooks only; no data/external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss — no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No hardcoded job/company/candidate state lists |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new endpoints; existing `api()` session_resume calls unchanged |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer path; UI error handling unchanged |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss — no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No backend debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses shared Modal + existing `lastParse` |
| astral.standards.in-scope-only | scoped | conforms | Single-page UI affordance only; no builder/DB/API |
| astral.standards.logging-via-utils | scoped | conforms | No new logging |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in `src/ui/frontend` page |
| astral.standards.no-hardcoded-sets | scoped | conforms | Modal `<pre>` colors match Manage Candidates pattern |
| astral.standards.public-then-helpers | scoped | conforms | Page-level control; no helper reorder inventiveness |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss — no `src/utils/**` |
| astral.state.core-decides-transitions | scoped | not-applicable | paths miss — no state-machine paths |
| astral.state.job-prior-states-enforced | scoped | not-applicable | paths miss — no job state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.ui.frontend-file-placement | scoped | conforms | Edit stays under `pages/AdminSessionResumePaste.tsx` |
| astral.ui.naming-conventions | scoped | conforms | Label **View Parsed JSON**; existing page naming |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker/RAILWAY knobs |

## Pattern conformance

none cited

## Plan adherence

Stage 1 matches: button between Parse and Open HTML; Modal + `JSON.stringify(lastParse)`; disabled when no payload; parse/html contracts untouched. Scope Single-Component matches. Engineer commit touches only `AdminSessionResumePaste.tsx`.

## Findings

None.

### What’s solid

Same `lastParse` Open HTML already POSTs — inspect without a second fetch or JSON-in-HTML dump.

### Recommended actions

resolve-child → User Testing.

**Notes:** no plan-rubric verdict attached. Three-dot vs `origin/dev` multiple-merge-base noise; product judgment uses AST-1035 commits + ftr…HEAD delta.

— Radia
context_tokens≈38000

#### betty — 2026-07-29T14:54:48.317Z
## QA test manifest (AST-1035)

**Publish:** `origin/sub/AST-1019/AST-1035-uat-view-parsed-json` @ `91d25515` (`merge-tests(AST-1035): origin/tests 3538ee6e`)

**FIX-UAT:** `docs/test-bible/**` on `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` vs `origin/tests` = trivial `tracker.md` blank-line only — skipped full bible re-read; grepped Session Resume Paste + §6c.

### Classification

1. **Existing coverage:** AST-987 `test_AdminSessionResumePaste.test.tsx` (render/parse/Open HTML/localStorage); AST-986 parse core/API.
2. **Broken / obsolete:** none — additive UI; extended AST-987 page suite in place.
3. **Gaps:** View Parsed JSON between Parse and Open HTML; modal shows exact `lastParse`; close keeps payload (§6c page render).

### Manifest (narrowed)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx
```

### Bible shasums (on publish ref)

- `docs/test-bible/frontend/pages.md` `1279d91629da8caa9cb3db3d43a1f3402bbec6ee`

#### ada — 2026-07-29T14:50:23.168Z
Plan Ready — [docs/features/artifacts/ast-1035-uat-view-parsed-json.md](https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1035-uat-view-parsed-json/docs/features/artifacts/ast-1035-uat-view-parsed-json.md) on `origin/sub/AST-1019/AST-1035-uat-view-parsed-json` (`95156909`).

**Scope:** Single-Component — `AdminSessionResumePaste.tsx` only: **View Parsed JSON** between Parse and Open HTML, Modal + `JSON.stringify(lastParse)` (same `{resume_structure, base_resume}` Open HTML already POSTs). No new API; no DB; no builder/CSS.

**Conf:** high — `lastParse` already retained after Parse; Open HTML posts it; Manage Candidates Modal+`<pre>` pattern exists.

**Risk:** low — additive UI; disabled when `!lastParse`; parse/html contracts untouched.

---

# UAT: View Parsed JSON button on Session Resume Paste

**Linear:** [AST-1035](https://linear.app/astralcareermatch/issue/AST-1035/uat-view-parsed-json-button-on-session-resume-paste)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1035-uat-view-parsed-json`

Session Resume Paste already keeps the successful Parse payload in `lastParse` (`resume_structure` + `base_resume`) and posts that same object to Open HTML — but the UI only exposes Parse and Open HTML controls. Susan cannot inspect the intermediate JSON to tell whether a remaining UAT gap is structure vs renderer. Add a **View Parsed JSON** control between those two buttons that shows the current `lastParse` payload read-only.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Fixture-driven UAT: Original-brief input paste → Open HTML matches desired structure + cosmetics (eye + HTML source). No ‘close enough.’”* Susan confirmed this debug affordance is **in scope for AST-1019** (under-defined original specification).
- **Correct outcome:** After a successful Parse, Susan can click **View Parsed JSON** (placed between Parse and Open HTML) and see the structured resume JSON — the same `resume_structure` + `base_resume` object Open HTML consumes — in a read-only display. Button disabled when there is no successful parse payload.
- **Sibling check:** AST-1020/1021 render cosmetics unchanged. AST-1027–1030 emit/marker contracts unchanged. AST-985/986/987 Session Resume Paste → Open HTML path unchanged (same `lastParse` body to `/api/admin/session_resume/html`). Verify: no new API; no candidate DB write; no JSON dumped into resume HTML.
- **Not sufficient:** Button label alone is **not** done — the view must show the same parse payload Open HTML uses.
- **Wrong fix rejected:** Dumping JSON into the resume HTML body; changing renderer contracts to invent missing fields; persisting session paste to the candidate DB; inventing new resume sections; a separate fetch that could diverge from `lastParse`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | Add **View Parsed JSON** between Parse and Open HTML; read-only display of `lastParse` (same object Open HTML posts) | ui/frontend |

**Out of scope (do not touch):** `src/core/builder.py` / stylesheet / marker emit; `/session_resume/parse` or `/html` contracts except as already consumed; cover-letter page; candidate DB persistence; `tests/` / bible (Betty).

## Root cause (plan-time)

`AdminSessionResumePaste.tsx` already stores `SessionResumeParse = { resume_structure, base_resume }` in `session_resume:last_parse` and `handleOpenHtml` POSTs `JSON.stringify(lastParse)` to `/api/admin/session_resume/html`. The button row only renders Parse + Open HTML — no inspect control. No backend gap for this UAT ask; the payload is already in memory/localStorage after Parse.

**Git hygiene:** Keep `origin/sub/AST-1019/AST-1035-uat-view-parsed-json` rooted on current `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` with only AST-1035 vocabulary commits in the `ftr..sub` range. Do **not** leave subjects matching `Merge remote-tracking branch` (validate-sub-log / merge-child gate).

## Stage 1: View Parsed JSON control + read-only display

**Done when:** On Session Resume Paste, after a successful Parse, a **View Parsed JSON** button sits between **Parse** and **Open HTML**; it is disabled when `lastParse` is null (and while parsing/opening as appropriate); activating it shows a read-only pretty-printed JSON of the **exact** `lastParse` object (`resume_structure` + `base_resume`) that Open HTML would POST; closing the view returns to the page without clearing `lastParse` or changing paste text. No new API routes. No changes to parse/html backend handlers.

1. In `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`:
   - Import the shared `Modal` component used by other admin pages (same pattern as `AdminManageCandidates.tsx` JSON view modal).
   - Add React state for whether the JSON modal is open (e.g. `jsonOpen` boolean), default `false`.
   - In the button row (`display: flex` after the textarea), insert a **View Parsed JSON** button **between** Parse and Open HTML:
     - `type="button"`, class consistent with siblings (`dep-btn` is fine — not the primary `save` style unless Parse stays primary).
     - Label: `View Parsed JSON`.
     - `disabled={!lastParse || parsing || opening}` (same gating spirit as Open HTML — no payload → disabled).
     - `onClick` sets the modal open (`true`). Does **not** call any API.
   - Render `<Modal open={jsonOpen} onClose={…} title="Parsed resume JSON">` (title may be tightened; must clearly identify the parse payload) containing a `<pre>` with `JSON.stringify(lastParse, null, 2)` when `lastParse` is non-null. Style the `<pre>` like Manage Candidates’ view modal (`whiteSpace: pre-wrap`, scrollable `maxHeight`, monospace-friendly font size) — reuse that look, do not invent a new design system.
   - Modal close must only clear `jsonOpen`; leave `lastParse` / localStorage intact.
2. Optionally tighten the page blurb one sentence to mention View Parsed JSON between Parse and Open HTML (keep it short; do not rewrite the whole help text).
3. Do **not** change `handleParse` / `handleOpenHtml` request/response contracts.
4. Do **not** add backend routes or persist JSON to the candidate DB.
5. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Modal + `JSON.stringify(lastParse)` (not a new-tab blob and not an inline always-visible dump). Modal matches existing admin “view JSON” UX (`AdminManageCandidates`); showing `lastParse` guarantees identity with the Open HTML POST body without a second fetch. New-tab would work but adds popup-blocker noise next to Open HTML.

## Stage 2: Compile check + manual smoke (build verification)

**Done when:** `npx tsc -b --noEmit` under `src/ui/frontend` passes after Stage 1. Manual/build smoke: with mocked or live session, Parse success → View Parsed JSON enabled → modal shows both `resume_structure` and `base_resume` keys; Open HTML still posts the same object; before Parse, View Parsed JSON is disabled. Spike dumps only under `debug/spikes/AST-1035/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, run `cd src/ui/frontend && npx tsc -b --noEmit` after the TSX edit.
2. Confirm `git diff` does not touch `src/core/**`, `data/admin/**`, or test-tree paths.
3. Note for UAT: after deploy, Session Resume Paste → Parse → View Parsed JSON → confirm JSON matches what Open HTML uses; then Open HTML still works.
4. If Modal import path or shared Modal API differs from Manage Candidates in a way that blocks a literal reuse, **stop**, comment on **bug** AST-1035 with the Stage blocked template (propose the concrete Modal import that exists), and wait.

## Self-Assessment

**Scope:** `Single-Component` — `AdminSessionResumePaste.tsx` only (UI control + read-only Modal over existing `lastParse`).

**Conf:** `high` — payload already in `lastParse`; Open HTML already posts it; Manage Candidates Modal+`<pre>` pattern exists on the same frontend.

**Risk:** `low` — additive UI only; no parse/html contract change; disabled state mirrors Open HTML gating.

## Code Rules self-review

- §1.3 DRY: reuse shared `Modal` + existing `lastParse`; no parallel parse fetch.
- §1.1 / scope isolation: no builder/CSS/marker edits; no DB persistence; no cover-letter page edits.
- §3.5 naming: button label matches ticket (**View Parsed JSON**).
- §3.6: spikes under `debug/spikes/AST-1035/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1035
**Publish ref tip (pre-docs):** `91d25515c9cd4c458394a4e8351556d5569ac68c`
**Overall:** CLEAN

### What’s solid

- **View Parsed JSON** between Parse and Open HTML; disabled when `!lastParse` (and while parsing/opening).
- Modal + `JSON.stringify(lastParse, null, 2)` — same object Open HTML POSTs; shared `Modal` + Manage Candidates `<pre>` look.
- No new API / DB / builder edits. Engineer footprint is one TSX file + plan.

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing.
