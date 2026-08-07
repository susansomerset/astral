<!-- linear-archive: AST-1033 archived 2026-08-05 -->

## Linear archive (AST-1033)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1033/read-email-admin-screen-ingest-seed-receive-email-on-gmail-account-for  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** High / —  
**Parent:** AST-1031 — Receive email on gmail account for astral  
**Blocked by / blocks / related:** parent: AST-1031

### Description

## What this implements

Owns authenticated admin API + **Read email** nav/screen: inbox list, click-through scrollable HTML body modal. Leaves this surface as the seed for a later Meteorite ingest epic (no ingest logic here). Does **not** own Gmail credential/scope plumbing (sibling AST-1032). After AST-1032.

## Citations

`pattern.ui.admin-endpoint`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.layers.import-direction`.

## Acceptance criteria

1. An authenticated admin can open **Read email** from admin nav and see a list of inbox messages for `astral.career.match@gmail.com` (read and unread).
2. Clicking a listed message opens a scrollable modal showing that message’s HTML body as returned by Gmail.
3. Unauthenticated callers cannot access the list or message-body endpoints/screens.

## Boundaries

Does **not** own Gmail OAuth/scope/token plumbing (AST-1032). Does **not** implement ingest/routing. Does **not** persist email bodies.

## Notes for planning

Auth-gated admin seed UI calling core APIs from AST-1032.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1031-receive-email-on-gmail-account-for-astral`, child `sub/AST-1031/AST-1033-read-email-admin-screen`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T05:09:17.067Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1033
**Publish ref:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen` @ `18b09a64` (product tip `a94497cc` + docs review)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1031/AST-1033-read-email-admin-screen` — 1033 ui/utils + carried AST-1032 core/external (blocked-by already reviewed).
**Notes:** Joan plan-rubric attached (APPROVED). C4 stragglers from three-dot including AST-1032 paths; all score **conforms** on substance. No fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence logic in admin inbox path |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` / agent path |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | No batch/entity work |
| astral.batch.batch-id-format | scoped | conforms | No batch ids |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Nav path/label in `NAV_CONFIG` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No new secrets; Gmail OAuth stays AST-1032 |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (`artifacts/**` / `scripts/spikes/**`) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plans under `docs/features/` — not misplaced spikes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file per ticket (1032 + 1033) |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns src/features; Betty owns tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | `test()`/`merge-tests()` are Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Gmail I/O in external (1032); UI calls core only |
| astral.layers.import-direction | scoped | conforms | `api_inbox` → core + utils + `ui.auth`; no ui→external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss (`scripts`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Nav from `NAV_CONFIG`; React renders API payloads |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check / persistence |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` both endpoints; `AdminRoute` screen |
| astral.standards.data-raises-caller-logs | scoped | conforms | API catches, logs, returns JSON 502 |
| astral.standards.database-header-inventory | scoped | not-applicable | layers miss (`data`) |
| astral.standards.debug-contract-gated | scoped | conforms | No new Style D `debug=` surface |
| astral.standards.dry-and-focused-functions | scoped | conforms | Thin handlers; no duplicated Gmail logic |
| astral.standards.in-scope-only | scoped | conforms | No ingest/persist/Gmail plumbing in 1033 commits |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` in `api_inbox` |
| astral.standards.no-cross-contamination | scoped | conforms | Layered seed surface |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new behavior enums in React |
| astral.standards.public-then-helpers | scoped | conforms | Route handlers only |
| astral.standards.utils-data-late-import-only | scoped | conforms | `config.py` nav-only; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | Display-only; no state machine |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | conforms | Flat `pages/AdminReadEmail.tsx`; CSS in `App.css` |
| astral.ui.naming-conventions | scoped | conforms | PascalCase page; snake_case path/API |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1033)` @ `a94497cc` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests`/`resolve` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child work on `sub/*` |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1031/AST-1033-read-email-admin-screen` |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/...` already ancestor before docs() |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1031` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Sandbox iframe + 502 mapping already in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match shipped 1033 code |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible on publish ref |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.ui.admin-endpoint` | conforms — dedicated `api_inbox` under `/api/admin/inbox` + `@require_admin` |
| `astral.patterns.require-auth-on-protected-endpoints` | conforms — endpoints + `AdminRoute` |
| `astral.layers.ui-config-driven-business-logic` | conforms — `NAV_CONFIG` + API-driven table |
| `astral.layers.import-direction` | conforms — ui→core+utils; never external |

## Plan adherence

1033 Stages 1–2 match Self-Assessment **Single-Component**. Nav, blueprint registration, list/get 502 mapping, sandboxed iframe modal, and route placement match the plan bible. No ingest/persist smuggling. Three-dot also carries AST-1032 (blocked-by) already reviewed on AST-1032.

## Findings

### fix-now
(none)

### discuss
**straggler (Joan excluded → in-scope on three-dot; substance conforms):**
1. `astral.agent.do-task-delegation`
2. `astral.agent.grade-vector-validation`
3. `astral.batch.batch-id-first`
4. `astral.batch.batch-id-format`
5. `astral.batch.claim-process-release`
6. `astral.batch.entity-agent-responses-latest-only`
7. `astral.debug.spikes-under-debug-dir`
8. `astral.docs.features-single-file-per-ticket`
9. `astral.git.engineer-test-tree-ban`
10. `astral.layers.core-vs-external-bright-line`
11. `astral.patterns.coat-check-never-store-empty`
12. `astral.patterns.render-verdict-orchestrates-consult`
13. `astral.state.core-decides-transitions`
14. `astral.state.no-daisy-chain-in-run`

Cause: three-dot includes AST-1032 core/external/tests/docs; Joan’s plan-time Files Changed were ui+utils only.

### advisory
- Empty-array fallback when list JSON lacks `messages` is defensive UI; acceptable for seed.

### What’s solid
- Auth on API + screen; sandboxed HTML preview; thin core wrappers; NAV sync with routes.

### Recommended actions
- Hedy: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

context_tokens≈48000

#### betty — 2026-07-29T05:06:39.751Z
1. `tests/component/ui/api/test_api_inbox.py` — list/get 200/400/502 + 401/403
2. `tests/component/utils/test_config.py::TestAst1033ReadEmailNav` — NAV after Session Cover Letter
3. `tests/component/frontend/pages/test_AdminReadEmail.test.tsx` — §6c page: list, modal iframe, errors

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py \
  tests/component/utils/test_config.py::TestAst1033ReadEmailNav

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminReadEmail.test.tsx
```

**Pass:** pytest + Vitest green on narrowed args.

**Broken/revised:** none additive — `inbox_client` fixture in `tests/component/ui/conftest.py`.
**Integration:** no existing scenarios for Read email / `/api/admin/inbox/*` — none revised.

**Publish:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen` @ `a94497cc` (`merge-tests(AST-1033): origin/tests f53b9d0a8dc852516f520307186984730e200451`)

**Bible shasums on publish ref:**
- `docs/test-bible/ui/api/api_inbox.md` `e20cc8bd6c550f13e673ee566f1eb06637a0f67b`
- `docs/test-bible/frontend/pages.md` `2c9e3f166451735329aedb4cda32322171ed7c05`
- `docs/test-bible/utils/config.md` `f3e88f08dfc5d232a69aa3981759451e1bb36b9f`

— Betty

#### joan — 2026-07-29T04:58:53.592Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1033
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `bf79e945`. Layers `ui` + `utils`. Blocked-by AST-1032; plan calls `src.core.inbox` only (no ui→external).
**Implementer:** Hedy (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Admin opens Read email + sees inbox list | Stages 1–2 (NAV + list API + AdminReadEmail table) |
| 2 Click → scrollable HTML modal | Stage 2 (wide Modal + sandboxed iframe) |
| 3 Unauthenticated cannot access list/body endpoints/screens | Stage 1 `@require_admin` + Stage 2 `AdminRoute` |
| 4 Monitor send dual-scope token | N/A — boundary: AST-1032 |
| 5 Controlled external I/O gate | N/A — boundary: AST-1032 (failures surface as 502) |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Nav + inbox list (read+unread) | 1–2 |
| 2 Click → scrollable HTML modal | 2 |
| 3 Unauthenticated blocked | 1–2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 NAV_CONFIG + `api_inbox` + register blueprint | Functional scope admin surface; Architectural admin-endpoint / require-auth; import-direction |
| 2 AdminReadEmail + route + CSS | Functional scope list + modal; Boundaries (no ingest/persist/Gmail plumbing) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan docs on child sub |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No skip-ftr procedure |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1031` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Sandbox iframe + 502 mapping documented; no product ambiguity |
| orch.pipeline.plan-is-bible | conforms | Stages binding; Gmail/ingest excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Hedy on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Nav path/label in NAV_CONFIG |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No new secrets; Gmail stays AST-1032 |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/features |
| astral.layers.import-direction | conforms | ui → core + utils + ui.auth; never external/data |
| astral.layers.ui-config-driven-business-logic | conforms | Nav from NAV_CONFIG; React renders API payloads |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_admin` on both endpoints; `AdminRoute` on screen |
| astral.standards.data-raises-caller-logs | conforms | API catches, logs, returns JSON 502 |
| astral.standards.debug-contract-gated | conforms | No new Style D debug |
| astral.standards.dry-and-focused-functions | conforms | Thin handlers; no duplicated Gmail logic |
| astral.standards.in-scope-only | conforms | Excludes AST-1032 plumbing, ingest, persist, tests |
| astral.standards.logging-via-utils | conforms | `get_logger` in api_inbox |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | No new behavior enums in React |
| astral.standards.public-then-helpers | conforms | Route handlers only |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.ui.frontend-file-placement | conforms | Flat `pages/AdminReadEmail.tsx`; styles in App.css |
| astral.ui.naming-conventions | conforms | PascalCase page; snake_case path/API |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.batch.* (4) — layers/paths miss
- astral.debug.* (2) — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss (Gmail I/O stays AST-1032)
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.state.core-decides-transitions — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Dedicated `api_inbox` blueprint under `/api/admin/inbox` — separable Meteorite seed; auth still `@require_admin`.
2. Sandboxed iframe (`sandbox=""`) instead of `dangerouslySetInnerHTML` — correct XSS posture for foreign HTML.
3. Wide modal already `height: 90vh` + flex body — iframe `height: 100%` satisfies scrollable HTML preview.
4. No list pagination UI — full array from AST-1032 matches parent “every message”.
5. Self-assessment Single-Component / high / Medium — honest about auth exposure risk.

— Joan
context_tokens≈78000

#### hedy — 2026-07-29T04:57:14.128Z
Plan published on `origin/sub/AST-1031/AST-1033-read-email-admin-screen` @ `bf79e945`.

**Plan:** [docs/features/meteorite/ast-1033-read-email-admin-screen.md](https://github.com/susansomerset/astral/blob/sub/AST-1031/AST-1033-read-email-admin-screen/docs/features/meteorite/ast-1033-read-email-admin-screen.md)

**Self-assessment**
- **Scope:** Single-Component — admin UI only: NAV entry, thin `api_inbox` blueprint over existing `src.core.inbox`, one React page + route + CSS; no external/data/secret changes.
- **Conf:** high — same `@require_admin` + `AdminRoute` seed pattern as Session Resume; AST-1032 list/get contracts already on ftr.
- **Risk:** Medium — auth miss would expose mailbox content; mitigated by `@require_admin`, `AdminRoute`, and sandboxed iframe (`sandbox=""`).

---

# AST-1033 — Read email admin screen (ingest seed)

**Linear:** [AST-1033](https://linear.app/astralcareermatch/issue/AST-1033/read-email-admin-screen-ingest-seed-receive-email-on-gmail-account-for)
**Parent:** [AST-1031](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral) — Receive email on gmail account for astral
**Publish ref:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen`

Auth-gated admin API + **Read email** nav/screen: list every INBOX message for `GMAIL_USER` (read + unread), click one, show its HTML body in a scrollable modal. Calls AST-1032’s `src.core.inbox` only — UI never imports `src.external.gmail`. Seed surface for a later Meteorite ingest epic; no ingest, persistence, or Gmail credential work here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Admin nav item **Read email** → `/admin/read_email` | utils |
| `src/ui/api/api_inbox.py` | New blueprint: list + get-html admin endpoints, `@require_admin` | ui |
| `src/ui/server.py` | Register `inbox_bp` | ui |
| `src/ui/frontend/src/pages/AdminReadEmail.tsx` | New admin page: inbox table + HTML body modal | ui |
| `src/ui/frontend/src/routes.tsx` | Route `admin/read_email` under `AdminRoute` | ui |
| `src/ui/frontend/src/App.css` | `.email-html-frame` so wide-modal iframe fills and scrolls | ui |

## Stage 1: Nav + auth-gated inbox API

**Done when:** `NAV_CONFIG` exposes **Read email**; `GET /api/admin/inbox/messages` and `GET /api/admin/inbox/messages/<message_id>` return JSON from `src.core.inbox` under `@require_admin`; unauthenticated callers get 401 and non-admins get 403; UI module never imports external/data.

1. In `src/utils/config.py`, inside the Admin group of `NAV_CONFIG` (after **Session Cover Letter**), append:

```python
{"label": "Read email", "path": "/admin/read_email"},
```

Keep the existing SYNC comment contract with `routes.tsx` — do not rename the path after this step.

2. Create `src/ui/api/api_inbox.py` with module docstring:

```
Read-email admin API (AST-1033 / Meteorite seed).

Thin Flask wrappers over src.core.inbox. No Gmail I/O here; no persistence.
```

3. In that file, define:

```python
from flask import Blueprint, jsonify

from ui.auth import require_admin
from src.core.inbox import get_message_html, list_inbox_messages
from src.utils.logging import get_logger

logger = get_logger(__name__)

inbox_bp = Blueprint("inbox", __name__, url_prefix="/api/admin/inbox")
```

⚠️ **Decision:** Dedicated `api_inbox.py` blueprint (not more routes stuffed into `api_admin.py`) so this Meteorite seed stays a separable UI surface for the later ingest epic. Prefix stays under `/api/admin/…` so `@require_admin` matches every other admin tool.

4. Add `GET ""` route? No — use explicit paths:

```python
@inbox_bp.route("/messages", methods=["GET"])
@require_admin
def inbox_list_messages():
    try:
        messages = list_inbox_messages()
    except Exception as e:
        logger.warning("[api_inbox] list failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify({"messages": messages}), 200


@inbox_bp.route("/messages/<message_id>", methods=["GET"])
@require_admin
def inbox_get_message(message_id: str):
    mid = (message_id or "").strip()
    if not mid:
        return jsonify({"error": "message_id is required"}), 400
    try:
        payload = get_message_html(mid)
    except Exception as e:
        logger.warning("[api_inbox] get failed id=%s: %s", mid, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(payload), 200
```

Response contracts (match AST-1032 TypedDicts; do not reshape keys):

- List: `{"messages": [{"id", "thread_id", "subject", "from_address", "date", "unread"}, ...]}`
- Get: `{"id": "<message_id>", "html_body": "<html or empty string>"}`

⚠️ **Decision:** Map core/external failures to **502** (upstream Gmail / controlled-I/O / OAuth), not 500. Empty `html_body` is a successful 200 — do not invent plain-text HTML.

5. In `src/ui/server.py`, after the existing `admin_bp` registration block, register the new blueprint:

```python
from ui.api.api_inbox import inbox_bp  # noqa: E402
app.register_blueprint(inbox_bp)
```

Follow the same `# noqa: E402` style as neighboring blueprint imports.

6. Do **not** import `src.external.gmail` or `src.data.*` from this module. Do **not** add mark-read, archive, delete, label, or persistence.

**Done when (recheck):** Admin JWT can hit both endpoints; missing/invalid session → 401; authenticated non-admin → 403; list returns `messages` array; get returns `id` + `html_body`.

## Stage 2: Read email admin page + modal

**Done when:** Authenticated admin opens **Read email** from nav, sees inbox rows (subject/from/date/read-unread), clicks a row, and a scrollable wide modal shows that message’s HTML body via sandboxed iframe; non-admins cannot reach the route.

1. Create `src/ui/frontend/src/pages/AdminReadEmail.tsx`:

- On mount, `GET /api/admin/inbox/messages` via `api` from `../lib/api`.
- Local state: `messages`, `loading`, `error`, `selectedId`, `htmlBody`, `bodyLoading`, `bodyError`.
- Render a heading **Read email** and a simple HTML `<table>` (not `ListPage` / not `DATA_SHAPES` — inbox is not a persisted entity shape). Columns in order: **Subject**, **From**, **Date**, **Status** where Status is `Unread` if `unread === true` else `Read`.
- Each data row is clickable (`cursor: pointer` via existing table row styling or a class already used on admin lists). On click: set `selectedId`, clear prior body error, `GET /api/admin/inbox/messages/<id>`, store `html_body` into `htmlBody`.
- While the modal is open, show `Modal` from `../components/Modal` with:
  - `open={selectedId !== null}`
  - `onClose` clears `selectedId`, `htmlBody`, `bodyError`
  - `title` = subject of the selected row, or `"Message"` if subject empty
  - `size="wide"`
  - **No** `onSave` prop (footer shows Cancel only)
- Modal body content:
  - If `bodyLoading`: short “Loading…” text
  - Else if `bodyError`: show the error string
  - Else: wrap an iframe:

```tsx
<div className="email-html-frame">
  <iframe title="Email body" sandbox="" srcDoc={htmlBody || ""} />
</div>
```

⚠️ **Decision:** Render Gmail HTML inside a sandboxed iframe (`sandbox=""` — no tokens) so email CSS/scripts cannot break the admin chrome. Do **not** use `dangerouslySetInnerHTML` for the body. Empty `html_body` still opens the modal with a blank iframe (valid Gmail case when no `text/html` part).

- Surface list-load failures with inline error text (and optional `Toast` if the page already imports Toast — either is fine; prefer the same Toast pattern as `AdminSessionResumePaste.tsx` if you add toast).
- Do not invent filters, pagination UI, or mark-as-read controls.

2. In `src/ui/frontend/src/routes.tsx`:

- Import `AdminReadEmail` from `./pages/AdminReadEmail`.
- Under the Admin routes block, add:

```tsx
{ path: "admin/read_email", element: <AdminRoute><AdminReadEmail /></AdminRoute> },
```

Place it after `admin/session_cover_letter` to match `NAV_CONFIG` order.

3. In `src/ui/frontend/src/App.css`, after the wide-modal rules (near `.modal-card--wide .modal-body`), add:

```css
/* AST-1033: Gmail HTML preview fills wide modal and scrolls inside the iframe */
.email-html-frame {
  height: 100%;
  overflow: hidden;
}
.email-html-frame iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}
```

Wide modal already sets `.modal-card--wide .modal-body { overflow: hidden; padding: 0; }` — the iframe scrolls internally; that satisfies the parent AC “scrollable modal” for HTML bodies.

4. Do **not** add ingest/routing UI, DATA_SHAPES entries, database tables, or Gmail env/config changes.

**Done when (recheck):** Nav shows **Read email**; admin route loads the table; click opens wide modal with sandboxed HTML; `AdminRoute` + `@require_admin` cover AC3 for screen and endpoints.

## Out of scope (do not implement here)

- Gmail OAuth / dual-scope token / `src.external.gmail` changes (AST-1032).
- Ingest, classify, reply, label, delete, archive, or mark-read.
- Persisting email bodies into Astral tables.
- CSE env vars or monitor send contract changes.
- Editing `tests/` or `docs/test-bible/**` (Betty owns those after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — admin UI surface only: one NAV entry, one thin inbox API blueprint calling existing core, one React page + route + CSS; no external/data/config secrets changes.

**Conf:** `high` — mirrors Session Resume / other `@require_admin` + `AdminRoute` admin seeds; core list/get contracts already shipped on ftr via AST-1032.

**Risk:** `Medium` — auth miss would expose mailbox content; iframe `sandbox=""` and `@require_admin` are the mitigations. Wrong API reshaping would break the React table/modal against AST-1032 TypedDict keys.

## Rules self-review

- **§1.3 DRY / public-then-helpers:** Thin route handlers only; no duplicated Gmail logic in UI.
- **§2.1 secrets-from-environ:** No new secrets; mailbox identity stays in AST-1032 / env.
- **§2.4 batch:** N/A — no entity batch claim.
- **§2.6 state machine:** N/A — display-only seed.
- **§3.2 / §3.3 imports:** `api_inbox.py` → core + utils + `ui.auth` only; React → `/api/admin/inbox/*` only; never ui→external.
- **§3.5 naming:** `AdminReadEmail.tsx`, path `/admin/read_email`, blueprint `inbox`.
- **`astral.patterns.require-auth-on-protected-endpoints`:** `@require_admin` on both endpoints; `AdminRoute` on the screen.
- **`astral.layers.ui-config-driven-business-logic`:** Nav via `NAV_CONFIG`; React renders API payloads without inventing inbox rules.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen`
**Plan path:** `docs/features/meteorite/ast-1033-read-email-admin-screen.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ab21fc2f` | NAV **Read email**; `api_inbox` list/get under `@require_admin`; register `inbox_bp` |
| 2 | `1c3505ce` | `AdminReadEmail` table + sandboxed HTML modal; route + CSS |

**Tip:** `055acb74cebc8493f2f4499dad9a794ab0b2ed03` on `origin/sub/AST-1031/AST-1033-read-email-admin-screen`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1033
**Publish ref tip (pre-docs):** `a94497cc0cdc6b88c0c0fb08e1f01c3c024f563a`
**Overall:** DISCUSS

### What’s solid
- `@require_admin` on both inbox endpoints; `AdminRoute` on `/admin/read_email`; UI → core only (no external).
- Nav via `NAV_CONFIG`; sandboxed iframe (`sandbox=""`); 502 mapping for upstream failures; Stages 1–2 match plan.

### Issues
- **discuss (straggler ×14):** Joan excluded several statutes at plan time (1033 Files Changed = ui+utils); three-dot vs `origin/dev` also carries AST-1032 core/external/tests/docs, so those statutes score in-scope. All **conforms** on substance; no product fix expected.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `18b09a64` — **fix-now:** none; **discuss:** statute straggler ×14 (all substance **conforms**); no advisory product items.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (AST-1032 core/external/tests/docs on the same tip) — no code delta. Advanced to **User Testing**.
