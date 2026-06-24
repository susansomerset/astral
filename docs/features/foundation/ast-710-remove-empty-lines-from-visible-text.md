# AST-710 — Remove empty lines from visible text

<!-- linear-archive: AST-710 archived 2026-06-23 -->

## Linear archive (AST-710)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-710/remove-empty-lines-from-visible-text  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Scraped page visible text often arrives with long runs of blank lines between content blocks, inflating storage and polluting downstream consult and agent prompts. This feature adds a shared normalization step in the gazer scrape pipeline so persisted visible text keeps readable paragraph breaks without redundant empty rows.

## Functional scope

* Provide a reusable text normalizer that collapses consecutive blank lines to a single blank line while preserving non-empty line order and content.
* Treat lines that contain only whitespace (spaces, tabs) as blank for collapse purposes.
* Apply normalization on every gazer pipeline path that persists scraped visible page text before writing to company or job records — JD scrape batches and company homepage fetch batches.
* Run normalization on the full visible text blob immediately after scrape and before downstream trimming, classification, or save steps that consume that blob.

## Boundaries

* Does not change HTML extraction, browser scraping, or JD boilerplate prune rules.
* Does not normalize raw job listing fragments, DOM snapshots, nav link enumerations, or text assembled for agent prompts outside the gazer save path.
* Does not backfill or re-process text already stored in the database.
* Does not add UI or debug-logging requirements.
* May change JD classifier outcomes for edge cases where excessive blank lines contributed to whitespace-heavy captures; that is expected and acceptable.

## Acceptance criteria

1. Given visible text with three or more consecutive blank lines (or whitespace-only lines) between content, the normalizer produces at most one blank line between those blocks.
2. Non-empty lines appear in the same order with unchanged content after normalization.
3. Persisted job descriptions from JD scrape batches and homepage text from website fetch batches reflect normalized text, verifiable by inspecting saved records after a scrape run.
4. Gazer batch behavior (pass/fail transitions, empty-text rejection) remains correct — normalization does not turn genuinely empty scrapes into non-empty saves.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-710 (parent) | ftr/AST-710-remove-empty-lines-from-visible-text |
| AST-713 | sub/AST-710/AST-713-collapse-blank-lines-gazer |
| AST-714 | sub/AST-710/AST-714-backfill-collapse-blank-lines-company-job-data |
| AST-715 | sub/AST-710/AST-715-fetch-website-runtime-blank-line-collapse |

**Epic worktree:** `astral-AST-710/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 19fdfe99-65d7-46ae-9f6a-65f001679bbd |
| Betty | qa | 1f93edf3-071e-4b24-bc6e-5ff1a97dee10 |
| Radia | review | 4d9f92cc-ff86-461a-a821-1d3b59baf9d7 |

---

## Original brief

We are doing a lot of screen scraping that includes a lot of empty whitespace between text content.  Please use the [formatting.py](<http://formatting.py>) file to strip excessive lines.  There should be only 1 empty row where there might have been more.

When the function is ready in formatting, add it to all the gaze functions before submitting visible text to be saved.

### Comments

#### chuckles — 2026-06-17T20:55:10.814Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-715** | fetch_website saves skip blank-line collapse at runtime (Remove empty lines from visible text) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-715** — _fetch_website saves skip blank-line collapse at runtime (Remove empty lines from visible text)_
- **Issue reported:** After **AST-713** landed, Susan ran `fetch_website_batch` (and related fetch-website flows) from current code. Newly saved `company_data.homepage_text` still contained consecutive blank lines that `backfill_collapse_blank_lines.py` subsequently removed — runtime gazer normalizati
- **Should now:** Every gazer path that persists scraped homepage visible text applies `collapse_consecutive_blank_lines` immediately after scrape and **before** save, so a fresh `fetch_website` run writes already-normalized text (at most one blank line between content blocks). No backfill needed 
- **Quick check (this fix only):**
  1. Pick a company whose homepage scrape produces multiple consecutive blank lines in raw visible text.
  2. Run `fetch_website_batch` from the deployed/local app code (not the backfill script).
  3. Inspect saved `company_data.homepage_text` — observe multiple consecutive blank lines remain.
  4. Run `scripts/migrations/backfill_collapse_blank_lines.py --company <short_name> --dry-run` — script reports the same row would change.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-17T20:44:33.543Z
It appears that this is not running at runtime.  I just ran a bunch of fetch_website functions from this version of the code, and it still left blanks behind that the backfill script cleaned up.

#### chuckles — 2026-06-16T20:59:37.205Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-714** | backfill script to collapse blank lines in company_data and job_data (Remove empty lines from visible text) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-714** — _backfill script to collapse blank lines in company_data and job_data (Remove empty lines from visible text)_
- **Issue reported:** Existing rows in `company_data` and `job_data` still contain runs of consecutive blank lines from scrapes saved before **AST-713** landed. New gazer saves are normalized, but Susan has no local script to clean already-persisted text blobs.
- **Should now:** A runnable local migration/backfill script applies `collapse_consecutive_blank_lines` to persisted visible-text fields in `company_data` and `job_data` (e.g. homepage text and job description keys), updates only rows that change, supports dry-run, and can target one company/job o
- **Quick check (this fix only):**
  1. Inspect a company or job record scraped before this epic — note multiple consecutive blank lines in saved visible text.
  2. Run the backfill script locally with `--dry-run` — script reports rows that would change.
  3. Run without dry-run — re-inspect the same record; at most one blank line remains between content blocks.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-16T20:51:29.002Z
@chuckles Can you also create a backfill script to remove the empty lines in existing company_data and job_data content? I want to run it locally, but staging shouldn't be necessary.

---

_Implementation detail may live in git history on `origin/dev`._
