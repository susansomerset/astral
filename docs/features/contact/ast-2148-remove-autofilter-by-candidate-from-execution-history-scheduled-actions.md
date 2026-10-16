# AST-2148 — Remove autofilter by candidate from Execution history & Scheduled Actions

<!-- linear-archive: AST-2148 archived 2026-10-16 -->

## Linear archive (AST-2148)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2148/remove-autofilter-by-candidate-from-execution-history-and-scheduled  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Astral is now truly multitenant, so the admin screens that monitor the dispatcher need to show the whole system by default. Today **Scheduled Actions** and **Execution History** silently default their **Candidate** filter to whichever candidate is selected in the left nav (and keep tracking it as the nav changes — AST-634 nav-sync), so an operator landing on either screen sees one tenant's slice and can miss running or schedulable jobs for everyone else. Susan expects both screens to open on **All** candidates and stay there until she narrows them herself.

## Functional scope

1. **Scheduled Actions opens on All candidates.** On first load the Candidate filter is **All** regardless of the left-nav selection, and changing the left-nav candidate never changes this screen's filter.
2. **Execution History opens on All candidates.** With no `candidate_id` in the URL, the Candidate filter is **All** and the ledger is not scoped to a candidate, regardless of the left-nav selection; changing the left-nav candidate never changes this screen's filter. An explicit `candidate_id` in the URL (bookmark / shared link) is still honored.
3. **Manual candidate filtering still works on both screens.** The existing Candidate dropdown (All + every candidate) stays; picking a candidate narrows the screen exactly as today.

Out of scope: other screens that use the nav-synced candidate default (Agent Timesheets, Vector Feedback, Task Performance), the left-nav selector itself, the Scheduled Actions **Add Task** modal's candidate pre-fill (that is a form default, not a filter), the Execution History timezone (still derived from the left-nav candidate), and any backend/API change.

## Component scope

* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — drop the nav-synced candidate filter default; filter starts at All.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` — **modified** (Execution History) — drop the nav-synced candidate filter default and the first-visit effect that writes the nav candidate into the URL.

Not touched: `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts` and `src/ui/frontend/src/components/AdminCandidateFilterControl.tsx` (still used, unchanged, by Agent Timesheets / Vector Feedback / Task Performance); `src/ui/api/api_admin.py` (`/api/admin/dispatch_tasks` and `/api/admin/dispatch_ledger` already return every candidate when no `candidate_id` is passed).

## Technical scope

* `AdminScheduledActions.tsx` — modified page component: stop using the nav-synced `useAdminCandidateFilter` hook; hold the Candidate filter as plain page state that starts at All (empty), with the candidate option list taken from the candidate context sorted the same way the shared control expects. The existing client-side row filter, the All-candidate default sort (by Avail desc), and the Add Task modal's `selectedId` pre-fill are unchanged.
* `AdminPerformanceMonitor.tsx` — modified page component: stop using the nav-synced hook; the Candidate filter value is read straight from the URL `candidate_id` param (absent = All) and written back through the existing URL setter; remove the first-visit effect that copies the left-nav candidate into the URL. Timezone derivation from the left-nav candidate is unchanged.
* **Test impact (Betty,** `qa-child`**):** the **AST-634** nav-default / nav-sync cases in `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` and the **AST-634** setup note in `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` assert the behavior being removed; the AST-628 summary in `docs/test-bible/frontend/pages.md` describes it. Other Scheduled Actions tests that render with a nav candidate and assume nav filtering may need fixtures adjusted. `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` stays as-is (hook unchanged).

## Architectural definition

* **Patterns to reuse:** no established pattern applies (frontend filter-default change on two admin pages; no in-force UI pattern covers admin list filters).
* **New patterns proposed:** none.
* **Applicable statutes:** none — no in-force statute governs frontend filter state; no logging, dispatch, entity, or API surface changes.

Canon Scope for this epic is therefore empty.

## Acceptance criteria

 1. **Wrong-shape guard:** `rg -n "useAdminCandidateFilter" src/ui/frontend/src/pages/AdminScheduledActions.tsx src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` returns nothing. Fail: either page still imports the nav-synced hook (including via a new option flag on it).
 2. **Hook and other screens untouched:** `git diff origin/dev -- src/ui/frontend/src/hooks/useAdminCandidateFilter.ts src/ui/frontend/src/components/AdminCandidateFilterControl.tsx src/ui/frontend/src/pages/AdminAgentTimesheets.tsx src/ui/frontend/src/pages/AdminVectorFeedback.tsx src/ui/frontend/src/pages/AdminTaskPerformance.tsx src/ui/api/` is empty. Fail: any diff.
 3. **Scheduled Actions default All:** with left-nav candidate **A** selected and dispatch tasks for **A** and **B**, first load shows the Candidate dropdown at **All** and rows for both **A** and **B**. Fail: dropdown shows **A** or **B**'s rows are hidden.
 4. **Scheduled Actions ignores nav:** switching left-nav from **A** to **B** leaves the Candidate dropdown and visible rows unchanged. Fail: dropdown changes or rows narrow.
 5. **Execution History default All:** opening Execution History with left-nav **A** selected and no `candidate_id` in the URL issues `/api/admin/dispatch_ledger` without a `candidate_id` query param, leaves the page URL without `candidate_id`, and shows the dropdown at **All**. Fail: the fetch or URL carries `candidate_id=A`, or the dropdown shows **A**.
 6. **Execution History ignores nav:** switching left-nav from **A** to **B** does not add/change `candidate_id` in the URL or the ledger fetch. Fail: either changes.
 7. **Bookmark honored:** opening Execution History with `?candidate_id=B` (left-nav **A**) fetches the ledger with `candidate_id=B` and shows **B** in the dropdown. Fail: fetch unscoped, scoped to **A**, or dropdown not **B**.
 8. **Manual filter still works:** on both screens, choosing **B** in the dropdown narrows to **B** (Scheduled Actions rows all have `candidate_id` **B**; Execution History refetches with `candidate_id=B`), and choosing **All** restores every candidate. Fail: selection has no effect or All does not restore.
 9. **Add Task pre-fill unchanged:** on Scheduled Actions with left-nav **A**, **Add Task** opens with Candidate **A**; with no left-nav candidate, Save stays disabled (`save disabled on add when no candidate selected` stays green). Fail: pre-fill is blank with **A** selected, or Save enables with no candidate.
10. **Build:** `npm run build` passes and `npm run lint` reports no findings in the changed files beyond those already on `origin/dev` (dev carries pre-existing lint errors); the Vitest files named in Technical scope pass. Fail: build error, a new lint finding in a changed file, or a failing Vitest.

## Open questions

none

## Proposed child tickets

#### 1: **Default Scheduled Actions and Execution History to All candidates - Katherine**

Removes the left-nav candidate auto-filter (initial default and nav-sync) from Scheduled Actions and Execution History so both open on **All** and only narrow when the operator picks a candidate; Execution History still honors an explicit `candidate_id` URL. Does not touch the shared hook, the other screens that use it, the Add Task pre-fill, or any API.
**Citations:** none — Canon Scope is empty (frontend filter default only; no in-force pattern or statute applies).
**Scope:**

* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — drop the nav-synced candidate filter default; filter starts at All. Technical: stop using the nav-synced `useAdminCandidateFilter` hook; hold the Candidate filter as plain page state that starts at All (empty), with the candidate option list taken from the candidate context sorted the same way the shared control expects. The existing client-side row filter, the All-candidate default sort (by Avail desc), and the Add Task modal's `selectedId` pre-fill are unchanged.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` — **modified** (Execution History) — drop the nav-synced candidate filter default and the first-visit effect that writes the nav candidate into the URL. Technical: stop using the nav-synced hook; the Candidate filter value is read straight from the URL `candidate_id` param (absent = All) and written back through the existing URL setter; remove the first-visit effect that copies the left-nav candidate into the URL. Timezone derivation from the left-nav candidate is unchanged.

Estimate: 2

**New patterns:** none.

**Monolith check:** Functional scope N = 3, children M = 1 — intentional: one inseparable small slice (the same few-line default change on two sibling admin pages that share one hook and one test bible section); splitting would double plan/test/review overhead for roughly a dozen lines.

**Scope partition check:** both Component scope files and both Technical scope items are claimed by child 1 only.

---

## Original brief

Now that we are truly multitenant, it's better to see all the possible and running jobs.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
