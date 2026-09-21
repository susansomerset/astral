<!-- linear-archive: AST-1097 archived 2026-08-07 -->

## Linear archive (AST-1097)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1097/restore-archive-active-intake-api-for-start-over-restart-intake-gets-a  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1096 — Restart intake gets a 500 error  
**Blocked by / blocks / related:** parent: AST-1096

### Description

## What this implements

Wire the missing authenticated `POST …/intake/sessions/active/archive` surface to existing core `archive_active_intake_session` with correct success / not-found / auth outcomes so the current Candidate Intake Start Over flow can clear an active session and proceed to fresh preamble. Does **not** own React dialog redesign or preamble/topic-menu work.

## In scope

- [X] `pattern.ui.admin-endpoint` — thin `@require_auth` blueprint route; delegate to core; map exceptions to JSON status codes
- [X] `pattern.layers.import-discipline` / `astral.layers.import-direction` — `api_intake.py` imports `src.core.intake` + `src.core.candidate` only (no UI→data)
- [X] `astral.patterns.require-auth-on-protected-endpoints` — archive mutator gated with `@require_auth`
- [X] `astral.standards.data-raises-caller-logs` — core raises; API maps `LookupError`/`ValueError` to 404 JSON
- [X] `astral.standards.in-scope-only` — restore archive HTTP surface only

## Considered but excluded

* React Start Over / Continue dialog redesign (`CandidateIntake.tsx` / `IntakeChatModal.tsx`) — already POSTs archive; AST-583/AST-1017 own UX
* Preamble, Ruth validation, Topic Menu, Estelle turn/build routes — unchanged
* Core `archive_active_intake_session` / `intakes_old` shape — already correct (AST-582/AST-590); this ticket is the missing UI route
* `orch.*` universal statutes — not per-child

## Acceptance criteria

1. [x] With an active intake for a candidate, Start Over (or equivalent restart) completes without a 500 / “method is not allowed” error.
2. [x] After Start Over succeeds, GET active session reports no active session; a new preamble/intake can start.
3. [x] The prior conversation is retained on the candidate as an archived intake history entry (not silently deleted).
4. [x] Continue still resumes the active session without archiving.
5. [x] Unauthenticated archive calls are rejected.

## Boundaries

Does **not** redesign Start Over / Continue dialog UX; does **not** change preamble, Ruth validation, Topic Menu, or Estelle turn/build. Does **not** alter `intakes_old` shape beyond the existing core archive contract.

## Notes for planning

Citations above. Core `archive_active_intake_session` already exists; UI already POSTs archive on Start Over — restore the missing HTTP route / contract.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1096-restart-intake-gets-a-500-error`, child `sub/AST-1096/AST-1097-restore-archive-active-intake-api`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T04:55:05.822Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api` contains `Merge remote-tracking branch 'origin/dev' into sub/...` (and a self-merge of the sub). validate-sub-log refuses merge into ftr.

@Ada Lovelace — rebuild publish-ref onto `origin/ftr/AST-1096-restart-intake-gets-a-500-error` with only AST-1097 vocabulary commits (plan/code/merge-tests/test/docs/resolve); no `git pull` / `Merge remote-tracking branch` subjects. Push `origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api` then Chuckles retries merge-child.

— Chuckles

#### radia — 2026-07-31T04:53:04.027Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1097
**Publish ref:** `origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api` @ `7e041a371a01b7aa576a2785bdc28343974a9ddb`
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api` — layers `{docs, ui}`; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.agent.do-task-delegation` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.batch.batch-id-first` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.batch.batch-id-format` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.batch.claim-process-release` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.config.config-source-of-truth` | scoped | conforms | no new behavior-driving config; archive stays in core |
| `astral.config.pass-threshold-vs-score-floor` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env introduced |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths match none of diff paths |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | features plan doc only; not a misplaced spike |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single docs/features/…/ast-1097-….md |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test() touched tests/bible only; Ada owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test-tree via Betty test()/merge-tests; engineer code() only |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.layers.import-direction` | scoped | conforms | api_intake imports core.intake + core.candidate only |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | thin JSON map of core outcomes; no UI business rules |
| `astral.patterns.coat-check-never-store-empty` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | @require_auth on archive mutator |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | core raises; API maps LookupError/ValueError→404 JSON |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.standards.debug-contract-gated` | scoped | conforms | no new debug= emission on archive route |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | delegates to archive_active_intake_session; no dup logic |
| `astral.standards.in-scope-only` | scoped | conforms | one route + import; no React/preamble/core edits |
| `astral.standards.logging-via-utils` | scoped | conforms | no print/getLogger; JSON errors only |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays in ui API module |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | no new state enums/sets |
| `astral.standards.public-then-helpers` | scoped | conforms | one public handler beside siblings; no helper scatter |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.state.core-decides-transitions` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | layers ∩ diff ['docs', 'ui'] empty |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | paths match none of diff paths |
| `astral.ui.naming-conventions` | scoped | conforms | snake_case archive_active_session; matches siblings |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no gunicorn/worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests(AST-1097) one SHA from origin/tests |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary on sub tip |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish only to origin/sub/AST-1096/AST-1097-… |
| `orch.git.ftr-sub-topology` | universal | conforms | child sub under parent ftr/AST-1096-… |
| `orch.git.merge-on-checkout` | universal | conforms | origin/dev merges into sub; no illegal recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase/force in tip history |
| `orch.git.no-dev-agent-branches` | universal | conforms | sub/… only; no dev-agent branch |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in astral-AST-1096 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | ValueError→404 + UI-route-only decisions in plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches Stage 1 handler verbatim |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Candidate; single-child restore |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute edits in diff |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test() + bible by Betty; engineer code-only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Ada Lovelace |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada remains assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned paths touched |

## Pattern conformance

| pattern / statute cited | verdict |
|-------------------------|---------|
| `pattern.ui.admin-endpoint` | conforms — thin auth + candidate check + core delegate + JSON status map |
| `pattern.layers.import-discipline` / `astral.layers.import-direction` | conforms — no UI→data |
| `astral.patterns.require-auth-on-protected-endpoints` | conforms |
| `astral.standards.data-raises-caller-logs` | conforms |
| `astral.standards.in-scope-only` | conforms |

## Plan adherence

Stage 1 handler in `src/ui/api/api_intake.py` matches the plan snippet (route, `@require_auth`, LookupError/ValueError→404, 200 core JSON). Self-Assessment Scope `minor` matches footprint (one import + one route; Betty tests/bible + plan doc only beyond that). No React/preamble/topic-menu/core smuggling. Conf high / Risk Medium remain honest.

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — excluded at plan time (plan Files Changed was ui-only); in-scope on diff via `docs/features/**`. Scores **conforms** (plan doc, not a spike).

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — excluded at plan time; in-scope via features plan file. Scores **conforms** (single `ast-1097-….md`).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — excluded at plan time; in-scope via `tests/**` + `docs/test-bible/**`. Scores **conforms** (Betty `test()` / `merge-tests`; Ada `code()` only on `src/`).

No **fix-now**. Product path is clean for resolve-child; stragglers need no code change.

## What’s solid

Exact AST-582-shaped restore: `@require_auth`, alphabetical core import, defense-in-depth ValueError→404, Betty coverage for auth/shape/404/post-archive GET.

## Notes

Joan plan-rubric verdict attached (APPROVED). §5f/§5g N/A (no new `debug=` surface; no `src/external/` LLM edits).

context_tokens≈42000

— Radia

#### betty — 2026-07-31T04:42:56.649Z
## QA test manifest — AST-1097

**Publish:** `origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api` @ `02a1b6ce` (`merge-tests(AST-1097): origin/tests c957bf7e`)

### 1. Existing coverage (bible-backed)
1. `tests/component/core/test_intake.py::TestIntakeArchive` — core `archive_active_intake_session` clears active, appends `intakes_old`, LookupError when none
2. `tests/component/frontend/pages/test_CandidateIntake.test.tsx` — Start Over / Continue / archive 404 tolerance (already POSTs archive; no React change this ticket)

### 2. Broken / obsolete
None — route was missing; no prior API assertions to revise. No existing integration scenario for this path.

### 3. Gaps (this pass)
1. `tests/component/ui/api/test_api_intake.py::TestAst1097ArchiveActiveRoute` — auth 401; missing candidate 404; 200 shape (`archived_session_id` / `archived_at` / `intakes_old_count`); no-active LookupError→404; core ValueError→404; after archive GET active→404

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_intake.py::TestAst1097ArchiveActiveRoute \
  tests/component/core/test_intake.py::TestIntakeArchive \
  -q
```

### Bible shasums on publish-ref
- `docs/test-bible/ui/api/api_intake.md` `6224b74f52fdd9441a525ad855e3f80b92e85c8a`
- `tests/component/ui/api/test_api_intake.py` `1af7711771e7045b43b68e7b68523068f2b62931`

— Betty

#### joan — 2026-07-31T04:32:14.804Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1097
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Start Over without 500 / method-not-allowed | Stage 1 — restore `POST …/sessions/active/archive` |
| AC2 After Start Over, GET active reports none; fresh preamble can start | Stage 1 Done when — successful archive then GET active 404 |
| AC3 Prior conversation retained as archived history (not deleted) | Stage 1 — delegate to existing core `archive_active_intake_session` (intakes_old); no delete path |
| AC4 Continue still resumes without archiving | Stage 1 Decision — no React/Continue changes; archive only on Start Over POST |
| AC5 Unauthenticated archive rejected | Stage 1 — `@require_auth` → 401 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Wire archive route | Purpose (Start Over broken); Functional scope 1–3; Architectural `pattern.ui.admin-endpoint` + import-discipline |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub ref via engineer plan/code vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-1096/AST-1097-… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1096 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented (ValueError→404; UI-route-only restore) |
| orch.pipeline.plan-is-bible | conforms | Binding stage + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits in plan |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.config.config-source-of-truth | conforms | No new behavior-driving config; archive semantics stay in core |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src change; Betty excluded |
| astral.layers.import-direction | conforms | UI → core.intake + core.candidate only; no UI→data |
| astral.layers.ui-config-driven-business-logic | conforms | Thin API maps core outcomes; no React archive rules |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_auth` on archive mutator |
| astral.standards.data-raises-caller-logs | conforms | Core raises; API maps LookupError/ValueError to JSON 404 |
| astral.standards.debug-contract-gated | conforms | No new debug-contract work in this route restore |
| astral.standards.dry-and-focused-functions | conforms | Reuses `archive_active_intake_session`; no duplicated archive logic |
| astral.standards.in-scope-only | conforms | Single file / single route; preamble/topic-menu/React out |
| astral.standards.logging-via-utils | conforms | No print/bare logging; JSON errors only |
| astral.standards.no-cross-contamination | conforms | Stays in ui API layer |
| astral.standards.no-hardcoded-sets | conforms | No new enums/state sets |
| astral.standards.public-then-helpers | conforms | One thin handler; no helper scatter |
| astral.ui.naming-conventions | conforms | snake_case route/path; matches sibling intake handlers |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers ∩ plan {ui} empty
- astral.agent.do-task-delegation — layers ∩ plan {ui} empty
- astral.agent.grade-vector-validation — layers ∩ plan {ui} empty
- astral.batch.batch-id-first — layers ∩ plan {ui} empty
- astral.batch.batch-id-format — layers ∩ plan {ui} empty
- astral.batch.claim-process-release — layers ∩ plan {ui} empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan {ui} empty
- astral.config.pass-threshold-vs-score-floor — layers ∩ plan {ui} empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {ui} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan {ui} empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {ui} empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan {ui} empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan {ui} empty
- astral.standards.database-header-inventory — layers ∩ plan {ui} empty
- astral.standards.utils-data-late-import-only — layers ∩ plan {ui} empty
- astral.state.core-decides-transitions — layers ∩ plan {ui} empty
- astral.state.job-prior-states-enforced — layers ∩ plan {ui} empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan {ui} empty
- astral.ui.frontend-file-placement — paths {src/ui/frontend/**} match none of plan paths

## Findings

None fix-now.

**acceptable:** Self-assessment Scope minor / Conf high / Risk Medium is honest; Medium risk mitigated by reusing AST-582 core return keys and 404-tolerant UI contract. ValueError→404 Decision matches sibling intake handlers.

**R6 checklist:** Definition fidelity pass (restore missing HTTP surface only). Layer/import pass. No new config. File placement N/A (existing api module). Error handling pass. DRY pass. No scope creep into React/preamble/topic-menu.

context_tokens≈48000

— Joan

#### ada — 2026-07-31T04:30:05.547Z
Plan: [`docs/features/candidate/ast-1097-restore-archive-active-intake-api.md`](https://github.com/susansomerset/astral/blob/sub/AST-1096/AST-1097-restore-archive-active-intake-api/docs/features/candidate/ast-1097-restore-archive-active-intake-api.md) @ `b5773cb2`

**Scope:** `minor` — one import + one `POST …/sessions/active/archive` route in `src/ui/api/api_intake.py`; core archive and React Start Over already exist.

**Conf:** `high` — AST-582 defined this exact endpoint contract; sibling handlers in the same file show the pattern; failure mode is a missing HTTP surface on the clean baseline, not a core bug.

**Risk:** `Medium` — archive sits on the live Start Over path; wrong status mapping could break the UI’s 404-tolerant Start Over or leave an active session uncleared — mitigated by reusing core return keys and AST-582 exception mapping.

---

# AST-1097 — Restore archive-active intake API for Start Over

**Linear:** [AST-1097](https://linear.app/astralcareermatch/issue/AST-1097/restore-archive-active-intake-api-for-start-over-restart-intake-gets-a)  
**Parent:** [AST-1096](https://linear.app/astralcareermatch/issue/AST-1096/restart-intake-gets-a-500-error)  
**Publish ref:** `sub/AST-1096/AST-1097-restore-archive-active-intake-api`

UAT Start Over posts `POST /api/candidates/{id}/intake/sessions/active/archive` and fails (500 / “method is not allowed”) because `src/ui/api/api_intake.py` has no archive route on the current line — core `archive_active_intake_session` and React `CandidateIntake.handleResumeStartOver` already exist (AST-582 / AST-583 lineage). Restore the thin authenticated UI endpoint that maps core success / not-found / auth outcomes so Start Over can clear the active session and open a fresh preamble.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_intake.py` | Import `archive_active_intake_session`; add `POST /<candidate_id>/intake/sessions/active/archive` with `@require_auth`, candidate 404, LookupError→404 (no active session), ValueError→404/400 as below, success→200 JSON from core | ui |

## Stage 1: Wire `POST …/sessions/active/archive`

**Done when:** Authenticated `POST /api/candidates/{candidate_id}/intake/sessions/active/archive` with an active session returns **200** and a JSON body with `archived_session_id`, `archived_at`, and `intakes_old_count` (core return keys); with no active session returns **404** `{"error": "no active intake session"}` (UI already treats 404 as tolerable); without auth returns **401**; unknown candidate returns **404**. After a successful archive, `GET …/sessions/active` returns **404** (no active session). Create/get-active/turns/build/preamble/topic-menu routes are unchanged.

1. In `src/ui/api/api_intake.py`, add `archive_active_intake_session` to the existing `from src.core.intake import (` block (alphabetically among the other intake imports — place after `create_intake_session_and_start` / with the other `archive_*` / `fetch_*` names; keep the import list core-only — do **not** import `database` or `src.data`).

2. Immediately after `get_active_session` (the `GET …/sessions/active` handler, currently ending ~L89), register:

   ```python
   @intake_bp.route("/<candidate_id>/intake/sessions/active/archive", methods=["POST"])
   @require_auth
   def archive_active_session(candidate_id):
       if not get_candidate(candidate_id):
           return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
       try:
           result = archive_active_intake_session(candidate_id)
       except LookupError as e:
           return jsonify({"error": str(e)}), 404
       except ValueError as e:
           return jsonify({"error": str(e)}), 404
       return jsonify(result), 200
   ```

3. Do **not** change `archive_active_intake_session` in `src/core/intake.py`, `CandidateIntake.tsx`, `IntakeChatModal.tsx`, preamble/topic-menu routes, or `intakes_old` shape. Core already raises `LookupError("no active intake session")` when none is active and `ValueError` when the candidate is missing; the handler above maps both to **404** so the React Start Over path (`!r.ok && r.status !== 404`) stays compatible.

⚠️ **Decision:** Map core `ValueError` (candidate missing) to **404**, not **400** — matches sibling intake handlers (`get_active_session`, `get_session`) that 404 when `get_candidate` fails, and the pre-check already returns 404 before calling core; the `except ValueError` is defense-in-depth if core is called without that guard later.

⚠️ **Decision:** Restore only the UI API route — do not re-implement archive logic in the blueprint. AST-582 core + AST-590 `save_candidate_data` contract already work; this ticket’s failure mode is a missing HTTP surface (clean-baseline / route gap), not a core bug.

## Self-Assessment

**Scope:** minor — one new route + one import in `src/ui/api/api_intake.py`.

**Conf:** high — AST-582 already defined this exact endpoint contract; core and React callers are present; sibling handlers in the same file show the `@require_auth` + `get_candidate` + exception-map pattern.

**Risk:** Medium — Start Over / archive is on the live intake lifecycle path; wrong status mapping could break the UI’s 404-tolerant Start Over or leave an active session uncleared. Mitigated by reusing core return keys and matching AST-582 API expectations (`requires_auth`, `404_when_none`, `200_shape`).

## Code Rules self-review

| Rule | Check |
|------|--------|
| §2.9 / `astral.patterns.require-auth-on-protected-endpoints` | `@require_auth` on the mutator |
| §3.3 / `astral.layers.import-direction` | UI → `src.core.intake` + `src.core.candidate` only; no UI→data |
| `pattern.ui.admin-endpoint` | Thin blueprint: auth, candidate lookup, delegate, map exceptions to JSON status |
| `astral.standards.data-raises-caller-logs` | Core raises; API maps to status codes — no swallowed errors |
| `astral.standards.in-scope-only` | No React, preamble, topic-menu, or core archive edits |
| §1.3 DRY | Reuse `archive_active_intake_session` — do not duplicate archive / `intakes_old` logic in UI |

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-1097 |
| Publish ref | `origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api` |
| Built | `094477b9` |
| Notes | Stage 1 — `POST …/sessions/active/archive` in `api_intake.py`. |

### Radia — code-rubric.v1 (revision=1)

**Publish tip at review:** `d50bcfbbc3a16fdd8a7323d247fc3039e112ac7d`  
**Overall:** DISCUSS (product CLEAN; C4 stragglers only)

**What’s solid:** Thin `@require_auth` archive route matches Stage 1 verbatim; UI→core only; LookupError/ValueError→404; Betty owns test-tree; no scope creep into React/preamble/core.

**Issues (discuss):** C4 stragglers — Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot diff brings them in-scope. All three score **conforms** (plan doc not a spike; single features file; Betty `test()`/`merge-tests` for test-tree). No product fix-now.

**Recommended actions:** Resolve-child can treat as paperwork; no code change required for the stragglers.

## Resolution

**2026-07-31** — `resolve(AST-1097): — clean`

- Radia code-rubric.v1 rev=1: **DISCUSS** overall; **no fix-now**. Three C4 stragglers all **conforms** — no product or plan-content change required.
- Merged `origin/dev` + Radia `docs(AST-1097): Radia review — findings` (`7e041a37`) onto publish-ref; product archive route unchanged from `code(AST-1097)`.
- §9a dry-run vs `origin/dev` and `origin/ftr/AST-1096-restart-intake-gets-a-500-error` before User Testing.
