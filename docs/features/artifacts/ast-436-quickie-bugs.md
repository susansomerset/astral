# AST-436 — Quickie bugs

<!-- linear-archive: AST-436 archived 2026-06-15 -->

## Linear archive (AST-436)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-436/quickie-bugs  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan hit four small but annoying UI regressions while exercising Artifacts and admin tooling on `dev`. None are new features — they are polish fixes that restore expected layout and live data on screens she uses daily (Candidate Profile, Scheduled Actions / dispatch, Execution History). Shipping them together avoids four one-line tickets and keeps UAT friction low while larger artifact work (AST-300/301, AST-307 remainder) continues.

## Functional scope

### 1\. Candidate Profile — cover letter signature image as a tab

The cover letter **signature image** control currently renders as a separate block **below** the profile’s tabbed text areas. It should live **inside the same tabbed pattern** as the other profile text sections (alongside Bio Summary, Sample Cover Letter, Cover Letter Signature text, etc.), not as an orphan section under the tabs.

The signature **text** field already has a tab (“Cover Letter Signature”); the **image** upload, preview, remove control, and limit messaging belong in a dedicated tab (label TBD in plan — e.g. “Signature Image”) with the same save/cancel behavior as the rest of the profile page.

### 2\. Scheduled Actions — refresh “Avail” after manual run

On **Scheduled Actions** (dispatch tasks list), the **Avail** column (`available_count`) reflects how many entities are eligible for that dispatch row. When Susan clicks **Run** on a row and the manual batch **finishes**, that count must update to reflect post-run eligibility **without** requiring a full page reload. In-progress runs may continue to show the prior count until completion; on completion, the row’s Avail value must match what a fresh load of the dispatch tasks API would return.

### 3\. Execution History — default to today only

On **Execution History** (`/admin/performance_monitor`), the list must **not** briefly (or persistently) show all historical batches before the date filter applies. On first open, the table must show only batches whose **started** time falls on **today** in the **selected candidate’s timezone** (same “today” semantics already intended for the From date filter). Changing From/To or other filters must continue to work; the default view is today-through-today (or equivalent single-day window) without a flash of unfiltered rows.

### 4\. Execution History — in-progress rows vs “check” batches

**Skip Checks** exists to hide low-value ledger rows: batches that **completed** with **zero** processed / pass / fail / error counts (health-check style runs). **In-progress** batches (`RUNNING` status) with count zero must **remain visible** and show `RUNNING` in the Status column — they must **not** be hidden or misclassified as check-only rows. Only **finished** zero-count batches may be suppressed when Skip Checks is enabled (default on). When Skip Checks is off, all rows including zero-count completed batches still appear.

## Boundaries

* Does **not** implement Job Analysis Report resume/cover letter panels (AST-307 remainder) or artifact pipeline behavior.
* Does **not** change dispatch scoring, batch sizing, or scheduler semantics — only UI refresh and display rules.
* Does **not** redesign Scheduled Actions or Execution History layout beyond what is needed for these four fixes.
* Does **not** alter cover letter signature validation rules (JPEG limits, data URL storage) — only where the image editor appears on Candidate Profile.
* Does **not** add new admin routes or change production prompt/rubric diagnostics (AST-434/438).

## Acceptance criteria

1. **Profile tabs:** Opening Candidate Profile, the signature **image** control appears as its own tab in the tabbed section; nothing signature-image-related remains in a standalone section below the tabs. Upload, preview, remove, and save persist `profile.cover_letter_signature_image` as today.
2. **Profile tabs:** Signature **text** remains editable in its existing tab; contact fields and other tabs unchanged.
3. **Dispatch Avail:** After a manual **Run** completes on a Scheduled Actions row, the **Avail** column for that row updates without reload (verified by running a task that changes eligible entity count, or by observing count refresh when the run ends).
4. **Execution History default:** Cold load of Execution History shows only today’s batches (candidate TZ); no full-history flash on first paint.
5. **Execution History filters:** Setting From/To to other dates still filters correctly; clearing or widening dates shows the expected wider set.
6. **Execution History RUNNING:** With **Skip Checks** on (default), a `RUNNING` batch with all count columns zero is **visible** and Status reads **RUNNING**.
7. **Execution History checks:** With **Skip Checks** on, a **COMPLETED** (or otherwise finished) batch with all count columns zero is **hidden**.
8. **Execution History checks off:** With **Skip Checks** off, finished zero-count batches are visible again.

## Dependencies and blockers

* **AST-366** / **AST-310** — Done (signature profile fields and validation). This ticket adjusts layout and admin UX only.
* None blocking start.

## Open questions

1. **Signature image tab label** — Susan’s preference for tab title (“Signature Image”, “Cover Letter Signature (image)”, or merge image into the existing “Cover Letter Signature” tab with text above image).
2. **Dispatch Avail refresh** — Is polling thread status until idle sufficient, or must we also listen for a specific API completion event? (Implementer chooses minimal working approach; acceptance is observable row update after run ends.)

### Comments

#### chuckles — 2026-05-23T03:14:54.729Z
## Landed on origin/dev — Chuckles

- `origin/ftr/AST-436-quickie-bugs` was already on local `dev` (prep-uat); pushed `origin/dev`
- Deleted `origin/ftr/AST-436-quickie-bugs`
- Moved to **Done** (were PR Ready): **AST-436** (parent), **AST-442**, **AST-443**, **AST-444** (Katherine assignee unchanged on children)

Push range: `a4e624a3..7e7d36e0` on `origin/dev`

— Chuckles

#### chuckles — 2026-05-23T03:10:21.554Z
## UAT Ready — Chuckles (prep-uat rerun)

Refreshed **local `dev`** from latest **`origin/ftr/AST-436-quickie-bugs`** (Katherine fixes after last prep-uat). Child branches were merged on prior run; `sub/*` already deleted.

**Parent branch:** `origin/ftr/AST-436-quickie-bugs`

**Children (on ftr):** AST-442, AST-443, AST-444

**New since last UAT:** `85ca94e1` — profile hooks crash fix (signature image tab); execution history date inputs (draft + blur commit; clear From without forcing today back)

Local `dev` merged (prep-uat §8). Restart the app if running, then test.

`ftr` tip: `1fca1bd3` · local `dev` merge: `7e7d36e0`

## Manual test steps

**Prerequisites:** Local `dev`; app restarted.

1. **Profile — no crash** — Open Candidate Profile; page loads (no React hooks error). Signature **image** on its own tab; upload/preview/remove/save work.
2. **Profile — signature text** — Cover Letter Signature text tab unchanged.
3. **Scheduled Actions — Avail** — Manual **Run** on a row; when finished, **Avail** updates without reload.
4. **Execution History — today default** — Cold open; only today’s batches (candidate TZ); no full-history flash.
5. **Execution History — clear From** — Clear the **From** date; it stays cleared (does not snap back to today until you set it).
6. **Execution History — blur commit** — Edit From/To, tab away; filter applies on blur.
7. **Execution History — RUNNING** — Skip Checks on: zero-count **RUNNING** batch visible with RUNNING status.
8. **Execution History — finished checks** — Skip Checks on: finished zero-count batch hidden; off → visible again.

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### katherine — 2026-05-23T02:55:45.660Z
Tests passed by Katherine (**test-astral** rerun, parent **AST-436**).

**Branch:** `origin/ftr/AST-436-quickie-bugs` @ `85ca94e1` (UAT fixes + Betty’s augmented tests — no additional product commits this pass).

**Manifest (all green):**
1. `npx vitest run tests/component/frontend/pages/test_CandidateProfile.test.tsx` — **4 passed** (includes hooks-safe profile load + signature image tab)
2. `npx vitest run tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — **5 passed** (today default, skip-checks RUNNING, date blur commit)
3. `npx vitest run tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **12 passed**
4. `npx vitest run tests/component/frontend/components/test_TabbedTextArea.test.tsx` — **3 passed**

`npx tsc -b --noEmit` — clean.

**Covers Susan UAT failures:** profile black screen (hooks order) + Execution History date typing/clear (draft + blur + `userSetDateFrom`).

Please re-pull **`ftr/AST-436-quickie-bugs`** and re-run UAT items **1** and **4** on local `dev` after Chuckles merge, or test directly from this `ftr` tip.

#### betty — 2026-05-23T02:49:31.057Z
[check-linear]

Sorry I missed your @betty on this parent earlier — **check-linear** only scanned **assignee = me**; **AST-436** is on you, and the @mention was in the thread body (Linear search did not surface it in my §0b pass). I have tightened my habit: **parent UAT threads + `@betty` on Team Astral** get `list_comments` even when I am not assignee.

---

### 1. Profile black screen (AC 1 failed)

**Cause:** `useMemo` for `signatureImagePanel` ran **after** loading early returns. First paint returned before the hook ran; second paint called it → Rules of Hooks violation → blank app chrome (nav disappears with the route tree).

**Why QA missed it:** AST-442 manifest only ran **`TabbedTextArea.customPanels`** in isolation and **`test_CandidateProfile`** without **`/api/ui_config`** — so we never mounted the real **Candidate Profile** route with the tab wiring. Component test passed; full page did not.

**Fix:** `origin/ftr/AST-436-quickie-bugs` — hooks moved above early returns; handlers via `useCallback`.

**QA change (recommendation):** For any ticket that changes a **routed page**, manifest must include at least one test that **renders that page** (with required API mocks: shapes + `ui_config` here), not only a child component.

---

### 2. Execution History date field (AC 4 failed)

**Cause:** `onChange` pushed every keystroke into URL search params → immediate ledger refetch → controlled input snapped mid-typing. Clearing **From** also re-ran the “default today” effect because the URL lost `date_from`.

**Why QA missed it:** Tests asserted default-today **API query** and skip-checks behavior, not **typing UX** (multi-digit day/month) or **clearing** the default.

**Fix:** Local draft state; commit on **blur**; `userSetDateFrom` ref so clearing does not re-inject today into the fetch filter.

**QA change (recommendation):** Add manifest steps (or RTL) for: type a full date without mid-entry reset; blur to apply; clear **From** and confirm wide fetch / empty param.

---

### Git

- **Branch:** `origin/ftr/AST-436-quickie-bugs` @ tip after push
- **Tests added:** full **Candidate Profile** load + signature tab; date blur does not refetch until blur

Katherine remains assignee on **AST-442** / **AST-444** children; parent **User Testing** unchanged — please re-pull `ftr/AST-436` and re-run UAT items 1 and 4.

— Betty

#### susan — 2026-05-23T02:42:04.667Z
1. Profile test: When I click on the Profile navigation, the navigation disappears and nothing renders on the screen, it just goes black in the browser tab.
   1. I want @betty to explain how this passed through QA, and what she recommends that we add/change to our qa approach to avoid these simple issues getting all the way to UAT.
   2. Obviously, please get this bug fixed.
2. Passed.
3. Passed.
4. Failed: Trying to delete the default date does not work, I can't even select the whole date.  Also, trying to type "21" for "05/21/2026", it automatically refreshes for "05/02/2026" and then "05/01/2026" because it didn't let me enter two numbers at once.  This is deeply wrong.  Again, what are we testing, exactly?  I want @betty's advice ont his.
5. Passed
6. Didn't test, but it's fine.
7. Didn't test, but it's fine.

#### chuckles — 2026-05-22T17:27:05.146Z
## UAT Ready — Chuckles (prep-uat — Astral Artifacts)

All **3** child branches merged into parent branch and child branches deleted.

**Parent branch:** `origin/ftr/AST-436-quickie-bugs`

**Merged in order:**
1. **AST-442** — signature image tab on Candidate Profile (deleted)
2. **AST-443** — Scheduled Actions Avail refresh after manual run (deleted)
3. **AST-444** — Execution History today filter + skip checks (deleted)

Local `dev` merged (prep-uat §8). Restart the app if running, then test.

`ftr` tip: `2d4f6a1e` · local `dev` rollup: `ed879a6b`

## Manual test steps

**Prerequisites:** Local `dev`; app restarted.

1. **Profile — Signature Image tab** — Candidate Profile → confirm signature **image** upload/preview/remove is its own tab (not below tabs). Signature **text** still on its tab. Save persists.
2. **Scheduled Actions — Avail** — Run a dispatch row manually; when the run **finishes**, **Avail** updates without full page reload.
3. **Execution History — today default** — Cold open Execution History; only **today’s** batches (candidate TZ); no flash of full history.
4. **Execution History — date filters** — Change From/To; wider/narrow sets behave correctly.
5. **Execution History — RUNNING + Skip Checks** — With Skip Checks **on**, a **RUNNING** zero-count batch stays visible with status RUNNING.
6. **Execution History — finished checks** — With Skip Checks **on**, a **finished** zero-count batch is **hidden**.
7. **Execution History — Skip Checks off** — Finished zero-count batches visible again.

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-05-19T21:02:04.929Z
prep-uat blocked — not all children are rollup-safe.

Still in flight:
  AST-442  Code Complete  assigned to Katherine Johnson
  AST-443  Code Complete  assigned to Katherine Johnson
  AST-444  Code Complete  assigned to Katherine Johnson

Cannot merge until every sibling is User Testing, Done, PR Ready, or canceled.

Next pipeline: Betty **qa-astral** → Katherine **test-astral** → Radia **review-astral** → Katherine **resolve-astral** (each child to User Testing), then re-run **prep-uat** for Artifacts.

— Chuckles

#### chuckles — 2026-05-19T16:27:57.226Z
## Dispatch — Chuckles

Dispatched **3** child tickets from the approved definition (Execution History items 3+4 combined — same page).

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-442 | Cover letter signature image tab | Katherine | `sub/AST-436/AST-442-quickie-bugs-cover-letter-signature-image-tab` | — |
| AST-443 | Scheduled actions avail refresh after manual run | Katherine | `sub/AST-436/AST-443-quickie-bugs-scheduled-actions-avail-refresh-after-manual-run` | — |
| AST-444 | Execution history today filter and skip checks | Katherine | `sub/AST-436/AST-444-quickie-bugs-execution-history-today-filter-and-skip-checks` | — |

**Assignment rationale:**
- **Katherine:** All three are React admin/candidate UI surfaces (`CandidateProfile`, `AdminScheduledActions`, `AdminPerformanceMonitor`). No backend contract changes required beyond existing APIs.
- **Ada / Hedy:** Not assigned — queue kept light; no core/dispatch-layer work in scope.

**Definition notes (dispatch defaults):**
- Signature image tab label → **Signature Image** dedicated tab (per functional scope); override in plan if you prefer merge with text tab.
- Avail refresh → implementer picks minimal approach (thread poll until idle + `loadData` is fine).

Susan can override any assignment by reassigning the child ticket directly.

Parent **In Progress**, assignee Chuckles. **prep-uat** merges child branches when all children reach **User Testing**.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-436-quickie-bugs` @ `ceec63c7`
- Children: `origin/sub/AST-436/AST-442-…`, `AST-443-…`, `AST-444-…` (same tip)

— Chuckles

#### chuckles — 2026-05-19T16:24:09.868Z
## Dispatch blocked — Chuckles

Cannot dispatch yet (§2a / §2b):

**Assignee:** Parent is assigned to **Susan**. Dispatch requires **assignee = Chuckles** — reassign Chuckles when the definition is approved for dispatch.

**Open questions still in Description:**
1. Signature image tab label — separate tab vs merged into “Cover Letter Signature” with text above image?
2. Dispatch Avail refresh — resolved for dispatch if you accept “implementer picks minimal approach; AC = Avail updates when run ends” — please confirm in a comment or remove from Open questions.

@susan — after assignee → Chuckles and open questions cleared, say **dispatch AST-436** again.

— Chuckles

#### chuckles — 2026-05-19T16:19:23.487Z
Definition draft ready for review. Key decisions made:
- Four independent UI fixes bundled under one parent; dispatch as up to four child tickets is fine.
- Signature **image** moves into profile tabbed UI; signature **text** stays on its existing tab.
- Execution History: fix default “today” load + separate RUNNING rows from zero-count **completed** check batches (Skip Checks scope).
- Scheduled Actions: Avail column must refresh after manual run completes.

**Open questions:** 2 (tab label for signature image; implementer choice on refresh mechanism — acceptance is post-run Avail update).

Please review the Description and comment with changes or approval.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
