# AST-1097 — Restore archive-active intake API for Start Over

**Linear:** [AST-1097](https://linear.app/astralcareermatch/issue/AST-1097/restore-archive-active-intake-api-for-start-over-restart-intake-gets-a)  
**Parent:** [AST-1096](https://linear.app/astralcareermatch/issue/AST-1096/restart-intake-gets-a-500-error)  
**Publish ref:** `sub/AST-1096/AST-1097-restore-archive-active-intake-api`

UAT Start Over posts `POST /api/candidates/{id}/intake/sessions/active/archive` and fails (500 / “method is not allowed”) because `src/ui/api/api_intake.py` has no archive route on the current line — core `archive_active_intake_session` and React `CandidateIntake.handleResumeStartOver` already exist (AST-582 / AST-583 lineage). Restore the thin authenticated UI endpoint that maps core success / not-found / auth outcomes so Start Over can clear the active session and open a fresh preamble.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_intake.py` | Import `archive_active_intake_session`; add `POST /<candidate_id>/intake/sessions/active/archive` with `@require_auth`, candidate 404, LookupError→404 (no active session), ValueError→404/400 as below, success→200 JSON from core | ui |

## Stage 1: Wire `POST …/sessions/active/archive`

**Done when:** Authenticated `POST /api/candidates/{candidate_id}/intake/sessions/active/archive` with an active session returns **200** and a JSON body with `archived_session_id`, `archived_at`, and `intakes_old_count` (core return keys); with no active session returns **404** `{"error": "no active intake session"}` (UI already treats 404 as tolerable); without auth returns **401**; unknown candidate returns **404**. After a successful archive, `GET …/sessions/active` returns **404** (no active session). Create/get-active/turns/build/preamble/topic-menu routes are unchanged.

1. In `src/ui/api/api_intake.py`, add `archive_active_intake_session` to the existing `from src.core.intake import (` block (alphabetically among the other intake imports — place after `create_intake_session_and_start` / with the other `archive_*` / `fetch_*` names; keep the import list core-only — do **not** import `database` or `src.data`).

2. Immediately after `get_active_session` (the `GET …/sessions/active` handler, currently ending ~L89), register:

   ```python
   @intake_bp.route("/<candidate_id>/intake/sessions/active/archive", methods=["POST"])
   @require_auth
   def archive_active_session(candidate_id):
       if not get_candidate(candidate_id):
           return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
       try:
           result = archive_active_intake_session(candidate_id)
       except LookupError as e:
           return jsonify({"error": str(e)}), 404
       except ValueError as e:
           return jsonify({"error": str(e)}), 404
       return jsonify(result), 200
   ```

3. Do **not** change `archive_active_intake_session` in `src/core/intake.py`, `CandidateIntake.tsx`, `IntakeChatModal.tsx`, preamble/topic-menu routes, or `intakes_old` shape. Core already raises `LookupError("no active intake session")` when none is active and `ValueError` when the candidate is missing; the handler above maps both to **404** so the React Start Over path (`!r.ok && r.status !== 404`) stays compatible.

⚠️ **Decision:** Map core `ValueError` (candidate missing) to **404**, not **400** — matches sibling intake handlers (`get_active_session`, `get_session`) that 404 when `get_candidate` fails, and the pre-check already returns 404 before calling core; the `except ValueError` is defense-in-depth if core is called without that guard later.

⚠️ **Decision:** Restore only the UI API route — do not re-implement archive logic in the blueprint. AST-582 core + AST-590 `save_candidate_data` contract already work; this ticket’s failure mode is a missing HTTP surface (clean-baseline / route gap), not a core bug.

## Self-Assessment

**Scope:** minor — one new route + one import in `src/ui/api/api_intake.py`.

**Conf:** high — AST-582 already defined this exact endpoint contract; core and React callers are present; sibling handlers in the same file show the `@require_auth` + `get_candidate` + exception-map pattern.

**Risk:** Medium — Start Over / archive is on the live intake lifecycle path; wrong status mapping could break the UI’s 404-tolerant Start Over or leave an active session uncleared. Mitigated by reusing core return keys and matching AST-582 API expectations (`requires_auth`, `404_when_none`, `200_shape`).

## Code Rules self-review

| Rule | Check |
|------|--------|
| §2.9 / `astral.patterns.require-auth-on-protected-endpoints` | `@require_auth` on the mutator |
| §3.3 / `astral.layers.import-direction` | UI → `src.core.intake` + `src.core.candidate` only; no UI→data |
| `pattern.ui.admin-endpoint` | Thin blueprint: auth, candidate lookup, delegate, map exceptions to JSON status |
| `astral.standards.data-raises-caller-logs` | Core raises; API maps to status codes — no swallowed errors |
| `astral.standards.in-scope-only` | No React, preamble, topic-menu, or core archive edits |
| §1.3 DRY | Reuse `archive_active_intake_session` — do not duplicate archive / `intakes_old` logic in UI |

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-1097 |
| Publish ref | `origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api` |
| Built | `094477b9` |
| Notes | Stage 1 — `POST …/sessions/active/archive` in `api_intake.py`. |
