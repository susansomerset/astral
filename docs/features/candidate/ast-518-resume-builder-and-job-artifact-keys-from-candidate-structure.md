# AST-518 — Resume builder and job artifact keys from candidate structure

**Linear:** [AST-518](https://linear.app/astralcareermatch/issue/AST-518/resume-builder-and-job-artifact-keys-from-candidate-structure)  
**Parent:** [AST-477](https://linear.app/astralcareermatch/issue/AST-477/candidate-resume-structure) — Candidate Resume Structure  
**Blocked by:** [AST-517](https://linear.app/astralcareermatch/issue/AST-517/per-candidate-resume-structure-storage-and-craft-resume-base-candidate) (must land `resolve_resume_structure` + blob shape first)  
**Publish ref:** `origin/sub/AST-477/AST-518-resume-builder-and-job-artifact-keys-from-candidate-structure`  
**Project:** Astral Candidate

## Summary

Make `src/core/builder.py` and job artifact persistence consume each candidate's **`artifacts.resume_structure`** catalog (section order, titles, enabled flags, accent on structure) instead of hardcoded `_RESUME_BODY_KEYS` / global `BUILD_CONFIG["artifact_shapes"]["resume_content"]` key lists. Job `resume_content` keys must be a **subset** of the candidate's enabled section ids; orphan keys are stripped on save and omitted at render. Contact/header sections remain on structure with snapshots on job artifacts per AST-477 Q4. Cover letter storage accepts canonical **`Subject`** / **`Letter`** keys with backward-compatible read of legacy `re_line` / `body`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Structure-driven section order/titles; accent from `resume_structure`; filter render dict to catalog. | core |
| `src/core/candidate.py` | Import-safe helpers: ordered enabled ids, title map, filter content dict to structure (reuse AST-517 resolve). | core |
| `src/core/tracker.py` | Filter `resume_content` before save; cover letter normalize accepts Subject/Letter aliases. | core |
| `src/utils/config.py` | Comment + optional `artifact_shapes["cover_letter"]` alias docs; no new hardcoded section order lists. | utils |

**Out of scope:** Structure persistence and `craft_resume_base` (AST-517), Base Resume Content UI (AST-519), AST-300 daisy-chain orchestration, prompt rewrites in Manage Tasks (document only).

## Stage 1: Shared structure projection helpers

**Done when:** Given `candidate_data`, helpers return deterministic ordered section ids and title map; disabled sections excluded; contact sections included when enabled.

1. In `src/core/candidate.py` (AST-517 must have landed first), add:
   - `enabled_resume_section_ids(resume_structure: dict) -> list[str]` — sort `sections` values by `order` ascending, return ids where `enabled` is true.
   - `resume_section_titles(resume_structure: dict) -> dict[str, str]` — map id → `title` for enabled sections.
   - `filter_content_to_resume_structure(content: dict, resume_structure: dict, *, allow_contact: bool = True) -> dict` — keep only keys in enabled ids; when `allow_contact` false, drop ids in `RESUME_STRUCTURE_CONTACT_SECTION_IDS` (for job-agent slices); string values only; omit empty strings.
2. `resolve_resume_structure(candidate_data)` from AST-517 is the single entry — do not duplicate default logic in builder/tracker.

## Stage 2: Builder — style, headers, body emission

**Done when:** `build_base_resume` and `build_resume_from_job` render sections in candidate catalog order with catalog titles; disabled sections absent; accent from structure with legacy fallback.

1. In `src/core/builder.py`, update `_merge_effective_style(candidate_data)`:
   - Read `accent_color` from `resolve_resume_structure(candidate_data)` first.
   - If missing, fall back to `artifacts.base_resume.accent_color` (legacy AST-297 path).
2. Replace module-level `_RESUME_BODY_KEYS`, `_KEY_TO_HEADING` **usage** in emission (constants may remain temporarily for tests but must not drive order):
   - Add `_structure_ordered_body_ids(resume_structure) -> list[str]` returning enabled ids excluding contact trio (those render in header block today).
   - Add `_emit_body_sections_html(render, ordered_ids, titles) -> str` — iterate `ordered_ids`; skip empty content; use `titles.get(id, id.replace("_"," ").title())` for `<h2>` text; preserve existing per-key HTML templates (`professional_summary` multi-para, `core_competencies` class, etc.) keyed by section id.
3. In `build_resume_from_job` / `build_base_resume`, after `_resolve_resume_sections` / base_resume load:
   - `structure = candidate_mod.resolve_resume_structure(cd)`
   - `render = filter_content_to_resume_structure(render, structure)` (job path: filter job/base merged dict).
   - Pass ordered ids + titles into `_emit_body_sections_html`.
4. Keep `_apply_profile_to_render_dict` behavior for live profile overwrite of contact fields on **render** dict; job `resume_content` snapshot still stored on job row when job agents persist (Stage 3).

⚠️ **Decision:** Header HTML (`candidate_name`, `candidate_title`, `candidate_contact_detail`) continues to use the top-of-page template; only **body** sections move to structure-ordered emission. Contact fields remain in structure catalog for id/title/enabled consistency.

## Stage 3: Job artifact key filtering and contact snapshot

**Done when:** Saving job `resume_content` drops keys not in candidate catalog; job agents cannot persist edits to contact sections via parsed task output; contact snapshot copied from base/job render source at persist time.

1. In `src/core/tracker.py`, update `save_job_artifact_resume_content(astral_job_id, resume_content)`:
   - Load job → company → candidate; `structure = resolve_resume_structure(candidate_data)`.
   - Filter with `filter_content_to_resume_structure(resume_content, structure, allow_contact=False)` for agent-editable keys only.
   - Build contact snapshot dict for ids in `RESUME_STRUCTURE_CONTACT_SECTION_IDS` that are enabled: prefer values from incoming `resume_content`, else from `artifacts.base_resume`, else empty string.
   - Merge snapshot into filtered dict; save merged result.
2. Update `slice_parsed_for_artifact_shape(parsed, "resume_content")` caller path in `persist_job_artifact_from_parsed` to run the same filter+snapshot pipeline (extract helper `_prepare_job_resume_content(resume_content, candidate_data) -> dict` in `tracker.py` to avoid duplication).
3. Update `BUILD_CONFIG["artifact_shapes"]["resume_content"]` comment only: shape documents **superset of known ids**; runtime allowed keys are per-candidate structure subset. Do **not** remove static shape keys (downstream docs reference them).

## Stage 4: Cover letter Subject / Letter alias (read + persist)

**Done when:** Job cover letter dict accepts `Subject`/`Letter` or legacy `re_line`/`body`; builder `_resolve_cover_letter` and `normalize_cover_letter_artifact` emit canonical stored form.

1. In `tracker.normalize_cover_letter_artifact`, map incoming keys:
   - `Subject` or `re_line` → stored `Subject` (string)
   - `Letter` or `body` → stored `Letter` (string)
   - `signature` unchanged optional
   - Return dict with keys **`Subject`**, **`Letter`**, **`signature`** (all strings).
2. In `builder._resolve_cover_letter` and `_cover_letter_nonempty`, accept either naming on read; normalize to internal `{re_line, body, signature}` **only inside builder** for existing `_emit_cover_sections_html` OR update cover emit to read `Subject`/`Letter` — pick one path in implementation, but stored job JSON uses `Subject`/`Letter`.
3. Update `BUILD_CONFIG["artifact_shapes"]["cover_letter"]` to list `Subject` and `Letter` as required string fields; keep comment that legacy tasks may still output `re_line`/`body` until prompts updated.
4. Update `parsed_matches_artifact_shape` for `cover_letter` to return true if either naming convention satisfies required fields (implement in tracker helper, not agent.py).

⚠️ **Decision:** Do **not** change `TASK_CONFIG["draft_cover_letter"]` prompts in this ticket — normalization shims only. Prompt/key migration is a follow-up Manage Tasks change.

## Stage 5: Verify builder against acceptance criterion 3

**Done when:** Manual or existing builder smoke (if present): candidate A structure with three enabled body sections → job `resume_content` with extra key `orphan_section` stripped on save; builder HTML shows no orphan heading; candidate B catalog unchanged.

1. Grep repo for tests touching `build_base_resume` / `persist_job_artifact_from_parsed`; extend closest existing test file if one exists, else manual checklist in Linear comment only (no new test module unless Betty adds in qa pass).

## Self-Assessment

**Scope — `Single-Component`**  
Primary surface is `builder.py` with small tracker/candidate helper wiring; no React changes.

**Conf — `Medium`**  
Depends on AST-517 blob shape; cover letter dual-key shim needs careful read paths.

**Risk — `Medium`**  
Wrong filtering would drop valid resume sections or show stale headings in PDF/HTML output.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | Single `_prepare_job_resume_content`; structure resolve only in candidate.py. |
| §1.4 | No new hardcoded section order in builder; orders from structure. |
| §2.1 Config | Static artifact shape docs remain in config; runtime subset from structure. |
| §2.4 Batch | Tracker save hooks only; no claim/batch changes. |
| §2.6 State machine | N/A. |
| §3.3 Imports | builder → candidate, tracker → candidate; no ui/external. |
| §3.5 Naming | snake_case helpers. |

**Conflicts:** `artifact_shapes["resume_content"]` static key list vs per-candidate subset — mitigated by comments + runtime filter (documented in Stage 3).

## Review

| Field | Value |
|-------|-------|
| Branch | `origin/sub/AST-477/AST-518-resume-builder-and-job-artifact-keys-from-candidate-structure` |
| Status | Review Posted — Radia 2026-05-28 |

## Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — builder/tracker filtering, cover Subject/Letter shims, and AC #3 on publish ref @ `047ae6e5`. |
| **discuss** — inherited orphan tests (AST-517 merge) | Same defer as **AST-517** — Betty / prep-uat before parent merge; manifest uses `TestAst518*` / revised AST-302/309 only. |
| **discuss** — static `artifact_shapes.resume_content` vs runtime subset | Documented in plan Stage 3; job-craft prompt alignment deferred to parent **AST-477** / Manage Tasks — not blocking. |
| **advisory** — empty contact snapshot strings | Accepted; historical job resume HTML contract per plan. |

**Publish ref:** `origin/sub/AST-477/AST-518-resume-builder-and-job-artifact-keys-from-candidate-structure` · Betty manifest green · §9a clean (dev + parent ftr).

## Execution contract

- Requires AST-517 merged to `dev-ada` before Stage 1 implementation begins; if `resolve_resume_structure` missing at build time, **stop** with Linear comment on AST-518.
- Do not implement AST-519 admin/UI endpoints.
- Blocking ambiguity on cover HTML template field names after Stage 4 — comment on AST-477 with options: (a) builder internal map only, (b) rename emit templates to Subject/Letter.
