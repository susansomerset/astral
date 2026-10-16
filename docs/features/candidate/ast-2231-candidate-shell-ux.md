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

**Done when:** Non-admin never sees the candidate `<select>` or mobile candidate menu; admin still does. First visit (`NAV_STORAGE_KEY` absent) expands only groups with `recent === true`; persisted `[]` stays collapsed. Profile shows a yellow attention mark iff the Profile item has `attention === true`. Disabled items remain visible as non-links. Empty nav (stage 0) is not a usable candidate-facing menu.

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

   - **Seed gate (null key only):** After a successful `nav_config` fetch that yields `data: NavGroup[]`, seed expand **only when** `localStorage.getItem(NAV_STORAGE_KEY) === null` (key never written — true first visit / cleared storage). Then:

     ```ts
     setExpanded(new Set(data.filter(g => g.recent === true).map(g => g.label)))
     ```

     Do **not** call `saveExpanded` for this seed — user toggle remains the only writer to localStorage.
   - **Persisted empty is intentional:** If the key exists and parses to `[]` (user collapsed every group), `loadExpanded()` returns an empty `Set` — **do not** re-seed from `recent`. Treat that as all-collapsed.
   - If the key exists with any labels, keep that Set; never overwrite with API `recent` on later fetches.
   - ⚠️ **Decision:** Distinguish “key absent” from “key present with `[]`”. Empty-Set-from-`loadExpanded()` alone is **not** a seed signal (Joan round=1).

4. **Incomplete Profile alert (AC 10 — UI half).** When rendering Candidate group items, if `item.path === "/candidate/profile"` and `item.attention === true`, append a yellow attention affordance next to the label (both enabled `NavLink` and disabled `span` paths). Use a dedicated class (e.g. `nav-link-attention`) — not an emoji sticker. If `attention` is absent/false, render nothing extra.

5. **Disabled-but-visible.** Keep the existing branch: `enabled` → `NavLink`; else `<span className="nav-link disabled">`. Do not hide disabled items. Do not navigate on disabled click (`pointer-events: none` already in CSS).

6. **Stage 0 (AC 8).** Do not special-case state names in the shell. When the API returns no Candidate/Criteria/Company/Job Opportunities groups (stage 0 omit from #3), the sidebar simply has no those groups — already non-interactive. Do not invent client-side stage math. Admin-only groups may still appear for admins when the API includes them.

7. Keep auth gate (`authLoading`), `selectedId` refetch, silent 30s poll, hamburger/drawer, search, logo theme, and `AdminDeployFooter` behavior unchanged aside from the picker visibility rule. The silent poll / refetch path updates `navGroups` (and loading/error) only — it must **not** call `setExpanded` except when the step-3 null-key seed rule fires (once per browser until the user toggles and writes storage).

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

## Revisions

### Revision 1 — 2026-10-16
Driven by: Joan `[plan-discuss] round=1 concern` / fix-now — recent-expand seed cannot tell fresh session from persisted `[]`.
Changes: Stage 1 step 3 seeds only when `localStorage.getItem(NAV_STORAGE_KEY) === null`; persisted `[]` stays all-collapsed; step 7 states silent poll must not reset `expanded` except that one-shot seed.

## Execution contract

- Stages in order; one `code(AST-2231):` commit per stage on the epic worktree; push each to `origin/sub/AST-2225/AST-2231-candidate-shell-ux`.
- Before Stage 1 coding: verify tip has #3 `recent` / `attention` / stage-0 omit — else stop and comment (Prerequisite).
- Do not add files outside **Files Changed**.
- On ambiguity → stop and comment on parent AST-2225 with the Stage N blocked template.

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Ticket:** AST-2231
**Overall:** REVISE
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref tip:** `69badaef9f4727cd823d49c8fbd84df53b30a6a2` (`origin/sub/AST-2225/AST-2231-candidate-shell-ux`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | X | | Frontend-only; no `src/ui/api/**` changes |

## Traceability

AC8 → Stage 1 step 6 (rely on #3 omitting stage-0 groups; no client stage math). AC9 → Stage 1 step 2 (picker/menu only when `isAdmin`). AC10 → Stage 1 step 4 + Stage 2 (Profile `attention` affordance). Parent AC 10 (recent expand) → Stage 1 step 3 (seed expand from group `recent`; API/config from #3). Parent AC 1–7, 11–13 → N/A (vocabulary, advancement, nav map owned elsewhere). Child does not own API `incomplete_profile` (#2/#3).

## Findings

### fix-now
- **Location:** Stage 1 step 3 — default-collapse + recent expand
- **Finding:** Seeding expanded groups when `loadExpanded()` is **empty** cannot distinguish (a) fresh session / never written `nav:expanded` from (b) user toggled and saved an empty expanded set (`[]` in localStorage). Today `loadExpanded()` returns `new Set()` for both; re-seeding from API `recent` on every nav fetch (including 30s poll) would re-expand “recent” groups after the user deliberately collapsed everything.
- **Recommendation:** Seed only when `localStorage.getItem(NAV_STORAGE_KEY) === null` (first visit), or use a one-shot ref on the first successful fetch; treat persisted `[]` as intentional “all collapsed.” Spell that in the plan before build.

### discuss
- **Location:** Stage 1 step 3 vs Stage 1 step 7 (30s poll)
- **Finding:** Even with a null-key-only seed, the plan should state explicitly that silent poll updates `navGroups` only and must **not** reset `expanded` unless the seed rule above fires once.
- **Recommendation:** One sentence in step 3 or 7 so implementer does not call `setExpanded` inside the poll path.

### acceptable
- **Location:** Linear assignee
- **Finding:** Assignee Ada Lovelace (Joan expected during validate pass).
- **Recommendation:** Chuckles handoff only.

### acceptable
- **Location:** Prerequisite AST-2230
- **Finding:** Hard stop if `recent` / `attention` / stage-0 omit missing — correct; no client-side heuristics or `api_system.py` edits.
- **Recommendation:** None.

**R6 (summary):** Scope gate matches ticket (NavigationShell + App.css only). Picker hide, disabled-but-visible, Profile attention, stage-0 via empty API groups, and prerequisite on #3 are otherwise faithful to parent shell slice. Estimate 2 — agree once expand-seed rule is tightened.

context_tokens≈95000

## Joan validate (round 2 — APPROVED)

[plan-rubric]
**Ticket:** AST-2231
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref tip:** `f3a0f1dd3d80573cf4e0b44416695a9e27b0d73d` (`origin/sub/AST-2225/AST-2231-candidate-shell-ux`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | X | | Frontend-only; no `src/ui/api/**` changes |

## Traceability

AC8 → Stage 1 step 6 (stage-0 groups omitted by #3; no client stage math). AC9 → Stage 1 step 2 (`isAdmin`-only picker/menu). AC10 → Stage 1 step 4 + Stage 2 (`attention` affordance). Parent recent-expand → Stage 1 step 3 (null-key seed from group `recent`; #3 API). Parent AC 1–7, 11–13 → N/A.

## Findings

### discuss
- **Location:** Stage 1 step 3 vs step 7 — null-key seed
- **Finding:** Step 7 requires `setExpanded` at most once per browser until the user writes storage, but step 3 only gates on `getItem === null`, which stays true on every poll until the first toggle — implementer should use a one-shot ref (or equivalent) so the 30s poll does not keep re-applying `recent`.
- **Recommendation:** Optional one-line in step 3 naming `useRef` / `expandedSeededFromApi`; step 7 already states the intent — build can proceed.

### acceptable
- **Location:** Revision 1 / Plan Discuss round 1
- **Finding:** Prior fix-now (empty `loadExpanded()` vs persisted `[]`) is addressed: null-key-only seed, persisted `[]` stays collapsed, poll must not reset `expanded` except that seed.
- **Recommendation:** None.

### acceptable
- **Location:** Prerequisite AST-2230
- **Finding:** Stop gate if `recent` / `attention` / stage-0 omit missing; no client heuristics or API edits.
- **Recommendation:** None.

**R6 (summary):** Scope gate holds (NavigationShell + App.css). Picker hide, disabled-but-visible, Profile attention, stage-0 via empty candidate-facing groups, and #3 prerequisite remain faithful. Estimate 2 — agree.

context_tokens≈102000

## Review (build stub)

**Publish ref:** `origin/sub/AST-2225/AST-2231-candidate-shell-ux`
**Plan path:** `docs/features/candidate/ast-2231-candidate-shell-ux.md`

**Built tip:** `cc79c2c6b33e6a5aea9243fd0156e9c55688dcab` (`cc79c2c6b`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `87122ae4b` | Non-admin hide picker; null-key recent seed; Profile attention |
| 2 | `cc79c2c6b` | `.nav-link-attention` yellow via `--warning` |

**Betty note:** Frontend shell only. Consumes AST-2230 `recent` / `attention` / stage-0 omit. No test-tree edits.
