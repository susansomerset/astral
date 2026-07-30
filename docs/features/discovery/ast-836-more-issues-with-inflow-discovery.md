# AST-836 — More issues with inflow_discovery

<!-- linear-archive: AST-836 archived 2026-07-29 -->

## Linear archive (AST-836)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-836/more-issues-with-inflow-discovery  
**Status at archive:** Archive  
**Project:** Astral Discovery  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Had this log content, history declared 1 error for the whole batch (which is fine), but no new companies were added to company (that I can see).

```
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='HIPAA compliance and your digital copier Read more PAUBOX' url='https://www.instagram.com/p/DaDiGb0GVC-/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Project Manager – SaaS Implementations (Government & Healthcare)' url='https://www.linkedin.com/jobs/view/project-manager-%E2%80%93-saas-implementations-government-healthcare-at-council-capital-4423182973'
[2026-06-30 23:55:15] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:55:15] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 10/20 high-touch customer success enterprise B2B -> 100 hit(s)
[2026-06-30 23:55:15] INFO src.core.roster:  | search_term='high-touch customer success enterprise B2B' raw_hits=100
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='How our demand gen manager created an ad campaign in a day' url='https://hightouch.com/blog/day-in-the-life-ad-studio'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Senior • Manager of Client Success • Chicago, IL | MindPal Jobs' url='https://mindpal.co/jobs/75348'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Introducing Lifecycle Studio - Hightouch' url='https://hightouch.com/blog/introducing-lifecycle-studio'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Manager of Customer Success at Steer.io - Remote - RemoteLeaf' url='https://remoteleaf.com/company/steerio/manager-of-customer-success-united-states-2/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Solutions Engineer, Mid-Market (Pre-Sales) - Greenhouse' url='https://job-boards.greenhouse.io/hightouch/jobs/6104620004'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Apply to Head of Implementation at AccelerateHC - Recruiterflow' url='https://recruiterflow.com/acceleratehc/jobs/549?widget=1'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Senior Director, Regional Customer Success (AMER) - Vonage' url='https://www.vonage.com/careers/job-details/8591899002/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Senior Director, Regional Customer Success (AMER) - LinkedIn' url='https://www.linkedin.com/jobs/view/senior-director-regional-customer-success-amer-at-vonage-4429846463'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Remote Enterprise Customer Success Manager at Dutchie - NoDesk' url='https://nodesk.co/remote-jobs/dutchie-enterprise-customer-success-manager/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Customer Success Manager, Enterprise - Dealpath - LinkedIn' url='https://www.linkedin.com/jobs/view/customer-success-manager-enterprise-at-dealpath-4428317068'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Head of Technical Account Management (West) - Mediabistro' url='https://www.mediabistro.com/jobs/3540982539-head-of-technical-account-management-west'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='High Touch Implementation Specialist - Americas - PST - Ashby' url='https://builtin.com/job/high-touch-implementation-specialist-americas-pst/9930463'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Senior Manager, Solutions Builder - Germany - Salesforce' url='https://www.salesforce.com/company/careers/jobs/JR349033/senior-manager-solutions-builder/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='5 Best Lead Generation Companies in New York for 2026' url='https://www.callboxinc.com/blog/lead-generation-companies-new-york/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Principal Customer Success Manager, Strategic - 2.halvolink' url='https://2.halvolink.liveblog365.com/job/2656654'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Senior Bilingual Customer Success Manager (French & English)' url='https://ca.linkedin.com/jobs/view/senior-bilingual-customer-success-manager-french-english-b2b-saas-at-dext-4434355733'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Mid-Market Customer Success Manager - America - EU Remote Jobs' url='https://euremotejobs.com/job/mid-market-customer-success-manager-america/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Regional Director, Customer Success - Virtual Vocations' url='https://www.virtualvocations.com/job/regional-director-customer-success-3117638-i.html'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Ditch Pain Point and Pitch the "Gain Point" in Your 2026 Outreach' url='https://shivyaanchi.com/b2b-ditch-pain-point-and-pitch-the-gain-point-in-your-2026-outreach/'
[2026-06-30 23:55:15] INFO src.core.roster:  | hit title='Mastering Customer Retention Cost in 2026 - Sprints & Sneakers' url='https://www.sprintsandsneakers.com/insights/customer-retention-cost'
[2026-06-30 23:55:15] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:55:15] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 11/20 insurance claims automation platform -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'insurance claims automation platform': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 12/20 insurtech payment processing for carriers -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'insurtech payment processing for carriers': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 13/20 legal practice management platform B2B -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'legal practice management platform B2B': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 14/20 manufacturing execution system cloud -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'manufacturing execution system cloud': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 15/20 medical device quality assurance cloud -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'medical device quality assurance cloud': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 16/20 municipal citizen services software -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'municipal citizen services software': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 17/20 pharma quality management cloud -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'pharma quality management cloud': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 18/20 professional services automation platform -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'professional services automation platform': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 19/20 regulatory compliance platform for financial services -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'regulatory compliance platform for financial services': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] INFO src.core.roster: roster.run_inflow_discovery_batch index 20/20 supply chain visibility platform enterprise -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'supply chain visibility platform enterprise': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-30 23:55:15] ERROR dispatch.scheduler: [inflow_discovery/inflow_discovery-c650e03b-4e43-4745-9b2a-ffba9855cedc] crashed
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 544, in _dispatch_one
    await _tracked()
  File "/app/src/core/dispatcher.py", line 534, in _tracked
    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)
  File "/app/src/core/dispatcher.py", line 663, in _run_dispatch_loop
    summary = await _run_task(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 434, in _run_task
    summary = await _run_unified(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 375, in _run_unified
    results = await _warm_then_gather(_one, entities, _SUMMARY_ZERO)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 71, in _warm_then_gather
    first = await one_fn(entities[0])
            ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2045, in run_consult_task
    return await roster.run_inflow_discovery_batch(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 841, in run_inflow_discovery_batch
    ok, outcome = record_inflow_discovery_hit(candidate_id, hit, index=hit_i)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 379, in record_inflow_discovery_hit
    save_company(
  File "/app/src/data/database.py", line 1069, in save_company
    _remove_jobs_by_company(short_name)
  File "/app/src/data/database.py", line 1326, in _remove_jobs_by_company
    _ensure_job_schema(conn)
  File "/app/src/data/database.py", line 1379, in _ensure_job_schema
    conn.execute(f"""
sqlite3.IntegrityError: UNIQUE constraint failed: job.company, job.job_title, job.company_job_id
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Corporate Financial Reporting Manager in Milwaukee, Wisconsin ...' url='https://careers.paysbig.com/us/en/job/CORPO004236/Corporate-Financial-Reporting-Manager'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Market Assessments: A Guide for Growth and Capital Strategy - DFIN' url='https://www.dfinsolutions.com/knowledge-hub/blog/what-is-a-market-assessment'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='AS 2201: An Audit of Internal Control Over Financial Reporting That ...' url='https://pcaobus.org/oversight/standards/auditing-standards/details/as-2201--an-audit-of-internal-control-over-financial-reporting-that-is-integrated-with-an-audit-of-financial-statements-(effective-on-12-15-2026)'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Analyst II, Regulatory - Jobs | Southern Company' url='https://southerncompany-gas.jobs/atlanta-ga/analyst-ii-regulatory/EB0BFA83EEAD4E28BED4C831977F96DB/job/'
[2026-06-30 23:55:07] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:55:07] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:55:07] INFO src.core.roster: roster.run_inflow_discovery_batch index 8/20 government permitting and licensing platform -> 100 hit(s)
[2026-06-30 23:55:07] INFO src.core.roster:  | search_term='government permitting and licensing platform' raw_hits=100
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Government Operations Management Software - Infor' url='https://www.infor.com/en/industries/public-sector/government-operations'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Engineering, Floodplain Permitting & Right-of-Way - Galveston County' url='https://www.galvestoncountytx.gov/county-offices/engineering-right-of-way'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='POSSE ELS: Enterprise Licensing System - Computronix' url='https://www.computronix.com/government-software-solutions/enterprise-licensing-system/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Providence' url='https://providenceri.portal.opengov.com/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title="Meet Tennessee's 30-Day Permit Rule: HB2552 Guide - OpenGov" url='https://opengov.com/article/hb2552-30-day-permit-rule/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='AI Adoption in Permitting & Licensing: A Practical...' url='https://www.tylertech.com/resources/resource-downloads/ai-adoption-in-permitting-licensing-a-practical-guide'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Customer Stories - OpenGov' url='https://opengov.com/customers/all/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='licensing and permits Service | National Platform (National Portal)' url='https://my.gov.sa/en/services/1394549'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Flyer: AI in Enterprise Permitting & Licensing - Tyler Technologies' url='https://www.tylertech.com/resources/resource-downloads/flyer-ai-in-enterprise-permitting-licensing'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='City of Jersey City: Home' url='https://www.jerseycitynj.gov/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Access2Pay - LLM Information Page' url='https://access2pay.com/llm-info/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Construction licenses - خدمات بلدي | Balady Platform' url='https://balady.gov.sa/en/all-products/10470'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='OaklandCA.gov' url='https://www.oaklandca.gov/Home'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='The City of Las Cruces' url='https://lascruces.gov/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Best Practices for Running a Thriving Community in 2026' url='https://www.centralsquare.com/resources/articles/best-practices-for-running-a-thriving-community-in-2026'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Property Information and Reports | Saint Paul Minnesota' url='https://www.stpaul.gov/departments/safety-inspections/report-concern/property-information-and-reports'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='services.mde.maryland. gov/Application/SearchPermitTypes' url='https://www.facebook.com/MDEnvironment/posts/have-you-heard-you-can-now-apply-for-over-50-types-of-permits-on-our-environment/1432533088903950/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Building Permits - Reno.gov' url='https://reno.gov/business-development/development-services/building-permits.php'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='ACP-backed Schneider Geospatial picks up govtech firm New ...' url='https://www.pehub.com/acp-backed-schneider-geospatial-picks-up-govtech-firm-new-england-geosystems/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Schneider Geospatial Adds New England GeoSystems' url='https://lasvegassun.com/news/2026/jun/24/schneider-geospatial-adds-new-england-geosystems/'
[2026-06-30 23:55:07] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:55:07] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:55:07] INFO src.core.roster: roster.run_inflow_discovery_batch index 9/20 healthcare compliance management SaaS -> 100 hit(s)
[2026-06-30 23:55:07] INFO src.core.roster:  | search_term='healthcare compliance management SaaS' raw_hits=100
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Compliance Startups funded by Y Combinator (YC) 2026' url='https://www.ycombinator.com/companies/industry/compliance'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Oreste Cipolla | Partner - White & Case LLP' url='https://www.whitecase.com/people/oreste-cipolla'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='SOC 2 vs. HIPAA: Key Differences Every Healthcare Technology ...' url='https://circle.healthcare/blogs/soc2-vs-hipaa-healthcare-tech-vendors/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='A Complete Overview of SaaS Compliance - Sprinto' url='https://sprinto.com/blog/saas-compliance-guide/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Top 10 Healthcare Workforce Management Software (2026)' url='https://www.varshealth.com/post/healthcare-workforce-management-software-comparison'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='SaaS Security Posture Management (SSPM) Solution Brief' url='https://www.paloaltonetworks.com/resources/datasheets/saas-security-posture-management'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Data Analytics & Reporting | Wolters Kluwer' url='https://www.wolterskluwer.com/en/about-us/data-and-reporting'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Sales Tax on SaaS: State-by-State Guide (2026 Update)' url='https://www.numeral.com/blog/sales-tax-on-saas'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Senior Product Manager – Rural Health Managed Services' url='https://www.builtinboston.com/job/senior-product-manager-rural-health-managed-services/9966525'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Introduction of CT License Intelligence | Wolters Kluwer' url='https://www.wolterskluwer.com/en/news/introduction-of-ct-license-intelligence'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Healthcare Cybersecurity Services // Echelon Risk + Cyber' url='https://echeloncyber.com/industries/healthcare-cybersecurity-services'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Meihua International pivots into healthcare SaaS | MHUAF SEC Filing' url='https://www.stocktitan.net/sec-filings/MHUAF/6-k-meihua-international-medical-technologies-co-ltd-current-report-f-805d2623fbc5.html'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='HealthcareInfoSecurity: Healthcare infosec news, training, education' url='https://www.healthcareinfosecurity.com/'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Director, Risk & Compliance Management at Parexel' url='https://jobs.parexel.com/en/job/reino-unido/director-risk-and-compliance-management/877/97086807856'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Kieran Lynch | VP of Global Sales - ViClarity' url='https://www.viclarity.com/eu/about/executive-team/kieran-lynch'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='[Remote] Project Manager - 2.halvolink' url='https://2.halvolink.liveblog365.com/job/2684672'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='Compliance & Quality Manager - Myworkdayjobs.com' url='https://iqvia.wd1.myworkdayjobs.com/en-US/IQVIA/job/Compliance---Quality-Manager_R1550658'
[2026-06-30 23:55:07] INFO src.core.roster:  | hit title='r/SaaS on Reddit: Looking for smart builders/developers to help us ...' url='https://www.reddit.com/r/SaaS/comments/1ugt0e7/looking_for_smart_buildersdevelopers_to_help_us/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Field service ROI calculator | Estimate your ROI - Fieldcode' url='https://fieldcode.com/en/pricing-plans/field-service-management-software-roi-calculator'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Can asset tracking help prevent equipment downtime? - Gomocha' url='https://www.gomocha.com/can-asset-tracking-help-prevent-equipment-downtime/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Field Service Management System | Accruent Field' url='https://www.accruent.com/products/accruent-field'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='IFS - YouTube' url='https://www.youtube.com/@IFSdotcom/videos'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='What is the ROI of investing in asset tracking software? - Gomocha' url='https://www.gomocha.com/what-is-the-roi-of-investing-in-asset-tracking-software/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Industrial AI for Energy and Utilities: How IFS delivers real results' url='https://www.linkedin.com/pulse/industrial-ai-energy-utilities-how-ifs-delivers-real-results-ifs-gicyc'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Customer Engagement Solutions for Telecom & Utilities | Verint' url='https://www.verint.com/telecom-utilities/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='10 Field Service Features Your SMB Needs Today - Salesforce' url='https://www.salesforce.com/blog/small-business/field-service-features-for-smbs/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Appointment Scheduling Software for Field Service Teams Guide' url='https://www.genicteams.com/appointment-scheduling-software-for-field-service-teams/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Director, Energy Storage Services in Teaneck, NJ, United States' url='https://careers.qcells.com/jobs/17924618-director-energy-storage-services'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='QuickBooks and Field Service Software Integration Basics' url='https://contractorincharge.com/blog/quickbooks-and-field-service-software-integration-basics'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Government Operations Management Software - Infor' url='https://www.infor.com/en/industries/public-sector/government-operations'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='How a Field Service Management App Increased Productivity' url='https://www.spec-india.com/case-study/how-field-service-management-app-increased-technician-productivity'
[2026-06-30 23:55:00] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:55:00] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:55:00] INFO src.core.roster: roster.run_inflow_discovery_batch index 7/20 financial regulatory reporting software -> 100 hit(s)
[2026-06-30 23:55:00] INFO src.core.roster:  | search_term='financial regulatory reporting software' raw_hits=100
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='AML Regulatory Reporting Software - Alessa' url='https://alessa.com/software-solutions/aml-compliance/regulatory-reporting/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Financial Reporting Manager - Regulatory - Myworkdayjobs.com' url='https://westernalliancebank.wd5.myworkdayjobs.com/en-US/WAB/job/Financial-Reporting-Manager_R12953'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Financial Transactions and Reports Analysis Centre of Canada' url='https://www.canada.ca/en/financial-transactions-reports-analysis.html'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Director of Financial Operations & Regulatory Reporting – Tipalti' url='https://www.welcometothejungle.com/en/companies/tipalti/jobs/director-of-financial-operations-regulatory-reporting_foster-city-ca_hgkkn6hw'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Jaisel Patel - Latham & Watkins' url='https://www.lw.com/en/people/jaisel-patel'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Making Conservation a California Way of Life Regulation' url='https://www.waterboards.ca.gov/conservation/regs/water_efficiency_legislation.html'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='10 Best Financial Reporting Tools & Platforms Of 2026 - HighRadius' url='https://www.highradius.com/resources/Blog/best-financial-reporting-tools/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Accountant Senior - Reporting & Analysis - Myworkdayjobs.com' url='https://careoregon.wd12.myworkdayjobs.com/co/job/portland-oregon/accountant-senior---reporting---analysis_jr100945'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Sr Specialist, Financial Analysis (External Reporting)' url='https://transamerica.wd5.myworkdayjobs.com/en-US/US/job/Cedar-Rapids-Iowa/Sr-Specialist--Financial-Analysis--External-Reporting-_MG1005-1'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Best ESG Risk Management Software in 2026 - Safety Culture' url='https://safetyculture.com/apps/esg-risk-management-software'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Regulatory Reporting | Kaizen' url='https://www.kaizenreporting.com/regulatory-reporting/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Tracking regulatory changes in the second Trump administration' url='https://www.brookings.edu/articles/tracking-regulatory-changes-in-the-second-trump-administration/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Financial Disclosure Management Software – IRIS CARBON®' url='https://iriscarbon.com/products/iris-carbon-for-disclosure-management/'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Reporting, Associate / Assistant Vice President - Teal' url='https://www.tealhq.com/job/enterprise-reporting-analytics-assistant-vice-president_7ea1a9151fad706b7dacb051831fd0fa07614'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Job Description - Sports Wagering Compliance Officer I (260004ND)' url='https://massanf.taleo.net/careersection/ex/jobdetail.ftl?job=260004ND&tz=GMT-04%3A00&tzname=America%2FNew_York'
[2026-06-30 23:55:00] INFO src.core.roster:  | hit title='Texas and Colorado Enter Into a Joint AML Enforcement Action ...' url='https://www.sheppard.com/insights/blogs/texas-and-colorado-enter-into-a-joint-aml-enforcement-action-against-money-transmitter'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='Trading Technologies Launches Powerful New Multi-Asset Trade ...' url='https://www.prnewswire.com/news-releases/trading-technologies-launches-powerful-new-multi-asset-trade-surveillance-tools-for-exchanges-regulators-and-financial-institutions-302812166.html'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='BESS Senior Engineer - Climatebase' url='https://www.climatebase.org/job/74031298/bess-senior-engineer?source=jobs_directory_algolia&queryID=114c7e2a0a8e4a123a580fe89308cd31&utm_source=xinquji'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='National Community Solar Partnership Technical Assistance ...' url='https://www.energy.gov/cmei/systems/national-community-solar-partnership-technical-assistance-engagement-summaries'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title="FedEx Freight's Q4 2026 Earnings: Key Factors Shaping Market ..." url='https://www.firstchicagoinsurance.com/expert-time/FedEx-Freights-Q4-2026-Earnings-Key-Factors-Shaping-Market-Expectations-32-18244'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='News List | William Blair' url='https://www.williamblair.com/News-List'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='Dow Jones – Trusted News & Data' url='https://www.dowjones.com/'
[2026-06-30 23:54:59] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:54:59] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:54:59] INFO src.core.roster: roster.run_inflow_discovery_batch index 6/20 field service management utility software -> 100 hit(s)
[2026-06-30 23:54:59] INFO src.core.roster:  | search_term='field service management utility software' raw_hits=100
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='Field Service Management: From Spreadsheets to Seamless ...' url='https://utilities.sysco-software.com/field-service-management-spreadsheet-to-seamless/'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='Vision | All-in-One Field Service Management Software' url='https://www.ecisolutions.com/products/vision/'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='Gas Infrastructure & Utilities Software | Sysco Software' url='https://utilities.sysco-software.com/'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='SAP Field Service Management' url='https://community.sap.com/t5/c-khhcw49343/SAP+Field+Service+Management/pd-p/73554900100700002181'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='Utilities Transmission & Distribution Field Service Consultant or ...' url='https://www.accenture.com/us-en/careers/jobdetails?id=R00333800_en&title=Utilities+Transmission+%26+Distribution+Field+Service+Consultant+or+Manager'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='How Flo-Rite Fluids Gained Full Field Visibility - FieldEquip' url='https://fieldequip.com/case-study/an-oil-field-service-company/'
[2026-06-30 23:54:59] INFO src.core.roster:  | hit title='Housecall Pro: Field Service – Apps on Google Play' url='https://play.google.com/store/apps/details?id=housecall.pros&hl=en_SG'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Connector for Trello & Jira on FORGE - Atlassian Marketplace' url='https://marketplace.atlassian.com/apps/1231790/connector-for-trello-jira-on-forge'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Enterprise Systems Manager, Recruiting Systems - OpenAI' url='https://openai.com/careers/enterprise-systems-manager-recruiting-systems-san-francisco/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Freshservice/Freshdesk Integration for Jira (FORGE)' url='https://marketplace.atlassian.com/apps/1227929/freshservice-freshdesk-integration-for-jira-forge'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='MadCap IXIA CCMS for Policies & Procedures' url='https://www.madcapsoftware.com/solutions/ixia-ccms/policies-procedures/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='7 Best UKG Pro (Ultipro) Alternatives in 2026 - Gusto' url='https://gusto.com/resources/guides/best-ukgpro-alternatives'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Best Document Control Software (2026) - Doxis' url='https://www.doxis.com/en/blog/best-document-control-software'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='POSSE ELS: Enterprise Licensing System - Computronix' url='https://www.computronix.com/government-software-solutions/enterprise-licensing-system/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='LuitBiz BPM Modules | Workflow Automation & Business Process ...' url='https://www.luitinfotech.com/products/bpm/modules.php'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='REST API: The URL is not configured correctly - IBM' url='https://www.ibm.com/docs/en/baw/26.0.x?topic=configuration-rest-api-url-is-not-configured-correctly'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Enterprise Git Identity Management: Multi-Account Configuration ...' url='https://support.tools/enterprise-git-identity-management-conditional-configuration-guide/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='ITIL service desk software: 5 solutions to consider for your business' url='https://monday.com/blog/service/itil-service-desk-software/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Senior Functional Leader, Enterprise Data Management | GE Vernova' url='https://careers.gevernova.com/senior-functional-leader-enterprise-data-management/job/R5042767'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Setting Up a New Ticketing Application - TeamDynamix' url='https://solutions.teamdynamix.com/TDClient/1965/Portal/KB/Article/171944/Setting-Up-a-New-Ticketing-Application'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='PLEXIS Healthcare Systems Helps Health Plans Modernize Claims ...' url='https://tech.einnews.com/amp/pr_news/923118986/plexis-healthcare-systems-helps-health-plans-modernize-claims-operations-without-replacing-their-core-business-model'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Configuration: Enterprise DLP - Palo Alto Networks | TechDocs' url='https://docs.paloaltonetworks.com/strata-cloud-manager/getting-started/configuration-scm/manage-configuration-enterprise-dlp'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Top 6 Best Invoice Factoring Software: Read Before You Buy' url='https://factoravenue.com/blog/top-6-best-invoice-factoring-software-built-for-modern-teams/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='LOS Integration Partners - AFR Services' url='https://www.afrservices.com/services/for-banks-credit-unions/integration-partners/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Senior Maximo Application Developer (IBM Maximo)' url='https://omnisciusconsulting.applytojob.com/apply/5R4uk662cc/Senior-Maximo-Application-Developer-IBM-Maximo'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Why automated network configuration assurance matters ... - Red Hat' url='https://www.redhat.com/zh-cn/blog/why-automated-network-configuration-assurance-matters-enterprise-netops'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='OasisLMS Learning Management System Features' url='https://oasis-lms.com/feature-page'
[2026-06-30 23:54:51] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:54:51] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:54:51] INFO src.core.roster: roster.run_inflow_discovery_batch index 5/20 energy asset management and trading SaaS -> 100 hit(s)
[2026-06-30 23:54:51] INFO src.core.roster:  | search_term='energy asset management and trading SaaS' raw_hits=100
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Nuveen | Investment Management' url='https://www.nuveen.com/en-us/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Trade Mark Journal - Government of Bermuda' url='https://www.gov.bm/sites/default/files/2026-06/Trade%20Mark%20Journal%20No.%2096%20%28Part%20I%29.pdf'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Russian Harmful Foreign Activities Sanctions' url='https://ofac.treasury.gov/faqs/topic/6626'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Weekly market commentary | BlackRock Investment Institute' url='https://www.blackrock.com/us/individual/insights/blackrock-investment-institute/weekly-commentary'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='ICG: Home' url='https://www.icgam.com/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Volue: Powering those who power the world' url='https://www.volue.com/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Heat, Flexibility & Intelligence - Start Up Energy Transition' url='https://www.startup-energy-transition.com/heat-flexibility-intelligence/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Global Markets Poised for Further Gains as Geopolitical Risks Ease ...' url='https://www.creatingnycsmiles.com/expert-time/Global-Markets-Poised-for-Further-Gains-as-Geopolitical-Risks-Ease-and-AI-Earnings-Surge-34-17819'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Advancing Clean Energy and Climate Tech Startups in ASEAN ...' url='https://aseanenergy.org/publications/advancing-clean-energy-and-climate-tech-startups-in-asean-through-the-asean-sparks-catalyse/download'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Meet Unity | Comprehensive Renewable Energy Management ...' url='https://www.powerfactors.com/unity'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Solicitations - SVCE - Silicon Valley Clean Energy' url='https://svcleanenergy.org/solicitations/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Managing Director & VP, Asset Operations — Volue - Rejobs' url='https://rejobs.org/en/renewable-energy-jobs/136229-managing-director-vp-asset-operations-volue'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='EnergyChoiceMatters.com -- News on Retail Energy Choice, Electric ...' url='http://www.energychoicematters.com/'
[2026-06-30 23:54:51] INFO src.core.roster:  | hit title='Manager, Power Markets - 26-232D New 2 Locations - LinkedIn' url='https://www.linkedin.com/jobs/view/manager-power-markets-26-232d%0A-%0A-%0A-new%0A%0A-%0A-2-locations-at-energy-acuity-4433885670'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='Java Spring Engineer — LIMS & Biotech Workflows | San Diego' url='https://www.jobleads.com/us/job/java-spring-engineer-lims-biotech-workflows--san-diego--ec2097e503a2c3cb78b619cf271288d2a'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='Grape Ripeness Logger vs. agCOMMANDER Comparison' url='https://sourceforge.net/software/compare/Grape-Ripeness-Logger-vs-agCOMMANDER/'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='The Middleware Is Dead. Long Live the Balance. As ... - Instagram' url='https://www.instagram.com/p/DaDGOMYEo0s/'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='When self-hosted AI is worth it for biotech - CodePhusion' url='https://codephusion.com/blog/self-hosted-ai-for-biotech'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='List of electronic laboratory notebook software packages - Wikipedia' url='https://en.wikipedia.org/wiki/List_of_electronic_laboratory_notebook_software_packages'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='CloudLIMS hiring Integration Engineer in Indore, Madhya Pradesh ...' url='https://in.linkedin.com/jobs/view/integration-engineer-at-cloudlims-4432633724'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='The convergence of AI-driven engineering biology and emerging ...' url='https://www.sciencedirect.com/science/article/pii/S0958166926000686'
[2026-06-30 23:54:50] INFO src.core.roster:  | hit title='Simplify your laboratory workflow with Cubis® III. No middleware. No ...' url='https://www.facebook.com/PharmaFocusEurope/posts/simplify-your-laboratory-workflow-with-cubis-iiino-middleware-no-hidden-costs-ju/1075250491927383/'
[2026-06-30 23:54:50] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:54:50] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:54:50] INFO src.core.roster: roster.run_inflow_discovery_batch index 4/20 configurable enterprise workflow automation -> 100 hit(s)
[2026-06-30 23:54:50] INFO src.core.roster:  | search_term='configurable enterprise workflow automation' raw_hits=100
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='TALENT Software Services hiring Laboratory/Clinical Lab Scientist ...' url='https://www.linkedin.com/jobs/view/laboratory-clinical-lab-scientist-at-talent-software-services-4430277352'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='News and Blog-new - Dendi Software' url='https://dendisoftware.com/news-and-blog-new'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Search our Job Opportunities at Quest Diagnostics' url='https://careers.questdiagnostics.com/search-jobs'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Open Remote Jobs at Labcorp' url='https://careers.labcorp.com/global/en/remote-jobs'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Sr. Project Manager, Clinical Lab Equipment Implementation ...' url='https://jobs.danaher.com/global/en/job/DANAGLOBALR1310628EXTERNALENGLOBAL/Sr-Project-Manager-Clinical-Lab-Equipment-Implementation-Healthcare'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Cortechs.ai: Home' url='https://www.cortechs.ai/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='How Ultra-Rapid Molecular Diagnostics Are Reshaping the Clinical ...' url='https://www.quidelortho.com/global/en/resources/articles/how-ultra-rapid-molecular-diagnostics-are-reshaping-the-clinical-laboratory'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Cloud First Digital Pathology in a High-Volume Regional Laboratory' url='https://www.clinicallab.com/your-model-from-our-experience-cloud-first-digital-pathology-in-a-high-volume-regional-laboratory-28681'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Advances in Digital Pathology - LigoLab' url='https://www.ligolab.com/post/benefits-of-digital-pathology'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Leica Offers Up Free Video of its Popular Executive War College ...' url='https://www.clinicallab.com/leica-offers-up-free-video-of-its-popular-executive-war-college-session-28703'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Laboratory Information Systems (LIS vs LIMS) for Data Management' url='https://www.ligolab.com/post/https-www-ligolab-com-lims-data-management'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='p-Tau 205 Assay | Quanterix' url='https://www.quanterix.com/simoa-assay-kits-and-reagents/p-tau-205/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Boost empower software data with cloud-based AI - Select Science' url='https://www.selectscience.net/webinar/enhancing-empower-software-data-with-cloud-based-applications'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='$15-$48/hr Genalyte Jobs (NOW HIRING) Jun 2026 - ZipRecruiter' url='https://www.ziprecruiter.com/Jobs/Genalyte'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Serology Lab Tech (HC Pro 1-Clinical Lab Science) (# 374424)' url='https://www.higheredjobs.com/region/details.cfm?JobCode=179484179&Title=Serology%20Lab%20Tech%20(HC%20Pro%201-Clinical%20Lab%20Science)%20(%23%20374424)'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='CellCarta and Sonic Healthcare CDx Partnership' url='https://cellcarta.com/science-hub/cellcarta-sonic-healthcare-strategic-partnership/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Tecan and NVIDIA Add AI Capabilities to Introspect Lab Platform' url='https://clpmag.com/lab-management/company-news/tecan-nvidia-add-ai-introspect-lab-analytics-platform/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Molecular Diagnostics Software and Equipment Specialist - Jobvite' url='https://jobs.jobvite.com/neogenomics/job/okQnAfwR'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Indica Labs Expands into Prostate Cancer, Improving NGS ...' url='https://indicalab.com/news/press-release/indica-labs-expands-into-prostate-cancer-improving-ngs-confidencethrough-precise-tumor-quantification/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Senior Software Engineers, ML / UX / DevOps & Test Automation' url='https://jobs.thermofisher.com/mx/es/job/R-01355333/Senior-Software-Engineers-ML-UX-DevOps-Test-Automation'
[2026-06-30 23:54:43] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:54:43] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:54:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 3/20 cloud LIMS for biotech laboratories -> 100 hit(s)
[2026-06-30 23:54:43] INFO src.core.roster:  | search_term='cloud LIMS for biotech laboratories' raw_hits=100
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Laboratory Information Management Systems (LIMS) Market' url='https://www.globenewswire.com/news-release/2026/06/26/3318323/0/en/laboratory-information-management-systems-lims-market-size-expected-to-reach-usd-5-19-billion-by-2030-marketsandmarkets.html'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='IT Support for Biotech & Life Sciences Companies - Boston Networks' url='https://bostonnetworks.com/industries-served/it-support-biotech-life-sciences/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='The 10 Best LIMS Platforms Leading Into 2026 - Genemod' url='https://genemod.net/blog/the-10-best-lims-platforms-leading-into-2026-features-trends-and-what-labs-need-next'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Integrating LIMS with AI in Laboratories for Scalable, Intelligent ...' url='https://www.labvantage.com/blog/integrating-lims-with-ai-in-laboratories-for-scalable-intelligent-digital-ecosystems/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Top 10 Benefits of LIMS Software for Pharmaceutical Laboratories' url='https://www.agaramtech.com/blog/top-10-benefits-of-lims-software-for-pharmaceutical-laboratories'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Inside Sales Specialist (Spanish) - Remote at CloudLIMS' url='https://dailyremote.com/remote-job/inside-sales-specialist-spanish-remote-5216628'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title="Biotechnology Lab Management Software: 2026 Buyer's Guide" url='https://newlabcloud.com/blog/biotechnology-lab-management-software-guide/'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Scientists resist ELNs and LIMS due to tedious data entry and lack of ...' url='https://www.linkedin.com/posts/will-deloache-6965a018_scientists-mostly-dislike-their-eln-or-lims-activity-7475649486896164864-OX9B'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Cloud-Based Laboratory Information Management System - NTHRYS' url='https://www.nthrys.com/home/pdfs/projects/biosciences--biosciences-global-market-expansion-strategy---cloud-based-lims-platform.pdf'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='LIMS Systems Industry Research Report: Future Market Growth from ...' url='https://www.linkedin.com/pulse/lims-systems-industry-research-report-future-market-growth-from-gnotf'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='Global LIMS market to reach $5.19B by 2030, dri... - Pluang' url='https://pluang.com/en/news-feed/pasar-sistem-manajemen-informasi-laboratorium-lims-diproyeksikan-meningkat'
[2026-06-30 23:54:43] INFO src.core.roster:  | hit title='AI LIMS Optimization Projects - NTHRYS' url='https://www.nthrys.com/home/pdfs/projects/ai-lims-optimization.pdf'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Laboratory Information Management Systems (LIMS) Market' url='https://www.globenewswire.com/news-release/2026/06/26/3318323/0/en/laboratory-information-management-systems-lims-market-size-expected-to-reach-usd-5-19-billion-by-2030-marketsandmarkets.html'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='BTO | DARPA' url='https://www.darpa.mil/about/offices/bto'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Principal Data Scientist - DDSAI - Agentic Lab Automation' url='https://www.careers.jnj.com/en/jobs/r-085522/principal-data-scientist-ddsai-agentic-lab-automation/'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Automated Flash Chromatography Purification Systems Market ...' url='https://www.indexbox.io/blog/automated-flash-chromatography-purification-systems-market-forecast-points-higher-toward-2035-driven-by-biopharma-automation-demands/'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Benefits and Types of Laboratory Automation Solutions' url='https://www.thermofisher.com/us/en/home/life-science/lab-equipment/lab-automation/why-automate.html'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Sr. Project Manager, Clinical Lab Equipment Implementation ...' url='https://jobs.danaher.com/global/en/job/DANAGLOBALR1310628EXTERNALENGLOBAL/Sr-Project-Manager-Clinical-Lab-Equipment-Implementation-Healthcare'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Chromatography Software Market Size & Insights Report [2035]' url='https://www.marketreportsworld.com/market-reports/chromatography-software-market-14729330'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Lab Automation Biotech Platform Dev | NTHRYS' url='https://www.nthrys.com/home/pdfs/projects/experimental-biotechnology--lab-automation-biotech-platform-dev.pdf'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Pascal Zimmermann ZenCELL 猫头鹰作者' url='https://zencellowl.com/zh/%E4%BD%9C%E8%80%85/%E5%B8%95%E6%96%AF%E5%8D%A1/'
[2026-06-30 23:54:42] INFO src.core.roster:  | hit title='Integrating LIMS with AI in Laboratories for Scalable, Intelligent ...' url='https://www.labvantage.com/blog/integrating-lims-with-ai-in-laboratories-for-scalable-intelligent-digital-ecosystems/'
[2026-06-30 23:54:42] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-30 23:54:42] INFO src.core.roster:  | last_scan_at bumped
[2026-06-30 23:54:42] INFO src.core.roster: roster.run_inflow_discovery_batch index 2/20 clinical lab software diagnostics -> 100 hit(s)
[2026-06-30 23:54:42] INFO src.core.roster:  | search_term='clinical lab software diagnostics' raw_hits=100
[2026-06-30 23:54:34] INFO dispatch.scheduler: Dispatching inflow_discovery — 1 available, batch inflow_discovery-c650e03b-4e43-4745-9b2a-ffba9855cedc
[2026-06-30 23:54:34] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 1/1 inflow_discovery -> loop iteration 1 starting
[2026-06-30 23:54:34] INFO src.core.dispatcher:  | available=1 effective_min=1 max_runs=1 draining=False entity_batch_id=inflow_discovery-c650e03b-4e43-4745-9b2a-ffba9855cedc
[2026-06-30 23:54:34] INFO src.core.dispatcher: dispatcher._run_task index 1/1 inflow_discovery -> running batch
[2026-06-30 23:54:34] INFO src.core.dispatcher:  | batch_size=10 batch_id=inflow_discovery-c650e03b-4e43-4745-9b2a-ffba9855cedc entity_type='candidate' trigger_state='LIVE_PROMPTS'
[2026-06-30 23:54:34] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 candidate/LIVE_PROMPTS -> claimed 1 entity/entities
[2026-06-30 23:54:34] INFO src.core.dispatcher:  | task_key=inflow_discovery batch_id=inflow_discovery-c650e03b-4e43-4745-9b2a-ffba9855cedc batch_call_mode=False dispatch batch_size=10 claim_cap=None
[2026-06-30 23:54:34] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 johnson -> claimed
[2026-06-30 23:54:34] INFO src.core.dispatcher:  | entity_type=candidate trigger_state=LIVE_PROMPTS state='LIVE_PROMPTS'
[2026-06-30 23:54:34] INFO src.core.roster: roster.run_inflow_discovery_batch index 1/20 biotech lab automation and data management -> 100 hit(s)
[2026-06-30 23:54:34] INFO src.core.roster:  | search_term='biotech lab automation and data management' raw_hits=100
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='AI in Regulated Labs: What Lab Managers Need to Know About GxP ...' url='https://www.labmanager.com/ai-in-regulated-labs-what-lab-managers-need-to-know-about-gxp-validation-and-data-integrity-35633'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Numera® fully automated modular bioprocess sampling - Securecell' url='https://www.securecell.ch/product-biotech/numera-advanced-bioprocess-sampling-solution'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Building the Future of Lab Automation | UC Berkeley Extension' url='https://voices.berkeley.edu/technology-and-information-management/building-future-lab-automation'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Training Programs and Certifications for AI and Automation in the Lab' url='https://www.labmanager.com/training-programs-and-certifications-for-ai-and-automation-in-the-lab-35644'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Careers - Legend Biotech' url='https://legendbiotech.com/careers/'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Managing Bioinformatics Workflows in Veterinary Diagnostics Using ...' url='https://www.globus.org/user-stories/managing-bioinformatics-workflows-in-veterinary-diagnostics-using-globus'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Automation - Page 2 of 3 - Drug Discovery World (DDW)' url='https://www.ddw-online.com/t/automation/page/2/'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Every delayed analytical result has a ripple effect. A ... - Instagram' url='https://www.instagram.com/p/DZ_74EVk9NN/'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Scientific Applications Analyst, Benchling - BIIE (Basel) - JOIN' url='https://join.com/companies/immune1/16363379-scientific-applications-analyst-benchling'
[2026-06-30 23:54:34] INFO src.core.roster:  | hit title='Agenda | BioTechX USA - Terrapinn' url='https://www.terrapinn.com/conference/biotechxusa/programme.stm'
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
