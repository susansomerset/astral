# AST-2231 — Candidate shell UX

- **Linear:** [AST-2231](https://linear.app/astralcareermatch/issue/AST-2231)
- **Parent:** [AST-2225](https://linear.app/astralcareermatch/issue/AST-2225) — Revise candidate ui and candidate states
- **Publish ref:** `origin/sub/AST-2225/AST-2231-candidate-shell-ux`

After AST-2230’s stage-gated `/api/nav_config`, render the progressive shell: hide the candidate picker for non-admins, default-collapse nav groups and expand only API-`recent` ones on a fresh session, show a yellow Profile attention affordance when the API marks it, keep disabled items visible, and treat an empty/stage-0 candidate-facing menu as non-interactive.

## Explicit scope gate

Ticket **## Scope** names only:

- `src/ui/frontend/src/components/NavigationShell.tsx`
- `src/ui/frontend/src/App.css`

No `config.py`, `api_system.py`, `routes.tsx`, readiness helpers, or vocabulary edits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/NavigationShell.tsx` | Non-admin hide picker; seed expand from group `recent`; Profile `attention` affordance; keep disabled-but-visible; stage-0 empty menu stays non-interactive | ui |
| `src/ui/frontend/src/App.css` | Yellow Profile attention styles; tighten disabled nav look if needed | ui |

## Canon (this ticket)

Read in full (named on the ticket):

- `stat.logging.info.api` → `canon/directives/active/stat.logging.info.api.md` — this ticket does **not** add/modify API routes; no progress `logger.info` to emit. Id stays in scope for score alignment only (shell consumes GET state; GET remains non-progress).

All other ids: id-only.

## Prerequisite (build, not this ticket’s Scope)

- **AST-2230 on tip** (User Testing sibling): `/api/nav_config` returns a **JSON array of groups** with:
  - item `"enabled": boolean` (disabled items still present)
  - group `"recent": boolean` on candidate-facing groups
  - Profile item (`path == "/candidate/profile"`) optional `"attention": boolean`
  - stage 0 → Candidate / Criteria / Company / Job Opportunities **omitted** (empty candidate-facing list for that user)
- **If tip lacks those keys** (2230 not merged into this sub yet): **stop** — comment on AST-2231 that build needs `origin/sub/AST-2225/AST-2230-stage-gated-nav` (or parent `ftr`) attached; **do not** invent `recent` / `attention` client-side heuristics or edit `api_system.py`.

## Stage 1: Picker hide + expand-from-recent + Profile attention (`NavigationShell.tsx`)

**Done when:** Non-admin never sees the candidate `<select>` or mobile candidate menu; admin still does. Fresh session (empty `nav:expanded` storage) expands only groups with `recent === true`. Profile shows a yellow attention mark iff the Profile item has `attention === true`. Disabled items remain visible as non-links. Empty nav (stage 0) is not a usable candidate-facing menu.

1. Extend local TS types to match #3’s additive payload (keep array root):

   ```ts
   interface NavItem {
     label: string
     path: string
     enabled: boolean
     count?: number
     attention?: boolean
   }
   interface NavGroup {
     label: string
     items: NavItem[]
     recent?: boolean
   }
   ```

2. **Picker contract (AC 9).** Today both wide `<select>` and narrow menu render whenever `candidates.length > 0`, with `disabled={!isAdmin}`. Change to:
   - Render the entire `sidebar-candidate-select` / `sidebar-candidate-menu` block **only when `isAdmin`** (and `candidates.length > 0` as today).
   - Non-admin: no select, no menu toggle, no candidate menu list. Bound candidate continues via `CandidateContext` without a visible picker.
   - ⚠️ **Decision:** Also omit the read-only state line for non-admins (it lived under the picker chrome). Admins keep select/menu + state line unchanged in behavior.

3. **Default-collapse + recent expand (parent recent chrome; API half is #3).** Keep `NAV_STORAGE_KEY = "nav:expanded"` and `toggleGroup` / `saveExpanded` as today.

   - After a successful `nav_config` fetch that yields `data: NavGroup[]`, if `loadExpanded()` is **empty** (fresh session / never toggled), set expanded to:

     ```ts
     new Set(data.filter(g => g.recent === true).map(g => g.label))
     ```

     Do **not** call `saveExpanded` for this seed — user toggle remains the only writer to localStorage.
   - If `loadExpanded()` is **non-empty**, keep that Set; do not overwrite with API `recent` on poll/refresh.
   - ⚠️ **Decision:** Seed only when storage is empty so a user’s collapses/expands survive the 30s silent poll. Fresh browser / cleared storage → API `recent` drives the first paint.

4. **Incomplete Profile alert (AC 10 — UI half).** When rendering Candidate group items, if `item.path === "/candidate/profile"` and `item.attention === true`, append a yellow attention affordance next to the label (both enabled `NavLink` and disabled `span` paths). Use a dedicated class (e.g. `nav-link-attention`) — not an emoji sticker. If `attention` is absent/false, render nothing extra.

5. **Disabled-but-visible.** Keep the existing branch: `enabled` → `NavLink`; else `<span className="nav-link disabled">`. Do not hide disabled items. Do not navigate on disabled click (`pointer-events: none` already in CSS).

6. **Stage 0 (AC 8).** Do not special-case state names in the shell. When the API returns no Candidate/Criteria/Company/Job Opportunities groups (stage 0 omit from #3), the sidebar simply has no those groups — already non-interactive. Do not invent client-side stage math. Admin-only groups may still appear for admins when the API includes them.

7. Keep auth gate (`authLoading`), `selectedId` refetch, silent 30s poll, hamburger/drawer, search, logo theme, and `AdminDeployFooter` behavior unchanged aside from the picker visibility rule.

8. Do **not** add API routes, config maps, or progress logging.

## Stage 2: Attention + disabled styles (`App.css`)

**Done when:** Profile attention is visibly yellow; disabled nav remains muted/non-clickable; no unrelated chrome restyle.

1. In `src/ui/frontend/src/App.css`, near `.nav-link.disabled`, add styles for the attention affordance, e.g.:

   ```css
   .nav-link-attention {
     /* yellow attention mark — uses theme tokens where possible; avoid purple glow / pill clusters */
     color: /* yellow/amber token or literal */;
     margin-left: 6px;
     font-size: 12px;
     /* decorative; not a second click target */
   }
   ```

   ⚠️ **Decision:** Prefer an existing CSS variable if the theme already has a warning/attention color; otherwise a single literal amber (`#c9a227` or similar) is fine. Do not introduce a new card/badge layout.

2. Leave `.nav-link.disabled` intact unless a one-line contrast tweak is needed for visibility of disabled-but-present labels. Do not restyle the whole sidebar.

3. Do not touch unrelated App.css sections (modals, buttons, resume editors, etc.).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Execution contract

- Stages in order; one `code(AST-2231):` commit per stage on the epic worktree; push each to `origin/sub/AST-2225/AST-2231-candidate-shell-ux`.
- Before Stage 1 coding: verify tip has #3 `recent` / `attention` / stage-0 omit — else stop and comment (Prerequisite).
- Do not add files outside **Files Changed**.
- On ambiguity → stop and comment on parent AST-2225 with the Stage N blocked template.
