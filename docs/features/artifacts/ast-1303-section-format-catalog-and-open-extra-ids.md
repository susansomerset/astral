# AST-1303 — Section format catalog and open extra ids

**Linear:** https://linear.app/astralcareermatch/issue/AST-1303/section-format-catalog-and-open-extra-ids  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections  
**Publish ref:** `sub/AST-1299/AST-1303-section-format-catalog-and-open-extra-ids`

Owns the config contract for required seven section ids, the closed body-format list (including `bullet_list` and `experience_detail`), default formats for required and historical optional slugs, and the allowed italic/bold emphasis tag names. Changes `normalize_resume_structure` so extra titled sections persist instead of raising `unknown resume section id`, and so the seven required ids cannot be omitted or disabled. Does **not** own HTML emit (**AST-1304**), hops/content blobs/legacy label ingest (**AST-1305**), or the structure editor UI (**AST-1306**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add required / historical-optional id tuples; compose `RESUME_STRUCTURE_KNOWN_SECTION_IDS` from them (same ten ids, same order); add body-format tuple, default-format map, extra-id pattern, reserved extra-id tuple, emphasis tag names; put `format` on each non-contact entry in `RESUME_STRUCTURE_DEFAULT`. | utils |
| `src/core/candidate.py` | `normalize_resume_structure`: require the seven ids (present + `enabled=True`); accept extra slug ids; persist `format` from config defaults / closed list; lock `experience` to `experience_detail`; drop `format` on contact ids. | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `src/core/builder.py` HTML emit by format, leftover prose Experience, Style D per-section debug | AST-1304 |
| Craft/draft hop schemas, `_flatten_craft_resume_section_strings` KNOWN gate, `draft_job_resume_allowed_section_keys`, legacy label→extra slug ingest | AST-1305 |
| Structure editor UI, format picker API shape, PUT overlay that can *remove* optionals | AST-1306 |
| `BUILD_CONFIG["supported_sections"]`, `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, cover-letter shape | out of this child |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 2, 4–6, 8–11 are siblings (emit / hops / UI / debug). Do not implement them here.

| Child AC | Stage |
|----------|--------|
| 1 — seven-only structure is valid; absent optionals do not fail **normalize** (builder render of that structure is AST-1304) | 2 |
| 2 — title change on a required section does not change its id | 2 (existing `title` field; id stays the dict key) |
| 3 — required sections cannot be removed | 2 |

## Stage 1: Config catalog

**Done when:** `src/utils/config.py` declares the required seven ids, historical optional ids, closed body formats, default format-per-slug map, extra-id pattern, reserved extra-id names, and emphasis tag names. `RESUME_STRUCTURE_KNOWN_SECTION_IDS` is still exactly the same ten strings in the same order as today (so AST-1270 / AST-1305 hop intersections do not move). `RESUME_STRUCTURE_DEFAULT` body sections carry `format` from the map. No `candidate.py` behavior change in this stage.

1. In `src/utils/config.py`, immediately above the existing `# Per-candidate resume section catalog (AST-517)` block (keep `RESUME_STRUCTURE_CONTACT_SECTION_IDS` where it is), replace the current `RESUME_STRUCTURE_KNOWN_SECTION_IDS` tuple with this family. Use these **exact** names and values:

   ```python
   # Per-candidate resume section catalog (AST-517 / AST-1303).
   # Persistence: artifacts.resume_structure. Extra ids are per-candidate;
   # this list is not a closed extra catalog.
   RESUME_STRUCTURE_REQUIRED_SECTION_IDS = (
       "candidate_name",
       "candidate_title",
       "candidate_tagline",
       "candidate_contact_detail",
       "professional_summary",
       "core_competencies",
       "experience",
   )
   RESUME_STRUCTURE_HISTORICAL_OPTIONAL_SECTION_IDS = (
       "prior_experience",
       "education_certifications",
       "technical_skills",
   )
   RESUME_STRUCTURE_KNOWN_SECTION_IDS = (
       *RESUME_STRUCTURE_REQUIRED_SECTION_IDS,
       *RESUME_STRUCTURE_HISTORICAL_OPTIONAL_SECTION_IDS,
   )
   RESUME_STRUCTURE_BODY_FORMATS = (
       "free_prose",
       "bullet_list",
       "word_cloud",
       "dual_column",
       "indented_bold_single",
       "experience_detail",
   )
   RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID = {
       "professional_summary": "free_prose",
       "core_competencies": "word_cloud",
       "experience": "experience_detail",
       "prior_experience": "word_cloud",
       "education_certifications": "indented_bold_single",
       "technical_skills": "dual_column",
   }
   RESUME_STRUCTURE_EMPHASIS_TAG_NAMES = ("i", "em", "b", "strong")
   RESUME_STRUCTURE_EXTRA_ID_PATTERN = r"^[a-z][a-z0-9_]*$"
   RESUME_STRUCTURE_RESERVED_EXTRA_IDS = (
       "sections",
       "accent_color",
       "content",
   )
   ```

   Keep `RESUME_STRUCTURE_CONTACT_SECTION_IDS` as the existing four-tuple (`candidate_name`, `candidate_title`, `candidate_tagline`, `candidate_contact_detail`). Do not add a seventh body format named `header`.

2. In `RESUME_STRUCTURE_DEFAULT["sections"]`, **do not** remove `prior_experience`, `education_certifications`, or `technical_skills` (parent: do not strip historical optionals from candidates who have them; default catalog stays the current ten). Add a `"format"` key **only** on the six ids that appear in `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`, each value read from that map (do not retype the format string):

   ```python
   "format": RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["professional_summary"],
   ```

   (same for `core_competencies`, `experience`, `prior_experience`, `education_certifications`, `technical_skills`). Contact/header ids must **not** gain a `format` key.

3. Do **not** edit `BUILD_CONFIG["supported_sections"]`, `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, `TASK_CONFIG`, `TOKEN_SOURCES`, or any hop seed JSON.

4. Do **not** change `src/core/candidate.py` in this stage (Stage 2 imports the new names). Leaving normalize on the old KNOWN reject for one commit is intentional.

⚠️ **Decision:** `RESUME_STRUCTURE_KNOWN_SECTION_IDS` stays the closed **historical** ten-id tuple, composed from required + historical optional so it cannot drift. Extra ids are **not** appended to KNOWN. Hop whitelist (`base_resume` ∩ KNOWN) stays AST-1305.

⚠️ **Decision:** Emphasis allowlist is HTML tag **names** (`i`, `em`, `b`, `strong`), not bracketed tokens and not a free attribute surface. AST-1304 is the only consumer; this ticket only declares the set.

⚠️ **Decision:** Contact/header sections are not one of the six body formats. They have no `format` in DEFAULT and Stage 2 strips `format` if a caller sends one.

## Stage 2: Normalize — required seven + open extras + format

**Done when:** Calling `normalize_resume_structure` on a dict whose `sections` are exactly the seven required ids (each with title / enabled True / order int / job_agent_editable bool, formats omitted) returns those seven, with `format` filled from `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID` on the three body required ids and **no** `format` on the four contact ids. The same call plus `highlights` / `publications` specs (`title` Highlights / Publications, `enabled` True, `format` `bullet_list`, order ints, `job_agent_editable` True) returns those extras with `format` `bullet_list`. Omitting `experience` raises `ValueError` whose message contains `missing required`. `enabled=False` on `professional_summary` raises `ValueError` whose message contains `cannot be disabled`. `professional_summary` with `title` `"Summary"` keeps `id` `"professional_summary"`. A current ten-id blob with **no** `format` keys still normalizes (defaults applied). `unknown resume section id` is no longer raised for a valid extra slug.

1. In `src/core/candidate.py`, extend the existing `from src.utils.config import` list (do not add a second config import) with:

   - `RESUME_STRUCTURE_REQUIRED_SECTION_IDS`
   - `RESUME_STRUCTURE_BODY_FORMATS`
   - `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`
   - `RESUME_STRUCTURE_EXTRA_ID_PATTERN`
   - `RESUME_STRUCTURE_RESERVED_EXTRA_IDS`

   Keep the existing `RESUME_STRUCTURE_KNOWN_SECTION_IDS` import (hop helpers still use it). Do **not** import `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES` (unused until AST-1304).

2. Next to `_HEX_COLOR_RE`, add:

   ```python
   _RESUME_SECTION_EXTRA_ID_RE = re.compile(RESUME_STRUCTURE_EXTRA_ID_PATTERN)
   ```

3. Rewrite **only** the section loop inside `normalize_resume_structure` (keep the existing `raw` / `sections` / `accent_color` preamble and the final empty-sections guard). Replace the current

   ```python
   if sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS:
       raise ValueError(f"unknown resume section id: {sid}")
   ```

   block and the `out["sections"][sid] = {…}` write with the following rules, in this order, for each `(sid, spec)` in `sections_in.items()`:

   a. Keep today’s checks: `spec` must be a `dict`; `str(spec.get("id") or sid).strip() == sid`; `title` is a non-empty stripped string; `enabled` is `bool`; `order` is `int`.

   b. `job_agent_editable`: if `sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS` and `job_agent_editable` is missing (`"job_agent_editable" not in spec`), set `job_ed = True`. Else require `isinstance(job_ed, bool)` as today (known slugs with a missing/non-bool value still raise).

   c. After the per-spec field checks, **before** writing `out["sections"][sid]`, if you have finished the loop setup: actually do the required-missing check **once before the loop** (not per spec):

      ```python
      missing = [rid for rid in RESUME_STRUCTURE_REQUIRED_SECTION_IDS if rid not in sections_in]
      if missing:
          raise ValueError(f"resume_structure missing required section(s): {missing}")
      ```

   d. If `sid in RESUME_STRUCTURE_REQUIRED_SECTION_IDS` and `enabled is False`: raise `ValueError(f"required section {sid} cannot be disabled")`.

   e. If `sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS`:
      - if `sid in RESUME_STRUCTURE_RESERVED_EXTRA_IDS`: raise `ValueError(f"invalid extra section id: {sid}")`
      - if `_RESUME_SECTION_EXTRA_ID_RE.fullmatch(sid)` is `None`: raise `ValueError(f"invalid extra section id: {sid}")`

   f. Resolve `format` into local `fmt` (`None` or a string from the closed list):

      | `sid` | Rule |
      |-------|------|
      | in `RESUME_STRUCTURE_CONTACT_SECTION_IDS` | Do not read `format` into the output spec. If `spec` has a `format` key, drop it (do not raise). |
      | `"experience"` | If `format` missing / `None` / blank string → `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["experience"]`. If present and not `"experience_detail"` → raise `ValueError("section experience format must be experience_detail")`. Output includes `"format": "experience_detail"`. |
      | any other id | If `format` missing / `None` / blank string → if `sid in RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID` use that map value; else raise `ValueError(f"section {sid} requires format")`. If present, `fmt` must be a member of `RESUME_STRUCTURE_BODY_FORMATS` else raise `ValueError(f"section {sid} format must be one of {list(RESUME_STRUCTURE_BODY_FORMATS)}")`. Output includes `"format": fmt`. |

   g. Write `out["sections"][sid]` as today’s five keys plus `"format"` when rule (f) says to include it. Do **not** copy other spec keys (`content`, `text`, etc.).

4. Do **not** change: `default_resume_structure`, `resolve_resume_structure`, `enabled_resume_structure_sections`, `enabled_resume_section_ids`, `resume_section_titles`, `filter_base_resume_to_structure`, `filter_content_to_resume_structure`, `split_craft_resume_base_payload`, `_flatten_craft_resume_section_strings`, `draft_job_resume_allowed_section_keys`, `normalize_craft_resume_base_agent_payload`, `normalize_draft_job_resume_agent_payload`, `validate_draft_job_resume_payload`, `src/core/builder.py`, `src/ui/api/api_candidate.py`, any TSX.

5. Do **not** add `debug=` / Style D logging to `normalize_resume_structure` (AST-1304).

6. Do **not** slug a title into an id. Extra keys must already match `RESUME_STRUCTURE_EXTRA_ID_PATTERN`. Title→id slugging of legacy label/content arrays is AST-1305.

⚠️ **Decision:** Required sections must be **present and `enabled=True`**. `enabled=False` on a required id is treated as removal. Title may change (`Professional Summary` → `Summary`); id stays the key.

⚠️ **Decision:** `experience` is locked to `experience_detail`. Other required/historical slugs may carry a different closed format if the caller sends one (AST-1306 format edits). Missing format on those slugs uses the default map so current persisted blobs keep working.

⚠️ **Decision:** PUT `/api/candidates/<id>/data` already merges incoming `sections` onto `resolve_resume_structure` then calls `normalize_resume_structure`. That overlay stays additive (omitting an optional in the PUT body does not delete it). Seven-only and extras-only **wholesale** dicts are the normalize contract (craft `split_craft_resume_base_payload` replaces structure from the agent blob). Do not change the PUT merge in this ticket (AST-1306).

⚠️ **Decision:** Extra sections may choose **any** of the six `RESUME_STRUCTURE_BODY_FORMATS`, including `experience_detail`. Publications in the parent brief is `bullet_list` (callers send that). Content-array filtering for non-`experience` `experience_detail` extras is AST-1304 / AST-1305 — this ticket only persists the structure row.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that does not exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits `code(AST-1303): …`, publishes to `origin/sub/AST-1299/AST-1303-section-format-catalog-and-open-extra-ids`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — one config catalog family plus the existing `normalize_resume_structure` gate in `candidate.py`; no builder, hops, or UI.

**Conf:** `high` — the reject site is the current `sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS` line; parent already named the seven ids, six formats, historical defaults, and italic/bold-only emphasis set.

**Risk:** `Medium` — a wrong required check or format lock would `ValueError` existing ten-id blobs (resolve would fall back to DEFAULT and look like a structure reset); changing KNOWN membership would break AST-1270 draft whitelist. Plan keeps KNOWN as the same ten ids and fills missing formats from the map.

## Code Rules check

- §1.1 / `astral.standards.in-scope-only`: only config + normalize. Hop flatten, builder emit, PUT merge, GET payload shape, craft schema left to siblings.
- §1.3 / `dry-and-focused-functions` / `public-then-helpers`: KNOWN composed from required + historical; DEFAULT `format` values read from `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`; no second format table; no new public helper (one loop change).
- §1.4 / `no-hardcoded-sets`: required ids, formats, defaults, extra-id pattern, reserved ids, emphasis tags live in config; normalize only reads them.
- §2.1 / `config-source-of-truth` / `pattern.config.config-block`: extend the existing `RESUME_STRUCTURE_*` family; do not invent a parallel catalog in core or React.
- §2.4 / §2.6: not applicable (no batch / state machine).
- §3.3 / `import-direction`: core → utils only; no new data/external/ui imports; do not import unused emphasis names.
- §3.5 naming: snake_case constants; no new files.
- `astral.standards.names-not-ticket-ids`: constant names are domain (`RESUME_STRUCTURE_*`), not `AST_1303_*`.
- `astral.standards.debug-contract-gated`: no new debug path here.
- `astral.git.engineer-test-tree-ban`: no `tests/` or bible edits.

## Contract for siblings (non-goals)

- **AST-1304** reads `format` from `resolve_resume_structure(…)["sections"][sid]` and `RESUME_STRUCTURE_BODY_FORMATS` / `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES`. Emit Highlights / Publications as `bullet_list`; do not treat leftover prose Experience as the required Experience section; Style D when `debug=True`.
- **AST-1305** stops treating extra keys as unknown solely because they are outside KNOWN; draft whitelist becomes this candidate’s current base_resume keys (including extras); legacy label/content arrays slug unmatched titles with `RESUME_STRUCTURE_EXTRA_ID_PATTERN`.
- **AST-1306** serves the format catalog from config via the API (not a hardcoded React list); operators add/title/format/enable/reorder optionals; required seven cannot be removed in the editor.
