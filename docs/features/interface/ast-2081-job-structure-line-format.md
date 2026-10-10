# AST-2081 — Job-scoped structure, Line format, format/flow catalog (Resume Edit Overhaul)

- **Parent:** [AST-2046 Resume Edit Overhaul](https://linear.app/astralcareermatch/issue/AST-2046)
- **Ticket:** [AST-2081](https://linear.app/astralcareermatch/issue/AST-2081)
- **Publish ref:** `sub/AST-2046/AST-2081-job-structure-line-format` (origin only)
- **Depends on:** nothing in this epic. Siblings #2–#4 (AST-2082, AST-2083, AST-2084) consume this ticket's payloads and routes; none of their files are touched here.
- **Canon Scope:** `patt.artifact.manage-catalog`, `patt.artifact.read-current`, `patt.artifact.write-operative`, `stat.logging.info.api`, `stat.logging.error`, `stat.logging.debug`.

This ticket ships the whole backend for the resume edit overhaul. A job resume gets its own structure: a new catalog key `job.artifacts.job_resume_structure`, an effective read that falls back to the candidate's structure until the job is edited, a catalog write, and GET/PUT routes. Job resume content prep and job resume print HTML (sections, order, titles, accent) use that effective structure. A new `line` body format prints as one line. The structure-editor payload is lifted out of the candidate route into one shared helper. Its catalog gains per-format labels, tooltip descriptions, and preview fonts, plus a Hidden flow label. The recommended-job artifact tabs gain a preview-thumbnail flag. There is no UI work here.

## Ground truth (verified on this branch at `b96f60588`)

- **Body formats:** `src/utils/config.py` L6943–6950 `RESUME_STRUCTURE_BODY_FORMATS` = `free_prose, bullet_list, word_cloud, dual_column, indented_bold_single, experience_detail`. Page-break labels are at L6958–6962 (`normal` → "Flow uninterrupted", `page_break_before` → "New page before", `avoid_split` → "Keep block together"). `BUILD_CONFIG` (L6040) is defined **before** these constants, so asserts against `BUILD_CONFIG["default_style"]["fonts"]` are legal there.
- **Fonts:** `BUILD_CONFIG["default_style"]["fonts"]` (L6042–6047) has `heading_stack`, `body_stack`, `list_stack`, `mono_stack`. In the builder CSS (`src/core/builder.py` L1303–1330, L1394–1405): `.summary-intro`, `p`, `ul`, `li`, and `.role-description` use the body font; `.competencies-list` (word cloud) and `.skill-category p` (dual column) use the list font.
- **Catalog:** `ARTIFACT_CONFIG` is at L6346–6435. The closed key-set assert is at L6437–6449. L6451–6462 asserts that `job.artifacts.resume_structure` is **absent** from the catalog. The new key is therefore named `job.artifacts.job_resume_structure`, which matches the ticket's PUT leaf `job_resume_structure`. The per-key assert blocks `_jr` / `_cl` are at L6505–6533. The header docstring key list is at L38.
- **Artifact tabs:** `JOBS_RECOMMENDED_ARTIFACT_TABS` L3564–3586 (`artifact_resume`, `artifact_cover`, `artifact_application`) is served as `UI_CONFIG[...]["report_artifact_tabs"]` (L4299).
- **Candidate structure GET:** `src/ui/api/api_candidate.py` L166–227. It builds `resolved = hydrate_resume_structure_from_base_resume(resolve_resume_structure(cd), artifacts.get("base_resume"))`, then `all_sections` + `catalog` inline. The ten `RESUME_STRUCTURE_*` imports at L59–68 are used **only** at L181–220.
- **Candidate structure PUT (validation to mirror):** `api_candidate.py` L475–488. `merged = dict(resolved)`, sections via `prepare_resume_structure_sections_for_save`, `accent_color` copied if present, then `normalize_resume_structure(merged)`.
- **Tracker:** `src/core/tracker.py` `_prepare_job_resume_content(resume_content, candidate_data)` L410–446 filters with `candidate_mod.resolve_resume_structure(cd)` (L417). Its callers are `save_job_artifact` L517 and `save_job_artifact_resume_content` L598. Tests call it with 2 positional args (`tests/component/core/test_tracker.py` L621, L1675, L2538, L2579). `get_job_current` is at L449. `save_job_artifact` is at L480; its per-key prepare chain is L514–532, and the identical-to-current no-op is at L538–541.
- **Builder:** `build_resume_from_job` L220–307 uses `candidate_mod.resolve_resume_structure(cd)` (L240), `_merge_effective_style(cd)` (L256), and `_accent_source_label(cd)` (L302). Both helpers (L141, L1057) resolve the candidate structure internally. Tests call both with one positional arg (`tests/component/core/test_builder.py` L454–463, L597, L691–719). The body emitter `_emit_body_sections_html` L1581–1689 skips unknown formats as "skipped — missing format" (L1600–1602), and empty text is skipped before the format branches (L1626–1628).
- **Jobs API:** `src/ui/api/api_jobs.py` handlers return `404 {"error": "Not found"}` for a missing job. Logging follows L462–471: `logger.exception("%s | api %s failed\n  %s: %s\n  Returning 500; …", cid, route, type(exc).__name__, exc)` + `server_error_from_exception(exc)`, then `logger.info("%s | api %s completed: PUT %s", cid, route, 200)`.
- **Lint baseline** (`ruff check <file> --output-format json | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))'`): config.py 94, candidate.py 132, tracker.py 157, builder.py 72, api_candidate.py 8, api_jobs.py 12.

### Known test drift (Betty — not fixed here)

These existing tests pin today's values and **will fail by design** after this ticket:

- `tests/component/utils/test_config.py` L5101 asserts the exact `RESUME_STRUCTURE_BODY_FORMATS` tuple, which gains `line`.
- `tests/component/utils/test_config.py` L5742 asserts the exact `ARTIFACT_CONFIG` key set, which gains `job.artifacts.job_resume_structure`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `line` format; `RESUME_STRUCTURE_BODY_FORMAT_DETAILS` (label, description, font stack per format); `RESUME_STRUCTURE_HIDDEN_FLOW_LABEL`; `job.artifacts.job_resume_structure` catalog entry + asserts; `preview_thumbnail` on the three recommended-job artifact tabs | utils |
| `src/core/candidate.py` | New public `resume_structure_editor_payload(resolved)` (lifted from the candidate route; catalog gains format details and the Hidden label) | core |
| `src/ui/api/api_candidate.py` | `get_candidate_resume_structure` returns `resume_structure_editor_payload(resolved)`; drop the now-unused config imports | ui |
| `src/core/tracker.py` | New `get_job_effective_resume_structure`; `_prepare_job_resume_content` filters to it; `save_job_artifact` accepts and validates `job.artifacts.job_resume_structure` | core |
| `src/ui/api/api_jobs.py` | New `GET /api/jobs/<id>/resume_structure` and `PUT /api/jobs/<id>/artifacts/job_resume_structure` | ui |
| `src/core/builder.py` | `line` branch in the body emitter; `build_resume_from_job` structure + accent from the job's effective structure; structure-source debug line | core |

**Scope gate:** all six rows are files this ticket's `## Scope` names, and each change is the kind its Technical scope describes: config catalog/label/font/flag entries, one shared payload helper, the route switched to it, the effective read + save + prep filter, two new authenticated routes, and a `line` branch + job-structure use in `build_resume_from_job` and its accent resolution. No frontend file, no `database.py` change (the generic `save_artifact` / `get_current_artifact` already take any leaf `artifact_type`).

## Stage 1: Config — Line format, format details, Hidden label, job structure key, thumbnail flag

**Done when:** `python3 -c "import sys; sys.path[:0]=['.','src']; from src.utils import config as c; print('line' in c.RESUME_STRUCTURE_BODY_FORMATS, c.ARTIFACT_CONFIG['job.artifacts.job_resume_structure']['body_shape'], [t['preview_thumbnail'] for t in c.JOBS_RECOMMENDED_ARTIFACT_TABS])"` prints `True resume_structure [True, True, False]`, and importing config raises no assert.

1. In `src/utils/config.py` `RESUME_STRUCTURE_BODY_FORMATS` (L6943–6950), add `    "line",` as the last element, after `"experience_detail",`. Change no other element.
2. Directly after that tuple's closing `)` (before the `# AST-1474` comment), insert exactly:

   ```python
   # AST-2081: editor metadata per body format — display label, tooltip description (settings + rules),
   # and the BUILD_CONFIG["default_style"]["fonts"] stack key the builder prints that format in.
   # Single SoT for format text/fonts; the frontend reads these from the structure catalog payload.
   RESUME_STRUCTURE_BODY_FORMAT_DETAILS = {
       "free_prose": {
           "label": "Prose",
           "description": (
               "Paragraphs of body text. A blank line starts a new paragraph; with no blank lines, "
               "each line prints as its own paragraph. <i> and <b> emphasis allowed."
           ),
           "font_stack": "body_stack",
       },
       "bullet_list": {
           "label": "Bullet List",
           "description": "One bullet per line. Blank lines are skipped. <i> and <b> emphasis allowed.",
           "font_stack": "body_stack",
       },
       "word_cloud": {
           "label": "Word Cloud",
           "description": (
               "Terms print uppercase in the list font and wrap between terms. "
               "Separate terms with | (prints as •)."
           ),
           "font_stack": "list_stack",
       },
       "dual_column": {
           "label": "Dual Column",
           "description": (
               "Skills grid in the list font. One category per line as \"Category: items\"; "
               "a line without \": \" prints as items only."
           ),
           "font_stack": "list_stack",
       },
       "indented_bold_single": {
           "label": "Indented Bold",
           "description": (
               "One entry per line. Text before the first | prints bold and the rest follows after •; "
               "a line without | prints fully bold."
           ),
           "font_stack": "body_stack",
       },
       "experience_detail": {
           "label": "Experience",
           "description": (
               "Roles edited as job entries (company, title, dates, location, accomplishments). "
               "Experience section only; its format cannot change."
           ),
           "font_stack": "body_stack",
       },
       "line": {
           "label": "Line",
           "description": "A single line of text. Line breaks are collapsed into spaces.",
           "font_stack": "body_stack",
       },
   }
   assert set(RESUME_STRUCTURE_BODY_FORMAT_DETAILS) == set(RESUME_STRUCTURE_BODY_FORMATS)
   assert all(
       d["font_stack"] in BUILD_CONFIG["default_style"]["fonts"]
       for d in RESUME_STRUCTURE_BODY_FORMAT_DETAILS.values()
   )
   ```

   ⚠️ **Decision:** One id-keyed dict per format (label, description, font stack key) rather than three parallel maps. One edit point per format, and the assert keeps it in lockstep with the format tuple. The font is stored as a **stack key**, so `BUILD_CONFIG` stays the only place font strings live. The payload resolves the key to the CSS string (Stage 2). Descriptions state the emitter rules actually implemented in `builder.py` (`_session_cover_letter_paragraphs`, `_emit_bullet_list_html`, `_glue_word_cloud_bullet_separators`, `_emit_skills_grid_html`, `_emit_education_list_html`, and the Stage 5 `line` branch).

3. Directly after `RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS = {…}` (closing `}` at L6962), insert:

   ```python
   # AST-2081: flow-state label for enabled=False (shown alongside the page-break policy labels).
   RESUME_STRUCTURE_HIDDEN_FLOW_LABEL = "Hidden"
   ```

4. In `ARTIFACT_CONFIG`, directly after the `"job.artifacts.cover_letter": {…},` entry (ends L6378), insert:

   ```python
       "job.artifacts.job_resume_structure": {
           "entity_type": "job",
           "candidate_scoped": True,
           # AST-2081: per-job resume structure; same structure dict contract as candidate.artifacts.resume_structure.
           "body_shape": "resume_structure",
           # Tracker owns first-row ingestion (job resume editor PUT); absent row → job inherits the candidate's.
           "ingestion_owner": "tracker",
       },
   ```

5. In the closed key-set assert (L6437–6449), add `    "job.artifacts.job_resume_structure",` directly after `    "job.artifacts.cover_letter",`. Leave the `job.artifacts.resume_structure` absent-assert (L6460) unchanged.
6. Directly after the `_cl` assert block (ends L6533 with the closing `}`), insert:

   ```python

   _jrs = ARTIFACT_CONFIG["job.artifacts.job_resume_structure"]
   assert _jrs["entity_type"] == "job"
   assert _jrs["entity_type"] in ENTITY_TYPES
   assert _jrs["candidate_scoped"] is True
   assert _jrs["body_shape"] == "resume_structure"
   assert _jrs["body_shape"] in BUILD_CONFIG["artifact_shapes"]
   assert _jrs["ingestion_owner"] == "tracker"
   assert set(_jrs.keys()) == {
       "entity_type",
       "candidate_scoped",
       "body_shape",
       "ingestion_owner",
   }
   ```

7. In the module docstring L38, change `job.artifacts.job_resume, job.artifacts.cover_letter,` to `job.artifacts.job_resume, job.artifacts.cover_letter, job.artifacts.job_resume_structure,`, and change the trailing `/ AST-1678)` to `/ AST-1678 / AST-2081)`.
8. In `JOBS_RECOMMENDED_ARTIFACT_TABS` (L3564–3586), add a `"preview_thumbnail"` key as the last key of each row: `True` on `artifact_resume`, `True` on `artifact_cover`, and `False` on `artifact_application`. Directly above the list's `# AST-1100` comment line, add `# AST-2081: preview_thumbnail — tab shows a print-preview thumbnail (instead of an inline editor) once generated.`
9. Run the Done-when command. Then run `python3 -m py_compile src/utils/config.py` and the lint baseline command for `src/utils/config.py` (must be ≤ 94). Commit: `code(AST-2081): config — line format, format details, hidden label, job structure key, thumbnail flag`.

## Stage 2: Shared structure-editor payload (candidate route)

**Done when:** `GET /api/candidates/<id>/resume_structure` returns the same `sections`, `all_sections`, `accent_color`, and every pre-existing `catalog` key with unchanged values as before. `catalog.body_formats` now ends with `"line"`, `catalog.body_format_details.line.label == "Line"`, `catalog.body_format_details.word_cloud.font_family` equals `BUILD_CONFIG["default_style"]["fonts"]["list_stack"]`, and `catalog.hidden_flow_label == "Hidden"`.

1. In `src/core/candidate.py`'s `from src.utils.config import (...)` block (L57–103), add these names in the `RESUME_STRUCTURE_*` run, keeping alphabetical position: `RESUME_STRUCTURE_BODY_FORMAT_DETAILS` (after `RESUME_STRUCTURE_BODY_FORMATS`), `RESUME_STRUCTURE_HIDDEN_FLOW_LABEL` (after `RESUME_STRUCTURE_EXTRA_ID_PATTERN`), `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT` (after `RESUME_STRUCTURE_KNOWN_SECTION_IDS`), and `RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID` + `RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS` (around the existing `RESUME_STRUCTURE_PAGE_BREAK_*` lines).
2. In `src/core/candidate.py`, directly after `enabled_resume_structure_sections` (ends L2960 `return enabled`), insert a new public function. Its body is the candidate route's L178–227 moved verbatim, with two catalog keys added:

   ```python
   def resume_structure_editor_payload(resolved: dict) -> dict:
       """Structure-editor payload for a resolved structure (AST-2081): sections, all_sections, accent_color, catalog.

       Shared by the candidate and job resume_structure GETs. Format labels/descriptions/fonts and flow
       labels come from config only — the frontend never hardcodes them.
       """
       accent = resolved.get("accent_color")
       if not isinstance(accent, str):
           accent = None
       required = set(RESUME_STRUCTURE_REQUIRED_SECTION_IDS)
       contact = set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
       all_sections = []
       sections_map = resolved.get("sections") if isinstance(resolved.get("sections"), dict) else {}
       # ... verbatim: the sorted(...) loop appending {id, title, enabled, order, format,
       #     job_agent_editable, required, format_locked, page_break_policy} (route L184–209) ...
       fonts = BUILD_CONFIG["default_style"]["fonts"]
       catalog = {
           # ... verbatim: the ten existing keys body_formats … page_break_policy_defaults (route L211–220) ...
           # AST-2081: per-format label / tooltip / preview font (CSS font-family string), id-keyed.
           "body_format_details": {
               fmt: {
                   "label": d["label"],
                   "description": d["description"],
                   "font_family": fonts[d["font_stack"]],
               }
               for fmt, d in RESUME_STRUCTURE_BODY_FORMAT_DETAILS.items()
           },
           "hidden_flow_label": RESUME_STRUCTURE_HIDDEN_FLOW_LABEL,
       }
       return {
           "sections": enabled_resume_structure_sections(resolved),
           "all_sections": all_sections,
           "accent_color": accent,
           "catalog": catalog,
       }
   ```

   The two `# ... verbatim` comments above are plan shorthand. Paste the route lines themselves, unchanged, and do not leave those comments in the code.

3. In `src/ui/api/api_candidate.py` `get_candidate_resume_structure` (L166–227), keep L169–177 (`candidate` fetch, 404, `cd`, `artifacts`, `resolved = hydrate_resume_structure_from_base_resume(...)`). Replace everything from `accent = resolved.get("accent_color")` (L178) through the closing `})` of the `return jsonify(...)` (L227) with:

   ```python
       return jsonify(resume_structure_editor_payload(resolved))
   ```

4. In `api_candidate.py`'s `from src.core.candidate import (...)` block, add `    resume_structure_editor_payload,` directly after `    resolve_resume_structure,`. In its `from src.utils.config import (...)` block, delete these ten lines: `RESUME_STRUCTURE_BODY_FORMATS`, `RESUME_STRUCTURE_CONTACT_SECTION_IDS`, `RESUME_STRUCTURE_EXTRA_ID_PATTERN`, `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT`, `RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID`, `RESUME_STRUCTURE_PAGE_BREAK_POLICIES`, `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`, `RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS`, `RESUME_STRUCTURE_REQUIRED_SECTION_IDS`, `RESUME_STRUCTURE_RESERVED_EXTRA_IDS`. Before deleting each one, confirm that `rg -n "\bNAME\b" src/ui/api/api_candidate.py` hits only the import line. If any hits elsewhere, stop and comment (plan drift).
5. Run `python3 -m py_compile src/core/candidate.py src/ui/api/api_candidate.py`. Lint: candidate.py ≤ 132, api_candidate.py ≤ 8. Commit: `code(AST-2081): shared resume_structure_editor_payload with format details + hidden label`.

## Stage 3: Tracker — job effective structure, structure write, content prep

**Done when:** For a job with no `job_resume_structure` row, `get_job_effective_resume_structure(jid)` equals `candidate_mod.resolve_resume_structure(cd)` of its owner, and no artifact row is written. `save_job_artifact(jid, "job.artifacts.job_resume_structure", body)` writes one `job`/`job_resume_structure` row (and a re-save of the same body writes none). After that write, the effective read returns the job row. `save_job_artifact(jid, "job.artifacts.job_resume", {...})` keeps content for a section that exists only in the job structure.

1. In `src/core/tracker.py`, directly after `logger = get_logger(__name__)` (L53), add:

   ```python
   _JOB_RESUME_STRUCTURE_KEY = "job.artifacts.job_resume_structure"
   ```

2. Directly after `_candidate_data_for_job` (ends L407) and before `_prepare_job_resume_content`, insert:

   ```python
   def get_job_effective_resume_structure(
       astral_job_id: Optional[str],
       candidate_data: Optional[dict] = None,
       *,
       hydrate_from_base: bool = False,
   ) -> dict:
       """Job's effective resume structure (AST-2081 / patt.artifact.read-current).

       Current job.artifacts.job_resume_structure row when one exists; else the owning candidate's
       resolved structure. candidate_data: caller's loaded candidate blob for that fallback (None →
       load the job's owner). hydrate_from_base applies to the fallback only: union base_resume
       section keys exactly like the candidate structure GET, so an unedited job's editor payload
       equals the candidate's. Read-only — never writes a row.
       """
       jid = (astral_job_id or "").strip()
       own = get_job_current(jid, _JOB_RESUME_STRUCTURE_KEY) if jid else None
       if isinstance(own, dict) and isinstance(own.get("sections"), dict) and own["sections"]:
           return own
       if isinstance(candidate_data, dict):
           cd = candidate_data
       else:
           cd = _candidate_data_for_job(jid) if jid else {}
       resolved = candidate_mod.resolve_resume_structure(cd)
       if not hydrate_from_base:
           return resolved
       arts = cd.get("artifacts") if isinstance(cd.get("artifacts"), dict) else {}
       return candidate_mod.hydrate_resume_structure_from_base_resume(resolved, arts.get("base_resume"))
   ```

   ⚠️ **Decision:** Effective read = job row, else **unhydrated** `resolve_resume_structure` (exactly what the job builder and content prep use today, so un-edited jobs print and save byte-identically). Only the editor GET passes `hydrate_from_base=True`, which reproduces the candidate GET's base-resume key union so AC16 (`all_sections` equal) holds. The job's own row is **never** hydrated from any resume body. Hydrating it would resurrect sections the operator deleted from the job, and #3's SECTION REMOVED rows depend on that deletion sticking. Alternatives considered: (a) always hydrate the fallback, which changes print output for un-edited jobs whose base resume has keys outside the structure; (b) return a `(structure, source)` tuple and let the route hydrate, which puts structure logic in the API layer.

   ⚠️ **Decision:** A stored row is returned as stored, with no re-normalize and no fallback on a malformed row. Every row passes `normalize_resume_structure` on write (step 4), and adding a silent fallback would be an unrequested heuristic.

3. Change `_prepare_job_resume_content` (L410):
   - Signature → `def _prepare_job_resume_content(resume_content: Dict[str, Any], candidate_data: dict, astral_job_id: Optional[str] = None) -> Dict[str, Any]:`
   - Docstring → `"""Filter to the job's effective structure (AST-2081); snapshot contact sections from payload or base_resume."""`
   - Replace L417 `structure = candidate_mod.resolve_resume_structure(cd)` with `structure = get_job_effective_resume_structure(astral_job_id, cd)`. Keep the hydrate lines L413–416 above it unchanged, so the fallback still sees the operative candidate structure.
   - Change the call at L517 to `_prepare_job_resume_content(blob, _candidate_data_for_job(jid), jid)`. Change the call at L598 to `_prepare_job_resume_content(resume_content, cd, astral_job_id)`.

   ⚠️ **Decision:** `astral_job_id` defaults to `None`, which falls back to today's candidate resolve, so the four existing two-arg test calls keep their behavior.

4. In `save_job_artifact`, insert a new branch directly after the `elif key == "job.artifacts.cover_letter":` block (ends L523) and before `elif shape_name == "resume_content":`:

   ```python
       elif key == _JOB_RESUME_STRUCTURE_KEY:
           # Same validation as the candidate structure PUT: merge over current effective, slug sections, normalize.
           if not isinstance(blob, dict):
               raise ValueError("job_resume_structure body must be a dict")
           merged = dict(get_job_effective_resume_structure(jid))
           if isinstance(blob.get("sections"), dict):
               merged["sections"] = candidate_mod.prepare_resume_structure_sections_for_save(blob["sections"])
           if "accent_color" in blob:
               merged["accent_color"] = blob["accent_color"]
           prepared = candidate_mod.normalize_resume_structure(merged)
   ```

   The rest of `save_job_artifact` stays unchanged: the identical-to-current no-op, `sources = source_artifact_ids` (the job_resume auto-cite branch is key-specific), and `database.save_artifact(..., candidate_id=cid)`.

   ⚠️ **Decision:** Merge over the effective structure, as the candidate PUT merges over `resolved`. A body without `accent_color` therefore keeps the inherited accent, so the first job save never silently drops the candidate's color. A body with `accent_color: null` clears it. Then the job prints with the legacy base_resume accent or the default, the same rule the candidate structure follows.

5. Update the module docstring line 6: `save_job_artifact, get_job_current (AST-1592 catalog write/current-read for job keys).` → `save_job_artifact, get_job_current (AST-1592 catalog write/current-read for job keys), get_job_effective_resume_structure (AST-2081).`
6. Run `python3 -m py_compile src/core/tracker.py`. Lint ≤ 157. Commit: `code(AST-2081): tracker — job effective resume structure, structure write, prep filter`.

## Stage 4: Jobs API — job structure GET and PUT

**Done when:** `GET /api/jobs/<id>/resume_structure` returns 200 with `sections`/`all_sections`/`accent_color`/`catalog`. For an unedited job, its `all_sections` equals the candidate GET's, and no artifact row is written. `PUT /api/jobs/<id>/artifacts/job_resume_structure` with `{"job_resume_structure": <structure>}` returns `{"ok": true}`. After it, the job GET shows the edit while the candidate GET and another job's GET are unchanged. Both routes return 404 for an unknown job id. The PUT returns 400 for a non-dict body or a structure `normalize_resume_structure` rejects (e.g. a required section missing). A successful PUT logs one `… | api <route> completed: PUT 200` INFO line; the GET logs no INFO (idempotent current-state read, `stat.logging.info.api`).

1. In `src/ui/api/api_jobs.py`'s `from src.core.tracker import (...)` block, add `    get_job_effective_resume_structure,` directly after `    get_job_artifacts,`. Directly after the `from src.core.roster import …` line (L12), add `from src.core.candidate import resume_structure_editor_payload`.
2. Directly after `put_job_cover_letter` (ends L383 `return jsonify({"ok": True})`), insert:

   ```python
   @jobs_bp.route("/<astral_job_id>/resume_structure")
   @require_auth
   def get_job_resume_structure(astral_job_id):
       """AST-2081: structure-editor payload for the job's effective resume structure (read-only)."""
       job = get_job(astral_job_id)
       if not job:
           return jsonify({"error": "Not found"}), 404
       cid = job.get("candidate_id") or "-"
       route = f"/api/jobs/{astral_job_id}/resume_structure"
       try:
           payload = resume_structure_editor_payload(
               get_job_effective_resume_structure(astral_job_id, hydrate_from_base=True)
           )
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the job resume editor shows no sections",
               cid,
               route,
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       return jsonify(payload)


   @jobs_bp.route("/<astral_job_id>/artifacts/job_resume_structure", methods=["PUT"])
   @require_auth
   def put_job_resume_structure(astral_job_id):
       """AST-2081: write the job's own resume structure via catalog write (candidate structure untouched)."""
       job = get_job(astral_job_id)
       if not job:
           return jsonify({"error": "Not found"}), 404
       data = request.get_json(silent=True)
       body = data.get("job_resume_structure") if isinstance(data, dict) else None
       if not isinstance(body, dict):
           return jsonify({"error": "job_resume_structure must be a dict"}), 400
       cid = job.get("candidate_id") or "-"
       route = f"/api/jobs/{astral_job_id}/artifacts/job_resume_structure"
       try:
           save_job_artifact(astral_job_id, "job.artifacts.job_resume_structure", body)
       except ValueError as exc:
           # Invalid structure (normalize / slug reject) — routed 400, no log.
           return jsonify({"error": str(exc)}), 400
       except Exception as exc:
           logger.exception(
               "%s | api %s failed\n  %s: %s\n  Returning 500; the job resume structure is unchanged",
               cid,
               route,
               type(exc).__name__,
               exc,
           )
           return server_error_from_exception(exc)
       logger.info("%s | api %s completed: PUT %s", cid, route, 200)
       return jsonify({"ok": True})
   ```

   ⚠️ **Decision:** Only the PUT emits the INFO completion line. `stat.logging.info.api` says "Idempotent GETs that only return current state are not progress — no info", and the candidate twin GET is silent. The parent's "each log one completion line" yields to canon here (Joan validate, discuss item). Both routes still log a caught exception once (`stat.logging.error`).

   ⚠️ **Decision:** The request body key is `job_resume_structure`, mirroring the sibling `PUT …/artifacts/job_resume` (`{"job_resume": …}`). The PUT returns `{"ok": True}` like its siblings; #3 refetches the GET when it needs the stored shape. The existing generic `…/artifacts/<artifact_key>/versions` and `…/current` routes accept the new full key with no change.

3. Run `python3 -m py_compile src/ui/api/api_jobs.py`. Lint ≤ 12. Commit: `code(AST-2081): jobs api — job resume_structure GET + PUT`.

## Stage 5: Builder — Line format and job-scoped structure/accent

**Done when:** A `line` section whose text is `"A\nB"` prints as exactly one `<p class="summary-intro">A B</p>` inside its `<section>`, and an empty `line` section is skipped like the other formats. For a job with its own structure, `build_resume(jid)` HTML follows that structure's section order, titles, and `accent_color`. `build_base_resume(cid)` HTML is unchanged. For a job with no structure row, `build_resume(jid)` HTML is byte-identical to before this ticket.

1. In `src/core/builder.py` `_emit_body_sections_html`, directly after the `elif fmt == "indented_bold_single":` block (ends L1654 `continue`) and before the final `else:`, insert:

   ```python
               elif fmt == "line":
                   # AST-2081: one paragraph; line breaks collapse to single spaces.
                   one_line = " ".join(ln.strip() for ln in str(text).splitlines() if ln.strip())
                   inner_html = f'      <p class="summary-intro">{_emit_inline_emphasis_html(one_line)}</p>'
   ```

   ⚠️ **Decision:** Reuse the `summary-intro` class so a Line section takes Prose spacing and the body font, which matches its catalog font (`body_stack`). No new CSS. `splitlines` + `strip` (not bare `str.split()`) collapses only line breaks, so the NBSP the `__` marker inserts mid-line survives. The empty-text skip already runs before the format branches (L1626–1628), so the per-section debug outcome reports `line` sections through the existing contract.

2. Change `_accent_source_label(candidate_data: dict) -> str:` (L141) to `_accent_source_label(candidate_data: dict, structure: Optional[dict] = None) -> str:`. Replace its first body line `structure = candidate_mod.resolve_resume_structure(candidate_data)` with `structure = structure if isinstance(structure, dict) else candidate_mod.resolve_resume_structure(candidate_data)`.
3. Change `_merge_effective_style(candidate_data: dict) -> dict:` (L1057) to `_merge_effective_style(candidate_data: dict, structure: Optional[dict] = None) -> dict:`. Update its docstring to `"""``default_style`` deep-copied; accent from the given (else candidate) resume_structure, else legacy base_resume."""`. Replace `structure = candidate_mod.resolve_resume_structure(candidate_data)` (L1061) with `structure = structure if isinstance(structure, dict) else candidate_mod.resolve_resume_structure(candidate_data)`.
4. Directly after `_cover_letter_source_label` (ends L138), insert:

   ```python
   def _structure_source_label(astral_job_id: Optional[str]) -> str:
       """Read-only label for which structure drives job resume HTML (AST-2081)."""
       jid = (astral_job_id or "").strip()
       if jid and tracker_mod.get_job_current(jid, "job.artifacts.job_resume_structure") is not None:
           return "get_job_current(job.artifacts.job_resume_structure)"
       return "candidate resume_structure"
   ```

5. In `build_resume_from_job`:
   - Replace L240 `structure = candidate_mod.resolve_resume_structure(cd)` with `structure = tracker_mod.get_job_effective_resume_structure(jid, cd)`.
   - Replace L256 `style = _merge_effective_style(cd)` with `style = _merge_effective_style(cd, structure)`.
   - Replace L302 `_log.debug_detail(f"accent_source={_accent_source_label(cd)!r}")` with `_log.debug_detail(f"accent_source={_accent_source_label(cd, structure)!r}")`, and directly after it add `_log.debug_detail(f"structure_source={_structure_source_label(jid)!r}")`.

   ⚠️ **Decision:** Pass the builder's own `cd` into the effective read. The in-memory candidate blob (with `_astral_candidate_id` for the legacy accent shim) then stays the fallback source. Without it, the tracker would re-fetch the candidate, which changes un-edited job output and breaks `build_resume_from_job`'s "no fetch" contract for callers passing in-memory blobs. `build_base_resume` and the session builders are not touched.

6. Run `python3 -m py_compile src/core/builder.py`. Lint ≤ 72. Commit: `code(AST-2081): builder — line format; job resume HTML from job effective structure`.

## Acceptance mapping (this ticket's AC 13–18)

- **AC13 Line end to end:** Stage 1 (`line` in `body_formats`, no format removed), Stage 5 (prints as one line, never "missing format"). The single-line input is #3's.
- **AC14 config-driven text:** Stage 1 + Stage 2. Labels, descriptions, fonts, and the Hidden/flow labels are all in the catalog payload. The frontend grep is #3/#4's.
- **AC15 isolation:** Stages 3–5. Job writes go to `job`/`job_resume_structure` rows only. The candidate GET and other jobs read their own rows or the candidate's, and job HTML uses the job's structure.
- **AC16 inherit until edited:** Stage 3 fallback + Stage 4 `hydrate_from_base=True`. The GET only reads.
- **AC17 job-only section survives save:** Stage 3 step 3 (prep filters to the job's effective structure).
- **AC18 job accent:** Stage 3 step 4 (accent stored on the job row) + Stage 5 steps 3 and 5 (job HTML accent from the job structure). `build_base_resume` is untouched.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Revisions

Revision 1 — 2026-10-09
Driven by: Joan validate (2026-10-09) discuss item — "`stat.logging.info.api` vs job structure GET … omit GET info (canon + parity with candidate GET) and keep INFO on PUT only".
Changes: Stage 4 — removed the `logger.info(... completed: GET ...)` line from `get_job_resume_structure`; Done-when now requires INFO on the PUT only; added a Decision citing the statute. Exception logging on both routes unchanged.

## Joan validate

[plan-rubric]
**Ticket:** AST-2081
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** `origin/sub/AST-2046/AST-2081-job-structure-line-format` @ `28a73a6fd`

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.write-operative | A | | |
| stat.logging.info.api | C | 2 | Stage 4 INFO on job structure GET; statute exempts idempotent current-state GETs (candidate twin is silent) |
| stat.logging.error | A | | |
| stat.logging.debug | A | | |

### Traceability

AC13→S1,S5 · AC14→S1,S2 (catalog payload; frontend grep is #3/#4) · AC15→S3–S5 · AC16→S3,S4 · AC17→S3 · AC18→S3,S5

### Findings

#### discuss — `stat.logging.info.api` vs job structure GET
- **Severity:** discuss
- **Location:** Stage 4 `get_job_resume_structure` — `logger.info(... completed: GET 200)`
- **Finding:** Plan logs a completion INFO on the job structure GET. `stat.logging.info.api` says idempotent GETs that only return current state are not progress and should not emit info. Today's `get_candidate_resume_structure` has no completion line; only the PUT is clearly “work completed.” Parent AST-2046 Architectural definition still asks for one completion line on **both** new job structure routes.
- **Recommendation:** Before build, pick one line: omit GET info (canon + parity with candidate GET) and keep INFO on PUT only, or escalate a one-line parent/arch amend if Susan wants GET logged anyway.

#### acceptable — No `## Self-assessment` block
- **Severity:** acceptable
- **Location:** Plan doc structure
- **Finding:** Estimate confirm only; no conf/self-assessment section.
- **Recommendation:** Optional for review parity; not blocking (same pattern as other backend-heavy plans).

#### acceptable — AC14 end-to-end proof split across children
- **Severity:** acceptable
- **Location:** Child AC14 vs plan Stages 1–2
- **Finding:** AC14’s `git grep` on `src/ui/frontend` is owned by UI siblings; this ticket correctly limits itself to catalog fields in the API payload.
- **Recommendation:** Betty/Radia UAT on #3/#4 for the grep half; backend stages here satisfy the data half.

### R6 (summary)

Definition fidelity: Plan matches AST-2081 `## Scope` and parent backend slice (six files, no UI). Files Changed rows align with dispatched scope. Stages 1–5 cover job catalog key, effective read (no GET write), merge/normalize PUT, shared editor payload, `line` emitter, and job-scoped builder structure/accent with explicit decisions (hydrate only on editor GET, optional third arg on prep, byte-identical unedited jobs). DRY: lifts candidate route payload into `resume_structure_editor_payload`. No sibling scope creep. Known config test drift is called out for Betty.

context_tokens≈42000

[plan-rubric] PROCEED (Commit: 28a73a6fd) Backend plan canon-clean; discuss GET info.

## Review (build)

**Built:** `origin/sub/AST-2046/AST-2081-job-structure-line-format` @ `f55297be64359eab5c69de53a4589afedc4ae1c7`

Stages 1–5: `1638cccdc` config (line format, `RESUME_STRUCTURE_BODY_FORMAT_DETAILS`, Hidden label, `job.artifacts.job_resume_structure`, `preview_thumbnail` flag) · `544187ded` shared `resume_structure_editor_payload` (candidate GET unchanged) · `49956da29` tracker `get_job_effective_resume_structure`, structure write branch, prep filter on job structure · `b86ebe3b4` jobs API GET + PUT · `f55297be6` builder `line` emitter and job-scoped structure/accent. Scratch checks (temp DB) green for tracker, routes, builder; `tests/component/core/test_builder.py` 192 passed (unchanged). Tests deferred to Betty — known drift: `test_config` format tuple and catalog key set (see Stage 1).

**Deviations:**
- Tracker and builder new annotations use `X | None` instead of `Optional[...]` (both modules have `from __future__ import annotations`); keeps ruff at baseline (UP045).
- `api_jobs.py` ruff 12 → 14: two TRY401 on the `logger.exception(..., type(exc).__name__, exc)` form `stat.logging.error` mandates (existing handlers in the file use the same form). Kept per canon.

## Radia review

[code-rubric]
**Ticket:** AST-2081
**Publish ref:** `ff46d7bd6fb80e80f3161df7b93fd68b0bbe4dee` (`origin/sub/AST-2046/AST-2081-job-structure-line-format`)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`
**Overall:** CLEAN

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.write-operative | A | | |
| stat.logging.info.api | A | | |
| stat.logging.error | A | | |
| stat.logging.debug | A | | |

### Column diff vs plan stage

- `stat.logging.info.api` — Joan **C/2** (plan Stage 4 logged GET completion); code **A** after Revision 1 (GET silent, PUT `logger.info` only — matches statute and candidate twin).
- All other ids: **(aligned)** with Joan’s **A** rows.

### Frame diff

(none)

### Findings

#### fix-now

(none)

#### discuss

(none) — Joan’s GET-info discuss was closed in Revision 1; implementation matches the documented Decision (PUT-only INFO).

#### advisory

- **sibling test carry:** `merge-tests` on the publish ref pulls non–AST-2081 manifest/bible rows and tests into the three-dot diff — expected, not product scope: `tests/component/core/test_roster.py`, `test_consult.py`, `test_gazer.py`, `test_contact.py`; `tests/component/frontend/components/test_BatchAgentDataModal.test.tsx`, `pages/test_AdminThemeExamples.test.tsx`; matching `docs/test-bible/core/{roster,consult,gazer,contact}.md`, `frontend/{components,pages,root}.md`. **Product** `src/**` touches only the six scoped files (config, candidate, tracker, api_candidate, api_jobs, builder).
- **AC14 grep half:** still owned by UI siblings (#3/#4); this diff correctly limits proof to catalog payload fields (Joan acceptable).
- **`api_jobs.py` ruff 12→14 (TRY401):** build note documents intentional match to existing `logger.exception(..., type(exc).__name__, exc)` handlers and `stat.logging.error` live-facts shape — not a canon defect.

### What’s solid

- Catalog: `job.artifacts.job_resume_structure` registered with closed-set and per-key asserts; `line` + `RESUME_STRUCTURE_BODY_FORMAT_DETAILS` + Hidden label + `preview_thumbnail` on artifact tabs.
- Read path: `get_job_effective_resume_structure` → `get_job_current` / candidate fallback; editor GET uses `hydrate_from_base=True` only on that path; no write on GET.
- Write path: structure branch mirrors candidate validation (merge → prepare sections → normalize); shared **identical-to-current** gate in `save_job_artifact` before `save_artifact`.
- API: job structure GET/PUT follow sibling 404/400/500 patterns; PUT completion INFO only; both routes single `logger.exception` on unrouted failures.
- DRY: `resume_structure_editor_payload` shared by candidate and job GETs; builder `line` branch + job-scoped structure/accent wired through effective structure.

context_tokens≈38000

[code-rubric] PROCEED (Commit: ff46d7bd6) Canon-clean; rev1 logging
