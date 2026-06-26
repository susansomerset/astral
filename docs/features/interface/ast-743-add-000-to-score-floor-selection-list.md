# AST-743 — Add 0.00 to score floor selection list

<!-- linear-archive: AST-743 archived 2026-06-23 -->

## Linear archive (AST-743)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-743/add-000-to-score-floor-selection-list  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-735; related: AST-737

### Description

## Purpose

Susan configures dispatch **score floor** on scored trigger rows via the **Edit Dispatch Task** modal on Scheduled Actions. The dropdown today starts at **1.00** (hardcoded in the frontend) even though the backend already accepts **0.00** as a stored floor. She needs **0.00** as a selectable option so she can claim jobs with any non-null **latest_score** (including zero) without raising the floor to 1.0. The allowed values must live in product config and be served to the UI through one shared source — not duplicated inline in React — per **ASTRAL_CODE_RULES** §1.4 / §2.1.

## Functional scope

* **Config catalog:** Define the complete ordered list of allowed **score_floor** dropdown values in `src/utils/config.py` (single source of truth). The list must include **0.00** and retain the existing **0.50** step through the current maximum (**10.00** unless Susan revises in Open questions).
* **Admin API exposure:** Expose that catalog to the admin frontend (extend an existing dispatch-task metadata endpoint or add a dedicated one) so the UI receives string values ready for `<select>` options — same pattern as `/api/admin/dispatch_tasks/state_options` for trigger states.
* **Edit Dispatch Task modal:** On **Scheduled Actions** (`AdminScheduledActions`), the **Score Floor** `<select>` in the create/edit dispatch-task modal must render options **only** from the API/config catalog — remove the hardcoded `useMemo` list.
* **Save and display parity:** When Susan picks **0.00** for a scored row, create/update persists **0.0** and the modal reopens showing **0.00** selected; the table **Floor** column shows **0.00** for that row.
* **Scored-row gating unchanged:** **Score Floor** remains visible only when the row is scored per `dispatch_claim_uses_score_floor` (input triggers such as **VALID_TITLE** stay unscored — no floor field). Default **1.00** when scored and unset stays as today.

## Boundaries

* Does **not** change `dispatch_claim_uses_score_floor`, dispatcher claim math, or `pass_threshold` grading — only admin selectable values and where the UI reads them (**AST-586** / **AST-617** behavior preserved).
* Does **not** redesign Scheduled Actions layout, grouping, or filters (**AST-735** is separate; this ticket may ship first).
* Does **not** implement the **AST-737** dispatch refactor (task-centric model).
* Does **not** add score-floor pickers elsewhere (e.g. Jobs Skipped display-only floor is out of scope unless it already duplicates the same hardcoded list — fix only the Edit Dispatch Task modal source of truth).
* Does **not** require backend debug-logging changes (UI-only + config/API catalog).

## Acceptance criteria

1. **0.00 in dropdown:** For a scored dispatch row, the Edit Dispatch Task modal **Score Floor** list includes **0.00** as the first option.
2. **Config-driven:** Allowed values are defined once in `config.py`; no duplicate numeric array remains in `AdminScheduledActions.tsx` for floor options.
3. **API-served:** The modal loads floor options from an admin API response (not client-invented constants).
4. **Persist 0.00:** Saving **0.00** on a scored row stores **0.0** in `dispatch_task.score_floor`; reload/edit shows **0.00** selected and the list row **Floor** column shows **0.00**.
5. **Existing range preserved:** Options from **1.00** through **10.00** in **0.50** steps remain available (plus **0.00** and **0.50** at the low end).
6. **Unscored rows unchanged:** Rows where `is_scored` is false still hide **Score Floor** and persist `score_floor` **null**.

## Dependencies and blockers

None. Backend already accepts `score_floor` **0.0** on scored updates; **AST-586** claim gating is shipped (**AST-617**).

**Adjacent (not blocking):** **AST-735** (Scheduled Actions screen edits) may touch the same page later — implement this catalog change in a way **AST-735** can reuse the same API/config source.

## Open questions

1. Confirm the low end is **0.00** and **0.50** then **1.00…10.00** in **0.50** steps (natural extension of today's list), rather than adding **0.00** alone without **0.50**.
   1. That's fine. We do like consistency around here!

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-743 (parent) | ftr/AST-743-add-000-to-score-floor-selection-list |
| AST-750 | sub/AST-743/AST-750-config-driven-score-floor-dropdown |

**Epic worktree:** `astral-AST-743/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 2265b0af-d3be-4e7f-b17e-4fe49d0ee777 |
| Betty | qa | 627e3599-768c-4e90-b971-056f5cf41746 |
| Radia | review | 3e4852ac-baad-4e7b-a737-d1b88229637e |

---

## Original brief

Update the list of numeric options for score floor to include 0.00 as a valid option.  Meanwhile, make sure that list is config-driven and universally referenced on the Edit Dispatch Task modal screen.

### Comments

#### susan — 2026-06-23T19:05:45.251Z
Please do update the ftr and sub branches with my changes to config.py so that they are in sync with what is on local dev's config.py file, then finish up 743 as PR Ready.

#### chuckles — 2026-06-23T18:53:51.673Z
[fix-uat] @susan

Your 2026-06-23 comment asks to confirm a config.py fix on **origin/dev** and close without further processing. Checked **origin/dev** @ `825d292`: that commit does **not** add `DISPATCH_SCORE_FLOOR_VALUES`, the admin `score_floor_options` endpoint, or the Scheduled Actions modal wiring — `AdminScheduledActions.tsx` still hardcodes 1.00–10.00.

The shipped AST-743 implementation is on **`origin/sub/AST-743/AST-750-config-driven-score-floor-dropdown`** (AST-750 at User Testing); it is **not** merged to **origin/dev** yet.

**Need your call (not a UAT bug):**
1. **`finish-up AST-743`** — land AST-750 via ftr → dev (normal ship), or
2. **Close AST-743/750 as superseded** — if your local intent was different from AST-750, say what you changed and where.

No `UAT:` bug children filed — your note is a close/merge decision, not a repro failure.

— Chuckles

#### susan — 2026-06-23T18:22:07.002Z
@chuckles I made my own updates to the config.py file to address this issue.  Please confirm that you see and agree with the change on origin/dev and close this ticket without further processing.

#### chuckles — 2026-06-18T22:57:12.951Z
@susan Headless `agent` hit Cursor usage limit during AST-750 test-child (stage 8). AST-750 is Tests Ready with Betty manifest posted; resume datt after spend limit or model switch.

— Chuckles

#### chuckles — 2026-06-18T22:38:06.611Z
@susan

1. Confirm the low end is **0.00** and **0.50** then **1.00…10.00** in **0.50** steps (natural extension of today's list), rather than adding **0.00** alone without **0.50**.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
