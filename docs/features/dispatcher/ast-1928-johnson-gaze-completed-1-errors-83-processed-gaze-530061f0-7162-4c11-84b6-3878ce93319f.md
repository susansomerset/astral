# AST-1928 — [✅/Johnson] gaze COMPLETED: 1 error(s) / 83 processed | gaze-530061f0-7162-4c11-84b6-3878ce93319f

<!-- linear-archive: AST-1928 archived 2026-10-16 -->

## Linear archive (AST-1928)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1928/johnson-gaze-completed-1-errors-83-processed-gaze-530061f0-7162-4c11  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Johnson's gaze batch `gaze-530061f0-7162-4c11-84b6-3878ce93319f` processed 83 companies with 1 error: `trustmarkbenefits_com` went `WATCH -> ERROR_GAZE` with only `[Scrape failed]` as the reason. The batch log has no `telescope job done` line for it and nothing that says why the scrape failed. In `src/core/gazer.py` `process_gazer_batch`, `asyncio.gather(..., return_exceptions=True)` captures the real exception from `scrape_one`, but only logs it when `debug=True`. It then writes a hard-coded `failure_message="Scrape failed"` to `company_job_scan` and the outcome dict. The same generic message also covers a company with an empty `job_site`, which never gets scraped. So the cause (timeout, navigation error, blocked page, bad URL, missing job_site) is lost in production, and the company is parked in `ERROR_GAZE` with no way to triage it short of re-running with `--debug`.

## To-be

When a company's gaze scrape fails, the recorded `failure_message` and the WARNING line carry the actual reason, for example the exception class and message, or "no job_site" for a company that was never scraped. AST-104's original spec did this with `failure_message=str(e)`. Someone reading the batch report can then tell whether `trustmarkbenefits_com` needs a site/URL fix, a Playwright stability fix, or just a retry.

## Proposed steps

1. In `process_gazer_batch`, keep the exception for each failed `scrape_one` in a map keyed by `short_name`, built from the existing `results` list. Do this regardless of `debug`.
2. In the per-company failure branch, set `failure_message` (both `record_to_company_job_scan` and the outcome `message`) to `"Scrape failed: <ExceptionType>: <message>"`. Use a distinct message when the company had no `job_site` and was never scraped.
3. Make sure the caller that logs `<short_name> -> ERROR_GAZE [...]` prints that richer message unchanged.
4. Re-run gaze for `trustmarkbenefits_com` to find the real cause. If it is site- or URL-specific, that is a separate data fix, not part of this ticket.

## Component scope

* `src/core/gazer.py` (modified): `process_gazer_batch` is where the scrape exception is dropped and the generic "Scrape failed" message is written.
* `tests/component/...` gazer batch test (modified or new, Betty's call): needs to assert that a raised scrape exception's text reaches `failure_message`.

## Technical scope

* `src/core/gazer.py`: modify `process_gazer_batch`. Keep each per-company scrape exception outside the debug-only block and use it for the `failure_message` and outcome `message` in the failure branch. Also tell "scrape raised" apart from "no job_site to scrape" so each failure records its real reason. No schema change, because `company_job_scan.failure_message` is already `TEXT`.

## Ancestor candidates

- [ ] AST-104 — Track Scan Results (`docs/features/gazer/ast-104-track-scan-results.md`): defined `company_job_scan.failure_message` and specified `failure_message=str(e)` on scrape exceptions. Current code drifted to a hard-coded "Scrape failed".
- [ ] AST-622 — Gazer company gaze / job list cache debug instrumentation (`docs/features/foundation/ast-622-gazer-company-gaze-job-cache-debug-instrumentation.md`): added the debug-only `scrape failed: {r!s}` logging, which is now the only place the real reason appears.
- [ ] AST-853 — Production Playwright browser stability (`docs/features/roster/ast-853-production-playwright-browser-stability.md`): relevant only if the trustmark failure turns out to be a Playwright/browser timeout rather than a site problem.

**Open question for Susan:** should this ticket only make the failure reason visible (the steps above), or should it also cover fixing `trustmarkbenefits_com`'s scrape itself once the reason is known?

## Original report

```
2026-10-01 19:06:33  [INFO]  johnson | dispatch company starting gaze
— 46 available (batch: gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  zycic_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=4 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  e413a6be | telescope job done:
https://www.zycic.com/careers -> https://www.zycic.com/careers
fields:html
2026-10-01 19:09:34  [INFO]  starr_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  fdd883c7 | telescope job done:
https://starrcompanies.wd1.myworkdayjobs.com/careers ->
https://starrcompanies.wd1.myworkdayjobs.com/careers fields:html
2026-10-01 19:09:34  [INFO]  appschopper_com | company gaze: ingest:
new=1 duplicates=1 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  fb1a63e1 | telescope job done:
https://www.appschopper.com/jobs -> https://www.appschopper.com/jobs
fields:html
2026-10-01 19:09:34  [INFO]  guidewire_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=6 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  c1e2f4dc | telescope job done:
https://www.guidewire.com/about/careers/jobs ->
https://www.guidewire.com/about/careers/jobs fields:html
2026-10-01 19:09:34  [INFO]  trustage_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  e8c37fa2 | telescope job done:
https://trustage.wd1.myworkdayjobs.com/TruStage ->
https://trustage.wd1.myworkdayjobs.com/TruStage fields:html
2026-10-01 19:09:34  [INFO]  cbts_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  ad0d7264 | telescope job done:
https://jobs.cbts.com/careers?&location=United+States ->
https://jobs.cbts.com/careers?start=0&location=United+States&pid=1443153644689&sort_by=distance&filter_include_remote=1&filter_include_relocation=0
fields:html
2026-10-01 19:09:34  [INFO]  pyapc_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  93f55b19 | telescope job done:
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=5b00e54e-f631-447b-975a-6481e099da3b&ccId=9201533170385_2&lang=en_US
-> https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=5b00e54e-f631-447b-975a-6481e099da3b&ccId=9201533170385_2&lang=en_US
fields:html
2026-10-01 19:09:34  [INFO]  bryantx_gov | company gaze: ingest: new=0
duplicates=0 title_mismatch=24 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  43c8b545 | telescope job done:
https://www.bryantxjobs.com/postings/search ->
https://www.bryantxjobs.com/postings/search fields:html
2026-10-01 19:09:34  [INFO]  callitdev_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=19 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  0fda5aa1 | telescope job done:
https://callitdev.com/en/careers -> https://callitdev.com/en/careers
fields:html
2026-10-01 19:09:34  [INFO]  tevora_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  b39086ee | telescope job done:
https://www.tevora.com/careers/job-openings ->
https://www.tevora.com/careers/job-openings/ fields:html
2026-10-01 19:09:34  [INFO]  riskonnect_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  9f0fd5f5 | telescope job done:
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=8781b54c-a13e-4584-93c7-fc74cce40486&ccId=19000101_000001&type=MP&lang=en_US
-> https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=8781b54c-a13e-4584-93c7-fc74cce40486&ccId=19000101_000001&type=MP&lang=en_US
fields:html
2026-10-01 19:09:34  [INFO]  instem_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  98f80baf | telescope job done:
https://instem.csod.com/ux/ats/careersite/1/home?c=instem ->
https://instem.csod.com/ux/ats/careersite/1/home?c=instem fields:html
2026-10-01 19:09:34  [INFO]  simco_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=20 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  0fecf46f | telescope job done:
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=4be3542f-f62b-45bd-979e-c4d85b180551&ccId=19000101_000001&type=JS&lang=en_US
-> https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=4be3542f-f62b-45bd-979e-c4d85b180551&ccId=19000101_000001&type=JS&lang=en_US
fields:html
2026-10-01 19:09:34  [INFO]  skyline_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=9 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  ebcde0f3 | telescope job done:
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=3ac0c0b7-b658-44c7-bc43-b2da9281dece&ccId=19000101_000001&lang=en_US
-> https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=3ac0c0b7-b658-44c7-bc43-b2da9281dece&ccId=19000101_000001&lang=en_US
fields:html
2026-10-01 19:09:34  [INFO]  numeral_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=24 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  6f73b7f2 | telescope job done:
https://jobs.ashbyhq.com/numeral?embed=js ->
https://jobs.ashbyhq.com/numeral?embed=js fields:html
2026-10-01 19:09:34  [INFO]  elmhurst_edu | company gaze: ingest:
new=0 duplicates=0 title_mismatch=14 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  383b4d71 | telescope job done:
https://apply.workable.com/elmhurst-edu ->
https://apply.workable.com/elmhurst-edu fields:html
2026-10-01 19:09:34  [INFO]  ramsoft_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  3bb7f755 | telescope job done:
https://ramsoftinc.bamboohr.com/careers ->
https://ramsoftinc.bamboohr.com/careers fields:html
2026-10-01 19:09:34  [INFO]  cambrex_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  094f78da | telescope job done:
https://careers.cambrex.com/jobs?country=United%20States%7CCanada%7CMexico
-> https://careers.cambrex.com/jobs?country=United%20States%7CCanada%7CMexico
fields:html
2026-10-01 19:09:34  [INFO]  accure_net | company gaze: ingest: new=0
duplicates=0 title_mismatch=7 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  ab047202 | telescope job done:
https://accure.jobs.personio.de -> https://accure.jobs.personio.de/
fields:html
2026-10-01 19:09:34  [INFO]  mysoftheaven_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  bb0a8061 | telescope job done:
https://mysoftheaven.com/career/jobs ->
https://mysoftheaven.com/career/jobs fields:html
2026-10-01 19:09:34  [INFO]  mocdoc_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=3 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  c2eefe1f | telescope job done:
https://mocdoc.com/career-healthcare-information-management ->
https://mocdoc.com/career-healthcare-information-management
fields:html
2026-10-01 19:09:34  [INFO]  munichre_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=4 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  447efe82 | telescope job done:
https://careers.munichre.com/en/munichre ->
https://careers.munichre.com/en/munichre fields:html
2026-10-01 19:09:34  [INFO]  markupdesigns_com | company gaze: ingest:
new=1 duplicates=0 title_mismatch=3 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  f5da229e | telescope job done:
https://www.markupdesigns.com/career ->
https://www.markupdesigns.com/career/ fields:html
2026-10-01 19:09:34  [INFO]  safetyculture_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=12 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:09:34  [INFO]  a8a5fa55 | telescope job done:
https://safetyculture.com/jobs -> https://mitti.com/jobs fields:html
2026-10-01 19:11:32  [INFO]  54f04a74 | telescope job done:
https://www.preactiveit.com/jobs -> https://www.preactiveit.com/jobs
fields:html
2026-10-01 19:11:32  [INFO]  persistencemarketresearch_com | company
gaze: ingest: new=0 duplicates=0 title_mismatch=5 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  81a0c448 | telescope job done:
https://www.persistencemarketresearch.com/career ->
https://www.persistencemarketresearch.com/career fields:html
2026-10-01 19:11:32  [INFO]  indx_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  446bc078 | telescope job done:
https://eng.wd3.myworkdayjobs.com/en-us/externalcareers?q=engineering%20industries%20excellence
-> https://eng.wd3.myworkdayjobs.com/en-us/externalcareers?q=engineering%20industries%20excellence
fields:html
2026-10-01 19:11:32  [INFO]  leverx_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  1065b092 | telescope job done:
https://career.leverx.com -> https://leverx.com/cookie-declaration
fields:html
2026-10-01 19:11:32  [INFO]  godrejinfotech_com | company gaze:
ingest: new=0 duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  bb9fbdd5 | telescope job done:
https://www.godrejinfotech.com/careers/we-are-hiring ->
https://www.godrejinfotech.com/careers/we-are-hiring fields:html
2026-10-01 19:11:32  [INFO]  trgsolutions_com | company gaze: ingest:
new=0 duplicates=1 title_mismatch=23 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  1455d0fd | telescope job done:
https://recruiting.ultipro.com/TRU1012TWEST/JobBoard/b695163a-a4cd-46b6-a55a-b18d37f3031d/?q=&o=postedDateDesc&w=&wc=&we=&wpst=
-> https://recruiting.ultipro.com/TRU1012TWEST/JobBoard/b695163a-a4cd-46b6-a55a-b18d37f3031d/?q=&o=postedDateDesc&w=&wc=&we=&wpst=
fields:html
2026-10-01 19:11:32  [INFO]  dilitrust_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=28 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  42372660 | telescope job done:
https://jobs.lever.co/dilitrust -> https://jobs.lever.co/dilitrust
fields:html
2026-10-01 19:11:32  [INFO]  descartes_com | company gaze: ingest:
new=1 duplicates=0 title_mismatch=23 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  0fd3afe3 | telescope job done:
https://careers.descartes.com/join-our-team ->
https://careers.descartes.com/join-our-team/ fields:html
2026-10-01 19:11:32  [INFO]  front_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=9 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [INFO]  f27075a8 | telescope job done:
https://front.com/jobs -> https://front.com/jobs fields:html
2026-10-01 19:11:32  [INFO]  trustmarkbenefits_com | company state:
WATCH -> ERROR_GAZE (batch: gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:11:32  [WARNING]  trustmarkbenefits_com -> ERROR_GAZE
[Scrape failed]
2026-10-01 19:12:31  [INFO]  ba504147 | telescope job done:
https://danishleadco.io/job-openings ->
https://danishleadco.io/job-openings fields:html
2026-10-01 19:12:31  [INFO]  basisglobal_co | company gaze: ingest:
new=0 duplicates=0 title_mismatch=18 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  23dd35ce | telescope job done:
https://basisglobal.co/about-us/ -> https://basisglobal.co/about-us/
fields:html
2026-10-01 19:12:31  [INFO]  pvwc_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  2468d719 | telescope job done:
https://www.pvwc.com/about-pvwc/careers/job-announcements ->
https://www.pvwc.com/About-PVWC/Careers/Job-Announcements fields:html
2026-10-01 19:12:31  [INFO]  aras_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=26 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  c2b2c17a | telescope job done:
https://aras.com/en/company/careers ->
https://aras.com/en/company/careers fields:html
2026-10-01 19:12:31  [INFO]  techaheadcorp_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=5 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  1096142c | telescope job done:
https://www.techaheadcorp.com/careers ->
https://www.techaheadcorp.com/careers/ fields:html
2026-10-01 19:12:31  [INFO]  infosys_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=2 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  d8261807 | telescope job done:
https://www.infosys.com/careers/americas/graduates.html ->
https://www.infosys.com/careers/americas/graduates.html fields:html
2026-10-01 19:12:31  [INFO]  eqmssmarteye_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=3 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  faa4ddb3 | telescope job done:
https://eqms-smarteye.com/category/jobs ->
https://eqms-smarteye.com/category/jobs/ fields:html
2026-10-01 19:12:31  [INFO]  tractian_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=108 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  53f57cf5 | telescope job done:
https://careers.tractian.com -> https://careers.tractian.com/
fields:html
2026-10-01 19:12:31  [INFO]  vsplc_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=6 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  416f5c4d | telescope job done:
https://vsplc.com/careers -> https://vsplc.com/careers fields:html
2026-10-01 19:12:31  [INFO]  novacura_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=8 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  24daa9ec | telescope job done:
https://job.novacura.com -> https://job.novacura.com/ fields:html
2026-10-01 19:12:31  [INFO]  quadrupleautomation_com | company gaze:
ingest: new=0 duplicates=0 title_mismatch=4 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  ea407ce2 | telescope job done:
https://www.quadrupleautomation.com/careers ->
https://www.quadrupleautomation.com/careers fields:html
2026-10-01 19:12:31  [INFO]  aizon_ai | company gaze: ingest: new=0
duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:31  [INFO]  792592b0 | telescope job done:
https://www.aizon.ai/careers -> https://www.aizon.ai/careers
fields:html
2026-10-01 19:12:31  [INFO]  preactiveit_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:38  [INFO]  finchannel_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:12:38  [INFO]  d042059b | telescope job done:
https://finchannel.com/category/working-for-the-financial-vacancies ->
https://finchannel.com/category/working-for-the-financial-vacancies/
fields:html
2026-10-01 19:12:38  [INFO]  danishleadco_io | company gaze: ingest:
new=0 duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:37  [INFO]  wisedocs_ai | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:37  [INFO]  29ba7eac | telescope job done:
https://www.wisedocs.ai/company/careers ->
https://www.wisedocs.ai/company/careers fields:html
2026-10-01 19:13:38  [INFO]  sublimelogics_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=5 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  d54a9c08 | telescope job done:
https://www.sublimelogics.com/careers ->
https://www.sublimelogics.com/careers/ fields:html
2026-10-01 19:13:38  [INFO]  darien_il_us | company gaze: ingest:
new=0 duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  db68ebfa | telescope job done:
https://www.darien.il.us/employment ->
https://www.darien.il.us/employment fields:html
2026-10-01 19:13:38  [INFO]  mongodb_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  7bd50282 | telescope job done:
https://www.mongodb.com/company/careers/see-jobs ->
https://www.mongodb.com/company/careers/see-jobs fields:html
2026-10-01 19:13:38  [INFO]  penny_co | company gaze: ingest: new=0
duplicates=0 title_mismatch=2 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  b8a91e80 | telescope job done:
https://penny.co/careers -> https://penny.co/careers fields:html
2026-10-01 19:13:38  [INFO]  upflow_io | company gaze: ingest: new=0
duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  f78076ad | telescope job done:
https://jobs.ashbyhq.com/upflow?embed=js ->
https://jobs.ashbyhq.com/upflow?embed=js fields:html
2026-10-01 19:13:38  [INFO]  careers_envestnet_com | company gaze:
ingest: new=0 duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  5cbdf21c | telescope job done:
https://careers.envestnet.com/search/jobs ->
https://careers.envestnet.com/search/jobs fields:html
2026-10-01 19:13:38  [INFO]  delcopa_gov | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  9e275483 | telescope job done:
https://www.delcopa.gov/employment/jobs-by-title ->
https://www.delcopa.gov/employment/by-title fields:html
2026-10-01 19:13:38  [INFO]  valant_io | company gaze: ingest: new=0
duplicates=0 title_mismatch=3 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  c16bd9a1 | telescope job done:
https://careers.valant.io -> https://careers.valant.io/ fields:html
2026-10-01 19:13:38  [INFO]  thezebra_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=7 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  a78c1d5e | telescope job done:
https://www.thezebra.com/about/careers ->
https://www.thezebra.com/about/careers/ fields:html
2026-10-01 19:13:38  [INFO]  inaza_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=2 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  43b56c29 | telescope job done:
https://www.inaza.com/careers -> https://www.inaza.com/careers
fields:html
2026-10-01 19:13:38  [INFO]  labroots_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=6 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  b2de1958 | telescope job done:
https://www.labroots.com/careers -> https://www.labroots.com/careers
fields:html
2026-10-01 19:13:38  [INFO]  perceptiveanalytics_com | company gaze:
ingest: new=1 duplicates=0 title_mismatch=4 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:38  [INFO]  fe821281 | telescope job done:
https://www.perceptive-analytics.com/careers ->
https://www.perceptive-analytics.com/careers/ fields:html
2026-10-01 19:13:51  [INFO]  ssivt_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:51  [INFO]  014c5b78 | telescope job done:
https://harriscomputer.wd3.myworkdayjobs.com/en-us/s_and_s ->
https://harriscomputer.wd3.myworkdayjobs.com/en-us/s_and_s fields:html
2026-10-01 19:13:51  [INFO]  pacera_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=5 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:13:51  [INFO]  47ab8a60 | telescope job done:
https://careers.pacera.com -> https://careers.pacera.com/ fields:html
2026-10-01 19:15:35  [INFO]  eproval_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=2 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:35  [INFO]  f15638b2 | telescope job done:
https://www.eproval.com/careers -> https://www.eproval.com/careers/
fields:html
2026-10-01 19:15:36  [INFO]  elkgrove_org | company gaze: ingest:
new=0 duplicates=0 title_mismatch=4 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  0c90b549 | telescope job done:
https://www.elkgrove.org/government/human-resources-office/open-positions
-> https://www.elkgrove.org/government/human-resources-office/open-positions
fields:html
2026-10-01 19:15:36  [INFO]  getaleph_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=13 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  a78124cc | telescope job done:
https://jobs.ashbyhq.com/aleph?embed=js ->
https://jobs.ashbyhq.com/aleph?embed=js fields:html
2026-10-01 19:15:36  [INFO]  clearwatersecurity_com | company gaze:
ingest: new=1 duplicates=1 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  d60f51dd | telescope job done:
https://clearwatersecurity.com/about-us/careers ->
https://clearwatersecurity.com/about-us/careers/ fields:html
2026-10-01 19:15:36  [INFO]  intelegencia_com | company gaze: ingest:
new=2 duplicates=0 title_mismatch=20 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  7080f4e1 | telescope job done:
https://www.intelegencia.com/careers ->
https://www.intelegencia.com/careers fields:html
2026-10-01 19:15:36  [INFO]  ajg_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  7860f5c4 | telescope job done:
https://jobs.ajg.com/ajg-home/jobs ->
https://jobs.ajg.com/ajg-home/jobs fields:html
2026-10-01 19:15:36  [INFO]  genesys_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  07cacd2f | telescope job done:
https://genesys.wd1.myworkdayjobs.com/Genesys ->
https://genesys.wd1.myworkdayjobs.com/Genesys fields:html
2026-10-01 19:15:36  [INFO]  stripe_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  94a10006 | telescope job done:
https://stripe.com/jobs/search -> https://stripe.com/careers/search
fields:html
2026-10-01 19:15:36  [INFO]  v2stech_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  f639b718 | telescope job done:
https://www.v2stech.com/careers -> https://www.v2stech.com/careers
fields:html
2026-10-01 19:15:36  [INFO]  netvendor_com | company gaze: ingest:
new=0 duplicates=0 title_mismatch=9 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  169b346e | telescope job done:
https://netvendor.bamboohr.com/careers ->
https://netvendor.bamboohr.com/careers fields:html
2026-10-01 19:15:36  [INFO]  hyperexponential_com | company gaze:
ingest: new=0 duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  b66d9b56 | telescope job done:
https://www.hyperexponential.com/careers/openings ->
https://www.hyperexponential.com/careers/openings fields:html
2026-10-01 19:15:36  [INFO]  getprosper_ai | company gaze: ingest:
new=0 duplicates=0 title_mismatch=12 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  147fc9a5 | telescope job done:
https://jobs.ashbyhq.com/prosper-ai?embed=js ->
https://jobs.ashbyhq.com/prosper-ai?embed=js fields:html
2026-10-01 19:15:36  [INFO]  careers_evercommerce_com | company gaze:
ingest: new=0 duplicates=0 title_mismatch=2 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  974da120 | telescope job done:
https://careers.evercommerce.com/us/search-results ->
https://careers.evercommerce.com/us/en fields:html
2026-10-01 19:15:36  [INFO]  careers_gehealthcare_com | company gaze:
ingest: new=0 duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  9b71645b | telescope job done:
https://careers.gehealthcare.com/global/en/search-results ->
https://careers.gehealthcare.com/global/en/search-results fields:html
2026-10-01 19:15:36  [INFO]  medicat_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=2 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  4540616d | telescope job done:
https://medicat.com/category/careers ->
https://medicat.com/category/careers/ fields:html
2026-10-01 19:15:36  [INFO]  henrycountyga_gov | company gaze: ingest:
new=0 duplicates=0 title_mismatch=10 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  05280ed5 | telescope job done:
https://www.governmentjobs.com/careers/henryga ->
https://www.governmentjobs.com/careers/henryga fields:html
2026-10-01 19:15:36  [INFO]  cytora_com | company gaze: ingest: new=0
duplicates=0 title_mismatch=9 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  2daaf108 | telescope job done:
https://jobs.ashbyhq.com/cytora.com ->
https://jobs.ashbyhq.com/cytora.com fields:html
2026-10-01 19:15:36  [INFO]  techforgov_ai | company gaze: ingest:
new=0 duplicates=1 title_mismatch=3 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  cf7e5eb3 | telescope job done:
https://www.techforgov.ai/contact-us/careers ->
https://www.techforgov.ai/contact-us/careers/ fields:html
2026-10-01 19:15:36  [INFO]  latimes_com | company gaze: ingest: new=1
duplicates=0 title_mismatch=7 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:36  [INFO]  eeba7685 | telescope job done:
https://www.dayforcehcm.com/CandidatePortal/en-US/nantmedia ->
https://jobs.dayforcehcm.com/nantmedia/CANDIDATEPORTAL fields:html
2026-10-01 19:15:41  [INFO]  johnson | dispatch company task
completed: gaze pass:82 fail:0 error:1 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:41  [INFO]  johnson | dispatch company stopping gaze
— 19 remaining after 83 run(s)
2026-10-01 19:15:41  [INFO]  gurnee_il_us | company gaze: ingest:
new=0 duplicates=0 title_mismatch=0 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:41  [INFO]  5af64987 | telescope job done:
https://www.gurnee.il.us/residents/i-want-to/apply-for-a-job ->
https://www.gurneeil.gov/residents/i-want-to/apply-for-a-job
fields:html
2026-10-01 19:15:41  [INFO]  mmlonline_com | company gaze: ingest:
new=1 duplicates=0 title_mismatch=20 (batch:
gaze-530061f0-7162-4c11-84b6-3878ce93319f)
2026-10-01 19:15:41  [INFO]  35fad1fa | telescope job done:
https://www.mmlonline.com/job-opportunities ->
https://www.mmlonline.com/job-opportunities fields:html
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
