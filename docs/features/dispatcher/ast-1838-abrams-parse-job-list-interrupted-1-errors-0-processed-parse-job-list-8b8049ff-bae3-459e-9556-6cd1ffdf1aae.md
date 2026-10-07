# AST-1838 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae

<!-- linear-archive: AST-1838 archived 2026-10-07 -->

## Linear archive (AST-1838)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1838/abrams-parse-job-list-interrupted-1-errors-0-processed-parse-job-list  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

A production `parse_job_list` batch (`parse_job_list-8b8049ff-…`, candidate abrams, 20 companies) froze the dispatcher's event loop for about 2 hours 5 minutes, and then the batch ended INTERRUPTED with `TimeoutError: dispatch timeout after 3600s` and 0 companies processed.

What the log shows:

* At 10:28:04, telescope returned the Volvo Group careers page (`jobs.volvogroup.com`). It had `visible_chars: 3,149,938`, with roughly 7.4MB of HTML.
* The next log line is at 12:33:26. Nothing was logged for 2h05m. After that, every queued telescope job completed at once, and each reported `wait_ms` of about 7.7 million ms. Their results had been sitting ready, but nothing on the loop could collect them.
* The 3600s dispatch `wait_for` did not fire at 11:24, one hour after the start. It fired at 12:34:30, the first time the loop got control back. That is the signature of a synchronous call blocking the event loop, not of a slow network call.
* Root cause: `run_parse_job_list_dispatch` → `_scrape_and_parse` calls `_culled_dom_for_parse` synchronously inside the coroutine. That calls `find_job_containers` in `src/utils/formatting.py`, which parses the whole DOM with BeautifulSoup `html.parser` and then runs `el.get_text()` for **every descendant**, once in Phase 1 and again in Phase 2. It also runs nested `descendants` scans to pick the deepest matches. On a 7.4MB DOM, this is quadratic work on the event-loop thread.
* A side effect was already visible at 10:25:55: `Task was destroyed but it is pending!` for `telescope-result-poller` (`src/external/telescope.py:278`) and for a `to_thread` task. It is not yet confirmed whether this is the same starvation or a separate lifecycle bug. See the open question below.

## To-be

* One oversized careers page cannot freeze the dispatcher. DOM culling for `parse_job_list` must never run CPU-heavy work on the event loop, and on large DOMs it must finish in roughly linear time.
* Dispatch timeouts and per-call provider budgets (AST-1189) fire on schedule, because the loop is never starved.
* The other companies in the batch still get processed. The heavy company either culls successfully or fails through the existing `_save_parse_dispatch_failure` / retry-strike path (AST-891 contract). It does not take the whole batch down to INTERRUPTED with 0 processed.

## Proposed steps

1. Rewrite `find_job_containers` so each element's lowercased text is computed once, bottom-up in a single post-order pass. Title-set membership per element is then derived from that cached text, which removes the `get_text()`-per-descendant quadratic. The "deepest all-match" selection and the Phase 2 sibling union keep their current semantics, using the cached sets instead of rescanning `descendants`.
2. Move the `_culled_dom_for_parse` calls inside the async paths off the event loop with `await asyncio.to_thread(...)`. There are three: `run_parse_job_list_dispatch._scrape_and_parse`, `_finalize_joblist_titles_after_chain`, and `_finalize_joblist_titles_select_only`. That way, even a slow parse cannot block timeouts, telescope polling, or sibling companies.
3. **Susan (2026-09-28):** add a cull criterion to `_cull_html` (`src/external/telescope.py`, the `scrape_page` html cull): any tag attribute value longer than `max_html_tag_length` (`ASTRAL_CONFIG["html_cull"]`, `src/utils/config.py`, set to 500) is replaced with `max_length_placeholder` (`"(snipped)"`), so snipped spots stay visible in the DOM. Stored binary/base64 data in attributes likely inflated the 7.4MB DOM. Culling then proceeds on what's left.
4. Add a component test that builds a large synthetic DOM with thousands of nested nodes and asserts `find_job_containers` returns the same containers as before on the existing fixtures. Also add one async test showing that a slow cull does not block a concurrent coroutine.
5. **Susan (2026-09-28): no DOM-size guard.** The attribute-length snip in step 3 is expected to resolve the oversized DOM.
6. Investigate the `telescope-result-poller` "Task was destroyed but it is pending" error only as far as confirming whether steps 1–3 remove it. If it survives, it becomes a separate bug.

## Component scope

* `src/utils/formatting.py` (modified): `find_job_containers` is where the quadratic BeautifulSoup walk lives. It needs a single-pass text/title cache.
* `src/core/roster.py` (modified): `_scrape_and_parse` inside `run_parse_job_list_dispatch`, `_finalize_joblist_titles_after_chain`, and `_finalize_joblist_titles_select_only` call `_culled_dom_for_parse` synchronously from async code. They need to offload it to a worker thread. The sync `make_locate_parse_resolver` callback stays sync.
* `src/external/telescope.py` (modified): `_cull_html` snips over-long attribute values to the placeholder; `_in_preserved_svg` becomes identity-based (never hashes a Tag); `extract_page_dom` offloads `_cull_html` to a worker thread. **Susan (2026-09-28): amended as written** — admin workbench `_cull_html` calls (\~629/631) left out.
* `src/utils/config.py` (modified): `ASTRAL_CONFIG["html_cull"]` gains `max_html_tag_length: 500` and `max_length_placeholder: "(snipped)"`.
* `tests/component/utils/test_formatting.py` (modified): add a large-DOM equivalence/performance case next to the existing `find_job_containers` tests.
* `tests/component/core/test_roster.py` (modified): existing tests monkeypatch `find_job_containers` and call `_culled_dom_for_parse` directly. They need to keep passing once the calls become `to_thread`, and they need one new non-blocking assertion.

## Technical scope

* `src/utils/formatting.py`: modified function `find_job_containers`. Replace per-element `get_text()` calls with one post-order pass that caches each Tag's matched-title set, so Phase 1 and Phase 2 run in roughly linear time over the DOM without changing which containers are returned.
* `src/core/roster.py`: modified functions `run_parse_job_list_dispatch` (inner `_scrape_and_parse`), `_finalize_joblist_titles_after_chain`, and `_finalize_joblist_titles_select_only`. Wrap the `_culled_dom_for_parse` call in `asyncio.to_thread` so CPU-bound culling never runs on the dispatcher's event loop. `_culled_dom_for_parse` itself stays a pure sync function.
* `src/external/telescope.py`: modified function `_cull_html`. After existing attribute stripping, replace any remaining attribute value whose length exceeds `html_cull.max_html_tag_length` with `html_cull.max_length_placeholder`; both keys required config (no in-code defaults).
* `src/external/telescope.py` — `_cull_html`: make `_in_preserved_svg` identity-based (return early on an empty set, otherwise compare by `id()`) so it never hashes a Tag. Same output, linear cost.
* `src/external/telescope.py` — `extract_page_dom`: modified to `await asyncio.to_thread(_cull_html, raw_html)` so the html cull never runs on the event loop.
* `src/utils/config.py`: two new keys in `ASTRAL_CONFIG["html_cull"]`.
* Tests: new test cases only, with no new fixtures or tables.

## Ancestor candidates

- [ ] AST-827 — Title handoff and DOM culling for parse_job_list (`docs/features/roster/ast-827-title-handoff-dom-cull.md`). Introduced `_culled_dom_for_parse` and the title-driven cull that blocks here.
- [ ] AST-891 — parse_job_list browser pressure and batch completion (`docs/features/roster/ast-891-parse-job-list-browser-and-batch.md`). Owns the contract that a batch finishes every claimed company and does not sit for a full dispatch timeout, which is exactly the contract broken here.
- [ ] AST-890 — parse_job_list error causing infinite loop (`docs/features/roster/ast-890-parse-job-list-error-causing-infinite-loop.md`). Parent of AST-891, with the same "batch stalls the roster pipeline" symptom family.
- [ ] AST-1189 — Provider call budget timeout failure class (`docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md`). Its per-call budget in `await_provider_call_with_budget` appears in this traceback and was also starved, but it is a victim, not the cause.
- [ ] AST-327 — Refactor task dispatcher to run independent threads (`docs/features/dispatcher/ast-327-refactor-task-dispatcher-independent-threads-plan.md`). Dispatcher threading model and the wait_for timeout that fired an hour late.

## Open questions for Susan

* ~~DOM-size guard~~: resolved, none (Susan 2026-09-28).
* Telescope poller destroyed-task error: no answer, so it stays as written in step 6 (confirm only; if it survives, it becomes a separate bug).

---

## Original report

2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>) fields=text,html
 careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>)
 titles=\["Physician Assistant", "Phlebotomist/Lab Tech", "Clinical
 Research Coordinator – Illinois", "Clinical Research Coordinator –
 Texas", "Clinical Research Coordinator – New Jersey", "Clinical
 Research Coordinator – North Carolina"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[13/20\] revivalresearch_org
 state=JOBLIST_IDENTIFIED url=[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://jobs.rcpsych.ac.uk](<https://jobs.rcpsych.ac.uk>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://jobs.rcpsych.ac.uk](<https://jobs.rcpsych.ac.uk>) fields=text,html careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://jobs.rcpsych.ac.uk](<https://jobs.rcpsych.ac.uk>)
 titles=\["Forensic Psychiatrists", "Senior Staff Specialist or Staff
 Specialist or Senior Medical Officer (Psychiatrist - Intellectual and
 Developmental Disability) (Bundaberg)", "Consultant Child and
 Adolescent Psychiatrist", "Senior Staff Specialist or Staff Specialist
 or Senior Medical Officer (Psychiatrist) (Hervey Bay and
 Maryborough)", "Clinical Director and Staff Specialist in Mental
 Health CCLHD"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[12/20\] rcpsych_ac_uk
 state=JOBLIST_IDENTIFIED url=[https://jobs.rcpsych.ac.uk](<https://jobs.rcpsych.ac.uk>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://rogersbh.org/careers](<https://rogersbh.org/careers>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://rogersbh.org/careers](<https://rogersbh.org/careers>) fields=text,html careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://rogersbh.org/careers](<https://rogersbh.org/careers>)
 titles=\["Mental Health Technician – Residential, Overnight",
 "Registered Nurse", "Therapist – Part Time/PRN"\]
 state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[11/20\] rogersbh_org
 state=JOBLIST_IDENTIFIED url=[https://rogersbh.org/careers](<https://rogersbh.org/careers>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://reviveresearch.org/careers](<https://reviveresearch.org/careers>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://reviveresearch.org/careers](<https://reviveresearch.org/careers>) fields=text,html
 careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://reviveresearch.org/careers](<https://reviveresearch.org/careers>)
 titles=\["CLINICAL RESEARCH COORDINATOR", "Research Regulatory
 Coordinator", "Clinical Research Medical Assistant", "MEDICAL
 ADMINISTRATIVE ASSISTANT", "Research Intern"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[10/20\] reviveresearch_org
 state=JOBLIST_IDENTIFIED url=[https://reviveresearch.org/careers](<https://reviveresearch.org/careers>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)
 fields=text,html careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)
 titles=\["Medical Assistant", "Patient Account Representative",
 "Environmental Svcs Worker", "Full Time - Surgical Scheduler -
 Orthopedics", "Transporter"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[9/20\] northwell_edu_2
 state=JOBLIST_IDENTIFIED
 url=[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://www.bcchr.ca/careers](<https://www.bcchr.ca/careers>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://www.bcchr.ca/careers](<https://www.bcchr.ca/careers>) fields=text,html careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://www.bcchr.ca/careers](<https://www.bcchr.ca/careers>)
 titles=\["Manager, Research IT, BC Children’s Hospital Research
 Institute"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[8/20\] bcchr_ca state=JOBLIST_IDENTIFIED
 url=[https://www.bcchr.ca/careers](<https://www.bcchr.ca/careers>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)
 fields=text,html careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)
 titles=\["PMO Manager", "Senior Property Accountant IV", "Systems
 Administrator III", "Billing Analyst", "Program Manager", "Application
 Support Analyst (SQL)", "Account Manager (Residential)", "SaaS
 Implementation Consultant (NA Hours)", "Project Scoping Specialist (UK
 Hours)", "Director - Product Management"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[7/20\] mrisoftware_com
 state=JOBLIST_IDENTIFIED
 url=[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>) fields=text,html
 careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)
 titles=\["Neurodiagnostic Technologist II – Epilepsy Monitoring
 (Nights)", "Neurodiagnostic Technologist II – EMU (3–12 hour shifts)",
 "Laboratory Services Manager – Blood Bank"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[6/20\] utmb_edu_2
 state=JOBLIST_IDENTIFIED url=[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://sc.edu/about/employment](<https://sc.edu/about/employment>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://sc.edu/about/employment](<https://sc.edu/about/employment>) fields=text,html
 careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://sc.edu/about/employment](<https://sc.edu/about/employment>)
 titles=\["Assistant Director, Facilities"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[5/20\] sc_edu state=JOBLIST_IDENTIFIED
 url=[https://sc.edu/about/employment](<https://sc.edu/about/employment>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://www.volvogroup.com/en/careers/job-openings.html](<https://www.volvogroup.com/en/careers/job-openings.html>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://www.volvogroup.com/en/careers/job-openings.html](<https://www.volvogroup.com/en/careers/job-openings.html>)
 fields=text,html careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://www.volvogroup.com/en/careers/job-openings.html](<https://www.volvogroup.com/en/careers/job-openings.html>)
 titles=\["Transport Analyst", "Accountant - R2R", "2027 Ausbildung
 Fachkraft (m/w/d) für Lagerlogistik", "Conseiller(e) Service Clients
 Atelier Poids-Lourds H/F - CDI", "Thesis work: Calculation of service
 intervals", "Jobstudent Talent Acquisition", "VIE - Adaptation buyer
 H/F", "Aprendiz Senai", "Senior Software Engineer", "Senior System
 Performance Engineer"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[4/20\] volvogroup_com_2
 state=JOBLIST_IDENTIFIED
 url=[https://www.volvogroup.com/en/careers/job-openings.html](<https://www.volvogroup.com/en/careers/job-openings.html>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>) fields=text,html
 careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>) titles=\["Senior Open-Source
 Python Engineer, ML Developer Tools - EMEA Remote", "Senior
 Open-Source Python Engineer, ML Developer Tools - US Remote", "Senior
 Machine Learning Engineer, Voice Agents - EMEA Remote", "Low-Level
 Senior Software Engineer, Xet Storage - US Remote", "Low-level Senior
 Software Engineer, Xet Storage - EMEA Remote", "Open-Source Machine
 Learning Engineer - US Remote", "Wild Card"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[3/20\] huggingface_co
 state=JOBLIST_IDENTIFIED url=[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>) fields=text,html
 careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>) titles=\["Staff Scientist
 I", "Deputy Director, Division of Extramural Research", "Staff
 Clinician", "Administrative Technician", "Biologist Scientist
 Administrator (Scientific Review Officer)", "Health Scientist
 Administrator (Program Officer)", "Lead Nuclear Medicine
 Technologist", "Mechanical Engineer", "Royalties Analyst",
 "Supervisory Data Scientist"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[2/20\] training_nih_gov
 state=JOBLIST_IDENTIFIED url=[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>)
 2026-09-28 10:24:56  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:24:56  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>) fields=text,html
 careers_list=True\]
 2026-09-28 10:24:56  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>) titles=\["Technical Site
 Lead  - SEI Customer Site - Fort Meade, MD", "Senior Solutions
 Engineer", "Solutions Engineer", "Technical Engagement Lead",
 "Executive Assistant to the Chief Financial Officer", "Software
 Engineer", "Senior Real-Time Embedded Software Engineer", "Senior
 Embedded Software Engineer", "Real-Time Embedded Software Engineer",
 "IT Support Associate"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:24:56  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[1/20\] cmu_wd5_myworkdayjobs_com
 state=JOBLIST_IDENTIFIED url=[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>)
 2026-09-28 10:24:56  \[DEBUG\]  1291: Beginning parse_job_list loop on 20 items
 2026-09-28 10:24:56  \[DEBUG\]  112: Calling
 roster.parse_job_list_batch:
 \[batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae, n=20\]
 2026-09-28 10:24:56  \[DEBUG\]  827: Calling consult.run_consult_task:
 \[entity_type=company, state=JOBLIST_IDENTIFIED, n=20,
 batch=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 task_key=parse_job_list\]
 2026-09-28 10:24:56  \[DEBUG\]  757: End company claim loop after 20 items
 2026-09-28 10:24:56  \[DEBUG\]  756: Beginning company claim loop on 20 items
 2026-09-28 10:24:56  \[DEBUG\]  750: Response from
 get_new_company_batch: 20 entities
 batch=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae
 2026-09-28 10:24:56  \[DEBUG\]  730: Calling get_new_company_batch:
 \[state=JOBLIST_IDENTIFIED, limit=20, candidate_id=abrams,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 sort_by=updated_at, scan_interval_hours=None, score_floor=None,
 states=\["JOBLIST_IDENTIFIED", "JOBLIST_IDENTIFIED_RETRY"\]\]
 2026-09-28 10:24:56  \[DEBUG\]  903: Calling \_run_unified:
 \[task_key=parse_job_list, batch_size=20, entity_type=company,
 trigger_state=JOBLIST_IDENTIFIED\]
 2026-09-28 10:24:56  \[DEBUG\]  1535: Calling \_run_task:
 \[task_key=parse_job_list, available=253\]
 2026-09-28 10:24:56  \[DEBUG\]  1486: Beginning dispatch loop on 253 items
 2026-09-28 10:24:56  \[DEBUG\]  1369: Calling \_run_dispatch_loop:
 \[task_key=parse_job_list, available=253,
 entity_batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae\]
 2026-09-28 10:24:56  \[INFO\]  abrams | dispatch company starting
 parse_job_list — 253 available (batch:
 parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae)
 2026-09-28 10:24:57  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[14/20\] pesi_com state=JOBLIST_IDENTIFIED
 url=[https://www.pesi.com/careers](<https://www.pesi.com/careers>)
 2026-09-28 10:24:57  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 5147, "visible_chars": 2001,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 10:25:01  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>)", "text":
 "\\nSkip to main contentSearchFiltersCityJob FunctionPosition
 TypeMoreSearch for Jobs page is loaded47 JOBS FOUNDJump to selected
 job detailsTechnical Site Lead  - SEI Customer Site - Fort Meade,
 MDlocationsLinthicumposted onPosted 4 Days Ago2025134Senior Solutions
 Engineerlocations2 Locationsposted onPosted 6 Days Ago2025117Solutions
 Engineerlocations2 Locationsposted onPosted 6 Days Ago2025119Technical
 Engagement LeadlocationsPittsburgh, PAposted onPosted 11 Days
 Ago2024913Executive Assistant to the Chief Financial
 OfficerlocationsPittsburgh, PAposted onPosted 12 Days
 Ago2025107Software EngineerlocationsPittsburgh, PAposted onPosted 14
 Days Ago2025049Senior Real-Time Embedded Software
 EngineerlocationsPittsburgh, PAposted onPosted 18 Days
 Ago2023158Senior Embedded Software EngineerlocationsPittsburgh,
 PAposted onPosted 20 Days Ago2024810Software
 EngineerlocationsPittsburgh, PAposted onPosted 25 Days
 Ago2024794Real-Time E<89290 chars
 omitted>s/jsd/main.js';document.getElementsByTagName('head')\[0\].appendChild(a);";b.getElementsByTagName('head')\[0\].appendChild(d)}}if(document.body){var
 a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else
 if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var
 e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();</script><iframe
 height="1" width="1" style="position: absolute; top: 0px; left:
 0px; border: medium; visibility: hidden;"></iframe>\\n</body>",
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 2001, "requested_url":
 "[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>)", "final_url":
 "[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>)"}}
 2026-09-28 10:25:01  \[INFO\]  0f74ce6a | telescope job done:
 [https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>) ->
 [https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>) fields:text,html
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 8c6d1153-bce7-4bb1-8aaa-71921f4009e9: {"url":
 "[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 16fe6019-e2be-4432-bb20-22efd2226de1: {"url":
 "[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 6ac62384-f858-4e79-b361-590a625f116c: {"url":
 "[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 fe10011a-b9dd-4aa4-9eca-8407f8c4225a: {"url":
 "[https://drugfree.org/article/work-at-the-partnership](<https://drugfree.org/article/work-at-the-partnership>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 3b0863d9-34bf-4c50-8bc5-28b40ba74cbf: {"url":
 "[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 1324363e-790c-4904-9f94-96f65784af41: {"url":
 "[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 bdbced09-5e95-43dd-89c2-353ab723fe14: {"url":
 "[https://www.pesi.com/careers](<https://www.pesi.com/careers>)", "fields": \["text", "html"\], "expand":
 true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 0de7f5f6-3aaf-44ca-8695-c662a4a133a2: {"url":
 "[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 a9e8a904-29e0-4e73-addb-5d94fe16a9c8: {"url":
 "[https://jobs.rcpsych.ac.uk](<https://jobs.rcpsych.ac.uk>)", "fields": \["text", "html"\], "expand":
 true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 9f409c0c-b143-444b-a77d-c592258d689f: {"url":
 "[https://rogersbh.org/careers](<https://rogersbh.org/careers>)", "fields": \["text", "html"\], "expand":
 true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 e7195918-031c-4096-9453-b4a699b7b64a: {"url":
 "[https://reviveresearch.org/careers](<https://reviveresearch.org/careers>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 139b0902-1136-46d8-b44e-953d0c00e51c: {"url":
 "[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 d4777c60-fd02-4fa4-8b49-4042659d9b96: {"url":
 "[https://www.bcchr.ca/careers](<https://www.bcchr.ca/careers>)", "fields": \["text", "html"\], "expand":
 true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 79d15fff-00db-4b12-9b8c-c011b3f21334: {"url":
 "[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 a8ba1924-2066-4498-8b77-33bfcf81d606: {"url":
 "[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 6d483653-eeb2-4649-8d1e-e476be116e66: {"url":
 "[https://sc.edu/about/employment](<https://sc.edu/about/employment>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 c6d3cab9-771a-482e-96b0-179dec48b561: {"url":
 "[https://www.volvogroup.com/en/careers/job-openings.html](<https://www.volvogroup.com/en/careers/job-openings.html>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 bd321bd4-b1e9-4ead-b07a-8366317f960e: {"url":
 "[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 75ac66fc-03dc-4fa2-8f42-eda3aaa6d77e: {"url":
 "[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  335: Calling telescope job
 0f74ce6a-d389-4f4d-8e0c-f27a1ab9252b: {"url":
 "[https://cmu.wd115.myworkdayjobs.com/SEI](<https://cmu.wd115.myworkdayjobs.com/SEI>)", "fields": \["text", "html"\],
 "expand": true, "wait_ready": true, "debug": true, "selector": "body"}
 2026-09-28 10:25:01  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>) fields=text,html
 careers_list=True\]
 2026-09-28 10:25:01  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>) titles=\["Commercial Sales
 Lead", "Publishing Operations Lead"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:25:01  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[20/20\] cochrane_org_2
 state=JOBLIST_IDENTIFIED url=[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>)
 2026-09-28 10:25:01  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)
 fields=text,html careers_list=True\]
 2026-09-28 10:25:01  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)
 titles=\["Clinical Research Coordinator- Neurology", "Clinic Nurse -
 Thoracic (IRP/Contingent)", "Staff Nurse - Hematology and Transplant
 (IRP/Contingent)", "Clinic Nurse (RN) - GU and Urology", "Research
 Senior Technician- Microbial Infection and Immunity", "Associate Nurse
 Manager - Acute Care - General Medicine", "CT Lead Tech $15,000
 Signing Bonus 3rd shift I UH Inpatient Patient Tower", "Post Doctoral
 Scholar - Comprehensive Cancer Center", "Specialty Practice
 Pharmacist", "Multi-Modality Imaging Tech $15,000 Signing Bonus"\]
 state=JOBLIST_IDENTIFIED
 2026-09-28 10:25:01  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[19/20\] careers_wexnermedical_osu_edu
 state=JOBLIST_IDENTIFIED
 url=[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)
 2026-09-28 10:25:01  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>)", "fields":
 \["text", "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>) fields=text,html
 careers_list=True\]
 2026-09-28 10:25:01  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>)
 titles=\["Attending Child and Adolescent Psychiatrists (UCSF Health)",
 "Attending Child and Adolescent Psychologist (UCSF Health)",
 "Attending Psychiatrists (UCSF Health)", "Attending Psychologist
 (Behavioral Sleep Medicine)", "Attending Psychologist (OCD Program)",
 "Attending Psychologist (UCSF Health)", "Attending Psychologist
 (Zuckerberg San Francisco General Hospital and Trauma Center)",
 "Attending Public Psychiatrists (Zuckerberg San Francisco General
 Hospital and Trauma Center)", "Clinical and Translational Researcher",
 "Mental Health Clinician-Educator (San Francisco VA Health Care
 System)"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:25:01  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[18/20\] psychiatry_ucsf_edu
 state=JOBLIST_IDENTIFIED url=[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>)
 2026-09-28 10:25:01  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://drugfree.org/article/work-at-the-partnership](<https://drugfree.org/article/work-at-the-partnership>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://drugfree.org/article/work-at-the-partnership](<https://drugfree.org/article/work-at-the-partnership>)
 fields=text,html careers_list=True\]
 2026-09-28 10:25:01  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://drugfree.org/article/work-at-the-partnership](<https://drugfree.org/article/work-at-the-partnership>)
 titles=\["Revenue Operations Coordinator"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:25:01  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[17/20\] drugfree_org
 state=JOBLIST_IDENTIFIED
 url=[https://drugfree.org/article/work-at-the-partnership](<https://drugfree.org/article/work-at-the-partnership>)
 2026-09-28 10:25:01  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies>)
 fields=text,html careers_list=True\]
 2026-09-28 10:25:01  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies>)
 titles=\["Alzheimer’s Society UKDTN Research Nurse"\]
 state=JOBLIST_IDENTIFIED
 2026-09-28 10:25:01  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[16/20\] oxfordhealthbrc_nihr_ac_uk
 state=JOBLIST_IDENTIFIED
 url=[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies>)
 2026-09-28 10:25:01  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)",
 "fields": \["text", "html"\], "expand": true, "wait_ready": true,
 "debug": true, "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)
 fields=text,html careers_list=True\]
 2026-09-28 10:25:01  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch:
 url=[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)
 titles=\["Technische Assistenz im Institut für Organische Chemie",
 "Research Associate for the Project “Cluster of Excellence, BlueMat:
 Water-driven Materials – Tunable Hydraulic and Capillarity-Driven
 Water Flow in Nanoporous Materials” § 28 Subsection 3 HmbHG",
 "Research Associate (Postdoc) Functional Ecology  § 28 Subsection 2
 HmbHG", "Research Associate “Ecology of living marine resources” § 28
 Subsection 1 HmbHG", "Research Associate for the Project “CLICCS” in
 Political Science, Economics, or a related field § 28 Subsection 3
 HmbHG", "Wissenschaftliche:r Mitarbeiter:in (Postdoc) Habilitation im
 Bereich Computational Systems Biomedicine § 28 Abs. 2 HmbHG",
 "Research Associate for the Project “Automated multi-writer
 Handwritten Text Recognition with continual learning (HTRcl)” (Centre
 for the Study of Manuscript Cultures) § 28 Subsection 3 HmbHG",
 "Research Associate for the Project “Cluster of Excellence, BlueMat:
 Water-driven Materials – Energy Storage in Supercapacitors” § 28
 Subsection 3 HmbHG", "Research Associate for the Project “MOMENTplus”
 § 28 Subsection 3 HmbHG", "Teamassistenz der Psychotherapeutischen
 Hochschulambulanz"\] state=JOBLIST_IDENTIFIED
 2026-09-28 10:25:01  \[DEBUG\]  1302: Calling
 run_parse_job_list_dispatch: \[15/20\] psy_unihamburg_de
 state=JOBLIST_IDENTIFIED
 url=[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)
 2026-09-28 10:25:01  \[DEBUG\]  564: Calling \_post_telescope:
 \[body={"url": "[https://www.pesi.com/careers](<https://www.pesi.com/careers>)", "fields": \["text",
 "html"\], "expand": true, "wait_ready": true, "debug": true,
 "selector": "body"}\]
 2026-09-28 10:25:01  \[DEBUG\]  1065: Calling scrape_page:
 \[url=[https://www.pesi.com/careers](<https://www.pesi.com/careers>) fields=text,html careers_list=True\]
 2026-09-28 10:25:01  \[DEBUG\]  1192: Calling
 run_parse_job_list_dispatch: url=[https://www.pesi.com/careers](<https://www.pesi.com/careers>)
 titles=\["Brand Manager (remote or in-office)", "Business Development
 Manager", "CE Accreditation Advisor – Licensed Counselor", "CE
 Accreditation Advisor – Licensed Psychologist", "Customer Success
 Specialist", "Direct Response Copywriter", "Email Marketing
 Strategist", "Lead Software Engineer", "Product Administration
 Specialist", "Social Media Strategist (Remote or Hybrid)"\]
 state=JOBLIST_IDENTIFIED
 2026-09-28 10:25:55  \[DEBUG\]  3243: Calling agent.do_task live_content: <ul>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/](<https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/>)">
 <h3>Clinical Director and Staff Specialist in Mental Health CCLHD</h3>
 </a>
 Central Coast Local District
 New South Wales

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/](<https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/>)">
 <h3>Consultant Child and Adolescent Psychiatrist</h3>
 </a>
 Kidswell
 London, North West England

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/](<https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/>)">
 <h3>Forensic Psychiatrists</h3>
 </a>
 Health New Zealand - Te Whatu Ora
 Other

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/](<https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/>)">
 <h3>Senior Staff Specialist or Staff Specialist or Senior Medical
 Officer (Psychiatrist - Intellectual and Developmental Disability)
 (Bundaberg)</h3>
 </a>
 Wide Bay Hospital & Health Service
 Bundaberg, Queensland

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/](<https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/>)">
 <h3>Senior Staff Specialist or Staff Specialist or Senior Medical
 Officer (Psychiatrist) (Hervey Bay and Maryborough)</h3>
 </a>
 Wide Bay Hospital & Health Service
 Hervey Bay and Maryborough, Queensland

</li>
 </ul>
 2026-09-28 10:25:55  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=rcpsych_ac_uk
 2026-09-28 10:25:55  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Forensic Psychiatrists", "Senior Staff
 Specialist or Staff Specialist or Senior Medical Officer (Psychiatrist

* Intellectual and Developmental Disability) (Bundaberg)", "Consultant
  Child and Adolescent Psychiatrist", "Senior Staff Specialist or Staff
  Specialist or Senior Medical Officer (Psychiatrist) (Hervey Bay and
  Maryborough)", "Clinical Director and Staff Specialist in Mental
  Health CCLHD"\] containers=\["<ul>\\n<li>\\n<a
  href="[https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/\\](<https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/%5C>)">\\n<h3>Clinical
  Director and Staff Specialist in Mental Health
  CCLHD</h3>\\n</a>\\nCentral Coast Local District\\nNew South
  Wales\\n\\n\\n</li>\\n<li>\\n<a
  href="[https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/\\](<https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/%5C>)">\\n<h3>Consultant
  Child and Adolescent Psychiatrist</h3>\\n</a>\\nKidswell\\nLondon, North
  West England\\n\\n\\n</li>\\n<li>\\n<a
  href="[https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/\\](<https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/%5C>)">\\n<h3>Forensic
  Psychiatrists</h3>\\n</a>\\nHealth New Zealand - Te Whatu
  Ora\\nOther\\n\\n\\n</li>\\n<li>\\n<a
  href="[https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/\\](<https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/%5C>)">\\n<h3>Senior
  Staff Specialist or Staff Specialist or Senior Medical Officer
  (Psychiatrist - Intellectual and Developmental Disability)
  (Bundaberg)</h3>\\n</a>\\nWide Bay Hospital & Health
  Service\\nBundaberg, Queensland\\n\\n\\n</li>\\n<li>\\n<a
  href="[https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/\\](<https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/%5C>)">\\n<h3>Senior
  Staff Specialist or Staff Specialist or Senior Medical Officer
  (Psychiatrist) (Hervey Bay and Maryborough)</h3>\\n</a>\\nWide Bay
  Hospital & Health Service\\nHervey Bay and Maryborough,
  Queensland\\n\\n\\n</li>\\n</ul>"\] cull_outcome='culled' dom_joined=<ul>
  <li>
  <a href="[https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/](<https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/>)">
  <h3>Clinical Director and Staff Specialist in Mental Health CCLHD</h3>
  </a>
  Central Coast Local District
  New South Wales

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/](<https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/>)">
 <h3>Consultant Child and Adolescent Psychiatrist</h3>
 </a>
 Kidswell
 London, North West England

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/](<https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/>)">
 <h3>Forensic Psychiatrists</h3>
 </a>
 Health New Zealand - Te Whatu Ora
 Other

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/](<https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/>)">
 <h3>Senior Staff Specialist or Staff Specialist or Senior Medical
 Officer (Psychiatrist - Intellectual and Developmental Disability)
 (Bundaberg)</h3>
 </a>
 Wide Bay Hospital & Health Service
 Bundaberg, Queensland

</li>
 <li>
 <a href="[https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/](<https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/>)">
 <h3>Senior Staff Specialist or Staff Specialist or Senior Medical
 Officer (Psychiatrist) (Hervey Bay and Maryborough)</h3>
 </a>
 Wide Bay Hospital & Health Service
 Hervey Bay and Maryborough, Queensland

</li>
 </ul>
 2026-09-28 10:25:55  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 21230, "visible_chars": 2194,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 10:25:55  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://jobs.rcpsych.ac.uk/](<https://jobs.rcpsych.ac.uk/>)", "text": "         We use
 cookies and similar technologies to make our site work, and to support
 analytics, personalization, and marketing.      Privacy Policy
 Accept   Deny Non-Essential    Manage Preferences
 \\n\\n\\n\\n\\n\\n\\n\\nCareer Center\\n\\n \\n \\nLooking For Qualified
 Candidates?\\nPost a Job \\n \\n\\n\\n\\n\\nJob Search
 Keywords\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\nSubmit Search\\nSearch Jobs\\n\\n\\n \\n\\n
 \\n\\n\\n\\n \\n\\n\\n Featured Jobs  \\n\\n \\n\\n\\n\\nClinical Director and
 Staff Specialist in Mental Health CCLHD\\n\\nCentral Coast Local
 District\\nNew South Wales\\n\\n\\n\\n\\n\\nConsultant Child and Adolescent
 Psychiatrist\\n\\nKidswell\\nLondon, North West
 England\\n\\n\\n\\n\\n\\nForensic Psychiatrists\\n\\nHealth New Zealand - Te
 Whatu Ora\\nOther\\n\\n\\n\\n\\n\\nSenior Staff Specialist or Staff
 Specialist or Senior Medical Officer (Psychiatrist - Intellectual and
 Developmental Disability) (Bundaberg)\\n\\nWide Bay Hospital & Health
 Service\\nBundaberg, Queensland\\n<54095 chars omitted>Close'><span
 aria-hidden='true'><svg xmlns='[http://www.w3.org/2000/svg](<http://www.w3.org/2000/svg>)' width='16'
 height='16' fill='currentColor' class='bi bi-x-lg' viewBox='0 0 16
 16'> <path d='M2.146 2.854a.5.5 0 1 1 .708-.708L8
 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0
 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293
 8z'/></svg></span></button>";\\njQuery("#cookie-consent").html(consent_content);\\n}\\n});\\n</script>\\n\\n\\n<iframe
 style="display: none;" name="\__uspapiLocator"></iframe><ul
 id="ui-id-1" tabindex="0" class="ui-menu ui-widget
 ui-widget-content ui-autocomplete ui-front" style="display: none;"
 unselectable="on"></ul><div role="status" aria-live="assertive"
 aria-relevant="additions" class="ui-helper-hidden-accessible"
 style="display: none;"></div></body>", "scrape_meta":
 {"bot_blocked": false, "cookies_dismissed": true, "issues": \[\],
 "content_chars": 2194, "requested_url": "[https://jobs.rcpsych.ac.uk](<https://jobs.rcpsych.ac.uk>)",
 "final_url": "[https://jobs.rcpsych.ac.uk/](<https://jobs.rcpsych.ac.uk/>)"}}
 2026-09-28 10:25:55  \[INFO\]  a9e8a904 | telescope job done:
 [https://jobs.rcpsych.ac.uk](<https://jobs.rcpsych.ac.uk>) -> [https://jobs.rcpsych.ac.uk/](<https://jobs.rcpsych.ac.uk/>)
 fields:text,html
 2026-09-28 10:25:55  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 10:25:55  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-1cb39e0468495f5b"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 10:25:55  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=rogersbh_org, n=4\]
 2026-09-28 10:25:55  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div aria-live="polite" class="swiper-wrapper
 elementor-slides" id="swiper-wrapper-a8aec4b651d2a5c4"><div
 aria-roledescription="slide" class="elementor-repeater-item-1363bc3
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="0"
 role="group"><div class="swiper-slide-bg"></div><a
 class="swiper-slide-inner"
 href="[https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741](<https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741>)"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Mental Health Technician –
 Residential, Overnight</div><div
 class="elementor-slide-description">Oconomowoc, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div><div
 aria-roledescription="slide" class="elementor-repeater-item-6a55170
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="1"
 role="group"><div class="swiper-slide-bg"></div><a
 class="swiper-slide-inner" href=<3881 chars
 omitted>Oconomowoc-Main-Campus-Oconomowoc-WI/Registered-Nurse---Residential_1712212-1"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Registered Nurse</div><div
 class="elementor-slide-description">Oconomowoc, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div><div
 aria-roledescription="slide" class="elementor-repeater-item-d8bb69a
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="2"
 role="group"><div class="swiper-slide-bg"></div><a
 class="swiper-slide-inner"
 href="[https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690](<https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690>)"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Therapist – Part Time/PRN</div><div
 class="elementor-slide-description">Brown Deer, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div></div>
 2026-09-28 10:25:55  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=rogersbh_org
 2026-09-28 10:25:55  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Mental Health Technician –
 Residential, Overnight", "Registered Nurse", "Therapist – Part
 Time/PRN"\] containers=\["<div aria-live="polite"
 class="swiper-wrapper elementor-slides"
 id="swiper-wrapper-a8aec4b651d2a5c4"><div
 aria-roledescription="slide" class="elementor-repeater-item-1363bc3
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="0"
 role="group"><div class="swiper-slide-bg"></div><a
 class="swiper-slide-inner"
 href="[https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741\\](<https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741%5C>)"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Mental Health Technician –
 Residential, Overnight</div><div
 class="elementor-slide-description">Oconomowoc, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div><div
 aria-roledescription="slide" class="elementor-repeater-item-6a55170
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="1"
 role="group"><div class="swiper-slide-bg"<4108 chars
 omitted>Registered-Nurse---Residential_1712212-1"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Registered Nurse</div><div
 class="elementor-slide-description">Oconomowoc, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div><div
 aria-roledescription="slide" class="elementor-repeater-item-d8bb69a
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="2"
 role="group"><div class="swiper-slide-bg"></div><a
 class="swiper-slide-inner"
 href="[https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690\\](<https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690%5C>)"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Therapist – Part Time/PRN</div><div
 class="elementor-slide-description">Brown Deer, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div></div>"\]
 cull_outcome='culled' dom_joined=<div aria-live="polite"
 class="swiper-wrapper elementor-slides"
 id="swiper-wrapper-a8aec4b651d2a5c4"><div aria-roledescription="slide"
 class="elementor-repeater-item-1363bc3 swiper-slide
 swiper-slide-duplicate" data-swiper-slide-index="0" role="group"><div
 class="swiper-slide-bg"></div><a class="swiper-slide-inner"
 href="[https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741](<https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741>)"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Mental Health Technician –
 Residential, Overnight</div><div
 class="elementor-slide-description">Oconomowoc, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div><div
 aria-roledescription="slide" class="elementor-repeater-item-6a55170
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="1"
 role="group"><div class="swiper-slide-bg"></div><a
 class="swiper-slide-inner" href=<3881 chars
 omitted>Oconomowoc-Main-Campus-Oconomowoc-WI/Registered-Nurse---Residential_1712212-1"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Registered Nurse</div><div
 class="elementor-slide-description">Oconomowoc, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div><div
 aria-roledescription="slide" class="elementor-repeater-item-d8bb69a
 swiper-slide swiper-slide-duplicate" data-swiper-slide-index="2"
 role="group"><div class="swiper-slide-bg"></div><a
 class="swiper-slide-inner"
 href="[https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690](<https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690>)"
 target="\_blank"><div class="swiper-slide-contents"><div
 class="elementor-slide-heading">Therapist – Part Time/PRN</div><div
 class="elementor-slide-description">Brown Deer, WI</div><div
 class="elementor-button elementor-slide-button
 elementor-size-md">Apply Here</div></div></a></div></div>
 2026-09-28 10:25:55  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 15473, "visible_chars": 9987,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 10:25:55  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://rogersbh.org/careers/](<https://rogersbh.org/careers/>)", "text":
 "\\n\\t\\t\\n\\t\\t\\n\\n\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\tSkip to content\\n\\t\\n
  \\n            \\n              Menu\\n            \\n        \\n
 Close\\n        \\t\\n\\t\\t\\n\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\n\\t\\n\\t\\n\\t\\t\\n
                    \\n                    What You'll Find on This
 Page\\n                    \\n                Careers at Rogers
 Behavioral HealthJoin the Rogers Behavioral Health TeamJoin the Rogers
 Behavioral Health TeamCareers at Rogers Behavioral Health Transform
 LivesWhy Work at Rogers?Career EventsAfter You ApplyReady to
 Apply?\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\tCareers at
 Rogers Behavioral
 Health\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\tHome
  Careers at Rogers Behavioral
 Health\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t<220518
 chars omitted>zUyNjE1YmYwNDkxNSJ9&mode=popup"
 id="limbic-chatbot-iframe" title="Limbic Access Chat"
 class="popup " aria-hidden="true"></iframe><button
 id="limbic-launcher-button" aria-label="Limbic Self Referral"
 name="Limbic Self Referral"
 data-testid="limbic-self-referral-launcher" class=""
 tabindex="0"><svg xmlns="[http://www.w3.org/2000/svg\\](<http://www.w3.org/2000/svg%5C>)" width="24"
 height="24" viewBox="0 0 24 24" fill="none"
 stroke="currentColor" stroke-width="2" stroke-linecap="round"
 stroke-linejoin="round" class="lucide lucide-x lb-open-icon"
 aria-hidden="true"><path d="M18 6 6 18"></path><path d="m6 6 12
 12"></path></svg><img class="lb-closed-icon" alt="Limbic Self
 Referral" src="[https://limbic-web-bot.s3.eu-west-2.amazonaws.com/assets/images/logo.png\\"></button></body>"](<https://limbic-web-bot.s3.eu-west-2.amazonaws.com/assets/images/logo.png%5C%22%3E%3C/button%3E%3C/body%3E%22>),
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 9987, "requested_url":
 "[https://rogersbh.org/careers](<https://rogersbh.org/careers>)", "final_url":
 "[https://rogersbh.org/careers/](<https://rogersbh.org/careers/>)"}}
 2026-09-28 10:25:55  \[INFO\]  9f409c0c | telescope job done:
 [https://rogersbh.org/careers](<https://rogersbh.org/careers>) -> [https://rogersbh.org/careers/](<https://rogersbh.org/careers/>)
 fields:text,html
 2026-09-28 10:25:55  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 10:25:55  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-b6db35f5a6786582"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 10:25:55  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=cmu_wd5_myworkdayjobs_com, n=4\]
 2026-09-28 10:25:55  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <ul aria-label="Page 1 of 3" role="list"><li
 class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a aria-current="false"
 class="css-19uc56f" data-automation-id="jobTitle"
 data-uxi-element-id="jobItem" data-uxi-item-rank="0"
 data-uxi-query-id="" data-uxi-widget-type="heading"
 href="/en-US/SEI/job/Linthicum/Technical-Site-Lead----SEI-Customer-Site---Fort-Meade--MD_2025134">Technical
 Site Lead  - SEI Customer Site - Fort Meade,
 MD</a></h3></div></div></div><div class="css-248241"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locationsLinthicum</div></div></div><div
 class="css-zoser8"><div class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 4 Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2025134</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-curr<14213 chars
 omitted>ss-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 30+ Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2024322</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="19" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/SEI/job/Pittsburgh-PA/AI-Red-Team-Engineer_2025000-1">AI
 Red Team Engineer</a></h3></div></div></div><div
 class="css-248241"><div class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locations2
 Locations</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 30+ Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2025000</li></ul></li></ul>
 2026-09-28 10:25:55  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=cmu_wd5_myworkdayjobs_com
 2026-09-28 10:25:55  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Technical Site Lead  - SEI Customer
 Site - Fort Meade, MD", "Senior Solutions Engineer", "Solutions
 Engineer", "Technical Engagement Lead", "Executive Assistant to the
 Chief Financial Officer", "Software Engineer", "Senior Real-Time
 Embedded Software Engineer", "Senior Embedded Software Engineer",
 "Real-Time Embedded Software Engineer", "IT Support Associate"\]
 containers=\["<ul aria-label="Page 1 of 3" role="list"><li
 class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a
 aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="0" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/SEI/job/Linthicum/Technical-Site-Lead----SEI-Customer-Site---Fort-Meade--MD_2025134">Technical
 Site Lead  - SEI Customer Site - Fort Meade,
 MD</a></h3></div></div></div><div class="css-248241"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locationsLinthicum</div></div></div><div
 class="css-zoser8"><div class="css-1y87fhn"><div
 class="css-k008qs" data-automation-id="postedOn">posted onPosted 4
 Days Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2025134</li></ul></li><li
 class="css-1q2dra3"><div class="css-qiqmbt"><div cla<15141 chars
 omitted>"postedOn">posted onPosted 30+ Days Ago</div></div></div><ul
 class="css-14a0imc" data-automation-id="subtitle"><li
 class="css-h2nt8k">2024322</li></ul></li><li
 class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a
 aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="19" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/SEI/job/Pittsburgh-PA/AI-Red-Team-Engineer_2025000-1">AI
 Red Team Engineer</a></h3></div></div></div><div
 class="css-248241"><div class="css-1y87fhn"><div
 class="css-k008qs" data-automation-id="locations">locations2
 Locations</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 30+ Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2025000</li></ul></li></ul>"\]
 cull_outcome='culled' dom_joined=<ul aria-label="Page 1 of 3"
 role="list"><li class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a aria-current="false"
 class="css-19uc56f" data-automation-id="jobTitle"
 data-uxi-element-id="jobItem" data-uxi-item-rank="0"
 data-uxi-query-id="" data-uxi-widget-type="heading"
 href="/en-US/SEI/job/Linthicum/Technical-Site-Lead----SEI-Customer-Site---Fort-Meade--MD_2025134">Technical
 Site Lead  - SEI Customer Site - Fort Meade,
 MD</a></h3></div></div></div><div class="css-248241"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locationsLinthicum</div></div></div><div
 class="css-zoser8"><div class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 4 Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2025134</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-curr<14213 chars
 omitted>ss-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 30+ Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2024322</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="19" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/SEI/job/Pittsburgh-PA/AI-Red-Team-Engineer_2025000-1">AI
 Red Team Engineer</a></h3></div></div></div><div
 class="css-248241"><div class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locations2
 Locations</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 30+ Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">2025000</li></ul></li></ul>
 2026-09-28 10:25:55  \[ERROR\]  Task was destroyed but it is pending!
 task: <Task pending name='telescope-result-poller'
 coro=<\_TelescopeQueue.\_poll_loop() running at
 /app/src/external/telescope.py:297> wait_for=<Future pending
 cb=\[Task.task_wakeup()\]>>
 2026-09-28 10:25:55  \[ERROR\]  Task was destroyed but it is pending!
 task: <Task pending name='Task-7406' coro=<to_thread() running at
 /root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
 wait_for=<Future pending
 cb=\[\_chain_future.<locals>.\_call_check_cancel() at
 /root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
 Task.task_wakeup()\]>>
 2026-09-28 10:25:56  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div aria-label="Cookie preferences." aria-live="polite"
 id="ccc" role="region"></div><div class="site-container"><ul
 class="genesis-skip-link"><li><a class="screen-reader-shortcut
 \__mPS2id \_mPS2id-h mPS2id-highlight mPS2id-highlight-first"
 href="#genesis-nav-primary"> Skip to primary navigation</a></li><li><a
 class="screen-reader-shortcut \__mPS2id \_mPS2id-h mPS2id-highlight"
 href="#genesis-content"> Skip to main content</a></li><li><a
 class="screen-reader-shortcut \__mPS2id \_mPS2id-h mPS2id-highlight
 mPS2id-highlight-last" href="#genesis-sidebar-primary"> Skip to
 primary sidebar</a></li><li><a class="screen-reader-shortcut \__mPS2id
 \_mPS2id-h" href="#genesis-footer-widgets"> Skip to
 footer</a></li></ul><div class="wrap"><div class="title-area"> <div
 class="site-title">
 <a href="[https://oxfordhealthbrc.nihr.ac.uk/](<https://oxfordhealthbrc.nihr.ac.uk/>)" title="Home">
 <img alt="NIHR Biomedical Research Centre: Oxford Health "/>
 </a>
 </div>
 </div><div class="widget-area header-widget-area">

<div class="header-email">
 <a href=<23540 chars omitted>d="text-5"><div class="widget-wrap"> <div
 class="textwidget"><div>The <a data-external-handled="true"
 href="[https://www.nihr.ac.uk/](<https://www.nihr.ac.uk/>)" rel="noopener" target="\_blank">National
 Institute for Health and Care Research (NIHR)</a> Biomedical Research
 Centre (BRC) is a partnership between Oxford Health NHS Foundation
 Trust and the University of Oxford.  We are part of the Oxford
 Academic Health Partners.</div>
 </div>
 </div></section>
 <section class="widget widget_sp_image" id="widget_sp_image-4"><div
 class="widget-wrap"><a class="widget_sp_image-image-link"
 data-external-handled="true" href="[https://www.oahp.org.uk/](<https://www.oahp.org.uk/>)"
 target="\_blank"><img alt="Oxford Academic Health Partners"
 class="attachment-full"/></a></div></section>
 </div></div></div><div class="wrap"><p>© 2026 NIHR Biomedical Research
 Centre: Oxford Health  · <a
 href="[https://oxfordhealthbrc.nihr.ac.uk/wp-login.php](<https://oxfordhealthbrc.nihr.ac.uk/wp-login.php>)">Log
 in</a></p></div></div>

<div class="ps2id-dummy-offset-wrapper"><div
 id="ps2id-dummy-offset"></div></div>
 2026-09-28 10:25:56  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=oxfordhealthbrc_nihr_ac_uk
 2026-09-28 10:25:56  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Alzheimer’s Society UKDTN Research
 Nurse"\] containers=\["<div aria-label="Cookie preferences."
 aria-live="polite" id="ccc" role="region"></div><div
 class="site-container"><ul class="genesis-skip-link"><li><a
 class="screen-reader-shortcut \__mPS2id \_mPS2id-h mPS2id-highlight
 mPS2id-highlight-first" href="#genesis-nav-primary"> Skip to
 primary navigation</a></li><li><a class="screen-reader-shortcut
 \__mPS2id \_mPS2id-h mPS2id-highlight" href="#genesis-content"> Skip
 to main content</a></li><li><a class="screen-reader-shortcut \__mPS2id
 \_mPS2id-h mPS2id-highlight mPS2id-highlight-last"
 href="#genesis-sidebar-primary"> Skip to primary
 sidebar</a></li><li><a class="screen-reader-shortcut \__mPS2id
 \_mPS2id-h" href="#genesis-footer-widgets"> Skip to
 footer</a></li></ul><div class="wrap"><div class="title-area">
 <div class="site-title">\\n<a
 href="[https://oxfordhealthbrc.nihr.ac.uk/\\](<https://oxfordhealthbrc.nihr.ac.uk/%5C>)" title="Home">\\n<img
 alt="NIHR Biomedical Research Centre: Oxford Health
 "/>\\n</a>\\n</div>\\n</div><div class="widget-area header-wid<24816
 chars omitted>"><div>The <a data-external-handled="true"
 href="[https://www.nihr.ac.uk/\\](<https://www.nihr.ac.uk/%5C>)" rel="noopener"
 target="\_blank">National Institute for Health and Care Research
 (NIHR)</a> Biomedical Research Centre (BRC) is a partnership between
 Oxford Health NHS Foundation Trust and the University of Oxford.  We
 are part of the Oxford Academic Health
 Partners.</div>\\n</div>\\n</div></section>\\n<section class="widget
 widget_sp_image" id="widget_sp_image-4"><div
 class="widget-wrap"><a class="widget_sp_image-image-link"
 data-external-handled="true" href="[https://www.oahp.org.uk/\\](<https://www.oahp.org.uk/%5C>)"
 target="\_blank"><img alt="Oxford Academic Health Partners"
 class="attachment-full"/></a></div></section>\\n</div></div></div><div
 class="wrap"><p>© 2026 NIHR Biomedical Research Centre: Oxford
 Health  · <a href="[https://oxfordhealthbrc.nihr.ac.uk/wp-login.php\\](<https://oxfordhealthbrc.nihr.ac.uk/wp-login.php%5C>)">Log
 in</a></p></div></div>\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n<div
 class="ps2id-dummy-offset-wrapper"><div
 id="ps2id-dummy-offset"></div></div>"\] cull_outcome='full_dom'
 dom_joined=<div aria-label="Cookie preferences." aria-live="polite"
 id="ccc" role="region"></div><div class="site-container"><ul
 class="genesis-skip-link"><li><a class="screen-reader-shortcut
 \__mPS2id \_mPS2id-h mPS2id-highlight mPS2id-highlight-first"
 href="#genesis-nav-primary"> Skip to primary navigation</a></li><li><a
 class="screen-reader-shortcut \__mPS2id \_mPS2id-h mPS2id-highlight"
 href="#genesis-content"> Skip to main content</a></li><li><a
 class="screen-reader-shortcut \__mPS2id \_mPS2id-h mPS2id-highlight
 mPS2id-highlight-last" href="#genesis-sidebar-primary"> Skip to
 primary sidebar</a></li><li><a class="screen-reader-shortcut \__mPS2id
 \_mPS2id-h" href="#genesis-footer-widgets"> Skip to
 footer</a></li></ul><div class="wrap"><div class="title-area"> <div
 class="site-title">
 <a href="[https://oxfordhealthbrc.nihr.ac.uk/](<https://oxfordhealthbrc.nihr.ac.uk/>)" title="Home">
 <img alt="NIHR Biomedical Research Centre: Oxford Health "/>
 </a>
 </div>
 </div><div class="widget-area header-widget-area">

<div class="header-email">
 <a href=<23540 chars omitted>d="text-5"><div class="widget-wrap"> <div
 class="textwidget"><div>The <a data-external-handled="true"
 href="[https://www.nihr.ac.uk/](<https://www.nihr.ac.uk/>)" rel="noopener" target="\_blank">National
 Institute for Health and Care Research (NIHR)</a> Biomedical Research
 Centre (BRC) is a partnership between Oxford Health NHS Foundation
 Trust and the University of Oxford.  We are part of the Oxford
 Academic Health Partners.</div>
 </div>
 </div></section>
 <section class="widget widget_sp_image" id="widget_sp_image-4"><div
 class="widget-wrap"><a class="widget_sp_image-image-link"
 data-external-handled="true" href="[https://www.oahp.org.uk/](<https://www.oahp.org.uk/>)"
 target="\_blank"><img alt="Oxford Academic Health Partners"
 class="attachment-full"/></a></div></section>
 </div></div></div><div class="wrap"><p>© 2026 NIHR Biomedical Research
 Centre: Oxford Health  · <a
 href="[https://oxfordhealthbrc.nihr.ac.uk/wp-login.php](<https://oxfordhealthbrc.nihr.ac.uk/wp-login.php>)">Log
 in</a></p></div></div>

<div class="ps2id-dummy-offset-wrapper"><div
 id="ps2id-dummy-offset"></div></div>
 2026-09-28 10:25:56  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 58628, "visible_chars": 1928,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 10:25:56  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/>)",
 "text": " Skip to primary navigation Skip to main content Skip to
 primary sidebar Skip to footer\\n\\n\\n\\n    \\n            About\\n\\n
 \\n\\n\\n\\n\\nYou are here: Home / About / Vacancies\\nWe are keen to
 recruit talented and committed researchers and support staff to the
 NIHR Biomedical Research Centre: Oxford Health.\\n\\n\\n\\nFor any queries
 about this page or to post a vacancy please contact Sarah
 Marr.\\n\\n\\n\\n\\n\\n\\nAlzheimer’s Society UKDTN Research Nurse\\n\\nFull
 time, Fixed Term 18 months Band 6: £39,959 – £48,117 Core hours 9am to
 5pm, Monday to Friday. Based full time on-site at the Warneford
 Hospital with frequent visits to other sites Would you like to be part
 of finding treatments for the future at the NIHR Clinical Research
 Facility: Oxford Health? Working within…Read
 more\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\nVacancies within our partner organisations
 can be found here:\\n\\n\\n\\nThe University of Oxford jobs\\n\\n\\n\\nOxford
 Health<63977 chars omitted>            },\\n
                                                         \],\\n
                                                      statement: {\\n
                         description: 'For more information, see
 our',\\n                            name: 'Data Control and Privacy
 Statement',\\n                            url:
 '[https://oxfordhealthbrc.nihr.ac.uk/data-control/](<https://oxfordhealthbrc.nihr.ac.uk/data-control/>)',\\n
           updated: '01/10/2025'\\n                        },\\n
                               sameSiteCookie: true,\\n
   sameSiteValue: 'Strict',\\n                    notifyDismissButton:
 true\\n                };\\n
 CookieControl.load(config);\\n            </script>\\n\\n\\n</body>",
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": true,
 "issues": \[\], "content_chars": 1928, "requested_url":
 "[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies>)", "final_url":
 "[https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/>)"}}
 2026-09-28 10:25:56  \[INFO\]  3b0863d9 | telescope job done:
 [https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies>) ->
 [https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/](<https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/>)
 fields:text,html
 2026-09-28 10:25:56  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 10:25:56  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-2f8e3fc24dbfc4a4"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 10:25:56  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=revivalresearch_org, n=4\]
 2026-09-28 10:25:56  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div class="awsm-job-listings awsm-lists"
 data-listings="10"><div class="awsm-job-listing-item awsm-list-item"
 id="awsm-list-item-36282"><div class="awsm-job-item"><div
 class="awsm-list-left-col"><h2 class="awsm-job-post-title">
 <a href="[https://revivalresearch.org/blogs/jobs/physician-assistant/](<https://revivalresearch.org/blogs/jobs/physician-assistant/>)">Physician
 Assistant</a></h2></div><div class="awsm-list-right-col"><div
 class="awsm-job-specification-wrapper"><div
 class="awsm-job-specification-item
 awsm-job-specification-job-category"><span
 class="awsm-job-specification-term">Clinical Research</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-type"><span
 class="awsm-job-specification-term">Full Time</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-location"><span
 class="awsm-job-specification-term">Michigan</span> <span
 class="awsm-job-specification-term">Texas</span></div></div><div
 class="awsm-job-more-container"><a class="awsm-job-more"
 href="[https://revivalresearch.org/blogs/j](<https://revivalresearch.org/blogs/j>)<10893 chars omitted>
 class="awsm-list-left-col"><h2 class="awsm-job-post-title">
 <a href="[https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/](<https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/>)">Clinical
 Research Coordinator – North Carolina</a></h2></div><div
 class="awsm-list-right-col"><div
 class="awsm-job-specification-wrapper"><div
 class="awsm-job-specification-item
 awsm-job-specification-job-category"><span
 class="awsm-job-specification-term">Clinical Research</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-type"><span
 class="awsm-job-specification-term">Full Time</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-location"><span
 class="awsm-job-specification-term">Cary</span> <span
 class="awsm-job-specification-term">North
 Carolina</span></div></div><div class="awsm-job-more-container"><a
 class="awsm-job-more"
 href="[https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/](<https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/>)">More
 Details <span></span></a></div></div></div></div></div>
 2026-09-28 10:25:56  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=revivalresearch_org
 2026-09-28 10:25:56  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Physician Assistant",
 "Phlebotomist/Lab Tech", "Clinical Research Coordinator – Illinois",
 "Clinical Research Coordinator – Texas", "Clinical Research
 Coordinator – New Jersey", "Clinical Research Coordinator – North
 Carolina"\] containers=\["<div class="awsm-job-listings awsm-lists"
 data-listings="10"><div class="awsm-job-listing-item
 awsm-list-item" id="awsm-list-item-36282"><div
 class="awsm-job-item"><div class="awsm-list-left-col"><h2
 class="awsm-job-post-title">\\n<a
 href="[https://revivalresearch.org/blogs/jobs/physician-assistant/\\](<https://revivalresearch.org/blogs/jobs/physician-assistant/%5C>)">Physician
 Assistant</a></h2></div><div class="awsm-list-right-col"><div
 class="awsm-job-specification-wrapper"><div
 class="awsm-job-specification-item
 awsm-job-specification-job-category"><span
 class="awsm-job-specification-term">Clinical
 Research</span></div><div class="awsm-job-specification-item
 awsm-job-specification-job-type"><span
 class="awsm-job-specification-term">Full Time</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-location"><span
 class="awsm-job-specification-term">Michigan</span> <span
 class="awsm-job-specification-term">Texas</span></div></div><div
 class="awsm-job-more-container"><a class="awsm-job-more" <11352
 chars omitted> class="awsm-job-post-title">\\n<a
 href="[https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/\\](<https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/%5C>)">Clinical
 Research Coordinator – North Carolina</a></h2></div><div
 class="awsm-list-right-col"><div
 class="awsm-job-specification-wrapper"><div
 class="awsm-job-specification-item
 awsm-job-specification-job-category"><span
 class="awsm-job-specification-term">Clinical
 Research</span></div><div class="awsm-job-specification-item
 awsm-job-specification-job-type"><span
 class="awsm-job-specification-term">Full Time</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-location"><span
 class="awsm-job-specification-term">Cary</span> <span
 class="awsm-job-specification-term">North
 Carolina</span></div></div><div class="awsm-job-more-container"><a
 class="awsm-job-more"
 href="[https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/\\](<https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/%5C>)">More
 Details <span></span></a></div></div></div></div></div>"\]
 cull_outcome='culled' dom_joined=<div class="awsm-job-listings
 awsm-lists" data-listings="10"><div class="awsm-job-listing-item
 awsm-list-item" id="awsm-list-item-36282"><div
 class="awsm-job-item"><div class="awsm-list-left-col"><h2
 class="awsm-job-post-title">
 <a href="[https://revivalresearch.org/blogs/jobs/physician-assistant/](<https://revivalresearch.org/blogs/jobs/physician-assistant/>)">Physician
 Assistant</a></h2></div><div class="awsm-list-right-col"><div
 class="awsm-job-specification-wrapper"><div
 class="awsm-job-specification-item
 awsm-job-specification-job-category"><span
 class="awsm-job-specification-term">Clinical Research</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-type"><span
 class="awsm-job-specification-term">Full Time</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-location"><span
 class="awsm-job-specification-term">Michigan</span> <span
 class="awsm-job-specification-term">Texas</span></div></div><div
 class="awsm-job-more-container"><a class="awsm-job-more"
 href="[https://revivalresearch.org/blogs/j](<https://revivalresearch.org/blogs/j>)<10893 chars omitted>
 class="awsm-list-left-col"><h2 class="awsm-job-post-title">
 <a href="[https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/](<https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/>)">Clinical
 Research Coordinator – North Carolina</a></h2></div><div
 class="awsm-list-right-col"><div
 class="awsm-job-specification-wrapper"><div
 class="awsm-job-specification-item
 awsm-job-specification-job-category"><span
 class="awsm-job-specification-term">Clinical Research</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-type"><span
 class="awsm-job-specification-term">Full Time</span></div><div
 class="awsm-job-specification-item
 awsm-job-specification-job-location"><span
 class="awsm-job-specification-term">Cary</span> <span
 class="awsm-job-specification-term">North
 Carolina</span></div></div><div class="awsm-job-more-container"><a
 class="awsm-job-more"
 href="[https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/](<https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/>)">More
 Details <span></span></a></div></div></div></div></div>
 2026-09-28 10:25:56  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 30012, "visible_chars": 3360,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 10:25:56  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>)", "text": "\\n\\nSkip
 to contentSkip to footer\\nCareersCurrent jobs\\n Looking to Build Your
 Career in Clinical Research? SearchFilter byAll Job CategoryAll Job
 CategoryClinical ResearchAll Job Category▾All Job CategoryClinical
 ResearchAll Job TypeAll Job TypeFull TimeAll Job Type▾All Job TypeFull
 TimeAll Job LocationAll Job
 LocationMichiganTexasElginIllinoisCaryNorth CarolinaHamiltonNew
 JerseyDentonMcKinneyAll Job Location▾All Job
 LocationMichiganTexasElginIllinoisCaryNorth CarolinaHamiltonNew
 JerseyDentonMcKinney\\nPhysician AssistantClinical ResearchFull
 TimeMichigan TexasMore Details \\nPhlebotomist/Lab TechClinical
 ResearchFull TimeTexas McKinneyMore Details \\nClinical Research
 Coordinator – IllinoisClinical ResearchFull TimeElgin IllinoisMore
 Details \\nClinical Research Coordinator – TexasClinical ResearchFull
 TimeTexas DentonMore Details \\nClinical Research Coordinator – New
 JerseyClinical ResearchFull TimeHamilton New JerseyMore Det<472048
 chars omitted>[e.com/recaptcha/api2/anchor?ar=1](<http://e.com/recaptcha/api2/anchor?ar=1>)&k=6LfKFG4rAAAAAO43lgGM-XzK3ffd9t6n1a6vXSQs&co=aHR0cHM6Ly9yZXZpdmFscmVzZWFyY2gub3JnOjQ0Mw..&hl=en&v=kemdRjWFxNjgsGdhRslyEPwU&size=invisible&anchor-ms=20000&execute-ms=30000&cb=szo9cm8m06b3"
 class="elementra_resize trx_addons_resize"></iframe></div><div
 class="grecaptcha-error"></div><textarea
 id="g-recaptcha-response-100000" name="g-recaptcha-response"
 class="g-recaptcha-response" style="width: 250px; height: 40px;
 border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px;
 resize: none; display: none;"></textarea></div><iframe
 style="display: none;" class="elementra_resize
 trx_addons_resize"></iframe></div><div class="content_wrap"
 style="height:0;visibility:hidden;"></div></body>", "scrape_meta":
 {"bot_blocked": false, "cookies_dismissed": false, "issues": \[\],
 "content_chars": 3360, "requested_url":
 "[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>)", "final_url":
 "[https://revivalresearch.org/careers](<https://revivalresearch.org/careers>)"}}
 2026-09-28 10:25:56  \[INFO\]  0de7f5f6 | telescope job done:
 [https://revivalresearch.org/careers](<https://revivalresearch.org/careers>) ->
 [https://revivalresearch.org/careers](<https://revivalresearch.org/careers>) fields:text,html
 2026-09-28 10:25:56  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 10:25:56  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-39fcf1efa26afc1a"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 10:25:56  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=training_nih_gov, n=4\]
 2026-09-28 10:25:56  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <ul class="usa-collection">
 <li class="usa-collection__item">
 <div class="usa-collection__body">
 <h2 class="usa-collection__heading"><a
 href="/careers/open-positions/job-02329d15-c2fe-4255-bf46-043a4e794e51"><span
 class="usa-sr-only">Read more about the </span>Staff Scientist I <span
 class="usa-sr-only"> job</span></a></h2>
 <div class="usa-collection__description">
 <ul class="details-list details-list--inline">
 <li class="details-list__item">
 <h3 class="details-list__label">Open:</h3>
           09/18/2026
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Category:</h3>
           Scientific
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Location:</h3>
                                 Durham, North Carolina
                   </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Institute or Center:</h3>
           NIEHS (National Institute of Environmental Health Sciences)
         </li>
 <li class="details-list__item<21269 chars omitted>nt Fire Chief<span
 class="usa-sr-only"> job</span></a></h2>
 <div class="usa-collection__description">
 <ul class="details-list details-list--inline">
 <li class="details-list__item">
 <h3 class="details-list__label">Open:</h3>
           09/24/2026 – 09/30/2026
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Category:</h3>
           Fire Protection and Prevention
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Location:</h3>
                                 Montgomery County, Maryland
                   </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Institute or Center:</h3>
                       OD (Office of the Director)
                 </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Hiring Path:</h3>
 <span class="usa-tooltip"><img alt="Internal to an agency - appears on
 USAJOBS" class="details-list__inline-group-item
 usa-tooltip__trigger"/></span>
 </li>
 </ul>
 </div>
 </div>
 </li>
 </ul>
 2026-09-28 10:25:56  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=training_nih_gov
 2026-09-28 10:25:56  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Staff Scientist I", "Deputy Director,
 Division of Extramural Research", "Staff Clinician", "Administrative
 Technician", "Biologist Scientist Administrator (Scientific Review
 Officer)", "Health Scientist Administrator (Program Officer)", "Lead
 Nuclear Medicine Technologist", "Mechanical Engineer", "Royalties
 Analyst", "Supervisory Data Scientist"\] containers=\["<ul
 class="usa-collection">\\n<li class="usa-collection__item">\\n<div
 class="usa-collection__body">\\n<h2
 class="usa-collection__heading"><a
 href="/careers/open-positions/job-02329d15-c2fe-4255-bf46-043a4e794e51"><span
 class="usa-sr-only">Read more about the </span>Staff Scientist I
 <span class="usa-sr-only"> job</span></a></h2>\\n<div
 class="usa-collection__description">\\n<ul class="details-list
 details-list--inline">\\n<li class="details-list__item">\\n<h3
 class="details-list__label">Open:</h3>\\n          09/18/2026\\n
  </li>\\n<li class="details-list__item">\\n<h3
 class="details-list__label">Category:</h3>\\n          Scientific\\n
      </li>\\n<li class="details-list__item">\\n<h3
 class="details-list__label">Location:</h3>\\n
        Durham, North Carolina\\n                  </li>\\n<li
 class="details-list__item">\\n<h3
 class="details-list__label">Institute or Center:</h3>\\n
 NIEHS (National Institute of Environmental Heal<22613 chars
 omitted>\\n<div class="usa-collection__description">\\n<ul
 class="details-list details-list--inline">\\n<li
 class="details-list__item">\\n<h3
 class="details-list__label">Open:</h3>\\n          09/24/2026 –
 09/30/2026\\n        </li>\\n<li class="details-list__item">\\n<h3
 class="details-list__label">Category:</h3>\\n          Fire
 Protection and Prevention\\n        </li>\\n<li
 class="details-list__item">\\n<h3
 class="details-list__label">Location:</h3>\\n
        Montgomery County, Maryland\\n                  </li>\\n<li
 class="details-list__item">\\n<h3
 class="details-list__label">Institute or Center:</h3>\\n
         OD (Office of the Director)\\n                </li>\\n<li
 class="details-list__item">\\n<h3
 class="details-list__label">Hiring Path:</h3>\\n<span
 class="usa-tooltip"><img alt="Internal to an agency - appears on
 USAJOBS" class="details-list__inline-group-item
 usa-tooltip__trigger"/></span>\\n</li>\\n</ul>\\n</div>\\n</div>\\n</li>\\n</ul>"\]
 cull_outcome='culled' dom_joined=<ul class="usa-collection">
 <li class="usa-collection__item">
 <div class="usa-collection__body">
 <h2 class="usa-collection__heading"><a
 href="/careers/open-positions/job-02329d15-c2fe-4255-bf46-043a4e794e51"><span
 class="usa-sr-only">Read more about the </span>Staff Scientist I <span
 class="usa-sr-only"> job</span></a></h2>
 <div class="usa-collection__description">
 <ul class="details-list details-list--inline">
 <li class="details-list__item">
 <h3 class="details-list__label">Open:</h3>
           09/18/2026
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Category:</h3>
           Scientific
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Location:</h3>
                                 Durham, North Carolina
                   </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Institute or Center:</h3>
           NIEHS (National Institute of Environmental Health Sciences)
         </li>
 <li class="details-list__item<21269 chars omitted>nt Fire Chief<span
 class="usa-sr-only"> job</span></a></h2>
 <div class="usa-collection__description">
 <ul class="details-list details-list--inline">
 <li class="details-list__item">
 <h3 class="details-list__label">Open:</h3>
           09/24/2026 – 09/30/2026
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Category:</h3>
           Fire Protection and Prevention
         </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Location:</h3>
                                 Montgomery County, Maryland
                   </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Institute or Center:</h3>
                       OD (Office of the Director)
                 </li>
 <li class="details-list__item">
 <h3 class="details-list__label">Hiring Path:</h3>
 <span class="usa-tooltip"><img alt="Internal to an agency - appears on
 USAJOBS" class="details-list__inline-group-item
 usa-tooltip__trigger"/></span>
 </li>
 </ul>
 </div>
 </div>
 </li>
 </ul>
 2026-09-28 10:25:56  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 22545, "visible_chars": 20128,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 10:25:56  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>)", "text":
 "\\nSkip to main content\\n\\n\\n\\n\\n  \\n    \\n      \\n    \\n        \\n\\n
       \\n    \\n\\n\\n  \\n\\n\\n        \\n    \\n  \\n\\n  \\n  \\n\\n  \\n      \\n
      \\n        \\n  \\n    \\n          \\n\\n  \\n\\n      \\n    \\n  \\n  \\n
     \\n  \\n    \\n    \\n                          \\n\\n  \\n      \\n
        \\n                          \\n                          \\n
   \\n        \\n        \\n          New Employees\\n                  \\n
             \\n                          \\n                          \\n
        \\n        \\n        \\n          Former Employees\\n
     \\n              \\n                          \\n
      \\n        \\n        \\n        \\n          Staff Resources\\n
            \\n              \\n                          \\n
             \\n        \\n                          \\n        \\n
  Careers\\n                        \\n      \\n              \\n
           <121510 chars omitted>m; visibility:
 hidden;"></iframe><script type="module"
 src="[https://static.cloudflareinsights.com/beacon.min.js/v31edd6df95cf4e85bb4c19e7a9bdbcba1788362987495\\](<https://static.cloudflareinsights.com/beacon.min.js/v31edd6df95cf4e85bb4c19e7a9bdbcba1788362987495%5C>)"
 integrity="sha512-iIg7k2xntmwu6/uSb5tpc/hySgZc4eoL31yB29W6tJFo2akwjPWcEqnCEdJvGexCL0KEQwVYv5BlowfhVz26hg=="
 data-cf-beacon="{"version":"2024.11.0","token":"4da10bb88a2f4316a9de363d388a5456","spa":2}"
 crossorigin="anonymous"></script>\\n\\n\\n<div
 id="drupal-live-announce" class="visually-hidden"
 aria-live="polite" aria-busy="false"></div><script
 id="\_fed_an_ua_tag" text="" charset="" type="text/javascript"
 src="[https://dap.digitalgov.gov/Universal-Federated-Analytics-Min.js?agency=HHS&subagency=NIH&sp=keys\\"></script></body>"](<https://dap.digitalgov.gov/Universal-Federated-Analytics-Min.js?agency=HHS&subagency=NIH&sp=keys%5C%22%3E%3C/script%3E%3C/body%3E%22>),
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 20128, "requested_url":
 "[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>)", "final_url":
 "[https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>)"}}
 2026-09-28 10:25:56  \[INFO\]  75ac66fc | telescope job done:
 [https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>) ->
 [https://hr.nih.gov/careers/open-positions](<https://hr.nih.gov/careers/open-positions>) fields:text,html
 2026-09-28 10:25:56  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 10:25:56  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-7d547b89ee1db4d3"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 10:25:56  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=rcpsych_ac_uk, n=4\]
 2026-09-28 10:28:03  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-17f3732d5d9ee8a5"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 10:28:03  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=oxfordhealthbrc_nihr_ac_uk, n=4\]
 2026-09-28 10:28:04  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 60334, "visible_chars": 3149938,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 10:28:04  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://jobs.volvogroup.com/?locale=en_US](<https://jobs.volvogroup.com/?locale=en_US>)", "text":
 "\\n\\n        \\n\\n    \\n        \\n        \\n            \\n
   \\n                    \\n    \\n    \\n        \\n
 Volvo Group JobsTogether we shape the world we want to live in\\n\\n
    \\n    \\n\\n    \\n        \\n\\t\\n\\t361555\\n\\n\\t\\n\\t15\\n\\n\\t\\n\\ten_US,
 fr_FR, es_MX, pt_BR, de_DE, it_IT, nl_NL, pl_PL, sv_SE, fi_FI, cs_CZ,
 nb_NO, zh_CN, ko_KR\\n\\n\\t\\n\\tView More\\n\\n\\t\\n\\tYour search did not
 match any jobs. Try adjusting the filters.\\n\\n\\t\\n\\tShow
 filters\\n\\tClose filters\\n\\n\\t\\n\\t\\n\\t\\t\\n\\t\\t\\tEnter job title or
 keyword\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tJob
 Category\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tLocation\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tOrganization\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tPosition
 Type\\n\\t\\t\\n\\t\\n\\n\\t\\n\\t\\n\\t\\t\\n\\t\\t\\tAvailable Jobs
 \\n\\t\\t\\n\\t\\t\\n\\t\\t\\tJob
 Category\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tOrganization\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tLocation\\n
                        3\\n\\t\\t\\tShow More\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tPosition
 Type\\n\\t\\t\\n\\t\\t\\n\\t\\t\\tPosted\\n\\t\\t\\n\\t\\t\\n<7409587 chars
 omitted>2000/svg"><g id="Page-1" stroke="none" stroke-width="1"
 fill="none" fill-rule="evenodd"><g id="Banner_02"
 class="ot-floating-button__svg-fill"
 transform="translate(-318.000000, -725.000000)" fill="#292B2E"
 fill-rule="nonzero"><g id="Group-2"
 transform="translate(305.000000, 712.000000)"><g
 id="icon/16px/white/close"><polygon id="Line1" points="13.3333333
 14.9176256 35.0823744 36.6666667 36.6666667 35.0823744 14.9176256
 13.3333333"></polygon><polygon id="Line2"
 transform="translate(25.000000, 25.000000) scale(-1, 1)
 translate(-25.000000, -25.000000) " points="13.3333333 14.9176256
 35.0823744 36.6666667 36.6666667 35.0823744 14.9176256
 13.3333333"></polygon></g></g></g></g></svg></button></div></div></div></body>",
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 3149938, "requested_url":
 "[https://www.volvogroup.com/en/careers/job-openings.html](<https://www.volvogroup.com/en/careers/job-openings.html>)",
 "final_url": "[https://jobs.volvogroup.com/?locale=en_US](<https://jobs.volvogroup.com/?locale=en_US>)"}}
 2026-09-28 10:28:04  \[INFO\]  c6d3cab9 | telescope job done:
 [https://www.volvogroup.com/en/careers/job-openings.html](<https://www.volvogroup.com/en/careers/job-openings.html>) ->
 [https://jobs.volvogroup.com/?locale=en_US](<https://jobs.volvogroup.com/?locale=en_US>) fields:text,html
 2026-09-28 10:28:04  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:33:26  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=cochrane_org_2, n=4\]
 2026-09-28 12:33:26  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <ul class="listing listing--news"><li><div
 class="grid"><div class="col-1/3@tabletwide"><a class="zoom"
 href="/about-us/news/commercial-sales-lead">
 </a></div>
 <div class="col-2/3@tabletwide"><p class="h6"><a class="zoom"
 href="/about-us/news/commercial-sales-lead">Commercial Sales
 Lead</a></p>
 <p class="date">10 September 2026</p>
 <p>6-month fixed term contract | Full Time | £48k per annum | Remote |
 Closing date: 4 October 2026</p>
 </div>
 </div>
 </li><li><div class="grid"><div class="col-1/3@tabletwide"><a
 class="zoom" href="/about-us/news/publishing-operations-lead">
 </a></div>
 <div class="col-2/3@tabletwide"><p class="h6"><a class="zoom"
 href="/about-us/news/publishing-operations-lead">Publishing Operations
 Lead</a></p>
 <p class="date">10 September 2026</p>
 <p>Permanent | Full Time | £45k per annum | Remote | Closing date: 7
 October 2026</p>
 </div>
 </div>
 </li></ul>
 2026-09-28 12:33:26  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=cochrane_org_2
 2026-09-28 12:33:26  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Commercial Sales Lead", "Publishing
 Operations Lead"\] containers=\["<ul class="listing
 listing--news"><li><div class="grid"><div
 class="col-1/3@tabletwide"><a class="zoom"
 href="/about-us/news/commercial-sales-lead">\\n</a></div>\\n<div
 class="col-2/3@tabletwide"><p class="h6"><a class="zoom"
 href="/about-us/news/commercial-sales-lead">Commercial Sales
 Lead</a></p>\\n<p class="date">10 September 2026</p>\\n<p>6-month
 fixed term contract | Full Time | £48k per annum | Remote | Closing
 date: 4 October 2026</p>\\n</div>\\n</div>\\n</li><li><div
 class="grid"><div class="col-1/3@tabletwide"><a class="zoom"
 href="/about-us/news/publishing-operations-lead">\\n</a></div>\\n<div
 class="col-2/3@tabletwide"><p class="h6"><a class="zoom"
 href="/about-us/news/publishing-operations-lead">Publishing
 Operations Lead</a></p>\\n<p class="date">10 September
 2026</p>\\n<p>Permanent | Full Time | £45k per annum | Remote | Closing
 date: 7 October 2026</p>\\n</div>\\n</div>\\n</li></ul>"\]
 cull_outcome='culled' dom_joined=<ul class="listing
 listing--news"><li><div class="grid"><div
 class="col-1/3@tabletwide"><a class="zoom"
 href="/about-us/news/commercial-sales-lead">
 </a></div>
 <div class="col-2/3@tabletwide"><p class="h6"><a class="zoom"
 href="/about-us/news/commercial-sales-lead">Commercial Sales
 Lead</a></p>
 <p class="date">10 September 2026</p>
 <p>6-month fixed term contract | Full Time | £48k per annum | Remote |
 Closing date: 4 October 2026</p>
 </div>
 </div>
 </li><li><div class="grid"><div class="col-1/3@tabletwide"><a
 class="zoom" href="/about-us/news/publishing-operations-lead">
 </a></div>
 <div class="col-2/3@tabletwide"><p class="h6"><a class="zoom"
 href="/about-us/news/publishing-operations-lead">Publishing Operations
 Lead</a></p>
 <p class="date">10 September 2026</p>
 <p>Permanent | Full Time | £45k per annum | Remote | Closing date: 7
 October 2026</p>
 </div>
 </div>
 </li></ul>
 2026-09-28 12:33:26  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7708799, "visible_chars": 6734,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:33:26  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>)", "text": "\\n
     \\n    \\n      \\n    \\n\\n\\n\\n\\n  \\n    \\n      \\n        \\n
  \\n             Filters\\n            Close search ✖\\n            \\n
           Filters\\n              Evidence\\n              Our
 evidence\\n              Exclude our evidence\\n
 Handbooks/Manuals\\n              Cochrane Handbook for Systematic
 Reviews of Interventions\\n              Methodological Expectations of
 Cochrane Intervention Reviews (MECIR)\\n              Cochrane Style
 Manual\\n              News\\n              News\\n              Exclude
 news\\n            \\n          \\n          \\n        \\n      \\n    \\n
 \\n\\n\\n  \\n    \\n                    \\n          \\n            \\n
          \\n    \\n  \\n    \\n        \\n\\n  \\n\\n  \\n\\n            \\n
     \\n        \\n                                      \\n          \\n
          \\n              \\n                  \\n    \\n  \\n    \\n
 \\n  Jobs\\n\\n\\n\\n  \\n\\n  \\n\\n           <43581 chars
 omitted>rackPageView"\]),\_paq.push(\["enableLinkTracking"\]),\_paq.push(\["enableHeartBeatTimer"\]),function(){\_paq.push(\["setTrackerUrl","[https://cochrane-org.matomo.cloud/matomo.php\\"\]),\_paq.push(\[\\"setSiteId\\",\\"1\\"\]),analytics_cookies&&\_paq.push(\[\\"rememberCookieConsentGiven\\](<https://cochrane-org.matomo.cloud/matomo.php%5C%22%5D),_paq.push(%5B%5C%22setSiteId%5C%22,%5C%221%5C%22%5D),analytics_cookies&&_paq.push(%5B%5C%22rememberCookieConsentGiven%5C>)",43800\]);var
 e=document,a=e.createElement("script"),t=e.getElementsByTagName("script")\[0\];a.async=!0,a.src="[https://cdn.matomo.cloud/cochrane-org.matomo.cloud/matomo.js\\](<https://cdn.matomo.cloud/cochrane-org.matomo.cloud/matomo.js%5C>)",t.parentNode.insertBefore(a,t)}();</script>\\n
  \\n\\n<ul id="ui-id-1" tabindex="0" class="ui-menu ui-widget
 ui-widget-content ui-autocomplete ui-front" style="display: none;"
 unselectable="on"></ul><div role="status" aria-live="assertive"
 aria-relevant="additions"
 class="ui-helper-hidden-accessible"></div></body>", "scrape_meta":
 {"bot_blocked": false, "cookies_dismissed": true, "issues": \[\],
 "content_chars": 6734, "requested_url":
 "[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>)", "final_url":
 "[https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>)"}}
 2026-09-28 12:33:26  \[INFO\]  8c6d1153 | telescope job done:
 [https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>) ->
 [https://www.cochrane.org/about-us/jobs](<https://www.cochrane.org/about-us/jobs>) fields:text,html
 2026-09-28 12:33:26  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:33:26  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-0dca90962bba3a32"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:33:26  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=reviveresearch_org, n=4\]
 2026-09-28 12:33:26  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div class="list-view"><div class="list-data"><div
 class="v1 sjb-job-7311"><div class="row"><div class="col-md-1 col-sm-2
 hidden-xs"><div class="company-logo">
 <a href="[https://reviveresearch.org/jobs/clinical-research-coordinator/](<https://reviveresearch.org/jobs/clinical-research-coordinator/>)"><img
 alt="Revive Research Institute, Inc." class="sjb-img-responsive
 entered litespeed-loaded"/></a></div></div><div class="col-md-11
 col-sm-12"><div class="row sjb-list-row"><div class="col-md-5
 col-sm-12"><div class="job-info"><h4>
 <a href="[https://reviveresearch.org/jobs/clinical-research-coordinator/](<https://reviveresearch.org/jobs/clinical-research-coordinator/>)">
 <span class="job-title">Clinical Research Coordinator</span> | <span
 class="company-name">Revive Research Institute, Inc.</span>
 </a></h4></div></div><div class="col-md-2 col-sm-4 col-xs-12"><div
 class="job-type">Full Time</div></div><div class="col-md-2 col-sm-4
 col-xs-12"><div class="job-location">Farmington Hills, MI, Michigan,
 Southfield, MI, Troy</div></div><div class="col-md-3 col-sm-4
 col-xs-12"><div class="job-date">Posted 3 years ago</div></div><<23287
 chars omitted>om">[zsuhrawardy@rev-research.com](<mailto:zsuhrawardy@rev-research.com>)</a> .<a
 href="[https://www.reviveresearch.org/job-location/southfield-mi/](<https://www.reviveresearch.org/job-location/southfield-mi/>)">Southfield
 Jobs</a><div class="job-features"><h3>Job Features</h3><table
 class="table"><tr><td>Job
 Category</td><td>Intern</td></tr></table></div><div
 class="clearfix"></div></div><div class="job-description"><div
 id="sjb_less_content_7319"><p>Are you looking for an unpaid or paid
 internship? Revive Research Institute is looking for college students
 for a three month internship opportunity located in Southfield, MI.
 Interns will have...</p></div><div
 class="sjb-apply-now-btn"><p></p><p><a class="btn btn-primary"
 href="javascript:void(0)" id="quick-apply-btn" job_id="7319">Quick
 Apply </a><a class="btn btn-primary"
 href="[https://reviveresearch.org/jobs/research-intern/](<https://reviveresearch.org/jobs/research-intern/>)">Read
 More</a></p><div class="sjb-view-less-btn"
 id="sjb_view_less_btn_7319"><a class="sjb_view_less_btn
 sjb_view_more_btn" data-id="7319">View
 less</a></div></div></div></div></div><div
 class="clearfix"></div></div>
 2026-09-28 12:33:26  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=reviveresearch_org
 2026-09-28 12:33:26  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["CLINICAL RESEARCH COORDINATOR",
 "Research Regulatory Coordinator", "Clinical Research Medical
 Assistant", "MEDICAL ADMINISTRATIVE ASSISTANT", "Research Intern"\]
 containers=\["<div class="list-view"><div class="list-data"><div
 class="v1 sjb-job-7311"><div class="row"><div class="col-md-1
 col-sm-2 hidden-xs"><div class="company-logo">\\n<a
 href="[https://reviveresearch.org/jobs/clinical-research-coordinator/\\](<https://reviveresearch.org/jobs/clinical-research-coordinator/%5C>)"><img
 alt="Revive Research Institute, Inc." class="sjb-img-responsive
 entered litespeed-loaded"/></a></div></div><div class="col-md-11
 col-sm-12"><div class="row sjb-list-row"><div class="col-md-5
 col-sm-12"><div class="job-info"><h4>\\n<a
 href="[https://reviveresearch.org/jobs/clinical-research-coordinator/\\](<https://reviveresearch.org/jobs/clinical-research-coordinator/%5C>)">\\n<span
 class="job-title">Clinical Research Coordinator</span> | <span
 class="company-name">Revive Research Institute, Inc.</span>
 </a></h4></div></div><div class="col-md-2 col-sm-4 col-xs-12"><div
 class="job-type">Full Time</div></div><div class="col-md-2 col-sm-4
 col-xs-12"><div class="job-location">Farmington Hills, MI,
 Michigan, Southfield, MI, Troy</div></div><div class="col-md-3
 col-sm-4 col-xs-12"><div c<23816 chars omitted><a
 href="[https://www.reviveresearch.org/job-location/southfield-mi/\\](<https://www.reviveresearch.org/job-location/southfield-mi/%5C>)">Southfield
 Jobs</a><div class="job-features"><h3>Job Features</h3><table
 class="table"><tr><td>Job
 Category</td><td>Intern</td></tr></table></div><div
 class="clearfix"></div></div><div class="job-description"><div
 id="sjb_less_content_7319"><p>Are you looking for an unpaid or paid
 internship? Revive Research Institute is looking for college students
 for a three month internship opportunity located in Southfield, MI.
 Interns will have...</p></div><div
 class="sjb-apply-now-btn"><p></p><p><a class="btn btn-primary"
 href="javascript:void(0)" id="quick-apply-btn"
 job_id="7319">Quick Apply </a><a class="btn btn-primary"
 href="[https://reviveresearch.org/jobs/research-intern/\\](<https://reviveresearch.org/jobs/research-intern/%5C>)">Read
 More</a></p><div class="sjb-view-less-btn"
 id="sjb_view_less_btn_7319"><a class="sjb_view_less_btn
 sjb_view_more_btn" data-id="7319">View
 less</a></div></div></div></div></div><div
 class="clearfix"></div></div>"\] cull_outcome='culled'
 dom_joined=<div class="list-view"><div class="list-data"><div
 class="v1 sjb-job-7311"><div class="row"><div class="col-md-1 col-sm-2
 hidden-xs"><div class="company-logo">
 <a href="[https://reviveresearch.org/jobs/clinical-research-coordinator/](<https://reviveresearch.org/jobs/clinical-research-coordinator/>)"><img
 alt="Revive Research Institute, Inc." class="sjb-img-responsive
 entered litespeed-loaded"/></a></div></div><div class="col-md-11
 col-sm-12"><div class="row sjb-list-row"><div class="col-md-5
 col-sm-12"><div class="job-info"><h4>
 <a href="[https://reviveresearch.org/jobs/clinical-research-coordinator/](<https://reviveresearch.org/jobs/clinical-research-coordinator/>)">
 <span class="job-title">Clinical Research Coordinator</span> | <span
 class="company-name">Revive Research Institute, Inc.</span>
 </a></h4></div></div><div class="col-md-2 col-sm-4 col-xs-12"><div
 class="job-type">Full Time</div></div><div class="col-md-2 col-sm-4
 col-xs-12"><div class="job-location">Farmington Hills, MI, Michigan,
 Southfield, MI, Troy</div></div><div class="col-md-3 col-sm-4
 col-xs-12"><div class="job-date">Posted 3 years ago</div></div><<23287
 chars omitted>om">[zsuhrawardy@rev-research.com](<mailto:zsuhrawardy@rev-research.com>)</a> .<a
 href="[https://www.reviveresearch.org/job-location/southfield-mi/](<https://www.reviveresearch.org/job-location/southfield-mi/>)">Southfield
 Jobs</a><div class="job-features"><h3>Job Features</h3><table
 class="table"><tr><td>Job
 Category</td><td>Intern</td></tr></table></div><div
 class="clearfix"></div></div><div class="job-description"><div
 id="sjb_less_content_7319"><p>Are you looking for an unpaid or paid
 internship? Revive Research Institute is looking for college students
 for a three month internship opportunity located in Southfield, MI.
 Interns will have...</p></div><div
 class="sjb-apply-now-btn"><p></p><p><a class="btn btn-primary"
 href="javascript:void(0)" id="quick-apply-btn" job_id="7319">Quick
 Apply </a><a class="btn btn-primary"
 href="[https://reviveresearch.org/jobs/research-intern/](<https://reviveresearch.org/jobs/research-intern/>)">Read
 More</a></p><div class="sjb-view-less-btn"
 id="sjb_view_less_btn_7319"><a class="sjb_view_less_btn
 sjb_view_more_btn" data-id="7319">View
 less</a></div></div></div></div></div><div
 class="clearfix"></div></div>
 2026-09-28 12:33:26  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7703190, "visible_chars": 17747,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:33:26  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://reviveresearch.org/careers/](<https://reviveresearch.org/careers/>)", "text": " \\n\\n
 \\n\\nHit enter to search or ESC to close\\nSearchClose Search\\n
 \\t\\t\\t\\t \\nCareers \\t\\t\\t\\t\\t\\tHome | Careers\\n\\n\\nCategoryClinical
 Research   Intern\\n\\nJob TypeFull TimeInternship\\n\\nLocationFarmington
 Hills, MIKingman, AZMichiganSouthfield, MITroy\\n\\nUnique opportunity
 to make an Impact in the healthcare industry…IMPROVE THE FUTURE AS OUR
 CLINICAL RESEARCH COORDINATOR!The professional we select for Revival
 Research Institute will have an overall responsibility to enhance our
 operational efficiency, market presence, affiliated partnerships, and
 staff development/performance.The qualified candidate we are looking
 for should be genuinely respectful of diverse points-of-view and
 strive for an environment in which inclusiveness drives productivity
 and results.Other requirements include:Bachelor’s degree with a
 Masters in a science-related field highly desired, or extensive
 experience in Clinical Research 2+ years of incr<133700 chars
 omitted>ups allow-same-origin allow-scripts allow-top-navigation
 allow-modals allow-popups-to-escape-sandbox
 allow-storage-access-by-user-activation"
 src="[https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LfnEm4rAAAAAH92Y8i-TpJF50j9lcm33jxMeK5-&co=aHR0cHM6Ly9yZXZpdmVyZXNlYXJjaC5vcmc6NDQz&hl=en&v=kemdRjWFxNjgsGdhRslyEPwU&size=invisible&anchor-ms=20000&execute-ms=30000&cb=yfmnkteb2add\\](<https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LfnEm4rAAAAAH92Y8i-TpJF50j9lcm33jxMeK5-&co=aHR0cHM6Ly9yZXZpdmVyZXNlYXJjaC5vcmc6NDQz&hl=en&v=kemdRjWFxNjgsGdhRslyEPwU&size=invisible&anchor-ms=20000&execute-ms=30000&cb=yfmnkteb2add%5C>)"></iframe></div><div
 class="grecaptcha-error"></div><textarea
 id="g-recaptcha-response-100000" name="g-recaptcha-response"
 class="g-recaptcha-response" style="width: 250px; height: 40px;
 border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px;
 resize: none; display: none;"></textarea></div><iframe
 style="display: none;"></iframe></div></body>", "scrape_meta":
 {"bot_blocked": false, "cookies_dismissed": false, "issues": \[\],
 "content_chars": 17747, "requested_url":
 "[https://reviveresearch.org/careers](<https://reviveresearch.org/careers>)", "final_url":
 "[https://reviveresearch.org/careers/](<https://reviveresearch.org/careers/>)"}}
 2026-09-28 12:33:26  \[INFO\]  e7195918 | telescope job done:
 [https://reviveresearch.org/careers](<https://reviveresearch.org/careers>) ->
 [https://reviveresearch.org/careers/](<https://reviveresearch.org/careers/>) fields:text,html
 2026-09-28 12:33:26  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:33:26  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-0ffb2a95be901829"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:33:26  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=psy_unihamburg_de, n=4\]
 2026-09-28 12:33:26  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <table class="noautoscale"
 id="bewerberportal"><tr><th>Stellenbezeichnung</th><th>Einrichtung</th><th>Vergütung</th><th>Bewerbungsfrist</th></tr><tr
 class="datensatz" data-einrichtung=",zd," data-fuehrung="nein"
 data-rid="2cd00972f9eab88bd5e0dcbefd4f767c8507c092"
 data-stellentyp="i" data-verg="E9A" id="bewerberportaltr0"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=2cd00972f9eab88bd5e0dcbefd4f767c8507c092">Technische
 Assistenz im Institut für Organische Chemie</a><span>Kennziffer</span>
 (602/9)</td><td>Fakultät für Mathematik, Informatik und
 Naturwissenschaften (Fachbereich Chemie)</td><td>EGR. 9A
 TV-L</td><td>28.09.2026</td></tr><tr class="datensatz"
 data-einrichtung=",zd,,zb," data-fuehrung="nein"
 data-rid="b771f9ec22ecb121240cdbf53af62d2550303a7f"
 data-stellentyp="d" data-verg="E13" id="bewerberportaltr1"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=b771f9ec22ecb121240cdbf53af62d2550303a7f">Research
 Associate for the Project “Cluster of Excellence, BlueMat: Water<14550
 chars omitted>ata-fuehrung="nein"
 data-rid="23952bc5eff9a8a908d5d2ed04ca1b446ea0281c"
 data-stellentyp="d" data-verg="E13" id="bewerberportaltr29"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=23952bc5eff9a8a908d5d2ed04ca1b446ea0281c">Wissenschaftliche:r
 Mitarbeiter:in § 28 Abs. 1 HmbHG</a><span>Kennziffer</span>
 (179)</td><td>Fakultät für Rechtswissenschaft</td><td>EGR. 13
 TV-L</td><td>31.10.2026</td></tr><tr class="datensatz"
 data-einrichtung=",za," data-fuehrung="ja"
 data-rid="f640e4898870a5fef69e751fb5ecb1e2466c6864"
 data-stellentyp="a" data-verg="W3" id="bewerberportaltr30"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=f640e4898870a5fef69e751fb5ecb1e2466c6864">W3
 Universitätsprofessur für Neuere Geschichte, insbesondere
 Zeitgeschichte in Verbindung mit der Position wissenschaftliche:r
 Direktor:in der Forschungsstelle für Zeitgeschichte in Hamburg
 (FZH)</a><span>Kennziffer</span> (2459/W3)</td><td>Fakultät für
 Geisteswissenschaften</td><td>W3</td><td>05.11.2026</td></tr></table>
 2026-09-28 12:33:26  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=psy_unihamburg_de
 2026-09-28 12:33:26  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Technische Assistenz im Institut für
 Organische Chemie", "Research Associate for the Project “Cluster of
 Excellence, BlueMat: Water-driven Materials – Tunable Hydraulic and
 Capillarity-Driven Water Flow in Nanoporous Materials” § 28 Subsection
 3 HmbHG", "Research Associate (Postdoc) Functional Ecology  § 28
 Subsection 2 HmbHG", "Research Associate “Ecology of living marine
 resources” § 28 Subsection 1 HmbHG", "Research Associate for the
 Project “CLICCS” in Political Science, Economics, or a related field §
 28 Subsection 3 HmbHG", "Wissenschaftliche:r Mitarbeiter:in (Postdoc)
 Habilitation im Bereich Computational Systems Biomedicine § 28 Abs. 2
 HmbHG", "Research Associate for the Project “Automated multi-writer
 Handwritten Text Recognition with continual learning (HTRcl)” (Centre
 for the Study of Manuscript Cultures) § 28 Subsection 3 HmbHG",
 "Research Associate for the Project “Cluster of Excellence, BlueMat:
 Water-driven Materials – Energy Storage in Supercapacitors” § 28
 Subsection 3 HmbHG", "Research Associate for the Project “MOMENTplus”
 § 28 Subsection 3 HmbHG", "Teamassistenz der Psychotherapeutischen
 Hochschulambulanz"\] containers=\["<table class="noautoscale"
 id="bewerberportal"><tr><th>Stellenbezeichnung</th><th>Einrichtung</th><th>Vergütung</th><th>Bewerbungsfrist</th></tr><tr
 class="datensatz" data-einrichtung=",zd," data-fuehrung="nein"
 data-rid="2cd00972f9eab88bd5e0dcbefd4f767c8507c092"
 data-stellentyp="i" data-verg="E9A"
 id="bewerberportaltr0"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=2cd00972f9eab88bd5e0dcbefd4f767c8507c092">Technische
 Assistenz im Institut für Organische Chemie</a><span>Kennziffer</span>
 (602/9)</td><td>Fakultät für Mathematik, Informatik und
 Naturwissenschaften (Fachbereich Chemie)</td><td>EGR. 9A
 TV-L</td><td>28.09.2026</td></tr><tr class="datensatz"
 data-einrichtung=",zd,,zb," data-fuehrung="nein"
 data-rid="b771f9ec22ecb121240cdbf53af62d2550303a7f"
 data-stellentyp="d" data-verg="E13"
 id="bewerberportaltr1"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=b771f9ec22ecb121240cdbf53af62d2550303a7f">Research
 Associate for the Project <15054 chars
 omitted>="23952bc5eff9a8a908d5d2ed04ca1b446ea0281c"
 data-stellentyp="d" data-verg="E13"
 id="bewerberportaltr29"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=23952bc5eff9a8a908d5d2ed04ca1b446ea0281c">Wissenschaftliche:r
 Mitarbeiter:in § 28 Abs. 1 HmbHG</a><span>Kennziffer</span>
 (179)</td><td>Fakultät für Rechtswissenschaft</td><td>EGR. 13
 TV-L</td><td>31.10.2026</td></tr><tr class="datensatz"
 data-einrichtung=",za," data-fuehrung="ja"
 data-rid="f640e4898870a5fef69e751fb5ecb1e2466c6864"
 data-stellentyp="a" data-verg="W3"
 id="bewerberportaltr30"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=f640e4898870a5fef69e751fb5ecb1e2466c6864">W3
 Universitätsprofessur für Neuere Geschichte, insbesondere
 Zeitgeschichte in Verbindung mit der Position wissenschaftliche:r
 Direktor:in der Forschungsstelle für Zeitgeschichte in Hamburg
 (FZH)</a><span>Kennziffer</span> (2459/W3)</td><td>Fakultät für
 Geisteswissenschaften</td><td>W3</td><td>05.11.2026</td></tr></table>"\]
 cull_outcome='culled' dom_joined=<table class="noautoscale"
 id="bewerberportal"><tr><th>Stellenbezeichnung</th><th>Einrichtung</th><th>Vergütung</th><th>Bewerbungsfrist</th></tr><tr
 class="datensatz" data-einrichtung=",zd," data-fuehrung="nein"
 data-rid="2cd00972f9eab88bd5e0dcbefd4f767c8507c092"
 data-stellentyp="i" data-verg="E9A" id="bewerberportaltr0"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=2cd00972f9eab88bd5e0dcbefd4f767c8507c092">Technische
 Assistenz im Institut für Organische Chemie</a><span>Kennziffer</span>
 (602/9)</td><td>Fakultät für Mathematik, Informatik und
 Naturwissenschaften (Fachbereich Chemie)</td><td>EGR. 9A
 TV-L</td><td>28.09.2026</td></tr><tr class="datensatz"
 data-einrichtung=",zd,,zb," data-fuehrung="nein"
 data-rid="b771f9ec22ecb121240cdbf53af62d2550303a7f"
 data-stellentyp="d" data-verg="E13" id="bewerberportaltr1"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=b771f9ec22ecb121240cdbf53af62d2550303a7f">Research
 Associate for the Project “Cluster of Excellence, BlueMat: Water<14550
 chars omitted>ata-fuehrung="nein"
 data-rid="23952bc5eff9a8a908d5d2ed04ca1b446ea0281c"
 data-stellentyp="d" data-verg="E13" id="bewerberportaltr29"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=23952bc5eff9a8a908d5d2ed04ca1b446ea0281c">Wissenschaftliche:r
 Mitarbeiter:in § 28 Abs. 1 HmbHG</a><span>Kennziffer</span>
 (179)</td><td>Fakultät für Rechtswissenschaft</td><td>EGR. 13
 TV-L</td><td>31.10.2026</td></tr><tr class="datensatz"
 data-einrichtung=",za," data-fuehrung="ja"
 data-rid="f640e4898870a5fef69e751fb5ecb1e2466c6864"
 data-stellentyp="a" data-verg="W3" id="bewerberportaltr30"><td><a
 href="/stellenangebote/ausschreibung.html?jobID=f640e4898870a5fef69e751fb5ecb1e2466c6864">W3
 Universitätsprofessur für Neuere Geschichte, insbesondere
 Zeitgeschichte in Verbindung mit der Position wissenschaftliche:r
 Direktor:in der Forschungsstelle für Zeitgeschichte in Hamburg
 (FZH)</a><span>Kennziffer</span> (2459/W3)</td><td>Fakultät für
 Geisteswissenschaften</td><td>W3</td><td>05.11.2026</td></tr></table>
 2026-09-28 12:33:26  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7690627, "visible_chars": 8028,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:33:26  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)",
 "text": "Zur MetanavigationZur HauptnavigationZur SucheZum InhaltZum
 SeitenfußFoto: UHH/EsfandiariStellenangebote der Universität
 HamburgHerzlich willkommen im Stellenportal der Universität Hamburg!
 Als eine der größten Universitäten Deutschlands verbinden wir ein
 vielfältiges und spannendes Lehrangebot mit exzellenter Forschung.
 Hier finden sich zahlreiche attraktive Karrierechancen, die auf
 neugierige und engagierte Talente warten. Wir freuen uns auf jede
 Bewerbung und darauf, gemeinsam die Zukunft zu gestalten!\\nInternes
 Stellenportal\\nJobbörse für Studierende\\n\\n\\n
 SucheStellentypStellentyp:
 AlleAlleProfessurenJuniorprofessurenVertretung von
 ProfessurenWissenschaftliches
 PersonalVerwaltungspersonalBibliothekspersonalFremdsprachliches
 PersonalIT-PersonalTechnisches
 PersonalAusbildungsplätzeVolontariatEinrichtungEinrichtung:
 AlleAlleFakultät für Re<67975 chars omitted>Zur Seite
 Systemakkreditierung"
 src="[https://assets.rrz.uni-hamburg.de/assets/AR-Siegel_81x81-aeebcf80607271e52345b193956c4aba9970c59d505a67449d6046fe89deb5a0.svg\\](<https://assets.rrz.uni-hamburg.de/assets/AR-Siegel_81x81-aeebcf80607271e52345b193956c4aba9970c59d505a67449d6046fe89deb5a0.svg%5C>)"></a></div></div><p
 class="copyright">© 2026 Universität Hamburg. Alle Rechte
 vorbehalten</p></nav></section></footer></div><div
 id="sponsors"></div><script>console.log('document ready: ' +
 ([Date.now](<http://Date.now>)() - t0) + ' ms');\\nvar t1 = [Date.now](<http://Date.now>)();</script><div
 class="tracking" style="display:none"><div
 class="etracker">OBVZu9</div></div><button type="button"
 id="scrollTopButton2" aria-label="nach oben scrollen"
 class=""></button></body>", "scrape_meta": {"bot_blocked": false,
 "cookies_dismissed": false, "issues": \[\], "content_chars": 8028,
 "requested_url":
 "[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)",
 "final_url": "[https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)"}}
 2026-09-28 12:33:26  \[INFO\]  1324363e | telescope job done:
 [https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)
 -> [https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de](<https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de>)
 fields:text,html
 2026-09-28 12:33:26  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:33:26  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-707ea2bc5134da7c"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:33:26  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=huggingface_co, n=4\]
 2026-09-28 12:33:26  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <ul class="styles--Qqz1P" data-ui="list" role="list"><li
 class="styles--1vo9F" data-id="DB4D7C0EC8" data-ui="job"
 role="listitem"><a aria-labelledby="DB4D7C0EC8_title
 DB4D7C0EC8_posted_on DB4D7C0EC8_department" class="styles--1OnOt"
 href="/huggingface/j/DB4D7C0EC8/"></a><div><h3 class="styles--3TJHk"
 data-ui="job-title" id="DB4D7C0EC8_title"><span>Senior Open-Source
 Python Engineer, ML Developer Tools - EMEA
 Remote</span></h3></div><span class="styles--QTMDv styles--2TdGW
 styles--2I8DW" data-ui="job-workplace">Remote</span><div
 class="styles--1Sarc undefined styles--Xn8hR"
 data-ui="job-location"></div><span class="" data-ui="job-department"
 id="DB4D7C0EC8_department">Product</span><span class=""
 data-ui="job-type">Full time</span></li><li class="styles--1vo9F"
 data-id="F88446C814" data-ui="job" role="listitem"><a
 aria-labelledby="F88446C814_title F88446C814_posted_on
 F88446C814_department" class="styles--1OnOt"
 href="/huggingface/j/F88446C814/"></a><div><h3 class="styles--3TJHk"
 data-u<3332 chars omitted>an></div></div><span class=""
 data-ui="job-department" id="19A136F8E2_department">Open
 Source</span><span class="" data-ui="job-type">Full
 time</span></li><li class="styles--1vo9F" data-id="0BD8C06DB3"
 data-ui="job" role="listitem"><a aria-labelledby="0BD8C06DB3_title
 0BD8C06DB3_posted_on 0BD8C06DB3_department 0BD8C06DB3_locations"
 class="styles--1OnOt" href="/huggingface/j/0BD8C06DB3/"></a><div><h3
 class="styles--3TJHk" data-ui="job-title"
 id="0BD8C06DB3_title"><span>Wild Card</span></h3></div><span
 class="styles--QTMDv styles--2TdGW styles--2I8DW"
 data-ui="job-workplace">Remote</span><div class="styles--1Sarc
 styles--Xn8hR" data-ui="job-location" id="0BD8C06DB3_locations"><div
 class="styles--11q6G" data-ui="job-location-tooltip"><span
 data-ellipsis-element="true"><span class="styles--QTMDv
 styles--2TdGW">United States</span></span></div></div><span class=""
 data-ui="job-department" id="0BD8C06DB3_department">Wild
 Card</span><span class="" data-ui="job-type">Full
 time</span></li></ul>
 2026-09-28 12:33:26  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=huggingface_co
 2026-09-28 12:33:26  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Senior Open-Source Python Engineer, ML
 Developer Tools - EMEA Remote", "Senior Open-Source Python Engineer,
 ML Developer Tools - US Remote", "Senior Machine Learning Engineer,
 Voice Agents - EMEA Remote", "Low-Level Senior Software Engineer, Xet
 Storage - US Remote", "Low-level Senior Software Engineer, Xet Storage

* EMEA Remote", "Open-Source Machine Learning Engineer - US Remote",
  "Wild Card"\] containers=\["<ul class="styles--Qqz1P" data-ui="list"
  role="list"><li class="styles--1vo9F" data-id="DB4D7C0EC8"
  data-ui="job" role="listitem"><a
  aria-labelledby="DB4D7C0EC8_title DB4D7C0EC8_posted_on
  DB4D7C0EC8_department" class="styles--1OnOt"
  href="/huggingface/j/DB4D7C0EC8/"></a><div><h3
  class="styles--3TJHk" data-ui="job-title"
  id="DB4D7C0EC8_title"><span>Senior Open-Source Python Engineer, ML
  Developer Tools - EMEA Remote</span></h3></div><span
  class="styles--QTMDv styles--2TdGW styles--2I8DW"
  data-ui="job-workplace">Remote</span><div class="styles--1Sarc
  undefined styles--Xn8hR" data-ui="job-location"></div><span
  class="" data-ui="job-department"
  id="DB4D7C0EC8_department">Product</span><span class=""
  data-ui="job-type">Full time</span></li><li class="styles--1vo9F"
  data-id="F88446C814" data-ui="job" role="listitem"><a
  aria-labelledby="F88446C814_title F88446C814_posted_on
  F88446C814_department" class="styles--1OnOt" href="/huggingfa<3632
  chars omitted>d="19A136F8E2_department">Open Source</span><span
  class="" data-ui="job-type">Full time</span></li><li
  class="styles--1vo9F" data-id="0BD8C06DB3" data-ui="job"
  role="listitem"><a aria-labelledby="0BD8C06DB3_title
  0BD8C06DB3_posted_on 0BD8C06DB3_department 0BD8C06DB3_locations"
  class="styles--1OnOt"
  href="/huggingface/j/0BD8C06DB3/"></a><div><h3
  class="styles--3TJHk" data-ui="job-title"
  id="0BD8C06DB3_title"><span>Wild Card</span></h3></div><span
  class="styles--QTMDv styles--2TdGW styles--2I8DW"
  data-ui="job-workplace">Remote</span><div class="styles--1Sarc
  styles--Xn8hR" data-ui="job-location"
  id="0BD8C06DB3_locations"><div class="styles--11q6G"
  data-ui="job-location-tooltip"><span
  data-ellipsis-element="true"><span class="styles--QTMDv
  styles--2TdGW">United States</span></span></div></div><span
  class="" data-ui="job-department"
  id="0BD8C06DB3_department">Wild Card</span><span class=""
  data-ui="job-type">Full time</span></li></ul>"\]
  cull_outcome='culled' dom_joined=<ul class="styles--Qqz1P"
  data-ui="list" role="list"><li class="styles--1vo9F"
  data-id="DB4D7C0EC8" data-ui="job" role="listitem"><a
  aria-labelledby="DB4D7C0EC8_title DB4D7C0EC8_posted_on
  DB4D7C0EC8_department" class="styles--1OnOt"
  href="/huggingface/j/DB4D7C0EC8/"></a><div><h3 class="styles--3TJHk"
  data-ui="job-title" id="DB4D7C0EC8_title"><span>Senior Open-Source
  Python Engineer, ML Developer Tools - EMEA
  Remote</span></h3></div><span class="styles--QTMDv styles--2TdGW
  styles--2I8DW" data-ui="job-workplace">Remote</span><div
  class="styles--1Sarc undefined styles--Xn8hR"
  data-ui="job-location"></div><span class="" data-ui="job-department"
  id="DB4D7C0EC8_department">Product</span><span class=""
  data-ui="job-type">Full time</span></li><li class="styles--1vo9F"
  data-id="F88446C814" data-ui="job" role="listitem"><a
  aria-labelledby="F88446C814_title F88446C814_posted_on
  F88446C814_department" class="styles--1OnOt"
  href="/huggingface/j/F88446C814/"></a><div><h3 class="styles--3TJHk"
  data-u<3332 chars omitted>an></div></div><span class=""
  data-ui="job-department" id="19A136F8E2_department">Open
  Source</span><span class="" data-ui="job-type">Full
  time</span></li><li class="styles--1vo9F" data-id="0BD8C06DB3"
  data-ui="job" role="listitem"><a aria-labelledby="0BD8C06DB3_title
  0BD8C06DB3_posted_on 0BD8C06DB3_department 0BD8C06DB3_locations"
  class="styles--1OnOt" href="/huggingface/j/0BD8C06DB3/"></a><div><h3
  class="styles--3TJHk" data-ui="job-title"
  id="0BD8C06DB3_title"><span>Wild Card</span></h3></div><span
  class="styles--QTMDv styles--2TdGW styles--2I8DW"
  data-ui="job-workplace">Remote</span><div class="styles--1Sarc
  styles--Xn8hR" data-ui="job-location" id="0BD8C06DB3_locations"><div
  class="styles--11q6G" data-ui="job-location-tooltip"><span
  data-ellipsis-element="true"><span class="styles--QTMDv
  styles--2TdGW">United States</span></span></div></div><span class=""
  data-ui="job-department" id="0BD8C06DB3_department">Wild
  Card</span><span class="" data-ui="job-type">Full
  time</span></li></ul>
  2026-09-28 12:33:26  \[DEBUG\]  1068: Response from scrape_page:
  {"outcome": "ready", "wait_ms": 7688858, "visible_chars": 4539,
  "load_all_jobs_ran": true, "ready": true}
  2026-09-28 12:33:26  \[DEBUG\]  566: Response from \_post_telescope:
  {"final_url": "[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>)", "text": " Job
  OpeningsIf you're interested in joining us, but don't tick every box,
  we still encourage you to apply! We're building a diverse team whose
  skills, experiences, and background complement one another. \\n\\nHot
  tip: unclick your automatically detected location below to see all
  available jobs as you can apply to them from any location!\\nJob
  Openings8 jobsWorkplace typeLocationWork typeUnited StatesDismiss
  United StatesClear filters We’ve detected your location and are
  showing jobs in United States. Clear the filters to display jobs in
  all locations. Senior Open-Source Python Engineer, ML Developer Tools
* EMEA RemoteRemoteProductFull timeSenior Open-Source Python Engineer,
  ML Developer Tools - US RemoteRemoteProductFull timeSenior Machine
  Learning Engineer, Voice Agents - EMEA RemoteRemoteScienceFull
  timeLow-Level Senior Software Engineer, Xet Storage - US
  RemoteRemoteProductFull timeLow-level Senior Software Engineer,
  Xe<511303 chars omitted>um=feature&utm_source=careers_page"
  rel="noreferrer"
  target="\_blank">Workable</a></span></div></footer></div></div><iframe
  height="1" width="1" style="position: absolute; top: 0px; left:
  0px; border: medium; visibility: hidden;"></iframe><noscript><iframe
  height="0" width="0" style="display: none; visibility: hidden;"
  src="[https://www.googletagmanager.com/ns.html?id=GTM-WKS7WTT&gtm_auth=SGnzIn3pcB7S4fevFXOKPQ&gtm_preview=env-2&gtm_cookies_win=x\\](<https://www.googletagmanager.com/ns.html?id=GTM-WKS7WTT&gtm_auth=SGnzIn3pcB7S4fevFXOKPQ&gtm_preview=env-2&gtm_cookies_win=x%5C>)"></iframe></noscript><iframe
  id="\_hjSafeContext_36081425" title="\_hjSafeContext"
  tabindex="-1" aria-hidden="true" src="about:blank"
  style="display: none !important; width: 1px !important; height: 1px
  !important; opacity: 0 !important; pointer-events: none
  !important;"></iframe></body>", "scrape_meta": {"bot_blocked": false,
  "cookies_dismissed": true, "issues": \[\], "content_chars": 4539,
  "requested_url": "[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>)",
  "final_url": "[https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>)"}}
  2026-09-28 12:33:26  \[INFO\]  bd321bd4 | telescope job done:
  [https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>) ->
  [https://apply.workable.com/huggingface](<https://apply.workable.com/huggingface>) fields:text,html
  2026-09-28 12:33:26  \[DEBUG\]  2174: Calling send_to_deepseek:
  \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
  max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
  2026-09-28 12:33:26  \[DEBUG\]  1341: Response from
  \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
  "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
  {"type": "CACHE_A", "id":
  "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
  {"type": "NO_CACHE", "id":
  "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-658d3e0556f09c10"},
  {"type": "TASK", "id":
  "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
  2026-09-28 12:33:26  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
  \[entity_type=company, task_key=parse_job_list,
  batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
  entity_id=bcchr_ca, n=4\]
  2026-09-28 12:33:26  \[DEBUG\]  3243: Calling agent.do_task
  live_content: Google Tag Manager (noscript)

End Google Tag Manager (noscript)
 <div class="wp-site-blocks"><div class="fndry-container
 fndry-responsive-bg fndry-responsive-border fndry-container--full
 fndry-pb--3 fndry-pt--0 fndry-pr--md-2 fndry-pl--md-2">
 <div class="fndry-container fndry-responsive-bg
 fndry-responsive-border fndry-pt--0">
 <div class="fndry-row fndry-align--start fndry-align--md-center
 fndry-justify--between fndry-justify--md-between">
 <div class="fndry-col fndry-responsive-bg fndry-col--3 fndry-col--md-4
 fndry-pt--2 fndry-pl--2 fndry-pl--md-1">
 <div class="wp-block-site-logo"><a class="custom-logo-link"
 href="[https://www.bcchr.ca/](<https://www.bcchr.ca/>)" rel="home"><img alt="BC Children’s
 Hospital Research Institute (BCCHR)"
 class="custom-logo"/></a></div></div>
 <div class="fndry-col fndry-responsive-bg fndry-col--9 fndry-col--md-6
 fndry-d--flex fndry-d--md-none fndry-flex--row fndry-align--center
 fndry-justify--end">
 <div class="fndry-container fndry-responsive-bg
 fndry-responsive-border fndry-pr--m<34073 chars omitted>container
 fndry-responsive-bg fndry-responsive-border mobile-border-bottom
 fndry-pt--3 fndry-pr--0 fndry-pl--0 fndry-pb--md-2">
 <div class="fndry-row fndry-row--gutter">
 <div class="fndry-col fndry-responsive-bg fndry-col--12 fndry-d--flex
 fndry-flex--col fndry-align--start fndry-justify--start">
 <a class="fndry-btn fndry-mb--2 fndry-btn-headerLogin"
 href="[http://www.bcchildrens.ca/](<http://www.bcchildrens.ca/>)" id="fndry-block-6509f4756b140"
 rel="" target="\_blank">BC Children’s Hospital</a><a class="fndry-btn
 fndry-mb--2 fndry-btn-headerLogin" href="[https://www.bcchf.ca/](<https://www.bcchf.ca/>)"
 id="fndry-block-6414d467f8311" rel="" target="\_blank">BC Children’s
 Hospital Foundation</a></div>
 </div></div>
 </div>
 </div></div>
 </div>
 </div></div>
 </div>
 </div>

<div aria-atomic="true" aria-live="assertive" aria-relevant="additions
 text" class="a11y-speak-region" id="a11y-speak-assertive"></div><div
 aria-atomic="true" aria-live="polite" aria-relevant="additions text"
 class="a11y-speak-region" id="a11y-speak-polite"></div>
 2026-09-28 12:33:26  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=bcchr_ca
 2026-09-28 12:33:26  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Manager, Research IT, BC Children’s
 Hospital Research Institute"\] containers=\["Google Tag Manager
 (noscript) \\n\\n End Google Tag Manager (noscript) \\n<div
 class="wp-site-blocks"><div class="fndry-container
 fndry-responsive-bg fndry-responsive-border fndry-container--full
 fndry-pb--3 fndry-pt--0 fndry-pr--md-2 fndry-pl--md-2">\\n<div
 class="fndry-container fndry-responsive-bg fndry-responsive-border
 fndry-pt--0">\\n<div class="fndry-row fndry-align--start
 fndry-align--md-center fndry-justify--between
 fndry-justify--md-between">\\n<div class="fndry-col
 fndry-responsive-bg fndry-col--3 fndry-col--md-4 fndry-pt--2
 fndry-pl--2 fndry-pl--md-1">\\n<div class="wp-block-site-logo"><a
 class="custom-logo-link" href="[https://www.bcchr.ca/\\](<https://www.bcchr.ca/%5C>)"
 rel="home"><img alt="BC Children’s Hospital Research Institute
 (BCCHR)" class="custom-logo"/></a></div></div>\\n<div
 class="fndry-col fndry-responsive-bg fndry-col--9 fndry-col--md-6
 fndry-d--flex fndry-d--md-none fndry-flex--row fndry-align--center
 fndry-justify--end">\\n<div class="fndry-container
 fndry-responsive-bg<35920 chars omitted>ry-pt--3 fndry-pr--0
 fndry-pl--0 fndry-pb--md-2">\\n<div class="fndry-row
 fndry-row--gutter">\\n<div class="fndry-col fndry-responsive-bg
 fndry-col--12 fndry-d--flex fndry-flex--col fndry-align--start
 fndry-justify--start">\\n<a class="fndry-btn fndry-mb--2
 fndry-btn-headerLogin" href="[http://www.bcchildrens.ca/\\](<http://www.bcchildrens.ca/%5C>)"
 id="fndry-block-6509f4756b140" rel="" target="\_blank">BC
 Children’s Hospital</a><a class="fndry-btn fndry-mb--2
 fndry-btn-headerLogin" href="[https://www.bcchf.ca/\\](<https://www.bcchf.ca/%5C>)"
 id="fndry-block-6414d467f8311" rel="" target="\_blank">BC
 Children’s Hospital
 Foundation</a></div>\\n</div></div>\\n</div>\\n</div></div>\\n</div>\\n</div></div>\\n</div>\\n</div>\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n<div
 aria-atomic="true" aria-live="assertive" aria-relevant="additions
 text" class="a11y-speak-region"
 id="a11y-speak-assertive"></div><div aria-atomic="true"
 aria-live="polite" aria-relevant="additions text"
 class="a11y-speak-region" id="a11y-speak-polite"></div>"\]
 cull_outcome='full_dom' dom_joined=Google Tag Manager (noscript)

End Google Tag Manager (noscript)
 <div class="wp-site-blocks"><div class="fndry-container
 fndry-responsive-bg fndry-responsive-border fndry-container--full
 fndry-pb--3 fndry-pt--0 fndry-pr--md-2 fndry-pl--md-2">
 <div class="fndry-container fndry-responsive-bg
 fndry-responsive-border fndry-pt--0">
 <div class="fndry-row fndry-align--start fndry-align--md-center
 fndry-justify--between fndry-justify--md-between">
 <div class="fndry-col fndry-responsive-bg fndry-col--3 fndry-col--md-4
 fndry-pt--2 fndry-pl--2 fndry-pl--md-1">
 <div class="wp-block-site-logo"><a class="custom-logo-link"
 href="[https://www.bcchr.ca/](<https://www.bcchr.ca/>)" rel="home"><img alt="BC Children’s
 Hospital Research Institute (BCCHR)"
 class="custom-logo"/></a></div></div>
 <div class="fndry-col fndry-responsive-bg fndry-col--9 fndry-col--md-6
 fndry-d--flex fndry-d--md-none fndry-flex--row fndry-align--center
 fndry-justify--end">
 <div class="fndry-container fndry-responsive-bg
 fndry-responsive-border fndry-pr--m<34073 chars omitted>container
 fndry-responsive-bg fndry-responsive-border mobile-border-bottom
 fndry-pt--3 fndry-pr--0 fndry-pl--0 fndry-pb--md-2">
 <div class="fndry-row fndry-row--gutter">
 <div class="fndry-col fndry-responsive-bg fndry-col--12 fndry-d--flex
 fndry-flex--col fndry-align--start fndry-justify--start">
 <a class="fndry-btn fndry-mb--2 fndry-btn-headerLogin"
 href="[http://www.bcchildrens.ca/](<http://www.bcchildrens.ca/>)" id="fndry-block-6509f4756b140"
 rel="" target="\_blank">BC Children’s Hospital</a><a class="fndry-btn
 fndry-mb--2 fndry-btn-headerLogin" href="[https://www.bcchf.ca/](<https://www.bcchf.ca/>)"
 id="fndry-block-6414d467f8311" rel="" target="\_blank">BC Children’s
 Hospital Foundation</a></div>
 </div></div>
 </div>
 </div></div>
 </div>
 </div></div>
 </div>
 </div>

<div aria-atomic="true" aria-live="assertive" aria-relevant="additions
 text" class="a11y-speak-region" id="a11y-speak-assertive"></div><div
 aria-atomic="true" aria-live="polite" aria-relevant="additions text"
 class="a11y-speak-region" id="a11y-speak-polite"></div>
 2026-09-28 12:33:26  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7685384, "visible_chars": 3793,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:33:26  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://www.bcchr.ca/careers/](<https://www.bcchr.ca/careers/>)", "text":
 "\\n\\n\\n\\n\\n\\n\\n\\n\\t\\n\\t\\n\\t\\n\\t\\n\\t\\n\\tBC Children’s Hospital Research
 Institute (BCCHR)Careers\\nCareersFurther your career as part of our
 vibrant research community.\\n\\n\\n\\n\\n\\n\\t\\n\\t\\n\\tWorking HereAre you
 passionate about child health research? Are you driven to discover,
 innovate, and achieve to transform the lives of kids in British
 Columbia and around the world? Join our team!Our 400+ investigators
 are relentless in the pursuit of discoveries and the translation of
 research into improved care, life-saving treatments, and excellence in
 child health. They are supported by the best and brightest trainees,
 skilled research staff, and a talented and dedicated administrative
 team.Members of our research and administrative staff are designated
 employees of either the Provincial Health Services Authority (PHSA) or
 the University of British Columbia (UBC).For Human Resources
 inquiries, contact: [hr@bcchr.ca](<mailto:hr@bcchr.ca>)\\n\\n\\t\\n\\t\\n\\n\\n\\n\\n\\n\\t\\n\\t<95234
 chars omitted>0;height:1px;width:1px;overflow:hidden;clip-path:inset(50%);border:0;word-wrap:normal
 !important;word-break:normal !important;"
 hidden="">Notifications</p><div id="a11y-speak-assertive"
 class="a11y-speak-region"
 style="position:absolute;margin:-1px;padding:0;height:1px;width:1px;overflow:hidden;clip-path:inset(50%);border:0;word-wrap:normal
 !important;word-break:normal !important;" aria-live="assertive"
 aria-relevant="additions text" aria-atomic="true"></div><div
 id="a11y-speak-polite" class="a11y-speak-region"
 style="position:absolute;margin:-1px;padding:0;height:1px;width:1px;overflow:hidden;clip-path:inset(50%);border:0;word-wrap:normal
 !important;word-break:normal !important;" aria-live="polite"
 aria-relevant="additions text" aria-atomic="true"></div></body>",
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 3793, "requested_url":
 "[https://www.bcchr.ca/careers](<https://www.bcchr.ca/careers>)", "final_url":
 "[https://www.bcchr.ca/careers/](<https://www.bcchr.ca/careers/>)"}}
 2026-09-28 12:33:26  \[INFO\]  d4777c60 | telescope job done:
 [https://www.bcchr.ca/careers](<https://www.bcchr.ca/careers>) -> [https://www.bcchr.ca/careers/](<https://www.bcchr.ca/careers/>)
 fields:text,html
 2026-09-28 12:33:26  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:33:26  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-1204b92a2210d27f"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:33:26  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=volvogroup_com_2, n=4\]
 2026-09-28 12:33:26  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div id="job--table"><div id="job--table--head"><span
 class="job--table--cell">Available Jobs (612)</span><span
 class="job--table--cell">Job Category</span><span
 class="job--table--cell">Organization</span><span
 class="job--table--cell">Location</span><span
 class="job--table--cell">Position Type</span><span
 class="job--table--cell">Posted</span></div><a class="job--table--row"
 href="[https://jobs.volvogroup.com/job/Hwaseong-People-&-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555](<https://jobs.volvogroup.com/job/Hwaseong-People-&-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555>)"
 title="People & Culture Coordinator Professional"><span
 class="job--table--cell job--table--title job--table--mobile"
 data-id="title" data-mobile="Available Jobs ">People & Culture
 Coordinator Professional </span><span class="job--table--cell
 job--table--department job--table--mobile" data-id="department"
 data-mobile="Job Category">People & Culture </span><span
 class="job--table--cell job--table--facility" data-id="facility">Volvo
 Trucks </span><span class="job--table--cell job<3864863 chars
 omitted>rotected veteran. Applying to this job offers you the
 opportunity to join Volvo Group. Every day, across the globe, our
 trucks, buses, engines, construction equipment, financial services,
 and solutions make modern life possible. We are almost 100,000 people
 empowered to shape the future landscape of efficient, safe and
 sustainable transport solutions. Fulfilling our mission creates
 countless career opportunities for talents with sharp minds and
 passion across the group’s leading brands and entities.  Part of Volvo
 Group, Volvo Construction Equipment is a global company driven by our
 purpose to build the world we want to live in. Together we develop and
 deliver solutions for a cleaner, smarter, and more connected world. By
 unleashing everyone’s full potential, we build a more sustainable
 future for all our stakeholders. Come join our team and help us build
 a better tomorrow. </span><span class="job--table--cell job--table--ID
 job--table--hidden" data-id="ID">1295-en_US </span></a></div>
 2026-09-28 12:33:26  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=volvogroup_com_2
 2026-09-28 12:33:26  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Transport Analyst", "Accountant -
 R2R", "2027 Ausbildung Fachkraft (m/w/d) für Lagerlogistik",
 "Conseiller(e) Service Clients Atelier Poids-Lourds H/F - CDI",
 "Thesis work: Calculation of service intervals", "Jobstudent Talent
 Acquisition", "VIE - Adaptation buyer H/F", "Aprendiz Senai", "Senior
 Software Engineer", "Senior System Performance Engineer"\]
 containers=\["<div id="job--table"><div id="job--table--head"><span
 class="job--table--cell">Available Jobs (612)</span><span
 class="job--table--cell">Job Category</span><span
 class="job--table--cell">Organization</span><span
 class="job--table--cell">Location</span><span
 class="job--table--cell">Position Type</span><span
 class="job--table--cell">Posted</span></div><a
 class="job--table--row"
 href="[https://jobs.volvogroup.com/job/Hwaseong-People-&-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555\\](<https://jobs.volvogroup.com/job/Hwaseong-People-&-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555%5C>)"
 title="People & Culture Coordinator Professional"><span
 class="job--table--cell job--table--title job--table--mobile"
 data-id="title" data-mobile="Available Jobs ">People & Culture
 Coordinator Professional </span><span class="job--table--cell
 job--table--department job--table--mobile" data-id="department"
 data-mobile="Job Category">People & Culture </span><span
 class="job--table--cell job--table--facility"
 data-id="facility">Volvo Trucks <3898010 chars omitted>ed veteran.
 Applying to this job offers you the opportunity to join Volvo Group.
 Every day, across the globe, our trucks, buses, engines, construction
 equipment, financial services, and solutions make modern life
 possible. We are almost 100,000 people empowered to shape the future
 landscape of efficient, safe and sustainable transport solutions.
 Fulfilling our mission creates countless career opportunities for
 talents with sharp minds and passion across the group’s leading brands
 and entities.  Part of Volvo Group, Volvo Construction Equipment is a
 global company driven by our purpose to build the world we want to
 live in. Together we develop and deliver solutions for a cleaner,
 smarter, and more connected world. By unleashing everyone’s full
 potential, we build a more sustainable future for all our
 stakeholders. Come join our team and help us build a better tomorrow.
 </span><span class="job--table--cell job--table--ID
 job--table--hidden" data-id="ID">1295-en_US </span></a></div>"\]
 cull_outcome='culled' dom_joined=<div id="job--table"><div
 id="job--table--head"><span class="job--table--cell">Available Jobs
 (612)</span><span class="job--table--cell">Job Category</span><span
 class="job--table--cell">Organization</span><span
 class="job--table--cell">Location</span><span
 class="job--table--cell">Position Type</span><span
 class="job--table--cell">Posted</span></div><a class="job--table--row"
 href="[https://jobs.volvogroup.com/job/Hwaseong-People-&-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555](<https://jobs.volvogroup.com/job/Hwaseong-People-&-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555>)"
 title="People & Culture Coordinator Professional"><span
 class="job--table--cell job--table--title job--table--mobile"
 data-id="title" data-mobile="Available Jobs ">People & Culture
 Coordinator Professional </span><span class="job--table--cell
 job--table--department job--table--mobile" data-id="department"
 data-mobile="Job Category">People & Culture </span><span
 class="job--table--cell job--table--facility" data-id="facility">Volvo
 Trucks </span><span class="job--table--cell job<3864863 chars
 omitted>rotected veteran. Applying to this job offers you the
 opportunity to join Volvo Group. Every day, across the globe, our
 trucks, buses, engines, construction equipment, financial services,
 and solutions make modern life possible. We are almost 100,000 people
 empowered to shape the future landscape of efficient, safe and
 sustainable transport solutions. Fulfilling our mission creates
 countless career opportunities for talents with sharp minds and
 passion across the group’s leading brands and entities.  Part of Volvo
 Group, Volvo Construction Equipment is a global company driven by our
 purpose to build the world we want to live in. Together we develop and
 deliver solutions for a cleaner, smarter, and more connected world. By
 unleashing everyone’s full potential, we build a more sustainable
 future for all our stakeholders. Come join our team and help us build
 a better tomorrow. </span><span class="job--table--cell job--table--ID
 job--table--hidden" data-id="ID">1295-en_US </span></a></div>
 2026-09-28 12:33:57  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=careers_wexnermedical_osu_edu, n=4\]
 2026-09-28 12:33:57  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <table class="jtable ui-widget-content"
 role="none"><tr><th class="jtable-column-header title-column
 ui-state-default"><div class="jtable-column-header-container"><span
 class="jtable-column-header-text">Job Title</span></div></th><th
 class="jtable-column-header location-column ui-state-default"><div
 class="jtable-column-header-container"><span
 class="jtable-column-header-text">Facility Name</span></div></th><th
 class="jtable-column-header city-state-column ui-state-default"><div
 class="jtable-column-header-container"><span
 class="jtable-column-header-text">City, ST</span></div></th></tr><tr
 aria-label="Clinical Research Coordinator- Neurology"
 class="jtable-data-row jtable-row-even"
 data-href="[https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131](<https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131>)"
 data-record-key="c24f9cb5-600c-46a8-b694-2a815db38131" role="link"
 tabindex="0"><td class="title-column"><span>Clinical Research
 Coordinator- Neurology</span></td<5292 chars
 omitted>tps://careers.wexnermedical.osu.edu/search/jobdetails/instructor-practice/79b81626-fdad-4e2d-a1e3-17781c197bdd"
 data-record-key="79b81626-fdad-4e2d-a1e3-17781c197bdd" role="link"
 tabindex="0"><td
 class="title-column"><span>Instructor-Practice</span></td><td
 class="location-column"><span>University Hospital - Doan
 Hall</span></td><td class="city-state-column"><span>Columbus,
 Ohio</span></td></tr><tr aria-label="Staff Nurse-B (RN) Emergency
 Department, University Hospital" class="jtable-data-row"
 data-href="[https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73](<https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73>)"
 data-record-key="e1e331ac-cf28-41dc-addf-1e7c93e87d73" role="link"
 tabindex="0"><td class="title-column"><span>Staff Nurse-B (RN)
 Emergency Department, University Hospital</span></td><td
 class="location-column"><span>University Hospital - Rhodes
 Hall</span></td><td class="city-state-column"><span>Columbus,
 Ohio</span></td></tr></table>
 2026-09-28 12:33:57  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=careers_wexnermedical_osu_edu
 2026-09-28 12:33:57  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Clinical Research Coordinator-
 Neurology", "Clinic Nurse - Thoracic (IRP/Contingent)", "Staff Nurse -
 Hematology and Transplant (IRP/Contingent)", "Clinic Nurse (RN) - GU
 and Urology", "Research Senior Technician- Microbial Infection and
 Immunity", "Associate Nurse Manager - Acute Care - General Medicine",
 "CT Lead Tech $15,000 Signing Bonus 3rd shift I UH Inpatient Patient
 Tower", "Post Doctoral Scholar - Comprehensive Cancer Center",
 "Specialty Practice Pharmacist", "Multi-Modality Imaging Tech $15,000
 Signing Bonus"\] containers=\["<table class="jtable ui-widget-content"
 role="none"><tr><th class="jtable-column-header title-column
 ui-state-default"><div class="jtable-column-header-container"><span
 class="jtable-column-header-text">Job Title</span></div></th><th
 class="jtable-column-header location-column ui-state-default"><div
 class="jtable-column-header-container"><span
 class="jtable-column-header-text">Facility Name</span></div></th><th
 class="jtable-column-header city-state-column ui-state-default"><div
 class="jtable-column-header-container"><span
 class="jtable-column-header-text">City, ST</span></div></th></tr><tr
 aria-label="Clinical Research Coordinator- Neurology"
 class="jtable-data-row jtable-row-even"
 data-href="[https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131\\](<https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131%5C>)"
 data-record-key="c24f9cb5-600c-46a8-b694-2a815db38131" role="link"
 tabindex="0"><td class="title-column"><span>Clinical Rese<5534
 chars omitted>du/search/jobdetails/instructor-practice/79b81626-fdad-4e2d-a1e3-17781c197bdd"
 data-record-key="79b81626-fdad-4e2d-a1e3-17781c197bdd" role="link"
 tabindex="0"><td
 class="title-column"><span>Instructor-Practice</span></td><td
 class="location-column"><span>University Hospital - Doan
 Hall</span></td><td class="city-state-column"><span>Columbus,
 Ohio</span></td></tr><tr aria-label="Staff Nurse-B (RN) Emergency
 Department, University Hospital" class="jtable-data-row"
 data-href="[https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73\\](<https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73%5C>)"
 data-record-key="e1e331ac-cf28-41dc-addf-1e7c93e87d73" role="link"
 tabindex="0"><td class="title-column"><span>Staff Nurse-B (RN)
 Emergency Department, University Hospital</span></td><td
 class="location-column"><span>University Hospital - Rhodes
 Hall</span></td><td class="city-state-column"><span>Columbus,
 Ohio</span></td></tr></table>"\] cull_outcome='culled'
 dom_joined=<table class="jtable ui-widget-content" role="none"><tr><th
 class="jtable-column-header title-column ui-state-default"><div
 class="jtable-column-header-container"><span
 class="jtable-column-header-text">Job Title</span></div></th><th
 class="jtable-column-header location-column ui-state-default"><div
 class="jtable-column-header-container"><span
 class="jtable-column-header-text">Facility Name</span></div></th><th
 class="jtable-column-header city-state-column ui-state-default"><div
 class="jtable-column-header-container"><span
 class="jtable-column-header-text">City, ST</span></div></th></tr><tr
 aria-label="Clinical Research Coordinator- Neurology"
 class="jtable-data-row jtable-row-even"
 data-href="[https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131](<https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131>)"
 data-record-key="c24f9cb5-600c-46a8-b694-2a815db38131" role="link"
 tabindex="0"><td class="title-column"><span>Clinical Research
 Coordinator- Neurology</span></td<5292 chars
 omitted>tps://careers.wexnermedical.osu.edu/search/jobdetails/instructor-practice/79b81626-fdad-4e2d-a1e3-17781c197bdd"
 data-record-key="79b81626-fdad-4e2d-a1e3-17781c197bdd" role="link"
 tabindex="0"><td
 class="title-column"><span>Instructor-Practice</span></td><td
 class="location-column"><span>University Hospital - Doan
 Hall</span></td><td class="city-state-column"><span>Columbus,
 Ohio</span></td></tr><tr aria-label="Staff Nurse-B (RN) Emergency
 Department, University Hospital" class="jtable-data-row"
 data-href="[https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73](<https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73>)"
 data-record-key="e1e331ac-cf28-41dc-addf-1e7c93e87d73" role="link"
 tabindex="0"><td class="title-column"><span>Staff Nurse-B (RN)
 Emergency Department, University Hospital</span></td><td
 class="location-column"><span>University Hospital - Rhodes
 Hall</span></td><td class="city-state-column"><span>Columbus,
 Ohio</span></td></tr></table>
 2026-09-28 12:33:57  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7713436, "visible_chars": 29894,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:33:57  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)",
 "text": "\\n    \\n\\n        \\n\\n    \\n\\n    \\n\\n    \\n        \\n\\n
 \\n    \\n        \\n    \\n    \\n    \\n    \\n    \\n    \\n\\n    \\n    \\n\\n
    \\n \\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n    \\n    \\n\\n\\n\\n\\n\\n\\n\\n    \\n        \\n
            \\n                Search Jobs\\n            \\n            \\n
                CareersSearch Jobs\\n            \\n        \\n
 \\n\\n\\n\\n\\n\\n\\n\\n\\n        \\n\\n\\n    \\n        \\n        \\n
 \\n\\n\\n        \\n        \\n\\n\\n\\n        \\n                        By
 Keyword\\n                            \\n\\n        \\n        \\n
               By Career Area \\n Select Career Area\\nAcademic
 Administration / Academic Program Services\\nAcademic Administration /
 Academic Success and Enrichment\\nAcademic Administration / Career
 Services\\nAcademic Administration / Registration and Records\\nAcademic
 Administration / Undergraduate Academic Advising\\nAdvanced Practice /
 Advanced Practice Education\\nAdvan<195087 chars omitted>fixed; top:
 0px; z-index: 2147483647;"> </iframe></div><script
 src="[https://objectstorage.us-phoenix-1.oraclecloud.com/n/axh6vrlxk8jb/b/nasrecruitment-assets/o/modern-chat-bubble/1dd83c0/vendors\~main.js\\](<https://objectstorage.us-phoenix-1.oraclecloud.com/n/axh6vrlxk8jb/b/nasrecruitment-assets/o/modern-chat-bubble/1dd83c0/vendors~main.js%5C>)"></script><script
 src="[https://objectstorage.us-phoenix-1.oraclecloud.com/n/axh6vrlxk8jb/b/nasrecruitment-assets/o/modern-chat-bubble/1dd83c0/nas_recruitment-main.js\\](<https://objectstorage.us-phoenix-1.oraclecloud.com/n/axh6vrlxk8jb/b/nasrecruitment-assets/o/modern-chat-bubble/1dd83c0/nas_recruitment-main.js%5C>)"
 id="modern-chat-main-url"></script><script
 src="[https://objectstorage.us-phoenix-1.oraclecloud.com/n/axh6vrlxk8jb/b/nasrecruitment-assets/o/modern-chat-bubble/1dd83c0/shared-text-message-icons.js\\](<https://objectstorage.us-phoenix-1.oraclecloud.com/n/axh6vrlxk8jb/b/nasrecruitment-assets/o/modern-chat-bubble/1dd83c0/shared-text-message-icons.js%5C>)"></script><iframe
 style="display: none;" name="\__uspapiLocator"></iframe><style
 id="uc-overflow-style">.overflowHidden {overflow: hidden
 !important;}</style></body>", "scrape_meta": {"bot_blocked": false,
 "cookies_dismissed": false, "issues": \[\], "content_chars": 29894,
 "requested_url":
 "[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)",
 "final_url": "[https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)"}}
 2026-09-28 12:33:57  \[INFO\]  16fe6019 | telescope job done:
 [https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>) ->
 [https://careers.wexnermedical.osu.edu/search/searchjobs](<https://careers.wexnermedical.osu.edu/search/searchjobs>)
 fields:text,html
 2026-09-28 12:33:57  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:33:57  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-abbda7ce86887323"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:33:57  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=sc_edu, n=4\]
 2026-09-28 12:33:57  \[DEBUG\]  3243: Calling agent.do_task
 live_content: Google Tag Manager (noscript)
 <a href="#main-content" id="skiptocontent"><span>Skip to
 Content</span></a><div id="main-wrapper">
 <div class="row hide-for-medium">
 <div class="column small-6 mobile-head"><a class="logo"
 href="[https://www.sc.edu](<https://www.sc.edu>)"><span>University of South Carolina
 Home</span></a></div>
 <div class="column small-6">

</div>
 </div>

<div class="search-wrapper">

Search [sc.edu](<http://sc.edu>)

</div>

<div class="column grid_12 main-nav_top"><a class="main-logo"
 href="[https://sc.edu](<https://sc.edu>)">
 <img alt="University of South Carolina Home"/>
 </a>

Search [sc.edu](<http://sc.edu>)

</div>
 <div class="column grid_12 main-nav_bottom"><ul class="nav-links"><li
 class="main-nav-link"><a
 href="/study/index.php"><span>Study</span></a><div
 class="flyout"><ol><li><a href="/study/index.php"><span>Study at South
 Carolina</span></a></li><li><a
 href="/study/majors_and_degrees/index.php"><span>Majors and Degrees at
 South Carolina</span></a></li><li><a
 href="/study/undergraduate-education/index.php"><span>Undergraduate
 Education<<26997 chars omitted>id="de"><span>©</span></a></span>
 <a href="[https://www.sc.edu/about/notices/](<https://www.sc.edu/about/notices/>)"><span>University of South
 Carolina</span></a>
 <a href="[https://www.sc.edu/about/notices/privacy/](<https://www.sc.edu/about/notices/privacy/>)"><span>Privacy</span></a>
 <a href="[https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/](<https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/>)"><span>Student
 Consumer Information</span></a>
 <a class="regional-link"
 href="[https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php](<https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php>)"><span>Student
 Consumer Information</span></a>
 <a href="[https://spend.admin.sc.edu/](<https://spend.admin.sc.edu/>)"><span>Transparency Initiative</span></a>
 <a href="[https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php](<https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php>)"><span>Civil
 Rights and Title IX</span></a>
 <a href="[https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php](<https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php>)"><span>Digital
 Accessibility</span></a>
 <a href="[https://www.sc.edu/about/contact/](<https://www.sc.edu/about/contact/>)"><span>Contact</span></a>

</div>
 </div>
 </div>

</div>
 2026-09-28 12:33:57  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=sc_edu
 2026-09-28 12:33:57  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Assistant Director, Facilities"\]
 containers=\["Google Tag Manager (noscript) \\n<a href="#main-content"
 id="skiptocontent"><span>Skip to Content</span></a><div
 id="main-wrapper"> \\n<div class="row hide-for-medium">\\n<div
 class="column small-6 mobile-head"><a class="logo"
 href="[https://www.sc.edu](<https://www.sc.edu>)"><span>University of South Carolina
 Home</span></a></div>\\n<div class="column
 small-6">\\n\\n</div>\\n</div>\\n\\n<div
 class="search-wrapper">\\n\\nSearch [sc.edu](<http://sc.edu>)\\n\\n\\n</div>\\n\\n\\n<div
 class="column grid_12 main-nav_top"><a class="main-logo"
 href="[https://sc.edu](<https://sc.edu>)">\\n<img alt="University of South Carolina
 Home"/>\\n</a>\\n\\nSearch [sc.edu](<http://sc.edu>)\\n\\n\\n\\n</div>\\n<div class="column
 grid_12 main-nav_bottom"><ul class="nav-links"><li
 class="main-nav-link"><a
 href="/study/index.php"><span>Study</span></a><div
 class="flyout"><ol><li><a href="/study/index.php"><span>Study at
 South Carolina</span></a></li><li><a
 href="/study/majors_and_degrees/index.php"><span>Majors and Degrees
 at South Carolina</span></a></li><li><a href="/st<28175 chars
 omitted><a href="[https://www.sc.edu/about/notices/\\](<https://www.sc.edu/about/notices/%5C>)"><span>University
 of South Carolina</span></a>\\n<a
 href="[https://www.sc.edu/about/notices/privacy/\\](<https://www.sc.edu/about/notices/privacy/%5C>)"><span>Privacy</span></a>\\n<a
 href="[https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/\\](<https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/%5C>)"><span>Student
 Consumer Information</span></a>\\n<a class="regional-link"
 href="[https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php\\](<https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php%5C>)"><span>Student
 Consumer Information</span></a>\\n<a
 href="[https://spend.admin.sc.edu/\\](<https://spend.admin.sc.edu/%5C>)"><span>Transparency
 Initiative</span></a>\\n<a
 href="[https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php\\](<https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php%5C>)"><span>Civil
 Rights and Title IX</span></a>\\n<a
 href="[https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php\\](<https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php%5C>)"><span>Digital
 Accessibility</span></a>\\n<a
 href="[https://www.sc.edu/about/contact/\\"><span>Contact</span></a>\\n\\n</div>\\n</div>\\n</div>\\n\\n\\n</div>"](<https://www.sc.edu/about/contact/%5C%22%3E%3Cspan%3EContact%3C/span%3E%3C/a%3E%5Cn%5Cn%3C/div%3E%5Cn%3C/div%3E%5Cn%3C/div%3E%5Cn%5Cn%5Cn%3C/div%3E%22>)\]
 cull_outcome='full_dom' dom_joined=Google Tag Manager (noscript)
 <a href="#main-content" id="skiptocontent"><span>Skip to
 Content</span></a><div id="main-wrapper">
 <div class="row hide-for-medium">
 <div class="column small-6 mobile-head"><a class="logo"
 href="[https://www.sc.edu](<https://www.sc.edu>)"><span>University of South Carolina
 Home</span></a></div>
 <div class="column small-6">

</div>
 </div>

<div class="search-wrapper">

Search [sc.edu](<http://sc.edu>)

</div>

<div class="column grid_12 main-nav_top"><a class="main-logo"
 href="[https://sc.edu](<https://sc.edu>)">
 <img alt="University of South Carolina Home"/>
 </a>

Search [sc.edu](<http://sc.edu>)

</div>
 <div class="column grid_12 main-nav_bottom"><ul class="nav-links"><li
 class="main-nav-link"><a
 href="/study/index.php"><span>Study</span></a><div
 class="flyout"><ol><li><a href="/study/index.php"><span>Study at South
 Carolina</span></a></li><li><a
 href="/study/majors_and_degrees/index.php"><span>Majors and Degrees at
 South Carolina</span></a></li><li><a
 href="/study/undergraduate-education/index.php"><span>Undergraduate
 Education<<26997 chars omitted>id="de"><span>©</span></a></span>
 <a href="[https://www.sc.edu/about/notices/](<https://www.sc.edu/about/notices/>)"><span>University of South
 Carolina</span></a>
 <a href="[https://www.sc.edu/about/notices/privacy/](<https://www.sc.edu/about/notices/privacy/>)"><span>Privacy</span></a>
 <a href="[https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/](<https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/>)"><span>Student
 Consumer Information</span></a>
 <a class="regional-link"
 href="[https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php](<https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php>)"><span>Student
 Consumer Information</span></a>
 <a href="[https://spend.admin.sc.edu/](<https://spend.admin.sc.edu/>)"><span>Transparency Initiative</span></a>
 <a href="[https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php](<https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php>)"><span>Civil
 Rights and Title IX</span></a>
 <a href="[https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php](<https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php>)"><span>Digital
 Accessibility</span></a>
 <a href="[https://www.sc.edu/about/contact/](<https://www.sc.edu/about/contact/>)"><span>Contact</span></a>

</div>
 </div>
 </div>

</div>
 2026-09-28 12:33:57  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7711080, "visible_chars": 15504,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:33:57  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://sc.edu/about/employment/](<https://sc.edu/about/employment/>)", "text": "\\nSkip to
 Content         \\n         \\n         \\n\\n         \\n            \\n
            \\n               \\n                  \\n
 [SC.edu](<http://SC.edu>)\\n                     About\\n                     employment\\n
                 \\n               \\n               \\n
 \\n                     Employment\\n                     \\t\\n
           When you work at the University of South Carolina, you're
 part of a statewide team\\n                        of more than 15,000
 people. Whether you're with campus services, administrative support\\n
                       or teach in the classroom, you're joining an
 award-winning workplace.\\n                     \\n
 \\n               \\n               \\t\\t\\t\\t\\n               \\n
         \\n                  \\n                     \\n
    \\n                        \\n                        University
 employees are part of o<93731 chars omitted>er-style:none;" alt=""
 src="[https://insight.adsrvr.org/track/pxl/?adv=75p86ce&ct=0:m8uuaom&fmt=3/\\](<https://insight.adsrvr.org/track/pxl/?adv=75p86ce&ct=0:m8uuaom&fmt=3/%5C>)"></div>\\n<script
 type="text/javascript" id=""
 charset="">!function(b,e,f,g,a,c,d){b.fbq||(a=b.fbq=function(){a.callMethod?a.callMethod.apply(a,arguments):a.queue.push(arguments)},b.\_fbq||(b.\_fbq=a),a.push=a,a.loaded=!0,a.version="2.0",a.queue=\[\],c=e.createElement(f),c.async=!0,c.src=g,d=e.getElementsByTagName(f)\[0\],d.parentNode.insertBefore(c,d))}(window,document,"script","[https://connect.facebook.net/en_US/fbevents.js\\");fbq(\\"init\\",\\"1438055863158990\\");fbq(\\"track\\",\\"PageView\\](<https://connect.facebook.net/en_US/fbevents.js%5C%22);fbq(%5C%22init%5C%22,%5C%221438055863158990%5C%22);fbq(%5C%22track%5C%22,%5C%22PageView%5C>)");</script>\\n<noscript><img
 height="1" width="1" style="display:none"
 src="[https://www.facebook.com/tr?id=1438055863158990&ev=PageView&noscript=1\\"></noscript>\\n</body>"](<https://www.facebook.com/tr?id=1438055863158990&ev=PageView&noscript=1%5C%22%3E%3C/noscript%3E%5Cn%3C/body%3E%22>),
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 15504, "requested_url":
 "[https://sc.edu/about/employment](<https://sc.edu/about/employment>)", "final_url":
 "[https://sc.edu/about/employment/](<https://sc.edu/about/employment/>)"}}
 2026-09-28 12:33:57  \[INFO\]  6d483653 | telescope job done:
 [https://sc.edu/about/employment](<https://sc.edu/about/employment>) -> [https://sc.edu/about/employment/](<https://sc.edu/about/employment/>)
 fields:text,html
 2026-09-28 12:33:57  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:33:57  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-3c047014ff1272c2"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:34:30  \[ERROR\]  abrams | dispatch company parse_job_list
   TimeoutError: dispatch timeout after 3600s
 batch=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae
   Truncating the batch
 Traceback (most recent call last):
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 520,
 in wait_for
     return await fut
            ^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 1536, in \_run_dispatch_loop
     summary = await \_run_task(task, ctx, debug)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 910, in \_run_task
     summary = await \_run_unified(task, ctx, debug)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 831, in \_run_unified
     result = await consult.run_consult_task(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/consult.py", line 72, in async_wrapper
     return await fn(\*args, \*\*kwargs)
            ^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/consult.py", line 2674, in run_consult_task
     r = await \_debug_await(
         ^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/consult.py", line 113, in \_debug_await
     result = await coro
              ^^^^^^^^^^
   File "/app/src/core/roster.py", line 1315, in parse_job_list_batch
     results = await asyncio.gather(
               ^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/roster.py", line 1306, in \_one
     result = await run_parse_job_list_dispatch(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/roster.py", line 1244, in run_parse_job_list_dispatch
     result = await \_scrape_and_parse()
              ^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/roster.py", line 1221, in \_scrape_and_parse
     parsed = await \_fetch_parse_job_list(dom_joined, short_name,
 debug=debug, ctx=ctx)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/roster.py", line 3244, in \_fetch_parse_job_list
     response = await do_task(
                ^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 103, in wrapper
     return await fn(\*args, \*\*kwargs)
            ^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 2198, in do_task
     result = await send_to_deepseek(
              ^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/external/deepseek.py", line 248, in send_to_deepseek
     response = await await_provider_call_with_budget(
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/utils/llm_external.py", line 90, in
 await_provider_call_with_budget
     done, \_pending = await asyncio.wait({task}, timeout=timeout_seconds)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 464, in wait
     return await \_wait(fs, timeout, return_when, loop)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 550, in \_wait
     await waiter
 asyncio.exceptions.CancelledError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
   File "/app/src/core/dispatcher.py", line 1373, in \_dispatch_one_body
     await \_tracked()
   File "/app/src/core/dispatcher.py", line 1361, in \_tracked
     await asyncio.wait_for(
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 519,
 in wait_for
     async with timeouts.timeout(timeout):
                ^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/root/.nix-profile/lib/python3.12/asyncio/timeouts.py", line
 115, in **aexit**
     raise TimeoutError from exc_val
 TimeoutError
 2026-09-28 12:34:30  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:34:30  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-fb20a970531cac71"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:34:30  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=utmb_edu_2, n=4\]
 2026-09-28 12:34:30  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div class="sf_cols">
 <div class="sf_colsOut sf_2cols_1_50">
 <div class="sf_colsIn sf_2cols_1in_50" id="Body_C014_Col00">
 <div class="utmbsf-content-block" utmb-4x-template="ContentBlock.Default">
 <p>Neurodiagnostic Technologist II – Epilepsy Monitoring
 (Nights)Galveston Campus<a class="btn btn-text"
 data-sf-ec-immutable="" href="[http://phxc3c.rfer.us/AA083hcqBNx](<http://phxc3c.rfer.us/AA083hcqBNx>)"
 target="\_blank" title="Click to Apply Now"><span
 class="blue-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p><p>Neurodiagnostic Technologist II – EMU
 (3–12 hour shifts)Galveston Campus<a class="btn btn-text"
 data-sf-ec-immutable=""
 href="[https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161](<https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161>)"
 target="\_blank" title="Click to Apply Now"><span
 class="blue-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p>
 </div>
 </div>
 </div>
 <div class="sf_colsOut sf_2cols_2_50">
 <div class="sf_colsIn sf_2cols_2in_50" id="Body_C014_Col01">
 <div class="utmbsf-content-block" utmb-4x-template="ContentBlock.Default">
 <p>Laboratory Services Manager – Blood BankGalveston Campus<a
 class="btn btn-text" data-sf-ec-immutable=" "
 href="[http://phxc3c.rfer.us/AA083XSKEb0](<http://phxc3c.rfer.us/AA083XSKEb0>)" target="\_blank " title="Click
 to Apply Now
     "><span class="teal-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p>
 </div>
 </div>
 </div>
 </div>
 2026-09-28 12:34:30  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=utmb_edu_2
 2026-09-28 12:34:30  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Neurodiagnostic Technologist II –
 Epilepsy Monitoring (Nights)", "Neurodiagnostic Technologist II – EMU
 (3–12 hour shifts)", "Laboratory Services Manager – Blood Bank"\]
 containers=\["<div class="sf_cols">\\n<div class="sf_colsOut
 sf_2cols_1_50">\\n<div class="sf_colsIn sf_2cols_1in_50"
 id="Body_C014_Col00">\\n<div class="utmbsf-content-block"
 utmb-4x-template="ContentBlock.Default">\\n<p>Neurodiagnostic
 Technologist II – Epilepsy Monitoring (Nights)Galveston Campus<a
 class="btn btn-text" data-sf-ec-immutable=""
 href="[http://phxc3c.rfer.us/AA083hcqBNx\\](<http://phxc3c.rfer.us/AA083hcqBNx%5C>)" target="\_blank"
 title="Click to Apply Now"><span class="blue-dark"><span
 class="blue-navy">  Apply
 Now</span></span></a></p><p>Neurodiagnostic Technologist II – EMU
 (3–12 hour shifts)Galveston Campus<a class="btn btn-text"
 data-sf-ec-immutable=""
 href="[https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161\\](<https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161%5C>)"
 target="\_blank" title="Click to Apply Now"><span
 class="blue-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p>\\n</div>\\n</div>\\n</div>\\n<div
 class="sf_colsOut sf_2cols_2_50">\\n<div class="sf_colsIn
 sf_2cols_2in_50" id="Body_C014_Col01">\\n<div
 class="utmbsf-content-block"
 utmb-4x-template="ContentBlock.Default">\\n<p>Laboratory Services
 Manager – Blood BankGalveston Campus<a class="btn btn-text"
 data-sf-ec-immutable=" " href="[http://phxc3c.rfer.us/AA083XSKEb0\\](<http://phxc3c.rfer.us/AA083XSKEb0%5C>)"
 target="\_blank " title="Click to Apply Now\\n    "><span
 class="teal-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p>\\n</div>\\n</div>\\n</div>\\n</div>"\]
 cull_outcome='culled' dom_joined=<div class="sf_cols">
 <div class="sf_colsOut sf_2cols_1_50">
 <div class="sf_colsIn sf_2cols_1in_50" id="Body_C014_Col00">
 <div class="utmbsf-content-block" utmb-4x-template="ContentBlock.Default">
 <p>Neurodiagnostic Technologist II – Epilepsy Monitoring
 (Nights)Galveston Campus<a class="btn btn-text"
 data-sf-ec-immutable="" href="[http://phxc3c.rfer.us/AA083hcqBNx](<http://phxc3c.rfer.us/AA083hcqBNx>)"
 target="\_blank" title="Click to Apply Now"><span
 class="blue-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p><p>Neurodiagnostic Technologist II – EMU
 (3–12 hour shifts)Galveston Campus<a class="btn btn-text"
 data-sf-ec-immutable=""
 href="[https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161](<https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161>)"
 target="\_blank" title="Click to Apply Now"><span
 class="blue-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p>
 </div>
 </div>
 </div>
 <div class="sf_colsOut sf_2cols_2_50">
 <div class="sf_colsIn sf_2cols_2in_50" id="Body_C014_Col01">
 <div class="utmbsf-content-block" utmb-4x-template="ContentBlock.Default">
 <p>Laboratory Services Manager – Blood BankGalveston Campus<a
 class="btn btn-text" data-sf-ec-immutable=" "
 href="[http://phxc3c.rfer.us/AA083XSKEb0](<http://phxc3c.rfer.us/AA083XSKEb0>)" target="\_blank " title="Click
 to Apply Now
     "><span class="teal-dark"><span class="blue-navy">  Apply
 Now</span></span></a></p>
 </div>
 </div>
 </div>
 </div>
 2026-09-28 12:34:30  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7767509, "visible_chars": 30662,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:34:30  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)", "text":
 "\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\t\\n\\n\\n\\n
 \\n\\n\\n\\n\\n    \\n    \\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n     \\n
   \\n\\n\\n    UTMB Health CareersExplore your passions. Lead the way in
 health care innovation. Make groundbreaking discoveries. Transform
 your career. External Applicants\\n\\n\\n \\n\\n Current UTMB
 Employees\\n\\n\\n \\n\\n Contract & Per Diem Staff\\n \\n\\n\\n     \\n\\n    \\n
        \\n    \\n        \\n    \\n        \\n    \\n        \\n    \\n    \\n
   \\n    \\n    \\n     \\n    \\n     \\n    \\n     \\n    \\n\\n\\n    \\n\\n
 \\n\\n    \\n\\n            \\n        \\n    \\n\\n            \\n        \\n
  \\n\\n    \\n\\n    \\nSet the Standards of Health CareUTMB Health is on a
 mission to improve health for the people of Texas and around the
 world. Our employees share a deep commitment to serving our students
 and patients in innovative ways, and we are looking for inspired
 individuals to join our team. Your accomplishments here will <142616
 chars omitted>);;(function() {\\n                        function
 loadHandler() {\\n                            var hf =
 $get('ctl06_TSSM');\\n                            if (!hf.\_RSSM_init) {
 hf.\_RSSM_init = true; hf.value = ''; }\\n
 hf.value += ';Telerik.Sitefinity.Resources, Version=15.4.8636.0,
 Culture=neutral,
 PublicKeyToken=b28c218413bdf563:en:e3c1f54b-3ea5-4781-8854-7c87826645f0:7a90d6a';\\n
                            Sys.Application.remove_load(loadHandler);\\n
                        };\\n
 Sys.Application.add_load(loadHandler);\\n
 })();//\]\]>\\n</script>\\n</form> \\n\\n\\n\\n\\n\\n\\n\\n<script id=""
 text="" charset="" type="text/javascript"
 src="[https://tag.simpli.fi/sifitag/7d9f25e0-d1df-0139-90f8-06b4c2516bae\\"></script></body>"](<https://tag.simpli.fi/sifitag/7d9f25e0-d1df-0139-90f8-06b4c2516bae%5C%22%3E%3C/script%3E%3C/body%3E%22>),
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": true,
 "issues": \[\], "content_chars": 30662, "requested_url":
 "[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)", "final_url":
 "[https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)"}}
 2026-09-28 12:34:30  \[INFO\]  a8ba1924 | telescope job done:
 [https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>) -> [https://www.utmb.edu/hr/careers](<https://www.utmb.edu/hr/careers>)
 fields:text,html
 2026-09-28 12:34:30  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:34:30  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-d361842569615e19"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:34:30  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=northwell_edu_2, n=4\]
 2026-09-28 12:34:30  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div class="widget clearfix widget-joblist"
 id="widget_job_list_v2-13" role="list"><div class="widget_joblist_row"
 role="listitem"><a
 href="/job-3/23501366/medical-assistant-plainview-ny/"
 lang="en">Medical Assistant</a><div class="widget_joblist_category"
 lang="en">Clinical Support</div><div class="widget_joblist_loc"
 lang="en">Plainview, NY</div></div><div class="widget_joblist_row alt"
 role="listitem"><a
 href="/job-3/23787555/patient-account-representative-lake-success-ny/"
 lang="en">Patient Account Representative</a><div
 class="widget_joblist_category" lang="en">Revenue Cycle</div><div
 class="widget_joblist_loc" lang="en">Lake Success, NY</div></div><div
 class="widget_joblist_row" role="listitem"><a
 href="/job-3/23659975/environmental-svcs-worker-new-hyde-park-ny/"
 lang="en">Environmental Svcs Worker</a><div
 class="widget_joblist_category" lang="en">Facilities and Support
 Services</div><div class="widget_joblist_loc" lang="en">New Hyde Park,
 NY</div></div><div class="widget_joblist_row alt" role="listitem"><a
 href="/job-3/23918518/full-time-surgical-scheduler-orthopedics-lynbrook-ny/"
 lang="en">Full Time - Surgical Scheduler - Orthopedics</a><div
 class="widget_joblist_category" lang="en">Clinical Support</div><div
 class="widget_joblist_loc" lang="en">Lynbrook, NY</div></div><div
 class="widget_joblist_row" role="listitem"><a
 href="/job-3/23742033/medical-assistant-rockville-centre-ny/"
 lang="en">Medical Assistant</a><div class="widget_joblist_category"
 lang="en">Clinical Support</div><div class="widget_joblist_loc"
 lang="en">Rockville Centre, NY</div></div><div
 class="widget_joblist_row alt" role="listitem"><a
 href="/job-3/23590496/transporter-forest-hills-ny/"
 lang="en">Transporter</a><div class="widget_joblist_category"
 lang="en">Facilities and Support Services</div><div
 class="widget_joblist_loc" lang="en">Forest Hills,
 NY</div></div></div>
 2026-09-28 12:34:30  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=northwell_edu_2
 2026-09-28 12:34:30  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Medical Assistant", "Patient Account
 Representative", "Environmental Svcs Worker", "Full Time - Surgical
 Scheduler - Orthopedics", "Transporter"\] containers=\["<div
 class="widget clearfix widget-joblist" id="widget_job_list_v2-13"
 role="list"><div class="widget_joblist_row" role="listitem"><a
 href="/job-3/23501366/medical-assistant-plainview-ny/"
 lang="en">Medical Assistant</a><div
 class="widget_joblist_category" lang="en">Clinical
 Support</div><div class="widget_joblist_loc" lang="en">Plainview,
 NY</div></div><div class="widget_joblist_row alt"
 role="listitem"><a
 href="/job-3/23787555/patient-account-representative-lake-success-ny/"
 lang="en">Patient Account Representative</a><div
 class="widget_joblist_category" lang="en">Revenue Cycle</div><div
 class="widget_joblist_loc" lang="en">Lake Success,
 NY</div></div><div class="widget_joblist_row" role="listitem"><a
 href="/job-3/23659975/environmental-svcs-worker-new-hyde-park-ny/"
 lang="en">Environmental Svcs Worker</a><div
 class="widget_joblist_category" lang="en">Facilities and Support
 Services</div><div class="widget_joblist_loc" lang="en">New Hyde
 Park, NY</div></div><div class="widget_joblist_row alt"
 role="listitem"><a
 href="/job-3/23918518/full-time-surgical-scheduler-orthopedics-lynbrook-ny/"
 lang="en">Full Time - Surgical Scheduler - Orthopedics</a><div
 class="widget_joblist_category" lang="en">Clinical
 Support</div><div class="widget_joblist_loc" lang="en">Lynbrook,
 NY</div></div><div class="widget_joblist_row" role="listitem"><a
 href="/job-3/23742033/medical-assistant-rockville-centre-ny/"
 lang="en">Medical Assistant</a><div
 class="widget_joblist_category" lang="en">Clinical
 Support</div><div class="widget_joblist_loc" lang="en">Rockville
 Centre, NY</div></div><div class="widget_joblist_row alt"
 role="listitem"><a
 href="/job-3/23590496/transporter-forest-hills-ny/"
 lang="en">Transporter</a><div class="widget_joblist_category"
 lang="en">Facilities and Support Services</div><div
 class="widget_joblist_loc" lang="en">Forest Hills,
 NY</div></div></div>"\] cull_outcome='culled' dom_joined=<div
 class="widget clearfix widget-joblist" id="widget_job_list_v2-13"
 role="list"><div class="widget_joblist_row" role="listitem"><a
 href="/job-3/23501366/medical-assistant-plainview-ny/"
 lang="en">Medical Assistant</a><div class="widget_joblist_category"
 lang="en">Clinical Support</div><div class="widget_joblist_loc"
 lang="en">Plainview, NY</div></div><div class="widget_joblist_row alt"
 role="listitem"><a
 href="/job-3/23787555/patient-account-representative-lake-success-ny/"
 lang="en">Patient Account Representative</a><div
 class="widget_joblist_category" lang="en">Revenue Cycle</div><div
 class="widget_joblist_loc" lang="en">Lake Success, NY</div></div><div
 class="widget_joblist_row" role="listitem"><a
 href="/job-3/23659975/environmental-svcs-worker-new-hyde-park-ny/"
 lang="en">Environmental Svcs Worker</a><div
 class="widget_joblist_category" lang="en">Facilities and Support
 Services</div><div class="widget_joblist_loc" lang="en">New Hyde Park,
 NY</div></div><div class="widget_joblist_row alt" role="listitem"><a
 href="/job-3/23918518/full-time-surgical-scheduler-orthopedics-lynbrook-ny/"
 lang="en">Full Time - Surgical Scheduler - Orthopedics</a><div
 class="widget_joblist_category" lang="en">Clinical Support</div><div
 class="widget_joblist_loc" lang="en">Lynbrook, NY</div></div><div
 class="widget_joblist_row" role="listitem"><a
 href="/job-3/23742033/medical-assistant-rockville-centre-ny/"
 lang="en">Medical Assistant</a><div class="widget_joblist_category"
 lang="en">Clinical Support</div><div class="widget_joblist_loc"
 lang="en">Rockville Centre, NY</div></div><div
 class="widget_joblist_row alt" role="listitem"><a
 href="/job-3/23590496/transporter-forest-hills-ny/"
 lang="en">Transporter</a><div class="widget_joblist_category"
 lang="en">Facilities and Support Services</div><div
 class="widget_joblist_loc" lang="en">Forest Hills,
 NY</div></div></div>
 2026-09-28 12:34:30  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7757669, "visible_chars": 14388,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:34:30  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)",
 "text": "\\n\\n\\n\\n\\t\\t\\t\\t\\nSkip to main contentHide Menu\\nSearch
 jobs\\nAbout us\\n\\n\\n\\n\\tOur culture\\n\\tBenefits\\n\\tCareer
 Experience\\n\\tAlumni Network\\n\\tLocations\\n\\tFAQ\\n\\n\\nCareer
 specialties\\n\\n\\n\\n\\tAdvanced Clinical Provider\\n\\tCancer\\n\\tClinical
 Care\\n\\tCulinary\\n\\tExecutives\\n\\tHome Health Aides\\n\\tInformation
 Technology\\n\\tLaboratory\\n\\tNursing\\n\\t\\n\\t\\tExternships, Fellowships
 and Nurse Residency Programs\\n\\t\\tPerioperative – Pre-Surgical, OR,
 PACU, Endoscopy\\n\\t\\n\\n\\tPhysicians\\n\\tProfessional / Technical /
 Support\\n\\tResearch\\n\\n\\nTemp jobs\\nStudents\\nVeterans\\nInclusion and
 Belonging\\nCareers blog\\n\\n\\n\\n\\t\\n\\n\\n\\n\\n\\n\\tMenu Hide\\n\\t\\tYou are
 here: Home\\nTogether, we will deliver healthcare to the communities
 where we live, love and belong\\n\\nSearch JobsJob ID, Keywords or MOS
 CodeSearch near a location\\n\\n\\n\\nAt Northwell Health, we’re 100,000+
 strong—caring for millions o<370179 chars omitted><script
 type="text/javascript"
 src="[https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places&callback=CWS_init_autocomplete&key=AIzaSyDkfM7EXTj6uNRi-BcpZcFHzP-gj5ToIhQ\\](<https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places&callback=CWS_init_autocomplete&key=AIzaSyDkfM7EXTj6uNRi-BcpZcFHzP-gj5ToIhQ%5C>)"></script><div
 role="status" aria-live="assertive" aria-relevant="additions"
 class="ui-helper-hidden-accessible"></div><span class="offscreen"
 aria-hidden="true" id="level2">level 2</span><ul id="ui-id-2"
 tabindex="0" class="ui-menu ui-widget ui-widget-content
 ui-autocomplete here-autocomplete ui-front" style="display: none;"
 unselectable="on"></ul><div role="status" aria-live="assertive"
 aria-relevant="additions"
 class="ui-helper-hidden-accessible"></div></body>", "scrape_meta":
 {"bot_blocked": false, "cookies_dismissed": false, "issues": \[\],
 "content_chars": 14388, "requested_url":
 "[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)",
 "final_url": "[https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)"}}
 2026-09-28 12:34:30  \[INFO\]  139b0902 | telescope job done:
 [https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)
 -> [https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav](<https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav>)
 fields:text,html
 2026-09-28 12:34:30  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:34:30  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-6d7a1fc7be9bec09"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:34:30  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=mrisoftware_com, n=4\]
 2026-09-28 12:34:30  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <ul aria-label="Page 1 of 5" role="list"><li
 class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a aria-current="false"
 class="css-19uc56f" data-automation-id="jobTitle"
 data-uxi-element-id="jobItem" data-uxi-item-rank="0"
 data-uxi-query-id="" data-uxi-widget-type="heading"
 href="/en-US/external_careersite/job/Cape-Town-South-Africa-Office/Support-Analyst_R-109362">Support
 Analyst</a></h3></div></div></div><div class="css-248241"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locationsCape Town, South Africa
 Office</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted
 Today</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-109362</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-current="false"
 class="css-19uc56f<14842 chars omitted>ostedOn">posted onPosted 4 Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-109171</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="19" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/external_careersite/job/Cleveland-Ohio-Office/Associate-Product-Marketing-Specialist_R-108835">Associate
 Product Marketing Specialist</a></h3></div></div></div><div
 class="css-248241"><div class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locations2
 Locations</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 5 Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-108835</li></ul></li></ul>
 2026-09-28 12:34:30  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=mrisoftware_com
 2026-09-28 12:34:30  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["PMO Manager", "Senior Property
 Accountant IV", "Systems Administrator III", "Billing Analyst",
 "Program Manager", "Application Support Analyst (SQL)", "Account
 Manager (Residential)", "SaaS Implementation Consultant (NA Hours)",
 "Project Scoping Specialist (UK Hours)", "Director - Product
 Management"\] containers=\["<ul aria-label="Page 1 of 5"
 role="list"><li class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a
 aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="0" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/external_careersite/job/Cape-Town-South-Africa-Office/Support-Analyst_R-109362">Support
 Analyst</a></h3></div></div></div><div class="css-248241"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locationsCape Town, South Africa
 Office</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted
 Today</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-109362</li></ul></li><li
 class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class=<15770 chars omitted>ul
 class="css-14a0imc" data-automation-id="subtitle"><li
 class="css-h2nt8k">R-109171</li></ul></li><li
 class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a
 aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="19" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/external_careersite/job/Cleveland-Ohio-Office/Associate-Product-Marketing-Specialist_R-108835">Associate
 Product Marketing Specialist</a></h3></div></div></div><div
 class="css-248241"><div class="css-1y87fhn"><div
 class="css-k008qs" data-automation-id="locations">locations2
 Locations</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 5 Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-108835</li></ul></li></ul>"\]
 cull_outcome='culled' dom_joined=<ul aria-label="Page 1 of 5"
 role="list"><li class="css-1q2dra3"><div class="css-qiqmbt"><div
 class="css-b3pn3b"><div class="css-b3pn3b"><h3><a aria-current="false"
 class="css-19uc56f" data-automation-id="jobTitle"
 data-uxi-element-id="jobItem" data-uxi-item-rank="0"
 data-uxi-query-id="" data-uxi-widget-type="heading"
 href="/en-US/external_careersite/job/Cape-Town-South-Africa-Office/Support-Analyst_R-109362">Support
 Analyst</a></h3></div></div></div><div class="css-248241"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locationsCape Town, South Africa
 Office</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted
 Today</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-109362</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-current="false"
 class="css-19uc56f<14842 chars omitted>ostedOn">posted onPosted 4 Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-109171</li></ul></li><li class="css-1q2dra3"><div
 class="css-qiqmbt"><div class="css-b3pn3b"><div
 class="css-b3pn3b"><h3><a aria-current="false" class="css-19uc56f"
 data-automation-id="jobTitle" data-uxi-element-id="jobItem"
 data-uxi-item-rank="19" data-uxi-query-id=""
 data-uxi-widget-type="heading"
 href="/en-US/external_careersite/job/Cleveland-Ohio-Office/Associate-Product-Marketing-Specialist_R-108835">Associate
 Product Marketing Specialist</a></h3></div></div></div><div
 class="css-248241"><div class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="locations">locations2
 Locations</div></div></div><div class="css-zoser8"><div
 class="css-1y87fhn"><div class="css-k008qs"
 data-automation-id="postedOn">posted onPosted 5 Days
 Ago</div></div></div><ul class="css-14a0imc"
 data-automation-id="subtitle"><li
 class="css-h2nt8k">R-108835</li></ul></li></ul>
 2026-09-28 12:34:30  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7746789, "visible_chars": 2156,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:34:30  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)",
 "text": "\\nSkip to main contentSearchFiltersLocationTime
 TypeDepartmentMoreSearch for Jobs page is loaded93 JOBS FOUNDJump to
 selected job detailsSupport AnalystlocationsCape Town, South Africa
 Officeposted onPosted TodayR-109362PMO ManagerlocationsCape Town,
 South Africa Officeposted onPosted 13 Days AgoR-108828Senior Property
 Accountant IVlocationsGurgaon, India Officeposted onPosted 25 Days
 AgoR-107768Systems Administrator IIIlocationsBangalore, India
 Officeposted onPosted 30+ Days AgoR-109356Account Executive -
 OccupierlocationsLondon, UK Officeposted onPosted TodayR-109575Billing
 AnalystlocationsCape Town, South Africa Officeposted onPosted 3 Days
 AgoR-109093Program Managerlocations2 Locationsposted onPosted 3 Days
 AgoR-109373Application Support Analyst (SQL)locationsCape Town, South
 Africa Officeposted onPosted 3 Days AgoR-107678Account Manager
 (Residential)locationsLondon, UK Officeposted onPosted 3<88484 chars
 omitted>81298 L37.8271845,13.4879395 L37.663301,13.4879395
 L37.663301,12.8280664 L37.927767,12.8280664 L37.927767,12.8280664 Z
 M37.8267961,13.1207091 L37.9079612,13.1207091 C37.9557282,13.1207091
 37.9906796,13.1119564 38.0128155,13.0974955 C38.0349515,13.0830346
 38.0462136,13.0602017 38.0462136,13.0267133 C38.0462136,12.9947471
 38.0349515,12.9696308 38.0120388,12.9532672 C37.9864078,12.9369036
 37.9499029,12.9296731 37.8998058,12.9296731 L37.8267961,12.9296731
 L37.8267961,13.1207091 L37.8267961,13.1207091 Z"
 fill="#2367AE"></path></g></g></g></g></g></g></g></g></svg></div><span
 class="css-1vfpfxb"></span></div><div class="css-1h61b0m">© 2026
 Workday, Inc. All rights
 reserved.</div></div></div></div></div></div>\\n\\n</body>",
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 2156, "requested_url":
 "[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)",
 "final_url": "[https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)"}}
 2026-09-28 12:34:30  \[INFO\]  79d15fff | telescope job done:
 [https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>) ->
 [https://mrisoftware.wd501.myworkdayjobs.com/external_careersite](<https://mrisoftware.wd501.myworkdayjobs.com/external_careersite>)
 fields:text,html
 2026-09-28 12:34:30  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:34:30  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-ea3eca2e0ffdfa5f"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]
 2026-09-28 12:34:30  \[DEBUG\]  1335: Calling \_store_prompt_blocks:
 \[entity_type=company, task_key=parse_job_list,
 batch_id=parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae,
 entity_id=psychiatry_ucsf_edu, n=4\]
 2026-09-28 12:34:30  \[DEBUG\]  3243: Calling agent.do_task
 live_content: <div class="accordion" data-once="accordion-keep-open"
 data-usb-keep-open="false" id="accordion-407489375">
 <div class="accordion-item">
 <h2 class="accordion-header" id="heading--accordion-item-1825782552">

```
   Attending Child and Adolescent Psychiatrists (UCSF Health)
```

</h2>
 <div aria-labelledby="heading--accordion-item-1825782552"
 class="accordion-collapse collapse js-accordion-keep-open"
 data-bs-parent="#accordion-407489375"
 data-once="accordion-item-keep-open" id="accordion-item-1825782552">
 <div class="accordion-body">
 <p>UCSF Health is currently recruiting for a variety of vacant
 child/adolescent psychiatry positions in both inpatient and outpatient
 services.</p>
 <p>Applications will be held and reviewed based on availability of
 positions and funding. These positions will be filled in a rank and
 series commensurate with experience.</p>
 <p><a class="btn btn-primary"
 href="[https://aprecruit.ucsf.edu/JPF05824](<https://aprecruit.ucsf.edu/JPF05824>)" target="\_blank">Find out
 more and apply</a></p>
 </div>
 </div>
 </di<8058 chars omitted>    Mental Health Clinician-Educator (San
 Francisco VA Health Care System)

</h2>
 <div aria-labelledby="heading--accordion-item-712047284"
 class="accordion-collapse collapse js-accordion-keep-open"
 data-bs-parent="#accordion-407489375"
 data-once="accordion-item-keep-open" id="accordion-item-712047284">
 <div class="accordion-body">
 <p>The Department of Psychiatry at the University of California, San
 Francisco invites applications from Clinician Educator members of the
 SFVAHCS Mental Health Service for a UCSF affiliate-paid faculty
 appointment. Applications will be held and reviewed based on
 availability of SFVAHCS Mental Health Service positions and funding.
 Start dates are variable, and these positions will be filled in the UC
 HS Clinical Professor or Professor of Clinical Psychiatry series at
 the rank commensurate with experience.</p>
 <p><a class="btn btn-primary"
 href="[https://aprecruit.ucsf.edu/JPF05634](<https://aprecruit.ucsf.edu/JPF05634>)" target="\_blank">Find out
 more and apply</a></p>
 </div>
 </div>
 </div>
 </div>
 2026-09-28 12:34:30  \[DEBUG\]  3242: Calling agent.do_task:
 task_key=parse_job_list index=psychiatry_ucsf_edu
 2026-09-28 12:34:30  \[DEBUG\]  1212: Response from
 \_culled_dom_for_parse: titles=\["Attending Child and Adolescent
 Psychiatrists (UCSF Health)", "Attending Child and Adolescent
 Psychologist (UCSF Health)", "Attending Psychiatrists (UCSF Health)",
 "Attending Psychologist (Behavioral Sleep Medicine)", "Attending
 Psychologist (OCD Program)", "Attending Psychologist (UCSF Health)",
 "Attending Psychologist (Zuckerberg San Francisco General Hospital and
 Trauma Center)", "Attending Public Psychiatrists (Zuckerberg San
 Francisco General Hospital and Trauma Center)", "Clinical and
 Translational Researcher", "Mental Health Clinician-Educator (San
 Francisco VA Health Care System)"\] containers=\["<div
 class="accordion" data-once="accordion-keep-open"
 data-usb-keep-open="false" id="accordion-407489375">\\n<div
 class="accordion-item">\\n<h2 class="accordion-header"
 id="heading--accordion-item-1825782552">\\n\\n      Attending Child
 and Adolescent Psychiatrists (UCSF Health)\\n    \\n</h2>\\n<div
 aria-labelledby="heading--accordion-item-1825782552"
 class="accordion-collapse collapse js-accordion-keep-open"
 data-bs-parent="#accordion-407489375"
 data-once="accordion-item-keep-open"
 id="accordion-item-1825782552">\\n<div
 class="accordion-body">\\n<p>UCSF Health is currently recruiting for
 a variety of vacant child/adolescent psychiatry positions in both
 inpatient and outpatient services.</p>\\n<p>Applications will be held
 and reviewed based on availability of positions and funding. These
 positions will be filled in a rank and series commensurate with
 experience.</p>\\n<p><a class="btn btn-primary"
 href="[https://aprecruit.ucsf.edu/JPF05824\\](<https://aprecruit.ucsf.edu/JPF05824%5C>)" target="\_blank">Find
 <8447 chars omitted>ucator (San Francisco VA Health Care System)\\n
 \\n</h2>\\n<div aria-labelledby="heading--accordion-item-712047284"
 class="accordion-collapse collapse js-accordion-keep-open"
 data-bs-parent="#accordion-407489375"
 data-once="accordion-item-keep-open"
 id="accordion-item-712047284">\\n<div
 class="accordion-body">\\n<p>The Department of Psychiatry at the
 University of California, San Francisco invites applications from
 Clinician Educator members of the SFVAHCS Mental Health Service for a
 UCSF affiliate-paid faculty appointment. Applications will be held and
 reviewed based on availability of SFVAHCS Mental Health Service
 positions and funding. Start dates are variable, and these positions
 will be filled in the UC HS Clinical Professor or Professor of
 Clinical Psychiatry series at the rank commensurate with
 experience.</p>\\n<p><a class="btn btn-primary"
 href="[https://aprecruit.ucsf.edu/JPF05634\\](<https://aprecruit.ucsf.edu/JPF05634%5C>)" target="\_blank">Find
 out more and apply</a></p>\\n</div>\\n</div>\\n</div>\\n</div>"\]
 cull_outcome='culled' dom_joined=<div class="accordion"
 data-once="accordion-keep-open" data-usb-keep-open="false"
 id="accordion-407489375">
 <div class="accordion-item">
 <h2 class="accordion-header" id="heading--accordion-item-1825782552">

```
   Attending Child and Adolescent Psychiatrists (UCSF Health)
```

</h2>
 <div aria-labelledby="heading--accordion-item-1825782552"
 class="accordion-collapse collapse js-accordion-keep-open"
 data-bs-parent="#accordion-407489375"
 data-once="accordion-item-keep-open" id="accordion-item-1825782552">
 <div class="accordion-body">
 <p>UCSF Health is currently recruiting for a variety of vacant
 child/adolescent psychiatry positions in both inpatient and outpatient
 services.</p>
 <p>Applications will be held and reviewed based on availability of
 positions and funding. These positions will be filled in a rank and
 series commensurate with experience.</p>
 <p><a class="btn btn-primary"
 href="[https://aprecruit.ucsf.edu/JPF05824](<https://aprecruit.ucsf.edu/JPF05824>)" target="\_blank">Find out
 more and apply</a></p>
 </div>
 </div>
 </di<8058 chars omitted>    Mental Health Clinician-Educator (San
 Francisco VA Health Care System)

</h2>
 <div aria-labelledby="heading--accordion-item-712047284"
 class="accordion-collapse collapse js-accordion-keep-open"
 data-bs-parent="#accordion-407489375"
 data-once="accordion-item-keep-open" id="accordion-item-712047284">
 <div class="accordion-body">
 <p>The Department of Psychiatry at the University of California, San
 Francisco invites applications from Clinician Educator members of the
 SFVAHCS Mental Health Service for a UCSF affiliate-paid faculty
 appointment. Applications will be held and reviewed based on
 availability of SFVAHCS Mental Health Service positions and funding.
 Start dates are variable, and these positions will be filled in the UC
 HS Clinical Professor or Professor of Clinical Psychiatry series at
 the rank commensurate with experience.</p>
 <p><a class="btn btn-primary"
 href="[https://aprecruit.ucsf.edu/JPF05634](<https://aprecruit.ucsf.edu/JPF05634>)" target="\_blank">Find out
 more and apply</a></p>
 </div>
 </div>
 </div>
 </div>
 2026-09-28 12:34:30  \[DEBUG\]  1068: Response from scrape_page:
 {"outcome": "ready", "wait_ms": 7740746, "visible_chars": 11432,
 "load_all_jobs_ran": true, "ready": true}
 2026-09-28 12:34:30  \[DEBUG\]  566: Response from \_post_telescope:
 {"final_url": "[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>)", "text": "\\n
  \\n    \\n\\n\\n      \\n      \\n        \\n    \\n      \\n        \\n\\n
 \\n    \\n  \\n\\n          \\n  \\n    \\n      \\n  \\n    \\n      \\n      \\n
          \\n\\n\\n\\n\\n\\n\\n  \\n    \\n      \\n        \\n        Career
 Opportunities\\n        \\n      \\n      \\n                        \\n
     \\n        \\n        \\n        \\n\\n    Take the next step in your
 career and make a meaningful impact with the UCSF Department of
 Psychiatry and Behavioral Sciences\\n\\n  \\n      \\n    \\n  \\n\\n\\n\\n
 \\n  \\n          \\n\\n\\n  \\n\\n\\n    \\n                            \\n  \\n
    \\n      \\n  \\n    \\n\\n  \\n  \\n    \\n\\n    \\n          \\n\\n
 \\n\\n    \\n  \\n  \\n\\n  \\n  \\n\\n\\n\\n  \\n    \\n
 \\n            \\n                              \\n
                      \\n
 \\n\\n\\n\\n\\n  \\n    \\n      \\n\\n    \\n          Academic faculty
 positions\\n\\n      \\n\\n\\n    \\n  \\n  \\n    <134230 chars omitted><div
 style="margin: 0px auto; top: 0px; left: 0px; right: 0px; position:
 fixed; border: 1px solid rgb(204, 204, 204); z-index: 2000000000;
 background-color: rgb(255, 255, 255);"><iframe title="recaptcha
 challenge expires in two minutes" style="width: 100%; height:
 100%;" name="c-oubrjzieqsu5" frameborder="0" scrolling="no"
 sandbox="allow-forms allow-popups allow-same-origin allow-scripts
 allow-top-navigation allow-modals allow-popups-to-escape-sandbox
 allow-storage-access-by-user-activation"
 src="[https://www.google.com/recaptcha/api2/bframe?hl=en&v=kemdRjWFxNjgsGdhRslyEPwU&k=6LfHrSkUAAAAAPnKk5cT6JuKlKPzbwyTYuO8--Vr&bft=0dAFcWeA6x1V9BtnwTOjA37Qw6KKMNpCuyeDp6JGj4gv6TOt9YE54V3_nr5Vi9zbFWF5qkKX26wxUkrwC8TF-6dBg7nh53XjQn3g\\"></iframe></div></div></body>"](<https://www.google.com/recaptcha/api2/bframe?hl=en&v=kemdRjWFxNjgsGdhRslyEPwU&k=6LfHrSkUAAAAAPnKk5cT6JuKlKPzbwyTYuO8--Vr&bft=0dAFcWeA6x1V9BtnwTOjA37Qw6KKMNpCuyeDp6JGj4gv6TOt9YE54V3_nr5Vi9zbFWF5qkKX26wxUkrwC8TF-6dBg7nh53XjQn3g%5C%22%3E%3C/iframe%3E%3C/div%3E%3C/div%3E%3C/body%3E%22>),
 "scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
 "issues": \[\], "content_chars": 11432, "requested_url":
 "[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>)", "final_url":
 "[https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>)"}}
 2026-09-28 12:34:30  \[INFO\]  6ac62384 | telescope job done:
 [https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>) ->
 [https://psychiatry.ucsf.edu/careers](<https://psychiatry.ucsf.edu/careers>) fields:text,html
 2026-09-28 12:34:30  \[DEBUG\]  2174: Calling send_to_deepseek:
 \[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
 max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams\]
 2026-09-28 12:34:30  \[DEBUG\]  1341: Response from
 \_store_prompt_blocks: \[{"type": "SYSTEM", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-system-da1ef1aba90460e6"},
 {"type": "CACHE_A", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-cache_a-850fac0c900f4d4f"},
 {"type": "NO_CACHE", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-no_cache-8d62f389641e54b8"},
 {"type": "TASK", "id":
 "parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae-task-46e4bb080ecca7c3"}\]

### Comments

#### chuckles — 2026-09-28T17:01:17.523Z
@susan finish-up blocked: `gh pr edit` (gh 2.46) fails on the retired Projects (classic) API, so create-dev-pr.py cannot update [PR #176](https://github.com/susansomerset/astral/pull/176). Nothing landed; ftr/sub refs intact. Options: patch create-dev-pr.py to `gh api -X PATCH`, upgrade gh, or merge #176 yourself. Reassign to Chuckles when ready.

#### chuckles — 2026-09-28T16:58:43.476Z
AST-1844 merge-child blocked — recalling Hedy for missing code(AST-1844) marker on the test-gap sub.

#### chuckles — 2026-09-28T16:29:42.659Z
[check-linear] amended — Hedy's two `src/external/telescope.py` lines (identity-based `_in_preserved_svg`, `to_thread` cull in `extract_page_dom`) added to Component/Technical scope; admin workbench path left out; assigned to Chuckles, `[bug-fix]` resumes Hedy's plan-fix on AST-1840

#### susan — 2026-09-28T16:28:48.100Z
@chuckles amend as written and reassign to yourself to continue.

#### chuckles — 2026-09-28T14:54:41.140Z
@susan AST-1840 is waiting on a scope amendment (Plan Discuss, Hedy's `[scope-gate]` on AST-1840). Her measurements show the 2h freeze is `_cull_html` in `src/external/telescope.py`, not `find_job_containers`. `_in_preserved_svg` (AST-1745) does set-membership checks on bs4 Tags, and bs4 hashes a Tag by serializing it, so the cost is quadratic: 1,000 rows took 144s, and 7MB didn't finish in 15 minutes. It also runs synchronously inside async `extract_page_dom`. The attribute snip runs after the slow part, so it won't help with speed.

To approve, add these two lines to AST-1838's Component/Technical scope under `src/external/telescope.py`:
- `_cull_html`: make `_in_preserved_svg` identity-based (return early on an empty set, otherwise compare by `id()`) so it never hashes a Tag. Same output, linear cost.
- `extract_page_dom`: modified to `await asyncio.to_thread(_cull_html, raw_html)` so the html cull never runs on the event loop.

Your call: should the admin workbench path (`telescope.py` ~629/631, which also calls `_cull_html` synchronously from async code) be included or left out?

Poller "Task was destroyed but it is pending": Hedy's read is that it survives this fix. `dispatcher._task_thread_target` closes each thread's loop without cancelling pending tasks. As step 6 says, I'll file it as a separate bug once this lands, unless you want it filed now.

When scope is amended (or you tell me "amend as written"), assign AST-1838 back to Chuckles and I'll respawn Hedy's plan-fix.

#### chuckles — 2026-09-28T14:22:49.619Z
[check-linear] Todo — DOM-size guard dropped from Proposed steps (attribute-length snip is the fix); poller error stays confirm-only per step 6; `[bug-fix]` picks it up

#### susan — 2026-09-28T14:21:40.633Z
@chuckles no dom size guard. The tag parameter limit should resolve the issue.

#### chuckles — 2026-09-28T14:00:43.260Z
[check-linear] answered — Proposed steps §3 now snips `_cull_html` attribute values over `html_cull.max_html_tag_length` (500, `src/utils/config.py`) to `"(snipped)"`, then culls the rest; Open questions (DOM-size guard, poller split) still open — to continue, assign to Chuckles (@susan)

#### susan — 2026-09-28T13:58:44.786Z
@chuckles my guess is that the culling of the dom allowed stored binary data in text.  Let's add an additional cull criteria in cull dom, where tag-parameter strings that are longer than max_html_tag_length (set in config.py to 500) are stripped with a max_length_placeholder of "(snipped)" so we can see where elements were snipped without guessing. Then proceed with what's left.

---

_Implementation detail may live in git history on `origin/dev`._
