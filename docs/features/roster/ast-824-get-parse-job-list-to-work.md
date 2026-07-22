# AST-824 — Get parse_job_list to work

<!-- linear-archive: AST-824 archived 2026-07-22 -->

## Linear archive (AST-824)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-824/get-parse-job-list-to-work  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

After the decomposed roster pipeline (**fetch_job_pages → select_job_page → parse_job_list**, AST-716 family), companies can reach **JOBLIST_IDENTIFIED** with multiple job titles from **select_job_page**, yet the separate **parse_job_list** dispatch sends the parsing agent a sliver of DOM — in Susan's repro, a single job anchor — instead of a careers-list fragment that contains all identified titles. That breaks container/tag discovery, wastes an LLM call, and blocks the company from **WATCH**. This epic restores the intended handoff: titles discovered during selection must survive in company data and must drive DOM trimming on the parse hop so **parse_job_list** receives token-sized but structurally complete listing HTML.

## Functional scope

* **Title persistence from select:** When **select_job_page** returns **JOBLIST_TITLES** on the decomposed **PJL_READY** path, every job title Grace reported is stored in company data in the field(s) the parse hop reads (today `job_titles`, plus any companion keys the parse step expects). Susan can inspect company data after **JOBLIST_IDENTIFIED** and see the same title list that appeared in the select response.
* **Title-driven DOM culling on parse:** When **parse_job_list** dispatch runs from **JOBLIST_IDENTIFIED** or **JOBLIST_IDENTIFIED_RETRY**, the Playwright DOM reload uses careers-list readiness (AST-689), then trims that DOM using the persisted title list so the content sent to **parse_job_list** is narrowed for tokens but still includes the listing region covering **all** saved titles — not one job link in isolation and not the full page when multiple distinct listings exist.
* **End-to-end decomposed success:** For a company that completed **select_job_page** with multiple titles on a real careers list page, a subsequent **parse_job_list** dispatch produces valid container/tag selectors, passes DOM validation, and transitions the company to **WATCH** with `job_site` set and `parse_instructions` persisted.
* **Failure semantics unchanged:** Missing URL, missing titles, empty DOM after reload, containers not found, invalid parse response, or validation failure still land in the existing retry/terminal states (**JOBLIST_IDENTIFIED_RETRY**, **COULD_NOT_PARSE_JOBLIST**, etc.) with `parse_job_list_notes` where applicable — not silent success.
* **Debug traceability (backend):** When `debug=True` on the parse dispatch path, logs show per company: how many titles were loaded from company data; DOM character count before and after title-driven culling; and an outcome line indicating whether culling produced a multi-title fragment or fell back. Detail lines use the AST-538 contract (index headers, `|` detail prefix).

## Boundaries

* Does **not** change **select_job_page** or **parse_job_list** agent prompt prose (Susan via Manage Tasks).
* Does **not** reintroduce the retired monolithic **find_job_page** dispatch or alter **fetch_job_pages** scrape batch behavior.
* Does **not** change careers-list readiness waits (AST-689) beyond using them as already wired on the parse DOM reload.
* Does **not** broaden scope to unrelated roster states (**vet_inflow_discovery**, prefilter, gaze JD scrape).
* Must **not** regress the **JOBS_FOUND** re-parse path that still chains select → parse in one batch — if the same title/cull bug exists there, fix must apply consistently without breaking that path's existing success cases.
* Config-driven values remain in config per Code Rules §2.1 — no new inline title/state lists.

## Acceptance criteria

1. Susan re-runs the [medicarerights.org](<http://medicarerights.org>) careers repro (**PJL_READY → select_job_page → JOBLIST_IDENTIFIED → parse_job_list**): after **JOBLIST_IDENTIFIED**, company data contains **both** job titles returned by select; Execution History for the **parse_job_list** hop shows live content that includes listing markup for **both** titles (not a lone `<a>` for the first job only).
2. On that repro, **parse_job_list** succeeds: company reaches **WATCH**, `job_site` is the selected careers URL, and `parse_instructions` (container, job_tag, container_index) is persisted and validates against the culled DOM.
3. A `debug=True` parse dispatch on the same repro logs title count, pre-cull and post-cull DOM sizes, and a clear cull outcome under the parse dispatch index header.
4. Existing component coverage for decomposed **select_job_page** / **parse_job_list** dispatch (AST-720/721) remains green; add or extend tests that lock title persistence and multi-title cull input when two titles are saved.
5. **JOBS_FOUND** re-parse smoke: a company with stored **job_site** that previously completed select→parse chaining still reaches **WATCH** when listings are present (no regression).

## Dependencies and blockers

* **AST-720** (decomposed **select_job_page**) and **AST-721** (decomposed **parse_job_list**) — shipped context; this ticket fixes a gap in their handoff, not a replacement.
* **AST-689** (careers-list scrape readiness) — parse DOM reload already depends on it.
* None blocking start.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-824 (parent) | ftr/AST-824-get-parse-job-list-to-work |
| AST-827 | sub/AST-824/AST-827-title-handoff-dom-cull |

**Epic worktree:** `astral-AST-824/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 2045ad3b-edc8-4c53-b4e6-1e89a594b6e8 |
| Betty | qa | abf19fdf-a244-4638-ba18-889c2a19e7b1 |
| Radia | review | 1e7ea413-3b2c-443e-a338-94bf9b8f9b12 |

---

## Original brief

When testing with [`https://www.medicarerights.org/careers`](<https://www.medicarerights.org/careers>) from `select_job_page`, there are two jobs listed (and included in the response from select_job_page), but apparently, when we rescraped for dom content and culled it down for the jobs, we ended up over-scraping and only sent this string as body dom content to provide the container and item elements.

```
<a href="https://www.medicarerights.org/careers/client-services-associate-bilingual-spanish-english">Client Services Associate: Bilingual Spanish and English</a>
```

This is obviously just the first hyperlink to the first job, not the body dom content for the careers page.

The logic, as I remember it, was that the titles were returned from select_job_page, and USED in trimming process with the dom content to narrow the amount of tokens sent for the parsing request.

It's possible with the refactor of the select-vs-parse, those text strings did not get incorporated in the "second hop" for parse_job_page.

Research the logic to confirm if this is missing.  This is not a one-off bug, this is probably a bug in the live data collection logic for parse_job_page and possible the data saving from select_job_page (which should add the example titles to company_data somewhere relevant)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
