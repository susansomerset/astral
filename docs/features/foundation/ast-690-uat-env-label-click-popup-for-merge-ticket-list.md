<!-- linear-archive: AST-690 archived 2026-06-23 -->

## Linear archive (AST-690)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-690/uat-env-label-click-popup-for-merge-ticket-list  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-675 — Create a ticket log in utils  
**Blocked by / blocks / related:** parent: AST-675

### Description

## What failed

With `ASTRAL_DEPLOY_ENV` set and an admin session on staging, the deploy footer environment label shows a text (I-beam) cursor on hover and **no** merge-ticket list appears — the native `title` tooltip does not surface ticket history.

## Expected

Admin can see up to **20** most recent logged parent tickets (id + timestamp), most recent first, with line breaks between entries — via an obvious click interaction on the environment label (popup/list), per Susan UAT feedback.

## Repro

1. Log in as admin on staging with `ASTRAL_DEPLOY_ENV` set (e.g. `dev`).
2. Open left nav; locate the deploy footer environment label.
3. Hover the environment string — I-beam cursor; no ticket list appears.
4. Susan expects click on the environment label to open a small popup/list of logged tickets.

## Parent AC (quoted inline)

> 4. With `ASTRAL_DEPLOY_ENV` set and admin session, hovering the environment label shows up to **20** ticket lines (id + timestamp), most recent first, separated by line breaks.

*(Implementation may use click + popup instead of hover* `title` *if that satisfies the display requirement and fixes the UAT failure.)*

## Boundaries

* This bug does **not** change: merge ticket log storage, append tool, finish-up wiring, deploy-status API shape, or non-admin nav.
* Does not add SHA to entries; does not call Linear API for ticket titles.

### Comments

#### radia — 2026-06-15T20:29:18.617Z
**Diff:** `origin/dev...origin/sub/AST-675/ast-690-uat-env-label-click-popup-for-merge-ticket-list` (`fd9e663b`)

### Plan fidelity (Stage 1)

Implementation matches the approved plan: `mergeTicketDisplayLines`, click-toggle `button` with `aria-expanded` / `aria-haspopup`, outside `mousedown` dismiss on `envWrapRef`, static `span` when `merge_tickets` empty/missing, `title` removed, 20-line cap preserved, poll/error/uptime branches untouched. No backend, API, utils, or sibling-scope drift (AST-681/683).

Ordering assumption holds: `deploy_status.py` already returns `merge_tickets` most-recent-first (`list(reversed(entries))`); UI `slice(0, 20)` is correct.

### ASTRAL_CODE_RULES

| Check | Result |
|-------|--------|
| §1.3 DRY | Reuses `fmtTime`; outside-click pattern consistent with admin UI conventions |
| §3.3 layer | Frontend-only; no `data` / `external` imports |
| §3.2 UI config | No hardcoded state lists; consumes API payload |
| §1.5 / §5f–g | N/A — no backend or LLM paths touched |

**fix-now:** none

### Tests / manifest

Betty manifest and `test_AdminDeployFooter.test.tsx` updates align with plan QA table: popup open/close, 20-item cap, static span when empty, no `title`. `docs/test-bible/frontend/components.md` AST-690 row matches pytest names. Tests Passed gate is credible for this scope.

### Advisory (non-blocking)

- **`key={line}`** on popup `<li>` — duplicate `ticket_id` + identical formatted timestamp would collide; consider `key={\`${ticket_id}-${recorded_at}\`}` or index if log ever duplicates (unlikely).
- **ARIA:** `role="listbox"` with plain `<li>` children is loose vs strict combobox/listbox pattern (`role="option"`); fine for admin footer, optional polish later.
- **Poll while open:** if `merge_tickets` empties on refresh, `ticketsOpen` can stay `true` with no visible popup until next interactive session — harmless edge case.

#### betty — 2026-06-15T20:27:28.514Z
## QA test manifest (AST-690)

**Publish ref:** `origin/sub/AST-675/ast-690-uat-env-label-click-popup-for-merge-ticket-list` @ `fd9e663b` (`merge-tests(AST-690): origin/tests 557cc266`)

**Bible shasum:** `docs/test-bible/frontend/components.md` → `d462a3e8d88014a9ee3c37b72f2d6b19f7174cf3`

### 1. Existing coverage (unchanged — no rerun required)

| Area | Bible | Notes |
| --- | --- | --- |
| Deploy status API / `merge_tickets` payload | `docs/test-bible/utils/deploy_status.md` | AST-681 — no API shape change this ticket |
| Non-admin footer gate | `docs/test-bible/frontend/components.md` AST-646 | `test_NavigationShell.test.tsx` unchanged |

### 2. Broken / obsolete tests (revised this pass)

| Old (AST-682) | Replacement (AST-690) |
| --- | --- |
| `test_sets_merge_ticket_tooltip_on_environment_label_when_merge_tickets_present` | `test_opens_merge_ticket_popup_on_environment_button_click_when_merge_tickets_present` |
| `test_omits_title_on_environment_label_when_merge_tickets_empty_or_missing` | `test_renders_static_environment_span_when_merge_tickets_empty_or_missing` |
| `test_caps_merge_ticket_tooltip_at_20_lines` | `test_caps_merge_ticket_popup_at_20_list_items` |

### 3. Manifest (test-child — run all)

**Compile:**

```bash
cd src/ui/frontend && npx tsc -b --noEmit
```

**Vitest (required):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

**Cases covered:**

1. Click env **button** opens `listbox` popup with ticket lines (`ticket_id` + `fmtTime`), API order, no `title` on control
2. Second click toggles closed; **outside `mousedown`** dismisses popup
3. Empty / missing `merge_tickets` → static **span**, no button, no popup
4. At most **20** `<li>` rows when API returns >20 entries
5. Existing: env+uptime success, env absent, deploy_status error — unchanged

**Pass criterion:** all manifest lines green; no backend pytest required (UI-only bug).

— Betty

#### katherine — 2026-06-15T20:11:28.466Z
Plan: `docs/features/foundation/ast-690-uat-env-label-click-popup-for-merge-ticket-list.md`

https://github.com/susansomerset/astral/blob/sub/AST-675/ast-690-uat-env-label-click-popup-for-merge-ticket-list/docs/features/foundation/ast-690-uat-env-label-click-popup-for-merge-ticket-list.md

**Scope:** `Single-Component` — `AdminDeployFooter.tsx` + popup CSS in `App.css`; replaces broken native `title` with click-to-toggle list; no backend/API changes.

**Conf:** `high` — Reuses `fmtTime`, 20-line cap, and existing outside-click pattern from admin UI.

**Risk:** `low` — Admin-only footer display; does not touch dispatch, auth, or non-admin nav.

---

# UAT: env label click popup for merge ticket list

**Linear:** [AST-690 — UAT: env label click popup for merge ticket list](https://linear.app/astralcareermatch/issue/AST-690/uat-env-label-click-popup-for-merge-ticket-list)

**Parent:** [AST-675 — Create a ticket log in utils](https://linear.app/astralcareermatch/issue/AST-675/create-a-ticket-log-in-utils) (AC reference only — do not implement sibling scope)

**Publish ref:** `origin/sub/AST-675/ast-690-uat-env-label-click-popup-for-merge-ticket-list` (origin only)

## Summary

UAT on staging showed the AST-682 native `title` tooltip on the admin deploy **environment label** does not surface merge-ticket history (I-beam cursor on hover, no ticket list). This bug replaces hover/`title` with a **click-to-toggle popup** listing up to **20** most recent parent ticket ids and formatted timestamps (one line each, most recent first). No backend, API, log storage, or finish-up changes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/AdminDeployFooter.tsx` | Click popup for merge tickets; remove `title`; outside-click close | ui |
| `src/ui/frontend/src/App.css` | Popup positioning, pointer cursor, button reset for env control | ui |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/ui/frontend/src/components/NavigationShell.tsx` | Admin-only footer gating unchanged (AC 6) |
| `src/utils/deploy_status.py` | `merge_tickets` payload unchanged |
| `src/ui/api/api_system.py` | `GET /api/deploy_status` unchanged |

**QA manifest (Betty — not engineer commits):** Betty updates `tests/component/frontend/components/test_AdminDeployFooter.test.tsx` at **Code Complete** (`qa-child`). Engineer does not commit under `tests/` or `docs/test-bible/**` (pre-commit hook).

**Out of scope:** merge ticket log / append tool (AST-681), finish-up wiring (AST-683), deploy-status API shape, non-admin nav, SHA in entries, Linear API for titles.

---

## Stage 1: Click popup on environment label

**Done when:** With `environment` set and non-empty `merge_tickets`, clicking the environment control toggles a visible popup with up to 20 lines (`AST-NNN <fmtTime>`), most recent first; clicking outside or pressing the control again closes it; env control shows pointer cursor (not I-beam); no `title` attribute on env control; when `merge_tickets` is empty or missing the env label is static text (no popup, no pointer); uptime, error branch, poll interval, and absent-environment layout unchanged; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/AdminDeployFooter.tsx`, add React imports:

   ```typescript
   import { useEffect, useRef, useState } from "react"
   ```

   (Replace the existing `useEffect, useState` import line.)

2. Rename and reshape the display helper (replace `formatMergeTicketTooltip`):

   ```typescript
   function mergeTicketDisplayLines(mergeTickets: MergeTicket[] | undefined): string[] {
     if (!mergeTickets?.length) return []
     return mergeTickets
       .slice(0, MERGE_TICKET_TOOLTIP_LIMIT)
       .map(({ ticket_id, recorded_at }) => `${ticket_id} ${fmtTime(recorded_at)}`)
   }
   ```

   ⚠️ **Decision:** Return an array of lines for popup `<li>` rendering instead of a `\n`-joined `title` string — native `title` failed UAT and does not support reliable multiline display.

3. Inside `AdminDeployFooter`, add state and ref:

   ```typescript
   const [ticketsOpen, setTicketsOpen] = useState(false)
   const envWrapRef = useRef<HTMLSpanElement>(null)
   ```

4. Add outside-click dismiss (same pattern as `AdminAnthropicAdHoc.tsx` save-as dropdown):

   ```typescript
   useEffect(() => {
     if (!ticketsOpen) return
     function handler(e: MouseEvent) {
       if (envWrapRef.current && !envWrapRef.current.contains(e.target as Node)) {
         setTicketsOpen(false)
       }
     }
     document.addEventListener("mousedown", handler)
     return () => document.removeEventListener("mousedown", handler)
   }, [ticketsOpen])
   ```

5. In the success render branch, replace the environment block. Compute once per render:

   ```typescript
   const ticketLines = mergeTicketDisplayLines(status!.merge_tickets)
   const envInteractive = ticketLines.length > 0
   ```

   Replace the existing `{status!.environment != null && ( ... )}` fragment with:

   ```tsx
   {status!.environment != null && (
     <>
       <span className="nav-deploy-env-wrap" ref={envWrapRef}>
         {envInteractive ? (
           <button
             type="button"
             className="nav-deploy-env nav-deploy-env-btn"
             aria-expanded={ticketsOpen}
             aria-haspopup="listbox"
             onClick={() => setTicketsOpen(open => !open)}
           >
             {status!.environment}
           </button>
         ) : (
           <span className="nav-deploy-env">{status!.environment}</span>
         )}
         {ticketsOpen && envInteractive && (
           <ul className="nav-deploy-tickets-popup" role="listbox" aria-label="Recent merge tickets">
             {ticketLines.map(line => (
               <li key={line}>{line}</li>
             ))}
           </ul>
         )}
       </span>
       <span className="nav-deploy-sep">·</span>
     </>
   )}
   ```

   ⚠️ **Decision:** Use `<button type="button">` only when tickets exist — keyboard-accessible toggle without `title`; static `<span>` when no history (not clickable).

   ⚠️ **Decision:** `mousedown` outside-click on `envWrapRef` wrapper so clicks inside the popup do not dismiss before toggle completes.

   Remove any `title={...}` on the environment control.

6. In `src/ui/frontend/src/App.css`, after `.nav-deploy-env { ... }`, add:

   ```css
   .nav-deploy-env-wrap {
     position: relative;
     display: inline-block;
   }
   .nav-deploy-env-btn {
     background: none;
     border: none;
     padding: 0;
     margin: 0;
     font: inherit;
     font-family: inherit;
     color: inherit;
     text-transform: inherit;
     cursor: pointer;
   }
   .nav-deploy-tickets-popup {
     position: absolute;
     left: 0;
     bottom: calc(100% + 6px);
     z-index: 20;
     min-width: 200px;
     max-width: 280px;
     margin: 0;
     padding: 6px 8px;
     list-style: none;
     background: var(--bg-elevated, var(--bg-deep));
     border: 1px solid var(--border);
     border-radius: 4px;
     box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
     font-size: 11px;
     line-height: 1.45;
     color: var(--text-secondary);
   }
   .nav-deploy-tickets-popup li {
     white-space: nowrap;
   }
   ```

   ⚠️ **Decision:** Popup anchors above the env label within the left nav footer (absolute positioning on wrap) — avoids clipping inside narrow nav without portaling.

7. Do **not** change:
   - The 30_000 ms poll interval or `useEffect` fetch logic.
   - Error branch (`Deploy status unavailable`).
   - Early return when `authLoading` or loading state.
   - Uptime span markup or classes.
   - Any file under `src/utils/`, `src/ui/api/`, `scripts/`, or `tests/`.

8. Run compile check:

   ```bash
   cd src/ui/frontend && npx tsc -b --noEmit
   ```

**Ritual:** `code(AST-690): env label click popup for merge tickets`

---

## QA expectations (Betty manifest — test-child gate)

Betty should **replace** AST-682 `title`-based tests with popup behavior (engineer runs manifest in **test-child**):

| Behavior | Suggested test updates |
| --- | --- |
| Click env button opens popup with ticket lines | `test_AdminDeployFooter.test.tsx` |
| Second click or outside mousedown closes popup | same |
| At most 20 `<li>` rows when API returns >20 entries | same |
| Empty / missing `merge_tickets` → plain span, no button, no popup | same |
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

**Scope:** `Single-Component` — `AdminDeployFooter.tsx` plus minimal CSS in `App.css`; consumes existing `merge_tickets` from deploy status; no utils/API changes.

**Conf:** `high` — Follows established outside-click pattern (`AdminAnthropicAdHoc`); reuses `fmtTime` and 20-line cap from AST-682; straightforward UI swap from broken `title` to click popup.

**Risk:** `low` — Admin-only deploy footer; wrong popup text does not affect dispatch or auth; worst case is misleading deploy history display or popup UX annoyance.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `fmtTime`; single helper; outside-click pattern matches existing admin UI |
| §2.1 Config | No new config keys; 20-line cap remains UI concern per parent AC |
| §3.3 Imports | Frontend-only; no layer violations |
| §3.5 Naming | `merge_tickets` matches API; `nav-deploy-*` class prefix consistent with footer |
| §1.5 Logging | N/A — no backend changes |

No conflicts requiring `conf-!!-NONE`.

---

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-675/ast-690-uat-env-label-click-popup-for-merge-ticket-list`  
**Product commit:** `4a17067c` (Stage 1 — click popup on env label; `AdminDeployFooter.tsx` + `App.css`)

---

## Resolution (2026-06-15)

**Publish ref:** `origin/sub/AST-675/ast-690-uat-env-label-click-popup-for-merge-ticket-list` @ `fd9e663b` (Radia review — fix-now: none)

Radia review clean — no fix-now, discuss, or product changes. Merged `origin/dev`, `origin/ftr/ast-675-create-a-ticket-log-in-utils`, and publish ref on epic worktree `work690`; §9a dry-run clean against `origin/dev` and `origin/ftr/ast-675-create-a-ticket-log-in-utils`.

**Advisory (no action):** `key={line}` collision unlikely; loose `listbox` ARIA acceptable for admin footer; poll-while-open edge case harmless.

**Outcome:** Admin deploy footer environment label opens click-to-toggle popup with up to 20 merge-ticket lines (`ticket_id` + `fmtTime`); static span when no history; native `title` removed.
