# AST-1306 — Author extra sections (title and format)

**Linear:** https://linear.app/astralcareermatch/issue/AST-1306/author-extra-sections-title-and-format  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections  
**Publish ref:** `sub/AST-1299/AST-1306-author-extra-sections-title-and-format`

After AST-1303: operators can add, title, format, enable, reorder, and remove optional sections on Base Resume Content; the required seven stay present and enabled. Format choices come from the config catalog via `GET /api/candidates/<id>/resume_structure` (not a hardcoded React list). Persist title and format on the existing section id. Does **not** own print CSS / HTML emit (**AST-1304**) or hop prompts / legacy label ingest (**AST-1305**).

## Prerequisite (Before Stage 1)

AST-1303 catalog names must already exist on this checkout (`After #1`). Before any edit, confirm `src/utils/config.py` defines all of:

- `RESUME_STRUCTURE_REQUIRED_SECTION_IDS`
- `RESUME_STRUCTURE_CONTACT_SECTION_IDS`
- `RESUME_STRUCTURE_KNOWN_SECTION_IDS`
- `RESUME_STRUCTURE_BODY_FORMATS`
- `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`
- `RESUME_STRUCTURE_EXTRA_ID_PATTERN`
- `RESUME_STRUCTURE_RESERVED_EXTRA_IDS`

and `src/core/candidate.py` has `normalize_resume_structure` that accepts extra slugs and rejects missing/disabled required ids.

If any of those names are missing, **stop**. Do not re-implement the catalog. Comment on **AST-1306** (not the parent) that this checkout does not yet contain AST-1303 and needs `origin/ftr/AST-1299-support-alternative-resume-sections` merged (sync-child looks for short ref `ftr/AST-1299`, which is not on origin).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT = "bullet_list"` next to the AST-1303 family. | utils |
| `src/core/candidate.py` | Add `slug_resume_section_id` and `prepare_resume_structure_sections_for_save`. Do **not** change `normalize_resume_structure` or `enabled_resume_structure_sections`. | core |
| `src/ui/api/api_candidate.py` | GET returns `all_sections` + `catalog` (keep `sections` as enabled `{id, label}`). PUT replaces `sections` when that key is present (no longer additive overlay). | ui |
| `src/ui/frontend/src/components/ResumeStructureEditor.tsx` | New editor: title / format / enable / reorder / remove optional / add extra. Format `<select>` options from `catalog.body_formats` only. | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Render the editor above the accent bar; refetch tabs after structure save. | ui |
| `src/ui/frontend/src/App.css` | Styles for the structure editor, next to `.base-resume-accent-bar`. | ui |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `src/core/builder.py` HTML emit by format; printed heading; leftover prose Experience; Style D debug | AST-1304 |
| Craft/draft hop schemas; legacy label/content → extra slug ingest | AST-1305 (may **import** `slug_resume_section_id`; this ticket does not implement ingest) |
| `enabled_resume_structure_sections` `{id, label}` contract; `ArtifactEditor.tsx` internals; `JobAnalysisReportModal.tsx` | unchanged — they keep reading GET `sections` |
| `NAV_CONFIG` / `routes.tsx` / `/api/system/ui_config` format catalog | do not add a page or duplicate the catalog on `ui_config` |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 1–2, 5–6, 8–11 are siblings (emit / hops / debug). Do not implement them here.

| Child AC | Stage |
|----------|--------|
| 3 — required title change keeps id (stored title; printed heading is AST-1304) | 1 persist + 2 editor |
| 4 — optional format change keeps id (stored format; HTML treatment is AST-1304) | 1 persist + 2 editor |
| 5 — required sections cannot be removed | 1 PUT replace + normalize; 2 no remove control |

## Stage 1: Catalog default, slug/rekey, GET catalog, PUT replace

**Done when:** `GET /api/candidates/<id>/resume_structure` (authenticated) returns `sections` (enabled `{id, label}` only, same as today), `all_sections` (every stored section including disabled, sorted by `order` then `id`), `accent_color`, and `catalog` whose `body_formats` is exactly `list(RESUME_STRUCTURE_BODY_FORMATS)` and whose `new_extra_default_format` is `"bullet_list"`. `PUT /api/candidates/<id>/data` with `artifacts.resume_structure.sections` equal to a full seven-required map plus `{highlights: {title: "Highlights", enabled: true, order: 10, format: "bullet_list", job_agent_editable: true}}` persists `highlights` and **drops** any historical optional that was omitted (e.g. `prior_experience` gone after omit). The same PUT with `professional_summary.title` `"Summary"` keeps id `professional_summary`. Omitting `experience` from the map returns 400. Accent-only PUT (`resume_structure: {accent_color: "#…"}` with **no** `sections` key) still updates accent and leaves sections unchanged. No TSX in this stage.

1. In `src/utils/config.py`, immediately after `RESUME_STRUCTURE_RESERVED_EXTRA_IDS = (...)`, add exactly:

   ```python
   RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT = "bullet_list"
   ```

   Do not add other config keys. Do not change `RESUME_STRUCTURE_DEFAULT` or the AST-1303 tuples/maps.

2. In `src/core/candidate.py`, extend the existing `from src.utils.config import` list (do not add a second config import) with `RESUME_STRUCTURE_RESERVED_EXTRA_IDS` only if it is not already imported. Do **not** import `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT` here (GET catalog reads it in the API).

3. Immediately after `normalize_resume_structure` (before `enabled_resume_structure_sections`), add these two public functions. If `slug_resume_section_id` already exists in this file when you reach this step (sibling AST-1305), **do not** add a second copy — call the existing function from `prepare_resume_structure_sections_for_save`. If it exists but the body is not the algorithm below, **stop** and comment on AST-1306.

   ```python
   def slug_resume_section_id(title: str) -> str:
       raw = (title or "").strip().lower()
       slug = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
       if not slug or _RESUME_SECTION_EXTRA_ID_RE.fullmatch(slug) is None:
           raise ValueError("invalid extra section title")
       if slug in RESUME_STRUCTURE_RESERVED_EXTRA_IDS:
           raise ValueError(f"invalid extra section id: {slug}")
       return slug


   def prepare_resume_structure_sections_for_save(sections_in) -> dict:
       if not isinstance(sections_in, dict) or not sections_in:
           raise ValueError("resume_structure.sections must be a non-empty dict")
       out = {}
       for sid, spec in sections_in.items():
           if not isinstance(spec, dict):
               raise ValueError(f"section {sid} must be a dict")
           key = str(sid)
           if key in RESUME_STRUCTURE_KNOWN_SECTION_IDS or _RESUME_SECTION_EXTRA_ID_RE.fullmatch(key):
               new_sid = key
           else:
               new_sid = slug_resume_section_id(str(spec.get("title") or ""))
           if new_sid in out:
               raise ValueError(f"duplicate section id after slug: {new_sid}")
           row = dict(spec)
           row["id"] = new_sid
           out[new_sid] = row
       return out
   ```

   Do **not** edit `normalize_resume_structure`, `enabled_resume_structure_sections`, `filter_base_resume_to_structure`, hop helpers, or `builder.py`.

4. In `src/ui/api/api_candidate.py`, extend the `from src.core.candidate import` list with `prepare_resume_structure_sections_for_save`. Extend the `from src.utils.config import` list with:

   - `RESUME_STRUCTURE_BODY_FORMATS`
   - `RESUME_STRUCTURE_CONTACT_SECTION_IDS`
   - `RESUME_STRUCTURE_EXTRA_ID_PATTERN`
   - `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT`
   - `RESUME_STRUCTURE_REQUIRED_SECTION_IDS`
   - `RESUME_STRUCTURE_RESERVED_EXTRA_IDS`

5. Replace the body of `get_candidate_resume_structure` (keep the 404 path) so it returns this JSON shape. Build `all_sections` from `resolved["sections"]` sorted by `(order, id)`. Do **not** change `enabled_resume_structure_sections`.

   ```python
   required = set(RESUME_STRUCTURE_REQUIRED_SECTION_IDS)
   contact = set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
   all_sections = []
   sections_map = resolved.get("sections") if isinstance(resolved.get("sections"), dict) else {}
   for sid, spec in sorted(
       sections_map.items(),
       key=lambda kv: (
           kv[1].get("order", 0) if isinstance(kv[1], dict) and isinstance(kv[1].get("order"), int) else 0,
           sid,
       ),
   ):
       if not isinstance(spec, dict):
           continue
       all_sections.append({
           "id": sid,
           "title": spec.get("title") or "",
           "enabled": bool(spec.get("enabled")),
           "order": spec.get("order") if isinstance(spec.get("order"), int) else 0,
           "format": spec.get("format") if isinstance(spec.get("format"), str) else None,
           "job_agent_editable": bool(spec.get("job_agent_editable")),
           "required": sid in required,
           "format_locked": sid == "experience" or sid in contact,
       })
   catalog = {
       "body_formats": list(RESUME_STRUCTURE_BODY_FORMATS),
       "required_ids": list(RESUME_STRUCTURE_REQUIRED_SECTION_IDS),
       "contact_ids": list(RESUME_STRUCTURE_CONTACT_SECTION_IDS),
       "extra_id_pattern": RESUME_STRUCTURE_EXTRA_ID_PATTERN,
       "reserved_extra_ids": list(RESUME_STRUCTURE_RESERVED_EXTRA_IDS),
       "new_extra_default_format": RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT,
   }
   return jsonify({
       "sections": enabled_resume_structure_sections(resolved),
       "all_sections": all_sections,
       "accent_color": accent,
       "catalog": catalog,
   })
   ```

   Keep today's `accent` coercion (`None` if not a `str`).

6. In `update_candidate_data`, change **only** the `merged["sections"]` assignment. Today's overlay is:

   ```python
   merged["sections"] = {**resolved.get("sections", {}), **rs_in["sections"]}
   ```

   Replace that line with:

   ```python
   merged["sections"] = prepare_resume_structure_sections_for_save(rs_in["sections"])
   ```

   Keep the `isinstance(rs_in.get("sections"), dict)` guard. If `sections` is absent, do not touch `merged["sections"]` (accent-only PUT stays an overlay on `resolved`). Keep the `accent_color` overlay as today.

7. Still in that `except ValueError` block: if `"accent"` is in `msg.lower()`, keep `{"error": "invalid accent_color"}`. **Else** return `jsonify({"error": msg}), 400` (the `ValueError` text), not the generic `"invalid resume_structure"`. Operators need the slug / required / format messages in the toast.

⚠️ **Decision:** Catalog is served on this GET, not on `/api/system/ui_config`. One fetch already loads structure; duplicating the list on `ui_config` would be a second source.

⚠️ **Decision:** `sections` stays enabled `{id, label}` so `ArtifactEditor` and `JobAnalysisReportModal` do not change. Authoring uses `all_sections` + `catalog`.

⚠️ **Decision:** When `sections` is present, PUT **replaces** the map (then `normalize_resume_structure`). Additive overlay cannot drop optionals. Accent-only PUT has no `sections` key and must not wipe sections. Craft hops do not persist through this overlay (they go through hop normalize) — replacing here does not change hop writes.

⚠️ **Decision:** Keys that are not known and not a valid extra slug (e.g. `_pending_0`) are slugged from `title` in core. React must not implement a slug algorithm. AST-1305 may import `slug_resume_section_id` for legacy ingest; this ticket does not call ingest.

⚠️ **Decision:** Stay on existing `@require_auth` candidate routes. Do not add an `/api/admin` blueprint or a new path. `pattern.ui.admin-endpoint` here means: resolve catalog + save rules in the API from config; React only renders.

⚠️ **Decision:** `format_locked` is `experience` or a contact id. Required body ids (`professional_summary`, `core_competencies`) may change format (AST-1303). Required ids still cannot be omitted or `enabled=False`.

## Stage 2: Structure editor on Base Resume Content

**Done when:** On `/artifacts/base_resume_content` with a selected candidate, a structure panel above the accent bar lists every section from `all_sections`. Changing `professional_summary` title to `Summary` and saving leaves the id `professional_summary` and updates the ArtifactEditor tab label to `Summary`. Adding a row titled `Highlights` with format `bullet_list` and saving creates id `highlights` (from the API slug, not a React slug). The format `<select>` options are exactly `catalog.body_formats` — no format string appears as a TSX literal except as a value read from `catalog`. Required rows have no Remove control and their enabled checkbox is disabled. Omitting a required id is impossible from the UI; the API still 400s if a crafted PUT drops one. No `NAV_CONFIG` / route change. No builder or hop files.

1. Create `src/ui/frontend/src/components/ResumeStructureEditor.tsx` (flat under `components/`, no ticket id in the filename). Export a default function with this props type (inline in the file, no new types module):

   ```ts
   type Catalog = {
     body_formats: string[]
     required_ids: string[]
     contact_ids: string[]
     extra_id_pattern: string
     reserved_extra_ids: string[]
     new_extra_default_format: string
   }

   type SectionRow = {
     id: string
     title: string
     enabled: boolean
     order: number
     format: string | null
     job_agent_editable: boolean
     required: boolean
     format_locked: boolean
   }

   type Props = {
     sections: SectionRow[]
     catalog: Catalog
     disabled: boolean
     onSave: (sections: SectionRow[]) => void
     saving: boolean
     error: string | null
   }
   ```

2. Local state: copy `props.sections` into `rows` whenever `props.sections` changes (`useEffect` keyed on `props.sections`). Also hold `addTitle` (string, default `""`) and `addFormat` (string, default `props.catalog.new_extra_default_format` or first `body_formats` entry if that string is empty).

3. Render a `<div className="base-resume-structure-editor">` with heading text `Resume sections` (`<span className="base-resume-structure-editor-title">`). For each row, in current array order, render a `<div className="base-resume-structure-row">` containing, in this order:

   - Read-only id: empty string when `id` starts with `_pending_`; otherwise the id text in `<span className="base-resume-structure-row-id">`.
   - Title `<input className="dep-input" type="text">` bound to `row.title`.
   - Format `<select className="dep-input">`:
     - Options = `catalog.body_formats.map(f => <option key={f} value={f}>{f}</option>)` — **do not** write a format-name array in this file.
     - If `row.format_locked`: `disabled`, value `row.format ?? ""` (contact shows empty; experience shows `experience_detail` from the row).
     - Else: value is `row.format` if it is in `catalog.body_formats`, otherwise `catalog.new_extra_default_format`.
   - Enabled `<input type="checkbox">`: `disabled={row.required}`; required rows stay checked.
   - Job-agent-editable `<input type="checkbox">` labeled `Job agent editable`.
   - Up / Down `<button type="button">`: swap this row with the previous / next row, then rewrite every row’s `order` to its index `0 .. n-1`. Disable Up on index 0 and Down on the last index.
   - Remove `<button type="button">`: only render when `!row.required`. Splice the row out. Do not render Remove on required rows.

4. Add-extra row (`<div className="base-resume-structure-add">`): title text input, format `<select>` from `catalog.body_formats` (value `addFormat`), button `Add section`. On click, if `addTitle.trim()` is empty, do nothing. Else append a row:

   ```ts
   {
     id: `_pending_${rows.length}`,
     title: addTitle.trim(),
     enabled: true,
     order: rows.length,
     format: addFormat,
     job_agent_editable: true,
     required: false,
     format_locked: false,
   }
   ```

   Then clear `addTitle`. Do **not** slug in React. Do **not** PUT on Add — wait for Save.

5. Save `<button type="button" className="base-resume-structure-save" disabled={disabled || saving}>` labeled `Save sections`. On click, call `onSave(rows)` (current local rows, including `_pending_*` ids). Show `error` under the button when `error` is non-null.

6. In `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`:

   a. Import `ResumeStructureEditor`.
   b. Add state: `allSections` (`SectionRow[]`), `catalog` (`Catalog | null`), `structureSaving` (boolean), `structureError` (`string | null`). Reuse the existing toast for success/failure text.
   c. In the existing `GET /api/candidates/${selectedId}/resume_structure` effect, keep setting `structureSections` from `data.sections` and `accent` from `data.accent_color`. Also set `allSections` from `Array.isArray(data.all_sections) ? data.all_sections : []` and `catalog` from `data.catalog` when it is a non-null object with `Array.isArray(data.catalog.body_formats)`. If `catalog` is missing or `body_formats` is not an array, set `catalog` to `null` (do not invent a format list).
   d. When `!selectedId`, also clear `allSections` and `catalog`.
   e. Add `saveStructure(rows)`:
      - Build a `sections` object keyed by `row.id`. Each value is `{ id: row.id, title: row.title, enabled: row.enabled, order: index, job_agent_editable: row.job_agent_editable }` plus `format: row.format` only when `row.format` is a non-empty string (contact rows omit `format`).
      - `PUT /api/candidates/${selectedId}/data` with `{ artifacts: { resume_structure: { sections } } }` — **do not** send `accent_color` on this PUT.
      - On success: toast `Resume sections saved`; re-run the same GET as the effect and apply the same setters (`structureSections`, `allSections`, `catalog`, `accent`).
      - On failure: set `structureError` to the API `error` string (fallback `Save failed`) and toast that text as `variant: "error"`.
   f. Above the accent bar, if `catalog !== null` and `selectedId`, render:

      ```tsx
      <ResumeStructureEditor
        sections={allSections}
        catalog={catalog}
        disabled={!selectedId}
        onSave={saveStructure}
        saving={structureSaving}
        error={structureError}
      />
      ```

      If `catalog` is null, render nothing for the editor (tabs + accent still work).

7. In `src/ui/frontend/src/App.css`, immediately after `.base-resume-accent-swatch:focus-visible { … }`, add:

   ```css
   .base-resume-structure-editor {
     padding: 10px 20px;
     border-bottom: 1px solid var(--border);
     background: var(--bg-elevated);
   }

   .base-resume-structure-editor-title {
     display: block;
     font-size: 12px;
     font-weight: 600;
     color: var(--text-muted);
     text-transform: uppercase;
     letter-spacing: 0.06em;
     margin-bottom: 8px;
   }

   .base-resume-structure-row,
   .base-resume-structure-add {
     display: flex;
     flex-wrap: wrap;
     align-items: center;
     gap: 8px;
     margin-bottom: 8px;
   }

   .base-resume-structure-row-id {
     font-size: 12px;
     color: var(--text-muted);
     min-width: 8em;
   }

   .base-resume-structure-save {
     margin-top: 4px;
   }
   ```

   Reuse `.dep-input` for inputs/selects. Do not add a new color token.

8. Do **not** edit `ArtifactEditor.tsx`, `JobAnalysisReportModal.tsx`, `NAV_CONFIG`, `routes.tsx`, `api_system.py`, `builder.py`, hop modules, or `enabled_resume_structure_sections`.

⚠️ **Decision:** Editor lives on the existing Base Resume Content page, not a new nav item. Operators already open that page to edit section bodies; structure belongs next to those tabs.

⚠️ **Decision:** Add is local until Save. One PUT sends the full map, including `_pending_*` keys that core slugs. Two pending rows that slug to the same id 400 via `duplicate section id after slug`.

⚠️ **Decision:** Optional sections can be removed (omit from the replace map). Required cannot. Disabled optionals stay in the map (`enabled: false`) so they can be re-enabled. Do not delete `base_resume` content keys in this ticket; the next content save still filters through `filter_base_resume_to_structure`.

⚠️ **Decision:** AC3/AC4 “printed heading” / “HTML treatment” are persist-here, emit-in-AST-1304. This ticket is done when the stored `title` / `format` change and the id does not.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.** No fix-on-the-fly.
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.

## Rules check

- **§1.3 DRY:** slug lives once in core; React does not copy the algorithm. Format list lives once in config and is echoed by GET `catalog`.
- **§2.1 config:** only `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT`; closed formats stay the AST-1303 tuple.
- **§2.4 batch / §2.6 state:** not touched.
- **§3.3 imports:** ui → core + utils; core → utils; no data/external from ui. New TSX is a default export under `components/`.
- **§3.5 naming:** `ResumeStructureEditor`, `slug_resume_section_id`, `prepare_resume_structure_sections_for_save`, `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT` — no `AST_1306` identifiers.

## Self-Assessment

**Scope:** Single-Component — one config key, two core helpers, the existing candidate GET/PUT, one new React component, the Base Resume Content page, and nearby CSS.

**Conf:** high — AST-1303 already owns normalize + the closed format list; this ticket only exposes that catalog on GET, switches PUT from overlay to replace when `sections` is sent, and adds a thin editor that renders the API payload.

**Risk:** Medium — a buggy replace PUT that runs on a partial `sections` map would drop optional (or, if normalize were skipped, required) rows; accent-only PUT must keep omitting `sections`, and `ArtifactEditor` must keep reading the unchanged `sections` key.

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1306
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1299/AST-1306-author-extra-sections-title-and-format` @ `2ea93a93bed6980c0d6b7cb5fe1ff5c248db783a`

## Traceability
Child AC1→S1–2; AC2→S1–2; AC3→S1–2 (plan doc labels these parent AC3/4/7 — see discuss)

## Findings

### discuss — Traceability table uses parent AC numbers, not child checkbox ids
**Location:** Traceability (this child's AC only)
**Finding:** Rows are labeled AC 3 / 4 / 5 (parent AC3 title, parent AC4 format, parent AC7 required). Child ticket has three ACs numbered 1–3 with the same content.
**Recommendation:** Non-blocking for build. When posting Linear, use child AC1→S1–2; AC2→S1–2; AC3→S1–2. Engineer may add a one-line note in the plan Revisions section for clarity.

### discuss — `pattern.ui.admin-endpoint` vs candidate routes
**Location:** Stage 1 decisions; child In scope
**Finding:** Pattern canonical_refs cite `api_admin.py`; plan correctly keeps `@require_auth` on existing `GET/PUT /api/candidates/...` and documents why (candidate-scoped artifacts, no duplicate catalog on `ui_config`). Matches parent Architectural definition intent (config resolved in API, React renders).
**Recommendation:** Acceptable — do not add `/api/admin` routes for this child.

— Joan
context_tokens≈95000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1299/AST-1306-author-extra-sections-title-and-format`
**Tip:** `cc00324c999561e4213fea9da1b7fc4e10958c4c`

| Stage | Commit | Summary |
|-------|--------|---------|
| ftr | `04dcb32d` | merge `origin/ftr/AST-1299-support-alternative-resume-sections` (AST-1303 catalog) |
| 1 | `bf147fb6` | catalog default, slug/rekey, GET `all_sections`+`catalog`, PUT replace |
| 2 | `cc00324c` | `ResumeStructureEditor` on Base Resume Content |


## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1306
**Publish ref:** `origin/sub/AST-1299/AST-1306-author-extra-sections-title-and-format` @ `1e405f2c43bee539306e983ee9a68d6c877afd8d`
**Overall:** FIX-NOW

## Statutes checked

Ticket-scoped product delta: `bf147fb6` + `cc00324c` + `1e405f2c` (`src/utils/config.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`, `ResumeStructureEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `App.css` modify/add). Formal three-dot `origin/dev...origin/sub` is epic-wide; predicates scored against ticket delta unless noted.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths in ticket delta |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent/dispatcher paths |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade/agent paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | conforms | one new config key; GET catalog reads `RESUME_STRUCTURE_*` from config |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no score-floor paths |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no env/secret wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch/seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run-next paths |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | engineer delta is `src/` + frontend (docs on Betty merge) |
| astral.git.betty-no-src-or-features | scoped | not-applicable | engineer role statute |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits touch planned `src/` + frontend only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | core helpers only; no external imports |
| astral.layers.import-direction | scoped | conforms | ui/api → core+utils; core → utils; no data/external from ui |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts paths |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | format list from GET `catalog.body_formats`; no TSX format literals |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | existing `@require_auth` candidate routes unchanged |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot paths |
| astral.seed.define-approved | scoped | not-applicable | no define paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migrations |
| astral.standards.debug-contract-gated | scoped | conforms | no new debug paths |
| astral.standards.dry-and-focused-functions | scoped | conforms | slug once in core; catalog once in config/API |
| astral.standards.in-scope-only | scoped | violates | `filter_content_to_resume_structure` changed — not in Files Changed / plan steps |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names (`slug_resume_section_id`, `ResumeStructureEditor`) |
| astral.standards.no-cross-contamination | scoped | violates | content-filter behavior bundled into structure-editor ticket |
| astral.standards.no-hardcoded-sets | scoped | conforms | formats/ids from config via GET catalog |
| astral.standards.public-then-helpers | scoped | conforms | two new public core helpers at module level |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | config delta does not import data |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job states |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run chain |
| astral.ui.frontend-file-placement | scoped | conforms | `ResumeStructureEditor.tsx` under `components/` |
| astral.ui.naming-conventions | scoped | conforms | PascalCase component, snake_case Python |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `1e405f2c` after `merge-tests` @ `b67ac6c6` |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1306): …` engineer commits |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1299/…` publish |
| orch.git.ftr-sub-topology | universal | conforms | child under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | ftr merge commit `04dcb32d` documented in stub |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no destructive git in delta |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1299` |
| orch.git.three-permanent-branches | universal | conforms | standard sub topology |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | follows approved plan except noted hunk |
| orch.pipeline.plan-is-bible | universal | violates | plan forbids expanding `candidate.py` beyond slug/prepare; filter_content edited |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to code shape |
| orch.pipeline.status-gates-skill-entry | universal | conforms | spawned at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | tests via Betty merge + `c4b7adbb` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | allowed paths |

**Count:** 65 active statutes scored.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan cites `pattern.ui.admin-endpoint` intent in decisions only; Joan accepted candidate-route placement |

## Plan adherence

**In scope (conforms):** `RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT` added; `slug_resume_section_id` + `prepare_resume_structure_sections_for_save` match Stage 1 algorithm; GET returns `sections` + `all_sections` + `catalog` + `accent_color`; PUT replaces `sections` when present (accent-only overlay preserved); `ValueError` text forwarded on 400; `ResumeStructureEditor` + Base Resume Content wiring + CSS match Stage 2; `normalize_resume_structure` / `enabled_resume_structure_sections` / `ArtifactEditor` untouched; no hardcoded format strings in TSX.

**Joan:** `[plan-rubric] revision=1` **APPROVED** — no Excluded-statute straggler list; prior discuss items (traceability labels, admin-endpoint pattern) non-blocking.

**Cross-ticket:** Relation `after AST-1303` satisfied (catalog names present). `filter_content_to_resume_structure` hunk is **AST-1305** content-ingest / legacy-array territory (AST-1303 explicitly left that helper untouched).

**Tip note:** `1e405f2c` fixes GET sort tie-break (`kv[0]` vs erroneous `sid` closure) — correct on tip; commit message is `test(AST-1306)` but touches product `api_candidate.py` (process advisory only).

## Findings

### fix-now — Out-of-plan `filter_content_to_resume_structure` change
**Location:** `src/core/candidate.py` — `filter_content_to_resume_structure` (~lines 2540–2552), introduced in `bf147fb6`
**Finding:** Stage 1 step 3 limits `candidate.py` edits to `slug_resume_section_id` and `prepare_resume_structure_sections_for_save` and explicitly leaves `filter_base_resume_to_structure` alone. Files Changed does not list content filtering. The diff widens job-array preservation to any key, adds string `experience` fallback, and coerces non-dict lists via `_coerce_resume_section_string` — content-shape behavior owned by **AST-1305** (legacy label/content arrays), not structure authoring.
**Recommendation:** Revert the `filter_content_to_resume_structure` hunk on this sub-branch; land equivalent behavior on the sibling ticket that owns content ingest/filtering. Structure editor + PUT replace do not require this change per the approved plan.

### advisory — Exported editor types
**Location:** `src/ui/frontend/src/components/ResumeStructureEditor.tsx`
**Finding:** Plan specified inline types; implementation `export type Catalog` / `SectionRow` for page import. Harmless DRY improvement.
**Recommendation:** No action required; optional one-line plan revision note.

## What's solid

- Config-driven catalog on GET; React renders `catalog.body_formats` only (no format literals in TSX).
- Slug algorithm lives once in core; `_pending_*` keys rekey correctly.
- PUT replace semantics + accent-only overlay match the binding decisions.
- Required rows: no Remove, enabled checkbox disabled; `format_locked` on contact + experience.
- Betty manifest covers slug/prepare, GET catalog, PUT replace/drop-optional, editor component, and page integration.

## Notes

- Publish tip `1e405f2c` includes `merge-tests` @ `b67ac6c6` (tests `c4b7adbb` + bundled sibling frontend test commits from origin/tests).
- Engineer product SHA for stages 1–2: `cc00324c`; sort-key fix on tip via `1e405f2c`.

## Frame diff

Self-Assessment **Single-Component** lists config key, two core helpers, GET/PUT, editor, page, CSS — **mismatch:** `filter_content_to_resume_structure` behavior change is an undeclared fifth `candidate.py` concern; revert restores frame alignment.

context_tokens≈110000
— Radia

## Resolution

**2026-08-11** — Radia **FIX-NOW**. Reverted the out-of-plan `filter_content_to_resume_structure` hunk in `src/core/candidate.py` to the AST-1303 loop (job-array only on `experience`; string values otherwise). That content-shape widening belongs on AST-1305. Advisory exported editor types left as-is.

## Bug: AST-1323 — Structure editor collapsible header row with body between

### As-is
On Base Resume Content, structure fields (title, format select, enabled, "Job agent editable", up/down, Remove) live in a flat `ResumeStructureEditor` panel above the accent bar. Section body text is edited separately in `ArtifactEditor` collapsible panels lower on the page, so structure controls and body text are not interleaved.

### To-be
Per section, one `CollapsiblePanel` header row holds: section title (label), format type select, enabled, **Job edit** (short label, same `job_agent_editable` field), and up/down. That section's body text appears in the panel body between headers (not in a separate stack at the bottom of the page). Add-section / required-cannot-remove / catalog-driven formats still hold from AST-1306.

### Repro
1. Open Artifacts → Base Resume Content with a candidate that has a resolved resume structure (default ten or seven + extras).
2. Observe the flat structure control rows at the top and the section text editors only in the `ArtifactEditor` stack below the accent bar.
3. Confirm structure controls are not on the same collapsible header as the section body.

### Root cause
AST-1306 Stage 2 shipped structure authoring as a standalone flat list (`ResumeStructureEditor`) stacked above an unchanged `ArtifactEditor`. The page never placed structure controls on `CollapsiblePanel` headers that already wrap each section body.

### Proposed change
UI-only. Do not change GET/PUT `/resume_structure`, slug/prepare, normalize, or config catalog.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, add optional authoring props used only by Base Resume Content (do **not** pass them from `JobAnalysisReportModal`):
   - `structureCatalog: Catalog | null`
   - `structureRows: SectionRow[]`
   - `onStructureRowsChange: (rows: SectionRow[]) => void`
   - `onStructureSave: (rows: SectionRow[]) => void`
   - `structureSaving: boolean`
   - `structureError: string | null`
   Import `Catalog` / `SectionRow` from `./ResumeStructureEditor` (or move those types into a tiny shared type export in that file and keep importing them).

2. When `useCandidateResumeStructure && structureCatalog != null`:
   - Keep the existing collapsible stack + `LabeledTextArea` body (section text between headers).
   - Replace the structureMode header `label`/`actions` so each `CollapsiblePanel` header is a **single row** containing, in order: title `<input className="dep-input">`, format `<select>` options from `structureCatalog.body_formats` only (same rules as today's editor: locked for contact/`experience`), Enabled checkbox (`disabled` when `row.required`), **Job edit** checkbox (label text exactly `Job edit`, still bound to `job_agent_editable`), Up / Down buttons (reindex `order` via `onStructureRowsChange`), Remove only when `!row.required`.
   - Map each rail tab to its `structureRows` entry by section id (`tab.id` / shape key). If a tab has no matching row, render the body as today without authoring controls.
   - Title edits update `structureRows[].title` (id unchanged). Format / enabled / job-edit / reorder / remove update `structureRows` the same way `ResumeStructureEditor` does today.
   - Below the stack: keep Generate/Save chrome; add the Add-section row (title + format from catalog + `Add section` creating `_pending_*` id) and a `Save sections` button that calls `onStructureSave(structureRows)`. Show `structureError` when non-null.
   - Do **not** hardcode a format-name array in TSX.

3. In `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`:
   - Remove the standalone `<ResumeStructureEditor … />` above the accent bar.
   - Pass `structureCatalog={catalog}`, `structureRows={allSections}`, `onStructureRowsChange={setAllSections}`, and the existing `saveStructure` / `structureSaving` / `structureError` into `ArtifactEditor`.
   - Keep accent bar + toast. Keep `structureSections` derived from GET `sections` for tab labels until structure save refetches (after save, `applyStructurePayload` already refreshes both).

4. In `src/ui/frontend/src/components/ResumeStructureEditor.tsx`: keep the file as the type export source (`Catalog`, `SectionRow`). Remove the default-exported flat editor UI if nothing imports it after step 3, ** leave a thin re-export module with types only — do not leave a second visible structure UI on the page.

5. In `src/ui/frontend/src/App.css`: add/adjust rules so structure header controls sit on one `collapsible-panel-header` row (flex, gap, wrap allowed). Reuse `.dep-input`. Drop unused `.base-resume-structure-row` rules only if nothing else references them after the move.

⚠️ **Decision:** Authoring lives on `ArtifactEditor` headers when catalog props are passed — not a second collapsible stack in `ResumeStructureEditor`. `JobAnalysisReportModal` keeps read-only structure tabs (no catalog props).

⚠️ **Decision:** Content save (base_resume) stays ArtifactEditor Save/autosave; structure persist stays the existing PUT replace via `Save sections` / `saveStructure`. Do not fold structure into the content Save body in this bug.

### Blast radius
- `ArtifactEditor` structureMode is also used by `JobAnalysisReportModal` — must remain unchanged unless catalog/authoring props are passed.
- Betty Vitest: `tests/component/frontend/components/test_ResumeStructureEditor.test.tsx`, `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` assume a standalone editor; expect **fix-board** / **qa-fix** to revise those tests.
- API/core/config contracts from AST-1306 are untouched.

### What must still hold
- Format `<option>`s come only from GET `catalog.body_formats` (AST-1306 AC / no-hardcoded-sets).
- Required sections: no Remove; enabled checkbox disabled; cannot omit required ids on save (AST-1306 AC5 / parent AC7).
- Title change on a required section keeps the same section id (AST-1306 AC3).
- Format change on an optional section keeps the same section id (AST-1306 AC4).
- PUT `/data` replaces `sections` when that key is sent; accent-only PUT leaves sections alone.
- `_pending_*` add still slugs from title in core on save.
- No print CSS / hop changes (AST-1304 / AST-1305).

## Radia review (AST-1323)

# Statutes checked

Ticket-scoped product delta: `21986a9e` (`ArtifactEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `ResumeStructureEditor.tsx` types-only, `App.css`). Formal `ftr...sub` three-dot diff includes unrelated sibling merges (AST-1311–1318 inbox/gmail/SA tests); scored on the four-file UI fix unless noted.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.* (3) | scoped | not-applicable | no agent paths |
| astral.batch.* (4) | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | conforms | format options from `structureCatalog.body_formats` prop (GET catalog) |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no score-floor paths |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no env wiring |
| astral.debug.* (2) | scoped | not-applicable | no debug paths |
| astral.dispatch.* (2) | scoped | not-applicable | no dispatch paths |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | engineer delta is frontend only |
| astral.git.betty-no-src-or-features | scoped | not-applicable | engineer role statute |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commit touches only planned `src/ui/frontend/**` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | UI-only delta |
| astral.layers.import-direction | scoped | conforms | page → components; no data/external imports added |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no hardcoded format tuple; catalog-driven `<select>` |
| astral.idioms.* (3) | scoped | not-applicable | no API/auth paths changed |
| astral.seed.* (5) | scoped | not-applicable | no seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB paths |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | authoring logic moved into existing `ArtifactEditor` stack; types retained in thin module |
| astral.standards.in-scope-only | scoped | conforms | UI-only; no API/core/config/hop edits |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names only |
| astral.standards.no-cross-contamination | scoped | conforms | optional props gated; `JobAnalysisReportModal` unchanged |
| astral.standards.no-hardcoded-sets | scoped | conforms | formats from catalog prop only |
| astral.standards.public-then-helpers | scoped | conforms | helpers scoped inside `ArtifactEditor` |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils change |
| astral.state.* (3) | scoped | not-applicable | no state machine |
| astral.ui.frontend-file-placement | scoped | conforms | changes under `components/` + `pages/` |
| astral.ui.naming-conventions | scoped | conforms | `structure-authoring-header`, existing BEM family |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.* (9) | universal | conforms | sub on ftr topology |
| orch.pipeline.* (4) | universal | conforms | fix-lane at Tests Passed |
| orch.roles.* (5) | universal | conforms | n/a to code shape |

**Count:** 65 active statutes scored.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan-fix is UI chrome relocation only |

## Plan adherence (plan-fix patch)

**Matches:** Optional authoring props on `ArtifactEditor`; structure controls on `CollapsiblePanel` header row (title, format, Enabled, **Job edit**, Up/Down, conditional Remove); `stopPropagation` on header controls; body `LabeledTextArea` unchanged between headers; add-section + `Save sections` below stack; standalone `ResumeStructureEditor` removed from page; `ResumeStructureEditor.tsx` reduced to type exports; `handleStructureRowsChange` also syncs tab labels (AC3-friendly); `JobAnalysisReportModal` does not pass catalog props.

**UI-only:** No GET/PUT/core/config changes — per plan.

## Fix-specific checks

### [bug-repro] — fix-now (stale sibling test)

| Test | Verdict |
|------|---------|
| `test_ArtifactsBaseResumeContent.test.tsx` — `AST-1323: structure controls on collapsible header with body between` | **OK** — asserts flat “Resume sections” panel gone, `Job edit` on `.collapsible-panel-header`, format `<select>` in header, body textarea between panels; pins To-be layout. |
| `tests/component/frontend/components/test_ResumeStructureEditor.test.tsx` | **fix-now** — still `import ResumeStructureEditor` default and renders flat editor UI removed in `21986a9e`. Module is types-only; this file will fail import/render. Bible notes it obsolete; Betty did not revise it in `bef854d1` while engineer removed the component. |

### ## What must still hold — OK

| Item | Verdict |
|------|---------|
| Formats from `catalog.body_formats` only | Options mapped from `structureCatalog.body_formats` — no TSX format literals. |
| Required: no Remove; enabled disabled | `!structureRow.required` gate; `disabled={structureRow.required}` on Enabled. |
| Title/format change keeps id | `patchStructureRow(structureRow.id, …)` — id stable. |
| PUT replace / accent-only / `_pending_*` slug | `saveStructure` in page unchanged; still core slug on save. |
| No AST-1304/1305 hop/emit changes | UI-only delta. |
| `JobAnalysisReportModal` read-only structure tabs | No catalog/authoring props passed. |

## Findings

### fix-now — Obsolete `test_ResumeStructureEditor.test.tsx` after default export removed
**Location:** `tests/component/frontend/components/test_ResumeStructureEditor.test.tsx` (unchanged on branch); `src/ui/frontend/src/components/ResumeStructureEditor.tsx` (types only @ `21986a9e`)
**Finding:** Plan step 4 removes the flat editor UI; engineer did. Component test still imports and renders `ResumeStructureEditor` default export (AST-1306 cases). Manifest green for `AST-1323` page repro does not excuse a broken sibling test file on full frontend tier.
**Recommendation:** Delete or rewrite `test_ResumeStructureEditor.test.tsx` to type-only smoke / drop file; migrate any still-needed catalog assertions into `test_ArtifactsBaseResumeContent` (page test already covers header authoring). Route via `resolve-child` or Betty `[qa-handoff]`.

### advisory — Dead CSS for removed flat editor
**Location:** `src/ui/frontend/src/App.css` — `.base-resume-structure-editor`, `.base-resume-structure-editor-title`, `.base-resume-structure-row`, `.base-resume-structure-row-id` unused after UI removal; `.base-resume-structure-add` / `.base-resume-structure-save` still used.
**Recommendation:** Optional cleanup per plan step 5; non-blocking.

## What's solid

- Correct UX target: structure authoring interleaved with section bodies on one collapsible stack.
- `structureAuthoring` gate prevents accidental authoring chrome on job modal / rubric modes.
- Bug-repro page test directly encodes the reported layout defect and To-be.

## Notes

- **Parent shape:** normal stacked on ftr → clean **PROCEED** path is **Review Posted → User Testing** (skip `resolve-child`) once fix-now cleared; current gate is **REVIEW**.
- **Tip:** `21986a9e` is the engineer product commit; `bef854d1` added page bug-repro only.
- **merge-tests @ `6797d902`:** carries unrelated sibling test/bible commits on the `ftr...sub` diff — not AST-1323 product scope.

## Frame diff

(none) — UI-only relocation matches plan-fix scope; stale component test is the gap.

context_tokens≈105000
— Radia

---
