# AUTH_CONFIG Stytch session rules + SPA-readable policy

**Linear:** [AST-1373](https://linear.app/astralcareermatch/issue/AST-1373)
**Parent:** [AST-1372](https://linear.app/astralcareermatch/issue/AST-1372) — Extend Stytch sessions
**Publish ref:** `sub/AST-1372/AST-1373-auth-config-stytch-session-rules`

Put Stytch client session lifetime and activity-extension cadence in `AUTH_CONFIG` as non-secret literals, and expose only those values on a deliberately public Flask endpoint so the SPA (sibling AST-1374) can read the same policy before Bearer login on authenticate handoff and after login for the extend loop.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `session_duration_minutes` / `activity_extension_interval_minutes` to `AUTH_CONFIG`; add `get_auth_session_policy()` that returns only those two ints | utils |
| `src/ui/api/api_system.py` | New open (no `@require_auth`) `GET /api/auth_session_policy` returning the policy JSON | ui |

**Out of this ticket (do not touch):** React authenticate / extend call sites (`stytchAuthenticateHandoff.ts`, `AuthContext.tsx`, etc.) — sibling **AST-1374**. Stytch Dashboard, JWT validation (`src/external/stytch.py`), admin lists, `/api/me`, log-off UX.

## Stage 1: AUTH_CONFIG session literals + SPA-safe helper

**Done when:** `AUTH_CONFIG` contains `session_duration_minutes: 20` and `activity_extension_interval_minutes: 10` as plain int literals (not `os.environ`); `get_auth_session_policy()` returns exactly those two keys as ints and never includes secrets or admin lists.

1. In `src/utils/config.py`, update the module header inventory line for `AUTH_CONFIG` so it mentions session duration / activity-extension cadence (AST-1373) in addition to Stytch credentials and admin lists.
2. In the `AUTH_CONFIG` block (after the existing `stytch_project_id` / `stytch_secret` entries), add exactly these keys as **plain literals** (not env lookups — they are not secrets and not environment-specific):
   - `"session_duration_minutes": 20`
   - `"activity_extension_interval_minutes": 10`
3. Keep existing keys and `_parse_csv_env` / `os.environ.get` behavior for admin lists and Stytch credentials unchanged.
4. Immediately after `get_auth_config()`, add:

```python
def get_auth_session_policy() -> Dict[str, int]:
    """Non-secret Stytch session policy for SPA (AST-1373). Never include secrets."""
    return {
        "session_duration_minutes": int(AUTH_CONFIG["session_duration_minutes"]),
        "activity_extension_interval_minutes": int(
            AUTH_CONFIG["activity_extension_interval_minutes"]
        ),
    }
```

5. Do **not** change `get_auth_config()` return shape beyond the new keys appearing when callers copy the full dict (existing callers that only read admin/stytch keys remain valid).

⚠️ **Decision:** Defaults are **20** (session lifetime minutes) and **10** (extend cadence minutes) per parent AST-1372 brief / child AC. Cadence must stay shorter than duration; if a future UAT pass retunes, change only these two literals.

⚠️ **Decision:** Policy lives on `AUTH_CONFIG` itself (not a nested sub-dict) so callers keep the existing flat-block pattern (`pattern.config.config-block`). Key names are explicit enough without nesting.

## Stage 2: Public session-policy API for pre-login SPA reads

**Done when:** Unauthenticated `GET /api/auth_session_policy` returns HTTP 200 JSON `{"session_duration_minutes": 20, "activity_extension_interval_minutes": 10}` (or whatever the config literals currently are); response never contains `stytch_secret`, `stytch_project_id`, admin emails/ids, or other AUTH_CONFIG secrets; existing `@require_auth` endpoints are unchanged.

1. In `src/ui/api/api_system.py`, import `get_auth_session_policy` from `src.utils.config` (add to the existing `src.utils.config` import list).
2. Under the comment `# --- Open endpoints (no auth) ---` (immediately after the existing `health` route, still **before** `# --- Authenticated endpoints ---`), add:

```python
@system_bp.route("/auth_session_policy")
def auth_session_policy():
    """Non-secret session duration + extend cadence for SPA (AST-1373). Public on purpose."""
    return jsonify(get_auth_session_policy())
```

3. Do **not** decorate this route with `@require_auth` or `@require_admin`.
4. Do **not** fold this payload into `GET /api/ui_config` (that route stays authenticated). Authenticate handoff must be able to fetch policy with no Bearer token.
5. Do **not** log the response body or AUTH_CONFIG contents from this handler.

⚠️ **Decision:** Dedicated open route `GET /api/auth_session_policy` rather than stripping auth from `/api/ui_config`. Statute `astral.idioms.require-auth-on-protected-endpoints` allows an explicitly public non-secret read; a dedicated route keeps the exception obvious and avoids leaking the rest of `UI_CONFIG` pre-login.

### Contract for sibling AST-1374 (do not implement here)

| Field | Type | Meaning |
|-------|------|---------|
| `session_duration_minutes` | int | Pass to Stytch `authenticateByUrl` / `session.authenticate` as `session_duration_minutes` |
| `activity_extension_interval_minutes` | int | SPA timer cadence between successful extends while a client session exists |

SPA must replace the hardcoded `SESSION_DURATION_MINUTES = 60` in `stytchAuthenticateHandoff.ts` by reading this endpoint — that replacement is **AST-1374**, not this ticket.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review (build)

**Built @ `b722667f`** — `origin/sub/AST-1372/AST-1373-auth-config-stytch-session-rules`

- Stage 1: `AUTH_CONFIG` `session_duration_minutes: 20` / `activity_extension_interval_minutes: 10`; `get_auth_session_policy()`
- Stage 2: open `GET /api/auth_session_policy` (no `@require_auth`)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1373
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1372/AST-1373-auth-config-stytch-session-rules` @ `2fa02d7869802800436a5ddbed3d0ade95d16160`

## Traceability
AC1→Stage 1; AC2→Stage 1 (+ dedicated helper); AC3→Stage 2 — parent authenticate/extend/regression AC deferred to AST-1374 per child boundaries.

## Findings

### acceptable — missing `## Self-Assessment`
**Location:** plan doc tail  
**Finding:** No formal self-assessment block (scope/conf axes).  
**Recommendation:** Optional at this footprint; engineer may add at build if Betty/Radia need it — not blocking.

context_tokens≈18500

---

[plan-rubric] PROCEED (Commit: 2fa02d78) Config policy API ready

AST-1373 plan approved.

---

**Gate check:** Plan Ready, assignee Joan — OK. No `[plan-discuss]` rounds.

**R5 / definition fidelity:** Two-file footprint (`config.py`, `api_system.py`) matches child scope. All three child AC map to Stages 1–2. Parent functional items for authenticate handoff, activity extend, and regression are explicitly out-of-scope (AST-1374). Boundaries honored (no React, Stytch Dashboard, JWT, log-off UX).

**R6 highlights:** Layer imports clean (`ui` → `utils` only). Session literals are plain ints in `AUTH_CONFIG`, not env lookups (`astral.config.secrets-and-env-specific-from-environ`). Dedicated public `GET /api/auth_session_policy` with no `@require_auth` is an explicit, documented exception (`astral.idioms.require-auth-on-protected-endpoints`); does not strip auth from `/api/ui_config`. `get_auth_session_policy()` returns only the two non-secret ints. `pattern.config.config-block` shape matches flat `AUTH_CONFIG` extension. Sibling contract table documents AST-1374 consumption.

**In-session R3/R4 (slim R7):** 14 universal orchestration statutes — all `conforms` (plan is docs-shaped workflow; no git/test-tree violations). Scoped considered: `astral.config.config-source-of-truth`, `astral.config.secrets-and-env-specific-from-environ`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, `astral.standards.public-then-helpers`, `astral.standards.dry-and-focused-functions`, `astral.standards.no-cross-contamination`, `astral.standards.names-not-ticket-ids`, `astral.ui.naming-conventions` — all `conforms`. Representative exclusions: `astral.standards.database-header-inventory` (no `data` layer); `astral.batch.*` / `astral.agent.*` / `astral.state.*` (no batch/agent/state touch); `astral.ui.frontend-file-placement` (no `frontend/` paths).

## Radia review

# Radia review — AST-1373

**Status gate:** Tests Passed (spawn prompt; trusted).  
**Baseline:** `origin/dev`  
**Publish ref:** `origin/sub/AST-1372/AST-1373-auth-config-stytch-session-rules` @ `f23fabf0`  
**Diff:** 7 files — `src/utils/config.py`, `src/ui/api/api_system.py`, Betty test-tree + plan doc (265 insertions, 1 deletion)

---

```
[code-rubric] revision=2
```

**Rubric:** code-rubric.v2  
**Ticket:** AST-1373  
**Publish ref:** `f23fabf0a29b9b9eca997e83678f39ec42706fa0`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single `merge-tests(AST-1373)` @ `f23fabf0` pins `origin/tests` `af078462`. |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `merge-tests` / `docs` commits use standard vocabulary. |
| `orch.git.flow-direction-inviolable` | universal | conforms | Product on `sub/*`; tests merged from `origin/tests`. |
| `orch.git.ftr-sub-topology` | universal | conforms | Child publish ref `sub/AST-1372/AST-1373-…` correct. |
| `orch.git.merge-on-checkout` | universal | conforms | No merge/checkout violation in commit history. |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history; no rebase/force evidence. |
| `orch.git.no-dev-agent-branches` | universal | conforms | No agent-prefixed publish refs. |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1372 epic worktree pattern honored. |
| `orch.git.three-permanent-branches` | universal | conforms | `dev` / `tests` / `main` topology respected. |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | 20/10 defaults pre-decided in plan/parent; no new product forks. |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 implemented as written. |
| `orch.pipeline.project-scoped-queues` | universal | conforms | N/A to diff substance. |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child gate satisfied. |
| `orch.roles.archie-approves-statutes` | universal | conforms | N/A to diff substance. |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty `test(AST-1373)` + one `merge-tests`; engineer `code` commit `src/` only. |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | N/A to diff substance. |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada assignee; review does not reassign. |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Engineer commit `b722667f` touches only `src/`. |
| `astral.agent.confidence-bounds` | scoped | not-applicable | No `src/core/**` agent grading paths. |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No dispatch/agent delegation changes. |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector paths. |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch layer. |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch layer. |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/process/release paths. |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No batch responses paths. |
| `astral.config.config-source-of-truth` | scoped | conforms | Session literals live in `AUTH_CONFIG`; SPA reads via API. |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | New keys are plain int literals; Stytch creds still `os.environ.get` (pre-existing). |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No `debug/**` or artifacts-dir paths. |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike/debug paths. |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch/seed paths. |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No run-next/dispatcher paths. |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Plan at `docs/features/foundation/ast-1373-….md`. |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commit `af078462` — test-bible + `tests/` only. |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer `b722667f` — `src/` only; test tree via Betty merge. |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | No `core` or `external` layer changes. |
| `astral.layers.import-direction` | scoped | conforms | `api_system.py` imports `get_auth_session_policy` from `utils` only. |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/**` changes. |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Policy served from config helper, not hardcoded in handler. |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check/session-store paths. |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No render/consult paths. |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | Deliberate open route under `# --- Open endpoints ---`; docstring + plan exception. |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed/admin JSON paths. |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No seed paths. |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No seed boot paths. |
| `astral.seed.define-approved` | scoped | not-applicable | No seed define paths. |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No seed operator paths. |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No seed coverage paths. |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No `data` layer. |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No `src/data/**` (Joan excluded — no straggler). |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | No `debug=` surfaces added. |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Thin `get_auth_session_policy()` + one-line route handler. |
| `astral.standards.in-scope-only` | scoped | conforms | No React, `stytch.py`, JWT, or AST-1374 call sites. |
| `astral.standards.logging-via-utils` | scoped | conforms | Handler does not log policy body (per plan). |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Domain names (`auth_session_policy`, `get_auth_session_policy`). |
| `astral.standards.no-cross-contamination` | scoped | conforms | Dedicated policy helper isolates non-secret surface from `get_auth_config()`. |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | 20/10 literals in `AUTH_CONFIG`, not scattered in UI/core. |
| `astral.standards.public-then-helpers` | scoped | conforms | `get_auth_session_policy()` placed immediately after `get_auth_config()`. |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No utils→data late import. |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state/tracker paths. |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state paths. |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run/daisy-chain paths. |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | No `frontend/**` (Joan excluded — no straggler). |
| `astral.ui.naming-conventions` | scoped | conforms | Route `/auth_session_policy` matches existing snake_case API style. |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No server/worker config changes. |

**Sweep count:** 65 active statutes scored (1 retired `astral.config.pass-threshold-vs-score-floor` ignored).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | Extends flat `AUTH_CONFIG` with non-secret literals; dedicated `get_auth_session_policy()` for SPA-safe subset; secrets stay env-backed. |

## Plan adherence

- **Stage 1:** `AUTH_CONFIG` header inventory updated; `session_duration_minutes: 20`, `activity_extension_interval_minutes: 10` as plain literals; `get_auth_session_policy()` returns exactly two int keys.
- **Stage 2:** Open `GET /api/auth_session_policy` placed after `health`, before authenticated block; no `@require_auth`; imports from existing `src.utils.config` block.
- **Estimate 2:** Footprint matches — two `src/` files + tests/docs; no scope creep.
- **AST-1374 boundary:** No `stytchAuthenticateHandoff.ts`, `AuthContext.tsx`, `src/external/stytch.py`, or dashboard work.
- **Joan straggler (C4):** Joan verdict attached; excluded statutes (`database-header-inventory`, `batch.*`, `agent.*`, `state.*`, `frontend-file-placement`) all `not-applicable` on diff — no straggler.

## C6 judgment aids (§5a)

| Topic | Result |
|-------|--------|
| Imports (B1) | Module-top import in `api_system.py`; test-local `from src.utils import config` inside monkeypatch test only — acceptable in test tree. |
| Layer compliance (B2) | `ui` → `utils` only. |
| Silent failure (D2) | None introduced. |
| Fallbacks (D3) | `int()` coercion on config values is bounded (literals are ints); no `or {}` masking. |
| Logging (E1) | No `print()` / ad-hoc logging in new handler. |
| Config in UI (G1) | Business policy read from config helper. |
| §5f debug | Not triggered. |
| §5g external | Not triggered. |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**
- **Response style consistency** — `health()` returns a bare dict; `auth_session_policy()` uses `jsonify()`. Both work under Flask; aligning style is optional polish, not blocking.
- **Invariant enforcement** — Plan documents cadence &lt; duration; tests assert at defaults only. Retuning literals without updating both could ship an invalid pair; acceptable at this footprint — AST-1374/UAT can catch if needed.

## What's solid

- Clean separation: `get_auth_session_policy()` never exposes secrets; tests assert forbidden keys absent.
- Betty workflow correct: engineer `src/` only → Betty `test` on `origin/tests` → single `merge-tests`.
- Tests cover open route (no Bearer), default payload, and monkeypatched config reflection on both helper and route.
- Module header inventory updated per plan.

## Frame diff

(none)

## Notes

- Joan plan-rubric verdict attached @ `2fa02d78`; no straggler.
- Tests/test-bible in three-dot diff ride Betty `merge-tests` SHA — not engineer scope creep.
- C7 complete; Chuckles may append to issue doc, commit `docs(AST-1373): Radia review — clean`, post slim upshot, advance to **Review Posted** → **User Testing** (PROCEED path).

context_tokens≈24000

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] PROCEED (Commit: f23fabf0) Session policy API clean
```
