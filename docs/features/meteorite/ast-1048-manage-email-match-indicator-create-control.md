<!-- linear-archive: AST-1048 archived 2026-08-05 -->

## Linear archive (AST-1048)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1048/manage-email-match-indicator-create-control-bind-email-to-candidate  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1044 — Bind email to candidate  
**Blocked by / blocks / related:** parent: AST-1044; blocks: AST-1049

### Description

## What this implements

Owns rename **Read email** → **Manage Email** and the admin surface changes: show match bind on listed/selected messages, enable **Create** only when matched, keep unmatched browse working. Does **not** own the reusable lookup (AST-1047) or strip/extract + meteorite create wire (sibling / AST-1034). After AST-1047.

## Citations

`pattern.ui.admin-endpoint`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.layers.import-direction`.

## Acceptance criteria

- [X] 2. On Manage Email, a message whose **From** uniquely matches via that lookup shows a clear visual bind to that candidate.
- [X] 3. On Manage Email, a matched message exposes an active **Create** control; an unmatched or ambiguous message does not.
- [X] 4. Admin nav/screen is labeled **Manage Email** (replacing **Read email**).
- [X] 5. Unauthenticated callers cannot run match or Create endpoints/screens.
- [X] 6. Existing inbox browse (list + HTML body view) still works for unmatched messages after this epic.

## Boundaries

- [X] Does **not** own the reusable lookup (AST-1047) or strip/extract + meteorite create wire (sibling / AST-1034).

## Notes for planning

After AST-1047. Admin page rename and match indicator + Create enablement only.

## Git branch (authoritative)

Parent `ftr/AST-1044-bind-email-to-candidate`; child `sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T19:40:51.669Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1048
**Publish ref:** `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control` @ `f13d5267` (product tip `5f69a906` + docs review)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control` — AST-1048 chrome (`AdminManageEmail.tsx`, `routes.tsx`, `App.css`, `NAV_CONFIG`) plus rolled-up AST-1047 core/utils/tests on this tip.
**Notes:** Joan plan-rubric APPROVED. C4 stragglers from plan-time UI-only exclusion vs three-dot tip that includes AST-1047 — substance **conforms**; no fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence / grade work in 1048 chrome; 1047 lookup untouched here |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | No batch claim |
| astral.batch.batch-id-format | scoped | conforms | No batch ids |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Nav label/path only in `NAV_CONFIG`; no React match field lists |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (`artifacts/**` / `scripts/spikes/**`) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plans under `docs/features/` — not spikes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file for AST-1048 (1047 plan is sibling tip rollup) |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns src/features; Betty owns tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | `test()`/`merge-tests()` Betty; Hedy did not edit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | 1048 UI only; Gmail stays external (1047 rollup) |
| astral.layers.import-direction | scoped | conforms | Page → `api()` only; no data/external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss (`scripts`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Create enablement = server `candidate_match.matched` |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | Keeps `AdminRoute`; inbox APIs stay `@require_admin` |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | layers miss (`data`) |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug in React; 1047 Style D already gated |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses list `candidate_match`; no second client lookup |
| astral.standards.in-scope-only | scoped | conforms | No strip/extract/meteorite POST; no lookup reimplementation |
| astral.standards.logging-via-utils | scoped | conforms | Untouched in 1048 chrome |
| astral.standards.no-cross-contamination | scoped | conforms | Layered UI only |
| astral.standards.no-hardcoded-sets | scoped | conforms | No inline email/name field lists in React |
| astral.standards.public-then-helpers | scoped | conforms | Page component; local matchCell/onCreateClick |
| astral.standards.utils-data-late-import-only | scoped | conforms | NAV_CONFIG only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | No state machine |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | conforms | Flat `pages/AdminManageEmail.tsx`; styles in `App.css` |
| astral.ui.naming-conventions | scoped | conforms | PascalCase page; snake_case `/admin/manage_email` |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1048)` @ `5f69a906` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` / `resolve(AST-1047)` on tip |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1044/AST-1048-manage-email-match-indicator-create-control` |
| orch.git.merge-on-checkout | universal | conforms | Tip stacks on `origin/ftr/AST-1044-bind-email-to-candidate` |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1044` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Path rename + disabled Create decided in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match `code(AST-1048)` |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.ui.admin-endpoint` | conforms — admin page + existing inbox APIs |
| `astral.patterns.require-auth-on-protected-endpoints` | conforms — `AdminRoute` |
| `astral.layers.ui-config-driven-business-logic` | conforms — enablement from server payload |
| `astral.layers.import-direction` | conforms — ui→api client only |

## Plan adherence

`code(AST-1048)` matches Stages 1–3 and Self-Assessment Single-Component / high / Medium. Consumes AST-1047 `candidate_match` only; Create click stub for AST-1049; unmatched list+HTML browse preserved; no `/admin/read_email` alias (intentional).

## Findings

### fix-now
(none)

### discuss
1. **straggler cluster** — Joan excluded agent/batch/core-vs-external/state/spike/features/test-tree statutes for a UI-only Files Changed table; three-dot tip includes rolled-up AST-1047 so those ids are in-scope. Substance: **conforms** (no Hedy product change expected for stragglers alone).

### advisory
(none)

### What’s solid
- Manage Email rename + match column/modal bind + disabled Create when unmatched.
- No client-side lookup; no meteorite create wire.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

context_tokens≈52000

#### betty — 2026-07-29T19:37:55.152Z
## QA test manifest — AST-1048

**Publish:** `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control` @ `5f69a906`
**Delivery:** `merge-tests(AST-1048): origin/tests 7a16dbbcd3ca4ce2dc24110a8fd46d4f3c416ffd`

### Existing coverage (revised)
1. `tests/component/utils/test_config.py::TestAst1033ReadEmailNav` — now asserts **Manage Email** / `/admin/manage_email` (no `/admin/read_email`)
2. `tests/component/frontend/pages/test_AdminManageEmail.test.tsx` — replaces `test_AdminReadEmail.test.tsx` (§6c page; keeps AST-1040 raw-source cases)

### Gaps (new AST-1048 cases in page suite)
3. Candidate column: matched bind vs `—`
4. Matched modal: bind line + **Create** enabled
5. Unmatched modal: no `.manage-email-match--modal`; **Create** disabled; HTML browse still works

### Broken / obsolete (revised this pass)
- `test_AdminReadEmail.test.tsx` + heading/import `AdminReadEmail` / "Read email"
- `TestAst1033ReadEmailNav.test_read_email_follows_session_cover_letter` path/label

### Integration
- No existing Admin Manage Email scenarios — none revised; did not invent new integration coverage.

### Narrowed run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1033ReadEmailNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

### Bible shasums (publish tip)
- `docs/test-bible/frontend/pages.md` `c6c3820ee5643320f09f10c8cbecf2d586db6a40b133aca011724fc9b3355cca`
- `docs/test-bible/utils/config.md` `05d2c70aaf9f5f8151fb2527f6569299c2bb504bdd90f023131ae83dc41b2706`

— Betty

#### joan — 2026-07-29T19:31:55.122Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1048
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `941f6315`. Publish ref `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`. Blocked-by AST-1047 acknowledged; consumes list `candidate_match` only; Create click stub correctly deferred to AST-1049.
**Implementer:** Hedy (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Reusable lookup | N/A — boundary: AST-1047 |
| 2 Visual From bind on Manage Email | Stage 2 |
| 3 Create active only when matched | Stage 3 (enablement; click wire N/A — AST-1049) |
| 4 Create strip/extract + meteorite job | N/A — boundary: AST-1049 |
| 5 Nav/screen labeled Manage Email | Stage 1 |
| 6 Unauthenticated cannot match/Create | Stage 1 keeps `AdminRoute`; inbox APIs stay `@require_admin` (unchanged) |
| 7 Style D debug on match/create backends | N/A — UI ticket; no React debug requirement |
| 8 Unmatched browse still works | Stages 2–3 (additive chrome; list+HTML unchanged for unmatched) |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 2 Clear visual bind from lookup match | 2 |
| 3 Active Create when matched; not when unmatched/ambiguous | 3 |
| 4 Admin nav/screen labeled Manage Email | 1 |
| 5 Unauthenticated cannot reach match/Create screens | 1 (`AdminRoute`) |
| 6 Unmatched list + HTML browse still works | 2–3 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Nav + route rename | Parent AC5 / child AC4; Purpose Manage Email surface |
| 2 Match indicator from `candidate_match` | Parent/child AC2; ui-config-driven (server payload) |
| 3 Create enablement stub | Parent/child AC3; Boundaries (no meteorite wire) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1048):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Depends on ftr tip with AST-1047 |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1044` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Path rename + disabled-vs-hidden Create decided in plan |
| orch.pipeline.plan-is-bible | conforms | Binding stages; siblings excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Hedy on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched (considered via matching; no agent work) |
| astral.config.config-source-of-truth | conforms | Nav label/path in `NAV_CONFIG` only |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/features |
| astral.layers.import-direction | conforms | UI → api client only; no Gmail/data |
| astral.layers.ui-config-driven-business-logic | conforms | Enablement = server `candidate_match.matched`; no React match rules |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Keeps `AdminRoute`; no public route |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work |
| astral.standards.debug-contract-gated | conforms | No new ungated debug |
| astral.standards.dry-and-focused-functions | conforms | Reuses list payload; no second lookup |
| astral.standards.in-scope-only | conforms | Excludes lookup, strip/extract, meteorite POST |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered UI only |
| astral.standards.no-hardcoded-sets | conforms | No inline match field lists in React |
| astral.standards.public-then-helpers | conforms | Page component rename only |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.ui.frontend-file-placement | conforms | Flat `pages/` rename; styles in `App.css` |
| astral.ui.naming-conventions | conforms | PascalCase page; snake_case route `/admin/manage_email` |
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
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
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
1. Create click is a silent no-op stub — correct child split; AST-1049 owns strip/extract + meteorite POST.
2. Disabled (visible) Create on unmatched vs hidden — matches parent “active when matched / not when unmatched” without orphan-job affordance.
3. Bind text `Matched: {astral_candidate_id}` is enough identity — ids are lowercase last-name slugs (e.g. `somerset`), not opaque UUIDs.
4. No `/admin/read_email` redirect — intentional for seed surface; Risk Medium notes bookmark break.
5. Self-assessment Single-Component / high / Medium — honest.

— Joan
context_tokens≈48000

#### hedy — 2026-07-29T19:28:57.920Z
Plan: [`docs/features/meteorite/ast-1048-manage-email-match-indicator-create-control.md`](https://github.com/susansomerset/astral/blob/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control/docs/features/meteorite/ast-1048-manage-email-match-indicator-create-control.md) on `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control` @ `941f6315`.

**Scope:** Single-Component — Admin Manage Email React + NAV_CONFIG/route rename + light CSS; consumes AST-1047 `candidate_match`; Create click stub left for AST-1049.

**Conf:** high — list enrichment already on ftr; existing Read email page/AdminRoute are the surfaces to rename/extend.

**Risk:** Medium — path rename breaks `/admin/read_email`; wrong enablement would expose Create on unmatched senders once AST-1049 wires the click.

---

# AST-1048 — Manage Email match indicator + Create control

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1048/manage-email-match-indicator-create-control-bind-email-to-candidate  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate  

**Publish ref (origin):** `sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`  
**Parent integration ref:** `ftr/AST-1044-bind-email-to-candidate`

Rename the admin **Read email** surface to **Manage Email**, render the AST-1047 `candidate_match` bind on list + selected message, and expose an **active Create** control only when `candidate_match.matched` is true — while unmatched messages stay fully browsable. Does **not** implement reusable lookup (AST-1047, already on `ftr`) or strip/extract + meteorite create (AST-1049).

Boundaries (do **not** implement): `get_candidate_id_for_query` / `CANDIDATE_LOOKUP_CONFIG` / inbox From enrichment (AST-1047); strip/extract, subject-in-content, `POST` meteorite create orchestration (AST-1049); multi-candidate picker; Gmail client changes; mailbox mutation; Profile/Admin contact editors.

**Depends on:** AST-1047 rolled on `origin/ftr/AST-1044-bind-email-to-candidate` (merge that tip before build — list payloads already include `candidate_match`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename Admin nav item label `Read email` → `Manage Email`; change path `/admin/read_email` → `/admin/manage_email` | utils |
| `src/ui/frontend/src/pages/AdminReadEmail.tsx` | Rename file → `AdminManageEmail.tsx`; heading, match column/indicator, Create enablement from `candidate_match` | ui |
| `src/ui/frontend/src/routes.tsx` | Import `AdminManageEmail`; route path `admin/manage_email` under `AdminRoute` | ui |
| `src/ui/frontend/src/App.css` | Minimal styles for match indicator + Create control on the Manage Email page (no new CSS framework) | ui |

No new API blueprints, no `src/core/**` changes, no `src/external/**` changes.

---

## Stage 1: Nav + route rename (Manage Email)

**Done when:** Admin sidebar shows **Manage Email** linking to `/admin/manage_email`; that route renders the (still-old-chrome) page under `AdminRoute`; `/admin/read_email` is no longer registered. No match/Create UI yet.

1. In `src/utils/config.py`, locate the Admin `NAV_CONFIG` item currently `{"label": "Read email", "path": "/admin/read_email"}` (after Session Cover Letter). Change it to:

```python
{"label": "Manage Email", "path": "/admin/manage_email"},
```

Keep relative order among Admin items unchanged (still immediately after Session Cover Letter).

2. Rename `src/ui/frontend/src/pages/AdminReadEmail.tsx` → `src/ui/frontend/src/pages/AdminManageEmail.tsx` (git `mv`). Rename the default export function `AdminReadEmail` → `AdminManageEmail`. Change the page `<h1>` text from `Read email` to `Manage Email`.

3. In `src/ui/frontend/src/routes.tsx`:
   - Update the import to `AdminManageEmail` from `./pages/AdminManageEmail`.
   - Change the route from `path: "admin/read_email"` to `path: "admin/manage_email"` with the same `<AdminRoute>` wrapper.
   - Do **not** leave a redirect/alias for `admin/read_email`.

⚠️ **Decision — path rename:** AC requires the screen/nav **label** Manage Email. Changing the path to `/admin/manage_email` keeps nav path and label aligned and avoids a permanent “Read email” URL. Deep links to `/admin/read_email` intentionally break (seed surface only; no public bookmarks required).

⚠️ **Decision — no backend rename:** Inbox APIs stay under `/api/admin/inbox/**` with `@require_admin` (AST-1033 / AST-1047). This ticket does not rename API prefixes.

---

## Stage 2: Match indicator from `candidate_match` (list + modal)

**Done when:** List rows that ship `candidate_match.matched === true` show a clear visual bind to `candidate_match.astral_candidate_id`; unmatched/ambiguous (`matched === false` or missing object) show a neutral empty/“—” cell; opening a row still loads HTML body as today; no Create button yet.

1. In `AdminManageEmail.tsx`, extend the `InboxMessage` type:

```ts
type CandidateMatch = {
  matched: boolean
  astral_candidate_id: string | null
}

type InboxMessage = {
  id: string
  thread_id: string
  subject: string
  from_address: string
  date: string
  unread: boolean
  candidate_match?: CandidateMatch
}
```

Treat missing `candidate_match` as unmatched (defensive — AST-1047 always attaches the object on list).

2. Add a table column **Candidate** (header after **From**, before **Date** is fine; keep one consistent order):

| Condition | Cell content |
|-----------|--------------|
| `row.candidate_match?.matched === true` and non-empty `astral_candidate_id` | Visible bind text: `Matched: {astral_candidate_id}` plus CSS class `manage-email-match` on the cell (or inner span) |
| otherwise | `—` (em dash), no match class |

3. In the message modal (after open), show the same bind under the modal title area (or as a one-line subtitle above the HTML body): when matched, render `Matched: {id}`; when not, omit the line (do not show “unmatched” noise — browse stays calm).

4. Do **not** re-call lookup from the browser. Do **not** invent match rules in React. Use only the server `candidate_match` payload from `GET /api/admin/inbox/messages`.

5. In `App.css`, add minimal rules for `.manage-email-match` (e.g. slightly emphasized text color using existing CSS variables such as `--text-primary` / accent already used on admin pages — no new purple/glow theme). Keep rules short; no layout rewrite of the table.

⚠️ **Decision — list is source of truth for bind:** AST-1047 enriches **list** only; get-message returns HTML. Selected-row match comes from the list row already in React state (`messages.find`). Do not change `get_message_html` / get API in this ticket.

---

## Stage 3: Create control enablement (no meteorite wire)

**Done when:** Matched selected message shows an enabled **Create** button; unmatched/ambiguous selected message shows **Create** disabled (or hidden — see Decision); unmatched browse (list + HTML modal) still works; clicking Create does **not** call meteorite create or strip/extract (AST-1049 owns that).

1. In the modal footer/actions area of `AdminManageEmail.tsx`, add:

```tsx
<button
  type="button"
  className="manage-email-create"
  disabled={!selected?.candidate_match?.matched}
  onClick={onCreateClick}
>
  Create
</button>
```

where `selected` is the current list row for `selectedId`.

2. Implement `onCreateClick` as a **no-op stub** for this ticket:

```ts
function onCreateClick() {
  // AST-1049 owns strip/extract + meteorite create wire from this control.
}
```

Do **not** `POST` `/api/candidates/.../meteorite/jobs`. Do **not** invent a new create inbox endpoint. Do **not** toast “not implemented” as product UX unless you need a temporary guard — prefer silent no-op so AST-1049 replaces the body without fighting a fake error path.

3. Enablement rule (literal):

- `disabled === false` only when `selected.candidate_match?.matched === true`.
- Otherwise `disabled === true` (button still visible so Susan sees the control exists but inactive).

4. Optional list-row Create is **out of scope** — Create lives on the open-message modal only (operator already inspecting the body).

5. Confirm `AdminRoute` remains on the route (Stage 1) so unauthenticated users cannot reach the screen; do not add a public route.

⚠️ **Decision — disabled vs hidden:** Parent AC3: matched exposes an **active** Create; unmatched does **not**. Showing a disabled Create on unmatched rows teaches the control without implying orphan jobs are creatable. Do not hide the button entirely on unmatched.

⚠️ **Decision — Create click owned by AST-1049:** This ticket’s AC stops at enablement chrome. Wiring Create to strip/extract + AST-1034 meteorite create is **AST-1049** only. Leaving a labeled stub `onCreateClick` avoids dual ownership of the same handler.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the Files Changed table.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`, then proceeds.

Blocking comment format (parent AST-1044):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — Admin Manage Email React page + `NAV_CONFIG` / route rename + light CSS; consumes AST-1047 `candidate_match` only; no core/API create path.

**Conf:** high — AST-1047 already ships list enrichment; existing `AdminReadEmail` + `AdminRoute` + nav config are the exact surfaces to rename/extend; Create stub boundary with AST-1049 is explicit.

**Risk:** Medium — nav/path rename breaks old `/admin/read_email` bookmarks and revises AST-1033 nav/path tests; wrong enablement would show Create on unmatched senders (orphan-job UX risk once AST-1049 wires click).

---

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | Reuse list `candidate_match`; no second lookup client-side |
| §2.1 / no-hardcoded-sets | Match eligibility from server payload; no inline email/name field lists in React |
| §3.3 import direction | UI → `api()` only; no Gmail/data imports in the page |
| `require-auth` / AdminRoute | Keep `AdminRoute`; inbox APIs stay `@require_admin` (unchanged) |
| ui-config-driven business logic | Create enablement = `candidate_match.matched` from API, not React heuristics |
| In-scope only | No strip/extract, no meteorite POST, no lookup config edits |

---

## Review (build stub)

**Publish ref:** `sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`
**Build tip:** `88df7b07ba5dce779485a6fd4fb93d681dcb1b5e`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1048
**Publish ref tip (pre-docs):** `5f69a906`
**Overall:** DISCUSS

### What’s solid
- Nav/route rename to Manage Email / `/admin/manage_email` under `AdminRoute`; no React lookup — consumes AST-1047 `candidate_match`.
- List Candidate column + modal bind; Create enabled only when `matched`; click stub deferred to AST-1049; unmatched browse preserved.
- PascalCase page + snake_case route; styles in `App.css`; no meteorite POST / strip-extract.

### Issues
- **discuss (straggler):** Joan excluded several statutes at plan time (UI-only Files Changed); three-dot tip also carries rolled-up AST-1047 `core`/`utils`/tests so those ids score in-scope (all **conforms** on substance). No product delta expected from Hedy for the stragglers alone.

### Recommended actions
- Hedy: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

---

## Resolution

**Date:** 2026-07-29  
**Review:** `[code-rubric] revision=1` — Overall **DISCUSS**; **fix-now:** none.

**Actions:**
- Acknowledged discuss straggler cluster (plan-time UI-only exclusions vs three-dot tip rolling AST-1047) — substance already **conforms**; no product change.
- No advisory items.

**Outcome:** `resolve(AST-1048): — clean` → User Testing.
