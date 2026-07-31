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
