# AST-1473 — Unblock AST-1469: LINEAR_KEY_JOAN missing on chuckles host

<!-- linear-archive: AST-1473 archived 2026-09-09 -->

## Linear archive (AST-1473)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1473/unblock-ast-1469-linear-key-joan-missing-on-chuckles-host  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1446; blocks: AST-1479; blocks: AST-1464; blocks: AST-1457

### Description

## Need

`LINEAR_KEY_JOAN` is unset on the chuckles host (`~/.config/team-chuckles/env` has every other persona key; Joan is missing). Sub-chuck cannot post Joan validate-plan §3i upshots (`linear_proxy.py --as joan save-comment`).

## Why it blocks

[AST-1469](https://linear.app/astralcareermatch/issue/AST-1469/job-source-tracker-meteorite-save-meteorite-component) is **Plan Ready** (Ada finished `plan-child`). Next stage is Joan `validate-plan`. Spawn can run in ASK mode, but Chuckles cannot write Joan's upshot or advance status without the key.

## What to do

1. Create/export Joan Clarke's Linear API key as `LINEAR_KEY_JOAN` on this host (same pattern as `LINEAR_KEY_RADIA`).
2. Add it to `~/.config/team-chuckles/env` and re-source / restart wake.
3. Move **this gate to Done** when the key works (`linear_proxy.py --as joan get-issue AST-1469 --brief`).

Neither the child nor the parent is assigned to you — reply here or attach the key value out-of-band; agents will place it. Child stays Ada / Plan Ready; parent stays Chuckles / In Progress.

## Also blocked (same host key)

* [AST-1479](https://linear.app/astralcareermatch/issue/AST-1479/applied-jobs-list-home-add-means-to-mark-job-as-applied-for) (Astral Tracker / [AST-1464](https://linear.app/astralcareermatch/issue/AST-1464/add-means-to-mark-job-as-applied-for)) — Joan validate-plan finished APPROVED/PROCEED; `docs(AST-1479): Joan validate` is on `origin/sub/AST-1464/AST-1479-applied-jobs-list-home`. Stuck only on `linear_proxy --as joan save-comment` for the §3i upshot, then Plan Approved + Ada build.

### Comments

#### chuckles — 2026-08-25T00:14:08.867Z
Also blocked (same host key): **AST-1454** (Astral Interface / AST-1446) — Joan validate-plan finished APPROVED/PROCEED; `docs(AST-1454): Joan validate` is on `origin/sub/AST-1446/AST-1454-job-detail-skipped-field-editors`. Stuck only on `linear_proxy --as joan save-comment` for the §3i upshot, then Plan Approved + Katherine build.

---

_Implementation detail may live in git history on `origin/dev`._
