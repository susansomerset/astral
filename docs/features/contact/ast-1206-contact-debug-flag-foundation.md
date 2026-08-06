# AST-1206 — Contact debug flag foundation (config, durable persist, core + admin API)

**Linear:** [AST-1206](https://linear.app/astralcareermatch/issue/AST-1206/contact-debug-flag-foundation-config-durable-persist-core-admin-api)  
**Parent:** [AST-1203](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages) — Need to be able to set the "Debug" flag for Slack messages  
**Publish ref:** `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation`

Owns `CONTACT_CONFIG` debug default + durable filename, data-layer read/write under the env `db_dir`, core get/set (mirror Manage Slack listen), and admin GET/PUT so the Contact Slack debug flag is readable/writable without React. Does **not** own Slack Events ingress wiring ([AST-1207](https://linear.app/astralcareermatch/issue/AST-1207)) or Manage Slack React Debug toggle ([AST-1208](https://linear.app/astralcareermatch/issue/AST-1208)).

**Depends on:** AST-1067 listen durable JSON pattern already on `origin/dev` (`CONTACT_CONFIG["listen_enabled"]` / `listen_state_filename`, `src/data/contact_listen.py`, `slack_listen_enabled` / `set_slack_listen_enabled`, `contact_bp` `/listen`). Mirror that shape with a **separate** file and key — do not overload the listen file.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `debug_enabled` + `debug_state_filename` to `CONTACT_CONFIG` + import-time asserts; refresh CONTACT_CONFIG inventory comment | utils |
| `src/data/contact_debug.py` | New: read/write debug JSON under `ASTRAL_CONFIG["db_dir"]` (values only) | data |
| `src/core/contact.py` | `slack_debug_enabled` / `set_slack_debug_enabled` (mirror listen get/set; Style D on set when `debug=True`) | core |
| `src/ui/api/api_contact.py` | GET/PUT `/debug` on existing `contact_bp` (`@require_admin`) | ui |

No edits to `src/external/slack.py`, Events blueprint / `handle_slack_event` / `receive_slack_events_http`, listen data/core/API paths, Estelle activity, skills ACL, turn loop, or Manage Slack React (`AdminManageSlack.tsx`). Do **not** add a SQLite table. Do **not** write into `contact_slack_listen.json`.

---

## Stage 1: Config — debug default + durable filename

**Done when:** `CONTACT_CONFIG` exposes `debug_enabled` (default `False`) and `debug_state_filename`; import-time asserts pass; no data/core/UI behavior change yet.

1. In `src/utils/config.py`, update the top-of-file inventory line for `CONTACT_CONFIG` so it mentions the debug flag alongside listen (keep the rest of that line’s meaning).

2. In `CONTACT_CONFIG`, immediately after `"listen_state_filename": "contact_slack_listen.json",`, add:

```python
    # Default off. Manage Slack Debug (AST-1206) owns the per-environment flip.
    "debug_enabled": False,
    # Durable Contact Slack debug flag filename under ASTRAL_CONFIG["db_dir"] (per Railway volume / env).
    "debug_state_filename": "contact_slack_debug.json",
```

3. After the existing assert on `listen_state_filename`, add:

```python
assert isinstance(CONTACT_CONFIG["debug_enabled"], bool)
assert isinstance(CONTACT_CONFIG["debug_state_filename"], str) and CONTACT_CONFIG["debug_state_filename"].endswith(".json")
```

⚠️ **Decision — separate durable file, not listen JSON / not env var / not SQLite:** Parent forbids overloading the listen file’s schema meaning. Same per-env volume pattern as AST-1067: JSON under that env’s `ASTRAL_DB_DIR`. Do **not** use `os.environ` for the operator flip (Manage Slack cannot write Railway env vars at runtime). Do **not** store a multi-env map — each deploy reads/writes **its own** volume.

⚠️ **Decision — default `False`:** Parent AC requires Debug off → no debug-contract lines on the inbound path; config default matches listen’s fail-closed posture when the durable file is missing.

**Done when (recheck):** `CONTACT_CONFIG["debug_enabled"] is False`; `CONTACT_CONFIG["debug_state_filename"] == "contact_slack_debug.json"`.

---

## Stage 2: Data layer — debug JSON read/write

**Done when:** `src/data/contact_debug.py` can load/save the debug bool under `db_dir`; missing/corrupt file → treat as no override; no logging; no core/UI callers yet.

1. Create `src/data/contact_debug.py` as a literal twin of `src/data/contact_listen.py`, with these exact contracts:

```python
"""Durable Contact Slack debug flag (AST-1206). Values only — no logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


def _debug_path() -> Path:
    return Path(ASTRAL_CONFIG["db_dir"]) / str(CONTACT_CONFIG["debug_state_filename"])


def load_contact_debug_enabled() -> Optional[bool]:
    """Return persisted debug bool, or None if missing/unreadable/invalid."""
    path = _debug_path()
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    val = raw.get("debug_enabled")
    if not isinstance(val, bool):
        return None
    return val


def save_contact_debug_enabled(enabled: bool) -> None:
    """Write ``{"debug_enabled": <bool>}`` (creates parent dirs as needed)."""
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    path = _debug_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"debug_enabled": enabled}, indent=2) + "\n",
        encoding="utf-8",
    )
```

⚠️ **Decision — `Optional[bool]` load:** `None` means “no durable override → keep `CONTACT_CONFIG["debug_enabled"]` default (`False`)”. Corrupt files fail closed (no override), same as listen.

**Done when (recheck):** Importing the module does not require Slack secrets; round-trip save → load returns the same bool on a temp `ASTRAL_DB_DIR`; file content is exactly `{"debug_enabled": <bool>}` (pretty-printed + trailing newline).

---

## Stage 3: Core — get/set debug (mirror current listen, not sticky hydrate)

**Done when:** `slack_debug_enabled()` reflects durable state via re-read every call; admin can flip via `set_slack_debug_enabled`; Style D emits on set only when the set call’s `debug=True`; Events / hear path are **not** edited.

1. Update `src/core/contact.py` module docstring to note AST-1206 Manage Slack debug get/set (still no Events wiring — AST-1207).

2. Extend the data import block (keep listen imports; add debug beside them):

```python
from src.data.contact_debug import (
    load_contact_debug_enabled,
    save_contact_debug_enabled,
)
from src.data.contact_listen import (
    load_contact_listen_enabled,
    save_contact_listen_enabled,
)
```

3. Immediately after `set_slack_listen_enabled` (before `list_estelle_activity`), add:

```python
def slack_debug_enabled() -> bool:
    """Return Contact Slack debug flag (durable file under db_dir is SoT when present)."""
    # Re-read every call — same posture as slack_listen_enabled (AST-1101).
    loaded = load_contact_debug_enabled()
    if loaded is not None:
        CONTACT_CONFIG["debug_enabled"] = loaded
    return bool(CONTACT_CONFIG["debug_enabled"])


def set_slack_debug_enabled(enabled: bool, *, debug: bool = False) -> bool:
    """Persist + apply Contact Slack debug flag for this deploy environment. Returns the stored bool."""
    if debug:
        logger.set_debug_flag(True)
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    save_contact_debug_enabled(enabled)
    CONTACT_CONFIG["debug_enabled"] = enabled
    if debug:
        logger.debug_index(
            func="contact.set_slack_debug_enabled",
            index=1,
            total=2,
            identifier="debug",
            outcome="found",
        )
        logger.debug_detail(f"requested={enabled}")
        logger.debug_index(
            func="contact.set_slack_debug_enabled",
            index=2,
            total=2,
            identifier="debug",
            outcome="recorded",
        )
        logger.debug_detail(
            f"debug_enabled={CONTACT_CONFIG['debug_enabled']} "
            f"environment={get_deploy_label()}"
        )
    return bool(CONTACT_CONFIG["debug_enabled"])
```

⚠️ **Decision — re-read every call, not sticky once-hydrate:** Current `slack_listen_enabled` re-reads the durable file every call (AST-1101 fixed sticky hydrate leaving listen stuck). Mirror that for debug so Admin toggles are visible to any future reader in-process without restart. Do **not** reintroduce `_debug_hydrated` sticky state.

⚠️ **Decision — set-call Style D uses the set function’s `debug` kwarg only:** The admin PUT may pass `debug=True` via `ui_llm_debug` (local Ad Hoc style). That is **not** the Contact Slack Events durable SoT. AST-1207 owns wiring Events/hear to `slack_debug_enabled()`. Do not call `slack_debug_enabled()` inside Events in this ticket.

**Done when (recheck):** With no durable file, `slack_debug_enabled()` is `False`. After `set_slack_debug_enabled(True)`, file exists under `db_dir` / `contact_slack_debug.json` and subsequent `slack_debug_enabled()` returns `True`. `contact_slack_listen.json` is untouched. No changes under Events handlers.

---

## Stage 4: Admin API — GET/PUT `/api/admin/contact/debug`

**Done when:** Authenticated admin can GET current debug state and PUT a bool; unauthenticated/non-admin rejected by existing `@require_admin`; payload shape mirrors `/listen` (flag + environment labels); no React changes.

1. Update `src/ui/api/api_contact.py` module docstring to include AST-1206 debug GET/PUT.

2. Extend the core import:

```python
from src.core.contact import (
    contact_is_production_deploy,
    contact_skills,
    list_estelle_activity,
    run_contact_skill,
    set_slack_debug_enabled,
    set_slack_listen_enabled,
    slack_debug_enabled,
    slack_listen_enabled,
)
```

3. Immediately after `contact_put_listen` (before `/estelle_activity`), add:

```python
def _debug_payload() -> dict:
    return {
        "debug_enabled": slack_debug_enabled(),
        "environment": get_deploy_label(),
        "is_production": contact_is_production_deploy(),
    }


@contact_bp.route("/debug", methods=["GET"])
@require_admin
def contact_get_debug():
    return jsonify(_debug_payload()), 200


@contact_bp.route("/debug", methods=["PUT"])
@require_admin
def contact_put_debug():
    body = request.get_json(silent=True) or {}
    enabled = body.get("debug_enabled")
    if not isinstance(enabled, bool):
        return jsonify({"error": "debug_enabled must be a bool"}), 400
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        set_slack_debug_enabled(enabled, debug=debug)
    except TypeError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_contact] debug set failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify(_debug_payload()), 200
```

⚠️ **Decision — mirror `/listen` payload extras:** Include `environment` + `is_production` so AST-1208 can render beside the listen controls without inventing a second env label source. Flag field name is `debug_enabled` (parallel to `listen_enabled`).

⚠️ **Decision — no React in this ticket:** Curl / admin API proves AC persistence for the foundation. Manage Slack Debug toggle UI is AST-1208.

**Done when (recheck):** `GET /api/admin/contact/debug` as admin returns JSON with bool `debug_enabled`, string `environment`, bool `is_production`. `PUT` with `{"debug_enabled": true}` then `GET` (and process restart with same `ASTRAL_DB_DIR`) still shows `true`. Non-bool body → 400. Listen GET/PUT behavior unchanged.

---

## Self-Assessment

**Scope:** `Single-Component` — Contact config + one new data module + two core helpers + two thin admin routes; no Events/React/listen ownership.

**Conf:** `high` — exact mirror of shipped AST-1067 listen durable JSON + admin GET/PUT, with AST-1101 re-read posture already proven on listen.

**Risk:** `low` — default-off separate file; no Events wiring yet (sibling); wrong persist would only break Admin debug SoT for AST-1208/1207 consumers, not listen or Estelle.

---

## Code-rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY / public-then-helpers | Core get/set placed beside listen helpers; data module twin of `contact_listen.py` — no duplicated listen logic. |
| §2.1 config SoT | Filename, default, JSON key names live in `CONTACT_CONFIG`; no hardcoded path strings in core/UI. |
| §2.4 batch processing | N/A — no batch claim/dispatch. |
| §2.6 state machine | N/A — no entity state transitions. |
| §3.3 imports | data→utils; core→data+utils; ui→core+utils; UI never imports data/external. |
| §3.5 naming / single worker | snake_case API fields; durable file same single-worker assumption as listen (no multi-worker sync). |
| §1.5.1 debug-contract-gated | Style D only inside `set_slack_debug_enabled` when its `debug` kwarg is True; data layer silent. |
| §1.1 in-scope-only | Explicit non-touch list: Events, React, listen file, SQLite. |

---

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation` |
| Tip | `6b9c405b` |
| Branch | `sub/AST-1203/AST-1206-contact-debug-flag-foundation` |

Stages 1–4 landed: `debug_enabled` + `debug_state_filename`, `contact_debug.py`, `slack_debug_enabled` / `set_slack_debug_enabled`, admin GET/PUT `/api/admin/contact/debug`.

---

## Radia review

[code-rubric] revision=1

| Field | Value |
|-------|-------|
| Rubric | code-rubric.v1 |
| Publish ref tip | `b52eb7c756122e4fcb4d7e4290bb0b3045dedb7d` |
| Overall | CLEAN |

Full active statute corpus (65 leaves under `canon/statutes/**`, 18 universal + 47 scoped) scored in-session per the Full-set sweep algorithm — zero `violates`, zero `needs-discussion`. Three `not-applicable` (`astral.debug.no-repo-root-artifacts-dir`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.ui.frontend-file-placement` — no matching diff paths). No Joan plan-rubric verdict attached to this ticket; not a block.

**What's solid:** `contact_debug.py` / `slack_debug_enabled` / `set_slack_debug_enabled` / `/debug` GET-PUT are literal twins of the shipped AST-1067 listen path (confirmed line-for-line against `contact_listen.py` and `set_slack_listen_enabled`) — same re-read-every-call posture, same Style D gating (`debug_index`/`debug_detail` only inside `if debug:`), same config-block placement, same `@require_admin` + JSON-error convention. Commit trail cleanly separates roles (`code(AST-1206)` touches `src/` only; `test(AST-1206)` + `merge-tests(AST-1206)` land via Betty on `tests/` + `docs/test-bible/` only) — no cross-contamination of the test-tree ban. In-scope-only holds: no Events, React, listen-file, or SQLite touches.

**Pattern conformance:** `pattern.config.config-block`, `pattern.ui.admin-endpoint` cited in the ticket description — not registered under `canon/patterns/` (none exists); functionally covered by `astral.config.config-source-of-truth` and `astral.patterns.require-auth-on-protected-endpoints`, both scored `conforms` above.

context_tokens≈9000

— Radia
