# Inventory and rewire remaining job artifact consumers

**Linear:** [AST-1593](https://linear.app/astralcareermatch/issue/AST-1593/inventory-and-rewire-remaining-job-artifact-consumers-support)
**Parent:** [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-job-artifactsjob-resume-and-job-artifactscover-letteras) — Support “job.artifacts.job_resume” and “job.artifacts.cover_letter” as artifacts
**Publish ref:** `sub/AST-1588/AST-1593-inventory-rewire-job-artifact-consumers`

After AST-1590 (catalog keys) and AST-1592 (tracker `save_job_artifact` / `get_job_current` + jobs API / agent), inventory every production surface that still treated `job_resume` / `cover_letter` as job-record or type-specific SoT, then rewire **builder** live resolve and remaining **UI** load/save assumptions onto the generic current-read / API contract. Jobs GET hydrate already overlays catalog currents under leaf keys; this ticket finishes builder + client decommission. No coat-check, no new body validation, no source-id UI.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/builder.py` — **modified** — live resume/cover resolve uses generic tracker current-read by catalog key
- `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — load/save follow rewired generic API/key contract
- `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** — content checks follow rewired payload / key contract
- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — only if tab/`artifact_key` wiring must cite catalog keys after config change

Every row in **Files Changed** is one of those paths (plus this plan doc). Do **not** re-own `tracker.py` / `api_jobs.py` / catalog / schema (siblings #1–#3).

## Inventory (parent AC7 — pre-change production surfaces)

Status column is relative to **this** ticket’s start tip (post AST-1590 + AST-1591 + AST-1592 on `origin/ftr/AST-1588-job-artifacts-job-resume-cover-letter`).

| Surface | R/W | Pre-#4 SoT path | Disposition |
|---------|-----|-----------------|-------------|
| `tracker.save_job_artifact` / `get_job_current` | W/R | catalog → artifacts table | **retired parallel SoT** — done AST-1592; leave |
| `tracker.hydrate_job_artifacts_for_display` (with job id) | R | `get_job_current` → leaf `job_resume` / `cover_letter` on display blob | **rewired** AST-1592; leave |
| `api_jobs` PUT `/artifacts/job_resume` \| `cover_letter` \| legacy `resume_content` | W | `save_job_artifact` + catalog keys | **rewired** AST-1592; leave |
| `api_jobs` job detail GET (hydrate w/ id) | R | hydrate current-read overlay | **rewired** AST-1592; leave |
| `agent` finalize body-replica land | W | `save_job_artifact` via `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` catalog keys | **rewired** AST-1592; leave |
| Type-specific public `save_job_artifact_job_resume_body` / `save_job_artifact_cover_letter` | W | deleted / forwarded in AST-1592 | **retired** AST-1592 (parent AC8); leave |
| `builder._resolve_resume_sections` / `_resume_content_source_label` | R | `job_data.artifacts.resume_content` then blob/`job_resume` pin then base_resume | **rewire this ticket** |
| `builder._resolve_cover_letter` / `_cover_letter_source_label` | R | `job_data.artifacts.cover_letter` (dict/pin) then sample | **rewire this ticket** |
| `ArtifactEditor` job load (`applyJobArtifactResponse`) | R | GET job `artifacts[leaf]`; empty `job_resume` falls back to `resume_content` sibling | **rewire this ticket** (drop sibling SoT fallback; trust hydrate current) |
| `ArtifactEditor` job save | W | PUT `/artifacts/{leaf}` body `{[leaf]: payload}` → API catalog write | **already on contract** — keep leaf URL/body keys (API maps to catalog); no change unless load path breaks |
| `recommendedJobReport` `printResumeVisible` / `printCoverVisible` / `reportHasArtifactContent` | R | leaf keys (+ resume_content OR for print resume) on hydrated artifacts | **rewire this ticket** — treat hydrated `job_resume` / `cover_letter` as SoT; resume_content only as legacy visibility, not SoT |
| `JobAnalysisReportModal` tab → `ArtifactEditor` | R/W | JAR `artifact_key` leaves (`job_resume` / `cover_letter`) | **no change** if leaves remain (AST-1590 1:1 map); see Decision |

Non-goals left out of inventory rows: session cover letter admin, candidate `base_resume` consumers, `proposed_answers` / notes / application_responses, coat-check.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Resolve live resume/cover via `tracker.get_job_current` + catalog keys; debug source labels name catalog/current-read path; stop treating job-record blobs as SoT | core |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Job-mode load uses hydrated current leaf body; remove `resume_content` sibling SoT fallback for empty `job_resume` | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Content / print visibility prefer hydrated `job_resume` / `cover_letter`; do not treat `resume_content` as job-resume SoT | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | **No product change** unless Stage 3 discovers leaf keys broken — Decision below | ui |

**Out of this ticket:** `src/utils/config.py`, `src/data/database.py`, `src/core/tracker.py`, `src/ui/api/api_jobs.py`, `src/core/agent.py`, coat-check, source-id UI, sibling blob catalog promotion, `tests/` / `docs/test-bible/**`.

## Stage 1: Builder live resolve via `get_job_current`

**Done when:** `build_resume` / `build_resume_from_job` / `build_cover_letter` / `build_cover_letter_from_job` obtain job resume and cover bodies via `tracker.get_job_current(..., "job.artifacts.job_resume"|"job.artifacts.cover_letter")` when `astral_job_id` is known. They do **not** treat `job_data.artifacts.job_resume` / `cover_letter` / `resume_content` as SoT. Debug source labels name the catalog current-read path (or base_resume / sample fallback), not `job_data.artifacts.*` SoT. Empty current + no base_resume still raises the existing missing-resume error.

1. In `src/core/builder.py`, update `_resolve_resume_sections` to accept `astral_job_id: Optional[str] = None` (keep `job_data` + `candidate_data` for fallbacks / keywords elsewhere):

   - If `astral_job_id` strips non-empty: `body = tracker_mod.get_job_current(jid, "job.artifacts.job_resume")`. If `_is_nonempty_resume_dict(body)`, return `dict(body)`.
   - Else (or current miss): existing candidate `load_pilot_base_resume_for_candidate` fallback unchanged.
   - **Delete** the branches that read `artifacts["resume_content"]`, pin-string `job_resume`, or dict `job_resume` from `job_data` as SoT.
   - Raise the same `ValueError("No resume_content on job and no base_resume on candidate")` when both current and base miss (message text may stay for compatibility).

2. Update `_resolve_cover_letter` similarly:

   - If job id known: `raw = tracker_mod.get_job_current(jid, "job.artifacts.cover_letter")`; if dict and `_cover_letter_nonempty`, return `_cover_letter_fields_for_read(raw)` (or normalize via existing helper).
   - Else: keep `candidate_data.context.raw_sample` last-resort sample behavior only (not catalog SoT).
   - **Delete** reads of `job_data.artifacts.cover_letter` dict/pin as SoT.

3. Update `_resume_content_source_label` / `_cover_letter_source_label` to take optional `astral_job_id` and report:

   - Resume: `"get_job_current(job.artifacts.job_resume)"` when current non-empty; else existing base_resume label; else `"missing"`. Never return `job_data.artifacts.resume_content` as the live SoT label.
   - Cover: `"get_job_current(job.artifacts.cover_letter)"` when current non-empty; else sample label; else `None`.

4. Thread `astral_job_id` from callers:

   - `build_resume_from_job`: `jid = str(job.get("astral_job_id") or "").strip() or None`; pass into resolve + source-label helpers.
   - `build_cover_letter_from_job`: same.
   - `build_resume` / `build_cover_letter` already load by id — ensure the job dict they pass includes `astral_job_id`.

5. Gate any new debug-contract lines on `debug=True` only (`astral.standards.debug-contract-gated`). No new imports from `src.data` or `src.ui` (builder already imports tracker).

⚠️ **Decision:** Prefer calling `get_job_current` inside builder over relying on a pre-hydrated `job_data.artifacts` blob. Hydrate is a display overlay for API/UI; builder must not treat that overlay (or legacy blobs) as authority — parent AC6 requires generic current-read.

## Stage 2: ArtifactEditor + recommendedJobReport client contract

**Done when:** Job-mode ArtifactEditor loads the hydrated **current** leaf body for `job_resume` / `cover_letter` without promoting `resume_content` as SoT when `job_resume` is empty. Save still PUTs leaf URL/body keys (API already maps to catalog). recommended-report content / print helpers treat hydrated `job_resume` / `cover_letter` as the job artifact signal; `resume_content` is not required for “has job resume” SoT.

1. In `ArtifactEditor.tsx` `applyJobArtifactResponse`:

   - Keep reading `artifacts[persistKey]` for leaf keys from JAR (`job_resume`, `cover_letter`, `proposed_answers`).
   - **Remove** the AST-1428 block that copies `artifacts.resume_content` into the editor when `persistKey === "job_resume"` and raw is null/empty/string. After AST-1592 hydrate, current job resume is already under `job_resume`; sibling `resume_content` must not become SoT for the job_resume tab.
   - Parent note: editor shows **CURRENT** (GET hydrate / current-read overlay), not an operative-by-id fetch — do **not** add an operative job_resume GET.

2. Job save path: leave PUT `/api/jobs/{id}/artifacts/{leaf}` + `{[leaf]: payload}` as-is (matches `api_jobs` leaf routes that call `save_job_artifact` with catalog keys). Do not invent hierarchical client keys this ticket.

3. In `recommendedJobReport.tsx`:

   - `printResumeVisible`: true when `artifactHasContent(artifacts, "job_resume")`. Do **not** OR `resume_content` as SoT for print-resume visibility (legacy blob is not catalog SoT). If a row has only ancient `resume_content` and no current `job_resume`, print resume stays hidden — correct under catalog SoT.
   - `printCoverVisible`: keep `artifactHasContent(artifacts, "cover_letter")` (hydrated current).
   - `reportHasArtifactContent` / tab helpers that iterate `artifact_key` from manifest: unchanged leaf keys.

## Stage 3: JobAnalysisReportModal — confirm no change

**Done when:** JAR modal still passes leaf `artTab.artifact_key` into ArtifactEditor; no catalog-key rewrite required. If Stage 2 load/save works with leaf keys from `JOBS_RECOMMENDED_ARTIFACT_TABS`, leave `JobAnalysisReportModal.tsx` untouched (file stays in Files Changed with “no change” / Decision only — do not invent drive-by edits).

⚠️ **Decision:** AST-1590 kept JAR tab `artifact_key` as leaf strings with a 1:1 catalog map. AST-1592 hydrate fills those leaves from `get_job_current`. Therefore this modal does **not** need hierarchical keys. If build discovers broken wiring, stop and comment on parent AST-1588 — do not silently expand Scope.

1. Manually verify (engineer during build): JAR Artifacts tabs still open ArtifactEditor with `job_resume` / `cover_letter`; craft task key branch `artTab.artifact_key === "cover_letter"` still matches. No code change if verified.

2. If verification fails because tabs somehow emit catalog keys, patch **only** the comparison / prop mapping needed to accept catalog keys **or** leaf keys — still within this file’s Scope line. Prefer dual-accept (`key === "cover_letter" || key === "job.artifacts.cover_letter"`) over rewriting config.

## Execution contract

- Stages 1 → 2 → 3 in order; one `code()` commit per stage (Stage 3 may be a docs-only note in the build stub if zero file diff — then skip empty commit and record “no modal change” in the build stub).
- Do not add files outside **Files Changed**.
- Ambiguity or codebase drift → stop; comment on parent AST-1588 with the Stage blocked template from plan-child.
- Engineer must not create or edit `tests/` or `docs/test-bible/**` (Betty `qa-child`).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

```text
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1593
**Overall:** APPROVED
**Publish ref:** `sub/AST-1588/AST-1593-inventory-rewire-job-artifact-consumers` @ `cbe5479b5098a9cf9933e0a99e4b06f5946e2bdd`

## Traceability
AC6 → Stage 1 (builder `get_job_current` by catalog key) + Stage 2 (ArtifactEditor load + `recommendedJobReport` visibility); jobs GET overlay → inventory row marked rewired AST-1592 (N/A to implement here); AC7 → plan **Inventory** table (pre-change surfaces + disposition); AC8 → inventory rows for type-specific tracker/API saves marked **retired** AST-1592 (verify-only on this ticket).

## Findings

### acceptable
- **Location:** Stage 2 (`printResumeVisible`) / Stage 1 (builder resolve)
- **Finding:** Dropping `resume_content` as job-resume SoT hides print/build for rows that still have only legacy `job_data.artifacts.resume_content` and no artifacts-table current.
- **Recommendation:** Intended under catalog SoT; matches parent decommission intent.

### acceptable
- **Location:** Stage 1 (`_resolve_resume_sections` when `astral_job_id` absent)
- **Finding:** Direct `build_resume_from_job` callers without `astral_job_id` skip job current-read and fall back to candidate `base_resume` only (no job_data blob reads).
- **Recommendation:** Production `build_resume` / `get_job` paths supply id; test-only callers are Betty’s problem.

### acceptable
- **Location:** Child AC8 vs ## Boundaries
- **Finding:** Type-specific tracker/API removal is owned by AST-1592; this plan documents disposition rather than re-grepping those symbols.
- **Recommendation:** Acceptable given `after #3` boundary; build should still confirm no regressions in scoped files.

### acceptable
- **Location:** `recommendedJobReport.artifactHasContent`
- **Finding:** Pin-string “has content” heuristic unchanged; plan only adjusts `printResumeVisible` OR on `resume_content`.
- **Recommendation:** Fine once hydrate supplies dict bodies from current-read overlay.

**Considered (in-session, slim R7):** Universal orch.* — conform. Scoped core/ui statutes (`import-direction`, `debug-contract-gated`, `in-scope-only`, `dry-and-focused-functions`) — conform. Draft patterns `patt.artifact.read-current`, `patt.artifacts.ui-consistency` — conform (leaf JAR keys + backend catalog mapping preserved). Publish ref includes AST-1592 `get_job_current` — dependency satisfied.

context_tokens≈61000
```
