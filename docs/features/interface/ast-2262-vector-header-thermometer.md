# AST-2262 — Vector-header thermometer (Update Criteria screens)

- **Linear:** [AST-2262](https://linear.app/astralcareermatch/issue/AST-2262) · parent [AST-2257](https://linear.app/astralcareermatch/issue/AST-2257)
- **Publish ref:** `origin/sub/AST-2257/AST-2262-vector-header-thermometer`

Each rubric vector header on the shared criteria editor shows how many grading runs are pinned to the version that is current, and a stacked bar of those letter grades. Hovering a segment shows the letter, the count, and the date that letter was last seen. Moving the version arrows reloads those figures for the version that just became current. The rollup and the nav badge stay on [AST-2261](https://linear.app/astralcareermatch/issue/AST-2261).

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

| File | Kind of change Scope allows |
|------|-----------------------------|
| `src/ui/frontend/src/components/RubricGradeThermometer.tsx` | **new** — one component. One segment per letter that has a count, in A-B-C-D-F-X order, colored with that letter's existing grade token, and a tooltip with the letter, the count, and the last-seen date. |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | **modified** — the rubric vector header gains the run count and the thermometer, fed by the AST-2261 read. The existing version-move reload runs that read again for the version that just became current. |
| `src/ui/frontend/src/App.css` | **modified** — new rules for the bar. Colors come from the existing grade tokens. |

No `src/core/candidate.py`, no `src/ui/api/`, no `src/ui/frontend/src/pages/`, no `CollapsiblePanel.tsx`, no `fmt.ts`. The header uses `CollapsiblePanel`'s existing `metadata` prop.

## Canon Scope (patterns read at plan)

Ticket Citations: `patt.artifact.ui-consistency`.

- **`patt.artifact.ui-consistency`:** Same-shaped artifact bodies share one editor. Rubric criteria are the exception that already lives in `ArtifactEditor` rubric mode (`rubricMode = !fixedFields`), not a page per rubric. This ticket adds the bar on that shared chrome. Do not add a thermometer under `src/ui/frontend/src/pages/`.

Parent Architectural definition lists no in-force statutes. Every other directive id stays **id-only** until build-child §8.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/RubricGradeThermometer.tsx` | New stacked-bar component | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Run count + bar on each rubric vector header; reload on version move | ui |
| `src/ui/frontend/src/App.css` | Bar track and per-letter segment colors | ui |

## Stages

### Stage 1: Thermometer component and bar colors

**Done when:** `RubricGradeThermometer` renders one horizontal segment per positive-count letter in A, B, C, D, F, X order, each segment's background is that letter's `--grade-*` token, and the segment's `title` is the letter, the count, and a `YYYY-MM-DD` date. A letter with count 0, or any letter outside that set, produces no segment.

1. Create `src/ui/frontend/src/components/RubricGradeThermometer.tsx`. Default export. Props:

   ```tsx
   export interface RubricGradeLetter {
     grade: string
     count: number
     last_seen: string
   }

   export default function RubricGradeThermometer({ letters }: { letters: RubricGradeLetter[] })
   ```

   No other props. No fetch. No candidate context.

2. Keep only letters whose `grade.trim().toUpperCase()` is in `["A", "B", "C", "D", "F", "X"]` and whose `count` is a number greater than 0. Sort that list by the array order above (A then B then C then D then F then X). Drop every other entry, including a zero count.

3. Render a `div` with class `rubric-grade-thermometer`. For each kept letter, a child `div` with class `rubric-grade-thermometer-seg seg-<letter lowercased>` (`seg-a` … `seg-x`) and `style={{ flexGrow: count, flexBasis: 0 }}`. Set `title` to `` `${grade}, ${count}, ${date}` `` where `grade` is the uppercased letter, `count` is the number, and `date` is `last_seen.trim().slice(0, 10)`. That slice is the calendar date on the timestamp AST-2261 stores (`YYYY-MM-DD HH:MM:SS`). Do not append a clock time. An empty kept list still renders the track `div` with no children.

   ⚠️ **Decision:** The tooltip date is the first ten characters of `last_seen`, not `fmtTime`. `fmt.ts` is outside this ticket's Scope, and `fmtTime` includes a clock. The stored prefix is already a calendar date.

4. In `src/ui/frontend/src/App.css`, after the `.grade-dot-letterless` block (the letterless grade-dot rules that end near the `.dot-x` letterless ring), add:

   ```css
   .rubric-grade-thermometer {
     display: flex;
     flex-direction: row;
     align-items: stretch;
     width: 8rem;
     height: 10px;
     border-radius: 2px;
     overflow: hidden;
     background: var(--bg-muted, var(--border-subtle));
   }
   .rubric-grade-thermometer-seg { height: 100%; }
   .rubric-grade-thermometer-seg.seg-a { background: var(--grade-a); }
   .rubric-grade-thermometer-seg.seg-b { background: var(--grade-b); }
   .rubric-grade-thermometer-seg.seg-c { background: var(--grade-c); }
   .rubric-grade-thermometer-seg.seg-d { background: var(--grade-d); }
   .rubric-grade-thermometer-seg.seg-f { background: var(--grade-f); }
   .rubric-grade-thermometer-seg.seg-x { background: var(--grade-x); }
   ```

   Do not set `min-width` on a segment. Do not add a color that is not `var(--grade-a)` through `var(--grade-x)`.

   ⚠️ **Decision:** The track is `8rem` wide so `flexGrow: count` has a box to share. The width is the bar's layout, not a cap on the count.

### Stage 2: Vector header and version-move reload

**Done when:** On a candidate criteria screen (`ArtifactEditor` rubric mode), each coded vector header shows that vector's `run_count` and `RubricGradeThermometer`. After the version arrows change which version is current, the same header shows the new version's `run_count` and letters. A shapes-mode or job editor does not fetch the rollup and does not render the bar.

The feed is the read [AST-2261](https://linear.app/astralcareermatch/issue/AST-2261) already shipped on `origin/ftr/AST-2257-update-criteria-screens`:

`GET /api/candidates/<candidate_id>/rubric/<artifact_key>/grade_rollup`

Success body (do not change it):

```json
{
  "artifact_key": "do_rubric",
  "vectors": [
    {
      "code": "AB",
      "label": "…",
      "rubric_vector_uuid": "…",
      "run_count": 0,
      "letters": [
        {"grade": "A", "count": 1, "last_seen": "YYYY-MM-DD HH:MM:SS"}
      ]
    }
  ]
}
```

`letters` is already non-zero grades in A-B-C-D-F-X order. The component still filters, so a stray zero does not take width.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, import `RubricGradeThermometer` from `./RubricGradeThermometer`.

2. Add state next to `criterionVersions`:

   ```tsx
   type GradeRollupVector = {
     code?: string
     run_count?: number
     letters?: { grade: string; count: number; last_seen: string }[]
   }
   const [gradeRollup, setGradeRollup] = useState<GradeRollupVector[] | null>(null)
   ```

   `null` means not loaded. An empty array means the read returned no vectors.

3. Add `refreshGradeRollup` with `useCallback`, beside `refreshVersions`. It runs only when `criterionVersionsOn && selectedId`. Otherwise it sets `gradeRollup` to `null` and returns. Request:

   `api(\`/api/candidates/${selectedId}/rubric/${encodeURIComponent(artifactKey)}/grade_rollup\`)`

   On `r.ok`, `setGradeRollup` to `Array.isArray(body.vectors) ? body.vectors : []` when `mountedRef.current`. On a non-OK response or a thrown error, `setGradeRollup(null)`. No toast. No log. Dependencies: `criterionVersionsOn`, `selectedId`, `artifactKey`.

4. In the existing `useEffect` that calls `refreshVersions` when `loaded` changes: when `loaded` is false, also `setGradeRollup(null)`. When `loaded` is true, also `void refreshGradeRollup()`. Add `refreshGradeRollup` to that effect's dependency list.

5. In `reloadFromServer`, on the candidate branch only (the `api(\`/api/candidates/${selectedId}\`)` path), call `void refreshGradeRollup()` in the same `.then` that calls `applyCandidateArtifactResponse`, after `setDirty(false)`. Do not call it on the `jobPersistence` branch. `moveVersion` already calls `reloadFromServer()` after a successful current-version PUT, so the arrows reload this read without a second call site.

6. In the `CollapsiblePanel` for each rail tab, pass `metadata` only when `criterionVersionsOn && rubricMode && tab.code && gradeRollup !== null`. Otherwise omit `metadata` (leave the prop unset). When passing it, find the vector whose `String(v.code ?? "").trim().toUpperCase()` equals `tab.code.trim().toUpperCase()`. If none, use `run_count` `0` and `letters` `[]`. Render:

   ```tsx
   <span className="rubric-grade-rollup">
     <span className="rubric-grade-run-count" title="grading runs">{runCount}</span>
     <RubricGradeThermometer letters={letters} />
   </span>
   ```

   `runCount` is `typeof vector.run_count === "number" ? vector.run_count : 0`. `letters` is `Array.isArray(vector.letters) ? vector.letters : []`. The visible run count is that integer, including `0`. Do not render the bar from any other component. Do not render it when the label `input` is showing or when it is hidden — the `metadata` slot stays on the panel for both the label span and the rename input.

7. In `src/ui/frontend/src/App.css`, next to the thermometer rules from Stage 1, add:

   ```css
   .rubric-grade-rollup {
     display: flex;
     flex-direction: row;
     align-items: center;
     gap: 6px;
   }
   .rubric-grade-run-count {
     font-variant-numeric: tabular-nums;
     color: var(--text-secondary);
   }
   ```

   The count sits in `collapsible-panel-metadata`, between the vector name and the version arrows. Do not edit `CollapsiblePanel.tsx`.

## Execution contract

The plan is binding. Execute steps in order within a stage, and stages in order. Do not add files. On ambiguity or drift, stop and comment on [AST-2257](https://linear.app/astralcareermatch/issue/AST-2257) with the Stage N blocked format from plan-child. One commit per stage on this epic worktree, published to `origin/sub/AST-2257/AST-2262-vector-header-thermometer`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2262
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2257/AST-2262-vector-header-thermometer` @ `b9a26183ed0b841e8f10da37f9e70faf3a909aa1`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |

## Traceability

`1 → Stage 2 (metadata `run_count` from `grade_rollup`); `2 → Stage 1 (`flexGrow` segments, `seg-*` + `--grade-*` tokens, zero/filter); `3 → Stage 1 (`title` with letter, count, `last_seen.slice(0,10)`); `4 → Stage 2 (`reloadFromServer` after `moveVersion` PUT + `refreshGradeRollup`); `5 → Scope gate + single `RubricGradeThermometer` in `ArtifactEditor`; parent AC `5–6` → N/A (nav rollup AST-2261); parent AC `7` → same as child AC `5`**

## Findings

### discuss — Pattern body still marked draft

- **Severity:** discuss
- **Location:** `patt.artifact.ui-consistency` corpus text
- **Finding:** Expanded directive body includes “**Status:** draft — Archie approval required before active,” while the id is in `canon/directives/active/` and frozen on this ticket’s Citations list.
- **Recommendation:** Archie/process hygiene only; plan behavior matches the pattern’s rubric exception (chrome on shared `ArtifactEditor`, no `pages/` fork). Do not widen Canon Scope on this pass.

### acceptable — Failed rollup read hides chrome

- **Severity:** acceptable
- **Location:** Stage 2 step 3 (`setGradeRollup(null)` on non-OK / throw)
- **Finding:** While `gradeRollup === null`, metadata (run count + bar) is omitted, which can look like a missing count until a successful load.
- **Recommendation:** Matches the plan’s no-toast read failure style; acceptable if Betty/UAT exercise a happy path with AST-2261 rollup present (already on `origin/ftr/AST-2257-update-criteria-screens` and this sub tip).

### acceptable — Native `title` tooltips

- **Severity:** acceptable
- **Location:** Stage 1 step 3
- **Finding:** Segment hover uses the HTML `title` attribute, not a shared tooltip component.
- **Recommendation:** Satisfies AC 3 (letter, count, calendar date on hover); no plan change required.

## R6 checklist (summary)

- Definition fidelity: three files only; explicit scope gate matches ticket **## Scope**; rollup/nav explicitly out of scope (AST-2261).
- DRY / scope: no duplicate bar under `pages/`; distinct from AST-2233/2234 report thermometer CSS/classes.
- Self-assessment: **Estimate** confirm `3 — agree` fits two focused stages.

context_tokens≈31000

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-2257/AST-2262-vector-header-thermometer`

**Product commits:**

| SHA | Stage | Summary |
|-----|-------|---------|
| `5e17e4cf3` | 1 | `RubricGradeThermometer` plus `--grade-*` segment colors |
| `ec5bbe45c` | 2 | Run count and bar on each rubric vector header; reload after version move |

**Built @ `ec5bbe45c`**
