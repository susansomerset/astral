# AST-1235 — Versioned consent record and API

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1235/versioned-consent-record-and-api-consent-install-disclosure  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch  

**Publish ref (origin):** `sub/AST-1173/AST-1235-versioned-consent-record-and-api`  
**Parent integration ref:** `ftr/AST-1173-consent-install-disclosure-affirmative-opt-in-and-off-switch`

Ship the durable **server-side Surfer consent record** under `candidate_data` plus an authenticated read/write HTTP surface so the extension and any web off-switch can answer: has this candidate consented, and to which disclosure wording? Parent AC3 (survive reinstall) and AC5 (config version reflects accepted wording) land here. Re-consent when the disclosure version bumps is enforced in core (`is_current` only when status is opted-in **and** `accepted_version` equals config `current_version`).

Boundaries (do **not** implement): install disclosure UI / affirmative opt-in chrome (**AST-1237**); off-switch placement / capture-path no-op gate (**AST-1238**); extension shell (**AST-1170**); legal review of copy.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `SURFER_CONSENT_CONFIG` (version, provisional disclosure copy, status vocabulary, `candidate_data_key`); module asserts; header inventory line | utils |
| `src/core/candidate.py` | Surfer consent normalize / get / is_current / opt-in / opt-out helpers + Style D found/recorded when `debug=True` | core |
| `src/ui/api/api_surfer.py` | New blueprint: `GET`/`PUT` `/api/candidates/<id>/surfer/consent` with `@require_auth` | ui |
| `src/ui/server.py` | Register `surfer_bp` | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `surfer_consent` meta sibling | docs |

No React pages, no database schema migration (meta key under existing `candidate_data` JSON), no extension code, no `tests/` / bible edits (Betty after Code Complete).

---

## Stage 1: `SURFER_CONSENT_CONFIG` contract

**Done when:** `SURFER_CONSENT_CONFIG` is importable from `src.utils.config` with a stable `candidate_data_key`, closed `statuses` tuple, non-empty `current_version` string, and non-empty `disclosure_copy` string; module asserts fail loudly on drift.

1. In `src/utils/config.py`, in the top-of-file Config sections inventory comment, add a line after `TOPIC_MENU_GEN_CONFIG` (or nearest Surfer-adjacent spot if one exists later):

   `SURFER_CONSENT_CONFIG — Surfer install disclosure version + copy + consent status vocabulary (AST-1235; UI = AST-1237/1238)`

2. Immediately **after** the `TOPIC_MENU_CONFIG` asserts block (before `TOPIC_MENU_GEN_CONFIG`), add:

```python
# AST-1235: versioned Surfer consent record (install UI = AST-1237; off-switch gate = AST-1238).
SURFER_CONSENT_CONFIG = {
    # Stable key under candidate_data (meta sibling of contact/context/artifacts/topic_menu).
    "candidate_data_key": "surfer_consent",
    # Bump this string when disclosure_copy changes; prior opt-ins stop being "current".
    "current_version": "1",
    # Friends-and-family provisional copy (parent Purpose / Functional scope). AST-1237 may
    # refine wording in the same keys — do not invent a second config block for copy.
    "disclosure_copy": (
        "Astral Surfer uses your own logged-in session on LinkedIn and Indeed to pull job "
        "postings into Astral. That use is not sanctioned by those sites' terms. We have "
        "designed the extension to behave like ordinary manual browsing to keep the risk "
        "low, but we cannot promise a site will never notice. If it does, any account-level "
        "consequence (warning, suspension) is yours, not Astral's.\n\n"
        "Surfer is optional — the rest of Astral works without it. This only reaches sources "
        "Astral otherwise cannot. You can turn Surfer off later from the extension or your "
        "Astral account."
    ),
    # Stored record statuses. Absence / unknown → treat as "none" in normalize.
    "statuses": ("none", "opted_in", "opted_out"),
    "default_status": "none",
}
```

3. Immediately after the block, add asserts:

   - `candidate_data_key == "surfer_consent"`.
   - `current_version` is a non-empty `str` after strip.
   - `disclosure_copy` is a non-empty `str` after strip.
   - `statuses` is a `tuple` equal to `("none", "opted_in", "opted_out")`.
   - `default_status` is in `statuses` and equals `"none"`.
   - `len(statuses) == len(set(statuses))`.

⚠️ **Decision:** One config block owns both **version** and **disclosure_copy**. Parent child #2 (**AST-1237**) owns install UI that *displays* the copy; it must not invent a parallel copy source — refine `disclosure_copy` / bump `current_version` here if wording changes. This ticket seeds provisional friends-and-family prose from the parent brief so AC5 is executable without waiting on #2.

⚠️ **Decision:** Version is an opaque non-empty string (`"1"`, `"2"`, …), not a content hash. Operators bump `current_version` whenever `disclosure_copy` changes. Core compares equality only.

---

## Stage 2: Core Surfer consent helpers

**Done when:** `src/core/candidate.py` exposes public helpers that load/store `candidate_data.surfer_consent`, compute `is_current` against config, and persist opt-in / opt-out; `debug=True` emits Style D found/recorded lines; no Flask routes yet.

1. Near the Topic Menu helpers in `src/core/candidate.py`, import `SURFER_CONSENT_CONFIG` from `src.utils.config` (add to the existing config import list).

2. Add `_surfer_consent_key() -> str` returning `str(SURFER_CONSENT_CONFIG["candidate_data_key"])`.

3. Add `_surfer_consent_now() -> str` returning UTC timestamp via `datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")` (same format as other candidate timestamps in this module). Import `datetime` / `timezone` if not already imported in the file.

4. Add `empty_surfer_consent() -> dict` returning:

```python
{
    "status": SURFER_CONSENT_CONFIG["default_status"],  # "none"
    "accepted_version": None,
    "updated_at": None,
}
```

5. Add `normalize_surfer_consent(raw: Any) -> dict`:

   - If `raw` is not a `dict`, return `empty_surfer_consent()`.
   - `status`: if `raw.get("status")` is in `SURFER_CONSENT_CONFIG["statuses"]`, use it; else `"none"`.
   - `accepted_version`: if value is a non-empty `str` after strip, keep stripped string; else `None`.
   - `updated_at`: if value is a non-empty `str` after strip, keep stripped string; else `None`.
   - Ignore unknown extra keys (do not persist them in the returned dict).
   - Return only those three keys.

6. Add `get_surfer_consent(candidate_id: str) -> dict`:

   - Load candidate via existing `get_candidate`; if missing, raise `ValueError(f"Candidate not found: {candidate_id}")`.
   - Return `normalize_surfer_consent((candidate.get("candidate_data") or {}).get(_surfer_consent_key()))`.

7. Add `is_surfer_consent_current(record: Any) -> bool`:

   - `n = normalize_surfer_consent(record)`.
   - Return `True` **only** when `n["status"] == "opted_in"` **and** `n["accepted_version"] == SURFER_CONSENT_CONFIG["current_version"]`.
   - Opted-in with a stale version → `False` (re-consent required — parent Open question 1 answer).
   - `opted_out` / `none` → `False`.

8. Add `surfer_consent_dto(candidate_id: str) -> dict` — read model for API / siblings:

   - `record = get_surfer_consent(candidate_id)`.
   - Return:

```python
{
    "status": record["status"],
    "accepted_version": record["accepted_version"],
    "updated_at": record["updated_at"],
    "current_version": SURFER_CONSENT_CONFIG["current_version"],
    "disclosure_copy": SURFER_CONSENT_CONFIG["disclosure_copy"],
    "is_current": is_surfer_consent_current(record),
}
```

⚠️ **Decision:** Include `disclosure_copy` + `current_version` on the DTO so **AST-1237** / **AST-1238** can render and gate from one GET without inventing a second config reader. This ticket still does not build disclosure UI.

9. Add `opt_in_surfer_consent(candidate_id: str, accepted_version: Any, *, debug: bool = False) -> dict`:

   - `logger.set_debug_flag(debug)` at entry.
   - If `accepted_version` is not a non-empty `str` after strip, raise `ValueError("accepted_version must be a non-empty string")`.
   - Strip it. If it does **not** equal `SURFER_CONSENT_CONFIG["current_version"]`, raise `ValueError("accepted_version does not match current disclosure version")`.
   - Build `to_store = {"status": "opted_in", "accepted_version": accepted_version, "updated_at": _surfer_consent_now()}`.
   - When `debug=True`, emit Style D **found** then **recorded** (`logger.debug_index` / `debug_detail`, `func="candidate.opt_in_surfer_consent"`, identifier=`candidate_id`, index `1/2` then `2/2`): found = normalize of current record; recorded = `to_store`.
   - Persist with `save_candidate_data(candidate_id, {_surfer_consent_key(): to_store}, debug=debug)`.
   - Return `surfer_consent_dto(candidate_id)`.

10. Add `opt_out_surfer_consent(candidate_id: str, *, debug: bool = False) -> dict`:

    - `logger.set_debug_flag(debug)` at entry.
    - Load current via `get_surfer_consent` (ensures candidate exists).
    - Build `to_store = {"status": "opted_out", "accepted_version": current["accepted_version"], "updated_at": _surfer_consent_now()}` — **preserve** last `accepted_version` for audit (which wording she had accepted before turning off); status alone drives `is_current` → `False`.
    - When `debug=True`, same found/recorded Style D pattern with `func="candidate.opt_out_surfer_consent"`.
    - Persist via `save_candidate_data` as above.
    - Return `surfer_consent_dto(candidate_id)`.

⚠️ **Decision:** No append-only event history table in this ticket. Current record + timestamps + preserved `accepted_version` on opt-out is the auditable answer for AC3/AC5. A future consent-history pattern can extend later (parent flagged the pattern for Archie).

⚠️ **Decision:** Helpers live in `src/core/candidate.py` next to Topic Menu (same `candidate_data` meta + `save_candidate_data` path). Do not create `src/core/surfer_consent.py` in this ticket.

---

## Stage 3: Authenticated Surfer consent API

**Done when:** `GET` and `PUT` `/api/candidates/<candidate_id>/surfer/consent` are registered, require auth, call core helpers only, and return the DTO JSON; missing candidate → 404; validation errors → 400.

1. Create `src/ui/api/api_surfer.py`:

```python
"""Surfer consent API (AST-1235). Extension + web off-switch share this record."""

from flask import Blueprint, jsonify, request

from src.core.candidate import (
    get_candidate,
    opt_in_surfer_consent,
    opt_out_surfer_consent,
    surfer_consent_dto,
)
from src.utils.deploy_status import ui_llm_debug
from ui.auth import require_auth

surfer_bp = Blueprint("surfer", __name__, url_prefix="/api/candidates")


def _debug_flag() -> bool:
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    return ui_llm_debug(explicit_debug=explicit)
```

2. Add `GET /<candidate_id>/surfer/consent` with `@require_auth`:

   - If `get_candidate(candidate_id)` is missing → `{"error": f"Candidate not found: {candidate_id}"}` 404.
   - Return `jsonify(surfer_consent_dto(candidate_id))` 200.
   - Do **not** call opt-in/opt-out on GET (read-only).

3. Add `PUT /<candidate_id>/surfer/consent` with `@require_auth`:

   - If candidate missing → 404 (same message).
   - Body = `request.get_json(silent=True) or {}`.
   - Read `action = body.get("action")`.
   - If `action == "opt_in"`: call `opt_in_surfer_consent(candidate_id, body.get("accepted_version"), debug=_debug_flag())`; on `ValueError` → 400 `{"error": str(e)}`; on success → 200 JSON DTO.
   - If `action == "opt_out"`: call `opt_out_surfer_consent(candidate_id, debug=_debug_flag())`; on `ValueError` → 400; success → 200 JSON DTO.
   - Else → 400 `{"error": "action must be opt_in or opt_out"}`.

⚠️ **Decision:** Single resource `PUT` with `action` rather than separate opt-in/opt-out routes — thin admin-endpoint shape (candidate-facing blueprint, not under `/api/admin`). Matches parent citation: reuse admin-endpoint shape only.

⚠️ **Decision:** Auth is `@require_auth` only — same candidate-path pattern as intake (`api_intake.py`). Do **not** invent per-candidate ownership binding in this ticket (friends-and-family Stytch sessions already gate the UI; extension auth wiring is **AST-1170** / sibling scope).

4. In `src/ui/server.py`, register the blueprint next to the other API imports (after intake is fine):

```python
from ui.api.api_surfer import surfer_bp  # noqa: E402
app.register_blueprint(surfer_bp)
```

5. Do **not** add Surfer consent fields to `GET /api/ui_config` in this ticket — clients use the consent GET DTO (includes copy + version). If a later React page wants catalog-only config without a candidate id, that ticket can extend `ui_config`.

---

## Stage 4: Document `surfer_consent` on the candidate data model

**Done when:** `CANDIDATE_DATA_MODEL.md` lists `surfer_consent` as a meta sibling and documents the record shape + `is_current` rule; no claim that meta is only lifecycle/intakes/topic_menu.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under `candidate_data (library + meta)`:

   - Extend the meta-siblings sentence to include `surfer_consent` (AST-1235).

2. Add subsection **### surfer_consent (AST-1235 / AST-1173)** after the `topic_menu` subsection:

```text
candidate_data.surfer_consent = {
  "status": "none" | "opted_in" | "opted_out",
  "accepted_version": "<str matching a SURFER_CONSENT_CONFIG current_version at opt-in>" | null,
  "updated_at": "<UTC YYYY-MM-DD HH:MM:SS>" | null
}
```

   - Config: `SURFER_CONSENT_CONFIG` in `src/utils/config.py` (`current_version`, `disclosure_copy`).
   - Core: `get_surfer_consent` / `is_surfer_consent_current` / `opt_in_surfer_consent` / `opt_out_surfer_consent` / `surfer_consent_dto` in `src/core/candidate.py`.
   - API: `GET`/`PUT /api/candidates/<id>/surfer/consent` (`src/ui/api/api_surfer.py`).
   - `is_current` is true only when `status == opted_in` and `accepted_version == SURFER_CONSENT_CONFIG["current_version"]`. Bumping `current_version` requires re-consent before capture may resume (enforced by siblings reading `is_current`).
   - Survives extension reinstall because the record is server-side under the candidate, not extension storage.
   - Install disclosure UI = **AST-1237**; off-switch + capture no-op = **AST-1238**.

3. Do **not** place Surfer consent under `contact` / `context` / `artifacts`.

---

## Self-Assessment

**Scope:** `Single-Component` — config contract + candidate core persistence helpers + thin authenticated blueprint + data-model doc; no React, no extension, no schema migration.

**Conf:** `high` — mirrors AST-1074 meta-sibling + `save_candidate_data` + intake-style `@require_auth` blueprint already on this line; parent open questions (re-consent; shared server record) are resolved.

**Risk:** `Medium` — a wrong `is_current` rule would either skip re-consent after a copy bump or falsely block capture; mitigated by equality check against config `current_version` and sibling tickets consuming `is_current` rather than raw status. Wrong action validation could record opt-in without a matching version — mitigated by server-side version match on opt-in.

---

## Code rules self-review

| Rule | Plan check |
|------|------------|
| §1.3 DRY | Reuse `save_candidate_data` / `get_candidate`; no parallel JSON writer |
| §2.1 config | Version, copy, statuses, key all in `SURFER_CONSENT_CONFIG`; no hardcoded sets in core/UI |
| §2.4 batch | N/A — candidates are not batch-claimed for consent |
| §2.6 state machine | Does not change `CANDIDATE_STATES`; consent is meta, not a lifecycle state |
| §2.9 / require-auth | Both routes `@require_auth` |
| §3.3 imports | UI → core + utils only; core uses data via existing `save_candidate_data` |
| §3.5 naming | `surfer_consent` / `SURFER_CONSENT_CONFIG` / `api_surfer.py` |
| §1.5.1 debug | Style D found/recorded gated on `debug=True` on write paths |
| Test tree | No `tests/` / bible edits |

No unresolved conflicts → Conf stays `high`.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1173/AST-1235-versioned-consent-record-and-api`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `6b3b49b0` | Plan doc |
| 1–4 | `aa0a6392` | `SURFER_CONSENT_CONFIG` + core helpers + `api_surfer` GET/PUT + data-model doc |

**Tip:** `aa0a6392` on publish ref (no PR yet).

---

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1
**Publish ref tip:** `f3ab8cce` (`sub/AST-1173/AST-1235-versioned-consent-record-and-api`)
**Overall:** CLEAN

Full 65-statute active set scored in-session against `git diff origin/dev...origin/sub/AST-1173/AST-1235-versioned-consent-record-and-api`. No `violates`, no `needs-discussion`. Four `not-applicable` (no `src/data/**`, `src/ui/frontend/**`, `scripts/**`, or `artifacts/**` touched by this diff). No Joan plan-rubric verdict attached — noted, not a block.

**What's solid**

- `SURFER_CONSENT_CONFIG` is the single source for version/copy/status vocabulary; core validates status against the config tuple, never an inline set (`astral.standards.no-hardcoded-sets`).
- `opt_in_surfer_consent` / `opt_out_surfer_consent` reuse the exact found(1/2)/recorded(2/2) Style D idiom already established at `mark_topic_menu_preamble_confirmed` (line ~1029) — debug-gated correctly, `debug_index` / `debug_detail` signatures match `src/utils/logging.py`.
- `_surfer_consent_key()` placed ahead of the public block matches the file's existing per-feature grouping convention (`_topic_menu_key()` precedent) — not a `public-then-helpers` violation.
- Both routes carry `@require_auth`; UI layer imports core + utils only; core raises `ValueError`, UI catches and returns 400/404 JSON.
- Git hygiene clean: single `merge-tests` commit citing one `origin/tests` SHA, correct commit vocabulary, engineer commit touches only `src/` + `docs/features/`, test commits touch only `tests/` + `docs/test-bible/`.
- Pattern conformance: `pattern.config.config-block` and `pattern.ui.admin-endpoint` both conform (config-block shape; auth + config-driven + thin API shape — candidate-facing placement is a documented plan decision, not admin-blueprint scope creep).

**Plan adherence:** Diff matches the four-stage plan (config contract, core helpers, API blueprint + registration, data-model doc) file-for-file; no extra `src/` scope. Self-Assessment `Conf: high` holds — no unresolved conflicts found.

**Frame diff:** none (description frame unchanged; diff matches plan as written).

context_tokens≈45000
— Radia

---

## Resolution

**Date:** 2026-08-07  
**Review:** `[code-rubric] revision=1` — **CLEAN** (no fix-now, no discuss).  
**Action:** No product changes. Radia `docs(AST-1235): Radia review — clean` already on publish tip via sync. Resolve commit records clean close-out before User Testing.
