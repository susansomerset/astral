<!-- linear-archive: AST-291 archived 2026-06-03 -->

## Linear archive (AST-291)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-291/create-artifacts-interface  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

1. Add Artifacts section to appear above candidate, below Company.
2. Artifacts menu option is visible when all required Candidate context is provided
3. Menu items under Artifacts are:
   * Base Resume Content
   * Company Watch Criteria
   * Job List Criteria
   * Job Description Criteria
   * Get Job Criteria
   * Do Job Criteria
   * Like Job Criteria
4. all of these pages have the same layout:
   1. Create a "sideTab" component that will display a name for the sections, with a flag to indicate if the tabs are editable (they will be for rubrics/criteria, but not for base resume).  Editing includes the sequence they appear in the list (so the candidate can naturally stack rank)
   2. sideTab component has a large text area, just like the new tabbed component we just added.
   3. Each text area displays a single element from artifacts: get_rubric, for example.

In future, we will make these screens more sophisticated to support self-use by the candidate, for now, I just need the thing to work.  ;-)

For the Base Resume Content, it will have these tabs with uneditable names and positions:

* Candidate Name
* Candidate Title
* Candidate Contact Detail
* Professional Summary
* Core Competencies
* Experience
* Prior Experience
* Education & Certifications
* Technical Skills

The Criteria pages will have editable, manually sortable tabs, each will map to a vector for the rubric, and the content will be free text (for now) giving instructions on how to grade for each vector. Users can add and remove tabs from the tab list, down to one tab, up to 15 tabs

When the user closes the window, the collection of criteria is auto-saved to the corresponding candidate_data.artifacts.\* element related to the criteria.

N.B., the users will see "criteria", but these are rubrics.  It's just not a common term outside of academia.

### Comments

_No comments._

---

# ast-291: Create Artifacts Interface — Plan

## Overview

Add an "Artifacts" nav section (between Companies and Candidate) with 7 pages that let users view and edit AI-produced artifacts stored in `candidate_data.artifacts`. All 7 pages share a `SideTabPanel` layout: vertical tabs on the left, large text area on the right.

Two modes:
- **Fixed tabs** (Base Resume Content) — tab labels and positions are immutable; content is editable
- **Editable tabs** (all 6 Criteria pages) — tabs can be renamed, reordered, added (max 15), and removed (min 1); auto-saves on navigation away

**Visibility gate:** Artifacts section appears when candidate reaches `CONTEXT_READY` (same gate as Base Resume and Astral Rubrics in the Candidate section).

---

## Data model

### Base Resume (`artifacts.base_resume`)

Currently a dict produced by `parse_resume_text`, with keys: `name`, `email`, `phone`, `linkedin`, `location`, `timezone`, `professional_summary`, `core_competencies` (list), `experience` (list), `prior_experience` (list), `certs_education` (list), `skills` (list).

The ticket specifies 9 fixed tabs with display labels. Mapping:

| Tab Label | artifact key | Type |
|-----------|-------------|------|
| Candidate Name | `candidate_name` | str |
| Candidate Title | `candidate_title` | str |
| Candidate Contact Detail | `candidate_contact_detail` | str |
| Professional Summary | `professional_summary` | str |
| Core Competencies | `core_competencies` | str |
| Experience | `experience` | str |
| Prior Experience | `prior_experience` | str |
| Education & Certifications | `education_certifications` | str |
| Technical Skills | `technical_skills` | str |

**Resolved:** Keys match the spec tab labels in snake_case (skipping `&`). All values are flat text (strings). The existing `parse_resume_text` task produces different keys (`name`, `certs_education`, `skills`, lists) — those will need a migration or schema update in a future ticket. For now, any existing `base_resume` data from the bootstrap script won't appear under the new keys, which is acceptable for v1.

### Criteria / Rubrics (`artifacts.<key>`)

Each criteria artifact is an array of vectors:

```json
[
  { "label": "Vector Name", "content": "Grading instructions..." },
  { "label": "Another Vector", "content": "..." }
]
```

| Menu Label | artifact key |
|-----------|-------------|
| Company Watch Criteria | `company_prefilter` |
| Job List Criteria | `joblist_rubric` |
| Job Description Criteria | `jobdesc_rubric` |
| Get Job Criteria | `get_rubric` |
| Do Job Criteria | `do_rubric` |
| Like Job Criteria | `like_rubric` |

When no data exists yet, the page initializes with a single empty vector: `[{ "label": "New Criterion", "content": "" }]`.

### Token resolution impact

`{$BASE_RESUME}` resolves via `_value_to_str` which JSON-serializes dicts. The new keys will change the JSON keys visible in prompts — this is intentional and makes the serialized output more readable.

For rubric tokens (`{$GET_RUBRIC}`, etc.), `_value_to_str` will serialize the array of `{ label, content }` objects. This produces readable output: each list item becomes a JSON object. If a formatted rendering is needed later (e.g., markdown headings per vector), we can add a custom resolver — but the JSON form works for v1.

---

## Sub 1: SideTabPanel component

**File:** `src/ui/frontend/src/components/SideTabPanel.tsx`

A reusable component with vertical tabs on the left and a large text area on the right.

### Props

```typescript
interface SideTab {
  id: string
  label: string
  content: string
}

interface SideTabPanelProps {
  tabs: SideTab[]
  editable?: boolean       // default false — labels and order are fixed
  minTabs?: number         // default 1
  maxTabs?: number         // default 15
  onChange: (tabs: SideTab[]) => void
}
```

### Behavior

**Both modes:**
- Click a tab to select it; the right pane shows that tab's content in a textarea
- Editing the textarea updates `content` for the selected tab via `onChange`

**Fixed mode** (`editable=false`):
- Tab labels render as plain text
- No reorder, add, or remove controls

**Editable mode** (`editable=true`):
- Tab labels are inline-editable (click label to rename, blur/enter to confirm)
- Up/down arrow buttons on each tab for manual reorder
- "×" button on each tab to remove (hidden when at `minTabs`)
- "+ Add" button below the tab list (hidden when at `maxTabs`)
- New tabs default to `{ id: uuid, label: "New Criterion", content: "" }`

### CSS

**File:** `src/ui/frontend/src/App.css` — new section `10d. SideTabPanel`

```
.side-tab-panel          — flex container (row)
.side-tab-list           — left column (vertical tab strip)
.side-tab-item           — individual tab row
.side-tab-item.active    — selected tab styling
.side-tab-label          — tab label (text or input)
.side-tab-controls       — reorder/remove buttons
.side-tab-add            — add button
.side-tab-content        — right column (textarea area)
.side-tab-textarea       — the textarea itself (large)
```

---

## Sub 2: ArtifactEditor page component

**File:** `src/ui/frontend/src/pages/Artifacts/ArtifactEditor.tsx`

Generic page that wraps `SideTabPanel` for a specific artifact. Used by all 7 pages.

### Props

```typescript
interface ArtifactEditorProps {
  title: string
  artifactKey: string      // key in candidate_data.artifacts
  fixedTabs?: { id: string; label: string }[]  // if set, tabs are fixed (base resume mode)
}
```

### Behavior

1. On mount, fetches candidate data via `GET /api/candidates/:id`
2. Extracts `candidate_data.artifacts[artifactKey]`
3. For **fixed tabs** (base resume): maps dict keys to `SideTab[]` using tab definitions from `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]`.
4. For **editable tabs** (criteria): maps array directly to `SideTab[]`. If null/empty, initializes with one default tab.
5. `onChange` from `SideTabPanel` updates local state
6. **Fixed tabs (base resume):** explicit Save/Cancel buttons (like other detail pages)
7. **Editable tabs (criteria):** auto-save with 2-second debounce after last change + save on unmount (useEffect cleanup) + beforeunload guard. Visual "Saved" / "Saving..." indicator.
8. Save calls `PUT /api/candidates/:id/data` with `{ artifacts: { [artifactKey]: data } }`
   - For base resume: converts `SideTab[]` back to dict `{ id: content }` (all flat text)
   - For criteria: converts `SideTab[]` to `[{ label, content }]` array

---

## Sub 3: Page wrappers

**Directory:** `src/ui/frontend/src/pages/Artifacts/`

Seven thin files, each rendering `ArtifactEditor` with the right config:

| File | artifactKey | title | mode |
|------|------------|-------|------|
| `BaseResumeContent.tsx` | `base_resume` | Base Resume Content | fixed tabs |
| `CompanyWatchCriteria.tsx` | `company_prefilter` | Company Watch Criteria | editable |
| `JobListCriteria.tsx` | `joblist_rubric` | Job List Criteria | editable |
| `JobDescCriteria.tsx` | `jobdesc_rubric` | Job Description Criteria | editable |
| `GetJobCriteria.tsx` | `get_rubric` | Get Job Criteria | editable |
| `DoJobCriteria.tsx` | `do_rubric` | Do Job Criteria | editable |
| `LikeJobCriteria.tsx` | `like_rubric` | Like Job Criteria | editable |

Each is ~5 lines:
```tsx
import ArtifactEditor from "./ArtifactEditor"
export default function GetJobCriteria() {
  return <ArtifactEditor title="Get Job Criteria" artifactKey="get_rubric" />
}
```

The base resume wrapper fetches tab definitions from `DATA_SHAPES` via the shapes API:
```tsx
export default function BaseResumeContent() {
  return <ArtifactEditor title="Base Resume Content" artifactKey="base_resume" shapesKey="base_resume_structure" />
}
```

---

## Sub 4: NAV_CONFIG + routes

### NAV_CONFIG (`config.py`)

Insert new group between Companies and Candidate:

```python
{
    "label": "Artifacts",
    "visible": "CONTEXT_READY",
    "items": [
        {"label": "Base Resume Content", "path": "/artifacts/base_resume_content"},
        {"label": "Company Watch Criteria", "path": "/artifacts/company_watch_criteria"},
        {"label": "Job List Criteria", "path": "/artifacts/job_list_criteria"},
        {"label": "Job Description Criteria", "path": "/artifacts/job_description_criteria"},
        {"label": "Get Job Criteria", "path": "/artifacts/get_job_criteria"},
        {"label": "Do Job Criteria", "path": "/artifacts/do_job_criteria"},
        {"label": "Like Job Criteria", "path": "/artifacts/like_job_criteria"},
    ],
},
```

### Routes (`routes.tsx`)

Add 7 imports and 7 route entries under a new `// Artifacts` section, between Companies and Candidate.

---

## Sub 5: Existing Candidate pages

The Candidate section currently has stub pages for "Base Resume" (`/candidate/base_resume`) and "Astral Rubrics" (`/candidate/astral_rubrics`). These serve different purposes:
- Candidate Base Resume is the candidate-facing view (future: formatted resume preview)
- Astral Rubrics is the candidate-facing summary of all rubrics

The new Artifacts pages are the editing interface for these artifacts. No changes to the existing Candidate stubs in this ticket — they can be enhanced separately.

---

## File change summary

| File | Change type |
|------|-------------|
| `src/ui/frontend/src/components/SideTabPanel.tsx` | **New** — reusable side-tab component |
| `src/ui/frontend/src/App.css` | Add SideTabPanel styles |
| `src/ui/frontend/src/pages/Artifacts/ArtifactEditor.tsx` | **New** — generic artifact editing page |
| `src/ui/frontend/src/pages/Artifacts/BaseResumeContent.tsx` | **New** — thin wrapper |
| `src/ui/frontend/src/pages/Artifacts/CompanyWatchCriteria.tsx` | **New** — thin wrapper |
| `src/ui/frontend/src/pages/Artifacts/JobListCriteria.tsx` | **New** — thin wrapper |
| `src/ui/frontend/src/pages/Artifacts/JobDescCriteria.tsx` | **New** — thin wrapper |
| `src/ui/frontend/src/pages/Artifacts/GetJobCriteria.tsx` | **New** — thin wrapper |
| `src/ui/frontend/src/pages/Artifacts/DoJobCriteria.tsx` | **New** — thin wrapper |
| `src/ui/frontend/src/pages/Artifacts/LikeJobCriteria.tsx` | **New** — thin wrapper |
| `src/ui/frontend/src/routes.tsx` | Add 7 artifact routes |
| `src/utils/config.py` | Add Artifacts nav group to NAV_CONFIG |

---

## What I won't change

- No backend API changes — uses existing `PUT /api/candidates/:id/data` with merge
- No database schema changes — artifacts are stored in the `candidate_data` JSON column
- No changes to `parse_resume_text` response schema
- No changes to `TOKEN_SOURCES` or `_value_to_str` — existing token resolution stays as-is
- No changes to existing Candidate stub pages (BaseResume, AstralRubrics)

---

## Resolved questions

1. **Base resume keys:** Use spec tab labels in snake_case (skip `&`). Keys: `candidate_name`, `candidate_title`, `candidate_contact_detail`, `professional_summary`, `core_competencies`, `experience`, `prior_experience`, `education_certifications`, `technical_skills`. Existing parse_resume_text output uses different keys — migration is a future task.

2. **Data format:** All values are flat text (strings). No list/array handling needed for v1. The parse_resume_text task currently produces some fields as lists — that will be reconciled when we make the screens more sophisticated.

## Additional UI enhancements (bundled in this ticket)

- **Themed scrollbars**: Light purple track, dark purple thumb, matching the app palette
- **Collapsible nav sections**: Click section header to toggle; default expanded; chevron indicator
- **Multi-column default sort**: ListPage auto-sorts by columns in order; `defaultDesc` flag per column for reverse default (e.g., timesheets)
- **Resizable columns**: Drag column header edges to adjust width; auto-layout preserved until first resize
