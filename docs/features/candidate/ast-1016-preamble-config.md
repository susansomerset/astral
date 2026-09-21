<!-- linear-archive: AST-1016 archived 2026-08-07 -->

## Linear archive (AST-1016)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1016/preamble-config-preamble-script-candidate-profile-preamble-to-intake  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-952 — Candidate Profile Preamble to Intake  
**Blocked by / blocks / related:** parent: AST-952; blocks: AST-1017

### Description

## What this implements

Add **PREAMBLE_CONFIG** in product config: step sequence, target blob/field names, Archie-provided **1st Try** / **2nd Try** prompt text, and **Intro** text for every new intake (Estelle-consistent presentation).

## Acceptance criteria

3. PREAMBLE_CONFIG defines sequence, target fields, Intro, and 1st/2nd Try copy; Intro appears at new-intake start in Estelle-consistent presentation.

## Boundaries

Does **not** own library persistence (AST-1014), Ruth validation (#2), or the intake UI (#4) — only the config script those consume.

## Notes for planning

After AST-1014. Archie will supply Intro / 1st Try / 2nd Try copy — placeholders ok until she provides final text. Config as source of truth (§2.1).

## Git branch (authoritative)

`sub/AST-952/<this-id>-preamble-config`. Publish to `origin/<publish-ref>` only.

### Comments

#### radia — 2026-07-28T19:09:17.856Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1016
**Publish ref:** `sub/AST-952/AST-1016-preamble-config` @ `064f9b04fe2cece67c903db4b78889770b2f797c` (product tip `2c0cb3f2`; docs append `064f9b04`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1016)` from Betty tip `302d78a0` |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocab on publish-ref |
| orch.git.flow-direction-inviolable | universal | conforms | Sub tip ahead of origin/dev; no reverse-flow |
| orch.git.ftr-sub-topology | universal | conforms | Child on `sub/AST-952/AST-1016-preamble-config` |
| orch.git.merge-on-checkout | universal | conforms | Tip includes merge(origin/dev) before code |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | Named sub/ only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-952 |
| orch.git.three-permanent-branches | universal | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Archie placeholders explicit; no open product blocker |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match shipped PREAMBLE_CONFIG + ui_config expose |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Candidate child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible only in Betty test/merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer code = config+api_system only |
| astral.agent.confidence-bounds | scoped | conforms | Confidence math untouched |
| astral.agent.do-task-delegation | scoped | conforms | No new AI path in AST-1016 delta |
| astral.agent.grade-vector-validation | scoped | conforms | No graded-task changes |
| astral.batch.batch-id-first | scoped | conforms | No claim API changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id work |
| astral.batch.claim-process-release | scoped | conforms | No batch claim/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_responses changes |
| astral.config.config-source-of-truth | scoped | conforms | PREAMBLE_CONFIG owns sequence/copy/targets/task_key |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Literals only; no os.environ |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/** / scripts/spikes/** miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under docs/features/; not a spike dump |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file ast-1016-preamble-config.md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits exclude src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commit has no tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O in AST-1016 delta |
| astral.layers.import-direction | scoped | conforms | ui_system → utils only for preamble |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths scripts miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Expose config; no React rules added |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Consult untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | ui_config keeps @require_auth |
| astral.standards.database-header-inventory | scoped | conforms | No new table misuse; header already updated on ancestor |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer touch in AST-1016 delta |
| astral.standards.debug-contract-gated | scoped | conforms | AST-1016 touches no debug= surfaces |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single config block; thin jsonify expose |
| astral.standards.in-scope-only | scoped | conforms | AST-1016 code = config.py + api_system.py only |
| astral.standards.logging-via-utils | scoped | conforms | No new logging paths |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in utils + ui api |
| astral.standards.no-hardcoded-sets | scoped | conforms | Steps/targets in config; asserts vs library keys |
| astral.standards.public-then-helpers | scoped | conforms | No conflicting layout |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data |
| astral.state.core-decides-transitions | scoped | conforms | No transition decisions |
| astral.state.job-prior-states-enforced | scoped | conforms | Job prior_states untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No batch daisy-chain |
| astral.ui.frontend-file-placement | scoped | conforms | AST-1016 code does not edit frontend |
| astral.ui.naming-conventions | scoped | conforms | Extends existing /api/ui_config |
| astral.ui.single-gunicorn-worker | scoped | conforms | Worker count untouched |

## Pattern conformance

none cited

## Plan adherence

Stages 1–2 match the shipped delta: `PREAMBLE_CONFIG` after `CANDIDATE_LIBRARY_CONFIG` with planned asserts; `preamble` on authenticated `ui_config`. Self-Assessment Single-Component / high / Medium matches. Intro *render* correctly deferred to AST-1017 (no CandidateIntake chrome in `code(AST-1016)`). Ancestor AST-1014 resolve already on tip.

## Findings

### discuss
1. **C4 stragglers** — Joan excluded at plan time, but three-dot tip vs `origin/dev` scores in-scope (tip carries resolved AST-1014 + Betty tests): `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.standards.database-header-inventory`, `astral.state.core-decides-transitions`, `astral.state.no-daisy-chain-in-run`, `astral.ui.frontend-file-placement`. All **conform** on tip; no product fix required for AST-1016.

### advisory
- Plan text says `/api/system/ui_config`; live route is `/api/ui_config` (system blueprint) — implementation correctly extends the existing endpoint.

## What’s solid

Config contract + asserts + ui_config expose are tight and boundary-clean.

## Recommended actions

No fix-now. Engineer may proceed via resolve-child / User Testing; straggler discuss is topology-only.

## Notes

Joan plan-rubric verdict attached (APPROVED). Docs append on plan file @ `064f9b04`.

context_tokens≈72000

#### betty — 2026-07-28T19:04:34.891Z
## QA test manifest

Publish: `origin/sub/AST-952/AST-1016-preamble-config` @ `2c0cb3f2` (`merge-tests(AST-1016): origin/tests 302d78a0`)

1. `tests/component/utils/test_config.py::TestAst1016PreambleConfig` — PREAMBLE_CONFIG intro, `validation_task_key`, ordered steps → `context.raw_resume` / `raw_profile` / `raw_sample`
2. `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_preamble_config` — `GET /api/ui_config` exposes `preamble` from PREAMBLE_CONFIG

Broken / obsolete: none for this tip (config-only + ui_config expose; Intro UI = AST-1017).

Bible shasums on publish tip:
- `docs/test-bible/utils/config.md` `7a6ed88867be19040464fd0097ff1b5e62b73286`
- `docs/test-bible/ui/api/api_system.md` `fdbb90e2b2fdde692ee68b4aaf71f2bac50fdd71`

Run on epic worktree after merge-on-checkout of the publish tip.

#### joan — 2026-07-28T18:11:48.776Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1016
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 library + columns | N/A — boundary (AST-1014); plan consumes `CANDIDATE_LIBRARY_CONFIG` keys only |
| AC2 Ruth Valid/Try Again/Escalate | N/A — boundary (AST-1015); plan only names `validation_task_key` + per-step `validation_question` |
| AC3 PREAMBLE_CONFIG sequence/targets/Intro/1st–2nd Try; Intro appears Estelle-consistent | Stage 1 defines block; Stage 2 exposes via `ui_config`. **Intro render** N/A — boundary (AST-1017); Decision documents the split |
| AC4 mechanical UI | N/A — boundary (AST-1017); no frontend page edits |
| AC5 hopes/interests/concerns; Estelle confirm | N/A — Decision excludes those steps; confirm is AST-953 |
| AC6 handoff readiness | N/A — requires Valid persist via siblings |
| AC7 Profile/Admin | N/A — boundary (AST-1014) |
| AC8 debug contract on validation/write paths | N/A — this child touches neither validation nor library-write `debug=` surfaces |

### Child AC → plan stages

| Child AC | Stages |
|----------|--------|
| PREAMBLE_CONFIG defines sequence, targets, Intro, 1st/2nd Try | Stage 1 |
| Intro appears at new-intake start (Estelle-consistent) | Config + `ui_config` expose (Stage 2); render owned by AST-1017 per child Boundaries / Decision |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| 1 `PREAMBLE_CONFIG` + asserts vs library vocabulary | Functional scope PREAMBLE_CONFIG; parent child #3; §2.1 |
| 2 Serve `preamble` on `GET /api/system/ui_config` | Makes Intro/steps readable to AST-1017 without a new endpoint |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge path in this config-only plan |
| orch.git.commit-vocabulary | conforms | No forbidden git ops prescribed |
| orch.git.flow-direction-inviolable | conforms | Publish ref `sub/AST-952/AST-1016-preamble-config` |
| orch.git.ftr-sub-topology | conforms | Child `sub/` under parent `ftr/` |
| orch.git.merge-on-checkout | conforms | No skip of merge discipline |
| orch.git.no-cherry-pick-rebase-force | conforms | None planned |
| orch.git.no-dev-agent-branches | conforms | Named `sub/` only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic AST-952 worktree |
| orch.git.three-permanent-branches | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Archie placeholders explicit; no open product blocker |
| orch.pipeline.plan-is-bible | conforms | Two-stage bible for config + expose |
| orch.pipeline.project-scoped-queues | conforms | Astral Candidate child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate gate |
| orch.roles.archie-approves-statutes | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no `tests/` edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A to plan body |
| orch.roles.engineer-assignee-through-resolve | conforms | Joan does not reassign |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.config.config-source-of-truth | conforms | `PREAMBLE_CONFIG` owns sequence/copy/targets/task_key |
| astral.config.secrets-and-env-specific-from-environ | conforms | Literals only; no `os.environ` |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.standards.in-scope-only | conforms | Config + ui_config only; UI/Ruth/library excluded |
| astral.standards.no-cross-contamination | conforms | Stays in utils + ui api |
| astral.standards.dry-and-focused-functions | conforms | Single config block; thin jsonify expose |
| astral.standards.public-then-helpers | conforms | N/A shape; no conflicting layout |
| astral.standards.no-hardcoded-sets | conforms | Steps/targets in config; asserts vs library keys |
| astral.standards.logging-via-utils | conforms | No new logging paths |
| astral.standards.data-raises-caller-logs | conforms | No data-layer touch |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.standards.debug-contract-gated | conforms | No `debug=` surfaces touched |
| astral.layers.import-direction | conforms | ui → utils only |
| astral.layers.ui-config-driven-business-logic | conforms | Expose config; no React rules |
| astral.ui.naming-conventions | conforms | Existing snake_case `/api/system/ui_config` |
| astral.ui.single-gunicorn-worker | conforms | Does not change worker count |
| astral.git.betty-no-src-or-features | conforms | Engineer owns these paths |
| astral.agent.confidence-bounds | conforms | Confidence math untouched |
| astral.state.job-prior-states-enforced | conforms | Job prior_states untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Extends existing authenticated `ui_config`; no decorator removal |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.config.pass-threshold-vs-score-floor, astral.standards.in-scope-only, astral.standards.no-cross-contamination, astral.standards.dry-and-focused-functions, astral.standards.public-then-helpers, astral.standards.no-hardcoded-sets, astral.standards.logging-via-utils, astral.standards.data-raises-caller-logs, astral.standards.utils-data-late-import-only, astral.standards.debug-contract-gated, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker, astral.git.betty-no-src-or-features, astral.agent.confidence-bounds, astral.state.job-prior-states-enforced, astral.patterns.require-auth-on-protected-endpoints

**Excluded:**
- astral.agent.do-task-delegation — layers/paths miss (core)
- astral.agent.grade-vector-validation — layers/paths miss (core)
- astral.batch.batch-id-first — layers/paths miss (core/data)
- astral.batch.batch-id-format — layers/paths miss (core/data)
- astral.batch.claim-process-release — layers/paths miss (core/data)
- astral.batch.entity-agent-responses-latest-only — layers/paths miss (core/data)
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss (docs not in Files Changed table)
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.state.core-decides-transitions — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss
- astral.ui.frontend-file-placement — paths `src/ui/frontend/**` miss

## Findings

### discuss
1. **Parent/child AC3 “Intro appears…”** — Plan correctly splits **string + ui_config expose** (this child) vs **render at new-intake start** (AST-1017) per Boundaries. Build must not quietly add `CandidateIntake.tsx` work here; AST-1017 must consume `preamble.intro`.
2. **`validation_question` + `validation_task_key`** — Slightly past the parent PREAMBLE_CONFIG bullet’s listed fields, but they are the right consumer contract for AST-1015/1017. Keep AST-1015 registering that exact `task_key`; do not invent the agent_task row here.

### acceptable
- Three-step resume → LinkedIn → sample minimum matches parent brief; excluding contact/name and hopes/interests/concerns steps is correct.
- Archie `[PLACEHOLDER — Archie]` strings are allowed by child Notes; finals are string swaps only.

**Self-assessment:** Single-Component / Conf high / Risk Medium — honest.

— Joan
context_tokens≈68000

#### ada — 2026-07-28T18:09:46.119Z
Plan: `docs/features/candidate/ast-1016-preamble-config.md`

https://github.com/susansomerset/astral/blob/sub/AST-952/AST-1016-preamble-config/docs/features/candidate/ast-1016-preamble-config.md

**Self-Assessment**
- **Scope:** `Single-Component` — `PREAMBLE_CONFIG` in `config.py` plus `preamble` on existing `GET /api/system/ui_config`; no library, Ruth task, or intake UI work.
- **Conf:** `high` — same config-block pattern as `CANDIDATE_LIBRARY_CONFIG` / `INTAKE_CONFIG`; step targets are shipped AST-1014 `context.raw_*` keys; Archie copy is placeholder-tagged.
- **Risk:** `Medium` — wrong target or `validation_task_key` would miswire AST-1017/1015; asserts + sibling contracts mitigate; Intro *render* stays AST-1017.

Two stages: (1) `PREAMBLE_CONFIG` (intro, three steps resume→LinkedIn→sample, `preamble_validate_response` task_key, asserts), (2) expose on `ui_config`.

Publish ref `sub/AST-952/AST-1016-preamble-config` @ `cbee4361`.

---

# AST-1016 — PREAMBLE_CONFIG preamble script

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1016/preamble-config-preamble-script-candidate-profile-preamble-to-intake  
**Parent:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  

**Publish ref (origin):** `sub/AST-952/AST-1016-preamble-config`  
**Parent integration ref:** `ftr/AST-952-candidate-profile-preamble-to-intake`

Ship **`PREAMBLE_CONFIG`** as the product-config source of truth for the mechanical intake preamble: ordered steps, each step’s target library field (`context.raw_*`), Archie-owned **Intro** / **1st Try** / **2nd Try** copy (placeholders until she supplies finals), and the Ruth validation task_key string consumers must call. Sibling **AST-1017** renders Intro and drives the step UI; sibling **AST-1015** owns the Ruth agent_task implementation.

Boundaries (do **not** implement): library persistence / remaps (AST-1014 — already on ftr), Ruth Valid/Try Again/Escalate agent_task body (AST-1015), mechanical intake front-door UI / Estelle chat chrome (AST-1017), Estelle confirm (AST-953), candidate state-machine vocabulary changes.

⚠️ **Decision — Parent AC3 “Intro appears…”:** This child owns the **Intro string** (and step copy) in config and makes the block readable to the UI via `/api/ui_config`. **Rendering** Intro at new-intake start in Estelle-consistent presentation is **AST-1017**. Do not edit `CandidateIntake.tsx` here.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `PREAMBLE_CONFIG` after `CANDIDATE_LIBRARY_CONFIG` (intro, steps, validation_task_key); assert step targets ⊆ library vocabulary | utils |
| `src/ui/api/api_system.py` | Include a JSON-safe `preamble` object on `GET /api/ui_config` from `PREAMBLE_CONFIG` | ui |

No frontend page changes, no `TASK_CONFIG` / agent_task rows, no database migration, no `tests/` edits (Betty owns tests after Code Complete).

---

## Stage 1: `PREAMBLE_CONFIG` contract

**Done when:** `PREAMBLE_CONFIG` is importable from `src.utils.config` with Intro + three ordered mechanical steps targeting `context.raw_resume` / `context.raw_profile` / `context.raw_sample`, 1st/2nd Try strings (Archie placeholders), and a `validation_task_key` literal; module-level asserts fail loudly if a step target is outside `CANDIDATE_LIBRARY_CONFIG`.

1. In `src/utils/config.py`, immediately **after** `CANDIDATE_LIBRARY_CONFIG` (before `assert "PROSPECT" not in CANDIDATE_STATES`), add:

```python
# AST-1016: mechanical preamble script (Intro + steps). UI = AST-1017; Ruth task = AST-1015.
PREAMBLE_CONFIG = {
    "intro": (
        "[PLACEHOLDER — Archie] Before we start with Estelle, we'll collect three "
        "source materials: your latest resume, your LinkedIn profile, and a sample "
        "cover letter from a past application."
    ),
    # AST-1015 must register an agent_task with this exact task_key (Ruth / Little Brain).
    "validation_task_key": "preamble_validate_response",
    "steps": [
        {
            "id": "raw_resume",
            "order": 1,
            "prompt_1st_try": (
                "[PLACEHOLDER — Archie] Let's start with your existing/latest resume. "
                "Paste the full text (or upload content) so we can store it as your raw resume."
            ),
            "prompt_2nd_try": (
                "[PLACEHOLDER — Archie] That didn't look like resume text. Please paste "
                "your full resume again — include roles, dates, and education if you have them."
            ),
            "target": {"blob": "context", "field": "raw_resume"},
            "validation_question": (
                "Does this response look like a valid answer to: paste your resume text?"
            ),
        },
        {
            "id": "raw_profile",
            "order": 2,
            "prompt_1st_try": (
                "[PLACEHOLDER — Archie] Next, paste your LinkedIn profile content "
                "(About, Experience, Education — the text you'd want Estelle to read)."
            ),
            "prompt_2nd_try": (
                "[PLACEHOLDER — Archie] That didn't look like a LinkedIn profile. "
                "Paste the profile text again (not just the profile URL)."
            ),
            "target": {"blob": "context", "field": "raw_profile"},
            "validation_question": (
                "Does this response look like a valid answer to: paste your LinkedIn profile text?"
            ),
        },
        {
            "id": "raw_sample",
            "order": 3,
            "prompt_1st_try": (
                "[PLACEHOLDER — Archie] Finally, paste a sample cover letter from a past "
                "application so we can learn your writing style."
            ),
            "prompt_2nd_try": (
                "[PLACEHOLDER — Archie] That didn't look like a cover letter. "
                "Paste a full sample cover letter (greeting through sign-off) again."
            ),
            "target": {"blob": "context", "field": "raw_sample"},
            "validation_question": (
                "Does this response look like a valid answer to: paste a sample cover letter?"
            ),
        },
    ],
}
```

2. Still in `config.py`, add asserts immediately after the block (same style as neighboring candidate asserts):

   - `PREAMBLE_CONFIG["validation_task_key"]` is a non-empty `str`.
   - `PREAMBLE_CONFIG["intro"]` is a non-empty `str`.
   - `steps` is a non-empty `list`; each step has keys `id`, `order`, `prompt_1st_try`, `prompt_2nd_try`, `target`, `validation_question` (all required strings / dict as above).
   - Step `order` values are unique and equal to `1..len(steps)` when sorted.
   - For each step: `target["blob"] == "context"` and `target["field"]` is in `CANDIDATE_LIBRARY_CONFIG["context_keys"]`.
   - Step `id` equals `target["field"]` (stable id for UI progress keys).

⚠️ **Decision:** Minimum mechanical sequence is exactly the three parent-brief sources (resume → LinkedIn → sample). Do **not** add contact/name/pronoun steps here — those are Profile/Admin + library columns (AST-1014), not this preamble script. Do **not** add hopes/interests/concerns steps — Topic Menu / Estelle (AST-953).

⚠️ **Decision:** `validation_task_key` is `"preamble_validate_response"`. AST-1015 must create the Ruth agent_task under that exact key (or stop and comment on the parent if they need a different key — then update this constant in a follow-up on this ticket). Do not invent the agent_task row in this ticket.

⚠️ **Decision:** Archie copy is placeholder-tagged with `[PLACEHOLDER — Archie]` so final wording is a string swap only — no step/id/target changes when finals arrive.

3. If `config.py`’s top-of-file comment inventory lists named `*_CONFIG` blocks, add a one-line entry for `PREAMBLE_CONFIG` next to `CANDIDATE_LIBRARY_CONFIG` / `INTAKE_CONFIG`.

---

## Stage 2: Serve preamble to UI consumers

**Done when:** Authenticated `GET /api/ui_config` JSON includes a `preamble` key whose value mirrors `PREAMBLE_CONFIG` (intro, validation_task_key, steps); no other ui_config keys change; `CandidateIntake.tsx` and other frontend pages are untouched.

1. In `src/ui/api/api_system.py`, import `PREAMBLE_CONFIG` from `src.utils.config` (same import site as `UI_CONFIG` / `BUILD_CONFIG`).

2. In `ui_config()`, add `"preamble": PREAMBLE_CONFIG` to the jsonify dict alongside the existing `**UI_CONFIG` / `base_resume_accent_palette` keys.

⚠️ **Decision:** Serve under `/api/ui_config` (system blueprint) rather than a new blueprint route — AST-1017 already (or will) load ui_config for shared UI literals; one fetch gives Intro + steps. Do not add a dedicated `/api/preamble` endpoint.

3. Do **not** change `INTAKE_CONFIG`, session create/archive flows, or Estelle agent wiring in this ticket.

---

## Out of scope (explicit)

- Rendering Intro / step prompts in the intake page (AST-1017).
- Calling Ruth / interpreting Valid|Try Again|Escalate (AST-1015 + AST-1017).
- Writing `context.raw_*` via PUT (already library/API from AST-1014; UI persist path is AST-1017).
- Replacing placeholder Archie strings with finals unless Archie comments them on this ticket during build — if she does, Stage 1 strings only (same keys).

---

## Self-Assessment

**Scope:** `Single-Component` — one config block in `config.py` plus a one-key expose on existing `ui_config`; no core library, validation, or intake UI work.

**Conf:** `high` — mirrors `CANDIDATE_LIBRARY_CONFIG` / `INTAKE_CONFIG` patterns; targets are already-shipped AST-1014 context keys; placeholders are explicit.

**Risk:** `Medium` — wrong `target` or `validation_task_key` would make AST-1017 write/validate against the wrong homes; asserts + sibling contracts mitigate; Intro presentation AC half depends on AST-1017 consuming this block.

## Review

**Publish ref:** `sub/AST-952/AST-1016-preamble-config`  
**Build tip:** `927658d1bf3dfec1e097308ddcd15b27342f6c05`

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Tip reviewed:** `2c0cb3f2cdc18f728b6db9767c709496474def2c` (`origin/sub/AST-952/AST-1016-preamble-config` vs `origin/dev`)
**Overall:** DISCUSS

#### What’s solid
- `PREAMBLE_CONFIG` matches plan Stage 1 (intro, three `context.raw_*` steps, `preamble_validate_response`, asserts vs `CANDIDATE_LIBRARY_CONFIG`).
- Stage 2: `GET /api/ui_config` exposes `preamble` with `@require_auth` retained; no intake UI / Ruth / library churn in the AST-1016 `code` commit.
- Ancestor AST-1014 fix-nows already resolved on this tip (`api_admin` token view, PUT `debug=ui_llm_debug()`, agent lazy-import comment).

#### Issues
1. **discuss** — C4 stragglers: Joan excluded 16 statutes at plan time that the three-dot tip scores in-scope because the tip also carries resolved AST-1014 (+ Betty tests). Not product defects on the AST-1016 delta; statutes themselves **conform**.

#### Advisory
- Plan prose says `/api/ui_config`; live route is `/api/ui_config` (system blueprint) — implementation correctly extends the existing surface.

#### Notes
Joan plan-rubric verdict attached (APPROVED). No fix-now on AST-1016 deliverable.

## Resolution

**2026-07-28** — resolve-child vs `[code-rubric] revision=1` (DISCUSS)

1. **fix-now** — none.
2. **discuss / C4 stragglers** — acknowledged; topology-only (tip carries AST-1014 + Betty tests). Statutes already **conform**; no product change.
3. **advisory / route path** — plan prose corrected to live `GET /api/ui_config` (implementation already correct).
