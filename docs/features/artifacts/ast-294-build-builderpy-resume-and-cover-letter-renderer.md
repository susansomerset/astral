<!-- linear-archive: AST-294 archived 2026-06-03 -->

## Linear archive (AST-294)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-294/build-builderpy-resume-and-cover-letter-renderer  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-295; related: AST-296; blocks: AST-307; blocks: AST-298

### Description

New core module src/core/builder.py. Two public functions: build_resume(job_id) and build_base_resume(candidate_id). Both resolve all data internally — builder calls [tracker.py](<http://tracker.py>) for job data (job_data.artifacts.resume_content, job_data.artifacts.cover_letter, job_data.critical_keywords) and [candidate.py](<http://candidate.py>) for candidate data (candidate_data.profile.\*, candidate_data.artifacts.base_resume). No caller legwork required. Renders print-ready HTML served via a Flask route in a new browser tab; user prints to PDF via browser native print. Cover letter is built only when job_data.artifacts.cover_letter is present. build_base_resume() builds from candidate_data.artifacts.base_resume content with no job context. Contact fields (name, email, phone, location, linkedin, github) are injected at render time from candidate_data.profile — never from artifact content. Hidden ATS keywords block injected from job_data.critical_keywords (sourced from grade_get response, parsed via split_to_list()) — present in PDF text layer, not visible on document.

### Comments

#### susan — 2026-05-05T17:39:47.905Z
[check-linear]

Resolved blocked e-push step.

- Verified against origin that `chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer` has **no commits ahead of `dev`** and is already contained in `origin/dev`.
- GitHub PR creation is not applicable now (`No commits between dev and branch`) because the branch content has already landed.
- Marked Linear ticket **Done**.
- Landed commit on `dev` lineage includes branch tip: `e528543aed2e0e25126ba65581dc337186d1e829`.

— Hedy (check-linear)

#### susan — 2026-05-05T17:31:51.597Z
[check-linear] blocked:

Step: e-push-linear for PR Ready ticket AST-294.

Issue:
- Local workspace is not in a safe push/merge state for this run: `git status --short` currently reports a very large unexpected deletion set unrelated to AST-294.
- `gh` CLI is unavailable in this shell environment (`command not found: gh`).

Proposed resolutions:
1. Confirm whether this workspace-wide deletion state is intentional; if yes, point me to the safe worktree/repo path for AST-294 push/merge operations.
2. If this is not intentional, restore the workspace to a known-good state, then rerun check-linear.
3. Approve using GitHub MCP merge tools directly (instead of `gh`) from a clean tree.

Until one of the above is confirmed, I am not merging/pushing from this environment.

— Hedy (check-linear)

#### susan — 2026-05-04T21:00:55.841Z
[check-linear]

**Queue:** `Hedy` (Astral Artifacts).

**Pass (2026-05-04)**
- Re-listed all seven statuses (250/page, no cursors) — only **AST-294** (Testing) carries **Hedy** right now.
- **Thread scan:** Latest `[check-linear]` is still `d0311166…`; nothing newer from Susan/engineers → **0** actionable comments.
- **Step 6 chain:** **a-plan-linear** — 0 **Todo** + Hedy; **e-push-linear** — 0 **PR Ready** + Hedy; **d-resolve-linear** — 0 **Review Posted** + Hedy; **b-build-linear** — 0 **Plan Approved** + Hedy. No runs.

— Betty

#### susan — 2026-05-04T20:48:37.476Z
[check-linear]

**Queue:** `Hedy` (Astral Artifacts).

**Pass 1 — AST-294**
- Radia’s **Review Posted** thread was actionable (no prior `[check-linear]` on this issue).
- **Fix-now:** Confirmed `e8852f68` on branch (`_coerce_candidate_blob` / row → inner `candidate_data`); pushed **`e528543a`** — dead `inner` assignment in `_emit_body_sections_html` (advisory), **Resolution** + Review table updates in combined doc.
- **Linear:** **Testing**, assignee Susan, labels preserved (`Hedy` + Conf/Risk/Scope/Feature).
- **Worktree:** edits in `astral-hedy` (branch already bound there).

— Betty

#### susan — 2026-05-04T20:48:35.046Z
Review feedback resolved. Branch `chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer` is ready for testing. Commit: `e528543a`

#### susan — 2026-05-04T20:47:31.994Z
[check-linear]

**Hedy queue pass (2026-05-04)**

- **Scanned** Astral Artifacts + label **Hedy** for statuses: Todo, Plan Ready, Plan Approved, In Progress, Code Complete, Review Posted, Testing (250/issue, no extra pages).
- **Actionable thread:** Radia review (2026-05-04) — `get_candidate` returns a **DB row**; `profile` / `artifacts` / `context` live under **`candidate_data`**.

**Done:**
- Added **`_coerce_candidate_blob`** in `src/core/builder.py` so we unwrap a full row or accept the inner blob.
- **`build_resume`** / **`build_base_resume`** now pass the inner dict into **`build_resume_from_job`** / style merge / `_merge_effective_style`.
- Documented in module docstring.
- **Commit:** `e8852f68` — `fix(AST-294): unwrap get_candidate row — use nested candidate_data blob` (pushed to `chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer`).

**Second pass:** no further unanswered items found after this reply (nothing newer than Radia’s note still lacking a `[check-linear]` follow-up).

**Step 6 (post-inbox a-plan → e-push → d-resolve → b-build chain):** skipped — no idle queue drain requested; running queue-mode plan/build without a named ticket would be unsafe from this session.

— Hedy (check-linear)

#### susan — 2026-05-04T20:08:09.368Z
**Review posted — Radia**

Summary: **1** fix-now (`get_candidate` returns a **row**; `artifacts` / `profile` / `context` live under **`candidate_data`** — `build_resume` / `build_base_resume` / `_merge_effective_style` currently read the wrong shape; see combined doc), **2** discuss, **2** advisory.

Diff reviewed: **`origin/dev`…feature branch** (merge-base `50aed96`). Owner back to **Hedy** per build handoff. Conf / Risk / Scope unchanged.

**Combined doc:**  
https://github.com/susansomerset/astral/blob/6f46eaa77f259a2e61572d6a9f5aaa20d6d8c1a4/docs/features/artifacts/ast-294-build-builderpy-resume-and-cover-letter-renderer.md

— Radia

#### susan — 2026-05-04T19:55:46.061Z
Built by **Hedy** (Cursor agent).

**Branch:** `chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer`  
**Commits:** `7424f4e` (feat — `builder.py`, `tracker.get_job`, `BUILD_CONFIG` v07 fonts + `ats_keyword_block` + colors), `b058132` (docs — plan review stub with hash).

**Summary:** `src/core/builder.py` — `build_resume`, `build_resume_from_job`, `build_base_resume` plus helpers per plan (resolve sections/cover, profile overlay, style merge, ResumeSite markers, HTML emit). `tracker.get_job` delegates to `database.get_job`. `BUILD_CONFIG["default_style"]` updated for Helvetica/Palatino stacks, Susan default accent/header, `ats_keyword_block` literals. **ResumeSite** tree left untracked locally (not in commit).

— Hedy

#### susan — 2026-05-04T19:53:03.677Z
Label review (build agent):

Conf: **agree** — conf-Medium (v07 parity + live `experience` shape still need a careful read of `dev` data).
Risk: **agree** — risk-Medium (profile/ATS HTML mistakes are user-visible).
Scope: **agree** — scope-Single-Component (`builder.py` + thin `tracker.get_job`, optional `BUILD_CONFIG` literals).

Proceeding with implementation.

#### susan — 2026-05-04T19:33:03.109Z
**Plan updated (Revision 5)** — same path on `chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer`, pushed to GitHub.

Incorporates your comments:
- **Removed** formal testing stage and `tests/` from the planned files table.
- **Split** former monolithic Stage 3 into **Stages 3–10** (one stage per helper / concern: `_resolve_resume_sections`, `_resolve_cover_letter`, `_apply_profile_to_render_dict`, `_merge_effective_style`, `_apply_resume_text_markers`, `_emit_job_resume_html`, then `build_base_resume` wiring).
- **`batch_id` vs `get_job`:** Plan now states builder does **not** take `batch_id` as a job key (§2.4 claim semantics); adds **`build_resume_from_job(job, candidate_data)`** so dispatcher/daisy-chain passes the hydrated row and skips a second fetch, while **`build_resume(job_id)`** still uses **`tracker.get_job`** for Flask/id-only callers.

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer/docs/features/artifacts/ast-294-build-builderpy-resume-and-cover-letter-renderer.md

#### susan — 2026-05-04T19:31:12.598Z
Remove Stage 4, we are not testing formally yet.

#### susan — 2026-05-04T19:30:06.074Z
Break Stage 3 into individual stages one per helper function.

#### susan — 2026-05-04T19:27:28.790Z
Your plan suggests adding a function for "get_job" in tracker.  Why add a new fetch pattern instead of using batch_id (which can be passed through the daisy-chain)?  batch_id and astral_job_id are very similar, but the batch_id locks the record, so we wouldn't have to include logic to make sure another process wasn't also working on that record.  This may be a case where the dispatcher sends the whole job record as ctx to build_resume, not requiring build_resume to fetch the job (and hit the database) as second time.

#### susan — 2026-05-04T19:21:55.150Z
**Plan (rewritten per a-plan-linear, Revision 4):** `docs/features/artifacts/ast-294-build-builderpy-resume-and-cover-letter-renderer.md` on branch `chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer` (pushed).

**GitHub:** https://github.com/susansomerset/astral/blob/chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer/docs/features/artifacts/ast-294-build-builderpy-resume-and-cover-letter-renderer.md

**Self-Assessment (from plan):**
- **Scope — scope-Single-Component:** One new `builder.py` plus thin `tracker.get_job` and optional `config.py` tuning; no dispatcher/UI in this ticket.
- **Conf — conf-Medium:** v07 CSS and schema keys are specified; live `experience` wire format must be verified on `dev` before implementation or escalate per execution contract.
- **Risk — risk-Medium:** Profile injection and ATS visibility mistakes are user-visible in PDFs but scoped to artifact HTML.

**Note:** Step 4 of the skill (`git checkout dev && rebase origin/main`) could not run in this worktree because `dev` is checked out in another worktree; `origin/main` was already reachable from this branch. Other agents should keep `dev` rebased from `astral` root.

**Hedy** queue label left unchanged per plan-linear step 10.

#### susan — 2026-04-29T20:37:44.387Z
**Susan’s questions — recorded decisions (2026-04-29)**

### 1) Who still showed “blocked by” 295/296?

**AST-294** still had Linear relation edges `blockedBy` → AST-295 and AST-296 in the API even if activity feed showed dependency churn. I **removed those two blocked-by links** on AST-294 so the graph matches shipped work on `dev` (`split_to_list`, `BUILD_CONFIG`). If anything else should stay linked, say so.

### 2) Section body format (you had no strong preference)

**Decision for v1:** treat artifact section strings as **plain text**: `html.escape`, preserve newlines with **`white-space: pre-wrap`** in CSS. No markdown renderer until we confirm artifacts store markdown/HTML. Documented here so build doesn’t guess.

### 3) Tracker vs `database.get_job` — excellent catch

- **`get_job_batch(batch_id)`** is for **dispatch batches** (a run’s claim set); a batch can have many jobs, or one — either way the key is **`batch_id`**, not a substitute for “fetch by `astral_job_id`”.
- **AST-294 builder** should load the job row via **`tracker`** once a thin **`tracker.get_job(astral_job_id)`** (delegating to `database.get_job`) exists.
- **Consult hygiene** is tracked separately: **[AST-372](https://linear.app/astralcareermatch/issue/AST-372/consult-fetch-job-by-id-through-tracker-not-database)** (Astral Consult, **Bug**) — `consult.py` should stop importing `get_job` from the data layer and call the tracker wrapper instead.

Plan doc on the feature branch will get a short **Revisions** block pointing at this comment.

— Hedy

#### susan — 2026-04-29T20:29:41.742Z
**Plan ready** — `docs/features/artifacts/ast-294-build-builderpy-resume-and-cover-letter-renderer.md` on branch `chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer`.

## Self-Assessment (for labels)

**Scope — `scope-Single-Component`** — One new core module (`builder.py`) plus optional small `BUILD_CONFIG` keys and optional tests; no Flask/UI in this ticket (AST-298 owns the route).

**Conf — `conf-Medium`** — `BUILD_CONFIG` + `split_to_list` patterns exist on `dev`, but HTML/CSS mapping from nested config and ATS/PDF visibility need a careful pass; markdown vs escaped text may need your call.

**Risk — `risk-Medium`** — Profile injection mistakes would wrong contact info on printed output; ATS keyword styling errors could hide or expose keywords incorrectly — contained to artifact rendering.

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-294-build-builderpy-resume-and-cover-letter-renderer/docs/features/artifacts/ast-294-build-builderpy-resume-and-cover-letter-renderer.md

— Hedy (plan-linear)

---

# AST-294 — Build `builder.py` — Resume and Cover Letter Renderer

**Linear:** [AST-294](https://linear.app/astralcareermatch/issue/AST-294/build-builderpy-resume-and-cover-letter-renderer)  
**Feature branch:** `<agent>/ast-294-build-builderpy-resume-and-cover-letter-renderer` (Linear `gitBranchName`)

## Summary

Add `src/core/builder.py` with synchronous **`build_resume(job_id: str) -> str`**, **`build_resume_from_job(job: dict, candidate_data: dict) -> str`**, and **`build_base_resume(candidate_id: str) -> str`**. The builder is a **read-only HTML renderer**, not a dispatcher and not a daisy-chain orchestrator: artifact pipelines and `do_task` produce JSON; the builder consumes it.

**Two entry points for job HTML:** (1) **`build_resume(job_id)`** — for Flask and any caller that only has an id: loads the job row once via **`tracker.get_job`**, resolves company → candidate, loads **`get_candidate`**, then delegates to **`build_resume_from_job`**. (2) **`build_resume_from_job(job, candidate_data)`** — for the dispatcher or daisy-chain when the **job record is already in memory** under an existing dispatch claim: **no second database read**; caller passes the same dict shape `tracker.get_job` would return, plus the already-loaded **`candidate_data`** dict. Both paths run identical resolution, profile injection, style merge, and HTML emission.

**Artifact precedence (builder-owned):** job `artifacts.resume_content` with **runtime fallback** to `candidate_data["artifacts"]["base_resume"]`; job `artifacts.cover_letter` with fallback from **`candidate_data["context"]["sample_cover_text"]`** mapped into `{re_line, body, signature}`; **`critical_keywords`** from the job dict when present. **`build_base_resume`** uses **`artifacts.base_resume`** only. Flask route wiring stays **AST-298**.

⚠️ **Decision — `batch_id` vs `astral_job_id` (Linear 2026-05-04):** Do **not** use `batch_id` as a substitute for loading a job by **`astral_job_id`**. Per **§2.4**, `batch_id` is the dispatch run’s **claim handle** for a set of rows; it is not a stable per-job identity and does not mean “fetch this job” in the data layer. The builder does not accept `batch_id`; locking for writers stays in claim/process/release upstream. Read-only render does not need to re-lock. When the pipeline already holds the hydrated job row, it calls **`build_resume_from_job`** and avoids redundant **`get_job`**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Add `get_job(astral_job_id: str)` — thin delegate to `database.get_job` for job-by-ID (distinct from `get_job_batch`). | core |
| `src/core/builder.py` | **New** — `build_resume`, `build_resume_from_job`, `build_base_resume`, private helpers (one concern per function as staged below). | core |
| `src/utils/config.py` | **Optional** — Extend `BUILD_CONFIG["default_style"]` for v07 parity (`styles07.css`), optional `ats_keyword_block`, optional `artifact_shapes` / admin keys for tagline + skills heading (Stage 1). | utils |

## Stage 1: Config and contracts (optional extensions)

**Done when:** Either (A) `BUILD_CONFIG` / `artifact_shapes` contain everything the builder needs for v07 parity and optional fields, or (B) deferrals are recorded under **Revisions** with a Linear escalation if schema names are not approved.

1. In `src/utils/config.py`, align `BUILD_CONFIG["default_style"]["fonts"]` and related tokens to the **legacy ResumeSite v07 snapshot** (kept locally outside this repo — **do not** re-import those binaries/HTML/CSS into `docs/`). Comment beside defaults should note v07 parity.
2. Optional keys for **tagline** / **skills section heading**: extend **`artifact_shapes["resume_content"]`**, **`supported_sections`**, and **`DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]`** in one edit if Susan has approved names; else **stop** with execution-contract comment.
3. Optional **`BUILD_CONFIG["default_style"]["ats_keyword_block"]`** (or under `print`) for hidden-keyword CSS — no magic literals in `builder.py`.

⚠️ **Decision:** Older **`final_style_parameters.txt`** / sibling CSS files are historical; authoritative literals are **`BUILD_CONFIG["default_style"]`** plus candidate overlays — compare visually against the external ResumeSite tree when adjusting typography.

## Stage 2: `tracker.get_job`

**Done when:** `tracker.get_job(astral_job_id)` exists, delegates to the data layer’s job-by-ID fetch, returns the same shape as today’s `database.get_job` (no new return contract).

1. In `src/core/tracker.py`, add `def get_job(astral_job_id: str)` calling the canonical job-by-ID function in `database.py` (match its signature and return value exactly).
2. Module comment: *Job-by-ID for render and id-only callers; not `get_job_batch` (dispatch-scoped). Consult → **AST-372** for `consult.py` to use this wrapper.*

## Stage 3: `builder.py` — module skeleton and public APIs

**Done when:** Module exists with docstring (§3.3 imports: no `ui`, no `external`, no `do_task`), and all three public functions are wired: **`build_resume_from_job`** contains only orchestration calls to later-stage helpers (stubs OK until those stages land in the same PR); **`build_resume`** calls `tracker.get_job` + `get_company` + `get_candidate` then **`build_resume_from_job`**; **`build_base_resume`** calls `get_candidate` then shared helpers (stubs OK for body until later stages).

1. Create `src/core/builder.py` with imports: `html`, `src.data.database` (`get_company` only), `src.core.tracker` (`get_job`), `src.core.candidate` (`get_candidate`), `src.utils.config` (`BUILD_CONFIG`), `src.utils.formatting` (`split_to_list`).
2. Implement **`build_resume(job_id: str) -> str`:** `job = tracker.get_job(job_id)`; if missing, `raise ValueError`. Resolve `candidate_id` via company row (`get_company` on job’s company short name); `get_candidate(candidate_id)`; then **`return build_resume_from_job(job, candidate_data)`**.
3. Declare **`def build_resume_from_job(job: dict, candidate_data: dict) -> str`** — extract `job_data = job.get("job_data")` or the plan-accurate key path used on `dev` (verify against `database.get_job` return shape in code before merging; if ambiguous, **stop and comment on Linear**). Delegate through helpers from Stages 4–9 in order.
4. Declare **`def build_base_resume(candidate_id: str) -> str`** — `get_candidate`; require `artifacts.base_resume`; reuse profile, style, marker, and HTML helpers **without** job `critical_keywords` or cover letter paths.

## Stage 4: Helper — `_resolve_resume_sections`

**Done when:** Function exists, unit-testable in isolation: given `job_data` and `candidate_data`, returns the dict of section fields to render (after logical merge of job vs base fallback), or raises `ValueError` if neither source yields a renderable dict.

1. Implement **`_resolve_resume_sections(job_data: dict, candidate_data: dict) -> dict`:** prefer `job_data.get("artifacts", {}).get("resume_content")` if non-empty dict; else `candidate_data.get("artifacts", {}).get("base_resume")` if non-empty dict; else `raise ValueError`.

## Stage 5: Helper — `_resolve_cover_letter`

**Done when:** Function returns either a `cover_letter`-shaped dict or `None` (omit cover section).

1. Implement **`_resolve_cover_letter(job_data: dict, candidate_data: dict) -> dict | None`:** use job `artifacts.cover_letter` if dict with any non-empty string field per `BUILD_CONFIG["artifact_shapes"]["cover_letter"]`; else if `candidate_data.get("context", {}).get("sample_cover_text")` is non-empty string, return `{"re_line": "", "body": <text>, "signature": ""}`; else `None`. Document v1 body mapping in the function docstring.

## Stage 6: Helper — `_apply_profile_to_render_dict`

**Done when:** Given render dict + `candidate_data["profile"]`, overwrites identity/contact fields; never trusts artifact strings for identity; concatenation rules documented in comments beside the code.

1. Implement overwrite of `candidate_name`, `candidate_title`, `candidate_contact_detail` (and optional tagline key if schema exists) from **`TOKEN_SOURCES` / admin field parity** (`profile.first`, `profile.last`, email, phone, location, `profile.github`, `profile.linkedin_url`, etc.).

## Stage 7: Helper — `_merge_effective_style`

**Done when:** Returns merged style dict (or structure the HTML stage consumes) from `BUILD_CONFIG["default_style"]` overlaid with `candidate_data["artifacts"]["base_resume"]` style keys (`accent_color`, etc.) per AST-296.

## Stage 8: Helper — `_apply_resume_text_markers`

**Done when:** Centralized application of `__` → U+00A0 and `~~` → U+2011 for string fields that may carry legacy ResumeSite conventions (same spirit as the old PostScript pipeline).

## Stage 9: Helper — `_emit_job_resume_html`

**Done when:** Single complete HTML document string: `<!doctype html>`, charset meta, embedded `<style>` from merged style matching **v07 CSS structure** (as encoded in `BUILD_CONFIG`), sections from `BUILD_CONFIG["supported_sections"]` intersected with resolved keys, empty sections omitted, `html.escape` + `white-space: pre-wrap` for v1 bodies, experience subsection follows live **`artifact_shapes`** / `dev` data (escalate if shape unknown), cover blocks if Stage 5 returned a dict, ATS block from `job_data.get("critical_keywords")` via `split_to_list` + **only** `BUILD_CONFIG` literals for CSS. Conditional **`#prior-experience { page-break-before: always; }`** only when that section is emitted.

## Stage 10: `build_base_resume` — wire shared helpers

**Done when:** `build_base_resume` returns full HTML using the same profile, style, marker, and emission helpers as the job path, with no cover and no `critical_keywords` block; missing `base_resume` → `raise ValueError`.

1. Resolve sections from `artifacts.base_resume` only (no job fallback).
2. Reuse Stages 6–9 helpers; skip job-only branches (cover, ATS).

## Self-Assessment

**Scope — `Single-Component`**  
One new module plus thin `tracker.get_job`; optional `config.py` only in Stage 1. No formal test stage in this ticket.

**Conf — `Medium`**  
v07 CSS and optional schema keys are specified; live `experience` wire format must match `dev` — verify before coding or escalate.

**Risk — `Medium`**  
Profile injection and ATS visibility errors are user-visible in PDFs; scoped to artifact HTML.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | Shared helpers for job and base resume paths; single emission helper. |
| §1.4 | Design literals in `BUILD_CONFIG` only. |
| §2.1 Config | Typography, ATS block, section metadata from `BUILD_CONFIG`. |
| §2.4 Batch | Builder does not participate in claim/clear; **`build_resume_from_job`** is the hook for callers that already hold batch context. |
| §2.6 State machine | N/A — read-only. |
| §3.3 Imports | Core → data, utils, `candidate`, `tracker` only. |
| §3.5 Naming | snake_case: `build_resume`, `build_resume_from_job`, `build_base_resume`. |

**Conflicts:** None; §4.1 “dev only” prose superseded for artifacts by feature-branch skills.

## ResumeSite parity (reference)

- **Tree:** Not in-repo — keep the ResumeSite HTML/CSS/PS snapshot **outside** `docs/` (local path only, not in git). Visual checks compare rendered HTML against that external tree; **`BUILD_CONFIG`** carries the literals the builder uses.
- **Per-candidate:** Optional tagline, optional sections, skills section title, accent from `candidate_data` (schema-dependent).
- **Cover:** JSON `cover_letter` + `context.sample_cover_text` fallback; not legacy `.ps` div format.

## Revisions

Revision 5 — 2026-05-04  
Driven by: Linear comments (Susan) — remove formal testing stage; **split implementation into one stage per helper**; **`batch_id` vs `get_job`** — document why `batch_id` is not the lookup key; add **`build_resume_from_job`** so dispatcher/daisy-chain avoids a second DB read while **`build_resume(job_id)`** stays for id-only callers.  
Changes: Removed Stage 4 (tests) and **`tests/`** from Files Changed; replaced monolithic Stage 3 with Stages 3–10 mapped to helpers; updated summary and self-review §2.4.

Revision 4 — 2026-04-29  
Driven by: **a-plan-linear** full replace.  
Changes: Skill-shaped plan (Layers, Stages, execution contract).

Revision 3 — 2026-04-29  
Driven by: Non-customized applications; builder-owned lookup.  
Changes: `resume_content` + `base_resume` fallback; sample cover mapping.

Revision 2 — 2026-04-29  
Driven by: External ResumeSite snapshot (reference only).  
Changes: Parity reference, fonts, per-candidate table (condensed in Rev 5+).

Revision 1 — 2026-04-29  
Driven by: Linear comment.  
Changes: `tracker.get_job`, plain-text v1.

Revision 6 — 2026-05-04  
Driven by: Radia review + **check-linear** (`f-resolve-linear`).  
Changes: Confirmed **`_coerce_candidate_blob`** on branch; advisory dead-`inner` cleanup; **Resolution** appended; Linear → **Testing**.

## Review

**Branch:** `<agent>/ast-294-build-builderpy-resume-and-cover-letter-renderer`  
**Diff reviewed:** `origin/dev`…`origin/<agent>/ast-294-build-builderpy-resume-and-cover-letter-renderer` (merge-base `50aed96`)  
**Implementation commit:** `7424f4eb595c36ce41b93128517812dbf2576619` — post-Radia: `e8852f68` (row→blob); doc Resolution + dead-`inner` cleanup on branch tip (see GitHub).  
**Reviewed:** 2026-05-04 — Radia (`e-review-linear`). Doc-only follow-ups may land in later commits on this branch. Merge to **`dev`** / PR and Linear states after review follow **`docs/ASTRAL_TEAM_WORKFLOW.md`** (manual architect / testing steps).

### What's solid

- **Plan shape:** `tracker.get_job` thin delegate to `database.get_job` with clear docstring on §2.4 vs `get_job_batch` (aligns with Susan/Hedy notes and AST-372 direction).
- **Layering (§3.3):** `builder.py` stays core → `candidate` / `tracker` / `database` / `utils` only; no UI or external I/O.
- **Read-only + escape:** Section bodies use `html.escape` + `white-space: pre-wrap` per recorded plan decision (plain text v1).
- **ATS strip:** `split_to_list` + `BUILD_CONFIG["default_style"]["ats_keyword_block"]` keeps “visually hidden keyword” knobs in config (§1.4 / §2.1).
- **Dual entry:** `build_resume` vs `build_resume_from_job` matches Revision 5 (id-only fetch vs hydrated row).

### Issues

| Severity | Topic | Notes |
|----------|--------|--------|
| **Fix now** | **`get_candidate` row vs `candidate_data` blob** | **Resolved:** `_coerce_candidate_blob` + `build_resume` / `build_base_resume` / `build_resume_from_job` entry paths (commit `e8852f68`). |
| Discuss | **`experience` wire format** | `_format_experience_value` JSON-dumps dict/list into one escaped block — fine for debugging v1, but plan flagged verifying live `experience` shape; confirm before operators rely on rendered layout. |
| Discuss | **HTML `id="summary"`** vs **`BUILD_CONFIG.supported_sections`** | `_KEY_TO_SECTION_ID` maps `professional_summary` → `summary` while config keys use `professional_summary`; document or align so PDF/CSS hooks do not drift. |
| Advisory | **Emit-time typography literals** | `_emit_html_document` embeds sizes (e.g. 33px, 20px) not read from `BUILD_CONFIG["default_style"]["type_scale"]` — acceptable bootstrap, but partial drift from the plan’s “literals in BUILD_CONFIG only” spirit (§2.1 / §1.4). |
| Advisory | **Dead assignment** | **Resolved:** compute `inner` only after the `professional_summary` branch (`continue`); see post-review commit on branch. |

### Recommended actions

| Priority | Action | Owner |
|----------|--------|-------|
| Fix now | Unwrap: shipped in `e8852f68`; doc updated here. Manual `build_base_resume` smoke on `dev` still recommended when data is handy. | Betty |
| Discuss | After first real job render on `dev`, confirm whether `experience` should stay prose, list, or structured HTML — adjust `_format_experience_value` accordingly. | Hedy / Susan |
| Advisory | Gradually map emitted CSS lengths to `BUILD_CONFIG` tokens once v07 parity stabilizes. | Hedy |

---

## Resolution

**Date:** 2026-05-04 — Betty (**check-linear** / **f-resolve-linear**)

- **Fix-now (`get_candidate` shape):** Already addressed on branch by **`e8852f68`** (`_coerce_candidate_blob`, `build_resume` / `build_resume_from_job` / `build_base_resume` use inner `candidate_data`).
- **Advisory (dead `inner`):** `inner = html.escape(...)` only after the `professional_summary` branch (`continue`), same push as this Resolution doc.
- **Discuss items:** Unchanged (experience wire format; `id="summary"` vs config keys) — no code change this pass.
- **Build:** `python3 -m compileall -q src` before push.

