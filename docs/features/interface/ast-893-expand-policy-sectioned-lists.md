<!-- linear-archive: AST-893 archived 2026-07-29 -->

## Linear archive (AST-893)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-893/optional-expand-all-policy-and-expand-allcollapse-all-chrome-allow  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-886 — Allow "Expand One/Expand All" for sectioned list components  
**Blocked by / blocks / related:** parent: AST-886

### Description

## What this implements

Shared sectioned-list UI gains an optional page-set expansion policy: **Expand One** by default (current accordion behavior — existing screens stay on this default with no forced refactor) vs **Expand All** when the hosting TypeScript page opts in. When Expand All is on, the user gets visible **Expand all** / **Collapse all** controls and may still expand or collapse individual sections so one or more sections are open without requiring every section to be expanded. Zero expanded remains valid under both policies.

## Acceptance criteria

1. With the default (Expand One / expand-all unset): at most one section is open at a time; expanding a second section closes the first; collapsing the open section leaves zero expanded — matching current accordion behavior on existing screens that are not opted in.
2. With Expand All opted in by the page: two or more sections can be open at the same time; collapsing one does not force-close the others.
3. With Expand All opted in: visible **Expand all** opens every section; visible **Collapse all** closes every section.
4. With Expand All opted in: the user can expand or collapse individual sections so that one or more (but not necessarily all) sections are open, without using Expand all.
5. Under both policies, every section can be collapsed so that zero sections are expanded.
6. Existing sectioned-list screens that do not opt in continue to behave as Expand One with no accidental multi-open and no required refactor of their prior expand logic beyond wiring the shared default.

## Boundaries

* Does **not** force existing screens off Expand One — default stays Expand One unless a page opts in.
* Does **not** invent new list data, filters, sort rules, or API contracts.
* Does **not** redesign section chrome beyond Expand all / Collapse all for Expand All mode, table layout, sticky columns, or admin filter bars.
* Does **not** add a global persisted preference for last-expanded sections.
* Does **not** change Recommended Jobs always-visible sections, AST-858, or AST-885 beyond shared expand primitives reused incidentally.
* Must not change Expand One behavior on Manage Tasks, Scheduled Actions, In Review, Skipped, and other current accordion consumers that remain on the default.
* Frontend-only — no backend debug-logging requirements.

## Notes for planning

* Parent **AST-886** definition is authoritative. React / TypeScript / CollapsiblePanel and sectioned list consumers — Katherine domain.
* Prefer extending shared sectioned-list / CollapsiblePanel coordination over one-off expand state per page. Page opts into Expand All; omission means Expand One.
* Preserve zero-expanded (AST-426 / CollapsiblePanel). Soften Boundaries in ASTRAL_CODE_RULES if needed for UI-only work — no [config.py](<http://config.py>) / API changes expected.
* UAT needs at least one page that opts into Expand All so multi-open and bulk controls are observable; other screens keep Expand One default.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-886-expand-one-expand-all-sectioned-lists`, child `sub/AST-886/<child-id>-expand-policy-sectioned-lists`. Created at **dispatch-parent**. Engineers publish to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-07-13T21:25:56.091Z
[merge-child] blocked: missing resolve(AST-893): on origin/sub/AST-886/AST-893-expand-policy-sectioned-lists

Resolution commit is `docs(AST-893): resolution — …` — validate-sub-log requires `resolve(AST-893):`.

@Katherine Johnson — empty commit `resolve(AST-893): Radia clean sign-off` and push publish tip (no force-push).

— Chuckles

#### chuckles — 2026-07-13T21:25:15.518Z
[merge-child] blocked: missing plan(AST-893): on origin/sub/AST-886/AST-893-expand-policy-sectioned-lists

Plan commit subject is `docs(AST-893): plan — …` — validate-sub-log requires `plan(AST-893):`.

@Katherine Johnson — on publish tip, add empty commit `plan(AST-893): expand policy sectioned lists` (or equivalently fix the plan commit subject without rewriting shared history) and push `origin/sub/AST-886/AST-893-expand-policy-sectioned-lists`. Do not force-push.

— Chuckles

#### radia — 2026-07-13T21:23:41.617Z
### What’s solid
- Stages 1–3 match plan: `useSectionExpandPolicy` Expand One/All Set semantics, `SectionExpandChrome` (**Expand all** / **Collapse all**), App.css `10f`, CollapsiblePanel comment-only.
- Opt-in correct: Scheduled Actions `expandAll: true` + chrome; Manage Tasks list / In Review / Skipped default Expand One, no chrome; edit-modal untouched.
- Auto-open + mount-when-expanded preserved on Scheduled Actions; candidate-change reset on In Review / Skipped.
- Boundaries held (frontend-only). §1.1 / §1.3 / §3.3 / §3.5 OK. Self-Assessment Scope matches. §5f/§5g N/A.
- Betty tests/bible on tip cover AC 1–6.

### Issues
None.

### Recommended actions
| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

Doc: https://github.com/susansomerset/astral/blob/88119b80dd3d7c57cbfd3d182a18a5f7888f4c2a/docs/features/interface/ast-893-expand-policy-sectioned-lists.md
`docs(AST-893): Radia review — clean` @ `88119b8`

#### betty — 2026-07-13T21:19:54.194Z
## QA test manifest

`origin/sub/AST-886/AST-893-expand-policy-sectioned-lists` @ `95f6b6d` (`merge-tests(AST-893): origin/tests cfdf768b31571ec6055cf535a6ee94f3833494ec`)

1. Hook Expand One / Expand All (AC 1–5) — `tests/component/frontend/hooks/test_useSectionExpandPolicy.test.tsx`
2. `SectionExpandChrome` labels + callbacks — `tests/component/frontend/components/test_SectionExpandChrome.test.tsx`
3. Manage Tasks list Expand One — second section closes first; no bulk chrome (§6c) — `test_AdminTaskPrompts.test.tsx` **AST-893 Expand One on Manage Tasks list**
4. In Review Expand One — second section closes first; no bulk chrome (§6c) — `test_JobsInReview.test.tsx` **AST-893 Expand One default**
5. Skipped Expand One — second section closes first; no bulk chrome (§6c) — `test_JobsSkipped.test.tsx` **AST-893 Expand One default**
6. Scheduled Actions Expand All — chrome, partial multi-open, Expand all / Collapse all (§6c) — `test_AdminScheduledActions.test.tsx` **AST-893 Expand All policy + bulk chrome**

**Broken / revised this pass:** Scheduled Actions `groups rows…` (Expand All stale-key cleanup vs remembered `openSection`); In Review / Skipped api mocks → `importOriginal` for AuthContext named exports.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useSectionExpandPolicy.test.tsx \
  ../../../tests/component/frontend/components/test_SectionExpandChrome.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-893|useSectionExpandPolicy|SectionExpandChrome|groups rows into DB"
```

Bible on publish tip:
- `docs/test-bible/frontend/hooks.md` shasum `54c4cfbfcc9e2a61e6ba96fc009d397ebfd4d68f`
- `docs/test-bible/frontend/components.md` shasum `15ee53fcf3cfeb85d7e497077e4da69319f1ee6c`
- `docs/test-bible/frontend/pages.md` shasum `fe32c6f048f450c9b3cd8b00b58171f9a2bd03a0`

— Betty

#### katherine — 2026-07-13T21:09:48.964Z
Plan: [`docs/features/interface/ast-893-expand-policy-sectioned-lists.md`](https://github.com/susansomerset/astral/blob/sub/AST-886/AST-893-expand-policy-sectioned-lists/docs/features/interface/ast-893-expand-policy-sectioned-lists.md)

**Scope:** Single-Component — frontend shared `useSectionExpandPolicy` + `SectionExpandChrome`, wire Manage Tasks list / In Review / Skipped as Expand One default, opt Scheduled Actions into Expand All for UAT.

**Conf:** high — CollapsiblePanel already supports controlled multi-open; Expand One is existing `string|null` accordion folded into one Set-based hook.

**Risk:** Medium — Expand One regression on three screens; Scheduled Actions must keep expand-only table mount (AST-746 sticky measure).

origin/`sub/AST-886/AST-893-expand-policy-sectioned-lists` @ `021f338`

---

# Optional Expand All policy and Expand all/Collapse all chrome (Allow "Expand One/Expand All" for sectioned list components)

**Linear:** [AST-893](https://linear.app/astralcareermatch/issue/AST-893/optional-expand-all-policy-and-expand-allcollapse-all-chrome-allow)  
**Parent:** [AST-886](https://linear.app/astralcareermatch/issue/AST-886/allow-expand-oneexpand-all-for-sectioned-list-components)  
**Publish ref:** `sub/AST-886/AST-893-expand-policy-sectioned-lists`

Shared sectioned-list expansion is page-owned: **Expand One** (accordion, at most one open, zero open valid) is the default when `expandAll` is omitted/false; **Expand All** is an opt-in on the hosting TypeScript page and adds visible **Expand all** / **Collapse all** chrome plus independent multi-section open. Existing accordion screens wire the shared default so behavior stays Expand One without a forced redesign of their section chrome.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` | New hook: Expand One vs Expand All state + bulk expand/collapse actions | ui |
| `src/ui/frontend/src/components/SectionExpandChrome.tsx` | New: **Expand all** / **Collapse all** button row (shown only for Expand All) | ui |
| `src/ui/frontend/src/App.css` | Styles for `.section-expand-chrome` under CollapsiblePanel section (TOC `10e`) | ui |
| `src/ui/frontend/src/components/CollapsiblePanel.tsx` | Doc-only: point parents at `useSectionExpandPolicy` for group coordination (no prop API change) | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Manage Tasks **list** sections: replace `openSection` / `resolvedOpenSection` with hook at Expand One default | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Replace `expandedSection` / `toggleSection` with hook at Expand One default | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Replace `expandedSection` / `toggleSection` with hook at Expand One default | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Opt into Expand All; wire hook + chrome; keep first-section auto-open via `setExpandedKeys` | ui |

**Out of scope (this ticket):** backend / `config.py` / API contracts; Recommended Jobs always-visible sections; Recommended Job Modal (AST-858); admin filter bar redesign / sticky columns / table layout; global persisted "last expanded" preference; Manage Tasks **edit modal** `editOpenPanel` accordion; `ArtifactEditor` criteria panels; migrating In Review / Skipped custom headers onto `CollapsiblePanel`; any edit under `tests/` or `docs/test-bible/**` (Betty at Code Complete).

**QA note (Betty — not engineer commits):** Manifest should cover Expand One regression on Manage Tasks list / In Review / Skipped, and Expand All + bulk chrome + partial multi-open on Scheduled Actions.

---

## Stage 1: Shared expand policy hook + bulk chrome

**Done when:** `useSectionExpandPolicy` and `SectionExpandChrome` exist and compile; App.css has chrome styles; `CollapsiblePanel` header comment documents parent-owned policy via the hook. No page behavior change yet.

1. Create `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` exporting:

   ```ts
   export type SectionExpandPolicyOptions = {
     /** When true → Expand All. Omit or false → Expand One (default). */
     expandAll?: boolean
     /** Current section keys in render order (used by expandAllSections). */
     sectionKeys: readonly string[]
   }

   export type SectionExpandPolicy = {
     isExpanded: (key: string) => boolean
     onExpandedChange: (key: string, next: boolean) => void
     expandAllSections: () => void
     collapseAllSections: () => void
     /** True only when expandAll is true — pages render SectionExpandChrome when this is true. */
     showBulkChrome: boolean
     /** Imperative set for page effects (e.g. Scheduled Actions first-section auto-open, candidate-change reset). */
     setExpandedKeys: (keys: ReadonlySet<string> | ((prev: ReadonlySet<string>) => ReadonlySet<string>)) => void
     expandedKeys: ReadonlySet<string>
   }

   export function useSectionExpandPolicy(options: SectionExpandPolicyOptions): SectionExpandPolicy
   ```

2. Implement state as a single `ReadonlySet<string>` (`useState`):
   - **Expand One** (`!expandAll`): `onExpandedChange(key, true)` → `new Set([key])`; `onExpandedChange(key, false)` → if `key` is in the set, `new Set()`, else leave unchanged.
   - **Expand All** (`expandAll === true`): add/remove `key` independently; never close siblings when opening another.
   - `expandAllSections`: `setExpandedKeys(new Set(sectionKeys))` (no-op useful effect when `sectionKeys` is empty).
   - `collapseAllSections`: `setExpandedKeys(new Set())`.
   - `isExpanded(key)`: `expandedKeys.has(key)`.
   - `showBulkChrome`: `!!expandAll`.
   - Do **not** add persistence, URL sync, or depth/distance limits.

3. Create `src/ui/frontend/src/components/SectionExpandChrome.tsx`:

   ```tsx
   export type SectionExpandChromeProps = {
     onExpandAll: () => void
     onCollapseAll: () => void
   }

   export default function SectionExpandChrome(props: SectionExpandChromeProps)
   ```

   Render a single row with two buttons, visible labels exactly **`Expand all`** and **`Collapse all`** (`type="button"`), class `section-expand-chrome`, calling the matching callbacks. No third control. No icons required.

4. In `src/ui/frontend/src/App.css`:
   - Add TOC line under `10e. CollapsiblePanel`: `10f. Section expand chrome (AST-893)`.
   - After the CollapsiblePanel block (~after `.artifact-editor-collapsible-stack`), add:

   ```css
   /* === 10f. Section expand chrome (AST-893) === */
   .section-expand-chrome {
     display: flex;
     flex-wrap: wrap;
     gap: 8px;
     align-items: center;
     margin-bottom: 12px;
   }
   .section-expand-chrome button {
     /* Match existing secondary admin/list button density: padding, border, border-radius, font from nearby list controls — not pill/chip chrome */
   }
   ```

   Fill button rules from an existing nearby control in this file (e.g. admin filter / list secondary button colors using `--border`, `--bg-elevated`, `--text-primary`) so the row matches Scheduled Actions density. Do not invent a new color token.

5. In `src/ui/frontend/src/components/CollapsiblePanel.tsx`, update the top file comment only (keep props/API identical). State clearly that single- vs multi-open for a group of panels is owned by the parent via `useSectionExpandPolicy` (`expandAll` omit/false = Expand One; `expandAll={true}` = Expand All), and that `expanded` / `onExpandedChange` remain the per-panel controlled API.

⚠️ **Decision:** Shared coordination is a hook + thin chrome component, not a new `SectionedList` wrapper and not React Context inside `CollapsiblePanel`. Pages already own section keys and panel rendering; a hook matches "page owns the setting" with the smallest surface and keeps In Review / Skipped on their existing custom headers (boundaries: no section-chrome redesign beyond Expand All bulk controls).

---

## Stage 2: Wire Expand One default on Manage Tasks list, In Review, Skipped

**Done when:** Those three screens use `useSectionExpandPolicy` with `expandAll` omitted/false; accordion + zero-expanded behavior matches today; no Expand all / Collapse all chrome appears on them.

1. In `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` (list sections only — **not** the edit-modal `editOpenPanel` stack):
   - Import `useSectionExpandPolicy`.
   - After `sections` is defined, call:

     ```ts
     const sectionKeys = useMemo(() => sections.map(s => s.sectionKey), [sections])
     const {
       isExpanded,
       onExpandedChange,
       setExpandedKeys,
       expandedKeys,
     } = useSectionExpandPolicy({ sectionKeys })
     ```

   - Remove `const [openSection, setOpenSection] = useState<string | null>(null)` and the `resolvedOpenSection` `useMemo`.
   - If any existing effect/logic depended on clearing a missing section key when `sections` changes, replace with: when `expandedKeys` has a key not in `sectionKeys`, call `setExpandedKeys(new Set())` (or drop stale keys) so a vanished group does not leave a ghost expanded id — same intent as today's `resolvedOpenSection` nulling.
   - On each list `CollapsiblePanel`: `expanded={isExpanded(sec.sectionKey)}` and `onExpandedChange={next => onExpandedChange(sec.sectionKey, next)}`.
   - Do **not** render `SectionExpandChrome`. Do **not** pass `expandAll: true`. Do **not** change edit-modal accordion (`editOpenPanel`).

2. In `src/ui/frontend/src/pages/JobsInReview.tsx`:
   - Import `useSectionExpandPolicy`.
   - Derive `sectionKeys` from the same `sections` array used for render (`sec.state`).
   - Replace `expandedSection` state and `toggleSection` with the hook (`expandAll` omitted).
   - Keep `useEffect(() => { setExpandedKeys(new Set()) }, [selectedId])` (same reset-on-candidate-change as today's `setExpandedSection(null)`).
   - Header button `onClick`: toggle via `onExpandedChange(sec.state, !isExpanded(sec.state))` (preserve current toggle semantics).
   - `isExpanded` drives the existing custom chevron/table visibility. Do **not** migrate onto `CollapsiblePanel`. Do **not** render bulk chrome.

3. In `src/ui/frontend/src/pages/JobsSkipped.tsx`: same pattern as JobsInReview (hook Expand One default, candidate-change reset via `setExpandedKeys(new Set())`, keep custom section headers).

⚠️ **Decision:** Manage Tasks list, In Review, and Skipped remain Expand One for this epic (AC 6 + Boundaries). Shared wiring replaces duplicated `string | null` accordion state but does not opt them into Expand All.

---

## Stage 3: Opt Scheduled Actions into Expand All + bulk chrome

**Done when:** Scheduled Actions allows multiple open sections, shows **Expand all** / **Collapse all**, supports partial multi-open and full collapse; first-section auto-open on first load still runs once; Manage Tasks / In Review / Skipped unchanged by this stage.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`:
   - Import `useSectionExpandPolicy` and `SectionExpandChrome`.
   - After `sections` is computed, call:

     ```ts
     const sectionKeys = useMemo(() => sections.map(s => s.sectionKey), [sections])
     const {
       isExpanded,
       onExpandedChange,
       expandAllSections,
       collapseAllSections,
       showBulkChrome,
       setExpandedKeys,
       expandedKeys,
     } = useSectionExpandPolicy({ expandAll: true, sectionKeys })
     ```

   - Remove `openSection` / `resolvedOpenSection`. Keep `didAutoOpenSectionRef`.
   - Rewrite the first-section auto-open effect to set keys via the hook (still once):

     ```ts
     useEffect(() => {
       if (didAutoOpenSectionRef.current || sections.length === 0) return
       didAutoOpenSectionRef.current = true
       setExpandedKeys(new Set([sections[0].sectionKey]))
     }, [sections, setExpandedKeys])
     ```

   - Stale-key cleanup: if `expandedKeys` references keys no longer in `sectionKeys`, drop those keys with `setExpandedKeys` (do not force-close unrelated still-valid keys under Expand All).
   - Immediately above the `sections.map(...)` CollapsiblePanel list (after loading/empty status branches, inside the branch that renders sections), when `showBulkChrome` render:

     ```tsx
     <SectionExpandChrome
       onExpandAll={expandAllSections}
       onCollapseAll={collapseAllSections}
     />
     ```

   - Per panel: `expanded={isExpanded(sec.sectionKey)}`; `onExpandedChange={next => onExpandedChange(sec.sectionKey, next)}`.
   - Keep the existing mount guard that only renders `ScheduledPhaseTable` when the section is expanded (`isExpanded(sec.sectionKey) ? <ScheduledPhaseTable … /> : null`) — same AST-746 measurement reason; do not remount tables for collapsed sections.
   - Do **not** change filters, column measure, sticky layout, modals, run/stop, or API calls.

⚠️ **Decision:** Scheduled Actions is the UAT opt-in for Expand All. Parent Boundaries name it among Expand One consumers that stay on default when not opted in; Notes require at least one page opted in for multi-open + bulk controls. Manage Tasks list, In Review, and Skipped stay Expand One. First-section auto-open is preserved as Expand All initial state (one open), not "open every section on load".

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-886/AST-893-expand-policy-sectioned-lists`, then proceeds.

Blocking comment format (on parent AST-886):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `Single-Component` — frontend-only shared expand hook/chrome plus four existing sectioned-list page wirings; no API, config, or data-layer change.

**Conf:** `high` — Expand One logic already lives as `string | null` on these pages; Expand All is the same set with independent membership; CollapsiblePanel already supports controlled multi-open when the parent allows it.

**Risk:** `Medium` — wrong default wiring on Manage Tasks / In Review / Skipped would regress accordion UX; Scheduled Actions Expand All must not break first-open measurement mount for sticky columns (AST-746).

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.1 Scope | Only files in the table; no Recommended Jobs / API / config. |
| §1.3 DRY | Single hook replaces four copies of accordion state. |
| §1.4 Magic | Policy is boolean `expandAll` on the page call site — not a hardcoded set of screen names in the hook. |
| §1.5 / §1.5.1 | Frontend-only — no backend debug-logging requirement. |
| §2.1 Config | No `config.py` change (Notes). |
| §3.3 Imports | Pages import hook + chrome + existing CollapsiblePanel; no cross-layer violations. |
| §3.5 UI placement | Hook under `src/hooks/` (matches existing `useAdminCandidateFilter`); chrome under `src/components/`; styles in `App.css` with TOC. |
| §3.5 Naming | PascalCase components; hook `useSectionExpandPolicy`; CSS `section-expand-chrome`. |

No rules conflicts requiring `conf-!!-NONE`. No ASTRAL_CODE_RULES boundary soften needed — this epic is already frontend-only and does not touch banned layers.

---

## Review (build)

**Built:** `origin/sub/AST-886/AST-893-expand-policy-sectioned-lists` @ `85920ff7bb46d5ab98e0648dec7e5d4bc1c94de0`

Stages 1–3: `useSectionExpandPolicy` + `SectionExpandChrome`; Expand One default on Manage Tasks list / In Review / Skipped; Scheduled Actions opts into Expand All with bulk chrome and first-section auto-open preserved. Tests deferred to Betty.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-886/AST-893-expand-policy-sectioned-lists`

### What’s solid

- Stages 1–3 match the plan: `useSectionExpandPolicy` Set semantics (Expand One vs Expand All), `SectionExpandChrome` with exact **Expand all** / **Collapse all** labels, App.css `10f`, CollapsiblePanel comment-only.
- Opt-in wiring correct: Scheduled Actions `expandAll: true` + bulk chrome; Manage Tasks list / In Review / Skipped default Expand One, no chrome; edit-modal accordion untouched.
- First-section auto-open + table mount-when-expanded preserved on Scheduled Actions; candidate-change reset preserved on In Review / Skipped.
- Boundaries held — frontend-only, no API/config, no Recommended Jobs / AST-858/885 scope creep.
- §1.1 / §1.3 / §3.3 / §3.5 satisfied; Self-Assessment Scope `Single-Component` matches the footprint. §1.5.1 / §5f / §5g N/A (UI-only).
- Betty hook/page/chrome tests + bible rows on the publish tip cover AC 1–6.

### Issues

None.

### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

---

## Resolution

**Date:** 2026-07-13  
**Radia review:** `docs(AST-893): Radia review — clean` @ `88119b8` — 0 fix-now · 0 discuss · 0 advisory.

No product or plan-doc code changes required. §9a dry-run clean vs `origin/dev` and vs `origin/ftr/AST-886-expand-one-expand-all-sectioned-lists`.
