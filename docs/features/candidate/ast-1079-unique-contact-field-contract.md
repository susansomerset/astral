<!-- linear-archive: AST-1079 archived 2026-08-11 -->

## Linear archive (AST-1079)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1079/unique-contact-field-contract-in-config-verify-unique-contact-info  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1045 — Verify unique contact info  
**Blocked by / blocks / related:** parent: AST-1045; blocks: AST-1080

### Description

## What this implements

Define config for which contact values participate in within-candidate dedupe and cross-candidate uniqueness, plus compare rules (e.g. casefold for emails). Prefer extending or siblinging the existing candidate lookup config rather than a parallel hardcoded list. Does **not** own save-path enforcement (sibling enforce slice). Does **not** own Profile UI (AST-1065).

## Acceptance criteria

- [X] 3. Which fields participate and how they compare (e.g. case-insensitive emails) are driven by config; changing the set does not require hunting hardcoded lists in core.
- [X] 4. Existing unambiguous email bind/lookup behavior remains usable: after enforcement, two live candidates cannot both hold the same uniqueness-scoped email (going forward) — this child supplies the shared vocabulary aligned with `CANDIDATE_LOOKUP_CONFIG` email paths (including transitional `profile.*` until gone).

## Boundaries

- [X] Does **not** own save-path enforcement (sibling AST-1080).
- [X] Does **not** own Profile/Admin contact UI (AST-1065).
- [X] Does **not** re-implement the contact library (AST-1014).

## In scope

- [X] `pattern.config.config-block` — new `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` sibling to `CANDIDATE_LOOKUP_CONFIG` in `src/utils/config.py`
- [X] `astral.config.config-source-of-truth` — uniqueness field participation + compare modes live in config literals
- [X] `astral.standards.no-hardcoded-sets` — no inline unique-field sets for the future save gate to re-invent
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/candidate/ast-1079-unique-contact-field-contract.md`

## Considered but excluded

- [X] Save-path within-candidate dedupe + cross-candidate hard-fail + domain error + Style D debug — AST-1080 (`src/core/candidate.py` / contact save path)
- [X] Profile / Admin contact UI surfacing — AST-1065 (`src/ui/`)
- [X] Contact library schema / `CANDIDATE_LIBRARY_CONFIG` key inventory — AST-1014 (already shipped; this ticket only asserts uniqueness paths ⊆ `contact_keys` where applicable)
- [X] `get_candidate_id_for_query` match semantics changes — AST-1047 (Done); this ticket only shares email/slack path objects with lookup
- [X] Batch claim/process, candidate state machine, dispatcher — N/A for config vocabulary

## Notes for planning

Open answers locked on parent: unique across candidates = all contact info; within-candidate = avoid adding the same contact info twice; hard-fail on cross-candidate collision; no legacy duplicate cleanup expected; align with lookup email paths.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1045-verify-unique-contact-info`, child `sub/AST-1045/AST-1079-unique-contact-field-contract`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-30T23:58:37.137Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1079
**Publish ref:** `249a8a37ab47e58432943727b5cbc4e34e5738e7` (`origin/sub/AST-1045/AST-1079-unique-contact-field-contract`)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1045/AST-1079-unique-contact-field-contract` — paths: `src/utils/config.py` (modify), `docs/features/candidate/ast-1079-unique-contact-field-contract.md` (add), `docs/test-bible/utils/config.md` (modify), `tests/component/utils/test_config.py` (add). Layers: `utils`, `docs`. Change types: `add`, `modify`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No graded-confidence / consult work |
| astral.agent.do-task-delegation | scoped | not-applicable | layers {core} ∩ {utils,docs}=∅ |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers {core} ∩ {utils,docs}=∅ |
| astral.batch.batch-id-first | scoped | not-applicable | layers {data,core} ∩ {utils,docs}=∅ |
| astral.batch.batch-id-format | scoped | not-applicable | layers {core,data} ∩ {utils,docs}=∅ |
| astral.batch.claim-process-release | scoped | not-applicable | layers {core,data} ∩ {utils,docs}=∅ |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers {core,data} ∩ {utils,docs}=∅ |
| astral.config.config-source-of-truth | scoped | conforms | New `*_CONFIG` literals; paths + compare in config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env; plain config literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths {artifacts/**,scripts/spikes/**} no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan doc only; no spike notes under docs/features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/candidate/ast-1079-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only test-tree + merge-tests; no src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` only `src/utils/config.py`; Betty owns tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers {core,external} ∩ {utils,docs}=∅ |
| astral.layers.import-direction | scoped | conforms | Utils-only; no illegal imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ {utils,docs}=∅ |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI; config vocabulary for later core gate |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers {core} ∩ {utils,docs}=∅ |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers {core} ∩ {utils,docs}=∅ |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers {ui} ∩ {utils,docs}=∅ |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers {data,core,ui} ∩ {utils,docs}=∅ |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} ∩ {utils,docs}=∅ |
| astral.standards.debug-contract-gated | scoped | conforms | No debug emission in config-only child |
| astral.standards.dry-and-focused-functions | scoped | conforms | Email/slack path objects reused by identity from lookup |
| astral.standards.in-scope-only | scoped | conforms | Config vocabulary only; enforce/UI/library excluded |
| astral.standards.logging-via-utils | scoped | conforms | No logging changes |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in utils/config |
| astral.standards.no-hardcoded-sets | scoped | conforms | Uniqueness set + compare modes live in config for AST-1080 |
| astral.standards.public-then-helpers | scoped | conforms | Config block + asserts; no scattered helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data import path added |
| astral.state.core-decides-transitions | scoped | not-applicable | layers {core,data} ∩ {utils,docs}=∅ |
| astral.state.job-prior-states-enforced | scoped | conforms | No job-state work |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers {core} ∩ {utils,docs}=∅ |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers {ui} ∩ {utils,docs}=∅ |
| astral.ui.naming-conventions | scoped | not-applicable | layers {ui} ∩ {utils,docs}=∅ |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1079)` SHA lands Betty tip |
| orch.git.commit-vocabulary | universal | conforms | plan/docs/code/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Publish only to origin/sub/AST-1045/AST-1079-… |
| orch.git.ftr-sub-topology | universal | conforms | Matches parent Git table child ref |
| orch.git.merge-on-checkout | universal | conforms | Worktree merge of origin/ftr clean before docs() |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None on publish tip |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub/AST-1045/AST-1079-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree astral-AST-1045 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Field-set Decisions cite locked parent OQs |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches Stage 1 plan block + asserts |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test() + merge-tests only on test-tree paths |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer Ada stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role hooks respected on publish path |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | Sibling `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` next to lookup |

Active `astral.patterns.*` covered in statutes table (all N/A here).

## Plan adherence

Stage 1 delivered as planned: docstring inventory line, sibling block after `CANDIDATE_LOOKUP_CONFIG` with shared email/slack path objects, compare/scopes, import-time asserts incl. `contact_keys` membership. Self-Assessment **minor / high / low** matches footprint (utils config only; no callers). Boundaries held vs AST-1080 / AST-1065 / AST-1014. No `conf-!!-NONE`.

## Findings

**discuss (straggler):** Joan plan-rubric Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` (plan Files Changed = utils only). Three-dot diff vs `origin/dev` puts `docs/features/**` + Betty test-tree paths in scope. All three score **conforms** — no product fix.

No fix-now.

## What’s solid

Identity-shared email/slack path tuples + asserts prevent vocabulary drift for AST-1080. Non-email uniqueness paths are `contact.*` only; compare modes match plan Decisions.

## Notes

Joan plan-rubric verdict attached (APPROVED). Non-blocking Joan discuss on slack_user_id inclusion remains documented in plan Decision — not re-opened as fix-now.

context_tokens≈42000

#### betty — 2026-07-30T23:53:45.987Z
## QA test manifest

`origin/sub/AST-1045/AST-1079-unique-contact-field-contract` @ `562bcc1d` (`merge-tests(AST-1079): origin/tests 3ab8ae6c`).

1. `tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig` — email/slack path identity with lookup; scalar/list paths; compare modes; scopes; keys ⊆ `contact_keys`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig \
  -q
```

**Bible sha256** (`git show origin/sub/AST-1045/AST-1079-unique-contact-field-contract:docs/test-bible/utils/config.md`):
- `docs/test-bible/utils/config.md` `8ac3eacdd76eec09fd025bc1b194e14469dd2ab5f2941d902061c3f891ece1ae`

— Betty

#### joan — 2026-07-30T23:48:27.341Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1079
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 cross-candidate collision refused on save | N/A — boundary (AST-1080 enforce) |
| AC2 within-candidate dedupe on save | N/A — boundary (AST-1080) |
| AC3 fields + compare modes driven by config | Stage 1 — `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` paths + `compare` |
| AC4 clear domain error to callers | N/A — boundary (AST-1080) |
| AC5 Style D debug on touched save paths | N/A — boundary (AST-1080) |
| AC6 bind/lookup usable; shared email vocabulary | Stage 1 — `email_paths` / `slack_user_id_paths` shared by identity with `CANDIDATE_LOOKUP_CONFIG` |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 uniqueness field contract in config | Purpose/Functional scope “Config names the unique set”; Architectural `pattern.config.config-block`; child AC3/AC4; parent OQ#1/#5 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Sub publish path; plan()/code() vocabulary implied |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1045/AST-1079-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1045 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Field-set Decisions cite locked parent OQs |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed + stage + Done-when |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded-confidence / consult work |
| astral.config.config-source-of-truth | conforms | New `*_CONFIG` literals; path participation + compare in config |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env; plain config literals |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features; Betty excluded |
| astral.layers.import-direction | conforms | utils-only; no illegal imports |
| astral.layers.ui-config-driven-business-logic | conforms | No UI; config vocabulary for core gate later |
| astral.standards.debug-contract-gated | conforms | No debug paths in this config-only child |
| astral.standards.dry-and-focused-functions | conforms | Email/slack path objects reused by reference from lookup |
| astral.standards.in-scope-only | conforms | Config vocabulary only; enforce/UI/library excluded |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.no-cross-contamination | conforms | Stays in utils/config |
| astral.standards.no-hardcoded-sets | conforms | Uniqueness set + compare modes live in config for AST-1080 |
| astral.standards.public-then-helpers | conforms | Config block + asserts; no scattered helpers |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import path added |
| astral.state.job-prior-states-enforced | conforms | No job-state work |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers ∩ plan {utils} empty
- astral.agent.grade-vector-validation — layers ∩ plan {utils} empty
- astral.batch.batch-id-first — layers ∩ plan {utils} empty
- astral.batch.batch-id-format — layers ∩ plan {utils} empty
- astral.batch.claim-process-release — layers ∩ plan {utils} empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan {utils} empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {utils} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan {utils} empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {utils} empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan {utils} empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan {utils} empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan {utils} empty
- astral.standards.data-raises-caller-logs — layers ∩ plan {utils} empty
- astral.standards.database-header-inventory — layers ∩ plan {utils} empty
- astral.state.core-decides-transitions — layers ∩ plan {utils} empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan {utils} empty
- astral.ui.frontend-file-placement — layers ∩ plan {utils} empty
- astral.ui.naming-conventions — layers ∩ plan {utils} empty

## Findings

None fix-now.

**discuss (non-blocking):** Uniqueness set includes `contact.slack_user_id` via shared lookup paths even though parent OQ#1 option list named emails/phone/LinkedIn/GitHub/websites (and locked “all contact info”). Plan Decision documents this as lookup identity-home alignment; acceptable.

**acceptable:** Sibling block (not a key on lookup) + identity-shared email/slack path objects; Self-assessment minor/high/low honest; enforce deferred to AST-1080.

**R6:** Definition fidelity pass (config vocabulary only). Config §2.1 / no-hardcoded-sets pass. Utils layer / import pass. No batch/state/UI/schema creep.

context_tokens≈36000

— Joan

#### chuckles — 2026-07-30T23:46:34.463Z
[thread-orphan] Joan session da0027e7-276d-4fe2-a6e6-65c8eb77e24d relocated
found: `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
expected: `/home/susan/.cursor/chats/e6a6ae7abe06cb3817928b42cbb73f1f/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`
— Chuckles

#### ada — 2026-07-30T23:46:05.192Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1045/AST-1079-unique-contact-field-contract/docs/features/candidate/ast-1079-unique-contact-field-contract.md

`origin/sub/AST-1045/AST-1079-unique-contact-field-contract` @ `3e6bf1b0`

**Scope:** minor — one utils config block (`CANDIDATE_CONTACT_UNIQUENESS_CONFIG`) + docstring/asserts; no core/data/UI.

**Conf:** high — sibling to `CANDIDATE_LOOKUP_CONFIG` with shared email/slack path objects; parent OQs lock identity-handle set and email alignment; enforce deferred to AST-1080.

**Risk:** low — no runtime callers until AST-1080; wrong paths would only misconfigure a future gate.

---

# AST-1079 — Unique-contact field contract in config

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1079/unique-contact-field-contract-in-config-verify-unique-contact-info  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info  

**Publish ref (origin):** `sub/AST-1045/AST-1079-unique-contact-field-contract`  
**Parent integration ref:** `ftr/AST-1045-verify-unique-contact-info`

Define the **config vocabulary** for which contact values participate in within-candidate dedupe and cross-candidate uniqueness, plus compare rules (casefold for emails/handles; exact for Slack user ids), as a sibling block next to `CANDIDATE_LOOKUP_CONFIG` so bind/lookup and the future save gate (AST-1080) share one email-path source. This ticket does **not** enforce uniqueness on save, touch Profile/Admin UI, or change the contact library schema.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` after `CANDIDATE_LOOKUP_CONFIG`; module-docstring inventory line; import-time asserts tying email/slack paths to lookup | utils |

---

## Stage 1: Uniqueness field contract in config

**Done when:** `from src.utils.config import CANDIDATE_CONTACT_UNIQUENESS_CONFIG` works; email paths are identical to `CANDIDATE_LOOKUP_CONFIG["email_paths"]` (including transitional `profile.*`); phone / github / linkedin_url / websites / slack_user_id participation and compare modes are readable from the block; no core, data, UI, or enforce logic exists yet.

1. In `src/utils/config.py` module docstring **Config sections** list, add one line (alphabetically near other candidate blocks is fine; place after the `CONTACT_CONFIG` line or next to candidate lookup if that inventory style is used):

```
  CANDIDATE_CONTACT_UNIQUENESS_CONFIG — contact uniqueness / within-candidate dedupe field paths + compare rules (AST-1079; sibling to CANDIDATE_LOOKUP_CONFIG)
```

2. Immediately **after** the existing `CANDIDATE_LOOKUP_CONFIG` block (the dict that ends with `slack_user_id_paths`, currently just above the `CONTACT_CONFIG` comment banner), and **before** the `CONTACT_CONFIG` banner, insert:

```python
# ---------------------------------------------------------------------------
# CANDIDATE_CONTACT_UNIQUENESS_CONFIG: save-gate field contract (AST-1079 / AST-1045).
# Vocabulary only — within-candidate dedupe + cross-candidate collision enforcement
# is AST-1080. Email / slack path tuples must stay aligned with CANDIDATE_LOOKUP_CONFIG.
# ---------------------------------------------------------------------------
CANDIDATE_CONTACT_UNIQUENESS_CONFIG = {
    # Same object as lookup — bind/lookup and uniqueness share one email vocabulary
    # (including transitional profile.* until gone).
    "email_paths": CANDIDATE_LOOKUP_CONFIG["email_paths"],
    # Non-email identity handles under the AST-1014 contact blob.
    "scalar_paths": (
        "contact.phone",
        "contact.github",
        "contact.linkedin_url",
    ),
    # List-valued contact fields: each non-empty entry is one uniqueness token.
    "list_paths": (
        "contact.websites",
    ),
    # Same object as lookup Slack homes (AST-1066 / AST-1068).
    "slack_user_id_paths": CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"],
    # Compare mode per path group. Enforcement (AST-1080) must:
    #   - strip whitespace on all string values before compare
    #   - for "casefold": compare with str.casefold()
    #   - for "exact": compare stripped strings as-is (no casefold)
    #   - skip empty / missing values (not uniqueness tokens)
    "compare": {
        "email": "casefold",
        "scalar": "casefold",
        "list": "casefold",
        "slack_user_id": "exact",
    },
    # Both scopes use the same path set. Semantics of refuse vs collapse are AST-1080
    # (parent OQ: avoid adding the same contact info twice; hard-fail cross-candidate).
    "scopes": (
        "within_candidate",
        "cross_candidate",
    ),
}
```

⚠️ **Decision — sibling block, not a key on `CANDIDATE_LOOKUP_CONFIG`:** Lookup is string→id match homes; uniqueness is save-gate participation + compare modes + list vs scalar shape. A sibling keeps lookup callers unchanged and avoids teaching every lookup reader about save scopes. Email/slack path **objects** are shared so the vocabularies cannot drift.

⚠️ **Decision — “all contact info” = identity handles from parent OQ options:** Parent OQ#1 listed emails / phone / LinkedIn / GitHub / websites and locked “All contact info.” Uniqueness-scoped set is those plus `contact.slack_user_id` (already a lookup identity home). **Not** in the uniqueness set: `location`, `timezone`, `cover_letter_signature`, `cover_letter_signature_image`, `title_patterns`, `reason_codes` — those are contact-blob keys but not identity handles in the OQ list.

⚠️ **Decision — transitional `profile.*` only on emails:** Parent AC#4 / OQ#5 require alignment with `CANDIDATE_LOOKUP_CONFIG` email paths (including transitional `profile.*`). Non-email uniqueness paths are `contact.*` only; do not invent `profile.phone` / `profile.websites` mirrors here.

⚠️ **Decision — compare modes:** Emails/handles use `casefold` (same intent as `CANDIDATE_LOOKUP_CONFIG["match_casefold"] is True`). Slack user ids use `exact` after strip (Slack ids are opaque tokens; do not casefold). Do **not** invent phone digit-normalization or URL canonicalization beyond strip+casefold in this ticket — `normalize_contact_urls` remains library coercion (AST-1014); AST-1080 may call it before uniqueness compare if the save path already does.

3. Immediately after the new block, add import-time asserts (same style as neighboring config asserts):

```python
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_paths"] is CANDIDATE_LOOKUP_CONFIG["email_paths"]
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["slack_user_id_paths"] is CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["compare"]["email"] == "casefold"
assert CANDIDATE_LOOKUP_CONFIG["match_casefold"] is True  # email uniqueness must stay casefold while lookup is
assert isinstance(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"], tuple) and CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"]
assert isinstance(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"], tuple) and CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scopes"] == ("within_candidate", "cross_candidate")
for _p in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"]:
    assert isinstance(_p, str) and _p.startswith("contact."), _p
for _p in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]:
    assert isinstance(_p, str) and _p.startswith("contact."), _p
_contact_key_set = set(CANDIDATE_LIBRARY_CONFIG["contact_keys"])
for _p in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"] + CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]:
    _key = _p.split(".", 1)[1]
    assert _key in _contact_key_set, _p
for _mode in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["compare"].values():
    assert _mode in ("casefold", "exact"), _mode
```

4. Do **not** edit `src/core/candidate.py`, `src/data/database.py`, UI, or any enforce/dedupe helpers. Do **not** add keys to `CANDIDATE_LOOKUP_CONFIG`. Do **not** change `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`. Do **not** register callers of the new block (AST-1080 owns that).

**Done when (recheck):** In a Python shell from repo root with `PYTHONPATH=.` (or the project’s usual import path):

```python
from src.utils.config import (
    CANDIDATE_CONTACT_UNIQUENESS_CONFIG,
    CANDIDATE_LOOKUP_CONFIG,
)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_paths"] == (
    "contact.contact_email",
    "contact.reply_email",
    "profile.contact_email",
    "profile.reply_email",
)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"] == (
    "contact.phone",
    "contact.github",
    "contact.linkedin_url",
)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"] == ("contact.websites",)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["slack_user_id_paths"] == ("contact.slack_user_id",)
```

---

## Self-Assessment

**Scope:** `minor` — one new utils config block + docstring/asserts; no core/data/UI.

**Conf:** `high` — mirrors `CANDIDATE_LOOKUP_CONFIG` / `CONTACT_CONFIG` sibling pattern; parent OQs lock field set and email alignment; enforce semantics deferred to AST-1080.

**Risk:** `low` — no callers until AST-1080; wrong paths would only misconfigure a future gate, not change runtime behavior in this ticket.

---

## Code Rules check (§8)

| Rule | Result |
|------|--------|
| §1.3 DRY | Email/slack path tuples reused by reference from `CANDIDATE_LOOKUP_CONFIG`; no second hardcoded email list |
| §2.1 config source of truth | New `*_CONFIG` block; literals only; no `os.environ` |
| §1.4 no-hardcoded-sets | Uniqueness participation lives in config for AST-1080 to read |
| §2.4 batch / §2.6 state machine | N/A — config vocabulary only |
| §3.3 imports | No new modules; utils-only change |
| §3.5 naming | `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` matches candidate + concern naming |

No conflicts requiring `conf-!!-NONE`.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-1079 |
| Publish ref | `origin/sub/AST-1045/AST-1079-unique-contact-field-contract` |
| Built | `fb4cd6e02c39ada87e5628f1177739f3cd536d8a` |
| Notes | Stage 1 — `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` sibling to lookup; email/slack path objects shared by identity. |

### Radia — code-rubric.v1

`[code-rubric] revision=1` · **Overall:** DISCUSS (stragglers only; product CLEAN)

**What’s solid**
- Sibling `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` matches plan Stage 1 verbatim: email/slack path objects shared by identity with `CANDIDATE_LOOKUP_CONFIG`; scalar/list paths + compare/scopes as specified; import-time asserts lock alignment and `contact_keys` membership.
- No core/data/UI/enforce creep — AST-1080 boundary held.
- Engineer `code()` touched only `src/utils/config.py`; Betty owns `test()` / `merge-tests`.

**Issues**
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot diff vs `origin/dev` brings `docs/features/**` + Betty test-tree paths in scope. All three score **conforms** on this diff — no product fix.

**Recommended actions**
- Ada: no code change required for stragglers; proceed `resolve-child` → User Testing unless a discuss thread is opened.
- Full statutes-checked table + Linear comment on AST-1079.

## Resolution

**Date:** 2026-07-30  
**Review tip:** `249a8a37` (`docs(AST-1079): Radia review — uniqueness field contract`)  
**Outcome:** clean — no fix-now; no product or config changes.

| Finding | Disposition |
| -- | -- |
| discuss (straggler) — Joan excluded spike/docs/engineer-test-tree-ban at plan time; three-dot diff scores conforms | Accepted as documented; no code or plan vocabulary change |
| Joan non-blocking discuss — `slack_user_id` in uniqueness via shared lookup paths | Left as plan Decision; not reopened |
