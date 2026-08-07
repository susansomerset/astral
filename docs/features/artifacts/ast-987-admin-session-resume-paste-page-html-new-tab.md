<!-- linear-archive: AST-987 archived 2026-08-05 -->

## Linear archive (AST-987)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-985 — Save resume pdf  
**Blocked by / blocks / related:** parent: AST-985

### Description

## What this implements

New Admin nav page + session retention for paste + last parse; call the session parse API sibling; open rendered HTML in a new tab via reused builder/HTML route family fed by session/in-memory JSON (no selected-candidate bind, no DB). Does not own parse agent prompts.

## Acceptance criteria

1. From the new **Admin** tool screen, Susan can paste resume text and run Parse; on success she receives structure-keyed resume JSON consistent with the existing base-resume parse contract (not a free-form blob).
2. Parse and HTML render succeed **without** depending on which candidate is selected in the app chrome (detached from the selector).
3. After a successful parse, a control opens a new browser tab showing HTML rendered with the existing resume HTML layout; Susan can Print → PDF from that tab; no job id is required.
4. Closing and reopening the tool screen within the same browser session restores the last pasted text and last successful parse result (Data Management–style retention); a full browser clear of site data wipes them.
5. Completing the flow does not create or update candidate `artifacts.base_resume` / `artifacts.resume_structure`, job artifacts, or any other durable store for this paste.
6. The UI inventory above is reflected in the shipped UX: new Admin paste page + session retention; reused parse pipeline, HTML builder/route family, and new-tab open — not ArtifactEditor, JAR materials preview, or selected-candidate inputs.
7. A failed parse surfaces a clear error on the paste screen and does not open a blank/broken HTML tab as if success occurred.

## Boundaries

* Does not own the non-persist parse backend — sibling **Session parse API (no persist, no candidate bind)**.
* Does not bind to the selected candidate or any job.
* Does not change Manage Tasks prompts or TASK_CONFIG registry shape.
* Does not generate server-side PDF — HTML new tab; user Print → PDF.

## Notes for planning

* Nav under **Admin**. Session retention mirrors Admin Data Management SQL history (`localStorage`).
* Reuse Toast and new-tab open pattern from Print Resume / materials preview.
* Depends on AST-986 API contract.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Engineers publish to `origin/<sub-ref>` by committing on the epic worktree sub checkout then `git push origin HEAD:<publish-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-07-27T22:27:13.871Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch 'origin/sub/…/AST-986…'` in the AST-987-only log. Rebase onto `origin/ftr/ast-985-save-resume-pdf` (AST-986 already on ftr), keep only AST-987 commits (no Merge remote-tracking), add `plan(AST-987): — sequence label for merge-child gate`, force-with-lease push publish ref. @Katherine Johnson

— Chuckles

#### radia — 2026-07-27T22:22:48.566Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-987
**Publish ref:** `origin/sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab` @ `e95ffa820399b831834e47f3fb0ca22fa4905c4a`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip includes single `merge-tests(AST-987)` SHA |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` + sibling merge vocab |
| orch.git.flow-direction-inviolable | universal | conforms | Merged AST-986 sub into AST-987; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-985/AST-987-…` matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | Sibling sub merge is forward integration |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review on `astral-AST-985` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Blob-URL HTML open matches planned AC |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches stages 1–3 + AST-986 call site |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests/bible via Betty `test`/`merge-tests` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays implementer |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected on tip vocabulary |
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence task in this child |
| astral.agent.do-task-delegation | scoped | conforms | No new do_task; parse via AST-986 API |
| astral.agent.grade-vector-validation | scoped | conforms | Not graded-vector work |
| astral.batch.batch-id-first | scoped | conforms | No new batch claim path in AST-987 delta |
| astral.batch.batch-id-format | scoped | conforms | No new batch_id generation in AST-987 delta |
| astral.batch.claim-process-release | scoped | conforms | Not a dispatch claim batch |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No entity agent_responses mutation here |
| astral.config.config-source-of-truth | scoped | conforms | Nav label/path only in NAV_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No new secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plans only; no spike notes under features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file per ticket (986 + 987) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty owns tests/bible; engineer owns src + features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code` commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Builder stays core; no external I/O |
| astral.layers.import-direction | scoped | conforms | ui→core builder; frontend→admin API |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Nav from NAV_CONFIG; page thin client |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Not consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` + `AdminRoute` |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (no `src/data/**`) |
| astral.standards.data-raises-caller-logs | scoped | conforms | Builder raises ValueError; UI JSON errors |
| astral.standards.debug-contract-gated | scoped | conforms | Style D gated on builder `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shares `_emit_html_document` / structure helpers |
| astral.standards.in-scope-only | scoped | conforms | Parse owned by AST-986; this child is HTML+UI |
| astral.standards.logging-via-utils | scoped | conforms | Builder uses `_log` debug helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Layered src paths |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state enums |
| astral.standards.public-then-helpers | scoped | conforms | Public `build_session_base_resume` beside `build_base_resume` |
| astral.standards.utils-data-late-import-only | scoped | conforms | NAV_CONFIG only; no utils→data invent |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next chain |
| astral.ui.frontend-file-placement | scoped | conforms | Flat `pages/AdminSessionResumePaste.tsx` + routes |
| astral.ui.naming-conventions | scoped | conforms | PascalCase page; snake_case admin paths |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn changes |

## Pattern conformance

none cited

## Plan adherence

Self-Assessment Scope `Single-Component` matches. Stages 1–3 delivered: session builder (no `get_candidate` / no profile overlay), Admin HTML POST, nav + paste page with `useLocalStorage` (`session_resume:*`), Open HTML only after successful parse + HTML POST (blob URL). AST-986 parse consumed only.

## Findings

**discuss** — straggler — Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban`; three-dot tip brings `docs/features/**` + tests/bible in scope. Sweep scores all three **conforms**. No product fix required.

## What’s solid

- Detached HTML path; no selected-candidate bind; fail → no tab.
- Debug Style D on builder; Betty manifest + `merge-tests(AST-987)`.

**Docs:** `docs(AST-987): Radia review — findings` pushed to publish-ref.

context_tokens≈48000

#### betty — 2026-07-27T22:14:18.107Z
## QA test manifest (AST-987)

**Publish:** `origin/sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab` @ `cbe3cbf` (`merge-tests(AST-987): origin/tests 1e242cdc40925c7b48cda198ad248d6b0981f7ad`)

**Scope:** `build_session_base_resume` + `POST /api/admin/session_resume/html` + Admin Session Resume Paste page (nav/route/`useLocalStorage`). Parse API owned by AST-986 (consumed only).

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume \
  tests/component/ui/api/test_api_admin.py::TestAst987SessionResumeHtmlApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx
```

1. **Builder** — `TestAst987BuildSessionBaseResume`: invalid structure/empty content → `ValueError`; success HTML from in-memory payload; **no** `get_candidate`; debug on/off.
2. **Admin HTML API** — `TestAst987SessionResumeHtmlApi`: `@require_admin` 403; bad body / builder `ValueError` → 400; success `text/html` + `ui_llm_debug`.
3. **Page (§6c)** — `test_AdminSessionResumePaste.test.tsx`: render + Parse success enables Open HTML (no auto-tab); parse fail error / no tab; Open HTML blob URL; HTML error / no tab; localStorage restore.

**Broken / obsolete:** none.

**Bible (on publish tip):**
- `docs/test-bible/frontend/pages.md` shasum `6b2de34d1263352795ec6c284512a7964e1b441f`

— Betty

#### joan — 2026-07-27T22:00:12.729Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-987
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1. Admin paste + Parse → structure-keyed resume JSON | Stage 3 Parse handler → AST-986 `POST /api/admin/session_resume/parse` |
| 2. Parse/HTML succeed without selected-candidate bind | Stages 1–3: synthetic `cd`, no `get_candidate` / `useCandidate` for parse/HTML |
| 3. Control opens HTML new tab; Print → PDF; no job id | Stages 1–2 builder+HTML POST; Stage 3 Open HTML → blob URL tab |
| 4. Session retention of paste + last successful parse | Stage 3 `useLocalStorage` keys; clear site data wipes |
| 5. No durable candidate/job artifact writes | Stages 1–3: no persist endpoints; response/localStorage only |
| 6. UI inventory (new Admin page + session; reused parse/HTML/new-tab) | Stage 3 nav/page; Stages 1–2 reuse builder emit; Stage 3 calls AST-986 parse |
| 7. Failed parse clear error; no success-shaped blank HTML | Stage 3: non-success parse never opens tab; HTML POST failures never open tab |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1–7 (same as parent AC list on child) | Mapped above; parse backend owned by AST-986 (blockedBy), consumed at Stage 3 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1. Session HTML builder | Purpose / Functional scope: render HTML from in-memory JSON; no candidate bind / no DB |
| 2. Admin session HTML route | Reused HTML builder/route family adapted for session/in-memory JSON under Admin |
| 3. Admin nav + paste page | New Admin screen, session retention, call #1 parse API, new-tab open control |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge/SHA invent |
| orch.git.commit-vocabulary | conforms | Plan doc only; no rogue commit vocab |
| orch.git.flow-direction-inviolable | conforms | Waits for AST-986 on ftr; no reverse-flow |
| orch.git.ftr-sub-topology | conforms | Publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | Mentions merge ftr after sibling land; no forbidden ops |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-985/… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-985 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Blob-URL vs GET is implementation; matches AC control |
| orch.pipeline.plan-is-bible | conforms | Detailed stages + AST-986 call contract |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan path |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Katherine |
| orch.roles.engineer-assignee-through-resolve | conforms | Katherine owns build after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded agent task in this child |
| astral.agent.do-task-delegation | conforms | No new do_task; parse via AST-986 API |
| astral.agent.grade-vector-validation | conforms | Not graded-vector work |
| astral.batch.batch-id-first | conforms | No new batch claim path |
| astral.batch.batch-id-format | conforms | No new batch_id generation here |
| astral.batch.claim-process-release | conforms | Not a dispatch claim batch |
| astral.batch.entity-agent-responses-latest-only | conforms | No entity agent_responses mutation |
| astral.config.config-source-of-truth | conforms | Nav label/path only in NAV_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring path |
| astral.config.secrets-and-env-specific-from-environ | conforms | No new secrets/env values |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src + features plan |
| astral.layers.core-vs-external-bright-line | conforms | Builder stays core; no external I/O invent |
| astral.layers.import-direction | conforms | ui → core builder; frontend → admin API only |
| astral.layers.ui-config-driven-business-logic | conforms | Nav from NAV_CONFIG; page is thin client |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Not consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_admin` on HTML POST; page under AdminRoute |
| astral.standards.data-raises-caller-logs | conforms | UI returns JSON errors; core raises ValueError |
| astral.standards.debug-contract-gated | conforms | Style D on builder when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Shares `_emit_html_document` / structure helpers |
| astral.standards.in-scope-only | conforms | Boundaries respect AST-986 ownership |
| astral.standards.logging-via-utils | conforms | Uses builder debug helpers |
| astral.standards.no-cross-contamination | conforms | Layered src paths only |
| astral.standards.no-hardcoded-sets | conforms | No new state enums |
| astral.standards.public-then-helpers | conforms | Public `build_session_base_resume` beside `build_base_resume` |
| astral.standards.utils-data-late-import-only | conforms | NAV_CONFIG only in config.py; no utils→data invent |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No run_next chain |
| astral.ui.frontend-file-placement | conforms | Flat `pages/AdminSessionResumePaste.tsx`; routes.tsx wiring |
| astral.ui.naming-conventions | conforms | PascalCase page; snake_case `/admin/session_resume_paste` |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss (docs)
- astral.git.engineer-test-tree-ban — paths miss (tests/bible)
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss (scripts)
- astral.standards.database-header-inventory — layers/paths miss (data)

## Findings

**discuss** — Retention uses `useLocalStorage` (Ad Hoc pattern) rather than Data Management’s raw `HISTORY_KEY` helper. Parent asks for Data Management–*style* browser retention; this still satisfies AC4. Keep keys namespaced (`session_resume:*`) as planned.

**acceptable** — Conf high / Risk Medium matches candidate-bound print-route footgun + AST-986 ftr dependency. Skipping `_apply_profile_to_render_dict` is the right detach move vs `build_base_resume`.

No fix-now findings. R1–R6 pass.

— Joan

context_tokens≈60000

#### katherine — 2026-07-27T21:54:39.294Z
Plan published for Joan (`validate-plan`).

**Plan doc:** [docs/features/artifacts/ast-987-admin-session-resume-paste-page-html-new-tab.md](https://github.com/susansomerset/astral/blob/sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab/docs/features/artifacts/ast-987-admin-session-resume-paste-page-html-new-tab.md) on `origin/sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab` @ `d28d240`.

**Self-assessment**
- **Scope:** `Single-Component` — session HTML builder helper, admin HTML POST, nav/route, one Admin paste page; no persist/schema/registry work.
- **Conf:** `high` — reuses `build_base_resume` emit path, Admin `api()` + `useLocalStorage`, and the AST-986 parse contract as the only parse call site.
- **Risk:** `Medium` — mistaken candidate-bound print route or craft persist would violate AC; plan forbids those paths and keeps Open HTML behind successful parse + successful HTML POST. Build waits on AST-986 landing on `ftr`.

**Approach notes:** HTML via `POST /api/admin/session_resume/html` → blob URL new tab (session JSON too large for GET `/candidate/resume/*`); contact/header from paste section strings, not selected-candidate profile.

---

# Admin Session Resume Paste page + HTML new tab (Save resume pdf)

**Linear:** [AST-987](https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf)
**Parent:** [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) — Save resume pdf
**Publish ref:** `origin/sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab`
**Blocked by:** [AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf) — `POST /api/admin/session_resume/parse` contract (consume only; do not re-implement parse)

Admin Session Resume Paste workbench: new Admin nav page where Susan pastes resume text, calls the AST-986 session parse API, retains paste + last successful parse in `localStorage` (Data Management–style), and opens rendered HTML in a new browser tab via a session HTML endpoint that reuses the base-resume builder with in-memory JSON — no selected-candidate bind, no DB writes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Add `build_session_base_resume(resume_structure, base_resume, *, debug=False) -> str` — same HTML emit path as `build_base_resume`, zero `get_candidate` / DB | core |
| `src/ui/api/api_admin.py` | Add `POST /api/admin/session_resume/html` (`@require_admin`) — validate JSON body, return `text/html` or JSON error | ui |
| `src/utils/config.py` | Add Admin `NAV_CONFIG` item for Session Resume Paste | utils |
| `src/ui/frontend/src/routes.tsx` | Register `/admin/session_resume_paste` under `AdminRoute` | ui |
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | New page: paste textarea, Parse, Open HTML, Toast, `useLocalStorage` retention | ui |

**Out of scope (do not touch):** AST-986 parse core/route (already planned/owned by Ada), `TASK_CONFIG` / Manage Tasks prompts, `ArtifactEditor` / Base Resume Content page, job resume/cover HTML routes behavior, Materials Preview modal, candidate selector wiring, `tests/`, bible, repo-root `artifacts/`.

## Dependency contract (AST-986 — call site only)

**`POST /api/admin/session_resume/parse`** (must exist before Stage 3 runtime exercise; merge `origin/ftr/ast-985-save-resume-pdf` after AST-986 lands on ftr):

- Request: `{ "resume_text": "<paste>" }`
- Success 200: `{ success: true, resume_structure, base_resume, parsed_response, batch_id, timesheet }`
- Failure 400/500: `{ success: false, error: "<clear message>", ... }` — treat any non-success / non-ok as failure; **never** open the HTML tab.

## Stage 1: Session HTML builder (core, no candidate bind)

**Done when:** `build_session_base_resume` returns print-oriented HTML from in-memory structure + content dicts; a grep of the function shows no `get_candidate`, `database.`, or `candidate_id`; empty/invalid inputs raise `ValueError` with clear messages.

1. In `src/core/builder.py`, add public function `build_session_base_resume(resume_structure: dict, base_resume: dict, *, debug: bool = False) -> str` immediately after `build_base_resume`.
2. Validate inputs before any emit:
   - If `resume_structure` is not a `dict`, or lacks a `sections` dict, raise `ValueError("resume_structure with sections is required")`.
   - If `base_resume` is not a non-empty `dict` (`_is_nonempty_resume_dict`), raise `ValueError("base_resume content is required")`.
3. Build a **synthetic** in-memory candidate blob only (never load a row):
   ```python
   cd = {
       "artifacts": {
           "resume_structure": resume_structure,
           "base_resume": base_resume,
       },
       "profile": {},
   }
   ```
   ⚠️ **Decision:** Detach from selected candidate by constructing `cd` entirely from the request payload. Do **not** call `candidate_mod.get_candidate` or read Flask/session candidate id.
4. Mirror `build_base_resume` emit steps on `cd`:
   - `structure = candidate_mod.resolve_resume_structure(cd)`
   - `render = candidate_mod.filter_content_to_resume_structure(dict(base_resume), structure)`
   - **Do not** call `_apply_profile_to_render_dict` — contact/header must come from paste/parse section strings (`candidate_name`, `candidate_title`, `candidate_contact_detail`), not a profile row.
   - `style = _merge_effective_style(cd)` (accent from session `resume_structure` / default `BUILD_CONFIG` only)
   - `markers = _apply_resume_text_markers(render)`
   - `ordered_body = _structure_ordered_body_ids(structure)`
   - `titles = candidate_mod.resume_section_titles(structure)`
   - `html_out = _emit_html_document(...)` with `include_cover=False`, same args as `build_base_resume`.
5. When `debug=True`, Style D header (`func="builder.build_session_base_resume"`, `index=1`, `total=1`, identifier=`"session"`, outcome success) plus detail lines for enabled sections / html_chars — no ungated `[DEBUG]` info lines (§1.5.1).
6. Return `html_out`. Do not write any candidate/job artifact.

## Stage 2: Admin session HTML route

**Done when:** `POST /api/admin/session_resume/html` is registered on `admin_bp`, requires admin auth, returns `text/html` on valid body and JSON `{success:false,error}` on bad input / `ValueError`; `py_compile` clean on touched Python files.

1. In `src/ui/api/api_admin.py`, import `build_session_base_resume` from `src.core.builder` and `Response` from Flask if not already imported.
2. Add route (place near the AST-986 parse route once present; if parse is not on this branch yet, place after other admin tool routes and leave a one-line comment `# AST-987 session resume HTML`):
   ```python
   @admin_bp.route("/session_resume/html", methods=["POST"])
   @require_admin
   def session_resume_html():
       body = request.get_json(silent=True) or {}
       structure = body.get("resume_structure")
       content = body.get("base_resume")
       if not isinstance(structure, dict) or not isinstance(content, dict):
           return jsonify({
               "success": False,
               "error": "resume_structure and base_resume objects are required",
           }), 400
       try:
           html = build_session_base_resume(
               structure,
               content,
               debug=ui_llm_debug(),
           )
       except ValueError as exc:
           return jsonify({"success": False, "error": str(exc)}), 400
       return Response(html, mimetype="text/html; charset=utf-8")
   ```
3. Do **not** register a new blueprint or change `server.py`.
4. Do **not** alter `/candidate/resume/base` or job resume/cover routes.
5. Compile: `python3 -m py_compile src/core/builder.py src/ui/api/api_admin.py`.

⚠️ **Decision:** HTML lives under `/api/admin/session_resume/html` next to the parse sibling (admin-gated), not as a GET on `/candidate/resume/*`. Session JSON is too large for a Print-Resume-style GET URL; the page POSTs via `api()` (Bearer) then opens a blob URL (Stage 3) — same builder family, adapted for in-memory JSON without server-side session cache.

## Stage 3: Admin nav + Session Resume Paste page

**Done when:** Admin nav shows **Session Resume Paste**; route `/admin/session_resume_paste` renders the page inside `AdminRoute`; paste + last successful parse restore after leave/return via `localStorage`; Parse calls AST-986; Open HTML only after a successful parse and only when the HTML POST succeeds; failed parse shows a clear error and never opens a tab; page does not read `useCandidate().selectedId` for parse/HTML.

1. In `src/utils/config.py` `NAV_CONFIG` Admin `items` list, add after **Data Management**:
   ```python
   {"label": "Session Resume Paste", "path": "/admin/session_resume_paste"},
   ```
2. In `src/ui/frontend/src/routes.tsx`:
   - Import `SessionResumePaste` from `./pages/AdminSessionResumePaste`.
   - Add child route: `{ path: "admin/session_resume_paste", element: <AdminRoute><SessionResumePaste /></AdminRoute> }` next to `admin/data_management`.
3. Create `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` as a default-export page component named `SessionResumePaste` (file name matches Admin section prefix; export default function `SessionResumePaste`).
4. **localStorage retention** (reuse `useLocalStorage` from `src/ui/frontend/src/lib/useLocalStorage.ts` — same persistence idea as Data Management SQL history / Ad Hoc):
   - Key `session_resume:paste_text` — `string`, default `""`. Bind to the textarea; updates write through automatically.
   - Key `session_resume:last_parse` — type:
     ```ts
     type SessionResumeParse = {
       resume_structure: Record<string, unknown>
       base_resume: Record<string, unknown>
     } | null
     ```
     default `null`. Set **only** on successful parse (`success === true` and both objects present). Do **not** clear on failed parse (keep prior success for Open HTML). Clearing site data wipes both keys (browser behavior — no extra code).
5. **UI layout** (reuse existing classes / inline style patterns from `AdminDataManagement.tsx` — `dep-btn`, `dep-input`, CSS variables; do **not** edit `App.css` unless a class is truly missing — prefer existing tokens):
   - Page title: `Session Resume Paste`.
   - Short helper line: paste a full resume, Parse to structure-keyed JSON, then Open HTML to print → PDF. State that this tool does not use the selected candidate and does not save to the database.
   - Multiline `<textarea className="dep-input">` bound to paste text (monospace, full width, ~16 rows, `spellCheck={false}`).
   - Buttons row:
     - **Parse** — disabled when `pasteText.trim()` is empty or `parsing` is true.
     - **Open HTML** — disabled when `lastParse` is null or `opening` / `parsing` is true.
   - Inline error `<p>` (or equivalent) for the latest parse/HTML failure message; clear it when a new Parse starts successfully or when paste changes if desired — minimum: set on failure, clear on successful parse.
   - `<Toast message={toast} onDone={clearToast} />` for success/error feedback.
6. **Parse handler** (`POST /api/admin/session_resume/parse`):
   ```ts
   const r = await api("/api/admin/session_resume/parse", {
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({ resume_text: pasteText }),
   })
   const data = await r.json().catch(() => ({}))
   ```
   - If `!r.ok` or `data.success !== true`: set error text from `data.error` or ``HTTP ${r.status}``; Toast variant `error`; **return without** updating `lastParse` and **without** opening a tab.
   - If success: require `data.resume_structure` and `data.base_resume` to be objects; otherwise treat as failure with a clear error.
   - On success: `setLastParse({ resume_structure: data.resume_structure, base_resume: data.base_resume })`; Toast success (e.g. `Parsed resume structure.`); clear inline error.
   - ⚠️ **Decision:** Do **not** auto-open the HTML tab on parse success — AC requires a **control** that opens the tab; the Open HTML button is that control (avoids surprise popup-blocker failures masking parse success).
7. **Open HTML handler** (`POST /api/admin/session_resume/html`):
   - Guard: if `!lastParse`, return.
   - `api("/api/admin/session_resume/html", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(lastParse) })`.
   - If `!r.ok`: try parse JSON error body for `error`; Toast error; **do not** open a tab.
   - If ok: `const html = await r.text()`; if empty/whitespace-only, Toast error and return.
   - Open tab:
     ```ts
     const blobUrl = URL.createObjectURL(new Blob([html], { type: "text/html;charset=utf-8" }))
     const win = window.open(blobUrl, "_blank", "noopener,noreferrer")
     if (!win) {
       setToast({ text: "Popup blocked — allow popups to open the HTML tab.", variant: "error" })
     }
     window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
     ```
   - ⚠️ **Decision:** Blob URL after authenticated POST (not `window.open("/candidate/resume/...")`) because session JSON is request-bodied and must not depend on selected-candidate query params or server-side draft storage.
8. **Hard UI bans:**
   - Do not import or call `useCandidate` for parse/HTML inputs (selector chrome may still render in the shell — ignore it).
   - Do not navigate to Base Resume Content, ArtifactEditor, Materials Preview, or job print routes.
   - Do not POST to candidate generate/persist artifact endpoints.
9. Typecheck/lint the touched frontend files with the repo’s usual frontend check if available (`npm` script in `src/ui/frontend`); at minimum ensure the new page compiles under Vite/`tsc` as used by other Admin pages.

## Self-Assessment

**Scope:** `Single-Component` — one builder helper, one admin HTML POST, nav/route wiring, and one Admin page; no schema/registry/persist path changes.

**Conf:** `high` — reuses `build_base_resume` emit helpers, Admin `@require_admin` + `api()` patterns, `useLocalStorage`, and the AST-986 parse contract already written on the sibling publish ref.

**Risk:** `Medium` — wrong wiring could call candidate-bound `/candidate/resume/base` or persist craft generate; the plan forbids those paths and keeps contact fields on paste JSON only. Build is blocked until AST-986’s parse route is on the epic `ftr` line.

## Code rules check

- §1.3 DRY: session builder shares `_emit_html_document` / structure helpers with `build_base_resume`; does not fork a second HTML template.
- §2.1: nav path/label only in `NAV_CONFIG`; no new TASK_CONFIG / magic state sets.
- §2.6: no candidate/job state transitions.
- §3.2 / §3.3: ui → core only for builder; no ui → data; frontend calls admin API only.
- §3.5: PascalCase page file, snake_case route path, flat `pages/` placement, routes.tsx SYNC comment honored via NAV_CONFIG.
- §1.5.1: debug Style D only when `debug=True` on the builder path.
- §3.6: no repo-root `artifacts/` directory; plan under `docs/features/artifacts/`.

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab`  
**Tip:** `2739b25`

**Stages delivered:**
- Stage 1 — `build_session_base_resume` in `src/core/builder.py` (in-memory structure + content; no `get_candidate` / profile overlay)
- Stage 2 — `POST /api/admin/session_resume/html` on `admin_bp` (`@require_admin`, `ui_llm_debug`)
- Stage 3 — `NAV_CONFIG` + `/admin/session_resume_paste` + `AdminSessionResumePaste.tsx` (`useLocalStorage` retention; AST-986 parse; blob URL Open HTML)

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-987
**Publish ref tip (pre-docs):** `cbe3cbff6b0228f684180bac4187d1301b76c27f`
**Overall:** DISCUSS

### What’s solid
- Stages 1–3 match plan: `build_session_base_resume` (synthetic `cd`, no `get_candidate` / no profile overlay), `POST /api/admin/session_resume/html` (`@require_admin`), Admin page + `NAV_CONFIG` + `AdminRoute`, `useLocalStorage` keys `session_resume:*`, Open HTML only after successful parse + successful HTML POST via blob URL.
- AST-986 parse consumed only; no TASK_CONFIG / persist / candidate print-route reuse.
- Debug Style D on builder when `debug=True`; Betty `merge-tests(AST-987)` + page/API/builder coverage.

### Findings
**discuss** — straggler — Joan excluded `astral.debug.spikes-under-debug-dir` / `astral.docs.features-single-file-per-ticket` / `astral.git.engineer-test-tree-ban`; three-dot tip brings `docs/features/**` + tests/bible in scope. All score **conforms**. No product action.

### Recommended actions
- Engineer: no fix-now; resolve-child when ready (acknowledge stragglers).

### Statutes checked
| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip ends with single `merge-tests(AST-987)` SHA |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` + sibling merge vocab |
| orch.git.flow-direction-inviolable | universal | conforms | Merged AST-986 sub into AST-987; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-985/AST-987-…` matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | Sibling sub merge is forward integration |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review on `astral-AST-985` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Blob-URL HTML open matches planned AC |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches stages 1–3 + AST-986 call site |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests/bible via Betty `test`/`merge-tests` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays implementer |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected on tip vocabulary |
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence task in this child |
| astral.agent.do-task-delegation | scoped | conforms | No new do_task; parse via AST-986 API |
| astral.agent.grade-vector-validation | scoped | conforms | Not graded-vector work |
| astral.batch.batch-id-first | scoped | conforms | No new batch claim path in AST-987 delta |
| astral.batch.batch-id-format | scoped | conforms | No new batch_id generation in AST-987 delta |
| astral.batch.claim-process-release | scoped | conforms | Not a dispatch claim batch |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No entity agent_responses mutation here |
| astral.config.config-source-of-truth | scoped | conforms | Nav label/path only in NAV_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No new secrets/env values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plans only; no spike notes under features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file per ticket (986 + 987) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty owns tests/bible; engineer owns src + features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code` commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Builder stays core; no external I/O |
| astral.layers.import-direction | scoped | conforms | ui→core builder; frontend→admin API |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Nav from NAV_CONFIG; page thin client |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Not consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` + `AdminRoute` |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (no `src/data/**`) |
| astral.standards.data-raises-caller-logs | scoped | conforms | Builder raises ValueError; UI JSON errors |
| astral.standards.debug-contract-gated | scoped | conforms | Style D gated on builder `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shares `_emit_html_document` / structure helpers |
| astral.standards.in-scope-only | scoped | conforms | Parse owned by AST-986; this child is HTML+UI |
| astral.standards.logging-via-utils | scoped | conforms | Builder uses `_log` debug helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Layered src paths |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state enums |
| astral.standards.public-then-helpers | scoped | conforms | Public `build_session_base_resume` beside `build_base_resume` |
| astral.standards.utils-data-late-import-only | scoped | conforms | NAV_CONFIG only; no utils→data invent |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next chain |
| astral.ui.frontend-file-placement | scoped | conforms | Flat `pages/AdminSessionResumePaste.tsx` + routes |
| astral.ui.naming-conventions | scoped | conforms | PascalCase page; snake_case admin paths |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn changes |

### Pattern conformance
none cited

### Plan adherence
Self-Assessment Scope `Single-Component` matches. Joan’s `useLocalStorage` retention note implemented with namespaced keys. Boundaries vs AST-986 held (consume parse; own HTML+UI).

### Notes
Joan plan-rubric verdict attached (APPROVED). Stragglers under Findings.

context_tokens≈48000

## Resolution

**Date:** 2026-07-27  
**Publish ref:** `origin/sub/AST-985/AST-987-admin-session-resume-paste-page-html-new-tab`  
**Radia tip intake:** `e95ffa8` (`docs(AST-987): Radia review — findings`)

- **fix-now:** none.
- **discuss (stragglers):** Acknowledged — Joan’s plan-rubric exclusions for `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` are scored **conforms** on the three-dot tip; no product or plan-stage change required.
- **advisory:** none.
- **Product delta this resolve:** none (clean).
