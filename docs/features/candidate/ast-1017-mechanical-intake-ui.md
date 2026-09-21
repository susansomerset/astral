<!-- linear-archive: AST-1017 archived 2026-08-07 -->

## Linear archive (AST-1017)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1017/mechanical-intake-front-door-ui-candidate-profile-preamble-to-intake  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-952 — Candidate Profile Preamble to Intake  
**Blocked by / blocks / related:** parent: AST-952

### Description

## What this implements

Resume → LinkedIn → sample cover letter (and any other PREAMBLE_CONFIG steps) mechanical UI that writes the correct fields and calls Ruth validation (AST-1015), driven by PREAMBLE_CONFIG (AST-1016). Familiar seamless feel into Estelle.

## Acceptance criteria

- [X] 4. Candidate can complete the mechanical preamble UI driven by PREAMBLE_CONFIG; Valid answers persist to the correct columns/blobs; UI calls Ruth validation rather than inlining a checker.
- [X] 5. Hopes, interests, and concerns exist as context fields for Topic Menu; Estelle confirm UI is **not** required in this epic (AST-953).
- [X] 6. After Valid mechanical sources are stored, contact + context are complete enough to feed AST-953.

## Boundaries

- [X] Does **not** own library (AST-1014), validation task (AST-1015), config (AST-1016), or Topic Menu / Estelle confirm (AST-953).
- [X] Does **not** inline Ruth validation or hardcode the preamble step script in React.
- [X] Does **not** add hopes/interests/concerns editors or change the candidate state machine.

## In scope

- [X] `astral.layers.ui-config-driven-business-logic` — mechanical UI reads `PREAMBLE_CONFIG` via `/api/ui_config`; does not own the script
- [X] `astral.config.config-source-of-truth` — Intro / steps / targets / try-copy from config; UI does not hardcode the sequence
- [X] `astral.ui.frontend-file-placement` — `IntakePreamblePanel` in `components/`; page stays `CandidateIntake.tsx`; styles in `App.css`
- [X] `astral.ui.naming-conventions` — PascalCase component; snake_case API paths unchanged
- [X] `astral.layers.import-direction` — React → API only; no core/data imports from frontend
- [X] `astral.docs.features-single-file-per-ticket` — one plan doc `docs/features/candidate/ast-1017-mechanical-intake-ui.md`
- [X] `astral.patterns.require-auth-on-protected-endpoints` — consume existing auth’d validate + PUT `/data` + ui_config (no new open routes)

## Considered but excluded

- [X] `astral.agent.do-task-delegation` — Ruth `do_task` owned by AST-1015; this UI only POSTs `/preamble/validate`
- [X] `astral.standards.debug-contract-gated` — backend-only; UI has no debug-logging requirement (§1.5.1)
- [X] `astral.layers.core-vs-external-bright-line` — no core/external changes in this child
- [X] `astral.standards.database-header-inventory` — no schema work (AST-1014)
- [X] `astral.state.core-decides-transitions` / candidate state registry — no state transitions
- [X] `astral.debug.spikes-under-debug-dir` — no spike deliverables
- [X] `astral.git.engineer-test-tree-ban` — no `tests/` edits (Betty)

## Notes for planning

After AST-1014, AST-1015, and AST-1016. Build requires AST-1015 on `origin/ftr` (validate route).

## Git branch (authoritative)

`sub/AST-952/AST-1017-mechanical-intake-ui`. Publish to `origin/<publish-ref>` only.

### Comments

#### chuckles — 2026-07-30T02:02:57.033Z
[merge-child] blocked:

- `validate-sub-log`: git pull merge on sub — `05ad519f Merge remote-tracking branch 'origin/dev' into sub/AST-952/AST-1017-mechanical-intake-ui` (replace with `git fetch && git merge origin/ftr/AST-952-candidate-profile-preamble-to-intake`). @Katherine Johnson
- Blockers not on ftr tip: AST-1014 (Ada), AST-1015 (Hedy — also validate-sub-log pull-merge). Parent wave resumes after those land on `origin/ftr/AST-952-candidate-profile-preamble-to-intake`.

— Chuckles

#### radia — 2026-07-30T02:00:31.027Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1017
**Publish ref:** `sub/AST-952/AST-1017-mechanical-intake-ui` @ `4c4d837f59d74bde36e43199926066e5b747a13e` (product tip `41777892`; docs append `4c4d837f`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single merge-tests(AST-1017) from Betty tip |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocab on publish-ref |
| orch.git.flow-direction-inviolable | universal | conforms | Publish to origin/sub only; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | Child on sub/AST-952/AST-1017-mechanical-intake-ui |
| orch.git.merge-on-checkout | universal | conforms | Tip merged ftr before build |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | Named sub/ only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-952 |
| orch.git.three-permanent-branches | universal | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Skip-non-empty Decision documented; no open blocker |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match shipped UI |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Candidate only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | universal | conforms | Vitest/bible via Betty merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer code = three UI files only |
| astral.agent.confidence-bounds | scoped | conforms | No confidence math in AST-1017 delta |
| astral.agent.do-task-delegation | scoped | conforms | UI POSTs validate; no do_task from React |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched by AST-1017 delta |
| astral.batch.batch-id-first | scoped | conforms | No claim API work |
| astral.batch.batch-id-format | scoped | conforms | No batch_id work in UI |
| astral.batch.claim-process-release | scoped | conforms | No batch claim path |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Intro/steps/prompts/targets from ui_config preamble |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets introduced |
| astral.debug.no-repo-root-artifacts-dir | scoped | conforms | No repo-root artifacts/ added by AST-1017 |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under docs/features/; not a spike |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file ast-1017-…md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits exclude product features authorship |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commit has no tests/ |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No core/external in AST-1017 delta |
| astral.layers.import-direction | scoped | conforms | React → api client only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | No scripts edits in AST-1017 delta |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | UI executes PREAMBLE_CONFIG; does not own script/validation |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | Consumes existing auth’d ui_config/validate/PUT; no new open routes |
| astral.standards.database-header-inventory | scoped | conforms | No schema work in AST-1017 delta |
| astral.standards.data-raises-caller-logs | scoped | conforms | UI Toast on API errors |
| astral.standards.debug-contract-gated | scoped | conforms | UI exempt (§1.5.1); no frontend debug contract |
| astral.standards.dry-and-focused-functions | scoped | conforms | One panel for all steps; reuse Modal/api/Toast/intake classes |
| astral.standards.in-scope-only | scoped | conforms | code(AST-1017) = App.css + IntakePreamblePanel + CandidateIntake only |
| astral.standards.logging-via-utils | scoped | conforms | Frontend Toast only |
| astral.standards.no-cross-contamination | scoped | conforms | Stays on frontend UI surface |
| astral.standards.no-hardcoded-sets | scoped | conforms | Script from config; PREAMBLE_OUTCOMES single UI mirror |
| astral.standards.public-then-helpers | scoped | conforms | Focused component helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data in AST-1017 delta |
| astral.state.core-decides-transitions | scoped | conforms | No candidate transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | conforms | Component in components/; page CandidateIntake.tsx; CSS App.css |
| astral.ui.naming-conventions | scoped | conforms | PascalCase IntakePreamblePanel; snake_case API paths |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker changes |

## Pattern conformance

none cited (ticket In-scope lists statute ids, not pattern catalog ids)

## Plan adherence

Stages 1–3 match: config-driven panel, Valid-only PUT, Try Again/Escalate stay, preamble→Estelle handoff, hard-gate removed, CSS reuse. Self-Assessment Single-Component / high / Medium fits. FIELD_TO_MATERIAL bridge matches sibling session-key table (not a second script).

## Findings

### discuss
1. **C4 stragglers** — Joan excluded at plan time; three-dot tip vs `origin/dev` scores in-scope (tip↔dev diverged; 425-path XOR / multiple merge bases): `astral.agent.confidence-bounds`, `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`, `astral.config.pass-threshold-vs-score-floor`, `astral.debug.no-repo-root-artifacts-dir`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.standards.database-header-inventory`, `astral.standards.utils-data-late-import-only`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced`, `astral.state.no-daisy-chain-in-run`. All **conform**; topology-only — no AST-1017 product fix.

### advisory
- Joan’s non-blocking plan discuss (Profile-entered `raw_*` skip Ruth) remains product policy, not a code defect.

## What’s solid

Valid gate before PUT; Escalate never advances; Continue-on-active skips preamble; Estelle-consistent Intro chrome.

## Recommended actions

No fix-now. Engineer may proceed via resolve-child / User Testing.

## Notes

Joan plan-rubric APPROVED. Docs append @ `4c4d837f`.

context_tokens≈82000

#### betty — 2026-07-30T01:56:38.093Z
Tests Ready — mechanical preamble UI coverage published.

**Publish:** `origin/sub/AST-952/AST-1017-mechanical-intake-ui` @ `41777892` (`merge-tests(AST-1017): origin/tests 37525794`)

**Manifest**
1. `tests/component/frontend/components/test_IntakePreamblePanel.test.tsx` — Intro + first pending step from ui_config; skip filled / Continue when no pending; Valid → PUT then advance; Try Again (no PUT / 2nd-try prompt); Escalate toast (no PUT / no advance)
2. `tests/component/frontend/pages/test_CandidateIntake.test.tsx` (§6c) — Start Intake confirm → preamble Modal; missing resume → preamble (no Profile hard-gate); Valid handoff → Estelle chat; Continue skips preamble; Start Over → preamble (not Estelle yet); Start Over archive 404 → preamble

**Fixture:** `tests/component/frontend/fixtures/ast1017PreambleConfig.ts`

**Broken / revised:** Profile resume hard-gate redirect toast; Start Over auto-start Estelle before preamble; Start Intake “saved resume…” hard-gate copy.

**Run**
```bash
cd src/ui/frontend && npm run test:component -- --run \
  ../../../tests/component/frontend/components/test_IntakePreamblePanel.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

**Bible shasums** (`origin/sub/AST-952/AST-1017-mechanical-intake-ui`)
- `docs/test-bible/frontend/pages.md` — `e968364f7a6cc6857196c6bff0b9261ec5e85ac3`
- `docs/test-bible/frontend/components.md` — `44afcb61c8c620542da683bd8a0937c0f83b5df5`

#### betty — 2026-07-30T01:56:29.285Z
## QA test manifest — AST-1017

`origin/sub/AST-952/AST-1017-mechanical-intake-ui` @ `41777892` (`merge-tests(AST-1017): origin/tests 375257945eb0159d6f1b4af4a16c0f86d7d8de0f`)

### Manifest

1. `tests/component/frontend/components/test_IntakePreamblePanel.test.tsx` — `IntakePreamblePanel (AST-1017)` (Intro, skip-filled Continue, Valid→PUT, Try Again, Escalate)
2. `tests/component/frontend/pages/test_CandidateIntake.test.tsx` — `CandidateIntake page` (§6c confirm→preamble Modal; no Profile resume hard-gate; Start Over→preamble; Valid handoff→Estelle)

### Obsolete / revised

- Profile resume hard-gate toast before Start Intake — removed; missing resume opens preamble
- Start Over → Estelle before mechanical preamble — now opens preamble first

### Run

```bash
cd src/ui/frontend && npx vitest run \
  ../../../../tests/component/frontend/components/test_IntakePreamblePanel.test.tsx \
  ../../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

### Bible shasums (`origin/sub/…` tip, sha256)

- `docs/test-bible/frontend/pages.md` — `157acf7a3b33af5a0d070dbf60338df10ef445d6def02d5863a215242c30ba3e`
- `docs/test-bible/frontend/components.md` — `7eb63e08456911688932f9ef149669e13b2945c8ace03884755dd174603dac3a`

#### joan — 2026-07-30T01:37:21.893Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1017
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 three blobs + name columns | N/A — boundary (AST-1014) |
| AC2 Ruth Valid/Try Again/Escalate agent_task | N/A — boundary (AST-1015); UI consumes POST validate only |
| AC3 PREAMBLE_CONFIG owns script/Intro/try-copy | N/A — boundary (AST-1016); UI reads via `/api/ui_config` |
| AC4 mechanical preamble UI; Valid persists; calls Ruth | Stages 1–2 (panel + CandidateIntake wiring); Valid-only PUT |
| AC5 hopes/interests/concerns exist; Estelle confirm not in epic | Stage 2 §8 — no editors; confirm left to AST-953; fields via AST-1014 |
| AC6 contact+context ready for AST-953 after Valid sources | Stage 1 `onComplete` materials + Stage 2 Estelle handoff; contact home is AST-1014 |
| AC7 Profile/Admin identity/pronoun editing | N/A — boundary (AST-1014) |
| AC8 backend debug=True found/recorded | N/A — boundary (backend siblings); UI explicitly exempt |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 IntakePreamblePanel | Purpose/Functional scope “Mechanical front door (UI)”; child AC4 |
| Stage 2 CandidateIntake wire | Functional scope handoff into Estelle; child AC4/AC6; seamless Intro presentation from AC3 via config |
| Stage 3 App.css Estelle-consistent | Parent Functional scope Intro/step copy Estelle-consistent presentation |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work in this UI plan |
| orch.git.commit-vocabulary | conforms | Execution contract uses plan()/code() publish vocabulary on sub ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/…; no reverse-flow proposed |
| orch.git.ftr-sub-topology | conforms | Child publish ref matches parent Git table sub topology |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe; build waits for 1015 on ftr |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force in plan |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-952/AST-1017-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-952 assumed |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions documented; block→parent comment if validate missing |
| orch.pipeline.plan-is-bible | conforms | Binding execution contract + Files Changed table present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope; no cross-project queue invention |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/ edits; Betty after Code Complete |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build; Chuckles orchestration only |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits proposed |
| astral.config.config-source-of-truth | conforms | Steps/Intro/prompts/targets from PREAMBLE_CONFIG via ui_config; no local script |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features; Betty excluded |
| astral.layers.import-direction | conforms | React → API only; no core/data imports |
| astral.layers.ui-config-driven-business-logic | conforms | UI executes config script; does not own sequence/copy/validation |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Consumes existing auth’d validate/PUT/ui_config; no new open routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work; UI uses Toast on API errors |
| astral.standards.debug-contract-gated | conforms | UI has no debug-logging requirement; backend siblings own contract |
| astral.standards.dry-and-focused-functions | conforms | Single panel for all steps; reuses Modal/api/Toast/intake classes |
| astral.standards.in-scope-only | conforms | Files Changed limited to three UI files; siblings/AST-953 excluded |
| astral.standards.logging-via-utils | conforms | No Python logging path; frontend Toast only |
| astral.standards.no-cross-contamination | conforms | Stays in frontend UI surface |
| astral.standards.no-hardcoded-sets | conforms | Script from config; PREAMBLE_OUTCOMES is single UI mirror of AST-1015 closed set |
| astral.standards.public-then-helpers | conforms | Component structure plan is focused; no scattered public API invention |
| astral.ui.frontend-file-placement | conforms | Component in components/; page CandidateIntake.tsx; styles App.css |
| astral.ui.naming-conventions | conforms | PascalCase IntakePreamblePanel; snake_case API paths unchanged |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker/config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

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

## Findings

None fix-now.

**discuss (non-blocking):** Stage 1 skip-non-empty Decision means Profile-entered `raw_*` bypasses Ruth. Acceptable for this child’s gap-fill front door; if Archie later wants every mechanical source Ruth-Valid before Topic Menu, that is a product follow-up — not a plan defect vs AST-1017 boundaries.

**acceptable:** Self-assessment Scope Single-Component / Conf high / Risk Medium matches the plan; Medium risk mitigation (Valid-only PUT; Escalate ≠ Valid; stop if validate route missing) is specific.

**R6 checklist:** Definition fidelity pass (mechanical UI only). Layer/import pass. Config consume-only pass. File placement pass. No batch/state-machine/do_task from React. DRY pass. No sibling scope creep.

context_tokens≈52000

— Joan

#### katherine — 2026-07-30T01:33:00.671Z
Plan published on `origin/sub/AST-952/AST-1017-mechanical-intake-ui` @ `130a929b`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-952/AST-1017-mechanical-intake-ui/docs/features/candidate/ast-1017-mechanical-intake-ui.md

**Self-assessment**
- **Scope:** Single-Component — React intake UI only (`IntakePreamblePanel` + `CandidateIntake` wiring + CSS); consumes AST-1014/1015/1016 APIs; no core/data/config authorship.
- **Conf:** high — sibling contracts are shipped (1014/1016 on ftr; 1015 on sub UT); existing intake modal, `api` client, and ui_config preamble expose are known; Valid/Try Again/Escalate handling is explicit.
- **Risk:** Medium — a wrong Valid gate would persist bad `raw_*` into the library Topic Menu reads; mitigated by requiring `success && outcome === "Valid"` before PUT and never treating Escalate as Valid. Build blocked if AST-1015 is not yet merged to ftr.

**Approach:** Config-driven preamble phase in a wide Modal before Estelle chat; skip steps whose library fields are already non-empty; Intro always shown when the preamble panel mounts; persist via PUT `/data` only after Ruth Valid.

---

# AST-1017 — Mechanical intake front door UI

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1017/mechanical-intake-front-door-ui-candidate-profile-preamble-to-intake  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1017-mechanical-intake-ui`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Ship the **mechanical preamble front door** on Candidate Intake: read `PREAMBLE_CONFIG` from `GET /api/ui_config`, show **Intro** in Estelle-consistent presentation, walk ordered steps (resume → LinkedIn → sample cover letter), call Ruth validation (`POST …/preamble/validate`), persist **only** on `outcome === "Valid"` into the AST-1014 context library fields, then hand off into the existing Estelle `IntakeChatModal` session flow. Familiar seamless feel — same wide modal chrome and `.intake-msg--assistant` styling as Estelle chat.

Boundaries (do **not** implement): contact/context/artifacts library schema or remaps (AST-1014), Ruth agent_task / `validate_preamble_answer` core (AST-1015), `PREAMBLE_CONFIG` ownership or copy edits (AST-1016), Topic Menu / Estelle “Anything here you would change?” confirm (AST-953), hopes/interests/concerns editors, candidate state-machine changes, new agent personas, inlined validation logic in React.

**Prerequisite at build:** AST-1014 + AST-1016 are on `origin/ftr/AST-952-candidate-profile-preamble-to-intake`. AST-1015 is User Testing on `origin/sub/AST-952/AST-1015-preamble-validation-ruth` — **Chuckles `merge-child` must land it on ftr before Stage 1 can call validate live**. If `POST /api/candidates/<id>/preamble/validate` is missing after merging ftr, **stop** and comment on parent AST-952 (do not stub validation in the UI).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/IntakePreamblePanel.tsx` | New: Intro + ordered mechanical steps; Ruth validate; PUT library on Valid only | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | New-intake → preamble phase → Estelle modal; remove Profile-only resume hard-gate when preamble can collect | ui |
| `src/ui/frontend/src/App.css` | Preamble panel styles reusing intake assistant/user message look; step composer | ui |

No Python/config/agent_task changes. No `IntakeChatModal.tsx` behavior change beyond receiving materials after preamble (same props). No `tests/` edits (Betty owns tests after Code Complete).

---

## Sibling contracts (read-only — do not re-implement)

### AST-1016 — `PREAMBLE_CONFIG` via ui_config

`GET /api/ui_config` (system blueprint, `@require_auth`) returns:

```json
{
  "preamble": {
    "intro": "<string>",
    "validation_task_key": "preamble_validate_response",
    "steps": [
      {
        "id": "raw_resume",
        "order": 1,
        "prompt_1st_try": "<string>",
        "prompt_2nd_try": "<string>",
        "target": { "blob": "context", "field": "raw_resume" },
        "validation_question": "<string>"
      }
    ]
  }
}
```

Three steps in order: `raw_resume` → `raw_profile` → `raw_sample`. UI must **not** hardcode step ids, prompts, or field names — iterate `preamble.steps` sorted by `order`.

### AST-1015 — Ruth validate API

```
POST /api/candidates/<candidate_id>/preamble/validate
Body: { "question": "<step.validation_question>", "answer": "<paste>", "step_index": <step.order>, "step_total": <steps.length> }
Response 200: { "success": bool, "outcome": "Valid"|"Try Again"|"Escalate"|null, "error": ..., "batch_id": ... }
```

- Advance / persist **only** when `success === true` and `outcome === "Valid"`.
- `Try Again` / `Escalate` / `success === false` → do **not** write library fields; do **not** advance.
- Do **not** call `do_task` or invent a client-side checker.

### AST-1014 — persist home

```
PUT /api/candidates/<candidate_id>/data
Body: { "context": { "<field>": "<answer>" } }
```

Deep-merge; one field per Valid step. After all steps done (or skipped), materials for Estelle session POST keep AST-558 call-boundary names:

| Session POST body key | Library field |
|-----------------------|---------------|
| `starting_resume_text` | `context.raw_resume` |
| `linkedin_profile_text` | `context.raw_profile` |
| `sample_cover_text` | `context.raw_sample` |

---

## Stage 1: `IntakePreamblePanel` — config-driven mechanical steps

**Done when:** A new component renders Intro + one step at a time from `preamble` config, calls Ruth validate, PUTs the target field only on Valid, handles Try Again / Escalate / transport errors without advancing, and invokes `onComplete(materials)` with the three session-body keys populated from the latest library values. `tsc` passes. Not yet wired as the Intake page gate.

1. Create `src/ui/frontend/src/components/IntakePreamblePanel.tsx` with props:

```ts
export type PreambleMaterials = {
  starting_resume_text: string
  sample_cover_text: string
  linkedin_profile_text: string
}

export type IntakePreamblePanelProps = {
  candidateId: string
  /** Current context raw_* (and legacy aliases already resolved by parent). */
  initialMaterials: PreambleMaterials
  onComplete: (materials: PreambleMaterials) => void
  onCancel: () => void
}
```

2. On mount, `GET /api/ui_config` and read `preamble`. If missing/malformed (`!intro` or `!Array.isArray(steps)` or empty steps), toast error and call `onCancel` — do not invent a local fallback script.

3. Build `pendingSteps`: sort `preamble.steps` by `order` ascending; **include** a step when the corresponding material string is empty after trim:

| `target.field` | material key |
|----------------|--------------|
| `raw_resume` | `starting_resume_text` |
| `raw_profile` | `linkedin_profile_text` |
| `raw_sample` | `sample_cover_text` |

⚠️ **Decision — skip non-empty targets:** If Profile (or a prior Valid preamble) already stored a non-empty value for that field, **skip** the step. Do not re-validate Profile-entered text in this ticket. Mechanical UI fills **gaps** and is the front door when fields are empty.

⚠️ **Decision — Intro always on this panel:** When the panel mounts for a new-intake / Start-Over path, always show `preamble.intro` as an assistant-styled bubble (`.intake-msg.intake-msg--assistant`) before the first pending prompt — even if `pendingSteps` is empty. If `pendingSteps` is empty after Intro, show a single **Continue** button that calls `onComplete(initialMaterials)`.

4. Layout inside the existing wide Modal body pattern (parent supplies Modal or this panel is placed where materials used to live — Stage 2 decides host; this component owns inner chrome only):

   - Thread region: Intro bubble; current step prompt as assistant bubble (`prompt_1st_try` on first attempt for that step, `prompt_2nd_try` after any Try Again on that step).
   - Composer: one `<textarea className="intake-preamble-input">` + **Submit** button (disabled when empty/busy).
   - Footer: **Cancel** → `onCancel`.

5. On Submit for step at index `i` in `pendingSteps` (1-based display index for humans is fine; Ruth `step_index` / `step_total` **must** be `step.order` and `preamble.steps.length` — full script length, not pending-only):

   a. `POST /api/candidates/${candidateId}/preamble/validate` with  
      `{ question: step.validation_question, answer: draft, step_index: step.order, step_total: preamble.steps.length }`.
   b. If HTTP not OK → toast error from body; stay on step.
   c. Parse JSON. If `!success` or `outcome` not in the closed set → toast `error` or “Validation failed”; stay.
   d. `outcome === "Try Again"` → set that step’s attempt to 2nd-try; replace visible prompt with `prompt_2nd_try`; clear draft; stay. Do **not** PUT.
   e. `outcome === "Escalate"` → toast: `This answer needs human review. Try a clearer paste, or edit this field on Profile and return to Intake.`; stay. Do **not** PUT. Do **not** treat Escalate as Valid.
   f. `outcome === "Valid"` → `PUT /api/candidates/${candidateId}/data` with  
      `{ context: { [step.target.field]: draft.trim() } }`  
      (`Content-Type: application/json`). On PUT failure → toast; stay (do not advance — Valid was judged but not recorded). On PUT OK → update local materials map for that field; advance to next pending step or `onComplete` with full materials.

6. Do **not** read or display `validation_task_key` in the UI beyond trusting the validate endpoint. Do **not** hardcode Valid/Try Again/Escalate string sets in multiple places — compare against the three literal strings in one local const `PREAMBLE_OUTCOMES` at the top of the file (UI mirror of the closed set; source of truth for outcomes remains AST-1015 config).

7. Reuse `api` from `../lib/api`, `Toast` patterns from `IntakeChatModal`. No new npm deps.

---

## Stage 2: Wire `CandidateIntake` — preamble before Estelle

**Done when:** New intake / Start Over opens the wide intake Modal in **preamble** phase first (Intro + mechanical steps); after `onComplete`, the same Modal (or immediate handoff) runs existing `IntakeChatModal` auto-start with persisted materials. Continue-on-active-session skips preamble. The old hard redirect “Add Original Resume Text on Profile before starting Intake” is removed when the preamble path can collect `raw_resume`. Profile remains available for edits; hopes/interests/concerns editors are **not** added.

1. In `CandidateIntake.tsx`, introduce phase state:

```ts
type IntakePhase = "idle" | "preamble" | "chat"
```

2. **Remove** the early return that toasts and `goProfile()` when `!loaded.starting_resume_text.trim()`. Instead keep loading materials (including empty strings) and proceed to confirm / resume dialog as today.

3. After user confirms **Start Intake** (no active session) **or** completes **Start Over** archive path:
   - Set `materials` from loaded/empty values.
   - Set phase `"preamble"` and open the wide Modal host (see step 5).
   - Do **not** open `IntakeChatModal` yet.

4. **Continue** on active session: set phase `"chat"`, open `IntakeChatModal` with current materials — **skip preamble** (session already past the front door).

5. Host chrome — pick **one** structure and implement exactly:

⚠️ **Decision — single wide Modal, two phases:** Reuse one `Modal open title="Candidate Intake" size="wide"`. When `phase === "preamble"`, render `IntakePreamblePanel` inside it. When `phase === "chat"`, render the **body** of today’s Estelle chat by either (a) extracting chat body from `IntakeChatModal` — **forbidden** (too much churn), or (b) closing preamble and mounting existing `IntakeChatModal` with `open autoStart` (and `freshStart` when Start Over). **Choose (b):** on preamble `onComplete`, set materials from callback, set `phase` to `"chat"`, mount `<IntakeChatModal … materials={materials} autoStart freshStart={…} />` as today. On preamble `onCancel`, `goProfile()`.

6. `IntakePreamblePanel` may render inside a lightweight wrapper Modal in the page when `phase === "preamble"`:

```tsx
{phase === "preamble" && (
  <Modal open onClose={goProfile} title="Candidate Intake" size="wide">
    <IntakePreamblePanel
      candidateId={selectedId}
      initialMaterials={materials}
      onComplete={handlePreambleComplete}
      onCancel={goProfile}
    />
  </Modal>
)}
{phase === "chat" && (
  <IntakeChatModal … />
)}
```

7. `handlePreambleComplete(m)`: `setMaterials(m)`; `setPhase("chat")`. Ensure `starting_resume_text` is non-empty before chat — if still empty after preamble (user cancelled mid-flight should not reach here; if Valid path somehow skipped resume), toast and `goProfile()` rather than POST session without resume.

8. Do **not** edit `NAV_CONFIG`, routes, or Estelle session/turn/build endpoints. Do **not** add hopes/interests/concerns fields to this UI (AC5: fields exist via AST-1014; confirm UI is AST-953).

---

## Stage 3: CSS — Estelle-consistent preamble presentation

**Done when:** Intro and step prompts visually match assistant bubbles in the intake thread; preamble composer aligns with existing intake composer spacing; no new global theme.

1. In `src/ui/frontend/src/App.css` under the existing `/* ---- Intake chat modal ---- */` section, add:

   - `.intake-preamble-panel` — column flex, gap matching `.intake-modal-body`
   - `.intake-preamble-thread` — reuse `.intake-thread` rules (or compose both classes in JSX: `className="intake-thread intake-preamble-thread"`)
   - `.intake-preamble-input` — same box model as `.intake-composer-input` / former `.intake-materials-field` min-height ~4rem
   - `.intake-preamble-actions` — footer row for Submit / Cancel matching `.intake-actions`

2. Prefer **reusing** `.intake-msg`, `.intake-msg--assistant`, `.intake-msg--user` over new bubble colors. Do not introduce a second visual language for Intro.

3. Run `cd src/ui/frontend && npx tsc -b --noEmit` after Stages 1–3. Fix only type errors in files listed in Files Changed.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the Files Changed table.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue (AST-952), and waits.**
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-952/AST-1017-mechanical-intake-ui`, then proceeds.

Blocking comment format (parent AST-952):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — React intake UI only (`IntakePreamblePanel` + `CandidateIntake` wiring + CSS). Consumes AST-1014/1015/1016 APIs; no core/data/config authorship.

**Conf:** high — sibling contracts are shipped (1014/1016 on ftr; 1015 on sub UT); existing intake modal, `api` client, and ui_config preamble expose are known; outcome handling rules are explicit in AST-1015.

**Risk:** Medium — wrong Valid gate would persist bad raw_* into the library that Topic Menu (AST-953) reads; mitigated by requiring `success && outcome === "Valid"` before PUT and never treating Escalate as Valid. Build blocked if AST-1015 is not yet on ftr.

---

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | One panel for all steps; reuse Modal/`api`/Toast/intake message classes; no duplicated step hardcodes |
| §1.4 / §2.1 / `astral.config.config-source-of-truth` | Step order, prompts, targets, Intro from `PREAMBLE_CONFIG` via ui_config only |
| §3.2 / `astral.layers.ui-config-driven-business-logic` | UI executes config; does not own script or validation |
| §3.3 import-direction | Frontend → API only; no core/data imports from React |
| §1.5.1 | UI has no debug-logging requirement (backend only) |
| §3.5 naming / file placement | PascalCase component in `components/`; page stays `CandidateIntake.tsx`; CSS in `App.css` |
| §2.6 state machine | No candidate state transitions |
| New agents | Forbidden — Ruth via AST-1015 API only |

---

## Review

**Publish ref:** `sub/AST-952/AST-1017-mechanical-intake-ui`  
**Build tip:** `54ed55439c794c55c9b26796f6a87102598adfe3`

### Stages delivered

1. `IntakePreamblePanel` — loads `preamble` from `GET /api/ui_config`; Intro + ordered gap-fill steps; Ruth `POST …/preamble/validate`; PUT `context.<field>` only on Valid; Try Again / Escalate do not advance.
2. `CandidateIntake` — new-intake / Start Over → preamble Modal → Estelle `IntakeChatModal`; Continue-on-active skips preamble; Profile resume hard-gate removed.
3. `App.css` — Estelle-consistent preamble panel / input / actions.

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Tip reviewed:** `417778929d12a8c8bf4ba8fbe4dc3ec1f14f6d16` (`origin/sub/AST-952/AST-1017-mechanical-intake-ui` vs `origin/dev`)
**Overall:** DISCUSS

#### What’s solid
- Stages 1–3 match plan: config-driven steps from `/api/ui_config`; Ruth validate before PUT; Valid-only persist; Escalate ≠ Valid; Continue-on-active skips preamble; Profile resume hard-gate removed.
- File placement / naming / import-direction clean (React → API only). AST-1017 `code` commit is exactly the three planned UI files.

#### Issues
1. **discuss** — C4 stragglers: Joan excluded statutes that the three-dot tip scores in-scope because tip↔`origin/dev` have diverged (425-path XOR incl. siblings/other epics). Listed in Linear comment; all **conform** on tip; no AST-1017 product fix.

#### Notes
Joan plan-rubric APPROVED. Tip and `origin/dev` report multiple merge bases — product judgment focused on AST-1017 delta; full-set sweep still vs three-dot.

## Resolution

**2026-07-30** — `resolve(AST-1017): — clean`

1. **fix-now** — none (Radia Overall DISCUSS; recommended proceed).
2. **discuss / C4 stragglers** — acknowledged; topology-only (tip↔`origin/dev` XOR). Statutes already **conform**; no AST-1017 product change.
3. **advisory / Profile skip Ruth** — acknowledged as product policy from plan Decision; not a code defect for this child.
