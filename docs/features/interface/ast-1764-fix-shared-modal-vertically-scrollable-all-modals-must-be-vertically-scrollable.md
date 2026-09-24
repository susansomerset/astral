# AST-1764 — fix: shared Modal vertically scrollable (All modals must be vertically scrollable)

<!-- linear-archive: AST-1764 archived 2026-09-24 -->

## Linear archive (AST-1764)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1764/fix-shared-modal-vertically-scrollable-all-modals-must-be-vertically  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1754 — All modals must be vertically scrollable  
**Blocked by / blocks / related:** parent: AST-1754

### Description

## What this implements

Make the shared admin `Modal` vertically scrollable by default so tall content is reachable in every modal (especially `size="wide"`), without breaking nested scroll owners like SideTabPanel. Approved ancestor: AST-1511 (archived — local wrapper only; this ticket lifts the contract into the shell).

## Scope

## Component scope

* `src/ui/frontend/src/components/Modal.tsx` — modified: shared modal shell is where “all modals scroll” has to land if CSS alone cannot cover wide + nested-scroll layouts.
* `src/ui/frontend/src/App.css` — modified: `.modal-body` / `.modal-card--wide .modal-body` (and related wide-modal rules) are the rules that currently clip tall content or force per-screen wrappers.

## Technical scope

* `Modal.tsx` — modified component markup/props only as needed so the shell exposes a reliable vertical scroll region (or a size-aware body class) for tall children; exact naming is plan-fix’s call.
* `App.css` — modified CSS rules for default and wide modal body overflow/flex so content scrolls when the shell owns scroll, while layouts that nest their own scroll region still fill height correctly.

## Acceptance criteria

- [X] Tall content in a default `Modal` scrolls inside the body; header/footer stay put.
- [X] Tall content in a `size="wide"` `Modal` that places children directly in the body (no custom inner scroll wrapper) is reachable via vertical scroll.
- [X] Wide modals that nest their own scroll region (e.g. SideTabPanel) still fill height and scroll correctly — no regression from lifting the shell contract.
- [X] New modals inherit scroll without inventing a per-screen wrapper.

## Boundaries

Does not rewrite individual feature screens unless a call site fights the new shell contract. Does not resurrect AST-1511’s ftr. Scope is explicit above — plan-fix plans against it.

## Notes for planning

Parent AST-1754 Description has As-is / To-be / Proposed steps. Seed context from docs/features/agent/ast-1511-show-differences-modal-does-not-scroll.md (and related AST-1506 root-cause notes on wide `overflow: hidden`).

## Git branch (authoritative)

Parent `ftr/AST-1754-all-modals-must-be-vertically-scrollable`. Child ref recorded in epic registry at bug-fix dispatch.

## Board — Joan (fix-board)

**Question:** Does this fix require touching canon?

**Answer:** No. The plan-fix patch only adjusts shared shell CSS (`App.css` wide-body overflow contract, optional `:has()` containment) and, if needed, `Modal.tsx` markup/classes — no feature-screen rewrites. Parent AST-1754 carries no frozen Canon Scope. The active roster (21 directives via `canon_clerk index`) has nothing governing modal scroll, overflow, or `Modal` shell behavior; the only UI-adjacent active pattern (`patt.artifact.ui-consistency`) covers artifact `body_shape` editors, not modal layout. Plan § What must still hold preserves dirty-close / footer / stacked behavior — no conflict with draft `patt.ui.dirty-leave-save-then-navigate` (“do not change Modal discard-on-close”). Same class as AST-1511, which got `[board-joan] CANON: OK`.

Verdict: **CANON: OK**

## Review — Radia (review-fix)

\[code-rubric\]
**Ticket:** AST-1764
**Publish ref:** `8a8510f4984116f6957cafdc8db3ed3be9be1d1a` (`origin/sub/AST-1754/AST-1764-fix-shared-modal-vertical-scroll`)
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Overall:** CLEAN

## Canon scores

(frozen Canon Scope empty — parent AST-1754 carries no canon list; fix-board Joan CANON: OK; no directives to score)

## Column diff vs plan stage

no plan-stage scores attached

## Frame diff

(none)

## Fix-specific checks

**\[bug-repro\]** not applicable — no qa-fix spawn on this ticket; board TESTS: REVISE deferred to sibling AST-1767 (per spawn prompt).

**## What must still hold — OK**

| Item | Verdict |
| -- | -- |
| Default `Modal` tall body scroll; header/footer fixed | OK — `.modal-body` rules untouched for non-wide cards |
| Wide `Modal` direct children reachable via vertical scroll | OK — `.modal-card--wide .modal-body` now `min-height: 0` + `overflow-y: auto` (was `overflow: hidden`) |
| Nested scroll owners (SideTabPanel, email HTML, batch wrapper) fill height and scroll internally | OK on static review — existing `height: 100%` / inner `overflow: auto` patterns preserved; plan contingency `:has()` correctly not preempted |
| New modals inherit shell scroll without per-screen wrapper | OK — global CSS contract change |
| Show Differences (AST-1511) fully reviewable | OK — local wrapper remains; shell scroll adds reachability (nested scroll acceptable per plan) |
| Dirty-close / footer / `showFooter` / `stacked` unchanged | OK — `Modal.tsx` not in diff |

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

* **Stale call-site comment** — `RepoJsonDivergenceBanner.tsx` still says wide modal-body is `overflow:hidden`; harmless, out of plan scope, but misleading for the next engineer.
* **Test gap acknowledged** — Betty `[board-betty] TESTS: REVISE` on AST-1764; sibling AST-1767 owns shared `test_Modal` wide-shell coverage. Not a product fix-now on this tip.
* **UAT spot-check** — plan step 4 (SideTabPanel, Read email HTML, Recommended report) still the right manual gate; CSS-only primary path did not add `:has()` containment rules, which is correct per plan unless a regression surfaces.

## What's solid

* Diff is minimal and matches plan-fix § Proposed change (1): `App.css` wide-body block + batch-wrapper comment only; no feature-screen churn.
* `min-height: 0` on the wide flex child is the right flexbox scroll fix alongside `overflow-y: auto`.
* Scope stays inside the two-file boundary; `Modal.tsx` contingency correctly skipped when CSS suffices.

## Chuckles branching

| Gate | Parent shape | Next action |
| -- | -- | -- |
| **PROCEED** (C7 complete) | **Orphaned** (per spawn) | → **Review Posted** → clean-review shortcut → **User Testing**; skip `resolve-child`; when UT clears, merge `sub/AST-1754/AST-1764-fix-shared-modal-vertical-scroll` **straight to** `origin/dev` (no `merge-child` / `prep-uat`) |

context_tokens≈14000

```
```

\[code-rubric\] PROCEED (Commit: 8a8510f4) wide shell scroll fixed

```
```

### Comments

#### radia — 2026-09-22T00:10:18.776Z
[code-rubric] PROCEED (Commit: 8a8510f4) wide shell scroll fixed — CLEAN; no fix-now. What-must-still-hold OK. Test gap remains on sibling AST-1767.

#### joan — 2026-09-22T00:05:38.951Z
[board-joan] CANON: OK — shared Modal/App.css shell scroll only; no active canon on modal overflow; same class as AST-1511.

#### joan — 2026-09-22T00:04:35.439Z
[board-joan]  CANON: OK

context_tokens≈12000

#### betty — 2026-09-22T00:04:26.421Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § Modal / test_Modal.test.tsx — missing shared wide Modal shell scroll for tall direct children (AST-1511 only covers Show Differences call-site wrapper)

#### katherine — 2026-09-22T00:03:01.730Z
`origin/sub/AST-1754/AST-1764-fix-shared-modal-vertical-scroll` @ `a44364d659db6588a3f38bde24d84fba46a9fa78` · shell scroll contract

---

_Implementation detail may live in git history on `origin/dev`._
