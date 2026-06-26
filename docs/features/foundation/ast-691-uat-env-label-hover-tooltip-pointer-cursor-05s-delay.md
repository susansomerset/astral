<!-- linear-archive: AST-691 archived 2026-06-23 -->

## Linear archive (AST-691)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-691/uat-env-label-hover-tooltip-pointer-cursor-05s-delay  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-675 — Create a ticket log in utils  
**Blocked by / blocks / related:** parent: AST-675

### Description

## What failed

After AST-690 (click popup), staging still fails Susan's UAT: the deploy footer environment label shows an **I-beam (text) cursor** instead of a pointer, and Susan does not get a reliable hover tooltip. The click-popup interaction is not what she wants.

## Expected

* **Cursor:** `pointer` (hand) on the environment label when merge tickets exist — never I-beam/text cursor.
* **Interaction:** **Hover** tooltip (not click-to-toggle). Tooltip appears after **0.5 seconds** of hover on the environment label.
* **Content:** Up to **20** lines, most recent first, one ticket per line.
* **Exact line format** (each line, no prefix bullets):

```
AST-675 6/15/26, 1:23:45 PM
AST-646 6/14/26, 3:45:12 PM
```

Pattern: `{TICKET_ID} {fmtTime(recorded_at)}` — ticket id, space, locale datetime from existing `fmtTime` (en-US, admin timezone). Empty/missing `merge_tickets` → no tooltip, static env label, default cursor.

## Repro

1. Log in as admin on staging with `ASTRAL_DEPLOY_ENV` set (e.g. `dev`) and at least one entry in merge ticket log.
2. Open left nav deploy footer; hover the environment label.
3. **Observed:** I-beam cursor; click popup from AST-690 — not a 0.5s hover tooltip.
4. **Expected:** pointer cursor; after 0.5s hover, tooltip shows lines like `AST-675 6/15/26, 1:23:45 PM` (up to 20).

## Parent AC (quoted inline)

> 4. With `ASTRAL_DEPLOY_ENV` set and admin session, hovering the environment label shows up to **20** ticket lines (id + timestamp), most recent first, separated by line breaks.

## Boundaries

* Does not change merge log, append tool, finish-up, deploy-status API, or non-admin nav.
* Replaces AST-690 click-popup UX with hover-delay tooltip + pointer cursor only.

### Comments

#### betty — 2026-06-16T00:34:09.897Z
## QA test manifest (AST-691)

**Publish ref:** `origin/sub/AST-675/ast-691-uat-env-label-hover-tooltip-pointer-cursor-05s-delay` @ `66d35ac` (`merge-tests(AST-691): origin/tests 081a83c3`)

**Bible shasum:** `docs/test-bible/frontend/components.md` → `e6f6873d108f4efbb7a8e200fa70ffdfb6ecb5e8fc9e3dec050e4d80d85527b9`

### 1. Broken / obsolete (revised this pass)
Replaced AST-690 click-popup tests with hover-delay tooltip coverage in `tests/component/frontend/components/test_AdminDeployFooter.test.tsx`:
- `test_shows_merge_ticket_tooltip_after_500ms_hover_on_env_wrap_when_merge_tickets_present`
- `test_hides_merge_ticket_tooltip_before_500ms_hover_and_on_mouse_leave`
- `test_renders_static_environment_span_when_merge_tickets_empty_or_missing` (no `nav-deploy-env-interactive`, no tooltip)
- `test_caps_merge_ticket_tooltip_at_20_lines`

### 2. Existing coverage (unchanged)
- `test_AdminDeployFooter.test.tsx` — env + uptime success, env omitted, deploy_status error
- `test_NavigationShell.test.tsx` — admin footer visible; non-admin absent

### 3. Run gate (test-child)

```bash
cd src/ui/frontend && npx tsc -b --noEmit

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx
```

— Betty

#### katherine — 2026-06-15T20:45:30.860Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-675/ast-691-uat-env-label-hover-tooltip-pointer-cursor-05s-delay/docs/features/foundation/ast-691-uat-env-label-hover-tooltip-pointer-cursor-05s-delay.md

**Self-assessment**

- **Scope:** `Single-Component` — replaces AST-690 click popup in `AdminDeployFooter.tsx` + `App.css` only; no API/utils changes.
- **Conf:** `high` — standard 500ms hover timer on env wrap; reuses `mergeTicketDisplayLines` / `fmtTime`; span + `cursor: pointer` instead of button.
- **Risk:** `low` — admin deploy footer only; failure modes are wrong tooltip text or hover UX, not auth or dispatch.

**Approach:** Remove click-toggle popup; show positioned tooltip after `MERGE_TICKET_HOVER_DELAY_MS = 500` on wrapper hover; plain div lines (no bullets); static span when `merge_tickets` empty.

---

# UAT: env label hover tooltip pointer cursor 0.5s delay

**Linear:** [AST-691 — UAT: env label hover tooltip pointer cursor 0.5s delay](https://linear.app/astralcareermatch/issue/AST-691/uat-env-label-hover-tooltip-pointer-cursor-05s-delay)

**Parent:** [AST-675 — Create a ticket log in utils](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (AC reference only — do not implement sibling scope)

**Publish ref:** `origin/sub/AST-675/ast-691-uat-env-label-hover-tooltip-pointer-cursor-05s-delay` (origin only)

## Summary

AST-690 shipped a **click-to-toggle** popup on the admin deploy environment label. Susan’s staging UAT still fails parent AC 4: the label shows an **I-beam (text) cursor** and she wants a **hover** tooltip (not click), appearing after **0.5 seconds** of hover. This bug **replaces** the AST-690 click-popup UX with a delayed hover tooltip and explicit **pointer** cursor when `merge_tickets` is non-empty. Content remains up to **20** lines of `{TICKET_ID} {fmtTime(recorded_at)}`, most recent first, with line breaks and **no** list bullets. No backend, API, log, or finish-up changes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | Remove click popup; add 500ms hover tooltip; pointer cursor on interactive env | ui |
| `src/ui/frontend/src/App.css` | Tooltip panel styles; pointer on interactive env; remove button/popup click styles | ui |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/frontend/src/components/NavigationShell.tsx` | Admin-only footer gating unchanged (AC 6) |
| `src/utils/deploy_status.py` | `merge_tickets` payload unchanged |
| `src/ui/api/api_system.py` | `GET /api/deploy_status` unchanged |

**QA manifest (Betty — not engineer commits):** Betty updates `tests/component/frontend/components/test_AdminDeployFooter.test.tsx` at **Code Complete** (`qa-child`). Engineer does not commit under `tests/` or `docs/test-bible/**` (pre-commit hook).

**Out of scope:** merge ticket log / append tool (AST-681), finish-up wiring (AST-683), deploy-status API shape, non-admin nav, SHA in entries, Linear API for titles, reintroducing native `title` on the env label.

---

## Stage 1: Hover-delay tooltip on environment label

**Done when:** With `environment` set and non-empty `merge_tickets`, the env label is a **span** (not a button) with `cursor: pointer`; hovering the env label **or** its tooltip panel for **0.5s** shows a tooltip with up to 20 plain-text lines (`AST-NNN <fmtTime>`), most recent first, separated by line breaks, **no** `<ul>` / bullets; moving pointer off the env wrap hides the tooltip and cancels a pending show; when `merge_tickets` is empty or missing the env label is a static span with default cursor and no tooltip; no `title` on env label; no click-to-toggle behavior; uptime, error branch, poll interval, and absent-environment layout unchanged; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/AdminDeployFooter.tsx`, adjust React imports to keep `useEffect`, `useRef`, `useState` (drop any import only used for click-popup if unused after edit).

2. Add module-level constant next to `MERGE_TICKET_TOOLTIP_LIMIT`:

   ```typescript
   const MERGE_TICKET_HOVER_DELAY_MS = 500
   ```

   Keep `mergeTicketDisplayLines` exactly as today (array of `{ticket_id} {fmtTime(recorded_at)}` strings, slice 0–20).

3. **Remove** all AST-690 click-popup state and logic:
   - Delete `ticketsOpen` state and `setTicketsOpen`.
   - Delete the `useEffect` that listens for `mousedown` outside `envWrapRef` to close the popup.
   - Remove `<button>`, `aria-expanded`, `aria-haspopup`, `onClick`, and `<ul role="listbox">` popup markup.

4. Add hover tooltip state and timer ref inside `AdminDeployFooter`:

   ```typescript
   const [tooltipVisible, setTooltipVisible] = useState(false)
   const hoverTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
   const envWrapRef = useRef<HTMLSpanElement>(null)
   ```

5. Add cleanup on unmount (single `useEffect` with empty deps):

   ```typescript
   useEffect(() => {
     return () => {
       if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current)
     }
   }, [])
   ```

6. Add hover handlers on the **wrapper** `span.nav-deploy-env-wrap` (not only the inner env span) so moving the pointer from the label into the tooltip does not dismiss it:

   ```typescript
   function handleEnvWrapMouseEnter() {
     if (!envInteractive) return
     if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current)
     hoverTimerRef.current = setTimeout(() => setTooltipVisible(true), MERGE_TICKET_HOVER_DELAY_MS)
   }

   function handleEnvWrapMouseLeave() {
     if (hoverTimerRef.current) {
       clearTimeout(hoverTimerRef.current)
       hoverTimerRef.current = null
     }
     setTooltipVisible(false)
   }
   ```

   ⚠️ **Decision:** 500ms delay is explicit in ticket — native `title` cannot meet this and failed UAT in AST-682; custom delayed panel is required.

   ⚠️ **Decision:** Hover on wrapper includes tooltip panel — standard tooltip hover target pattern; avoids flicker when crossing the gap between label and panel.

7. Replace the environment block in the success render branch. Compute per render (as today):

   ```typescript
   const ticketLines = mergeTicketDisplayLines(status!.merge_tickets)
   const envInteractive = ticketLines.length > 0
   ```

   Replace `{status!.environment != null && ( ... )}` with:

   ```tsx
   {status!.environment != null && (
     <>
       <span
         className="nav-deploy-env-wrap"
         ref={envWrapRef}
         onMouseEnter={handleEnvWrapMouseEnter}
         onMouseLeave={handleEnvWrapMouseLeave}
       >
         <span
           className={
             envInteractive
               ? "nav-deploy-env nav-deploy-env-interactive"
               : "nav-deploy-env"
           }
         >
           {status!.environment}
         </span>
         {tooltipVisible && envInteractive && (
           <div
             className="nav-deploy-tickets-tooltip"
             role="tooltip"
             aria-label="Recent merge tickets"
           >
             {ticketLines.map(line => (
               <div key={line} className="nav-deploy-tickets-tooltip-line">
                 {line}
               </div>
             ))}
           </div>
         )}
       </span>
       <span className="nav-deploy-sep">·</span>
     </>
   )}
   ```

   ⚠️ **Decision:** `<span>` only — no `<button>` — so the label never inherits text-selection I-beam from button/font reset quirks; `cursor: pointer` comes from CSS on `.nav-deploy-env-interactive`.

   ⚠️ **Decision:** Plain `<div>` lines per ticket (no `<ul>/<li>`, no bullets) — matches ticket “no prefix bullets” and exact line format.

   Remove any `title` attribute on the environment control.

8. In `src/ui/frontend/src/App.css`, update deploy footer styles:

   a. **Remove** rules that only served the click popup: `.nav-deploy-env-btn`, `.nav-deploy-tickets-popup`, `.nav-deploy-tickets-popup li`.

   b. **Keep** `.nav-deploy-env-wrap { position: relative; display: inline-block; }`.

   c. **Add** after `.nav-deploy-env`:

   ```css
   .nav-deploy-env-interactive {
     cursor: pointer;
   }
   .nav-deploy-tickets-tooltip {
     position: absolute;
     left: 0;
     bottom: calc(100% + 6px);
     z-index: 20;
     min-width: 200px;
     max-width: 280px;
     padding: 6px 8px;
     background: var(--bg-elevated, var(--bg-deep));
     border: 1px solid var(--border);
     border-radius: 4px;
     box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
     font-size: 11px;
     line-height: 1.45;
     color: var(--text-secondary);
   }
   .nav-deploy-tickets-tooltip-line {
     white-space: nowrap;
   }
   ```

   ⚠️ **Decision:** Reuse AST-690 popup positioning (above label, left-aligned) for visual continuity; interaction model changes from click to hover only.

9. Do **not** change:
   - The 30_000 ms poll interval or deploy_status fetch `useEffect`.
   - Error branch (`Deploy status unavailable`).
   - Early return when `authLoading` or loading state.
   - Uptime span markup or classes.
   - Any file under `src/utils/`, `src/ui/api/`, `scripts/`, or `tests/`.

10. Run compile check:

    ```bash
    cd src/ui/frontend && npx tsc -b --noEmit
    ```

**Ritual:** `code(AST-691): env label hover tooltip 0.5s delay`

---

## QA expectations (Betty manifest — test-child gate)

Betty should **replace** AST-690 click-popup tests with hover-tooltip behavior (engineer runs manifest in **test-child**):

| Behavior | Suggested test updates |
| --- | --- |
| After 500ms hover on env wrap, tooltip shows ticket lines | `test_AdminDeployFooter.test.tsx` (use `vi.useFakeTimers()` or `waitFor` with ≥500ms) |
| Tooltip hidden before 500ms hover; hidden on mouse leave | same |
| Interactive env span has pointer cursor (class `nav-deploy-env-interactive`) | same |
| At most 20 tooltip lines when API returns >20 entries | same |
| Empty / missing `merge_tickets` → plain span, no interactive class, no tooltip | same |
| No `title` on env label | same |
| Env absent → no env UI; uptime still shown | existing test — unchanged |
| Non-admin → footer not mounted | `test_NavigationShell.test.tsx` (unchanged) |

Suggested manifest pytest gate after Betty lands tests:

```bash
cd src/ui/frontend && npm run test -- --run \
  tests/component/frontend/components/test_AdminDeployFooter.test.tsx \
  tests/component/frontend/components/test_NavigationShell.test.tsx
```

---

## Execution contract (for the developer agent)

The plan is binding. Execute **Stage 1** only. Do not add files beyond the two listed above. Do not modify backend or tests. When `merge_tickets` shape differs from `{ ticket_id, recorded_at }`, stop and comment on AST-675.

Blocking comment format (parent issue):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `Single-Component` — `AdminDeployFooter.tsx` plus CSS in `App.css`; reverts AST-690 click UX to hover-delay tooltip; consumes existing `merge_tickets` from deploy status.

**Conf:** `high` — Straightforward React hover timer pattern; reuses `mergeTicketDisplayLines` and `fmtTime`; CSS positioning mirrors AST-690 popup panel.

**Risk:** `low` — Admin-only deploy footer; wrong tooltip text does not affect dispatch or auth; worst case is misleading deploy history display or annoying hover timing.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `fmtTime` and `mergeTicketDisplayLines`; no duplicate API calls |
| §2.1 Config | No new config keys; 20-line cap remains UI concern per parent AC |
| §3.3 Imports | Frontend-only; no layer violations |
| §3.5 Naming | `merge_tickets` matches API; `nav-deploy-*` class prefix consistent with footer |
| §1.5 Logging | N/A — no backend changes |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `sub/AST-675/ast-691-uat-env-label-hover-tooltip-pointer-cursor-05s-delay` @ `3ae44a1364b3c2d19d9325e4c4679ed5659d38ad`

**Stage 1:** Hover-delay tooltip replaces AST-690 click popup; pointer cursor on interactive env label; 500ms delay; plain div lines, no bullets.
