# AST-2067 — Version API routes (Artifact Edit Enhancements)

- **Ticket:** [AST-2067](https://linear.app/astralcareermatch/issue/AST-2067)
- **Parent:** [AST-2043 — Artifact Edit Enhancements](https://linear.app/astralcareermatch/issue/AST-2043)
- **Publish ref:** `origin/sub/AST-2043/AST-2067-version-api`
- **Depends on:** [AST-2066](https://linear.app/astralcareermatch/issue/AST-2066) (core list-versions / set-current functions; already on `origin/ftr/AST-2043-artifact-versions` and merged into this sub)

This ticket exposes sibling #1's version history over HTTP so the editors (sibling #3, [AST-2068](https://linear.app/astralcareermatch/issue/AST-2068)) can draw back/forward arrows. It adds six authenticated routes. Each catalog surface gets two: a GET that returns the chronological version map, and a PUT that moves `current` to a named version. The three surfaces are candidate catalog keys, one rubric criterion, and job catalog keys. The routes are thin. They check that the entity exists (404), turn core `ValueError`s into 400s (unknown or non-catalog keys, and uuids from another key, entity, or rubric code, which is the cross-key guard in AC 7), log unexpected exceptions once, and log one completion line on a successful PUT. They never write a body, so moving current is not a write-operative save. They do not touch the `proposed_answers` / `application_responses` routes. UI belongs to sibling #3 and core to sibling #1, and neither is planned here.

## Canon Scope (this ticket)

`patt.artifact.read-current`, `patt.artifact.write-operative`, `stat.logging.error`, `stat.logging.info.api`.

Resolved at `canon/directives/active/<id>.md`. The repo has no `docs/canon-index.md`, so the paths come from the parent's Architectural definition links (same as AST-2066).

## Explicit scope gate

Every file and change kind below comes from this ticket's `## Scope`:

- `src/ui/api/api_candidate.py`: "new authenticated routes: version list + set-current for candidate catalog keys and for a rubric criterion." This covers Stages 1 and 2.
- `src/ui/api/api_jobs.py`: "new authenticated routes: version list + set-current for job catalog keys." This covers Stage 3.

No other files are touched. The only new dependencies are imports of functions that already exist: AST-2066's core functions, and `ui.api_errors.server_error_from_exception`, which `src/ui/server.py` already uses. See the Decision under "Errors" below.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_candidate.py` | Import 4 core functions + `server_error_from_exception`. New routes `get_candidate_artifact_versions_api`, `put_candidate_artifact_current_api`, `get_rubric_criterion_versions_api`, `put_rubric_criterion_current_api` | ui |
| `src/ui/api/api_jobs.py` | Import 2 tracker functions + `server_error_from_exception`. New routes `get_job_artifact_versions_api`, `put_job_artifact_current_api` | ui |

## Shared conventions (apply to every stage)

- **Routes.** These are the six routes, with prefixes from the existing blueprints:

  | Method | Path | Body | 200 response |
  |--------|------|------|--------------|
  | GET | `/api/candidates/<candidate_id>/artifacts/<artifact_key>/versions` | none | `{"versions": {...}}` |
  | PUT | `/api/candidates/<candidate_id>/artifacts/<artifact_key>/current` | `{"artifact_uuid": "<uuid>"}` | `{"current": "<uuid>", "versions": {...}}` |
  | GET | `/api/candidates/<candidate_id>/rubric/<artifact_key>/<code>/versions` | none | `{"versions": {...}}` |
  | PUT | `/api/candidates/<candidate_id>/rubric/<artifact_key>/<code>/current` | `{"rubric_vector_uuid": "<uuid>"}` | `{"current": "<uuid>", "versions": {...}}` |
  | GET | `/api/jobs/<astral_job_id>/artifacts/<artifact_key>/versions` | none | `{"versions": {...}}` |
  | PUT | `/api/jobs/<astral_job_id>/artifacts/<artifact_key>/current` | `{"artifact_uuid": "<uuid>"}` | `{"current": "<uuid>", "versions": {...}}` |

  ⚠️ **Decision:** `<artifact_key>` is the **full catalog key** on the two artifact surfaces (`candidate.artifacts.base_resume`, `candidate.context.bio_summary`, `job.artifacts.cover_letter`, …). On the rubric surface it is the **rubric criteria key** (`do_rubric`, `jobdesc_rubric`, …, the keys of `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`), and `<code>` is the criterion code (`V01`). These are exactly the strings AST-2066's core functions take, so the route adds no key-resolution logic. The frontend today holds leaf keys (`artifactKey="base_resume"`, `contextKey="bio_summary"`), and sibling #3 builds the full key with `candidate.artifacts.${artifactKey}` / `candidate.context.${contextKey}` / `job.artifacts.${key}`. The rejected alternative was leaf keys in the URL with a leaf→catalog lookup in the route. That adds a resolver (a heuristic over the namespaces) that core doesn't have, and it would go wrong if two namespaces ever shared a leaf. Dots are legal in a Flask `<string>` path segment, and `encodeURIComponent` leaves them alone.

  ⚠️ **Decision:** Set-current is `PUT …/current` ("make this the current one", which is idempotent) rather than `POST`. That matches the existing `PUT …/artifacts/<leaf>` save routes. The new paths have more segments than every existing `/<id>/artifacts/<leaf>` route, so they cannot shadow them.

- **Version map shape.** This is AST-2066's map passed through unchanged: a dict keyed by row uuid, with each value `{"created_at": <str>, "current": <0|1>, "position": <1-based int>}`. Total = number of keys. An empty history is `{}` with 200, not 404.

  ⚠️ **Decision:** **`position` is the only order contract on the wire.** Flask 3.0's `DefaultJSONProvider.sort_keys` is `True` and the app does not override it (`rg sort_keys|json_provider src/ui` → none), so `jsonify` sends the uuid keys **alphabetically**, not chronologically. Sibling #3 orders versions by `position` (1 = oldest), not by JSON key order. Keeping the uuid-keyed dict follows Susan's index-by-id rule and AST-2066's shape. Turning off `sort_keys` app-wide would mean editing `src/ui/server.py` (out of scope) and would change every API response. Returning a list would break the index-by-id rule.

  ⚠️ **Decision:** The PUT returns the refreshed version map along with `current`, so the editor can redraw "N of M" without a second GET. Re-hydrating the body still goes through the existing current-read GET (`patt.artifact.read-current` Implementation #3). This route does not return the body.

- **Status codes** (parent Technical scope: "return 400 for unknown or non-versioned keys and for a uuid outside the key, and 404 for a missing entity"):
  - **404.** The entity is missing. Candidate: `get_candidate(candidate_id)` is falsy, so return `{"error": f"Candidate not found: {candidate_id}"}`, the same message as `get_candidate_detail`. Job: `get_job(astral_job_id)` is falsy, so return `{"error": "Not found"}`, the same as the existing job artifact PUTs. The entity check runs **first**, before body or key validation, matching existing routes.
  - **400 (body).** On a PUT, the uuid field is missing, not a string, or blank after strip, or the JSON body is not an object. Return `{"error": "artifact_uuid required"}` or `{"error": "rubric_vector_uuid required"}`. The route checks this because core's `(x or "").strip()` would raise `AttributeError` (a 500) on a non-string.
  - **400 (core `ValueError`).** Return `{"error": str(exc)}`. AST-2066's core raises `ValueError` for: unknown catalog key, a key owned by the wrong entity (a job key on the candidate route, a candidate key on the job route), a non-rubric criteria key, a blank code, and a uuid that is not a row of `(entity, key)` or `(candidate, task, code)`. That last case is the cross-key guard in AC 7. The data layer raises it before commit, so current is unchanged.
  - **Non-versioned keys.** `company_search_terms`, `application_responses`, `proposed_answers` and any other non-`ARTIFACT_CONFIG` key → core's `unknown catalog key` → 400. No extra allowlist in the route.

    ⚠️ **Decision:** `candidate.artifacts.resume_structure` is a real versioned catalog key, so the API serves it (200). The parent's "`resume_structure` has no arrows" is a UI rule that sibling #3 owns, and blocking it here would mean writing a second key list. If Archie wants the API to refuse it, add one `if artifact_key == "candidate.artifacts.resume_structure": return 400` line to both Stage 1 routes. Nothing else depends on this.

- **Errors (`stat.logging.error`).** Each route wraps its core call(s) in `try`. `except ValueError` returns 400 **without logging**: it is a routed validation reject that the handler answers, the same as `persist_skipped_edits` (`ValueError` → 400/409, no log). `except Exception` is an unrouted fault. It logs **once** with `logger.exception` (live facts, next step, traceback), then returns `server_error_from_exception(exc)`. The route never re-raises.

  ⚠️ **Decision:** The 500 response uses `server_error_from_exception` (`src/ui/api_errors.py`), the same payload the app-wide `@app.errorhandler(Exception)` in `src/ui/server.py` returns, so the frontend toast sees an identical 500 body. That global handler **does not log**. Letting the exception escape would leave nothing in `app_log`, and catching, logging and re-raising is a statute "Don't". So each route catches, logs, and returns the payload itself. Import: `from ui.api_errors import server_error_from_exception`. This uses the same `ui.` package root as `from ui.auth import …` in both files.

- **Info log (`stat.logging.info.api`).** Only a **successful PUT** emits one line at the route, just before its `return`:

  ```python
  logger.info("%s | api %s completed: PUT %s", <candidate_id>, route, 200)
  ```

  `<candidate_id>` is the path `candidate_id` on candidate routes, and `job.get("candidate_id") or "-"` on job routes. `route` is the concrete path string (f-string with the real ids/keys). GETs are idempotent reads, so they get no info line (statute: "Idempotent GETs that only return current state are not progress").

  ⚠️ **Decision:** Core `set_candidate_artifact_current` / `set_rubric_criterion_current` already emit a `stat.logging.info.entity` line (AST-2066). That is a different statute (entity event, Resolution #5), and the parent Architectural definition asks for both. The route line is the API completion. It is not a second copy of a `src/core/contact` line, so it does not hit the "core callee" Don't.

- **Write-operative / read-current.** Set-current is not a write-operative save. No body is created or changed and `save_artifact` is never called (`patt.artifact.write-operative`: moving current is metadata on existing rows). After a move, editors re-hydrate through the existing current-read GETs (`/api/candidates/<id>`, `/api/jobs/<id>`), per `patt.artifact.read-current` Implementation #3. Read-current Implementation #2's "invalidate candidate cache" has nothing to do here: there is no candidate artifact cache in `candidate.py` / `api_candidate.py` (grep `invalidat|_cache` → none).

---

## Stage 1: Candidate catalog key routes (version list + set-current)

**Done when:** With the Flask test client against a scratch DB, `GET /api/candidates/<cid>/artifacts/candidate.artifacts.base_resume/versions` returns 200 and the oldest-first map. `PUT …/current` with an older uuid returns 200 with that uuid current and logs one `api … completed: PUT 200` line. An unknown candidate returns 404. `candidate.artifacts.nope`, `job.artifacts.cover_letter`, and a uuid from another key or candidate each return 400 with current unchanged.

1. In `src/ui/api/api_candidate.py`, directly after the line `from ui.auth import require_auth, require_admin`, add:

   ```python
   from ui.api_errors import server_error_from_exception
   ```

2. In the same file, in the `from src.core.candidate import (...)` block:
   - directly after `    list_candidates as core_list_candidates,` add:

     ```python
         list_candidate_artifact_versions,
         list_rubric_criterion_versions,
     ```

   - directly after `    save_candidate_data,` add:

     ```python
         set_candidate_artifact_current,
         set_rubric_criterion_current,
     ```

   (Stage 2 uses the two rubric imports. They go in now so the import block changes only once.)

3. In the same file, directly after `get_operative_base_resume_api` (the function that ends with `    return jsonify({"base_resume": body})`) and before `@candidate_bp.route("", methods=["POST"])`, add:

   ```python
   @candidate_bp.route("/<candidate_id>/artifacts/<artifact_key>/versions", methods=["GET"])
   @require_auth
   def get_candidate_artifact_versions_api(candidate_id, artifact_key):
       """AST-2067: chronological version map for a candidate catalog key (oldest first)."""
       if not get_candidate(candidate_id):
           return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
       try:
           versions = list_candidate_artifact_versions(candidate_id, artifact_key)
       except ValueError as exc:
           # Unknown / non-candidate catalog key — routed reject, no log.
           return jsonify({"error": str(exc)}), 400
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the editor shows no version arrows",
               candidate_id,
               f"/api/candidates/{candidate_id}/artifacts/{artifact_key}/versions",
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       return jsonify({"versions": versions})


   @candidate_bp.route("/<candidate_id>/artifacts/<artifact_key>/current", methods=["PUT"])
   @require_auth
   def put_candidate_artifact_current_api(candidate_id, artifact_key):
       """AST-2067: move current to a named version of a candidate catalog key; body untouched."""
       if not get_candidate(candidate_id):
           return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
       body = request.get_json(silent=True)
       uid = body.get("artifact_uuid") if isinstance(body, dict) else None
       if not isinstance(uid, str) or not uid.strip():
           return jsonify({"error": "artifact_uuid required"}), 400
       route = f"/api/candidates/{candidate_id}/artifacts/{artifact_key}/current"
       try:
           current = set_candidate_artifact_current(candidate_id, artifact_key, uid)
           versions = list_candidate_artifact_versions(candidate_id, artifact_key)
       except ValueError as exc:
           # Bad key, or uuid outside this key/candidate (cross-key guard) — data layer rolled back.
           return jsonify({"error": str(exc)}), 400
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the editor keeps its loaded version",
               candidate_id,
               route,
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       logger.info("%s | api %s completed: PUT %s", candidate_id, route, 200)
       return jsonify({"current": current, "versions": versions})
   ```

## Stage 2: Rubric criterion routes (version list + set-current)

**Done when:** With the Flask test client against a scratch DB that has two versions of `V01` under `do_rubric`, `GET /api/candidates/<cid>/rubric/do_rubric/V01/versions` returns both oldest first. `PUT …/V01/current` with the older uuid returns 200, makes it V01's current, leaves every other code's current uuid unchanged, and logs one completion line. A uuid from `V02`, from another candidate, or the key `not_a_rubric` returns 400 with current unchanged. An unknown candidate returns 404.

1. In `src/ui/api/api_candidate.py`, directly after `put_candidate_artifact_current_api` (Stage 1), add:

   ```python
   @candidate_bp.route("/<candidate_id>/rubric/<artifact_key>/<code>/versions", methods=["GET"])
   @require_auth
   def get_rubric_criterion_versions_api(candidate_id, artifact_key, code):
       """AST-2067: chronological version map for one rubric criterion (shared code, oldest first)."""
       if not get_candidate(candidate_id):
           return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
       try:
           versions = list_rubric_criterion_versions(candidate_id, artifact_key, code)
       except ValueError as exc:
           # Not a rubric criteria key — routed reject, no log.
           return jsonify({"error": str(exc)}), 400
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the criterion shows no version arrows",
               candidate_id,
               f"/api/candidates/{candidate_id}/rubric/{artifact_key}/{code}/versions",
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       return jsonify({"versions": versions})


   @candidate_bp.route("/<candidate_id>/rubric/<artifact_key>/<code>/current", methods=["PUT"])
   @require_auth
   def put_rubric_criterion_current_api(candidate_id, artifact_key, code):
       """AST-2067: move current to a named version of one rubric criterion; other codes untouched."""
       if not get_candidate(candidate_id):
           return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
       body = request.get_json(silent=True)
       uid = body.get("rubric_vector_uuid") if isinstance(body, dict) else None
       if not isinstance(uid, str) or not uid.strip():
           return jsonify({"error": "rubric_vector_uuid required"}), 400
       route = f"/api/candidates/{candidate_id}/rubric/{artifact_key}/{code}/current"
       try:
           current = set_rubric_criterion_current(candidate_id, artifact_key, code, uid)
           versions = list_rubric_criterion_versions(candidate_id, artifact_key, code)
       except ValueError as exc:
           # Bad key, or uuid outside this candidate/task/code (cross-key guard) — data layer rolled back.
           return jsonify({"error": str(exc)}), 400
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the criterion keeps its loaded version",
               candidate_id,
               route,
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       logger.info("%s | api %s completed: PUT %s", candidate_id, route, 200)
       return jsonify({"current": current, "versions": versions})
   ```

   No new imports. Stage 1 step 2 already added both rubric functions.

## Stage 3: Job catalog key routes (version list + set-current)

**Done when:** With the Flask test client against a scratch DB, `GET /api/jobs/<jid>/artifacts/job.artifacts.cover_letter/versions` returns the oldest-first map. `PUT …/current` with an older uuid returns 200 with that uuid current and logs one completion line carrying the job's `candidate_id`. An unknown job returns 404. `candidate.artifacts.base_resume`, `job.artifacts.proposed_answers`, and a uuid from another job or key each return 400 with current unchanged.

1. In `src/ui/api/api_jobs.py`, directly after the line `from ui.auth import require_auth`, add:

   ```python
   from ui.api_errors import server_error_from_exception
   ```

2. In the same file, in the `from src.core.tracker import (...)` block:
   - directly after `    list_jobs_below_dispatch_score_floor,` add `    list_job_artifact_versions,`
   - directly after `    set_candidate_result,` add `    set_job_artifact_current,`

3. In the same file, directly after `put_job_proposed_answers` and before `@jobs_bp.route("/<astral_job_id>/skip", methods=["POST"])`, add:

   ```python
   @jobs_bp.route("/<astral_job_id>/artifacts/<artifact_key>/versions", methods=["GET"])
   @require_auth
   def get_job_artifact_versions_api(astral_job_id, artifact_key):
       """AST-2067: chronological version map for a job catalog key (oldest first)."""
       job = get_job(astral_job_id)
       if not job:
           return jsonify({"error": "Not found"}), 404
       try:
           versions = list_job_artifact_versions(astral_job_id, artifact_key)
       except ValueError as exc:
           # Unknown / non-job catalog key — routed reject, no log.
           return jsonify({"error": str(exc)}), 400
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the editor shows no version arrows",
               job.get("candidate_id") or "-",
               f"/api/jobs/{astral_job_id}/artifacts/{artifact_key}/versions",
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       return jsonify({"versions": versions})


   @jobs_bp.route("/<astral_job_id>/artifacts/<artifact_key>/current", methods=["PUT"])
   @require_auth
   def put_job_artifact_current_api(astral_job_id, artifact_key):
       """AST-2067: move current to a named version of a job catalog key; body untouched."""
       job = get_job(astral_job_id)
       if not job:
           return jsonify({"error": "Not found"}), 404
       body = request.get_json(silent=True)
       uid = body.get("artifact_uuid") if isinstance(body, dict) else None
       if not isinstance(uid, str) or not uid.strip():
           return jsonify({"error": "artifact_uuid required"}), 400
       cid = job.get("candidate_id") or "-"
       route = f"/api/jobs/{astral_job_id}/artifacts/{artifact_key}/current"
       try:
           current = set_job_artifact_current(astral_job_id, artifact_key, uid)
           versions = list_job_artifact_versions(astral_job_id, artifact_key)
       except ValueError as exc:
           # Bad key, or uuid outside this job/key (cross-key guard) — data layer rolled back.
           return jsonify({"error": str(exc)}), 400
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the editor keeps its loaded version",
               cid,
               route,
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       logger.info("%s | api %s completed: PUT %s", cid, route, 200)
       return jsonify({"current": current, "versions": versions})
   ```

   `tracker.set_job_artifact_current` does not log (AST-2066 Stage 4 Decision: `src/core/tracker` emits no entity line). This route line is the only info record of a job move.

## Verification (build-child §7)

- `python3 -m py_compile src/ui/api/api_candidate.py src/ui/api/api_jobs.py`
- `ruff check src/ui/api/api_candidate.py src/ui/api/api_jobs.py`: the baseline on this branch is **14** pre-existing findings. The count must not go up, and no finding may point at an AST-2067 line.
- No `.ts`/`.tsx` changes, so no `tsc`.
- Run each stage's **Done when** by hand with `app.test_client()` against a scratch DB (`debug/spikes/AST-2067/`, never committed). Local deploy env bypasses `require_auth` (synthetic operator).

## Notes for QA (Betty, informational only; no test-tree work in this ticket)

- **AC 7 (this ticket's AC).** Covered by all three PUT routes: a uuid from a different key (`base_resume` uuid on `…/candidate.context.bio_summary/current`), a different entity (another candidate's or job's uuid), or a different rubric code (V02 uuid on `…/V01/current`) → 400, and a follow-up GET shows the same `current` row as before.
- Body validation 400s (`artifact_uuid required` / `rubric_vector_uuid required`) are separate from the cross-key 400 (core message `… is not a version of …`).
- 404 runs before body validation, so an unknown entity with an empty body still returns 404.
- An empty history (key valid, no rows) returns 200 `{"versions": {}}`, not 404.
- Response JSON keys are sorted alphabetically by Flask, so assert chronology through each entry's `position`, not through key order.

## Estimate

Confirm Chuckles estimate: 2 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2067
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** 0cc6188afc2f2746087585ac5a6b7cf8aa52e6d8

## Canon scores

patt.artifact.read-current | A | | 
patt.artifact.write-operative | A | | 
stat.logging.error | A | | 
stat.logging.info.api | A | | 

## Traceability

AC7→St1+St2+St3 PUT routes (core `ValueError`→400 before commit; entity 404 first)

## Findings

### acceptable
- **Location:** Plan (whole doc)
- **Finding:** No Conf/Risk self-assessment block (Estimate confirm only).
- **Recommendation:** Same as AST-2066 — optional; not blocking for thin route ticket.

### discuss
- **Location:** Shared conventions — `resume_structure`
- **Finding:** Plan serves `candidate.artifacts.resume_structure` on the API while parent functional scope says Base Resume arrows step `base_resume` only (`resume_structure` has no arrows in UI).
- **Recommendation:** Sibling #3 can omit nav; optional one-line `if` 400 if Archie wants API parity with UI — not a canon defect.

- **Location:** Shared conventions — info logging
- **Finding:** Candidate/rubric PUTs will emit both `stat.logging.info.entity` (AST-2066 core) and `stat.logging.info.api` (this ticket); plan cites parent Architectural definition for both.
- **Recommendation:** Accept dual pipe (different statutes/events); job PUT remains API-only per tracker Notes.

context_tokens≈58000

## Review

- **Branch:** `origin/sub/AST-2043/AST-2067-version-api`
- **Build commits:** `03eebc50b` (Stage 1), `0bbf606ed` (Stage 2), `8abb0969e` (Stage 3)
- **Verified by hand (Flask test client + scratch DB, not committed):** each stage's Done when, including AC 7 on all three PUT surfaces. Cross-key, cross-entity, and cross-code uuids each return 400 and current is unchanged; wrong-surface, unknown, and non-catalog keys return 400; the uuid body check returns 400; a missing entity returns 404; empty history returns 200 `{}`; one `api … completed: PUT 200` line per successful PUT and none on GETs. Job routes stubbed only the `get_job` row lookup; artifact rows were real.
- **Lint deviation (resolved in favor of the code):** ruff TRY401 fires on the six planned `logger.exception(…, type(exc).__name__, exc)` calls, which match the `stat.logging.error` Do example. Blocker posted on AST-2043; Susan said continue, and the recommended option was taken: the code is unchanged, and the gate allows TRY401 on those six lines only. Ruff went from 14 to 20 across both files. The 6 new findings are exactly those TRY401s, with no other new findings.
