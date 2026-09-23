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

## Radia review

[code-rubric]
**Ticket:** AST-1692
**Publish ref:** 1090acb60260c93e45d08e5e51b7d11f1f81952e
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

*(Frozen list empty by design — ticket Citations: `none`; presentational React only; API/logging statutes owned by AST-1691. No directive ids to score.)*

## Column diff vs plan stage

(aligned) — Joan plan stage recorded no canon ids; code review has none to diff.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Severity:** advisory  
- **Location:** `origin/sub/AST-1685/AST-1692-meteorite-pane-recommended-modal` tip (`merge-tests` `1090acb6`)  
- **Finding:** Branch carries sibling merge-tests baggage beyond AST-1692’s three-file product scope: backend tests/bible for AST-1688–1694, core `test_meteorite.py` expansion, etc. AST-1692 product diff is frontend-only (`StateUiContext.tsx`, `JobMeteoritePane.tsx`, `JobAnalysisReportModal.tsx`); no `App.css` (per plan).  
- **Recommendation:** No AST-1692 product fix. Chuckles/merge-child: keep epic rollup tests aligned with landed product per sibling.

- **Severity:** advisory  
- **Location:** `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `describe("JobAnalysisReportModal — AST-1696 Copy Link")`  
- **Finding:** AST-1696 Copy Link tests landed on this branch; `RecommendedJobReportHeader` at tip has no `Copy Link` affordance. Betty’s manifest filters `--testNamePattern="AST-1692|AST-1551 Discussion"` — AST-1696 block excluded from manifest run.  
- **Recommendation:** None for AST-1692 canon/plan pass; reconcile when AST-1696 product lands or gate those tests.

## Notes

- **Canon Scope:** Empty frozen list is intentional (dispatch + Joan validate), not a scope gap. Do not retroactively score `astral.standards.*` or logging statutes — AST-1691 owns backend law; this child consumes shapes only.
- **Plan fidelity:** Stage 1 — `report_meteorite_sections` typed on manifest; `JobMeteoritePane` with `RelatedMeteorite`, `isNavigableHttpLink` (http/https prefix after trim), four `section_id` cases, read-only AI (`classify_outcome` + `entity-story-content` textarea), provenance + conditional `error`. Stage 2 — `related_meteorite` on `JobDetail`; `topTabs` filters `meteorite` when `related_meteorite == null`; `meteoriteSections` from manifest; pane wired on `activeTopTab === "meteorite"`. No Discussion/Summary/Artifacts edits beyond tab-order test expectations. `App.css` correctly omitted.
- **Sibling dependency (AST-1691):** Consumes `report_top_tabs`, `report_meteorite_sections`, and flat `related_meteorite` — field names and section ids lockstep with AST-1691 config. Tab label/order from manifest, not hardcoded TSX insertion.
- **Estimate footprint:** Confirm estimate **2** — ~169 lines new pane + ~25 lines modal/context wiring; proportionate.
- **AC coverage (manifest):** `test_JobMeteoritePane.test.tsx` — timestamps, http vs breadcrumb, read-only AI, provenance/error; `test_JobAnalysisReportModal.test.tsx` AST-1692 — tab present/absent; fixture updated with Meteorite tab + sections.

## What's solid

- AC1: Meteorite tab appears only when `related_meteorite != null`; omitted when null (Discussion remains last visible tab in null case).
- AC2–AC4: Timestamps from row; `estelle_notified_at` gated; http(s) → `<a>` with `noopener noreferrer`; breadcrumb → plain `<p>`; AI read-only with JSON pretty-print; no agent-story or stem fields.
- Reuses `ReportSectionList` + existing report CSS classes — matches plan’s no-`App.css` decision.
- Existing `useEffect` tab-reset when active key absent from `topTabs` handles job switch away from Meteorite — no duplicate reset added.

## Recommended actions (Chuckles downstream — not Radia)

- Append this artifact to `docs/features/interface/ast-1692-meteorite-pane-recommended-modal.md` under `## Review`.
- Commit + push `docs(AST-1692): Radia review — clean` on `origin/sub/AST-1685/AST-1692-meteorite-pane-recommended-modal`.
- Post slim upshot via `linear_proxy.py --as radia save-comment`.
- Move AST-1692 → **Review Posted**; datt **§3h** → **User Testing** (PROCEED).

context_tokens≈52000

---

[code-rubric] PROCEED (Commit: 1090acb6) Meteorite pane clean

---

## Resolution

**Date:** 2026-09-16  
**Publish tip:** `origin/sub/AST-1685/AST-1692-meteorite-pane-recommended-modal` @ `c9e83a0a5fc45f86625c31ab2205848579c32917`

- Radia **CLEAN / PROCEED** — no fix-now / discuss product changes.
- §9a: Betty cleared ftr test-tree conflict @ `40b9a5b5`; published `sync(dev)` tip so `origin/dev` is an ancestor.
- Dry-run clean vs `origin/dev` and vs `origin/ftr/AST-1685-view-related-meteorite-record-data`.

---

## Bug: AST-1769 — Meteorite tab missing on Recommended job modal (prod)

### As-is

On main/production, opening a Recommended job modal does not show the Meteorite top tab — even for jobs that came from a meteorite staging row.

### To-be

When a related `meteorite` row exists for the open job, the Recommended Job Report modal shows the Meteorite top tab (alongside Summary / Analysis / Artifacts / Discussion) and the read-only pane renders that row’s provenance.

### Repro

1. On production (or a DB that mirrors it), pick a Recommended job whose `job.source` is `"meteorite"` and `job.source_entity_id` is a live `meteorite.id`, but `meteorite.astral_job_id` for that row is null/blank (common after `create_meteorite_job` when `tracker.save_meteorite_job` returns `duplicate_skip` / `superseded` — that helper only calls `update_meteorite(..., astral_job_id=…)` when outcome is `created`).
2. Open the Recommended Job Report modal for that `astral_job_id`.
3. Observe: top tabs are Summary | Analysis | Artifacts | Discussion only — no Meteorite.
4. `GET /api/jobs/<astral_job_id>` returns `"related_meteorite": null` even though `get_meteorite(int(source_entity_id))` would return the staging row.

Fixture shape (no SQL seed — file/JSON persistence):

```json
{
  "job": {
    "astral_job_id": "job-1769",
    "source": "meteorite",
    "source_entity_id": "42",
    "company": "meteorite-acme"
  },
  "meteorite": {
    "id": 42,
    "astral_job_id": null,
    "state": "LANDED",
    "link": "https://example.com/jobs/1",
    "classify_outcome": "job",
    "content": "…"
  }
}
```

### Root cause

Ship is on `origin/main` (AST-1691 `related_meteorite` + AST-1692 tab filter). The UI correctly omits Meteorite when `related_meteorite` is null (`JobAnalysisReportModal` `topTabs` filter). The payload is null because `GET /api/jobs/<id>` only resolves via `get_meteorite_by_astral_job_id(astral_job_id)` (reverse link on `meteorite.astral_job_id`). That column is often unset for jobs that still have a live parent link the other way: `job.source == "meteorite"` + `job.source_entity_id` → meteorite id (AST-1701/1702). `create_meteorite_job` only writes `meteorite.astral_job_id` on outcome `created`, so supersede / duplicate_skip leaves the reverse link empty while the job remains openable from Recommended — tab stays hidden. Symptom is “tab missing”; defect is incomplete related-row resolve on the job detail route, not a missing React tab registration.

### Proposed change

Stay inside parent AST-1685 Component/Technical scope for the report attach path (`src/ui/api/api_jobs.py`, and `src/data/database.py` only if a tiny helper is cleaner). Do **not** edit `src/core/meteorite.py` land/`create_meteorite_job` in this bug (parent Component scope limits that file to retention, which is gone; parent Functional scope forbids land-runner edits). Do **not** change React tab gating — omit-when-null remains correct once the payload is honest.

1. In `src/ui/api/api_jobs.py`, import `get_meteorite` from `src.data.database` (alongside existing `get_meteorite_by_astral_job_id`).

2. In `detail(astral_job_id)`, inside the existing AST-1691 `related_meteorite` try block, after `row = get_meteorite_by_astral_job_id(astral_job_id)`:

   - If `row is None`:
     - Let `src = (job.get("source") or "").strip()`.
     - Let `sid = str(job.get("source_entity_id") or "").strip()`.
     - If `src == "meteorite"` (use `SOURCE_ENTITY_TYPE_METEORITE` from config if already imported in this module; otherwise the literal `"meteorite"` matching config) **and** `sid` is non-empty **and** `sid.isdigit()`: call `get_meteorite(int(sid))` and assign to `row` when not None.
     - Debug joints: log Calling/Response for the fallback `get_meteorite` the same way as the reverse-link call (`stat.logging.debug` — full response, no truncation).
   - Then keep the existing projection: if `row is None` → `job["related_meteorite"] = None`; else the same flat field dict as today (`id`, timestamps, `estelle_notified_at`, `link`, `classify_outcome`, `content`, `state`, `source_kind`, `source_id`, `error`).

3. Do **not** write `meteorite.astral_job_id` from this GET (read-only attach). Do **not** show the Meteorite tab when both reverse link and source_entity fallback miss. Do **not** hardcode a Meteorite tab in TSX.

⚠️ **Decision:** Prefer job `source` / `source_entity_id` fallback on the detail route over expanding `get_meteorite_by_astral_job_id`’s SQL contract — keeps the reverse-link helper’s meaning intact (astral_job_id column only) and matches parent Technical scope’s “attach `related_meteorite` on job GET” change kind. Optional later data-hygiene (always set `astral_job_id` on ok land outcomes in `create_meteorite_job`) is out of this bug’s epic Component scope for `meteorite.py`.

### Blast radius

- `GET /api/jobs/<id>` `related_meteorite` for meteorite-parented jobs that previously returned null — AST-1692 tab + pane will appear; AST-1694 `listing_href` path unchanged (separate helper).
- Gazed / company-parented Recommended jobs (`source != "meteorite"` or blank `source_entity_id`) stay null → four tabs only.
- Soft-fail `except` around the block still sets `related_meteorite=null` on throw.
- Tests that assert null when no reverse-link row may need a Betty revise if they used meteorite-sourced jobs without `astral_job_id` (fix-board / qa-fix).

### What must still hold

- Parent AC1: Meteorite tab only when a related meteorite row exists; omit when none (after both resolve attempts).
- Parent AC2: `related_meteorite` always present as object or `null`; projected fields unchanged when object.
- Parent AC3–5: pane timestamps / http(s) link / read-only AI behavior (AST-1692) unchanged.
- Parent AC6: Meteorite remains on `JOBS_RECOMMENDED_REPORT_TOP_TABS` / manifest — no TSX-only tab invention.
- Parent AC9: no stage/scrape/land/qualify runner edits in this fix.
- Gazed-only jobs without a meteorite parent stay on the existing four tabs.
