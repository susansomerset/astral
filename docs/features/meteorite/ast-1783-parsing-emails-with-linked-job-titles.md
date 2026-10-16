<!-- linear-archive: AST-1783 archived 2026-10-07 -->

## Linear archive (AST-1783)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1783/parsing-emails-with-linked-job-titles  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Meteorite already stages emails that are a bare list of job URLs or a rich HTML paste (Dice / inspector style) into http(s) `meteorite.link` rows and scrapes them. A common recruiter shape is different: each visible job title is itself the hyperlink (`<a href="https://…">Senior Widget Engineer</a>`). Today that shape is often classified as a text landable outcome, so the stage map writes an email breadcrumb into `meteorite.link` and the job-page `href` never reaches the meteorite table. Downstream scrape and listing already know what to do once `meteorite.link` is http — this epic makes linked-title emails first-class on the live `stage_meteorite` path so those hrefs are saved and titles still stage when the anchor names the role.

## Functional scope

* Recognize ingress blobs where one or more job titles are the visible text of http(s) anchors pointing at job pages (title-as-href), distinct from a bare URL list and from a full HTML page paste that already yields URL outcomes today.
* For each such title-link, stage a landable URL meteorite row whose `link` is the anchor `href` (http/https) and whose `job_title` is the anchor text when that text names a role. When the anchor text is only a generic CTA (e.g. Apply, View job, Click here), still save the href and omit or leave empty `job_title` rather than inventing a title.
* Teach the live `stage_meteorite` classify prompts to treat title-as-href as a URL landable shape using the existing closed outcomes — prefer `link_list` when there are several title-links, and `single_jd_with_more` when there is one JD plus one more posting URL. Do **not** add a seventh outcome string.
* When a classify jobs item carries an http(s) `job_link`, the meteorite row's `link` must be that URL — never replace it with an email breadcrumb. Breadcrumb on `meteorite.link` remains only for text landable outcomes that have no http(s) `job_link` (AST-1703).
* Out of scope: land → `job.job_link` / `listing_href` UI (already shipped AST-1693–1695); new classify outcome enum values; resurrecting the idle gazer email-ingest path; changing scrape/land runners beyond consuming a correctly staged http `link`.

## Component scope

* `data/admin/agent_task.json` — **modified** — `stage_meteorite` cache/user prompts teach title-as-href → `job_link` from href + `job_title` from role-naming anchor text; keep the six closed outcomes; no `$RESPONSE_SCHEMA` in prompts.
* `docs/uat-fixtures/AST-756/expected-agent_task.json` — **modified** — lockstep expected catalog text with the `stage_meteorite` prompt edits.
* `src/core/meteorite.py` — **modified** — stage map / post-map wiring prefers http(s) `job_link` on `meteorite.link` over email breadcrumb when present; keeps staged `job_title` on the row as today.

## Technical scope

* `data/admin/agent_task.json` — update `stage_meteorite` prompt instructions so title-as-href blobs are classified as URL landables (`link_list` / `single_jd_with_more` as appropriate), each jobs item sets `job_link` from the anchor href and optional `job_title` from role-naming anchor text (omit title for generic CTAs; never invent); keep electronic-contact, breadcrumb header fields, and JOB TITLE subject-prefer rules for other shapes; leave `$RESPONSE_SCHEMA` absent.
* `docs/uat-fixtures/AST-756/expected-agent_task.json` — mirror the same `stage_meteorite` prompt wording so the UAT catalog fixture stays in lockstep.
* `src/core/meteorite.py` — in the classify→row mapper (and/or the immediate post-map wiring in `stage_meteorite`), when a jobs item has an http(s) `job_link`, set the meteorite row `link` to that URL even if the classify outcome was a text landable; only call the email-breadcrumb helper when no http(s) `job_link` is present. Keep copying optional `job_title` / `employer_name` onto the row as today. When the row `link` is http(s), use the URL/scrape state path (`SCRAPE_LINK`) so scrape still runs; do not leave an http link stranded under READY solely because the outcome string was text. Do not invent a parallel HTML link harvester outside Ruth + this map preference.

## Architectural definition

* **Patterns to reuse** — `patt.task.daisy-chain` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.daisy-chain.md>)) — job URL and title must ride the meteorite row from stage through scrape/land; prefer fixing classify + map so `meteorite.link` / `job_title` are correct, not a second extract path that bypasses the staged row.
* **New patterns proposed** — none.
* **Applicable statutes** — `stat.logging.debug` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)) — no new chatter for linked-title recognition; keep existing classify call/response debug. `stat.logging.info.entity` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)) — id-only; do not add linked-title-specific entity info logs.

## Acceptance criteria

1. `rg -n 'href|title-as-href|anchor|job_link' data/admin/agent_task.json` (or equivalent wording in the `stage_meteorite` prompt fields) shows instruction that title hyperlinks must put the href in `job_link` and role-naming anchor text in `job_title`. Fail if `stage_meteorite` prompts never mention this shape, or only mention unrelated tasks.
2. `rg -n '\$RESPONSE_SCHEMA' data/admin/agent_task.json` shows no match inside `stage_meteorite` prompt fields. Fail if `$RESPONSE_SCHEMA` was added there.
3. `python3 -c 'from src.utils.config import STAGE_METEORITE_CONFIG; assert len(STAGE_METEORITE_CONFIG["outcomes"])==6'` exits 0. Fail if a seventh outcome was added.
4. After staging an email whose body is essentially `<a href="https://example.com/jobs/1">Senior Widget Engineer</a>` (and Ruth returns a landable URL jobs item with that `job_link` / `job_title`), the meteorite row has `link` exactly `https://example.com/jobs/1` and `job_title` `Senior Widget Engineer`. Fail if `link` is a non-http breadcrumb or NULL while that `job_link` was returned.
5. After staging the same shape when Ruth returns a **text** landable outcome but still includes http(s) `job_link` on the jobs item, the meteorite row `link` is that http URL (not a breadcrumb) and the row is on the scrape path (`state` `SCRAPE_LINK` or equivalent URL partition). Fail if `link` is still a `From:`/`To:` breadcrumb while `job_link` was http(s).
6. After staging a text landable with **no** http(s) `job_link` (classic single JD in body), `meteorite.link` remains the email breadcrumb. Fail if breadcrumb emails lose their breadcrumb.
7. Bare URL-list and Dice-style HTML paste shapes that already yield URL outcomes still produce http(s) `meteorite.link` (no regression). Fail if a previously working `link_list` / `single_jd_with_more` fixture now breadcrumb-links.
8. `diff -q` (or fixture test) between `data/admin/agent_task.json` `stage_meteorite` prompts and `docs/uat-fixtures/AST-756/expected-agent_task.json` shows the expected catalog updated in lockstep. Fail if only one side changed.

## Open questions

none

## Proposed child tickets

#### 1!: **stage_meteorite linked-title prompts - Ada**

Teach `stage_meteorite` prompts to classify title-as-href emails as URL landables (`link_list` / `single_jd_with_more`), set `job_link` from href and optional `job_title` from role-naming anchor text (omit for generic CTAs; never invent). Lockstep the AST-756 expected agent_task fixture. Does not own map breadcrumb-vs-http preference (sibling #2). Does not add a seventh outcome.
**Citations:** `patt.task.daisy-chain` (URL + title must be askable at stage so the row can carry them); `stat.logging.debug` / `stat.logging.info.entity` id-only (catalog-only child).
**Scope:** `data/admin/agent_task.json` — **modified** — `stage_meteorite` cache/user prompts teach title-as-href → `job_link` from href + `job_title` from role-naming anchor text; keep the six closed outcomes; no `$RESPONSE_SCHEMA` in prompts. `docs/uat-fixtures/AST-756/expected-agent_task.json` — **modified** — lockstep expected catalog text with the `stage_meteorite` prompt edits. Technical: update `stage_meteorite` prompt instructions so title-as-href blobs are classified as URL landables (`link_list` / `single_jd_with_more` as appropriate), each jobs item sets `job_link` from the anchor href and optional `job_title` from role-naming anchor text (omit title for generic CTAs; never invent); keep electronic-contact, breadcrumb header fields, and JOB TITLE subject-prefer rules for other shapes; leave `$RESPONSE_SCHEMA` absent. Mirror the same wording in the UAT catalog fixture.
**Estimate: 2**

#### 2: **Prefer http job_link over breadcrumb at stage map - Hedy**

When a classify jobs item carries http(s) `job_link`, write that URL onto `meteorite.link` even if the outcome string was text landable; breadcrumb only when no http job_link. Put http-linked rows on the scrape state path. Keeps staged `job_title` mapping as today. Does not edit agent_task prompts (sibling #1). after #1 for full UAT of the linked-title story.
**Citations:** `patt.task.daisy-chain` (staged `link` / title ride the row; do not invent a parallel HTML harvester); `stat.logging.debug`; `stat.logging.info.entity` id-only.
**Scope:** `src/core/meteorite.py` — **modified** — stage map / post-map wiring prefers http(s) `job_link` on `meteorite.link` over email breadcrumb when present; keeps staged `job_title` on the row as today. Technical: in the classify→row mapper (and/or the immediate post-map wiring in `stage_meteorite`), when a jobs item has an http(s) `job_link`, set the meteorite row `link` to that URL even if the classify outcome was a text landable; only call the email-breadcrumb helper when no http(s) `job_link` is present. Keep copying optional `job_title` / `employer_name` onto the row as today. When the row `link` is http(s), use the URL/scrape state path (`SCRAPE_LINK`) so scrape still runs; do not leave an http link stranded under READY solely because the outcome string was text. Do not invent a parallel HTML link harvester outside Ruth + this map preference.
**Estimate: 3**

**Monolith note:** two functional capabilities (prompt recognition + map http-prefer) across two children — matches N≥2 capabilities without a mega-ticket.

**Scope partition note:** child #1 owns catalog + fixture only; child #2 owns `src/core/meteorite.py` only — no overlapping files.

---

## Original brief

Meteorite correctly parses emails that have a list of raw links or an HTML element pasted from a webpage like [dice.com](<http://dice.com>).

It does not yet recognize the email type where the job titles are href'ed to job pages, and the link is lost when it is saved to the meteorite table.

[samplecombomessage.txt](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/103b7f1e-3980-41bd-8018-95a03bc3e259/aae995ca-86fd-448c-95f4-539cdb3df097)

### Comments

#### chuckles — 2026-09-25T16:19:40.125Z
[fix-intake] filed AST-1796 at Discussion (assignee Susan) for Susan UAT [bug] — combo JD + job-link array. Parent stays User Testing.

#### susan — 2026-09-25T16:15:01.726Z
\[bug\] See the attached sample message of a combo of job description and separate job links.  We need instruction to accommodate for this type in the response as an array of meteorites, some with job links, some with full job description contents (and link if available).

#### chuckles — 2026-09-24T18:24:28.351Z
AST-1785 REVIEW — merge-child blocked; refresh-ftr CONFLICT data/admin/agent_task.json — recalling @Ada Lovelace (AST-1784).

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/16177d858cdc50b83d1492c5daf74658/fc1ae619-f3c5-420b-b440-3dfe14ad6974/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/16177d858cdc50b83d1492c5daf74658/eba66a0d-dd5b-45d8-8545-9096d6a6a6ab/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/fa9ffc08-ac4c-4883-8469-facb8e7e9b1e/store.db` |
| Radia | review | `/home/susan/.cursor/chats/16177d858cdc50b83d1492c5daf74658/2327682e-84ee-4c14-89e2-26762d70b9f1/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1783 (parent) | ftr/AST-1783-parsing-emails-with-linked-job-titles |
| AST-1784 | sub/AST-1783/AST-1784-stage-meteorite-linked-title-prompts |
| AST-1785 | sub/AST-1783/AST-1785-prefer-http-job-link-over-breadcrumb |
| AST-1796 | sub/AST-1783/AST-1796-combo-email-mixed-jd-job-link-array |

**Epic worktree:** `astral-AST-1783/` — one active sub checked out at a time.
