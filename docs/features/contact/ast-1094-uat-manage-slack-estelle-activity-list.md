# AST-1094 — UAT: Manage Slack list of @Estelle users (bind status, msg count, last channel/ts)

**Linear:** [AST-1094](https://linear.app/astralcareermatch/issue/AST-1094/uat-manage-slack-list-of-estelle-users-bind-status-msg-count-last)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list`

UAT gap: Manage Slack (AST-1067) only exposes the listen switch. Parent AC #9 needs an admin list of Slack users who have @'ed Estelle — bind success/fail, inbound message count, last message timestamp + channel — so operators can verify resolve/bind without opening Slack history or a full transcript UI. Persist a **per–Slack-user activity summary** under the env `ASTRAL_DB_DIR` volume (JSON, not SQLite / not conversation SoT), record on each accepted `handle_slack_event` after resolve, expose via admin GET, and render on Manage Slack below the listen controls.

**Depends on:** AST-1067 (Manage Slack page + listen), AST-1068 (`resolve_slack_user`), AST-1069 (`handle_slack_event` accept path) — already on `origin/dev` / epic tip.

---

## UAT fitness

- **AC restored:** Parent AC #9 — "Admin **Manage Slack** lists Slack users who have @'ed Estelle: bind success/fail to an Astral candidate, inbound message count from that Slack user, and timestamp + channel of the last message seen."
- **Correct outcome:** Admin sees one row per Slack user who @'ed Estelle with bind success/fail, message count, last message timestamp + channel (not merely "error gone").
- **Sibling check:** AST-1067 listen on/off + non-prod prefix still work; AST-1068 resolve/PROSPECT still owns bind; AST-1069 Events verify/ack unchanged; AST-1070 process-local conversation cache unchanged (summary file is not that cache). Verified by not editing Events signing/challenge, skills ACL, turn-loop, or cache modules.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Full Estelle conversational transcript UI (AST-1046); inventing a second matcher beside `get_candidate_id_for_query`; making Slack history the DB SoT. Summary JSON + list UI restores AC #9 without those.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `activity_state_filename` to `CONTACT_CONFIG` + import-time assert | utils |
| `src/data/contact_estelle_activity.py` | New: load/save/list/record activity JSON under `db_dir` (values only) | data |
| `src/core/contact.py` | After accept+resolve in `handle_slack_event`, record activity; public `list_estelle_activity()` for API | core |
| `src/ui/api/api_contact.py` | GET `/estelle_activity` on `contact_bp` (`@require_admin`) | ui |
| `src/ui/frontend/src/pages/AdminManageSlack.tsx` | Below listen controls: table of activity rows | ui |

No edits to `src/external/slack.py`, Events blueprint / signing / challenge, `resolve_slack_user` body, skills ACL, conversation cache, or Estelle turn-loop. Do **not** add a SQLite table. Do **not** store full message bodies or thread transcripts in the activity file.

---

## Stage 1: Config — activity summary filename

**Done when:** `CONTACT_CONFIG` exposes the activity JSON filename; import-time assert passes; no data/core/UI behavior change yet.

1. In `src/utils/config.py`, inside `CONTACT_CONFIG`, immediately after `"listen_state_filename": "contact_slack_listen.json",`, add:

```python
    # Durable @Estelle per–Slack-user activity summary under ASTRAL_CONFIG["db_dir"] (AST-1094).
    "activity_state_filename": "contact_estelle_activity.json",
```

2. After the existing assert on `listen_state_filename`, add:

```python
assert isinstance(CONTACT_CONFIG["activity_state_filename"], str) and CONTACT_CONFIG["activity_state_filename"].endswith(".json")
```

⚠️ **Decision — JSON under `db_dir`, not SQLite:** Parent forbids full conversation exchanges as first-class DB transcript SoT; AC #9 needs a small durable **summary** for UAT. Matching AST-1067’s listen file keeps this UAT fix off `database-header-inventory` and scoped to the env volume. One file per deploy volume (no multi-env map).

**Done when (recheck):** `CONTACT_CONFIG["activity_state_filename"] == "contact_estelle_activity.json"`.

---

## Stage 2: Data layer — activity JSON read / record / list

**Done when:** `src/data/contact_estelle_activity.py` can load the map, upsert one Slack user’s summary, and return a list sorted by `last_message_ts` descending; missing/corrupt file → empty map; no logging; no core/UI callers yet.

1. Create `src/data/contact_estelle_activity.py`:

```python
"""Durable Contact @Estelle activity summary (AST-1094). Values only — no logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


def _activity_path() -> Path:
    return Path(ASTRAL_CONFIG["db_dir"]) / str(CONTACT_CONFIG["activity_state_filename"])


def _empty_store() -> dict:
    return {"by_slack_user_id": {}}


def load_estelle_activity_store() -> dict:
    """Return ``{"by_slack_user_id": {<id>: <row>}}``. Missing/corrupt → empty store."""
    path = _activity_path()
    if not path.is_file():
        return _empty_store()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return _empty_store()
    if not isinstance(raw, dict):
        return _empty_store()
    by = raw.get("by_slack_user_id")
    if not isinstance(by, dict):
        return _empty_store()
    # Keep only string keys → dict rows (drop garbage entries).
    cleaned: dict[str, dict] = {}
    for k, v in by.items():
        if isinstance(k, str) and k.strip() and isinstance(v, dict):
            cleaned[k] = v
    return {"by_slack_user_id": cleaned}


def save_estelle_activity_store(store: dict) -> None:
    """Write the activity store (creates parent dirs as needed)."""
    if not isinstance(store, dict):
        raise TypeError("store must be dict")
    by = store.get("by_slack_user_id")
    if not isinstance(by, dict):
        raise TypeError("store.by_slack_user_id must be dict")
    path = _activity_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"by_slack_user_id": by}, indent=2) + "\n",
        encoding="utf-8",
    )


def record_estelle_activity(
    *,
    slack_user_id: str,
    bind_ok: bool,
    astral_candidate_id: Optional[str],
    candidate_state: Optional[str],
    last_channel: Optional[str],
    last_message_ts: Optional[str],
) -> dict:
    """Upsert one Slack user: increment inbound count; refresh bind + last seen.

    Returns the updated row dict. Raises ``TypeError`` if ``slack_user_id`` is empty
    or ``bind_ok`` is not bool.
    """
    if not isinstance(slack_user_id, str) or not slack_user_id.strip():
        raise TypeError("slack_user_id must be non-empty str")
    if not isinstance(bind_ok, bool):
        raise TypeError("bind_ok must be bool")
    uid = slack_user_id.strip()
    store = load_estelle_activity_store()
    by = store["by_slack_user_id"]
    prev = by.get(uid) if isinstance(by.get(uid), dict) else {}
    prev_count = prev.get("inbound_message_count")
    count = int(prev_count) + 1 if isinstance(prev_count, int) and prev_count >= 0 else 1
    row = {
        "slack_user_id": uid,
        "bind_ok": bind_ok,
        "astral_candidate_id": astral_candidate_id if isinstance(astral_candidate_id, str) else None,
        "candidate_state": candidate_state if isinstance(candidate_state, str) else None,
        "inbound_message_count": count,
        "last_channel": last_channel if isinstance(last_channel, str) and last_channel else None,
        "last_message_ts": last_message_ts if isinstance(last_message_ts, str) and last_message_ts else None,
    }
    by[uid] = row
    save_estelle_activity_store(store)
    return row


def list_estelle_activity_rows() -> list[dict[str, Any]]:
    """All activity rows, sorted by ``last_message_ts`` descending (empty last)."""
    by = load_estelle_activity_store()["by_slack_user_id"]
    rows = [dict(v) for v in by.values() if isinstance(v, dict)]
    # Slack ``ts`` strings sort lexicographically in time order.
    rows.sort(key=lambda r: str(r.get("last_message_ts") or ""), reverse=True)
    return rows
```

⚠️ **Decision — increment only on record calls from accepted events:** Do not backfill from Slack history APIs. Counts start when this code ships; UAT can @Estelle after deploy to populate rows.

⚠️ **Decision — no message text in the file:** Row fields are identity + bind + count + last channel/ts only. Transcript bodies stay out (AST-1046 / wrong-fix boundary).

**Done when (recheck):** Module importable; `list_estelle_activity_rows()` returns `[]` when file missing; `record_estelle_activity(...)` creates the file under `db_dir` and increments count on second call for the same `slack_user_id`.

---

## Stage 3: Core — record on accept; public list helper

**Done when:** Every accepted `handle_slack_event` that reaches the post-resolve block records (or attempts to record) activity; API can call `list_estelle_activity()`; Style D when `debug=True` on record; early rejects (listen_off, duplicate, type_skipped, …) do **not** record.

1. In `src/core/contact.py`, near other public listen helpers, add:

```python
def list_estelle_activity(*, debug: bool = False) -> list[dict]:
    """Return durable @Estelle activity rows for Manage Slack (AST-1094)."""
    from src.data.contact_estelle_activity import list_estelle_activity_rows

    rows = list_estelle_activity_rows()
    if debug:
        log = get_logger(__name__)
        log.set_debug_flag(True)
        log.debug_index(
            func="contact.list_estelle_activity",
            index=1,
            total=1,
            identifier="activity",
            outcome="listed",
        )
        log.debug_detail(f"row_count={len(rows)}")
    return rows
```

2. In `handle_slack_event`, **after** the resolve block that sets `astral_candidate_id` / `candidate_state` / `candidate_created` (and **before** conversation-cache append / Estelle turn), record activity when `result["accepted"]` is True and there is a non-empty Slack user string **or** an empty user (bind fail). Concrete behavior:

```python
    # AST-1094: durable activity summary for Manage Slack (not conversation SoT).
    user_for_activity = user if isinstance(user, str) and user.strip() else None
    if user_for_activity is not None:
        bind_ok = isinstance(result.get("astral_candidate_id"), str) and bool(
            result.get("astral_candidate_id")
        )
        try:
            from src.data.contact_estelle_activity import record_estelle_activity

            record_estelle_activity(
                slack_user_id=user_for_activity,
                bind_ok=bind_ok,
                astral_candidate_id=result.get("astral_candidate_id")
                if isinstance(result.get("astral_candidate_id"), str)
                else None,
                candidate_state=result.get("candidate_state")
                if isinstance(result.get("candidate_state"), str)
                else None,
                last_channel=channel if isinstance(channel, str) else None,
                last_message_ts=msg_ts if isinstance(msg_ts, str) else None,
            )
            if debug:
                log.debug_index(
                    func="contact.handle_slack_event",
                    index=1,
                    total=1,
                    identifier=event_id,
                    outcome="activity_recorded",
                )
                log.debug_detail(
                    f"activity user={user_for_activity!r} bind_ok={bind_ok} "
                    f"channel={channel!r} ts={msg_ts!r}"
                )
        except Exception as exc:
            log.error("contact estelle activity record failed: %s", exc, exc_info=True)
    elif result.get("accepted"):
        # Accepted event with no Slack user → cannot key a row; skip record (bind fail
        # without an id is not listable). Do not invent a synthetic user key.
        if debug:
            log.debug_index(
                func="contact.handle_slack_event",
                index=1,
                total=1,
                identifier=event_id,
                outcome="activity_skipped_no_user",
            )
            log.debug_detail("activity skipped: missing slack user")
```

3. If `resolve_slack_user` can raise: wrap the existing resolve call so a failure still sets `astral_candidate_id=None`, `candidate_state=None`, `candidate_created=False`, then still records with `bind_ok=False` when `user` is present. Prefer:

```python
    if isinstance(user, str) and user.strip():
        try:
            resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)
            result["astral_candidate_id"] = resolved["astral_candidate_id"]
            result["candidate_state"] = resolved["state"]
            result["candidate_created"] = resolved["created"]
        except Exception as exc:
            log.error("contact resolve_slack_user failed: %s", exc, exc_info=True)
            result["astral_candidate_id"] = None
            result["candidate_state"] = None
            result["candidate_created"] = False
            result["resolve_error"] = str(exc)
    else:
        ...
```

Do **not** change `resolve_slack_user` itself. Do **not** change Events HTTP verify/ack.

⚠️ **Decision — record after resolve, before turn:** UAT cares about bind + inbound count even if the Estelle turn fails later. Turn failure must not skip the activity upsert.

⚠️ **Decision — late import of data helpers:** Keep top-of-module import graph clean; match existing listen hydrate pattern (`from src.data...` inside functions).

**Done when (recheck):** Calling `handle_slack_event` with a minimal accepted `app_mention` payload (listen on) creates/updates a row; `list_estelle_activity()` returns that row; listen_off path still returns early with no file write.

---

## Stage 4: Admin API — GET estelle activity

**Done when:** `GET /api/admin/contact/estelle_activity` returns `{ "users": [ ... ] }` for admins; unauthenticated/non-admin rejected by existing `@require_admin`.

1. In `src/ui/api/api_contact.py`, import `list_estelle_activity` from `src.core.contact` (alongside existing listen imports).

2. Add route:

```python
@contact_bp.route("/estelle_activity", methods=["GET"])
@require_admin
def contact_get_estelle_activity():
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        users = list_estelle_activity(debug=debug)
    except Exception as e:
        logger.warning("[api_contact] estelle_activity list failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify({"users": users}), 200
```

No PUT/DELETE in this ticket (read-only UAT list).

**Done when (recheck):** Route registered on `contact_bp`; response shape `{"users":[...]}` with row keys matching the data layer.

---

## Stage 5: Manage Slack UI — activity table

**Done when:** Admin Manage Slack still toggles listen; below that, a `list-page-table` lists activity rows (or empty state); load failures toast like listen.

1. In `src/ui/frontend/src/pages/AdminManageSlack.tsx`:

   - Add type:

```ts
type EstelleActivityRow = {
  slack_user_id: string
  bind_ok: boolean
  astral_candidate_id: string | null
  candidate_state: string | null
  inbound_message_count: number
  last_channel: string | null
  last_message_ts: string | null
}
```

   - State: `activity: EstelleActivityRow[]`, load in the same mount `useEffect` (or a second effect) via `api("/api/admin/contact/estelle_activity")`. On listen toggle success, **also** re-fetch activity (counts may not change on toggle — still refresh for consistency is optional; **required:** fetch on mount). Prefer: fetch listen + activity in parallel on mount; do **not** block listen toggle on activity errors.

   - Below the listen button block, render:

```tsx
      <h2 style={{ margin: "32px 0 12px", fontSize: 16, color: "var(--text-primary)" }}>
        @Estelle users
      </h2>
      <div className="list-page-table-wrap">
        <table className="list-page-table">
          <thead>
            <tr>
              <th>Slack user</th>
              <th>Bind</th>
              <th>Candidate</th>
              <th>Messages</th>
              <th>Last channel</th>
              <th>Last ts</th>
            </tr>
          </thead>
          <tbody>
            {activity.map(row => (
              <tr key={row.slack_user_id}>
                <td>{row.slack_user_id}</td>
                <td>{row.bind_ok ? "ok" : "fail"}</td>
                <td>{row.astral_candidate_id || "—"}</td>
                <td>{row.inbound_message_count}</td>
                <td>{row.last_channel || "—"}</td>
                <td>{row.last_message_ts || "—"}</td>
              </tr>
            ))}
            {activity.length === 0 && (
              <tr>
                <td colSpan={6}>No @Estelle users recorded yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
```

2. No new route — keep `/admin/manage_slack`. No NAV change.

⚠️ **Decision — reuse Manage Email table classes:** `list-page-table` / `list-page-table-wrap` already exist; do not invent a new card layout.

**Done when (recheck):** Page shows listen controls + activity table; empty store shows the empty row message; after a recorded event, refresh shows the Slack user with bind/count/channel/ts.

---

## Self-assessment

**Scope:** `MAJOR-CHANGE` — new data module + Contact record/list surface + admin GET + Manage Slack table; touches utils, data, core, ui.

**Conf:** `high` — builds on shipped Manage Slack page, `handle_slack_event` accept path, `resolve_slack_user`, and listen JSON-under-`db_dir` pattern; AC fields map 1:1 to row columns.

**Risk:** `Medium` — wrong/missing rows confuse UAT of resolve/bind; mitigated by recording only on accepted events after resolve, fail-closed corrupt file → empty list, no Slack history backfill, activity write errors logged without aborting the Estelle turn path after record is attempted (record before turn; turn errors do not roll back the row).

---

## Out of scope (do not implement)

- Full conversational transcript UI / AST-1046 turn-loop redesign
- Second candidate matcher / Slack history as DB SoT
- Events challenge/signing changes
- CONTACT_CONFIG skill ACL body edits
- SQLite new tables / `database.py` header inventory
- Clearing or editing activity rows from the UI
- Backfilling historical Slack messages into the summary file

---

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list` |
| Tip | `568af0b6` |
| Branch | `sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list` |

Stages 1–5 landed: `activity_state_filename`, `contact_estelle_activity.py`, record on accept + `list_estelle_activity`, GET `/estelle_activity`, Manage Slack activity table.


---

## Radia review — code-rubric.v1

**Overall:** CLEAN  
**Publish tip reviewed:** `65096646` (`origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list`)  
**Diff:** `origin/dev...65096646` — layers `{core, data, utils, ui, docs}`; change_types `{add, modify}`; 17 paths (focused UAT AC #9).

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
| astral.config.config-source-of-truth | scoped | conforms | activity_state_filename in CONTACT_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no threshold/score-floor edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no new secret literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan under docs/features — not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | one plan file AST-1094 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test/merge-tests touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer code() commits touch src only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external edits; UI never calls slack |
| astral.layers.import-direction | scoped | conforms | ui→core→data; data→utils only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | table renders API rows; no hard-coded state sets |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | no coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | no consult |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | GET /estelle_activity @require_admin |
| astral.standards.data-raises-caller-logs | scoped | conforms | data silent; core/API log failures |
| astral.standards.database-header-inventory | scoped | conforms | choose-JSON under db_dir; no new SQLite table |
| astral.standards.debug-contract-gated | scoped | conforms | Style D on list + record when debug=True |
| astral.standards.dry-and-focused-functions | scoped | conforms | data I/O vs core record/list vs thin API |
| astral.standards.in-scope-only | scoped | conforms | no Events/skills/turn-loop/cache ownership |
| astral.standards.logging-via-utils | scoped | conforms | Contact get_logger; data silent |
| astral.standards.no-cross-contamination | scoped | conforms | focused 17-path tip; no unrelated deletes |
| astral.standards.no-hardcoded-sets | scoped | conforms | filename from CONTACT_CONFIG |
| astral.standards.public-then-helpers | scoped | conforms | public list_estelle_activity / data record+list |
| astral.standards.utils-data-late-import-only | scoped | conforms | config has no data import |
| astral.state.core-decides-transitions | scoped | conforms | no state transition ownership; resolve untouched |
| astral.state.job-prior-states-enforced | scoped | conforms | no job prior-state edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | no dispatch chain |
| astral.ui.frontend-file-placement | scoped | conforms | extends AdminManageSlack.tsx |
| astral.ui.naming-conventions | scoped | conforms | snake_case /estelle_activity |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker config change |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests SHA 65096646 |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on origin/sub/AST-1043/AST-1094-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | tip includes merge-tests; no lost origin/dev paths |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none observed |
| orch.git.no-dev-agent-branches | universal | conforms | uses sub/AST-1043/AST-1094-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1043 |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions held (JSON summary; no transcript SoT) |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–5 land as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Contact child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no statute authorship |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test/bible + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer Katherine remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | doc-only review commit paths |

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.manage-pages / pattern.ui.admin-endpoint | conforms | Manage Slack table + thin admin GET |
| pattern.config.config-block | conforms | CONTACT_CONFIG activity_state_filename |
| pattern.core.contact-agent (proposed) | conforms | record on accept + list_estelle_activity |

### Plan adherence

Stages 1–5 match the combined plan almost verbatim (config key, data module, resolve wrap + activity record, GET route, Manage Slack table). Self-Assessment MAJOR-CHANGE / high / Medium matches footprint. Sibling boundaries held (no Events/skills/turn-loop/cache ownership).

### Findings

None.

### What’s solid

JSON-under-`db_dir` summary (not conversation SoT); record after resolve / before turn; bind_ok from candidate id; `@require_admin`; Style D gated; UI keeps listen usable if activity GET fails.

### Notes

no plan-rubric verdict attached

---

## Resolution

**Date:** 2026-07-31  
**Review tip:** `dae36e8c` (`docs(AST-1094): Radia review — clean`)  
**Overall:** CLEAN — **no fix-now**

- Acknowledged Radia **CLEAN** (`[code-rubric] revision=1`): Findings none; Stages 1–5 match plan; sibling boundaries held.
- No product or plan ACL changes in resolve.

