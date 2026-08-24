# AST-1454 — Job Detail skipped-field editors

**Linear:** [AST-1454](https://linear.app/astralcareermatch/issue/AST-1454/job-detail-skipped-field-editors-when-a-job-is-in-a-skipped-state-make)  
**Parent:** [AST-1446](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable)  
**Publish ref:** `sub/AST-1446/AST-1454-job-detail-skipped-field-editors`

When Job Detail loads a job whose GET payload has `fields_editable: true` (AST-1453), the Info tab’s title, link, and state become editable controls and the Job Description tab always offers a textarea (including empty JD). Save calls `PUT /api/jobs/<astral_job_id>` from #1 and refreshes the modal plus the list via `onRefresh`. Non-editable jobs stay display-only. Agent story tabs, Copy, and Skip This Job stay as they are today. Does not implement persist/API (sibling AST-1453).

## Scope (from ticket)

**Implements:** Job Detail chrome only — editable title, link, job description, and state when the API says the job is field-editable; empty JD still shows an editor; Save uses #1; non-skipped / non-editable stay display-only; Copy / Skip This Job unchanged.

**Boundaries:** Does not own persist/API (#1). Does not edit Recommended Job Report. Does not make agent responses, grades, artifacts, company, or timestamps editable.

Every file and change below stays inside that surface.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Extend `JobDetail` with `fields_editable` / `legal_next_states`; draft editors for title/link/state/JD; always show JD tab when editable; Modal `onSave` + explicit `dirty`; PUT save + error display; call `onRefresh` after successful persist | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Pass `onRefresh={load}` into `JobDetailModal` | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Pass `onRefresh={load}` into `JobDetailModal` | ui |

**Do not touch:** `src/ui/api/api_jobs.py`, `src/core/tracker.py`, `src/utils/config.py`, `JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx`, `AgentStoryTab.tsx`, `Modal.tsx`, `copyJobSnapshot.ts`, Skip / Copy handler bodies or labels, `JobsRecommended.tsx`, `tests/**`, `docs/test-bible/**`.

**Prerequisite (AST-1453):** After `sync-child.sh`, `GET /api/jobs/<id>` must return `fields_editable` and `legal_next_states`, and `PUT /api/jobs/<id>` must exist (sibling #1). If either is missing on the worktree tip, **stop** and comment on parent AST-1446 with the 🛑 Stage blocked format — do **not** reimplement persist or invent a TypeScript skipped-state list.

## Stage 1: Editable Info + Save (PUT) + list refresh wiring

**Done when:** Opening a job with `fields_editable: true` shows text inputs for title and link and a state `<select>` of `legal_next_states` (plus keep-current); Modal footer Save (`btn primary`) PUTs the draft and reloads the job from the response; `onRefresh` runs so Skipped/In Review lists refresh; a job with `fields_editable: false` (or missing) still shows today’s read-only Info rows; Copy and Skip This Job markup/handlers/labels are unchanged; agent story tabs remain read-only `AgentStoryTab`.

1. **Prerequisite check:** In the epic worktree after sync, confirm `src/ui/api/api_jobs.py` contains `_attach_skipped_edit_meta` and `persist_skipped_edits` (PUT). If absent, stop per Prerequisite above.

2. In `src/ui/frontend/src/pages/JobsSkipped.tsx`, change the `JobDetailModal` mount to:

```tsx
<JobDetailModal
  jobId={viewingId}
  onClose={() => { setViewingId(null); load() }}
  onRefresh={load}
/>
```

3. In `src/ui/frontend/src/pages/JobsInReview.tsx`, apply the same `onRefresh={load}` prop (same `onClose` pattern as today).

4. In `src/ui/frontend/src/components/JobDetailModal.tsx`, extend `JobDetail`:

```ts
interface JobDetail {
  astral_job_id: string
  job_title: string | null
  company: string
  job_link: string | null
  state: string
  state_changed_at: string | null
  created_at: string | null
  state_history?: Array<{ to_state?: string; timestamp?: string }>
  job_data?: Record<string, unknown>
  agent_story?: AgentStoryEntry[]
  fields_editable?: boolean
  legal_next_states?: string[]
}
```

5. Add draft state and helpers inside `JobDetailModal` (not in a new file):

- `type FieldDraft = { job_title: string; job_link: string; job_description: string; state: string }`
- `const [draft, setDraft] = useState<FieldDraft | null>(null)`
- `const [baseline, setBaseline] = useState<FieldDraft | null>(null)`
- `const [saving, setSaving] = useState(false)`
- `const [saveError, setSaveError] = useState<string | null>(null)`
- Helper `draftFromJob(j: JobDetail): FieldDraft` reads:
  - `job_title: j.job_title ?? ""`
  - `job_link: j.job_link ?? ""`
  - `job_description: String(((j.job_data as Record<string, unknown> | undefined)?.job_description) ?? "")`
  - `state: j.state`
- After a successful GET in `load`, if `res.ok`: `const data = await res.json() as JobDetail`; `setJob(data)`; `const d = draftFromJob(data)`; `setDraft(d)`; `setBaseline(d)`; `setSaveError(null)`.
- `const fieldsEditable = Boolean(job?.fields_editable)`
- `const isDraftDirty = Boolean(fieldsEditable && draft && baseline && (
    draft.job_title !== baseline.job_title
    || draft.job_link !== baseline.job_link
    || draft.job_description !== baseline.job_description
    || draft.state !== baseline.state
  ))`

⚠️ **Decision:** Editability comes only from GET `fields_editable` (server / `SKIPPED_STATES`). Do not import or hardcode skipped-state names in React. Empty / missing `fields_editable` means display-only.

6. Implement `async function handleSave()` on `JobDetailModal`:

- If `!jobId || !draft || !fieldsEditable || saving`, return.
- `setSaving(true)`; `setSaveError(null)`.
- Body: always include `job_title`, `job_link`, `job_description` from `draft`. Include `state` only when `draft.state !== (job?.state ?? "")`.
- `const res = await api(\`/api/jobs/${encodeURIComponent(jobId)}\`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })`
- Parse JSON once: `const body = await res.json().catch(() => ({}))` as `Record<string, unknown>`.
- If `res.ok`: treat `body` as `JobDetail`; `setJob(body)`; `const d = draftFromJob(body)`; `setDraft(d)`; `setBaseline(d)`; `onRefresh?.()`; then `setSaving(false)` and return.
- If not ok: `const msg = typeof body.error === "string" ? body.error : "Save failed"`.
  - If `msg.startsWith("Invalid transition")` or `msg.includes("not in allowed list")` or `msg === "Job is not in a skipped state"`: re-`load()` (await the existing `load` callback) then `onRefresh?.()`, then `setSaveError(msg)` (fields may already be persisted per AST-1453 ordering; leave-skipped race drops edit mode on reload).
  - Else: `setSaveError(msg)` only (no reload).
- `finally`: `setSaving(false)`.

⚠️ **Decision:** Do not toast. Inline `saveError` only. Do not close the modal on save success or failure (operator may keep editing). List freshness is `onRefresh`, not forced close.

7. Pass into `Modal`:

```tsx
<Modal
  open={!!jobId}
  onClose={onClose}
  title={job?.job_title || job?.company || "Job Detail"}
  size="wide"
  dirty={isDraftDirty}
  onSave={fieldsEditable ? () => { void handleSave() } : undefined}
>
```

Do not set `showFooter={false}`. When not editable, omit `onSave` (Cancel-only footer, same as today’s Modal default). Disable the Save button visually by not rendering a second Save — Modal’s Save is enough; while `saving`, Modal does not disable Save itself — guard inside `handleSave` with the `saving` flag (double-click safe). Optional: leave as is; do not edit `Modal.tsx`.

8. Update `InfoTab` props to receive editable draft controls:

- Pass `fieldsEditable`, `draft`, `legalNextStates: job?.legal_next_states ?? []`, `saveError`, `onDraftChange: (patch: Partial<FieldDraft>) => void` (parent does `setDraft(prev => prev ? { ...prev, ...patch } : prev)`), and keep existing Copy/Skip props.
- When `!fieldsEditable`: keep today’s read-only rows for Title, State, Link (link row only if `job.job_link`, unchanged).
- When `fieldsEditable` and `draft`:
  - **Title:** `<input className="dep-input" value={draft.job_title} onChange={e => onDraftChange({ job_title: e.target.value })} />` in the Title row value slot.
  - **Link:** always show the Link row (even if empty) with `<input className="dep-input" value={draft.job_link} onChange={...} />`.
  - **State:** show current `job.state` as today (including legacy hint). Below it (same row value column or immediately under), render:

    ```tsx
    <select
      className="dep-input"
      value={draft.state === job.state ? "" : draft.state}
      onChange={e => onDraftChange({ state: e.target.value || job.state })}
    >
      <option value="">No change</option>
      {[...legalNextStates].sort((a, b) => a.localeCompare(b)).map(s => (
        <option key={s} value={s}>{s}</option>
      ))}
    </select>
    ```

  - Company, Created, Last Transition, State History: unchanged display-only.
  - If `saveError`, render `<p className="entity-error">{saveError}</p>` immediately above the Copy/`entity-summary-actions` block.
  - Copy button and Skip This Job block: **byte-for-byte unchanged** (same wrappers, `className`, `onClick`, `disabled`, label expressions).

⚠️ **Decision:** State `<select>` lists only `legal_next_states` from the API (sorted for stable UX), plus a **No change** empty option that keeps `draft.state === job.state` so Save omits `state`. Do not list every `JOB_STATES` key. Do not invent a client-side prior-state check.

9. Do not change `handleCopySnapshot`, `handleSkip`, or agent-story rendering in this stage. JD tab may still hide when empty — Stage 2.

## Stage 2: Job Description editor (including empty JD)

**Done when:** For `fields_editable` jobs, a **Job Description** side tab is always present; its body is a `dep-input dep-textarea` bound to `draft.job_description` (empty string allowed); Save from Stage 1 persists a pasted description; for non-editable jobs, JD tab presence and read-only normalized display remain exactly as today (`hasJD` gate + `entity-jd-content`).

1. In `JobDetailModal`, replace the tab construction so:

```ts
const hasJD = Boolean((job?.job_data as Record<string, unknown>)?.job_description)
const showJdTab = fieldsEditable || hasJD
const sideTabs: SideTab[] = [
  { id: "__info__", label: "Info", content: "" },
  ...(showJdTab ? [{ id: "__jd__", label: "Job Description", content: "" }] : []),
  ...agentStory.map((entry, i) => ({
    id: `story_${i}`,
    label: entry.task_key,
    content: "",
  })),
]
```

2. In `renderSideContent` for `__jd__`:

- If `fieldsEditable` and `draft`: return

  ```tsx
  <textarea
    className="dep-input dep-textarea"
    value={draft.job_description}
    onChange={e => setDraft(prev => prev ? { ...prev, job_description: e.target.value } : prev)}
    rows={16}
    style={{ width: "100%", minHeight: 240 }}
  />
  ```

  Do not trim on change. Do not apply the 3+ newline collapse while editing.

- Else (read-only path): keep today’s normalize + `<div className="entity-jd-content">` exactly.

3. Fix story index offset: `const storyOffset = showJdTab ? 2 : 1` (was `hasJD ? 2 : 1`).

4. Agent story branch unchanged — still renders `<AgentStoryTab entry={entry} />` with no editors.

5. From `src/ui/frontend`, run `npm run build` (or `tsc -b`) and `npm run lint`. Fix only type/lint breaks caused by this ticket’s files. Do not expand scope to unrelated lint debt.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Execution contract

- Stages in order; steps in order within a stage.
- No new files beyond the Files Changed table.
- Ambiguity / missing AST-1453 API → stop, comment on **parent** AST-1446 with 🛑 format, wait.
- No `tests/` or `docs/test-bible/**` edits (Betty).
