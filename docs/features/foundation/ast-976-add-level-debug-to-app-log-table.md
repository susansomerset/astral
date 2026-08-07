# AST-976 — Add level "DEBUG" to app_log table

<!-- linear-archive: AST-976 archived 2026-08-05 -->

## Linear archive (AST-976)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-976/add-level-debug-to-app-log-table  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-360

### Description

## Purpose

Susan cannot tell clean production logging from debug noise in `app_log` because debug-gated emissions are persisted at **INFO** alongside ordinary INFO. When a run has **debug=True**, she needs true **DEBUG** rows in `app_log` so Execution History’s Level filter and raw SQL triage can separate debug contract output from the INFO that still appears when **debug=False**. This is a Foundation observability correctness fix — not a new debug-content program.

## Functional scope

* **DEBUG severity for debug-gated emissions:** When **debug=True**, backend debug-contract / debug-only log lines that today land as INFO are persisted to `app_log` with level **DEBUG**. Content and gating rules stay as defined by the existing backend debug contract (**AST-538** / Code Rules §1.5.1) — this epic corrects the **stored level**, not the shape of index headers or detail lines.
* **INFO remains INFO for normal production logging:** Ordinary INFO (and WARNING/ERROR) that runs when **debug=False** continues to persist at those levels. A **debug=False** run must not flood `app_log` with DEBUG rows from the debug-contract helpers.
* **Persistence path accepts DEBUG:** The path that writes buffered log records into `app_log` must actually record DEBUG-level records (not drop them and not coerce them to INFO).
* **DEBUG on Execution History Level list:** Execution History’s Level control includes **DEBUG** in the selectable level list (alongside All / INFO / WARNING / ERROR as applicable), so Susan can filter expanded batch logs to DEBUG-only after the persistence child lands.

## Boundaries

* Does **not** redesign the AST-538 debug contract (index headers, `|` detail prefix, truncation rules) — only the severity written to `app_log` for those gated emissions.
* Does **not** globally reduce INFO volume, add new debug call sites across roster/consult, or require React/UI debug logging.
* Does **not** backfill or rewrite historical `app_log` rows that were stored as INFO before this change.
* Does **not** change grandfathered `logger.info("[DEBUG] …")` call sites in untouched files unless the logging pipeline change naturally reclassifies only the debug-gated helpers — mass call-site cleanup across the product is out of scope.
* Must not break existing `app_log` write path constraints (late import / utils→data cycle guard per Code Rules §1.5).
* Execution History child owns only ensuring **DEBUG** is on the Level list and usable for filter/Copy empty-state behavior consistent with other levels — not a redesign of ledger columns, Skip Checks, Agent Data, or other Execution History filters.
* Adjacent: [AST-360](https://linear.app/astralcareermatch/issue/AST-360/periodic-data-cleanup) (periodic log cleanup) remains Backlog and is not part of this epic. Prior Level-filter work (**AST-838** / **AST-840**) may already list DEBUG — child #2 confirms or adds as needed; it does not reopen unrelated filter scope.

## Acceptance criteria

1. On a backend run with **debug=True** that emits debug-contract lines, `app_log` contains rows with level **DEBUG** for those emissions (verifiable via Execution History **Level = DEBUG** and/or direct inspection of `app_log`).
2. On an otherwise comparable run with **debug=False**, those same debug-contract lines do **not** appear as DEBUG (or at all); ordinary production INFO/WARNING/ERROR rows still appear as today.
3. Ordinary INFO lines that are not debug-gated still persist as **INFO** on both debug=True and debug=False runs (debug mode does not re-label all INFO as DEBUG).
4. Execution History Level control lists **DEBUG** as a selectable option; with **Level = DEBUG** on a debug=True batch that produced DEBUG rows, the expanded log shows those DEBUG lines; with **Level = INFO**, those DEBUG lines are hidden and INFO lines remain visible.
5. WARNING and ERROR persistence and display behavior are unchanged.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Persist DEBUG level for debug-gated app_log lines | Debug-gated backend emissions persist as **DEBUG** in `app_log` when **debug=True**; production INFO/WARNING/ERROR unchanged when **debug=False**; persistence path does not drop DEBUG. Does **not** own Execution History Level list UI. | Ada | — |
| 2 | Add DEBUG to Execution History Level list | Execution History Level control includes **DEBUG** so Susan can filter expanded logs to DEBUG-only (filter/Copy/empty-state consistent with other levels). Does **not** own app_log persistence or other Execution History redesign. If DEBUG is already present from prior Level-filter work, confirm it and close the gap only if missing. | Katherine | after #1 |

**Monolith check:** Four functional capabilities → two children (persistence vs Execution History Level list). Child #2 sequences after #1 so UAT can prove Level=DEBUG against real DEBUG rows.

**New patterns:** None. Reuses the existing backend debug-contract gate (**AST-538**); corrects stored severity and ensures Execution History can select DEBUG.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-976 (parent) | ftr/AST-976-add-level-debug-to-app_log-table |
| AST-979 | sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines |
| AST-980 | sub/AST-976/AST-980-add-debug-to-execution-history-level-list |

**Epic worktree:** `astral-AST-976/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during do-all-the-things / fix-uat. datt resume: read this table for child agent --resume ids.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | a1dc1804-3291-4ddc-9c8c-27830427ae93 |
| Katherine | engineer | 8c2dd064-c55d-4044-8705-f3d801e6e9e2 |
| Betty | qa | 92930c24-e1e0-47ca-a84d-d6e420ff170c |

---

## Original brief

We are capturing INFO and DEBUG both as INFO level in app_log table, making it hard to know what is clean logging and what is debugging noise.  So, when Debug=true, I expect to find rows of DEBUG level in app_log, as well as the normal INFO logging that happens even when Debug=false.

### Comments

#### chuckles — 2026-07-24T01:04:49.349Z
[datt-trace] **start** spawn=`b9c1a6f2` — **IN FLIGHT** spawning **Betty** role=qa `bootstrap` on `AST-979`
- parent: `AST-976`
- AGENT_SESSION: `92930c24-e1e0-47ca-a84d-d6e420ff170c`

— Chuckles

#### chuckles — 2026-07-24T01:03:54.772Z
[datt-trace] **start** spawn=`77616451` — **IN FLIGHT** spawning **Betty** role=qa `qa-child` on `AST-979`
- parent: `AST-976`
- AGENT_SESSION: `(none)`

— Chuckles

#### chuckles — 2026-07-24T01:03:23.147Z
[datt-trace] **end** spawn=`a3b7f28e` — **DONE** **Ada** role=engineer `build-child` on `AST-979`
- parent: `AST-976`
- exit: `0` · elapsed: `77s`

— Chuckles

#### chuckles — 2026-07-24T01:02:05.298Z
[datt-trace] **start** spawn=`a3b7f28e` — **IN FLIGHT** spawning **Ada** role=engineer `build-child` on `AST-979`
- parent: `AST-976`
- AGENT_SESSION: `a1dc1804-3291-4ddc-9c8c-27830427ae93`

— Chuckles

#### chuckles — 2026-07-24T01:01:48.030Z
[datt-trace] **end** spawn=`df48f866` — **DONE** **Ada** role=engineer `check-linear` on `AST-979, AST-980`
- parent: `AST-976`
- exit: `0` · elapsed: `49s`

— Chuckles

#### chuckles — 2026-07-24T01:01:46.662Z
[datt-trace] **end** spawn=`f6dfeca4` — **DONE** **Katherine** role=engineer `check-linear` on `AST-979, AST-980`
- parent: `AST-976`
- exit: `0` · elapsed: `48s`

— Chuckles

#### chuckles — 2026-07-24T01:00:57.504Z
[datt-trace] **start** spawn=`f6dfeca4` — **IN FLIGHT** spawning **Katherine** role=engineer `check-linear` on `AST-979, AST-980`
- parent: `AST-976`
- AGENT_SESSION: `8c2dd064-c55d-4044-8705-f3d801e6e9e2`

— Chuckles

#### chuckles — 2026-07-24T01:00:56.942Z
[datt-trace] **start** spawn=`df48f866` — **IN FLIGHT** spawning **Ada** role=engineer `check-linear` on `AST-979, AST-980`
- parent: `AST-976`
- AGENT_SESSION: `a1dc1804-3291-4ddc-9c8c-27830427ae93`

— Chuckles

#### chuckles — 2026-07-24T01:00:41.332Z
[datt-trace] **end** spawn=`91252884` — **DONE** **Joan** role=validate `validate-plan` on `AST-980`
- parent: `AST-976`
- exit: `0` · elapsed: `149s`

— Chuckles

#### chuckles — 2026-07-24T00:58:11.095Z
[datt-trace] **start** spawn=`91252884` — **IN FLIGHT** spawning **Joan** role=validate `validate-plan` on `AST-980`
- parent: `AST-976`
- AGENT_SESSION: `2f96bb3a-9e52-4b2a-80a0-b832afadc55f`

— Chuckles

#### chuckles — 2026-07-24T00:16:49.414Z
[datt-trace] **start** spawn=`a4ee6ed7` — **IN FLIGHT** spawning **Joan** role=validate `validate-plan` on `AST-979`
- parent: `AST-976`
- AGENT_SESSION: `2f96bb3a-9e52-4b2a-80a0-b832afadc55f`
- status: agent process starting now (waiting on subprocess)
- Active: set `Joan` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:13:32.375Z
[datt-trace] **start** spawn=`80567c9e` — **IN FLIGHT** spawning **Joan** role=validate `validate-plan` on `AST-979`
- parent: `AST-976`
- AGENT_SESSION: `2f96bb3a-9e52-4b2a-80a0-b832afadc55f`
- status: agent process starting now (waiting on subprocess)
- Active: set `Joan` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:13:15.522Z
[datt-trace] **end** spawn=`03d6301f` — **DONE** **Katherine** role=engineer `plan-child` on `AST-980`
- parent: `AST-976`
- exit: `0` · elapsed: `135s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:06:50.896Z
[datt-trace] **start** — spawning **Ada** role=engineer `plan-child` on `AST-979`
- parent: `AST-976`
- AGENT_SESSION: `a1dc1804-3291-4ddc-9c8c-27830427ae93`
- Active: set `Ada` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:03:48.346Z
[datt-trace] **start** — spawning **Ada** role=engineer `plan-child` on `AST-979`
- parent: `AST-976`
- AGENT_SESSION: `a1dc1804-3291-4ddc-9c8c-27830427ae93`
- Active: set `Ada` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-23T23:23:01.577Z
[check-linear] Todo — Proposed #2 already covers Execution History Level DEBUG; Linear children at dispatch

#### susan — 2026-07-23T23:18:30.150Z
Add a child ticket for adding DEBUG to the level list on executive history.

---

_Implementation detail may live in git history on `origin/dev`._
