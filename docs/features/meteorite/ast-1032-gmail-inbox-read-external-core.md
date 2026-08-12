<!-- linear-archive: AST-1032 archived 2026-08-05 -->

## Linear archive (AST-1032)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1032/gmail-inbox-read-external-core-receive-email-on-gmail-account-for  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** High / —  
**Parent:** AST-1031 — Receive email on gmail account for astral  
**Blocked by / blocks / related:** parent: AST-1031; blocks: AST-1033

### Description

## What this implements

Owns Gmail API list/get for `astral.career.match@gmail.com` (read + unread), returns message metadata and HTML body to callers, honors controlled-external-I/O, and uses **one** dual-scope OAuth token so existing send keeps working. Does **not** own admin nav or the React modal (sibling AST-1033).

## Citations

`pattern.layers.import-discipline`; `astral.layers.core-vs-external-bright-line`; `astral.config.secrets-and-env-specific-from-environ`.

## Acceptance criteria

1. Callers can list inbox messages for `astral.career.match@gmail.com` (read and unread) with identifying metadata.
2. Callers can fetch a selected message’s HTML body as returned by Gmail.
3. Monitor alert email send still succeeds using the same single dual-scope `GOOGLE_REFRESH_TOKEN` after read ships.
4. With controlled external I/O disabled (integration/harness posture), live Gmail read is blocked the same way other gated external calls are — no silent live inbox hits from tests.

## Boundaries

Does **not** own admin nav, list UI, or HTML modal. Does **not** ingest/persist emails. Does **not** change CSE env vars.

## Notes for planning

Single dual-scope token: `gmail.send` + `gmail.readonly`. Env: `GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1031-receive-email-on-gmail-account-for-astral`, child `sub/AST-1031/AST-1032-gmail-inbox-read`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T04:50:45.135Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1032
**Publish ref:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read` @ `a9adbdc5` (product tip `1241834f` + docs review)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1031/AST-1032-gmail-inbox-read` — `src/external/gmail.py` (M), `src/core/inbox.py` (A), plan + Betty tests/bible.
**Notes:** Joan plan-rubric verdict attached (APPROVED). Three C4 stragglers (excluded at plan; in-scope on three-dot diff) — all score **conforms** on substance; no fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence / grade-vector logic in inbox path |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` / agent delegation |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | No batch/entity work |
| astral.batch.batch-id-format | scoped | conforms | No batch ids |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | No config.py; OAuth stays environ; CSE untouched |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Gmail OAuth via `os.environ[...]`; no CSE key reuse |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (`artifacts/**` / `scripts/spikes/**`) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan under `docs/features/` — not a misplaced spike |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file `ast-1032-gmail-inbox-read-external-core.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer `code()`/`docs()` on src+features; Betty only tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | `test()`/`merge-tests()` are Betty; engineer did not touch tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Gmail I/O in external; core logs/re-raises only |
| astral.layers.import-direction | scoped | conforms | `gmail`→utils; `inbox`→external+utils; no ui→external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss (`scripts`) |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers miss (`ui` / `config.py`) — AST-1033 |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check / persistence |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers miss (`ui`) — AST-1033 |
| astral.standards.data-raises-caller-logs | scoped | conforms | list/get raise; core logs then re-raises; send bool preserved |
| astral.standards.database-header-inventory | scoped | not-applicable | layers miss (`data`) |
| astral.standards.debug-contract-gated | scoped | conforms | No new `debug=` Style D surface |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shared `_build_credentials`/`_build_service`; thin core wrapper |
| astral.standards.in-scope-only | scoped | conforms | No UI/persist/CSE/admin — boundary AST-1033 held |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` in core; external stays silent like send |
| astral.standards.no-cross-contamination | scoped | conforms | Layered shapes; TypedDict returns |
| astral.standards.no-hardcoded-sets | scoped | conforms | Scopes + API page size constants; paginate to exhaustion |
| astral.standards.public-then-helpers | scoped | conforms | Public send/list/get first; helpers below |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers miss (`utils`) |
| astral.state.core-decides-transitions | scoped | conforms | No state machine |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers miss (`ui`) |
| astral.ui.naming-conventions | scoped | not-applicable | layers miss (`ui`) |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers miss (`ui` / scripts / config) |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1032)` @ `1241834f` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child work on `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1031/AST-1032-gmail-inbox-read` |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/...` already ancestor before docs() |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1031` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Dual-scope + raise-vs-bool already decided in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match shipped code |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible on publish ref |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit; no banned paths |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.layers.import-discipline` | conforms — core→external+utils; external→utils only |
| `astral.layers.core-vs-external-bright-line` | conforms — I/O in `gmail.py`; orchestration in `inbox.py` |
| `astral.config.secrets-and-env-specific-from-environ` | conforms — existing OAuth env vars; no CSE |

## Plan adherence

Diff matches Stages 1–2 and Self-Assessment **Single-Component** / high / Medium. Dual-scope shared credentials, list pagination without result cap, HTML-or-empty extraction, controlled-I/O gates, and core log+re-raise match the plan bible. No AST-1033 UI/auth smuggling.

## Findings

### fix-now
(none)

### discuss
1. **straggler** — `astral.debug.spikes-under-debug-dir` excluded at plan time but in-scope on diff (`docs/features/**`). Substance: **conforms**.
2. **straggler** — `astral.docs.features-single-file-per-ticket` excluded at plan time but in-scope on diff. Substance: **conforms** (one plan file).
3. **straggler** — `astral.git.engineer-test-tree-ban` excluded at plan time but in-scope on diff (Betty `tests/**` + bible). Substance: **conforms**.

### advisory
- Ops remint of dual-scope `GOOGLE_REFRESH_TOKEN` remains a parent/live-UAT dependency (not a code defect).

### What’s solid
- Shared `_GMAIL_SCOPES` + `_build_service`; send bool contract unchanged; list/get raise after gate.
- Public-then-helpers; TypedDict shapes; no inventing HTML from text/plain.

### Recommended actions
- Ada: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

context_tokens≈42000

#### betty — 2026-07-29T04:48:04.227Z
1. `tests/component/external/test_gmail.py` — full module (AST-391 send + AST-1032 dual-scope / list / get HTML / helpers / controlled-I/O gate)
2. `tests/component/core/test_inbox.py` — core list/get passthrough + log/re-raise

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_gmail.py \
  tests/component/core/test_inbox.py
```

**Pass:** pytest green; `src/external/gmail.py` stays LOCKED_AT_100.

**Broken/revised:** expanded `test_gmail.py` for dual-scope + list/get (send bool contract preserved).
**Integration:** no existing `tests/integration/` scenarios touch Gmail — none revised; no new scenarios.

**Publish:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read` @ `1241834f` (`merge-tests(AST-1032): origin/tests 101c8beae14cb68026d287c47556bd8a3012be49`)

**Bible shasums on publish ref:**
- `docs/test-bible/external/gmail.md` `80722d47d0a58890f8c629dbd268b04aa069b5c1`
- `docs/test-bible/core/inbox.md` `7c15559b74514596c14bd971d900bf453da3654b`

— Betty

#### joan — 2026-07-29T04:39:16.821Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1032
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `0342d804`. Layers `external` + `core` (new `inbox.py`). No Plan Discuss rounds.
**Implementer:** Ada (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Admin opens Read email + sees inbox list | Partial — Stages 1–2 supply list API for AST-1033; nav/screen N/A — boundary AST-1033 |
| 2 Click message → HTML modal | Partial — Stages 1–2 supply get HTML for AST-1033; modal N/A — AST-1033 |
| 3 Unauthenticated blocked | N/A — boundary: AST-1033 (`require_auth`) |
| 4 Monitor send still works on dual-scope token | Stage 1 (`_GMAIL_SCOPES` + shared `_build_credentials`; send bool contract preserved) |
| 5 Controlled external I/O blocks live Gmail read | Stage 1 (`require_controlled_external_io` on list/get/send) |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 List inbox (read+unread) with identifying metadata | 1–2 |
| 2 Fetch selected message HTML body | 1–2 |
| 3 Send still succeeds on same dual-scope token | 1 |
| 4 Controlled I/O gate blocks live read when disabled | 1 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 External dual-scope + list/get | Purpose/Functional scope Gmail API read; Boundaries (no CSE, no mutate); Architectural bright line |
| 2 Core `inbox.py` thin orchestrator | import-discipline for AST-1033; no persistence |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan docs path on child sub |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No procedure that skips ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1031` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Dual-scope + raise-vs-bool decisions documented; ops remint is parent dependency |
| orch.pipeline.plan-is-bible | conforms | Stages binding; UI/persist excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | No do_task / agent path |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | No config.py; OAuth stays environ; CSE untouched |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Required Gmail OAuth via `os.environ[...]`; no CSE key reuse |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Gmail I/O in external; core orchestrates/logs only |
| astral.layers.import-direction | conforms | external→utils; core→external+utils; no ui→external |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | External raises on list/get; core logs then re-raises; send keeps bool |
| astral.standards.debug-contract-gated | conforms | No new Style D debug contract |
| astral.standards.dry-and-focused-functions | conforms | Shared credential/service helpers; thin core wrapper |
| astral.standards.in-scope-only | conforms | Explicitly excludes AST-1033 UI, persist, CSE, tests |
| astral.standards.logging-via-utils | conforms | `get_logger` in core inbox |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Scopes/page size as module constants; no result cap |
| astral.standards.public-then-helpers | conforms | Public send/list/get first; helpers below |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.layers.ui-config-driven-business-logic — layers/paths miss (UI is AST-1033)
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss (UI/API is AST-1033)
- astral.standards.database-header-inventory — layers/paths miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss
- astral.ui.single-gunicorn-worker — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. List→per-id metadata N+1 is inherent to Gmail list API; full pagination with no result cap matches parent “every message” / no silent truncation.
2. Raise on list/get vs send’s bool — intentional; send contract preserved.
3. Ops remint of dual-scope refresh token before live UAT is parent dependency, not code in this ticket.
4. Empty `html_body` when no `text/html` part — honest; does not invent HTML from plain text.
5. Self-assessment Single-Component / high / Medium — honest about send regression risk.

— Joan
context_tokens≈75000

#### ada — 2026-07-29T04:36:32.968Z
Plan doc: [docs/features/meteorite/ast-1032-gmail-inbox-read-external-core.md](https://github.com/susansomerset/astral/blob/sub/AST-1031/AST-1032-gmail-inbox-read/docs/features/meteorite/ast-1032-gmail-inbox-read-external-core.md) on `origin/sub/AST-1031/AST-1032-gmail-inbox-read` @ `0342d804`.

**Scope — Single-Component:** Extends `src/external/gmail.py` and adds thin `src/core/inbox.py`; no UI/data/config.py. AST-1033 remains the admin surface consumer.

**Conf — high:** Same OAuth env + `require_controlled_external_io` path as send; dual-scope constant and TypedDict list/get shapes mirror existing external patterns (`google_cse`).

**Risk — Medium:** Shared credential helper / scope list could regress monitor `send_email` if wrong; plan keeps send’s bool-never-raise contract and only raises on the new list/get entry points.

---

# AST-1032 — Gmail inbox read (external + core)

**Linear:** [AST-1032](https://linear.app/astralcareermatch/issue/AST-1032/gmail-inbox-read-external-core-receive-email-on-gmail-account-for)
**Parent:** [AST-1031](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral) — Receive email on gmail account for astral
**Publish ref:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read`

Extend the existing Gmail external module so callers can list every inbox message (read and unread) for `GMAIL_USER` and fetch a selected message’s HTML body, orchestrated through a thin core wrapper. One dual-scope OAuth refresh token (`gmail.send` + `gmail.readonly`) keeps monitor alert send working. Live Gmail I/O honors `require_controlled_external_io` the same way send already does. Does **not** own admin nav, list UI, HTML modal, persistence, or CSE env vars (sibling AST-1033 owns the admin surface).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/gmail.py` | Dual-scope credential helper; `list_inbox_messages`; `get_message_html`; keep `send_email` on shared credentials | external |
| `src/core/inbox.py` | New thin orchestrator: list + get HTML, log failures, re-raise | core |

## Stage 1: External — dual-scope credentials + list/get

**Done when:** `src/external/gmail.py` can list every INBOX message with identifying metadata and return a selected message’s HTML body; `send_email` builds credentials from the same dual-scope set; every live Gmail call (send, list, get) invokes `require_controlled_external_io` before network I/O; module still fails import-time if required env vars are missing.

1. In `src/external/gmail.py`, update the module docstring to state that this module owns Gmail **send and inbox read** via one dual-scope OAuth client, and that required env vars remain `GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (optional `GOOGLE_TOKEN_URI`). Do **not** read or write `GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_ID`.

2. Add a module-level constant immediately after the existing env reads:

```python
_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]
_LIST_PAGE_SIZE = 500  # Gmail API page size only — not a result cap; paginate until exhausted
```

⚠️ **Decision:** One shared `_GMAIL_SCOPES` list for **all** credential builds (send and read). Parent AC requires a single dual-scope `GOOGLE_REFRESH_TOKEN`; listing both scopes on every call matches that contract. Ops remint of the refresh token (both scopes) is a parent dependency before live UAT — not this ticket’s code change.

3. Add TypedDict return shapes (import `TypedDict` from `typing`) near the top after imports:

```python
class GmailInboxMessage(TypedDict):
    id: str
    thread_id: str
    subject: str
    from_address: str
    date: str
    unread: bool


class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
```

Export them via module `__all__` if the file already uses `__all__`; otherwise leave public by name (same style as current `send_email`). Prefer adding:

```python
__all__ = [
    "GmailInboxMessage",
    "GmailMessageHtml",
    "send_email",
    "list_inbox_messages",
    "get_message_html",
]
```

4. Add helpers **below** public functions (public-first rule §1.3). Implement:

- `_build_credentials() -> Credentials` — same fields as today’s `send_email` credential block, but `scopes=_GMAIL_SCOPES` (not send-only).
- `_build_service()` — `build("gmail", "v1", credentials=_build_credentials())`.
- `_header_map(payload_headers) -> dict[str, str]` — lowercased name → value for Gmail `payload.headers` list entries.
- `_decode_b64url(data: str) -> str` — `base64.urlsafe_b64decode` with padding fix; decode UTF-8 with `errors="replace"`.
- `_extract_html_body(payload: dict) -> str` — depth-first walk of `payload` / `parts`: if `mimeType == "text/html"` and `body.data` is present, return decoded string; recurse into `parts`; if no HTML part exists, return `""` (do **not** invent HTML from `text/plain`).
- `_message_metadata(raw: dict) -> GmailInboxMessage` — from a `users.messages.get` resource (`format="metadata"`): `id`, `thread_id` from `threadId` (empty string if missing), `subject` / `from_address` / `date` from headers `Subject` / `From` / `Date` (empty string if missing), `unread` = `"UNREAD" in (raw.get("labelIds") or [])`.

5. Refactor `send_email` to call `require_controlled_external_io("gmail.send_email")` then `_build_service()` instead of inlining Credentials/build. Keep the existing success/`except Exception: return False` contract unchanged (still never raises to monitor).

6. Add public `list_inbox_messages() -> list[GmailInboxMessage]`:
   - Call `require_controlled_external_io("gmail.list_inbox_messages")` first.
   - Build service via `_build_service()`.
   - Paginate `users().messages().list(userId="me", labelIds=["INBOX"], maxResults=_LIST_PAGE_SIZE, pageToken=...)` until `nextPageToken` is absent. Collect every message id from every page. **Do not** stop early after N messages — page size is only the Gmail API page parameter.
   - For each message id, call `users().messages().get(userId="me", id=message_id, format="metadata", metadataHeaders=["Subject", "From", "Date"])` and append `_message_metadata(...)`.
   - Preserve Gmail list order (do not re-sort).
   - On any exception after the controlled-I/O gate, **raise** (do not swallow like `send_email`). Empty inbox → `[]`.

⚠️ **Decision:** Raise on list/get failures (unlike `send_email`’s bool). Inbox callers need the payload or a hard failure for admin HTTP mapping; monitor’s “never raise” contract stays local to `send_email`.

7. Add public `get_message_html(message_id: str) -> GmailMessageHtml`:
   - Call `require_controlled_external_io("gmail.get_message_html")` first.
   - `users().messages().get(userId="me", id=message_id, format="full")`.
   - Return `{"id": message_id, "html_body": _extract_html_body(raw.get("payload") or {})}`.
   - On any exception after the gate, **raise**.

**Done when (recheck):** Importing the module still validates the four required env vars; `send_email` uses `_GMAIL_SCOPES`; list paginates INBOX to completion; get returns HTML-or-empty; both new entry points gate through `require_controlled_external_io` with distinct caller strings.

## Stage 2: Core — inbox orchestrator for AST-1033

**Done when:** `src/core/inbox.py` exposes list + get helpers that call external, log failures, and re-raise — ready for AST-1033’s admin API without UI importing external.

1. Create `src/core/inbox.py` with module docstring:

```
Inbox read orchestration for Meteorite seed (AST-1032).

Thin core wrapper over src.external.gmail list/get. No persistence, no admin HTTP.
AST-1033 owns the Read email admin surface and calls these functions.
```

2. Imports (allowed: external + utils only for this module — no data layer):

```python
from src.external.gmail import (
    GmailInboxMessage,
    GmailMessageHtml,
    get_message_html as external_get_message_html,
    list_inbox_messages as external_list_inbox_messages,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)
```

3. Public functions (no helpers needed unless DRY requires them):

```python
def list_inbox_messages() -> list[GmailInboxMessage]:
    """Return every INBOX message metadata row for GMAIL_USER (read + unread)."""
    try:
        return external_list_inbox_messages()
    except Exception as e:
        logger.warning("[inbox] list_inbox_messages failed: %s", e)
        raise


def get_message_html(message_id: str) -> GmailMessageHtml:
    """Return HTML body payload for one Gmail message id."""
    try:
        return external_get_message_html(message_id)
    except Exception as e:
        logger.warning("[inbox] get_message_html failed id=%s: %s", message_id, e)
        raise
```

4. Do **not** add Flask routes, React files, NAV_CONFIG entries, database tables, or CSE config. Do **not** mutate mailbox state (no mark-read, archive, delete, label).

**Done when (recheck):** Core callers can `from src.core.inbox import list_inbox_messages, get_message_html` and receive the TypedDict shapes; failures are logged once then re-raised; no UI/data imports.

## Out of scope (do not implement here)

- AST-1033 admin nav / list screen / HTML modal / auth-gated HTTP.
- Persisting email bodies or ingest/routing.
- Reminting `GOOGLE_REFRESH_TOKEN` in any environment (ops / parent dependency).
- Changing CSE env vars or `GOOGLE_CSE_CONFIG`.
- Editing `tests/` or `docs/test-bible/**` (Betty owns those after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — extends one external module and adds one thin core orchestrator; no UI, data, or config.py changes.

**Conf:** `high` — reuses the existing Gmail OAuth + `require_controlled_external_io` pattern with a clear dual-scope constant and TypedDict returns matching `google_cse`-style external shapes.

**Risk:** `Medium` — wrong scopes or credential helper regression would break monitor alert send; list/get raises change the failure mode vs send’s bool, but send’s public contract is explicitly preserved.

## Rules self-review

- **§1.3 DRY / public-then-helpers:** Shared `_build_credentials` / `_build_service`; public `send_email` / `list_inbox_messages` / `get_message_html` first, helpers below.
- **§2.1 secrets-from-environ:** No new secrets in config; continue `os.environ[...]` for OAuth; CSE keys untouched.
- **§2.4 batch:** N/A — no entity batch claim.
- **§2.5 / §2.6:** External owns Gmail I/O; core orchestrates/logs; no state machine.
- **§3.3 imports:** `gmail.py` → utils only; `inbox.py` → external + utils only; UI never imports external.
- **§3.5 naming:** snake_case Python module `inbox.py`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read`
**Plan path:** `docs/features/meteorite/ast-1032-gmail-inbox-read-external-core.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `0fc6531f` | Dual-scope credentials; `list_inbox_messages` / `get_message_html` in `src/external/gmail.py` |
| 2 | `69750f7d` | Thin `src/core/inbox.py` orchestrator (log + re-raise) |

**Tip:** `ac6addfd` on `origin/sub/AST-1031/AST-1032-gmail-inbox-read`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1032
**Publish ref tip (pre-docs):** `1241834f0eaac855ac04cfcbab647c8b3f23ee49`
**Overall:** DISCUSS

### What’s solid
- Dual-scope `_GMAIL_SCOPES` shared by send/list/get; `send_email` bool contract preserved; list/get raise after `require_controlled_external_io`.
- Thin `src/core/inbox.py` logs then re-raises; no UI/data/CSE bleed; public-then-helpers in `gmail.py`.
- Diff matches plan Stages 1–2 and Self-Assessment Single-Component.

### Issues
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot diff now includes `docs/features/**` + Betty `tests/**` / `docs/test-bible/**` so they score in-scope (all **conforms** on substance).

### Recommended actions
- Ada: acknowledge stragglers (no product change expected) then proceed resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `a9adbdc5` — **fix-now:** none; **discuss:** three statute stragglers (all substance **conforms**); **advisory:** dual-scope token remint remains parent/live-UAT ops.

No product changes. Acknowledged discuss stragglers (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) as plan-time exclusions that became in-scope on the three-dot diff — no code delta. Advisory remint stays on parent AST-1031. Advanced to **User Testing**.
