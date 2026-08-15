# AST-1262 — Decide AST-1255: approve @stytch/vanilla-js ^5.45.1 pin

<!-- linear-archive: AST-1262 archived 2026-08-14 -->

## Linear archive (AST-1262)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1262/decide-ast-1255-approve-stytchvanilla-js-5451-pin  
**Status at archive:** Archive  
**Project:** Astral Surfer  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1255; blocks: AST-1170

### Description

## What Susan must do

Decide the Plan Discuss escalate on [AST-1255](https://linear.app/astralcareermatch/issue/AST-1255/extension-auth-session-path-extension-shell-manifest-v3-scaffold-and) (extension auth session path).

Joan’s escalate finding: plan is architecturally sound; one wrong dep pin remains — `@stytch/vanilla-js` has no `19.x` (highest is `6.x`; web app resolves `5.45.1` via `@stytch/react` peer `^5.0.0`).

### Recommended action (least ceremony)

1. On this Task, comment **Approve: pin** `"@stytch/vanilla-js": "^5.45.1"` (do not take `latest` / 6.x).
2. Mark this Task **Done**.

Hedy then patches those two plan lines and proceeds to Plan Approved without another full Joan pass (unless you prefer Joan re-validate the two-line edit — say so in the comment).

### Alternative

If you disagree with the pin, write the version you want on this Task before Done.

— Joan

### Comments

#### susan — 2026-08-07T18:25:04.676Z
**Approve: pin** `"@stytch/vanilla-js": "^5.45.1"` (do not take `latest` / 6.x)

#### joan — 2026-08-07T18:17:54.358Z
Susan: one-line decision on this Task — approve `^5.45.1` pin (recommended) or name your version — then mark Done. Child **AST-1255** is back on Hedy; parent **AST-1170** on Chuckles.

— Joan
context_tokens≈22000

---

_Implementation detail may live in git history on `origin/dev`._
