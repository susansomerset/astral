<!-- linear-archive: AST-986 archived 2026-08-05 -->

## Linear archive (AST-986)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-985 — Save resume pdf  
**Blocked by / blocks / related:** parent: AST-985; blocks: AST-987

### Description

## What this implements

Backend: accept pasted resume text, run the existing parse-to-structure pipeline against the **default** structure contract, return structure-keyed JSON **without** reading/writing the selected candidate or any job artifacts; debug-capable on the parse hop per AST-538 when debug is on. Does not own UI or HTML tab.

## Acceptance criteria

1. From the new **Admin** tool screen, Susan can paste resume text and run Parse; on success she receives structure-keyed resume JSON consistent with the existing base-resume parse contract (not a free-form blob).
2. Parse and HTML render succeed **without** depending on which candidate is selected in the app chrome (detached from the selector).
3. Completing the flow does not create or update candidate `artifacts.base_resume` / `artifacts.resume_structure`, job artifacts, or any other durable store for this paste.
4. A failed parse surfaces a clear error on the paste screen and does not open a blank/broken HTML tab as if success occurred.

## Boundaries

* Does not own the Admin paste page, nav, session retention, or new-tab HTML open — sibling **Admin Session Resume Paste page + HTML new tab**.
* Does not bind to the selected candidate or any job.
* Does not change Manage Tasks prompts or TASK_CONFIG registry shape beyond what is required to invoke the existing parse path in a non-persist mode.
* Does not generate server-side PDF.

## Notes for planning

* Reuse `craft_resume_base` / parse-to-structure pipeline; default resume-structure contract (no selected-candidate structure/accent/profile).
* Debug Style D on touched `debug=` surfaces per AST-538 / Code Rules.
* UI is Katherine’s sibling; expose a clear API contract she can call.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent. Engineers publish to `origin/<sub-ref>` by committing on the epic worktree sub checkout then `git push origin HEAD:<publish-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-07-27T22:25:37.207Z
[merge-child] blocked: missing plan(AST-986): sequence label (plan-child wrote docs(AST-986): plan — …). Add empty commit `plan(AST-986): — sequence label for merge-child gate` on publish ref and push. @Ada Lovelace

— Chuckles

#### radia — 2026-07-27T22:20:23.065Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-986
**Publish ref:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind` @ `6d1f8db0879b1720f460377cf98c1c2665c23bc2`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip includes single `merge-tests(AST-986)` SHA |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary on tip |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish-ref only; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-985/AST-986-…` matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | No checkout/merge violation in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | No `dev-<agent>` / agent-named publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review on `astral-AST-985` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Synthetic ctx / ledger sentinel are planned impl choices |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches plan stages + API contract |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible via `test`/`merge-tests`; not engineer product commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays implementer through review |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected on tip vocabulary |
| astral.agent.confidence-bounds | scoped | conforms | Not a graded confidence task |
| astral.agent.do-task-delegation | scoped | conforms | Core calls `do_task("craft_resume_base")` |
| astral.agent.grade-vector-validation | scoped | conforms | Not a graded-vector path |
| astral.batch.batch-id-first | scoped | conforms | Opens ledger with `batch_id` then `log_batch_id` |
| astral.batch.batch-id-format | scoped | conforms | `user-session-parse-resume-{uuid}` prefix form |
| astral.batch.claim-process-release | scoped | conforms | Cost ledger only; not dispatch claim |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | TASK_CONFIG `entity_type: None` skips entity response store |
| astral.config.config-source-of-truth | scoped | conforms | Uses `default_resume_structure` / TASK_CONFIG; no schema edit |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring / score_floor path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No new secrets or env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (no `artifacts/**` / spikes) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan only; no spike notes under features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-986-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty path is tests/bible; Ada owns src + features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code` commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | LLM I/O behind `do_task` |
| astral.layers.import-direction | scoped | conforms | ui→core; core→data/agent/utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Thin Admin route validate+delegate |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Not consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` on POST |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (no `src/data/**`) |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core/UI return JSON errors; caller logs |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Parallel session fn; not a persist-path flag |
| astral.standards.in-scope-only | scoped | conforms | Product delta is core+admin API; UI is AST-987 |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / debug helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in layered src |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state enums; intentional ledger key |
| astral.standards.public-then-helpers | scoped | conforms | Public `run_session_resume_parse` beside craft helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss (no `src/utils/**`) |
| astral.state.core-decides-transitions | scoped | conforms | No candidate/job transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state machine work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Single craft hop |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss (no `src/ui/frontend/**`) |
| astral.ui.naming-conventions | scoped | conforms | snake_case `/session_resume/parse` |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |

## Pattern conformance

none cited

## Plan adherence

Self-Assessment Scope `Single-Component` matches. Stages 1–2 delivered: synthetic default-structure ctx (no `astral_candidate_id`), response-only `split_craft_resume_base_payload`, ledger sentinel `session`, `@require_admin` Admin POST. AST-987 UI/HTML boundary held. Joan’s ledger-key / entity_type notes implemented as planned.

## Findings

**discuss** — straggler — Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time; three-dot tip brings `docs/features/**` + `tests/**`/`docs/test-bible/**` in scope. Sweep scores all three **conforms** (single plan file; Betty owns tests). No product fix required.

## What’s solid

- No persist/bind: no `get_candidate`/`save_candidate` in `run_session_resume_parse`; `craft_resume_base` `entity_type: None`.
- Debug Style D gated; `debug_detail_block` truncates.
- Betty manifest + `merge-tests(AST-986)` on tip.

**Docs:** `docs(AST-986): Radia review — findings` pushed to publish-ref.

context_tokens≈45000

#### betty — 2026-07-27T22:10:38.492Z
## QA test manifest (AST-986)

**Publish:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind` @ `066bbe6` (`merge-tests(AST-986): origin/tests 172d84787a51e283db2ce12e769d455fc92fbfe0`)

**Scope:** `run_session_resume_parse` + `POST /api/admin/session_resume/parse` — default-structure craft, response-only, no candidate bind/persist. UI/HTML/session = AST-987 (out of scope).

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst986SessionResumeParse \
  tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi \
  -q
```

1. **Core** — `TestAst986SessionResumeParse`: 400 empty/non-str; ledger `user-session-parse-resume` + sentinel `session`; fail/exception/non-dict → 500; success splits payload; **no** `get_candidate`/`save_candidate`; ctx omits `astral_candidate_id`; debug Style D on/off.
2. **Admin API** — `TestAst986SessionResumeParseApi`: `@require_admin` 403; empty/non-str/`get_json` miss → core 400; success forwards `ui_llm_debug`; 500 passthrough.

**Broken / obsolete:** none.

**Bible (on publish tip):**
- `docs/test-bible/core/candidate.md` shasum `7085d81843db74c45f0e263fa00e187f011105e8`

— Betty

#### joan — 2026-07-27T21:57:52.606Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-986
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1. Admin paste + Parse → structure-keyed resume JSON | Stages 1–2 (`run_session_resume_parse` + `POST /api/admin/session_resume/parse`); UI screen is AST-987 |
| 2. Parse/HTML succeed without selected-candidate bind | Stage 1 synthetic ctx (no `astral_candidate_id` / no `get_candidate`); HTML open is AST-987 |
| 3. Open HTML new tab / Print → PDF | N/A — boundary: sibling AST-987 |
| 4. Session retention of paste + last parse | N/A — boundary: sibling AST-987 |
| 5. No durable candidate/job artifact writes | Stage 1 forbidden persist list + response-only `resume_structure`/`base_resume` |
| 6. UI inventory (new Admin page + session; reused parse/HTML/new-tab) | Partial — this child owns reused parse API; page/session/HTML are AST-987 |
| 7. Failed parse clear error; no success-shaped blank HTML | Stage 1–2 / API contract: non-success `success:false` + 400/500; HTML gate is AST-987 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1. Paste/Parse → structure-keyed JSON (base-resume contract) | 1–2 |
| 2. Detached from candidate selector | 1 (synthetic ctx + hard rules) |
| 3. No durable artifact/store writes | 1 (forbidden persist paths) |
| 4. Failed parse clear error (no success HTML) | 1–2 API contract |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1. Core session parse (no persist) | Parent Purpose / Functional scope: parse-to-structure, default contract, no candidate bind, no DB write |
| 2. Admin API route | Parent child #1 deliverable: expose Admin POST for Katherine; Boundaries: no UI/HTML/TASK_CONFIG shape change |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | Plan does not merge tests or invent Betty SHA flow |
| orch.git.commit-vocabulary | conforms | Plan is docs/features plan only; no rogue commit vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish ref / sub topology respected; no reverse-flow steps |
| orch.git.ftr-sub-topology | conforms | Child publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | No checkout/merge procedure that violates merge-on-checkout |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force in plan |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-985/… not agent-named branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-985 assumed; no extra worktrees |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions are implementation (synthetic ctx / ledger sentinel), not product forks |
| orch.pipeline.plan-is-bible | conforms | Detailed stages + API contract for build bible |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan path |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly out of scope: tests/bible |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer is Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Ada owns build after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned path edits planned |
| astral.agent.confidence-bounds | conforms | craft_resume_base is not a graded confidence task |
| astral.agent.do-task-delegation | conforms | Core calls `do_task("craft_resume_base")` with task_key from TASK_CONFIG |
| astral.agent.grade-vector-validation | conforms | Not a graded-vector task |
| astral.batch.batch-id-first | conforms | Session ledger opens with batch_id then log_batch_id; not entity claim |
| astral.batch.batch-id-format | conforms | `f"{ledger_task_key}-{uuid}"` matches format |
| astral.batch.claim-process-release | conforms | Not a dispatch claim batch; optional cost ledger only |
| astral.batch.entity-agent-responses-latest-only | conforms | Relies on TASK_CONFIG entity_type None so `_store_agent_response` skips entity mutation |
| astral.config.config-source-of-truth | conforms | Reuses RESUME_STRUCTURE_DEFAULT / TASK_CONFIG; no schema edit |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring / score_floor path |
| astral.config.secrets-and-env-specific-from-environ | conforms | No new secrets or env-specific literals |
| astral.git.betty-no-src-or-features | conforms | Engineer (Ada) owns src + features plan; Betty not authoring |
| astral.layers.core-vs-external-bright-line | conforms | Core orchestrates; Anthropic I/O stays behind do_task/external |
| astral.layers.import-direction | conforms | ui → core only; core uses existing data/agent/utils |
| astral.layers.ui-config-driven-business-logic | conforms | Route is thin validate+delegate; no React business rules |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys touched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Not a consult/render_verdict flow |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_admin` on Admin POST |
| astral.standards.data-raises-caller-logs | conforms | Core/UI return JSON errors; no data-layer logging plan |
| astral.standards.debug-contract-gated | conforms | Style D gated on debug=True via ui_llm_debug |
| astral.standards.dry-and-focused-functions | conforms | Parallel session function; avoids silent flag on persist path |
| astral.standards.in-scope-only | conforms | Files/stages match child boundaries; siblings explicit |
| astral.standards.logging-via-utils | conforms | Uses logging utils / debug helpers |
| astral.standards.no-cross-contamination | conforms | Stays in layered src paths |
| astral.standards.no-hardcoded-sets | conforms | No new state enums; ledger key is session cost label |
| astral.standards.public-then-helpers | conforms | Public `run_session_resume_parse` beside existing craft helpers |
| astral.state.core-decides-transitions | conforms | No candidate/job state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state machine work |
| astral.state.no-daisy-chain-in-run | conforms | Single craft hop; no run_next chain invent |
| astral.ui.naming-conventions | conforms | snake_case Admin API path `/session_resume/parse` |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss (artifacts/**, scripts/spikes/**)
- astral.debug.spikes-under-debug-dir — paths miss (debug/**, docs/features/**, scripts/spikes/**)
- astral.docs.features-single-file-per-ticket — layers/paths miss (docs)
- astral.git.engineer-test-tree-ban — paths miss (tests/**, test-bible)
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss (scripts)
- astral.standards.database-header-inventory — layers/paths miss (data)
- astral.standards.utils-data-late-import-only — layers/paths miss (utils)
- astral.ui.frontend-file-placement — paths miss (src/ui/frontend/**)

## Findings

**discuss** — Stage 1 ledger key `user-session-parse-resume` is a custom string beside `_ledger_task_key_for_ui_generate` (`user-{task_key}`). Distinct key is fine for session cost visibility; at build time keep it intentional (do not silently collide with recover-by-ledger for real candidates).

**discuss** — With `requires_candidate_key` + `index=batch_id`, `_effective_entity_type` resolves to `candidate` for agent_data storage while raw TASK_CONFIG `entity_type: None` still skips `_store_agent_response`. Plan already notes this; confirm craft_resume_base does not trip caller-token hydration against the session batch id (expected: no).

**acceptable** — Self-assessment Conf high / Risk Medium matches synthetic-ctx + persist-avoidance complexity.

No fix-now findings. R1–R6 pass.

— Joan

context_tokens≈52000

#### ada — 2026-07-27T21:51:47.523Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind/docs/features/artifacts/ast-986-session-parse-api-no-persist-no-candidate-bind.md @ 60dce7a on origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind.

Scope: Single-Component — run_session_resume_parse in candidate.py + POST /api/admin/session_resume/parse; no UI/HTML/TASK_CONFIG schema edits.

Conf: high — reuses craft_resume_base + default_resume_structure + split_craft_resume_base_payload with synthetic ctx (no selected candidate).

Risk: Medium — accidental persist if someone reuses run_candidate_artifact_generation; plan forbids that path and omits astral_candidate_id.

Contract for AST-987: success returns resume_structure + base_resume (response-only); non-success never implies open-HTML.

---

# Session parse API (no persist, no candidate bind) (Save resume pdf)

**Linear:** [AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf)
**Parent:** [AST-985](https://linear.app/astralcareermatch/issue/AST-985/save-resume-pdf) — Save resume pdf
**Publish ref:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind`

Admin convenience backend: accept pasted resume text, run the existing `craft_resume_base` parse-to-structure pipeline against the **default** resume-structure contract, and return structure-keyed JSON **without** reading or writing the selected candidate (or any job artifacts). Katherine’s sibling **AST-987** owns the Admin paste page, session retention, and HTML new-tab open — this ticket exposes the API contract she calls.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `run_session_resume_parse(resume_text, *, debug=False)` — synthetic default-structure ctx, `do_task("craft_resume_base")`, split payload, **never** `save_candidate` / `get_candidate` | core |
| `src/ui/api/api_admin.py` | Add `POST /api/admin/session_resume/parse` (`@require_admin`) — validate body, call core, return JSON contract | ui |

**Out of scope (do not touch):** React pages/nav, HTML builder routes, `run_candidate_artifact_generation` persist path, `parse_candidate_resume`, Manage Tasks prompts / `TASK_CONFIG["craft_resume_base"]` schema shape, job artifact paths, `tests/`, bible.

## API contract (for AST-987)

**`POST /api/admin/session_resume/parse`**
- Auth: `@require_admin` (same as other Admin tools).
- Request JSON: `{ "resume_text": "<pasted full resume text>" }` — required; after strip, must be non-empty.
- Success **200**:
  ```json
  {
    "success": true,
    "resume_structure": { "sections": { "...": { "id", "title", "enabled", "order", "job_agent_editable" } } },
    "base_resume": { "<section_id>": "<string content>", "...": "..." },
    "parsed_response": { "...": "full craft_resume_base agent JSON" },
    "batch_id": "<ledger batch id or null>",
    "timesheet": {}
  }
  ```
  - `resume_structure` / `base_resume` come from `split_craft_resume_base_payload(parsed)` — same shape Base Resume Content persists under `artifacts.*`, but **response-only**.
  - `base_resume` keys are enabled section ids from the resolved structure (default catalog when the model omits/invalidates structure).
- Client errors **400**: `{ "success": false, "error": "<clear message>" }` — e.g. missing/empty `resume_text`, non-object body.
- Server / agent failures **500**: `{ "success": false, "error": "<clear message>", "batch_id": "..." }` — never imply success; Katherine must not open an HTML tab on non-success.

**Detached rules (hard):**
- Do **not** read Flask/session candidate selector, `request` candidate id, or `database.get_candidate` for this flow.
- Do **not** call `database.save_candidate`, `_persist_craft_dispatch_success`, or job artifact writers.
- Synthetic `ctx` must **omit** `astral_candidate_id` so `do_task` does not overlay company_search_terms / candidate API key from a real row.

## Stage 1: Core session parse (no persist)

**Done when:** `run_session_resume_parse` accepts paste text, invokes `craft_resume_base` with default structure + synthetic ctx, returns `(body, status)` matching the success/error shapes above, and a grep of the function shows no `get_candidate` / `save_candidate`.

1. In `src/core/candidate.py`, add public function `run_session_resume_parse(resume_text: str, *, debug: bool = False) -> Tuple[Dict[str, Any], int]` near `run_candidate_artifact_generation` / `parse_candidate_resume` (same module owns craft resume split helpers).
2. Validate input: if `resume_text` is not a `str` or `not resume_text.strip()`, return `({"success": False, "error": "resume_text is required"}, 400)` — do not call `do_task`.
3. Build synthetic token ctx (**no** `astral_candidate_id` key):
   ```python
   structure = default_resume_structure()
   paste = resume_text.strip()
   ctx = {
       "candidate_data": {
           "context": {"starting_resume_text": paste},
           "artifacts": {"resume_structure": structure},
       },
   }
   ```
   ⚠️ **Decision:** Satisfy `TASK_CONFIG["craft_resume_base"]["requires_candidate_key"]` with an in-memory `candidate_data` dict only — do **not** flip `requires_candidate_key` or change the response_schema. Default structure comes from `default_resume_structure()` / `RESUME_STRUCTURE_DEFAULT`, not from any selected candidate’s `artifacts.resume_structure`.
4. Ledger + batch (mirror UI generate cost trail without binding a real candidate):
   - `ledger_task_key = "user-session-parse-resume"`
   - `batch_id = f"{ledger_task_key}-{uuid.uuid4()}"`
   - `database.save_dispatch_ledger(batch_id, ledger_task_key, "session", started_at, entity_type=None, batch_size=1)` then `log_batch_id.set(batch_id)`.
   - ⚠️ **Decision:** Ledger `candidate_id="session"` is a sentinel for Admin cost visibility — **not** an `astral_candidate_id`. Do not resolve or create a candidate row for it.
5. Set debug flag: `logger.set_debug_flag(debug)`. When `debug=True`, Style D: one `debug_index` header for the parse hop (`func="run_session_resume_parse"`, `index=1`, `total=1`, identifier=`batch_id` or `"session"`, outcome success/fail) plus `debug_detail` / `debug_detail_block` for error text or truncated payload — no new ungated `[DEBUG]` info lines (§1.5.1).
6. Call `asyncio.run(do_task(task_key="craft_resume_base", live_content=paste, index=batch_id, ctx=ctx, debug=debug))` inside try/except.
   - ⚠️ **Decision:** Pass `index=batch_id` (session-scoped), **not** a real candidate id. `craft_resume_base` has `entity_type: None`, so `_store_agent_response` skips entity `agent_responses` mutation; agent_data blocks (if stored via effective entity_type) key off the session batch id, never a live candidate.
7. On exception or `not result.get("success")`: update ledger `FAILED` (when batch opened), return 500 body with `success: false` and `error` from exception / `result["error"]` / `"do_task returned None"`.
8. On success: `parsed = result["parsed_response"]`; require `isinstance(parsed, dict)` else 500 with clear error. Call `structure_out, content = split_craft_resume_base_payload(parsed)`. Update ledger `COMPLETED` + `compute_batch_cost` like `run_candidate_artifact_generation`. Return 200 body with `success`, `resume_structure=structure_out`, `base_resume=content`, `parsed_response=parsed`, `batch_id`, `timesheet=result.get("timesheet", {})`.
9. **Forbidden in this function:** any call to `database.get_candidate`, `database.save_candidate`, `_persist_craft_dispatch_success`, `_stash_pending_craft_generation`, or job/tracker artifact writers. Do not reuse `run_candidate_artifact_generation` (it persists `craft_resume_base` today) or `parse_candidate_resume` (same).
10. `finally`: `flush_log_buffer()`; `log_batch_id.set(None)`.

## Stage 2: Admin API route

**Done when:** `POST /api/admin/session_resume/parse` is registered on `admin_bp`, requires admin auth, validates JSON, delegates to `run_session_resume_parse`, and returns its `(body, status)` unchanged; `py_compile` clean on touched files.

1. In `src/ui/api/api_admin.py`, import `run_session_resume_parse` from `src.core.candidate` (keep ui → core only).
2. Add route:
   ```python
   @admin_bp.route("/session_resume/parse", methods=["POST"])
   @require_admin
   def session_resume_parse():
       body = request.get_json(silent=True) or {}
       resume_text = body.get("resume_text")
       result_body, status = run_session_resume_parse(
           resume_text if isinstance(resume_text, str) else "",
           debug=ui_llm_debug(),
       )
       return jsonify(result_body), status
   ```
   - Pass `""` when `resume_text` is missing/non-string so core returns the 400 `resume_text is required` message (single validation home).
   - Use existing `ui_llm_debug()` (already imported in this module) for the debug flag — same pattern as adhoc / candidate generate.
3. Do **not** register a new blueprint or touch `server.py` (admin_bp already registered).
4. Do **not** add NAV_CONFIG entries or frontend files (AST-987).
5. Compile: `python3 -m py_compile src/core/candidate.py src/ui/api/api_admin.py`.

## Self-Assessment

**Scope:** `Single-Component` — one core orchestrator beside existing craft helpers plus one Admin POST route; no schema/registry/UI surface.

**Conf:** `high` — reuses `do_task("craft_resume_base")`, `default_resume_structure()`, and `split_craft_resume_base_payload`; the only new behavior is synthetic ctx + skipping persist.

**Risk:** `Medium` — a mistaken `astral_candidate_id` or reuse of `run_candidate_artifact_generation` would write `artifacts.base_resume` / `resume_structure` on a real candidate; the plan forbids those paths and uses a session ledger sentinel.

## Code rules check

- §1.3 DRY: new function parallel to `parse_candidate_resume` / UI generate, not a silent flag on the persist path.
- §2.1: no new behavior literals outside existing `RESUME_STRUCTURE_DEFAULT` / TASK_CONFIG; no TASK_CONFIG schema edit.
- §2.4: optional session ledger with batch_id-first; not a dispatch claim batch.
- §2.6: no candidate/job state transitions.
- §3.3: ui → core only; core → data/agent/utils as today.
- §1.5.1: debug Style D only when `debug=True`.
- §3.6: no repo-root `artifacts/` directory.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind`  
**Tip:** `9c49edb`

**Stages delivered:**
- Stage 1 — `run_session_resume_parse` in `src/core/candidate.py` (synthetic default structure, ledger sentinel `session`, no `get_candidate`/`save_candidate`)
- Stage 2 — `POST /api/admin/session_resume/parse` on `admin_bp` (`@require_admin`, `ui_llm_debug`)

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-986
**Publish ref tip (pre-docs):** `066bbe625c6741bd6f3695c52f4103025de8b902`
**Overall:** DISCUSS

### What’s solid
- Stages 1–2 match plan: `run_session_resume_parse` + `POST /api/admin/session_resume/parse` (`@require_admin`), synthetic ctx omits `astral_candidate_id`, ledger sentinel `session`, response-only split payload.
- No `get_candidate` / `save_candidate` / persist helpers in the new path; `craft_resume_base` `entity_type: None` preserved.
- Debug Style D gated on `debug=True` via `ui_llm_debug()`; `debug_detail_block` truncates.
- Betty `merge-tests(AST-986)` + manifest coverage for core/API; UI/HTML left to AST-987.

### Findings
**discuss** — straggler — Joan excluded `astral.debug.spikes-under-debug-dir` / `astral.docs.features-single-file-per-ticket` / `astral.git.engineer-test-tree-ban` at plan time; three-dot tip brings `docs/features/**` + `tests/**`/`docs/test-bible/**` in scope. Code scores **conforms** (plan file only; Betty owns tests). No product action required unless Archie wants plan-time exclusion wording tightened.

### Recommended actions
- Engineer: no fix-now; proceed resolve-child when ready (or acknowledge stragglers).
- AST-987: consume success/`success:false` contract only.

### Statutes checked
| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip ends with single `merge-tests(AST-986)` SHA |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary on tip |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish-ref only; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-985/AST-986-…` matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | No checkout/merge violation in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force on tip |
| orch.git.no-dev-agent-branches | universal | conforms | No `dev-<agent>` / agent-named publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review on `astral-AST-985` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Synthetic ctx / ledger sentinel are planned impl choices |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches plan stages + API contract |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible via `test`/`merge-tests`; not engineer product commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays implementer through review |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected on tip vocabulary |
| astral.agent.confidence-bounds | scoped | conforms | Not a graded confidence task |
| astral.agent.do-task-delegation | scoped | conforms | Core calls `do_task("craft_resume_base")` |
| astral.agent.grade-vector-validation | scoped | conforms | Not a graded-vector path |
| astral.batch.batch-id-first | scoped | conforms | Opens ledger with `batch_id` then `log_batch_id` |
| astral.batch.batch-id-format | scoped | conforms | `user-session-parse-resume-{uuid}` prefix form |
| astral.batch.claim-process-release | scoped | conforms | Cost ledger only; not dispatch claim |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | TASK_CONFIG `entity_type: None` skips entity response store |
| astral.config.config-source-of-truth | scoped | conforms | Uses `default_resume_structure` / TASK_CONFIG; no schema edit |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring / score_floor path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No new secrets or env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (no `artifacts/**` / spikes) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan only; no spike notes under features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-986-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty path is tests/bible; Ada owns src + features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code` commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | LLM I/O behind `do_task` |
| astral.layers.import-direction | scoped | conforms | ui→core; core→data/agent/utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Thin Admin route validate+delegate |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Not consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` on POST |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (no `src/data/**`) |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core/UI return JSON errors; caller logs |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Parallel session fn; not a persist-path flag |
| astral.standards.in-scope-only | scoped | conforms | Product delta is core+admin API; UI is AST-987 |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / debug helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in layered src |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state enums; intentional ledger key |
| astral.standards.public-then-helpers | scoped | conforms | Public `run_session_resume_parse` beside craft helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss (no `src/utils/**`) |
| astral.state.core-decides-transitions | scoped | conforms | No candidate/job transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state machine work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Single craft hop |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss (no `src/ui/frontend/**`) |
| astral.ui.naming-conventions | scoped | conforms | snake_case `/session_resume/parse` |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |

### Pattern conformance
none cited

### Plan adherence
Self-Assessment Scope `Single-Component` matches (core orchestrator + Admin POST). Boundaries held vs AST-987. Joan discuss items (distinct ledger key; agent_data vs entity_type None) implemented as planned — no new product discuss beyond C4 stragglers.

### Notes
Joan plan-rubric verdict attached (APPROVED). Stragglers listed under Findings.

context_tokens≈45000

## Resolution (Ada / resolve-child) — 2026-07-27

**Review tip:** `origin/sub/AST-985/AST-986-session-parse-api-no-persist-no-candidate-bind` @ `6d1f8db` (Radia `docs(AST-986): Radia review — findings`).

**fix-now:** none.

**Discuss:** C4 straggler (Joan plan-time exclusions vs three-dot tip paths) — acknowledged; Radia scored **conforms** and called out no product action. Left as-is (no plan-wording churn without Archie ask).

**Product delta this resolve:** none — clean resolve.
