<!-- linear-archive: AST-1066 archived 2026-08-11 -->

## Linear archive (AST-1066)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1066/contact-core-module-and-contact-config-slack-bot-agent  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1043 — Slack Bot Agent  
**Blocked by / blocks / related:** parent: AST-1043; blocks: AST-1071; blocks: AST-1069

### Description

## What this implements

Stand up Contact in core plus CONTACT_CONFIG (skills/ACL distinct from TASK_CONFIG), listen flag, Slack-user-id on CANDIDATE_LOOKUP_CONFIG, and environ secrets contracts. Does not own Slack HTTP Events plumbing (#2), Manage Slack UI (#3), Slack resolve/PROSPECT create (#4), context load (#5), or skill endpoint bodies (#6).

## Acceptance criteria

- [X] CONTACT_CONFIG exists in config and is distinct from TASK_CONFIG / dispatch.
- [X] Contact core module scaffold exists for siblings to extend.
- [X] CANDIDATE_LOOKUP_CONFIG can carry a Slack-user-id match home (used by #4).

## Boundaries

Does not own Slack webhook ingress, Manage Slack UI, PROSPECT create, conversation cache, or skill runners.

## In scope

- [X] `pattern.config.config-block` — CONTACT_CONFIG + CANDIDATE_LOOKUP_CONFIG slack_user_id_paths
- [X] `pattern.core.contact-agent` (proposed) — `src/core/contact.py` scaffold exemplar
- [X] `astral.config.config-source-of-truth` — behavior flags / ACL / env-name contracts in [config.py](<http://config.py>)
- [X] `astral.config.secrets-and-env-specific-from-environ` — SLACK_* values not in config literals; env names only
- [X] `astral.layers.import-direction` — [contact.py](<http://contact.py>) → utils only
- [X] `astral.layers.core-vs-external-bright-line` — no Slack HTTP I/O in this ticket
- [X] `astral.standards.no-hardcoded-sets` — paths / skill ACL / env names from config
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` — sibling scopes excluded
- [X] `astral.standards.public-then-helpers` / `astral.standards.dry-and-focused-functions` — public Contact helpers

## Considered but excluded

- [X] `pattern.external.slack-events` — AST-1069 owns external slack Events verify/ack/post
- [X] `pattern.ui.admin-endpoint` / `astral.patterns.require-auth-on-protected-endpoints` — AST-1067 Manage Slack
- [X] `pattern.state.entity-state-transitions` / PROSPECT registry — AST-1068
- [X] `astral.standards.debug-contract-gated` — no found/recorded I/O paths in this scaffold ticket
- [X] `astral.standards.database-header-inventory` — no schema/table changes
- [X] `astral.standards.logging-via-utils` — no new operational log paths beyond module logger import

## Notes for planning

Contact vs Consult shape; CONTACT_CONFIG ≠ TASK_CONFIG.

## Git branch (authoritative)

Parent `ftr/AST-1043-slack-bot-agent`; child `sub/AST-1043/AST-1066-contact-core-module-and-contact-config`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1066-contact-core-module-and-contact-config.md` @ `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config` tip `cb4f3227` (build; review stub follows).

### Comments

#### radia — 2026-07-30T02:56:50.046Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1066
**Publish ref:** `e8dd2a8b` on `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`
**Overall:** DISCUSS

**Diff change set:** `origin/dev...e8dd2a8b` — layers `{core, utils, docs}`; paths `src/core/contact.py` (A), `src/utils/config.py` (M), plan + test-bible + component tests; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no graded agent tasks / confidence surfaces |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task / TASK_CONFIG dispatch paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade vectors |
| astral.batch.batch-id-first | scoped | not-applicable | no batch claim API |
| astral.batch.batch-id-format | scoped | not-applicable | no batch_id generation |
| astral.batch.claim-process-release | scoped | not-applicable | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_data / entity refs |
| astral.config.config-source-of-truth | scoped | conforms | CONTACT_CONFIG + slack_user_id_paths live in config.py |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | env *names* only; no Slack secret values / import-time reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plan only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan at docs/features/contact/ast-1066-… |
| astral.git.betty-no-src-or-features | scoped | needs-discussion | merge-tests exception ok; follow-up scrub `a106fadf` still edits src/ |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty test/merge-tests vocabulary only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | contact.py config readers only; no Slack HTTP I/O |
| astral.layers.import-direction | scoped | conforms | contact.py → utils only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** in diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no ui layer paths |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | no ui endpoints |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data-layer work |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | conforms | no found/recorded I/O / debug= surfaces this ticket |
| astral.standards.dry-and-focused-functions | scoped | conforms | thin public helpers; meteorite-shaped scaffold |
| astral.standards.in-scope-only | scoped | conforms | sibling scopes absent from product delta |
| astral.standards.logging-via-utils | scoped | conforms | get_logger from utils; no print/bare logging |
| astral.standards.no-cross-contamination | scoped | conforms | TASK_CONFIG untouched; CONTACT_CONFIG separate ACL |
| astral.standards.no-hardcoded-sets | scoped | conforms | paths / ACL / env names from config |
| astral.standards.public-then-helpers | scoped | conforms | five public functions; no private helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py add has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no PROSPECT/state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch run_next |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend paths |
| astral.ui.naming-conventions | scoped | not-applicable | no ui paths |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single merge-tests SHA then restorative scrub |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/fix vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish only on origin/sub/AST-1043/AST-1066-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in product commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1066-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions held; Betty @susan on tests-branch bleed |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match tip product |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute/pattern-catalog edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible; engineer owns src/plan |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Ada remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | CONTACT_CONFIG + CANDIDATE_LOOKUP slack_user_id_paths |
| pattern.core.contact-agent (proposed) | conforms | src/core/contact.py scaffold exemplar |

## Plan adherence

Stages 1–2 land exactly: CONTACT_CONFIG distinct from TASK_CONFIG, env-name contracts, `slack_user_id_paths`, five public Contact helpers, no Slack HTTP / PROSPECT / UI / skill runners. Self-Assessment Single-Component / high / low matches footprint. Out-of-scope siblings clean on tip product (post-scrub).

## Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` now in-scope on tip (docs/features + tests/bible). All three score **conforms** — no product action.

**discuss** — `astral.git.betty-no-src-or-features`: merge-tests exception covers `25aa2de8`; follow-up `fix(AST-1066)` scrub `a106fadf` still edits `src/` / drops AST-1072 feature doc to restore Ada tip. Operational recovery after polluted `origin/tests` ancestry (Betty already @susan). Tip product matches Ada build — no Contact scaffold fix required.

## What’s solid

Config home + Contact scaffold mirror meteorite pattern; secrets deferred; listen default off; empty skills with TASK_CONFIG collision assert; Betty component coverage matches bible.

Plan append: `docs/features/contact/ast-1066-contact-core-module-and-contact-config.md` @ `e8dd2a8b`.

context_tokens≈52000

— Radia

#### betty — 2026-07-30T02:52:48.634Z
## QA test manifest — AST-1066

`origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config` @ `a106fadf`

- `merge-tests(AST-1066): origin/tests d82783c4402c1a4b73b191b57bfb57776dd20b55` @ `25aa2de8`
- follow-up `fix(AST-1066): scrub merge-tests product bleed…` @ `a106fadf` — restores Ada tip `agent.py` / `config.py` / `agent_task.json` and drops AST-1072 feature doc that rode in via polluted `origin/tests` ancestry. Tip vs Ada build (`e85f4ac3`) is **tests/bible only**.

### Manifest

1. `tests/component/utils/test_config.py::TestAst1066ContactConfig`
2. `tests/component/core/test_contact.py::TestAst1066ContactScaffold`

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1066ContactConfig \
  tests/component/core/test_contact.py::TestAst1066ContactScaffold \
  -q
```

(7 passed vs tip product.)

### Broken / obsolete

none — additive `CONTACT_CONFIG` + `slack_user_id_paths` + new `src/core/contact.py`. AST-1047 email/name asserts unchanged.

### Bible shasums (`origin/sub/…` tip, sha256)

- `docs/test-bible/core/contact.md` — `9ab92b28d1417f59bff7ab723c13f3ec312e43113151e3c0b1f3b6703ee15c8f`
- `docs/test-bible/utils/config.md` — `8de7c5009ca8db0ddd07ee64374bdfe5cfda73484ec7c5218972571bd66d4dcd`

### Note (@susan)

`origin/tests` tip parent is `docs(AST-1072)` / `code(AST-1072)` product history — merge-tests from that tip pulled AST-1072 into this child’s publish ref until scrubbed. Worth a separate tests-branch cleanup so future `merge-tests` do not re-bleed.

#### joan — 2026-07-30T02:38:49.057Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1066
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle DM/@ ingress plumbing | N/A — boundary (AST-1069 / AST-1046) |
| AC2 Events Request URL verify/ack | N/A — boundary (AST-1069) |
| AC3 Manage Slack listen + `[env]` prefix | Partial home only — `listen_enabled` + prefix template in CONTACT_CONFIG; UI/apply is AST-1067 |
| AC4 Slack resolve + PROSPECT create | Partial — `CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]` only; matcher/PROSPECT is AST-1068 |
| AC5 routing exposes candidate state | N/A — boundary (AST-1068) |
| AC6 Slack conversation load/cache | N/A — boundary (AST-1070) |
| AC7 CONTACT_CONFIG skills/ACL distinct from TASK_CONFIG | Stage 1 CONTACT_CONFIG + empty `skills` + TASK_CONFIG collision assert; runners AST-1071 |
| AC8 debug=True found/recorded | N/A — no I/O paths this ticket (explicit Out of scope) |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| CONTACT_CONFIG exists, distinct from TASK_CONFIG/dispatch | Stage 1 |
| Contact core module scaffold | Stage 2 |
| CANDIDATE_LOOKUP_CONFIG Slack-user-id match home | Stage 1 §3 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 CONTACT_CONFIG + lookup home | Purpose Contact vs Consult / CONTACT_CONFIG; Functional scope secrets-in-environ contracts; child #1 |
| Stage 2 `src/core/contact.py` scaffold | Architectural `pattern.core.contact-agent` exemplar; import-direction / core-vs-external bright line |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Execution contract publishes on sub with plan/code vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1043/AST-1066-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1043 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions; stop→parent on drift |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child Contact scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute/pattern-catalog edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) builds after approve |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded agent tasks |
| astral.agent.do-task-delegation | conforms | No do_task; Contact skills ≠ TASK_CONFIG |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | No batch claim API |
| astral.batch.batch-id-format | conforms | No batch_id generation |
| astral.batch.claim-process-release | conforms | No batch processing |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data / entity refs |
| astral.config.config-source-of-truth | conforms | CONTACT_CONFIG + lookup paths in config.py |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Env names only; values deferred to AST-1069 strict reads |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features |
| astral.layers.core-vs-external-bright-line | conforms | No Slack HTTP I/O in core scaffold |
| astral.layers.import-direction | conforms | contact.py → utils only |
| astral.layers.ui-config-driven-business-logic | conforms | No React business rules; utils config home only |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work |
| astral.standards.debug-contract-gated | conforms | No debug I/O paths this ticket |
| astral.standards.dry-and-focused-functions | conforms | Thin public helpers; mirrors meteorite scaffold |
| astral.standards.in-scope-only | conforms | Sibling scopes listed Out of scope |
| astral.standards.logging-via-utils | conforms | get_logger from utils; no print/bare logging |
| astral.standards.no-cross-contamination | conforms | No TASK_CONFIG/tests/sibling edits |
| astral.standards.no-hardcoded-sets | conforms | Paths/ACL/env names in config |
| astral.standards.public-then-helpers | conforms | Five public functions; no private helpers required |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import |
| astral.state.core-decides-transitions | conforms | No PROSPECT/state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch run_next |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core,utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**acceptable:** Self-assessment Single-Component / Conf high / Risk low is honest for a config+scaffold ticket; deferred Slack `os.environ` reads and empty `skills` are explicit Decisions that keep unrelated processes from crashing and leave skill ids to AST-1071.

**R6 checklist:** Definition fidelity pass (child #1 only). Layer/import pass. Config + secrets-name contracts pass. No batch/state/UI creep. DRY via meteorite-shaped scaffold. Sibling Out of scope list complete.

context_tokens≈48000

— Joan

#### chuckles — 2026-07-30T02:35:34.441Z
[thread-orphan] Joan session relocated
found: `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
expected: `/home/susan/.cursor/chats/dc8b9f956372ceed188a68a2d2f8f217/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
— Chuckles

#### ada — 2026-07-30T02:34:54.981Z
Plan published.

**Doc:** https://github.com/susansomerset/astral/blob/sub/AST-1043/AST-1066-contact-core-module-and-contact-config/docs/features/contact/ast-1066-contact-core-module-and-contact-config.md
**Tip:** `c6219447` on `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`

**Self-assessment**
- **Scope:** Single-Component — CONTACT_CONFIG + lookup path + `src/core/contact.py` scaffold; no UI/external/data.
- **Conf:** high — mirrors METEORITE_CONFIG/meteorite scaffold; AST-1047 lookup-home style; sibling boundaries explicit.
- **Risk:** low — listen default False + empty skills; Slack env reads deferred to AST-1069 so import does not crash unrelated processes.

---

# AST-1066 — Contact core module and CONTACT_CONFIG

**Linear:** [AST-1066](https://linear.app/astralcareermatch/issue/AST-1066/contact-core-module-and-contact-config-slack-bot-agent)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`

Stand up **Contact** as a core module plus a **`CONTACT_CONFIG`** block (skills/ACL vocabulary distinct from `TASK_CONFIG` / dispatch), a default-off listen flag, Slack secret **env-name** contracts, and a Slack-user-id match home on **`CANDIDATE_LOOKUP_CONFIG`**. This is the foundation siblings (#2–#6) extend. Does **not** own Slack Events HTTP, Manage Slack UI, resolve/PROSPECT create, conversation cache, or skill runner bodies.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CONTACT_CONFIG`; extend `CANDIDATE_LOOKUP_CONFIG` with `slack_user_id_paths`; document Slack env names in module docstring | utils |
| `src/core/contact.py` | New Contact scaffold module (listen + skills ACL readers; no Slack I/O) | core |

---

## Stage 1: `CONTACT_CONFIG` + Slack lookup home

**Done when:** `CONTACT_CONFIG` and `CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]` are importable from `src.utils.config`; no `TASK_CONFIG` keys are reused as Contact skill ids; Slack secret **values** are not present in config; no core/UI/external callers yet.

1. In `src/utils/config.py` module docstring **Required environment variables** list, append (comment only — do **not** `os.environ[...]` these at import time in this ticket):

```
  SLACK_BOT_TOKEN       — Estelle bot token (Contact / external slack; AST-1069 reads)
  SLACK_SIGNING_SECRET  — Slack Events signing secret (AST-1069 verifies)
```

2. In the same docstring **Config sections** list, add:

```
  CONTACT_CONFIG  — Contact listen flag, Slack env-name contracts, skills ACL (AST-1066; distinct from TASK_CONFIG)
```

3. Immediately **after** the existing `CANDIDATE_LOOKUP_CONFIG` block (currently ends with `"match_casefold": True`), **extend** that dict — do **not** replace email/name paths — by adding:

```python
    # Slack user id homes (AST-1066). Matcher inclusion is AST-1068 — config home only here.
    "slack_user_id_paths": (
        "contact.slack_user_id",
    ),
```

⚠️ **Decision:** Canonical path is `contact.slack_user_id` under `candidate_data` (same blob family as AST-1014 contact email). AST-1068 owns persisting the value and teaching `get_candidate_id_for_query` to scan these paths. This ticket does **not** edit `src/core/candidate.py`.

4. Immediately **after** the extended `CANDIDATE_LOOKUP_CONFIG` (before `INBOX_CREATE_JOB_CONFIG`), add:

```python
# ---------------------------------------------------------------------------
# CONTACT_CONFIG: Astral Contact / Estelle foundation (AST-1066 / AST-1043).
# Skills ACL is Contact-only — never dispatch TASK_CONFIG / agent_task catalog rows.
# Secret *values* live in environ; this block stores env *names* + behavior flags.
# ---------------------------------------------------------------------------
CONTACT_CONFIG = {
    # Default off. Manage Slack (AST-1067) owns the per-environment flip.
    "listen_enabled": False,
    # Format with environment= (deploy label). AST-1067 applies when listen is on
    # and deploy is not production.
    "non_production_reply_prefix_template": "[{environment}] ",
    # Environ name contracts — readers use os.environ[CONTACT_CONFIG["…_env"]] (no .get).
    "bot_token_env": "SLACK_BOT_TOKEN",
    "signing_secret_env": "SLACK_SIGNING_SECRET",
    # skill_key → ACL metadata dict. Empty until AST-1071 registers entity-save skills.
    "skills": {},
}

assert isinstance(CONTACT_CONFIG["listen_enabled"], bool)
assert isinstance(CONTACT_CONFIG["skills"], dict)
assert CONTACT_CONFIG["bot_token_env"] == "SLACK_BOT_TOKEN"
assert CONTACT_CONFIG["signing_secret_env"] == "SLACK_SIGNING_SECRET"
# Contact skills must not collide with dispatch/agent TASK_CONFIG keys.
for _skill_key in CONTACT_CONFIG["skills"]:
    assert _skill_key not in TASK_CONFIG, _skill_key
```

⚠️ **Decision — CONTACT_CONFIG ≠ TASK_CONFIG:** Contact skills are an internal ACL for entity-save paths (AST-1071), not dispatcher/`do_task` catalog entries. Keep a separate top-level block even if the dict shape looks similar later. Empty `skills` is intentional so #1 can land without inventing skill ids that #6 owns.

⚠️ **Decision — secrets contract:** Store only env **names** here. Do **not** call `os.environ["SLACK_BOT_TOKEN"]` (or signing secret) at config import in this ticket — Contact is not live until AST-1069, and crashing every local/test process for unused Slack vars would break unrelated work. AST-1069’s `src/external/slack.py` reads with `os.environ[CONTACT_CONFIG["bot_token_env"]]` (strict, no `.get`) when Events/post paths run.

⚠️ **Decision — listen flag:** Literal `False` in config (behavior flag, §2.1). Per-environment persistence/UI is AST-1067; this ticket only provides the default home siblings read via Contact helpers.

5. Do **not** add `PROSPECT` to `CANDIDATE_STATES`. Do **not** remove `assert "PROSPECT" not in CANDIDATE_STATES`. Do **not** add Slack env reads that crash import. Do **not** edit `TASK_CONFIG`.

**Done when (recheck):** `from src.utils.config import CONTACT_CONFIG, CANDIDATE_LOOKUP_CONFIG` works; `slack_user_id_paths == ("contact.slack_user_id",)`; `listen_enabled is False`; `skills == {}`.

---

## Stage 2: `src/core/contact.py` scaffold

**Done when:** Contact core module imports cleanly; public helpers read only from `CONTACT_CONFIG`; no Slack HTTP, no DB writes, no UI routes, no skill runners.

1. Create `src/core/contact.py` with module docstring:

```
Contact: Slack foundation + CONTACT_CONFIG skills ACL (Astral Contact / AST-1066).

Siblings extend: Events ingress (AST-1069), Manage Slack listen UI (AST-1067),
resolve/PROSPECT (AST-1068), conversation context (AST-1070), skill runners (AST-1071).
Estelle conversational turn loop lives on AST-1046 — not here.
```

2. Imports (utils only — no `src.external`, no `src.ui`, no data mutations):

```python
from typing import Any, Dict, Tuple

from src.utils.config import CONTACT_CONFIG
from src.utils.logging import get_logger

logger = get_logger(__name__)
```

3. Public API (public-first; no private helpers required in this ticket):

```python
def slack_listen_enabled() -> bool:
    """Return CONTACT_CONFIG listen flag (default False until Manage Slack flips it)."""
    return bool(CONTACT_CONFIG["listen_enabled"])


def contact_skills() -> Dict[str, Any]:
    """Shallow copy of CONTACT_CONFIG['skills'] ACL map (empty until AST-1071)."""
    return dict(CONTACT_CONFIG["skills"])


def contact_skill_keys() -> Tuple[str, ...]:
    """Ordered tuple of allowlisted Contact skill keys."""
    return tuple(CONTACT_CONFIG["skills"].keys())


def slack_env_names() -> Dict[str, str]:
    """Map logical secret → environ variable name (values never returned)."""
    return {
        "bot_token": str(CONTACT_CONFIG["bot_token_env"]),
        "signing_secret": str(CONTACT_CONFIG["signing_secret_env"]),
    }


def non_production_reply_prefix(environment: str) -> str:
    """Format CONTACT_CONFIG non-production reply prefix (AST-1067 applies when listen on)."""
    env = (environment or "").strip()
    return str(CONTACT_CONFIG["non_production_reply_prefix_template"]).format(
        environment=env
    )
```

4. Do **not** implement: webhook verify/ack/post, Manage Slack endpoints, `get_candidate_id_for_query` changes, PROSPECT create, conversation cache, skill runner callables, or `debug=` Style D lines (no found/recorded I/O paths in this ticket yet).

⚠️ **Decision — core vs external:** Contact core owns orchestration helpers and config reads. Slack signing verify / Web API post belong in `src/external/slack.py` (AST-1069). Core must not import external Slack clients in this scaffold.

**Done when (recheck):** `from src.core.contact import slack_listen_enabled, contact_skills, slack_env_names` works; `slack_listen_enabled() is False`; `contact_skill_keys() == ()`; `slack_env_names()["bot_token"] == "SLACK_BOT_TOKEN"`.

---

## Out of scope (do not implement here)

- `src/external/slack.py` / Events API webhook / URL challenge / signing verify / post message (AST-1069).
- Admin Manage Slack UI + persist listen flip + apply `[env]` prefix on outbound (AST-1067).
- Extend `get_candidate_id_for_query` to scan `slack_user_id_paths`; PROSPECT state + create (AST-1068).
- Slack conversation history load/cache (AST-1070).
- Register/run entity-save skills under `CONTACT_CONFIG["skills"]` (AST-1071).
- Estelle turn loop / envelope (AST-1046).
- Pattern catalog file for `pattern.core.contact-agent` (proposed; harvest after Archie).
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

---

## Self-Assessment

**Scope:** `Single-Component` — one config block (+ lookup path tuple), one new core module; no UI/external/data schema.

**Conf:** `high` — mirrors `METEORITE_CONFIG` + `meteorite.py` scaffold pattern; lookup home extension matches AST-1047 `CANDIDATE_LOOKUP_CONFIG` style; sibling boundaries are explicit in parent child list.

**Risk:** `low` — default `listen_enabled=False` and empty `skills` cannot activate Slack or entity writes; deferred `os.environ` reads avoid import-time crash for unrelated processes.

## Rules self-review

- **§2.1 / secrets-from-environ:** Secret **values** not in config; env **names** + listen/prefix/skills literals are.
- **§2.1 / no-hardcoded-sets:** Skill ACL and Slack path homes live only in config blocks.
- **§2.5 / §3.3 import-direction:** `contact.py` → utils only; no external Slack I/O.
- **§1.3 public-then-helpers:** Five public functions; no private helpers required.
- **§1.1 in-scope-only:** Sibling scopes listed under Out of scope; no PROSPECT / webhook / UI.
- **§1.5.1 debug-contract:** No new debug paths this ticket (no found/recorded I/O yet).
- **no-cross-contamination:** Do not edit `TASK_CONFIG`, `tests/`, or sibling publish refs.

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on epic worktree; publish to `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`. On ambiguity or codebase drift, stop and comment on parent **AST-1043** with the Stage-blocked format — do not improvise.

## Review (build stub)

- **Publish ref:** `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`
- **Tip:** `cb4f3227` — Contact scaffold + CONTACT_CONFIG (stages 1–2)
- **Stage commits:** `db5e2b79` (config), `cb4f3227` (core module)

---

## Review (Radia / code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1066  
**Publish ref:** `a106fadf` on `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`  
**Overall:** DISCUSS

**Diff change set:** `origin/dev...a106fadf` — layers `{core, utils, docs}`; paths `src/core/contact.py` (A), `src/utils/config.py` (M), plan + test-bible + component tests; change_types `{add, modify}`.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no graded agent tasks / confidence surfaces |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task / TASK_CONFIG dispatch paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade vectors |
| astral.batch.batch-id-first | scoped | not-applicable | no batch claim API |
| astral.batch.batch-id-format | scoped | not-applicable | no batch_id generation |
| astral.batch.claim-process-release | scoped | not-applicable | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_data / entity refs |
| astral.config.config-source-of-truth | scoped | conforms | CONTACT_CONFIG + slack_user_id_paths live in config.py |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | env *names* only; no Slack secret values / import-time reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plan only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan at docs/features/contact/ast-1066-… |
| astral.git.betty-no-src-or-features | scoped | needs-discussion | merge-tests exception ok; follow-up scrub `a106fadf` still edits src/ |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty test/merge-tests vocabulary only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | contact.py config readers only; no Slack HTTP I/O |
| astral.layers.import-direction | scoped | conforms | contact.py → utils only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** in diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no ui layer paths |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | no ui endpoints |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data-layer work |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | conforms | no found/recorded I/O / debug= surfaces this ticket |
| astral.standards.dry-and-focused-functions | scoped | conforms | thin public helpers; meteorite-shaped scaffold |
| astral.standards.in-scope-only | scoped | conforms | sibling scopes absent from product delta |
| astral.standards.logging-via-utils | scoped | conforms | get_logger from utils; no print/bare logging |
| astral.standards.no-cross-contamination | scoped | conforms | TASK_CONFIG untouched; CONTACT_CONFIG separate ACL |
| astral.standards.no-hardcoded-sets | scoped | conforms | paths / ACL / env names from config |
| astral.standards.public-then-helpers | scoped | conforms | five public functions; no private helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py add has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no PROSPECT/state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch run_next |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend paths |
| astral.ui.naming-conventions | scoped | not-applicable | no ui paths |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | single merge-tests SHA then restorative scrub |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/fix vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | publish only on origin/sub/AST-1043/AST-1066-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe in product commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1066-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions held; Betty @susan on tests-branch bleed |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match tip product |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute/pattern-catalog edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible; engineer owns src/plan |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Ada remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | CONTACT_CONFIG + CANDIDATE_LOOKUP slack_user_id_paths |
| pattern.core.contact-agent (proposed) | conforms | src/core/contact.py scaffold exemplar |

### Plan adherence

Stages 1–2 land exactly: CONTACT_CONFIG distinct from TASK_CONFIG, env-name contracts, `slack_user_id_paths`, five public Contact helpers, no Slack HTTP / PROSPECT / UI / skill runners. Self-Assessment Single-Component / high / low matches footprint. Out-of-scope siblings clean on tip product (post-scrub).

### Findings

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` now in-scope on tip (docs/features + tests/bible). All three score **conforms** — no product action.

**discuss** — `astral.git.betty-no-src-or-features`: merge-tests exception covers `25aa2de8`; follow-up `fix(AST-1066)` scrub `a106fadf` still edits `src/` / drops AST-1072 feature doc to restore Ada tip. Operational recovery after polluted `origin/tests` ancestry (Betty already @susan). Tip product matches Ada build — no Contact scaffold fix required.

### What’s solid

Config home + Contact scaffold mirror meteorite pattern; secrets deferred; listen default off; empty skills with TASK_CONFIG collision assert; Betty component coverage matches bible.

context_tokens≈52000

## Resolution (2026-07-30)

Radia **Overall: DISCUSS** @ `e8dd2a8b` — **no fix-now**.

| Finding | Disposition |
|---------|-------------|
| C4 stragglers (`spikes-under-debug-dir`, `features-single-file-per-ticket`, `engineer-test-tree-ban`) | Acknowledged — all **conforms**; no product action |
| `betty-no-src-or-features` / scrub `a106fadf` | Acknowledged — tip product matches Ada build; Betty already flagged `origin/tests` bleed to Susan; no Contact scaffold change |

**Product delta this resolve:** none. Publish tip advances with this Resolution note only.
