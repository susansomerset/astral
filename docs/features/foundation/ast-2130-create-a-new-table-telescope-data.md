# AST-2130 — Create a new table telescope_data

<!-- linear-archive: AST-2130 archived 2026-10-16 -->

## Linear archive (AST-2130)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2130/create-a-new-table-telescope-data  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Today every Telescope scrape we keep lands inside an entity JSON blob — company page text and links in `company.company_data`, the scraped job description in `job.job_data`. Those blobs grow without bound, get loaded whole on every read, and the only way to reclaim space is to surgically rewrite them. This epic gives scraped content its own `telescope_data` table in `astral.db`: one record per piece of content, typed (`VISIBLE_TEXT`, `PAGE_LINKS`, room for more later), owned by gazer (core) through `database.py`, which hands back the new row's id for the caller to keep in the entity record. Every pipeline scrape is kept — bad captures included, for debugging — and culled later. Outcome Susan expects: entity blobs carry small row ids and human/agent-authored text, not raw page text; scrape volume can be measured and trimmed on one table with plain SQL; nothing downstream reads differently.

## Functional scope

1. **Telescope content table.** A new `telescope_data` table in `astral.db` stores scraped content as separate records: a row id (uuid), the `candidate_id` of the entity it was scraped for, the source URL, a free-text content-type key, the content (compressed at rest like `agent_data.block_data`), and a capture timestamp. Type keys in use: `VISIBLE_TEXT`, `PAGE_LINKS`. `DOM_CONTENT` stays a reserved name only — no DOM is stored (today's architecture keeps DOM in memory for the run). The type key is **not** validated in code, so binary / JSON types can be added later without a code gate.
2. **Gazer owns the table.** `src/core/gazer.py` is the only module that writes or reads `telescope_data` (through `database.py`). Gazer provides the scrape-and-keep calls (visible text, link lists) and the resolve-by-id read; other core modules and the admin preview go through gazer. The Telescope client (`src/external/telescope.py`) stays I/O-only and unchanged. No new wrapper module.
3. **Persist everything.** Every pipeline scrape that returns visible text or a link list is stored, whether or not the caller ends up using it (bot walls, failed classifications, too-short JDs included). The admin Telescope test page is not a pipeline scrape and is not stored.
4. **Entity records hold row ids.** Where an entity blob used to hold scraped content, it holds the telescope row id (or, for multi-page fields, a list of `{url, row id}`) instead. Readers accept both shapes (legacy text or row id) so blobs can be cleared after the migration loads.
5. **All company page scrapes move.** Homepage visible text, homepage nav links, culture pages, the selected job-list page text, and possible-job-list page scrapes (text + links) are stored as telescope rows referenced from `company_data`. Fields derived from those pages (assembled PJL content, merged PJL nav links) are rebuilt from the referenced rows when read, not stored.
6. **Job description = preamble + scraped text, read-only.** The existing `job_data.job_description` key becomes the preamble field — email / contact preamble, pasted JD text, agent-parsed listing text. The job also keeps a reference to the telescope row holding the scraped JD when a job link was scraped. One reader composes the complete JD (preamble, then scraped text with today's prune / collapse rules); every JD consumer, including the job APIs the UI reads, gets that composed string. The JD is **read-only** in the job modal (it is not a versioned artifact), and the job edit API no longer writes it.
7. **Readers unchanged in output.** Every company and job reader — prompt assembly, readiness checks, culture cache, coat-check fetch-on-missing, admin task-prompt preview, job list / detail APIs — resolves the row ids and produces the same text it does today.
8. **Existing company data moves in three steps.** Export the scraped keys from existing `company_data` to a JSON file of telescope rows; load (upsert) that file into `telescope_data`; then, once loaded, update `company_data` to replace the scraped content with the row ids. Existing jobs need no move: their current `job_description` text is already valid preamble with no scraped reference, which composes to the same JD.

Out of scope: retention / pruning automation; `meteorite.content` and the meteorite land paths (they hand text to the job's preamble field, which keeps working); storing DOM; the Telescope service (`service/telescope/**`) and client (`src/external/telescope.py`); the admin Telescope test page; historical one-off scripts under `scripts/migrations/` that read old blob keys.

## Component scope

* `src/data/database.py` — **modified** — new `telescope_data` table, idempotent schema-ensure, save (returns row id) and read-by-id(s) data functions, schema-ensure registry entries, module-header table inventory line.
* `src/utils/config.py` — **modified** — content-type key names, the list of `company_data` keys that hold telescope row ids, and the job-data key for the scraped-JD reference.
* `src/core/gazer.py` — **modified** — owns `telescope_data`: scrape-and-keep calls and resolve-by-id helper; `fetch_website`, `fetch_job_pages` and `fetch_jd` store row ids; culture-cache checks resolve ids.
* `src/core/tracker.py` — **modified** — composed-JD reader; JD coat-check returns the composed JD; job-field edit no longer writes the JD.
* `src/core/consult.py` — **modified** — JD readers switch to the composed-JD reader.
* `src/ui/api/api_jobs.py` — **modified** — job list / detail responses carry the composed JD in the field the UI already reads; the job edit route stops accepting `job_description`.
* `src/ui/frontend/src/components/JobDetailModal.tsx` — **modified** — JD shown read-only; no longer part of the edit draft or save payload.
* `src/core/roster.py` — **modified** — company scrape writers use gazer's scrape-and-keep calls and store row ids (homepage, nav links, culture pages, job-list text, PJL pages); readers resolve ids via gazer; derived PJL fields rebuilt on read; `get_company_data` resolves ids before coat-check.
* `src/ui/api/api_admin.py` — **modified** — admin ad-hoc task-prompt preview resolves company row ids via gazer and uses the composed JD for jobs.
* `scripts/migrations/migrate_company_scrape_to_telescope_data.py` — **new** — export → load → clear for existing company scrape content.

## Technical scope

* `src/data/database.py` — new table `telescope_data` (uuid primary key, `candidate_id`, `url`, `data_type` free text, compressed content blob, `created_at`) with an index on `candidate_id` + `created_at`; new save function that inserts one row and returns its id, with no allow-list check on `data_type`; new read function by one id and by a list of ids returning plain content; new schema-ensure function wired into the existing schema-ensure registry; header inventory updated.
* `src/utils/config.py` — new config block naming the content-type keys (`VISIBLE_TEXT`, `PAGE_LINKS`, reserved `DOM_CONTENT`) and listing the `company_data` keys that now hold row ids (`homepage_text`, `nav_links`, `website_content`, `job_list_visible`, `pjl_scrape_pages`), with a module-level assert that each is still in `ROSTER_CONFIG["company_data_keys"]`; new `TRACKER_CONFIG["job_data_keys"]` entry for the scraped-JD reference.
* `src/core/gazer.py` — new scrape-and-keep functions wrapping the Telescope visible-text and link-list calls core already uses: call Telescope, save every result (with the entity's `candidate_id` and URL) via the new data function, return content plus row id; new resolve helper that takes a stored value (row id, list of `{url, row id}`, or legacy text) and returns content in today's shape (string, enumerated links, or `[{url, content}]`); modified `fetch_website_batch` and `fetch_job_pages_batch` to store row ids; modified the JD save path in `fetch_jd` to keep classification / min-length gates on the pruned text and store the scraped-JD reference instead of JD text; modified culture-cache checks to resolve ids.
* `src/core/tracker.py` — new composed-JD function: preamble (`job_description`), then the referenced scraped text (via gazer's resolve helper) run through the existing JD prune / blank-line-collapse rules; modified `get_job_data` so the JD key returns the composed value (self-heal path unchanged); modified job-field update to drop `job_description` handling.
* `src/core/consult.py` — modified JD reads (live-content assembly, relative-JD and batch JD paths) to call the composed-JD function instead of reading `job_data` directly.
* `src/ui/api/api_jobs.py` — modified `list_view` and `detail` to place the composed JD in the response's `job_data.job_description` (response only; never written back); modified `persist_skipped_edits` to remove `job_description` from accepted fields.
* `src/ui/frontend/src/components/JobDetailModal.tsx` — modified JD field to read-only display; removed from draft, dirty check and save payload.
* `src/core/roster.py` — modified `_fetch_nav_links`, `_fetch_website_content`, homepage / prefilter writers and the select-job-page `job_list_visible` writer to use gazer's scrape-and-keep calls and store row ids; modified `_scrape_pjl_page` / PJL merge to keep `{url, row id}` per page; modified readers (homepage presence check, prefilter homepage block, upshot culture text, PJL assembly and nav-link merge) to resolve via gazer; modified `get_company_data` to resolve id-holding keys before the coat-check handler.
* `src/ui/api/api_admin.py` — modified `_build_adhoc_live_content` company branch to resolve ids via gazer and job branch to use the composed-JD function.
* `scripts/migrations/migrate_company_scrape_to_telescope_data.py` — new script with three modes: **export** (read every company's scraped keys, write a JSON file of telescope rows with pre-assigned uuids, the company's `candidate_id`, and the id each blob key should hold; no DB writes), **load** (upsert the file into `telescope_data` by uuid; re-run adds nothing), **clear** (replace each scraped key in `company_data` with its row id(s) from the file; refuses if any referenced row is missing).

## Architectural definition

* **Patterns to reuse** — no established pattern applies. (`agent_data` — compressed content rows outside the entity blob — is the working precedent, not a canonized pattern.)
* **New patterns proposed** — **Scrape content lives in** `telescope_data`**, owned by gazer; entity records hold row ids.** Flagged for Archie. Implementation does not wait on approval; approving it makes this the rule for future scrape writers (meteorite, contact).
* **Applicable statutes**
  * `stat.logging.debug` — new data / gazer functions and the migration log Calling / Response at debug. [link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
  * `stat.logging.warning` — per-entity save / resolve / move failures warn with who and why. [link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
  * `stat.logging.error` — exceptions logged once at the handler. [link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
  * `stat.logging.info.entity` — writer and migration progress lines use the id-pipe type + event shape. [link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
  * Not applicable, stated explicitly: `astral.entity.required-metadata` — `telescope_data` is a content table, not an entity table.

## Acceptance criteria

 1. **Table shape.** `sqlite3 astral.db ".schema telescope_data"` shows a uuid primary key plus `candidate_id`, `url`, `data_type`, a content blob, and `created_at`. Fail: table or any of those columns missing.
 2. **No type gate.** Saving a row with `data_type="JSON"` succeeds and selecting it returns `JSON`. Fail: save raises or rejects.
 3. **Every pipeline scrape is kept, with candidate.** After `fetch_website` for company X, `telescope_data` has new `VISIBLE_TEXT` and `PAGE_LINKS` rows whose `candidate_id` equals `SELECT candidate_id FROM company WHERE short_name='X'`. A `fetch_jd` run on a job whose page is bot-walled or classified closed still adds its `VISIBLE_TEXT` row. Fail: missing row, or NULL / wrong `candidate_id` on an entity-scoped scrape.
 4. **Gazer is the only owner.** `git grep -n -i "telescope_data" -- src/core src/ui ':!src/core/gazer.py'` shows no import or call of a `database.py` telescope function (only calls into gazer); `git diff origin/dev...HEAD --stat -- src/external/telescope.py service/telescope` is empty. Fail: another module touches the table directly, or the client / service changed.
 5. **Company blobs hold ids, not text.** After `fetch_website` for X, `json_extract(company_data,'$.homepage_text')` and `'$.nav_links'` are uuid-shaped and each resolves to a `telescope_data` row; same for `website_content` / `pjl_scrape_pages` entries (each `{url, id}`) after the culture and PJL fetches. `json_extract(company_data,'$.pjl_assembled_content')` and `'$.pjl_nav_links'` are NULL on newly written companies. Fail: any of those keys holds page text.
 6. **Company readers unchanged.** For one company, the admin ad-hoc preview for `prefilter_company`, `select_job_page` and `gaze` returns byte-identical text before migration (text in blob) and after `clear` (ids in blob). Fail: any diff.
 7. **JD composes.** For a job with preamble P and a scraped-JD reference, `GET /api/jobs/<id>` returns `job_data.job_description` == P followed by the pruned scraped text; for a job with no reference (pasted / meteorite / existing), it returns exactly today's stored text. Fail: mismatch.
 8. **One JD reader.** `git grep -n -E "\.get\((jd_key|[\"']job_description[\"'])" -- src/core src/ui/api ':!src/core/tracker.py'` returns nothing. Fail: any direct read outside tracker.
 9. **JD is read-only.** `PUT /api/jobs/<id>` with only `{"job_description": "x"}` returns 400 and `job_data` is unchanged; with `job_title` plus `job_description`, the title saves and `job_data.job_description` is unchanged. In the job modal the JD is not editable: `git grep -n "job_description: e.target.value" -- src/ui/frontend` returns nothing. Fail: JD written via the API or editable in the modal.
10. **Migration is staged and safe.** `export` writes the JSON file and a `SELECT short_name, company_data FROM company` dump plus `SELECT COUNT(*) FROM telescope_data` are unchanged. `load` run twice: the second run adds 0 rows. `clear` run against an empty `telescope_data` exits non-zero and changes no company row. After `load` then `clear`, AC 5 and AC 6 hold for every company. Fail: export writes to the DB, load duplicates, or clear proceeds with rows missing.
11. **Deleting content needs no blob surgery.** Deleting the `telescope_data` row referenced by a company's `website_content` leaves `company.company_data` byte-identical, and the next `get_company_data(company, "website_content")` re-runs the coat-check fetch instead of raising. Fail: blob changes or read raises.

## Open questions

None.

## Proposed child tickets

#### 1!!!: **telescope_data table and config - Ada**

Ships the `telescope_data` table, schema-ensure, save-returns-id and read-by-id(s) functions, and the config naming content types, id-holding company keys, and the scraped-JD reference key. Observable: AC 1 and 2 on fresh and existing `astral.db`. Does **not** add gazer ownership (#2), JD (#3), roster paths (#4), or move data (#5).
**Citations:** `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`.
**Scope:** `src/data/database.py` — new table `telescope_data` (uuid primary key, `candidate_id`, `url`, `data_type` free text, compressed content blob, `created_at`) with an index on `candidate_id` + `created_at`; new save function that inserts one row and returns its id, with no allow-list check on `data_type`; new read function by one id and by a list of ids returning plain content; new schema-ensure function wired into the existing schema-ensure registry; header inventory updated. `src/utils/config.py` — new config block naming the content-type keys (`VISIBLE_TEXT`, `PAGE_LINKS`, reserved `DOM_CONTENT`) and listing the `company_data` keys that now hold row ids (`homepage_text`, `nav_links`, `website_content`, `job_list_visible`, `pjl_scrape_pages`), with a module-level assert that each is still in `ROSTER_CONFIG["company_data_keys"]`; new `TRACKER_CONFIG["job_data_keys"]` entry for the scraped-JD reference.
Estimate: 3

#### 2!!: **Gazer owns telescope_data; gazer scrapes keep everything - Hedy**

After #1. Gazer's scrape-and-keep calls and resolve helper (legacy-text tolerant); gazer's own writers (`fetch_website`, `fetch_job_pages`, `fetch_jd`) store row ids and its culture cache resolves them. Observable: AC 3, 4, and 5 for the gazer-written keys. Does **not** compose the JD for readers (#3) or change roster paths (#4).
**Citations:** `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.info.entity`.
**Scope:** `src/core/gazer.py` — new scrape-and-keep functions wrapping the Telescope visible-text and link-list calls core already uses: call Telescope, save every result (with the entity's `candidate_id` and URL) via the new data function, return content plus row id; new resolve helper that takes a stored value (row id, list of `{url, row id}`, or legacy text) and returns content in today's shape (string, enumerated links, or `[{url, content}]`); modified `fetch_website_batch` and `fetch_job_pages_batch` to store row ids; modified the JD save path in `fetch_jd` to keep classification / min-length gates on the pruned text and store the scraped-JD reference instead of JD text; modified culture-cache checks to resolve ids.
Estimate: 5

#### 3!: **Composed, read-only job description - Katherine**

After #2. One composed-JD reader (preamble + pruned scraped text) used by every JD consumer and returned by the job APIs; JD becomes read-only in the modal and the edit API. Observable: AC 7, 8, 9. Does **not** touch gazer's JD write (#2) or company paths (#4).
**Citations:** `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`.
**Scope:** `src/core/tracker.py` — new composed-JD function: preamble (`job_description`), then the referenced scraped text (via gazer's resolve helper) run through the existing JD prune / blank-line-collapse rules; modified `get_job_data` so the JD key returns the composed value (self-heal path unchanged); modified job-field update to drop `job_description` handling. `src/core/consult.py` — modified JD reads (live-content assembly, relative-JD and batch JD paths) to call the composed-JD function instead of reading `job_data` directly. `src/ui/api/api_jobs.py` — modified `list_view` and `detail` to place the composed JD in the response's `job_data.job_description` (response only; never written back); modified `persist_skipped_edits` to remove `job_description` from accepted fields. `src/ui/frontend/src/components/JobDetailModal.tsx` — modified JD field to read-only display; removed from draft, dirty check and save payload.
Estimate: 5

#### 4!: **Roster company scrapes and admin preview on telescope_data - Ada**

After #2. Roster's company writers use gazer's scrape-and-keep calls and store row ids; roster readers, `get_company_data` and the admin preview resolve via gazer; derived PJL fields rebuilt on read. Observable: AC 5 for roster-written keys, AC 6 (fresh-write side), AC 11. Does **not** move existing blob data (#5).
**Citations:** `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.info.entity`.
**Scope:** `src/core/roster.py` — modified `_fetch_nav_links`, `_fetch_website_content`, homepage / prefilter writers and the select-job-page `job_list_visible` writer to use gazer's scrape-and-keep calls and store row ids; modified `_scrape_pjl_page` / PJL merge to keep `{url, row id}` per page; modified readers (homepage presence check, prefilter homepage block, upshot culture text, PJL assembly and nav-link merge) to resolve via gazer; modified `get_company_data` to resolve id-holding keys before the coat-check handler. `src/ui/api/api_admin.py` — modified `_build_adhoc_live_content` company branch to resolve ids via gazer and job branch to use the composed-JD function.
Estimate: 5

#### 5: **Export / load / clear existing company scrape data - Hedy**

After #3 and #4 (all readers must resolve ids before blobs are cleared). Three-step move of existing company scrape content into `telescope_data`. Observable: AC 10, and AC 6 across all companies after `clear`. Does **not** touch jobs (existing JD text is already valid preamble).
**Citations:** `stat.logging.debug`, `stat.logging.warning`, `stat.logging.info.entity`.
**Scope:** `scripts/migrations/migrate_company_scrape_to_telescope_data.py` — new script with three modes: **export** (read every company's scraped keys, write a JSON file of telescope rows with pre-assigned uuids, the company's `candidate_id`, and the id each blob key should hold; no DB writes), **load** (upsert the file into `telescope_data` by uuid; re-run adds nothing), **clear** (replace each scraped key in `company_data` with its row id(s) from the file; refuses if any referenced row is missing).
Estimate: 3

**New patterns:** "Scrape content lives in `telescope_data`, owned by gazer; entity records hold row ids" — #2 builds it, #3 and #4 consume it; future meteorite / contact scrape writers reuse it.

**Monolith check:** 8 capabilities, 5 children — table, gazer ownership, JD, roster paths, data move.

**Scope partition check:** `database.py` + `config.py` → #1; `gazer.py` → #2; `tracker.py` + `consult.py` + `api_jobs.py` + `JobDetailModal.tsx` → #3; `roster.py` + `api_admin.py` → #4; migration script → #5. Every Component / Technical scope item claimed once.

---

## Original brief

In parallel to how agent_data is referenced within entity tables, so too should telescope data be captured and referenced within entity tables, so that we no longer store scraped text in the entity tables.

Visible Text, nav links and HTML dom content should be stored as separate records with a type key for VISIBLE_TEXT, PAGE_LINKS, DOM_CONTENT, so as telescope returns any of those, they are stored in the telescope data table (in astral.db).

This will allow for maintenance of volume size without having to surgically update entity_data blobs.

### Comments

#### chuckles — 2026-10-11T02:11:51.171Z
[fix-intake] Live DB cleanup done. I backed up `~/astral/data/astral.db` to `~/astral-db-backups/astral.db.bak-AST-2130-20261011`, outside the repo. Then I dropped `telescope_data` and its index. All 113 rows were test fixtures (`acme.com`, `*.example`). The integrity check passed. The table comes back empty when PR [#300](https://github.com/susansomerset/astral/pull/300) merges. No bugs filed.

#### susan — 2026-10-11T02:10:06.906Z
Go

#### chuckles — 2026-10-11T00:50:51.140Z
[check-linear] answered. Pipeline blockers are resolved; the live DB cleanup is still waiting on you.

- **Ada's AST-2134 block:** resolved. AST-2133 landed on `ftr` (`tracker.compose_job_description` is present), AST-2134 finished Stage 5, and all five children are User Testing. Parent PR: [#300](https://github.com/susansomerset/astral/pull/300).
- **Ada's AST-2131 `created_at` block:** resolved. The insert passes `_utc_now()` explicitly (her option 1).
- **Live DB pollution:** not resolved. Your live `~/astral/data/astral.db` still has the `telescope_data` table and its 113 test rows. Reply "go" and they get backed up, then the table is dropped (once PR #300 merges, the app recreates it empty). (@susan)

#### susan — 2026-10-11T00:40:24.815Z
@chuckles Has this been resolved?

#### ada — 2026-10-11T00:11:41.058Z
🛑 AST-2134 Stage 5 blocked: AST-2133 not merged on ftr (`tracker.compose_job_description` absent on `origin/ftr/AST-2130-telescope-data` @ `442b1f61b`). Stages 1–4 published: `origin/sub/AST-2130/AST-2134-roster-telescope-data` @ `a25c7d188`. AST-2134 stays Plan Approved; Stage 5 resumes after AST-2133 lands on ftr.

#### chuckles — 2026-10-10T23:42:15.418Z
AST-2133 estimate 5→3 — reader reuses AST-2132's pattern; rest is mechanical call-site and field removal across four files.

#### chuckles — 2026-10-10T23:33:17.896Z
@susan Live DB pollution from AST-2130 test runs (not blocking the pipeline; needs your go-ahead):
- `astral-AST-2130/data/astral.db` symlinks to `~/astral/data/astral.db`; test runs during [AST-2132](https://linear.app/astralcareermatch/issue/AST-2132) created the `telescope_data` table there and inserted 113 fake rows (`https://canonical.example` etc., 2026-10-10 ~23:22).
- Nothing has been deleted. Options: back up, then delete those rows / drop the table (dev doesn't have it yet). Reply here and an agent will do it.

#### ada — 2026-10-10T23:05:16.238Z
🛑 Stage 2 blocked: AST-2131 plan says created_at "takes the column default", but the mirrored column has no default
Step: Stage 1 step 2 (`created_at <same column definition agent_data uses>`) + Stage 2 step 2 ("Let `created_at` take the column default").
Issue: live `agent_data.created_at` is `TIMESTAMP NOT NULL` with no DEFAULT; `save_agent_data` passes `ts = created_at or _utc_now()` explicitly. Executed literally, every `save_telescope_data` INSERT raises NOT NULL constraint failed. Stage 0 drift check otherwise clean (all six symbols present as described).
Proposed resolutions:
1. (recommended) Keep `created_at TIMESTAMP NOT NULL`; `save_telescope_data` includes `created_at` in the INSERT with `_utc_now()` — same timestamp format as `agent_data`, so `(candidate_id, created_at)` ordering matches the rest of the DB.
2. Column `created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`, INSERT omits it — but SQLite's `YYYY-MM-DD HH:MM:SS` differs from `_utc_now()` format used elsewhere.

#### chuckles — 2026-10-10T23:03:19.084Z
AST-2131 estimate 3→2 — known agent_data pattern across two files, no callers yet.

#### chuckles — 2026-10-10T22:57:37.394Z
@susan Found them — your answers were inline in the Description, and I'd missed that they'd landed. They're folded into the definition now: gazer owns `telescope_data` (`telescope.py` untouched), every pipeline scrape is kept, `candidate_id` comes from the entity row (you're right that `company` has it), JD is read-only in the modal and the edit API, and `job_description` stays as the preamble field. Open questions: none. Moved to Todo.

#### chuckles — 2026-10-10T22:57:28.230Z
[check-linear] answered — all five answers folded into the definition (gazer owns `telescope_data`, persist everything, `candidate_id` from the entity, JD read-only, `job_description` stays as preamble). Open questions now empty; Discussion > Todo (@susan)

#### susan — 2026-10-10T22:55:25.584Z
@chuckles they were all answered, please look again.

#### chuckles — 2026-10-10T22:15:55.013Z
@susan

The 5 questions in my previous comment are still open (also listed under `## Open questions` in the Description): layer rule, opt-in vs persist-everything, `candidate_id` on company scrapes, JD modal edit, preamble field name. If you want the recommended default on all five, reply "defaults" and I will move this to Todo.

#### chuckles — 2026-10-10T21:20:59.387Z
@susan

On DOM: no, nothing persists DOM today. `fetch_job_pages` keeps visible text + nav links per PJL page; the `select_job_page` fallback pulls DOM live, keeps it in memory for that run, and hands the culled DOM to `parse_job_list`. Definition now stores visible text + links only; `DOM_CONTENT` is just a reserved name.

1. **Layer rule.** `telescope.py` → `database.py` breaks the external-imports-utils-only rule (`stat.layers.import-direction`, draft). Approve one late import inside the persist helper as a named exception (same shape as `logging.py`), or have a thin core wrapper do the save?
2. **Opt-in or persist everything?** Recommended: persist only when the caller asks, so bot-wall probes, admin scrapes and discarded results don't add rows. Or store every visible-text / links return?
3. **`candidate_id` on company scrapes.** Companies aren't candidate-scoped. Recommended: fill it from the candidate whose dispatch run triggered the scrape, NULL for admin / scripts. OK?
4. **Editing the JD in the job modal.** Recommended (no UI change): a saved edit writes the full edited text into the preamble field and drops the scraped reference. Or the modal edits only the preamble and shows scraped text read-only (brings frontend into scope)?
5. **Preamble field name.** Recommended: existing `job_data.job_description` becomes the preamble field, so existing jobs need no migration. Or a new name (plus a job-side migration)?

#### chuckles — 2026-10-10T19:56:39.683Z
@susan

1. **Which fields move?** Default: only the `company_data` scrape keys (`homepage_text`, `nav_links`, `website_content`, `job_list_visible`, `pjl_scrape_pages`, `pjl_nav_links`). Should `pjl_assembled_content` (derived from the PJL pages) stay in the blob or be rebuilt on read? And confirm `job_data.job_description` and `meteorite.content` stay put (both also hold pasted / user-edited text).
2. **Capture everything Telescope returns, or only what we keep today?** Nothing persists DOM today, and the JD and meteorite scrapes keep only a processed result. Default: store only what's persisted today, at the core layer, leaving `src/external/telescope.py` alone. Or do you want every return (all three types, every scrape) captured — which means passing entity context into the client and more volume?
3. **How do entity tables "reference" a telescope row?** Default mirrors `agent_data`: the telescope row carries `entity_type` + `entity_id` and the blob holds nothing. Alternative: the blob keeps a pointer (telescope row id) per key.
4. **History or current-only?** Default: append a row per scrape, read latest (like `agent_data`). Alternative: replace the prior row for the same entity + type + URL on re-scrape.
5. **Retention/pruning automation** — out of scope here, or add a prune command/admin action to this epic?

---

_Implementation detail may live in git history on `origin/dev`._
