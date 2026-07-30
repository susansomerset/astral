# AST-1070 — Slack-sourced conversation context load and cache

**Linear:** [AST-1070](https://linear.app/astralcareermatch/issue/AST-1070/slack-sourced-conversation-context-load-and-cache)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`

Give Contact a way to **load recent Slack thread/channel history** for Estelle turns, with an **optional process-local cache** and **append** of new inbound/outbound messages. **Source of truth remains Slack** (Web API history/replies). Does **not** add a full-exchange DB transcript table. Does **not** own Events verify/ack (AST-1069), Manage Slack (AST-1067), resolve/PROSPECT (AST-1068), skill runners (AST-1071), or the Estelle turn loop (AST-1046).

Depends on **AST-1069** (`src/external/slack.py` + Contact ingress already on `ftr`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `CONTACT_CONFIG` with history limit, cache capacity, cache TTL | utils |
| `src/external/slack.py` | Add `fetch_conversation_history` (`conversations.history` / `conversations.replies`) | external |
| `src/core/contact.py` | `load_slack_conversation_context`, `append_slack_conversation_message`; append on accepted inbound; optional `contact_post_message` (post + append) | core |

No UI blueprint. No `database.py` schema / transcript table. No Manage Slack / resolve / skills / turn-loop changes beyond inbound append hook on existing `handle_slack_event` accept path.

---

## Stage 1: Config — context load / cache contracts

**Done when:** `CONTACT_CONFIG` exposes history page size, cache conversation capacity, and cache TTL; asserts pass; no secret values in config.

1. Extend `CONTACT_CONFIG` (keep existing listen / skills / Events / Socket keys) with:

```python
    # AST-1070: Slack history page size for context loads (Web API limit param).
    "context_history_limit": 50,
    # Process-local cache: max distinct (channel, thread) keys retained.
    "context_cache_max_conversations": 256,
    # Seconds before a cached conversation is considered stale (force Slack refetch).
    "context_cache_ttl_seconds": 300,
```

2. Asserts: all three are `int` and `> 0`; `context_history_limit` is the Slack `limit` passed to external (no hardcoded limit in core/external call sites).

⚠️ **Decision — process-local cache, not a DB transcript table:** Parent AC6 and Boundaries forbid a separate full-exchange transcript SoT in DB. Single gunicorn worker (RAILWAY_CONFIG) makes an in-process cache sufficient for this epic. Document that multi-worker would need shared cache (out of scope). Do **not** add `CREATE TABLE` / coat-check transcript storage.

---

## Stage 2: External — `fetch_conversation_history`

**Done when:** External can pull recent messages from a channel or thread via Slack Web API; no Contact/cache logic; no outcome logging.

1. In `src/external/slack.py`, add:

```python
def fetch_conversation_history(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    limit: int,
) -> list[dict]:
    """Fetch recent messages from Slack (SoT). Raise on HTTP/transport / ok:false."""
```

2. Behavior (literal):

   - `require_controlled_external_io("slack.fetch_conversation_history")`.
   - Token: `os.environ[CONTACT_CONFIG["bot_token_env"]]` (strict).
   - If `thread_ts` is set → `POST`/`GET` **`conversations.replies`** with `channel`, `ts=thread_ts`, `limit`.
   - Else → **`conversations.history`** with `channel`, `limit`.
   - Return the `messages` list from the JSON response (each item a Slack message dict). Raise on non-2xx or `ok is not True` (include Slack `error` in exception message; do not log).
   - Do **not** filter bot/subtype here — Contact decides what to keep for context.

3. Keep existing verify / challenge / `post_message` / Socket Mode helpers unchanged.

---

## Stage 3: Contact — load, cache, append

**Done when:** Core loads context (Slack SoT + process-local cache), can append messages, Style D when `debug=True`; UI never imports external.

1. Module-level process-local cache (same spirit as `event_id` dedupe):

   - Key: `(channel, thread_ts or "")`.
   - Value: `{ "messages": list[dict], "fetched_at": float }` (monotonic or `time.time()`).
   - Cap keys by `CONTACT_CONFIG["context_cache_max_conversations"]` (OrderedDict LRU).
   - Thread-safe with a lock.

2. Public functions (names exact):

```python
def load_slack_conversation_context(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    refresh: bool = False,
    debug: bool = False,
) -> dict:
    """Return recent conversation messages for a channel or thread.

    SoT is Slack. Cache is process-local only — never a DB transcript store.
    """

def append_slack_conversation_message(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    message: dict,
    debug: bool = False,
) -> None:
    """Append one message into the process-local cache for that conversation key."""

def contact_post_message(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Post via external slack.post_message, then append outbound text into cache."""
```

3. `load_slack_conversation_context` behavior:

   - Normalize `channel` (strip); empty → raise `ValueError`.
   - If cache hit and not `refresh` and age `< context_cache_ttl_seconds`: return  
     `{"channel", "thread_ts", "messages", "source": "cache"}`.
   - Else: `messages = fetch_conversation_history(channel=…, thread_ts=…, limit=CONTACT_CONFIG["context_history_limit"])`; store in cache; return  
     `{"channel", "thread_ts", "messages", "source": "slack"}`.
   - Message dicts returned are the Slack API shapes (pass-through); do not invent a parallel transcript schema.
   - `debug=True`: Style D index + detail (`source`, channel, thread_ts, `len(messages)`); truncate long text previews.

4. `append_slack_conversation_message` behavior:

   - If no cache entry for the key yet, create one with `messages=[message]` and `fetched_at=now` (warm without Slack round-trip).
   - Else append `message` and trim to `context_history_limit` (keep newest).
   - `message` must be a `dict` with at least `text` and `ts` (string); raise `ValueError` otherwise.

5. `contact_post_message`: call `post_message`; on success append an outbound message dict using Slack response fields when present (`ts` from the API response; `text` as posted). Placeholder `user`/`bot_id` only for cache-local identity of Estelle’s own outbound — document that load still returns Slack API shapes from history fetches. Return the Web API JSON. AST-1046 should prefer this helper for outbound so cache stays warm.

6. Wire **inbound append** into existing `handle_slack_event`: when result `accepted` is True, call `append_slack_conversation_message` with:
   - `channel=event["channel"]`
   - `thread_ts=event.get("thread_ts")` only — if missing/`None`, normalize to `""` for the cache key (channel-only DM / channel root). **Never** pass message `ts` as the cache-key thread component.
   - `message={"user", "text", "ts"}` from the event (`ts` lives **inside** the message dict only).
   Do **not** fetch history inside `handle_slack_event` (ack path stays light).

⚠️ **Decision — cache key uses Slack thread_ts only:** Key is `(channel, thread_ts or "")`. Channel @-mention threads pass Slack’s `thread_ts`. DMs / channel roots without a thread use `""`. Message `ts` is never the key’s thread component (that would shard one DM into one key per message). Document in code comment.

⚠️ **Decision — no DB table:** Explicit parent boundary. Refresh always available via `refresh=True` / TTL expiry → Slack SoT.

---

## Stage 4: Self-check / no UI

**Done when:** No new blueprint; `api_slack` / `api_contact` unchanged except transitive core behavior; import direction holds (core→external only).

1. Confirm `src/ui/api/*` does not call `fetch_conversation_history`.
2. No frontend. No Manage Slack. No PROSPECT. No Estelle turn.

---

## Out of scope (explicit)

- Events signature verify / URL challenge / daemon ack (AST-1069 — already shipped).
- Manage Slack listen UI / env prefix (AST-1067).
- `get_candidate_id_for_query` / PROSPECT create (AST-1068).
- CONTACT_CONFIG skill runner bodies (AST-1071 — already on ftr).
- Estelle conversational turn + CHAT envelope (AST-1046).
- Full-exchange DB transcript table / coat-check conversation store.
- Multi-worker shared cache.
- Changing Socket Mode script beyond what Contact append provides for free.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new Slack history external I/O, Contact load/cache/append surface, config contracts, and inbound append hook on accept.

**Conf:** `high` — Slack `conversations.history` / `replies` are fixed APIs; AST-1069 left `post_message` + Contact module; parent forbids transcript SoT so process-local cache is the matching design.

**Risk:** `MEDIUM` — stale/wrong context could mislead Estelle turns (AST-1046); mitigated by TTL + `refresh=True` + Slack as SoT on miss/expiry. No open unauthenticated surface added.

---

## Revisions

### Revision 1 — 2026-07-30

Driven by: Joan `[plan-discuss] round=1 concern` — fix-now Stage 3.6 vs Decision contradict on DM cache key (`ts` vs `""`).

Changes:

- Stage 3 step 6: inbound append passes `thread_ts=event.get("thread_ts")` only; message `ts` stays inside the message dict, never as the cache-key thread component.
- Decision wording aligned: key is `(channel, thread_ts or "")` only.
- Step 5: clarify outbound append prefers Slack response fields; placeholder bot identity is cache-local only (Joan discuss non-blocking).

## Review (build stub)

- **Publish ref:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`
- **Tip:** `c34507c9` — Contact load/cache/append + inbound warm (stages 1–3)
- **Stage commits:** `392d01f5` (config), `45ce50a0` (external), `c34507c9` (contact)

---

## Review (Radia / code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1070  
**Publish ref:** `8f936a1b` on `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context` (docs tip follows)  
**Overall:** FIX-NOW

**Diff change set:** `origin/dev...8f936a1b` — layers `{core, external, utils, ui, docs, scripts}`; tip carries AST-1066/1069/1071 ancestry plus AST-1070 context load/cache; change_types `{add, modify}`.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | no graded agent tasks |
| astral.agent.do-task-delegation | scoped | conforms | no do_task |
| astral.agent.grade-vector-validation | scoped | conforms | no grade vectors |
| astral.batch.batch-id-first | scoped | conforms | no batch claim |
| astral.batch.batch-id-format | scoped | conforms | no batch_id |
| astral.batch.claim-process-release | scoped | conforms | no batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data |
| astral.config.config-source-of-truth | scoped | conforms | history limit / cache max / TTL in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | bot token via env name at call time in external |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plans only — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file per ticket under docs/features/contact/ |
| astral.git.betty-no-src-or-features | scoped | conforms | merge-tests `5ce882c8` tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty vocabulary |
| astral.layers.core-vs-external-bright-line | scoped | conforms | history HTTP only in external fetch_conversation_history |
| astral.layers.import-direction | scoped | conforms | core→external; no UI history fetch |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Socket Mode script under scripts/ (ancestry) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | limits from config; thin API ancestry only |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | process-local cache only — no coat-check transcript |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new unprotected data routes this ticket |
| astral.standards.data-raises-caller-logs | scoped | conforms | external raises; Contact decides |
| astral.standards.database-header-inventory | scoped | not-applicable | no data/schema paths |
| astral.standards.debug-contract-gated | scoped | needs-discussion | Style D present; detail omits plan `source=` field (tied to return-shape drift) |
| astral.standards.dry-and-focused-functions | scoped | conforms | load/append/fetch/post split |
| astral.standards.in-scope-only | scoped | conforms | no Manage Slack / resolve / turn-loop product |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger; external silent on outcomes |
| astral.standards.no-cross-contamination | scoped | conforms | context keys only; skills/Events/ACL boundaries held |
| astral.standards.no-hardcoded-sets | scoped | conforms | limit/max/TTL from CONTACT_CONFIG |
| astral.standards.public-then-helpers | scoped | needs-discussion | `_context_cache_*` helpers sit above public load/append API |
| astral.standards.utils-data-late-import-only | scoped | conforms | config.py has no data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend paths |
| astral.ui.naming-conventions | scoped | conforms | existing snake_case admin/events routes (ancestry) |
| astral.ui.single-gunicorn-worker | scoped | conforms | process-local cache; multi-worker OOS |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests `5ce882c8` then publish-ref merge |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests/merge vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1070-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | merge origin/dev + publish-ref present |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1070-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Joan r1 DM-key Decision held in code |
| orch.pipeline.plan-is-bible | universal | violates | load return type/shape + missing channel empty raise vs Stage 3 |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Hedy remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.core.contact-agent (proposed) | needs-discussion | load/append/post present; load return shape ≠ plan Stage 3 dict |
| pattern.external.slack-events (proposed) | conforms | fetch_conversation_history on external slack |
| pattern.config.config-block | conforms | context_history_limit / cache max / TTL |

### Plan adherence

Stages 1–2 and most of Stage 3 land (config keys, external fetch, process-local cache, DM key = `thread_ts` only, inbound append on accept, `contact_post_message`). **Breaks Stage 3 binding return contract** and channel normalize/raise. Betty already noted list return vs plan dict envelope. Self-Assessment MAJOR-CHANGE / high / MEDIUM still honest for the intended design.

### Findings

**fix-now** — `orch.pipeline.plan-is-bible` / Stage 3 `load_slack_conversation_context`  
**Location:** `src/core/contact.py` `load_slack_conversation_context`  
**Issue:** Plan requires `-> dict` returning `{"channel", "thread_ts", "messages", "source": "cache"|"slack"}`. Tip returns `list[dict]` (messages only). Also plan requires strip channel + `ValueError` on empty — not implemented.  
**Action:** Restore Stage 3 envelope (and channel validate); Betty will need bible/test revision for the dict shape (or engineer `[qa-handoff]` if tests were written to the list drift).

**discuss** — C4 straggler: Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.ui.naming-conventions` now in-scope via tip ancestry (docs/tests/scripts/ui). All score **conforms** / expected — no product action.

**discuss** — `astral.standards.public-then-helpers`: `_context_cache_key` / `_context_cache_put` appear before public load/append (prefer public-first section then helpers).

**discuss** — `astral.standards.debug-contract-gated`: Style D fires, but detail uses `count=` / outcomes `cache_hit`|`fetched` rather than plan’s `source=` field (same envelope drift).

### What’s solid

DM cache key uses Slack `thread_ts` only (Joan Revision 1); history I/O stays in external; TTL + `refresh=` + config caps; inbound append on accept; no DB transcript SoT.

context_tokens≈56000
