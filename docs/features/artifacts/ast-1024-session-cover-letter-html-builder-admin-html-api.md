# Session cover letter HTML builder + admin HTML API (Session Cover Letter)

**Linear:** [AST-1024](https://linear.app/astralcareermatch/issue/AST-1024/session-cover-letter-html-builder-admin-html-api-session-cover-letter)
**Parent:** [AST-1023](https://linear.app/astralcareermatch/issue/AST-1023/session-cover-letter) — Session Cover Letter
**Publish ref:** `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api`
**Unblocks:** [AST-1025](https://linear.app/astralcareermatch/issue/AST-1025/admin-session-cover-letter-page-session-retention) — Admin page + localStorage (consume this API only; do not implement React here)

Core session cover emit from an in-memory field payload (no job load; no artifact persist) producing golden SomersetCover HTML, plus an Admin `POST` HTML route under existing admin auth. Optional signature-image read from the **selected** candidate profile when a `candidate_id` is supplied — otherwise name-only sign-off. Owns Style D debug on touched backend paths. Does **not** own Admin React page, nav, or session retention.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["session_cover_letter"]` field contract (keys + required flags + document title) | utils |
| `src/core/builder.py` | Add `build_session_cover_letter` + session-only SomersetCover emit helpers; update module public list | core |
| `src/ui/api/api_admin.py` | Add `POST /api/admin/session_cover_letter/html` (`@require_admin`) — validate JSON, return `text/html` or JSON error | ui |

**Out of scope (do not touch):** React pages / `NAV_CONFIG` / routes / localStorage (AST-1025), job `build_cover_letter` / `build_cover_letter_from_job` / `_emit_cover_sections_html` / materials cover tabs, `TASK_CONFIG` / Manage Tasks / dispatch chains, candidate or job artifact writers, Session Resume Paste routes, `tests/`, bible, repo-root `artifacts/`.

## API contract (for AST-1025)

**`POST /api/admin/session_cover_letter/html`**
- Auth: `@require_admin` (same as Session Resume Paste admin tools).
- Request JSON:
  ```json
  {
    "from_block": "Susan Somerset • Oakland, CA\nhire@susansomerset.com • 415-745-5238",
    "letter_date": "July 27, 2026",
    "to_block": "",
    "subject": "",
    "letter": "Dear Hiring Team,\n\nParagraph two…",
    "signoff_closing": "Best,",
    "signature": "Susan Somerset",
    "candidate_id": null
  }
  ```
  - Field keys and required flags come from `BUILD_CONFIG["session_cover_letter"]["fields"]` (Stage 1).
  - `candidate_id`: optional. Omit, `null`, or `""` → no candidate read (name-only sign-off). Non-empty string → optional profile signature-image read only.
  - Aligns with cover artifact naming spine: `subject` ↔ `Subject`, `letter` ↔ `Letter`, `signature` ↔ `signature`. Session also carries layout fields (`from_block`, `letter_date`, `to_block`, `signoff_closing`) that job artifacts do not store today.
- Success **200**: raw HTML body, `Content-Type: text/html; charset=utf-8` (same pattern as `POST /api/admin/session_resume/html`).
- Client / validation failures **400**: `{ "success": false, "error": "<clear message>" }` — never return success HTML on failure.
- Unknown / missing candidate when `candidate_id` is non-empty: **400** with clear error (do not silently pretend no candidate).

**Detached rules (hard):**
- Do **not** load a job or read `job_data.artifacts.cover_letter`.
- Do **not** call `save_candidate`, job artifact writers, or any cover-letter chain task.
- Letter field values come **only** from the request body. Candidate row (when id provided) is used **only** for `profile.cover_letter_signature_image` via existing `_safe_image_src`.
- Do **not** change `/candidate/cover/<job_id>` or job cover emit DOM/CSS.

## Stage 1: Config field contract

**Done when:** `BUILD_CONFIG["session_cover_letter"]` exists with document title and the field map below; no other config blocks changed for this ticket.

1. In `src/utils/config.py`, inside `BUILD_CONFIG` (after `artifact_shapes` / near cover-related keys is fine), add:
   ```python
   "session_cover_letter": {
       "document_title": "SomersetCover",
       "fields": {
           "from_block": {"required": True},
           "letter_date": {"required": True},
           "to_block": {"required": False},
           "subject": {"required": False},
           "letter": {"required": True},
           "signoff_closing": {"required": True},
           "signature": {"required": True},
       },
   },
   ```
2. Do **not** add `NAV_CONFIG` entries (AST-1025).
3. Do **not** change `artifact_shapes["cover_letter"]` (Subject/Letter/signature stays the job artifact shape).

⚠️ **Decision:** Config owns the session field keys so AST-1025 form + this API share one spine without hardcoding duplicate required lists in React and Flask.

## Stage 2: Session SomersetCover builder (core)

**Done when:** `build_session_cover_letter` returns a standalone print-oriented HTML document whose DOM matches Original-brief SomersetCover blocks (`fromBlock`, optional `toBlock` / `lettersubject`, `letterdate`, `lettercontent`, `letterSignoff`); no job load; optional signature image only from selected candidate profile; empty/invalid required fields raise `ValueError` with clear messages; `debug=True` emits Style D headers + `|` detail.

1. In `src/core/builder.py` module docstring public list, append ``build_session_cover_letter``.
2. Add public function immediately after `build_session_base_resume`:
   ```python
   def build_session_cover_letter(
       fields: dict,
       *,
       candidate_id: Optional[str] = None,
       debug: bool = False,
   ) -> str:
   ```
3. When `debug=True`, call `_log.set_debug_flag(True)` before other work.
4. Validate `fields`:
   - If `fields` is not a `dict`, raise `ValueError("session cover letter fields object is required")`.
   - Read `cfg = BUILD_CONFIG["session_cover_letter"]` and `field_defs = cfg["fields"]`.
   - For each key in `field_defs`: coerce missing → `""`; require `isinstance(..., str)` else raise `ValueError(f"{key} must be a string")`; if `field_defs[key]["required"]` and not `value.strip()`, raise `ValueError(f"{key} is required")`.
   - Ignore unknown extra keys in `fields` (do not error).
5. Resolve optional signature image (read-only):
   - `sig_src = None`.
   - If `candidate_id` is a non-empty string after strip:
     - `row = candidate_mod.get_candidate(candidate_id.strip())`.
     - If not `row`, raise `ValueError(f"Candidate not found: {candidate_id.strip()}")`.
     - `cd = _coerce_candidate_blob(row)`; `profile = cd.get("profile") or {}`.
     - `sig_src = _safe_image_src(profile.get("cover_letter_signature_image"))` (may remain `None` → name-only sign-off).
   - If `candidate_id` is `None` / non-str / blank: do **not** call `get_candidate`.
6. Emit HTML via new helper `_emit_session_cover_html_document(fields, signature_image_src=sig_src) -> str` (see step 7). Do **not** call `_emit_html_document`, `_emit_cover_sections_html`, or job cover builders.
7. Implement `_emit_session_cover_html_document`:
   - Pull colors/fonts from `BUILD_CONFIG["default_style"]` the same way `_emit_html_document` reads accent / header / text / border / font stacks (literal defaults only as fallbacks matching today’s builder).
   - Document `<title>` and meta description use `BUILD_CONFIG["session_cover_letter"]["document_title"]` (and signature name when present for meta).
   - CSS: session-only SomersetCover rules from parent Original brief — `:root` tokens; `body` / `.cover-letter` / `.fromBlock` / `.toBlock` / `.letterdate` / `.lettersubject` / `.lettercontent` / `.lettercontent p` / `.letterSignoff` / `.signature-img` (`height: 61px`, `margin: 8px 0 -25px 0`); `@page` / `@media print` rules from the brief’s second `<style>` block. Do **not** copy the full resume body stylesheet (experience/skills/h2 chrome). Do **not** modify the CSS string inside `_emit_html_document`.
   - Body structure (escape all text with `html.escape`; image `src` via `_safe_image_src` only — already validated):
     ```html
     <main>
       <div class="cover-letter">
         <div class="fromBlock">…</div>          <!-- required; newlines → <br> between escaped lines -->
         <!-- optional .toBlock if to_block.strip() -->
         <div class="letterdate">…</div>
         <!-- optional .lettersubject if subject.strip() -->
         <div class="lettercontent">…</div>     <!-- paragraphs: see step 8 -->
         <div class="letterSignoff">…</div>     <!-- see step 9 -->
       </div>
     </main>
     ```
8. Paragraphize `letter`:
   - Normalize `\r\n` → `\n`, strip.
   - Split on blank lines: `re.split(r"\n\s*\n", text)`; keep non-empty stripped chunks as `<p>` bodies (escape each chunk; preserve single newlines inside a chunk as spaces, or as `<br>` — pick **`<br>`** after escape so pasted single-newline breaks survive).
   - If the split yields a single chunk that still contains `\n`, split that chunk on `\n` into separate `<p>` tags (form textarea UX).
9. Sign-off block (class `letterSignoff`):
   - Emit `html.escape(signoff_closing)` then `<br>`.
   - If `signature_image_src`: emit `<img src="..." class="signature-img" alt="Signature">` then `<br>` (`src` attribute-escaped with `html.escape(..., quote=True)`).
   - Emit `html.escape(signature)` (typed name — always, including when image present).
10. When `debug=True`, Style D:
    - Header: `func="builder.build_session_cover_letter"`, `index=1`, `total=1`, `identifier=candidate_id.strip() if candidate_id else "session"`, outcome `"success — session cover html"`.
    - Detail lines (`|`): which required fields were non-empty; `to_block`/`subject` present or omitted; `candidate_id` used or not; `signature_image=accepted|absent_or_rejected|skipped_no_candidate`; `html_chars=…`; optional truncated `html_preview` via `debug_detail_block`.
    - On validation failure before emit, use `_emit_builder_failure` with the same `func` name (mirror `build_session_base_resume`).
11. Return the HTML string. Forbidden: any `save_*` / artifact write / job fetch.

⚠️ **Decision:** Session-only golden cover DOM/CSS (Original brief), not a backfill of job `build_cover_letter`. Archie: no job cover upgrade this epic.

⚠️ **Decision:** Optional `candidate_id` is explicit in the request (Katherine passes selected id or omits). Server does not invent candidate context from Flask cookies/session beyond what the JSON body provides.

## Stage 3: Admin HTML route

**Done when:** `POST /api/admin/session_cover_letter/html` is registered on `admin_bp`, requires admin auth, returns `text/html` on valid body and JSON `{success:false,error}` on bad input / `ValueError`; `py_compile` clean on touched Python files.

1. In `src/ui/api/api_admin.py`, import `build_session_cover_letter` from `src.core.builder` (keep existing `build_session_base_resume` import; extend that import line). Import `BUILD_CONFIG` from `src.utils.config` if not already imported in this module.
2. Add route immediately after `session_resume_html` (leave comment `# AST-1024 session cover letter HTML`):
   ```python
   @admin_bp.route("/session_cover_letter/html", methods=["POST"])
   @require_admin
   def session_cover_letter_html():
       body = request.get_json(silent=True) or {}
       if not isinstance(body, dict):
           return jsonify({"success": False, "error": "JSON object body is required"}), 400
       # Field keys from config only — do not hardcode the key list here (Joan plan-discuss round=1).
       field_defs = BUILD_CONFIG["session_cover_letter"]["fields"]
       fields = {k: body.get(k, "") for k in field_defs}
       raw_cid = body.get("candidate_id")
       candidate_id = raw_cid.strip() if isinstance(raw_cid, str) else None
       if candidate_id == "":
           candidate_id = None
       try:
           html_out = build_session_cover_letter(
               fields,
               candidate_id=candidate_id,
               debug=ui_llm_debug(),
           )
       except ValueError as exc:
           return jsonify({"success": False, "error": str(exc)}), 400
       return Response(html_out, mimetype="text/html; charset=utf-8")
   ```
3. Do **not** register a new blueprint or change `server.py`.
4. Do **not** alter `/api/admin/session_resume/*` or `/candidate/cover/<job_id>`.
5. Compile: `python3 -m py_compile src/utils/config.py src/core/builder.py src/ui/api/api_admin.py`.

⚠️ **Decision:** API builds `fields` by iterating `BUILD_CONFIG["session_cover_letter"]["fields"]` so config remains the single key spine (AST-1025 form + Flask + core). `candidate_id` stays outside that map. Required/type validation stays in core (Stage 2).

## Self-Assessment

**Scope:** `Single-Component` — config field contract, one core session emit path beside `build_session_base_resume`, and one Admin POST HTML route; job cover emit and React left untouched.

**Conf:** `high` — mirrors AST-987 session HTML pattern (`build_session_base_resume` + admin POST); SomersetCover DOM/CSS is specified in the parent Original brief; signature-image reuse of `_safe_image_src` is known.

**Risk:** `Medium` — mistaken reuse of job cover emit or a write path would contaminate job/candidate artifacts or change materials preview; the plan forbids those paths and keeps session CSS/DOM isolated.

## Code rules check

- §1.1 / `in-scope-only`: no job cover backfill, no React/nav, no artifact writes.
- §1.3 DRY: new session emit helper; reuse `_safe_image_src` / `_coerce_candidate_blob` / `_emit_builder_failure`; do not fork job `_emit_cover_sections_html`. Stage 3 field keys iterated from config (no duplicate hardcoded list).
- §1.5.1: Style D only when `debug=True` via `ui_llm_debug()` / `debug=` pass-through.
- §2.1 / `no-hardcoded-sets`: field keys + title in `BUILD_CONFIG["session_cover_letter"]`; API maps body via those keys; style tokens from `default_style`.
- §2.9 / require-auth: `@require_admin` on the new Admin route.
- §3.3: ui → core + utils; core may call `candidate_mod.get_candidate` for optional image read.
- §3.6: no repo-root `artifacts/` directory.

## Revisions

Revision 1 — 2026-07-29
Driven by: Joan `[plan-discuss] round=1 concern` — Stage 3 hardcoded seven-key `body.get` dict duplicated `BUILD_CONFIG["session_cover_letter"]["fields"]` (violates config-source-of-truth / DRY / no-hardcoded-sets).
Changes: Stage 3 builds `fields = {k: body.get(k, "") for k in BUILD_CONFIG["session_cover_letter"]["fields"]}`; `candidate_id` remains outside the map; Decision + Code rules check updated.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1023/AST-1024-session-cover-letter-html-builder-admin-html-api`
**Tip:** `db3915d4`

**Stages delivered:**
- Stage 1 — `BUILD_CONFIG["session_cover_letter"]` field contract + document title
- Stage 2 — `build_session_cover_letter` + `_emit_session_cover_html_document` (SomersetCover; optional candidate signature image read-only)
- Stage 3 — `POST /api/admin/session_cover_letter/html` (`@require_admin`, fields from config keys)

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1024
**Publish ref tip (pre-docs):** `053830d3`
**Overall:** DISCUSS

### What’s solid
- Stages 1–3 match the plan bible: config field spine, session-only SomersetCover emit, Admin POST under `@require_admin`.
- Stage 3 iterates `BUILD_CONFIG["session_cover_letter"]["fields"]` (Joan Revision 1).
- No job cover reuse, no artifact writes, optional candidate signature via `_safe_image_src` only.
- Style D gated on `debug=True` / `ui_llm_debug()` with index + `|` detail + `debug_detail_block`.

### Issues
**discuss (C4 stragglers — Joan Excluded, in-scope on code diff):**
1. `astral.debug.spikes-under-debug-dir` — `docs/features/**` present (plan/review doc); substance conforms (not a misplaced spike).
2. `astral.docs.features-single-file-per-ticket` — single features file; substance conforms.
3. `astral.git.engineer-test-tree-ban` — `tests/**` + bible via Betty `test`/`merge-tests`; engineer `code()` touched only `src/`; substance conforms.

**fix-now:** none

### Recommended actions
- Ada: acknowledge C4 stragglers in resolve (no product change required) → User Testing.

## Resolution

**2026-07-29** — Radia `[code-rubric] revision=1` Overall DISCUSS; tip intake `d5813c67` (docs-only) after product `053830d3`.

- **fix-now:** none — no product changes.
- **discuss (C4 stragglers):** acknowledged — Joan Excluded statutes became in-scope via features/test-tree on the tip; substance already **conforms** (plan under `docs/features/`, single ticket file, Betty owns tests/bible; engineer `code()` was src-only). No product or plan-stage change.
- **advisory:** none.
