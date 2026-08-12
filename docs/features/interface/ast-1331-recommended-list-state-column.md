# AST-1331 — Recommended list State column

- **Linear:** [AST-1331](https://linear.app/astralcareermatch/issue/AST-1331/recommended-list-state-column-add-job-state-to-recommended-job-list)
- **Parent:** [AST-1330](https://linear.app/astralcareermatch/issue/AST-1330/add-job-state-to-recommended-job-list-tables)
- **Publish ref:** `sub/AST-1330/AST-1331-recommended-list-state-column`

Add a sortable **State** column to every Recommended list table that displays each row’s existing job state string (the stored `JOB_STATES` key already on the list row, e.g. `BUILD_ARTIFACTS`). Meteorites stay one section; State makes in-progress vs ready vs untouched distinguishable without opening a job. No section regrouping, modal, API, or label-map work.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Add State column + `state` sort branch on every Recommended section table | ui |

**Do not touch:** `src/ui/api/**`, `src/utils/config.py`, State UI manifest / `StateUiContext`, `JobsSkipped.tsx` / `JobsInReview.tsx` / other job list pages, Recommended Job Modal / report components, `CandidateJobRowActions.tsx`, section grouping logic in `JobsRecommended.tsx`, `tests/**`, `docs/test-bible/**`.

**Do not add:** human-readable state label maps, hardcoded state allowlists, new config keys, API fields, or section membership changes.

---

## Stage 1: State column + sort on Recommended tables

**Done when:** Every visible Recommended section table (Meteorites and non-Meteorite sections) has a sortable **State** header; each row cell shows that job’s `state` string (raw key). Sorting by State toggles asc/desc like Job Title / Company / Updated. Section membership, phase score columns, Updated, row click → report, and Skip / other row actions are unchanged. No other files changed.

1. In `src/ui/frontend/src/pages/JobsRecommended.tsx`, in `sortRecommendedJobs`, after the `state_changed_at` branch and before the `phaseFields.includes(col)` branch, add a `col === "state"` branch that compares `(a.state || "").localeCompare(b.state || "")` (same string sort as `JobsSkipped.tsx` `sortJobs` for `"state"`). Do not invent a custom state order.

2. In the same file, in every section table `<thead>` row, insert a **State** column header **after Company** and **before** the `phase_score_columns` map, matching peer sortable headers:

```tsx
                      <th className="sortable" onClick={() => handleSort(sec.state, "state")}>
                        State{sortIndicator(sec.state, "state")}
                      </th>
```

Do not wrap this header in a Meteorites-only condition — AC requires State on every visible Recommended section table.

3. In the same file, in every section table `<tbody>` row, insert a State cell in the same column position (after Company `<td>`, before the phase-score `<td>` map):

```tsx
                        <td>{job.state || "\u2014"}</td>
```

Display the stored key only. Do not map through section labels, `legacyStateSectionLabel`, or any display enum. Empty/missing `state` uses the same em dash as Job Title.

4. Leave alone (verify by reading, do not edit for this ticket):
   - `sections` useMemo (Meteorite prefix split, `manifest.jobs.recommended.sections` grouping, legacy unmapped sections).
   - Default sort `{ col: "state_changed_at", asc: false }`, `handleSort` toggle behavior, phase score columns, Updated / `<Time>`, `CandidateJobRowActions`, `openJobReport` row click, modal / toast wiring.
   - API call `GET /api/jobs?view=recommended&…` — `state` is already on each row (`Job.state`); do not change the client URL or response shaping.

⚠️ **Decision:** Column placement after Company / before phase scores, matching Skipped floor State placement and keeping Meteorite triage early in the row. Raw `job.state` string only — parent/child boundaries forbid inventing human-readable labels.

⚠️ **Decision:** Single-file UI change. List rows already carry `state`; no API or config work. Peer sort pattern already exists on Skipped (`col === "state"` + localeCompare).

---

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1331
**Overall:** APPROVED
**Publish ref:** `sub/AST-1330/AST-1331-recommended-list-state-column` @ `68ff11567decff69ee7a7efc8793637f135e8428`

### Traceability

AC1–AC5 → Stage 1 (`JobsRecommended.tsx`: `sortRecommendedJobs` `state` branch, State header/cell after Company before phase scores, per-section sort via existing `sections.map` loop).

### Findings

(none)

context_tokens≈22000
