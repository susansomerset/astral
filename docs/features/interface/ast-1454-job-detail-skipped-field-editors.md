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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1454
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1446/AST-1454-job-detail-skipped-field-editors` @ `3896ae6f835baf45cb9bb1bd1e501fb52e6da445`

**Gates:** Plan Ready · assignee Joan · 0 Plan Discuss rounds · child scope only *(publish tip unchanged this session)*

## Traceability
AC1→S1+S2 · AC2→S1 (`handleSave` PUT + `onRefresh` on Skipped/In Review) · AC3→S2 · AC4→S1 (state `<select>` from `legal_next_states` + save error reload path) · AC5→S1 (`onRefresh={load}` on `JobsSkipped`) · AC6→S1 (`fields_editable` gate) · AC7→S1 step 8–9 (Copy/Skip markup unchanged; Retry/bulk untouched per do-not-touch)

## Findings

No `fix-now` findings.

### acceptable
- **Location:** Prerequisite — AST-1453 API on worktree tip
- **Finding:** Plan requires `_attach_skipped_edit_meta` + `PUT persist_skipped_edits` after `sync-child.sh`; epic worktree may not have #1 merged yet.
- **Recommendation:** Keep the documented 🛑 stop gate; build #1 first (already approved). Joan does not re-plan persist here.

### acceptable
- **Location:** Stage 1 — invalid-transition error handling
- **Finding:** On 409 transition errors, plan reloads + shows inline error; field edits may already have persisted per AST-1453 ordering.
- **Recommendation:** Matches sibling #1 contract and parent “correct the record” intent; no plan change.

### acceptable
- **Location:** Stage 1 — editable Link row
- **Finding:** Editable mode replaces `<a href>` with `<input>`; operator cannot click-through while editing.
- **Recommendation:** Reasonable edit-mode tradeoff; no change unless Susan wants a separate “open link” control.

**Considered (in-session):** Universal orchestration statutes — N/A. Scoped statutes/plan citations (`astral.layers.ui-config-driven-business-logic` via server `fields_editable`/`legal_next_states` only; `astral.ui.frontend-file-placement` flat `components/`/`pages/`; `astral.ui.naming-conventions`; `astral.standards.no-hardcoded-sets` no TS skipped list; `astral.standards.dry-and-focused-functions` draft helpers in-modal; patterns `pattern.ui.shared-button-roles` Modal `btn primary` Save / `btn secondary` Cancel; `pattern.ui.admin-endpoint` thin client over #1 PUT) — all conform. `JobDetailModal` mounts only from `JobsSkipped` / `JobsInReview`; both get `onRefresh`. Files Changed stays inside child scope.

context_tokens≈103000

## Review

- **Commit:** `43129c21f78c405b13115db420f3b4df713a4516`
- **Publish ref:** `origin/sub/AST-1446/AST-1454-job-detail-skipped-field-editors`
- **Stages:** 1–2 (editable Info + Save PUT + list `onRefresh`; JD tab always when editable)


## Radia review

# Radia review — AST-1454

**Publish ref:** `origin/sub/AST-1446/AST-1454-job-detail-skipped-field-editors` @ `f396d05c0eb443fa414300e7d61545e3dc163c69`  
**Baseline:** `origin/dev` · **Status:** Tests Passed (trusted) · **Product:** `43129c21` (+ Betty `9081bc47`)  
**Prerequisite AST-1453:** `_attach_skipped_edit_meta` + `persist_skipped_edits` present on worktree tip ✓

---

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1454  
**Publish ref:** `origin/sub/AST-1446/AST-1454-job-detail-skipped-field-editors` @ `f396d05c0eb443fa414300e7d61545e3dc163c69`  
**Overall:** CLEAN

## Statutes checked

64 active rows (`canon/statutes/README.md` § Harvested corpus). Scored against AST-1454 product + Betty test delta.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no dispatch edits |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | — |
| astral.batch.claim-process-release | scoped | not-applicable | — |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | — |
| astral.config.config-source-of-truth | scoped | not-applicable | no config edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | — |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | — |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | — |
| astral.dispatch.seed-auto-false | scoped | not-applicable | — |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | — |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single issue doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty: tests + bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer excluded tests/ |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | frontend-only delta |
| astral.layers.import-direction | scoped | conforms | React uses `api()` only; no data/external imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | — |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | editability + successors from GET only; no TS skipped-state list |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | — |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | frontend client; auth via existing `api()` |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | — |
| astral.seed.archie-catalog-wins | scoped | not-applicable | — |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | — |
| astral.seed.define-approved | scoped | not-applicable | — |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | — |
| astral.seed.other-via-coverage-join | scoped | not-applicable | — |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | — |
| astral.standards.database-header-inventory | scoped | not-applicable | — |
| astral.standards.debug-contract-gated | scoped | not-applicable | — |
| astral.standards.dry-and-focused-functions | scoped | conforms | draft helpers in-modal; no new files |
| astral.standards.in-scope-only | scoped | conforms | JobDetailModal + JobsSkipped + JobsInReview only |
| astral.standards.logging-via-utils | scoped | not-applicable | — |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain field names |
| astral.standards.no-cross-contamination | scoped | conforms | no tracker/api/config/copy/skip body edits |
| astral.standards.no-hardcoded-sets | scoped | conforms | state options from `legal_next_states` only |
| astral.standards.public-then-helpers | scoped | not-applicable | React module |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | — |
| astral.state.core-decides-transitions | scoped | conforms | no client prior-state logic; PUT delegates to #1 |
| astral.state.job-prior-states-enforced | scoped | conforms | select lists API successors only |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | — |
| astral.ui.frontend-file-placement | scoped | conforms | `components/` + `pages/` only |
| astral.ui.naming-conventions | scoped | conforms | `dep-input`, `entity-error`, `btn secondary` |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | — |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests at tip |
| orch.git.commit-vocabulary | universal | conforms | — |
| orch.git.flow-direction-inviolable | universal | conforms | — |
| orch.git.ftr-sub-topology | universal | conforms | sub branch OK |
| orch.git.merge-on-checkout | universal | conforms | sync(dev)/ftr on publish ref |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | — |
| orch.git.no-dev-agent-branches | universal | conforms | — |
| orch.git.one-epic-worktree-per-parent | universal | conforms | — |
| orch.git.three-permanent-branches | universal | conforms | diff vs origin/dev |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | plan decisions documented |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | — |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | — |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | — |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | — |

**C4 straggler:** Joan APPROVED @ `3896ae6f`; no Excluded statute table attached.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.shared-button-roles | conforms | Save via Modal `btn primary`; Copy/Skip remain `btn secondary` |
| pattern.ui.admin-endpoint | conforms | thin client over AST-1453 PUT; eligibility from GET meta |

## Plan adherence

**Stage 1:** `fields_editable` gate; draft/baseline/dirty; `handleSave` PUT with conditional `state`; 409 reload+error path; `onRefresh={load}` on Skipped/InReview; Modal `dirty`/`onSave`; Copy/Skip handlers/markup unchanged.

**Stage 2:** `showJdTab = fieldsEditable || hasJD`; editable JD textarea; `storyOffset = showJdTab ? 2 : 1`; read-only JD path unchanged.

Estimate **3** fits (~179 LOC product). `JobsRecommended.tsx`, `api_jobs.py`, `tracker.py` untouched. AST-1453 prerequisite satisfied on tip.

**Minor layout note:** state `<select>` lives in a separate **Change to** row rather than under the State value column as plan prose suggested — functionally equivalent; see advisory.

## Frame diff

| Plan frame | Tip |
|------------|-----|
| JobDetailModal.tsx | ✓ |
| JobsSkipped.tsx `onRefresh` | ✓ |
| JobsInReview.tsx `onRefresh` | ✓ |
| No backend / Recommended / Modal.tsx | ✓ |
| Betty tests + bible | expected (`9081bc47`) |

(none)

## Findings

No **fix-now** or **discuss**.

### advisory

- **Location:** `InfoTab` state control layout  
- **Finding:** Plan step 8 placed the `<select>` under the State row; implementation uses a separate row labeled **Change to**.  
- **Recommendation:** Accept unless Susan wants exact plan layout; no behavior change needed.

- **Location:** Modal Save during `saving`  
- **Finding:** Save button not visually disabled while PUT in flight (plan allowed this; `handleSave` guards double-submit).  
- **Recommendation:** Optional UX polish in AST-1454 resolve or defer; not blocking.

- **Location:** component tests  
- **Finding:** No test for inline 400 errors (empty title/link from API).  
- **Recommendation:** Optional Betty lock; handler displays `body.error`.

### acceptable (Joan — unchanged)

- AST-1453 prerequisite stop gate — satisfied on tip.  
- 409 transition reload path — matches #1 field-before-hop contract.  
- Editable link replaces click-through — edit-mode tradeoff.

## What's solid

- Server-driven editability; no hardcoded skipped states.  
- State select sorted + **No change** omits `state` from PUT.  
- Empty JD tab + textarea when editable.  
- Betty covers editable/non-editable, PUT+onRefresh, 409 error path, page-level list refresh.

## Notes

- `blockedBy AST-1453 (User Testing)` — prerequisite API present on publish ref; no review blocker.  
- C7 complete. Chuckles: append, commit docs, post slim upshot, → Review Posted.

context_tokens≈28000

---

```
[code-rubric] PROCEED (Commit: f396d05c) skipped-field editors clean
```
