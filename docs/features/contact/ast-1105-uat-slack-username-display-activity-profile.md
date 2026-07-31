# AST-1105 — UAT: Slack username/display on Manage Slack activity + Profile

**Linear:** [AST-1105](https://linear.app/astralcareermatch/issue/AST-1105/uat-slack-usernamedisplay-on-manage-slack-activity-profile)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`

UAT gap after AST-1094: Manage Slack @Estelle activity rows show only opaque `U…` Slack user ids, and Candidate Profile does not surface Slack user id / Slack username for Slack-bound candidates. `fetch_user_profile` / `resolve_slack_user` already call Slack `users.info` for PROSPECT first/last seed but do not return or persist Slack **username** (`user.name`), do not store display name on activity rows, and Profile NAV fields omit `contact.slack_user_id` / `contact.slack_username`.

**Depends on:** AST-1094 (activity JSON + Manage Slack table), AST-1068 (`resolve_slack_user` + `contact.slack_user_id`), AST-1067 (Manage Slack page) — on tip / `origin/dev`.

---

## UAT fitness

- **AC restored:** Parent AC #4 — "Slack @Estelle resolves via `get_candidate_id_for_query` (AST-1047) using Slack user id; first unknown Slack user creates **PROSPECT** with Slack user id stored and Slack-seeded profile fields; no @ means no candidate row from Slack." Parent AC (quoted as #5 on this bug; same Manage Slack list AC as prior #9) — "Admin **Manage Slack** lists Slack users who have @'ed Estelle: bind success/fail to an Astral candidate, inbound message count from that Slack user, and timestamp + channel of the last message seen." — restored with human-readable Slack identity on those rows plus Profile Slack id/username.
- **Correct outcome:** Activity list shows username and/or display name **plus** Slack user id (bind/count/channel/ts held); Profile shows Slack user id and Slack username for Slack-bound candidates.
- **Sibling check:** AST-1094 activity persistence/API shape extended only with optional identity fields; AST-1068 resolve still keys on Slack user id via `get_candidate_id_for_query` (no second matcher); AST-1067 listen switch unchanged; AST-1101 hear path unchanged. Verified by not editing Events verify/ack, listen flip, turn envelope, or Socket Mode production ingress.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Fabricating display names without Slack `users.info`; scraping Slack HTML; inventing a second identity matcher beside `get_candidate_id_for_query`; Socket Mode as production ingress.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/slack.py` | `fetch_user_profile`: add `username` from Slack `user.name` | external |
| `src/core/contact.py` | Persist `contact.slack_username` on PROSPECT create; return username/display from resolve; backfill username on match when missing; pass identity into `record_estelle_activity` | core |
| `src/data/contact_estelle_activity.py` | Optional `slack_username` + `slack_display_name` on record/list rows | data |
| `src/utils/config.py` | Profile Contact Information fields: `contact.slack_user_id`, `contact.slack_username` | utils |
| `src/ui/frontend/src/pages/AdminManageSlack.tsx` | Activity table columns for username / display name | ui |

No Events signing/challenge changes. No listen flip changes. No turn-loop / envelope. No Socket Mode production path. Do **not** add a second candidate matcher. Do **not** invent names without `users.info`. Do **not** put Slack username into `CONTACT_CONFIG["skills"]["save_candidate_contact"]["allowed_paths"]` (same ownership rule as `slack_user_id` — Contact resolve owns it).

---

## Stage 1: External — `users.info` username

**Done when:** `fetch_user_profile` returns `username` (Slack login name) alongside existing `first` / `last` / `display_name` / `slack_user_id`.

1. In `src/external/slack.py`, inside `fetch_user_profile`, after reading `user` / `profile`, set:

```python
    username = str(user.get("name") or "").strip()
```

2. Add `"username": username` to the returned dict (empty string when Slack omits it — never fabricate).

⚠️ **Decision — username = Slack `user.name`:** That is the workspace username/handle. Display name stays `profile.display_name` / `real_name` (already returned). Do not invent a synthetic handle from first/last.

**Done when (recheck):** Return keys include `username`; still no logging in external.

---

## Stage 2: Data — activity row identity fields

**Done when:** `record_estelle_activity` accepts optional `slack_username` / `slack_display_name` and persists them on the row; list returns them; missing previous rows stay valid without those keys.

1. In `src/data/contact_estelle_activity.py`, extend `record_estelle_activity` signature with:

```python
    slack_username: Optional[str] = None,
    slack_display_name: Optional[str] = None,
```

2. When building `row`, after `slack_user_id`:

```python
        "slack_username": slack_username.strip()
        if isinstance(slack_username, str) and slack_username.strip()
        else (prev.get("slack_username") if isinstance(prev.get("slack_username"), str) else None),
        "slack_display_name": slack_display_name.strip()
        if isinstance(slack_display_name, str) and slack_display_name.strip()
        else (prev.get("slack_display_name") if isinstance(prev.get("slack_display_name"), str) else None),
```

Preserve prior identity when a later record call passes `None` (e.g. transient `users.info` failure) so counts still update without wiping names.

**Done when (recheck):** New record with names → list row includes them; second record with `None` names keeps prior names and increments count.

---

## Stage 3: Core — resolve persist + activity identity

**Done when:** New PROSPECTs store `contact.slack_user_id` **and** `contact.slack_username`; resolve return includes `slack_username` / `slack_display_name`; matched candidates missing username get a one-time backfill via `users.info` + `save_candidate_data`; activity record receives those fields.

1. In `resolve_slack_user` **create** path, change `candidate_data` to:

```python
    username = str(profile.get("username") or "").strip()
    candidate_data = {
        "contact": {
            "slack_user_id": sid,
            "slack_username": username,
        },
    }
```

Return dict gains:

```python
        "slack_username": username,
        "slack_display_name": display,
```

2. In **found** path (existing `cid`), after loading the row:

- Read `contact = (row.get("candidate_data") or {}).get("contact")` if dict.
- `username = contact.get("slack_username")` if str else `""`.
- `display` may be empty on found (activity still needs display): if `username` is empty **or** you need display for activity, call `fetch_user_profile(sid)` once.
- If username was empty and fetch returns a username, merge via `save_candidate_data(cid, {"contact": {"slack_user_id": sid, "slack_username": username}}, debug=debug)` (merge keeps other contact keys).
- Always return `slack_username` / `slack_display_name` on the resolve result (strings, possibly empty).

3. In `handle_slack_event`, after resolve succeeds or fails with a user id, when calling `record_estelle_activity`, pass:

```python
                slack_username=resolved.get("slack_username")  # only when resolve ran
                # Prefer: stash resolved dict; on resolve exception leave names None.
```

Concrete wiring:

- Keep a local `resolved_meta = {"slack_username": None, "slack_display_name": None}` before resolve.
- On successful resolve, set from return keys.
- On resolve exception with a user, optionally `try: fetch_user_profile(user_for_activity)` for activity names only (do not create candidate).
- Pass into `record_estelle_activity`.

⚠️ **Decision — backfill on match, not Profile→Slack scrape:** Existing Slack-bound PROSPECTs created before this ticket lack `contact.slack_username`. Next @Estelle accept fills Profile + activity. Do not call Slack from the Profile UI.

⚠️ **Decision — no second matcher:** Lookup remains `get_candidate_id_for_query(slack_user_id)` only.

**Done when (recheck):** Create path stores username; match path returns username (backfill if needed); activity row after accept has `slack_username` and/or `slack_display_name` when Slack provides them.

---

## Stage 4: Config — Profile Slack fields

**Done when:** Candidate Profile Contact Information section lists Slack user id and Slack username keys.

1. In `src/utils/config.py`, inside `NAV_CONFIG` (or the profile detail block that serves Candidate Profile — the `"label": "Contact Information"` fields list under `detail.profile`), immediately after the name fields / before email fields, insert:

```python
                        {"key": "contact.slack_user_id", "label": "Slack user id", "type": "text"},
                        {"key": "contact.slack_username", "label": "Slack username", "type": "text"},
```

Exact insertion: after `{"key": "full", ...}` and before `contact.contact_email` in that Contact Information `fields` list (same block ~line 4037 area).

2. Do **not** add these paths to `CONTACT_CONFIG["skills"]["save_candidate_contact"]["allowed_paths"]`.

⚠️ **Decision — ordinary text fields:** FormFields has no read-only type; showing empty for non-Slack candidates is fine. Resolve owns writes; UAT can see values after bind.

**Done when (recheck):** `/api/nav_config` (or profile field payload) includes both keys with those labels.

---

## Stage 5: Manage Slack UI — show names

**Done when:** Activity table shows Slack username and display name in addition to Slack user id; empty names render as `—`; bind/count/channel/ts unchanged.

1. In `AdminManageSlack.tsx`, extend `EstelleActivityRow`:

```ts
  slack_username: string | null
  slack_display_name: string | null
```

2. Map those fields from the activity API JSON (same null/string guards as other columns).

3. Table header: add **Username** and **Display** after **Slack user** (or replace the single Slack user cell with id + username/display — prefer **separate columns** for clarity):

| Slack user | Username | Display | Bind | Candidate | Messages | Last channel | Last ts |

4. Cells: `row.slack_username || "—"`, `row.slack_display_name || "—"`.

**Done when (recheck):** Empty store still shows empty-state row; mocked users with names render in the new columns.

---

## Self-assessment

**Scope:** `MAJOR-CHANGE` — external profile shape + resolve contact persist/backfill + activity row fields + Profile NAV fields + Manage Slack columns.

**Conf:** `high` — reuses existing `users.info` helper and AST-1094 activity/UI path; AC maps to concrete fields.

**Risk:** `Medium` — extra `users.info` on match-without-username; mitigated by one call per accept and preserving prior activity names when fetch fails; no fabricated identities.

---

## Out of scope (do not implement)

- Fabricating usernames without Slack
- Second matcher / Socket Mode production ingress
- Events verify/ack, listen switch, Estelle turn envelope
- Adding slack_username to Contact skill ACL write paths
- Backfilling all historical activity rows via Slack history APIs (next @Estelle fills names)

---

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile` |
| Tip | `e8017442` |
| Branch | `sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile` |

Stages 1–5 landed: `fetch_user_profile.username`, activity identity fields, resolve persist/backfill + activity wiring, Profile Slack fields, Manage Slack Username/Display columns.

