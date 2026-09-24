# AST-1787 — Slack channel list, membership, and full history (external)

**Linear:** [AST-1787](https://linear.app/astralcareermatch/issue/AST-1787/slack-channel-list-membership-and-full-history-external-manage)  
**Parent:** [AST-1786](https://linear.app/astralcareermatch/issue/AST-1786/manage-candidates-snapshot-slack-channel-candidate-mapping) — Manage Candidates Snapshot Slack Channel + candidate mapping  
**Publish ref:** `sub/AST-1786/AST-1787-slack-channel-list-membership-full-history`

Child #1 of AST-1786: add Slack external helpers for (1) bot-visible channel options for the Manage Candidates picker, (2) per-user channel membership check for the admin warning, and (3) fully paginated channel message history in ascending date order for the snapshot clipboard. Does **not** own Contact orchestration, admin routes, `DATA_SHAPES`, or Manage Candidates UI (siblings AST-1788 / AST-1789).

## UAT fitness

- **AC restored:** Parent AST-1786 AC **6** (partial — history ascending / full pagination in external): “Row **S** icon-control … fetches the stored channel’s messages via admin API and copies JSON to the clipboard with messages in ascending date order. Fail if order is descending, if messages are truncated to a single page when more exist…”. Parent AC **8**: “External Slack I/O for list / membership / history lives in `src/external/slack.py` and is reached from core/API — not from `AdminManageCandidates.tsx`.” Parent AC **9**: “`rg -n "conversations.members" src/external/slack.py` may match the **membership-check** helper for a known user+channel; it must not be used as a workspace poster/user pool source. Fail if membership enumeration replaces `_iter_conversations` / poster-pool logic.”
- **Correct outcome:** Hedy (sibling #2) can call three exported helpers and receive: channel `{id, name}` options for the picker; a boolean membership answer for a known `slack_user_id` + channel; and a complete oldest→newest message list for a stored channel (all pages), without React talking to Slack.
- **Sibling check:** AST-1667 poster pool (`list_workspace_posters` / `_iter_conversations` / `_collect_poster_ids_for_channel`) still does **not** use `conversations.members` as a user pool — membership helper is a separate public function; poster-pool path unchanged. Verified by reading `list_workspace_posters` / `_iter_conversations` after the change and confirming no new `conversations.members` call inside them. Sibling #2 (Contact/API) and #3 (UI) stay out of this file’s Files Changed table.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done — helpers must return correct shapes and full ascending history.
- **Wrong fix rejected:** Extending limited `fetch_conversation_history` with a larger default `limit` (still one page, still Slack’s newest-first default) does not satisfy AC6. Using `conversations.members` to rebuild the workspace poster/bind pool violates AC9 / AST-1667. Putting Slack Web API calls in React violates AC8.

## Explicit scope gate

Ticket **## Scope** (verbatim partition):

- `src/external/slack.py` — channel list / membership / full history ascending helpers only (extend or complement limited `fetch_conversation_history` as needed).

**Out of scope (siblings):** Contact orchestration (`src/core/contact.py`), admin routes (`src/ui/api/api_contact.py`), shapes (`src/utils/config.py`), Manage Candidates / Candidate Profile UI.

**Depends on:** nothing (wave-1). Sibling #2 (Hedy) consumes these helpers after this lands.

**Canon Scope (read in full for plan):** `stat.logging.debug`, `stat.logging.error`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/slack.py` | New public helpers: bot-visible channel list (id+name), membership check via `conversations.members`, full paginated history ascending; module docstring + `__all__`; reuse `_slack_bot_get` / pagination norms; leave limited `fetch_conversation_history` and poster-pool path unchanged | external |

No other files. Do **not** add config keys, UI, Contact orchestration, or admin routes.

## Stage 1: Channel list, membership, full history helpers

**Done when:** Three new functions are exported from `src/external/slack.py`, each gated by `require_controlled_external_io`, with `logger.debug` begin/end (and callee in/out where a private helper is called) per `stat.logging.debug`; no `logger.info` in this module; hard Slack/transport / `ok:false` failures **raise** (do not log-and-re-raise — callers log per `stat.logging.error`). Channel list returns bot-visible public/private channels as `{id, name}` sorted by name. Membership check uses `conversations.members` only for a known user+channel and returns `bool`. Full history returns every page of `conversations.history` for one channel, ordered oldest→newest. Poster-pool / `_iter_conversations` / `list_workspace_members` behavior is unchanged.

1. In `src/external/slack.py`, update the module docstring:
   - Mention the three new helpers (channel picker list, membership check, full ascending history) alongside existing Web API helpers.
   - Keep call-time env / `require_controlled_external_io` rules.
   - Keep logging contract: **no** `logger.info` outcome lines; **do** `logger.debug` at loop joints; fatal failures **raise**.

2. Add to `__all__` (in this order after existing exports, before `open_socket_mode_connection` if present — keep alphabetical-by-existing-block stable by appending the three names after `list_workspace_members`):
   - `"list_bot_channels"`
   - `"is_channel_member"`
   - `"fetch_full_conversation_history"`

3. Add public `list_bot_channels() -> list[dict]`:
   - Gate: `require_controlled_external_io("slack.list_bot_channels")`.
   - Call-time bot token via existing `_slack_bot_get` (same as `_iter_conversations`).
   - Paginate `conversations.list` with params: `types="public_channel,private_channel"`, `exclude_archived=True`, `limit=_PAGE_LIMIT`, cursor from `response_metadata.next_cursor`.
   - ⚠️ **Decision:** Picker types are `public_channel,private_channel` only — not `im`/`mpim`. Admin is assigning a Slack **channel** for snapshot; DMs are not picker options. Poster-pool `_iter_conversations` keeps its existing broader types unchanged.
   - For each channel dict: keep only entries with non-empty string `id`; `name` = `str(ch.get("name") or "").strip()` (empty name allowed if Slack returns none — still include the row if `id` is present).
   - Return list of `{"id": <channel_id>, "name": <name>}` sorted by `(name.lower(), id)`.
   - Debug: `Beginning conversations.list channels loop on unknown items` before the while; `End conversations.list channels loop after %s items` with len(result) after; outer `Calling list_bot_channels: []` / `Response from list_bot_channels: %s` with the full list (do not truncate — `stat.logging.debug`).
   - On `ok:false` or HTTP/transport failure: **raise** `RuntimeError` / let `raise_for_status` propagate — same as `_iter_conversations`. No soft-skip.

4. Add public `is_channel_member(*, channel: str, slack_user_id: str) -> bool`:
   - Gate: `require_controlled_external_io("slack.is_channel_member")`.
   - Strip `channel` and `slack_user_id`; if either is empty after strip, raise `ValueError` with a clear message (`channel is required` / `slack_user_id is required`).
   - Paginate `conversations.members` with `channel=<channel>`, `limit=_PAGE_LIMIT`, cursor from `response_metadata.next_cursor`.
   - For each page’s `members` list: if the stripped `slack_user_id` appears as a string member id, return `True` immediately (early exit).
   - If pagination exhausts without a match, return `False`.
   - Debug: begin/end on the members loop (`Beginning conversations.members loop on unknown items` / `End conversations.members loop after %s pages` or after member-id count scanned — use page count or cumulative member count consistently; prefer cumulative members seen); callee-style `Calling is_channel_member: channel=… slack_user_id=…` / `Response from is_channel_member: %s`.
   - On `ok:false` / HTTP failure: **raise** (hard-fail). Soft-skip set used by poster history does **not** apply here — admin asked about a specific channel.
   - ⚠️ **Decision:** Use `conversations.members` only inside this helper. Do **not** call it from `list_workspace_posters`, `_iter_conversations`, `_collect_poster_ids_for_channel`, or `list_workspace_members`. AC9 / AST-1667 ban stands for poster/user pool.

5. Add public `fetch_full_conversation_history(*, channel: str) -> list[dict]`:
   - Gate: `require_controlled_external_io("slack.fetch_full_conversation_history")`.
   - Strip `channel`; empty → `ValueError("channel is required")`.
   - Reuse private `_paginate_messages("conversations.history", {"channel": channel, "limit": _PAGE_LIMIT}, soft_skip=False)` so all pages are collected. If `_paginate_messages` returns `None` only under soft-skip — with `soft_skip=False` it either returns a list or raises; treat a returned list as authoritative.
   - Slack returns newest-first within/across pages as collected by `_paginate_messages` (pages appended in API order). After collecting, sort ascending by message `ts` (string Slack timestamp sorts correctly lexicographically). Messages missing `ts` sort last (stable: put them after all with `ts`, preserve relative order among themselves via a secondary index if needed — simplest: `sorted(msgs, key=lambda m: str(m.get("ts") or ""))` so empty ts sorts first; **instead** use `key=lambda m: (0, str(m["ts"])) if isinstance(m.get("ts"), str) and m.get("ts") else (1, "")` so missing `ts` sort last).
   - Return the sorted list of message dicts (same dicts Slack returned — do not strip fields; siblings build JSON).
   - Do **not** change `fetch_conversation_history` (limited single-request helper stays for Estelle / existing callers).
   - Debug: `Calling fetch_full_conversation_history: channel=…`; after pagination `Beginning ascending sort loop on %s items` / `End ascending sort loop after %s items`; `Response from fetch_full_conversation_history: %s` with full list (no truncate).
   - Hard-fail on `ok:false` / HTTP (no soft-skip) — stored channel snapshot must not silently return empty on `not_in_channel`.

6. Leave unchanged:
   - `fetch_conversation_history` signature and single-page behavior.
   - `list_workspace_posters`, `_iter_conversations`, `_collect_poster_ids_for_channel`, `_enrich_posters`, `list_workspace_members`.
   - No new imports beyond what already exists unless a typing need appears (prefer existing `List`, `Dict`, `Any`).

7. Sanity after edit (build-child will run these; plan-child does not implement):
   - `rg -n "conversations.members" src/external/slack.py` matches only `is_channel_member` (and its debug string / method name) — not poster-pool helpers.
   - `rg -n "def list_bot_channels|def is_channel_member|def fetch_full_conversation_history" src/external/slack.py` finds all three.
   - No `logger.info` added in this module.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Contact/API/config/UI, or alter poster-pool semantics.
- On ambiguity or drift — stop, comment on parent AST-1786 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `stat.logging.debug` | pattern — read in full; debug begin/end + callee in/out; no truncate; no call-site gate |
| `stat.logging.error` | pattern — read in full; external raises, does not log-and-re-raise; handlers (siblings) log once |

No placement statutes named on this ticket. No harvested pattern ids apply (`no established pattern applies` on parent).

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1787
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `e8c548243066583fe743d3807e633de2e1f90a40`

## Canon scores

stat.logging.debug | A | | plan Stage 1 — begin/end + Calling/Response on all three helpers; no truncate; no call-site gate; matches existing slack.py outer-loop pattern
stat.logging.error | A | | external raises on hard Slack failures; no log-and-re-raise; ValueError for empty inputs; siblings log per statute

## Traceability

AC6 (partial — full pagination + ascending in external) → Stage 1 step 5 `fetch_full_conversation_history` (`_paginate_messages` all pages, `ts` ascending sort); AC8 → Files Changed + Stage 1 steps 3–5 (`slack.py` only, gated I/O); AC9 → Stage 1 step 4 `is_channel_member` + step 6 poster-pool unchanged + sanity `rg`; AC1–5, AC7, AC10 → N/A — sibling #2/#3 scope

## Findings

### acceptable

- **Scope fidelity:** Single file `src/external/slack.py`; explicit scope gate matches ticket `## Scope`; siblings correctly excluded.
- **Definition fidelity:** Implements child slice only — three exported helpers for picker list, membership bool, full ascending history; leaves `fetch_conversation_history` and poster-pool path untouched per parent Technical scope and AC9.
- **UAT fitness:** Correctly rejects one-page/limit-only history extension and poster-pool `conversations.members` misuse; sibling AST-1667 boundary called out.
- **DRY / reuse:** `list_bot_channels` parallels `_iter_conversations` with a documented narrower `types` filter and `{id,name}` shape — justified for picker vs poster scan; reuses `_slack_bot_get`, `_PAGE_LIMIT`, `_paginate_messages`.
- **Self-assessment:** Estimate confirm 3 — agree; one stage, one file, three functions; proportionate to AST-1667 precedent.

context_tokens≈32000
```
