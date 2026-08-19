<!-- linear-archive: AST-1304 archived 2026-08-19 -->

## Linear archive (AST-1304)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1304/builder-emit-by-section-format-support-alternative-resume-sections  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1299 — Support alternative resume sections  
**Blocked by / blocks / related:** parent: AST-1299

### Description

## What this implements

After #1: render enabled sections in structure order by format, reusing the existing Somerset treatments; Highlights and Publications print as `bullet_list`; `experience_detail` uses today’s job-array fields; html-style italic/bold in body text render; leftover prose Experience is not treated as the required Experience section. When `debug=True`, log id / title / format / emit outcome per section (Style D). Does not own hop schemas or the structure editor.

## Acceptance criteria

- [X] Adding Highlights as `bullet_list` and Publications as `bullet_list` (titles + bodies) prints those headings and bulleted lines in structure order.
- [X] Changing an optional section’s format changes the HTML treatment without creating a new section id.
- [X] Html-style italic and bold tags in a `bullet_list` body (and other body formats) render as italic and bold; other tags are not a raw HTML hole.
- [X] A leftover prose Experience string is not rendered as the required Experience section; Experience counts only as an `experience_detail` array (regenerate).
- [X] With `debug=True` on the builder, each enabled section logs id, title, format, and whether it emitted, under Style D headers and `|` detail.

## Boundaries

- [X] Does not own hop schemas (sibling AST-1305) or the structure editor (sibling AST-1306). After #1.
- [X] Does not change cover-letter shape or emit.
- [X] Does not edit `BUILD_CONFIG["supported_sections"]` or invent new visual styles beyond reusing Somerset list chrome for `bullet_list`.
- [X] Does not drop leftover Experience prose in `filter_content_to_resume_structure` (tracker persist / regenerate is AST-1305); builder emit skips it.
- [X] Does not slug titles or accept extra keys on craft/draft hops (AST-1305).

## In scope

- [X] `pattern.config.config-block` — consume `RESUME_STRUCTURE_BODY_FORMATS` / `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID` / `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES`; do not invent a second format table in the builder
- [X] `astral.config.config-source-of-truth` — format dispatch and emphasis allowlist read from the AST-1303 catalog in `src/utils/config.py`
- [X] `astral.standards.no-hardcoded-sets` — no inline `("i", "em", "b", "strong")` or six-format tuple in `builder.py`
- [X] `astral.standards.dry-and-focused-functions` — reuse existing Somerset emit helpers; add `_emit_bullet_list_html` / `_emit_inline_emphasis_html` only
- [X] `astral.standards.debug-contract-gated` — per-section Style D trail only when `debug=True`
- [X] `astral.standards.in-scope-only` — `src/core/builder.py` emit + `filter_content_to_resume_structure` keep-loop; no hops, editor, or cover letter
- [X] `astral.standards.public-then-helpers` — public builder signatures unchanged; new work is helpers
- [X] `astral.layers.import-direction` — builder adds config names only; filter change stays in core
- [X] `astral.layers.core-vs-external-bright-line` — HTML emit stays in core builder
- [X] `astral.standards.names-not-ticket-ids` — `_emit_inline_emphasis_html`, not `AST_1304_*`
- [X] `astral.standards.no-cross-contamination` — no hop/UI/cover files
- [X] `astral.standards.logging-via-utils` — existing `get_logger` / Style D helpers

## Considered but excluded

- [X] `astral.agent.do-task-delegation` — craft/draft hop accept of extra keys is AST-1305
- [X] `pattern.ui.admin-endpoint` / `astral.layers.ui-config-driven-business-logic` — format picker API + editor are AST-1306
- [X] `filter_base_resume_to_structure` / token serialize / legacy label ingest — AST-1305
- [X] `normalize_resume_structure` / `RESUME_STRUCTURE_*` catalog writes — AST-1303 (already shipped)
- [X] `astral.batch.claim-process-release` — no dispatch lifecycle
- [X] `astral.dispatch.run-next-is-chain-authority` — hop order unchanged
- [X] `astral.ui.single-gunicorn-worker` — `RAILWAY_CONFIG` untouched
- [X] `astral.state.*` / seed / consult idioms — builder does not transition entities or touch agent_task seeds
- [X] `BUILD_CONFIG["supported_sections"]` / `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` — not this child
- [X] `tests/`, `docs/test-bible/**` — Betty

## Notes for planning

Citations: `pattern.config.config-block`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`.

Plan: `docs/features/artifacts/ast-1304-builder-emit-by-section-format.md`

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1299-support-alternative-resume-sections`,
child `sub/AST-1299/AST-1304-builder-emit-by-section-format`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-11T07:08:32.668Z
[merge-child] blocked: duplicate merge-tests(AST-1304) count=3; also git pull / sibling Merge remote-tracking commits on the sub.

@Hedy Lamarr — rebuild `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` so `validate-sub-log` passes: exactly one `merge-tests(AST-1304)`, no `Merge remote-tracking branch` subjects, 1304-only plan/code/test/docs/resolve (do not merge sibling subs). Force-with-lease on this sub only — never origin/dev.

@Betty White — after Hedy’s tip is linear, one merge-tests delivery if the rebuilt stack still needs it.

— Chuckles

#### chuckles — 2026-08-11T07:02:19.036Z
[merge-child] blocked:

`validate-sub-log`: duplicate `merge-tests(AST-1304)` on sub — count=3 (amend on tests, one merge-tests only).

@Betty White — return-pass deliveries landed three `merge-tests(AST-1304)` (`143ba359`, `8398463c`, `1fb4ff0f`). Gate allows one. Child is User Testing; assignee stays Hedy. After hygiene, Chuckles re-runs merge-child.

Also missing `resolve(AST-1304):` — clean-review shortcut skipped resolve-child. Next validate will require that vocabulary commit (`docs(AST-1304): Radia review — clean` is present).

— Chuckles

#### radia — 2026-08-11T07:00:48.367Z
[code-rubric] revision=1
**Overall:** CLEAN
Format dispatch, bullet_list, emphasis allowlist, leftover Experience skip, filter widen, and Style D per-section trail match approved plan.
context_tokens≈115000
— Radia

#### betty — 2026-08-11T06:53:29.832Z
[check-linear]

- `test_candidate.py` no longer imports `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` at module level (AST-1305 catalog name). That import is inside `TestAst1305HopsContentBlobsAndLegacyLabels` only, so AST-1304 collection of this file works without the 1305 constant.
- Quote-entity assert kept: `html.escape` `&quot;`.
- Manifest unchanged.
- `origin/tests` `8f90dfdd` — `test(AST-1304): keep AST-1305 extra-format import off test_candidate module`
- `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `1fb4ff0f` (`merge-tests(AST-1304): origin/tests 8f90dfddf475163fb0c5baf775b9263623a5083e`)
- bible `docs/test-bible/core/builder.md` shasum `59faa635c09d437be64fd5fc592867f92db9b171`

```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1304BuilderEmitByFormat \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks \
  tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  tests/component/core/test_candidate.py::TestAst1304FilterContentToResumeStructure \
  tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection::test_filter_content_drops_orphan_and_empty_strings \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_filter_content_preserves_nonempty_job_array \
  tests/component/core/test_builder.py::TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only \
  -q
```

#### hedy — 2026-08-11T06:51:19.138Z
[qa-handoff]

@Betty White

Manifest (exact, from your `[check-linear]`):
```
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py::TestAst1304BuilderEmitByFormat tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume tests/component/core/test_builder.py::TestAst998ExperienceJobRender tests/component/core/test_candidate.py::TestAst1304FilterContentToResumeStructure tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection::test_filter_content_drops_orphan_and_empty_strings tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_filter_content_preserves_nonempty_job_array tests/component/core/test_builder.py::TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only -q
```

On `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `8398463c` (your `merge-tests` of `origin/tests` `2670b28d`): **collection error**, listed candidate nodes never run.

```
ImportError: cannot import name 'RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT' from 'src.utils.config'
tests/component/core/test_candidate.py:21
```

That name is **AST-1305** product (`docs/features/artifacts/ast-1305-hops-content-blobs-and-legacy-extra-labels.md` Stage 1). It is not on this child’s product tree and is out of AST-1304 scope (plan: builder emit + filter keep-loop only; no catalog writes).

`merge-tests(AST-1304)` of `origin/tests` `2670b28d` also brought `test(AST-1305)` (`f27148fd`, `06ace6fe`), which added the module-level import. That breaks **every** `test_candidate.py` node on AST-1304, including `TestAst1304FilterContentToResumeStructure`.

Please keep the `&quot;` helper assert, and either:
- merge-tests only the AST-1304 quote-entity commit onto this sub (do not land AST-1305 test imports here), or
- move `RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT` off the `test_candidate.py` module import (into AST-1305 classes only) so this file still collects on AST-1304 product.

Then re-post Tests Ready / reassign Hedy. I will not add the AST-1305 constant on this ticket.

#### betty — 2026-08-11T06:49:13.002Z
[check-linear]

- Fixed `TestAst1304BuilderEmitByFormat::test_emphasis_helper_restores_closed_tags_and_escapes_the_rest` — attributed `<i>` now expects CPython `html.escape` `&quot;`, not `&#34;`.
- Manifest unchanged (same class/node list). Bible `docs/test-bible/core/builder.md` notes the quote entity.
- `origin/tests` `2670b28d` — `test(AST-1304): expect html.escape quote entity on attributed emphasis tags`
- `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `8398463c` (`merge-tests(AST-1304): origin/tests 2670b28d38d17590bad1f8c3bf734dfebf95bd22`)
- bible `docs/test-bible/core/builder.md` shasum `a8b93207855c0248f9d4e9a7c63cd7965cef11f1`

```bash
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1304BuilderEmitByFormat \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks \
  tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume \
  tests/component/core/test_builder.py::TestAst998ExperienceJobRender \
  tests/component/core/test_candidate.py::TestAst1304FilterContentToResumeStructure \
  tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection::test_filter_content_drops_orphan_and_empty_strings \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_filter_content_preserves_nonempty_job_array \
  tests/component/core/test_builder.py::TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only \
  -q
```

#### hedy — 2026-08-11T06:47:22.479Z
[qa-handoff]

@Betty White

Manifest (exact):
```
ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py::TestAst1304BuilderEmitByFormat tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume tests/component/core/test_builder.py::TestAst998ExperienceJobRender tests/component/core/test_candidate.py::TestAst1304FilterContentToResumeStructure tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection::test_filter_content_drops_orphan_and_empty_strings tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_filter_content_preserves_nonempty_job_array tests/component/core/test_builder.py::TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only -q
```

Result on `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `785be890`: **1 failed, 32 passed**.

Failed node: `TestAst1304BuilderEmitByFormat.test_emphasis_helper_restores_closed_tags_and_escapes_the_rest`

```
assert fn('x <i onclick="x">nope</i> y') == "x &lt;i onclick=&#34;x&#34;&gt;nope&lt;/i&gt; y"
- x &lt;i onclick=&#34;x&#34;&gt;nope&lt;/i&gt; y
+ x &lt;i onclick=&quot;x&quot;&gt;nope&lt;/i&gt; y
```

This is a **test assertion** problem, not a product hole:

- Plan Stage 1: `html.escape` the slices. CPython `html.escape(..., quote=True)` emits `&quot;`, not `&#34;`.
- Attributed open + orphan `</i>` are both escaped (no raw tag). Session test `test_emphasis_tags_render_other_tags_escaped` is already green on that contract.
- Style D `skipped — missing format` walk is green after `test(AST-1304)` (`785be890`) — session emit keeps a structure when `normalize_resume_structure` rejects an extra that lacks `format`.

Please change the helper assert to expect `&quot;` (or compare decoded text). Do not require `&#34;`. Then re-post Tests Ready / reassign Hedy.

#### betty — 2026-08-11T06:40:42.016Z
1. `./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py::TestAst1304BuilderEmitByFormat tests/component/core/test_builder.py::TestBuilderHelpers::test_emits_body_sections_and_cover_blocks tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume tests/component/core/test_builder.py::TestAst998ExperienceJobRender tests/component/core/test_candidate.py::TestAst1304FilterContentToResumeStructure tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection::test_filter_content_drops_orphan_and_empty_strings tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_filter_content_preserves_nonempty_job_array tests/component/core/test_builder.py::TestAst581ResumeCoverSplit::test_build_cover_letter_from_job_emits_cover_only -q`

2. New: `TestAst1304BuilderEmitByFormat` — bullet_list Highlights/Publications in order; format swap keeps `id="education"`; emphasis tags render / other tags escaped; leftover Experience prose skipped; job array still emits; extra `experience_detail` + `_render_content_keys`; Style D per enabled section; `debug=False` quiet; cover debug has no resume-section trail.

3. New: `TestAst1304FilterContentToResumeStructure` — leftover Experience prose kept; extra job array kept; scalar list coerced; mixed dict-list dropped.

4. Revised (broken by emit-by-format): `TestBuilderHelpers::test_emits_body_sections_and_cover_blocks` (job array for Experience); `TestAst987BuildSessionBaseResume::test_renders_from_in_memory_payload_no_candidate_bind`; `TestAst998ExperienceJobRender::test_session_legacy_string_experience_still_prose`.

5. Bible: `docs/test-bible/core/builder.md` `### AST-1304 · AST-1299` — shasum `98541459644d19a28d467344fbb99ea42874c924` on `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format`.

`origin/tests` `6e51cf514c62ec45a09d4af1f96b5ae2a6051cd2`
`origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` `143ba359` (`merge-tests(AST-1304): origin/tests 6e51cf514c62ec45a09d4af1f96b5ae2a6051cd2`)

— Betty

#### joan — 2026-08-11T06:18:30.312Z
[plan-rubric] revision=1
**Overall:** APPROVED
2 discuss (non-blocking): AC numbering vs child checkboxes; filter persist vs AST-1305 hop ingest
context_tokens≈95000
— Joan

#### hedy — 2026-08-11T06:14:17.968Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1299/AST-1304-builder-emit-by-section-format/docs/features/artifacts/ast-1304-builder-emit-by-section-format.md

`origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `f51e905d`

**Scope:** Single-Component — resume HTML emit in `builder.py` plus the `filter_content_to_resume_structure` keep-loop so extra bodies reach that emit; no hops, editor, or cover letter.

**Conf:** high — AST-1303 already persisted `format` and the emphasis tag names; five of six treatments already exist as id-keyed branches; this ticket rekeys them and adds `bullet_list`.

**Risk:** Medium — a wrong format map regresses every printed resume; a loose emphasis restore would be an HTML hole; leftover Experience prose is skipped at emit only so tracker persist stays AST-1305.

---

# AST-1304 — Builder emit by section format

**Linear:** https://linear.app/astralcareermatch/issue/AST-1304/builder-emit-by-section-format  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections  
**Publish ref:** `sub/AST-1299/AST-1304-builder-emit-by-section-format`

After AST-1303: render enabled resume sections in structure order by each section’s `format`, reusing the existing Somerset HTML treatments. Highlights and Publications print as `bullet_list`. Required `experience` emits only as an `experience_detail` job array (leftover prose is not rendered). Html-style italic/bold tags in body text render; other tags are escaped. When `debug=True`, each enabled section logs id / title / format / emit outcome under Style D headers and `|` detail. Does **not** own hop schemas (**AST-1305**) or the structure editor (**AST-1306**). Does **not** change cover-letter emit.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Dispatch body emit by `format`; add `bullet_list` treatment; skip leftover prose Experience; restore allowlisted italic/bold in body text; Style D per-section trail when `debug=True`. | core |
| `src/core/candidate.py` | Widen `filter_content_to_resume_structure` so extra `experience_detail` job arrays and extra list-of-scalars bodies reach the builder. Do **not** drop leftover Experience prose here (builder emit skips it). | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `RESUME_STRUCTURE_*` catalog, `normalize_resume_structure`, emphasis tag **names** | AST-1303 (already on `origin/ftr/AST-1299-support-alternative-resume-sections`) |
| Craft/draft hop schemas, `_flatten_craft_resume_section_strings` KNOWN gate, `draft_job_resume_allowed_section_keys`, legacy label→extra slug, `filter_base_resume_to_structure` / token serialize | AST-1305 |
| Structure editor UI, format picker API, PUT overlay that can remove optionals | AST-1306 |
| `BUILD_CONFIG["supported_sections"]`, cover-letter HTML (`_emit_somerset_cover_html_document`, `_emit_cover_sections_html`) | out of this child |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 5–8 are AST-1305. Parent AC 3 (printed heading follows title) is already true: `_emit_body_sections_html` uses `resume_section_titles`; AST-1306 owns the editor that changes the title. Parent AC 1 (seven-only structure renders) is verified in Stage 1 — emit already walks enabled ids only.

| Child AC | Stage |
|----------|--------|
| 2 — Highlights + Publications as `bullet_list` print heading + bullets in structure order | 1 |
| 3 — changing an optional section’s format changes HTML treatment; id unchanged | 1 |
| 4 — italic/bold tags render; other tags are not a raw HTML hole | 1 |
| 5 — leftover prose Experience is not rendered as the required Experience section | 1 |
| 6 — `debug=True`: each enabled section logs id, title, format, emit outcome (Style D + `\|`) | 2 |

## Stage 1: Emit by format, bullet_list, emphasis, skip leftover prose

**Done when:** Calling `build_session_base_resume` (or `build_base_resume` / `build_resume_from_job`) with a normalized structure that is only the seven required ids plus enabled `highlights` / `publications` (`format` `bullet_list`) and a content blob whose `highlights` / `publications` values are newline-separated strings (or lists of scalar lines) produces HTML that contains those two `<h2>` titles in structure order, each followed by a `<ul>` of `<li>` lines. Changing `education_certifications` `format` from `indented_bold_single` to `bullet_list` on the same id emits `<ul><li>…` instead of `div.education-list`, and the section DOM id stays `education` (`_KEY_TO_SECTION_ID`). A `professional_summary` (or `bullet_list`) body containing `<i>…</i>` / `<em>…</em>` / `<b>…</b>` / `<strong>…</strong>` renders those tags; a body containing `<script>alert(1)</script>` or `<i onclick="x">` does not put a raw tag in the HTML (escaped). Required `experience` whose content is a non-empty prose string produces **no** Experience `<section>` (no `div.prose-block` fallback). Required `experience` that is a job array still emits `_emit_experience_jobs_html` as today. A seven-only structure (no optional keys) still emits header + the enabled body sections that have content. Cover-letter functions are unchanged. No new Style D per-section indexes yet.

1. In `src/core/builder.py`, extend the existing `from src.utils.config import` list (do not add a second config import) with:

   - `RESUME_STRUCTURE_BODY_FORMATS`
   - `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`
   - `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES`

   Keep `BUILD_CONFIG` and `RESUME_STRUCTURE_CONTACT_SECTION_IDS`.

2. Next to `_KEY_TO_HEADING`, add a module-level regex built from config (do not hardcode `i\|em\|b\|strong` in the pattern):

   ```python
   _EMPHASIS_TAG_RE = re.compile(
       r"</?(?:" + "|".join(re.escape(n) for n in RESUME_STRUCTURE_EMPHASIS_TAG_NAMES) + r")>",
       re.IGNORECASE,
   )
   ```

   Add helper `_emit_inline_emphasis_html(text: str) -> str` in the helpers section (with the other `_emit_*` functions, after `_resume_site_markers`):

   - If `text` is empty, return `""`.
   - Walk `_EMPHASIS_TAG_RE.finditer(text)`. For each match, `html.escape` the slice before the match; then emit a **lowercase** tag with no attributes: `</name>` if the match starts with `</`, else `<name>`, where `name` is `match.group(0).strip("</>").lower()`.
   - Escape the tail after the last match.
   - Tags with attributes, whitespace inside the brackets, or names not in `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES` do **not** match the regex and stay in the escaped text.

   ⚠️ **Decision:** Escape-then-restore via exact no-attribute tags (not a general HTML sanitizer). That is the closed italic/bold surface AST-1303 declared. `<I>` becomes `<i>`; `<i class="x">` stays escaped.

3. In `src/core/candidate.py`, rewrite **only** the value-keep loop inside `filter_content_to_resume_structure` (keep the `allowed` / `allow_contact` preamble). For each `key` in `allowed`:

   | `val` | Action |
   |-------|--------|
   | `is_experience_job_array(val)` and `val` nonempty | `out[key] = val` — **any** enabled id, not only `"experience"` |
   | `key == "experience"` and `val` is a nonempty stripped string | `out[key] = val` — leftover prose stays in the filtered dict so tracker persist (`_prepare_job_resume_content` / `persist_job_artifact_from_parsed`) does not silently drop it; **builder emit** skips it in step 7 |
   | any other key | if `val` is a nonempty stripped string → keep it; elif `val` is a nonempty list and **every** item is not a `dict` → set `out[key]` to `_coerce_resume_section_string(val)` when that returns a string; else drop |

   Do **not** change `filter_base_resume_to_structure`, `_flatten_craft_resume_section_strings`, `split_craft_resume_base_payload`, hop validators, or token serialize.

   ⚠️ **Decision:** Extra `experience_detail` job arrays must survive the filter or Stage 1 cannot emit them. Extra `bullet_list` list-of-scalars must coerce to a newline string or Highlights stored as a list never prints. Dropping Experience prose in this shared filter would change tracker persist — that regenerate is AST-1305.

4. In `src/core/builder.py`, add `_html_section_dom_id(sid: str) -> str` that returns `_KEY_TO_SECTION_ID[sid]` when present, else `sid.replace("_", "-")`. Use this everywhere `_emit_body_sections_html` currently does `_KEY_TO_SECTION_ID.get(key, key)`.

5. Add `_emit_bullet_list_html(text: str) -> str`:

   - Split `str(text)` on lines; skip blank/whitespace lines.
   - Each remaining line → `        <li>{_emit_inline_emphasis_html(line)}</li>`.
   - If no items, return `""`.
   - Else return `      <ul>\n` + joined items + `\n      </ul>`.

   Do **not** add a new CSS class. In the golden stylesheet inside `_emit_html_document`, change the existing selectors:

   - `.role ul` → `section ul, .role ul` (same declarations)
   - `.role li` → `section li, .role li` (same declarations)
   - `.role li:last-child` → `section li:last-child, .role li:last-child` (same declarations)

   ⚠️ **Decision:** Highlights bullets share Experience list chrome. That is reuse of the Somerset treatment, not a new visual language. Do not add `bullet-list` classes or new type-scale tokens.

6. Change `_emit_html_document` to take `resume_structure: Optional[dict] = None` (after `body_section_titles`). Pass it through to `_emit_body_sections_html`. Update the three resume callers (`build_resume_from_job`, `build_base_resume`, `build_session_base_resume`) to pass `resume_structure=structure`. Do **not** change cover-letter callers (they do not use `_emit_html_document`).

7. Rewrite `_emit_body_sections_html` to take `resume_structure: Optional[dict] = None` and dispatch **by format**, not by section id. Keep the `for key in ordered_ids` loop and the empty-skip behavior.

   Resolve format for each `key`:

   ```python
   spec = ((resume_structure or {}).get("sections") or {}).get(key) or {}
   fmt = spec.get("format") or RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID.get(key)
   ```

   If `fmt` is not in `RESUME_STRUCTURE_BODY_FORMATS`, skip the section (do not emit JSON / `prose-block`).

   Heading: `html.escape(titles.get(key, _KEY_TO_HEADING.get(key, key.replace("_", " ").title())))` — unchanged title source. DOM id: `_html_section_dom_id(key)`.

   Coerce non-array body content to a string the same way as today (`str(raw)` / `_format_experience_value` only when `raw` is `dict`/`list` **and** format is not `experience_detail` / not a job array). Prefer: if `raw` is a string, use it; if `raw` is a list of non-dicts, join with `"\n"` (filter step 3 already does this; keep the join here as defense if a caller skips the filter).

   | `fmt` | Emit (reuse existing helpers; do not fork a second visual language) |
   |-------|---------------------------------------------------------------------|
   | `free_prose` | Today’s `professional_summary` path: `_session_cover_letter_paragraphs` → `<p class="summary-intro">{_emit_inline_emphasis_html(p)}</p>` |
   | `bullet_list` | `_emit_bullet_list_html`; skip section if it returns `""` |
   | `word_cloud` | Today’s `core_competencies` / `prior_experience` path: `<p class="competencies-list">{_emit_inline_emphasis_html(text)}</p>` |
   | `dual_column` | `_emit_skills_grid_html` after switching that helper’s `html.escape` calls to `_emit_inline_emphasis_html`; skip if empty |
   | `indented_bold_single` | `_emit_education_list_html` after the same escape→emphasis swap; skip if empty |
   | `experience_detail` | If `candidate_mod.is_experience_job_array(raw)` and `_emit_experience_jobs_html(raw)` is nonempty → today’s role `<article>` block. **If `key == "experience"` and `raw` is not a job array → skip (no `div.prose-block`).** If `key != "experience"` and `raw` is not a job array → skip (do not `json.dumps`). |

   Delete the id-keyed `if key == "professional_summary"` / `education_certifications` / `technical_skills` / `core_competencies` / `experience` / `prior_experience` branches. Historical slugs keep today’s look because AST-1303 default formats match those treatments.

   In `_emit_experience_jobs_html`, replace `html.escape` on `title_text`, `loc_text`, `lead`, and `bullet` with `_emit_inline_emphasis_html`. Leave attribute/id escaping as `html.escape`.

   ⚠️ **Decision:** Required Experience has no prose render fallback (parent). Extra sections may use `experience_detail` and then must be a job array to print. Format, not id, chooses the treatment so AST-1306 format edits change HTML without minting a new id.

8. Update `_render_content_keys` so **any** nonempty job-array value (not only `markers["experience"]`) is included alongside nonempty strings.

9. Do **not** in this stage: add per-section `debug_index` calls; edit cover-letter emit; edit `BUILD_CONFIG["supported_sections"]`; remove the unused `emit_prior_experience` parameter; add `debug=` to `normalize_resume_structure`.

## Stage 2: Style D per-section emit trail

**Done when:** With `debug=True` on `build_session_base_resume` / `build_base_resume` / `build_resume_from_job`, after the existing document-level success `debug_index` (`index 1/1`), the log also has one Style D header per **enabled** section (`enabled_resume_section_ids` order) with universal `index N/M` (`M` = enabled count), `identifier` = section id, and `outcome` one of `emitted`, `skipped — empty`, `skipped — leftover prose`, `skipped — not job array`, `skipped — missing format`. Each header is followed by `|` detail `title=<repr> format=<repr>` (`format=None` for contact/header ids). With `debug=False`, none of these new lines appear. Existing document-level details (`resume_source`, `html_preview`, …) stay.

1. Add optional kwargs to `_emit_html_document` and `_emit_body_sections_html`: `debug: bool = False`, `debug_func: str = ""`. The three resume callers pass `debug=debug` and `debug_func` equal to that public function’s current `func=` string (`builder.build_resume_from_job`, `builder.build_base_resume`, `builder.build_session_base_resume`).

2. Inside `_emit_body_sections_html`, record per-id emit result while looping (`emitted` vs skip reason). After the loop, **only if** `debug` is True:

   - `_log.set_debug_flag(True)` is already set by the public caller; do not emit when `debug` is False.
   - `enabled = candidate_mod.enabled_resume_section_ids(resume_structure or {})`
   - `total = len(enabled)` (use `1` if empty so you never pass `total=0`)
   - For `i, sid` in `enumerate(enabled, start=1)`:
     - `spec` / `title` from structure; `fmt = spec.get("format")` (absent on contact ids → `None`)
     - Contact/header (`sid in RESUME_STRUCTURE_CONTACT_SECTION_IDS`): `outcome = "emitted"` if `str(render.get(sid) or "").strip()` else `"skipped — empty"`
     - Body id that appended a chunk: `"emitted"`
     - Body id skipped because leftover Experience prose: `"skipped — leftover prose"`
     - Body id skipped because `experience_detail` and not a job array (extras): `"skipped — not job array"`
     - Body id skipped because `fmt` not in `RESUME_STRUCTURE_BODY_FORMATS`: `"skipped — missing format"`
     - Else: `"skipped — empty"`
     - `_log.debug_index(func=debug_func or "builder._emit_body_sections_html", index=i, total=total, identifier=sid, outcome=outcome)`
     - `_log.debug_detail(f"title={title!r} format={fmt!r}")`

   Do **not** `debug_detail_block` the per-section HTML (the document-level `html_preview` already truncates the full document via `truncate_debug_content`).

3. Keep the existing document-level success/failure `debug_index` + details on the three public resume builders. Per-section indexes are **additional**. Do not add this trail to `build_cover_letter` / `build_cover_letter_from_job` / `build_session_cover_letter`.

⚠️ **Decision:** Per-section `debug_index` (Style D headers) rather than only `|` lines under the document header — parent AC names Style D headers with id / title / format / emit outcome. Contact ids are enabled sections and must appear in the `N/M` walk even though they are not body formats.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that does not exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits `code(AST-1304): …`, publishes to `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — resume HTML emit in `builder.py` plus the existing `filter_content_to_resume_structure` keep-loop so extra bodies reach that emit; no hops, no editor, no cover letter, no new config catalog.

**Conf:** `high` — AST-1303 already persisted `format` and `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES`; every treatment except `bullet_list` already exists as an id-keyed branch; this ticket rekeys those branches and adds one list helper.

**Risk:** `Medium` — a wrong format map would regress every printed resume; a loose emphasis restore would open an HTML hole; dropping Experience prose in the shared filter would change tracker persist (explicitly not done).

## Code Rules check

- §1.1 / `astral.standards.in-scope-only`: only builder emit + the filter keep-loop the emit needs. Hops, editor, cover letter, `BUILD_CONFIG["supported_sections"]` left to siblings / out of scope.
- §1.3 / `dry-and-focused-functions` / `public-then-helpers`: one format dispatch; reuse `_emit_education_list_html` / `_emit_skills_grid_html` / `_emit_experience_jobs_html` / `_session_cover_letter_paragraphs`; new helpers are `_emit_inline_emphasis_html`, `_emit_bullet_list_html`, `_html_section_dom_id`.
- §1.4 / `no-hardcoded-sets`: formats and emphasis tag names read from `RESUME_STRUCTURE_BODY_FORMATS` / `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES` / `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`; do not retype `("i", "em", "b", "strong")` or the six format strings in builder.
- §1.5.1 / `astral.standards.debug-contract-gated`: Stage 2 lines only when `debug=True`; Style D `index N/M`; `|` detail; no new lines when `debug=False`.
- §2.1 / `config-source-of-truth` / `pattern.config.config-block`: consume AST-1303 catalog; do not invent a parallel format table in builder.
- §2.4 / §2.6: not applicable (no batch / state machine).
- §3.3 / `import-direction`: builder already imports core + utils + data; new names are utils config only. `candidate.py` filter change stays in core.
- §3.5 naming: snake_case helpers; no new files; no `AST_1304_*` symbols.
- `astral.standards.names-not-ticket-ids`: helper names are domain (`_emit_inline_emphasis_html`), not ticket-prefixed.
- `astral.git.engineer-test-tree-ban`: no `tests/` or bible edits. Existing filter tests that assume extra lists / extra job arrays are dropped may fail — Betty owns that revision.

## Contract for siblings (non-goals)

- **AST-1305** accepts extra keys on craft/draft hops and regenerates leftover Experience prose in persisted blobs. This ticket only refuses to **print** leftover Experience prose.
- **AST-1306** lets operators change `format` / title. This ticket is why that change reprints with a different treatment and the same id.

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1304
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `f51e905d7cbb6176b09918ddc5b82b4af223e16e`

## Traceability
Child AC1→S1; AC2→S1; AC3→S1; AC4→S1; AC5→S2; parent AC1→S1; parent AC3→(titles unchanged); parent AC2/4/5/11→child AC1–5/S1–2; parent AC5–8→AST-1305

## Findings

### discuss — Traceability table uses parent AC numbers (2–6), not child checkbox order (1–5)
**Location:** Traceability (this child's AC only)
**Finding:** Child ticket lists five AC bullets without parent indices; plan maps parent AC2–6 / 11. Content aligns; numbering differs.
**Recommendation:** Non-blocking. Engineer may cross-reference child Description when implementing.

### discuss — `filter_content_to_resume_structure` widens persist path before AST-1305 hop ingest
**Location:** Stage 1 step 3; Contract for siblings
**Finding:** Filter keeps leftover Experience prose and extra list/job-array bodies so emit can run; hop acceptance of extra keys remains AST-1305. End-to-end Highlights/Publications from craft hops needs 1305 on the rollup line.
**Recommendation:** Non-blocking for this child — plan correctly scopes emit vs persist and names AST-1305 for regenerate.

— Joan
context_tokens≈95000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format`
**Tip:** `757f2cda6f7555191fa83a899a6ad9660f251ef9`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `6c6e7dd5` | emit by format, bullet_list, emphasis, skip leftover prose Experience |
| 2 | `757f2cda` | Style D per-section emit trail |

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1304
**Publish ref:** `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `1fb4ff0fd4a167fe68416d4a19af6cca225d2122`
**Overall:** CLEAN

## Statutes checked

Ticket-scoped product delta: `6c6e7dd5` + `757f2cda` (`src/core/builder.py`, `src/core/candidate.py` modify). Formal three-dot `origin/dev...origin/sub` is epic-wide (branch also carries merged AST-1303/1305/1306 ancestry); predicates scored against ticket delta unless noted.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths in ticket delta |
| astral.agent.do-task-delegation | scoped | conforms | emit/validate paths unchanged at call sites; no new Anthropic assembly |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | conforms | formats/emphasis from `RESUME_STRUCTURE_*` imports; no parallel catalog in builder |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no score-floor paths |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no env/secret wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch/seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run-next paths |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | engineer delta is `src/` only |
| astral.git.betty-no-src-or-features | scoped | not-applicable | engineer role statute |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits touch only planned `src/core/*` files |
| astral.layers.core-vs-external-bright-line | scoped | conforms | builder stays core; no new external imports |
| astral.layers.import-direction | scoped | conforms | builder → core/utils/data unchanged; candidate filter in core |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts paths |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI paths |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API paths |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot paths |
| astral.seed.define-approved | scoped | not-applicable | no define paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer edits |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migrations |
| astral.standards.debug-contract-gated | scoped | conforms | per-section `debug_index` + `\|` `debug_detail` only when `debug=True`; universal `index N/M`; cover letter untouched |
| astral.standards.dry-and-focused-functions | scoped | conforms | single format dispatch; reuses existing `_emit_*` helpers |
| astral.standards.in-scope-only | scoped | conforms | builder emit + filter keep-loop only; hops/editor/cover-letter schema untouched |
| astral.standards.logging-via-utils | scoped | conforms | `_log` contract helpers; no new `print` / raw loggers |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain helper names (`_emit_inline_emphasis_html`, etc.) |
| astral.standards.no-cross-contamination | scoped | conforms | no hop/editor/build_config edits in ticket commits |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | no hardcoded-set statute paths in ticket delta (formats/emphasis read from config) |
| astral.standards.public-then-helpers | scoped | conforms | new helpers private/module-level under existing public builders |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data change |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job states |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend |
| astral.ui.naming-conventions | scoped | not-applicable | no UI |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `1fb4ff0f` after `merge-tests` |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1304): …` engineer commits |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1299/…` publish |
| orch.git.ftr-sub-topology | universal | conforms | child under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | ftr + sibling sub merges documented on branch |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no destructive git in delta |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1299` |
| orch.git.three-permanent-branches | universal | conforms | standard sub topology |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | follows approved plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match binding steps |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to code shape |
| orch.pipeline.status-gates-skill-entry | universal | conforms | spawned at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | tests via Betty merge + manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | allowed paths |

**Count:** 65 active statutes scored.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan references `pattern.config.config-block` intent via Code Rules; no `canon/patterns/**` id in Architectural definition |

## Plan adherence

**Stage 1:** Config imports added; `_EMPHASIS_TAG_RE` + `_emit_inline_emphasis_html` built from `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES`; `_emit_bullet_list_html` + `section ul/li` stylesheet selectors; `_html_section_dom_id`; `_emit_body_sections_html` dispatches by `format` with leftover Experience prose skip and extra `experience_detail` job-array path; `_emit_html_document` + three resume callers pass `resume_structure`; education/skills/experience job text uses emphasis helper; `_render_content_keys` includes any nonempty job array; `filter_content_to_resume_structure` widened per plan table (extra job arrays, leftover Experience prose kept for persist, scalar-list coerce).

**Stage 2:** `debug` / `debug_func` threaded through `_emit_html_document` → `_emit_body_sections_html`; per-enabled-section Style D trail with planned outcomes; document-level success indexes preserved on public builders; cover-letter path still uses `_emit_somerset_cover_html_document` (no per-section trail).

**Joan:** `[plan-rubric] revision=1` **APPROVED** — Excluded `debug-contract-gated` at plan time is satisfied on touched builder paths; filter/persist vs AST-1305 regenerate tension is plan-documented (non-blocking).

**Cross-ticket:** No hop schema, editor, or `BUILD_CONFIG["supported_sections"]` edits in ticket commits. Sibling merges on branch do not expand AST-1304 product footprint beyond the two planned files.

**C6 lenses:** No silent failure, layer violations, UI hardcoding, or external cleanliness issues on touched paths. §5f debug contract satisfied on Stage 2 trail.

## Findings

(none)

## What's solid

- Format-driven dispatch preserves historical Somerset treatments via AST-1303 default map; `bullet_list` is the only new visual helper.
- Closed emphasis surface: escape-then-restore exact no-attribute tags; attributed/script tags stay escaped.
- Leftover Experience prose skipped at emit while filter keeps it for tracker persist — matches explicit plan decision vs AST-1305 regenerate.
- Betty manifest `TestAst1304BuilderEmitByFormat` + `TestAst1304FilterContentToResumeStructure` cover highlights/publications, format swap, emphasis safety, prose skip, extra job arrays, and Style D outcomes.

## Notes

- Publish tip `1fb4ff0f` includes `merge-tests` after engineer product SHA `757f2cda`.
- Branch ancestry merges AST-1305/1306 for rollup; ticket-scoped review uses isolated `6c6e7dd5^..757f2cda` diff.
- Joan discuss on filter widening vs hop ingest is plan-approved; no action required on this child.

## Frame diff

(none) — Self-Assessment **Single-Component** matches the two-file `builder.py` + filter keep-loop footprint.

context_tokens≈115000
— Radia

## Resolution

2026-08-11 — Radia `[code-rubric] revision=1` **CLEAN**. No fix-now. No product change on resolve.

- **advisory (sibling ancestry):** publish ref rebuilt onto `origin/ftr` — AST-1304 commits only; no `Merge remote-tracking branch`; one `merge-tests(AST-1304)`.
- **advisory (filter vs AST-1305):** leftover Experience prose stays in `filter_content_to_resume_structure` per this plan; emit still skips it.

Publish intake: `1e842153` (`docs(AST-1304): Radia review — clean`).

