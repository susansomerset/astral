# AST-2068 — Blur-save + version arrows in the editors (Artifact Edit Enhancements)

- **Ticket:** [AST-2068](https://linear.app/astralcareermatch/issue/AST-2068)
- **Parent:** [AST-2043 — Artifact Edit Enhancements](https://linear.app/astralcareermatch/issue/AST-2043)
- **Publish ref:** `origin/sub/AST-2043/AST-2068-version-ui`
- **Depends on:** [AST-2067](https://linear.app/astralcareermatch/issue/AST-2067) (six version routes) and [AST-2066](https://linear.app/astralcareermatch/issue/AST-2066) (core). Both are already on `origin/ftr/AST-2043-artifact-versions` and merged into this sub.

This ticket is the UI half of the epic. The 2-second autosave timer in `ArtifactEditor` goes away. Editors that used it (Base Resume Content sections, the criteria pages, and Job Resume) now save when a field loses focus and something changed, so each version is one meaningful edit. One new presentational control, `ArtifactVersionNav`, draws back/forward arrows with a "3 of 7" indicator. It is mounted at artifact level on fixed-field editors (Base Resume Content, Job Resume, Cover Letter), per criterion on the candidate criteria pages, and at artifact level on the seven `candidate.context.*` pages (`ContextTextPage`). A move saves any unsaved edit first, calls AST-2067's `PUT …/current`, and then reloads the body through the existing current-read GET. No backend code changes here.

## Canon Scope (this ticket)

`patt.artifact.ui-consistency`, `patt.artifact.read-current`.

Resolved at `canon/directives/active/<id>.md`. The repo has no `docs/canon-index.md`, so the paths come from the parent's Architectural definition links (same as AST-2066 / AST-2067).

- **ui-consistency.** There is one shared nav component, and its placement comes from editor shape (fixed fields vs criteria) rather than from per-key forks. The client invents no storage keys. Saves keep using the existing `PUT /api/candidates/<id>/data` and `PUT /api/jobs/<id>/artifacts/<leaf>` contracts.
- **read-current.** After a move, the editor re-hydrates through the existing GETs (`/api/candidates/<id>`, `/api/jobs/<id>`). Both already overlay current rows for every key this ticket touches: `hydrate_operative_*_for_response` for base_resume and the seven context keys, `hydrate_rubric_artifacts_for_response` → `rubric_criteria_for_task(current_only=True)` for all seven rubric keys, and `hydrate_job_artifacts_for_display` → `get_job_current` for `job_resume` / `cover_letter`. No new blob readers.

## Explicit scope gate

Every file and change kind below comes from this ticket's `## Scope`:

- `src/ui/frontend/src/components/ArtifactVersionNav.tsx`: "shared back/forward arrows + position indicator control". This is Stage 1. The module also exports the version-map type and a pure position helper, so both editors read the map the same way.
- `src/ui/frontend/src/components/ArtifactEditor.tsx`: "blur-save replaces the autosave timer. Artifact-level nav for catalog keys, per-criterion nav in rubric mode. Flush unsaved edits before a move, reload after." These are Stages 2 and 3.
- `src/ui/frontend/src/components/ContextTextPage.tsx`: "artifact-level nav for the seven `candidate.context.*` pages, and reload after a move." This is Stage 4.

No other files change. `LabeledTextArea` / `ExperienceJobsEditor` expose no textarea `onBlur`, so blur is caught by a React `onBlur` on the editor's own `.dep-body` wrapper (React `onBlur` bubbles focusout from descendants). No CSS file is touched: styling is inline, the same way `ContextTextPage` and the existing status span do it, plus the existing `icon-control` class. The page files (`pages/*.tsx`, `JobAnalysisReportModal.tsx`) are not touched.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ArtifactVersionNav.tsx` | **New.** `VersionMap` type, `versionNavState()` helper, default `ArtifactVersionNav` control | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Remove `AUTOSAVE_MS` + timer; blur-save; `doSave` returns `boolean`; `reloadFromServer()` extracted from Cancel; version maps, `moveVersion`, artifact-level + per-criterion nav | ui |
| `src/ui/frontend/src/components/ContextTextPage.tsx` | Version map + nav in header; `handleSave` async → `boolean`; save-before-move; reload body after move | ui |

## Shared conventions (apply to every stage)

- **Routes (AST-2067, unchanged).** These are the six routes:

  | Surface | Base (`<base>`) | GET `<base>/versions` | PUT `<base>/current` body |
  |---|---|---|---|
  | Candidate catalog key | `/api/candidates/<cid>/artifacts/<full key>` | `{versions}` | `{"artifact_uuid": …}` |
  | Rubric criterion | `/api/candidates/<cid>/rubric/<rubric key>/<code>` | `{versions}` | `{"rubric_vector_uuid": …}` |
  | Job catalog key | `/api/jobs/<jid>/artifacts/<full key>` | `{versions}` | `{"artifact_uuid": …}` |

  Full key = `candidate.artifacts.${artifactKey}`, `candidate.context.${contextKey}`, or `job.artifacts.${jobPersistence.artifactKey}`. The rubric key is the page's existing `artifactKey` (`do_rubric`, …). Path segments built from keys and codes go through `encodeURIComponent` (dots survive). `selectedId` stays unencoded, matching every existing candidate URL in both files. `jobId` is encoded, matching existing job URLs.

- **Version map.** `{ [uuid]: { created_at, current: 0|1, position } }`, keyed by row uuid (index-by-id). Flask sorts JSON keys alphabetically, so **`position` (1 = oldest) is the only order contract**. `versionNavState` finds the `current === 1` entry's position, and the uuids at `position - 1` / `position + 1`, by `position`. Key order is never used.

- **When maps are fetched.** On every editor (re)load and after every successful save, awaited inside the save so a flush-then-move can never be overwritten by a late pre-move map. After a move, the PUT response's `versions` replaces that one map. A version GET that is non-OK or throws hides that nav (`null`). Nothing is toasted, because history display never blocks editing.

- **Move sequence (both editors).** (1) Wait for any in-flight blur-save. (2) If edits are still unsaved, save them as one version, and abort the move if that save fails (the save already toasts). (3) `PUT <base>/current`. On non-OK, toast the server's `error` and leave the body alone. (4) Apply the returned map. (5) Re-hydrate the body through the existing current-read GET (`patt.artifact.read-current` Implementation #3).

  ⚠️ **Decision:** Unsaved edits are saved before a move in **every** editor, including the explicit-Save ones (Cover Letter, the seven context pages). Parent Functional scope #5 states this without carving out explicit-Save editors. The alternatives would silently discard the draft or disable the arrows while dirty. The first loses work; the second blocks a stated behavior.

- **Nav disabled** while reviewing a Generate result (`snapshot !== null`, the AST-905 "no silent save while reviewing" rule), while Generate is running, and while a move is in flight. It is **not** disabled while `saving`: a click on an arrow blurs the field first, which starts a save, and disabling on `saving` would swallow that same click. The move waits for the pending save instead.

- **Empty history.** `total === 0` (no rows yet, e.g. a never-saved key or an embedded QC/GC/RC criterion with no `rubric_vector` rows) renders no nav. `1 of 1` renders with both arrows disabled.

---

## Stage 1: Shared `ArtifactVersionNav` control

**Done when:** `src/ui/frontend/src/components/ArtifactVersionNav.tsx` exists, `npx tsc -b` is clean, and eslint on the file is clean. No editor imports it yet.

1. Create `src/ui/frontend/src/components/ArtifactVersionNav.tsx` with exactly:

   ```tsx
   /** One row of an AST-2067 version map; `position` is 1 = oldest. */
   export interface VersionEntry {
     created_at: string
     current: number
     position: number
   }

   /** Version map keyed by row uuid (artifact_uuid / rubric_vector_uuid). */
   export type VersionMap = Record<string, VersionEntry>

   /**
    * Current position + neighbor uuids. Order comes from `position` only — the API's JSON keys
    * arrive sorted by uuid, not chronologically (AST-2067).
    */
   export function versionNavState(versions: VersionMap) {
     const ids = Object.keys(versions)
     const cur = ids.find(id => versions[id].current === 1)
     const position = cur ? versions[cur].position : 0
     const at = (p: number) => ids.find(id => versions[id].position === p) ?? null
     return { position, total: ids.length, backUuid: at(position - 1), forwardUuid: at(position + 1) }
   }

   interface ArtifactVersionNavProps {
     position: number
     total: number
     onBack: () => void
     onForward: () => void
     disabled?: boolean
   }

   /** Shared back/forward arrows + "N of M" for every versioned editor (patt.artifact.ui-consistency). */
   export default function ArtifactVersionNav({
     position,
     total,
     onBack,
     onForward,
     disabled = false,
   }: ArtifactVersionNavProps) {
     if (total === 0) return null
     // No current row (should not happen) → indicator only, no moves.
     const off = disabled || position < 1
     return (
       <span style={{ display: "inline-flex", alignItems: "center", gap: 6, marginRight: 8 }}>
         <button
           type="button"
           className="icon-control"
           aria-label="Previous version"
           title="Previous version"
           disabled={off || position <= 1}
           onClick={onBack}
         >
           ←
         </button>
         <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
           {position} of {total}
         </span>
         <button
           type="button"
           className="icon-control"
           aria-label="Next version"
           title="Next version"
           disabled={off || position >= total}
           onClick={onForward}
         >
           →
         </button>
       </span>
     )
   }
   ```

   ⚠️ **Decision:** The glyphs are `←` / `→`, not `◀` / `▶`. `CollapsiblePanel` already uses `▶` / `▼` as its expand chevron, and the per-criterion nav sits in that same header row.

   ⚠️ **Decision:** `versionNavState` lives in this file, not in each editor, so both editors read `position` the same way. It is a pure helper of the control, not an API call, so the component stays presentational (parent Technical scope).

## Stage 2: `ArtifactEditor` — blur-save replaces the autosave timer

**Done when:** `git grep -n "AUTOSAVE_MS" -- src/ui/frontend/src/components/ArtifactEditor.tsx` returns nothing and `tsc` / eslint are clean. By hand on Base Resume Content: typing 20+ characters into one section adds no `base_resume` row, blurring adds exactly 1, and focusing then blurring without an edit adds 0. On Do Job Criteria, focus/blur without an edit adds no `rubric_vector` row (ACs 1–3). Cancel still restores from the server on the explicit-Save job editors.

All edits are in `src/ui/frontend/src/components/ArtifactEditor.tsx`.

1. Delete the line `const AUTOSAVE_MS = 2000`.

2. Replace

   ```ts
     const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
   ```

   with

   ```ts
     // In-flight blur-save; an arrow move awaits it before deciding whether to flush (AST-2068).
     const pendingSaveRef = useRef<Promise<boolean> | null>(null)
   ```

3. Replace the comment line `// Criteria (free-form) and resume structure editors autosave bodies; shapesKey job editors keep explicit Save/Cancel.` with `// Criteria (free-form) and resume structure editors blur-save bodies; shapesKey job editors keep explicit Save/Cancel.` The `autosaveBodies` line under it is unchanged.

4. In `doSave`:
   - Change `const doSave = useCallback(async (t: SideTab[], autosave = false) => {` to `const doSave = useCallback(async (t: SideTab[], autosave = false): Promise<boolean> => {`.
   - In the experience-parse loop, change `return` (after `setToast({ text: unsupportedExperienceMessage, variant: "error" })`) to `return false`. Do the same for the `return` in the `buildPayload` `catch`.
   - In the `if (jobPersistence) {` branch:
     - Replace `if (tabsRef.current === t) setDirty(false)` with

       ```ts
               if (tabsRef.current === t) {
                 setDirty(false)
                 // Ref too: a move awaiting this save must not re-flush the same body before the next render.
                 dirtyRef.current = false
               }
       ```

     - Directly after `if (!autosave) jobPersistence.onSaved?.()`, add `return true`.
     - At the end of that branch's `catch` block (after its `setToast`), add `return false`.
     - Delete the bare `return` that follows that branch's `finally { setSaving(false) }` block. It is unreachable once both arms return.
   - Change `if (!selectedId) return` (directly before `setSaving(true)` in the candidate path) to `if (!selectedId) return false`.
   - In the candidate `try`, replace `if (tabsRef.current === t) setDirty(false)` with the same four-line block as above (`setDirty(false)` plus `dirtyRef.current = false`). Directly after `setToast({ text: "Saved", variant: "success" })` in that `try`, add `return true`.
   - In the candidate `catch`, after its `setToast`, add `return false`.

5. Replace the whole `handleChange` function with:

   ```ts
     function handleChange(next: SideTab[]) {
       setTabs(next)
       setDirty(true)
     }

     // Blur-save (AST-2068): a field losing focus after an edit saves one version; an unchanged blur saves
     // nothing. bodiesEditable is false while reviewing Generate, so review content never persists silently (AST-905).
     function handleBodyBlur() {
       if (!autosaveBodies || !bodiesEditable || !dirtyRef.current) return
       pendingSaveRef.current = doSave(tabsRef.current, true)
     }
   ```

6. In the unmount effect (`// Auto-save on unmount when dirty …`), delete the line `if (timerRef.current) clearTimeout(timerRef.current)`. The rest of the effect is unchanged.

7. Replace the whole `handleCancel` function with:

   ```ts
     /** Re-run the existing current-read GET hydrate (patt.artifact.read-current) — Cancel and after a version move. */
     function reloadFromServer() {
       if (jobPersistence) {
         if ((shapesKey || structureMode) && !fixedFieldKeys) return
         api(`/api/jobs/${encodeURIComponent(jobPersistence.jobId)}`).then(r => r.json()).then(job => {
           applyJobArtifactResponse(job)
           setDirty(false)
         }).catch(() => setJobLoadError(true))
         return
       }
       if (!selectedId || ((shapesKey || structureMode) && !fixedFieldKeys)) return
       api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
         applyCandidateArtifactResponse(c)
         setDirty(false)
       })
     }

     function handleCancel() {
       if (snapshot) {
         setTabs(snapshot)
         setSnapshot(null)
         setDirty(false)
         return
       }
       reloadFromServer()
     }
   ```

8. Change `<div className="dep-body">` (the one directly after the `dep-header` block's closing `</div>`) to `<div className="dep-body" onBlur={handleBodyBlur}>`.

⚠️ **Decision:** Every field blur inside the body counts, including moving between two inputs of one Experience job, the rename input, the code input, and the importance `<select>`. Each one that follows an edit saves one version. That is the parent's literal rule ("saved when a field loses focus and its text changed"), and rubric fingerprinting / the candidate identical no-op absorb any blur whose net body is unchanged.

⚠️ **Decision:** Button-only tab chrome (× remove, ▲/▼ reorder, + Add before its rename input autofocuses) marks the editor dirty but does not save on its own. The edit is saved by the next field blur, an arrow move, unmount, or the browser's existing `beforeunload` prompt, and the header shows "Unsaved changes" meanwhile. The rejected alternative was an immediate save inside `removeTab` / `moveTab`. That adds a save trigger the parent did not define, and Chrome already blurs the clicked button when focus moves on.

## Stage 3: `ArtifactEditor` — version arrows (artifact-level + per-criterion)

**Done when:** `tsc` / eslint are clean. By hand: Base Resume Content and JAR Cover Letter show `N of N` in the header, with back disabled at 1 and forward disabled at N. Pressing back shows the previous body and `N-1 of N`. On Do Job Criteria, each coded criterion shows its own arrows, and pressing back on one changes only that criterion's body and indicator. The JAR Application Questions tab shows no arrows and makes no `/versions` request. Typing into a section and then clicking back saves the typed edit as one new version before moving (AC 4).

All edits are in `src/ui/frontend/src/components/ArtifactEditor.tsx`.

1. Directly after `import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react"`, add:

   ```ts
   import ArtifactVersionNav, { versionNavState, type VersionMap } from "./ArtifactVersionNav"
   ```

2. Directly after the `criteriaToTabs` function (before `export default function ArtifactEditor(`), add:

   ```ts
   /** AST-2067 per-criterion version route base (rubric criteria key + shared code). */
   function rubricCriterionVersionsBase(candidateId: string, artifactKey: string, code: string) {
     return `/api/candidates/${candidateId}/rubric/${encodeURIComponent(artifactKey)}/${encodeURIComponent(code)}`
   }
   ```

3. Directly after `const [editingId, setEditingId] = useState<string | null>(null)`, add:

   ```ts
     // AST-2068 version arrows: maps keyed by row uuid; per-criterion maps keyed by rubric code.
     const [artifactVersions, setArtifactVersions] = useState<VersionMap | null>(null)
     const [criterionVersions, setCriterionVersions] = useState<Record<string, VersionMap>>({})
     const [moving, setMoving] = useState(false)
   ```

4. Directly after the `fixedFieldKeys` declaration (the `const fixedFieldKeys = fixedFields ? … : ""` block), add:

   ```ts
     // Artifact-level arrows on fixed-field bodies only (resume_content structure, cover_letter shape) —
     // chosen by editor shape, not a key list. Candidate criteria step per criterion instead; job dict
     // editors (Application Questions) are not catalog artifacts and get none.
     const artifactVersionsBase = !fixedFields
       ? null
       : jobPersistence
         ? `/api/jobs/${encodeURIComponent(jobPersistence.jobId)}/artifacts/${encodeURIComponent(`job.artifacts.${jobPersistence.artifactKey}`)}`
         : selectedId
           ? `/api/candidates/${selectedId}/artifacts/${encodeURIComponent(`candidate.artifacts.${artifactKey}`)}`
           : null
     // Free-form criteria chrome on a candidate page = rubric_vector criteria.
     const criterionVersionsOn = tabChromeEditable && !jobPersistence && !!selectedId
   ```

5. Directly before the comment `// Build the payload from current tabs`, add:

   ```ts
     /** Fetch version maps (on load + after each save). Non-OK / network error → that nav hides; never blocks editing. */
     const refreshVersions = useCallback(async () => {
       const getVersions = async (base: string): Promise<VersionMap | null> => {
         try {
           const r = await api(`${base}/versions`)
           return r.ok ? ((await r.json()).versions as VersionMap) : null
         } catch {
           return null
         }
       }
       if (artifactVersionsBase) {
         const v = await getVersions(artifactVersionsBase)
         if (mountedRef.current) setArtifactVersions(v)
       }
       if (criterionVersionsOn && selectedId) {
         // Every coded criterion: the client cannot tell which codes the server just appended/upticked.
         const codes = [...new Set(tabsRef.current.map(t => t.code).filter((c): c is string => !!c))]
         const pairs = await Promise.all(
           codes.map(async c => [c, await getVersions(rubricCriterionVersionsBase(selectedId, artifactKey, c))] as const),
         )
         if (!mountedRef.current) return
         const next: Record<string, VersionMap> = {}
         for (const [c, v] of pairs) if (v) next[c] = v
         setCriterionVersions(next)
       }
     }, [artifactVersionsBase, criterionVersionsOn, selectedId, artifactKey])

     // Version maps follow every (re)load; clear on unload so a previous candidate's map never drives a move.
     useEffect(() => {
       if (!loaded) {
         setArtifactVersions(null)
         setCriterionVersions({})
         return
       }
       void refreshVersions()
     }, [loaded, refreshVersions])
   ```

6. In `doSave`, directly after **each** `setToast({ text: "Saved", variant: "success" })` (one in the job branch, one in the candidate branch), add `await refreshVersions()`, placed before that branch's `return true` / `onSaved` line. Add `refreshVersions` as the last entry of `doSave`'s dependency array (after `structureRows,`).

   ⚠️ **Decision:** `await`, not `void`. A save that flushes before a move must finish refreshing before the move's `PUT …/current`. Otherwise a late pre-move GET could overwrite the move's returned map and show the wrong `N of M`. `refreshVersions` never throws.

7. Directly after the `reloadFromServer` function (Stage 2 step 7), add:

   ```ts
     /** Arrow move (AST-2068): flush unsaved edits as one version, move current, re-hydrate via current-read GET. */
     async function moveVersion(base: string, body: Record<string, string>, apply: (v: VersionMap) => void) {
       setMoving(true)
       try {
         if (pendingSaveRef.current) await pendingSaveRef.current
         // autosave=true: job editors must not fire onSaved (modal reload would unmount mid-move).
         if (dirtyRef.current && !(await doSave(tabsRef.current, true))) return
         const resp = await api(`${base}/current`, {
           method: "PUT",
           headers: { "Content-Type": "application/json" },
           body: JSON.stringify(body),
         })
         if (!resp.ok) {
           const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
           throw new Error(err.error || `Move failed (${resp.status})`)
         }
         const data = await resp.json()
         if (!mountedRef.current) return
         apply(data.versions as VersionMap)
         reloadFromServer()
       } catch (e) {
         if (mountedRef.current) setToast({ text: (e as Error).message || "Move failed", variant: "error" })
       } finally {
         if (mountedRef.current) setMoving(false)
       }
     }

     function renderVersionNav(versions: VersionMap, base: string, uuidField: string, apply: (v: VersionMap) => void) {
       const nav = versionNavState(versions)
       const go = (uuid: string | null) => {
         if (uuid) void moveVersion(base, { [uuidField]: uuid }, apply)
       }
       return (
         <ArtifactVersionNav
           position={nav.position}
           total={nav.total}
           // Not `saving`: an arrow click blurs the field first; moveVersion awaits that save instead.
           disabled={inReview || generating || moving}
           onBack={() => go(nav.backUuid)}
           onForward={() => go(nav.forwardUuid)}
         />
       )
     }

     function renderCriterionNav(code: string) {
       const versions = criterionVersions[code]
       if (!criterionVersionsOn || !selectedId || !versions) return null
       return renderVersionNav(
         versions,
         rubricCriterionVersionsBase(selectedId, artifactKey, code),
         "rubric_vector_uuid",
         v => setCriterionVersions(prev => ({ ...prev, [code]: v })),
       )
     }
   ```

8. In the JSX, directly after `<div className="dep-actions">` (inside `dep-header`, before `{canGenerate && (`), add:

   ```tsx
               {artifactVersionsBase && artifactVersions
                 && renderVersionNav(artifactVersions, artifactVersionsBase, "artifact_uuid", setArtifactVersions)}
   ```

9. In the `CollapsiblePanel` `actions` prop, inside `<span className="side-tab-controls">`, directly before `{!rubricMode && (`, add:

   ```tsx
                         {tab.code ? renderCriterionNav(tab.code) : null}
   ```

   The actions slot already calls `stopPropagation` on click (`CollapsiblePanel`), so arrow clicks do not toggle the panel. The arrows sit inside `.dep-body`, so tabbing or clicking from a textarea to an arrow blur-saves first, and the move awaits that save.

⚠️ **Decision:** Per-criterion arrows apply to **all seven** candidate criteria pages (`company_prefilter`, `joblist_rubric`, `jobdesc_rubric`, `do_rubric`, `get_rubric`, `like_rubric`, `meteorite_jobdesc_rubric`), not six. They all share the one rubric-mode path and are all `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` keys, so excluding one would need a per-key fork (ui-consistency). The parent's "six" appears to be a miscount. Company Search Terms is not an `ArtifactEditor` page and is untouched.

⚠️ **Decision:** A criterion gets arrows only once it has a `code`. A brand-new criterion has none on the client until the page next loads (the save path assigns codes server-side and `doSave` does not re-hydrate tabs). It gets arrows on the next load. Re-hydrating after every blur-save would reset the focus and caret mid-edit.

⚠️ **Decision:** After each save, every coded criterion's map is re-fetched (one GET per criterion, at most `MAX_ARTIFACT_TABS` = 15). Diffing which codes changed would be a client-side shortcut that can miss server-side code upticks (AST-2008), so it is not used here. If Susan wants it narrowed, that is a follow-up.

⚠️ **Decision:** `resume_structure` gets no arrows. Base Resume Content only ever requests `candidate.artifacts.${artifactKey}` = `candidate.artifacts.base_resume` (AST-2067 Resolution, Discuss 2).

## Stage 4: `ContextTextPage` — artifact-level arrows on the seven context pages

**Done when:** `tsc` / eslint are clean. By hand on Bio Summary: the header shows `N of N`, with back disabled at 1 and forward disabled at N. Pressing back shows the previous text and `N-1 of N`. Save still works, and a changed Save advances to `N+1 of N+1`. Typing an edit and then pressing back saves the edit first (`N+1`), then moves to `N of N+1`. With an empty draft on a `plain_text` page, pressing back shows the existing "cannot be empty" toast and does not move (AC 4).

All edits are in `src/ui/frontend/src/components/ContextTextPage.tsx`.

1. Directly after `import api from "../lib/api"`, add:

   ```ts
   import ArtifactVersionNav, { versionNavState, type VersionMap } from "./ArtifactVersionNav"
   ```

2. Directly after `const plainTextEmpty = bodyShape === "plain_text" && !draft.trim()`, add:

   ```ts
     const [versions, setVersions] = useState<VersionMap | null>(null)
     const [moving, setMoving] = useState(false)
     // AST-2067 version routes take the full catalog key.
     const versionsBase = selectedId
       ? `/api/candidates/${selectedId}/artifacts/${encodeURIComponent(`candidate.context.${contextKey}`)}`
       : null

     /** Current-read GET (patt.artifact.read-current) — initial load and after a move. */
     const loadBody = useCallback(async () => {
       if (!selectedId) return
       const c = await api(`/api/candidates/${selectedId}`).then(r => r.json())
       const val = coerceToString(c.candidate_data?.context?.[contextKey])
       setSaved(val)
       setDraft(val)
     }, [selectedId, contextKey])

     /** Version map; non-OK / network error → no arrows, editing unaffected. */
     const refreshVersions = useCallback(async () => {
       if (!versionsBase) return
       try {
         const r = await api(`${versionsBase}/versions`)
         setVersions(r.ok ? ((await r.json()).versions as VersionMap) : null)
       } catch {
         setVersions(null)
       }
     }, [versionsBase])
   ```

3. Replace the existing load `useEffect` (the one that starts `useEffect(() => {` / `if (!selectedId) return` / `setLoading(true)` and ends `}, [selectedId, contextKey])`) with:

   ```ts
     useEffect(() => {
       if (!selectedId) return
       setLoading(true)
       setVersions(null)
       void refreshVersions()
       loadBody().finally(() => setLoading(false))
     }, [selectedId, loadBody, refreshVersions])
   ```

4. Replace the whole `handleSave` function with:

   ```ts
     async function handleSave(): Promise<boolean> {
       /* v8 ignore next -- @preserve */
       if (!selectedId) return false
       if (bodyShape === "plain_text" && !draft.trim()) {
         setToast({ text: `${title} cannot be empty`, variant: "error" })
         return false
       }
       try {
         const r = await api(`/api/candidates/${selectedId}/data`, {
           method: "PUT",
           headers: { "Content-Type": "application/json" },
           body: JSON.stringify({ context: { [contextKey]: draft } }),
         })
         if (!r.ok) {
           const e = await r.json()
           throw new Error(e.error || "Save failed")
         }
         const c = await r.json()
         const val = coerceToString(c.candidate_data?.context?.[contextKey]) || draft
         setSaved(val)
         setDraft(val)
         setToast({ text: `${title} saved`, variant: "success" })
         // Awaited: a save-before-move must refresh before the move's PUT (no late stale map).
         await refreshVersions()
         return true
       } catch (e) {
         setToast({ text: (e as Error).message, variant: "error" })
         return false
       }
     }

     /** Arrow move (AST-2068): save an unsaved draft as one version first, move current, reload via current-read GET. */
     async function handleMove(uuid: string | null) {
       if (!uuid || !versionsBase) return
       setMoving(true)
       try {
         if (draft !== saved && !(await handleSave())) return
         const r = await api(`${versionsBase}/current`, {
           method: "PUT",
           headers: { "Content-Type": "application/json" },
           body: JSON.stringify({ artifact_uuid: uuid }),
         })
         if (!r.ok) {
           const e = await r.json().catch(() => ({ error: `HTTP ${r.status}` }))
           throw new Error(e.error || `Move failed (${r.status})`)
         }
         setVersions((await r.json()).versions as VersionMap)
         await loadBody()
       } catch (e) {
         setToast({ text: (e as Error).message || "Move failed", variant: "error" })
       } finally {
         setMoving(false)
       }
     }
   ```

   The Save behavior is unchanged: the same request, the same toasts, the same `|| draft` fallback, and the same plain-text guard. The function is just `async` now, returns success, and refreshes the map.

5. Directly before the component's final `return (` (after the two early-return `if (loading)` / `if (!selectedId)` lines), add:

   ```ts
     const nav = versions ? versionNavState(versions) : null
   ```

6. In the JSX, inside `<div className="dep-actions">`, directly before `<button className="btn secondary" onClick={handleCancel}>Cancel</button>`, add:

   ```tsx
               {nav && (
                 <ArtifactVersionNav
                   position={nav.position}
                   total={nav.total}
                   disabled={moving}
                   onBack={() => void handleMove(nav.backUuid)}
                   onForward={() => void handleMove(nav.forwardUuid)}
                 />
               )}
   ```

7. Change `<button className="btn primary" onClick={handleSave} disabled={plainTextEmpty}>Save</button>` to `<button className="btn primary" onClick={() => void handleSave()} disabled={plainTextEmpty}>Save</button>`. Otherwise the click event would be passed into the now-`async` function and its promise left floating.

⚠️ **Decision:** The explicit Save stays (parent Technical scope). No blur-save on context pages.

## Verification (build-child §7)

Run from the epic worktree. `node_modules` is not installed in `astral-AST-2043/src/ui/frontend/` today, so install it first (it is gitignored, so nothing gets committed):

```bash
cd src/ui/frontend
[ -d node_modules ] || npm ci
npx tsc -b
npx eslint src/components/ArtifactVersionNav.tsx src/components/ArtifactEditor.tsx src/components/ContextTextPage.tsx
cd ../../..
git grep -n "AUTOSAVE_MS" -- src/ui/frontend/src/components/ArtifactEditor.tsx   # AC 3: no output
```

- `tsc` must be clean and eslint must report no findings on the three files. If eslint already flags pre-existing lines in `ArtifactEditor.tsx` / `ContextTextPage.tsx` on the untouched base, record that baseline count in the Review section first. The count must not rise, and no finding may point at an AST-2068 line.
- Run each stage's **Done when** by hand through `launch.sh` (Flask `:5001` + Vite `:5173`) from the epic worktree. Count rows with `list_artifacts` / `list_rubric_vectors(..., current_only=False)` in a Python shell. Any scratch output goes under `debug/spikes/AST-2068/` and is never committed.
- No `tests/` edits (engineer test-tree ban).

## Notes for QA (Betty, informational only; no test-tree work in this ticket)

- **Likely-affected existing tests:** `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (anything driving the 2 s timer with fake timers now needs a blur; extra `/versions` GETs on load and after save), `test_ContextTextPage.test.tsx` and the seven `pages/test_Candidate*.test.tsx` (an extra `/versions` GET on load and after Save; Save is now `async`), and `pages/test_ArtifactsBaseResumeContent.test.tsx` (save timing).
- **AC 1/2 (blur):** type, then blur → exactly one PUT; focus then blur with no edit → no PUT; while `snapshot` (Generate review) is set, blur → no PUT.
- **AC 4 (arrows):** back disabled at `1 of N`, forward disabled at `N of N`; back → PUT `…/current` with the `position - 1` uuid (chosen by `position`, never by JSON key order), then the current-read GET re-runs. Surfaces: Base Resume Content and JAR Cover Letter (header), Bio Summary (`ContextTextPage` header), and one Do Job Criteria criterion (panel actions).
- **Negative surfaces:** JAR Application Questions has no arrows and makes no `/versions` request. Base Resume Content never requests `resume_structure` versions. Company Search Terms is untouched.
- **Move with unsaved edit:** one save PUT, then the `…/current` PUT, in that order. If the save fails, there is no `…/current` PUT.

## Estimate

Confirm Chuckles estimate: 3 — agree
