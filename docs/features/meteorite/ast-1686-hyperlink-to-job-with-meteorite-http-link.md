# AST-1686 — Hyperlink to job with meteorite http link

<!-- linear-archive: AST-1686 archived 2026-09-24 -->

## Linear archive (AST-1686)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1686/hyperlink-to-job-with-meteorite-http-link  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Meteorite scraps often carry a real ATS `http(s)` posting URL even when Astral’s scraper cannot read the page (bot / Cloudflare challenge). Humans still need that URL as the apply path — a bot wall must not hide the click-through. This epic (Astral Meteorite) ensures `job.job_link` is populated from the meteorite http link even when the fetch is bot-blocked, creates a job when JD text arrived by non-scrape means, and surfaces that href on every job UI that opens or titles a listing.

## Functional scope

* Whenever a meteorite row has an `http(s)` `link`, the related job’s `job.job_link` is set to that URL — including when scrape or qualify classifies the page/content as bot-blocked.
* Pre-land meteorite rows in `BOT_BLOCKED` that already have usable JD text from a non-scrape source (email body, paste, or other assembled `content` — not the failed Playwright fetch) create/land a job with that http `job.job_link` so apply is possible. Link-only bot-blocked scraps with no alternate JD text stay on Estelle paste recovery (AST-1561) until text exists.
* On Recommended Job Report, the job title is a navigable hyperlink to the resolved listing URL (`job.job_link` when http(s), else related `meteorite.link` when http(s)).
* Recommended **Apply** (CANDIDATE_REVIEW CLIENT action) opens that same resolved URL.
* Job Detail (In Review / Skipped and any other job UI that shows a listing link today) exposes the same http(s) listing href — including when `job.state` is `BOT_BLOCKED`.
* Non-http meteorite breadcrumbs stay non-navigable (http(s)-only rule, aligned with AST-1640).
* Does **not** own the Recommended Meteorite provenance tab body (AST-1685), copy-single-page deep link (AST-1687), or source_entity parent reshape (AST-1640). Ships its own minimal `astral_job_id` → meteorite link lookup (does not wait on AST-1685).

## Component scope

* `src/core/meteorite.py` — **modified** — on land / create paths, always copy http(s) `meteorite.link` onto `job.job_link`; when state is `BOT_BLOCKED` but non-scrape JD `content` is present, create/land the job with that link (do not invent content from a blocked scrape).
* `src/core/consult.py` — **modified** — qualify `BOT_BLOCKED` destination still persists/preserves http(s) `job.job_link` from input/meteorite link (today’s early return must not leave apply without a URL when one exists).
* `src/core/tracker.py` — **modified** only as needed for save/initialize helpers that write `job_link` on the bot-blocked / land paths above.
* `src/data/database.py` — **modified** — minimal read helper `astral_job_id` → meteorite row (or link field) for listing-href fallback; header inventory note.
* `src/ui/api/api_jobs.py` — **modified** — `GET /api/jobs/<id>` exposes one resolved http(s)-only listing/apply href (`job.job_link` else related meteorite http link).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — header title + CLIENT Apply use the resolved listing href.
* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` — **modified** — title `<a href>` uses the resolved listing href; plain title when none.
* `src/ui/frontend/src/components/JobDetailModal.tsx` — **modified** — listing/open link uses the same resolved http(s) href (covers In Review / Skipped `BOT_BLOCKED` and peers that open this modal).

## Technical scope

* `meteorite` land/create: when `meteorite.link` is http(s), pass it as `job_link` into `save_meteorite_job` / `create_meteorite_job` even if the row was or remains bot-blocked; when `BOT_BLOCKED` + non-empty non-scrape `content`, run the create/land path that attaches `astral_job_id` (link-only empty-content BOT_BLOCKED unchanged for AST-1561).
* `consult` qualify_meteorite bot branch: before/with state → `BOT_BLOCKED`, ensure http(s) job_link is written or kept (initialize_job or equivalent column update) from the resolved input/meteorite URL.
* `tracker`: only the save/initialize touch points required by the above writers.
* `database`: reverse read by `astral_job_id` → meteorite link (or row); no create/update in this helper.
* `api_jobs`: serialize resolved listing href as http(s) string or null; prefer `job.job_link` when http(s), else meteorite http link.
* Recommended modal + header: title href and Apply `window.open` share that field.
* `JobDetailModal`: listing `<a>` / open control uses the same field when http(s).

## Architectural definition

* **Patterns to reuse** — [`patt.entity.batch-processing`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>) — land/create from bot-blocked rows with alternate text stays on the existing claim → process → release land path; do not invent a parallel ingress runner.
* **New patterns proposed** — none.
* **Applicable statutes** —
  * [`stat.logging.info.entity`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>) — land/create and qualify bot-blocked link writes stay id-pipe entity info lines.
  * [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — job detail listing-href attachment logs progress once at the completing route.
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — lookup/hydrate detail stays ContextVar-gated.
  * [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — land/qualify/route failures log once at the handler with traceback.
  * [`stat.logging.warning`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>) — per-row land/qualify misses warn who/why without aborting the batch.

## Acceptance criteria

1. Land/create of a meteorite row whose `link` is `https://example.test/job/1` writes `job.job_link` to that URL even when the row’s scrape/qualify outcome is bot-blocked. Fail: `job.job_link` empty/null while meteorite http link exists.
2. A pre-land `BOT_BLOCKED` meteorite with non-empty non-scrape `content` and http(s) `link` ends with a job row (`astral_job_id` set) and that http `job.job_link`. Fail: content+link bot-blocked row never creates a job, or creates a job without the http link.
3. A link-only `BOT_BLOCKED` meteorite with empty `content` does **not** create a job in this epic (still Estelle paste / AST-1561). Fail: empty-content bot-blocked rows are force-landed.
4. `GET /api/jobs/<id>` includes a resolved listing href that is the http(s) `job.job_link` when set, else http(s) related `meteorite.link`, else `null`. Fail: field absent; non-http breadcrumb returned; or http meteorite link ignored when `job.job_link` empty.
5. Recommended report: title is `<a href="{listing}>` when listing href is http(s); Apply in `CANDIDATE_REVIEW` opens the same URL. Fail: title plain while href exists, or Apply opens a different/missing URL.
6. Opening Job Detail for a `BOT_BLOCKED` job (In Review / Skipped) shows a navigable listing control to that same http(s) URL when present. Fail: no clickable listing on bot-blocked jobs that have `job.job_link` or related meteorite http link.
7. `grep` of this epic’s diff does not add a second full `related_meteorite` provenance payload for AST-1685’s pane — only the minimal link/href lookup. Fail: this epic re-implements the full Meteorite tab contract.

## Open questions

none

## Proposed child tickets

#### 1!: **Persist meteorite http onto job.job_link (+ land when text without scrape) - Hedy**

Land/create and qualify bot-blocked paths always write http(s) `meteorite.link` → `job.job_link`; `BOT_BLOCKED` + non-scrape content creates/lands a job; link-only empty content stays on AST-1561. Does not own API listing field or React (#2, #3).
**Citations:** `patt.entity.batch-processing`, `stat.logging.info.entity`, `stat.logging.debug`, `stat.logging.error`, `stat.logging.warning`.
**Scope:** `src/core/meteorite.py` (land/create + BOT_BLOCKED-with-content create); `src/core/consult.py` (qualify bot-blocked preserves/writes job_link); `src/core/tracker.py` (only save/initialize touch points required). Technical: http(s) copy onto `job.job_link`; create/land when content present on bot-blocked row; no force-land of empty-content BOT_BLOCKED.
**Estimate: 5**

#### 2!: **Minimal listing-href on job GET - Ada**

DB reverse link lookup + `GET /api/jobs/<id>` resolved http(s) listing href (`job.job_link` else meteorite http link). Does not own writers (#1) or React (#3).
**Citations:** `stat.logging.info.api`, `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/data/database.py` (minimal astral_job_id → meteorite link/row read + header inventory); `src/ui/api/api_jobs.py` (resolved listing href on detail). Technical: http(s)-only string or null; prefer job column then meteorite link.
**Estimate: 2**

#### 3: **All job UI surfaces use listing href - Katherine**

Recommended title + Apply and Job Detail listing control consume the resolved listing href. Does not own API/writers (#1, #2).
**Citations:** none — presentational / client open only.
**Scope:** `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`; `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`; `src/ui/frontend/src/components/JobDetailModal.tsx`. Technical: shared href for title/Apply/detail listing; non-http → not navigable.
**Estimate: 2** — after #2 (and after #1 for UAT of bot-blocked rows that now carry job_link).

**Monolith check:** Functional scope has 6 capabilities; 3 children — OK (write path, API resolve, UI surfaces).

**Scope partition check:** Every Component/Technical item appears in exactly one child Scope block.

---

## Original brief

Even if the link is bot blocked, the candidate can click on the link to apply to the job.

### Comments

#### chuckles — 2026-09-16T23:15:36.200Z
AST-1693 REVIEW — merge-child blocked; recalling Betty (duplicate merge-tests) and Hedy (sub not on ftr after AST-1694 landed).

#### chuckles — 2026-09-16T21:51:48.164Z
@susan

1. **Linear project** — Ticket has no project today. Confirm **Astral Interface** (siblings AST-1685 / AST-1687) vs **Astral Meteorite**.
2. **Surfaces** — Recommended report title + Apply only, or also In Review / Skipped **Job Detail** when `job.state == BOT_BLOCKED`?
3. **Data vs UI fallback** — Is UI/API resolution (`job.job_link` http else `meteorite.link` http) enough, or must land/qualify also **write** meteorite http onto `job.job_link` when bot-blocked so the column itself stays populated?
4. **Pre-land meteorite `BOT_BLOCKED`** (scrape blocked, no `astral_job_id` yet) — in scope to create a job row with that http link for apply, or **out of scope** (stay on Estelle paste-recovery / AST-1561 until LANDED)?
5. **AST-1685 dependency** — Block this epic on AST-1685’s `related_meteorite` / DB helper, or ship a minimal listing-href lookup here and let 1685 own the full Meteorite pane?

---

_Implementation detail may live in git history on `origin/dev`._
