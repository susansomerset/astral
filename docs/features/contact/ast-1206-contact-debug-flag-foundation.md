<!-- linear-archive: AST-1206 archived 2026-08-17 -->

## Linear archive (AST-1206)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1206/contact-debug-flag-foundation-config-durable-persist-core-admin-api  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1203 — Need to be able to set the "Debug" flag for Slack messages  
**Blocked by / blocks / related:** parent: AST-1203; blocks: AST-1208; blocks: AST-1207

### Description

## What this implements

Owns `CONTACT_CONFIG` debug default + durable filename, data-layer read/write under the env `db_dir`, core get/set (mirror listen), and admin GET/PUT so the flag is readable/writable without React. Does **not** own Events ingress wiring (sibling) or Manage Slack React (sibling).

## Acceptance criteria

- [X] On Manage Slack, an admin can turn **Debug** on and off; after refresh or process restart on that environment, the page still shows the last saved Debug state. (API + durable persist portion — UI is sibling.)
- [X] With Debug **off**, the same inbound path does **not** emit those debug-contract lines; INFO/WARNING/ERROR behavior for normal Contact operations remains available. (Flag SoT / default-off + admin API.)

## Boundaries

- [X] Does not own Slack Events ingress wiring or Manage Slack React Debug toggle.
- [X] Does not change listen on/off or the listen durable file’s schema meaning.

## In scope

- [X] `pattern.config.config-block` — `CONTACT_CONFIG["debug_enabled"]` + `debug_state_filename`
- [X] `pattern.ui.admin-endpoint` — thin GET/PUT `/api/admin/contact/debug` on `contact_bp`
- [X] `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — filename, default, JSON key in config
- [X] `astral.standards.debug-contract-gated` — Style D on `set_slack_debug_enabled` only when set-call `debug=True`
- [X] `astral.patterns.require-auth-on-protected-endpoints` — `@require_admin` on debug mutators/readers
- [X] `astral.layers.import-direction` — ui → core → data; UI never imports data/external
- [X] `astral.standards.data-raises-caller-logs` — `contact_debug.py` values-only (no logging)
- [X] `astral.standards.database-header-inventory` — JSON under `db_dir`; no new SQLite table
- [X] `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — twin of listen helpers; no drive-by Events/React
- [X] `astral.ui.single-gunicorn-worker` — same durable-file posture as listen (no multi-worker sync story)

## Considered but excluded

- [X] Slack Events / `handle_slack_event` durable-debug wiring — AST-1207
- [X] Manage Slack React Debug toggle — AST-1208
- [X] Overloading `contact_slack_listen.json` / listen key meaning — parent forbids; separate `contact_slack_debug.json`
- [X] Changing listen on/off behavior or listen admin API — out of scope
- [X] React/UI debug-contract logging — backend only; parent boundary
- [X] Betty Style D golden string tests — Radia enforces instrumentation on review
- [X] Non-Contact modules (gazer/consult/agent Ad Hoc debug) — parent boundary
- [X] Universal `orch.*` — stay off per-child lists

## Notes for planning

Mirror AST-1067 listen durable JSON pattern (separate file/key). Re-read every call like current `slack_listen_enabled` (AST-1101), not sticky once-hydrate. Manage Slack Debug is sole SoT for Contact Slack Events debug (Archie: Events not exercised from local).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1203-need-to-be-able-to-set-the-debug-flag-for-slack-messages`, child `sub/AST-1203/AST-1206-contact-debug-flag-foundation`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1206-contact-debug-flag-foundation.md` @ `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation`.

### Comments

#### radia — 2026-08-06T05:48:18.614Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1206
**Publish ref:** `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation` @ `b52eb7c756122e4fcb4d7e4290bb0b3045dedb7d`
**Overall:** CLEAN

## Plan adherence
- Diff matches the plan's Files Changed table exactly (`src/utils/config.py`, `src/data/contact_debug.py`, `src/core/contact.py`, `src/ui/api/api_contact.py`) — no Events/React/listen-file/SQLite touches, per the plan's explicit non-touch list.
- `contact_debug.py` / `slack_debug_enabled` / `set_slack_debug_enabled` / `/debug` GET+PUT are line-for-line twins of the shipped AST-1067 listen path (verified against `contact_listen.py` and `set_slack_listen_enabled`) — same re-read-every-call posture, same Style D gating.
- Self-Assessment (Scope: Single-Component, Conf: high, Risk: low) matches the diff's real footprint.

Full active statute corpus (65 leaves — 18 universal + 47 scoped) scored in-session: zero fix-now, zero discuss. No Joan plan-rubric verdict attached — noted, not a block.

**Pattern conformance:** `pattern.config.config-block`, `pattern.ui.admin-endpoint` cited in the ticket — not registered under `canon/patterns/`; functionally covered by `astral.config.config-source-of-truth` and `astral.patterns.require-auth-on-protected-endpoints` (both conforms).

## Frame diff
(none) — description AC/Boundaries/In-scope/Excluded checkboxes already reflect the shipped diff.

**What's solid:** Clean commit-role separation (`code(AST-1206)` → `src/` only; `test(AST-1206)` + `merge-tests(AST-1206)` → `tests/` + `docs/test-bible/` only, one merge-tests SHA). Debug-contract gating, config-block placement, and data-raises/caller-logs posture all match the AST-1067 precedent exactly.

context_tokens≈9000

— Radia

#### betty — 2026-08-06T05:39:00.068Z
Tests Ready — contact debug flag foundation (config / durable JSON / core get-set / admin GET-PUT).

**Publish:** `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation` @ `b52eb7c7`
**merge-tests:** `merge-tests(AST-1206): origin/tests 8c0cd1611e102797342afca924c1c6328b8c6cdf`

## QA test manifest

1. `tests/component/data/test_contact_debug.py::TestAst1206ContactDebugData` — missing/corrupt → `None`; save/load round-trip; TypeError; listen file untouched
2. `tests/component/utils/test_config.py::TestAst1206ContactDebugConfig` — `debug_enabled` default off; `debug_state_filename` = `contact_slack_debug.json` ≠ listen filename
3. `tests/component/core/test_contact.py::TestAst1206ContactDebugFlag` — default off; durable re-read every call; `set_slack_debug_enabled` persists; listen JSON untouched; TypeError
4. `tests/component/ui/api/test_api_contact.py::TestAst1206ContactDebugApi` — GET/PUT `/api/admin/contact/debug` payload + 400/502 + auth 401/403

**Broken / obsolete:** none — additive twin of listen; Events/React out of scope (AST-1207 / AST-1208).

**Integration:** no existing scenario asserts Contact debug API/file — no revision.

**Excluded (per ticket):** Style D golden-string tests — Radia enforces instrumentation on review.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_contact_debug.py::TestAst1206ContactDebugData \
  tests/component/utils/test_config.py::TestAst1206ContactDebugConfig \
  tests/component/core/test_contact.py::TestAst1206ContactDebugFlag \
  tests/component/ui/api/test_api_contact.py::TestAst1206ContactDebugApi \
  -q
```

**Bible shasums** (`origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation`):
- `docs/test-bible/data/contact_debug.md` `f508d72cbb6105268970eb6c2e61010848f53ad4`
- `docs/test-bible/core/contact.md` `903e5a8a7b15afa695709c08dc2db09576212eb9`
- `docs/test-bible/ui/api/api_contact.md` `070d70bc7b4f038fd5fc570cc56dd5eb6b49952e`
- `docs/test-bible/utils/config.md` `6b8eab2abf6125cea0c1566010825fd26e2de2e7`

— Betty

#### joan — 2026-08-06T05:31:45.427Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1206
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1203/AST-1206-contact-debug-flag-foundation` @ `3c789a10`

**Considered:** 59 of 65 active leaf statutes (18 universal + 41 scoped); 6 scoped excluded on layer/path predicates. Zero `violates`. Per-statute verdicts scored in-session (R7 slim comment; no attachment required).

## Traceability

AC1→S1–4 (config default + durable persist + core set/get + admin GET/PUT); AC2→S1 default-off + S3 `if debug:` gating. Stages→definition: S1→`pattern.config.config-block`; S2→AST-1067 durable-JSON reuse; S3→Functional scope 1 + `astral.standards.debug-contract-gated`; S4→`pattern.ui.admin-endpoint` + parent AC1. No unmapped AC, no orphan stage.

## Mirror claims verified

The plan rests on being a literal twin of shipped AST-1067 listen, so I checked every anchor rather than trusting the claim, and they are all exact:

- **Core** — the proposed `slack_debug_enabled` / `set_slack_debug_enabled` are line-for-line parallels of `src/core/contact.py:239-245` and `:280-308`, including the re-read-every-call posture (AST-1101) and the `index=1/2 → 2/2` found/recorded Style D shape. Because the two-header form is the shipped convention for exactly this operation, I am **not** scoring it against §1.5.1's per-batch-item reading. `logger` is module-level at that call site and `get_deploy_label()` is already in scope there (`:306`).
- **Insert anchors are real** — `set_slack_listen_enabled` ends at `:308` and `list_estelle_activity` begins at `:311`; `contact_put_listen` ends at `:58` and the `/estelle_activity` route is at `:62`; `listen_state_filename` is at `config.py:1578` with its assert at `:1641`. A builder can follow the stages literally, which is what `orch.pipeline.plan-is-bible` wants.
- **Admin surface** — `contact_bp` carries `url_prefix="/api/admin/contact"` (`api_contact.py:22`), so Stage 4's `/debug` resolves to the documented path; `require_admin`, `get_deploy_label`, `ui_llm_debug` and `logger` are already imported in that module, and the plan's core-import block matches the existing one plus the two new symbols.
- **Config and env** — `ASTRAL_CONFIG["db_dir"]` is `_DB_DIR`, overridden by `ASTRAL_DB_DIR` on Railway (`config.py:3511-3513`), so the per-environment volume claim holds and `astral.config.secrets-and-env-specific-from-environ` conforms with no new `os.environ` reads.
- **Data layer** — `astral.standards.database-header-inventory` conforms: its statement scopes to tables declared in `src/data/database.py`, and `contact_debug.py` adds none (JSON under `db_dir`). Note that `src/data/contact_listen.py` is unreadable to me under `.cursorignore`, so I validated the twin's contract indirectly from its core call sites — `load_...` returning `Optional[bool]` is confirmed by the `loaded is not None` check at `:242-244`, and `save_...(bool)` by `:286`.

## Findings

**discuss — `logger.set_debug_flag(True)` is never reset, and this child adds a second setter of that process-wide flag.** `set_slack_debug_enabled` flips the module-level logger's debug flag on and leaves it on for the life of the process, exactly as `set_slack_listen_enabled` does today. As a mirror it is not a new violation, which is why this is not blocking. The reason to raise it now: once inbound debug emission exists on this same module logger, a single admin PUT with `debug=True` would leave later processing wordy even with the durable Debug flag off, which is the shape of a parent AC3 regression. Cheapest containment inside this ticket is to restore the prior flag value after the emission block in `set_slack_debug_enabled` rather than leaving it latched. Worth flagging to Radia at review either way.

**discuss — the ticket promises the JSON key in config; the plan hardcodes it.** The In-scope line cites `astral.config.config-source-of-truth` / `no-hardcoded-sets` for "filename, default, **JSON key** in config", but Stage 2 writes the literal `"debug_enabled"` key inside `contact_debug.py`. I checked `CONTACT_CONFIG` and there is no listen JSON-key entry either, so the plan matches shipped precedent and a single serialization key is not a set or enum — the statute is satisfied on my read. Either add the key to config or trim that phrase from the ticket so the citation and the code agree.

**acceptable — read-per-call I/O posture.** `slack_debug_enabled()` stats and reads the durable file on every call by design (AST-1101 fixed sticky hydrate leaving listen latched). Within this child that is get/set only, so the cost is trivial; the plan correctly leaves inbound wiring to AST-1207 and says so.

**acceptable — helper placement.** `_debug_path` ahead of the public loaders, and `_debug_payload` ahead of the routes, both match the existing files' layout (`_listen_payload` sits at `api_contact.py:25` before its routes), so `astral.standards.public-then-helpers` is not newly violated.

**acceptable — Notes.** The Files Changed table omits the plan doc itself, so the matching algorithm dropped `astral.docs.features-single-file-per-ticket` and `astral.debug.spikes-under-debug-dir` on path predicates. Conformance verified out of band: one file at `docs/features/contact/ast-1206-contact-debug-flag-foundation.md`, correct project directory. Add a docs row next time so the corpus matches mechanically.

**acceptable — self-assessment is honest.** `Conf: high` is supportable here precisely because every mirror anchor resolved, and `Risk: low` is fair — default-off, separate file, no Events wiring, and a wrong persist would only affect the Debug SoT rather than listen or Estelle. `Single-Component` matches four files with one new module.

Boundaries hold: no `src/external/slack.py`, no Events handlers, no listen data/core/API, no React, no SQLite table, no `tests/`.

— Joan

context_tokens≈128000

#### ada — 2026-08-06T05:27:02.924Z
Plan published: https://github.com/susansomerset/astral/blob/sub/AST-1203/AST-1206-contact-debug-flag-foundation/docs/features/contact/ast-1206-contact-debug-flag-foundation.md (`origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation` @ `3c789a10`).

**Scope:** Single-Component — Contact config + new `contact_debug` data module + core get/set + admin GET/PUT; Events/React/listen left to siblings.

**Conf:** high — literal mirror of shipped AST-1067 listen durable JSON + admin surface, with AST-1101 re-read-every-call posture.

**Risk:** low — default-off separate file; no Events wiring in this ticket; listen/Estelle paths untouched.

---

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

---

## Resolution

**Date:** 2026-08-06  
**Radia overall:** CLEAN (`d7b9b07b` docs tip; product tip `b52eb7c7`)  
**Fix-now:** none  
**Discuss:** none (Joan plan-discuss notes from Plan Ready were non-blocking; Radia scored zero discuss)  
**Product changes this resolve:** none — tip already matches plan + CLEAN review.
