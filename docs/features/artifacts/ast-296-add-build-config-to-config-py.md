<!-- linear-archive: AST-296 archived 2026-06-03 -->

## Linear archive (AST-296)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-296/add-build-config-to-configpy  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-309; blocks: AST-300; blocks: AST-297

### Description

Add BUILD_CONFIG block to src/utils/config.py. Contains: default_style (full v07 design system: font stacks, sizes, weights, line heights, spacing, decorative h2 flanking-rule treatment, print rules — single source of truth for all render styling); supported_sections (array of known section types with formatting rules: summary, experience, competencies, education, skills, prior_experience, cover letter blocks — door left open for future types like publications_articles); artifact_shapes (expected JSON structure for resume_content and cover_letter artifacts — defines the contract between agent output and builder input). Candidate-level style overrides (accent_color, any default_style overrides) stored in candidate_data.artifacts.base_resume and merged over BUILD_CONFIG.default_style at render time.

### Comments

#### radia — 2026-05-18T18:57:42.147Z
@Susan — belated thread reply from Radia (this @ mention predates my Linear MCP identity posting as **Radia Perlman**).

**Review did run** same day (2026-04-29): combined doc on the feature branch, **0 fix-now**, merged to **`dev`** via PR #122 (`658b3d9c`). Findings are in `docs/features/artifacts/ast-296-add-build-config-to-config-py.md` on **`dev`**.

Nothing further needed from me unless you want a fresh pass on current **`origin/dev`** — ticket is **Done**.

— Radia

#### susan — 2026-04-29T20:13:19.418Z
**Merged to `dev`** — squash merge commit `658b3d9c870b7dd24b5d1626c13d1c6c261e710e`.

- **PR:** https://github.com/susansomerset/astral/pull/122 (base **`dev`**; replaces closed PR #121 which targeted `main`)
- **Combined doc on `dev`:** `docs/features/artifacts/ast-296-add-build-config-to-config-py.md`
- **Remote feature branch** `chuckles/ast-296-add-build_config-to-configpy` deleted after attachment refresh.

— Ada (e-push-linear)

#### susan — 2026-04-29T19:59:45.229Z
Review feedback resolved. Branch `chuckles/ast-296-add-build_config-to-configpy` is ready for testing. Commit: `300fca6d1e76add3b7227682b35648f1ca108e98`

— Ada

#### susan — 2026-04-29T19:56:18.151Z
**Review posted — Radia**

Summary: **0** fix-now, **1** discuss, **1** advisory (see combined doc for tables and rule citations).

Handoff: owner label back to **Ada** per thread (implementer sign-off). Conf / Risk / Scope unchanged.

**Review doc (feature branch @ commit with latest review header + findings):**  
https://github.com/susansomerset/astral/blob/14c138ff1fed2534c0266722bd287804d1210649/docs/features/artifacts/ast-296-add-build-config-to-config-py.md

— Radia

#### susan — 2026-04-29T19:05:44.485Z
**@Radia — implementer: Ada.** I shipped this build (BUILD_CONFIG in `config.py`). Label is on you for review; branch/commits below.

- **Branch:** `chuckles/ast-296-add-build_config-to-configpy`
- **Implementation commit:** `a8a01849b0d6beab74d2025ab265075d6e444298`
- **Doc stub:** `5e68d55` (review section in the combined plan doc)
- **Latest tip (small fix after stub):** `2fb8898`

— Ada

#### susan — 2026-04-29T19:03:50.784Z
**Branch tip (post-nit):** `2fb8898` — `supported_sections["candidate_name"].heading_level` now points at `candidate_name_line` to match `default_style.type_scale` keys.

— Ada

#### susan — 2026-04-29T19:03:25.790Z
**Build handoff (Code Complete)**

- **Branch:** `chuckles/ast-296-add-build_config-to-configpy`
- **Implementation commit:** `a8a01849b0d6beab74d2025ab265075d6e444298` (`BUILD_CONFIG` in `src/utils/config.py`)
- **Doc stub commit:** `5e68d55` (review section in combined plan doc)

— Ada

#### susan — 2026-04-29T19:00:40.235Z
Label review: agree on all three.

— Ada

#### susan — 2026-04-29T18:56:40.255Z
No need to update the plan document, but a smoke test is not necessary for this change.  If issues come up, we will address them downstream.

#### susan — 2026-04-29T03:39:55.048Z
**Plan ready** (a-plan-linear)

**Doc:** `docs/features/artifacts/ast-296-add-build-config-to-config-py.md` (on `dev` and on branch `chuckles/ast-296-add-build_config-to-configpy`; Linear attachment uses the same blob URL).

**Self-assessment**
- **Scope — Single-Component:** Only `src/utils/config.py` (plus optional tiny test); all changes stay in the utils config layer with no runtime wiring.
- **Conf — Medium:** Adding the block is straightforward, but v07 completeness and aligning `artifact_shapes` with AST-309 / `craft_resume_base` need a deliberate pass during implementation.
- **Risk — Medium:** Bad shapes or section IDs would confuse or break builder and artifact pipelines once they read BUILD_CONFIG; scope stays artifacts-only.

**ASTRAL_CODE_RULES self-review:** §1.3 DRY (single block, align IDs with DATA_SHAPES/tasks), §2.1 config literals, §2.4/§2.6 N/A, §3.3 utils-only, §3.5 naming — no blocking conflicts.

---

# AST-296 — Add BUILD_CONFIG to config.py

**Linear:** [AST-296](https://linear.app/astralcareermatch/issue/AST-296/add-build-config-to-configpy) — Add BUILD_CONFIG to config.py  
**Project:** Astral Artifacts  
**Priority / estimate:** High / 3 points  
**Parent / blocked-by:** None

## Goal

Introduce a `BUILD_CONFIG` block in `src/utils/config.py` as the single source of truth for artifact rendering: default CSS/design tokens (v07 system), supported resume/cover sections and their formatting rules, and the JSON contracts (`artifact_shapes`) for `resume_content` and `cover_letter` consumed by the builder and agent pipelines. Per the ticket, candidate-level overrides (`accent_color`, partial `default_style` overrides) live in `candidate_data.artifacts.base_resume` and are merged over `BUILD_CONFIG["default_style"]` at render time — **merge implementation is out of scope for this ticket** (covered by builder work and AST-297); this ticket only defines the base config shape others will merge against.

## Numbered steps

1. **Module header** — Add `BUILD_CONFIG` to the docstring list at the top of `config.py` (same style as `NAV_CONFIG`, `DATA_SHAPES`, etc.) so discoverability matches the rest of the file.

2. **`default_style`** — Add a nested dict under `BUILD_CONFIG["default_style"]` capturing the v07 design system as **named literals**: font stacks, type scale (sizes/weights/line-heights), spacing scale, colors used by the template (including any default accent reserved for “no candidate override”), decorative h2 / flanking-rule treatment, and print `@media` oriented rules expressed as structured keys (e.g. print margins, page-break hints) that `builder.py` (or a Jinja/CSS generator) can map to output later — **no magic numbers** outside this tree; use nested dicts with clear key names per §1.4 / §2.1. If the full v07 spec lives outside the repo, add a short comment pointing to it and land the complete key structure with sensible defaults so follow-up tickets only tune values.

3. **`supported_sections`** — Register known section types and formatting metadata (e.g. heading level, list vs prose, optional page-break policy) using **stable string IDs as dict keys** (e.g. `summary`, `experience`, `competencies`, `education`, `skills`, `prior_experience`, plus cover-letter logical blocks), not anonymous list items — matches the project rule for ID-keyed collections. Leave room for future keys (e.g. `publications_articles`) without implementing them. **Flag:** align ID names with `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]` keys and `TASK_CONFIG["craft_resume_base"]["response_schema"]` where they describe the same slice of resume content, so agents, UI, and builder do not diverge (rename only if a separate normalization ticket agrees).

4. **`artifact_shapes`** — Define the expected JSON shapes for per-job artifacts (at minimum `resume_content` and `cover_letter`) as **documentation-first nested dicts** in config: field names, required/optional semantics, and brief comments in the surrounding section header if needed. `resume_content` should mirror the pipeline output the builder will render (aligned with existing `craft_*` task schemas where those artifacts are produced). `cover_letter` should align with the object contract described in AST-309 (`re_line`, `body`, `signature`) so BUILD_CONFIG is the shared contract — if AST-309 lands first, match it; if this lands first, encode that shape here and AST-309 adjusts prompts only.

5. **Placement** — Define `BUILD_CONFIG` in `config.py` near other static contracts (e.g. after `DATA_SHAPES`, before `TOKEN_SOURCES`) with a section comment banner matching existing `NAV_CONFIG` / `DATA_SHAPES` style. No new imports from core/data/external.

6. **Optional smoke** — If a lightweight test module already asserts config invariants, add a test that `BUILD_CONFIG` exists and has top-level keys `default_style`, `supported_sections`, `artifact_shapes`; skip if the repo has no config tests (none today for BUILD_CONFIG).

## Files Changed (summary)

| File | Change |
|------|--------|
| `src/utils/config.py` | Docstring + new `BUILD_CONFIG` constant (three sub-trees as above). |
| `tests/...` (optional) | One test file only if an existing pattern covers static config shapes. |

## Decisions flagged for implementation

- **v07 completeness:** Confirm whether v07 is fully specified in-repo; if not, land structure + placeholders and track value tuning separately.
- **Section ID naming:** Resolve `summary` vs `professional_summary` (ticket wording vs existing schema keys) before wiring builder.
- **cover_letter shape:** Single object contract vs string; follow AST-309.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | One `BUILD_CONFIG`; section IDs documented to stay aligned with `DATA_SHAPES` / task schemas — no second list of section names elsewhere in this ticket. |
| §2.1 Config | All behavior-driving style lists and shapes are literals in `config.py`; no env lookups for BUILD_CONFIG. |
| §2.4 Batch | N/A — no dispatch changes. |
| §2.6 State machine | N/A — no state transitions. |
| §3.3 Imports | Utils-only; no new cross-layer imports. |
| §3.5 Naming | `BUILD_CONFIG` matches existing `*_CONFIG` naming. |

**Conflicts:** None that block planning. Residual risk is **naming drift** between `artifact_shapes` and live `TASK_CONFIG` schemas — mitigate by explicitly listing corresponding `task_key`s in the plan comment above `artifact_shapes` in code.

## Self-Assessment

**Scope — `Single-Component`**  
Only `src/utils/config.py` is in scope (plus optional tiny test); all changes live in the utils config layer with no runtime wiring.

**Conf — `Medium`**  
The work is well understood (add a config block), but v07 token completeness and exact field alignment with AST-309 / `craft_resume_base` need a quick pass during implementation to avoid rework.

**Risk — `Medium`**  
Wrong or incomplete `artifact_shapes` or section IDs would break or confuse downstream builder and agent tasks once they start reading BUILD_CONFIG; contained to artifacts, not dispatch or consult.

---

## Review

**Branch:** `<agent>/ast-296-add-build_config-to-configpy`  
**Implementation commit:** `a8a01849b0d6beab74d2025ab265075d6e444298`  
**Code tip reviewed:** `2fb8898` (BUILD_CONFIG + stub + `heading_level` / `type_scale` alignment). Radia’s notes below landed in subsequent doc-only commits on this branch.  
**Reviewed:** 2026-04-29 — Radia (`e-review-linear`)

### What's solid

- **Plan fidelity:** Module header, `BUILD_CONFIG` placement after `DATA_SHAPES` and before `TOKEN_SOURCES`, the three sub-trees (`default_style`, `supported_sections`, `artifact_shapes`), and ID-keyed `supported_sections` all match the plan. Optional smoke test correctly omitted after Susan’s Linear direction (downstream if needed).
- **§2.1 / §3.3 / §3.5:** All artifact contract literals live in `src/utils/config.py`; no new cross-layer imports; `BUILD_CONFIG` naming matches existing `*_CONFIG` blocks.
- **Drift control:** Comments tie `supported_sections` / `artifact_shapes["resume_content"]` to `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]` and `TASK_CONFIG["craft_resume_base"]["response_schema"]`; spot-check confirms keys match. `artifact_shapes["cover_letter"]` matches the AST-309 three-string contract (`re_line`, `body`, `signature`).
- **§1.3 / §1.4:** Single authoritative block; typography and spacing numbers sit under named keys (not scattered through core).

### Issues

| Severity | Topic | Notes |
|----------|--------|--------|
| — | — | No fix-now items. |
| Discuss | `supported_sections[*].heading_level` semantics | Values mix role tokens (`section_heading`, `none`) with a `type_scale` key (`candidate_name_line`). That is coherent once documented, but the field name reads like an HTML outline level; builder/AST-297 consumers should treat it as “which type_scale entry (or none) styles this block’s heading.” |
| Advisory | Un-enumerated conventions | `body_kind`, `page_break_policy`, and `section_heading_decoration.style` are string tokens without a central enum in config — fine for this ticket; consider tightening when the builder reads them. |

### Recommended actions

| Priority | Action | Owner |
|----------|--------|-------|
| Discuss | In builder or AST-297, document or type the interpretation of `heading_level` (role vs `type_scale` key) so render code does not guess. | Ada / builder |
| Advisory | When adding automated config invariant tests later, assert `artifact_shapes["resume_content"]` keys stay identical to `TASK_CONFIG["craft_resume_base"]["response_schema"]`. | Future |

---

## Resolution

### Discuss — `supported_sections[*].heading_level` semantics

**Decision:** Clarify at the source in `config.py`: values are always either `none` or a key under `default_style["type_scale"]` (same namespace as that dict), not HTML outline levels. Radia’s table note stands; builder/AST-297 can add stronger typing when they consume this.

**Code:** `src/utils/config.py` — comment block immediately above `supported_sections`.

### Advisory — un-enumerated string tokens; future drift test

**Status:** Deferred. Review accepted loose `body_kind` / `page_break_policy` / decoration `style` strings for this ticket; invariant test for `artifact_shapes["resume_content"]` vs `craft_resume_base` waits on a utils/config test harness.

---

**Artifact doc path (repo):** `docs/features/artifacts/ast-296-add-build-config-to-config-py.md`
