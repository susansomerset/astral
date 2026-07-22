# AST-835 — Rate limit queries for a config-driven pause

<!-- linear-archive: AST-835 archived 2026-07-22 -->

## Linear archive (AST-835)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-835/rate-limit-queries-for-a-config-driven-pause  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Google Custom Search powers roster inflow discovery and company website resolution. A single discovery batch can fire many paginated CSE requests in seconds; when Google's per-minute quota is exceeded (HTTP 429), the product today logs a warning per term and keeps going—turning the rest of the batch into a wall of failures instead of backing off. Susan needs Astral to pace CSE queries and pause when rate-limited so scheduled inflow work finishes reliably without burning quota or leaving terms falsely marked stale.

## Functional scope

* **Config-driven query pacing:** Add config literals for a minimum delay between successive Google CSE HTTP requests. Every roster path that calls Google CSE applies this pacing before each request, including paginated pages within one search.
* **Config-driven pause on rate limit:** When Google CSE returns HTTP 429 or an API error indicating rate limit / quota exceeded, pause for a configurable duration, then retry the same request. Config also caps how many pause-and-retry cycles are attempted per request.
* **Shared behavior across CSE call sites:** Pacing and pause-and-retry apply wherever the product issues Google CSE queries today—inflow discovery batch (per search term) and company website resolution—not only one path.
* **Graceful degradation after exhausted retries:** If pause-and-retry is exhausted, surface failure using the same outcome semantics the call site uses today: discovery counts an error for that term, does not bump `last_scan_at`, and continues remaining terms; resolve returns a CSE failure without changing company state.
* **Debug traceability:** When `debug=True`, log pacing delays, rate-limit pause start/end, and retry outcomes under Style D index headers (AST-538 contract)—what was attempted and what was recorded, not only pass/fail counts.

## Boundaries

* Does not change search term selection, `freq_hrs` cadence, `max_results_per_query`, or date-restrict settings (existing inflow config).
* Does not add admin UI knobs for pause or delay values—config literals only (ASTRAL_CODE_RULES §2.1).
* Does not rate-limit Anthropic, Playwright, or other external I/O.
* Does not fix unrelated failures in the attached log (e.g. job-table unique constraint during hit recording)—separate ticket unless Susan folds it in.
* Does not alter dispatch scheduler active/paused toggle behavior.

## Acceptance criteria

1. With a non-zero configured inter-query delay, a discovery batch that issues multiple CSE requests spaces HTTP calls by at least that delay (observable via test mocks or timed integration).
2. On HTTP 429, the system pauses for the configured duration before retrying; with `debug=True`, each pause and retry is visible under the current index header.
3. After configured retries are exhausted, discovery behavior for that term matches pre-change error semantics (`last_scan_at` not bumped; error counted; remaining terms still attempted unless open question #1 changes this).
4. Website resolution receives the same pacing and 429 pause-and-retry behavior; exhausted retries return CSE failure without company state transition.
5. Inter-query delay, rate-limit pause duration, and max retry count live as config literals with documented units—no environment-variable overrides.

## Dependencies and blockers

None. Inflow discovery and resolve paths are shipped; this hardens the existing Google CSE integration.

## Open questions

Resolved at dispatch (Susan moved parent to Todo, 2026-07-02):

1. **429 exhausted mid-batch:** Continue remaining terms — do not stop the batch (Functional scope default).
2. **Config defaults:** Engineer proposes inter-query delay and pause duration in plan; Susan confirms at UAT.
3. **Job UNIQUE crash:** Out of scope — separate ticket (Boundaries).

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-835 (parent) | ftr/AST-835-rate-limit-queries-for-a-config-driven-pause |
| AST-837 | sub/AST-835/AST-837-google-cse-query-pacing-and-rate-limit-pause |
| AST-839 | sub/AST-835/AST-839-uat-cse-debug-verbose-per-http-trace |

**Epic worktree:** `astral-AST-835/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 2f8533fd-58b6-4d11-a30f-74c1da94e1c9 |
| Betty | qa | d948897a-39b7-4e25-9df6-a21e6b804ef3 |
| Radia | review | 78a52e2e-d6a6-41fe-8ad1-0edbc621606f |

---

## Original brief

```
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Enterprise Account Manager Job at Revivn - Brooklyn, New York' url='https://www.sonara.ai/job-details/enterprise-account-manager-at-revivn-9158363d-574d-76b9-22db-dd4397fab486'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Director of Enterprise reputed company - 2.halvolink' url='https://2.halvolink.liveblog365.com/job/2644836'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Product Adoption Director, Industries Job - Salesforce Inc' url='https://www.monster.com/job-openings/product-adoption-director-industries-atlanta-ga--29747ffb-34b1-47ca-a921-f3e6fd551a49'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Job Application for Senior Product Designer, AI Creative at Hightouch' url='https://job-boards.greenhouse.io/hightouch/jobs/6103070004'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Customer Success Startups funded by Y Combinator (YC) 2026' url='https://www.ycombinator.com/companies/industry/customer-success'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Head Of Customer Success Jobs in New York - Migrate Mate' url='https://migratemate.co/head-of-customer-success-jobs/new-york'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Regional Director, Customer Success - Virtual Vocations' url='https://www.virtualvocations.com/job/regional-director-customer-success-3117638-i.html'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Ditch Pain Point and Pitch the "Gain Point" in Your 2026 Outreach' url='https://shivyaanchi.com/b2b-ditch-pain-point-and-pitch-the-gain-point-in-your-2026-outreach/'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Mastering Customer Retention Cost in 2026 - Sprints & Sneakers' url='https://www.sprintsandsneakers.com/insights/customer-retention-cost'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Director, Customer Success - SMB & MM at Fundraise Up - Remote' url='https://remoteleaf.com/company/fundraise-up/director-customer-success-smb-mm-brazil/'
[2026-06-29 21:47:43] INFO src.core.roster:  | hit title='Mid Market Account Executive, Spectrum Business' url='https://jobs.spectrum.com/job/austin/mid-market-account-executive-spectrum-business/4673/97097167040'
[2026-06-29 21:47:43] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:43] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 11/20 insurance claims automation platform -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'insurance claims automation platform': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 12/20 insurtech payment processing for carriers -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'insurtech payment processing for carriers': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 13/20 legal practice management platform B2B -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'legal practice management platform B2B': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 14/20 manufacturing execution system cloud -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'manufacturing execution system cloud': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 15/20 medical device quality assurance cloud -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'medical device quality assurance cloud': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 16/20 municipal citizen services software -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'municipal citizen services software': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 17/20 pharma quality management cloud -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'pharma quality management cloud': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 18/20 professional services automation platform -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'professional services automation platform': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 19/20 regulatory compliance platform for financial services -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'regulatory compliance platform for financial services': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] INFO src.core.roster: roster.run_inflow_discovery_batch index 20/20 supply chain visibility platform enterprise -> CSE failed: Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] WARNING src.core.roster: run_inflow_discovery_batch: CSE failed for term 'supply chain visibility platform enterprise': Google CSE HTTP 429: {
  "error": {
    "code": 429,
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user' of service 'customsearch.googleapis.com' for consumer 'project_number:204821334018'.",
        "domain": "global",
        "reason": "rateLimitExceeded"
    …
[2026-06-29 21:47:43] ERROR dispatch.scheduler: [inflow_discovery/inflow_discovery-4f4554af-e57a-49b4-9ec1-ed3a391317bb] crashed
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
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Billing and Revenue Specialist - Azara Healthcare' url='https://www.azarahealthcare.com/billing-and-revenue-specialist'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Vice President of Technology Assets - CIP Medical - LinkedIn' url='https://www.linkedin.com/jobs/view/vice-president-of-technology-assets-at-cip-medical-4431264444'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Healthcare Cybersecurity Services // Echelon Risk + Cyber' url='https://echeloncyber.com/industries/healthcare-cybersecurity-services'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Meihua International pivots into healthcare SaaS | MHUAF SEC Filing' url='https://www.stocktitan.net/sec-filings/MHUAF/6-k-meihua-international-medical-technologies-co-ltd-current-report-f-805d2623fbc5.html'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='OIG Corporate Integrity Agreements: Oversight, AI Governance, and ...' url='https://www.pyapc.com/insights/the-evolution-of-oig-corporate-integrity-agreements-a-new-era-of-oversight-accountability-ai-governance-and-compliance-expectations/'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Director, Risk & Compliance Management at Parexel' url='https://jobs.parexel.com/en/job/reino-unido/director-risk-and-compliance-management/877/97086807856'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='SEAP Compliance Specialist - Myworkdayjobs.com' url='https://redhat.wd5.myworkdayjobs.com/en-US/Jobs/job/SEAP-Compliance-Specialist_R-057454-1'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Kieran Lynch | VP of Global Sales - ViClarity' url='https://www.viclarity.com/eu/about/executive-team/kieran-lynch'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='r/SaaS on Reddit: Looking for smart builders/developers to help us ...' url='https://www.reddit.com/r/SaaS/comments/1ugt0e7/looking_for_smart_buildersdevelopers_to_help_us/'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='[Remote] Project Manager - 2.halvolink' url='https://2.halvolink.liveblog365.com/job/2684672'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Continuum GRC: Enterprise Risk Management & GRC Solution ...' url='https://continuumgrc.com/'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Compliance & Quality Manager - Myworkdayjobs.com' url='https://iqvia.wd1.myworkdayjobs.com/en-US/IQVIA/job/Compliance---Quality-Manager_R1550658'
[2026-06-29 21:47:39] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:39] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:39] INFO src.core.roster: roster.run_inflow_discovery_batch index 10/20 high-touch customer success enterprise B2B -> 100 hit(s)
[2026-06-29 21:47:39] INFO src.core.roster:  | search_term='high-touch customer success enterprise B2B' raw_hits=100
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Mid-Market Customer Success Manager - America - LinkedIn' url='https://www.linkedin.com/jobs/view/mid-market-customer-success-manager-america-at-ashby-4403347450'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Introducing Lifecycle Studio - Hightouch' url='https://hightouch.com/blog/introducing-lifecycle-studio'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Manager of Customer Success at Steer.io - Remote - RemoteLeaf' url='https://remoteleaf.com/company/steerio/manager-of-customer-success-united-states-2/'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Senior • Manager of Client Success • Chicago, IL | MindPal Jobs' url='https://mindpal.co/jobs/75348'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Apply to Head of Implementation at AccelerateHC - Recruiterflow' url='https://recruiterflow.com/acceleratehc/jobs/549?widget=1'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Senior Director, Regional Customer Success (AMER) - Vonage' url='https://www.vonage.com/careers/job-details/8591899002/'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Head of Technical Account Management (West) - Mediabistro' url='https://www.mediabistro.com/jobs/3540828115-head-of-technical-account-management-west'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='Remote Enterprise Customer Success Manager at Dutchie - NoDesk' url='https://nodesk.co/remote-jobs/dutchie-enterprise-customer-success-manager/'
[2026-06-29 21:47:39] INFO src.core.roster:  | hit title='High Touch Implementation Specialist - Americas - PST - Ashby' url='https://builtin.com/job/high-touch-implementation-specialist-americas-pst/9930463'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Best Practices for Running a Thriving Community in 2026' url='https://www.centralsquare.com/resources/articles/best-practices-for-running-a-thriving-community-in-2026'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Property Information and Reports | Saint Paul Minnesota' url='https://www.stpaul.gov/departments/safety-inspections/report-concern/property-information-and-reports'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Idaho Transportation Department' url='https://itd.idaho.gov/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='services.mde.maryland. gov/Application/SearchPermitTypes' url='https://www.facebook.com/MDEnvironment/posts/have-you-heard-you-can-now-apply-for-over-50-types-of-permits-on-our-environment/1432533088903950/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Access2Pay | Cloud-based Payment Systems and Solutions' url='https://access2pay.com/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='ACP-backed Schneider Geospatial picks up govtech firm New ...' url='https://www.pehub.com/acp-backed-schneider-geospatial-picks-up-govtech-firm-new-england-geosystems/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Home | Collier County, FL' url='https://www.collier.gov/Home'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Schneider Geospatial Adds New England GeoSystems' url='https://lasvegassun.com/news/2026/jun/24/schneider-geospatial-adds-new-england-geosystems/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Burbankca.gov' url='https://www.burbankca.gov/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='City of San Diego Official Website' url='https://www.sandiego.gov/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Building Permits - Reno.gov' url='https://reno.gov/business-development/development-services/building-permits.php'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Reno.gov' url='https://www.reno.gov/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Parks & Recreation | West Chester Borough, PA - Official Website' url='https://www.west-chester.com/139/Parks-Recreation'
[2026-06-29 21:47:38] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:38] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:38] INFO src.core.roster: roster.run_inflow_discovery_batch index 9/20 healthcare compliance management SaaS -> 100 hit(s)
[2026-06-29 21:47:38] INFO src.core.roster:  | search_term='healthcare compliance management SaaS' raw_hits=100
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Compliance Startups funded by Y Combinator (YC) 2026' url='https://www.ycombinator.com/companies/industry/compliance'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Oreste Cipolla | Partner - White & Case LLP' url='https://www.whitecase.com/people/oreste-cipolla'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='SOC 2 vs. HIPAA: Key Differences Every Healthcare Technology ...' url='https://circle.healthcare/blogs/soc2-vs-hipaa-healthcare-tech-vendors/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='A Complete Overview of SaaS Compliance - Sprinto' url='https://sprinto.com/blog/saas-compliance-guide/'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Top 10 Healthcare Workforce Management Software (2026)' url='https://www.varshealth.com/post/healthcare-workforce-management-software-comparison'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='SaaS Security Posture Management (SSPM) Solution Brief' url='https://www.paloaltonetworks.com/resources/datasheets/saas-security-posture-management'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Senior Product Manager – Rural Health Managed Services' url='https://www.builtinboston.com/job/senior-product-manager-rural-health-managed-services/9966525'
[2026-06-29 21:47:38] INFO src.core.roster:  | hit title='Introduction of CT License Intelligence | Wolters Kluwer' url='https://www.wolterskluwer.com/en/news/introduction-of-ct-license-intelligence'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='What Is Field Service Management Software? - Sodtrack' url='https://www.sodtrack.com/what-is-field-service-management'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='B2W Track: Field Performance Tracking & Analysis Software - Trimble' url='https://www.trimble.com/en/resources/construction/docs/b2w-track-field-performance-tracking-analysis-software'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Housecall Pro: Field Service – Apps on Google Play' url='https://play.google.com/store/apps/details?id=housecall.pros&hl=en_SG'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Field service ROI calculator | Estimate your ROI - Fieldcode' url='https://fieldcode.com/en/pricing-plans/field-service-management-software-roi-calculator'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Can asset tracking help prevent equipment downtime? - Gomocha' url='https://www.gomocha.com/can-asset-tracking-help-prevent-equipment-downtime/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Field Service Management System | Accruent Field' url='https://www.accruent.com/products/accruent-field'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='IFS - YouTube' url='https://www.youtube.com/@IFSdotcom/videos'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='What is the ROI of investing in asset tracking software? - Gomocha' url='https://www.gomocha.com/what-is-the-roi-of-investing-in-asset-tracking-software/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Industrial AI for Energy and Utilities: How IFS delivers real results' url='https://www.linkedin.com/pulse/industrial-ai-energy-utilities-how-ifs-delivers-real-results-ifs-gicyc'
[2026-06-29 21:47:31] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:31] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:31] INFO src.core.roster: roster.run_inflow_discovery_batch index 7/20 financial regulatory reporting software -> 100 hit(s)
[2026-06-29 21:47:31] INFO src.core.roster:  | search_term='financial regulatory reporting software' raw_hits=100
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='AML Regulatory Reporting Software - Alessa' url='https://alessa.com/software-solutions/aml-compliance/regulatory-reporting/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Financial Transactions and Reports Analysis Centre of Canada' url='https://www.canada.ca/en/financial-transactions-reports-analysis.html'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Making Conservation a California Way of Life Regulation' url='https://www.waterboards.ca.gov/conservation/regs/water_efficiency_legislation.html'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='USOGE | OGE' url='https://www.oge.gov/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Director of Financial Operations & Regulatory Reporting – Tipalti' url='https://www.welcometothejungle.com/en/companies/tipalti/jobs/director-of-financial-operations-regulatory-reporting_foster-city-ca_hgkkn6hw'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Jaisel Patel - Latham & Watkins' url='https://www.lw.com/en/people/jaisel-patel'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Banks, building societies and investment firms | Bank of England' url='https://www.bankofengland.co.uk/prudential-regulation/regulatory-reporting/regulatory-reporting-banking-sector/banks-building-societies-and-investment-firms'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Regulatory Reporting | Kaizen' url='https://www.kaizenreporting.com/regulatory-reporting/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='10 Best Financial Reporting Tools & Platforms Of 2026 - HighRadius' url='https://www.highradius.com/resources/Blog/best-financial-reporting-tools/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Sr Specialist, Financial Analysis (External Reporting)' url='https://transamerica.wd5.myworkdayjobs.com/en-US/US/job/Cedar-Rapids-Iowa/Sr-Specialist--Financial-Analysis--External-Reporting-_MG1005-1'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Best ESG Risk Management Software in 2026 - Safety Culture' url='https://safetyculture.com/apps/esg-risk-management-software'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Financial Reporting Manager - Regulatory @ Western Alliance Bank' url='https://www.tealhq.com/job/financial-reporting-manager-regulatory_7ea1ad90ded59fee5b467feba26cab9fd57fc'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='UKSEF Reporting Software for FCA Filings | IRIS Carbon®' url='https://iriscarbon.com/products/uksef-reporting/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Director, Finance (External Reporting) - Myworkdayjobs.com' url='https://transamerica.wd5.myworkdayjobs.com/en-US/US/job/Cedar-Rapids-Iowa/Director--Finance--External-Reporting-_MG1003'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Reporting, Associate / Assistant Vice President - Teal' url='https://www.tealhq.com/job/enterprise-reporting-analytics-assistant-vice-president_7ea1a9151fad706b7dacb051831fd0fa07614'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Revisions to Financial Forms Reporting and Filing Requirements' url='https://www.federalregister.gov/documents/2026/06/24/2026-12712/revisions-to-financial-forms-reporting-and-filing-requirements'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Financial Disclosure Management Software – IRIS CARBON®' url='https://iriscarbon.com/products/iris-carbon-for-disclosure-management/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Texas and Colorado Enter Into a Joint AML Enforcement Action ...' url='https://www.sheppard.com/insights/blogs/texas-and-colorado-enter-into-a-joint-aml-enforcement-action-against-money-transmitter'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Tracking regulatory changes in the second Trump administration' url='https://www.brookings.edu/articles/tracking-regulatory-changes-in-the-second-trump-administration/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Corporate Financial Reporting Manager in Milwaukee, Wisconsin ...' url='https://careers.paysbig.com/us/en/job/CORPO004236/Corporate-Financial-Reporting-Manager'
[2026-06-29 21:47:31] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:31] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:31] INFO src.core.roster: roster.run_inflow_discovery_batch index 8/20 government permitting and licensing platform -> 100 hit(s)
[2026-06-29 21:47:31] INFO src.core.roster:  | search_term='government permitting and licensing platform' raw_hits=100
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Products — MyGovernmentOnline (MGO) Government Software ...' url='https://landing.mgoconnect.org/products'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='POSSE ELS: Enterprise Licensing System - Computronix' url='https://www.computronix.com/government-software-solutions/enterprise-licensing-system/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Digital Innovation Initiative | City of Sandy Springs' url='https://www.sandyspringsga.gov/innovate/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Providence' url='https://providenceri.portal.opengov.com/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='Welcome to Division of Occupational and Professional Licenses' url='https://dopl.idaho.gov/'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='licensing and permits Service | National Platform (National Portal)' url='https://my.gov.sa/en/services/1394549'
[2026-06-29 21:47:31] INFO src.core.roster:  | hit title='City of Jersey City: Home' url='https://www.jerseycitynj.gov/'
[2026-06-29 21:47:30] INFO src.core.roster:  | hit title='Utility Management Insights & Trends | Bynry Blogs' url='https://www.bynry.com/blog'
[2026-06-29 21:47:30] INFO src.core.roster:  | hit title='Partners | AssetCore' url='https://assetcore.ai/partners/'
[2026-06-29 21:47:30] INFO src.core.roster:  | hit title='SAP Field Service Management' url='https://community.sap.com/t5/c-khhcw49343/SAP+Field+Service+Management/pd-p/73554900100700002181'
[2026-06-29 21:47:30] INFO src.core.roster:  | hit title='Utilities Transmission & Distribution Field Service Consultant or ...' url='https://www.accenture.com/us-en/careers/jobdetails?id=R00333800_en&title=Utilities+Transmission+%26+Distribution+Field+Service+Consultant+or+Manager'
[2026-06-29 21:47:30] INFO src.core.roster:  | hit title='Senior Staff Engineer – Enterprise Middleware Platform & Migration ...' url='https://www.aep.com/careers/position?job=JOB_POSTING-3-25400'
[2026-06-29 21:47:30] INFO src.core.roster:  | hit title='Senior Staff Engineer – Enterprise Middleware Platform & Migration ...' url='https://www.aep.com/careers/position?job=JOB_POSTING-3-25400'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Multiple Award Schedule - GSA' url='https://www.gsa.gov/buy-through-us/purchasing-programs/multiple-award-schedule'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Meet Unity | Comprehensive Renewable Energy Management ...' url='https://www.powerfactors.com/unity'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='EnergyChoiceMatters.com -- News on Retail Energy Choice, Electric ...' url='http://www.energychoicematters.com/'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Solicitations - SVCE - Silicon Valley Clean Energy' url='https://svcleanenergy.org/solicitations/'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Managing Director & VP, Asset Operations — Volue - Rejobs' url='https://rejobs.org/en/renewable-energy-jobs/136229-managing-director-vp-asset-operations-volue'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Manager, Power Markets - 26-232D New 2 Locations - LinkedIn' url='https://www.linkedin.com/jobs/view/manager-power-markets-26-232d%0A-%0A-%0A-new%0A%0A-%0A-2-locations-at-energy-acuity-4433885670'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='BESS Senior Engineer - Climatebase' url='https://www.climatebase.org/job/74031298/bess-senior-engineer?source=jobs_directory_algolia&queryID=114c7e2a0a8e4a123a580fe89308cd31&utm_source=xinquji'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Trading Technologies Launches Powerful New Multi-Asset Trade ...' url='https://www.prnewswire.com/news-releases/trading-technologies-launches-powerful-new-multi-asset-trade-surveillance-tools-for-exchanges-regulators-and-financial-institutions-302812166.html'
[2026-06-29 21:47:23] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:23] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:23] INFO src.core.roster: roster.run_inflow_discovery_batch index 6/20 field service management utility software -> 100 hit(s)
[2026-06-29 21:47:23] INFO src.core.roster:  | search_term='field service management utility software' raw_hits=100
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Gas Infrastructure & Utilities Software | Sysco Software' url='https://utilities.sysco-software.com/'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Utility ERP Software: Dynamics 365 vs SAP, Oracle and IFS' url='https://akitais.com/news/utility-erp-software-comparison/'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Field Force Scheduling Software Dispatch Service Technicians' url='https://fieldequip.com/field-service-scheduling-dispatch-software'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Vision | All-in-One Field Service Management Software' url='https://www.ecisolutions.com/products/vision/'
[2026-06-29 21:47:23] INFO src.core.roster:  | hit title='Railcar Repair Management Software | AAR Billing and CRB' url='https://fieldequip.com/railcar-repair-management/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='7 Best UKG Pro (Ultipro) Alternatives in 2026 - Gusto' url='https://gusto.com/resources/guides/best-ukgpro-alternatives'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='OnitX ELM: Enterprise Legal Management' url='https://www.onit.com/resources/onitx-elm-enterprise-legal-management/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='POSSE ELS: Enterprise Licensing System - Computronix' url='https://www.computronix.com/government-software-solutions/enterprise-licensing-system/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='REST API: The URL is not configured correctly - IBM' url='https://www.ibm.com/docs/en/baw/26.0.x?topic=configuration-rest-api-url-is-not-configured-correctly'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Executive Director, Enterprise Administrative Systems' url='https://jobs.villanova.edu/postings/35451'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='ITIL service desk software: 5 solutions to consider for your business' url='https://monday.com/blog/service/itil-service-desk-software/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='FIPS compliance - IBM' url='https://www.ibm.com/docs/en/baw/26.0.x?topic=overview-fips-compliance'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='The 2026 Essential Guide to Project Risk Management Software' url='https://planisware.com/resources/risk-management/2026-essential-guide-project-risk-management-software'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Configuration: Enterprise DLP - Palo Alto Networks | TechDocs' url='https://docs.paloaltonetworks.com/strata-cloud-manager/getting-started/configuration-scm/manage-configuration-enterprise-dlp'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Top 6 Best Invoice Factoring Software: Read Before You Buy' url='https://factoravenue.com/blog/top-6-best-invoice-factoring-software-built-for-modern-teams/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='LOS Integration Partners - AFR Services' url='https://www.afrservices.com/services/for-banks-credit-unions/integration-partners/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Senior Maximo Application Developer (IBM Maximo)' url='https://omnisciusconsulting.applytojob.com/apply/5R4uk662cc/Senior-Maximo-Application-Developer-IBM-Maximo'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Why automated network configuration assurance matters ... - Red Hat' url='https://www.redhat.com/zh-cn/blog/why-automated-network-configuration-assurance-matters-enterprise-netops'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='OasisLMS Learning Management System Features' url='https://oasis-lms.com/feature-page'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Sales Tax Software That Fits Your Business | Prophit.ai' url='https://prophit.ai/sales-tax-software'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='NetSuite to Intuit Enterprise Suite Migration - Fourlane' url='https://www.fourlane.com/netsuite-to-intuit-enterprise-suite'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Find the Best CLM for Your Company Size - Contract Logix' url='https://www.contractlogix.com/solutions/by-company-size/'
[2026-06-29 21:47:22] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:22] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:22] INFO src.core.roster: roster.run_inflow_discovery_batch index 5/20 energy asset management and trading SaaS -> 100 hit(s)
[2026-06-29 21:47:22] INFO src.core.roster:  | search_term='energy asset management and trading SaaS' raw_hits=100
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Enverus | Creating the future of energy together.' url='https://www.enverus.com/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Nuveen | Investment Management' url='https://www.nuveen.com/en-us/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Russian Harmful Foreign Activities Sanctions' url='https://ofac.treasury.gov/faqs/topic/6626'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='smartPulse Mobile - Apps on Google Play' url='https://play.google.com/store/apps/details?id=io.smartpulse.mobile&hl=en_US'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Weekly market commentary | BlackRock Investment Institute' url='https://www.blackrock.com/us/individual/insights/blackrock-investment-institute/weekly-commentary'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Volue: Powering those who power the world' url='https://www.volue.com/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Heat, Flexibility & Intelligence - Start Up Energy Transition' url='https://www.startup-energy-transition.com/heat-flexibility-intelligence/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Wood Mackenzie | Data & analytics solutions' url='https://www.woodmac.com/'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Trade Mark Journal - Government of Bermuda' url='https://safekey.gov.bm/sites/default/files/2026-06/Trade%20Mark%20Journal%20No.%2096%20%28Part%20I%29.pdf'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Global Markets Poised for Further Gains as Geopolitical Risks Ease ...' url='https://www.creatingnycsmiles.com/expert-time/Global-Markets-Poised-for-Further-Gains-as-Geopolitical-Risks-Ease-and-AI-Earnings-Surge-34-17819'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Murex | 领英' url='https://cn.linkedin.com/company/murex'
[2026-06-29 21:47:22] INFO src.core.roster:  | hit title='Trade Mark Journal - Bernews' url='https://cloudfront.bernews.com/wp-content/uploads/2026/06/Trade-Mark-Journal-No.-96-Part-I.pdf'
[2026-06-29 21:47:13] INFO src.core.roster:  | hit title='Director – Cheminformatics Job in New York, NY at ... - Mediabistro' url='https://www.mediabistro.com/jobs/3540841490-director-cheminformatics'
[2026-06-29 21:47:13] INFO src.core.roster:  | hit title='Software Engineer - AI Products @ STARLIMS' url='https://careers.franciscopartners.com/companies/starlims-2/jobs/84442576-software-engineer-ai-products'
[2026-06-29 21:47:13] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:13] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:13] INFO src.core.roster: roster.run_inflow_discovery_batch index 4/20 configurable enterprise workflow automation -> 100 hit(s)
[2026-06-29 21:47:13] INFO src.core.roster:  | search_term='configurable enterprise workflow automation' raw_hits=100
[2026-06-29 21:47:13] INFO src.core.roster:  | hit title='Freshservice/Freshdesk Integration for Jira (FORGE)' url='https://marketplace.atlassian.com/apps/1227929/freshservice-freshdesk-integration-for-jira-forge'
[2026-06-29 21:47:13] INFO src.core.roster:  | hit title='Enterprise Systems Manager, Recruiting Systems - OpenAI' url='https://openai.com/careers/enterprise-systems-manager-recruiting-systems-san-francisco/'
[2026-06-29 21:47:13] INFO src.core.roster:  | hit title='MadCap IXIA CCMS for Policies & Procedures' url='https://www.madcapsoftware.com/solutions/ixia-ccms/policies-procedures/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='News and Blog-new - Dendi Software' url='https://dendisoftware.com/news-and-blog-new'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='navify® Pathology Lab Advantage - Roche Diagnostics' url='https://diagnostics.roche.com/us/en/products/instruments/navify-pathology-lab-advantage-ins-2105.html'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Search our Job Opportunities at Quest Diagnostics' url='https://careers.questdiagnostics.com/search-jobs'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Veterinary Diagnostic Laboratories' url='https://csuveterinaryhealth.org/veterinary-diagnostic-laboratories/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Cortechs.ai: Home' url='https://www.cortechs.ai/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Cloud First Digital Pathology in a High-Volume Regional Laboratory' url='https://www.clinicallab.com/your-model-from-our-experience-cloud-first-digital-pathology-in-a-high-volume-regional-laboratory-28681'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Sr. Program Manager, Clinical Chemistry & Immunoassay (Business ...' url='https://jobs.danaher.com/global/en/job/DANAGLOBALR1303753EXTERNALENGLOBAL/Sr-Program-Manager-Clinical-Chemistry-Immunoassay-Business-Unit'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Advances in Digital Pathology - LigoLab' url='https://www.ligolab.com/post/benefits-of-digital-pathology'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Leica Offers Up Free Video of its Popular Executive War College ...' url='https://www.clinicallab.com/leica-offers-up-free-video-of-its-popular-executive-war-college-session-28703'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Product Designer - AI and Enterprise Software Job Posting Title here' url='https://jobs.thermofisher.com/global/en/job/R-01353684/Product-Designer-AI-and-Enterprise-Software-Job-Posting-Title-here'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='p-Tau 205 Assay | Quanterix' url='https://www.quanterix.com/simoa-assay-kits-and-reagents/p-tau-205/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Boost empower software data with cloud-based AI - Select Science' url='https://www.selectscience.net/webinar/enhancing-empower-software-data-with-cloud-based-applications'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Serology Lab Tech (HC Pro 1-Clinical Lab Science) (# 374424)' url='https://www.higheredjobs.com/region/details.cfm?JobCode=179484179&Title=Serology%20Lab%20Tech%20(HC%20Pro%201-Clinical%20Lab%20Science)%20(%23%20374424)'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='CellCarta and Sonic Healthcare CDx Partnership' url='https://cellcarta.com/science-hub/cellcarta-sonic-healthcare-strategic-partnership/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Clinical Lab Scientist II - Sacramento - Thermo Fisher Scientific' url='https://jobs.thermofisher.com/global/en/job/R-01356538/Clinical-Lab-Scientist-II-Sacramento'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Lab Logic Brings Intelligent Case Orchestration to HALO AP® and ...' url='https://indicalab.com/news/halo-ap-lab-logic/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Molecular Diagnostics Software and Equipment Specialist - Jobvite' url='https://jobs.jobvite.com/neogenomics/job/okQnAfwR'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Neurology 4-Plex D (BD-Tau, NfL, GFAP*, UCH-L1 - Quanterix' url='https://www.quanterix.com/simoa-assay-kits-and-reagents/neurology-4-plex-d-bd-tau-nfl-gfap-uch-l1/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Phlebotomy & Medical Lab Technician: Patient-Focused Diagnostics' url='https://www.jobleads.com/us/job/phlebotomy-medical-lab-technician-patient-focused-diagnostics--boston--e9e0112a07b534ad9a7cb411830752683'
[2026-06-29 21:47:12] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:12] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:12] INFO src.core.roster: roster.run_inflow_discovery_batch index 3/20 cloud LIMS for biotech laboratories -> 100 hit(s)
[2026-06-29 21:47:12] INFO src.core.roster:  | search_term='cloud LIMS for biotech laboratories' raw_hits=100
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Agentic AI in Clinical Research - CloudLIMS' url='https://cloudlims.com/tag/agentic-ai-in-clinical-research/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Laboratory Information Management Systems (LIMS) Market' url='https://www.globenewswire.com/news-release/2026/06/26/3318323/0/en/laboratory-information-management-systems-lims-market-size-expected-to-reach-usd-5-19-billion-by-2030-marketsandmarkets.html'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='IT Support for Biotech & Life Sciences Companies - Boston Networks' url='https://bostonnetworks.com/industries-served/it-support-biotech-life-sciences/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='The 10 Best LIMS Platforms Leading Into 2026 - Genemod' url='https://genemod.net/blog/the-10-best-lims-platforms-leading-into-2026-features-trends-and-what-labs-need-next'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Integrating LIMS with AI in Laboratories for Scalable, Intelligent ...' url='https://www.labvantage.com/blog/integrating-lims-with-ai-in-laboratories-for-scalable-intelligent-digital-ecosystems/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Top 10 Benefits of LIMS Software for Pharmaceutical Laboratories' url='https://www.agaramtech.com/blog/top-10-benefits-of-lims-software-for-pharmaceutical-laboratories'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Inside Sales Specialist (Spanish) - Remote at CloudLIMS' url='https://dailyremote.com/remote-job/inside-sales-specialist-spanish-remote-5216628'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title="Biotechnology Lab Management Software: 2026 Buyer's Guide" url='https://newlabcloud.com/blog/biotechnology-lab-management-software-guide/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='MSCC Applications Support download | SourceForge.net' url='https://sourceforge.net/projects/mscc-applications-nsm/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Global LIMS market to reach $5.19B by 2030, dri... - Pluang' url='https://pluang.com/en/news-feed/pasar-sistem-manajemen-informasi-laboratorium-lims-diproyeksikan-meningkat'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='AI LIMS Optimization Projects - NTHRYS' url='https://www.nthrys.com/home/pdfs/projects/ai-lims-optimization.pdf'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Java Spring Engineer — LIMS & Biotech Workflows | San Diego' url='https://www.jobleads.com/us/job/java-spring-engineer-lims-biotech-workflows--san-diego--ec2097e503a2c3cb78b619cf271288d2a'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='List of electronic laboratory notebook software packages - Wikipedia' url='https://en.wikipedia.org/wiki/List_of_electronic_laboratory_notebook_software_packages'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='The Middleware Is Dead. Long Live the Balance. As ... - Instagram' url='https://www.instagram.com/p/DaDGOMYEo0s/'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='When self-hosted AI is worth it for biotech - CodePhusion' url='https://codephusion.com/blog/self-hosted-ai-for-biotech'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='CloudLIMS hiring Integration Engineer in Indore, Madhya Pradesh ...' url='https://in.linkedin.com/jobs/view/integration-engineer-at-cloudlims-4432633724'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='The convergence of AI-driven engineering biology and emerging ...' url='https://www.sciencedirect.com/science/article/pii/S0958166926000686'
[2026-06-29 21:47:12] INFO src.core.roster:  | hit title='Simplify your laboratory workflow with Cubis® III. No middleware. No ...' url='https://www.facebook.com/PharmaFocusEurope/posts/simplify-your-laboratory-workflow-with-cubis-iiino-middleware-no-hidden-costs-ju/1075250491927383/'
[2026-06-29 21:47:04] INFO dispatch.scheduler: Dispatching inflow_discovery — 1 available, batch inflow_discovery-4f4554af-e57a-49b4-9ec1-ed3a391317bb
[2026-06-29 21:47:04] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 1/1 inflow_discovery -> loop iteration 1 starting
[2026-06-29 21:47:04] INFO src.core.dispatcher:  | available=1 effective_min=1 max_runs=1 draining=False entity_batch_id=inflow_discovery-4f4554af-e57a-49b4-9ec1-ed3a391317bb
[2026-06-29 21:47:04] INFO src.core.dispatcher: dispatcher._run_task index 1/1 inflow_discovery -> running batch
[2026-06-29 21:47:04] INFO src.core.dispatcher:  | batch_size=10 batch_id=inflow_discovery-4f4554af-e57a-49b4-9ec1-ed3a391317bb entity_type='candidate' trigger_state='LIVE_PROMPTS'
[2026-06-29 21:47:04] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 candidate/LIVE_PROMPTS -> claimed 1 entity/entities
[2026-06-29 21:47:04] INFO src.core.dispatcher:  | task_key=inflow_discovery batch_id=inflow_discovery-4f4554af-e57a-49b4-9ec1-ed3a391317bb batch_call_mode=False dispatch batch_size=10 claim_cap=None
[2026-06-29 21:47:04] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 johnson -> claimed
[2026-06-29 21:47:04] INFO src.core.dispatcher:  | entity_type=candidate trigger_state=LIVE_PROMPTS state='LIVE_PROMPTS'
[2026-06-29 21:47:04] INFO src.core.roster: roster.run_inflow_discovery_batch index 1/20 biotech lab automation and data management -> 100 hit(s)
[2026-06-29 21:47:04] INFO src.core.roster:  | search_term='biotech lab automation and data management' raw_hits=100
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='AI in Regulated Labs: What Lab Managers Need to Know About GxP ...' url='https://www.labmanager.com/ai-in-regulated-labs-what-lab-managers-need-to-know-about-gxp-validation-and-data-integrity-35633'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Numera® fully automated modular bioprocess sampling - Securecell' url='https://www.securecell.ch/product-biotech/numera-advanced-bioprocess-sampling-solution'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Tecan Brings Agentic AI to Introspect Platform with NVIDIA BioNeMo ...' url='https://www.labmanager.com/tecan-brings-agentic-ai-to-introspect-platform-with-nvidia-bionemo-agent-toolkit-35613'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Managing Bioinformatics Workflows in Veterinary Diagnostics Using ...' url='https://www.globus.org/user-stories/managing-bioinformatics-workflows-in-veterinary-diagnostics-using-globus'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Automation - Page 2 of 3 - Drug Discovery World (DDW)' url='https://www.ddw-online.com/t/automation/page/2/'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Scientific Applications Analyst, Benchling - BIIE (Basel) - JOIN' url='https://join.com/companies/immune1/16363379-scientific-applications-analyst-benchling'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Agenda | BioTechX USA - Terrapinn' url='https://www.terrapinn.com/conference/biotechxusa/programme.stm'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Every delayed analytical result has a ripple effect. A ... - Instagram' url='https://www.instagram.com/p/DZ_74EVk9NN/'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Laboratory Information Management Systems (LIMS) Market' url='https://www.globenewswire.com/news-release/2026/06/26/3318323/0/en/laboratory-information-management-systems-lims-market-size-expected-to-reach-usd-5-19-billion-by-2030-marketsandmarkets.html'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='BTO | DARPA' url='https://www.darpa.mil/about/offices/bto'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Automated Flash Chromatography Purification Systems Market ...' url='https://www.indexbox.io/blog/automated-flash-chromatography-purification-systems-market-forecast-points-higher-toward-2035-driven-by-biopharma-automation-demands/'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title="Saziye Yorulmaz Avsar's Post - LinkedIn" url='https://www.linkedin.com/posts/saziye-yorulmaz-avsar-869791aa_aiusecase-helloworld-spos-activity-7475101624567234563-7HaE'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Senior Scientist – Protein Expression Sciences (Antibody Discovery)' url='https://regeneron.wd1.myworkdayjobs.com/en-us/careers/job/senior-scientist---protein-expression-sciences--antibody-discovery-_r48393-1'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Laboratory Software Market Size, Industry Outlook, and Growth ...' url='https://www.linkedin.com/pulse/laboratory-software-market-size-industry-outlook-d90ac'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Benefits and Types of Laboratory Automation Solutions' url='https://www.thermofisher.com/us/en/home/life-science/lab-equipment/lab-automation/why-automate.html'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Pascal Zimmermann ZenCELL 猫头鹰作者' url='https://zencellowl.com/zh/%E4%BD%9C%E8%80%85/%E5%B8%95%E6%96%AF%E5%8D%A1/'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Integrating LIMS with AI in Laboratories for Scalable, Intelligent ...' url='https://www.labvantage.com/blog/integrating-lims-with-ai-in-laboratories-for-scalable-intelligent-digital-ecosystems/'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Tecan and NVIDIA Add AI Capabilities to Introspect Lab Platform' url='https://clpmag.com/lab-management/company-news/tecan-nvidia-add-ai-introspect-lab-analytics-platform/'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='Senior Clinical Informatics Specialist Jobs in Massachusetts' url='https://migratemate.co/senior-clinical-informatics-specialist-jobs/massachusetts'
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='The convergence of AI-driven engineering biology and emerging ...' url='https://www.sciencedirect.com/science/article/pii/S0958166926000686'
[2026-06-29 21:47:04] INFO src.core.roster:  | ... 80 more hits omitted from log
[2026-06-29 21:47:04] INFO src.core.roster:  | last_scan_at bumped
[2026-06-29 21:47:04] INFO src.core.roster: roster.run_inflow_discovery_batch index 2/20 clinical lab software diagnostics -> 100 hit(s)
[2026-06-29 21:47:04] INFO src.core.roster:  | search_term='clinical lab software diagnostics' raw_hits=100
[2026-06-29 21:47:04] INFO src.core.roster:  | hit title='TALENT Software Services hiring Laboratory/Clinical Lab Scientist ...' url='https://www.linkedin.com/jobs/view/laboratory-clinical-lab-scientist-at-talent-software-services-4430277352'
```

### Comments

#### chuckles — 2026-07-02T23:21:22.997Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-839** | CSE debug verbose per-HTTP trace (pacing + request outcome) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-839** — _CSE debug verbose per-HTTP trace (pacing + request outcome)_
- **Issue reported:** With `debug=True` on inflow discovery, CSE pacing lines appear in a burst at one log timestamp (many `pacing: sleeping …` lines at 6:52:48 PM with no HTTP outcome between them). Susan cannot tell whether the process slept 12s between every CSE call or what each HTTP request retur
- **Should now:** When `debug=True`, each Google CSE HTTP request emits verbose debug under the current Style D index: pacing sleep (if any) **at the time it happens**, then the HTTP outcome (status code, pagination start, item count or rate-limit signal) before the next request — so UAT can corre
- **Quick check (this fix only):**
  1. Run inflow discovery with `debug=True` for a candidate with stale search terms (e.g. manual dispatch on staging).
  2. Open logs for `roster.run_inflow_discovery_batch`.
  3. Observe multiple `pacing: sleeping …` lines sharing the same timestamp and no per-request HTTP result lines.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-02T23:12:26.536Z
Yes, remember that debug logging should be VERBOSE for reasons just like this.

#### chuckles — 2026-07-02T23:09:58.378Z
[check-linear] answered (@susan)

Not 12s between every CSE call — inter_query_delay_sec is 1.2s between successive HTTP requests (including pagination inside one search_google_cse).

Same log timestamp on every pacing line: roster buffers pace_detail during the call and flushes after search_google_cse returns; sleeps already ran sequentially during pagination.

One term at max_results=100 can issue up to 10 HTTP pages (~9 pacing gaps, not 12s each displayed line).

Debug gap noted: we log pacing/retry text only, not per-HTTP status after each page — say the word if you want that in fix-uat.

— Chuckles

#### susan — 2026-07-02T23:08:42.670Z
Question for @chuckles Why did I see the pause showing repeatedly without any activity between them (in debug mode):

```
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 0.84s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
7/2/26, 6:52:48 PM	INFO	src.core.roster	| pacing: sleeping 1.20s before CSE HTTP request
```

Can you please check the actual code to make sure that we're not sleeping 12 seconds in between each and every CSE call?  Of we are, that's silly.  If we're not, why are we not adding debug content to declare the http request results?

#### chuckles — 2026-07-01T00:02:11.561Z
@susan

1. After pause-and-retry is exhausted on a 429 mid-batch, should discovery **stop the batch immediately** (leave remaining terms for the next dispatch) instead of continuing through the rest of the terms?
2. Preferred default values for inter-query delay (seconds) and rate-limit pause duration (seconds)?
3. Is the `UNIQUE constraint failed: job.company, job.job_title, job.company_job_id` crash at the end of the attached log in scope for this epic, or a separate ticket?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
