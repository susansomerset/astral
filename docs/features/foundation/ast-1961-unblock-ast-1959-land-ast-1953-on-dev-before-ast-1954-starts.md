# AST-1961 — Unblock AST-1959: land AST-1953 on dev before AST-1954 starts

<!-- linear-archive: AST-1961 archived 2026-10-08 -->

## Linear archive (AST-1961)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1961/unblock-ast-1959-land-ast-1953-on-dev-before-ast-1954-starts  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1954

### Description

**What's needed:** AST-1953 (agent settings on the wire) landed on `origin/dev`, meaning your PR Ready followed by `finish-up`. Then move this ticket to **Done**.

**Why:** AST-1954's children build directly on AST-1953's code: the settings resolver and the provider object `llm_compat` merges, plus `config.py`, `agent.py` and `database.py`. AST-1954's `ftr` and `sub/*` branches are seeded from `dev`, so until AST-1953 is on `dev` the engineers would plan and build against the old code. User Testing on AST-1953 isn't enough, because that work is still only on `ftr/AST-1953-agent-settings`.

**Blocks:** AST-1959 and AST-1960 (children of AST-1954), and the parent AST-1954.

Nothing else is needed from you: no file and no answer. Neither the children nor the parent is assigned to you. AST-1959 stays with Hedy, AST-1960 with Katherine, and AST-1954 with Chuckles. Once this is **Done**, the next watcher poll resumes AST-1954 and the children start planning.

### Comments

#### chuckles — 2026-10-04T00:21:49.833Z
[check-linear] answered — confirmed: AST-1953 is Done and its code is on `origin/dev` (tip `66d98fa7b`). Gate met, so I moved this to Done. AST-1954 resumes on the next watcher poll.

#### susan — 2026-10-04T00:20:55.239Z
@chuckles the code for 1953 is already on the dev branch.

#### chuckles — 2026-10-04T00:18:05.937Z
Holding per #1. Reopened so the watcher keeps AST-1954 parked. Move this to Done once AST-1953 has landed on `dev` (after finish-up). Nothing else is needed until then.

#### susan — 2026-10-04T00:17:08.623Z
Wait, please. (#1)

#### chuckles — 2026-10-04T00:15:33.264Z
@susan I reopened this gate. It was closed with "Option 1 — validator exception, live on main @ 63934dc", which reads like the answer to AST-1962, the AST-1958 validator gate (that one is Done too). This gate's condition isn't met yet: AST-1953 is at User Testing and is not on `origin/dev` (`dev` is still at `5d4d8e2f2`). AST-1954's branches are seeded from `dev`, so if I start now, Hedy and Katherine plan and build against the code from before AST-1953.

How should AST-1954 proceed? Choose one:

1. **Wait (recommended):** move this to Done after AST-1953 lands on `dev` (PR Ready, then finish-up).
2. **Start now on AST-1953's branch:** I merge `origin/ftr/AST-1953-agent-settings` into `ftr/AST-1954-host-probe` so the children build on AST-1953's code. If AST-1953 changes during UAT, `ftr/AST-1954` needs that merge again.
3. **Start now on `dev` as-is:** the children build against the old code. Expect rework and conflicts when AST-1953 lands.

Reply with the number and move this to Done.

#### susan — 2026-10-04T00:13:23.805Z
Option 1 — validator exception, live on main @ 63934dc.

---

_Implementation detail may live in git history on `origin/dev`._
