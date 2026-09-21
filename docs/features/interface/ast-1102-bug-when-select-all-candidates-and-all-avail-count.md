# AST-1102 — Bug when select All candidates and All avail count

<!-- linear-archive: AST-1102 archived 2026-08-07 -->

## Linear archive (AST-1102)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1102/bug-when-select-all-candidates-and-all-avail-count  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

On Admin → Scheduled Actions, widening the list to **Candidate: All** and **Avail: All** tears the SPA down to a blank black page (no header, no nav — empty `#root`). Operators cannot inspect the full dispatch-task set when those filters are open. This epic restores a usable page for that filter combination without changing what Avail or Candidate mean.

## Functional scope

1. **Survive Candidate All + Avail All.** Choosing Candidate: All together with Avail: All on Admin → Scheduled Actions keeps app chrome and the Scheduled Actions screen mounted — no blank/black viewport.
2. **Honor Avail All and Candidate All semantics.** With those two controls at All (and no other narrowing filters), rows that Candidate or Avail > 0 would hide remain eligible to show, including zero/empty Avail rows, matching the existing Avail All behavior from AST-887 / AST-888.
3. **Preserve defaults and other filters.** Default landing (Avail > 0 engaged), single-candidate views, and AND intersection with the rest of the filter bar continue to work as today.
4. **No total SPA wipe.** That filter combination must not leave only an empty document shell; the operator always sees header/nav plus either the list, the existing empty-filter status, or a clear on-page failure — never a featureless black screen.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (frontend bug fix on the existing Scheduled Actions client-side filter/list surface from AST-751 / AST-887 / AST-888; not a new admin HTTP surface, so `pattern.ui.admin-endpoint` does not apply unless root cause proves an API contract change).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` (touch only what the crash requires); `astral.standards.dry-and-focused-functions` (keep filter/render helpers focused); `astral.ui.frontend-file-placement` and `astral.ui.naming-conventions` (UI file/layout contract); `astral.layers.ui-config-driven-business-logic` (do not bury new business rules in React if any logic must move).

## Boundaries

* Does not change how Available is calculated, claimed, or dispatched.
* Does not change Avail column formatting (zero/empty still show as today).
* Does not add new Avail modes, redesign the filter bar, or alter Run / Stop / AUTO / edit-modal / Manage Tasks behavior.
* Does not change Recommended Jobs or other sectioned screens.
* Does not open a separate global React error-boundary epic; any recovery UI is only as needed to stop this blank-page failure on Scheduled Actions.
* Frontend-focused unless investigation shows a server fault as root cause; no new backend debug-logging requirements by default.
* Must not break AST-887 / AST-888 Avail filter and default-landing semantics.

## Acceptance criteria

1. On Admin → Scheduled Actions, set **Candidate** to All and **Avail** to All: header, nav, and Scheduled Actions content remain visible (not a blank black page).
2. With that combination and no other narrowing filters, rows with zero/empty Avail that exist in the loaded data remain visible (Avail All semantics).
3. After reproducing the former failure path, the document is not left as an empty `#root` shell with no app UI.
4. Fresh load still defaults Avail to > 0 and remains usable; selecting a specific candidate remains usable.
5. Changing Candidate and Avail among All / specific / > 0 does not blank the page for any of those combinations.

## Dependencies and blockers

none. (Avail filter and default landing from AST-885 / AST-887 / AST-888 already shipped.)

## Open questions

none.

## Proposed child tickets

#### 1: **Fix Scheduled Actions blank page on Candidate All + Avail All - Katherine**

Reproduce the blank-page failure when Candidate and Avail are both All, fix the render/runtime fault so chrome and list (or empty-filter status) stay up, and verify defaults plus other filter combos still behave. Does **not** own Avail calculation, dispatch, or filter-bar redesign.

**Citations:** `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.layers.ui-config-driven-business-logic`; patterns: `no established pattern applies`.

**Monolith check:** Functional scope has 4 capabilities and 1 proposed child — intentional: one inseparable vertical slice (reproduce + fix + verify filter survival) on a single admin screen.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1102 (parent) | ftr/AST-1102-bug-when-select-all-candidates-and-all-avail-count |
| AST-1104 | sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all |

**Epic worktree:** `astral-AST-1102/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/c6c7140e3f8d56a234588dc84b5fe0b6/be5940a4-3047-40ab-a8ac-cf4df9f4bd23/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/db7e6409-36d3-40d4-83cb-ca0ed4ede5f0/store.db` |
| Radia | review | `/home/susan/.cursor/chats/c6c7140e3f8d56a234588dc84b5fe0b6/7238e903-f136-4f63-8628-fff9047e09b3/store.db` |

---

## Original brief

webpage goes blank (black), no header, no nav, just black.

View page source gives me this:

```

<!doctype html>
<html lang="en">
  <head>
    <script type="module">import { injectIntoGlobalHook } from "/@react-refresh";
injectIntoGlobalHook(window);
window.$RefreshReg$ = () => {};
window.$RefreshSig$ = () => (type) => type;</script>

    <script type="module" src="/@vite/client"></script>

    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/astral_favicon.svg" />
    <link rel="icon" type="image/png" href="/astral_favicon.png" />
    <link rel="apple-touch-icon" href="/astral_favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <title>Astral</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx?t=1785472660683"></script>
  </body>
</html>
```

### Comments

#### chuckles — 2026-07-31T06:14:52.097Z
[refresh-ftr] blocked: merge origin/dev into origin/ftr/AST-1102-bug-when-select-all-candidates-and-all-avail-count

**@Betty White** (test tree):
- `tests/component/core/test_agent.py`

Resolve on astral-tests / reconcile onto `origin/ftr/AST-1102-bug-when-select-all-candidates-and-all-avail-count`, then Chuckles retries refresh-ftr.

— Chuckles

#### chuckles — 2026-07-31T04:57:29.842Z
[thread-missing] Team threads for Katherine / Betty / Radia were missing on this host; reminted and persisted via populate-team.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
