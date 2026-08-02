# AST-1141 — Admin Land Meteorite API for selected message ids

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1141/admin-land-meteorite-api-for-selected-message-ids-manage-email-select  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite  

**Publish ref (origin):** `sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`  
**Parent integration ref:** `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`

Thin authenticated admin HTTP surface for **Land Meteorite**: accept an explicit list of Astral inbox message ids, call AST-1140’s `run_gaze_email_selected_ids`, and return the per-id outcome payload (including skips) so Manage Email React (AST-1142) can show batch feedback without leaving the page. Does **not** own multi-select chrome or Create retirement (AST-1142). Does **not** own core ingest (AST-1140). Does **not** call the retired Create strip/extract path (`create_meteorite_job_from_inbox_message`).

**Depends on:** AST-1140 on `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite` (merge that tip before build — public `run_gaze_email_selected_ids` + `GAZE_EMAIL_CONFIG` selected outcome keys must exist).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_inbox.py` | Add `POST /land-meteorite` under existing inbox admin blueprint; `@require_admin`; call core selected-ids entrypoint; return per-id outcomes | ui |

No `src/core/**`, no React, no `src/utils/config.py` (outcome vocabulary already on AST-1140), no new blueprint, no `tests/` / bible.

---

## Stage 1: `POST /api/admin/inbox/land-meteorite`

**Done when:** An authenticated admin can `POST` a JSON body with a non-empty `message_ids` list and receive `200` with the AST-1140 result shape (`results` + totals). Empty / missing / non-list `message_ids` → `400`. Unauthenticated → `401`, non-admin → `403`. Upstream/core failures → `502`. The Create strip/extract helper is never imported or called from this route.

1. In `src/ui/api/api_inbox.py`, extend the module docstring to note AST-1141 Land Meteorite selected-ids admin mutator (keep the AST-1033/1047/1049/1061 lines).

2. Add imports (keep existing imports; add only what the new route needs):

```python
import asyncio

from src.core.gaze_email import run_gaze_email_selected_ids
```

Do **not** import `create_meteorite_job_from_inbox_message` for this route (it may remain for the legacy create-job route until AST-1142 retires Create).

3. Add this route on `inbox_bp` (after the existing create-job handler is fine — same blueprint prefix `/api/admin/inbox`):

```python
@inbox_bp.route("/land-meteorite", methods=["POST"])
@require_admin
def inbox_land_meteorite():
    body = request.get_json(silent=True) or {}
    raw_ids = body.get("message_ids")
    if not isinstance(raw_ids, list):
        return jsonify({"error": "message_ids must be a list"}), 400
    # Strip empties the same way core does; reject empty selection at the API edge
    # so Manage Email can treat empty as non-actionable without a core round-trip.
    message_ids = [str(x).strip() for x in raw_ids if str(x or "").strip()]
    if not message_ids:
        return jsonify({"error": "message_ids is required"}), 400
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        result = asyncio.run(
            run_gaze_email_selected_ids(message_ids, debug=debug)
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_inbox] land-meteorite failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify(result), 200
```

4. Response contract (pass-through of AST-1140 return dict — do **not** reshape keys):

```json
{
  "results": [
    {
      "message_id": "<id>",
      "outcome": "<string from GAZE_EMAIL_CONFIG / bound helper>",
      "astral_candidate_id": "<id or null>"
    }
  ],
  "total_processed": 0,
  "total_passed": 0,
  "total_failed": 0,
  "total_errors": 0,
  "total_skipped": 0
}
```

Skip outcomes already defined on AST-1140 (`skipped-unbound`, `skipped-not-in-inbox`, `skipped-unmatched`, plus bound outcomes such as `archived` / `ignored` / `failed` / `error`). AST-1142 renders these; this ticket only returns them.

5. Behavior rules (literal):

   - Call **only** `run_gaze_email_selected_ids` for the batch — never `create_meteorite_job_from_inbox_message`, never dispatcher `run_gaze_email(task)`.
   - Preserve caller order of non-empty ids (core already preserves order).
   - Do **not** stamp `last_email_check` in the API (core already does not).
   - Do **not** add React, nav, or Create-retirement logic here.
   - Do **not** invent a parallel Land-Meteorite config block; wire path is the literal `/land-meteorite` on the existing inbox admin blueprint (same pattern as `/messages` and `/messages/<id>/create-job`).

⚠️ **Decision — stay on `api_inbox.py`:** Manage Email already talks to `/api/admin/inbox/**` (AST-1033/1048/1049). Land Meteorite is the batch mutator for that same surface; a new blueprint would only split the inbox admin contract without a layer reason.

⚠️ **Decision — reject empty at the API edge:** Parent AC2 (“empty selection is not actionable”) is primarily UI, but the mutator must not silently no-op. Mirror create-job’s `400` for missing id so AST-1142 can rely on enablement + a hard server check.

⚠️ **Decision — `asyncio.run`:** `run_gaze_email_selected_ids` is async (shares `_handle_bound`). Other admin/async Flask routes already use `asyncio.run` (`api_admin` adhoc, `api_intake`). No new event-loop helper.

**Done when (recheck):**

- `python3 -m py_compile src/ui/api/api_inbox.py` succeeds.
- Route is registered: `POST /api/admin/inbox/land-meteorite` with `@require_admin`.
- Manual smoke (admin token): non-empty `message_ids` → `200` + `results` length matching stripped ids; `{}` or `"message_ids": []` → `400`; no Bearer → `401`.

---

## Self-Assessment

**Scope:** `Single-Component` — one new route on the existing inbox admin blueprint; no core or React.

**Conf:** `high` — AST-1140 return contract is on `ftr`; pattern matches `api_inbox` create-job + `asyncio.run` elsewhere; auth decorator already required on this blueprint.

**Risk:** `Medium` — mutator touches live mailbox ingest for selected ids; wrong wiring to Create strip/extract or missing `@require_admin` would be severe. Mitigations are explicit import/call ban on Create and `@require_admin` on the route.

---

## Code Rules check

- **§2.9 / `astral.patterns.require-auth-on-protected-endpoints`:** `@require_admin` on the mutator (stricter than `@require_auth`; matches every other inbox admin route).
- **§3.2 / `astral.layers.core-vs-external-bright-line`:** UI calls core only; no Gmail/external imports in `api_inbox.py`.
- **`astral.layers.ui-config-driven-business-logic`:** eligibility/skip/create decisions stay in core; API validates request shape and returns core outcomes; React (sibling) only renders.
- **§1.3 / `pattern.ui.admin-endpoint`:** thin Flask wrapper; no business rules invented in the route beyond empty-list / type guards.
- **§2.1:** no new config block; selected outcome vocabulary already in `GAZE_EMAIL_CONFIG` (AST-1140).
- **§3.3:** ui → core + utils only; no data/external imports added.

---

## Review

| Stage | Commit | Notes |
|-------|--------|-------|
| 1 | `e7144d4a` | `POST /api/admin/inbox/land-meteorite` → `run_gaze_email_selected_ids` |
