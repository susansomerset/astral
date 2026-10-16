# AST-2080 — Unblock AST-2078: pick (a) drop all gunicorn access lines or (b) drop only polling paths

<!-- linear-archive: AST-2080 archived 2026-10-16 -->

## Linear archive (AST-2080)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2080/unblock-ast-2078-pick-a-drop-all-gunicorn-access-lines-or-b-drop-only  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** unassigned  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2074

### Description

## What's needed

Pick one option for [AST-2078](https://linear.app/astralcareermatch/issue/AST-2078) (the fix for [AST-2074](https://linear.app/astralcareermatch/issue/AST-2074), gunicorn polling logs on prod). Ada's plan is published; make-fix waits on this choice.

* **(b) — recommended by Ada:** drop only a config-listed set of polling paths (starting with `/api/deploy_status`) from `gunicorn.access`; every other request line still logs. Fully inside the ticket's current scope.
* **(a):** drop every `gunicorn.access` line on prod. About the same amount of code, but Chuckles amends the ticket scope first.

Both are a filter in `src/utils/logging.py` driven by `RAILWAY_CONFIG`. Joan: canon OK for either. Betty: tests needed either way ([AST-2079](https://linear.app/astralcareermatch/issue/AST-2079), shape depends on your pick).

## Why not just turn access logging off in the launcher

Ada found that prod's INFO app logs only appear *because of* the same Railway gunicorn log config that turns on access logging (Python's root logger defaults to WARNING and the guard in `logging.py` that raises it to INFO never runs under gunicorn). Removing that env config would silence all `logger.info` lines on prod. So the plan leaves the Railway env alone. That root-level issue is a separate latent bug — worth its own ticket; it's not fixed here.

## How to answer

Reply here with **(a)** or **(b)** and move this ticket to **Done**. Neither AST-2074 nor AST-2078 is assigned to you — the agents pick it up when this is Done.

Full plan: `docs/features/foundation/ast-1777-logging-levels.md` § "Bug: AST-2078" on `sub/AST-2074/AST-2078-gunicorn-polling-logs`.

### Comments

#### susan — 2026-10-09T01:02:51.271Z
B please.

#### chuckles — 2026-10-09T00:57:21.908Z
Closed with no (a)/(b) reply — proceeding with **(b)** (Ada's recommendation: drop only config-listed polling paths, starting with `/api/deploy_status`). Reopen and reply (a) if that's wrong; nothing lands on dev before your UAT.

---

_Implementation detail may live in git history on `origin/dev`._
