<!-- linear-archive: AST-1005 archived 2026-08-05 -->

## Linear archive (AST-1005)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1005/uat-parse-validation-false-missing-candidate-name-after-job-array  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-994 — Parse resume json output is incomplete  
**Blocked by / blocks / related:** parent: AST-994

### Description

## What failed

On Session Resume Paste / craft-base parse UAT, experience jobs return correctly as an array, but the UI validation popup claims the response is missing `candidate_name` — even though the returned JSON includes `agent_payload.resume_structure.candidate_name` (e.g. `"Susan Somerset"`) alongside a well-formed `experience` job array.

Susan: “Did we miss updating the response validation logic?”

## Expected

A successful craft-base parse whose `resume_structure` includes `candidate_name` and the experience job array must pass response validation and not show a false “missing candidate_name” failure.

## Repro

1. Open Session Resume Paste (Admin) on staging/`dev`.
2. Paste a multi-job resume and run Parse (craft-base).
3. Observe experience jobs look correct in the payload.
4. Note validation popup claiming missing `candidate_name` while the JSON body still contains `resume_structure.candidate_name`.

## Parent AC (quoted inline)

> 1. After craft-base parse of a multi-job resume paste, Experience is an ordered list of jobs; each job exposes company, title, dates, location, and one accomplishments text block observable in the parse JSON (session parse response and/or Base Resume Content equivalent).

> Contract alignment (parent Functional scope): Task response contracts / structure expectations for craft-base and job-tailored Experience match the job-array shape so validation and downstream split/persist paths accept the new form without silently flattening it back to a single string.

## Diagnosis

* **Hypothesis:** Response validation / task contract still expects pre–job-array Experience (string or different shape), so schema/path checks fail after Experience became an array and surface a misleading `candidate_name` missing error even when that field is present.
* **Correct outcome:** Valid parse JSON with `candidate_name` + experience job array passes validation; user can accept/use the parse without a false-missing popup.
* **Wrong fix to avoid:** Swallowing validation errors; removing `candidate_name` checks; flattening Experience back to a single string; treating “no popup” alone as done without confirming AC #1 payload remains a real job array.
* **Related siblings / contracts:** AST-996 (craft-base job-array contract), AST-997 (job-tailored same shape), AST-998 (HTML builders) — validation must accept the shared job-array contract without breaking those paths.

## Boundaries

* This bug does **not** change: AST-993 richer role chrome; cover-letter HTML; inventing candidate fields; relaxing factual job metadata rules.
* "No more stacktrace / no more error" alone is **not** done — Parent AC + Correct outcome must hold.

### Comments

#### radia — 2026-07-28T15:29:31.061Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1005
**Publish ref:** `32c2338d` on `origin/sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name` (baseline `origin/dev`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| --- | --- | --- | --- |
| astral.agent.confidence-bounds | scoped | conforms | core touched; no graded confidence changes |
| astral.agent.do-task-delegation | scoped | conforms | craft-base normalize + schema validate path only |
| astral.agent.grade-vector-validation | scoped | conforms | no graded vectors |
| astral.batch.batch-id-first | scoped | conforms | no new batch APIs |
| astral.batch.batch-id-format | scoped | conforms | untouched |
| astral.batch.claim-process-release | scoped | conforms | no new claim pattern |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | untouched |
| astral.config.config-source-of-truth | scoped | conforms | no config literal/schema drift; required `candidate_name` kept |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | conforms | no repo-root `artifacts/` dump |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under `docs/features/**` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one combined plan/review file for AST-1005 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test`/`merge-tests` touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code(AST-1005)` has no tests/ |
| astral.layers.core-vs-external-bright-line | scoped | conforms | promote + schema harden stay in core |
| astral.layers.import-direction | scoped | conforms | core-only product edit |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no `scripts/**`) |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths miss (no `src/ui/**`) |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check changes |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult/render-verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss (no `src/ui/**`) |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer logging; validation errors still return |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (`src/data/**`) |
| astral.standards.debug-contract-gated | scoped | conforms | no new ungated debug |
| astral.standards.dry-and-focused-functions | scoped | conforms | shared `_promote` + dedicated object-field validator |
| astral.standards.in-scope-only | scoped | needs-discussion | tip includes AST-1001 bible README via merge-tests (see findings) |
| astral.standards.logging-via-utils | scoped | conforms | no new logging anti-patterns |
| astral.standards.no-cross-contamination | scoped | conforms | product layers clean; bible pollution is tests-line |
| astral.standards.no-hardcoded-sets | scoped | conforms | promote uses known section ids; schema unchanged |
| astral.standards.public-then-helpers | scoped | conforms | helpers near existing validate/flatten |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss (no `src/utils/**`) |
| astral.state.core-decides-transitions | scoped | conforms | no state machine |
| astral.state.job-prior-states-enforced | scoped | conforms | untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths miss |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip includes `merge-tests(AST-1005)` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` |
| orch.git.flow-direction-inviolable | universal | conforms | publish to child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-994/AST-1005-…` matches branch law |
| orch.git.merge-on-checkout | universal | conforms | no skip of merge procedure |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | work on ticket sub |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-994` |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis followed; no schema weaken |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match tip; wrong fixes rejected |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | assignee left untouched for resolve |
| orch.roles.pre-commit-path-bans | universal | conforms | role path bans respected |

## Pattern conformance

none cited

## Plan adherence

Stages 1–2 match: promote direct `resume_structure` known section ids (incl. job-array experience) before default wipe; `_validate_schema_object_fields` for list `items_schema` without envelope recurse; required `candidate_name` not loosened; experience remains list+items_schema. Self-Assessment Single-Component fits. Wrong fixes (toast suppress / flatten / drop required) not taken.

## Findings

### fix-now
(none)

### discuss
1. **Cross-ticket / in-scope tip hygiene** — three-dot vs `origin/dev` includes `docs(AST-1001): test bible — missing-thread skill policy docs-acceptance` (`docs/test-bible/README.md`) pulled through `merge-tests` from `origin/tests`. Not in AST-1005 Files Changed / UAT bug scope. Product `agent.py`/`candidate.py` fix is clean; scrub is tests-line / rollup hygiene (Chuckles/Betty), not a craft-base logic defect.

### advisory
(none)

## What’s solid

False-missing name fixed by promote-before-wipe; items_schema no longer misreads job objects as envelopes; AC #1 job-array shape preserved.

## Notes

no plan-rubric verdict attached — not a block. 56 active statutes checked.

context_tokens≈32000

#### betty — 2026-07-28T15:26:29.027Z
## QA test manifest — AST-1005

**Publish:** `origin/sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name` @ `236a7dd0` (`merge-tests(AST-1005): origin/tests f7e4d098`)

### Classification
1. **Existing coverage:** `TestAst517ResumeStructure` (normalize/inject/content-map promote); `TestAst996ExperienceJobArray` (job-array preserve); `TestResponseSchemaBranches` (schema type branches)
2. **Broken / obsolete (fixed this pass):** `TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema` — criteria fixture now includes required `code` under hardened `items_schema` object-field validation
3. **Gaps (new):** `TestAst1005FalseMissingCandidateName` (direct `resume_structure` key promote with/without sections; still-missing name); `TestAst1005ItemsSchemaObjectValidation` (path-prefixed item errors; valid job array; no envelope recurse on items)

### Manifest (test-child)

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst1005FalseMissingCandidateName tests/component/core/test_candidate.py::TestAst996ExperienceJobArray tests/component/core/test_candidate.py::TestAst517ResumeStructure tests/component/core/test_agent.py::TestAst1005ItemsSchemaObjectValidation tests/component/core/test_agent.py::TestResponseSchemaBranches -q`

**Pass:** narrowed pytest green (not zero-arg / branch-lock).

### Bible (publish tip)

| File | sha256 |
| --- | --- |
| `docs/test-bible/core/candidate.md` | `ba1fed14656b135f40151ccab045e0db8806cb48fee96ff5423223316f78d242` |
| `docs/test-bible/core/agent.md` | `1252824549e317dc251784e077bf4667851d8f65b524b3cd8e5f216f771d4851` |

#### ada — 2026-07-28T15:19:59.825Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name/docs/features/artifacts/ast-1005-uat-parse-validation-false-missing-candidate-name.md

**Scope:** Single-Component — craft-base normalize in `candidate.py` plus list-item schema validation in `agent.py`; no UI/config/builder changes.

**Conf:** high — reproduced false-missing when `candidate_name` is only under `resume_structure`; promote gap + sections-wipe order are explicit in current code.

**Risk:** Medium — validate path used by paste-resume; mitigated by known-id-only promote and skip-if-top-level-non-empty (existing `_promote` rules).

---

# UAT: parse validation false-missing candidate_name after job-array

**Linear:** [AST-1005](https://linear.app/astralcareermatch/issue/AST-1005/uat-parse-validation-false-missing-candidate-name-after-job-array)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name`

After AST-996/997 experience job-array contracts, Session Resume Paste craft-base validation can fail with `Missing required field 'candidate_name'` even when the name is present as `agent_payload.resume_structure.candidate_name` beside a well-formed experience job array. Admin surfaces that server error as a toast. Root cause (reproduced): `_flatten_craft_resume_section_strings` promotes from `resume_structure.content` and content-block nests, but **not** from direct keys on `resume_structure`; and when `sections` is missing, normalize replaces `resume_structure` with `default_resume_structure()` **after** flatten, wiping sibling section values before they can be lifted. Schema still requires top-level `candidate_name`. Secondary: `_validate_response_schema` recursively validates `items_schema` list elements with the same envelope helper. Fix: promote known section ids from direct `resume_structure` keys (preserving experience job arrays) before any default-structure replace; validate list items with a dedicated non-envelope field checker. Do not loosen required `candidate_name` or drop job-array `items_schema`.

## UAT fitness

- **AC restored:** Parent AC (quoted on bug): after craft-base parse of a multi-job resume paste, Experience is an ordered list of jobs with company/title/dates/location/accomplishments observable in parse JSON; task response contracts for craft-base (and shared job-array shape) accept the new form without silently flattening Experience back to a string.
- **Correct outcome:** Valid craft-base parse JSON with `candidate_name` present under `resume_structure` (direct key and/or existing content-map paths) **plus** experience as a job array passes response validation; user can accept/use the parse without a false-missing `candidate_name` popup.
- **Sibling check:** AST-996/997 keep experience as required/optional list of objects with `items_schema` (company, title, dates, location, accomplishments); AST-998 HTML builders unchanged. Verify by normalize+schema on a payload with job-array experience after promote — experience remains a list of dicts, not a string.
- **Not sufficient:** Hiding the Admin toast / swallowing the validation error string without making nested-name + job-array payloads actually pass schema.
- **Wrong fix rejected:** Removing `candidate_name` from required fields; accepting empty name; flattening Experience back to a single string; skipping schema validation when experience is a list; UI-only toast suppression.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Promote known section ids from direct keys on `resume_structure` (incl. `candidate_name`, experience job arrays) before default-structure replace; do not early-return flatten solely because `sections` is missing | core |
| `src/core/agent.py` | Validate `items_schema` list elements with a dedicated item-field helper (not full envelope recurse) | core |

**Out of scope:** `tests/`, bible; Admin toast UI rewrite; AST-993 chrome; cover-letter HTML; inventing candidate fields; changing `_EXPERIENCE_JOB_ITEM_SCHEMA` field set.

## Stage 1: Promote direct `resume_structure` section keys before wipe

**Done when:** A craft-base `agent_payload` with `candidate_name` only as a direct key on `resume_structure` (with or without `sections`) and top-level experience as a job array normalizes so top-level `candidate_name` is set; subsequent schema validation does not return `Missing required field 'candidate_name'` when other required fields are present. Replacing missing `sections` with `default_resume_structure()` no longer discards sibling section values that should have been promoted.

1. In `src/core/candidate.py`, update `_flatten_craft_resume_section_strings`:
   - If `resume_structure` is not a dict, return (unchanged).
   - **Do not** return early solely because `sections` is missing or not a dict — still run promotions below. Keep the existing `sections`-enabled nested-content loop only when `sections` is a dict (skip that loop when absent).
   - After the existing `content` map and `_CRAFT_RESUME_CONTENT_DICT_KEYS` promotions, add a pass over `RESUME_STRUCTURE_KNOWN_SECTION_IDS`: for each `sid`, if `sid` is a key on `resume_structure` (direct), call the existing `_promote(sid, raw_struct[sid])` (same rules: experience job-array preserve via `_is_experience_job_array`; string coerce for other ids; never overwrite non-empty top-level).
   - ⚠️ **Decision:** Promote only known section ids from direct keys — not arbitrary `resume_structure` keys (avoids lifting `sections`/`content` metadata).
2. In `normalize_craft_resume_base_agent_payload`, keep order: call `_flatten_craft_resume_section_strings(payload)` **before** any `payload["resume_structure"] = default_resume_structure()` when sections are missing. After Stage 1.1, sibling values are already on the payload top-level, so the default replace is safe.
3. Do not change `TASK_CONFIG` / experience `items_schema` / required `candidate_name`.

**Verification:** Local normalize + `_validate_response_schema(…, TASK_CONFIG["craft_resume_base"]["response_schema"], …)` for: (a) `resume_structure.candidate_name` + `sections` + job-array experience, other required fields top-level → ok; (b) same without `sections` → ok after promote then default struct; (c) name absent everywhere → still `Missing required field 'candidate_name'`.

## Stage 2: Harden list `items_schema` validation

**Done when:** List fields with `items_schema` (craft-base `experience`) validate each element's fields without treating the element as an `{agent_performance, agent_payload}` envelope; path-prefixed item errors remain (`experience[i]: …`).

1. In `src/core/agent.py`, near `_validate_response_schema`, add a helper (e.g. `_validate_schema_object_fields(obj, fields_schema, path_prefix)`) that for a dict `obj` walks `fields_schema` with the same required / type / enum checks already used for payload fields (str/bool/int/list/dict), returning the first error string or `None`. Do **not** look for `agent_payload` / `agent_performance` / failure envelopes inside this helper.
2. In `_validate_response_schema`, when `items_schema` is present and the value is a list: keep the non-dict item type error; replace the recursive `_validate_response_schema(item, items_schema, task_key)` call with the new helper, prefixing failures as `f"{field_name}[{idx}]: {item_err}"`.
3. Do not change envelope validation for the top-level parse object.

**Verification:** Valid job-array experience still passes; an experience item missing `company` yields an `experience[0]: …` missing-field error (not an envelope message); Stage 1 cases (a)–(c) unchanged.

## Stage 3: Regression sanity (no new files)

**Done when:** Engineer has exercised normalize+validate for nested-name + job-array (pass), missing name (fail), experience string (fail list type); experience remains a list of job objects after success — AC #1 shape intact.

1. No additional product files. Optional one-off local Python exercise only (do not add `tests/` or bible edits).
2. Confirm job-tailored paths that share flatten only if they call `_flatten_craft_resume_section_strings` / craft-base normalize — do not broaden into draft/finalize schema edits unless a shared helper change forces a one-line call-site note (prefer craft-base-only).

**Verification:** (pass/fail matrix above); Admin toast no longer shows false-missing name for the UAT repro payload shape.

## Self-Assessment

**Scope:** `Single-Component` — craft-base normalize in `candidate.py` plus list-item schema validation in `agent.py`; no UI, config schema, or builder changes.

**Conf:** `high` — false-missing reproduced with nested-only `resume_structure.candidate_name`; promote gap and sections-wipe order are explicit in current code; fix reuses existing `_promote` rules.

**Risk:** `Medium` — sits on the craft-base validate path used by paste-resume; wrong overwrite of good top-level fields or incorrect experience coerce would regress parses. Mitigated by known-id-only promote and skip-if-top-level-non-empty rules already in `_promote`.

## Code-rules check

- **Relevant statutes:** schema-and-contracts; agent-payload-contract; error-propagation (Admin toast shows server `data.error`); single normalize-before-validate write path for craft-base.
- **Compliance:** Lift nested section values into the existing required top-level contract rather than weakening schema; keep experience `list` + `items_schema`; do not swallow validation failures.
- **Challenges / exclusions:** No new HTTP route; no `tests/` or bible (Betty); no UI toast rewrite — fixing the server validation path removes the false popup; do not invent candidate fields when truly absent.

## Plan Completeness Checklist

- [x] Every stage has a concrete verification step
- [x] Files Changed table lists all files expected to touch
- [x] No stage depends on a file or function that isn't created in a prior stage or already in the codebase
- [x] Self-assessment Scope/Conf/Risk with justifications
- [x] Scope is AST-1005 only (not parent epic remainder)
- [x] UAT fitness filled from bug Description (parent Description not fetched)
- [x] Code-rules check completed

## Review (build stub)

**Publish ref:** `origin/sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name`
**Plan path:** `docs/features/artifacts/ast-1005-uat-parse-validation-false-missing-candidate-name.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | f348d69a | Promote known ids from resume_structure; dedicated items_schema object validator |

**Tip:** f348d69a (before stub docs commit).

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Publish ref tip:** (see Linear / post-push SHA) on `origin/sub/AST-994/AST-1005-uat-parse-validation-false-missing-candidate-name`
**Baseline:** `origin/dev`
**Overall:** DISCUSS

### What’s solid
- Promote known section ids from direct `resume_structure` keys before default wipe; experience job arrays preserved via existing `_promote`.
- `_validate_schema_object_fields` for `items_schema` (no envelope recurse); required `candidate_name` unchanged.
- Betty coverage for promote + items_schema paths.

### Issues
**discuss:** Tip three-dot includes `docs(AST-1001)` bible README via `merge-tests` from `origin/tests` — outside AST-1005 Files Changed / UAT scope (tests-line pollution, not product defect).

### Recommended actions
No product fix-now. Resolve may proceed on agent/candidate; Chuckles/Betty can scrub AST-1001 README from this tip / tests line if rollup hygiene requires it.

## Resolution

**Date:** 2026-07-28
**Review tip:** `32c2338d` (Radia `docs(AST-1005): Radia review — findings`)
**Overall:** DISCUSS → resolved for User Testing (no fix-now); spawn direction: proceed.

### fix-now
(none)

### discuss
1. Cross-ticket AST-1001 bible README on tip via `merge-tests` — accepted as tests-line / rollup hygiene (Chuckles/Betty), not a craft-base product defect. No product change on this resolve.

### advisory
(none)

**Outcome:** Clean resolve — no code delta vs Radia tip. Proceed to User Testing.
