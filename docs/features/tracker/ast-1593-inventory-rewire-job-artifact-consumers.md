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

## Review (build)

**Built @ `4f0edd01`** — `origin/sub/AST-1588/AST-1593-inventory-rewire-job-artifact-consumers`

Product stages 1–2 landed (builder `get_job_current`; ArtifactEditor + recommendedJobReport drop resume_content SoT). Stage 3: JobAnalysisReportModal unchanged — JAR tabs still leaf `job_resume` / `cover_letter` (AST-1590 1:1 map). Test path remains Betty `qa-child`.


## Radia review

```text
# Radia review — AST-1593

`[code-rubric] revision=2`
**Rubric:** code-rubric.v2
**Ticket:** AST-1593
**Publish ref:** `sub/AST-1588/AST-1593-inventory-rewire-job-artifact-consumers` @ `635a58e43f4929980ac4d7a07ba7440fbba36869`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1593)` on publish ref. |
| orch.git.commit-vocabulary | universal | conforms | Staged `code` / `test` / `docs` / `merge-tests`. |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/AST-1588/…` only. |
| orch.git.ftr-sub-topology | universal | conforms | Epic stack on branch includes siblings 1590–1592 as expected. |
| orch.git.merge-on-checkout | universal | conforms | No violation in diff. |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history. |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish branches. |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree pattern OK. |
| orch.git.three-permanent-branches | universal | conforms | Publish ref is `sub/*`. |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Legacy decommission tradeoffs documented in Joan attachment. |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 delivered; Stage 3 no-change documented. |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code. |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed. |
| orch.roles.archie-approves-statutes | universal | conforms | N/A. |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible via Betty + `merge-tests`. |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A. |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee through Tests Passed. |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-ban violations observed. |
| astral.agent.* (3) | scoped | not-applicable | No agent changes in AST-1593 commits. |
| astral.batch.* (4) | scoped | not-applicable | No batch paths. |
| astral.config.* (2) | scoped | not-applicable | No config changes in AST-1593 product commits. |
| astral.debug.* (2) | scoped | not-applicable | No debug spike paths. |
| astral.dispatch.* (2) | scoped | not-applicable | No dispatch changes. |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file for AST-1593. |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty paths are tests/bible only. |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-tree via Betty pipeline. |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Builder stays core; UI stays ui. |
| astral.layers.import-direction | scoped | conforms | Builder → tracker/candidate/data (pre-existing data import); UI components import lib only. |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts diff. |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Leaf JAR keys preserved; no new hardcoded state lists. |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Empty-body skip unchanged in tracker path; no new coat-check. |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult paths. |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No API auth changes in 1593 commits. |
| astral.seed.* (5) | scoped | not-applicable | No seed paths. |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer logging. |
| astral.standards.database-header-inventory | scoped | not-applicable | No data-layer changes in 1593 commits. |
| astral.standards.debug-contract-gated | scoped | conforms | Source-label `debug_detail` lines remain inside existing `if debug:` blocks. |
| astral.standards.dry-and-focused-functions | scoped | conforms | `astral_job_id` threaded through resolve + label helpers. |
| astral.standards.in-scope-only | scoped | conforms | AST-1593 commits touch only builder + two frontend modules; tracker/api/agent untouched. |
| astral.standards.logging-via-utils | scoped | conforms | No new raw loggers. |
| astral.standards.names-not-ticket-ids | scoped | conforms | AST cites in comments only. |
| astral.standards.no-cross-contamination | scoped | conforms | No out-of-layer imports added. |
| astral.standards.no-hardcoded-sets | scoped | conforms | Catalog keys as string literals match plan inventory. |
| astral.standards.public-then-helpers | scoped | conforms | Public `build_*` entrypoints unchanged; private `_resolve_*` updated. |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils changes in 1593 commits. |
| astral.state.* (3) | scoped | not-applicable | No state-machine edits. |
| astral.ui.frontend-file-placement | scoped | conforms | Changes under `src/ui/frontend/src/components/` and `lib/`. |
| astral.ui.naming-conventions | scoped | conforms | No naming violations observed. |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server config. |

**Active set:** 65 statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | No approved-catalog "Patterns to reuse" block; Joan references draft `read-current` / `ui-consistency` in attachment only. |

## Plan adherence

**Stages 1–2 delivered; Stage 3 correctly skipped.**

- **Stage 1:** `_resolve_resume_sections` / `_resolve_cover_letter` call `tracker.get_job_current` with catalog keys when `astral_job_id` is set; job-record `resume_content`, pin-string, and blob SoT branches removed; source labels report `get_job_current(job.artifacts.*)`; `build_resume` / `build_resume_from_job` / `build_cover_letter_from_job` thread `jid`.
- **Stage 2:** `ArtifactEditor` drops `resume_content` sibling fallback for empty `job_resume`; `printResumeVisible` uses hydrated `job_resume` only; save path unchanged (leaf PUT).
- **Stage 3:** `JobAnalysisReportModal.tsx` has **no diff** — consistent with AST-1590 leaf JAR keys + build stub note.
- **Scope gate:** AST-1593 product commits (`26f1ad5c`, `4f0edd01`) are limited to `builder.py`, `ArtifactEditor.tsx`, `recommendedJobReport.tsx` only.
- **Estimate 3** fits footprint.

**Inventory (AC7):** Plan table documents pre-change surfaces and dispositions; implementation matches rewired rows.

## Findings

### advisory

- **Legacy `resume_content`-only rows** — builder print and `printResumeVisible` will not treat legacy blob-only resume as SoT until a catalog current exists. Joan flagged as intended decommission; downstream UAT should spot-check migrated jobs.
- **`JobAnalysisReportModal.tsx` in plan Files Changed but zero diff** — acceptable per Stage 3 decision; build stub records verification.
- **`docs/test-bible/core/builder.md` shasum** still "fill after publish" — Betty/Chuckles doc hygiene only.
- **`_resume_content_source_label` name** retained though label text is now catalog-path — cosmetic; no behavior impact.

## What's solid

- Builder no longer treats `job_data.artifacts` as operative SoT for live resume/cover — aligns with AST-1592 `get_job_current`.
- UI load path trusts hydrate overlay under leaf keys; removes AST-1428 sibling promotion that fought catalog SoT.
- Tests cover catalog-over-blob precedence, debug source labels, ArtifactEditor no-fallback, and `printResumeVisible` SoT shift.
- Full epic foundation (1590 config, 1591 sources, 1592 tracker/API/agent) present on branch for integration.

## Frame diff

**AST-1593 product:** `src/core/builder.py` catalog current-read resolve; `ArtifactEditor.tsx` load contract; `recommendedJobReport.tsx` print visibility.

**Epic stack on branch (expected):** AST-1590–1592 sibling product + tests — required dependency, not scope creep in 1593 commits.

**Deferred / N/A:** JAR modal wiring unchanged; coat-check / source-id UI / hierarchical client keys correctly out of scope.

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute straggler list.
- Downstream after parent lands: UAT on JAR tab load/save, builder live build, and recommended-report print for jobs with artifacts-table currents vs legacy blob-only rows.
- Tip under review: `635a58e4`.

context_tokens≈65000
```


## Bug: AST-1599 — Job modal hides resume/cover behind source-base-resume message

### As-is
After successful artifact generation for a recommended job, the Recommended Job modal Artifacts tab no longer presents the job resume / cover letter editors; it shows a **Source base resume** heading and the empty copy **No pinned base resume for this build** (and related loading/error/JSON when a pin exists).

### To-be
The Artifacts tab shows resume and cover letter the same way as before the catalog rewire: hydrated **current** `job_resume` / `cover_letter` via ArtifactEditor (artifact-table SoT). The modal must **not** reference, fetch, or display source / base-resume provenance (no Source base resume panel, no pin gap message, no operative base_resume JSON).

### Repro
1. On a candidate with a recommended job, run Generate Artifacts through completion (tasks succeed; job leaves build-in-progress).
2. Open that job’s Recommended Job Report modal → **Artifacts** top tab.
3. Observe: **Source base resume** / **No pinned base resume for this build** instead of (or crowding out) Job Resume / Cover Letter editors.
4. Confirm `job_data.base_resume_artifact_id` is absent on the job (or unused) — the empty message is provenance UI, not a missing job_resume body signal.

### Root cause
AST-1585 added a JAR **Source base resume** panel (`renderSourceBaseResumeBlock` + `jobBaseResumeArtifactId` / `fetchOperativeBaseResume`) that always renders on the Artifacts pane (in-progress, empty, and populated branches). Parent AST-1588 / AST-1593 explicitly do **not** require source-id or base-resume provenance on the job modal (`no requirement to display source ids in UI this epic`; Susan: do not reference sources on the job modal). When `hasArtifactContent` is false after a finished build (no Generate action for that state), the empty branch returns **only** that panel — so the user sees the wrong provenance gap instead of resume/cover. Even when editors would render, the provenance block remains contrary to epic UI intent.

### Proposed change
Concrete make-fix steps (no judgment calls):

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`:
   - Delete `renderSourceBaseResumeBlock` and every call site in `renderArtifactsPane` (in-progress / empty / populated).
   - Delete state `sourceBaseResume`, `sourceBaseResumeError`, `sourceBaseResumeLoading` and the `useEffect` that calls `fetchOperativeBaseResume` when `activeTopTab === "artifacts"`.
   - Remove imports of `fetchOperativeBaseResume` and `jobBaseResumeArtifactId` from this file.
   - Keep Artifacts pane behavior otherwise: in-progress → Generating… + Cancel; empty → Generate only; populated → `ReportSectionList` + `renderArtifactSection` (ArtifactEditor) for tabs with `artifactHasContent` — same leaf `artifact_key` contract as AST-1593 Stage 3 (no hierarchical key rewrite).

2. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`:
   - If `jobBaseResumeArtifactId` and `fetchOperativeBaseResume` are unused after step 1, delete those two exports (and any imports only they needed). Do **not** change `printResumeVisible` / `printCoverVisible` / `artifactHasContent` / `anyReportArtifactContent` (AST-1593 SoT rules stay).
   - Do **not** remove Contact / candidate operative `base_resume` API surfaces (AST-1585 Contact path stays; this bug is job-modal only).

3. Do **not** add a replacement provenance UI, do **not** surface `source_artifact_ids` or `base_resume_artifact_id` on the job modal, and do **not** reintroduce `resume_content` sibling SoT fallbacks.

⚠️ **Decision:** Remove the AST-1585 JAR provenance panel entirely rather than “fix the empty message.” Epic + Susan forbid source/base-resume references on this modal; the empty pin copy is not a valid substitute for missing job artifact bodies.

### Blast radius
- **JAR Artifacts tab UI** — AST-1585 Stage 3 panel gone; Vitest/bible nodes that assert Source base resume / pin gap / operative JSON on JAR will need Betty revise (`qa-fix` if board says TESTS: REVISE).
- **`recommendedJobReport.tsx` helpers** — shared lib; confirm no other importers of `jobBaseResumeArtifactId` / `fetchOperativeBaseResume` before delete (today: JAR modal only).
- **AST-1593** hydrate leaf load/save, builder `get_job_current`, print visibility — must not regress.
- **AST-1591/1592** table `source_artifact_ids` and tracker citation — backend stays; UI must not re-display that provenance here.
- Contact Estelle / `GET .../operative/base_resume` (AST-1585 Stages 1–2) — untouched.

### What must still hold
- Parent AC6 / AST-1593: UI load and jobs GET for `job_resume` / `cover_letter` use generic current-read / hydrate overlay; not `job_data.artifacts.*` blob SoT.
- Parent Technical scope: no requirement to display source ids in UI this epic; ArtifactEditor still CURRENT (not operative-by-id) for job keys.
- AST-1593 Stage 2: no `resume_content` sibling SoT fallback in ArtifactEditor; `printResumeVisible` stays `job_resume`-only.
- Artifact generation / Generate / Cancel / populated editor strip behavior otherwise unchanged.

## Radia review (AST-1599)

# Radia review-fix — AST-1599 (F7)

`[code-rubric] revision=2`
**Rubric:** code-rubric.v2
**Ticket:** AST-1599
**Publish ref:** `sub/AST-1588/AST-1599-job-modal-hides-resume-cover` @ `292029f5c2fd136fe951a22082c2973abef597a7`
**Diff base:** `origin/ftr/AST-1588-job-artifacts-job-resume-cover-letter...origin/sub/AST-1588/AST-1599-job-modal-hides-resume-cover` (fix slice: AST-1599 product + tests only)
**Parent:** AST-1588 (normal — not orphaned; merge via epic `ftr`, not straight-to-dev)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1599)` on publish ref. |
| orch.git.commit-vocabulary | universal | conforms | `docs` / `test` / `code` / `merge-tests` vocabulary. |
| orch.git.flow-direction-inviolable | universal | conforms | Bug `sub/AST-1588/…` on in-flight epic. |
| orch.git.ftr-sub-topology | universal | conforms | Diff base `ftr/AST-1588-…` per fix-lane. |
| orch.git.merge-on-checkout | universal | conforms | N/A to code. |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history. |
| orch.git.no-dev-agent-branches | universal | conforms | No agent branches. |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree OK. |
| orch.git.three-permanent-branches | universal | conforms | `sub/*` publish ref. |
| orch.pipeline.* (4) | universal | conforms | Fix-lane F7 at Tests Passed. |
| orch.roles.* (5) | universal | conforms | Betty qa-fix + board; engineer product fix. |
| astral.agent.* | scoped | not-applicable | No agent paths. |
| astral.batch.* | scoped | not-applicable | No batch paths. |
| astral.config.* | scoped | not-applicable | No config changes in 1599 product commits. |
| astral.debug.* | scoped | not-applicable | No debug paths. |
| astral.dispatch.* | scoped | not-applicable | No dispatch changes. |
| astral.docs.features-single-file-per-ticket | scoped | discuss | Plan-fix patch appended to `ast-1593-*.md` (process quirk); content is AST-1599-specific. |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty owns tests/bible. |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-tree via Betty pipeline. |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | UI-only fix. |
| astral.layers.import-direction | scoped | conforms | Modal imports lib/utils only; no data/core imports added. |
| astral.layers.scripts-exempt | scoped | not-applicable | No scripts. |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No new hardcoded state lists; leaf `artifact_key` contract preserved. |
| astral.idioms.* | scoped | not-applicable / conforms | No coat-check/auth/consult changes. |
| astral.seed.* | scoped | not-applicable | No seed paths. |
| astral.standards.* (11 applicable) | scoped | conforms | UI-only deletion; no logging/data/utils bends; scope matches plan-fix. |
| astral.state.* | scoped | not-applicable | No state-machine edits. |
| astral.ui.* (3) | scoped | conforms | Files under `src/ui/frontend/`; naming/placement OK. |

**Active set:** 65 statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | No catalog pattern ids in plan-fix patch. |

## Plan-fix adherence

**Proposed change steps 1–3 delivered.**

1. **`JobAnalysisReportModal.tsx`:** `renderSourceBaseResumeBlock`, related state, `useEffect` fetch, and imports removed; `renderArtifactsPane` branches retain Generating/Cancel, Generate-only, and populated `ReportSectionList` without provenance wrapper.
2. **`recommendedJobReport.tsx`:** `jobBaseResumeArtifactId` and `fetchOperativeBaseResume` deleted; `printResumeVisible` / `printCoverVisible` / `artifactHasContent` untouched in code commit.
3. **No replacement provenance UI**; no `source_artifact_ids` / `base_resume_artifact_id` surfacing; no `resume_content` sibling fallback reintroduced.

**Board context:** `[board-joan] CANON: OK`; `[board-betty] TESTS: REVISE` — addressed by qa-fix `[bug-repro]` + revised Vitest.

## Fix-specific checks

### `[bug-repro]` — **OK**

Two tagged tests in `test_JobAnalysisReportModal.test.tsx` (`AST-1599` describe):

| Test | Pins to-be | Pre-fix fail? |
|------|------------|---------------|
| Populated Artifacts (`CANDIDATE_REVIEW`, job_resume + cover_letter) | `queryByText("Source base resume")` absent; gap copy absent; section headers include Job Resume + Cover Letter; zero `/operative/base_resume` calls | Yes — AST-1585 panel always rendered |
| Empty Artifacts (Generate) | No source panel/gap; Generate button present | Yes — empty branch returned source block |

Assertions are concrete (not tautologies). Lib helper unit tests for deleted exports correctly removed.

### `## What must still hold` — **OK**

| Item | Verdict |
|------|---------|
| AST-1593 hydrate/current-read for job_resume/cover_letter (not blob SoT) | **holds** — ArtifactEditor / hydrate paths not modified |
| No source-id UI on job modal | **holds** — panel + fetch removed |
| No `resume_content` sibling SoT in ArtifactEditor | **holds** — not touched |
| `printResumeVisible` job_resume-only | **holds** — only JAR helpers deleted from lib |
| Generate / Cancel / populated editor strip | **holds** — in-progress / empty / populated branches preserved minus provenance wrapper |

**Blast radius:** Contact `GET .../operative/base_resume` coverage remains in `tests/component/ui/api/test_api_candidate.py` (AST-1585); backend citation unchanged.

## Findings

### advisory

- **`if (!generate) return null`** when manifest lacks a Generate action — replaces the old “source block only” empty state. Correct per fix decision (provenance UI was never valid); if a state truly has neither generate nor artifact content, pane is blank — acceptable edge.
- **Full `ftr...sub` three-dot diff is wide** (stacked AST-1596–1598 siblings on branch); **AST-1599 fix slice** is two product files + Vitest/bible — review scoped to that slice.
- **Plan-fix doc location** — patch lives at bottom of `ast-1593-inventory-rewire-job-artifact-consumers.md` per `plan-fix` convention; process-only note.

## What's solid

- Surgical removal of AST-1585 JAR provenance UI that contradicted epic “no source display on job modal.”
- Dead lib exports removed with zero remaining importers.
- `[bug-repro]` directly encodes Susan’s UAT symptom (resume/cover hidden behind source-base-resume message).
- AST-1593 SoT rules and Contact operative API left intact.

## Frame diff

**AST-1599 fix (product):** `JobAnalysisReportModal.tsx` (−provenance panel/state/fetch); `recommendedJobReport.tsx` (−`jobBaseResumeArtifactId`, −`fetchOperativeBaseResume`).

**Tests/bible:** `test_JobAnalysisReportModal.test.tsx` `[bug-repro]` suite; retired AST-1585 JAR + lib helper tests; `docs/test-bible/frontend/components.md` § AST-1599 manifest.

**Not in fix slice:** tracker, api_jobs, database, builder, ArtifactEditor `resume_content` logic.

## Notes for Chuckles

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal AST-1588 UAT-batch | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped) |

context_tokens≈72000

---

```
[code-rubric] PROCEED (Commit: 292029f5) JAR provenance panel removed
```
