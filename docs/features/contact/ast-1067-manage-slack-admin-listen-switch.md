# AST-1067 — Manage Slack: admin listen switch (per environment) + non-prod reply tag

**Linear:** [AST-1067](https://linear.app/astralcareermatch/issue/AST-1067/manage-slack-admin-listen-switch-per-environment-non-prod-reply-tag)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`

Admin **Manage Slack** page flips Contact’s Slack listen/respond flag for the **current deploy environment**, persists that choice under the env’s `ASTRAL_DB_DIR` volume, and applies the existing `[{environment}] ` prefix to Contact outbound reply text when the deploy is not production. Does **not** own Events verify/ack (AST-1069), resolve/PROSPECT (AST-1068), conversation cache (AST-1070), skill runners (AST-1071), or Estelle turn loop (AST-1046).

**Depends on:** AST-1069 on `origin/ftr/AST-1043-slack-bot-agent` (`CONTACT_CONFIG["listen_enabled"]`, `slack_listen_enabled()`, `non_production_reply_prefix()`, `post_message` in external, `contact_bp` registered). Merge that tip before build.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `listen_state_filename` + `production_deploy_env` to `CONTACT_CONFIG`; NAV item for Manage Slack | utils |
| `src/data/contact_listen.py` | New: read/write listen JSON under `ASTRAL_CONFIG["db_dir"]` (values only) | data |
| `src/core/contact.py` | Hydrate/set listen; `format_contact_reply_text` + `post_contact_reply`; Style D when `debug=True` | core |
| `src/ui/api/api_contact.py` | GET/PUT `/listen` on existing `contact_bp` (`@require_admin`) | ui |
| `src/ui/frontend/src/pages/AdminManageSlack.tsx` | New Manage Slack admin page (env label + listen toggle) | ui |
| `src/ui/frontend/src/routes.tsx` | Route `/admin/manage_slack` behind `AdminRoute` | ui |

No edits to `src/external/slack.py` (keep `post_message` dumb), Events blueprint, resolve/PROSPECT, skills ACL, or Estelle turn loop. Do **not** add a SQLite table.

---

## Stage 1: Config — listen persistence filename + production env label + NAV

**Done when:** `CONTACT_CONFIG` exposes filename + production deploy string; Admin nav lists Manage Slack; import-time asserts pass; no data/core/UI behavior change yet.

1. In `src/utils/config.py`, inside `CONTACT_CONFIG` (immediately after `"listen_enabled": False,`), add:

```python
    # Durable listen flag filename under ASTRAL_CONFIG["db_dir"] (per Railway volume / env).
    "listen_state_filename": "contact_slack_listen.json",
    # ASTRAL_DEPLOY_ENV value (case-insensitive) that skips non-prod reply prefix.
    "production_deploy_env": "production",
```

2. After the existing `assert isinstance(CONTACT_CONFIG["listen_enabled"], bool)`, add:

```python
assert isinstance(CONTACT_CONFIG["listen_state_filename"], str) and CONTACT_CONFIG["listen_state_filename"].endswith(".json")
assert isinstance(CONTACT_CONFIG["production_deploy_env"], str) and CONTACT_CONFIG["production_deploy_env"].strip()
```

3. In `NAV_CONFIG` Admin `items`, immediately after the Manage Email entry, append:

```python
            {"label": "Manage Slack", "path": "/admin/manage_slack"},
```

⚠️ **Decision — durable file, not env var / not SQLite:** Parent requires a per-environment flip operators control from Manage Slack. `ASTRAL_DEPLOY_ENV` already labels the process; a JSON file under that env’s `ASTRAL_DB_DIR` volume persists across restarts without a schema migration. Do **not** use `os.environ["SLACK_LISTEN_ENABLED"]` (Manage Slack cannot write Railway env vars at runtime). Do **not** store a multi-env map in one file — each deploy only ever reads/writes **its own** volume.

⚠️ **Decision — production label literal in config:** Prefix skip uses `CONTACT_CONFIG["production_deploy_env"]` compared case-insensitively to stripped `ASTRAL_DEPLOY_ENV` (§2.1 / no-hardcoded-sets). Unset / empty / `"Astral"` fallback deploy labels are **non-production** and get the prefix.

**Done when (recheck):** `CONTACT_CONFIG["listen_state_filename"] == "contact_slack_listen.json"`; `CONTACT_CONFIG["production_deploy_env"] == "production"`; NAV includes Manage Slack path `/admin/manage_slack`.

---

## Stage 2: Data layer — listen JSON read/write

**Done when:** `src/data/contact_listen.py` can load/save the listen bool under `db_dir`; missing/corrupt file → treat as no override; no logging; no core/UI callers yet.

1. Create `src/data/contact_listen.py`:

```python
"""Durable Contact Slack listen flag (AST-1067). Values only — no logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


def _listen_path() -> Path:
    return Path(ASTRAL_CONFIG["db_dir"]) / str(CONTACT_CONFIG["listen_state_filename"])


def load_contact_listen_enabled() -> Optional[bool]:
    """Return persisted listen bool, or None if missing/unreadable/invalid."""
    path = _listen_path()
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    val = raw.get("listen_enabled")
    if not isinstance(val, bool):
        return None
    return val


def save_contact_listen_enabled(enabled: bool) -> None:
    """Write ``{"listen_enabled": <bool>}`` (creates parent dirs as needed)."""
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    path = _listen_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"listen_enabled": enabled}, indent=2) + "\n",
        encoding="utf-8",
    )
```

⚠️ **Decision — Optional[bool] load:** `None` means “no durable override → keep `CONTACT_CONFIG["listen_enabled"]` default (`False`)”. Corrupt files fail closed (no override), same as missing.

**Done when (recheck):** Importing the module does not require Slack secrets; round-trip save → load returns the same bool on a temp `ASTRAL_DB_DIR`.

---

## Stage 3: Core — set/hydrate listen + outbound reply prefix + post helper

**Done when:** `slack_listen_enabled()` reflects durable state; admin can flip via `set_slack_listen_enabled`; `format_contact_reply_text` / `post_contact_reply` apply non-prod prefix; `debug=True` emits Style D on set + post; Events path still only **reads** listen.

1. Update `src/core/contact.py` module docstring to note AST-1067 Manage Slack listen + outbound prefix (still no Estelle turn loop).

2. Extend imports:

```python
from typing import Any, Dict, List, Optional, Tuple

from src.data.contact_listen import (
    load_contact_listen_enabled,
    save_contact_listen_enabled,
)
from src.external.slack import parse_url_verification, post_message, verify_slack_signature
from src.utils.deploy_status import get_deploy_label
```

(Keep existing candidate / logging imports. `post_message` joins the existing external.slack import used by Events — do not import slack from UI.)

3. After module-level `_seen_lock` / `_TEXT_DEBUG_MAX`, add:

```python
_listen_hydrated = False
```

4. Replace `slack_listen_enabled` body so it hydrates once from data, then returns the in-process flag:

```python
def slack_listen_enabled() -> bool:
    """Return Contact listen flag (durable override under db_dir, else CONTACT_CONFIG default)."""
    _hydrate_listen_state()
    return bool(CONTACT_CONFIG["listen_enabled"])
```

5. Add public helpers **immediately after** `non_production_reply_prefix` (before `contact_skill_meta`) — public-then-helpers:

```python
def contact_is_production_deploy() -> bool:
    """True when ASTRAL_DEPLOY_ENV matches CONTACT_CONFIG production_deploy_env (case-insensitive)."""
    ...

def set_slack_listen_enabled(enabled: bool, *, debug: bool = False) -> bool:
    """Persist + apply listen flag for this deploy environment. Returns the stored bool."""
    ...

def format_contact_reply_text(text: str) -> str:
    """Prefix non-production Contact replies with ``[<environment>] ``; production unchanged."""
    ...

def post_contact_reply(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Format outbound text (non-prod prefix) then ``external.slack.post_message``."""
    ...
```

Concrete behavior for `contact_is_production_deploy`:
- `raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()`
- Return `raw.lower() == str(CONTACT_CONFIG["production_deploy_env"]).strip().lower()`

Concrete behavior for `set_slack_listen_enabled`:
- If `debug`: `logger.set_debug_flag(True)`.
- `enabled` must be `bool` — else `raise TypeError("enabled must be bool")`.
- Call `save_contact_listen_enabled(enabled)`.
- Set `CONTACT_CONFIG["listen_enabled"] = enabled`.
- Set `_listen_hydrated = True`.
- If `debug`: Style D found (requested value) then recorded (persisted value + `get_deploy_label()`), using `func="contact.set_slack_listen_enabled"`, `identifier="listen"`.
- Return `bool(CONTACT_CONFIG["listen_enabled"])`.

Concrete behavior for `_hydrate_listen_state` (private, below public API):
- If `_listen_hydrated`: return.
- `loaded = load_contact_listen_enabled()`.
- If `loaded is not None`: `CONTACT_CONFIG["listen_enabled"] = loaded`.
- Set `_listen_hydrated = True`.

Concrete behavior for `format_contact_reply_text`:
- `body = text if isinstance(text, str) else ""`
- If `contact_is_production_deploy()`: return `body`
- Return `non_production_reply_prefix(get_deploy_label()) + body`

Concrete behavior for `post_contact_reply`:
- If `debug`: `logger.set_debug_flag(True)`.
- `outbound = format_contact_reply_text(text)`
- If `debug`: Style D found (channel + truncated raw text) then recorded (truncated outbound + whether prefix applied), `func="contact.post_contact_reply"`, `identifier=channel`.
- `return post_message(channel=channel, text=outbound, thread_ts=thread_ts)` — do not catch; let transport errors propagate to callers.

⚠️ **Decision — Contact owns prefix, external stays dumb:** AST-1069 left `post_message` as raw Web API. Estelle (AST-1046) and any future Contact reply path must call `post_contact_reply` (or at least `format_contact_reply_text`) so non-prod tagging cannot be skipped by accident. Do **not** change `external.slack.post_message` signature.

⚠️ **Decision — prefix whenever non-production:** Apply prefix based on deploy env only (not gated on listen). Inbound listen gate remains `handle_slack_event` / `slack_listen_enabled()`. Parent AC: when listen is on **and** non-prod, replies are tagged — production never tagged.

⚠️ **Decision — mutate CONTACT_CONFIG in-process:** After hydrate/set, `CONTACT_CONFIG["listen_enabled"]` is the process source of truth so existing `slack_listen_enabled()` readers (Events) stay one-line and process-local. Durable file is the cross-restart source.

**Done when (recheck):** With a temp db_dir, `set_slack_listen_enabled(True)` → new process/module re-import path that calls `slack_listen_enabled()` after hydrate returns `True`; `format_contact_reply_text("hi")` with `ASTRAL_DEPLOY_ENV=staging` returns `"[staging] hi"`; with `ASTRAL_DEPLOY_ENV=production` returns `"hi"`.

---

## Stage 4: Admin API — GET/PUT listen on `contact_bp`

**Done when:** Authenticated admin can read and flip listen for the current environment via `/api/admin/contact/listen`; non-admin → 403.

1. In `src/ui/api/api_contact.py`, extend imports:

```python
from src.core.contact import (
    contact_is_production_deploy,
    contact_skills,
    run_contact_skill,
    set_slack_listen_enabled,
    slack_listen_enabled,
)
from src.utils.deploy_status import get_deploy_label, ui_llm_debug
```

2. Add routes on existing `contact_bp` (keep skills routes unchanged):

```python
@contact_bp.route("/listen", methods=["GET"])
@require_admin
def contact_get_listen():
    ...

@contact_bp.route("/listen", methods=["PUT"])
@require_admin
def contact_put_listen():
    ...
```

`GET` response `200`:

```json
{
  "listen_enabled": false,
  "environment": "staging",
  "is_production": false
}
```

- `listen_enabled` = `slack_listen_enabled()`
- `environment` = `get_deploy_label()`
- `is_production` = `contact_is_production_deploy()` (import from core; do not re-implement the compare in the route)

`PUT` body: `{"listen_enabled": <bool>}`. Reject missing/non-bool with `400` `{"error": "listen_enabled must be a bool"}`. Optional `debug` via query/body same pattern as skills route → `ui_llm_debug`. Call `set_slack_listen_enabled(enabled, debug=debug)`. Response `200` same shape as GET after the flip.

⚠️ **Decision — extend `api_contact`, not a new blueprint:** Listen is Contact’s flag; skills already live under `/api/admin/contact`. One admin Contact surface.

**Done when (recheck):** `GET /api/admin/contact/listen` as admin returns JSON with the three keys; `PUT` with `true` then `GET` shows `listen_enabled: true`; non-admin → 403.

---

## Stage 5: Frontend — Manage Slack page + route

**Done when:** Admin can open Manage Slack from the nav, see current environment, and toggle listen; route is admin-gated.

1. Create `src/ui/frontend/src/pages/AdminManageSlack.tsx`:
   - On mount: `GET /api/admin/contact/listen` via existing `api` helper; show loading / error / toast on failure (mirror `AdminManageEmail` patterns: `Toast`, padding 24, h1 “Manage Slack”).
   - Display: environment label; listen status text (`On` / `Off`); production note when `is_production` (e.g. “Production — replies are not prefixed”); when not production, note that replies are prefixed with `[<environment>] `.
   - Primary control: button “Enable listen” when off / “Disable listen” when on. On click: `PUT /api/admin/contact/listen` with `{"listen_enabled": <next>}`; update local state from response; toast success/error.
   - Keep the page minimal — no inbox tables, no Slack message list, no skills UI.

2. In `src/ui/frontend/src/routes.tsx`:
   - Import `AdminManageSlack`.
   - Add `{ path: "admin/manage_slack", element: <AdminRoute><AdminManageSlack /></AdminRoute> }` immediately after the `manage_email` route.

**Done when (recheck):** Nav → Manage Slack renders; toggle calls PUT and reflects new state; non-admin route blocked by `AdminRoute`.

---

## Out of scope (do not implement)

- Events verify/ack/dedupe / Socket Mode (AST-1069 — already on ftr).
- Resolve Slack user / PROSPECT create (AST-1068).
- Conversation cache / history load (AST-1070).
- Skill ACL runners beyond existing AST-1071 surface.
- Estelle conversational turn / calling `post_contact_reply` from the turn loop (AST-1046) — this ticket only provides the helper.
- Changing `external.slack.post_message` to auto-prefix.
- Multi-environment map in one process; Railway env-var mutation from the UI.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new data helper + Contact listen mutate/prefix/post + admin API + new admin React page/nav/route; touches utils, data, core, and ui.

**Conf:** `high` — builds on shipped `CONTACT_CONFIG["listen_enabled"]`, `non_production_reply_prefix`, `contact_bp` / `@require_admin`, and Manage Email page patterns; persistence path is a single JSON file under existing `db_dir`.

**Risk:** `HIGH` — a stuck listen=on could make Estelle respond in the wrong env; mitigated by default-off + fail-closed corrupt-file handling + explicit per-volume file (no cross-env bleed) + production prefix skip via config literal.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Notes |
|------|--------|
| §1.1 / in-scope-only | Stages stay on listen UI + durable flag + outbound prefix helper; no Events/resolve/cache/turn-loop |
| §1.3 DRY | Prefix formatting reuses `non_production_reply_prefix`; post goes through one Contact helper |
| §2.1 config | Filename + production label literals in `CONTACT_CONFIG`; secrets unchanged |
| §2.5 / import-direction | UI → core → data/external; UI never imports `external.slack` |
| §2.9 require_admin | Both listen routes `@require_admin`; page behind `AdminRoute` |
| §3.2 no core file I/O | JSON read/write lives in `src/data/contact_listen.py` |
| §3.5 NAV ↔ routes | NAV path and `routes.tsx` path both `/admin/manage_slack` |
| No-hardcoded-sets | Production env string + filename from config |
| Debug contract | Style D only when `debug=True` on set/post |
| Database header inventory | N/A — no SQLite table |
