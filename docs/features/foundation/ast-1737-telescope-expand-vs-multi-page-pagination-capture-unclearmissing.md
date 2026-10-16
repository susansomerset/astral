# AST-1737 — Telescope expand vs multi-page pagination capture unclear/missing

<!-- linear-archive: AST-1737 archived 2026-10-02 -->

## Linear archive (AST-1737)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1737/telescope-expand-vs-multi-page-pagination-capture-unclearmissing  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] Is expand the same as pagination? Did we lose the pagination scrape feature with this migration?  If I go to a url and I have 1500 results across 15 screens, will telescope capture all 15 sets of 100?

## As-is

Unclear whether expand equals pagination; multi-screen result sets (e.g. 15×100) may not all be captured after the playwright→Telescope migration.

## To-be

Expand (or an explicit pagination path) captures all paginated result screens for a URL, or the contract documents that expand is load-more only and pagination must be requested separately.

## Proposed change

- [X] `service/telescope/app.py` — Field description on `expand` (text + html): scroll + Load More/Show More; not numbered/Next pagination
- [X] `service/telescope/interact.py` — `expand_page` docstring matches that contract (no logic change)
- [X] `src/ui/frontend/src/pages/AdminTelescope.tsx` — expand label: scroll / Load More — not numbered pages

## Suggested engineer

Ada Lovelace

## Radia review-fix (AST-1737)

Overall: CLEAN. Expand contract documented (scroll/Load More ≠ numbered pages). Clean-review → User Testing.

### Comments

#### radia — 2026-09-21T00:39:29.736Z
[code-rubric] PROCEED (Commit: bb58b9fb) Expand contract documented

#### joan — 2026-09-21T00:29:00.186Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T00:28:26.141Z
[board-betty] TESTS: OK

#### ada — 2026-09-21T00:27:24.521Z
`origin/sub/AST-1721/AST-1737-telescope-expand-vs-multi-page-pagination` @ `41527552190f2ce0bcce48060caa524950847ba7` · expand = load-more only

---

_Implementation detail may live in git history on `origin/dev`._
