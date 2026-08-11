# AST-1305 — Hops, content blobs, and legacy extra labels

**Linear:** https://linear.app/astralcareermatch/issue/AST-1305/hops-content-blobs-and-legacy-extra-labels  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections  
**Publish ref:** `sub/AST-1299/AST-1305-hops-content-blobs-and-legacy-extra-labels`

After **AST-1303**: craft-base and draft-job accept extra section keys that exist on that candidate’s base resume / structure; they must not fail with “unknown section” merely because the key is outside `RESUME_STRUCTURE_KNOWN_SECTION_IDS`. Draft whitelist is this candidate’s current `artifacts.base_resume` section keys (including extras), not `base ∩ KNOWN`. Legacy `{label, content}` arrays keep unmatched titles as extra sections (id slugged from the title) on ingest and in `{$BASE_RESUME}` token JSON. Experience persists only as an `experience_detail` job array — leftover prose Experience is omitted / rejected, not stored as the required Experience section. Does **not** own HTML chrome (**AST-1304**), AST-1201 generation order, or the structure editor (**AST-1306**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT = "bullet_list"` next to the AST-1303 `RESUME_STRUCTURE_*` family. | utils |
| `src/core/candidate.py` | Legacy label ingest + slug; token serialize keeps unmatched titles; flatten/split/filters accept extra ids and job arrays; draft whitelist drops the KNOWN intersection; draft validate rejects prose Experience. | core |
| `src/core/tracker.py` | `_resume_section_has_body` / `_resume_payload_body`: a non-empty job array is a body for any section id, not only `experience`. `_prepare_job_resume_content` keeps keys that are enabled on structure **or** in the base-derived allowed set. | core |
| `src/ui/api/api_candidate.py` | `PUT /api/candidates/<id>/data`: when `artifacts.base_resume` is a label/content list (or a dict), call the core ingest helper before filter/save so unmatched titles become extra structure rows + id-keyed content. | ui |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `src/core/builder.py` HTML emit by format, leftover prose Experience **render**, Style D per-section debug | AST-1304 |
| Structure editor, format picker API, PUT overlay that removes optionals | AST-1306 |
| `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` required ten fields, `finalize_job_resume` schema, `BUILD_CONFIG["supported_sections"]` | out of this child (schema already ignores unknown keys; extras are not a closed catalog) |
| Cover-letter shape / emit | parent boundary |
| AST-1201 daisy-chain generation order | adjacent, not this child |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 1–4, 7, 9, 11 are siblings (normalize / emit / editor / emphasis / debug). Do not implement them here.

| Child AC | Stage |
|----------|--------|
| 5 — craft-base and draft-job accept extra keys on this candidate’s base / structure; no “unknown section” solely for being outside the old ten-id list | 2 |
| 6 — a job resume cannot introduce a section the candidate structure does not enable (and cannot invent a key that is on neither structure nor this candidate’s base) | 2 |
| 7 — Abrams-style label/content array with Highlights and Publications does not drop those labels on ingest or token serialize | 1 |
| 8 — leftover prose Experience is not persisted as the required Experience section; Experience counts only as an `experience_detail` array | 3 |

## Stage 1: Config default + legacy label ingest + token serialize

**Done when:** `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` is `"bullet_list"` in `src/utils/config.py`. Calling `ingest_legacy_label_content_base_resume` on a seven-required-only normalized structure plus a label/content list that includes items titled `Highlights` and `Publications` (plus a `Professional Summary` row) returns a content dict that has `highlights` and `publications` string values and a structure whose `sections` include those two ids with `title` Highlights / Publications, `enabled` True, `format` `bullet_list`, and `job_agent_editable` True. `format_base_resume_for_token` on `artifacts.base_resume` set to that same list (structure still seven-only) returns JSON that contains `"highlights"` and `"publications"` keys — those labels are not omitted. A `Experience` list row whose `content` is a prose string does **not** appear as a string under `"experience"` in the token JSON.

1. In `src/utils/config.py`, immediately after `RESUME_STRUCTURE_RESERVED_EXTRA_IDS` (the AST-1303 family), add:

   ```python
   RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT = "bullet_list"
   ```

   Do **not** change `RESUME_STRUCTURE_KNOWN_SECTION_IDS`, `RESUME_STRUCTURE_DEFAULT`, `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, `TASK_CONFIG`, `TOKEN_SOURCES`, or `BUILD_CONFIG["artifact_shapes"]`.

2. In `src/core/candidate.py`, extend the existing `from src.utils.config import` list (do not add a second config import) with `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT`. Keep the AST-1303 names already imported (`RESUME_STRUCTURE_EXTRA_ID_PATTERN`, `RESUME_STRUCTURE_RESERVED_EXTRA_IDS`, `RESUME_STRUCTURE_KNOWN_SECTION_IDS`, `RESUME_STRUCTURE_DEFAULT`, `RESUME_STRUCTURE_REQUIRED_SECTION_IDS`, `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`, `RESUME_STRUCTURE_BODY_FORMATS`, `RESUME_STRUCTURE_CONTACT_SECTION_IDS`).

3. Next to `_RESUME_SECTION_EXTRA_ID_RE`, add these helpers (private, after the extra-id regex). Do **not** put slug/title sets inline in callers.

   ```python
   def _slug_resume_extra_section_id(title: str, used: set) -> str:
   ```

   Rules, in order:
   - `s = re.sub(r"[^a-z0-9]+", "_", title.strip().lower()).strip("_")`
   - If `s` is empty or `s[0]` is not `a-z`, set `s = ("s_" + s) if s else "section"`.
   - While `s` is in `used` or `s` is in `RESUME_STRUCTURE_RESERVED_EXTRA_IDS` or `_RESUME_SECTION_EXTRA_ID_RE.fullmatch(s)` is `None`: set `s = f"{base}_{n}"` with `base` equal to the first computed `s` and `n` starting at `2`, incrementing.
   - Add the final `s` to `used` and return it.

   ```python
   def _title_to_structure_section_id(title: str, structure: dict) -> Optional[str]:
   ```

   - `needle = title.strip().casefold()`
   - Walk `structure["sections"]` (if a dict): if `str(spec.get("title") or "").strip().casefold() == needle`, return that `sid`.
   - Else walk `RESUME_STRUCTURE_DEFAULT["sections"]` the same way; return that default id if the titles match (so `Education & Certifications` maps to `education_certifications` even on a seven-only live structure).
   - Else return `None`.

4. Add a **public** function in the public resume-structure block (with `normalize_resume_structure` / `format_base_resume_for_token`, before helpers):

   ```python
   def ingest_legacy_label_content_base_resume(raw_base: Any, structure: dict) -> tuple[dict, dict]:
       """Map dict or {label, content} list → (id-keyed content, structure with extras)."""
   ```

   Implementation (no other behavior):

   a. `base_struct = normalize_resume_structure(structure)` if `structure` is a dict with `sections`, else `default_resume_structure()`. Work on a deep copy of `base_struct` named `out_struct`.

   b. `used = set(out_struct["sections"])`. `content: dict = {}`. `next_order = 1 + max((spec.get("order") or 0) for spec in out_struct["sections"].values())` (use `0` if sections empty — it will not be, required seven are present).

   c. If `raw_base` is a `dict`: for each `(k, v)` in `raw_base.items()`:
      - Skip `k` in `RESUME_STRUCTURE_RESERVED_EXTRA_IDS` and skip `k == "accent_color"`.
      - If `k == "experience"` and not `_is_experience_job_array(v)`: skip (do not store prose Experience).
      - If `_is_experience_job_array(v)` and `v`: `content[k] = v`.
      - Elif `isinstance(v, str)`: `content[k] = v`.
      - Else skip.
      - If `k not in out_struct["sections"]` and `_RESUME_SECTION_EXTRA_ID_RE.fullmatch(k)` and `k not in RESUME_STRUCTURE_RESERVED_EXTRA_IDS`: append a section row (step e) with `sid=k`, `title=k.replace("_", " ").title()`, then `used.add(k)`.

   d. If `raw_base` is a `list`: for each `item` in `raw_base`:
      - Skip if `item` is not a `dict`.
      - `label = str(item.get("label") or "").strip()`. Skip if `label` is empty.
      - `sid = _title_to_structure_section_id(label, out_struct)`.
      - If `sid is None`: `sid = _slug_resume_extra_section_id(label, used)` and append a section row (step e) with that `sid` and `title=label`.
      - `val = item.get("content")`.
      - If `sid == "experience"` and not `_is_experience_job_array(val)`: do **not** write `content["experience"]` (regenerate; still keep/create the experience **structure** row that already exists).
      - Elif `_is_experience_job_array(val)` and `val`: `content[sid] = val`.
      - Else: `content[sid] = str(val) if val is not None else ""`.

   e. Extra / newly introduced historical-optional row shape (write into `out_struct["sections"][sid]` only when the id is missing):

      ```python
      {
          "id": sid,
          "title": title,
          "enabled": True,
          "order": next_order,
          "job_agent_editable": True,
          "format": (
              RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID[sid]
              if sid in RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID
              else RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT
          ),
      }
      ```

      Then `next_order += 1`. Contact ids must not be created here (they already exist on a valid structure). `experience` already exists; do not add a second Experience extra.

   f. `out_struct = normalize_resume_structure(out_struct)` and return `(content, out_struct)`.

   ⚠️ **Decision:** Unmatched Abrams titles become extras with `format` from `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` (`bullet_list`), not `experience_detail`. Publications is a bullet list (parent). Historical titles that match `RESUME_STRUCTURE_DEFAULT` titles reuse those ids (Prior Experience / Education & Certifications / Technical Skills) instead of minting a parallel extra.

   ⚠️ **Decision:** Slug collisions and reserved ids (`sections`, `accent_color`, `content`) take `_2`, `_3`, … so a label is never dropped (AC7).

5. Replace the body of `format_base_resume_for_token` after `raw = artifacts.get("base_resume")` and `structure = resolve_resume_structure(cd)` with:

   - `content, _struct = ingest_legacy_label_content_base_resume(raw, structure)`
   - `section_ids = {sid for sid, spec in _struct.get("sections", {}).items() if isinstance(spec, dict) and spec.get("id")}`
   - `payload = filter_base_resume_to_structure(content, section_ids)`
   - `return json.dumps(payload, indent=2) if payload else ""`

   Do **not** write the database from this function (token resolve stays read-only). The ingest helper is pure.

   Delete the old `title_to_id` / `legacy` loop that skipped labels when `sid` was missing — that is the AC7 drop bug.

6. In `src/ui/api/api_candidate.py` `update_candidate_data`, import `ingest_legacy_label_content_base_resume` from `src.core.candidate` (same import block that already pulls `filter_base_resume_to_structure` / `resolve_resume_structure` / `normalize_resume_structure`). After `resolved = resolve_resume_structure(cd)` and the existing incoming-`resume_structure` merge + `normalize_resume_structure` (keep that block), if `"base_resume" in arts` and `arts["base_resume"]` is a `list` or `dict`:

   - `content, ingested_struct = ingest_legacy_label_content_base_resume(arts["base_resume"], arts.get("resume_structure") or resolved)`
   - `arts["base_resume"] = content`
   - `arts["resume_structure"] = ingested_struct`

   Then keep the existing `filter_base_resume_to_structure(arts["base_resume"], section_ids)` call, but recompute `section_ids` from `enabled_resume_structure_sections(ingested_struct)` **after** ingest (so Highlights / Publications survive the filter).

   Do **not** edit ArtifactEditor or any TSX.

## Stage 2: Craft flatten + draft whitelist (extra keys)

**Done when:** `_flatten_craft_resume_section_strings` on a payload whose `resume_structure.sections` includes enabled `highlights` / `publications` (`bullet_list`) and whose nested `content` dict has those string keys promotes `highlights` and `publications` onto the top-level payload (they are not discarded for being outside KNOWN). `draft_job_resume_allowed_section_keys` on a candidate whose `artifacts.base_resume` is `{"professional_summary": "…", "highlights": "…"}` returns a list that includes `highlights` and does **not** require `highlights in RESUME_STRUCTURE_KNOWN_SECTION_IDS`. `validate_draft_job_resume_payload` accepts a nested or flat draft whose section keys are exactly that allowed set, and returns an error whose message contains `Unknown resume section key` when the payload includes `not_a_section`. A draft key that is on neither enabled structure nor this candidate’s base-derived allowed set is rejected.

1. In `src/core/candidate.py`, add a private predicate next to the flatten helpers:

   ```python
   def _is_resume_content_section_id(sid: str) -> bool:
       if sid in RESUME_STRUCTURE_RESERVED_EXTRA_IDS or sid == "accent_color":
           return False
       if sid in RESUME_STRUCTURE_KNOWN_SECTION_IDS:
           return True
       return _RESUME_SECTION_EXTRA_ID_RE.fullmatch(sid) is not None
   ```

2. In `_flatten_craft_resume_section_strings`, change `_promote`:

   - Replace `if sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS: return` with `if not _is_resume_content_section_id(sid): return`.
   - Replace the two `sid == "experience" and _is_experience_job_array(...)` branches with the same logic for **any** `sid`: if `payload[sid]` is already a job array, return; if `val` is a job array, set `payload[sid] = val` and return.

3. In the same function, replace `for sid in RESUME_STRUCTURE_KNOWN_SECTION_IDS:` (direct keys on `raw_struct`) with:

   ```python
   for sid in list(raw_struct.keys()):
       if _is_resume_content_section_id(sid):
           _promote(sid, raw_struct[sid])
   ```

   Keep the enabled-`sections` nested `content`/`text`/`value`/`body` loop as it is (it already walks whatever ids are on the structure, including extras from AST-1303).

4. Replace `draft_job_resume_allowed_section_keys` so it no longer intersects `RESUME_STRUCTURE_KNOWN_SECTION_IDS`.

   ```python
   def draft_job_resume_allowed_section_keys(candidate_data: dict) -> list[str]:
       """Section keys from artifacts.base_resume (including extras); not ∩ KNOWN."""
   ```

   Rules:
   - Read `artifacts.base_resume`. If missing / neither `dict` nor `list`: return `[]`.
   - `structure = resolve_resume_structure(cd)`.
   - `content, ingested = ingest_legacy_label_content_base_resume(base, structure)`.
   - Return `sorted(k for k in content if _is_resume_content_section_id(k))`.

   Do **not** call `enabled_resume_section_ids` for this whitelist (AST-1270: candidates without a useful structure blob still validate when base keys match; extras on the base now count).

   ⚠️ **Decision:** Whitelist = this candidate’s current base section keys after label ingest, including extra slugs. It is **not** `base ∩ KNOWN` and **not** “all enabled structure ids” (a job still cannot invent a section that is only on structure and not on base — same AST-1270 rule, now open to extras).

5. In `validate_draft_job_resume_payload`, keep the unknown-key error shape:

   `Unknown resume section key '{key}' (not in candidate base_resume keys: {sorted(allowed)})`

   That error must fire for keys outside `allowed` (AC6: job cannot introduce a section this candidate does not already have on base / ingested extras). Do **not** add a second reject that mentions “ten” or `KNOWN`.

   Leave consult-key rejects and metadata skips unchanged.

6. In `src/core/tracker.py` `_prepare_job_resume_content`, after `filtered = filter_content_to_resume_structure(...)`:

   - `allowed = set(candidate_mod.draft_job_resume_allowed_section_keys(candidate_data))`
   - For each `sid, val` in `(resume_content or {}).items()`: if `sid in allowed` and `sid not in filtered` and `sid not in RESUME_STRUCTURE_CONTACT_SECTION_IDS`:
     - if `_is_experience_job_array(val) and val`: `filtered[sid] = val`
     - elif `isinstance(val, str) and val.strip()`: `filtered[sid] = val`
   - Then keep the existing contact snapshot merge.

   This is how an un-ingested Abrams list (token showed `highlights`; structure not yet saved) still persists on the job without allowing a brand-new id the base never had.

7. In `src/core/tracker.py`:

   - `_resume_section_has_body`: if `candidate_mod.is_experience_job_array(val) and val`: return `True` for **any** `sid` (not only `experience`). Keep the string-strip fallback for non-arrays.
   - `_resume_payload_body`: copy a value when `isinstance(v, str)` **or** `candidate_mod.is_experience_job_array(v)` (any key, not only `k == "experience"`). Keep nest-key / metadata skips.

8. Do **not** edit `src/core/agent.py` schema validation (`_validate_schema_object_fields` already ignores keys that are not in the schema). Do **not** add extra keys to `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`. Do **not** change `do_task` call sites — persist still goes through existing `split_craft_resume_base_payload` / draft validate that `do_task` already invokes (`astral.agent.do-task-delegation`).

## Stage 3: Experience persists only as `experience_detail` array

**Done when:** `split_craft_resume_base_payload({"resume_structure": <valid seven+>, "experience": "prose leftover"})` returns content **without** an `experience` key. `filter_base_resume_to_structure({"experience": "prose"}, {..., "experience"})` does not include `experience`. `validate_draft_job_resume_payload` on a payload whose `experience` value is a non-empty string returns an error containing `experience_detail` and does **not** accept the string. A well-typed job array still validates and still lands in content / token JSON.

1. In `filter_base_resume_to_structure`:

   ```python
   if _is_experience_job_array(v) and v:
       out[k] = v
   elif k != "experience" and isinstance(v, str):
       out[k] = v
   ```

   Do not `str()`-corrupt other shapes. Empty job arrays are omitted.

2. In `filter_content_to_resume_structure`, same rule: keep non-empty job arrays for any allowed key; keep non-empty strings for allowed keys **except** `experience`.

3. In `split_craft_resume_base_payload`, when copying `enabled_ids` from `parsed`:

   - If `_is_experience_job_array(val)` and `val`: `content[key] = val`.
   - Elif `key != "experience"` and `isinstance(val, str)`: `content[key] = val`.
   - Do not copy a prose `experience` string.

4. In `validate_draft_job_resume_payload`, replace the `experience` string-accept branch. After the existing job-array accept path, if `key == "experience"` and the value is not a non-empty job array:

   - `err = "Section 'experience' must be an experience_detail job array"`
   - `rejected.append(key)` and `break`

   Delete the `if isinstance(val, str): accepted.append(key); continue` path for `experience`. Location-coercion on job dicts stays as it is today.

   ⚠️ **Decision:** Do not invent a stub job object from leftover prose. Omit on persist/token and fail draft validate so the hop regenerates a real `experience_detail` array. AST-1304 still owns “do not render leftover prose as the Experience section” if an old blob is read by the builder before this persist path rewrites it.

5. Do **not** change `pin_experience_job_facts_from_base` (it already no-ops when base or tailored experience is not a job array).

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that does not exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits `code(AST-1305): …`, publishes to `origin/sub/AST-1299/AST-1305-hops-content-blobs-and-legacy-extra-labels`, then continues.

**Parent attach:** this child is **After AST-1303**. `sync-child.sh --ftr AST-1299` looks for `origin/ftr/AST-1299` (missing). Before Stage 1, merge `origin/ftr/AST-1299-support-alternative-resume-sections` if it is not already an ancestor of `HEAD` (AST-1303 catalog + `normalize_resume_structure` extras must be on the tree).

## Self-Assessment

**Scope:** `Single-Component` — content-contract work in `candidate.py` (ingest, flatten, whitelist, filters) with a one-constant config add and thin tracker / `api_candidate` callers; no builder emit and no editor.

**Conf:** `high` — AST-1303 named the exact leftover sites (`_flatten_craft_resume_section_strings` KNOWN gate, `draft_job_resume_allowed_section_keys`, label→slug ingest); schema validation already allows extra keys; the drop bugs are the `title_to_id` miss and `base ∩ KNOWN`.

**Risk:** `Medium` — a wrong whitelist would fail draft hops or let a job invent a section; omitting prose Experience will empty that key on old string blobs until the hop regenerates the array (intended). Slug collision suffixes could rename a second “Highlights” to `highlights_2` rather than merge.

## Code Rules check

- §1.1 / `astral.standards.in-scope-only`: hops, content blobs, legacy ingest only. No `builder.py`, no TSX, no finalize schema, no AST-1201 order.
- §1.3 / `dry-and-focused-functions` / `public-then-helpers`: one ingest function shared by token serialize, PUT, and draft whitelist; slug/title match are helpers under it; no second copy of extra-id rules.
- §1.4 / `no-hardcoded-sets`: extra-id pattern, reserved ids, default extra format, historical titles all from `RESUME_STRUCTURE_*`. No inline `{"highlights", "publications"}`.
- §2.1 / `config-source-of-truth` / `pattern.config.config-block`: `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` lives in the existing family; callers read it.
- §2.2 / `astral.agent.do-task-delegation`: do not add a new Anthropic/path assembly; change normalize/validate/split that `do_task` already calls.
- §2.4 / §2.6: not applicable (no new batch / state machine).
- §3.3 / `import-direction`: core → utils; UI → core only (PUT calls ingest); tracker already imports candidate.
- §3.5 naming: `ingest_legacy_label_content_base_resume`, `_slug_resume_extra_section_id` — domain names, not `AST_1305_*`.
- `astral.standards.debug-contract-gated`: no new debug lines (AST-1272 draft trail stays as-is; builder Style D is AST-1304).
- `astral.git.engineer-test-tree-ban`: no `tests/` or bible edits.

## Contract for siblings (non-goals)

- **AST-1304** renders extras by `format`; does not treat leftover prose Experience as the required Experience section; Style D when `debug=True`.
- **AST-1306** is how operators add/title/format extras in the editor. This ticket only mints extras from legacy labels / extra ids already on the hop payload.
- **AST-1303** already accepts extra slugs on `normalize_resume_structure` and locks `experience` format to `experience_detail`. Do not revisit that loop except by calling `normalize_resume_structure` on ingest output.

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1305
**Publish ref:** `sub/AST-1299/AST-1305-hops-content-blobs-and-legacy-extra-labels` @ `1cc15431`
**Overall:** APPROVED

## Traceability

| Child AC | Plan stage(s) | Definition anchor |
|----------|---------------|-------------------|
| 1 — Craft-base / draft-job accept extra keys on this candidate’s base/structure; no “unknown section” solely for being outside old ten-id list | Stage 2 (flatten `_is_resume_content_section_id`, whitelist ingest); Stage 1 ingest on token path | Parent functional scope: “Craft-base and draft-job hops accept those extra keys” |
| 2 — Job resume cannot introduce a section the candidate structure does not enable | Stage 2 (`validate_draft_job_resume_payload` unknown-key gate; tracker `_prepare_job_resume_content`) | Parent functional scope: “Job artifacts remain a subset of the candidate’s **enabled** structure ids” |
| 3 — Abrams label/content with Highlights/Publications not dropped on ingest or token serialize | Stage 1 (`ingest_legacy_label_content_base_resume`, `format_base_resume_for_token`, PUT ingest) | Parent: “Legacy label/content arrays keep extra titles” |
| 4 — Leftover prose Experience not persisted; Experience only as `experience_detail` array | Stage 3 (filters, split, draft validate reject prose) | Parent: “Experience content is an `experience_detail` array; leftover prose … regenerated” |

Stages → child AC: Stage 1 → AC 3; Stage 2 → AC 1–2; Stage 3 → AC 4. No orphan stages.

## Statute verdicts

| Statute / pattern | Verdict | Rationale |
|-------------------|---------|-----------|
| `pattern.config.config-block` | conforms | `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` added beside existing `RESUME_STRUCTURE_*` family |
| `astral.config.config-source-of-truth` | conforms | Extra default format + slug rules read config; no parallel catalog in core |
| `astral.standards.no-hardcoded-sets` | conforms | Removes `KNOWN` intersection / title-map drop; `_is_resume_content_section_id` uses pattern + reserved ids |
| `astral.agent.do-task-delegation` | conforms | Changes normalize/validate/split paths `do_task` already calls; no new Anthropic path |
| `astral.standards.in-scope-only` | conforms | `candidate.py`, one config constant, thin `tracker` / `api_candidate`; no builder/TSX |
| `astral.standards.dry-and-focused-functions` | conforms | Single public `ingest_legacy_label_content_base_resume` shared by token, PUT, whitelist |
| `astral.standards.public-then-helpers` | conforms | Ingest public; slug/title helpers private |
| `astral.layers.import-direction` | conforms | core → utils; `api_candidate` → core ingest |
| `astral.standards.names-not-ticket-ids` | conforms | Domain names (`ingest_legacy_label_content_base_resume`, etc.) |
| `astral.standards.no-cross-contamination` | conforms | Explicit non-goals for builder emit and editor |

## Considered and excluded

**Considered:** statutes/patterns in child **In scope** (above).

**Excluded (boundary / sibling):**
- `astral.standards.debug-contract-gated` — Style D builder trail is AST-1304
- `astral.layers.ui-config-driven-business-logic` — format picker HTTP is AST-1306
- `src/core/builder.py` HTML emit — AST-1304
- Structure editor / TSX — AST-1306
- `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` / `finalize_job_resume` / `BUILD_CONFIG["supported_sections"]` — schema already ignores unknown keys; out of child
- Cover-letter shape — parent boundary
- AST-1201 generation order — adjacent, unchanged
- `astral.batch.claim-process-release`, `astral.dispatch.run-next-is-chain-authority` — no dispatch lifecycle change
- `tests/`, `docs/test-bible/**` — Betty

## Findings

| Sev | Location | Finding | Recommendation |
|-----|----------|---------|----------------|
| **discuss** | Stage 2 §6 (`tracker._prepare_job_resume_content`) | Child AC 2 / parent functional scope require job ⊆ **enabled** structure ids. Stage 2 step 6 re-injects base-whitelist keys dropped by `filter_content_to_resume_structure` (enabled-only) so Abrams extras can persist before structure is saved on disk. Deliberate, but tensions with strict “does not enable” wording if a base key exists while the persisted structure row is disabled or absent. | Confirm product intent: keep bridge for un-ingested extras, or intersect `allowed` with `enabled_resume_section_ids(resolve_resume_structure(cd))` (possibly after in-memory ingest) before re-inject. |
| **acceptable** | Traceability table in plan doc | Plan doc labels child work as parent AC 5–8; Linear child ACs are 1–4. | Cosmetic; mapping is correct. |
| **acceptable** | Stage 3 `filter_content_to_resume_structure` | AST-1304 sibling also widens this helper for format emit. | Merge-order coordination on `origin/ftr/AST-1299`; not a plan defect for this child. |

**Tip verification:** On worktree tip, `format_base_resume_for_token` still drops unmatched labels (`title_to_id` miss at lines 2080–2082), `draft_job_resume_allowed_section_keys` is `base ∩ KNOWN` dict-only, `_flatten_craft_resume_section_strings` gates on `RESUME_STRUCTURE_KNOWN_SECTION_IDS` — all named sites the plan targets. AST-1303 `RESUME_STRUCTURE_EXTRA_ID_PATTERN` / `normalize_resume_structure` extras are present; `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` is not yet (Stage 1 adds it). Dependency merge note in execution contract is appropriate.

**Self-assessment:** Single-Component / high conf / medium risk — honest; sites and failure modes are specific.

context_tokens≈38000
— Joan

## Review (build stub)

**Publish ref:** `origin/sub/AST-1299/AST-1305-hops-content-blobs-and-legacy-extra-labels`  
**Tip:** `2fb7a993f4d1b8068bad70102c2cea0c65770ace`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `98bb5bbe` | `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT`; ingest + token serialize + PUT |
| 2 | `71c60385` | flatten extras; draft whitelist without KNOWN ∩; tracker persist bridge |
| 3 | `2fb7a993` | Experience persists only as `experience_detail` job array |

---

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1305
**Publish ref:** `origin/sub/AST-1299/AST-1305-hops-content-blobs-and-legacy-extra-labels` @ `59d6244ec909d0edf2ee79e1952470f68eebf804`
**Overall:** CLEAN

## Statutes checked

Ticket-scoped product delta: `98bb5bbe` + `71c60385` + `2fb7a993` (`src/utils/config.py`, `src/core/candidate.py`, `src/core/tracker.py`, `src/ui/api/api_candidate.py` modify). Formal three-dot `origin/dev...origin/sub` is epic-wide; predicates scored against ticket delta unless noted.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent module edits in ticket delta |
| astral.agent.do-task-delegation | scoped | conforms | split/flatten/validate paths `do_task` already calls; no new Anthropic assembly |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade paths in delta |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | conforms | `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` in config family; callers read constants |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no score-floor paths |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no env/secret wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch/seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run-next paths |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | engineer delta is `src/` only |
| astral.git.betty-no-src-or-features | scoped | not-applicable | engineer role statute |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits touch only planned `src/` files |
| astral.layers.core-vs-external-bright-line | scoped | conforms | core + thin api; no external imports |
| astral.layers.import-direction | scoped | conforms | core→utils; api→core; tracker→candidate (existing) |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts paths |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no frontend/TSX in delta (Joan excluded at plan) |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | existing `@require_auth` PUT/GET unchanged |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot paths |
| astral.seed.define-approved | scoped | not-applicable | no define paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migrations |
| astral.standards.debug-contract-gated | scoped | not-applicable | no new debug emission (Joan excluded at plan) |
| astral.standards.dry-and-focused-functions | scoped | conforms | single `ingest_legacy_label_content_base_resume` shared by token, PUT, whitelist |
| astral.standards.in-scope-only | scoped | conforms | planned files only; no builder/TSX/hop schema edits |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names (`ingest_legacy_label_content_base_resume`, etc.) |
| astral.standards.no-cross-contamination | scoped | conforms | explicit sibling boundaries respected |
| astral.standards.no-hardcoded-sets | scoped | conforms | KNOWN intersection removed; pattern/reserved ids from config |
| astral.standards.public-then-helpers | scoped | conforms | ingest public; slug/title helpers private |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | config delta does not import data |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job states |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend paths |
| astral.ui.naming-conventions | scoped | not-applicable | no UI paths |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `59d6244e` after merge-tests |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1305): …` engineer commits |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1299/…` publish |
| orch.git.ftr-sub-topology | universal | conforms | child under parent ftr; AST-1303 ancestor present |
| orch.git.merge-on-checkout | universal | conforms | prerequisite AST-1303 catalog on tree |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no destructive git in delta |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1299` |
| orch.git.three-permanent-branches | universal | conforms | standard sub topology |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | follows approved plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match binding steps |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to code shape |
| orch.pipeline.status-gates-skill-entry | universal | conforms | spawned at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | tests via Betty merge + `f27148fd` / `59d6244e` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | allowed paths |

**Count:** 65 active statutes scored.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` beside existing `RESUME_STRUCTURE_*` family |
| none other cited | — | Plan references config-block intent; no additional `canon/patterns/**` ids |

## Plan adherence

**Stage 1:** `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT = "bullet_list"`; `_slug_resume_extra_section_id` / `_title_to_structure_section_id`; public `ingest_legacy_label_content_base_resume` with dict/list paths, prose Experience omission, collision suffixes, final `normalize_resume_structure`; `format_base_resume_for_token` uses ingest (AC7 drop bug removed); PUT calls ingest after structure merge, recomputes enabled `section_ids`, then filters.

**Stage 2:** `_is_resume_content_section_id`; flatten promotes extras + job arrays on any sid; `draft_job_resume_allowed_section_keys` uses ingest (no `∩ KNOWN`); validate keeps unknown-key shape; tracker bridge + `_resume_section_has_body` / `_resume_payload_body` widened for any-key job arrays.

**Stage 3:** `filter_base_resume_to_structure`, `filter_content_to_resume_structure`, `split_craft_resume_base_payload` omit prose `experience`; draft validate rejects non-array Experience with `experience_detail` message.

**Boundaries:** `normalize_resume_structure` loop not rewritten (only called from ingest); no `builder.py`, TSX, hop schema, or `enabled_resume_structure_sections` contract changes. AST-1306 `slug_resume_section_id` / editor not on this publish ref (correct sibling split).

**Joan:** `[plan-rubric] revision=1` **APPROVED** — tracker bridge tension documented in plan Stage 2 §6; no straggler (excluded statutes remain n/a on this diff).

**C6 lenses:** Top-level imports; ui→core only; no silent failure, print, or debug additions; no hardcoded format/id sets in callers.

## Findings

(none — fix-now)

### advisory — Tracker bridge vs strict “enabled structure” wording
**Location:** `src/core/tracker.py` `_prepare_job_resume_content` (Stage 2 §6)
**Finding:** Re-injects base-whitelist keys dropped by enabled-only `filter_content_to_resume_structure` so Abrams extras persist before structure is saved — exactly as the approved plan documents. Joan flagged AC2 wording tension; implementation matches the binding decision.
**Recommendation:** No code change required on resolve; note for UAT that base-key ⊆ job persist is intentional until structure rows exist on disk.

### advisory — `filter_content` scalar-list coercion
**Location:** `src/core/candidate.py` `filter_content_to_resume_structure`
**Finding:** Stage 3 step text names job arrays + strings; implementation also coerces non-dict lists via `_coerce_resume_section_string` (tested in `TestAst1305HopsContentBlobsAndLegacyLabels`).
**Recommendation:** Optional plan-doc one-liner; behavior is consistent with legacy label content shapes.

### advisory — Ftr merge coordination
**Location:** `filter_content_to_resume_structure` (also touched by AST-1304 / AST-1306 on sibling branches)
**Finding:** Joan noted merge-order coordination on `origin/ftr/AST-1299`; this child’s hunk is plan-owned.
**Recommendation:** Chuckles/merge-child reconcile if siblings land overlapping lines — not a defect in this sub tip.

## What's solid

- AC7 fix: unmatched Abrams labels (`highlights`, `publications`) survive ingest and `{$BASE_RESUME}` token JSON.
- Extra hop keys accepted via `_is_resume_content_section_id` without reopening closed KNOWN catalog.
- Draft whitelist is per-candidate base keys post-ingest; unknown-key gate preserved.
- Prose Experience omitted on ingest/token/split/filter and rejected on draft validate.
- Single ingest function DRY across token, PUT, and whitelist paths.

## Notes

- Engineer product SHAs: `98bb5bbe`, `71c60385`, `2fb7a993`; publish tip `59d6244e` includes Betty merge-tests + `[qa-handoff]` manifest trim (`06ace6fe`).
- AST-1303 prerequisite satisfied on branch ancestry; `blockedBy AST-1303` relation met.

## Frame diff

(none) — Self-Assessment **Single-Component** matches four-file `src/` footprint.

context_tokens≈115000
— Radia

---
