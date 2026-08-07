<!-- linear-archive: AST-1025 archived 2026-08-05 -->

## Linear archive (AST-1025)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1025/admin-session-cover-letter-page-session-retention-session-cover-letter  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1023 — Session Cover Letter  
**Blocked by / blocks / related:** parent: AST-1023

### Description

## What this implements

New Admin nav page (second item under Session Resume): field inputs for the cover-letter blocks, browser session retention, call sibling HTML API, open rendered HTML in a new tab (Session Resume Paste UX twin). Does **not** own core emit/CSS golden parity.

## Citations

`pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`

## Acceptance criteria

1. From the new **Admin** Session Cover Letter screen, Susan can enter cover-letter field values and open a new tab showing styled cover-letter HTML.
2. Susan can Print → PDF from that tab; no server-generated PDF file is required.
3. Closing and reopening the tool within the same browser session restores the last entered field values (and last successful render inputs if retained); clearing site data wipes them.
4. Completing the flow does not create or update candidate or job cover-letter artifacts or any other durable store for this session.
5. Failed validation/render surfaces a clear error on the Admin screen and does not open a blank/broken HTML tab as success.

## Boundaries

Does **not** own core session cover emit or golden CSS. Does **not** upgrade job cover HTML. Does **not** merge into Session Resume Paste page (separate Admin nav item). After AST-1024.

## Notes for planning

Reuse Session Resume Paste UX patterns (localStorage, new-tab open, toast). Nav under Admin near Session Resume Paste.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/ast-1023-session-cover-letter`, child `sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T03:56:50.816Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1025
**Publish ref:** `origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention` @ `f7320b88` (product tip reviewed `f3061950`; this SHA is docs-only)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention`
**Layers:** core, ui, utils, docs (+ Betty tests/bible; three-dot includes landed AST-1024)
**Notes:** Joan plan-rubric APPROVED attached. AST-1025 `code()` = page + routes + NAV only. C4 stragglers from three-dot ancestry / Betty tests — substance conforms. No product fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence / agent scoring in AST-1025 |
| astral.agent.do-task-delegation | scoped | conforms | No do_task (C4 straggler via AST-1024 in three-dot) |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched (C4 straggler) |
| astral.batch.batch-id-first | scoped | conforms | Untouched (C4 straggler) |
| astral.batch.batch-id-format | scoped | conforms | Untouched (C4 straggler) |
| astral.batch.claim-process-release | scoped | conforms | Untouched (C4 straggler) |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched (C4 straggler) |
| astral.config.config-source-of-truth | scoped | conforms | Nav from `NAV_CONFIG`; field keys mirrored per Joan Decision |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No repo-root `artifacts/**` / `scripts/spikes/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` (C4 straggler) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One `ast-1025-…` features file (C4 straggler) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty tests/bible only; engineer owns page/nav |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` = frontend+NAV; tests via Betty (C4 straggler) |
| astral.layers.core-vs-external-bright-line | scoped | conforms | AST-1025 no core/external edit (C4 via 1024 ancestry) |
| astral.layers.import-direction | scoped | conforms | React → frontend libs/contexts only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss — no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Nav config-driven; server validates fields |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched (C4 straggler) |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched (C4 straggler) |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `AdminRoute` + existing admin HTML API auth |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer work; API errors surfaced in UI |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss — no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No React debug contract (backend owned by AST-1024) |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses `useLocalStorage` / `api` / Toast / blob-tab |
| astral.standards.in-scope-only | scoped | conforms | No builder/API rewrite; Session Resume Paste untouched |
| astral.standards.logging-via-utils | scoped | conforms | No new backend logging |
| astral.standards.no-cross-contamination | scoped | conforms | No artifact save APIs; optional `candidate_id` only |
| astral.standards.no-hardcoded-sets | scoped | conforms | Nav in config; field mirror Joan Decision (no GET) |
| astral.standards.public-then-helpers | scoped | conforms | Default-export page; helpers inline |
| astral.standards.utils-data-late-import-only | scoped | conforms | NAV one-liner only — no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | Untouched (C4 straggler) |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched (C4 straggler) |
| astral.ui.frontend-file-placement | scoped | conforms | Flat `pages/AdminSessionCoverLetter.tsx` |
| astral.ui.naming-conventions | scoped | conforms | PascalCase page; snake_case route |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1025)` @ `f3061950` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/AST-1023/…` only |
| orch.git.ftr-sub-topology | universal | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr` ancestor of tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops in range |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket `sub/*` publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1023` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Separate Admin nav already parent-decided |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches Stages 1–2; boundaries held |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible on tip |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Assignee remains Katherine |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer SHA avoids banned test paths |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.ui.admin-endpoint` | conforms — consumes AST-1024 Admin HTML API via `api()` |
| `pattern.config.config-block` | conforms — `NAV_CONFIG` item |
| `astral.layers.ui-config-driven-business-logic` | conforms — covered in statutes |
| `astral.config.config-source-of-truth` | conforms — covered in statutes |

## Plan adherence

Self-Assessment `Single-Component` matches: NAV + one React page/route + localStorage. No builder/CSS/API ownership. Field-mirror Decision matches Joan APPROVED. Cross-ticket: blockedBy AST-1024 consumed as call site only; Session Resume Paste not edited.

## Findings

### fix-now
(none)

### discuss
1. **C4 stragglers (14)** — Joan Excluded at plan time; in-scope on full three-dot (AST-1024 ancestry + features/tests): `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.state.core-decides-transitions`, `astral.state.no-daisy-chain-in-run`. All substance **conforms**.

### advisory
(none)

## What’s solid

Open HTML failure never opens a tab; empty HTML error; `last_render` only on success; popup-blocked Toast; optional `candidate_id` from `selectedId`.

## Recommended actions

Katherine: acknowledge C4 stragglers in resolve (no product change) → User Testing.

context_tokens≈68000

#### betty — 2026-07-29T03:54:01.382Z
## QA test manifest

**Publish:** `origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention` @ `f3061950`
**merge-tests:** `merge-tests(AST-1025): origin/tests ab6e07a833077be1c8405e7696959a63e4dc7b6f`

### Classification
1. **Existing coverage:** AST-1024 HTML API / builder (sibling — do not re-run as this ticket’s primary gate).
2. **Broken / obsolete:** none.
3. **Gaps (this pass):** §6c Admin page Vitest + NAV_CONFIG order.

### Manifest (test-child — narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1025SessionCoverLetterNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionCoverLetter.test.tsx
```

1. `TestAst1025SessionCoverLetterNav` — Admin nav: Session Cover Letter immediately after Session Resume Paste.
2. `test_AdminSessionCoverLetter.test.tsx` (§6c) — render page + helper; Open HTML disabled until required fields; success posts fields + `candidate_id` null → blob tab + `last_render`; 400 / empty HTML → error, no tab; selected candidate forwards `candidate_id`; localStorage field restore on remount.

**Integration:** `test_candidate_nav_api.py` Jobs gates only — no revision; no new integration coverage.

### Bible shasums (`origin/<publish-ref>`)
- `docs/test-bible/frontend/pages.md` `856f7f6bcee7760c404df3eabc3c196c586be9dbffcfb928138a46803196cc3f`
- `docs/test-bible/utils/config.md` `9e87d09eedd97e05a81f7020cb0e76606c6c4b45f8bb149c6ba75dbe96932b44`

— Betty

#### joan — 2026-07-29T03:47:34.004Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1025
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `f42b582b`. Blocked-by AST-1024 Plan Approved / landed HTML API acknowledged; page consumes call site only.
**Implementer:** Katherine (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Admin screen enter fields + open SomersetCover HTML | Stages 1–2 |
| 2 No job id; form fields; optional selected-candidate signature | Stage 2 (`candidate_id` from `selectedId` or null) |
| 3 Print → PDF; no server PDF | Inherent (HTML blob tab) |
| 4 Browser session retention of fields (+ last successful render inputs) | Stage 2 `useLocalStorage` |
| 5 No durable candidate/job artifact write | Stage 2 hard rules |
| 6 Clear error; no success blank/broken tab | Stage 2 Open HTML failure path |
| 7 Style D backend debug | N/A — boundary: AST-1024 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Admin screen + Open HTML new tab | 1–2 |
| 2 Print → PDF; no server PDF | 2 (HTML only) |
| 3 Session restore of fields / last render inputs | 2 |
| 4 No durable artifact writes | 2 hard rules |
| 5 Failed validation → clear error; no success tab | 2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 NAV_CONFIG + route under AdminRoute | Functional Admin workbench; Boundaries (separate nav item) |
| 2 Page + localStorage + Open HTML API call | Parent/child AC1–6 UI/retention; twin of Session Resume Paste |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1025):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No skip of ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1023` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Separate Admin nav item already parent-decided |
| orch.pipeline.plan-is-bible | conforms | Stages binding; core emit excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Artifacts |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Katherine on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Nav from NAV_CONFIG; server field spine remains BUILD_CONFIG; page mirrors keys for UX only (Decision) |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/features |
| astral.layers.import-direction | conforms | React → frontend libs only; no ui→data |
| astral.layers.ui-config-driven-business-logic | conforms | Nav config-driven; validation remains on server |
| astral.patterns.require-auth-on-protected-endpoints | conforms | AdminRoute + existing admin HTML API auth |
| astral.standards.data-raises-caller-logs | conforms | No new data-layer work |
| astral.standards.debug-contract-gated | conforms | No React debug contract |
| astral.standards.dry-and-focused-functions | conforms | Reuses useLocalStorage / api / Toast / blob-tab pattern |
| astral.standards.in-scope-only | conforms | Excludes builder, job cover, Session Resume Paste edits |
| astral.standards.logging-via-utils | conforms | No new backend logging |
| astral.standards.no-cross-contamination | conforms | No artifact save APIs |
| astral.standards.no-hardcoded-sets | conforms | Nav in config; field mirror documented Decision (no new GET) |
| astral.standards.public-then-helpers | conforms | N/A-ish for React page; helpers inline |
| astral.standards.utils-data-late-import-only | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.ui.frontend-file-placement | conforms | Flat `pages/AdminSessionCoverLetter.tsx` |
| astral.ui.naming-conventions | conforms | PascalCase page; snake_case route |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.batch.batch-id-first — layers/paths miss
- astral.batch.batch-id-format — layers/paths miss
- astral.batch.claim-process-release — layers/paths miss
- astral.batch.entity-agent-responses-latest-only — layers/paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.state.core-decides-transitions — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Page-local `SESSION_COVER_FIELDS` mirror of BUILD_CONFIG keys — explicit Decision; server remains validation SoT; matches Session Resume Paste client-shape pattern; no new GET config endpoint this ticket.
2. `session_cover_letter:last_render` is a success snapshot; Open HTML uses live form fields (correct for fields-only tool). Field `localStorage` alone restores entered values for AC3; last_render is optional retained metadata (unlike resume `last_parse`, which is the Open HTML payload).
3. Self-assessment Single-Component / high / Medium — honest.
4. Failure path never opens a tab; empty HTML treated as error — meets AC5.
5. Separate Admin nav item — matches parent Boundaries.

— Joan
context_tokens≈48000

#### katherine — 2026-07-29T03:44:55.140Z
Plan published.

**Doc:** [docs/features/artifacts/ast-1025-admin-session-cover-letter-page-session-retention.md](https://github.com/susansomerset/astral/blob/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention/docs/features/artifacts/ast-1025-admin-session-cover-letter-page-session-retention.md) on `origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention` @ `f42b582b`.

**Self-assessment**
- **Scope — Single-Component:** Admin `NAV_CONFIG` + one React route/page with `localStorage`; no core/data changes.
- **Conf — high:** Twin of AST-987 Session Resume Paste against landed AST-1024 `POST /api/admin/session_cover_letter/html`.
- **Risk — Medium:** Admin nav/routing surface; Open HTML must not open empty tabs on failure; Session Resume Paste stays untouched.

---

# Admin Session Cover Letter page + session retention (Session Cover Letter)

**Linear:** [AST-1025](https://linear.app/astralcareermatch/issue/AST-1025/admin-session-cover-letter-page-session-retention-session-cover-letter)
**Parent:** [AST-1023](https://linear.app/astralcareermatch/issue/AST-1023/session-cover-letter) — Session Cover Letter
**Publish ref:** `origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention`
**Blocked by (landed):** [AST-1024](https://linear.app/astralcareermatch/issue/AST-1024/session-cover-letter-html-builder-admin-html-api-session-cover-letter) — consume `POST /api/admin/session_cover_letter/html` only; do not re-implement emit/CSS

New Admin nav page (sibling of Session Resume Paste): cover-letter field inputs, browser `localStorage` retention, call the AST-1024 HTML API, open rendered HTML in a new tab. Does **not** own core session cover emit or golden CSS parity.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Admin `NAV_CONFIG` item for Session Cover Letter (after Session Resume Paste) | utils |
| `src/ui/frontend/src/routes.tsx` | Register `/admin/session_cover_letter` under `AdminRoute` | ui |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | New page: field inputs, Open HTML, Toast, `useLocalStorage` retention, optional `candidate_id` | ui |

**Out of scope (do not touch):** `src/core/builder.py` / SomersetCover CSS / `build_session_cover_letter`, `POST /api/admin/session_cover_letter/html` body validation beyond calling it, job cover HTML routes, Session Resume Paste page/routes, Base Resume Content / JAR / Materials Preview, `TASK_CONFIG` / Manage Tasks / dispatch, candidate or job artifact writers, `tests/`, bible, repo-root `artifacts/`, `App.css` unless a class is truly missing (prefer existing `dep-btn` / `dep-input` tokens).

## Dependency contract (AST-1024 — call site only)

**`POST /api/admin/session_cover_letter/html`** (already on `origin/ftr/ast-1023-session-cover-letter` after merge):

- Auth: `@require_admin` (via `api()` Bearer, same as Session Resume Paste).
- Request JSON field keys from `BUILD_CONFIG["session_cover_letter"]["fields"]`:
  - Required: `from_block`, `letter_date`, `letter`, `signoff_closing`, `signature`
  - Optional: `to_block`, `subject`
  - Optional: `candidate_id` — omit / `null` / `""` → name-only sign-off; non-empty string → optional profile signature-image read on server
- Success **200**: raw HTML body, `Content-Type: text/html; charset=utf-8`
- Failure **400**: `{ "success": false, "error": "<clear message>" }` — treat any non-ok as failure; **never** open the HTML tab

## Stage 1: Admin nav + route registration

**Done when:** Admin sidebar shows **Session Cover Letter** immediately after **Session Resume Paste**; navigating to `/admin/session_cover_letter` renders inside `AdminRoute` (page stub OK until Stage 2 fills UI).

1. In `src/utils/config.py` `NAV_CONFIG` Admin `items` list, immediately after the Session Resume Paste entry, add:
   ```python
   {"label": "Session Cover Letter", "path": "/admin/session_cover_letter"},
   ```
2. In `src/ui/frontend/src/routes.tsx`:
   - Import `SessionCoverLetter` from `./pages/AdminSessionCoverLetter`.
   - Add child route next to `admin/session_resume_paste`:
     ```tsx
     { path: "admin/session_cover_letter", element: <AdminRoute><SessionCoverLetter /></AdminRoute> },
     ```
3. Create `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` as a default-export page component named `SessionCoverLetter` (file name matches Admin section prefix; export default function `SessionCoverLetter`). Stage 1 may ship a minimal shell (title + helper line only) if Stage 2 is the same commit wave — prefer implementing Stage 2 in the same build pass so the route is not empty in production.

⚠️ **Decision:** Separate Admin nav item (not nested inside Session Resume Paste), matching parent UI inventory and ticket Boundaries.

## Stage 2: Session Cover Letter page + localStorage + Open HTML

**Done when:** From Admin → Session Cover Letter, Susan can enter field values, Open HTML opens a new tab with styled cover HTML on success; failed validation/render shows a clear error and does **not** open a blank/broken tab; leave/return within the same browser session restores field values and last successful render inputs via `localStorage`; clearing site data wipes them; no candidate/job artifact writes occur from this page.

1. **Field spine (page-local mirror of config):** At the top of `AdminSessionCoverLetter.tsx`, define:
   ```ts
   /** Must match BUILD_CONFIG["session_cover_letter"]["fields"] keys/required (AST-1024). */
   const SESSION_COVER_FIELDS = [
     { key: "from_block", label: "From block", required: true, rows: 3 },
     { key: "letter_date", label: "Date", required: true, rows: 1 },
     { key: "to_block", label: "To block", required: false, rows: 2 },
     { key: "subject", label: "Subject", required: false, rows: 1 },
     { key: "letter", label: "Letter body", required: true, rows: 12 },
     { key: "signoff_closing", label: "Sign-off closing", required: true, rows: 1 },
     { key: "signature", label: "Signature name", required: true, rows: 1 },
   ] as const
   type SessionCoverFieldKey = (typeof SESSION_COVER_FIELDS)[number]["key"]
   type SessionCoverFields = Record<SessionCoverFieldKey, string>
   ```
   Empty default: every key → `""`.

   ⚠️ **Decision:** Mirror keys/required in the page (Session Resume Paste also keeps client payload shape local). Server remains validation source of truth; React uses this list for labels, required UX, and JSON assembly. Do **not** add a new GET config endpoint in this ticket.

2. **localStorage retention** (reuse `useLocalStorage` from `src/ui/frontend/src/lib/useLocalStorage.ts`):
   - Key `session_cover_letter:fields` — type `SessionCoverFields`, default all `""`. Bind every input; writes through on change.
   - Key `session_cover_letter:last_render` — type:
     ```ts
     type SessionCoverLastRender = {
       fields: SessionCoverFields
       candidate_id: string | null
     } | null
     ```
     default `null`. Set **only** after a successful Open HTML (200 + non-empty HTML). Do **not** clear on failed Open HTML (keep prior success). Clearing site data wipes both keys (browser behavior — no extra code).

3. **Selected candidate (optional signature only):**
   - `const { selectedId } = useCandidate()` from `../contexts/CandidateContext`.
   - Helper line must state: letter fields come from this form; if a candidate is selected and has a profile signature image, the server may include it in the sign-off; otherwise name-only. Render still works with no candidate selected. This tool does not save to the database.
   - On Open HTML, set `candidate_id` to `selectedId` when it is a non-empty string; otherwise send `null` (or omit — API accepts both).

4. **UI layout** (clone Session Resume Paste patterns — `dep-btn`, `dep-input`, CSS variables; do **not** edit `App.css` unless a class is missing):
   - Page title: `Session Cover Letter`.
   - Short helper paragraph (see step 3).
   - For each entry in `SESSION_COVER_FIELDS` in order: label (append ` (optional)` when `!required`), then:
     - `rows === 1`: `<input className="dep-input" type="text" … />` (full width)
     - `rows > 1`: `<textarea className="dep-input" rows={rows} … />` (full width, `spellCheck={false}` for letter body; monospace optional for letter only)
   - Buttons row:
     - **Open HTML** — disabled when any `required` field has `trim() === ""`, or when `opening` is true.
   - Inline error `<p>` for the latest failure; clear when Open HTML starts.
   - `<Toast message={toast} onDone={clearToast} />` for success/error feedback.

5. **Open HTML handler** (`POST /api/admin/session_cover_letter/html`):
   - Guard: if required fields incomplete or `opening`, return.
   - `setOpening(true)`; clear inline error.
   - Build body:
     ```ts
     const body = {
       ...fields,
       candidate_id: selectedId && selectedId.trim() ? selectedId.trim() : null,
     }
     ```
   - `api("/api/admin/session_cover_letter/html", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })`.
   - If `!r.ok`: parse JSON error when possible (`data.error`); set inline error + Toast `error`; **do not** open a tab; **do not** update `last_render`.
   - If ok: `const html = await r.text()`; if empty/whitespace-only → error Toast, no tab, no `last_render` update.
   - On success HTML:
     ```ts
     setLastRender({ fields: { ...fields }, candidate_id: body.candidate_id })
     const blobUrl = URL.createObjectURL(new Blob([html], { type: "text/html;charset=utf-8" }))
     const win = window.open(blobUrl, "_blank", "noopener,noreferrer")
     if (!win) {
       setToast({ text: "Popup blocked — allow popups to open the HTML tab.", variant: "error" })
     }
     window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
     ```
     Toast success optional (e.g. `Opened cover letter HTML.`) — keep quiet if popup succeeded; always Toast on popup blocked / errors.
   - `finally`: `setOpening(false)`.

6. **Hard rules for this page:**
   - Do **not** call any candidate/job save API, parse API, or artifact endpoints.
   - Do **not** auto-open a tab on mount or on field change — only the Open HTML control.
   - Do **not** merge this UI into `AdminSessionResumePaste.tsx`.
   - Do **not** change `POST /api/admin/session_cover_letter/html` or builder emit.

7. **Verify by hand (builder):**
   - `cd src/ui/frontend && npx tsc --noEmit` (or the repo’s usual frontend typecheck) on touched TS files.
   - Confirm nav label + route load; Open HTML with required fields filled returns a tab; blank required field keeps button disabled; force a 400 (e.g. empty `from_block` via temporary bypass only if needed — prefer relying on disabled button + server message) and confirm no tab opens.

## Self-Assessment

**Scope:** `Single-Component` — Admin nav config + one React route/page with localStorage; no core/data changes.

**Conf:** `high` — direct twin of AST-987 Session Resume Paste UX against a landed AST-1024 HTML contract already merged on `ftr`.

**Risk:** `Medium` — Admin nav/routing surface; a bad Open HTML handler could open empty tabs or confuse users, but Session Resume Paste stays untouched and failures must stay on-page.

## Code-rules self-review

- **§1.3 DRY:** Reuse `useLocalStorage`, `api()`, `Toast`, `dep-*` classes, and the blob-URL new-tab pattern from `AdminSessionResumePaste.tsx`; do not fork a second storage helper.
- **§2.1 / config-source-of-truth:** Nav path/label from `NAV_CONFIG`; field key/required spine remains `BUILD_CONFIG["session_cover_letter"]` on the server — page mirrors keys for UX only (Decision in Stage 2).
- **§2.4 batch / §2.6 state machine:** N/A — no batch or state-machine work.
- **§3.3 imports:** React page imports only frontend libs/contexts/components; no new Python ui→data paths.
- **§3.5 naming:** `AdminSessionCoverLetter.tsx`, route `/admin/session_cover_letter`, snake_case API path already provided by AST-1024.
- **§1.5.1 debug:** No React debug contract; do not add frontend debug logging.
- **in-scope-only / no-cross-contamination:** No artifact persistence; optional `candidate_id` is read-only for signature on the server.

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1023/AST-1025-admin-session-cover-letter-page-session-retention`
**Tip:** `ac23db55`

**Stages delivered:**
- Stage 1 — `NAV_CONFIG` Session Cover Letter + `/admin/session_cover_letter` under `AdminRoute`
- Stage 2 — `AdminSessionCoverLetter.tsx` field form, `useLocalStorage` retention, Open HTML → AST-1024 API + blob tab

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1025
**Publish ref tip (pre-docs):** `f3061950`
**Overall:** DISCUSS

### What’s solid
- Stages 1–2 match plan: `NAV_CONFIG` + `/admin/session_cover_letter` under `AdminRoute`, page twin of Session Resume Paste.
- Open HTML failure path never opens a tab; empty HTML treated as error; `last_render` only on success.
- Field/key mirror Decision matches Joan-approved plan; server remains validation SoT.
- Engineer `code()` touched only planned files (no builder/API rewrite).

### Issues
**discuss (C4 stragglers — Joan Excluded; in-scope on `origin/dev...publish-ref` which includes AST-1024 + Betty tests):** 14 statutes (agent/batch/core-bright-line/patterns/state + spikes/features/engineer-test-tree). All substance **conforms** (untouched or process-clean).

**fix-now:** none

### Recommended actions
- Katherine: acknowledge C4 stragglers in resolve (no product change) → User Testing.

## Resolution

**2026-07-29** — Radia `[code-rubric] revision=1` Overall DISCUSS; tip intake `f7320b88` (docs-only) after product/tests `f3061950`.

- **fix-now:** none — no product changes.
- **discuss (C4 stragglers):** acknowledged — Joan Excluded statutes became in-scope via three-dot ancestry (AST-1024 + features/test-tree); substance already **conforms**. No product or plan-stage change.
- **advisory:** none.
