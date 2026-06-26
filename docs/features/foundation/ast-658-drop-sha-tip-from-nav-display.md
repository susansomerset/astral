# AST-658 — Drop SHA tip from nav display

<!-- linear-archive: AST-658 archived 2026-06-23 -->

## Linear archive (AST-658)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-658/drop-sha-tip-from-nav-display  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

AST-640 shipped an admin-only nav footer showing deploy environment, git commit tip, and server uptime. Railway deploy images do not include a `.git` tree, so the footer often shows a meaningless commit value (e.g. `unknown`) instead of a real deploy tip. This follow-up simplifies the footer to the signals that actually work on Railway: which environment the server is running and how long that process has been up. Admins still get deploy context without clutter or false precision.

## Functional scope

1. **Remove commit tip from admin nav footer** — The read-only deploy footer at the bottom of the left sidebar no longer displays a git short hash, commit message tooltip, or placeholder when git is unavailable.
2. **Keep environment label** — When the server has a configured deploy environment, the footer still shows that label (`local`, `test`, `staging`, or `production` per existing rules).
3. **Keep server uptime** — The footer still shows process uptime in the existing compact format (`<1m`, `5m`, `1h15m`, `3d22h07m`, etc.).
4. **Admin-only, read-only** — Same visibility and behavior as AST-640: administrators only; no links, buttons, or copy actions.
5. **Uniform display** — Commit tip is omitted on all deploy targets (Railway and local), not only when git resolution fails.

## Boundaries

* **Not a replacement for deploy verification** — Does not add Railway links, PR numbers, or build IDs elsewhere in the UI.
* **Not a health dashboard** — Does not change Performance Monitor, scheduler status, or `/health`.
* **Not for non-admin users** — Footer remains hidden when the user is not an administrator.
* **No backend debug logging** — UI readout only; no `debug=` contract changes.
* **Does not block or revert AST-640** — This refines the shipped footer; it does not reopen the original epic scope.

## Acceptance criteria

1. Signed in as admin on Railway staging or production → nav footer shows deploy environment (when configured) and uptime only; no commit hash, tooltip, or `unknown` commit text.
2. Signed in as admin on local dev → footer shows environment (when configured) and uptime only; no commit hash or tooltip.
3. Signed in as non-admin on the same deploy → nav footer absent; layout unchanged.
4. Uptime strings still follow AST-640 format rules (`<1m` under one minute; minute-only under one hour; `XhYm` under one day; `XdYhZZm` at one day+).
5. After a server restart or redeploy, displayed uptime reflects the new process within one normal API refresh cycle.

## Dependencies and blockers

* **Related:** AST-640 / AST-646 (admin deploy status footer and API — must exist on the branch under test).
* **Blocking:** none.

## Open questions

(none)

---

## Original brief

The tip is not available on Railway, so we might as well remove it from there, just show the deploy environment string and the uptime.

### Comments

#### chuckles — 2026-06-15T18:10:23.452Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-658 (parent) | ftr/AST-658-drop-sha-tip-from-nav-display |
| AST-679 | sub/AST-658/AST-679-remove-commit-tip-from-admin-deploy-footer |

**Epic worktree:** `astral-AST-658/` — one active sub checked out at a time.

**Parent:** AST-658

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
