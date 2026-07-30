# AST-1068 — Slack resolve via get_candidate_id_for_query + PROSPECT create

**Linear:** [AST-1068](https://linear.app/astralcareermatch/issue/AST-1068/slack-resolve-via-get-candidate-id-for-query-prospect-create)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`

Extend shipped AST-1047 **`get_candidate_id_for_query`** to scan **`CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]`**, register **`PROSPECT`** on **`CANDIDATE_STATES`**, and add Contact **`resolve_slack_user`** that looks up by Slack user id and, **only when Estelle is in play** (accepted DM / `app_mention`), creates a PROSPECT with `contact.slack_user_id` + Slack-seeded name fields. Does **not** own Events verify/ack (AST-1069), Manage Slack UI (AST-1067), conversation cache (AST-1070), skill ACL bodies (AST-1071), or Estelle turn loop (AST-1046).

**Depends on (already on `origin/ftr/AST-1043-slack-bot-agent`):** AST-1066 (`slack_user_id_paths` + Contact scaffold), AST-1069 (`handle_slack_event` accept path).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `PROSPECT` on `CANDIDATE_STATES`; drop “not a registry key” assert/comment; optional `CONTACT_CONFIG` id template | utils |
| `docs/ASTRAL_CODE_RULES.md` | One-line `CANDIDATE_STATES` catalog: PROSPECT is a real key (was “No PROSPECT”) | docs |
| `src/core/candidate.py` | Teach `get_candidate_id_for_query` to scan `slack_user_id_paths`; add `initiate_prospect_candidate(...)` | core |
| `src/external/slack.py` | Add `fetch_user_profile(user_id)` via Slack `users.info` (call-time token) | external |
| `src/core/contact.py` | Add `resolve_slack_user(...)`; call it from `handle_slack_event` after accept | core |

---

## Stage 1: PROSPECT registry + lookup matcher

**Done when:** `PROSPECT` is a real `CANDIDATE_STATES` key; `get_candidate_id_for_query` returns a unique id when the needle matches `contact.slack_user_id`; no Contact create yet.

1. In `src/utils/config.py` `CANDIDATE_STATES` block:

   - Replace the header comment line that says `PROSPECT is conceptual only — not a registry key` with: `PROSPECT = Slack-created candidate (AST-1068); prior_states None (entry state).`
   - Add as the **first** registry entry (before `NEW_CANDIDATE`):

```python
    "PROSPECT": {"prior_states": None, "progress_rank": -1},
```

   - **Delete** `assert "PROSPECT" not in CANDIDATE_STATES`.
   - Keep `assert CANDIDATE_CONFIG["initial_state"] in CANDIDATE_STATES` (still `NEW_CANDIDATE` for admin/`initiate_candidate` — do **not** change `initial_state` to PROSPECT).

⚠️ **Decision — PROSPECT vs NEW_CANDIDATE:** Slack create-on-miss lands in **`PROSPECT`**. Admin/`initiate_candidate` stays on **`NEW_CANDIDATE`**. `prior_states: None` on both entry states (same unrestricted pattern as `INACTIVE` / `DELETED`). Downstream intake may later transition PROSPECT → NEW_CANDIDATE / INTAKE (out of scope here — `NEW_CANDIDATE` already allows unrestricted entry).

2. In `CONTACT_CONFIG`, add (after `app_token_env` is fine):

```python
    # Deterministic astral_candidate_id for Slack-created PROSPECTs (format with slack_user_id=).
    "prospect_candidate_id_template": "slack-{slack_user_id}",
```

   Assert: `"{slack_user_id}" in CONTACT_CONFIG["prospect_candidate_id_template"]`.

3. In `docs/ASTRAL_CODE_RULES.md` §2.1 **CANDIDATE_STATES** bullet, change the trailing `No PROSPECT.` to: `Includes PROSPECT (Slack create-on-miss; AST-1068).`

4. In `src/core/candidate.py` `get_candidate_id_for_query`:

   - Change the path tuple to:

```python
    paths = (
        tuple(CANDIDATE_LOOKUP_CONFIG["email_paths"])
        + tuple(CANDIDATE_LOOKUP_CONFIG["name_paths"])
        + tuple(CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"])
    )
```

   - Keep existing needle normalization (`parseaddr` / `@` rule) and `match_casefold` behavior for **all** paths (Slack ids are opaque tokens; casefold is harmless and keeps one compare path).
   - Do **not** create candidates here. Do **not** invent a second matcher function.

5. Still in `candidate.py`, add public:

```python
def initiate_prospect_candidate(
    astral_candidate_id: str,
    candidate_data: Optional[Dict[str, Any]] = None,
) -> None:
    """Create a candidate row in PROSPECT (Slack create-on-miss). Not NEW_CANDIDATE."""
```

   Behavior (literal):

   - Strip `astral_candidate_id`; if empty → `ValueError("astral_candidate_id is required")`.
   - If `get_candidate(astral_candidate_id)` is not None → `ValueError` (already exists).
   - `state="PROSPECT"` (literal from registry — do not use `CANDIDATE_CONFIG["initial_state"]`).
   - `database.save_candidate(...)` with `candidate_data=candidate_data or {}` and `state_history` via existing `_append_candidate_state_history({}, "", "PROSPECT", now)` (same timestamp format as `initiate_candidate`).

⚠️ **Decision — separate initiator:** Do not overload `initiate_candidate` with a state kwarg that admin POST might misuse. Slack-only create uses `initiate_prospect_candidate`.

**Done when (recheck):** `from src.utils.config import CANDIDATE_STATES` → `"PROSPECT" in CANDIDATE_STATES`; `get_candidate_id_for_query` matches a row whose `candidate_data.contact.slack_user_id` equals the needle (unique).

---

## Stage 2: Slack `users.info` + Contact resolve + wire into Events accept

**Done when:** Accepted DM / `app_mention` events resolve to an `astral_candidate_id` + candidate `state`; first unknown Slack user creates PROSPECT with stored Slack id and seeded names; bare lookup miss outside Estelle-in-play does **not** create.

1. In `src/external/slack.py`, export and implement:

```python
def fetch_user_profile(user_id: str) -> dict:
    """GET users.info; return a small profile dict. Call-time bot token. No logging."""
```

   Behavior (literal):

   - `require_controlled_external_io("slack.fetch_user_profile")`.
   - `token = os.environ[CONTACT_CONFIG["bot_token_env"]]` (strict — no `.get`).
   - `POST` or `GET` `https://slack.com/api/users.info` with `user=<stripped user_id>` and Bearer/token auth matching existing `post_message` style in this file.
   - On HTTP/transport failure → raise (same family as `post_message`).
   - Parse JSON; if `ok` is not true → raise `RuntimeError` with Slack `error` string when present.
   - From `user.profile` (and top-level `user` as fallback), return **only**:

```python
{
    "slack_user_id": <stripped user_id>,
    "first": <profile.first_name or "">,
    "last": <profile.last_name or "">,
    "display_name": <profile.display_name or profile.real_name or "">,
}
```

   - All string values stripped; missing → `""`. Do **not** log. Do **not** return email/phone/token fields.

2. In `src/core/contact.py`, add public:

```python
def resolve_slack_user(
    slack_user_id: str,
    *,
    estelle_in_play: bool,
    debug: bool = False,
) -> dict:
    """Lookup Slack user → astral candidate; create PROSPECT only when estelle_in_play."""
```

   Behavior (literal):

   - `sid = (slack_user_id or "").strip()`. If empty → `ValueError("slack_user_id is required")`.
   - If `debug`: `logger.set_debug_flag(True)`.
   - **Lookup:** `cid = get_candidate_id_for_query(sid, debug=debug)`.
   - If `cid` is not None:
     - `row = get_candidate(cid)` (must exist).
     - If `debug`: Style D `func="contact.resolve_slack_user"`, outcome `found|matched`, details `slack_user_id=`, `candidate_id=`, `state=`.
     - Return `{"astral_candidate_id": cid, "state": row["state"], "created": False}`.
   - If `cid` is None and **`estelle_in_play` is not True**:
     - If `debug`: outcome `found|none` (no create).
     - Return `{"astral_candidate_id": None, "state": None, "created": False}`.
   - If `cid` is None and **`estelle_in_play` is True** (create path):
     - `profile = fetch_user_profile(sid)` from `src.external.slack`.
     - `new_id = CONTACT_CONFIG["prospect_candidate_id_template"].format(slack_user_id=sid)`. Strip/lower the id the same way admin create does for consistency: `.strip().lower()`.
     - Build `candidate_data`:

```python
{
    "contact": {"slack_user_id": sid},
    "profile": {
        "first": profile.get("first") or "",
        "last": profile.get("last") or "",
    },
}
```

     - If `profile["display_name"]` is non-empty and both first/last empty, set `profile["first"] = display_name` (single-field seed — do not invent a last name).
     - Call `initiate_prospect_candidate(new_id, candidate_data)`.
     - If `debug`: outcome `recorded|created`, details `slack_user_id=`, `candidate_id=`, `state=PROSPECT`.
     - Return `{"astral_candidate_id": new_id, "state": "PROSPECT", "created": True}`.

⚠️ **Decision — AC3 “no create without @Estelle in play”:** Create is gated by the explicit `estelle_in_play=True` kw-only flag. `get_candidate_id_for_query` never creates. Callers that are not Contact Events accept must pass `False` (or omit create by not calling resolve).

⚠️ **Decision — id template:** `slack-{slack_user_id}` lowercased keeps create idempotent under races (second create hits “already exists” — on `ValueError` from `initiate_prospect_candidate`, re-lookup via `get_candidate_id_for_query(sid)` and return matched row with `created=False` if found; else re-raise).

3. In `handle_slack_event`, **after** building the accepted `result` dict and **before** the final debug/return (only on the `accepted=True` path):

   - Read `user = result.get("user")`.
   - If `user` is a non-empty `str`:
     - `resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)`
     - Set `result["astral_candidate_id"] = resolved["astral_candidate_id"]`
     - Set `result["candidate_state"] = resolved["state"]`
     - Set `result["candidate_created"] = resolved["created"]`
   - Else leave those keys absent / set to `None` (do not create).

⚠️ **Decision — wire site:** AST-1069 left `handle_slack_event` without resolve by design. Estelle-in-play **is** that function’s accept path (DM `message` or `app_mention` after listen/dedupe/type filters). Do **not** create from URL verification, signature failure, or `accepted=False` returns.

4. Do **not** edit Manage Slack UI, conversation cache, skill runners, `TASK_CONFIG`, or Estelle turn loop. Do **not** edit `tests/` / bible.

**Done when (recheck):** With listen on and an accepted `app_mention`/`message` DM payload for an unknown Slack user, Contact returns `astral_candidate_id` + `candidate_state="PROSPECT"` and a row stores `contact.slack_user_id`; a second event for the same user matches without a second row; `resolve_slack_user(..., estelle_in_play=False)` on a miss returns null id and creates nothing.

---

## Out of scope (do not implement here)

- Events signature / challenge / dedupe / Socket Mode (AST-1069 — already shipped).
- Manage Slack listen flip UI (AST-1067).
- Conversation history load/cache (AST-1070).
- CONTACT_CONFIG skill runner inventory changes (AST-1071 — do not allowlist `contact.slack_user_id` there).
- Estelle conversational turn / `post_message` reply loop (AST-1046).
- Formal PROSPECT → NEW_CANDIDATE intake automation (future; registry only enables the hop).
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — candidate state registry + lookup matcher + Contact resolve create path + external `users.info`; touches utils/core/external and a one-line code-rules catalog fix.

**Conf:** `high` — extends AST-1047 matcher and AST-1066 path home; mirrors `initiate_candidate` for PROSPECT; Events accept hook is the natural Estelle-in-play gate from AST-1069.

**Risk:** `HIGH` — wrong create gate could invent candidates without @/DM; wrong PROSPECT registry could break candidate transitions; `users.info` needs controlled I/O. Mitigated by `estelle_in_play` flag, separate initiator, and `require_controlled_external_io`.

## Rules self-review

- **§2.1 / no-hardcoded-sets:** Slack id path + prospect id template + PROSPECT key live in config.
- **§2.6 / core-decides-transitions:** Core chooses PROSPECT on create; data only saves the state parameter.
- **§2.5 / §3.3:** `users.info` in external; Contact orchestrates; candidate matcher stays in `candidate.py`.
- **§1.5.1 debug-contract:** Style D only when `debug=True` on resolve.
- **§1.1 in-scope-only:** Sibling scopes listed Out of scope.
- **secrets-from-environ:** Token via `CONTACT_CONFIG["bot_token_env"]` at call time (existing 1069 pattern).

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on epic worktree; publish to `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`. On ambiguity or drift, stop and comment on parent **AST-1043** with the Stage-blocked format — do not improvise.
