# Recommended job report modal — tabs, header, list entry (Recommended Job Modal)

**Linear:** [AST-565](https://linear.app/astralcareermatch/issue/AST-565/recommended-job-report-modal-tabs-header-list-entry-recommended-job)  
**Parent:** [AST-499 — Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-499/recommended-job-modal)  
**Publish ref (origin):** `sub/AST-499/AST-565-recommended-job-report-modal-tabs-header-list-entry`  
**Parent integration ref:** `ftr/AST-499-recommended-job-modal`

Replace the **AST-481** vertical-stack **`JobAnalysisReportModal`** stub with a wide, left-tab **Recommended Job Report** modal (In Review / **`JobDetailModal`** rail pattern). **Row click** on the Recommended list opens this modal; remove the redundant **Jr** row action. Sticky header shows company + candidate contact affordances; tabs cover Job Summary, full JD, JD/DO/GET/LIKE phase consult (Estelle **`take_*`** above **`AgentAnalysisHeader`** vectors), and dynamic artifact editors when `job_data.artifacts` has content. Primary chrome (**Generate Artifacts**, **Cancel**, **Apply**) reads **`jobs.recommended.primary_actions_by_state`** from **`GET /api/state_ui_manifest`** (**AST-562**). **`take_jd`** parsing/render follows **AST-561**.

---

## Prerequisite gate (before Stage 1)

1. On **`dev-kath`**: **`git fetch origin`**; **`git merge origin/dev`** (merge-clean gate: **`BEHIND=0`**, **`origin/dev` ancestor of HEAD**).
2. Merge integration lines **in order** (resolve conflicts on **`dev-kath`**, commit merge if needed):
   - **`origin/ftr/AST-499-recommended-job-modal`**
   - **`origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt`**
   - **`origin/sub/AST-499/AST-562-generate-artifacts-cancel-job-transitions-api`**
   - **`origin/sub/AST-499/AST-565-recommended-job-report-modal-tabs-header-list-entry`**
3. Confirm **`origin/sub/AST-499/AST-565-recommended-job-report-modal-tabs-header-list-entry`** exists (**§4a** — do not create).
4. Read sibling plans on the merged tips: **AST-561** (`take_jd` field), **AST-562** (`JOBS_RECOMMENDED_PRIMARY_ACTIONS`, `POST …/generate_artifacts`, `POST …/cancel_artifact_build`).
5. If **`primary_actions_by_state`** or **`take_jd`** in **`TASK_CONFIG["analysis_upshot"]["response_schema"]`** is missing after merges, **stop** — comment on **AST-565** naming missing blocker SHA; do not invent parallel APIs or schema fields.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOBS_RECOMMENDED_REPORT_PHASE_TABS`, `JOBS_RECOMMENDED_ARTIFACT_TABS`, extend `JOBS_RECOMMENDED_PRIMARY_ACTIONS` with **Apply**; expose via `build_state_ui_manifest()` | utils |
| `src/ui/api/api_jobs.py` | `PUT …/artifacts/cover_letter`, `PUT …/artifacts/application_responses` (mirror **AST-553** resume PUT) | ui |
| `src/ui/frontend/src/lib/analysisUpshot.ts` | Add **`take_jd`** to type + parser (**AST-561** contract) | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.ts` | Tab builders, grade-dot tab labels, artifact presence helpers | ui |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Mirror new manifest keys under `jobs.recommended` | ui |
| `src/ui/frontend/src/components/SideTabPanel.tsx` | Optional `renderTabLabel?: (tab) => ReactNode` | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Sticky header: title, company site, copyable candidate links, primary action slot | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Rebuild: tab rail + panes; remove vertical **`CollapsiblePanel`** stack | ui |
| `src/ui/frontend/src/components/CandidateJobRowActions.tsx` | Drop **Jr** when `showViewAnalysis={false}` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Generalize `jobPersistence` to `{ jobId, artifactKey, onSaved }` + correct PUT path | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Row click → report modal; remove **`JobDetailModal`** row entry + **Jr** wiring | ui |
| `src/ui/frontend/src/App.css` | Report shell: sticky header, tab label grade dots, in-progress chrome | ui |

**Out of scope (ticket boundaries):** `take_jd` schema/prompt (**AST-561**), generate/cancel tracker+routes (**AST-562**), Recommended list grouping (**AST-522** — Done), consult scoring/dispatch, server HTML builder, new dispatch rows, **`tests/`**, **`docs/ASTRAL_TEST_BIBLE.md`** (Betty after **Code Complete**).

**Spike / Playwright:** none.

---

## Stage 1: Config — report tab manifest + Apply primary action

**Done when:** `build_state_ui_manifest()["jobs"]["recommended"]` includes `report_phase_tabs`, `report_artifact_tabs`, and `primary_actions_by_state` with **Apply** on **`CANDIDATE_REVIEW`**; duplicate `jobs.recommended` dict key in `build_state_ui_manifest()` is gone (single block); `python3 -m py_compile src/utils/config.py` passes.

1. In **`src/utils/config.py`**, after **`JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS`**, add:

   ```python
   JOBS_RECOMMENDED_REPORT_PHASE_TABS = [
       {"tab_id": "phase_jd", "nav_label": "JD", "grades_field": "jd_grades", "take_key": "take_jd"},
       {"tab_id": "phase_do", "nav_label": "DO", "grades_field": "do_grades", "take_key": "take_do"},
       {"tab_id": "phase_get", "nav_label": "GET", "grades_field": "get_grades", "take_key": "take_get"},
       {"tab_id": "phase_like", "nav_label": "LIKE", "grades_field": "like_grades", "take_key": "take_like"},
   ]

   JOBS_RECOMMENDED_ARTIFACT_TABS = [
       {"tab_id": "artifact_resume", "nav_label": "Resume", "artifact_key": "resume_content", "shapes_key": None, "use_resume_structure": True},
       {"tab_id": "artifact_cover", "nav_label": "Cover Letter", "artifact_key": "cover_letter", "shapes_key": "cover_letter", "use_resume_structure": False},
       {"tab_id": "artifact_application", "nav_label": "Application", "artifact_key": "application_responses", "shapes_key": None, "use_resume_structure": False},
   ]
   ```

   Assert each **`grades_field`** is a key in **`JOBS_UI_GRADE_RUBRIC`**.

2. Extend **`JOBS_RECOMMENDED_PRIMARY_ACTIONS`** (from **AST-562**) with:

   ```python
   "CANDIDATE_REVIEW": [
       {
           "action_key": "apply",
           "label": "Apply",
           "method": "CLIENT",
           "path_suffix": "job_link",
       },
   ],
   ```

   **`method: "CLIENT"`** means no POST — UI opens **`job.job_link`** in a new tab when the action runs.

3. In **`build_state_ui_manifest()`**, ensure **one** `"recommended"` object under `"jobs"` containing **`sections`**, **`phase_score_columns`**, **`primary_actions_by_state`** (from **AST-562**), plus:

   ```python
   "report_phase_tabs": list(JOBS_RECOMMENDED_REPORT_PHASE_TABS),
   "report_artifact_tabs": list(JOBS_RECOMMENDED_ARTIFACT_TABS),
   "report_fixed_tabs": [
       {"tab_id": "summary", "nav_label": "Job Summary"},
       {"tab_id": "jd_full", "nav_label": "Job Description"},
   ],
   ```

4. Run **`python3 -m py_compile src/utils/config.py`**.

⚠️ **Decision:** Phase/artifact tab metadata lives in config (**§1.4**) so nav layout can change without rewriting pane logic; **`tab_id`** strings are stable React keys. **`take_key`** maps to **`analysis_upshot`** fields (**AST-561** adds **`take_jd`**).

---

## Stage 2: `StateUiContext` + `analysisUpshot.ts` + `recommendedJobReport.ts`

**Done when:** `cd src/ui/frontend && npx tsc -b --noEmit` passes; **`parseAnalysisUpshot`** accepts payloads with **`take_jd`**; helpers export tab-label grade dots and artifact-nonempty checks.

1. In **`StateUiContext.tsx`**, extend **`StateUiManifest["jobs"]["recommended"]`** with optional arrays matching Stage 1 keys: **`primary_actions_by_state`**, **`report_fixed_tabs`**, **`report_phase_tabs`**, **`report_artifact_tabs`** (typed fields, not `[key: string]: unknown`).

2. In **`analysisUpshot.ts`**:
   - Add **`take_jd: string`** to **`AnalysisUpshot`** (after **`take_like`**, before **`whole_jd_upshot`**).
   - In **`parseAnalysisUpshot`**, require **`typeof raw.take_jd === "string"`** (same as other **`take_*`**).
   - Include **`take_jd`** in **`hasSubstantiveContent`** headline check.

3. Create **`src/ui/frontend/src/lib/recommendedJobReport.ts`** with:

   - **`export type ReportPrimaryAction`** — mirror manifest action objects (`action_key`, `label`, `method`, `path_suffix`).
   - **`export function primaryActionsForState(manifest, state: string): ReportPrimaryAction[]`** — read **`manifest?.jobs.recommended.primary_actions_by_state[state] ?? []`**.
   - **`export function artifactHasContent(artifacts: unknown, key: string): boolean`** — true when **`artifacts[key]`** is a non-empty object (dict with any non-empty string value) or non-empty array.
   - **`export function buildPhaseTabGradeDots(job, gradesField, rubricArtifactKey, candidateArtifacts): ReactNode`** — use **`buildJobListRubricColumnsFromArtifact`**, **`sortJobListRubricColumns`**, and the **`gradeAndConfidenceForCol`** pattern from **`JobsInReview.tsx`** (extract shared **`gradeAndConfidenceForCol`** into this file or import from a small shared helper in **`rubricDisplay.ts`** if duplication exceeds ~15 lines). Render **`span.grade-dot`** elements in **importance-desc** order only (no vector names in the rail — parent: `GET: ● ● ● ●`). Return **`null`** when no grades.
   - **`export function formatPhaseTabNavLabel(prefix: string, dots: ReactNode): ReactNode`** — e.g. **`<>JD {dots}</>`** with **`className="recommended-report-tab-label"`**.

4. Run **`cd src/ui/frontend && npx tsc -b --noEmit`**.

⚠️ **Decision:** Grade dots on nav tabs reuse list/criteria **`.grade-dot`** CSS (**§3.5** naming) rather than inventing a second badge component.

---

## Stage 3: `SideTabPanel` label hook + header component + CSS

**Done when:** **`SideTabPanel`** can render custom tab labels; **`RecommendedJobReportHeader`** renders with sticky layout; modal wide card shows header above rail.

1. In **`SideTabPanel.tsx`**, add optional prop:

   ```typescript
   renderTabLabel?: (tab: SideTab) => ReactNode
   ```

   Default: **`renderTabLabel ?? (t => t.label)`** inside the rail item (replace plain **`{tab.label}`** span).

2. Create **`RecommendedJobReportHeader.tsx`**:
   - Props: **`jobTitle`**, **`companyName`**, **`companyWebsite: string | null`**, **`jobLink: string | null`**, **`jobState`**, **`profileLinks: Array<{ key: string; label: string; value: string; copyable?: boolean }>`**, **`primaryAction: ReportPrimaryAction | null`**, **`onPrimaryAction: () => void`**, **`primaryBusy: boolean`**, **`stateLabel?: string`** (manifest section label for **`BUILD_ARTIFACTS`** → show **In Progress** subtext).
   - Layout: **`div.recommended-report-header`** — row 1 title + state; row 2 company name + external link when **`companyWebsite`**; row 3 candidate links — email/github/linkedin as **`button.recommended-report-copy-link`** calling **`navigator.clipboard.writeText`** with toast or inline **Copied** (pattern from **`AdminDataManagement.tsx`** clipboard one-liner); row 4 primary action button (**`modal-btn save`**) when **`primaryAction`** set, disabled when **`primaryBusy`** or missing **`jobLink`** for **Apply**.
   - Do **not** fetch here — parent passes resolved strings.

3. In **`App.css`** (section **8c** area), add:
   - **`.recommended-report-shell`** — flex column; **`max-height: min(80vh, 900px)`**.
   - **`.recommended-report-header`** — **`position: sticky; top: 0; z-index: 2`**, background **`var(--bg-card)`**, border-bottom, padding.
   - **`.recommended-report-body .side-tab-panel`** — flex **`1 1 auto`**, **`min-height: 0`** (scroll in **`.side-tab-content`** only).
   - **`.recommended-report-tab-label .grade-dot`** — smaller font (11px), inline-flex, margin-left 2px.
   - **`.recommended-report-empty`** — muted empty copy (reuse **`.job-analysis-upshot-empty`** color).

4. Run **`cd src/ui/frontend && npx tsc -b --noEmit`**.

---

## Stage 4: Rebuild `JobAnalysisReportModal` — tab shell + summary/JD/phase panes

**Done when:** Opening the modal shows left tabs (**Summary**, **Job Description**, JD/DO/GET/LIKE when upshot exists), sticky header, manifest-driven primary button; no vertical **`UpshotRenderer`** stack; jobs without **`analysis_upshot`** show empty states without throw.

1. In **`JobAnalysisReportModal.tsx`**, replace the body layout (keep **`Modal`** **`size="wide"`**, **`load`**, error handling):

   **Data loads (inside existing `load` callback after job JSON):**
   - When **`job.company`** is non-empty, **`GET /api/companies/${encodeURIComponent(job.company)}`** → stash **`company_website`** in component state (ignore 404 — header omits link).
   - Read **`useCandidate()`** selected candidate **`candidate_data.profile`** for **`contact_email`**, **`reply_email`**, **`linkedin_url`**, **`github`** → build **`profileLinks`** (skip empty strings).

   **Tab list construction** (memo on job + manifest + candidate artifacts):
   - Start with manifest **`report_fixed_tabs`**: always **`summary`**, **`jd_full`**.
   - Append **`report_phase_tabs`** entries **only when** **`parseAnalysisUpshot(job_data.analysis_upshot)`** is non-null (phase tabs hidden when no upshot — AC #8).
   - Append **`report_artifact_tabs`** entries **only when** **`artifactHasContent(job_data.artifacts, artifact_key)`** for each row.
   - Map each row to **`SideTab`** `{ id: tab_id, label: nav_label, content: "" }` — phase tabs use **`renderTabLabel`** with **`buildPhaseTabGradeDots`** (pass grades from flattened job fields: read **`job_data[grades_field]`** or top-level if API already flattened in detail response — prefer **`job_data`** first, then top-level job key).

   **Shell JSX:**

   ```tsx
   <div className="recommended-report-shell">
     <RecommendedJobReportHeader … />
     <div className="recommended-report-body">
       <SideTabPanel tabs={tabs} renderTabLabel={…} renderContent={renderReportPane} />
     </div>
   </div>
   ```

   **`renderReportPane(tabId)`** panes:
   - **`summary`**: **`whole_jd_upshot`** as prominent paragraph; below, optional **Noteworthy Caveats** (`upshot.caveats` list) and **Questions to Ask** (`upshot.candidate_questions` list) when non-empty; if no upshot, **`.recommended-report-empty`**: **No analysis upshot on file.**
   - **`jd_full`**: full JD text — **`job_data.job_description`**, trim, **`replace(/\n{3,}/g, "\n\n")`**, **no `slice(4000)`** (AC: full JD tab).
   - **`phase_jd` / `phase_do` / `phase_get` / `phase_like`**: (1) **Estelle's Thoughts** — **`UpshotStringBlock`** heading **`snakeCaseToTitle(take_key)`**, body from **`upshot[take_key]`**; (2) **`AgentAnalysisHeader`** with grades from **`job_data[grades_field]`** (array form) and **`rubricArtifact`** from **`manifest.jobs.grade_rubric_by_field[grades_field]`** resolved against candidate **`artifacts`**; empty take → omit block; empty grades → show **No consult detail on file.** under thoughts.
   - Remove old **`UpshotRenderer`** vertical ordering ( **`take_get` before `take_do`** etc.) — phase content lives only on phase tabs; summary tab owns **`whole_jd_upshot`** + global caveats/questions.

2. **Primary action wiring** (manifest-driven, no hardcoded state→label map):
   - **`const actions = primaryActionsForState(manifest, job.state)`** — use **`actions[0]`** only (v1 one primary button).
   - **`generate_artifacts`**: **`POST /api/jobs/${jobId}/generate_artifacts`** → on success **`load()`** + **`onRefresh?.()`**; set **`primaryBusy`** during fetch; on 409 show error inline in modal.
   - **`cancel_build`**: **`POST /api/jobs/${jobId}/cancel_artifact_build`** — same refresh pattern.
   - **`apply`** (**`method === "CLIENT"`**): **`window.open(job.job_link, "_blank", "noopener,noreferrer")`** when **`job.job_link`** truthy; else disable button.

3. Remove from this modal:
   - Footer **`Applied`** button and **`CandidateActionNotesModal`** / **`runAction("applied")`** — terminal **Applied** stays on list row (**AST-312**).
   - **`phaseEAgentStory`** **`CollapsiblePanel`** map — out of scope for Recommended report v1 (parent: skip state history diagram; agent story not in AC).
   - Inline **`entity-summary`** Company/State/Updated rows (superseded by header).

4. Keep **`showResumeDraft`** block **out** of this pass — resume moves to artifact tab in Stage 5 (remove AST-553 inline draft section from modal body).

5. Run **`cd src/ui/frontend && npx tsc -b --noEmit`**.

⚠️ **Decision:** Phase tabs require valid **`analysis_upshot`** object (parser gate) even if individual **`take_*`** strings are empty — matches **AST-561** required-string schema. Summary tab still renders with only **`whole_jd_upshot`**.

---

## Stage 5: Artifact tabs — API PUT + `ArtifactEditor` job persistence

**Done when:** When **`job_data.artifacts`** holds resume/cover/application content, corresponding nav tabs appear with edit/save; saves persist via job PUT routes; **`npx tsc -b --noEmit`** passes.

1. In **`api_jobs.py`**, add routes (same auth/error pattern as **`put_job_resume_content`**):

   **`PUT /api/jobs/<astral_job_id>/artifacts/cover_letter`**
   - Body **`{ "cover_letter": <dict> }`**; validate dict; call **`save_job_artifact_cover_letter(astral_job_id, body)`** from tracker.
   - Import **`save_job_artifact_cover_letter`** alongside existing tracker imports.

   **`PUT /api/jobs/<astral_job_id>/artifacts/application_responses`**
   - Body **`{ "application_responses": <dict> }`**; validate dict; call **`save_job_data(astral_job_id, {"artifacts": {"application_responses": body}}, merge=True)`** via tracker **`save_job_data`** (no dedicated tracker helper yet — inline merge in route through **`save_job_data`** import).

2. In **`ArtifactEditor.tsx`**, change **`jobPersistence`** type to:

   ```typescript
   jobPersistence?: { jobId: string; artifactKey: string; onSaved?: () => void }
   ```

   - Load job artifacts from **`GET /api/jobs/:id`** → **`job_data.artifacts[artifactKey]`** (not hardcoded **`resume_content`**).
   - Save URL: **`PUT /api/jobs/${jobId}/artifacts/${artifactKey}`** with body **`{ [artifactKey]: buildPayload(t) }`**.
   - Keep **`useCandidateResumeStructure`** + **`structureSections`** for resume tab only.

3. In **`JobAnalysisReportModal.tsx`** **`renderReportPane`**, for each visible artifact tab from manifest:
   - **`artifact_resume`**: **`ArtifactEditor`** with **`artifactKey="resume_content"`**, **`useCandidateResumeStructure`**, **`structureSections`** from existing resume-structure fetch (keep **`useEffect`** on **`selectedId`** from current modal).
   - **`artifact_cover`**: **`ArtifactEditor`** with **`artifactKey="cover_letter"`**, **`shapesKey="cover_letter"`**, **`taskKey="craft_cover_letter"`** (Generate hidden via **`jobPersistence`** — no Generate in job mode).
   - **`artifact_application`**: **`ArtifactEditor`** with **`artifactKey="application_responses"`**, **`taskKey="propose_application_responses"`**, rubric/freeform mode (no **`shapesKey`**) — renders editable key/value text areas from object keys present in stored blob.

4. Run **`python3 -m py_compile src/ui/api/api_jobs.py`** and **`cd src/ui/frontend && npx tsc -b --noEmit`**.

⚠️ **Decision:** Application responses use generic dict editor (rubric-mode **`ArtifactEditor`**) because **`artifact_shapes`** has no fixed **`application_responses`** block yet — display/edit stored keys only, no invented schema fields.

---

## Stage 6: Recommended list entry — row click + remove **Jr**

**Done when:** Clicking a Recommended row opens **`JobAnalysisReportModal`**; **`JobDetailModal`** is not opened from row click; **Jr** button absent; **Sk** and post-applied row actions unchanged.

1. In **`JobsRecommended.tsx`**:
   - Remove **`viewingId`** state and **`<JobDetailModal …>`** mount.
   - Change row **`onClick`** from **`setViewingId`** to **`setReportId(job.astral_job_id)`**.
   - On **`CandidateJobRowActions`**, pass **`showViewAnalysis={false}`** (new prop) and **remove **`onViewAnalysis`** prop**.

2. In **`CandidateJobRowActions.tsx`**:
   - Add optional **`showViewAnalysis?: boolean`** default **`true`**.
   - In the **`REVIEW_LIKE`** branch, render **Jr** only when **`showViewAnalysis !== false && onViewAnalysis`**.

3. Manual sanity (engineer, pre-Betty): Recommended page → row click opens tabbed modal; **Sk** still works; **Jr** gone.

4. Run **`cd src/ui/frontend && npx tsc -b --noEmit`**.

---

## Stage 7: Verify + Betty handoff

**Done when:** Compile gates pass; Linear **Code Complete** comment lists Betty manifest extensions (engineer does **not** edit **`tests/`**).

1. Run:

   ```bash
   python3 -m py_compile src/utils/config.py src/ui/api/api_jobs.py
   cd src/ui/frontend && npx tsc -b --noEmit
   ```

2. Linear comment for Betty (**Code Complete**): extend Vitest **`test_JobAnalysisReportModal.test.tsx`**, **`test_JobsRecommended.test.tsx`**, **`test_CandidateJobRowActions.test.tsx`**, **`test_ArtifactEditor.test.tsx`**; pytest **`test_api_jobs.py`** for new PUT routes; **`test_config.py`** for report manifest keys + **Apply** action.

---

## Execution contract (for the developer agent)

- Execute **Stages 1 → 7** in order; **one commit per stage** on **`dev-kath`**, then Joan **`store-code-commit`** to **`origin/sub/AST-499/AST-565-recommended-job-report-modal-tabs-header-list-entry`** after each stage (**build-astral** §6).
- Do **not** edit **`tests/`** or **`ASTRAL_TEST_BIBLE.md`**.
- Do **not** reimplement **AST-561** / **AST-562** server work.
- Blocking questions → parent **AST-499** thread:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Replaces the report modal shell, adds config manifest slices, two job artifact PUT routes, list entry behavior, and a new header component across **`config.py`**, API, and multiple frontend modules.

**Conf:** `Medium` — Patterns exist (**`SideTabPanel`**, **`AgentAnalysisHeader`**, **AST-562** manifest actions, **AST-553** job persistence), but tab assembly, grade-dot rail labels, and artifact generalization require careful integration with merged sibling branches.

**Risk:** `Medium` — Recommended triage UX regresses if row click, primary actions, or upshot empty states break; wrong merge order without **AST-561/562** tips would ship a modal that cannot Generate/Cancel or render **`take_jd`**.

---

## Self-review against ASTRAL_CODE_RULES

| Rule | Plan compliance |
|------|-----------------|
| **§1.3 DRY** | Reuses **`SideTabPanel`**, **`AgentAnalysisHeader`**, **`ArtifactEditor`**, **`buildJobListRubricColumnsFromArtifact`**; shared grade matching extracted to **`recommendedJobReport.ts`**. |
| **§1.4 config SSOT** | Tab order, phase keys, primary actions (including **Apply**) and artifact tab defs in **`config.py`** / manifest — not hardcoded TS state maps. |
| **§2.1 config** | No new task keys; extends existing **`JOBS_RECOMMENDED_*`** blocks only. |
| **§2.4 batch** | No batch changes; cancel API owned by **AST-562**. |
| **§2.6 state machine** | UI triggers **AST-562** POST routes only; **Apply** is client navigation. |
| **§3.3 imports** | API routes call tracker only; frontend uses **`api()`** fetch wrappers. |
| **§3.5 naming** | **`recommendedJobReport.ts`**, **`RecommendedJobReportHeader`**, CSS **`recommended-report-*`** prefix; **`take_jd`** matches **AST-561**. |

No conflicts requiring **`conf-!!-NONE`**.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-499/AST-565-recommended-job-report-modal-tabs-header-list-entry`  
**Review doc commit:** (Joan publish SHA appended after `store-review-commit`)

### What's solid

- **Plan fidelity / AC:** Tabbed **`JobAnalysisReportModal`** with manifest-driven fixed/phase/artifact tabs; **`take_jd`** + Estelle thoughts above **`AgentAnalysisHeader`** on phase panes; grade dots in vector-importance order on rail labels; full JD tab (no 4k slice); sticky **`RecommendedJobReportHeader`** with company site + copyable profile links; **`JobsRecommended`** row click opens report and **Jr** is gone; primary actions (**Generate Artifacts**, **Cancel**, **Apply**) read **`primary_actions_by_state`** — no parallel TS action map.
- **§1.4 / §2.1 config SSOT:** **`JOBS_RECOMMENDED_REPORT_*`**, **`report_fixed_tabs`**, and **Apply** on **`CANDIDATE_REVIEW`** live in **`config.py`** / **`build_state_ui_manifest()`** with rubric asserts on **`grades_field`**.
- **§3.3 layers:** New PUT routes delegate to **`tracker`** only; frontend uses **`api()`** wrappers; no **`src.data`** in UI modules touched for this ticket.
- **Sibling boundaries:** Consumes **AST-562** POST routes and manifest actions (not **`approve_artifacts`**); **`take_jd`** parser field aligns with **AST-561** schema on the same publish tip.
- **Tests (Betty):** Vitest covers tab rail, phase content, grade dots, header links, Generate/Apply wiring, empty upshot, artifact tab; pytest covers new PUT routes and manifest keys.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `JobAnalysisReportModal.tsx` — `inProgressSubtext` | Hardcoded `job.state === "BUILD_ARTIFACTS" ? "In Progress"` duplicates manifest **`sections`** label already resolved via **`stateSectionLabel`**. **§3.2 G1** prefers config/manifest for state chrome — drop the override and use **`stateSectionLabel`** only (or a manifest key if copy must differ). |
| **discuss** | `JobAnalysisReportModal.tsx` — `tabs` useMemo | When **`manifest`** is null (e.g. manifest fetch error), modal shows **"No report tabs available"** even if job payload loaded. **`JobsRecommended`** gates on **`loadState`**, but modal is reusable — consider empty-state copy that distinguishes manifest failure vs missing upshot. |
| **advisory** | `RecommendedJobReportHeader.tsx` | Fallback **`jobState.replace(/_/g, " ")`** when **`stateLabel`** absent — acceptable if manifest always ready; document or remove if modal never mounts without manifest. |
| **advisory** | Plan vs ship | Plan Stage 2 names **`recommendedJobReport.ts`**; shipped **`recommendedJobReport.tsx`** because helpers return **`ReactNode`** — harmless. |

No **fix-now** items for **resolve-astral**.

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| Remove redundant **`BUILD_ARTIFACTS` / "In Progress"** override; rely on manifest **`sections`** label | Katherine | One-line delete in **`JobAnalysisReportModal`** unless Susan wants different copy than manifest |
| Optional: clearer modal empty state when **`manifest`** is null | Katherine | Low priority — list page already blocks |
| Proceed **resolve-astral** (doc-only nits above) | Katherine | No application blockers |

---

## Resolution

**2026-06-02 — resolve-astral (Katherine)**

Radia review had no **fix-now** items. Addressed **discuss** nits:

1. **`JobAnalysisReportModal.tsx`:** Removed hardcoded `BUILD_ARTIFACTS` → `"In Progress"` override; header **`stateLabel`** uses manifest **`sections`** via **`stateSectionLabel`** only (**§3.2 G1**).
2. **`JobAnalysisReportModal.tsx`:** Empty tab rail distinguishes missing manifest (**"Report layout unavailable…"**) from an otherwise empty tab list.

Radia **advisory** items (header fallback label, `.tsx` vs `.ts` plan name) left unchanged — acceptable per review.
