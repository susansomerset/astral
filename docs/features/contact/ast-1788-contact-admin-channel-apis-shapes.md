# AST-1788 — Contact admin channel APIs + shapes

**Linear:** [AST-1788](https://linear.app/astralcareermatch/issue/AST-1788/contact-admin-channel-apis-shapes-manage-candidates-snapshot-slack)  
**Parent:** [AST-1786](https://linear.app/astralcareermatch/issue/AST-1786/manage-candidates-snapshot-slack-channel-candidate-mapping) — Manage Candidates Snapshot Slack Channel + candidate mapping  
**Publish ref:** `sub/AST-1786/AST-1788-contact-admin-channel-apis-shapes`

Child #2 of AST-1786: Contact orchestration + `@require_admin` GET routes for bot-visible channel options, membership check (bound Slack user vs chosen channel), and stored-channel message snapshot JSON; plus `DATA_SHAPES` Manage Candidates list column for Slack username and Candidate Profile contact fields for stored channel id + name. Persists channel fields through the **existing** candidate create / data PUT deep-merge (no new writer). Does **not** own external Slack method bodies (AST-1787) or Manage Candidates React (AST-1789).

## UAT fitness

- **AC restored:** Parent AST-1786 AC **1**: “Manage Candidates list shows a Slack username column whose cell equals `candidate_data.contact.slack_username` when set, and a clear empty/placeholder when unset.” Parent AC **2** (persist half via shapes + existing write path): “Add/edit can select a Slack channel …; save persists both `contact.slack_channel_id` and `contact.slack_channel_name` on the candidate. Fail if only one field is stamped or if React calls Slack Web API directly.” Parent AC **7**: “Snapshot / channel / membership admin routes require admin auth.” Parent AC **8**: “External Slack I/O for list / membership / history lives in `src/external/slack.py` and is reached from core/API — not from `AdminManageCandidates.tsx`.” Parent AC **10**: “Candidate Profile shapes expose the new Slack channel fields under Contact Information (id + name).”
- **Correct outcome:** Katherine (sibling #3) can call three admin GETs and receive channel `{id, name}` options, a membership payload that drives unbound / not-member warnings without blocking selection, and a full ascending message list JSON for the candidate’s stored channel; Manage list shapes include a Slack username column key; profile shapes expose `contact.slack_channel_id` + `contact.slack_channel_name`. Channel id+name persist when React stamps them on existing create/PUT — this ticket does not invent a parallel writer.
- **Sibling check:** AST-1787 exports `list_bot_channels`, `is_channel_member`, `fetch_full_conversation_history` on `origin/ftr/AST-1786-manage-candidates-snapshot-slack-channel` (already synced onto this publish-ref tip). This ticket calls those helpers only — does not edit `src/external/slack.py`. AST-1789 owns React flatten/column/select/**S**; this ticket’s API JSON contracts and shapes keys are the handoff. Verified by Files Changed fence + route contracts below.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done — routes must return the shapes and membership/snapshot semantics above; list + profile shapes must land.
- **Wrong fix rejected:** Putting Slack Web API calls in `api_contact.py` (skipping core) or inventing a new candidate write endpoint for channel fields violates AC2/AC8 and the ticket Scope. Emitting progress `info` on these idempotent GETs violates `stat.logging.info.api` (same as `/unbound_slack_users`).

## Explicit scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/contact.py` — channel-list / membership / snapshot orchestration
- `src/ui/api/api_contact.py` — `@require_admin` routes
- `src/utils/config.py` — Manage list Slack username column + profile `contact.slack_channel_id` / `contact.slack_channel_name`

**Out of scope (siblings):** `src/external/slack.py` helper bodies (AST-1787 — call only); `AdminManageCandidates.tsx` / Candidate Profile page edits (AST-1789).

**Depends on:** AST-1787 helpers already on this tip after `sync-child` with parent ftr segment `AST-1786-manage-candidates-snapshot-slack-channel`:

| Helper | Return |
|--------|--------|
| `list_bot_channels()` | `list[{"id": str, "name": str}]` sorted by name |
| `is_channel_member(*, channel, slack_user_id)` | `bool` (raises `ValueError` if either arg empty after strip) |
| `fetch_full_conversation_history(*, channel)` | `list[dict]` messages oldest→newest |

**Canon Scope (read in full for plan):** `stat.logging.info.api`, `stat.logging.debug`, `stat.logging.error`. Patterns: none (`no established pattern applies` on parent).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `DATA_SHAPES["candidates"]["list"]["manage"]` Slack username column; profile Contact Information fields `contact.slack_channel_id` + `contact.slack_channel_name` | utils |
| `src/core/contact.py` | Orchestration: channel options, membership-vs-bound-user, snapshot from stored channel; import Ada’s three helpers | core |
| `src/ui/api/api_contact.py` | Three `@require_admin` GET thin wrappers | ui |

No other files. Do **not** edit `src/external/slack.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`, or any frontend file. Do **not** add a new candidate writer.

⚠️ **Decision — no new persist route:** Channel id+name land via existing `POST /api/candidates` / `PUT /api/candidates/<id>/data` deep-merge of `candidate_data.contact` (same path as Slack bind). This ticket only adds shapes keys + read APIs; Katherine stamps both fields on save.

## Stage 1: DATA_SHAPES list column + profile channel fields

**Done when:** `DATA_SHAPES["candidates"]["list"]["manage"]` includes a Slack username column keyed for flattened list cells, and `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information fields include both `contact.slack_channel_id` and `contact.slack_channel_name` with admin-suitable labels, immediately after the existing `contact.slack_username` field. No Contact or API behavior changes yet.

1. In `src/utils/config.py`, inside `DATA_SHAPES["candidates"]["list"]["manage"]`, append after the existing columns (after `dispatch_task_count` is fine — order is display order; prefer placing Slack username after `contact_email` if that column were present — it is not on list today; place after `last` / before `state`, or after `api_key_status`):
   - ⚠️ **Decision — list key `slack_username`:** Use `{"key": "slack_username", "label": "Slack username", "sortable": True}` — parallel to list’s existing flattened `contact_email` key (not a dotted `contact.*` path). Katherine’s flatten will map `candidate_data.contact.slack_username` → top-level `slack_username` for the cell (parent AC1). Do **not** use `contact.slack_username` as the list key.
2. In `DATA_SHAPES["candidates"]["detail"]["profile"]` → the section whose `"label"` is `"Contact Information"` → `"fields"` list, immediately **after** the existing `{"key": "contact.slack_username", ...}` entry, insert:
   - `{"key": "contact.slack_channel_id", "label": "Slack channel id", "type": "text"}`
   - `{"key": "contact.slack_channel_name", "label": "Slack channel name", "type": "text"}`
3. Do **not** remove or rename existing slack_user_id / slack_username profile fields. Do **not** add channel fields to `edit.manage` (add/edit channel UI is AST-1789 via custom select, not shapes-driven edit form).
4. Compile/lint is N/A for config-only dict edits; still run a quick `python3 -c "from src.utils.config import DATA_SHAPES; …"` sanity that the keys are present before the stage commit.

## Stage 2: Contact orchestration (channel list / membership / snapshot)

**Done when:** Three public helpers exist on `src.core.contact` that call only Ada’s external functions (plus `get_candidate` for bound/stored fields), return the plain dict/list shapes documented below, and use `logger.debug` Calling/Response joints without catching Slack failures to log-and-re-raise.

1. In `src/core/contact.py` module docstring, add an AST-1788 line: admin channel-list / membership / snapshot orchestration for Manage Candidates (no Estelle turn-loop changes).

2. Imports from `src.external.slack` — add:
   - `list_bot_channels`
   - `is_channel_member`
   - `fetch_full_conversation_history`
   - Keep existing imports; do not remove `list_workspace_members` / `list_workspace_posters`.

3. Add a private helper (same file) to read contact blob without inventing a new candidate API:
   ```python
   def _candidate_contact(candidate_id: str) -> tuple[Optional[dict], dict]:
       """Return (candidate_row_or_None, contact_dict). contact_dict is {} when missing."""
   ```
   - `cid = (candidate_id or "").strip()`; if empty, return `(None, {})`.
   - `row = get_candidate(cid)` (already imported).
   - If `row is None`, return `(None, {})`.
   - `cd = row.get("candidate_data")`; contact = `cd.get("contact")` when both are `dict`, else `{}`.
   - Return `(row, contact if isinstance(contact, dict) else {})`.

4. Add public **`list_admin_slack_channels(*, debug: bool = False) -> list[dict]`**:
   - If `debug`: `logger.set_debug_flag(True)` (same entry pattern as `list_unbound_slack_users`).
   - `logger.debug("Calling list_bot_channels: []")` then `channels = list_bot_channels()` then `logger.debug("Response from list_bot_channels: %s", channels)`.
   - Return the list unchanged (already `{id, name}` sorted by Ada).
   - Propagate exceptions to the API handler — do not catch.

5. Add public **`check_admin_slack_channel_membership(*, astral_candidate_id: str, channel: str, debug: bool = False) -> dict`**:
   - If `debug`: `logger.set_debug_flag(True)`.
   - Strip `channel`; empty → raise `ValueError("channel is required")`.
   - `_candidate_contact(astral_candidate_id)` → if row is `None`, raise `ValueError("candidate not found")` (API maps to 404).
   - `uid = contact.get("slack_user_id")`; normalize to stripped str or `""`.
   - ⚠️ **Decision — unbound short-circuit:** If `uid` is empty, **do not** call `is_channel_member` (Ada raises `ValueError` on empty slack_user_id). Return:
     ```python
     {
         "channel": channel.strip(),
         "slack_user_id": "",
         "is_member": False,
         "warn": True,
         "warn_reason": "unbound",
     }
     ```
   - Else call Ada:
     - `logger.debug("Calling is_channel_member: channel=%s slack_user_id=%s", ch, uid)`
     - `member = is_channel_member(channel=ch, slack_user_id=uid)`
     - `logger.debug("Response from is_channel_member: %s", member)`
   - Return:
     ```python
     {
         "channel": ch,
         "slack_user_id": uid,
         "is_member": bool(member),
         "warn": not bool(member),
         "warn_reason": None if member else "not_member",
     }
     ```
   - When `is_member` is True: `warn` is False and `warn_reason` is `None` (parent AC5).

6. Add public **`get_admin_slack_channel_snapshot(*, astral_candidate_id: str, debug: bool = False) -> dict`**:
   - If `debug`: `logger.set_debug_flag(True)`.
   - `_candidate_contact(astral_candidate_id)` → missing candidate → `ValueError("candidate not found")`.
   - `channel_id = contact.get("slack_channel_id")`; strip to str; empty → raise `ValueError("slack_channel_id is required")` (API → 400).
   - `channel_name = contact.get("slack_channel_name")`; use stripped str or `""` (do not require name for snapshot).
   - Call Ada:
     - `logger.debug("Calling fetch_full_conversation_history: channel=%s", channel_id)`
     - `messages = fetch_full_conversation_history(channel=channel_id)`
     - `logger.debug("Response from fetch_full_conversation_history: %s", messages)`
   - Return:
     ```python
     {
         "astral_candidate_id": cid,
         "channel_id": channel_id,
         "channel_name": channel_name,
         "messages": messages,  # ascending list of Slack message dicts
     }
     ```

7. Do **not** add Contact `logger.info` for these helpers (`stat.logging.info.api` owns completing-route progress; these callees stay silent on info). Do **not** change Estelle turn-loop / listen / resolve paths.

8. Compile/lint `src/core/contact.py` before the stage commit.

## Stage 3: Admin GET routes

**Done when:** Three `@require_admin` GET routes under `/api/admin/contact` return the JSON contracts below, log once with `logger.exception` on handler failure (`stat.logging.error`), and do **not** emit progress `| api … completed: GET …` lines (`stat.logging.info.api` — idempotent GETs, same as `/unbound_slack_users`).

1. In `src/ui/api/api_contact.py`, import the three Stage 2 helpers from `src.core.contact`.

2. Add **`GET /slack_channels`**:
   ```python
   @contact_bp.route("/slack_channels", methods=["GET"])
   @require_admin
   def contact_get_slack_channels():
       ...
   ```
   - Resolve `debug` via `ui_llm_debug` + `request.args.get("debug", …)` like `contact_get_unbound_slack_users`.
   - `channels = list_admin_slack_channels(debug=debug)`; return `jsonify({"channels": channels}), 200`.
   - On exception: `logger.exception` with live facts + next step (“Channel list was not returned”); return `jsonify({"error": str(e)}), 502`.

3. Add **`GET /slack_channel_membership`**:
   ```python
   @contact_bp.route("/slack_channel_membership", methods=["GET"])
   @require_admin
   def contact_get_slack_channel_membership():
       ...
   ```
   - Query params: `astral_candidate_id` (required str), `channel` (required str).
   - Missing/empty either → `400` + `{"error": "..."}` without calling core (or let core `ValueError` map below).
   - Call `check_admin_slack_channel_membership(astral_candidate_id=…, channel=…, debug=debug)`.
   - Return `jsonify(payload), 200`.
   - `ValueError` whose message is `candidate not found` → `404` + `{"error": …}` (no exception log — configured miss).
   - Other `ValueError` (e.g. channel required) → `400`.
   - Other exceptions → `logger.exception` + `502` (“Membership check was not returned”).

4. Add **`GET /slack_channel_snapshot`**:
   ```python
   @contact_bp.route("/slack_channel_snapshot", methods=["GET"])
   @require_admin
   def contact_get_slack_channel_snapshot():
       ...
   ```
   - Query param: `astral_candidate_id` (required).
   - Call `get_admin_slack_channel_snapshot(astral_candidate_id=…, debug=debug)`.
   - Return `jsonify(payload), 200` (includes `messages` ascending).
   - `ValueError` `candidate not found` → `404`; `slack_channel_id is required` → `400`.
   - Other exceptions → `logger.exception` + `502` (“Channel snapshot was not returned”).

5. ⚠️ **Decision — no api info on these GETs:** Per `stat.logging.info.api`, idempotent GETs are not progress — do **not** call `_api_completed` / emit `| api … completed: GET …` on success. Comment one line above each handler (same spirit as unbound GET). PUT/POST progress elsewhere unchanged.

6. Do **not** register a new blueprint; `contact_bp` is already on `/api/admin/contact`.

7. Compile/lint `src/ui/api/api_contact.py` before the stage commit.

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Ada/Katherine scopes, or invent a channel write API.
- On ambiguity or drift — stop, comment on parent AST-1786 with the Stage blocked template, wait.

**Sibling AST-1789 consumes:**

| Route | Response |
|-------|----------|
| `GET /api/admin/contact/slack_channels` | `{"channels":[{"id","name"},…]}` |
| `GET /api/admin/contact/slack_channel_membership?astral_candidate_id=&channel=` | `{"channel","slack_user_id","is_member","warn","warn_reason"}` where `warn_reason` ∈ `{null,"unbound","not_member"}` |
| `GET /api/admin/contact/slack_channel_snapshot?astral_candidate_id=` | `{"astral_candidate_id","channel_id","channel_name","messages":[…]}` ascending |
| Shapes | list key `slack_username`; profile `contact.slack_channel_id` + `contact.slack_channel_name` |

**Acceptance mapped (this child):**

| AC | Where |
|----|--------|
| 1 (list Slack username column) | Stage 1 step 1 (Katherine flatten/display) |
| 2 (persist id+name via existing write) | Stage 1 steps 2–3 + Decision (no new writer); Katherine stamps |
| 7 (admin auth) | Stage 3 `@require_admin` on all three |
| 8 (external via core, not React) | Stage 2 calls Ada helpers; Stage 3 thin wrappers only |
| 10 (profile channel fields) | Stage 1 step 2 |

Parent AC 3–6, 9 → N/A for this ticket (UI / external sibling).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `stat.logging.info.api` | statute — read in full; completing-route progress; **idempotent GETs are not progress** (no info on these three routes) |
| `stat.logging.debug` | statute — read in full; Calling/Response (+ loop begin/end if any) at core joints; no truncate; no call-site gate |
| `stat.logging.error` | statute — read in full; handler logs once with facts + traceback + next step; core raises, does not log-and-re-raise |

No placement statutes named. No harvested pattern ids (`no established pattern applies` on parent).

## Joan validate

[plan-rubric]
**Ticket:** AST-1788
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `2dd09cfe6511f69c2cf364e02049376052c4181f`

## Canon scores

stat.logging.info.api | A | | Stage 3 — no `_api_completed` / progress info on idempotent GETs; mirrors `/unbound_slack_users`; core callees stay silent on info
stat.logging.debug | A | | Stage 2 — Calling/Response at core→external joints; `set_debug_flag` entry pattern matches `list_unbound_slack_users`; no truncate; no call-site gate
stat.logging.error | A | | Stage 3 — `logger.exception` with facts + next step on 502; core propagates; configured misses (404/400) not log-and-re-raise

## Traceability

AC1 (list Slack username column) → Stage 1 step 1 shape key `slack_username` (Katherine flatten/display in AST-1789); AC2 (persist id+name via existing write) → Stage 1 steps 2–3 + no-new-writer decision (Katherine stamps on create/PUT); AC7 (admin auth) → Stage 3 `@require_admin` on all three routes; AC8 (external via core, not React) → Stage 2 Ada helper calls + Stage 3 thin wrappers only; AC10 (profile channel fields) → Stage 1 step 2; AC3–6, AC9 → N/A — UI (#3) / external (#1) siblings

## Findings

### acceptable

- **Scope fidelity:** Files Changed matches ticket `## Scope` exactly; fences `slack.py`, frontend, and new candidate writer.
- **Dependency:** Publish-ref tip carries AST-1787 helpers (`list_bot_channels`, `is_channel_member`, `fetch_full_conversation_history`) — prerequisite satisfied.
- **Definition fidelity:** Orchestration + admin GETs + shapes only; membership payload (`warn` / `warn_reason` unbound vs not_member vs member-silent) supports parent AC3–5 via sibling #3; snapshot returns ascending `messages` from Ada.
- **Pattern reuse:** Stage 2/3 mirror existing `list_unbound_slack_users` / `contact_get_unbound_slack_users` split (core debug + API exception handling, no GET progress info).
- **AC1 honesty:** Shape key lands here; `flattenCandidate` extension correctly deferred to AST-1789 — consistent with child partition.
- **Self-assessment:** Estimate confirm 3 — agree; three ordered stages, established Contact admin patterns.

context_tokens≈50000
