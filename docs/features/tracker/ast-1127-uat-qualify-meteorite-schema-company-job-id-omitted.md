<!-- linear-archive: AST-1127 archived 2026-08-11 -->

## Linear archive (AST-1127)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1127/uat-qualify-meteorite-still-fails-schema-when-company-job-id-omitted  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1119 — Fallback for company job id  
**Blocked by / blocks / related:** parent: AST-1119

### Description

## What failed

`qualify_meteorite` still dies in agent RESPONSE validation when Ruth omits `company_job_id`:

```
[2026-08-02 18:11:23] ERROR src.core.agent: do_task validation failed. task_key='qualify_meteorite' error=jobs[0]: Missing required field 'company_job_id'
```

AST-1120 wired UUID-from-`job_link` only before the consult empty-id content gate. That path never runs when the key is absent/`null`, because schema validation aborts first.

## Expected

When AI omits or returns empty/`null` `company_job_id` and `job_link` has a UUID path segment, qualify records that UUID as `company_job_id` and continues (does not fail with Missing required field / empty-id solely for missing AI id).

## Acceptance criteria

- [X] Parent AC2: Empty/missing AI `company_job_id` + UUID path segment in `job_link` records that UUID and does not fail empty-id / schema Missing required field for omit alone.
- [X] Parent AC1: Non-empty AI `company_job_id` still recorded unchanged.
- [X] Parent AC3: Empty/missing AI id + no UUID in `job_link` still fails empty-id gate after resolve.

## Boundaries

- [X] Does not change meteorite create paths that leave `company_job_id` empty until qualify.
- [X] Does not expand to `qualify_job_listings`.
- [X] Does not use `job_site`.
- [X] "No more Missing required field" alone is not done — Parent AC + Correct outcome must hold.
- [X] Does not swallow schema errors, delete validation, prompt-only fix, or remove AST-1120 consult fallback.

## In scope

- [X] `astral.config.config-source-of-truth` — flip `TASK_CONFIG["qualify_meteorite"].response_schema` `company_job_id.required` to `False`
- [X] `astral.standards.in-scope-only` — schema unblock only; consult resolve remains AST-1120
- [X] `astral.agent.do-task-delegation` — existing `_validate_response_schema` behavior; no new validator
- [X] `pattern.identity.url-uuid-path-external-id-fallback` — keep AST-1120 resolve reachable for omit/`null`
- [X] `astral.batch.entity-agent-responses-latest-only` — post-decode apply still owns empty after schema pass

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` — AST-1121 source labels unchanged; this bug does not edit Style D
- [X] Catch-all swallow of schema errors / delete validation — Wrong fix
- [X] Prompt rewrite as primary fix — Wrong fix
- [X] Remove consult `_resolve_company_job_id` — Wrong fix
- [X] Host allowlists / `job_site` — parent Boundaries
- [X] Meteorite create paths — out of bug Boundaries

## Diagnosis

* **Hypothesis:** `TASK_CONFIG["qualify_meteorite"]["response_schema"]` still marks `company_job_id` `required: True`; `do_task` → `_validate_response_schema` rejects absent/`null` before `qualify_meteorite` process can call `_resolve_company_job_id`.
* **Correct outcome:** omit/`null`/empty AI id + UUID in `job_link` → recorded UUID; non-empty AI id still wins; no UUID still fails empty-id after resolve (not schema Missing required field for omit alone when link may supply it).
* **Wrong fix to avoid:** catch-all swallow of schema errors; delete schema validation; prompt-only “always return company_job_id”; remove consult fallback; invent host allowlists.
* **Related siblings / contracts:** AST-1120 resolve helper + consult wire must remain; AST-1121 debug source labels must still classify AI vs UUID-from-`job_link` vs neither after the real path runs.

## Repro

1. Run `qualify_meteorite` on a meteorite job whose Ruth RESPONSE omits `company_job_id` (or sets it null) but includes an http `job_link` with a UUID path segment (e.g. Dice-style `…/<uuid>`).
2. Observe `do_task validation failed … Missing required field 'company_job_id'` — task never reaches consult resolve.
3. Confirm a RESPONSE with `company_job_id: ""` would have reached consult fallback, but omit/`null` does not.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1119-fallback-for-company-job-id`, child `sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted`. Seeded at fix-uat.

### Comments

#### radia — 2026-08-02T18:57:34.629Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1127
**Publish ref:** `origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted` @ `2d35bcca`
**Overall:** CLEAN

Diff baseline: `origin/dev...origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted` — layers `{docs, utils}`; change_types `{add, modify}`. Parent User Testing → skipped `origin/ftr` merge; `origin/dev` already up to date.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no confidence/grade changes; config schema only |
| `astral.agent.do-task-delegation` | scoped | not-applicable | layers ['core'] ∩ diff ['docs', 'utils'] empty |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | layers ['core'] ∩ diff ['docs', 'utils'] empty |
| `astral.batch.batch-id-first` | scoped | not-applicable | layers ['data', 'core'] ∩ diff ['docs', 'utils'] empty |
| `astral.batch.batch-id-format` | scoped | not-applicable | layers ['core', 'data'] ∩ diff ['docs', 'utils'] empty |
| `astral.batch.claim-process-release` | scoped | not-applicable | layers ['core', 'data'] ∩ diff ['docs', 'utils'] empty |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | layers ['core', 'data'] ∩ diff ['docs', 'utils'] empty |
| `astral.config.config-source-of-truth` | scoped | conforms | required flag flipped in TASK_CONFIG only |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | thresholds untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env reads added |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths no match among ['artifacts/**', 'scripts/spikes/**'] |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | docs/features plan only; not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no run_next/dispatch chain edits |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no seed/dispatch_task rows; schema flag only |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single docs/features/tracker/ast-1127-….md |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commits only tests/bible; merge-tests ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | tests/bible only in test()+merge-tests commits |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | layers ['core', 'external'] ∩ diff ['docs', 'utils'] empty |
| `astral.layers.import-direction` | scoped | conforms | utils config only; no layer-bend imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ['scripts'] ∩ diff ['docs', 'utils'] empty |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | TASK_CONFIG schema; no UI rule surface |
| `astral.patterns.coat-check-never-store-empty` | scoped | not-applicable | layers ['core'] ∩ diff ['docs', 'utils'] empty |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | not-applicable | layers ['core'] ∩ diff ['docs', 'utils'] empty |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ['ui'] ∩ diff ['docs', 'utils'] empty |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no catalog edits |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | schema config not seed/boot |
| `astral.seed.define-approved` | scoped | conforms | no seed define |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | untouched |
| `astral.seed.other-via-coverage-join` | scoped | conforms | untouched |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | layers ['data', 'core', 'ui'] ∩ diff ['docs', 'utils'] empty |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ['data'] ∩ diff ['docs', 'utils'] empty |
| `astral.standards.debug-contract-gated` | scoped | conforms | no debug emission changes |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | one-flag config change; no new helpers |
| `astral.standards.in-scope-only` | scoped | conforms | qualify_meteorite company_job_id required flag only |
| `astral.standards.logging-via-utils` | scoped | conforms | no logging changes |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | no new symbols; ticket only in comment |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays in TASK_CONFIG qualify_meteorite schema |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | no host allowlists; schema flag only |
| `astral.standards.public-then-helpers` | scoped | conforms | no new functions |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | config module pattern unchanged |
| `astral.state.core-decides-transitions` | scoped | not-applicable | layers ['core', 'data'] ∩ diff ['docs', 'utils'] empty |
| `astral.state.job-prior-states-enforced` | scoped | conforms | prior_states untouched |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | layers ['core'] ∩ diff ['docs', 'utils'] empty |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ['ui'] ∩ diff ['docs', 'utils'] empty |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ['ui'] ∩ diff ['docs', 'utils'] empty |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no worker/deployment changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | one merge-tests(AST-1127) on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub child ref |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1119/AST-1127-… matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | origin/dev already up to date on tip |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits; no cherry-pick/rebase/force |
| `orch.git.no-dev-agent-branches` | universal | conforms | child publish-ref is sub/… not agent-named |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in astral-AST-1119 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branch |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | UAT schema fix matches parent AC2 diagnosis |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 config-only matches tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Tracker UAT bug AST-1127 only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada stays assignee through Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path edits in product commits |

## Pattern conformance

| pattern | verdict |
|---------|---------|
| `pattern.identity.url-uuid-path-external-id-fallback` | conforms — AST-1120 resolve left reachable; this ticket only unblocks schema entry |

## Plan adherence

Stage 1 matches tip: `TASK_CONFIG["qualify_meteorite"]…company_job_id` `required: False` + assert; sibling item fields stay required; no consult/agent/create edits. Self-Assessment Scope `minor` matches. UAT fitness: restores Parent AC2 by letting omit/`null` reach `_resolve_company_job_id`, not stacktrace silence alone. Wrong fixes avoided.

## Findings

None.

## What's solid

Config SoT one-flag flip; `type: str` retained; empty-id authority remains AST-1120 consult resolve; Betty coverage for omit→UUID + schema optional.

## Recommended actions

Resolve-child: no product edits required.

**Notes:** Joan `[validate-plan uat-thin]` APPROVED attached as comment — no full plan-rubric Excluded list → no C4 straggler sweep. Active statute count checked: 65.

context_tokens≈38000

#### betty — 2026-08-02T18:55:02.738Z
1. `tests/component/utils/test_config.py::TestAst1127QualifyMeteoriteCompanyJobIdOptional` — `company_job_id.required is False`; `_validate_response_schema` allows omit / `null` / `""`; sibling fields still required.
2. `tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig` — revised: `company_job_id` optional; other item fields still required.
3. `tests/component/core/test_consult.py::TestAst1127QualifyMeteoriteOmitCompanyJobId` — RESPONSE omits `company_job_id` key + Dice UUID `job_link` → recorded UUID + pass.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1127QualifyMeteoriteCompanyJobIdOptional \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_consult.py::TestAst1127QualifyMeteoriteOmitCompanyJobId \
  -q
```

**Broken / obsolete:** `TestAst1060QualifyMeteoriteConfig` asserted `company_job_id` `required is True` — revised this pass.

**Integration:** none revised.

**Publish:** `origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted` @ `e40e7386` (`merge-tests(AST-1127): origin/tests 7f6aafa5`).

**Bible shasums on publish tip:**
- `docs/test-bible/utils/config.md` `d20c2d2d7d05f7f168e4ef18c5830d0b4d153f7f`
- `docs/test-bible/core/consult.md` `e8969b233648607eaa751bce4db8fa3d457f42f4`

— Betty

#### joan — 2026-08-02T18:51:40.345Z
[validate-plan uat-thin]
**Ticket:** AST-1127
**Overall:** APPROVED

## UAT-thin checklist

- [x] Plan cites Parent AC (AC2 primary; AC1/AC3 preserved) in ## UAT fitness — not symptom-only
- [x] Stage 1 achieves Correct outcome: `company_job_id` `required: False` so omit/`null`/empty pass schema into AST-1120 resolve; AI still wins; no UUID still empty-id fail after resolve — not merely silencing `Missing required field`
- [x] Wrong fixes rejected (swallow schema errors, delete validation, prompt-only, remove consult fallback, host allowlists) — plan is config flag only
- [x] No catch-and-ignore / delete-log-path / empty-success / bypass
- [x] Sibling check: AST-1120 resolve/wire untouched and reachable; AST-1121 labels still classify after real path
- [x] Boundaries respected: no create / `job_site` / `qualify_job_listings` / other required-field weaken

## Notes

## UAT fitness present. Scope minor / Conf high / Risk Medium honest for a single schema `required` flip with `type: str` retained.

context_tokens≈22000

— Joan

#### ada — 2026-08-02T18:49:40.116Z
Plan published on `origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted` @ `2c906573`.

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted/docs/features/tracker/ast-1127-uat-qualify-meteorite-schema-company-job-id-omitted.md

**Self-assessment**
- **Scope:** `minor` — one `TASK_CONFIG["qualify_meteorite"]` schema flag (`company_job_id` `required: False`); consult resolve untouched.
- **Conf:** `high` — matches `_validate_schema_object_fields` null-skip for optional fields; same pattern as `qualify_job_listings` optional `company_job_id`; AST-1120 already owns empty→UUID.
- **Risk:** `Medium` — over-loosening schema could hide bad payloads; mitigated by keeping `type: "str"` and other item fields required, plus empty-id gate after resolve.

**UAT fitness:** AC2 restored by unblocking omit/`null` into AST-1120 resolve; stacktrace removal alone is not done.

---

# AST-1127 — UAT: qualify_meteorite still fails schema when company_job_id omitted

**Linear:** [AST-1127](https://linear.app/astralcareermatch/issue/AST-1127/uat-qualify-meteorite-still-fails-schema-when-company-job-id-omitted)
**Parent:** [AST-1119](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id) — Fallback for company job id
**Publish ref:** `origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted`

UAT bug: Ruth omit/`null` `company_job_id` still dies in `do_task` RESPONSE schema validation (`Missing required field 'company_job_id'`) before `qualify_meteorite` can run AST-1120’s `_resolve_company_job_id`. Fix is config-only: mark that field optional in `TASK_CONFIG["qualify_meteorite"]["response_schema"]` so missing/`null`/empty reach the existing consult resolve (AI wins; else UUID path segment from `job_link`; else empty-id fail). Does **not** swallow schema errors, rewrite prompts, touch create paths, `job_site`, or `qualify_job_listings`.

## UAT fitness

- **AC restored:** Parent AC2 — *Empty/missing AI `company_job_id` + `job_link` containing a UUID path segment … records that UUID as `company_job_id` and does not hit the empty-id fail gate.* Also preserves AC1 (non-empty AI unchanged) and AC3 (no UUID still empty-id fail).
- **Correct outcome:** omit/`null`/empty AI id + UUID in `job_link` → recorded UUID and continue past schema; non-empty AI id still wins; no UUID still fails empty-id after resolve (not `Missing required field` for omit alone when link may supply it).
- **Sibling check:** AST-1120 `_resolve_company_job_id` + wire before empty-id gate must remain and actually run; AST-1121 Style D found-source labels (`AI` / `UUID-from-job_link` / `neither`) still classify after the real path runs. Verified by not editing consult resolve/debug — only unblocking schema entry.
- **Not sufficient:** Removing the stacktrace / `Missing required field` alone is **not** done.
- **Wrong fix rejected:** catch-all swallow of schema errors; delete schema validation; prompt-only “always return company_job_id”; remove consult fallback; invent host allowlists — hypothesis matches AC; flip `required` to `False` (same pattern as `qualify_job_listings` optional metadata fields).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | In `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]`, set `company_job_id` `required: False` (keep `type: "str"`) | utils |

No consult/agent/meteorite-create edits. No tests/bible. Do **not** change other `qualify_meteorite` required fields (`astral_job_id`, `job_title`, `job_link`, `jd_text`).

## Stage 1: Allow omit/`null` company_job_id through RESPONSE schema

**Done when:** A RESPONSE job object missing `company_job_id` or with `company_job_id: null` passes `_validate_response_schema` for `qualify_meteorite`; present non-str values still fail type check; consult resolve path is unchanged and remains the empty-id authority.

1. In `src/utils/config.py`, locate `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]["company_job_id"]` (currently `{"type": "str", "required": True}` with comment `# external job UUID`).

2. Change **only** that field to:

```python
"company_job_id":  {"type": "str", "required": False},  # AST-1127: omit/null → consult UUID fallback
```

Keep sibling item fields (`astral_job_id`, `job_title`, `job_link`, `jd_text`) `required: True`.

3. Add a one-line assert near other TASK_CONFIG / qualify_meteorite asserts if the file already asserts this block; otherwise add after the `TASK_CONFIG` definition (or immediately after the qualify_meteorite dict closes if that is the local pattern):

```python
assert TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]["company_job_id"]["required"] is False
```

⚠️ **Decision — config `required: False` only, no agent.py fork:** `_validate_schema_object_fields` already treats `required=False` + `val is None` (missing key or JSON null) as skip; type `str` still rejects wrong types when present. Matches `qualify_job_listings` optional `company_job_id`. Consult already uses `(response_job.get("company_job_id") or "").strip()` before `_resolve_company_job_id` — no consult change in this bug.

⚠️ **Decision — do not weaken other required fields:** Title/link/JD gates stay schema-required; only the external id may be recovered from `job_link` per parent AC2.

**Done when (recheck):**

```python
from src.utils.config import TASK_CONFIG
from src.core.agent import _validate_response_schema

schema = TASK_CONFIG["qualify_meteorite"]["response_schema"]
# envelope shape used by do_task — agent_performance success + jobs payload
base = {
    "agent_performance": "success",
    "agent_payload": {
        "jobs": [{
            "astral_job_id": "j1",
            "job_title": "Engineer",
            "job_link": "https://www.dice.com/company-profile/9f704ad3-7a18-506a-bd5e-6a84e73b7c00",
            "jd_text": "x" * 50,
        }]
    },
}
# omit company_job_id
assert _validate_response_schema(base, schema, "qualify_meteorite") is None
# null
base["agent_payload"]["jobs"][0]["company_job_id"] = None
assert _validate_response_schema(base, schema, "qualify_meteorite") is None
# empty string still allowed through schema (consult resolve owns empty)
base["agent_payload"]["jobs"][0]["company_job_id"] = ""
assert _validate_response_schema(base, schema, "qualify_meteorite") is None
```

Adjust the envelope keys if `_validate_response_schema` expects a different payload shape on this tip — read `do_task` / `_validate_response_schema` once and use the same envelope the production path builds; do **not** invent a second validator. `python3 -m py_compile src/utils/config.py` succeeds. No edits under `src/core/consult.py` / `src/core/agent.py` unless the recheck proves the envelope helper needs a trivial import-only smoke (still no behavior change there).

## Self-Assessment

**Scope:** `minor` — one `TASK_CONFIG` boolean on `qualify_meteorite.response_schema`; no new helpers, no apply-surface rewrite.

**Conf:** `high` — diagnosis matches `_validate_schema_object_fields` (`required and val is None`); AST-1120 resolve already handles empty AI id; `qualify_job_listings` already uses optional `company_job_id`.

**Risk:** `Medium` — loosening schema could let bad types through if mis-set, but `type: "str"` remains; empty-id gate + resolve still fail when no UUID. Wrong if someone also flips other required fields (explicitly forbidden).

## Rules check (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §2.1 config SoT | Schema required flag lives in `TASK_CONFIG` only |
| §1.1 in-scope-only | Bug surface = schema gate blocking consult resolve; no create/`job_site`/listings |
| §2.2 do-task delegation | No new validation path; existing `_validate_response_schema` + consult apply |
| AST-1120 pattern | Resolve helper untouched; this ticket only unblocks entry |

No plan conflicts requiring `conf-!!-NONE`.

## Review

**Publish ref:** `origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted`
**Tip (pre-review):** `e40e7386` (`merge-tests` + Betty coverage)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `7bfaf610` | `qualify_meteorite` `company_job_id` `required: False` + assert |
| tests | `7f6aafa5` / `e40e7386` | Betty schema-optional + omit→UUID consult coverage + `merge-tests` |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Overall:** CLEAN

**What's solid**
- Single `TASK_CONFIG` flip: `company_job_id` `required: False` with `type: str` kept; module assert pins the flag.
- Sibling fields stay required; no consult/agent/create/`job_site`/`qualify_job_listings` edits — AST-1120 resolve remains empty-id authority.
- UAT fitness: unblocks omit/`null` into existing resolve (AC2), not symptom-only stacktrace silence.

**Issues**
- None.

**Recommended actions**
- Resolve-child can proceed; no product edits.

## Resolution

**Date:** 2026-08-02  
**Radia tip:** `2d35bcca` (`docs(AST-1127): Radia review — clean`)

- **fix-now / discuss / advisory:** none — Radia CLEAN; no product edits.
- **Ship:** Stage 1 schema flag stands; AST-1120 resolve remains empty-id authority for omit/`null`/empty AI id.
