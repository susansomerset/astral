# AST-864 — Foreign key search term to company

<!-- linear-archive: AST-864 archived 2026-07-29 -->

## Linear archive (AST-864)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-864/foreign-key-search-term-to-company  
**Status at archive:** Archive  
**Project:** Astral Discovery  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Company discovery from Google CSE currently records hits without retaining which search term produced them. Without that link, Susan cannot judge term quality (including dud/ignore outcomes) or later attach real foreign-key metrics. This epic establishes the originating search term on each discovered company row so results stay attributable end to end.

## Functional scope

* When Google CSE discovery creates a company from a hit, persist the originating search-term string on that company at record time.
* Carry the same originating search-term string through any ingest path that creates a company from a Google search hit so the value is not dropped between search and save.
* Keep the originating search term on the company regardless of later vet or prefilter outcomes that ignore, reject, or otherwise discard the company as a prospect — ignored results still retain the term that found them.
* Expose the stored originating search term wherever company data is already readable for inspection during UAT (admin/data surfaces that already show the company), without building new search-term management UI.
* When discovery/ingest runs with debug enabled, include the originating search term in per-company working detail for newly recorded companies (found + recorded), following the backend debug contract.

## Boundaries

* Does not implement a true foreign key from company to `company_search_terms` (or search-term row ids). Title aspiration stays deferred; this epic is the interim denormalized string column Susan specified.
* Does not add search-term child-record UI, term metrics dashboards, or term-quality reporting — that belongs with sibling AST-865 (and later work).
* Does not change CSE query behavior, staleness/`freq_hrs` eligibility, dedupe rules, vet pass/fail transitions, or company state machines except to stamp and retain the originating term.
* Does not backfill historical company rows that were discovered before this ships.
* Does not break existing company discovery, ingest, or vet flows for candidates already using table-backed search terms.
* Schema change is expected; any new company column must stay within the data-layer table inventory rules (ASTRAL_CODE_RULES §1.1).

## Acceptance criteria

1. A company newly recorded from a Google CSE discovery hit has its originating search-term string stored on the company row.
2. A company that is later ignored/rejected/vet-failed (or otherwise discarded as a prospect) still retains that same originating search-term string.
3. Running discovery for a known search term and inspecting a resulting company (including an ignored outcome) shows that exact term as the stored origin.
4. With debug enabled on the discovery/ingest path, each newly recorded company's debug working detail includes the originating search term that was stored.
5. Companies created outside Google CSE discovery are unchanged (no false originating term required).
6. Existing discovery eligibility, CSE search, URL/slug dedupe, and vet transitions continue to behave as they do today aside from the new stored term.

## Dependencies and blockers

none.

Related (not blocking): AST-865 — UI to manage search terms as child records; shares the longer-term FK/metrics intent but is out of scope here.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-864 (parent) | ftr/AST-864-foreign-key-search-term-to-company |
| AST-877 | sub/AST-864/AST-877-originating-search-term |

**Epic worktree:** `astral-AST-864/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 3fd45fe6-958c-4aec-a475-059532b93b60 |
| Betty | qa | c076b0db-dafe-4a1a-983b-a65664ad1676 |
| Radia | review | ac1b10e0-507d-433d-9a1b-604e2233b2c5 |

---

## Original brief

We need to save the I'd for the search terms to the results, including ignores.

For now just add a column to company table with the original search terms that found the company, and passing the string through to ingest the record from the Google search.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
