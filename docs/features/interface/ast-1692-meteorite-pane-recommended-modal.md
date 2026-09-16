# AST-1692 — Meteorite pane on Recommended modal

**Linear:** [AST-1692](https://linear.app/astralcareermatch/issue/AST-1692/meteorite-pane-on-recommended-modal-view-related-meteorite-record-data)
**Parent:** [AST-1685](https://linear.app/astralcareermatch/issue/AST-1685/view-related-meteorite-record-data-on-recommended-job-modal) — View related meteorite record data on recommended job modal
**Publish ref:** `sub/AST-1685/AST-1692-meteorite-pane-recommended-modal`

Wire a config-driven **Meteorite** top tab on the Recommended Job Report modal and a read-only `JobMeteoritePane` that renders staging-row provenance from `related_meteorite`. Omit the tab when the payload is null. Consumes AST-1691 API/manifest contracts; does not own retention or backend.

## UAT fitness

- **AC restored:** Parent AC1 — "Opening a Recommended job that has a `meteorite` row with matching `astral_job_id` shows top tabs Summary | Analysis | Artifacts | Discussion | **Meteorite**. Fail: Meteorite missing when such a row exists, or Meteorite appears for a job with no related row." Parent AC3 — "Meteorite pane timestamps match the staging row’s `created_at` / `updated_at` / `state_changed_at` (and `estelle_notified_at` when non-null)." Parent AC4 — "When `meteorite.link` starts with `http://` or `https://`, the pane exposes a navigable href; otherwise plain text (not an href)." Parent AC5 — "AI section shows `classify_outcome` and `content` only from the meteorite row (read-only) — no agent-story blocks and no company-stem fields required in this pane."
- **Correct outcome:** Operators reviewing a Recommended meteorite job can open **Meteorite** next to Discussion and scan live staging-row timestamps, link/breadcrumb, and AI `classify_outcome`/`content` without leaving the modal; gazed-only jobs keep the existing four tabs (Meteorite omitted).
- **Sibling check:** AST-1691 supplies `related_meteorite` on `GET /api/jobs/<id>`, Meteorite on `JOBS_RECOMMENDED_REPORT_TOP_TABS`, and `jobs.recommended.report_meteorite_sections` — this ticket consumes those shapes only (no Python edits). AST-1690 keeps job-linked LANDED rows readable — this ticket only displays. Verified by Scope Boundaries and Files Changed (frontend only).
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Hardcoding a Meteorite tab label/order only in React (or inventing section ids in TSX) fights sibling AC6 / parent config-driven contract. Showing an empty Meteorite tab when `related_meteorite` is null fails AC1. Treating every non-empty `link` as `href` (without `http://`/`https://` prefix check) fails AC4. Pulling agent-story / company-stem into this pane fails AC5.

## Explicit scope gate

This ticket’s **Scope** names only: `src/ui/frontend/src/contexts/StateUiContext.tsx`; `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`; `src/ui/frontend/src/components/JobMeteoritePane.tsx`; `src/ui/frontend/src/App.css` (only if needed). Stages below stay inside those files and those change kinds.

**Depends on (AST-1691 — User Testing; consume only):**

| Manifest / API field | Shape | UI use |
|----------------------|-------|--------|
| `jobs.recommended.report_top_tabs` | includes `{tab_id: "meteorite", nav_label: "Meteorite"}` after Discussion | filter into `TabBar` only when payload non-null |
| `jobs.recommended.report_meteorite_sections` | four `{section_id, nav_label, default_expanded}` — `meteorite_timestamps`, `meteorite_link`, `meteorite_ai`, `meteorite_provenance` | pane section list (order/labels from manifest) |
| `GET /api/jobs/<id>` → `related_meteorite` | flat object with `id`, `created_at`, `updated_at`, `state_changed_at`, `estelle_notified_at`, `link`, `classify_outcome`, `content`, `state`, `source_kind`, `source_id`, `error` — or JSON `null` | pane body + tab visibility |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type `report_meteorite_sections` on `jobs.recommended` | ui |
| `src/ui/frontend/src/components/JobMeteoritePane.tsx` | **New** — read-only Meteorite section stack via `ReportSectionList` | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Type `related_meteorite` on job detail; filter Meteorite top tab when null; render `JobMeteoritePane` | ui |

**Out of scope / do not touch:** `src/utils/config.py`, `api_system.py`, `api_jobs.py`, `database.py`, `meteorite.py` (AST-1691 / AST-1690); `JobDiscussionPane.tsx` / agent-story paths; `tests/` / bible (Betty).

⚠️ **Decision:** Omit `App.css` from this plan. Reuse existing `recommended-report-*`, `job-analysis-upshot-body`, `entity-story-content`, and `recommended-report-title-link` / plain text for link honesty. If UAT shows a real visual gap existing classes cannot cover, escalate — do not invent CSS in build.

## Canon Scope (this ticket)

Citations: **none** — presentational React only; API/logging statutes owned by AST-1691. No pattern files to read for this plan.

## Stages

### Stage 1: Manifest types + `JobMeteoritePane`

**Done when:** `StateUiManifest.jobs.recommended` types `report_meteorite_sections`. A new `JobMeteoritePane` renders the four manifest sections against a `related_meteorite` object: timestamps (incl. `estelle_notified_at` only when non-null), http(s)-gated link, read-only AI fields, provenance fields (`error` only when present). No modal wire-up yet.

1. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, inside `jobs.recommended`, after the existing `report_artifact_tabs?` block (and before `meteorite_section?`), add:

```ts
report_meteorite_sections?: Array<{
  section_id: string
  nav_label: string
  default_expanded: boolean
}>
```

   Do **not** add Discussion section typing here (out of this ticket’s Scope wording — Meteorite only). Do **not** invent extra keys.

2. Create `src/ui/frontend/src/components/JobMeteoritePane.tsx`.

3. Exports / types in that file:

```ts
export type RelatedMeteorite = {
  id: number | string | null
  created_at: string | null
  updated_at: string | null
  state_changed_at: string | null
  estelle_notified_at: string | null
  link: string | null
  classify_outcome: string | null
  content: string | null
  state: string | null
  source_kind: string | null
  source_id: string | null
  error: string | null
}

type Props = {
  sections: readonly ReportSectionDef[]
  relatedMeteorite: RelatedMeteorite
}
```

4. Helper `isNavigableHttpLink(raw: string | null | undefined): boolean`:
   - If `raw` is null/undefined, return `false`.
   - Let `t = raw.trim()`.
   - Return `t.startsWith("http://") || t.startsWith("https://")` (exact prefixes after trim — matches parent AC4 wording; do **not** accept bare domains or `mailto:`).

5. Helper `formatMeteoriteAiContent(raw: string): string` — same as Discussion: `try { return JSON.stringify(JSON.parse(raw), null, 2) } catch { return raw }`.

6. Helper `renderFieldRows(rows: Array<{ label: string; value: string }>): ReactNode`:
   - If `rows.length === 0`, return `<p className="recommended-report-empty">No values on file.</p>`.
   - Else render a stack of labeled lines, each:
     - outer: `<div className="job-analysis-upshot-body">` (or a fragment of them)
     - text: `{label}: {value}` with `value` non-empty strings only (callers filter).

   Keep this tiny and local — do not add a shared form component.

7. Default export `JobMeteoritePane({ sections, relatedMeteorite })`:

```tsx
return (
  <ReportSectionList
    sections={sections}
    renderSection={(sectionId) => {
      // switch on sectionId — see step 8
    }}
  />
)
```

8. `renderSection` cases (exact `section_id` strings from AST-1691 config — do **not** invent aliases):

   - **`meteorite_timestamps`:** Build rows in order:
     - `{ label: "created_at", value: String(relatedMeteorite.created_at ?? "").trim() }` — include only when value non-empty after trim.
     - same for `updated_at`, `state_changed_at`.
     - `estelle_notified_at` — include **only** when `relatedMeteorite.estelle_notified_at != null` and `String(...).trim() !== ""`.
     - Pass to `renderFieldRows`.

   - **`meteorite_link`:** Let `link = (relatedMeteorite.link ?? "").trim()`.
     - If empty: `<p className="recommended-report-empty">No link on file.</p>`.
     - Else if `isNavigableHttpLink(link)`: `<a href={link} target="_blank" rel="noopener noreferrer" className="recommended-report-title-link">{link}</a>`.
     - Else: `<p className="job-analysis-upshot-body">{link}</p>` (plain text — **no** `<a>`).

   - **`meteorite_ai`:**
     - Outcome line: if `classify_outcome` non-null and trimmed non-empty, show a read-only line `classify_outcome: …` via `job-analysis-upshot-body`.
     - Content: if `content` non-null and trimmed non-empty, render `<textarea className="entity-story-content" readOnly value={formatMeteoriteAiContent(String(content))} />`.
     - If both empty: `<p className="recommended-report-empty">No AI content on file.</p>`.
     - No inputs other than read-only textarea; no agent-story; no company-stem fields.

   - **`meteorite_provenance`:** rows in order `id`, `state`, `source_kind`, `source_id` when each trimmed string form is non-empty; `error` only when non-null and trimmed non-empty. Use `renderFieldRows`.

   - **default:** return `null` (unknown section ids — do not invent bodies).

⚠️ **Decision:** Section order and `default_expanded` come from the manifest list passed by the modal — the pane does not re-sort or hardcode the four section defs. Unknown `section_id` → null body (still a CollapsiblePanel header from the list).

### Stage 2: Wire modal — filter tab + render pane

**Done when:** Opening a job with non-null `related_meteorite` shows Meteorite in the top `TabBar` after Discussion and selecting it renders `JobMeteoritePane`. Opening a job with `related_meteorite === null` (or missing key treated as null) does **not** show Meteorite. No Python/CSS changes.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`:
   - Import `JobMeteoritePane`, `type RelatedMeteorite` from `./JobMeteoritePane`.

2. Extend `JobDetail`:

```ts
related_meteorite?: RelatedMeteorite | null
```

3. Replace the `topTabs` `useMemo` so Meteorite is filtered by payload:

```ts
const topTabs = useMemo(() => {
  const rows = manifest?.jobs.recommended.report_top_tabs ?? []
  const hasMeteorite = job?.related_meteorite != null
  return rows
    .filter(r => r.tab_id !== "meteorite" || hasMeteorite)
    .map(r => ({ key: r.tab_id, label: r.nav_label }))
}, [manifest, job?.related_meteorite])
```

   Do **not** hardcode the Meteorite label or insert a tab outside `report_top_tabs`. Do **not** filter other tabs.

4. Add `meteoriteSections` `useMemo` (peer to `discussionSections`):

```ts
const meteoriteSections = useMemo((): ReportSectionDef[] => {
  const rows = manifest?.jobs.recommended.report_meteorite_sections ?? []
  return rows.map(s => ({
    section_id: s.section_id,
    nav_label: s.nav_label,
    default_expanded: s.default_expanded,
  }))
}, [manifest])
```

   Read from the typed manifest field (Stage 1) — no local cast unless the type is somehow unavailable (it must be typed).

5. In the tab-pane block, after the Discussion branch, add:

```tsx
{activeTopTab === "meteorite" && job?.related_meteorite != null && (
  <JobMeteoritePane
    sections={meteoriteSections}
    relatedMeteorite={job.related_meteorite}
  />
)}
```

6. Do **not** change Summary / Analysis / Artifacts / Discussion bodies, header chrome, or primary actions.

⚠️ **Decision:** Treat missing `related_meteorite` key like null for tab filtering (`job?.related_meteorite != null`). AST-1691 always sets the key; defensive omit still satisfies AC1’s “no related row → no tab.”

⚠️ **Decision:** Existing `useEffect` that resets `activeTopTab` when the active key is absent from `topTabs` already covers “was on Meteorite, switched to a job without related row” — do not add a second reset effect.

## Estimate

Confirm Chuckles estimate: 2 — agree

## AC → stage map

| AC (this child) | Stage |
|-----------------|-------|
| AC1 Meteorite tab when related row / omit when null | Stage 2 |
| AC2 timestamps match staging row (+ `estelle_notified_at` when set) | Stage 1 |
| AC3 http(s) href vs plain breadcrumb | Stage 1 |
| AC4 AI `classify_outcome` + `content` read-only only | Stage 1 |

Parent AC2/6 → AST-1691; parent AC7–9 → AST-1690 (out of scope).

## Joan validate

[plan-rubric]
**Ticket:** AST-1692
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1685/AST-1692-meteorite-pane-recommended-modal` @ `bb3d0090ba0628b75125e58ded481b530ad7b0c1`

## Canon scores

*(none on ticket — intentional presentational-only scope per dispatch and plan `## Canon Scope`; API/logging statutes owned by AST-1691. No ids to score.)*

## Traceability

Child AC **1** (Meteorite tab when related row / omit when null) → Stage **2**; AC **2** (timestamps + `estelle_notified_at` when set) → Stage **1**; AC **3** (http(s) href vs plain breadcrumb) → Stage **1**; AC **4** (read-only `classify_outcome` + `content` only) → Stage **1**. Parent AC **2, 6** → AST-1691; parent AC **7–9** → AST-1690 (plan marks N/A). No orphan stages; no unmapped child AC.

## Findings

### acceptable

- **Location:** `## Canon Scope` / ticket Citations
- **Finding:** Frozen directive list is empty by design (“presentational React only”), not an omitted Canon Scope. Parent epic statutes apply to backend siblings; this child correctly consumes AST-1691 shapes without re-scoring logging law.
- **Recommendation:** None.

- **Location:** Stage 1 — `formatMeteoriteAiContent`
- **Finding:** Duplicates the JSON pretty-print pattern in `JobDiscussionPane` / `AgentStoryTab`. Plan explicitly keeps a local helper; `astral.standards.dry-and-focused-functions` is not on this ticket’s list.
- **Recommendation:** None for plan approval — optional future extract if a shared util emerges.

- **Location:** Stage 2 — `topTabs` filter
- **Finding:** Payload-gated Meteorite tab (`related_meteorite != null`) while label/order still come from `report_top_tabs` satisfies parent AC1 and defers parent AC6 manifest contract to AST-1691 consumption, not TSX invention.
- **Recommendation:** None.

- **Location:** Depends-on table / sibling shapes
- **Finding:** Consumed field names and `section_id` strings match AST-1691 plan (`meteorite_timestamps`, `meteorite_link`, `meteorite_ai`, `meteorite_provenance`; flat `related_meteorite` projection).
- **Recommendation:** None — build ordering “after #2” is a workflow gate, not a plan defect.

## R6 (summary)

Definition fidelity: frontend-only; four scoped files; no Python, retention, or agent-story creep. Files Changed matches ticket `## Scope` (`App.css` omitted with documented reuse decision). DRY: peers `JobDiscussionPane` + existing `ReportSectionList` / report CSS classes. Self-assessment: estimate **2 — agree** fits two focused stages. Plan Discuss rounds: **0** completed (Plan Ready; one Katherine publish comment only).

context_tokens≈48000

---

[plan-rubric] PROCEED (Commit: bb3d0090) pane plan ready

---

## Review

**Built:** `origin/sub/AST-1685/AST-1692-meteorite-pane-recommended-modal` @ `8ce9a6d607d8b97bc4489d1784709d36c733f078`

Stages 1–2: `report_meteorite_sections` typed; `JobMeteoritePane` read-only stack; Meteorite top tab filtered on non-null `related_meteorite` and wired in `JobAnalysisReportModal`. Tests deferred to Betty.
