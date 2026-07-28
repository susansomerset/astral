# Nested typography markers on render (Resume Render Format discrepancies)

**Linear:** [AST-1007](https://linear.app/astralcareermatch/issue/AST-1007/nested-typography-markers-on-render-resume-render-format-discrepancies)
**Parent:** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-993/AST-1007-nested-typography-markers-on-render`

Shared resume HTML builders already run `_apply_resume_text_markers` before emit, but that helper only transforms **top-level** string values. Nested string leaves — especially AST-994/998 experience job-array fields (`company`, `title`, `dates`, `location`, `accomplishments`) and any list/dict nests under other render keys — stay unmarked in the markers dict. Parent AC2 requires `__` → NBSP (`\u00a0`), `~~` → non-breaking hyphen (`\u2011`), and `" • "` → `\u00a0• ` through those nested strings on session, base, and job-tailored HTML, with fixture-driven proof that literal `__` / `~~` are gone from the rendered body sections this ticket owns. This plan deepens the existing markers pass only — it does **not** own role/education/skills layout chrome (AST-1008 / AST-1009 / AST-1010) or re-parse experience job arrays (AST-994).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Deep-walk `_apply_resume_text_markers` over dict/list nests; apply `_resume_site_markers` to every string leaf; keep emit-time experience markers (idempotent); no layout/CSS/emit-structure changes | core |

**Out of scope (do not touch):** `_emit_experience_jobs_html` role chrome / lead-vs-bullets (AST-1008); education line / skills category grid / prior-list markup (AST-1009); header `Name • Title` composition, meta description, embedded stylesheet expansion (AST-1010); cover-letter body marker policy; `candidate.py` parse / job-array contract; `config.py` marker literals (leave `_resume_site_markers` transforms as-is); `tests/`, bible (Betty).

## Marker contract (existing — do not redefine)

`_resume_site_markers(text)` in `src/core/builder.py` already implements:

1. `__` → `\u00a0` (NBSP)
2. `~~` → `\u2011` (non-breaking hyphen)
3. `" • "` → `"\u00a0• "` (legacy bullet spacing)

Do **not** change these three substitutions, add new marker pairs, or move them into `BUILD_CONFIG` in this ticket.

## Stage 1: Deep-walk `_apply_resume_text_markers`

**Done when:** Calling `_apply_resume_text_markers` on a render dict that contains (a) top-level strings with `__` / `~~` / `" • "` and (b) an AST-996 experience job array whose nested string fields also contain those markers returns a new structure where **every** string leaf has been passed through `_resume_site_markers`, with no literal `__` or `~~` remaining in those leaves; non-string leaves and empty strings behave as today; `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` still call this helper once before `_emit_html_document` (no new call sites).

1. In `src/core/builder.py`, replace the body of `_apply_resume_text_markers(render: dict) -> dict` so it returns a **new** top-level dict (same keys as `render`) whose values are produced by a private recursive helper (name it `_mark_resume_value` or similar, defined immediately below `_apply_resume_text_markers` in the helpers section):
   - **`str`:** return `_resume_site_markers(v)`.
   - **`dict`:** return `{k: recurse(v) for k, v in obj.items()}` (new dict; do not mutate the input).
   - **`list` / `tuple`:** return a new `list` of `recurse(item)` for each item (preserve list type in the output even if input was a tuple).
   - **Anything else** (`None`, `bool`, `int`, unexpected objects): return unchanged.
2. Update the docstring of `_apply_resume_text_markers` from “shallow copy” to state that it deep-walks dict/list nests and applies `_resume_site_markers` to every string leaf.
3. Do **not** change `_resume_site_markers` itself.
4. Do **not** remove or alter the existing `_resume_site_markers(...)` calls inside `_emit_experience_jobs_html` (AST-998). Double application is idempotent for the three substitutions above; leave them as defense-in-depth for direct helper calls.
   ⚠️ **Decision:** Single authoritative transform for the shared render dict is the deep `_apply_resume_text_markers` pass used by all three resume HTML surfaces; emit-time markers on experience fields stay. Do not invent a second marker vocabulary or a config block for marker pairs.
5. Do **not** change `_emit_body_sections_html`, `_emit_html_document` CSS, header/contact join chrome, education/skills markup, or cover-letter emit.
6. Do **not** edit `tests/` or bible — Betty owns fixture assertions after Code Complete.

## Stage 2: Fixture-driven proof on all three surfaces (manual / build verification)

**Done when:** With a minimal in-memory render (or session paste content) that plants `__` / `~~` / `" • "` in `candidate_name` or `candidate_title`, `candidate_contact_detail` (or profile-derived contact), `core_competencies`, at least one experience job’s `company`/`title`/`accomplishments`, `prior_experience`, and `technical_skills`, each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` produces HTML whose corresponding visible text contains `\u00a0` / `\u2011` (or the escaped/HTML-equivalent forms after `html.escape`) and does **not** contain the literal two-character sequences `__` or `~~` in those sections’ body text. Layout classes (`.role`, skills grid, education lines, meta description) are **not** asserted here — siblings own those.

1. During **build-child**, verify Stage 1 by exercising the three public builders with marker-laden nested content (REPL, ad-hoc script under `debug/spikes/AST-1007/`, or temporary local calls — **do not** commit spike output; **do not** add files under repo-root `artifacts/`). Prefer content shaped like the parent AST-993 paste fixture’s marker substrings (e.g. `Fractional__TPM`, `AI~~Assisted__Delivery`, `Somerset__Consulting`, `sprint~~level`, `Jira__•__Confluence`) rather than inventing a new marker dialect.
2. Confirm HTML source for those sections has no leftover literal `__` / `~~` in the escaped text nodes for header/title, contact, competencies, experience job strings, prior experience, and skills (string section path as today).
3. If deep-walk changes break an assumption documented in this plan (e.g. a non-string leaf that must not be copied), **stop**, comment on the **parent** AST-993 with the Stage blocked template, and wait — do not improvise.

## Self-Assessment

**Scope:** `Single-Component` — one core helper in `src/core/builder.py` (deep-walk of the existing markers pass); no UI, config, or parse-layer files.

**Conf:** `high` — `_resume_site_markers` and the three-surface call sites already exist; AST-998 already applies markers at experience emit; the gap is shallow vs deep walk, which is a localized recursion change with idempotent overlap.

**Risk:** `Medium` — wrong recursion (mutating inputs, walking non-render blobs, skipping list leaves) could leave markers literal or double-transform unexpected values; impact is typography in resume HTML across session/base/job surfaces, not dispatch or DB state.

## Code rules check

- §1.3 DRY: one deep markers pass for the render dict; reuse existing `_resume_site_markers`; leave emit-time experience calls (idempotent) rather than forking a second transform.
- §1.1 / scope isolation: only `builder.py` markers helper; no sibling layout chrome.
- §2.1: no new config keys; marker literals stay in the existing helper (grandfathered with AST-998).
- §2.4 / §2.6: N/A (no batch/state-machine work).
- §3.3: core-only change; no new imports across layers.
- §3.5 naming: private helper `_mark_resume_value` (or equivalent) beside `_apply_resume_text_markers`.
- §3.6: spike/debug under `debug/spikes/AST-1007/` only if used; never commit spike dumps.
