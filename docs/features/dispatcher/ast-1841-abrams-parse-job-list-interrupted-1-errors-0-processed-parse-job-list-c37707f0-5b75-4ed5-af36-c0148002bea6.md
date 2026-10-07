# AST-1841 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6

<!-- linear-archive: AST-1841 archived 2026-10-07 -->

## Linear archive (AST-1841)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1841/abrams-parse-job-list-interrupted-1-errors-0-processed-parse-job-list  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Abrams `parse_job_list` batch `parse_job_list-c37707f0…` (12:39:59 → 14:50:56 UTC, **INTERRUPTED — 1 error / 0 processed**) showed three things. Two of them are already fixed on `dev`:

1. **\~2h event-loop stall (12:43 → 14:49), resolved on dev.** [AST-1840](https://linear.app/astralcareermatch/issue/AST-1840/fix-parse-job-list-dom-cull-blocks-event-loop-on-oversized-pages-snip) (`fb472a98`, part of [AST-1838](https://linear.app/astralcareermatch/issue/AST-1838/abrams-parse-job-list-interrupted-1-errors-0-processed-parse-job-list), on dev 19:18 UTC) moved the DOM culls off the event loop and fixed the quadratic `_cull_html`.
2. **Dispatch-thread loop teardown (12:40:33 "Event loop is closed" / "Task was destroyed but it is pending!" /** `telescope-result-poller` **destroyed), resolved on dev.** `c86d8b5c` added `_TelescopeQueue.aclose_current_loop()` / `close_loop_resources()` in `src/external/telescope.py` and calls it from `dispatcher._task_thread_target` before `loop.close()`.
3. **Still open: one-shot** `asyncio.run(...)` **callers never release Telescope's per-loop state.** `asyncio.run` closes its loop with the `_LoopState` for that loop (asyncpg pool, LISTEN connection, `telescope-result-poller` task, wake tasks) still open. `_TelescopeQueue._state()` later forgets closed loops from its dict but never closes their pool, because it can't once the loop is gone. Every such request can emit the same teardown errors seen at 12:40:33 and leak a pool plus a listener connection to the Telescope DB. Confirmed Telescope-reaching call sites: `src/ui/api/api_admin.py:2256` (`admin_telescope_scrape`), `src/ui/api/api_meteorite.py:109` (`land_meteorite`), `src/ui/api/api_inbox.py:222` (`_land_all`), `src/core/gazer.py:1482` (`ingest_meteorite_jobs_from_email_html_sync`).

## To-be

Every one-shot event loop that can touch Telescope awaits `close_loop_resources()` before the loop closes, the same guarantee dispatch threads already have. No "Event loop is closed" / "Task was destroyed" teardown noise, and no leaked Telescope DB pools or listener connections from Flask/admin/inbox requests.

## Proposed steps

1. Add one sync helper in `src/external/telescope.py`, next to `close_loop_resources`. It runs a coroutine through `asyncio.run` via a small wrapper that awaits the coroutine and then, in a `finally`, awaits `close_loop_resources()`. The teardown rule lives in one place.
2. Replace `asyncio.run(...)` with that helper at the four confirmed Telescope-reaching sites (`api_admin.py:2256`, `api_meteorite.py:109`, `api_inbox.py:222`, `gazer.py:1482`).
3. Component test: after the helper returns, the queue holds no `_LoopState` for that loop, and a coroutine that used the queue leaves no pending poller.

## Component scope

* `src/external/telescope.py` — modified. It owns the per-loop Telescope state and its teardown (`close_loop_resources`), so the one-shot-loop runner that guarantees that teardown belongs here too.
* `src/ui/api/api_admin.py` — modified. The admin Telescope scrape handler runs `admin_telescope_scrape` under a bare `asyncio.run`.
* `src/ui/api/api_meteorite.py` — modified. `land_meteorite` reaches Telescope (`meteorite.py` → `telescope.get_visible_text`) under a bare `asyncio.run`.
* `src/ui/api/api_inbox.py` — modified. `_land_all` lands meteorites (same Telescope reach) under a bare `asyncio.run`.
* `src/core/gazer.py` — modified. `ingest_meteorite_jobs_from_email_html_sync` is the sync wrapper for Flask/inbox callers and uses a bare `asyncio.run`.


* `src/core/contact.py` — modified (scope amended per [AST-1849](https://linear.app/astralcareermatch/issue/AST-1849/fix-asynciorun-callers-leak-telescope-per-loop-state-poolpoller-at) \[scope-gate\]). The contact-task dispatch loop runs async handlers (`create_contact_meteorite`, `contact_task_gazer_scrape`) under a bare `asyncio.run` (`asyncio.run(handler(cid, param, debug=debug))`), and those handlers reach Telescope.

Other `asyncio.run` sites (`candidate.py`, the other `contact.py` calls, `intake.py`, `api_intake.py`, and `api_admin.py:1679` workbench) are out of scope unless `plan-fix` shows they reach Telescope. In that case, amend scope before touching them.

## Technical scope

* `src/external/telescope.py` — new function: a sync runner that wraps `asyncio.run` and always awaits `close_loop_resources()` before the loop closes. This gives one-shot loops the same teardown guarantee `dispatcher._task_thread_target` already has.
* `src/ui/api/api_admin.py` — modified function (the Telescope scrape endpoint handler): call the new runner instead of `asyncio.run`, so the admin scrape releases its pool and poller.
* `src/ui/api/api_meteorite.py` — modified function (the land-meteorite endpoint handler): call the new runner instead of `asyncio.run`, for the same reason.
* `src/ui/api/api_inbox.py` — modified function (the inbox land-all handler): call the new runner instead of `asyncio.run`, for the same reason.
* `src/core/gazer.py` — modified function `ingest_meteorite_jobs_from_email_html_sync`: call the new runner instead of `asyncio.run`, for the same reason.


* `src/core/contact.py` — modified function (the contact-task dispatch loop, `asyncio.run(handler(...))` site only): call the new runner instead of `asyncio.run`, for the same reason. Other `asyncio.run` calls in `contact.py` stay as-is (they don't reach Telescope).

## Ancestor candidates

- [ ] [AST-1726](https://linear.app/astralcareermatch/issue/AST-1726/platform-telescopepy-drop-in-and-playwright-decommission-astral) — platform [telescope.py](<http://telescope.py>) drop-in / playwright decommission (`docs/features/foundation/ast-1726-platform-telescope-py-drop-in-playwright-decommission.md`): introduced the Telescope client whose per-loop queue state these callers leak
- [ ] [AST-1838](https://linear.app/astralcareermatch/issue/AST-1838/abrams-parse-job-list-interrupted-1-errors-0-processed-parse-job-list) — parse_job_list event loop block (on dev via #176): same incident shape. Its child [AST-1840](https://linear.app/astralcareermatch/issue/AST-1840/fix-parse-job-list-dom-cull-blocks-event-loop-on-oversized-pages-snip) fixed the stall half of this report.
- [ ] AST-327 — refactor task dispatcher to run independent threads (`docs/features/dispatcher/ast-327-refactor-task-dispatcher-independent-threads-plan.md`): origin of the multi-loop model (thread loops plus `asyncio.run` loops) that makes per-loop teardown necessary

---

## Original report

Full log below. It was decoded from the attached alert email (same content as the attachment).

```text
2026-09-28 12:39:59  [DEBUG]  750: Response from
get_new_company_batch: 20 entities
batch=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6
2026-09-28 12:39:59  [DEBUG]  730: Calling get_new_company_batch:
[state=JOBLIST_IDENTIFIED, limit=20, candidate_id=abrams,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
sort_by=updated_at, scan_interval_hours=None, score_floor=None,
states=["JOBLIST_IDENTIFIED", "JOBLIST_IDENTIFIED_RETRY"]]
2026-09-28 12:39:59  [DEBUG]  903: Calling _run_unified:
[task_key=parse_job_list, batch_size=20, entity_type=company,
trigger_state=JOBLIST_IDENTIFIED]
2026-09-28 12:39:59  [DEBUG]  1535: Calling _run_task:
[task_key=parse_job_list, available=253]
2026-09-28 12:39:59  [DEBUG]  1486: Beginning dispatch loop on 253 items
2026-09-28 12:39:59  [DEBUG]  1369: Calling _run_dispatch_loop:
[task_key=parse_job_list, available=253,
entity_batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6]
2026-09-28 12:39:59  [INFO]  abrams | dispatch company starting
parse_job_list — 253 available (batch:
parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6)
2026-09-28 12:40:00  [DEBUG]  335: Calling telescope job
f5714de8-a233-44d0-be66-4907e7caac87: {"url":
"https://mrisoftware.wd501.myworkdayjobs.com/external_careersite",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}
2026-09-28 12:40:00  [DEBUG]  335: Calling telescope job
0b44fff6-0d1e-468e-8d24-2b2ea4670aa4: {"url":
"https://www.utmb.edu/hr/careers", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:00  [DEBUG]  335: Calling telescope job
eb844f45-8dc0-4961-a8bc-44204e6d86ff: {"url":
"https://sc.edu/about/employment", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:00  [DEBUG]  335: Calling telescope job
9b32c3cc-535d-4a90-8b32-668f506d7d3a: {"url":
"https://www.volvogroup.com/en/careers/job-openings.html", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}
2026-09-28 12:40:00  [DEBUG]  335: Calling telescope job
3cf0016a-7706-455b-9091-570ba0d64134: {"url":
"https://apply.workable.com/huggingface", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:00  [DEBUG]  335: Calling telescope job
4da6ab15-e736-4968-8687-498e88fc61f5: {"url":
"https://hr.nih.gov/careers/open-positions", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}
2026-09-28 12:40:00  [DEBUG]  335: Calling telescope job
a5f29456-3361-4f26-b751-3faee726f6f2: {"url":
"https://cmu.wd115.myworkdayjobs.com/SEI", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://www.cochrane.org/about-us/jobs", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://www.cochrane.org/about-us/jobs fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://www.cochrane.org/about-us/jobs titles=["Commercial Sales
Lead", "Publishing Operations Lead"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [20/20] cochrane_org_2
state=JOBLIST_IDENTIFIED url=https://www.cochrane.org/about-us/jobs
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://careers.wexnermedical.osu.edu/search/searchjobs",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://careers.wexnermedical.osu.edu/search/searchjobs
fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://careers.wexnermedical.osu.edu/search/searchjobs
titles=["Clinical Research Coordinator- Neurology", "Clinic Nurse -
Thoracic (IRP/Contingent)", "Staff Nurse - Hematology and Transplant
(IRP/Contingent)", "Clinic Nurse (RN) - GU and Urology", "Research
Senior Technician- Microbial Infection and Immunity", "Associate Nurse
Manager - Acute Care - General Medicine", "CT Lead Tech $15,000
Signing Bonus 3rd shift I UH Inpatient Patient Tower", "Post Doctoral
Scholar - Comprehensive Cancer Center", "Specialty Practice
Pharmacist", "Multi-Modality Imaging Tech $15,000 Signing Bonus"]
state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [19/20] careers_wexnermedical_osu_edu
state=JOBLIST_IDENTIFIED
url=https://careers.wexnermedical.osu.edu/search/searchjobs
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://psychiatry.ucsf.edu/careers", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://psychiatry.ucsf.edu/careers fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://psychiatry.ucsf.edu/careers
titles=["Attending Child and Adolescent Psychiatrists (UCSF Health)",
"Attending Child and Adolescent Psychologist (UCSF Health)",
"Attending Psychiatrists (UCSF Health)", "Attending Psychologist
(Behavioral Sleep Medicine)", "Attending Psychologist (OCD Program)",
"Attending Psychologist (UCSF Health)", "Attending Psychologist
(Zuckerberg San Francisco General Hospital and Trauma Center)",
"Attending Public Psychiatrists (Zuckerberg San Francisco General
Hospital and Trauma Center)", "Clinical and Translational Researcher",
"Mental Health Clinician-Educator (San Francisco VA Health Care
System)"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [18/20] psychiatry_ucsf_edu
state=JOBLIST_IDENTIFIED url=https://psychiatry.ucsf.edu/careers
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://drugfree.org/article/work-at-the-partnership",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://drugfree.org/article/work-at-the-partnership
fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://drugfree.org/article/work-at-the-partnership
titles=["Revenue Operations Coordinator"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [17/20] drugfree_org
state=JOBLIST_IDENTIFIED
url=https://drugfree.org/article/work-at-the-partnership
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies
fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies
titles=["Alzheimer’s Society UKDTN Research Nurse"]
state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [16/20] oxfordhealthbrc_nihr_ac_uk
state=JOBLIST_IDENTIFIED
url=https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de
fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de
titles=["Technische Assistenz im Institut für Organische Chemie",
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
Hochschulambulanz"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [15/20] psy_unihamburg_de
state=JOBLIST_IDENTIFIED
url=https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://www.pesi.com/careers", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://www.pesi.com/careers fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://www.pesi.com/careers
titles=["Brand Manager (remote or in-office)", "Business Development
Manager", "CE Accreditation Advisor – Licensed Counselor", "CE
Accreditation Advisor – Licensed Psychologist", "Customer Success
Specialist", "Direct Response Copywriter", "Email Marketing
Strategist", "Lead Software Engineer", "Product Administration
Specialist", "Social Media Strategist (Remote or Hybrid)"]
state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [14/20] pesi_com state=JOBLIST_IDENTIFIED
url=https://www.pesi.com/careers
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://revivalresearch.org/careers", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://revivalresearch.org/careers fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://revivalresearch.org/careers
titles=["Physician Assistant", "Phlebotomist/Lab Tech", "Clinical
Research Coordinator – Illinois", "Clinical Research Coordinator –
Texas", "Clinical Research Coordinator – New Jersey", "Clinical
Research Coordinator – North Carolina"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [13/20] revivalresearch_org
state=JOBLIST_IDENTIFIED url=https://revivalresearch.org/careers
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://jobs.rcpsych.ac.uk", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://jobs.rcpsych.ac.uk fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://jobs.rcpsych.ac.uk
titles=["Forensic Psychiatrists", "Senior Staff Specialist or Staff
Specialist or Senior Medical Officer (Psychiatrist - Intellectual and
Developmental Disability) (Bundaberg)", "Consultant Child and
Adolescent Psychiatrist", "Senior Staff Specialist or Staff Specialist
or Senior Medical Officer (Psychiatrist) (Hervey Bay and
Maryborough)", "Clinical Director and Staff Specialist in Mental
Health CCLHD"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [12/20] rcpsych_ac_uk
state=JOBLIST_IDENTIFIED url=https://jobs.rcpsych.ac.uk
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://rogersbh.org/careers", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://rogersbh.org/careers fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://rogersbh.org/careers
titles=["Mental Health Technician – Residential, Overnight",
"Registered Nurse", "Therapist – Part Time/PRN"]
state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [11/20] rogersbh_org
state=JOBLIST_IDENTIFIED url=https://rogersbh.org/careers
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://reviveresearch.org/careers", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://reviveresearch.org/careers fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://reviveresearch.org/careers
titles=["CLINICAL RESEARCH COORDINATOR", "Research Regulatory
Coordinator", "Clinical Research Medical Assistant", "MEDICAL
ADMINISTRATIVE ASSISTANT", "Research Intern"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [10/20] reviveresearch_org
state=JOBLIST_IDENTIFIED url=https://reviveresearch.org/careers
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav
fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav
titles=["Medical Assistant", "Patient Account Representative",
"Environmental Svcs Worker", "Full Time - Surgical Scheduler -
Orthopedics", "Transporter"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [9/20] northwell_edu_2
state=JOBLIST_IDENTIFIED
url=https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://www.bcchr.ca/careers", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://www.bcchr.ca/careers fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://www.bcchr.ca/careers
titles=["Manager, Research IT, BC Children’s Hospital Research
Institute"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [8/20] bcchr_ca state=JOBLIST_IDENTIFIED
url=https://www.bcchr.ca/careers
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://mrisoftware.wd501.myworkdayjobs.com/external_careersite",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://mrisoftware.wd501.myworkdayjobs.com/external_careersite
fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://mrisoftware.wd501.myworkdayjobs.com/external_careersite
titles=["PMO Manager", "Senior Property Accountant IV", "Systems
Administrator III", "Billing Analyst", "Program Manager", "Application
Support Analyst (SQL)", "Account Manager (Residential)", "SaaS
Implementation Consultant (NA Hours)", "Project Scoping Specialist (UK
Hours)", "Director - Product Management"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [7/20] mrisoftware_com
state=JOBLIST_IDENTIFIED
url=https://mrisoftware.wd501.myworkdayjobs.com/external_careersite
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://www.utmb.edu/hr/careers", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://www.utmb.edu/hr/careers fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://www.utmb.edu/hr/careers
titles=["Neurodiagnostic Technologist II – Epilepsy Monitoring
(Nights)", "Neurodiagnostic Technologist II – EMU (3–12 hour shifts)",
"Laboratory Services Manager – Blood Bank"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [6/20] utmb_edu_2
state=JOBLIST_IDENTIFIED url=https://www.utmb.edu/hr/careers
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://sc.edu/about/employment", "fields": ["text",
"html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://sc.edu/about/employment fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch: url=https://sc.edu/about/employment
titles=["Assistant Director, Facilities"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [5/20] sc_edu state=JOBLIST_IDENTIFIED
url=https://sc.edu/about/employment
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://www.volvogroup.com/en/careers/job-openings.html",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://www.volvogroup.com/en/careers/job-openings.html
fields=text,html careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://www.volvogroup.com/en/careers/job-openings.html
titles=["Transport Analyst", "Accountant - R2R", "2027 Ausbildung
Fachkraft (m/w/d) für Lagerlogistik", "Conseiller(e) Service Clients
Atelier Poids-Lourds H/F - CDI", "Thesis work: Calculation of service
intervals", "Jobstudent Talent Acquisition", "VIE - Adaptation buyer
H/F", "Aprendiz Senai", "Senior Software Engineer", "Senior System
Performance Engineer"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [4/20] volvogroup_com_2
state=JOBLIST_IDENTIFIED
url=https://www.volvogroup.com/en/careers/job-openings.html
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://apply.workable.com/huggingface", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://apply.workable.com/huggingface fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://apply.workable.com/huggingface titles=["Senior Open-Source
Python Engineer, ML Developer Tools - EMEA Remote", "Senior
Open-Source Python Engineer, ML Developer Tools - US Remote", "Senior
Machine Learning Engineer, Voice Agents - EMEA Remote", "Low-Level
Senior Software Engineer, Xet Storage - US Remote", "Low-level Senior
Software Engineer, Xet Storage - EMEA Remote", "Open-Source Machine
Learning Engineer - US Remote", "Wild Card"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [3/20] huggingface_co
state=JOBLIST_IDENTIFIED url=https://apply.workable.com/huggingface
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://hr.nih.gov/careers/open-positions", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://hr.nih.gov/careers/open-positions fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://hr.nih.gov/careers/open-positions titles=["Staff Scientist
I", "Deputy Director, Division of Extramural Research", "Staff
Clinician", "Administrative Technician", "Biologist Scientist
Administrator (Scientific Review Officer)", "Health Scientist
Administrator (Program Officer)", "Lead Nuclear Medicine
Technologist", "Mechanical Engineer", "Royalties Analyst",
"Supervisory Data Scientist"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [2/20] training_nih_gov
state=JOBLIST_IDENTIFIED url=https://hr.nih.gov/careers/open-positions
2026-09-28 12:40:00  [DEBUG]  564: Calling _post_telescope:
[body={"url": "https://cmu.wd115.myworkdayjobs.com/SEI", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}]
2026-09-28 12:40:00  [DEBUG]  1065: Calling scrape_page:
[url=https://cmu.wd115.myworkdayjobs.com/SEI fields=text,html
careers_list=True]
2026-09-28 12:40:00  [DEBUG]  1192: Calling
run_parse_job_list_dispatch:
url=https://cmu.wd115.myworkdayjobs.com/SEI titles=["Technical Site
Lead  - SEI Customer Site - Fort Meade, MD", "Senior Solutions
Engineer", "Solutions Engineer", "Technical Engagement Lead",
"Executive Assistant to the Chief Financial Officer", "Software
Engineer", "Senior Real-Time Embedded Software Engineer", "Senior
Embedded Software Engineer", "Real-Time Embedded Software Engineer",
"IT Support Associate"] state=JOBLIST_IDENTIFIED
2026-09-28 12:40:00  [DEBUG]  1302: Calling
run_parse_job_list_dispatch: [1/20] cmu_wd5_myworkdayjobs_com
state=JOBLIST_IDENTIFIED url=https://cmu.wd115.myworkdayjobs.com/SEI
2026-09-28 12:40:00  [DEBUG]  1291: Beginning parse_job_list loop on 20 items
2026-09-28 12:40:00  [DEBUG]  112: Calling
roster.parse_job_list_batch:
[batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6, n=20]
2026-09-28 12:40:00  [DEBUG]  827: Calling consult.run_consult_task:
[entity_type=company, state=JOBLIST_IDENTIFIED, n=20,
batch=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
task_key=parse_job_list]
2026-09-28 12:40:00  [DEBUG]  757: End company claim loop after 20 items
2026-09-28 12:40:00  [DEBUG]  756: Beginning company claim loop on 20 items
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
c449dd2c-bd79-4115-8f53-dc8c5d972e2f: {"url":
"https://www.cochrane.org/about-us/jobs", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
dd6a600a-2d44-446a-a97f-349e76379d61: {"url":
"https://careers.wexnermedical.osu.edu/search/searchjobs", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
7679559a-3056-4350-a93a-9d41545e3f5f: {"url":
"https://psychiatry.ucsf.edu/careers", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
c5eef091-f6af-480a-babe-846a13e12d29: {"url":
"https://drugfree.org/article/work-at-the-partnership", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
7c3f7498-a16e-4ec8-82be-877abbbe6f2f: {"url":
"https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies", "fields":
["text", "html"], "expand": true, "wait_ready": true, "debug": true,
"selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
36b66f0c-e349-43bc-868d-832e8b40b4fa: {"url":
"https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
cb9d71ac-62f6-4378-9697-5f6618eb88a7: {"url":
"https://www.pesi.com/careers", "fields": ["text", "html"], "expand":
true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
ff28c96b-6990-434d-946a-c9ae5d9b86e2: {"url":
"https://revivalresearch.org/careers", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
3be968f3-8dcd-4d17-8e06-981c9de2d902: {"url":
"https://jobs.rcpsych.ac.uk", "fields": ["text", "html"], "expand":
true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
a0885a9d-0f07-4d3f-aae5-cc203bd89341: {"url":
"https://rogersbh.org/careers", "fields": ["text", "html"], "expand":
true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
40ab146c-3a4b-496c-bc4c-5588a04aadd5: {"url":
"https://reviveresearch.org/careers", "fields": ["text", "html"],
"expand": true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
32491242-377b-42c8-8ac3-a964789a1dc4: {"url":
"https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav",
"fields": ["text", "html"], "expand": true, "wait_ready": true,
"debug": true, "selector": "body"}
2026-09-28 12:40:01  [DEBUG]  335: Calling telescope job
469c6744-5b53-46b9-ba23-91e3a462c857: {"url":
"https://www.bcchr.ca/careers", "fields": ["text", "html"], "expand":
true, "wait_ready": true, "debug": true, "selector": "body"}
2026-09-28 12:40:33  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://cmu.wd115.myworkdayjobs.com/SEI", "text":
"\nSkip to main contentSearchFiltersCityJob FunctionPosition
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
Ago2024794Real-Time E<89295 chars
omitted>s/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);\";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var
a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else
if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var
e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();</script><iframe
height=\"1\" width=\"1\" style=\"position: absolute; top: 0px; left:
0px; border: medium; visibility: hidden;\"></iframe>\n</body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 2001, "requested_url":
"https://cmu.wd115.myworkdayjobs.com/SEI", "final_url":
"https://cmu.wd115.myworkdayjobs.com/SEI"}}
2026-09-28 12:40:33  [INFO]  a5f29456 | telescope job done:
https://cmu.wd115.myworkdayjobs.com/SEI ->
https://cmu.wd115.myworkdayjobs.com/SEI fields:text,html
2026-09-28 12:40:33  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 12:40:33  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-d070477f10361b7a"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 12:40:33  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=rogersbh_org, n=4]
2026-09-28 12:40:33  [DEBUG]  3243: Calling agent.do_task
live_content: <div aria-live="polite" class="swiper-wrapper
elementor-slides" id="swiper-wrapper-c19bd4958c84b1b1"><div
aria-roledescription="slide" class="elementor-repeater-item-1363bc3
swiper-slide swiper-slide-duplicate" data-swiper-slide-index="0"
role="group"><div class="swiper-slide-bg"></div><a
class="swiper-slide-inner"
href="https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741"
target="_blank"><div class="swiper-slide-contents"><div
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
target="_blank"><div class="swiper-slide-contents"><div
class="elementor-slide-heading">Registered Nurse</div><div
class="elementor-slide-description">Oconomowoc, WI</div><div
class="elementor-button elementor-slide-button
elementor-size-md">Apply Here</div></div></a></div><div
aria-roledescription="slide" class="elementor-repeater-item-d8bb69a
swiper-slide swiper-slide-duplicate" data-swiper-slide-index="2"
role="group"><div class="swiper-slide-bg"></div><a
class="swiper-slide-inner"
href="https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690"
target="_blank"><div class="swiper-slide-contents"><div
class="elementor-slide-heading">Therapist – Part Time/PRN</div><div
class="elementor-slide-description">Brown Deer, WI</div><div
class="elementor-button elementor-slide-button
elementor-size-md">Apply Here</div></div></a></div></div>
2026-09-28 12:40:33  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=rogersbh_org
2026-09-28 12:40:33  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Mental Health Technician –
Residential, Overnight", "Registered Nurse", "Therapist – Part
Time/PRN"] containers=["<div aria-live=\"polite\"
class=\"swiper-wrapper elementor-slides\"
id=\"swiper-wrapper-c19bd4958c84b1b1\"><div
aria-roledescription=\"slide\" class=\"elementor-repeater-item-1363bc3
swiper-slide swiper-slide-duplicate\" data-swiper-slide-index=\"0\"
role=\"group\"><div class=\"swiper-slide-bg\"></div><a
class=\"swiper-slide-inner\"
href=\"https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741\"
target=\"_blank\"><div class=\"swiper-slide-contents\"><div
class=\"elementor-slide-heading\">Mental Health Technician –
Residential, Overnight</div><div
class=\"elementor-slide-description\">Oconomowoc, WI</div><div
class=\"elementor-button elementor-slide-button
elementor-size-md\">Apply Here</div></div></a></div><div
aria-roledescription=\"slide\" class=\"elementor-repeater-item-6a55170
swiper-slide swiper-slide-duplicate\" data-swiper-slide-index=\"1\"
role=\"group\"><div class=\"swiper-slide-bg\"<4108 chars
omitted>Registered-Nurse---Residential_1712212-1\"
target=\"_blank\"><div class=\"swiper-slide-contents\"><div
class=\"elementor-slide-heading\">Registered Nurse</div><div
class=\"elementor-slide-description\">Oconomowoc, WI</div><div
class=\"elementor-button elementor-slide-button
elementor-size-md\">Apply Here</div></div></a></div><div
aria-roledescription=\"slide\" class=\"elementor-repeater-item-d8bb69a
swiper-slide swiper-slide-duplicate\" data-swiper-slide-index=\"2\"
role=\"group\"><div class=\"swiper-slide-bg\"></div><a
class=\"swiper-slide-inner\"
href=\"https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690\"
target=\"_blank\"><div class=\"swiper-slide-contents\"><div
class=\"elementor-slide-heading\">Therapist – Part Time/PRN</div><div
class=\"elementor-slide-description\">Brown Deer, WI</div><div
class=\"elementor-button elementor-slide-button
elementor-size-md\">Apply Here</div></div></a></div></div>"]
cull_outcome='culled' dom_joined=<div aria-live="polite"
class="swiper-wrapper elementor-slides"
id="swiper-wrapper-c19bd4958c84b1b1"><div aria-roledescription="slide"
class="elementor-repeater-item-1363bc3 swiper-slide
swiper-slide-duplicate" data-swiper-slide-index="0" role="group"><div
class="swiper-slide-bg"></div><a class="swiper-slide-inner"
href="https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Oconomowoc-Main-Campus-Oconomowoc-WI/Mental-Health-Technician---Residential--Overnight_1710741"
target="_blank"><div class="swiper-slide-contents"><div
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
target="_blank"><div class="swiper-slide-contents"><div
class="elementor-slide-heading">Registered Nurse</div><div
class="elementor-slide-description">Oconomowoc, WI</div><div
class="elementor-button elementor-slide-button
elementor-size-md">Apply Here</div></div></a></div><div
aria-roledescription="slide" class="elementor-repeater-item-d8bb69a
swiper-slide swiper-slide-duplicate" data-swiper-slide-index="2"
role="group"><div class="swiper-slide-bg"></div><a
class="swiper-slide-inner"
href="https://rogersbh.wd1.myworkdayjobs.com/RBHCareer/job/Brown-Deer-Main-Campus-Brown-Deer-WI/Therapist--Part-Time-PRN--Brown-Deer_1710690"
target="_blank"><div class="swiper-slide-contents"><div
class="elementor-slide-heading">Therapist – Part Time/PRN</div><div
class="elementor-slide-description">Brown Deer, WI</div><div
class="elementor-button elementor-slide-button
elementor-size-md">Apply Here</div></div></a></div></div>
2026-09-28 12:40:33  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 27025, "visible_chars": 9987,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 12:40:33  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://rogersbh.org/careers/", "text":
"\n\t\t\n\t\t\n\n\t\t\n\n\n\n\n\n\n\n\n\n\tSkip to content\n\t\n
 \n            \n              Menu\n            \n        \n
Close\n        \t\n\t\t\n\t\t\t\n\t\t\t\t\n\t\t\t\t\t\t\n\t\t\t\n\t\n\t\n\t\t\n
                   \n                    What You'll Find on This
Page\n                    \n                Careers at Rogers
Behavioral HealthJoin the Rogers Behavioral Health TeamJoin the Rogers
Behavioral Health TeamCareers at Rogers Behavioral Health Transform
LivesWhy Work at Rogers?Career EventsAfter You ApplyReady to
Apply?\t\t\n\t\t\t\t\n\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\tCareers at
Rogers Behavioral
Health\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\t\t\t\n\t\t\t\n\t\t\t\t\t\t\n\t\t\n\t\t\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\tHome
 Careers at Rogers Behavioral
Health\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\<219394
chars omitted>><a href=\"#\" data-fp-lang=\"fa\"><span
translate=\"no\">Farsi (Persian)</span></a><a href=\"#\"
data-fp-lang=\"hy\"><span translate=\"no\">Armenian</span></a><a
href=\"#\" data-fp-lang=\"ja\"><span
translate=\"no\">Japanese</span></a><a href=\"#\"
data-fp-lang=\"fr\"><span translate=\"no\">French</span></a><a
href=\"#\" data-fp-lang=\"pa\"><span
translate=\"no\">Punjabi</span></a></div><a href=\"#\"
translate=\"yes\" id=\"freshpaint-active-language\"><span
translate=\"no\">English</span></a></div><script
src=\"https://widget.us.limbic.ai/iframe-loader.js?iframe=eyJpZnJhbWVUb2tlbiI6InJ5aFhmOWtobkswMzVBdHc0Nkc2bEgwV3h5S3hYV29HR1AzMXhsX0t2dyIsImlmcmFtZVNvdXJjZSI6Imh0dHBzOi8vd2lkZ2V0LnVzLmxpbWJpYy5haT9hZ2VudElEPTY5NDA3N2FhYjM2YzUyNjE1YmYwNDkxNSJ9&amp;mode=popup\"
defer=\"\"></script></body>", "scrape_meta": {"bot_blocked": false,
"cookies_dismissed": false, "issues": [], "content_chars": 9987,
"requested_url": "https://rogersbh.org/careers", "final_url":
"https://rogersbh.org/careers/"}}
2026-09-28 12:40:33  [INFO]  a0885a9d | telescope job done:
https://rogersbh.org/careers -> https://rogersbh.org/careers/
fields:text,html
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.171.2.129:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [ERROR]  Fatal error on SSL protocol
protocol: <asyncio.sslproto.SSLProtocol object at 0x7fa7e53f45c0>
transport: <_SelectorSocketTransport closing fd=15>
Traceback (most recent call last):
  File "/opt/venv/lib/python3.12/site-packages/asyncpg/pool.py", line
239, in release
    await self._con.reset(timeout=budget)
  File "/opt/venv/lib/python3.12/site-packages/asyncpg/connection.py",
line 1571, in reset
    await self.execute(reset_query)
  File "/opt/venv/lib/python3.12/site-packages/asyncpg/connection.py",
line 354, in execute
    result = await self._protocol.query(query, timeout)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "asyncpg/protocol/protocol.pyx", line 358, in query
  File "asyncpg/protocol/protocol.pyx", line 713, in
asyncpg.protocol.protocol.BaseProtocol._get_timeout
  File "asyncpg/protocol/protocol.pyx", line 717, in
asyncpg.protocol.protocol.BaseProtocol._get_timeout_impl
AttributeError: 'NoneType' object has no attribute '_config'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
line 1075, in write
    n = self._sock.send(data)
        ^^^^^^^^^^^^^^^^^^^^^
OSError: [Errno 9] Bad file descriptor

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/root/.nix-profile/lib/python3.12/asyncio/sslproto.py", line
694, in _write_appdata
    self._do_write()
  File "/root/.nix-profile/lib/python3.12/asyncio/sslproto.py", line
713, in _do_write
    self._process_outgoing()
  File "/root/.nix-profile/lib/python3.12/asyncio/sslproto.py", line
719, in _process_outgoing
    self._transport.write(data)
  File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
line 1081, in write
    self._fatal_error(exc, 'Fatal write error on socket transport')
  File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
line 894, in _fatal_error
    self._force_close(exc)
  File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
line 906, in _force_close
    self._loop.call_soon(self._call_connection_lost, exc)
  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py",
line 795, in call_soon
    self._check_closed()
  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py",
line 541, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
2026-09-28 12:40:33  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 12:40:33  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-6bdb4cf4aa1c256c"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 12:40:33  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=northwell_edu_2, n=4]
2026-09-28 12:40:33  [DEBUG]  3243: Calling agent.do_task
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
2026-09-28 12:40:33  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=northwell_edu_2
2026-09-28 12:40:33  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Medical Assistant", "Patient Account
Representative", "Environmental Svcs Worker", "Full Time - Surgical
Scheduler - Orthopedics", "Transporter"] containers=["<div
class=\"widget clearfix widget-joblist\" id=\"widget_job_list_v2-13\"
role=\"list\"><div class=\"widget_joblist_row\" role=\"listitem\"><a
href=\"/job-3/23501366/medical-assistant-plainview-ny/\"
lang=\"en\">Medical Assistant</a><div
class=\"widget_joblist_category\" lang=\"en\">Clinical
Support</div><div class=\"widget_joblist_loc\" lang=\"en\">Plainview,
NY</div></div><div class=\"widget_joblist_row alt\"
role=\"listitem\"><a
href=\"/job-3/23787555/patient-account-representative-lake-success-ny/\"
lang=\"en\">Patient Account Representative</a><div
class=\"widget_joblist_category\" lang=\"en\">Revenue Cycle</div><div
class=\"widget_joblist_loc\" lang=\"en\">Lake Success,
NY</div></div><div class=\"widget_joblist_row\" role=\"listitem\"><a
href=\"/job-3/23659975/environmental-svcs-worker-new-hyde-park-ny/\"
lang=\"en\">Environmental Svcs Worker</a><div
class=\"widget_joblist_category\" lang=\"en\">Facilities and Support
Services</div><div class=\"widget_joblist_loc\" lang=\"en\">New Hyde
Park, NY</div></div><div class=\"widget_joblist_row alt\"
role=\"listitem\"><a
href=\"/job-3/23918518/full-time-surgical-scheduler-orthopedics-lynbrook-ny/\"
lang=\"en\">Full Time - Surgical Scheduler - Orthopedics</a><div
class=\"widget_joblist_category\" lang=\"en\">Clinical
Support</div><div class=\"widget_joblist_loc\" lang=\"en\">Lynbrook,
NY</div></div><div class=\"widget_joblist_row\" role=\"listitem\"><a
href=\"/job-3/23742033/medical-assistant-rockville-centre-ny/\"
lang=\"en\">Medical Assistant</a><div
class=\"widget_joblist_category\" lang=\"en\">Clinical
Support</div><div class=\"widget_joblist_loc\" lang=\"en\">Rockville
Centre, NY</div></div><div class=\"widget_joblist_row alt\"
role=\"listitem\"><a
href=\"/job-3/23590496/transporter-forest-hills-ny/\"
lang=\"en\">Transporter</a><div class=\"widget_joblist_category\"
lang=\"en\">Facilities and Support Services</div><div
class=\"widget_joblist_loc\" lang=\"en\">Forest Hills,
NY</div></div></div>"] cull_outcome='culled' dom_joined=<div
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
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8045' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8044' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8043' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8040' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8038' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8037' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8036' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8035' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-8034' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-7905' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-7904' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-7903' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='Task-7901' coro=<to_thread() running at
/root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
wait_for=<Future pending
cb=[_chain_future.<locals>._call_check_cancel() at
/root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
Task.task_wakeup()]>>
2026-09-28 12:40:33  [WARNING]  telescope result poll failed:
RuntimeError: coroutine ignored GeneratorExit
2026-09-28 12:40:33  [ERROR]  Task was destroyed but it is pending!
task: <Task pending name='telescope-result-poller'
coro=<_TelescopeQueue._poll_loop() running at
/app/src/external/telescope.py:305> wait_for=<Future finished
result=[<Record oid=2...ype_name=None>, <Record
oid=2...ype_name=None>]>>
2026-09-28 12:40:33  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 18090, "visible_chars": 13597,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 12:40:33  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav",
"text": "\n\n\n\n\t\t\t\t\nSkip to main contentHide Menu\nSearch
jobs\nAbout us\n\n\n\n\tOur culture\n\tBenefits\n\tCareer
Experience\n\tAlumni Network\n\tLocations\n\tFAQ\n\n\nCareer
specialties\n\n\n\n\tAdvanced Clinical Provider\n\tCancer\n\tClinical
Care\n\tCulinary\n\tExecutives\n\tHome Health Aides\n\tInformation
Technology\n\tLaboratory\n\tNursing\n\t\n\t\tExternships, Fellowships
and Nurse Residency Programs\n\t\tPerioperative – Pre-Surgical, OR,
PACU, Endoscopy\n\t\n\n\tPhysicians\n\tProfessional / Technical /
Support\n\tResearch\n\n\nTemp jobs\nStudents\nVeterans\nInclusion and
Belonging\nCareers blog\n\n\n\n\t\n\n\n\n\n\n\tMenu Hide\n\t\tYou are
here: Home\nTogether, we will deliver healthcare to the communities
where we live, love and belong\n\nSearch JobsJob ID, Keywords or MOS
CodeSearch near a location\n\n\n\nAt Northwell Health, we’re 100,000+
strong—caring for millions o<369479 chars
omitted>a=[10,25,50,75,100],m=setInterval(function(){for(var
l=c.target.getCurrentTime()/k*100,b=0;b<a.length;b++)l>=a[b]&&(window.dataLayer.push({event:\"gtm.video\",video_status:\"progress\",video_percent:a[b],video_title:c.target.getVideoData().title,\nvideo_url:g.src}),a.splice(b,1));a.length===0&&clearInterval(m)},1E3)})}else
setTimeout(e,300)}window.addEventListener(\"load\",e)})();</script>\n<ul
id=\"ui-id-2\" tabindex=\"0\" class=\"ui-menu ui-widget
ui-widget-content ui-autocomplete here-autocomplete ui-front\"
style=\"display: none;\" unselectable=\"on\"></ul><div role=\"status\"
aria-live=\"assertive\" aria-relevant=\"additions\"
class=\"ui-helper-hidden-accessible\"></div></body>", "scrape_meta":
{"bot_blocked": false, "cookies_dismissed": false, "issues": [],
"content_chars": 13597, "requested_url":
"https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav",
"final_url": "https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav"}}
2026-09-28 12:40:33  [INFO]  32491242 | telescope job done:
https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav
-> https://jobs.northwell.edu/?utm_source=corp&utm_medium=website&utm_campaign=topnav
fields:text,html
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.213.120.106:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.160.15.121:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.147.174.182:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  480: Response from telescope wake:
http://10.137.85.223:8080/wake ConnectError: All connection attempts
failed
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.159.223.97:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.236.195.178:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.225.152.224:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.191.122.46:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  477: Response from telescope wake:
http://10.173.146.100:8080/wake 200 {"status":"awake","woke":true}
2026-09-28 12:40:33  [DEBUG]  470: Calling telescope wake: 10
replica(s) ["http://10.137.85.223:8080/wake",
"http://10.147.174.182:8080/wake", "http://10.159.223.97:8080/wake",
"http://10.160.15.121:8080/wake", "http://10.171.2.129:8080/wake",
"http://10.173.146.100:8080/wake", "http://10.191.122.46:8080/wake",
"http://10.213.120.106:8080/wake", "http://10.225.152.224:8080/wake",
"http://10.236.195.178:8080/wake"]
2026-09-28 12:43:08  [DEBUG]  3243: Calling agent.do_task
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
2026-09-28 12:43:08  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=huggingface_co
2026-09-28 12:43:08  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Senior Open-Source Python Engineer, ML
Developer Tools - EMEA Remote", "Senior Open-Source Python Engineer,
ML Developer Tools - US Remote", "Senior Machine Learning Engineer,
Voice Agents - EMEA Remote", "Low-Level Senior Software Engineer, Xet
Storage - US Remote", "Low-level Senior Software Engineer, Xet Storage
- EMEA Remote", "Open-Source Machine Learning Engineer - US Remote",
"Wild Card"] containers=["<ul class=\"styles--Qqz1P\" data-ui=\"list\"
role=\"list\"><li class=\"styles--1vo9F\" data-id=\"DB4D7C0EC8\"
data-ui=\"job\" role=\"listitem\"><a
aria-labelledby=\"DB4D7C0EC8_title DB4D7C0EC8_posted_on
DB4D7C0EC8_department\" class=\"styles--1OnOt\"
href=\"/huggingface/j/DB4D7C0EC8/\"></a><div><h3
class=\"styles--3TJHk\" data-ui=\"job-title\"
id=\"DB4D7C0EC8_title\"><span>Senior Open-Source Python Engineer, ML
Developer Tools - EMEA Remote</span></h3></div><span
class=\"styles--QTMDv styles--2TdGW styles--2I8DW\"
data-ui=\"job-workplace\">Remote</span><div class=\"styles--1Sarc
undefined styles--Xn8hR\" data-ui=\"job-location\"></div><span
class=\"\" data-ui=\"job-department\"
id=\"DB4D7C0EC8_department\">Product</span><span class=\"\"
data-ui=\"job-type\">Full time</span></li><li class=\"styles--1vo9F\"
data-id=\"F88446C814\" data-ui=\"job\" role=\"listitem\"><a
aria-labelledby=\"F88446C814_title F88446C814_posted_on
F88446C814_department\" class=\"styles--1OnOt\" href=\"/huggingfa<3632
chars omitted>d=\"19A136F8E2_department\">Open Source</span><span
class=\"\" data-ui=\"job-type\">Full time</span></li><li
class=\"styles--1vo9F\" data-id=\"0BD8C06DB3\" data-ui=\"job\"
role=\"listitem\"><a aria-labelledby=\"0BD8C06DB3_title
0BD8C06DB3_posted_on 0BD8C06DB3_department 0BD8C06DB3_locations\"
class=\"styles--1OnOt\"
href=\"/huggingface/j/0BD8C06DB3/\"></a><div><h3
class=\"styles--3TJHk\" data-ui=\"job-title\"
id=\"0BD8C06DB3_title\"><span>Wild Card</span></h3></div><span
class=\"styles--QTMDv styles--2TdGW styles--2I8DW\"
data-ui=\"job-workplace\">Remote</span><div class=\"styles--1Sarc
styles--Xn8hR\" data-ui=\"job-location\"
id=\"0BD8C06DB3_locations\"><div class=\"styles--11q6G\"
data-ui=\"job-location-tooltip\"><span
data-ellipsis-element=\"true\"><span class=\"styles--QTMDv
styles--2TdGW\">United States</span></span></div></div><span
class=\"\" data-ui=\"job-department\"
id=\"0BD8C06DB3_department\">Wild Card</span><span class=\"\"
data-ui=\"job-type\">Full time</span></li></ul>"]
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
2026-09-28 12:43:08  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 43616, "visible_chars": 4539,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 12:43:08  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://apply.workable.com/huggingface", "text": " Job
OpeningsIf you're interested in joining us, but don't tick every box,
we still encourage you to apply! We're building a diverse team whose
skills, experiences, and background complement one another. \n\nHot
tip: unclick your automatically detected location below to see all
available jobs as you can apply to them from any location!\nJob
Openings8 jobsWorkplace typeLocationWork typeUnited StatesDismiss
United StatesClear filters We’ve detected your location and are
showing jobs in United States. Clear the filters to display jobs in
all locations. Senior Open-Source Python Engineer, ML Developer Tools
- EMEA RemoteRemoteProductFull timeSenior Open-Source Python Engineer,
ML Developer Tools - US RemoteRemoteProductFull timeSenior Machine
Learning Engineer, Voice Agents - EMEA RemoteRemoteScienceFull
timeLow-Level Senior Software Engineer, Xet Storage - US
RemoteRemoteProductFull timeLow-level Senior Software Engineer,
Xe<511303 chars omitted>um=feature&amp;utm_source=careers_page\"
rel=\"noreferrer\"
target=\"_blank\">Workable</a></span></div></footer></div></div><iframe
height=\"1\" width=\"1\" style=\"position: absolute; top: 0px; left:
0px; border: medium; visibility: hidden;\"></iframe><noscript><iframe
height=\"0\" width=\"0\" style=\"display: none; visibility: hidden;\"
src=\"https://www.googletagmanager.com/ns.html?id=GTM-WKS7WTT&amp;gtm_auth=SGnzIn3pcB7S4fevFXOKPQ&amp;gtm_preview=env-2&amp;gtm_cookies_win=x\"></iframe></noscript><iframe
id=\"_hjSafeContext_97137555\" title=\"_hjSafeContext\"
tabindex=\"-1\" aria-hidden=\"true\" src=\"about:blank\"
style=\"display: none !important; width: 1px !important; height: 1px
!important; opacity: 0 !important; pointer-events: none
!important;\"></iframe></body>", "scrape_meta": {"bot_blocked": false,
"cookies_dismissed": true, "issues": [], "content_chars": 4539,
"requested_url": "https://apply.workable.com/huggingface",
"final_url": "https://apply.workable.com/huggingface"}}
2026-09-28 12:43:08  [INFO]  3cf0016a | telescope job done:
https://apply.workable.com/huggingface ->
https://apply.workable.com/huggingface fields:text,html
2026-09-28 12:43:08  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 12:43:08  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-437b325288c0c8d7"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 12:43:08  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=cmu_wd5_myworkdayjobs_com, n=4]
2026-09-28 12:43:08  [DEBUG]  3243: Calling agent.do_task
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
2026-09-28 12:43:08  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=cmu_wd5_myworkdayjobs_com
2026-09-28 12:43:08  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Technical Site Lead  - SEI Customer
Site - Fort Meade, MD", "Senior Solutions Engineer", "Solutions
Engineer", "Technical Engagement Lead", "Executive Assistant to the
Chief Financial Officer", "Software Engineer", "Senior Real-Time
Embedded Software Engineer", "Senior Embedded Software Engineer",
"Real-Time Embedded Software Engineer", "IT Support Associate"]
containers=["<ul aria-label=\"Page 1 of 3\" role=\"list\"><li
class=\"css-1q2dra3\"><div class=\"css-qiqmbt\"><div
class=\"css-b3pn3b\"><div class=\"css-b3pn3b\"><h3><a
aria-current=\"false\" class=\"css-19uc56f\"
data-automation-id=\"jobTitle\" data-uxi-element-id=\"jobItem\"
data-uxi-item-rank=\"0\" data-uxi-query-id=\"\"
data-uxi-widget-type=\"heading\"
href=\"/en-US/SEI/job/Linthicum/Technical-Site-Lead----SEI-Customer-Site---Fort-Meade--MD_2025134\">Technical
Site Lead  - SEI Customer Site - Fort Meade,
MD</a></h3></div></div></div><div class=\"css-248241\"><div
class=\"css-1y87fhn\"><div class=\"css-k008qs\"
data-automation-id=\"locations\">locationsLinthicum</div></div></div><div
class=\"css-zoser8\"><div class=\"css-1y87fhn\"><div
class=\"css-k008qs\" data-automation-id=\"postedOn\">posted onPosted 4
Days Ago</div></div></div><ul class=\"css-14a0imc\"
data-automation-id=\"subtitle\"><li
class=\"css-h2nt8k\">2025134</li></ul></li><li
class=\"css-1q2dra3\"><div class=\"css-qiqmbt\"><div cla<15141 chars
omitted>"postedOn\">posted onPosted 30+ Days Ago</div></div></div><ul
class=\"css-14a0imc\" data-automation-id=\"subtitle\"><li
class=\"css-h2nt8k\">2024322</li></ul></li><li
class=\"css-1q2dra3\"><div class=\"css-qiqmbt\"><div
class=\"css-b3pn3b\"><div class=\"css-b3pn3b\"><h3><a
aria-current=\"false\" class=\"css-19uc56f\"
data-automation-id=\"jobTitle\" data-uxi-element-id=\"jobItem\"
data-uxi-item-rank=\"19\" data-uxi-query-id=\"\"
data-uxi-widget-type=\"heading\"
href=\"/en-US/SEI/job/Pittsburgh-PA/AI-Red-Team-Engineer_2025000-1\">AI
Red Team Engineer</a></h3></div></div></div><div
class=\"css-248241\"><div class=\"css-1y87fhn\"><div
class=\"css-k008qs\" data-automation-id=\"locations\">locations2
Locations</div></div></div><div class=\"css-zoser8\"><div
class=\"css-1y87fhn\"><div class=\"css-k008qs\"
data-automation-id=\"postedOn\">posted onPosted 30+ Days
Ago</div></div></div><ul class=\"css-14a0imc\"
data-automation-id=\"subtitle\"><li
class=\"css-h2nt8k\">2025000</li></ul></li></ul>"]
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
2026-09-28 12:43:08  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 33847, "visible_chars": 2001,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 12:43:09  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 54631, "visible_chars": 3184439,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 12:43:09  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://jobs.volvogroup.com/?locale=en_US", "text":
"\n\n        \n\n    \n        \n        \n            \n
  \n                    \n    \n    \n        \n
Volvo Group JobsTogether we shape the world we want to live in\n\n
   \n    \n\n    \n        \n\t\n\t361555\n\n\t\n\t15\n\n\t\n\ten_US,
fr_FR, es_MX, pt_BR, de_DE, it_IT, nl_NL, pl_PL, sv_SE, fi_FI, cs_CZ,
nb_NO, zh_CN, ko_KR\n\n\t\n\tView More\n\n\t\n\tYour search did not
match any jobs. Try adjusting the filters.\n\n\t\n\tShow
filters\n\tClose filters\n\n\t\n\t\n\t\t\n\t\t\tEnter job title or
keyword\n\t\t\n\t\t\n\t\t\tJob
Category\n\t\t\n\t\t\n\t\t\tLocation\n\t\t\n\t\t\n\t\t\tOrganization\n\t\t\n\t\t\n\t\t\tPosition
Type\n\t\t\n\t\n\n\t\n\t\n\t\t\n\t\t\tAvailable Jobs
\n\t\t\n\t\t\n\t\t\tJob
Category\n\t\t\n\t\t\n\t\t\tOrganization\n\t\t\n\t\t\n\t\t\tLocation\n
                       3\n\t\t\tShow More\n\t\t\n\t\t\n\t\t\tPosition
Type\n\t\t\n\t\t\n\t\t\tPosted\n\t\t\n\t\t\n\<7490512 chars
omitted>2000/svg\"><g id=\"Page-1\" stroke=\"none\" stroke-width=\"1\"
fill=\"none\" fill-rule=\"evenodd\"><g id=\"Banner_02\"
class=\"ot-floating-button__svg-fill\"
transform=\"translate(-318.000000, -725.000000)\" fill=\"#292B2E\"
fill-rule=\"nonzero\"><g id=\"Group-2\"
transform=\"translate(305.000000, 712.000000)\"><g
id=\"icon/16px/white/close\"><polygon id=\"Line1\" points=\"13.3333333
14.9176256 35.0823744 36.6666667 36.6666667 35.0823744 14.9176256
13.3333333\"></polygon><polygon id=\"Line2\"
transform=\"translate(25.000000, 25.000000) scale(-1, 1)
translate(-25.000000, -25.000000) \" points=\"13.3333333 14.9176256
35.0823744 36.6666667 36.6666667 35.0823744 14.9176256
13.3333333\"></polygon></g></g></g></g></svg></button></div></div></div></body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 3184439, "requested_url":
"https://www.volvogroup.com/en/careers/job-openings.html",
"final_url": "https://jobs.volvogroup.com/?locale=en_US"}}
2026-09-28 12:43:09  [INFO]  9b32c3cc | telescope job done:
https://www.volvogroup.com/en/careers/job-openings.html ->
https://jobs.volvogroup.com/?locale=en_US fields:text,html
2026-09-28 12:43:09  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 12:43:09  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-fc8a15bdf6b74718"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 12:43:09  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=oxfordhealthbrc_nihr_ac_uk, n=4]
2026-09-28 12:43:09  [DEBUG]  3243: Calling agent.do_task
live_content: <div aria-label="Cookie preferences." aria-live="polite"
id="ccc" role="region"><div id="ccc-overlay"></div><div
aria-labelledby="ccc-title" aria-modal="true"
class="ccc-module--slideout ccc-module--right" id="ccc-module"
role="dialog"><div class="ccc-content--dark" id="ccc-content"><div
class="ccc-panel" id="cc-panel"><h1 id="ccc-title">This site uses
cookies</h1><p class="ccc-intro">Some cookies are essential for
security, while others help us to improve your experience by providing
insights into how the site is being used. </p><div
id="ccc-statement"><p><span class="ccc-statement-description">For more
information, see our </span><a class="ccc-link ccc-tabbable"
href="https://oxfordhealthbrc.nihr.ac.uk/data-control/" rel="noopener"
target="_blank"><span class="ccc-statement-name">Data Control and
Privacy Statement</span><span class="ccc-svg-element"><span
class="ccc-sr-only">(Opens in a new
window)</span></span></a></p></div><div
id="ccc-button-holder"><span>Accept Recommended</span><25116 chars
omitted>d="text-5"><div class="widget-wrap"> <div
class="textwidget"><div>The <a data-external-handled="true"
href="https://www.nihr.ac.uk/" rel="noopener" target="_blank">National
Institute for Health and Care Research (NIHR)</a> Biomedical Research
Centre (BRC) is a partnership between Oxford Health NHS Foundation
Trust and the University of Oxford.  We are part of the Oxford
Academic Health Partners.</div>
</div>
</div></section>
<section class="widget widget_sp_image" id="widget_sp_image-4"><div
class="widget-wrap"><a class="widget_sp_image-image-link"
data-external-handled="true" href="https://www.oahp.org.uk/"
target="_blank"><img alt="Oxford Academic Health Partners"
class="attachment-full"/></a></div></section>
</div></div></div><div class="wrap"><p>© 2026 NIHR Biomedical Research
Centre: Oxford Health  · <a
href="https://oxfordhealthbrc.nihr.ac.uk/wp-login.php">Log
in</a></p></div></div>

















<div class="ps2id-dummy-offset-wrapper"><div
id="ps2id-dummy-offset"></div></div>
2026-09-28 12:43:09  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=oxfordhealthbrc_nihr_ac_uk
2026-09-28 12:43:09  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Alzheimer’s Society UKDTN Research
Nurse"] containers=["<div aria-label=\"Cookie preferences.\"
aria-live=\"polite\" id=\"ccc\" role=\"region\"><div
id=\"ccc-overlay\"></div><div aria-labelledby=\"ccc-title\"
aria-modal=\"true\" class=\"ccc-module--slideout ccc-module--right\"
id=\"ccc-module\" role=\"dialog\"><div class=\"ccc-content--dark\"
id=\"ccc-content\"><div class=\"ccc-panel\" id=\"cc-panel\"><h1
id=\"ccc-title\">This site uses cookies</h1><p
class=\"ccc-intro\">Some cookies are essential for security, while
others help us to improve your experience by providing insights into
how the site is being used. </p><div id=\"ccc-statement\"><p><span
class=\"ccc-statement-description\">For more information, see our
</span><a class=\"ccc-link ccc-tabbable\"
href=\"https://oxfordhealthbrc.nihr.ac.uk/data-control/\"
rel=\"noopener\" target=\"_blank\"><span
class=\"ccc-statement-name\">Data Control and Privacy
Statement</span><span class=\"ccc-svg-element\"><span
class=\"ccc-sr-only\">(Opens in a new
window)</span></span></a></p></div><div id<26462 chars
omitted>\"><div>The <a data-external-handled=\"true\"
href=\"https://www.nihr.ac.uk/\" rel=\"noopener\"
target=\"_blank\">National Institute for Health and Care Research
(NIHR)</a> Biomedical Research Centre (BRC) is a partnership between
Oxford Health NHS Foundation Trust and the University of Oxford.  We
are part of the Oxford Academic Health
Partners.</div>\n</div>\n</div></section>\n<section class=\"widget
widget_sp_image\" id=\"widget_sp_image-4\"><div
class=\"widget-wrap\"><a class=\"widget_sp_image-image-link\"
data-external-handled=\"true\" href=\"https://www.oahp.org.uk/\"
target=\"_blank\"><img alt=\"Oxford Academic Health Partners\"
class=\"attachment-full\"/></a></div></section>\n</div></div></div><div
class=\"wrap\"><p>© 2026 NIHR Biomedical Research Centre: Oxford
Health  · <a href=\"https://oxfordhealthbrc.nihr.ac.uk/wp-login.php\">Log
in</a></p></div></div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n<div
class=\"ps2id-dummy-offset-wrapper\"><div
id=\"ps2id-dummy-offset\"></div></div>"] cull_outcome='full_dom'
dom_joined=<div aria-label="Cookie preferences." aria-live="polite"
id="ccc" role="region"><div id="ccc-overlay"></div><div
aria-labelledby="ccc-title" aria-modal="true"
class="ccc-module--slideout ccc-module--right" id="ccc-module"
role="dialog"><div class="ccc-content--dark" id="ccc-content"><div
class="ccc-panel" id="cc-panel"><h1 id="ccc-title">This site uses
cookies</h1><p class="ccc-intro">Some cookies are essential for
security, while others help us to improve your experience by providing
insights into how the site is being used. </p><div
id="ccc-statement"><p><span class="ccc-statement-description">For more
information, see our </span><a class="ccc-link ccc-tabbable"
href="https://oxfordhealthbrc.nihr.ac.uk/data-control/" rel="noopener"
target="_blank"><span class="ccc-statement-name">Data Control and
Privacy Statement</span><span class="ccc-svg-element"><span
class="ccc-sr-only">(Opens in a new
window)</span></span></a></p></div><div
id="ccc-button-holder"><span>Accept Recommended</span><25116 chars
omitted>d="text-5"><div class="widget-wrap"> <div
class="textwidget"><div>The <a data-external-handled="true"
href="https://www.nihr.ac.uk/" rel="noopener" target="_blank">National
Institute for Health and Care Research (NIHR)</a> Biomedical Research
Centre (BRC) is a partnership between Oxford Health NHS Foundation
Trust and the University of Oxford.  We are part of the Oxford
Academic Health Partners.</div>
</div>
</div></section>
<section class="widget widget_sp_image" id="widget_sp_image-4"><div
class="widget-wrap"><a class="widget_sp_image-image-link"
data-external-handled="true" href="https://www.oahp.org.uk/"
target="_blank"><img alt="Oxford Academic Health Partners"
class="attachment-full"/></a></div></section>
</div></div></div><div class="wrap"><p>© 2026 NIHR Biomedical Research
Centre: Oxford Health  · <a
href="https://oxfordhealthbrc.nihr.ac.uk/wp-login.php">Log
in</a></p></div></div>

















<div class="ps2id-dummy-offset-wrapper"><div
id="ps2id-dummy-offset"></div></div>
2026-09-28 12:43:09  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 52897, "visible_chars": 2625,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 12:43:09  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/",
"text": "This site uses cookiesSome cookies are essential for
security, while others help us to improve your experience by providing
insights into how the site is being used. For more information, see
our Data Control and Privacy Statement(Opens in a new window)Accept
RecommendedRejectNecessary CookiesNecessary cookies enable core
functionality. The website cannot function properly without these
cookies, and they can only be disabled by changing your browser
preferences.Google AnalyticsUsed to gather anonymous session data such
as device, browser, time on pageGoogle_AnalyticsYouTube AnalyticsUsed
by YouTube to track user interaction with embedded videosYouTubeAbout
this tool(Opens in a new window) Skip to primary navigation Skip to
main content Skip to primary sidebar Skip to footer\n\n\n\n    \n
      About\n\n    \n\n\n\n\nYou are here: Home / About /
Vacancies\nWe are keen to recruit talented and committed <69376 chars
omitted>           },\n
                                    ],\n
                                 statement: {\n
    description: 'For more information, see our',\n
        name: 'Data Control and Privacy Statement',\n
          url: 'https://oxfordhealthbrc.nihr.ac.uk/data-control/',\n
                         updated: '01/10/2025'\n
 },\n                                        sameSiteCookie: true,\n
                 sameSiteValue: 'Strict',\n
notifyDismissButton: true\n                };\n
CookieControl.load(config);\n            </script>\n\n\n</body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 2625, "requested_url":
"https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies", "final_url":
"https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/"}}
2026-09-28 12:43:09  [INFO]  7c3f7498 | telescope job done:
https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies ->
https://oxfordhealthbrc.nihr.ac.uk/about-us/vacancies/
fields:text,html
2026-09-28 12:43:09  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 12:43:09  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-7fbf699182bceabf"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 12:43:09  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=training_nih_gov, n=4]
2026-09-28 12:43:09  [DEBUG]  3243: Calling agent.do_task
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
2026-09-28 12:43:09  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=training_nih_gov
2026-09-28 12:43:09  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Staff Scientist I", "Deputy Director,
Division of Extramural Research", "Staff Clinician", "Administrative
Technician", "Biologist Scientist Administrator (Scientific Review
Officer)", "Health Scientist Administrator (Program Officer)", "Lead
Nuclear Medicine Technologist", "Mechanical Engineer", "Royalties
Analyst", "Supervisory Data Scientist"] containers=["<ul
class=\"usa-collection\">\n<li class=\"usa-collection__item\">\n<div
class=\"usa-collection__body\">\n<h2
class=\"usa-collection__heading\"><a
href=\"/careers/open-positions/job-02329d15-c2fe-4255-bf46-043a4e794e51\"><span
class=\"usa-sr-only\">Read more about the </span>Staff Scientist I
<span class=\"usa-sr-only\"> job</span></a></h2>\n<div
class=\"usa-collection__description\">\n<ul class=\"details-list
details-list--inline\">\n<li class=\"details-list__item\">\n<h3
class=\"details-list__label\">Open:</h3>\n          09/18/2026\n
 </li>\n<li class=\"details-list__item\">\n<h3
class=\"details-list__label\">Category:</h3>\n          Scientific\n
     </li>\n<li class=\"details-list__item\">\n<h3
class=\"details-list__label\">Location:</h3>\n
       Durham, North Carolina\n                  </li>\n<li
class=\"details-list__item\">\n<h3
class=\"details-list__label\">Institute or Center:</h3>\n
NIEHS (National Institute of Environmental Heal<22613 chars
omitted>\n<div class=\"usa-collection__description\">\n<ul
class=\"details-list details-list--inline\">\n<li
class=\"details-list__item\">\n<h3
class=\"details-list__label\">Open:</h3>\n          09/24/2026 –
09/30/2026\n        </li>\n<li class=\"details-list__item\">\n<h3
class=\"details-list__label\">Category:</h3>\n          Fire
Protection and Prevention\n        </li>\n<li
class=\"details-list__item\">\n<h3
class=\"details-list__label\">Location:</h3>\n
       Montgomery County, Maryland\n                  </li>\n<li
class=\"details-list__item\">\n<h3
class=\"details-list__label\">Institute or Center:</h3>\n
        OD (Office of the Director)\n                </li>\n<li
class=\"details-list__item\">\n<h3
class=\"details-list__label\">Hiring Path:</h3>\n<span
class=\"usa-tooltip\"><img alt=\"Internal to an agency - appears on
USAJOBS\" class=\"details-list__inline-group-item
usa-tooltip__trigger\"/></span>\n</li>\n</ul>\n</div>\n</div>\n</li>\n</ul>"]
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
2026-09-28 12:43:09  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 45722, "visible_chars": 20128,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 12:43:09  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://hr.nih.gov/careers/open-positions", "text":
"\nSkip to main content\n\n\n\n\n  \n    \n      \n    \n        \n\n
      \n    \n\n\n  \n\n\n        \n    \n  \n\n  \n  \n\n  \n      \n
     \n        \n  \n    \n          \n\n  \n\n      \n    \n  \n  \n
    \n  \n    \n    \n                          \n\n  \n      \n
       \n                          \n                          \n
  \n        \n        \n          New Employees\n                  \n
            \n                          \n                          \n
       \n        \n        \n          Former Employees\n
    \n              \n                          \n
     \n        \n        \n        \n          Staff Resources\n
           \n              \n                          \n
            \n        \n                          \n        \n
 Careers\n                        \n      \n              \n
          <121510 chars omitted>m; visibility:
hidden;\"></iframe><script type=\"module\"
src=\"https://static.cloudflareinsights.com/beacon.min.js/v31edd6df95cf4e85bb4c19e7a9bdbcba1788362987495\"
integrity=\"sha512-iIg7k2xntmwu6/uSb5tpc/hySgZc4eoL31yB29W6tJFo2akwjPWcEqnCEdJvGexCL0KEQwVYv5BlowfhVz26hg==\"
data-cf-beacon=\"{&quot;version&quot;:&quot;2024.11.0&quot;,&quot;token&quot;:&quot;4da10bb88a2f4316a9de363d388a5456&quot;,&quot;spa&quot;:2}\"
crossorigin=\"anonymous\"></script>\n\n\n<div
id=\"drupal-live-announce\" class=\"visually-hidden\"
aria-live=\"polite\" aria-busy=\"false\"></div><script
id=\"_fed_an_ua_tag\" text=\"\" charset=\"\" type=\"text/javascript\"
src=\"https://dap.digitalgov.gov/Universal-Federated-Analytics-Min.js?agency=HHS&amp;subagency=NIH&amp;sp=keys\"></script></body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 20128, "requested_url":
"https://hr.nih.gov/careers/open-positions", "final_url":
"https://hr.nih.gov/careers/open-positions"}}
2026-09-28 12:43:09  [INFO]  4da6ab15 | telescope job done:
https://hr.nih.gov/careers/open-positions ->
https://hr.nih.gov/careers/open-positions fields:text,html
2026-09-28 12:43:09  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 12:43:09  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-1c15584876be8d97"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 12:43:09  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=huggingface_co, n=4]
2026-09-28 14:49:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=pesi_com, n=4]
2026-09-28 14:49:56  [DEBUG]  3243: Calling agent.do_task
live_content: <div class="accordion"
id="ac03ab4555-b533-4256-a3ec-c309d42ea6d0">
<div class="accordion-item">
<h2 class="accordion-header"
id="ac4b13863a-e58d-4987-adc3-006c978d3aaaHeadline">

                                        Brand Manager (remote or in-office)

</h2>
<div aria-labelledby="ac4b13863a-e58d-4987-adc3-006c978d3aaaHeadline"
class="accordion-collapse collapse"
id="ac4b13863a-e58d-4987-adc3-006c978d3aaaContent" role="region">
<div class="accordion-body">
<p>Who We’re Looking for:</p>
<p>We’re growing fast and we’re looking for a Brand Manager who thinks
like an entrepreneur and thrives on turning ideas into revenue. This
isn’t just about running campaigns—it’s about becoming THE marketer
for one of our brands. From affiliates and partnerships to email,
social, and PPC, you’ll be collaborating with a passionate team to
drive growth across every channel.</p>
<p>You should be obsessed with crafting offers that convert, love
testing and scaling what<62332 chars omitted>t-switching</li>
<li>People who get flustered when priorities shift mid-day</li>
<li>People who would rather build the app than talk to the people using it</li>
<li>People who need a fully defined process before they can act</li>
<li>People who are uncomfortable saying “I don’t know yet” while they
find out</li>
</ul>
<p>Candidates must be able to provide proof of eligibility to work in
the United States following an offer of employment.</p>
<p>Please email your resume to <a aria-label="Link careers@pesi.com."
class="fui-Link ___1q1shib f2hkw1w f3rmtva f1ewtqcl fyind8e f1k6fduh
f1w7gpdv fk6fouc fjoy568 figsok6 f1s184ao f1mk8lai fnbmjn9 f1o700av
f13mvf36 f1cmlufx f9n3di6 f1ids18y f1tx3yz7 f1deo86v f1eh06m1 f1iescvh
fhgqx19 f1olyrje f1p93eir f1nev41a f1h8hb77 f1lqvz6u f10aw75t fsle3fq
f17ae5zn" href="mailto:careers@pesi.com" id="menur5c5" rel="noreferrer
noopener" target="_blank" title="mailto:careers@pesi.com (Opens in a
new window)">careers@pesi.com.</a></p>
</div>
</div>
</div>
</div>
2026-09-28 14:49:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=pesi_com
2026-09-28 14:49:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Brand Manager (remote or in-office)",
"Business Development Manager", "CE Accreditation Advisor – Licensed
Counselor", "CE Accreditation Advisor – Licensed Psychologist",
"Customer Success Specialist", "Direct Response Copywriter", "Email
Marketing Strategist", "Lead Software Engineer", "Product
Administration Specialist", "Social Media Strategist (Remote or
Hybrid)"] containers=["<div class=\"accordion\"
id=\"ac03ab4555-b533-4256-a3ec-c309d42ea6d0\">\n<div
class=\"accordion-item\">\n<h2 class=\"accordion-header\"
id=\"ac4b13863a-e58d-4987-adc3-006c978d3aaaHeadline\">\n\n
                           Brand Manager (remote or in-office)\n
                             \n</h2>\n<div
aria-labelledby=\"ac4b13863a-e58d-4987-adc3-006c978d3aaaHeadline\"
class=\"accordion-collapse collapse\"
id=\"ac4b13863a-e58d-4987-adc3-006c978d3aaaContent\"
role=\"region\">\n<div class=\"accordion-body\">\n<p>Who We’re Looking
for:</p>\n<p>We’re growing fast and we’re looking for a Brand Manager
who thinks like an entrepreneur and thrives on turning ideas into
revenue. This isn’t just about running campaigns—it’s about becoming
THE marketer for one of our brands. From affiliates and partnerships
to email, social, and PPC, you’ll be collaborating with a passionate
team to drive growth across every channel.</p>\n<p>You should be
obsessed with crafting offers that conve<63695 chars omitted>e who get
flustered when priorities shift mid-day</li>\n<li>People who would
rather build the app than talk to the people using it</li>\n<li>People
who need a fully defined process before they can act</li>\n<li>People
who are uncomfortable saying “I don’t know yet” while they find
out</li>\n</ul>\n<p>Candidates must be able to provide proof of
eligibility to work in the United States following an offer of
employment.</p>\n<p>Please email your resume to <a aria-label=\"Link
careers@pesi.com.\" class=\"fui-Link ___1q1shib f2hkw1w f3rmtva
f1ewtqcl fyind8e f1k6fduh f1w7gpdv fk6fouc fjoy568 figsok6 f1s184ao
f1mk8lai fnbmjn9 f1o700av f13mvf36 f1cmlufx f9n3di6 f1ids18y f1tx3yz7
f1deo86v f1eh06m1 f1iescvh fhgqx19 f1olyrje f1p93eir f1nev41a f1h8hb77
f1lqvz6u f10aw75t fsle3fq f17ae5zn\" href=\"mailto:careers@pesi.com\"
id=\"menur5c5\" rel=\"noreferrer noopener\" target=\"_blank\"
title=\"mailto:careers@pesi.com (Opens in a new
window)\">careers@pesi.com.</a></p>\n</div>\n</div>\n</div>\n</div>"]
cull_outcome='culled' dom_joined=<div class="accordion"
id="ac03ab4555-b533-4256-a3ec-c309d42ea6d0">
<div class="accordion-item">
<h2 class="accordion-header"
id="ac4b13863a-e58d-4987-adc3-006c978d3aaaHeadline">

                                        Brand Manager (remote or in-office)

</h2>
<div aria-labelledby="ac4b13863a-e58d-4987-adc3-006c978d3aaaHeadline"
class="accordion-collapse collapse"
id="ac4b13863a-e58d-4987-adc3-006c978d3aaaContent" role="region">
<div class="accordion-body">
<p>Who We’re Looking for:</p>
<p>We’re growing fast and we’re looking for a Brand Manager who thinks
like an entrepreneur and thrives on turning ideas into revenue. This
isn’t just about running campaigns—it’s about becoming THE marketer
for one of our brands. From affiliates and partnerships to email,
social, and PPC, you’ll be collaborating with a passionate team to
drive growth across every channel.</p>
<p>You should be obsessed with crafting offers that convert, love
testing and scaling what<62332 chars omitted>t-switching</li>
<li>People who get flustered when priorities shift mid-day</li>
<li>People who would rather build the app than talk to the people using it</li>
<li>People who need a fully defined process before they can act</li>
<li>People who are uncomfortable saying “I don’t know yet” while they
find out</li>
</ul>
<p>Candidates must be able to provide proof of eligibility to work in
the United States following an offer of employment.</p>
<p>Please email your resume to <a aria-label="Link careers@pesi.com."
class="fui-Link ___1q1shib f2hkw1w f3rmtva f1ewtqcl fyind8e f1k6fduh
f1w7gpdv fk6fouc fjoy568 figsok6 f1s184ao f1mk8lai fnbmjn9 f1o700av
f13mvf36 f1cmlufx f9n3di6 f1ids18y f1tx3yz7 f1deo86v f1eh06m1 f1iescvh
fhgqx19 f1olyrje f1p93eir f1nev41a f1h8hb77 f1lqvz6u f10aw75t fsle3fq
f17ae5zn" href="mailto:careers@pesi.com" id="menur5c5" rel="noreferrer
noopener" target="_blank" title="mailto:careers@pesi.com (Opens in a
new window)">careers@pesi.com.</a></p>
</div>
</div>
</div>
</div>
2026-09-28 14:49:56  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7779384, "visible_chars": 65212,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:49:56  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://www.pesi.com/careers/", "text": "
This website uses cookies and tracking technologies to improve user
experience and analyze performance. These may record your activities
(such as content or products considered or purchased) and share the
data with third-party providers, including advertising, and analytics
partners. You can manage your preferences at any time.  For more
information:     Cookie Notice       Settings
\n    \n\n\n    \n    \n    \n        \n            Skip to main
content\n        \n        \n            \n        \n    \n\n     \n\n
   \n             \n                \n                    \n
             \n                            \n
          Attending the FREE Mindfulness program today? CLICK HERE to
register or for login information. \n
  \n                            \n                        \n
         \n                \n   <243954 chars
omitted>amp;tl=Careers%20%7C%20PESI&amp;p=https%3A%2F%2Fwww.pesi.com%2Fcareers%2F&amp;r=&amp;lt=9561&amp;evt=pageLoad&amp;sv=2&amp;cdb=AQAS&amp;rn=915784\"></div><div
id=\"om-jmo70ob2xkuxkqticufy-holder\"></div><div
id=\"om-n9eh7no17yga96z45s8r-holder\"></div><div
id=\"om-xrr1ashl88bgnn1bfnxv-holder\"></div><div
id=\"om-u4zwwzfhhfqgguhoc8ph-holder\"></div><div
id=\"om-xfqrtn4xg8dgyucxysdw-holder\"></div><div
id=\"om-xlmatfcchcurt39fmtse-holder\"></div><div
id=\"om-gp88ionakzqt3sxcxncp-holder\"></div><div
id=\"om-v0da9ub233xuo3jd5p6k-holder\"></div><div
id=\"om-ne8ctz9qrfuhgamehnxd-holder\"></div><div
id=\"om-t76s0izcyiqkcq3r34ih-holder\"></div><div
id=\"om-ujmxo90zawbwxhrg8ot8-holder\"></div><div
id=\"om-i7qk6it8mfzyotu7h7vd-holder\"></div><div
id=\"om-sqm4wnykwwc2bwj8zkx7-holder\"></div></body>", "scrape_meta":
{"bot_blocked": false, "cookies_dismissed": false, "issues": [],
"content_chars": 65212, "requested_url":
"https://www.pesi.com/careers", "final_url":
"https://www.pesi.com/careers/"}}
2026-09-28 14:49:56  [INFO]  cb9d71ac | telescope job done:
https://www.pesi.com/careers -> https://www.pesi.com/careers/
fields:text,html
2026-09-28 14:49:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:49:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-ec596d381ac4ed8c"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:49:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=reviveresearch_org, n=4]
2026-09-28 14:49:56  [DEBUG]  3243: Calling agent.do_task
live_content: <div class="list-view"><div class="list-data"><div
class="v1 sjb-job-7311"><div class="row"><div class="col-md-1 col-sm-2
hidden-xs"><div class="company-logo">
<a href="https://reviveresearch.org/jobs/clinical-research-coordinator/"><img
alt="Revive Research Institute, Inc." class="sjb-img-responsive
entered litespeed-loaded"/></a></div></div><div class="col-md-11
col-sm-12"><div class="row sjb-list-row"><div class="col-md-5
col-sm-12"><div class="job-info"><h4>
<a href="https://reviveresearch.org/jobs/clinical-research-coordinator/">
<span class="job-title">Clinical Research Coordinator</span> | <span
class="company-name">Revive Research Institute, Inc.</span>
</a></h4></div></div><div class="col-md-2 col-sm-4 col-xs-12"><div
class="job-type">Full Time</div></div><div class="col-md-2 col-sm-4
col-xs-12"><div class="job-location">Farmington Hills, MI, Michigan,
Southfield, MI, Troy</div></div><div class="col-md-3 col-sm-4
col-xs-12"><div class="job-date">Posted 3 years ago</div></div><<23287
chars omitted>om">zsuhrawardy@rev-research.com</a> .<a
href="https://www.reviveresearch.org/job-location/southfield-mi/">Southfield
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
href="https://reviveresearch.org/jobs/research-intern/">Read
More</a></p><div class="sjb-view-less-btn"
id="sjb_view_less_btn_7319"><a class="sjb_view_less_btn
sjb_view_more_btn" data-id="7319">View
less</a></div></div></div></div></div><div
class="clearfix"></div></div>
2026-09-28 14:49:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=reviveresearch_org
2026-09-28 14:49:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["CLINICAL RESEARCH COORDINATOR",
"Research Regulatory Coordinator", "Clinical Research Medical
Assistant", "MEDICAL ADMINISTRATIVE ASSISTANT", "Research Intern"]
containers=["<div class=\"list-view\"><div class=\"list-data\"><div
class=\"v1 sjb-job-7311\"><div class=\"row\"><div class=\"col-md-1
col-sm-2 hidden-xs\"><div class=\"company-logo\">\n<a
href=\"https://reviveresearch.org/jobs/clinical-research-coordinator/\"><img
alt=\"Revive Research Institute, Inc.\" class=\"sjb-img-responsive
entered litespeed-loaded\"/></a></div></div><div class=\"col-md-11
col-sm-12\"><div class=\"row sjb-list-row\"><div class=\"col-md-5
col-sm-12\"><div class=\"job-info\"><h4>\n<a
href=\"https://reviveresearch.org/jobs/clinical-research-coordinator/\">\n<span
class=\"job-title\">Clinical Research Coordinator</span> | <span
class=\"company-name\">Revive Research Institute, Inc.</span>
</a></h4></div></div><div class=\"col-md-2 col-sm-4 col-xs-12\"><div
class=\"job-type\">Full Time</div></div><div class=\"col-md-2 col-sm-4
col-xs-12\"><div class=\"job-location\">Farmington Hills, MI,
Michigan, Southfield, MI, Troy</div></div><div class=\"col-md-3
col-sm-4 col-xs-12\"><div c<23816 chars omitted><a
href=\"https://www.reviveresearch.org/job-location/southfield-mi/\">Southfield
Jobs</a><div class=\"job-features\"><h3>Job Features</h3><table
class=\"table\"><tr><td>Job
Category</td><td>Intern</td></tr></table></div><div
class=\"clearfix\"></div></div><div class=\"job-description\"><div
id=\"sjb_less_content_7319\"><p>Are you looking for an unpaid or paid
internship? Revive Research Institute is looking for college students
for a three month internship opportunity located in Southfield, MI.
Interns will have...</p></div><div
class=\"sjb-apply-now-btn\"><p></p><p><a class=\"btn btn-primary\"
href=\"javascript:void(0)\" id=\"quick-apply-btn\"
job_id=\"7319\">Quick Apply </a><a class=\"btn btn-primary\"
href=\"https://reviveresearch.org/jobs/research-intern/\">Read
More</a></p><div class=\"sjb-view-less-btn\"
id=\"sjb_view_less_btn_7319\"><a class=\"sjb_view_less_btn
sjb_view_more_btn\" data-id=\"7319\">View
less</a></div></div></div></div></div><div
class=\"clearfix\"></div></div>"] cull_outcome='culled'
dom_joined=<div class="list-view"><div class="list-data"><div
class="v1 sjb-job-7311"><div class="row"><div class="col-md-1 col-sm-2
hidden-xs"><div class="company-logo">
<a href="https://reviveresearch.org/jobs/clinical-research-coordinator/"><img
alt="Revive Research Institute, Inc." class="sjb-img-responsive
entered litespeed-loaded"/></a></div></div><div class="col-md-11
col-sm-12"><div class="row sjb-list-row"><div class="col-md-5
col-sm-12"><div class="job-info"><h4>
<a href="https://reviveresearch.org/jobs/clinical-research-coordinator/">
<span class="job-title">Clinical Research Coordinator</span> | <span
class="company-name">Revive Research Institute, Inc.</span>
</a></h4></div></div><div class="col-md-2 col-sm-4 col-xs-12"><div
class="job-type">Full Time</div></div><div class="col-md-2 col-sm-4
col-xs-12"><div class="job-location">Farmington Hills, MI, Michigan,
Southfield, MI, Troy</div></div><div class="col-md-3 col-sm-4
col-xs-12"><div class="job-date">Posted 3 years ago</div></div><<23287
chars omitted>om">zsuhrawardy@rev-research.com</a> .<a
href="https://www.reviveresearch.org/job-location/southfield-mi/">Southfield
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
href="https://reviveresearch.org/jobs/research-intern/">Read
More</a></p><div class="sjb-view-less-btn"
id="sjb_view_less_btn_7319"><a class="sjb_view_less_btn
sjb_view_more_btn" data-id="7319">View
less</a></div></div></div></div></div><div
class="clearfix"></div></div>
2026-09-28 14:49:56  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7773439, "visible_chars": 17747,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:49:56  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://reviveresearch.org/careers/", "text": " \n\n
\n\nHit enter to search or ESC to close\nSearchClose Search\n
\t\t\t\t \nCareers \t\t\t\t\t\tHome | Careers\n\n\nCategoryClinical
Research   Intern\n\nJob TypeFull TimeInternship\n\nLocationFarmington
Hills, MIKingman, AZMichiganSouthfield, MITroy\n\nUnique opportunity
to make an Impact in the healthcare industry…IMPROVE THE FUTURE AS OUR
CLINICAL RESEARCH COORDINATOR!The professional we select for Revival
Research Institute will have an overall responsibility to enhance our
operational efficiency, market presence, affiliated partnerships, and
staff development/performance.The qualified candidate we are looking
for should be genuinely respectful of diverse points-of-view and
strive for an environment in which inclusiveness drives productivity
and results.Other requirements include:Bachelor’s degree with a
Masters in a science-related field highly desired, or extensive
experience in Clinical Research 2+ years of incr<133703 chars
omitted>ups allow-same-origin allow-scripts allow-top-navigation
allow-modals allow-popups-to-escape-sandbox
allow-storage-access-by-user-activation\"
src=\"https://www.google.com/recaptcha/api2/anchor?ar=1&amp;k=6LfnEm4rAAAAAH92Y8i-TpJF50j9lcm33jxMeK5-&amp;co=aHR0cHM6Ly9yZXZpdmVyZXNlYXJjaC5vcmc6NDQz&amp;hl=en&amp;v=kemdRjWFxNjgsGdhRslyEPwU&amp;size=invisible&amp;anchor-ms=20000&amp;execute-ms=30000&amp;cb=rc7mckft23z4\"></iframe></div><div
class=\"grecaptcha-error\"></div><textarea
id=\"g-recaptcha-response-100000\" name=\"g-recaptcha-response\"
class=\"g-recaptcha-response\" style=\"width: 250px; height: 40px;
border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px;
resize: none; display: none;\"></textarea></div><iframe
style=\"display: none;\"></iframe></div></body>", "scrape_meta":
{"bot_blocked": false, "cookies_dismissed": false, "issues": [],
"content_chars": 17747, "requested_url":
"https://reviveresearch.org/careers", "final_url":
"https://reviveresearch.org/careers/"}}
2026-09-28 14:49:56  [INFO]  40ab146c | telescope job done:
https://reviveresearch.org/careers ->
https://reviveresearch.org/careers/ fields:text,html
2026-09-28 14:49:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:49:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-3cb1da1b4c30e6d8"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:49:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=drugfree_org, n=4]
2026-09-28 14:49:56  [DEBUG]  3243: Calling agent.do_task
live_content: <div class="go3670563033"
id="hs-web-interactives-top-push-anchor"></div>
 Google Tag Manager (noscript)

 End Google Tag Manager (noscript)

<div class="coa-main-header__extra-links">
<a class="coa-main-header__extra-links--primary" href="#FUNHCTRHDZC">Donate</a>
<a class="coa-main-header__extra-links--secondary"
href="/recursos-en-espanol/" lang="es"><span>Recursos en
</span>Español</a>
</div>
<div class="coa-main-header__logo-line">
<a class="coa-main-header__logo" data-track-action="top navigation
link clicked" data-track-event="navigation" data-track-label="clicked:
Logo" href="https://drugfree.org">
</a>
<div class="coa-main-header__logo-line-buttons">
<a class="coa-main-header__logo-line-button coa-main-header__search"
href="https://drugfree.org?s="></a>




</div>
</div>
<ul class="primary-menu">
<li class="primary-menu__main-item menu-item menu-item-type-custom
menu-item-object-custom menu-item-has-children menu-item-171459"
data-menu-id="menu-0">
<span class="primary-menu__<38978 chars omitted>ll receive a response
to text or email within 24 hours

Msg and data rates may apply. Msg frequency varies.
Text HELP for help or STOP to opt out. <a
href="https://drugfree.org/helpline-terms-of-use/">Terms</a> and <a
href="https://drugfree.org/article/privacy-policy/">Privacy</a></p>
</div>
</div>
</div>
</div>
 HEAD SCRIPTS

 FOOTER SCRIPTS





 Cookie Consent Notice






<div class="go2933276541 go2369186930"
id="hs-web-interactives-top-anchor"></div>
<div class="go2933276541 go1348078617"
id="hs-web-interactives-bottom-anchor"></div>
<div id="hs-web-interactives-floating-container">
<div class="go2417249464 go613305155"
id="hs-web-interactives-floating-top-left-anchor">
</div>
<div class="go2417249464 go471583506"
id="hs-web-interactives-floating-top-right-anchor">
</div>
<div class="go2417249464 go3921366393"
id="hs-web-interactives-floating-bottom-left-anchor">
</div>
<div class="go2417249464 go3967842156"
id="hs-web-interactives-floating-bottom-right-anchor">
</div>
</div>
2026-09-28 14:49:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=drugfree_org
2026-09-28 14:49:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Revenue Operations Coordinator"]
containers=["<div class=\"go3670563033\"
id=\"hs-web-interactives-top-push-anchor\"></div>\n Google Tag Manager
(noscript) \n\n End Google Tag Manager (noscript) \n\n<div
class=\"coa-main-header__extra-links\">\n<a
class=\"coa-main-header__extra-links--primary\"
href=\"#FUNHCTRHDZC\">Donate</a>\n<a
class=\"coa-main-header__extra-links--secondary\"
href=\"/recursos-en-espanol/\" lang=\"es\"><span>Recursos en
</span>Español</a>\n</div>\n<div
class=\"coa-main-header__logo-line\">\n<a
class=\"coa-main-header__logo\" data-track-action=\"top navigation
link clicked\" data-track-event=\"navigation\"
data-track-label=\"clicked: Logo\"
href=\"https://drugfree.org\">\n</a>\n<div
class=\"coa-main-header__logo-line-buttons\">\n<a
class=\"coa-main-header__logo-line-button coa-main-header__search\"
href=\"https://drugfree.org?s=\"></a>\n\n\n\n\n</div>\n</div>\n<ul
class=\"primary-menu\">\n<li class=\"primary-menu__main-item menu-item
menu-item-type-custom menu-item-object-custom menu-item-has-children
menu-ite<40917 chars omitted>data rates may apply. Msg frequency
varies.\nText HELP for help or STOP to opt out. <a
href=\"https://drugfree.org/helpline-terms-of-use/\">Terms</a> and <a
href=\"https://drugfree.org/article/privacy-policy/\">Privacy</a></p>\n</div>\n</div>\n</div>\n</div>
\n HEAD SCRIPTS \n\n FOOTER SCRIPTS \n\n\n\n\n\n Cookie Consent Notice
\n\n\n\n\n\n\n<div class=\"go2933276541 go2369186930\"
id=\"hs-web-interactives-top-anchor\"></div>\n<div
class=\"go2933276541 go1348078617\"
id=\"hs-web-interactives-bottom-anchor\"></div>\n<div
id=\"hs-web-interactives-floating-container\">\n<div
class=\"go2417249464 go613305155\"
id=\"hs-web-interactives-floating-top-left-anchor\">\n</div>\n<div
class=\"go2417249464 go471583506\"
id=\"hs-web-interactives-floating-top-right-anchor\">\n</div>\n<div
class=\"go2417249464 go3921366393\"
id=\"hs-web-interactives-floating-bottom-left-anchor\">\n</div>\n<div
class=\"go2417249464 go3967842156\"
id=\"hs-web-interactives-floating-bottom-right-anchor\">\n</div>\n</div>"]
cull_outcome='full_dom' dom_joined=<div class="go3670563033"
id="hs-web-interactives-top-push-anchor"></div>
 Google Tag Manager (noscript)

 End Google Tag Manager (noscript)

<div class="coa-main-header__extra-links">
<a class="coa-main-header__extra-links--primary" href="#FUNHCTRHDZC">Donate</a>
<a class="coa-main-header__extra-links--secondary"
href="/recursos-en-espanol/" lang="es"><span>Recursos en
</span>Español</a>
</div>
<div class="coa-main-header__logo-line">
<a class="coa-main-header__logo" data-track-action="top navigation
link clicked" data-track-event="navigation" data-track-label="clicked:
Logo" href="https://drugfree.org">
</a>
<div class="coa-main-header__logo-line-buttons">
<a class="coa-main-header__logo-line-button coa-main-header__search"
href="https://drugfree.org?s="></a>




</div>
</div>
<ul class="primary-menu">
<li class="primary-menu__main-item menu-item menu-item-type-custom
menu-item-object-custom menu-item-has-children menu-item-171459"
data-menu-id="menu-0">
<span class="primary-menu__<38978 chars omitted>ll receive a response
to text or email within 24 hours

Msg and data rates may apply. Msg frequency varies.
Text HELP for help or STOP to opt out. <a
href="https://drugfree.org/helpline-terms-of-use/">Terms</a> and <a
href="https://drugfree.org/article/privacy-policy/">Privacy</a></p>
</div>
</div>
</div>
</div>
 HEAD SCRIPTS

 FOOTER SCRIPTS





 Cookie Consent Notice






<div class="go2933276541 go2369186930"
id="hs-web-interactives-top-anchor"></div>
<div class="go2933276541 go1348078617"
id="hs-web-interactives-bottom-anchor"></div>
<div id="hs-web-interactives-floating-container">
<div class="go2417249464 go613305155"
id="hs-web-interactives-floating-top-left-anchor">
</div>
<div class="go2417249464 go471583506"
id="hs-web-interactives-floating-top-right-anchor">
</div>
<div class="go2417249464 go3921366393"
id="hs-web-interactives-floating-bottom-left-anchor">
</div>
<div class="go2417249464 go3967842156"
id="hs-web-interactives-floating-bottom-right-anchor">
</div>
</div>
2026-09-28 14:49:56  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7771794, "visible_chars": 9275,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:49:56  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://drugfree.org/article/work-at-the-partnership/",
"text": "\n\n\n\n                    \n    \n    \n        \n    \n
    Open positions\n    \n        \n    \n    \n        \n
\n                                                Work at Partnership
to End Addiction\n                    \n    \n        \n            \n
       \n    \n    \n
                              \n            \n        \n    \n
                   \n                    \n    \n        \n
\n                \n                                            \n
                                                   \n
              \n\n                \n        \n
   On This Page\n                    \n                1Open
positions\n    \n    \n    \n    \n    \n    \n\n
                                      \n                        \n
                  <118574 chars omitted>\n<div class=\"go2933276541
go2369186930\" id=\"hs-web-interactives-top-anchor\"><div
id=\"hs-interactives-modal-overlay\"
class=\"go1632949049\"></div></div>\n<div class=\"go2933276541
go1348078617\" id=\"hs-web-interactives-bottom-anchor\"></div>\n<div
id=\"hs-web-interactives-floating-container\">\n  <div
id=\"hs-web-interactives-floating-top-left-anchor\"
class=\"go2417249464 go613305155\">\n  </div>\n  <div
id=\"hs-web-interactives-floating-top-right-anchor\"
class=\"go2417249464 go471583506\">\n  </div>\n  <div
id=\"hs-web-interactives-floating-bottom-left-anchor\"
class=\"go2417249464 go3921366393\">\n  </div>\n  <div
id=\"hs-web-interactives-floating-bottom-right-anchor\"
class=\"go2417249464 go3967842156\">\n  </div>\n</div>\n</body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": true,
"issues": [], "content_chars": 9275, "requested_url":
"https://drugfree.org/article/work-at-the-partnership", "final_url":
"https://drugfree.org/article/work-at-the-partnership/"}}
2026-09-28 14:49:56  [INFO]  c5eef091 | telescope job done:
https://drugfree.org/article/work-at-the-partnership ->
https://drugfree.org/article/work-at-the-partnership/ fields:text,html
2026-09-28 14:49:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:49:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-739781f1bf674fc7"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:49:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=mrisoftware_com, n=4]
2026-09-28 14:49:56  [DEBUG]  3243: Calling agent.do_task
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
2026-09-28 14:49:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=mrisoftware_com
2026-09-28 14:49:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["PMO Manager", "Senior Property
Accountant IV", "Systems Administrator III", "Billing Analyst",
"Program Manager", "Application Support Analyst (SQL)", "Account
Manager (Residential)", "SaaS Implementation Consultant (NA Hours)",
"Project Scoping Specialist (UK Hours)", "Director - Product
Management"] containers=["<ul aria-label=\"Page 1 of 5\"
role=\"list\"><li class=\"css-1q2dra3\"><div class=\"css-qiqmbt\"><div
class=\"css-b3pn3b\"><div class=\"css-b3pn3b\"><h3><a
aria-current=\"false\" class=\"css-19uc56f\"
data-automation-id=\"jobTitle\" data-uxi-element-id=\"jobItem\"
data-uxi-item-rank=\"0\" data-uxi-query-id=\"\"
data-uxi-widget-type=\"heading\"
href=\"/en-US/external_careersite/job/Cape-Town-South-Africa-Office/Support-Analyst_R-109362\">Support
Analyst</a></h3></div></div></div><div class=\"css-248241\"><div
class=\"css-1y87fhn\"><div class=\"css-k008qs\"
data-automation-id=\"locations\">locationsCape Town, South Africa
Office</div></div></div><div class=\"css-zoser8\"><div
class=\"css-1y87fhn\"><div class=\"css-k008qs\"
data-automation-id=\"postedOn\">posted onPosted
Today</div></div></div><ul class=\"css-14a0imc\"
data-automation-id=\"subtitle\"><li
class=\"css-h2nt8k\">R-109362</li></ul></li><li
class=\"css-1q2dra3\"><div class=\"css-qiqmbt\"><div
class=\"css-b3pn3b\"><div class=\<15770 chars omitted>ul
class=\"css-14a0imc\" data-automation-id=\"subtitle\"><li
class=\"css-h2nt8k\">R-109171</li></ul></li><li
class=\"css-1q2dra3\"><div class=\"css-qiqmbt\"><div
class=\"css-b3pn3b\"><div class=\"css-b3pn3b\"><h3><a
aria-current=\"false\" class=\"css-19uc56f\"
data-automation-id=\"jobTitle\" data-uxi-element-id=\"jobItem\"
data-uxi-item-rank=\"19\" data-uxi-query-id=\"\"
data-uxi-widget-type=\"heading\"
href=\"/en-US/external_careersite/job/Cleveland-Ohio-Office/Associate-Product-Marketing-Specialist_R-108835\">Associate
Product Marketing Specialist</a></h3></div></div></div><div
class=\"css-248241\"><div class=\"css-1y87fhn\"><div
class=\"css-k008qs\" data-automation-id=\"locations\">locations2
Locations</div></div></div><div class=\"css-zoser8\"><div
class=\"css-1y87fhn\"><div class=\"css-k008qs\"
data-automation-id=\"postedOn\">posted onPosted 5 Days
Ago</div></div></div><ul class=\"css-14a0imc\"
data-automation-id=\"subtitle\"><li
class=\"css-h2nt8k\">R-108835</li></ul></li></ul>"]
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
2026-09-28 14:49:56  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7761750, "visible_chars": 2156,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:49:56  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://mrisoftware.wd501.myworkdayjobs.com/external_careersite",
"text": "\nSkip to main contentSearchFiltersLocationTime
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
L37.8267961,13.1207091 L37.8267961,13.1207091 Z\"
fill=\"#2367AE\"></path></g></g></g></g></g></g></g></g></svg></div><span
class=\"css-1vfpfxb\"></span></div><div class=\"css-1h61b0m\">© 2026
Workday, Inc. All rights
reserved.</div></div></div></div></div></div>\n\n</body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 2156, "requested_url":
"https://mrisoftware.wd501.myworkdayjobs.com/external_careersite",
"final_url": "https://mrisoftware.wd501.myworkdayjobs.com/external_careersite"}}
2026-09-28 14:49:56  [INFO]  f5714de8 | telescope job done:
https://mrisoftware.wd501.myworkdayjobs.com/external_careersite ->
https://mrisoftware.wd501.myworkdayjobs.com/external_careersite
fields:text,html
2026-09-28 14:49:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:49:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-53707e5762f45983"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:49:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=revivalresearch_org, n=4]
2026-09-28 14:49:56  [DEBUG]  3243: Calling agent.do_task
live_content: <div class="awsm-job-listings awsm-lists"
data-listings="10"><div class="awsm-job-listing-item awsm-list-item"
id="awsm-list-item-36282"><div class="awsm-job-item"><div
class="awsm-list-left-col"><h2 class="awsm-job-post-title">
<a href="https://revivalresearch.org/blogs/jobs/physician-assistant/">Physician
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
href="https://revivalresearch.org/blogs/j<10893 chars omitted>
class="awsm-list-left-col"><h2 class="awsm-job-post-title">
<a href="https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/">Clinical
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
href="https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/">More
Details <span></span></a></div></div></div></div></div>
2026-09-28 14:49:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=revivalresearch_org
2026-09-28 14:49:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Physician Assistant",
"Phlebotomist/Lab Tech", "Clinical Research Coordinator – Illinois",
"Clinical Research Coordinator – Texas", "Clinical Research
Coordinator – New Jersey", "Clinical Research Coordinator – North
Carolina"] containers=["<div class=\"awsm-job-listings awsm-lists\"
data-listings=\"10\"><div class=\"awsm-job-listing-item
awsm-list-item\" id=\"awsm-list-item-36282\"><div
class=\"awsm-job-item\"><div class=\"awsm-list-left-col\"><h2
class=\"awsm-job-post-title\">\n<a
href=\"https://revivalresearch.org/blogs/jobs/physician-assistant/\">Physician
Assistant</a></h2></div><div class=\"awsm-list-right-col\"><div
class=\"awsm-job-specification-wrapper\"><div
class=\"awsm-job-specification-item
awsm-job-specification-job-category\"><span
class=\"awsm-job-specification-term\">Clinical
Research</span></div><div class=\"awsm-job-specification-item
awsm-job-specification-job-type\"><span
class=\"awsm-job-specification-term\">Full Time</span></div><div
class=\"awsm-job-specification-item
awsm-job-specification-job-location\"><span
class=\"awsm-job-specification-term\">Michigan</span> <span
class=\"awsm-job-specification-term\">Texas</span></div></div><div
class=\"awsm-job-more-container\"><a class=\"awsm-job-more\" <11352
chars omitted> class=\"awsm-job-post-title\">\n<a
href=\"https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/\">Clinical
Research Coordinator – North Carolina</a></h2></div><div
class=\"awsm-list-right-col\"><div
class=\"awsm-job-specification-wrapper\"><div
class=\"awsm-job-specification-item
awsm-job-specification-job-category\"><span
class=\"awsm-job-specification-term\">Clinical
Research</span></div><div class=\"awsm-job-specification-item
awsm-job-specification-job-type\"><span
class=\"awsm-job-specification-term\">Full Time</span></div><div
class=\"awsm-job-specification-item
awsm-job-specification-job-location\"><span
class=\"awsm-job-specification-term\">Cary</span> <span
class=\"awsm-job-specification-term\">North
Carolina</span></div></div><div class=\"awsm-job-more-container\"><a
class=\"awsm-job-more\"
href=\"https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/\">More
Details <span></span></a></div></div></div></div></div>"]
cull_outcome='culled' dom_joined=<div class="awsm-job-listings
awsm-lists" data-listings="10"><div class="awsm-job-listing-item
awsm-list-item" id="awsm-list-item-36282"><div
class="awsm-job-item"><div class="awsm-list-left-col"><h2
class="awsm-job-post-title">
<a href="https://revivalresearch.org/blogs/jobs/physician-assistant/">Physician
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
href="https://revivalresearch.org/blogs/j<10893 chars omitted>
class="awsm-list-left-col"><h2 class="awsm-job-post-title">
<a href="https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/">Clinical
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
href="https://revivalresearch.org/blogs/jobs/clinical-research-coordinator-north-carolina/">More
Details <span></span></a></div></div></div></div></div>
2026-09-28 14:49:56  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7730892, "visible_chars": 3360,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:49:56  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://revivalresearch.org/careers", "text": "\n\nSkip
to contentSkip to footer\nCareersCurrent jobs\n Looking to Build Your
Career in Clinical Research? SearchFilter byAll Job CategoryAll Job
CategoryClinical ResearchAll Job Category▾All Job CategoryClinical
ResearchAll Job TypeAll Job TypeFull TimeAll Job Type▾All Job TypeFull
TimeAll Job LocationAll Job
LocationMichiganTexasElginIllinoisCaryNorth CarolinaHamiltonNew
JerseyDentonMcKinneyAll Job Location▾All Job
LocationMichiganTexasElginIllinoisCaryNorth CarolinaHamiltonNew
JerseyDentonMcKinney\nPhysician AssistantClinical ResearchFull
TimeMichigan TexasMore Details \nPhlebotomist/Lab TechClinical
ResearchFull TimeTexas McKinneyMore Details \nClinical Research
Coordinator – IllinoisClinical ResearchFull TimeElgin IllinoisMore
Details \nClinical Research Coordinator – TexasClinical ResearchFull
TimeTexas DentonMore Details \nClinical Research Coordinator – New
JerseyClinical ResearchFull TimeHamilton New JerseyMore Det<471859
chars omitted>popups-to-escape-sandbox
allow-storage-access-by-user-activation\"
src=\"https://www.google.com/recaptcha/api2/anchor?ar=1&amp;k=6LfKFG4rAAAAAO43lgGM-XzK3ffd9t6n1a6vXSQs&amp;co=aHR0cHM6Ly9yZXZpdmFscmVzZWFyY2gub3JnOjQ0Mw..&amp;hl=en&amp;v=kemdRjWFxNjgsGdhRslyEPwU&amp;size=invisible&amp;anchor-ms=20000&amp;execute-ms=30000&amp;cb=sfqoipmpyuwe\"></iframe></div><div
class=\"grecaptcha-error\"></div><textarea
id=\"g-recaptcha-response-100000\" name=\"g-recaptcha-response\"
class=\"g-recaptcha-response\" style=\"width: 250px; height: 40px;
border: 1px solid rgb(193, 193, 193); margin: 10px 25px; padding: 0px;
resize: none; display: none;\"></textarea></div><iframe
style=\"display: none;\"></iframe></div><div class=\"content_wrap\"
style=\"height:0;visibility:hidden;\"></div></body>", "scrape_meta":
{"bot_blocked": false, "cookies_dismissed": false, "issues": [],
"content_chars": 3360, "requested_url":
"https://revivalresearch.org/careers", "final_url":
"https://revivalresearch.org/careers"}}
2026-09-28 14:49:56  [INFO]  ff28c96b | telescope job done:
https://revivalresearch.org/careers ->
https://revivalresearch.org/careers fields:text,html
2026-09-28 14:49:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:49:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-0a3505b5373ff861"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:49:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=volvogroup_com_2, n=4]
2026-09-28 14:49:56  [DEBUG]  3243: Calling agent.do_task
live_content: <div id="job--table"><div id="job--table--head"><span
class="job--table--cell">Available Jobs (619)</span><span
class="job--table--cell">Job Category</span><span
class="job--table--cell">Organization</span><span
class="job--table--cell">Location</span><span
class="job--table--cell">Position Type</span><span
class="job--table--cell">Posted</span></div><a class="job--table--row"
href="https://jobs.volvogroup.com/job/Hwaseong-People-&amp;-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555"
title="People &amp; Culture Coordinator Professional"><span
class="job--table--cell job--table--title job--table--mobile"
data-id="title" data-mobile="Available Jobs ">People &amp; Culture
Coordinator Professional </span><span class="job--table--cell
job--table--department job--table--mobile" data-id="department"
data-mobile="Job Category">People &amp; Culture </span><span
class="job--table--cell job--table--facility" data-id="facility">Volvo
Trucks </span><span class="job--table--cell job<3907900 chars
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
2026-09-28 14:49:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=volvogroup_com_2
2026-09-28 14:49:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Transport Analyst", "Accountant -
R2R", "2027 Ausbildung Fachkraft (m/w/d) für Lagerlogistik",
"Conseiller(e) Service Clients Atelier Poids-Lourds H/F - CDI",
"Thesis work: Calculation of service intervals", "Jobstudent Talent
Acquisition", "VIE - Adaptation buyer H/F", "Aprendiz Senai", "Senior
Software Engineer", "Senior System Performance Engineer"]
containers=["<div id=\"job--table\"><div id=\"job--table--head\"><span
class=\"job--table--cell\">Available Jobs (619)</span><span
class=\"job--table--cell\">Job Category</span><span
class=\"job--table--cell\">Organization</span><span
class=\"job--table--cell\">Location</span><span
class=\"job--table--cell\">Position Type</span><span
class=\"job--table--cell\">Posted</span></div><a
class=\"job--table--row\"
href=\"https://jobs.volvogroup.com/job/Hwaseong-People-&amp;-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555\"
title=\"People &amp; Culture Coordinator Professional\"><span
class=\"job--table--cell job--table--title job--table--mobile\"
data-id=\"title\" data-mobile=\"Available Jobs \">People &amp; Culture
Coordinator Professional </span><span class=\"job--table--cell
job--table--department job--table--mobile\" data-id=\"department\"
data-mobile=\"Job Category\">People &amp; Culture </span><span
class=\"job--table--cell job--table--facility\"
data-id=\"facility\">Volvo Trucks <3941441 chars omitted>ed veteran.
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
</span><span class=\"job--table--cell job--table--ID
job--table--hidden\" data-id=\"ID\">1295-en_US </span></a></div>"]
cull_outcome='culled' dom_joined=<div id="job--table"><div
id="job--table--head"><span class="job--table--cell">Available Jobs
(619)</span><span class="job--table--cell">Job Category</span><span
class="job--table--cell">Organization</span><span
class="job--table--cell">Location</span><span
class="job--table--cell">Position Type</span><span
class="job--table--cell">Posted</span></div><a class="job--table--row"
href="https://jobs.volvogroup.com/job/Hwaseong-People-&amp;-Culture-Coordinator-Professional-18488/1369700155/?feedId=361555"
title="People &amp; Culture Coordinator Professional"><span
class="job--table--cell job--table--title job--table--mobile"
data-id="title" data-mobile="Available Jobs ">People &amp; Culture
Coordinator Professional </span><span class="job--table--cell
job--table--department job--table--mobile" data-id="department"
data-mobile="Job Category">People &amp; Culture </span><span
class="job--table--cell job--table--facility" data-id="facility">Volvo
Trucks </span><span class="job--table--cell job<3907900 chars
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
2026-09-28 14:50:22  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7821994, "visible_chars": 11432,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:22  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://psychiatry.ucsf.edu/careers", "text": "\n
 \n    \n\n\n      \n      \n        \n    \n      \n        \n\n
\n    \n  \n\n          \n  \n    \n      \n  \n    \n      \n      \n
         \n\n\n\n\n\n\n  \n    \n      \n        \n        Career
Opportunities\n        \n      \n      \n                        \n
    \n        \n        \n        \n\n    Take the next step in your
career and make a meaningful impact with the UCSF Department of
Psychiatry and Behavioral Sciences\n\n  \n      \n    \n  \n\n\n\n
\n  \n          \n\n\n  \n\n\n    \n                            \n  \n
   \n      \n  \n    \n\n  \n  \n    \n\n    \n          \n\n
\n\n    \n  \n  \n\n  \n  \n\n\n\n  \n    \n
\n            \n                              \n
                     \n
\n\n\n\n\n  \n    \n      \n\n    \n          Academic faculty
positions\n\n      \n\n\n    \n  \n  \n    \<133110 chars
omitted>adobeDataLayer.push({vimeovideo:{title:e}})})),player.getVideoId().then((function(e){window.adobeDataLayer.push({vimeovideo:{id:e}})})),_satellite.track(\"video_50\"),lastCheckPoint=50):cent>=75&&lastCheckPoint<75&&(player.getVideoTitle().then((function(e){window.adobeDataLayer.push({vimeovideo:{title:e}})})),player.getVideoId().then((function(e){window.adobeDataLayer.push({vimeovideo:{id:e}})})),_satellite.track(\"video_75\"),lastCheckPoint=75)),e.seconds!==e.duration||videoEnded||(player.getVideoTitle().then((function(e){window.adobeDataLayer.push({vimeovideo:{title:e}})})),player.getVideoId().then((function(e){window.adobeDataLayer.push({vimeovideo:{id:e}})})),_satellite.track(\"video_end\"),lastCheckPoint=0,videoEnded=!0),cent<25&&(videoEnded=!1)}))}\n});</script></body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 11432, "requested_url":
"https://psychiatry.ucsf.edu/careers", "final_url":
"https://psychiatry.ucsf.edu/careers"}}
2026-09-28 14:50:22  [INFO]  7679559a | telescope job done:
https://psychiatry.ucsf.edu/careers ->
https://psychiatry.ucsf.edu/careers fields:text,html
2026-09-28 14:50:22  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:22  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-42fbc01c6aed54fe"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:22  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=rcpsych_ac_uk, n=4]
2026-09-28 14:50:22  [DEBUG]  3243: Calling agent.do_task live_content: <ul>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/">
<h3>Forensic Psychiatrists</h3>
</a>
Health New Zealand - Te Whatu Ora
Other


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/">
<h3>Senior Staff Specialist or Staff Specialist or Senior Medical
Officer (Psychiatrist - Intellectual and Developmental Disability)
(Bundaberg)</h3>
</a>
Wide Bay Hospital &amp; Health Service
Bundaberg, Queensland


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/">
<h3>Clinical Director and Staff Specialist in Mental Health CCLHD</h3>
</a>
Central Coast Local District
New South Wales


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/">
<h3>Consultant Child and Adolescent Psychiatrist</h3>
</a>
Kidswell
London, North West England


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/">
<h3>Senior Staff Specialist or Staff Specialist or Senior Medical
Officer (Psychiatrist) (Hervey Bay and Maryborough)</h3>
</a>
Wide Bay Hospital &amp; Health Service
Hervey Bay and Maryborough, Queensland


</li>
</ul>
2026-09-28 14:50:22  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=rcpsych_ac_uk
2026-09-28 14:50:22  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Forensic Psychiatrists", "Senior Staff
Specialist or Staff Specialist or Senior Medical Officer (Psychiatrist
- Intellectual and Developmental Disability) (Bundaberg)", "Consultant
Child and Adolescent Psychiatrist", "Senior Staff Specialist or Staff
Specialist or Senior Medical Officer (Psychiatrist) (Hervey Bay and
Maryborough)", "Clinical Director and Staff Specialist in Mental
Health CCLHD"] containers=["<ul>\n<li>\n<a
href=\"https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/\">\n<h3>Forensic
Psychiatrists</h3>\n</a>\nHealth New Zealand - Te Whatu
Ora\nOther\n\n\n</li>\n<li>\n<a
href=\"https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/\">\n<h3>Senior
Staff Specialist or Staff Specialist or Senior Medical Officer
(Psychiatrist - Intellectual and Developmental Disability)
(Bundaberg)</h3>\n</a>\nWide Bay Hospital &amp; Health
Service\nBundaberg, Queensland\n\n\n</li>\n<li>\n<a
href=\"https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/\">\n<h3>Clinical
Director and Staff Specialist in Mental Health
CCLHD</h3>\n</a>\nCentral Coast Local District\nNew South
Wales\n\n\n</li>\n<li>\n<a
href=\"https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/\">\n<h3>Consultant
Child and Adolescent Psychiatrist</h3>\n</a>\nKidswell\nLondon, North
West England\n\n\n</li>\n<li>\n<a
href=\"https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/\">\n<h3>Senior
Staff Specialist or Staff Specialist or Senior Medical Officer
(Psychiatrist) (Hervey Bay and Maryborough)</h3>\n</a>\nWide Bay
Hospital &amp; Health Service\nHervey Bay and Maryborough,
Queensland\n\n\n</li>\n</ul>"] cull_outcome='culled' dom_joined=<ul>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/forensic-psychiatrists/85357807/">
<h3>Forensic Psychiatrists</h3>
</a>
Health New Zealand - Te Whatu Ora
Other


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-intellectual-and-developmental-disability-bundaberg/85777054/">
<h3>Senior Staff Specialist or Staff Specialist or Senior Medical
Officer (Psychiatrist - Intellectual and Developmental Disability)
(Bundaberg)</h3>
</a>
Wide Bay Hospital &amp; Health Service
Bundaberg, Queensland


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/clinical-director-and-staff-specialist-in-mental-health-cclhd/85789120/">
<h3>Clinical Director and Staff Specialist in Mental Health CCLHD</h3>
</a>
Central Coast Local District
New South Wales


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/consultant-child-and-adolescent-psychiatrist/85411845/">
<h3>Consultant Child and Adolescent Psychiatrist</h3>
</a>
Kidswell
London, North West England


</li>
<li>
<a href="https://jobs.rcpsych.ac.uk/job/senior-staff-specialist-or-staff-specialist-or-senior-medical-officer-psychiatrist-hervey-bay-and-maryborough/85788727/">
<h3>Senior Staff Specialist or Staff Specialist or Senior Medical
Officer (Psychiatrist) (Hervey Bay and Maryborough)</h3>
</a>
Wide Bay Hospital &amp; Health Service
Hervey Bay and Maryborough, Queensland


</li>
</ul>
2026-09-28 14:50:22  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7820607, "visible_chars": 2223,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:22  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://jobs.rcpsych.ac.uk/", "text": "       Close
this dialog          We use cookies and similar technologies to make
our site work, and to support analytics, personalization, and
marketing. To learn more, view the disclosures.     Privacy Policy
 Manage Preferences                    \n\n\n\n\n\n\n\nCareer
Center\n\n \n \nLooking For Qualified Candidates?\nPost a Job \n
\n\n\n\n\nJob Search Keywords\n\n\n\n\n\n\n\n\n\n\nSubmit
Search\nSearch Jobs\n\n\n \n\n \n\n\n\n \n\n\n Featured Jobs  \n\n
\n\n\n\nForensic Psychiatrists\n\nHealth New Zealand - Te Whatu
Ora\nOther\n\n\n\n\n\nSenior Staff Specialist or Staff Specialist or
Senior Medical Officer (Psychiatrist - Intellectual and Developmental
Disability) (Bundaberg)\n\nWide Bay Hospital & Health
Service\nBundaberg, Queensland\n\n\n\n\n\nClinical Director and Staff
Specialist in Mental Health CCLHD\n\nCentral Coast Local District\nNew
South Wales\n\n\n\n\n\nConsultant Child and Adolescent
Psychiatrist\n\nKidswell\n<54100 chars omitted>Close'><span
aria-hidden='true'><svg xmlns='http://www.w3.org/2000/svg' width='16'
height='16' fill='currentColor' class='bi bi-x-lg' viewBox='0 0 16
16'> <path d='M2.146 2.854a.5.5 0 1 1 .708-.708L8
7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0
1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293
8z'/></svg></span></button>\";\njQuery(\"#cookie-consent\").html(consent_content);\n}\n});\n</script>\n\n\n<iframe
style=\"display: none;\" name=\"__uspapiLocator\"></iframe><ul
id=\"ui-id-1\" tabindex=\"0\" class=\"ui-menu ui-widget
ui-widget-content ui-autocomplete ui-front\" style=\"display: none;\"
unselectable=\"on\"></ul><div role=\"status\" aria-live=\"assertive\"
aria-relevant=\"additions\" class=\"ui-helper-hidden-accessible\"
style=\"display: none;\"></div></body>", "scrape_meta":
{"bot_blocked": false, "cookies_dismissed": true, "issues": [],
"content_chars": 2223, "requested_url": "https://jobs.rcpsych.ac.uk",
"final_url": "https://jobs.rcpsych.ac.uk/"}}
2026-09-28 14:50:22  [INFO]  3be968f3 | telescope job done:
https://jobs.rcpsych.ac.uk -> https://jobs.rcpsych.ac.uk/
fields:text,html
2026-09-28 14:50:22  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:22  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-72f2303866f14c68"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:22  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=bcchr_ca, n=4]
2026-09-28 14:50:22  [DEBUG]  3243: Calling agent.do_task
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
href="https://www.bcchr.ca/" rel="home"><img alt="BC Children’s
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
href="http://www.bcchildrens.ca/" id="fndry-block-6509f4756b140"
rel="" target="_blank">BC Children’s Hospital</a><a class="fndry-btn
fndry-mb--2 fndry-btn-headerLogin" href="https://www.bcchf.ca/"
id="fndry-block-6414d467f8311" rel="" target="_blank">BC Children’s
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
2026-09-28 14:50:22  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=bcchr_ca
2026-09-28 14:50:22  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Manager, Research IT, BC Children’s
Hospital Research Institute"] containers=["Google Tag Manager
(noscript) \n\n End Google Tag Manager (noscript) \n<div
class=\"wp-site-blocks\"><div class=\"fndry-container
fndry-responsive-bg fndry-responsive-border fndry-container--full
fndry-pb--3 fndry-pt--0 fndry-pr--md-2 fndry-pl--md-2\">\n<div
class=\"fndry-container fndry-responsive-bg fndry-responsive-border
fndry-pt--0\">\n<div class=\"fndry-row fndry-align--start
fndry-align--md-center fndry-justify--between
fndry-justify--md-between\">\n<div class=\"fndry-col
fndry-responsive-bg fndry-col--3 fndry-col--md-4 fndry-pt--2
fndry-pl--2 fndry-pl--md-1\">\n<div class=\"wp-block-site-logo\"><a
class=\"custom-logo-link\" href=\"https://www.bcchr.ca/\"
rel=\"home\"><img alt=\"BC Children’s Hospital Research Institute
(BCCHR)\" class=\"custom-logo\"/></a></div></div>\n<div
class=\"fndry-col fndry-responsive-bg fndry-col--9 fndry-col--md-6
fndry-d--flex fndry-d--md-none fndry-flex--row fndry-align--center
fndry-justify--end\">\n<div class=\"fndry-container
fndry-responsive-bg<35920 chars omitted>ry-pt--3 fndry-pr--0
fndry-pl--0 fndry-pb--md-2\">\n<div class=\"fndry-row
fndry-row--gutter\">\n<div class=\"fndry-col fndry-responsive-bg
fndry-col--12 fndry-d--flex fndry-flex--col fndry-align--start
fndry-justify--start\">\n<a class=\"fndry-btn fndry-mb--2
fndry-btn-headerLogin\" href=\"http://www.bcchildrens.ca/\"
id=\"fndry-block-6509f4756b140\" rel=\"\" target=\"_blank\">BC
Children’s Hospital</a><a class=\"fndry-btn fndry-mb--2
fndry-btn-headerLogin\" href=\"https://www.bcchf.ca/\"
id=\"fndry-block-6414d467f8311\" rel=\"\" target=\"_blank\">BC
Children’s Hospital
Foundation</a></div>\n</div></div>\n</div>\n</div></div>\n</div>\n</div></div>\n</div>\n</div>\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n<div
aria-atomic=\"true\" aria-live=\"assertive\" aria-relevant=\"additions
text\" class=\"a11y-speak-region\"
id=\"a11y-speak-assertive\"></div><div aria-atomic=\"true\"
aria-live=\"polite\" aria-relevant=\"additions text\"
class=\"a11y-speak-region\" id=\"a11y-speak-polite\"></div>"]
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
href="https://www.bcchr.ca/" rel="home"><img alt="BC Children’s
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
href="http://www.bcchildrens.ca/" id="fndry-block-6509f4756b140"
rel="" target="_blank">BC Children’s Hospital</a><a class="fndry-btn
fndry-mb--2 fndry-btn-headerLogin" href="https://www.bcchf.ca/"
id="fndry-block-6414d467f8311" rel="" target="_blank">BC Children’s
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
2026-09-28 14:50:22  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7817388, "visible_chars": 3793,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:22  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://www.bcchr.ca/careers/", "text":
"\n\n\n\n\n\n\n\n\t\n\t\n\t\n\t\n\t\n\tBC Children’s Hospital Research
Institute (BCCHR)Careers\nCareersFurther your career as part of our
vibrant research community.\n\n\n\n\n\n\t\n\t\n\tWorking HereAre you
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
inquiries, contact: hr@bcchr.ca\n\n\t\n\t\n\n\n\n\n\n\t\n\t\<95232
chars omitted>0;height:1px;width:1px;overflow:hidden;clip-path:inset(50%);border:0;word-wrap:normal
!important;word-break:normal !important;\"
hidden=\"\">Notifications</p><div id=\"a11y-speak-assertive\"
class=\"a11y-speak-region\"
style=\"position:absolute;margin:-1px;padding:0;height:1px;width:1px;overflow:hidden;clip-path:inset(50%);border:0;word-wrap:normal
!important;word-break:normal !important;\" aria-live=\"assertive\"
aria-relevant=\"additions text\" aria-atomic=\"true\"></div><div
id=\"a11y-speak-polite\" class=\"a11y-speak-region\"
style=\"position:absolute;margin:-1px;padding:0;height:1px;width:1px;overflow:hidden;clip-path:inset(50%);border:0;word-wrap:normal
!important;word-break:normal !important;\" aria-live=\"polite\"
aria-relevant=\"additions text\" aria-atomic=\"true\"></div></body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 3793, "requested_url":
"https://www.bcchr.ca/careers", "final_url":
"https://www.bcchr.ca/careers/"}}
2026-09-28 14:50:22  [INFO]  469c6744 | telescope job done:
https://www.bcchr.ca/careers -> https://www.bcchr.ca/careers/
fields:text,html
2026-09-28 14:50:22  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:22  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-f44091e44d069562"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:22  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=utmb_edu_2, n=4]
2026-09-28 14:50:22  [DEBUG]  3243: Calling agent.do_task
live_content: <div class="sf_cols">
<div class="sf_colsOut sf_2cols_1_50">
<div class="sf_colsIn sf_2cols_1in_50" id="Body_C014_Col00">
<div class="utmbsf-content-block" utmb-4x-template="ContentBlock.Default">
<p>Neurodiagnostic Technologist II – Epilepsy Monitoring
(Nights)Galveston Campus<a class="btn btn-text"
data-sf-ec-immutable="" href="http://phxc3c.rfer.us/AA083hcqBNx"
target="_blank" title="Click to Apply Now"><span
class="blue-dark"><span class="blue-navy">  Apply
Now</span></span></a></p><p>Neurodiagnostic Technologist II – EMU
(3–12 hour shifts)Galveston Campus<a class="btn btn-text"
data-sf-ec-immutable=""
href="https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161"
target="_blank" title="Click to Apply Now"><span
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
href="http://phxc3c.rfer.us/AA083XSKEb0" target="_blank " title="Click
to Apply Now
    "><span class="teal-dark"><span class="blue-navy">  Apply
Now</span></span></a></p>
</div>
</div>
</div>
</div>
2026-09-28 14:50:22  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=utmb_edu_2
2026-09-28 14:50:22  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Neurodiagnostic Technologist II –
Epilepsy Monitoring (Nights)", "Neurodiagnostic Technologist II – EMU
(3–12 hour shifts)", "Laboratory Services Manager – Blood Bank"]
containers=["<div class=\"sf_cols\">\n<div class=\"sf_colsOut
sf_2cols_1_50\">\n<div class=\"sf_colsIn sf_2cols_1in_50\"
id=\"Body_C014_Col00\">\n<div class=\"utmbsf-content-block\"
utmb-4x-template=\"ContentBlock.Default\">\n<p>Neurodiagnostic
Technologist II – Epilepsy Monitoring (Nights)Galveston Campus<a
class=\"btn btn-text\" data-sf-ec-immutable=\"\"
href=\"http://phxc3c.rfer.us/AA083hcqBNx\" target=\"_blank\"
title=\"Click to Apply Now\"><span class=\"blue-dark\"><span
class=\"blue-navy\">  Apply
Now</span></span></a></p><p>Neurodiagnostic Technologist II – EMU
(3–12 hour shifts)Galveston Campus<a class=\"btn btn-text\"
data-sf-ec-immutable=\"\"
href=\"https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161\"
target=\"_blank\" title=\"Click to Apply Now\"><span
class=\"blue-dark\"><span class=\"blue-navy\">  Apply
Now</span></span></a></p>\n</div>\n</div>\n</div>\n<div
class=\"sf_colsOut sf_2cols_2_50\">\n<div class=\"sf_colsIn
sf_2cols_2in_50\" id=\"Body_C014_Col01\">\n<div
class=\"utmbsf-content-block\"
utmb-4x-template=\"ContentBlock.Default\">\n<p>Laboratory Services
Manager – Blood BankGalveston Campus<a class=\"btn btn-text\"
data-sf-ec-immutable=\" \" href=\"http://phxc3c.rfer.us/AA083XSKEb0\"
target=\"_blank \" title=\"Click to Apply Now\n    \"><span
class=\"teal-dark\"><span class=\"blue-navy\">  Apply
Now</span></span></a></p>\n</div>\n</div>\n</div>\n</div>"]
cull_outcome='culled' dom_joined=<div class="sf_cols">
<div class="sf_colsOut sf_2cols_1_50">
<div class="sf_colsIn sf_2cols_1in_50" id="Body_C014_Col00">
<div class="utmbsf-content-block" utmb-4x-template="ContentBlock.Default">
<p>Neurodiagnostic Technologist II – Epilepsy Monitoring
(Nights)Galveston Campus<a class="btn btn-text"
data-sf-ec-immutable="" href="http://phxc3c.rfer.us/AA083hcqBNx"
target="_blank" title="Click to Apply Now"><span
class="blue-dark"><span class="blue-navy">  Apply
Now</span></span></a></p><p>Neurodiagnostic Technologist II – EMU
(3–12 hour shifts)Galveston Campus<a class="btn btn-text"
data-sf-ec-immutable=""
href="https://aa083.referrals.selectminds.com/jobs/neurodiagnostic-tech-ii-emu-nights-partial-36-hrs-3-12hr-shifts-17161"
target="_blank" title="Click to Apply Now"><span
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
href="http://phxc3c.rfer.us/AA083XSKEb0" target="_blank " title="Click
to Apply Now
    "><span class="teal-dark"><span class="blue-navy">  Apply
Now</span></span></a></p>
</div>
</div>
</div>
</div>
2026-09-28 14:50:22  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7811826, "visible_chars": 30662,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:22  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://www.utmb.edu/hr/careers", "text":
"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\t\n\n\n\n
\n\n\n\n\n    \n    \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n     \n
  \n\n\n    UTMB Health CareersExplore your passions. Lead the way in
health care innovation. Make groundbreaking discoveries. Transform
your career. External Applicants\n\n\n \n\n Current UTMB
Employees\n\n\n \n\n Contract & Per Diem Staff\n \n\n\n     \n\n    \n
       \n    \n        \n    \n        \n    \n        \n    \n    \n
  \n    \n    \n     \n    \n     \n    \n     \n    \n\n\n    \n\n
\n\n    \n\n            \n        \n    \n\n            \n        \n
 \n\n    \n\n    \nSet the Standards of Health CareUTMB Health is on a
mission to improve health for the people of Texas and around the
world. Our employees share a deep commitment to serving our students
and patients in innovative ways, and we are looking for inspired
individuals to join our team. Your accomplishments here will <140030
chars omitted>;;(function() {\n                        function
loadHandler() {\n                            var hf =
$get('ctl06_TSSM');\n                            if (!hf._RSSM_init) {
hf._RSSM_init = true; hf.value = ''; }\n
hf.value += ';Telerik.Sitefinity.Resources, Version=15.4.8636.0,
Culture=neutral,
PublicKeyToken=b28c218413bdf563:en:e3c1f54b-3ea5-4781-8854-7c87826645f0:7a90d6a';\n
                           Sys.Application.remove_load(loadHandler);\n
                       };\n
Sys.Application.add_load(loadHandler);\n
})();//]]>\n</script>\n</form> \n\n\n\n\n\n\n\n<script id=\"\"
text=\"\" charset=\"\" type=\"text/javascript\"
src=\"https://tag.simpli.fi/sifitag/7d9f25e0-d1df-0139-90f8-06b4c2516bae\"></script></body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 30662, "requested_url":
"https://www.utmb.edu/hr/careers", "final_url":
"https://www.utmb.edu/hr/careers"}}
2026-09-28 14:50:22  [INFO]  0b44fff6 | telescope job done:
https://www.utmb.edu/hr/careers -> https://www.utmb.edu/hr/careers
fields:text,html
2026-09-28 14:50:22  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:22  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-4e9e9ac800d86f29"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:22  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=sc_edu, n=4]
2026-09-28 14:50:22  [DEBUG]  3243: Calling agent.do_task
live_content: Google Tag Manager (noscript)
<a href="#main-content" id="skiptocontent">Skip to Content</a><div
id="main-wrapper">
<div class="row hide-for-medium">
<div class="column small-6 mobile-head"><a class="logo"
href="https://www.sc.edu">University of South Carolina Home</a></div>
<div class="column small-6">

</div>
</div>

<div class="search-wrapper">

Search sc.edu


</div>


<div class="column grid_12 main-nav_top"><a class="main-logo"
href="https://sc.edu">
<img alt="University of South Carolina Home"/>
</a>

Search sc.edu



</div>
<div class="column grid_12 main-nav_bottom"><ul class="nav-links"><li
class="main-nav-link"><a href="/study/index.php">Study</a><div
class="flyout"><ol><li><a href="/study/index.php">Study at South
Carolina</a></li><li><a
href="/study/majors_and_degrees/index.php">Majors and Degrees at South
Carolina</a></li><li><a
href="/study/undergraduate-education/index.php">Undergraduate
Education</a></li><li><a
href="/study/graduate-education/index.php">Graduate Educ<25624 chars
omitted> of South Carolina</a>
<a href="https://www.sc.edu/about/notices/privacy/"><span>Privacy</span></a>
<a href="https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/">Student
Consumer Information</a>
<a class="regional-link"
href="https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php">Student
Consumer Information</a>
<a href="https://spend.admin.sc.edu/">Transparency Initiative</a>
<a href="https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php">Civil
Rights and Title IX</a>
<a href="https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php">Digital
Accessibility</a>
<a href="https://www.sc.edu/about/contact/">Contact</a>

</div>
</div>
</div>


</div>



<a href="https://a.cms.omniupdate.com/11/?skin=sc&amp;account=University_South_Carolina&amp;site=USC_Columbia&amp;action=de&amp;path=/about/employment/index.pcf"
id="de">©</a>
2026-09-28 14:50:22  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=sc_edu
2026-09-28 14:50:22  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Assistant Director, Facilities"]
containers=["Google Tag Manager (noscript) \n<a href=\"#main-content\"
id=\"skiptocontent\">Skip to Content</a><div id=\"main-wrapper\">
\n<div class=\"row hide-for-medium\">\n<div class=\"column small-6
mobile-head\"><a class=\"logo\" href=\"https://www.sc.edu\">University
of South Carolina Home</a></div>\n<div class=\"column
small-6\">\n\n</div>\n</div>\n\n<div
class=\"search-wrapper\">\n\nSearch sc.edu\n\n\n</div>\n\n\n<div
class=\"column grid_12 main-nav_top\"><a class=\"main-logo\"
href=\"https://sc.edu\">\n<img alt=\"University of South Carolina
Home\"/>\n</a>\n\nSearch sc.edu\n\n\n\n</div>\n<div class=\"column
grid_12 main-nav_bottom\"><ul class=\"nav-links\"><li
class=\"main-nav-link\"><a href=\"/study/index.php\">Study</a><div
class=\"flyout\"><ol><li><a href=\"/study/index.php\">Study at South
Carolina</a></li><li><a
href=\"/study/majors_and_degrees/index.php\">Majors and Degrees at
South Carolina</a></li><li><a
href=\"/study/undergraduate-education/index.php\">Undergraduate
Education</<26807 chars
omitted>//www.sc.edu/about/notices/privacy/\"><span>Privacy</span></a>\n<a
href=\"https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/\">Student
Consumer Information</a>\n<a class=\"regional-link\"
href=\"https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php\">Student
Consumer Information</a>\n<a
href=\"https://spend.admin.sc.edu/\">Transparency Initiative</a>\n<a
href=\"https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php\">Civil
Rights and Title IX</a>\n<a
href=\"https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php\">Digital
Accessibility</a>\n<a
href=\"https://www.sc.edu/about/contact/\">Contact</a>\n\n</div>\n</div>\n</div>\n\n\n</div>\n\n\n\n<a
href=\"https://a.cms.omniupdate.com/11/?skin=sc&amp;account=University_South_Carolina&amp;site=USC_Columbia&amp;action=de&amp;path=/about/employment/index.pcf\"
id=\"de\">©</a>"] cull_outcome='full_dom' dom_joined=Google Tag
Manager (noscript)
<a href="#main-content" id="skiptocontent">Skip to Content</a><div
id="main-wrapper">
<div class="row hide-for-medium">
<div class="column small-6 mobile-head"><a class="logo"
href="https://www.sc.edu">University of South Carolina Home</a></div>
<div class="column small-6">

</div>
</div>

<div class="search-wrapper">

Search sc.edu


</div>


<div class="column grid_12 main-nav_top"><a class="main-logo"
href="https://sc.edu">
<img alt="University of South Carolina Home"/>
</a>

Search sc.edu



</div>
<div class="column grid_12 main-nav_bottom"><ul class="nav-links"><li
class="main-nav-link"><a href="/study/index.php">Study</a><div
class="flyout"><ol><li><a href="/study/index.php">Study at South
Carolina</a></li><li><a
href="/study/majors_and_degrees/index.php">Majors and Degrees at South
Carolina</a></li><li><a
href="/study/undergraduate-education/index.php">Undergraduate
Education</a></li><li><a
href="/study/graduate-education/index.php">Graduate Educ<25624 chars
omitted> of South Carolina</a>
<a href="https://www.sc.edu/about/notices/privacy/"><span>Privacy</span></a>
<a href="https://www.sc.edu/about/offices_and_divisions/financial_aid/forms_and_resources/student_consumer_information/">Student
Consumer Information</a>
<a class="regional-link"
href="https://www.sc.edu/about/system_and_campuses/palmetto_college/internal/financial_aid/consumer_information/index.php">Student
Consumer Information</a>
<a href="https://spend.admin.sc.edu/">Transparency Initiative</a>
<a href="https://www.sc.edu/about/offices_and_divisions/civil_rights_title_ix/index.php">Civil
Rights and Title IX</a>
<a href="https://www.sc.edu/about/offices_and_divisions/digital-accessibility/index.php">Digital
Accessibility</a>
<a href="https://www.sc.edu/about/contact/">Contact</a>

</div>
</div>
</div>


</div>



<a href="https://a.cms.omniupdate.com/11/?skin=sc&amp;account=University_South_Carolina&amp;site=USC_Columbia&amp;action=de&amp;path=/about/employment/index.pcf"
id="de">©</a>
2026-09-28 14:50:22  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7809618, "visible_chars": 15674,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:22  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://sc.edu/about/employment/", "text": "\nSkip to
Content         \n         \n         \n\n         \n            \n
           \n               \n                  \n
SC.edu\n                     About\n                     employment\n
                \n               \n               \n
\n                     Employment\n                     \t\n
          When you work at the University of South Carolina, you're
part of a statewide team\n                        of more than 15,000
people. Whether you're with campus services, administrative support\n
                      or teach in the classroom, you're joining an
award-winning workplace.\n                     \n
\n               \n               \t\t\t\t\n               \n
        \n                  \n                     \n
   \n                        \n                        University
employees are part of o<90640 chars omitted>er-style:none;\" alt=\"\"
src=\"https://insight.adsrvr.org/track/pxl/?adv=75p86ce&amp;ct=0:m8uuaom&amp;fmt=3/\"></div>\n<script
type=\"text/javascript\" id=\"\"
charset=\"\">!function(b,e,f,g,a,c,d){b.fbq||(a=b.fbq=function(){a.callMethod?a.callMethod.apply(a,arguments):a.queue.push(arguments)},b._fbq||(b._fbq=a),a.push=a,a.loaded=!0,a.version=\"2.0\",a.queue=[],c=e.createElement(f),c.async=!0,c.src=g,d=e.getElementsByTagName(f)[0],d.parentNode.insertBefore(c,d))}(window,document,\"script\",\"https://connect.facebook.net/en_US/fbevents.js\");fbq(\"init\",\"1438055863158990\");fbq(\"track\",\"PageView\");</script>\n<noscript><img
height=\"1\" width=\"1\" style=\"display:none\"
src=\"https://www.facebook.com/tr?id=1438055863158990&amp;ev=PageView&amp;noscript=1\"></noscript>\n</body>",
"scrape_meta": {"bot_blocked": false, "cookies_dismissed": false,
"issues": [], "content_chars": 15674, "requested_url":
"https://sc.edu/about/employment", "final_url":
"https://sc.edu/about/employment/"}}
2026-09-28 14:50:22  [INFO]  eb844f45 | telescope job done:
https://sc.edu/about/employment -> https://sc.edu/about/employment/
fields:text,html
2026-09-28 14:50:22  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:22  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-b3559635447b6ac3"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:22  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=psy_unihamburg_de, n=4]
2026-09-28 14:50:22  [DEBUG]  3243: Calling agent.do_task
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
2026-09-28 14:50:22  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=psy_unihamburg_de
2026-09-28 14:50:22  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Technische Assistenz im Institut für
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
Hochschulambulanz"] containers=["<table class=\"noautoscale\"
id=\"bewerberportal\"><tr><th>Stellenbezeichnung</th><th>Einrichtung</th><th>Vergütung</th><th>Bewerbungsfrist</th></tr><tr
class=\"datensatz\" data-einrichtung=\",zd,\" data-fuehrung=\"nein\"
data-rid=\"2cd00972f9eab88bd5e0dcbefd4f767c8507c092\"
data-stellentyp=\"i\" data-verg=\"E9A\"
id=\"bewerberportaltr0\"><td><a
href=\"/stellenangebote/ausschreibung.html?jobID=2cd00972f9eab88bd5e0dcbefd4f767c8507c092\">Technische
Assistenz im Institut für Organische Chemie</a><span>Kennziffer</span>
(602/9)</td><td>Fakultät für Mathematik, Informatik und
Naturwissenschaften (Fachbereich Chemie)</td><td>EGR. 9A
TV-L</td><td>28.09.2026</td></tr><tr class=\"datensatz\"
data-einrichtung=\",zd,,zb,\" data-fuehrung=\"nein\"
data-rid=\"b771f9ec22ecb121240cdbf53af62d2550303a7f\"
data-stellentyp=\"d\" data-verg=\"E13\"
id=\"bewerberportaltr1\"><td><a
href=\"/stellenangebote/ausschreibung.html?jobID=b771f9ec22ecb121240cdbf53af62d2550303a7f\">Research
Associate for the Project <15054 chars
omitted>=\"23952bc5eff9a8a908d5d2ed04ca1b446ea0281c\"
data-stellentyp=\"d\" data-verg=\"E13\"
id=\"bewerberportaltr29\"><td><a
href=\"/stellenangebote/ausschreibung.html?jobID=23952bc5eff9a8a908d5d2ed04ca1b446ea0281c\">Wissenschaftliche:r
Mitarbeiter:in § 28 Abs. 1 HmbHG</a><span>Kennziffer</span>
(179)</td><td>Fakultät für Rechtswissenschaft</td><td>EGR. 13
TV-L</td><td>31.10.2026</td></tr><tr class=\"datensatz\"
data-einrichtung=\",za,\" data-fuehrung=\"ja\"
data-rid=\"f640e4898870a5fef69e751fb5ecb1e2466c6864\"
data-stellentyp=\"a\" data-verg=\"W3\"
id=\"bewerberportaltr30\"><td><a
href=\"/stellenangebote/ausschreibung.html?jobID=f640e4898870a5fef69e751fb5ecb1e2466c6864\">W3
Universitätsprofessur für Neuere Geschichte, insbesondere
Zeitgeschichte in Verbindung mit der Position wissenschaftliche:r
Direktor:in der Forschungsstelle für Zeitgeschichte in Hamburg
(FZH)</a><span>Kennziffer</span> (2459/W3)</td><td>Fakultät für
Geisteswissenschaften</td><td>W3</td><td>05.11.2026</td></tr></table>"]
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
2026-09-28 14:50:22  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7797049, "visible_chars": 8028,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:22  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de",
"text": "Zur MetanavigationZur HauptnavigationZur SucheZum InhaltZum
SeitenfußFoto: UHH/EsfandiariStellenangebote der Universität
HamburgHerzlich willkommen im Stellenportal der Universität Hamburg!
Als eine der größten Universitäten Deutschlands verbinden wir ein
vielfältiges und spannendes Lehrangebot mit exzellenter Forschung.
Hier finden sich zahlreiche attraktive Karrierechancen, die auf
neugierige und engagierte Talente warten. Wir freuen uns auf jede
Bewerbung und darauf, gemeinsam die Zukunft zu gestalten!\nInternes
Stellenportal\nJobbörse für Studierende\n\n\n
SucheStellentypStellentyp:
AlleAlleProfessurenJuniorprofessurenVertretung von
ProfessurenWissenschaftliches
PersonalVerwaltungspersonalBibliothekspersonalFremdsprachliches
PersonalIT-PersonalTechnisches
PersonalAusbildungsplätzeVolontariatEinrichtungEinrichtung:
AlleAlleFakultät für Re<67975 chars omitted>Zur Seite
Systemakkreditierung\"
src=\"https://assets.rrz.uni-hamburg.de/assets/AR-Siegel_81x81-aeebcf80607271e52345b193956c4aba9970c59d505a67449d6046fe89deb5a0.svg\"></a></div></div><p
class=\"copyright\">© 2026 Universität Hamburg. Alle Rechte
vorbehalten</p></nav></section></footer></div><div
id=\"sponsors\"></div><script>console.log('document ready: ' +
(Date.now() - t0) + ' ms');\nvar t1 = Date.now();</script><div
class=\"tracking\" style=\"display:none\"><div
class=\"etracker\">OBVZu9</div></div><button type=\"button\"
id=\"scrollTopButton2\" aria-label=\"nach oben scrollen\"
class=\"\"></button></body>", "scrape_meta": {"bot_blocked": false,
"cookies_dismissed": false, "issues": [], "content_chars": 8028,
"requested_url":
"https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de",
"final_url": "https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de"}}
2026-09-28 14:50:22  [INFO]  36b66f0c | telescope job done:
https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de
-> https://www.uni-hamburg.de/stellenangebote.html?etcc_cu=onsite&etcc_cmp_onsite=stellenangebote&etcc_med_onsite=footer-de
fields:text,html
2026-09-28 14:50:22  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:22  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-3ccc68934c550041"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:56  [ERROR]  abrams | dispatch company parse_job_list
  TimeoutError: dispatch timeout after 3600s
batch=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6
  Truncating the batch
Traceback (most recent call last):
  File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 520,
in wait_for
    return await fut
           ^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 1536, in _run_dispatch_loop
    summary = await _run_task(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 910, in _run_task
    summary = await _run_unified(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 831, in _run_unified
    result = await consult.run_consult_task(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 72, in async_wrapper
    return await fn(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2674, in run_consult_task
    r = await _debug_await(
        ^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 113, in _debug_await
    result = await coro
             ^^^^^^^^^^
  File "/app/src/core/roster.py", line 1315, in parse_job_list_batch
    results = await asyncio.gather(
              ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1306, in _one
    result = await run_parse_job_list_dispatch(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1244, in run_parse_job_list_dispatch
    result = await _scrape_and_parse()
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1221, in _scrape_and_parse
    parsed = await _fetch_parse_job_list(dom_joined, short_name,
debug=debug, ctx=ctx)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 3244, in _fetch_parse_job_list
    response = await do_task(
               ^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 103, in wrapper
    return await fn(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 2198, in do_task
    result = await send_to_deepseek(
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/deepseek.py", line 248, in send_to_deepseek
    response = await await_provider_call_with_budget(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/utils/llm_external.py", line 90, in
await_provider_call_with_budget
    done, _pending = await asyncio.wait({task}, timeout=timeout_seconds)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 464, in wait
    return await _wait(fs, timeout, return_when, loop)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 550, in _wait
    await waiter
asyncio.exceptions.CancelledError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1373, in _dispatch_one_body
    await _tracked()
  File "/app/src/core/dispatcher.py", line 1361, in _tracked
    await asyncio.wait_for(
  File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 519,
in wait_for
    async with timeouts.timeout(timeout):
               ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/asyncio/timeouts.py", line
115, in __aexit__
    raise TimeoutError from exc_val
TimeoutError
2026-09-28 14:50:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-d1942fe332469b47"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=cochrane_org_2, n=4]
2026-09-28 14:50:56  [DEBUG]  3243: Calling agent.do_task
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
2026-09-28 14:50:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=cochrane_org_2
2026-09-28 14:50:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Commercial Sales Lead", "Publishing
Operations Lead"] containers=["<ul class=\"listing
listing--news\"><li><div class=\"grid\"><div
class=\"col-1/3@tabletwide\"><a class=\"zoom\"
href=\"/about-us/news/commercial-sales-lead\">\n</a></div>\n<div
class=\"col-2/3@tabletwide\"><p class=\"h6\"><a class=\"zoom\"
href=\"/about-us/news/commercial-sales-lead\">Commercial Sales
Lead</a></p>\n<p class=\"date\">10 September 2026</p>\n<p>6-month
fixed term contract | Full Time | £48k per annum | Remote | Closing
date: 4 October 2026</p>\n</div>\n</div>\n</li><li><div
class=\"grid\"><div class=\"col-1/3@tabletwide\"><a class=\"zoom\"
href=\"/about-us/news/publishing-operations-lead\">\n</a></div>\n<div
class=\"col-2/3@tabletwide\"><p class=\"h6\"><a class=\"zoom\"
href=\"/about-us/news/publishing-operations-lead\">Publishing
Operations Lead</a></p>\n<p class=\"date\">10 September
2026</p>\n<p>Permanent | Full Time | £45k per annum | Remote | Closing
date: 7 October 2026</p>\n</div>\n</div>\n</li></ul>"]
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
2026-09-28 14:50:56  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7854128, "visible_chars": 6734,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:56  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://www.cochrane.org/about-us/jobs", "text": "\n
    \n    \n      \n    \n\n\n\n\n  \n    \n      \n        \n
 \n             Filters\n            Close search ✖\n            \n
          Filters\n              Evidence\n              Our
evidence\n              Exclude our evidence\n
Handbooks/Manuals\n              Cochrane Handbook for Systematic
Reviews of Interventions\n              Methodological Expectations of
Cochrane Intervention Reviews (MECIR)\n              Cochrane Style
Manual\n              News\n              News\n              Exclude
news\n            \n          \n          \n        \n      \n    \n
\n\n\n  \n    \n                    \n          \n            \n
         \n    \n  \n    \n        \n\n  \n\n  \n\n            \n
    \n        \n                                      \n          \n
         \n              \n                  \n    \n  \n    \n
\n  Jobs\n\n\n\n  \n\n  \n\n           <43581 chars
omitted>rackPageView\"]),_paq.push([\"enableLinkTracking\"]),_paq.push([\"enableHeartBeatTimer\"]),function(){_paq.push([\"setTrackerUrl\",\"https://cochrane-org.matomo.cloud/matomo.php\"]),_paq.push([\"setSiteId\",\"1\"]),analytics_cookies&&_paq.push([\"rememberCookieConsentGiven\",43800]);var
e=document,a=e.createElement(\"script\"),t=e.getElementsByTagName(\"script\")[0];a.async=!0,a.src=\"https://cdn.matomo.cloud/cochrane-org.matomo.cloud/matomo.js\",t.parentNode.insertBefore(a,t)}();</script>\n
 \n\n<ul id=\"ui-id-1\" tabindex=\"0\" class=\"ui-menu ui-widget
ui-widget-content ui-autocomplete ui-front\" style=\"display: none;\"
unselectable=\"on\"></ul><div role=\"status\" aria-live=\"assertive\"
aria-relevant=\"additions\"
class=\"ui-helper-hidden-accessible\"></div></body>", "scrape_meta":
{"bot_blocked": false, "cookies_dismissed": true, "issues": [],
"content_chars": 6734, "requested_url":
"https://www.cochrane.org/about-us/jobs", "final_url":
"https://www.cochrane.org/about-us/jobs"}}
2026-09-28 14:50:56  [INFO]  c449dd2c | telescope job done:
https://www.cochrane.org/about-us/jobs ->
https://www.cochrane.org/about-us/jobs fields:text,html
2026-09-28 14:50:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-d58dc7440be3edaa"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=careers_wexnermedical_osu_edu, n=4]
2026-09-28 14:50:56  [DEBUG]  3243: Calling agent.do_task
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
data-href="https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131"
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
data-href="https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73"
data-record-key="e1e331ac-cf28-41dc-addf-1e7c93e87d73" role="link"
tabindex="0"><td class="title-column"><span>Staff Nurse-B (RN)
Emergency Department, University Hospital</span></td><td
class="location-column"><span>University Hospital - Rhodes
Hall</span></td><td class="city-state-column"><span>Columbus,
Ohio</span></td></tr></table>
2026-09-28 14:50:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=careers_wexnermedical_osu_edu
2026-09-28 14:50:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Clinical Research Coordinator-
Neurology", "Clinic Nurse - Thoracic (IRP/Contingent)", "Staff Nurse -
Hematology and Transplant (IRP/Contingent)", "Clinic Nurse (RN) - GU
and Urology", "Research Senior Technician- Microbial Infection and
Immunity", "Associate Nurse Manager - Acute Care - General Medicine",
"CT Lead Tech $15,000 Signing Bonus 3rd shift I UH Inpatient Patient
Tower", "Post Doctoral Scholar - Comprehensive Cancer Center",
"Specialty Practice Pharmacist", "Multi-Modality Imaging Tech $15,000
Signing Bonus"] containers=["<table class=\"jtable ui-widget-content\"
role=\"none\"><tr><th class=\"jtable-column-header title-column
ui-state-default\"><div class=\"jtable-column-header-container\"><span
class=\"jtable-column-header-text\">Job Title</span></div></th><th
class=\"jtable-column-header location-column ui-state-default\"><div
class=\"jtable-column-header-container\"><span
class=\"jtable-column-header-text\">Facility Name</span></div></th><th
class=\"jtable-column-header city-state-column ui-state-default\"><div
class=\"jtable-column-header-container\"><span
class=\"jtable-column-header-text\">City, ST</span></div></th></tr><tr
aria-label=\"Clinical Research Coordinator- Neurology\"
class=\"jtable-data-row jtable-row-even\"
data-href=\"https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131\"
data-record-key=\"c24f9cb5-600c-46a8-b694-2a815db38131\" role=\"link\"
tabindex=\"0\"><td class=\"title-column\"><span>Clinical Rese<5534
chars omitted>du/search/jobdetails/instructor-practice/79b81626-fdad-4e2d-a1e3-17781c197bdd\"
data-record-key=\"79b81626-fdad-4e2d-a1e3-17781c197bdd\" role=\"link\"
tabindex=\"0\"><td
class=\"title-column\"><span>Instructor-Practice</span></td><td
class=\"location-column\"><span>University Hospital - Doan
Hall</span></td><td class=\"city-state-column\"><span>Columbus,
Ohio</span></td></tr><tr aria-label=\"Staff Nurse-B (RN) Emergency
Department, University Hospital\" class=\"jtable-data-row\"
data-href=\"https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73\"
data-record-key=\"e1e331ac-cf28-41dc-addf-1e7c93e87d73\" role=\"link\"
tabindex=\"0\"><td class=\"title-column\"><span>Staff Nurse-B (RN)
Emergency Department, University Hospital</span></td><td
class=\"location-column\"><span>University Hospital - Rhodes
Hall</span></td><td class=\"city-state-column\"><span>Columbus,
Ohio</span></td></tr></table>"] cull_outcome='culled'
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
data-href="https://careers.wexnermedical.osu.edu/search/jobdetails/clinical-research-coordinator--neurology/c24f9cb5-600c-46a8-b694-2a815db38131"
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
data-href="https://careers.wexnermedical.osu.edu/search/jobdetails/staff-nurse-b-rn-emergency-department-university-hospital/e1e331ac-cf28-41dc-addf-1e7c93e87d73"
data-record-key="e1e331ac-cf28-41dc-addf-1e7c93e87d73" role="link"
tabindex="0"><td class="title-column"><span>Staff Nurse-B (RN)
Emergency Department, University Hospital</span></td><td
class="location-column"><span>University Hospital - Rhodes
Hall</span></td><td class="city-state-column"><span>Columbus,
Ohio</span></td></tr></table>
2026-09-28 14:50:56  [DEBUG]  1068: Response from scrape_page:
{"outcome": "ready", "wait_ms": 7827411, "visible_chars": 29894,
"load_all_jobs_ran": true, "ready": true}
2026-09-28 14:50:56  [DEBUG]  566: Response from _post_telescope:
{"final_url": "https://careers.wexnermedical.osu.edu/search/searchjobs",
"text": "\n    \n\n        \n\n    \n\n    \n\n    \n        \n\n
\n    \n        \n    \n    \n    \n    \n    \n    \n\n    \n    \n\n
   \n \n\n\n\n\n\n\n\n\n\n\n    \n    \n\n\n\n\n\n\n\n    \n        \n
           \n                Search Jobs\n            \n            \n
               CareersSearch Jobs\n            \n        \n
\n\n\n\n\n\n\n\n\n        \n\n\n    \n        \n        \n
\n\n\n        \n        \n\n\n\n        \n                        By
Keyword\n                            \n\n        \n        \n
              By Career Area \n Select Career Area\nAcademic
Administration / Academic Program Services\nAcademic Administration /
Academic Success and Enrichment\nAcademic Administration / Career
Services\nAcademic Administration / Registration and Records\nAcademic
Administration / Undergraduate Academic Advising\nAdvanced Practice /
Advanced Practice Education\nAdvan<194931 chars omitted> 0px; display:
none; visibility: hidden;\" id=\"batBeacon424070459294\" width=\"0\"
height=\"0\" alt=\"\"
src=\"https://bat.bing.com/action/0?ti=295024660&amp;tm=gtm002&amp;Ver=2&amp;mid=fc70c9e4-d420-46ed-ace1-d7ce0e6dc328&amp;bo=1&amp;sid=c0f7b830bb3911f196e65bf8e7c5904f&amp;vid=c0f7e3a0bb3911f189c8cfcaddf01653&amp;vids=1&amp;msclkid=N&amp;pi=0&amp;lg=en-US&amp;sw=1280&amp;sh=2000&amp;sc=24&amp;nwd=1&amp;tl=Search%20Jobs%20-%20Ohio%20State%20Medical%20Center&amp;p=https%3A%2F%2Fcareers.wexnermedical.osu.edu%2Fsearch%2Fsearchjobs&amp;r=&amp;lt=2261&amp;evt=pageLoad&amp;sv=2&amp;cdb=AQAQ&amp;rn=377417\"></div><div
style=\"visibility: hidden;\" aria-hidden=\"true\"
id=\"usercentrics-root\"
data-created-at=\"1790599214628\"></div></body>", "scrape_meta":
{"bot_blocked": false, "cookies_dismissed": false, "issues": [],
"content_chars": 29894, "requested_url":
"https://careers.wexnermedical.osu.edu/search/searchjobs",
"final_url": "https://careers.wexnermedical.osu.edu/search/searchjobs"}}
2026-09-28 14:50:56  [INFO]  dd6a600a | telescope job done:
https://careers.wexnermedical.osu.edu/search/searchjobs ->
https://careers.wexnermedical.osu.edu/search/searchjobs
fields:text,html
2026-09-28 14:50:56  [DEBUG]  2174: Calling send_to_deepseek:
[task_key=parse_job_list, provider=deepseek, model=deepseek-v4-pro,
max_tokens=16000, temp=0.3, skip_cache=False, candidate=abrams]
2026-09-28 14:50:56  [DEBUG]  1341: Response from
_store_prompt_blocks: [{"type": "SYSTEM", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-system-e7a2386ffba4938b"},
{"type": "CACHE_A", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-cache_a-9b9feba69a5936a8"},
{"type": "NO_CACHE", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-no_cache-313958e7f7b248bd"},
{"type": "TASK", "id":
"parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6-task-a6ed275e5f09a75d"}]
2026-09-28 14:50:56  [DEBUG]  1335: Calling _store_prompt_blocks:
[entity_type=company, task_key=parse_job_list,
batch_id=parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6,
entity_id=psychiatry_ucsf_edu, n=4]
2026-09-28 14:50:56  [DEBUG]  3243: Calling agent.do_task
live_content: <div class="accordion" data-once="accordion-keep-open"
data-usb-keep-open="false" id="accordion-1521733153">
<div class="accordion-item">
<h2 class="accordion-header" id="heading--accordion-item-908720554">

      Attending Child and Adolescent Psychiatrists (UCSF Health)

</h2>
<div aria-labelledby="heading--accordion-item-908720554"
class="accordion-collapse collapse js-accordion-keep-open"
data-bs-parent="#accordion-1521733153"
data-once="accordion-item-keep-open" id="accordion-item-908720554">
<div class="accordion-body">
<p>UCSF Health is currently recruiting for a variety of vacant
child/adolescent psychiatry positions in both inpatient and outpatient
services.</p>
<p>Applications will be held and reviewed based on availability of
positions and funding. These positions will be filled in a rank and
series commensurate with experience.</p>
<p><a class="btn btn-primary"
href="https://aprecruit.ucsf.edu/JPF05824" target="_blank">Find out
more and apply</a></p>
</div>
</div>
</div<8066 chars omitted> Mental Health Clinician-Educator (San
Francisco VA Health Care System)

</h2>
<div aria-labelledby="heading--accordion-item-1915671055"
class="accordion-collapse collapse js-accordion-keep-open"
data-bs-parent="#accordion-1521733153"
data-once="accordion-item-keep-open" id="accordion-item-1915671055">
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
href="https://aprecruit.ucsf.edu/JPF05634" target="_blank">Find out
more and apply</a></p>
</div>
</div>
</div>
</div>
2026-09-28 14:50:56  [DEBUG]  3242: Calling agent.do_task:
task_key=parse_job_list index=psychiatry_ucsf_edu
2026-09-28 14:50:56  [DEBUG]  1212: Response from
_culled_dom_for_parse: titles=["Attending Child and Adolescent
Psychiatrists (UCSF Health)", "Attending Child and Adolescent
Psychologist (UCSF Health)", "Attending Psychiatrists (UCSF Health)",
"Attending Psychologist (Behavioral Sleep Medicine)", "Attending
Psychologist (OCD Program)", "Attending Psychologist (UCSF Health)",
"Attending Psychologist (Zuckerberg San Francisco General Hospital and
Trauma Center)", "Attending Public Psychiatrists (Zuckerberg San
Francisco General Hospital and Trauma Center)", "Clinical and
Translational Researcher", "Mental Health Clinician-Educator (San
Francisco VA Health Care System)"] containers=["<div
class=\"accordion\" data-once=\"accordion-keep-open\"
data-usb-keep-open=\"false\" id=\"accordion-1521733153\">\n<div
class=\"accordion-item\">\n<h2 class=\"accordion-header\"
id=\"heading--accordion-item-908720554\">\n\n      Attending Child and
Adolescent Psychiatrists (UCSF Health)\n    \n</h2>\n<div
aria-labelledby=\"heading--accordion-item-908720554\"
class=\"accordion-collapse collapse js-accordion-keep-open\"
data-bs-parent=\"#accordion-1521733153\"
data-once=\"accordion-item-keep-open\"
id=\"accordion-item-908720554\">\n<div
class=\"accordion-body\">\n<p>UCSF Health is currently recruiting for
a variety of vacant child/adolescent psychiatry positions in both
inpatient and outpatient services.</p>\n<p>Applications will be held
and reviewed based on availability of positions and funding. These
positions will be filled in a rank and series commensurate with
experience.</p>\n<p><a class=\"btn btn-primary\"
href=\"https://aprecruit.ucsf.edu/JPF05824\" target=\"_blank\">Find
o<8455 chars omitted>tor (San Francisco VA Health Care System)\n
\n</h2>\n<div aria-labelledby=\"heading--accordion-item-1915671055\"
class=\"accordion-collapse collapse js-accordion-keep-open\"
data-bs-parent=\"#accordion-1521733153\"
data-once=\"accordion-item-keep-open\"
id=\"accordion-item-1915671055\">\n<div
class=\"accordion-body\">\n<p>The Department of Psychiatry at the
University of California, San Francisco invites applications from
Clinician Educator members of the SFVAHCS Mental Health Service for a
UCSF affiliate-paid faculty appointment. Applications will be held and
reviewed based on availability of SFVAHCS Mental Health Service
positions and funding. Start dates are variable, and these positions
will be filled in the UC HS Clinical Professor or Professor of
Clinical Psychiatry series at the rank commensurate with
experience.</p>\n<p><a class=\"btn btn-primary\"
href=\"https://aprecruit.ucsf.edu/JPF05634\" target=\"_blank\">Find
out more and apply</a></p>\n</div>\n</div>\n</div>\n</div>"]
cull_outcome='culled' dom_joined=<div class="accordion"
data-once="accordion-keep-open" data-usb-keep-open="false"
id="accordion-1521733153">
<div class="accordion-item">
<h2 class="accordion-header" id="heading--accordion-item-908720554">

      Attending Child and Adolescent Psychiatrists (UCSF Health)

</h2>
<div aria-labelledby="heading--accordion-item-908720554"
class="accordion-collapse collapse js-accordion-keep-open"
data-bs-parent="#accordion-1521733153"
data-once="accordion-item-keep-open" id="accordion-item-908720554">
<div class="accordion-body">
<p>UCSF Health is currently recruiting for a variety of vacant
child/adolescent psychiatry positions in both inpatient and outpatient
services.</p>
<p>Applications will be held and reviewed based on availability of
positions and funding. These positions will be filled in a rank and
series commensurate with experience.</p>
<p><a class="btn btn-primary"
href="https://aprecruit.ucsf.edu/JPF05824" target="_blank">Find out
more and apply</a></p>
</div>
</div>
</div<8066 chars omitted> Mental Health Clinician-Educator (San
Francisco VA Health Care System)

</h2>
<div aria-labelledby="heading--accordion-item-1915671055"
class="accordion-collapse collapse js-accordion-keep-open"
data-bs-parent="#accordion-1521733153"
data-once="accordion-item-keep-open" id="accordion-item-1915671055">
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
href="https://aprecruit.ucsf.edu/JPF05634" target="_blank">Find out
more and apply</a></p>
</div>
</div>
</div>
</div>
```

### Comments

#### chuckles — 2026-09-29T01:36:29.748Z
@susan finish-up is stuck: `gh` 2.46 fails `gh pr edit 185` on every try (GitHub retired Projects (classic)), and nothing has landed. Upgrade `gh`, approve a `gh api` PATCH fix to `create-dev-pr.py`, or merge PR #185 by hand, then hand the parent back to me at PR Ready.

#### chuckles — 2026-09-28T20:52:52.740Z
[check-linear] answered — loop teardown is already fixed for dispatch threads on dev; a smaller gap remains for asyncio.run callers (@susan)

**Correction to my last reply:** Proposed step 3 is no longer outstanding for dispatch threads. `c86d8b5c` ("fix(dispatch): … telescope cleanup", on dev via `2ebfa611` at 19:28 UTC) already does what I recommended:
- `_TelescopeQueue.aclose_current_loop()` pops this loop's `_LoopState`, cancels the poller and wake tasks, and closes the listener and pool.
- `close_loop_resources()` is the module-level entry point for that.
- `dispatcher._task_thread_target` runs `close_loop_resources()`, then `_cancel_pending_tasks(loop)`, then `loop.close()`. That's the exact path that produced the 12:40:33 "Event loop is closed" / "Task was destroyed" errors.

**What's left:** the one-shot `asyncio.run(...)` callers (for example `gazer.py:1482`, `intake.py:739`, and `asyncio.run` in the `api_*` Flask handlers) still close their loop without calling `close_loop_resources()`. `_TelescopeQueue._state()` only forgets closed loops from its dict; it never closes their pool. Any of those paths that touches Telescope can still log the same teardown errors.

**Cleanest fix (recommended):** add one helper next to `close_loop_resources`, for example `run_with_cleanup(coro)`. It would call `asyncio.run` on a wrapper that awaits `coro` and then awaits `close_loop_resources()` in a `finally`. Then swap `asyncio.run` for it at the call sites that can reach Telescope. That's one owner of the teardown rule and no per-site copies. `plan-fix` would list the exact call sites.

**Alternatives I'd skip:**
- Letting `_state()` close stale pools lazily doesn't work: the loop is already closed, so the asyncpg close can't run.
- A process-wide `atexit` hook only runs at exit and misses per-request loops.

**Net for this ticket:** the stall is resolved on dev (AST-1840) and the dispatch-thread teardown is fixed (`c86d8b5c`). Only the `asyncio.run` gap is left. To close as resolved, move to Done. To pursue the helper, assign to Chuckles and I'll narrow the scope sections to it.

#### susan — 2026-09-28T20:51:51.260Z
@chuckles What is the cleanest recommended solution to the Loop teardown chaos?

#### chuckles — 2026-09-28T20:44:03.786Z
[check-linear] answered — mostly resolved on dev; one small item still open (@susan)

- **Description:** the full original log is back at the bottom, inside a `text` code block. I decoded it from the attached alert email, so there are no markdown escapes.
- **Main stall (Proposed step 2): resolved on dev.** AST-1840 (`fb472a98`, part of AST-1838 "parse_job_list event loop block", on dev via #176 at 19:18 UTC) moves the DOM culls off the event loop (`asyncio.to_thread` at `roster.py` 1220 / 2714 / 2780 and in `telescope.extract_page_dom`). It also fixes the quadratic `_cull_html` (a bs4 `Tag.__hash__` membership test). This batch ran 12:39–14:50 UTC, before that landed, so it hit the old code.
- **Loop teardown noise (Proposed step 3): still outstanding.** `dispatcher._task_thread_target` still calls `loop.close()` with no telescope per-loop cleanup, and `_TelescopeQueue` has no shutdown for `_LoopState` (pool, listener, poller). This produced the 12:40:33 "Event loop is closed" / "Task was destroyed" errors. It's noisy but didn't cause the stall.
- **Summary undercount (Proposed step 4):** I didn't verify it this pass.
- **Your call:** close this as resolved by AST-1838/AST-1840, or keep it narrowed to the telescope loop teardown (step 3). To continue with the narrowed fix, assign to Chuckles.

#### susan — 2026-09-28T20:41:06.208Z
@chuckles First, please update the description of this bug to enclose the original log content in a codeblock to make scrolling easier.  Then, do a quick look through the latest code on the dev branch and confirm if this issue's proposed fix is still outstanding or if it has been resolved with more recent code on dev.

---

_Implementation detail may live in git history on `origin/dev`._
