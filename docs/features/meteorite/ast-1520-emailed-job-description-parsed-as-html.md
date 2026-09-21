# AST-1520 — Emailed job description parsed as HTML

<!-- linear-archive: AST-1520 archived 2026-09-09 -->

## Linear archive (AST-1520)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1520/emailed-job-description-parsed-as-html  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Sorry, before you revise the as-is/to-be content, please RESPOND to my question.

I want to understand the logical progression of email parsing.

Is it:

1. Is it from our candidate? (From == bound email)
   1. if Yes, Does it have a subject? (e.g. "Fwd…" or "http…")
      1. If yes, is the subject a pure URL? (http://…)
         1. If yes, does the email have text a body?
            1. If yes, then TREAT THE LINK as the job_link and the body as the Job Description text and set it for qualification.
            2. If no, can playwright scrape the visible text (no links) frost m that url?
               1. If yes, then treat the link as the job_link and the scraped visible text as the job description content and set it for qualification
               2. If no, then set the link as a job_link, create the job, and set it to state "BOT_BLOCKED" so that a human can provide the jd content in the ui later.
         2. if no, then are there any hyperlinks in the body of the message?
            1. If Yes, then can playwright scrape the visible text from that link?
               1. If yes, then APPEND the visible text to the email's body and save the whole thing in the JD text for the new job, set for qualification
               2. If no, then just store the email body with the subject prepended in the job description and set for qualification.
            2. if no, then just store the email body with the subject prepended in the job description and set for qualification
   2. If no, does the body contain pure HTML elements, as if it were copied from an inspector?
      1. if yes, then can we parse individual links from the email body?
         1. If yes, can playwright scrape the pages email body for the jd text?
            1. If yes, create one job per link with the jd text.
            2. If no, create one job per link with state = 'BOT_BLOCKED', no jd
         2. If no, then store the email body in the job description and set for qualification.
      2. If no, then store the email body in the job description and set for qualification.
2. if no (but it is bound to a candidate), then are there any hyperlinks in the body of the message?
   1. If Yes, then can playwright scrape the visible text from that link?
      1. If yes, then APPEND the visible text to the email's body and save the whole thing in the JD text for the new job, set for qualification
      2. If no, then just store the email body with the subject prepended in the job description and set for qualification.
   2. if no, then just store the email body with the subject prepended in the job description and set for qualification

There. That ought to do the trick. Then from that state, the "Ruth, what the heckaroony is this?" message with the new job record can be as complete as possible.

---

I overstated the importance of one issue over the other. The MAIN issue is that an email with just a JD text is not getting ingested properly.

We recently wrote some code for a meteorite endpoint that could receive a blob of text and ask the agent to parse it into a job object. Can we rewire the meteorite_email to use that ingress point?

A candidate emailed a job description (with no subject), and the response from meteorite_email tried to parse html links.

```
[2026-08-27 02:14:00] INFO src.core.agent: run_next chain entry: task=meteorite_email batch_id=meteorite_email-3c1a7593-186f-4018-ae28-a8ef0ac79001
[2026-08-27 02:14:00] INFO src.external.deepseek: LLM deepseek task=meteorite_email 1.2s stop=end_turn tokens in=209 out=108
[2026-08-27 02:14:00] INFO src.core.agent: do_task(meteorite_email) completed successfully batch_id=meteorite_email-3c1a7593-186f-4018-ae28-a8ef0ac79001 index=1a03a664b0c21704
```

It also did not archive the message in the gmail inbox. It shoudl have EITHER errored and left the message in the inbox, OR, completed successfully and archived the message.

In this case, it ERRONEOUSLY completed successfully AND didn't archive the message.

Please tell me how the meteorite_email function decides which fork to take before calling the agent for discernment?

## Fork logic — answer to Susan's question

**Short answer:** No — today's code does not follow your tree. It uses **four coarse shapes** decided entirely inside `_handle_bound` in `src/core/meteorite_email.py` from **subject text + body empty/non-empty + subject-is-URL**, then calls Ruth on two of them **before** any scrape/land decision. It does **not** call `land_meteorite`, does **not** create `BOT_BLOCKED` jobs on scrape failure, and does **not** append scraped link text into a JD blob the way your tree describes.

**What runs before** `_handle_bound`**: **`run_meteorite_email` lists the inbox. Unbound mail (From matches no candidate) is ignored or Trashed after retention — never ingested. Mail bound to a **different** candidate is skipped. Only mail whose `candidate_match.matched` and `astral_candidate_id` equals **this dispatch row's candidate** enters `_handle_bound`.

**What** `_handle_bound` **actually does (in order):**

| Step | Condition | What happens | Maps to your tree? |
| -- | -- | -- | -- |
| A | Non-empty subject, subject **not** a URL, empty body | **ignore** — leave inbox, count pass | Partial: empty body with subject only |
| B | Empty subject **and** empty body | **ignore** | — |
| C | Empty subject, **non-empty body** | `html_links` — assemble visible text + `--- LINKS ---`, call Ruth (`do_task meteorite_email`), ingest **only** Ruth `jobs[]` rows with a `job_link` (Playwright scrape per link via `_ingest_link`; skip if short/duplicate) | **Your failing case lands here.** Your tree's "no subject → plain JD text → land body" is **not** this branch's fallback; zero-link Ruth success → zero outcomes → `ignored-empty` pass, inbox unchanged |
| D | Subject **is** a URL (`http`/`https`), empty body | `subject_url` — `_ingest_link(subject)` scrape only; no Ruth | Partial: your "URL subject, no body → scrape URL" only |
| E | Non-empty subject, non-empty body (including URL subject **with** body) | `subject_body` — Ruth first; if Ruth returns `jd_link` → scrape that link with body as suffix; else if Ruth `content_text` or `subject+body` long enough → `create_meteorite_job` (legacy, not `land_meteorite`) | Partial: your "subject + body" / link-in-body paths, but Ruth decides links, no BOT_BLOCKED, no append-scrape-to-body |
| F | Anything else | **ignore** | — |

**Gaps vs your tree (not implemented today):**

* No `land_meteorite(text=…)` ingress — JD-as-text paths should use your new blob parser, not Ruth `html_links` alone.
* No `BOT_BLOCKED` create when Playwright cannot scrape.
* No **append scraped link visible text to email body** then single-JD land.
* No **inspector/pasted-HTML** detection — no-subject + body always → `html_links` regardless of link count.
* URL subject **with** body goes to `subject_body` **+ Ruth**, not "treat subject as job_link and body as JD" directly.
* Your outer numbered item **"2. if no (but it is bound…)"** does not match a separate code path — if you meant **no subject**, that is already branch C above; if you meant **not bound to this candidate**, the message never reaches `_handle_bound`.

**Your reported email:** bound candidate, **no subject**, JD text body → branch **C (**`html_links`**)** → Ruth called → likely empty/zero-link `jobs` → nothing ingested → `_finalize_archive([])` → inbox kept, dispatcher still passes.

**Approved ancestor:** Susan checked **AST-1472**, which retargeted inbox `fetch_email` → `land_meteorite` via `inbox._land_bound_inbox_message` and explicitly deferred `src/core/meteorite_email.py` ("per-candidate mailbox poller stays as-is"). This bug completes that deferred gap on the candidate-bound dispatcher path, plus Gmail archive/trash outcomes `fetch_email` does not own.

## As-is

Bound `meteorite_email` still uses the four-shape Ruth-first fork above. Plain JD text with no subject is forced through `html_links` **+ Ruth**, not `land_meteorite`. When Ruth succeeds but returns no scrapeable links, ingest is empty, the message is not archived, and the run still counts as passed — while `fetch_email` (AST-1472) already lands bound mail through `land_meteorite(candidate_id, text=…)` for the same inbox content shape.

## To-be

`meteorite_email` follows Susan's decision tree (preserved above), using `land_meteorite` as the JD-text ingress the way AST-1472 established for `fetch_email` — not a second enrich pipeline. Playwright scrape success/failure branches land with link+text or `BOT_BLOCKED` per the tree; multi-link inspector pastes land one job per link. After successful land (or acceptable duplicate skip), **archive** the Gmail message; on error, **leave inbox** and fail the run. Ruth / "what the heckaroony" runs **after** the job record exists with assembled JD content. Reuse AST-1470 `land_meteorite` and mirror AST-1472 field-mapping discipline; do **not** edit `inbox.py` / `gazer.py` except shared helper extraction if plan-fix finds DRY without scope creep.

## Proposed steps

1. `plan-fix` against `docs/features/meteorite/ast-1472-inbox-fetch-email-gaze-email-retarget.md` + Susan's tree — stage `_handle_bound` rewrite in `meteorite_email.py` only (AST-1472 scope gate explicitly excluded this file; bug-fix owns the completion).
2. Replace Ruth-first `html_links` for no-subject JD text with `await land_meteorite(cid, text=visible_text, job_link=…)` (same late-import / kwargs spirit as `inbox._land_bound_inbox_message`).
3. Implement remaining tree branches (URL subject + body, body links → scrape append → land, inspector multi-link, `BOT_BLOCKED` on scrape fail) — confirm Tracker/state API at plan-fix or file gap child.
4. Map land rollup outcomes + archive via existing `archive_message`; error → inbox stays, dispatcher fail (fix `_finalize_archive` empty-outcomes pass).
5. Betty: component matrix starting with reported case (no-subject JD text → land + archive); reuse AST-1472 land-outcome fixtures where applicable.

## Component scope

* `src/core/meteorite_email.py` — complete AST-1472's deferred retarget: replace `_handle_bound` routing with Susan's tree + `land_meteorite`; keep unbound Trash / `last_email_check` stamp owned here (not in inbox `fetch_email`).
* `src/core/meteorite.py` — read-only expected (`land_meteorite` already public from AST-1470); call it, do not fork enrich.
* `src/core/inbox.py` — read-only preferred; optional shared land helper extraction only if plan-fix proves DRY without widening AST-1472 footprint.
* `src/utils/config.py` — modify only if routing literals belong in `METEORITE_EMAIL_*_CONFIG`.
* Component tests under `tests/component/core/` — Betty owns; meteorite_email land + archive regressions (AST-1472 test patterns in `test_inbox.py` are reference, not edit target unless shared helper moves).

## Technical scope

* `src/core/meteorite_email.py` — **major modified** `_handle_bound`: Susan's bind → subject → URL → links → scrape → `land_meteorite` / BOT_BLOCKED progression; **modified** `_finalize_archive`: land success → archive, error → inbox + fail (no pass-without-ingest). **Modified** `run_meteorite_email`: unchanged list/bind/filter; outcomes driven by new `_handle_bound` returns.
* `src/core/meteorite.py` — **no change expected**; consume existing `land_meteorite(text=, job_link=, scraps=)`.
* `src/utils/config.py` — **optional config keys** for shape-detection thresholds if statute requires.
* Component tests — **new cases** in meteorite_email suite: no-subject JD text, URL+body, scrape-fail BOT_BLOCKED, multi-link inspector paste.

## Ancestor candidates

- [X] AST-1472 — inbox fetch_email retarget to land_meteorite (**Susan approved** — direct precedent; explicitly deferred meteorite_email.py; this bug completes that gap)
- [ ] AST-1470 — land_meteorite core (text blob → enrich → Tracker save; dependency of AST-1472)
- [ ] AST-1457 — Meteorite component parent epic
- [ ] AST-1471 — meteorite intake API + Contact land path (adjacent API wrapper)
- [ ] AST-1136 — candidate-bound meteorite_email runner (_handle_bound / archive / unbound hygiene originally landed here)
- [ ] AST-1182 / AST-1213 — legacy Ruth html_links / subject_body modes being replaced

### Comments

#### cursor — 2026-08-27T02:58:36.180Z
[**Meteorite email jd flow**](<https://www.cursor.com/agents/bc-103abc90-04ed-41ab-9255-d1182cfcd761>)

Fixed AST-1520 in draft PR [#48](<https://github.com/susansomerset/astral/pull/48>).

## What was broken

Your reported email (bound candidate, **no subject**, JD text body) hit the old `html_links` branch → Ruth ran → returned no scrapeable links → **zero ingest outcomes** → `_finalize_archive([])` treated it as a pass (`ignored-empty`) → message stayed in Gmail while the dispatcher counted success.

## New fork logic (before any Ruth call)

`_handle_bound` now follows your tree using `land_meteorite` as the default JD-text ingress:

| Condition | Route | Archive on success? |
| -- | -- | -- |
| Non-URL subject + empty body | ignore | n/a |
| Both empty | ignore | n/a |
| URL subject + body | `land_meteorite(link=subject, text=body)` | yes |
| URL subject + empty body | scrape → land; scrape fail → **BOT_BLOCKED** | yes |
| Subject + body + links | scrape first link (+ subject/body suffix) | yes |
| Subject + body, no links | `land_meteorite` | yes |
| No subject + inspector HTML (≥2 links or `<html>`/`<body>`) | per-link scrape/land | yes |
| No subject + plain JD text | `land_meteorite` (`shape=plain_jd`) | yes |

Ruth is **no longer** the first fork for plain text. Ruth helpers remain in the module for tests/back-compat but bound routing does not call them.

## Archive contract fix

* **Before:** empty outcomes → pass, inbox unchanged
* **After:** empty or all-error outcomes → **error count**, inbox unchanged
* Created or all-duplicate-skip → archive (unchanged)

## Tests

33/33 passing in `tests/component/core/test_meteorite_email.py`, including new `TestAst1520PlainJdLandMeteorite` covering the exact failing case (plain JD lands + archives; land failure leaves inbox + errors).

**Repository:** `susansomerset/astral`
**Branch:** `chuckles-ast1520-email-jd-land-d761`

[View PR](<https://github.com/susansomerset/astral/pull/48>) · [Open in Desktop](<https://cursor.com/background-agent?bcId=bc-103abc90-04ed-41ab-9255-d1182cfcd761>) · [Open in Web](<https://www.cursor.com/agents/bc-103abc90-04ed-41ab-9255-d1182cfcd761>)

#### unknown — 2026-08-27T02:51:16.411Z
This thread is for an agent session with Cursor. [View on Cursor →](https://www.cursor.com/agents/bc-103abc90-04ed-41ab-9255-d1182cfcd761)

---

_Implementation detail may live in git history on `origin/dev`._
