<!-- linear-archive: AST-307 archived 2026-06-03 -->

## Linear archive (AST-307)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-307/job-analysis-report-modal-recommended-job-detail  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-312

### Description

React modal opened from the Recommended Jobs list. Replaces the old Job Analysis Report concept (pipeline is now DO→GET→LIKE order). Built entirely on the new CollapsiblePanel component. Sections rendered in order: Job Summary, Full Description, then one panel per agent response task (label from get_task_label() — print_label field in TASK_CONFIG with snake_case Title Case fallback, e.g. grade_get → 'Grade Get'), then Resume Draft panel, then Cover Letter panel. Agent response panels show dot matrix in collapsed header row. Resume Draft panel expands to read-only rendered resume preview; Edit button opens a second modal (modal-on-modal) for editing job_data.artifacts.resume_content sections as text areas. Cover Letter panel expands to directly editable fields inline: Re: line (job_data.artifacts.cover_letter.re_line), body (job_data.artifacts.cover_letter.body), signature text (job_data.artifacts.cover_letter.signature — pre-populated from candidate_data.profile.cover_letter_signature but overridable per job). Print button calls Flask route → opens [builder.py](<http://builder.py>) output in new tab. Implementation note: get_task_label(task_key) helper reads TASK_CONFIG\[task_key\].print_label if present, otherwise derives label as Title Case from snake_case key.

### Comments

#### chuckles — 2026-05-18T19:17:55.620Z
## finish-up (cleanup) — Chuckles

AST-307 is **Done**, not **PR Ready** — skipped formal finish-up gate.

`origin/ftr/AST-307-job-analysis-report-modal-recommended-job` had **0 commits** ahead of `origin/dev` (product already via PR #127). **Deleted** stale feature branch.

— Chuckles

#### susan — 2026-05-04T21:37:27.514Z
**Plan doc:** `docs/features/artifacts/ast-307-job-analysis-report-modal-recommended-job-detail.md`

**Self-assessment:**
- **Scope — MAJOR-CHANGE:** New modal, data load, tabs/panels, artifact editing, print path — coordinates with AST-308/311/312.
- **Conf — Medium:** Ownership split across parallel tickets; handshake before duplicating modal shell.
- **Risk — HIGH:** Wrong saves against `job_data` are high-impact.

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-307-job-analysis-report-modal-recommended-job-detail/docs/features/artifacts/ast-307-job-analysis-report-modal-recommended-job-detail.md

— Katherine (a-plan-linear)

---

# Job Analysis Report Modal — Recommended Job Detail

**Linear:** https://linear.app/astralcareermatch/issue/AST-307/job-analysis-report-modal-recommended-job-detail  
**Feature branch:** `<agent>/ast-307-job-analysis-report-modal-recommended-job-detail`

**`JobsRecommended.tsx`** row click opens **`JobAnalysisReportModal`** (new) with **tabbed editor** for resume/cover letter drafts per **AST-300**/**AST-301**; **AST-312** adds action column — coordinate so row click vs icon click does not double-open. **AST-311** provides job list API shape; **AST-308** may own modal shell — check for duplicate work before creating second modal component.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | `onClick` row → `setSelectedJobId` + modal open; `stopPropagation` on action cells (**AST-312**). | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (name TBD) | Tabs + embed **`ArtifactEditor`** or reuse from candidate artifacts. | ui |
| `src/ui/api/api_jobs.py` | Read paths for `job_data.artifacts.*` already used by **AST-311** — extend only if new fields needed. | ui |
| `src/ui/frontend/src/App.css` | Modal + tab chrome. | ui |

---

## Stage 1: Dependency handshake

**Done when:** Comment on **AST-307** linking **AST-308**/311/312 owners; confirm single modal component ownership.

---

## Stage 2: Modal shell + data load

**Done when:** Opening modal fetches job detail JSON including artifact blobs needed for editors.

---

## Stage 3: Tabbed editors

**Done when:** Resume tab binds to `job_data.artifacts.resume_content` draft; cover letter tab analogous when **AST-301** lands — stub tab with “not generated” if absent.

---

## Stage 4: Save / finalize flows

**Done when:** Matches product spec from **AST-300** (candidate edits before final) — wire save endpoints if separate from autosave.

---

## Stage 5: Verify

**Done when:** `tsc`; click-through from Recommended list; no duplicate modals with **AST-312**.

---

## Execution contract

If **AST-308** already implements modal, **extend** it rather than fork.

---

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
New modal + tabs + job artifact editing.

**Conf — `Medium`**  
Parallel UI tickets (308/311/312) need ordering.

**Risk — `HIGH`**  
Wrong save target could corrupt `job_data`.

---

## Self-review vs ASTRAL_CODE_RULES

§3.5; §1.4 theme tokens for modal chrome. **Conflicts:** coordinate with **AST-312** event propagation.
