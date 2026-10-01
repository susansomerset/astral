# AST-1917 — Scheduled Actions header dropdown

- **Parent:** [AST-1875 — add a selection box on Scheduled Tasks to set concurrent tasks limit](https://linear.app/astralcareermatch/issue/AST-1875)
- **Ticket:** [AST-1917](https://linear.app/astralcareermatch/issue/AST-1917)
- **Publish ref:** `sub/AST-1875/AST-1917-header-dropdown` (origin only)

Sibling AST-1916 (User Testing, merged to `origin/ftr/AST-1875-runtime-auto-thread-cap`) made the scheduler read its AUTO-thread cap live each tick and exposed it as `GET` / `POST /api/admin/scheduler/auto_thread_cap`. This ticket adds the operator control: a `<select>` in the Scheduled Actions page header, pre-selected to the live effective cap, whose options are generated from the `min` / `max` bounds the API returns (which come from `ASTRAL_CONFIG` — no 1/100 literals in the page). Picking a value POSTs it; the select reflects the server-returned value and reverts on any error. No backend changes.

## API contract consumed (from AST-1916, verified on this branch)

- `GET /api/admin/scheduler/auto_thread_cap` → `200` `{"max_auto_threads": <effective int>, "default": <config int>, "min": <config int>, "max": <config int>}`
- `POST /api/admin/scheduler/auto_thread_cap` with JSON body `{"max_auto_threads": <int>}` → `200` with the same payload as GET, or `400` `{"error": "..."}` (cap unchanged). The setter rejects strings/floats/bools, so the body **must** carry a JSON number.
- Both routes are `@require_admin` (`src/ui/api/api_admin.py` lines 2118–2142).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `AutoThreadCap` type + path const; state; one-shot GET on mount; POST change handler (optimistic, revert on error); header `<select>` with options generated from `min..max` | ui |

This is the only file in this ticket's `## Scope`. No new component file (`astral.ui.frontend-file-placement` — the control is ~15 lines of JSX in the page that owns the header). No CSS changes.

---

## Stage 1: Header dropdown wired to the cap API

**Done when:** With the dev server running and an admin session, opening Scheduled Actions shows a "Max AUTO threads" select at the left of the header controls cluster, pre-selected to `3` on a fresh start, offering exactly 1..100. Choosing `7` sends `POST /api/admin/scheduler/auto_thread_cap` with body `{"max_auto_threads":7}`, the select stays on 7, and a reload shows 7. When the POST fails (e.g. stopping the backend first), the select reverts to the previous value and an error toast appears.

All edits are in `src/ui/frontend/src/pages/AdminScheduledActions.tsx`.

1. Directly after the closing `}` of `interface ThreadEntry { ... }` (currently line 106), insert a blank line, then:

   ```ts
   // AST-1917: payload of GET/POST /api/admin/scheduler/auto_thread_cap (AST-1916). min/max come from
   // ASTRAL_CONFIG via the API so the dropdown range is never hardcoded in this page.
   type AutoThreadCap = { max_auto_threads: number; default: number; min: number; max: number }

   const AUTO_THREAD_CAP_PATH = "/api/admin/scheduler/auto_thread_cap"
   ```

2. Inside `ScheduledActions()`, directly after the line `const [stoppingAll, setStoppingAll] = useState(false)` (currently line 356), insert:

   ```ts

     // AST-1917: live AUTO-thread cap for the header dropdown (null until loaded → dropdown hidden)
     const [autoThreadCap, setAutoThreadCap] = useState<AutoThreadCap | null>(null)
   ```

3. Directly after the thread-status polling `useEffect` (the block ending `}, [loadThreadStatus])`, currently line 373), insert:

   ```ts

     useEffect(() => {
       // One-shot load on mount. Silent on failure, like loadThreadStatus: no dropdown rather than a wrong one.
       void (async () => {
         try {
           const res = await api(AUTO_THREAD_CAP_PATH)
           if (res.ok) setAutoThreadCap(await res.json())
         } catch {
           // network/parse failure → leave the dropdown hidden
         }
       })()
     }, [])
   ```

4. Directly after the `handleKillAll` function (ends with its closing `}` after `setStoppingAll(false)`'s `finally` block, currently line 652), insert:

   ```ts

     const handleAutoThreadCapChange = async (next: number) => {
       const prev = autoThreadCap
       if (!prev) return
       // Optimistic so the select doesn't snap back while the POST is in flight; reverted on any failure.
       setAutoThreadCap({ ...prev, max_auto_threads: next })
       try {
         const res = await api(AUTO_THREAD_CAP_PATH, {
           method: "POST",
           headers: { "Content-Type": "application/json" },
           // Must be a JSON number — the dispatcher setter rejects strings (AST-1916 strict type check).
           body: JSON.stringify({ max_auto_threads: next }),
         })
         if (!res.ok) await readApiError(res, AUTO_THREAD_CAP_PATH, "POST") // always throws ApiError
         setAutoThreadCap(await res.json()) // server-returned value is authoritative
       } catch (e) {
         setAutoThreadCap(prev)
         setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: "Failed to set max AUTO threads", variant: "error" })
       }
     }
   ```

5. In the returned JSX, inside `<div className="list-page-header">`'s controls `<div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>` (currently line 772), insert as the **first** child — before the `{activeThreads.length > 0 && (` running badge:

   ```tsx
             {autoThreadCap && (
               <label
                 style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}
                 title={`Max AUTO tasks running at once (config default ${autoThreadCap.default}). Manual Run is not capped. Resets to the default on server restart.`}
               >
                 Max AUTO threads
                 <select
                   value={autoThreadCap.max_auto_threads}
                   onChange={e => { void handleAutoThreadCapChange(Number(e.target.value)) }}
                 >
                   {/* min..max inclusive, step 1 — bounds from the API, never literals */}
                   {Array.from({ length: autoThreadCap.max - autoThreadCap.min + 1 }, (_, i) => autoThreadCap.min + i).map(n => (
                     <option key={n} value={n}>{n}</option>
                   ))}
                 </select>
               </label>
             )}
   ```

6. Add no imports — `useEffect`, `useState`, `api`, `readApiError`, `ApiError`, `errorToastFromApiError`, and `setToast` already exist in this file. Change nothing else in the file.

⚠️ **Decision:** Load the cap in its own one-shot mount `useEffect`, not inside `loadData`'s `Promise.all`. `loadData` re-runs every time a thread finishes, so folding the cap in would re-fetch it constantly for no benefit. The cap only changes through this control (process-local override, single worker), so one load plus the POST response is enough.

⚠️ **Decision:** If the GET fails, the dropdown stays hidden and no toast is shown. That matches the existing `loadThreadStatus` header idiom (non-ok is ignored silently). It also keeps current page tests stable: their `installBaseApiMocks` (`tests/component/frontend/test-utils.tsx`) throws `Unhandled api …` for unknown URLs, and the `try/catch` absorbs that instead of adding a stray toast to every existing test. The alternative was an error toast on load failure. I rejected it for this pass because it would put a toast into every existing page test that doesn't mock the new route.

⚠️ **Decision:** Optimistic update plus explicit revert, rather than leaving the controlled select on the old value until the POST returns. Without the optimistic step, the select visibly snaps back to the old number during the round-trip. The Scope's "reflects the server-returned value (reverts on error)" is satisfied by `setAutoThreadCap(await res.json())` on success and `setAutoThreadCap(prev)` in the `catch`, which covers both HTTP errors (via `readApiError`, which always throws) and network failures.

⚠️ **Decision:** Options are computed inline in JSX (`Array.from` over `min..max`) with no `useMemo`. That's 100 small elements, rebuilt only when the page re-renders. A memo would add lines and a hooks-deps question for no measurable gain.

⚠️ **Decision:** The label is "Max AUTO threads", not "Concurrent tasks". Only AUTO threads are capped (CLICK / manual Run is outside the cap, parent Functional scope 4), so the label says exactly what the number governs. The tooltip states the config default (from the API's `default` field), that manual Run is uncapped, and that restart resets it. Susan can rename at UAT; the change is a single string.

⚠️ **Decision:** No `disabled` / saving state on the select during the POST. The optimistic update already reflects the choice, and a second pick mid-flight just issues another POST whose response wins. Adding a saving flag would cost another state variable for one short round-trip.

## Compile / lint (before commit)

From `src/ui/frontend/` (run `npm ci` first if `node_modules/` is absent in the epic worktree):

- `npm run build` (runs `tsc -b && vite build`): must pass.
- `npm run lint`: no new problems in `src/pages/AdminScheduledActions.tsx` compared with the same command on the pre-change tree.
- `grep -nE '\b100\b' src/pages/AdminScheduledActions.tsx` shows nothing (AC 3).

## Notes for Betty (not engineer work)

- Existing `tests/component/frontend/pages/test_AdminScheduledActions*.test.tsx` mocks do not route `/api/admin/scheduler/auto_thread_cap`. After this change those tests should still pass, because the throw is caught and the dropdown stays hidden. New dropdown coverage will need a mock for GET (payload above) and POST.

## Execution contract

Execute steps in order. Do not add files, imports, CSS, state, or behaviour beyond this plan. If a referenced anchor has drifted (e.g. `interface ThreadEntry`, `handleKillAll`, or the header controls `<div>` is gone or renamed, or the API payload differs from the contract above), stop and post on the parent:

```
🛑 Stage 1 blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Acceptance criteria map

| AC | Covered by |
|----|------------|
| 1 Default shown | Step 3 loads `max_auto_threads` (config default until changed); step 5 binds it as the select value |
| 2 Range 1..100 | Step 5 generates `min..max` inclusive, step 1, from the API bounds (`ASTRAL_CONFIG` 1 / 100) |
| 3 Single source for bounds (UI half) | No numeric bound literals in the page; options derive from `autoThreadCap.min` / `.max` |

## Canon

| Directive | How the plan complies |
|-----------|-----------------------|
| `astral.layers.ui-config-driven-business-logic` | Range and default are resolved server-side from `ASTRAL_CONFIG` and served by the API; React only renders them |
| `astral.ui.frontend-file-placement` | Change stays in the existing flat `src/pages/AdminScheduledActions.tsx`; no new files |
| `astral.config.config-source-of-truth` | No second copy of the default or bounds in TSX; `config.py` remains the single source |

## Estimate

Confirm Chuckles estimate: 1 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1917
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `origin/sub/AST-1875/AST-1917-header-dropdown` @ `e5c8aaac787adf90314285a8b66c1b1149d8633e`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.ui.frontend-file-placement | A | | |
| astral.config.config-source-of-truth | A | | |

## Traceability

AC 1→Stage 1 steps 3+5 (GET `max_auto_threads` binds select; fresh server ⇒ effective equals config default); AC 2→step 5 (`min..max` inclusive step 1 from API); AC 3→steps 5+lint `grep` (no bound literals). Parent AC 3–9 N/A (backend #1). Stage 1→parent Purpose 3, Functional scope 3–4, parent AC 8 UI half.

## Findings

**discuss** — Location: Stage 1 step 3 / Decision (silent GET failure)  
Child AC 1 fails if the dropdown is absent; hiding the control on GET failure matches `loadThreadStatus` but means a broken cap API looks like “no dropdown” with no toast. Acceptable for build; flag for UAT if Susan wants visible load errors.

**acceptable** — Location: ticket assignee vs validate-plan gate  
Assignee is implementer (Hedy), not Joan; spawn still requested review — Chuckles should restore assignee after posting upshot per §8.

**acceptable** — Location: plan doc (no `## Self-assessment`)  
Scope is single-file, one stage; explicit Decisions cover risk (optimistic UI, test mocks). Not `!!-NONE` conf.

**acceptable** — Location: Done-when / Stage 1  
“Pre-selected to `3`” and “1..100” describe today’s config/API, not TS literals; runtime range stays API-driven.

context_tokens≈42000

## Review (build)

**Built:** `sub/AST-1875/AST-1917-header-dropdown` @ `774ace245`
**Scope:** `AdminScheduledActions.tsx` only — `AutoThreadCap` type + path const, cap state, one-shot GET on mount (silent on failure), optimistic POST handler with revert + toast, header "Max AUTO threads" `<select>` with options generated from API `min..max`.
**Checks:** `tsc -b --noEmit` clean; `npm run build` green; eslint on the page shows only the 2 pre-existing `no-extra-boolean-cast` errors (same as pre-change tree); no `\b100\b` in the page (AC 3); existing `test_AdminScheduledActions*.test.tsx` 79/79 green (new route unmocked → caught, dropdown hidden).
**Betty:** new coverage needs mocks for GET (payload `{max_auto_threads, default, min, max}`) and POST (200 same payload / 400 `{error}`): default selected, `min..max` option count, POST body is a JSON number, revert + toast on 400.
