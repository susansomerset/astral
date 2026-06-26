# AST-626 — Table Upsert - ensure schema before running

<!-- linear-archive: AST-626 archived 2026-06-23 -->

## Linear archive (AST-626)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-626/table-upsert-ensure-schema-before-running  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan uses table upsert to move admin data between environments — Data Management **Table Upsert** (paste Copy Output JSON) and config-table sync (`agent_task`, `candidate`, `dispatch_task` via admin API and push/pull scripts). Astral applies column migrations lazily: each table’s `_ensure_*_schema` runs when normal app code first touches that table, not at deploy. Upsert validates that source columns exactly match the target’s current schema and rejects the job on mismatch — but upsert does not run schema ensure first (only `agent_task` in the Copy Output path today). On staging or any lightly used database, a table can exist with an older column set Susan has no other admin way to upgrade, so sync fails with “columns must match exactly” even though the running codebase knows the full schema. This fix restores environment sync as a reliable admin workflow.

## Functional scope

* **Schema ensure before validation:** At the start of every table upsert operation, run the target table’s idempotent lazy schema ensure (if one exists for that table) **before** comparing column lists or applying rows.
* **Copy Output upsert (Data Management):** The generic table upsert path (`table_copy_upsert`) ensures schema for the selected table, then proceeds with existing validate-then-apply semantics (PK required, exact column keys, FK all-or-nothing, `agent_task` versioning).
* **Config-table upsert:** The config-table upsert path (`upsert_config_table` / `apply_config_table_upsert`, used by push and pull scripts) ensures schema for `dispatch_task`, `agent_task`, and `candidate` before column comparison and merge.
* **Registry behavior:** Tables with a registered lazy ensure handler get migrated in place; tables with no handler behave as today (no-op ensure step).
* **Preserve existing upsert semantics:** Non-destructive merge, transactional rollback on constraint failure, and success counts (inserted / updated / skipped) unchanged from AST-373.

## Boundaries

* Does **not** change upsert merge rules, allowlists, or UI layout from AST-373 / AST-464 / AST-465.
* Does **not** invent new migrations — only invokes existing `_ensure_*_schema` logic already owned by the data layer.
* Does **not** fix true code-version skew (source running newer code with columns the target codebase does not know about). Susan must deploy matching code; this ticket fixes stale schema on the **same** deployed version.
* Does **not** add a standalone “migrate schema only” admin action; ensure runs as a side effect of upsert.
* Does **not** run schema ensure on server bootstrap, deploy, or scheduler tick (see [AST-383](https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy)).
* Must **not** break existing Data Management SQL, schema browser, Manage Tasks, or config-table push/pull scripts after ensure is added.

## Acceptance criteria

1. On a database where a upsert-eligible table exists but lazy migrations have never run for that table, pasting valid Copy Output JSON from a same-version source via Data Management **Table Upsert** completes successfully (or fails only on real validation/constraint errors — not column mismatch caused by missing ALTER columns).
2. Pushing or pulling `dispatch_task`, `agent_task`, or `candidate` between local and staging succeeds when the target table was previously “fresh” (no prior code path had triggered ensure for that table).
3. After ensure runs, if columns still differ (genuine skew), Susan sees the existing explicit mismatch error with got vs expected column lists — not a silent partial write.
4. `agent_task` upsert still honors Manage Tasks versioning: unchanged historical rows are no-ops; changed content creates new versions as today.
5. Tables without a lazy ensure handler upsert exactly as they do now.

## Dependencies and blockers

None.

## Open questions

None.

---

## Original brief

I cannot upsert content from local database vs the database on staging.  I get an error that the columns must match exactly, but it won't when the table is fresh, and there's no other way to trigger the lazy ensure.

### Comments

#### chuckles — 2026-06-14T20:37:56.562Z
@Susan — **finish-up blocked:** `finish-up-land.sh` needs `gh` authenticated on this machine (`gh auth login`). Installed `gh` via Homebrew; `create-dev-pr.py --create` fails before PR/land. Parent reassigned to you; wrap lock cleared. Re-run wrap after `gh auth login`, or land manually: `./scripts/git/finish-up-land.sh ast-626-table-upsert-ensure-schema-before-running`.

— Chuckles

#### chuckles — 2026-06-14T18:42:45.467Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-637** | company table upsert wrong-keys after AST-629 |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-14T18:35:46.985Z
## Git (fix-uat — bug dispatch)

| Ticket | `origin/…` |
|--------|------------|
| AST-637 | sub/AST-626/AST-637-uat-company-table-upsert-wrong-keys-after-ast-629 |

— Chuckles

#### susan — 2026-06-14T18:33:22.600Z
Still same issue.

Here is a sample of 2 records I'm trying to insert:

```
[
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"prefilter_company_notes\": \"Komodo Health is a healthcare data/AI platform company with strong domain alignment and clear product orientation. Multiple vectors grade well for Susan. | **Industry & Domain Alignment: A** \\u2014 Komodo operates squarely in healthcare technology, specifically healthcare data analytics, clinical data platforms, and AI for healthcare. Their 'Healthcare Map' is a longitudinal patient-level data platform serving life sciences and healthcare organizations. This is core health IT/clinical data.\\n\\n**Remote Work Compatibility: X** \\u2014 The homepage contains no information about office locations for employees, remote work policies, or hybrid arrangements. The site is product/customer-facing with no careers or culture signals visible.\\n\\n**Company Size & Stage: B** \\u2014 Komodo Health is a well-known growth-stage health tech company (Series E, ~400-500 employees based on public knowledge), but the homepage itself doesn't explicitly state employee count. However, the breadth of product lines (Healthcare Map, AI assistant 'Marmot', multiple enterprise use cases across clinical development, medical affairs, HEOR, commercial), the sophistication of the platform, and the enterprise-grade positioning all signal a company well past early startup stage and likely in the 200-1000 range. Grading B based on available signals suggesting mid-to-late growth stage.\\n\\n**Mission & Product Orientation: A** \\u2014 Clear product platform (Healthcare Map, conversational AI for healthcare analytics) with a mission oriented toward improving healthcare decision-making through real-world evidence and patient-level insights. Use cases span clinical trial recruitment, patient journey mapping, and outcomes research \\u2014 directly aligned with improving patient care and clinical systems.\\n\\n**US Presence & Time Zone Compatibility: X** \\u2014 The homepage does not explicitly state headquarters location or office locations. Komodo Health is known to be SF-based, but the scraped homepage content doesn't confirm this. No geographic information is visible.\\n\\nWith two A grades, one B, and two X grades, the company clears the WATCH threshold (at least 2 B-or-above, no F's). The two X grades are below the 3+ threshold for UNKNOWN.\", \"nav_links\": \"1: https://www.komodohealth.com/\\n2: https://www.komodohealth.com\\n3: https://www.komodohealth.com/solutions\\n4: https://www.komodohealth.com/solutions/marmot\\n5: https://www.komodohealth.com/solutions/software\\n6: https://www.komodohealth.com/solutions/mapai\\n7: https://www.komodohealth.com/solutions/maplab\\n8: https://www.komodohealth.com/solutions/maplab/maplab-enterprise\\n9: https://www.komodohealth.com/solutions/maplab/mapexplorer\\n10: https://www.komodohealth.com/mapview\\n11: https://www.komodohealth.com/komodo-drug-projections\\n12: https://www.komodohealth.com/solutions/custom-analytics\\n13: https://www.komodohealth.com/solutions/clinical-alerts\\n14: https://www.komodohealth.com/solutions/field-sales-insights\\n15: https://www.komodohealth.com/solutions/kol-profiling\\n16: https://www.komodohealth.com/solutions/medical-information-cloud\\n17: https://www.komodohealth.com/solutions/publications-planning\\n18: https://mavens.com/products/medical-affairs/research-grants\\n19: https://www.komodohealth.com/solutions/healthcare-map\\n20: https://www.komodohealth.com/solutions/mapenhance\\n21: https://www.komodohealth.com/industries\\n22: https://www.komodohealth.com/industries/life-sciences\\n23: https://www.komodohealth.com/industries/life-sciences/clinical-development\\n24: https://www.komodohealth.com/industries/life-sciences/commercial\\n25: https://www.komodohealth.com/industries/life-sciences/heor\\n26: https://www.komodohealth.com/industries/life-sciences/medical-affairs\\n27: https://www.komodohealth.com/industries/medtech\\n28: https://www.komodohealth.com/industries/patient-services\\n29: https://www.komodohealth.com/industries/consultancies\\n30: https://www.komodohealth.com/industries/financial-services\\n31: https://www.komodohealth.com/industries/government\\n32: https://www.komodohealth.com/industries/data-partners\\n33: https://www.komodohealth.com/industries/risk-bearing-entities\\n34: https://www.komodohealth.com/resources\\n35: https://www.komodohealth.com/perspectives\\n36: https://www.komodohealth.com/press\\n37: https://www.komodohealth.com/news\\n38: https://www.komodohealth.com/publications\\n39: https://www.komodohealth.com/qe-reports\\n40: https://www.komodohealth.com/events-webinars\\n41: https://www.komodohealth.com/company\\n42: https://www.komodohealth.com/company/\\n43: https://www.komodohealth.com/why-komodo\\n44: https://www.komodohealth.com/careers/life-at-komodo\\n45: https://www.komodohealth.com/careers\\n46: https://komodohealthsupport.zendesk.com/hc/en-us\\n47: https://www.komodohealth.com/get-demo\\n48: https://www.komodohealth.com/contact\\n49: https://www.komodohealth.com/demos\\n50: https://www.komodohealth.com/perspectives/real-world-insights-improve-kidney-cancer-outcomes\\n51: https://www.komodohealth.com/perspectives/fda-glp-1-approval-may-reduce-reliance-on-cpap\\n52: https://www.komodohealth.com/perspectives/ai-accelerates-early-commercialization\\n53: https://www.komodohealth.com/privacy-notice\\n54: https://www.linkedin.com/company/komodo-health\\n55: https://www.youtube.com/channel/UCNbTrJncBfa5iIUUndc4RFQ\\n56: https://twitter.com/komodohealth\\n57: https://www.komodohealth.com/global-expert-privacy-notice\\n58: https://www.komodohealth.com/terms-of-service\\n59: https://komodohealth-privacy.my.onetrust.com/webform/5c3cf8b1-3cf1-422d-84d5-618844b7316f/580adaab-6481-479f-9643-50464eea9863\\n60: https://trust.komodohealth.com\\n61: https://www.komodohealth.com/sitemap\\n62: https://www.onetrust.com/products/cookie-consent\", \"parse_instructions\": {\"container\": \"div.job-posts\", \"job_tag\": \"tr.job-post\"}, \"culture_links_to_explore\": [\"32\", \"30\", \"3\", \"27\", \"17\"], \"website_content\": [{\"url\": \"https://www.komodohealth.com/industries/data-partners\", \"content\": \"Skip to main content\\n\\n\\n\\n\\n\\n\\t\\t\\t\\t\\n \\t\\t\\n\\t\\t\\n\\n\\n\\n\\t\\n\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tPartnerships Make Your Offering Defensible From Day OneWhatever you sell, embed, or build, Komodo\\u2019s Healthcare Map and Marmot give it something no general AI platform can match. Hundreds of enterprise customers already run on them.Explore a Partnership\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tSkip a Decade of Data EngineeringThe Healthcare Map is the foundation you\\u2019d spend 10 years trying to build. A trillion+ linked records across 60+ sources, covering the full U.S. patient population, updated daily. It arrives analysis-ready, so your team starts where the hard work ends.Explore the Healthcare Map\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tAI Your Customers Can Actually DefendMarmot is Komodo\\u2019s AI engine. When you embed it, the governance comes with it. Reproducible outputs. Traceable methodology. Evaluation gates before anything reaches your customers. You build on top. The hard infrastructure is already there.Explore Marmot\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tYour Product on Komodo, Real DifferentiationPartners build on Komodo because it gives their product something the market can\\u2019t get anywhere else. The solutions they take to clients, the answers their customers rely on: none of that is available to a competitor starting from scratch. It shows in the market.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tOne Platform, Multiple Ways to Go to MarketEmbed Komodo in what you sell. Resell it to your book. Co-sell into shared accounts. Build something new together. Start with the motion that fits how you already work. Scale the one that wins. Hundreds of enterprise customers already trust what you\\u2019d be bringing them.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tMultiple Ways to Work Together, One First ConversationWalk us through what you sell, how you sell it, and where Komodo fits. We\\u2019ll map the path to a partnership that actually ships.Explore a Partnership\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\n\\n\\t\\n\\n\\n\\t\\t\\t\\n\\t\\t\\n\\n        \\n        \\n\\t\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n  \\n  \\n  \\n  \\n  \\n  \\n  \\n  \\n\\nCookiesThis site uses cookies to enhance user experience and analyze performance and traffic on our website. By clicking \\\"Allow Cookies,\\\" you are agreeing to the placement of cookies that we may use to share information about your use of our site with our social media, advertising, and analytics partners. Cookie NoticeCookie Settings  Allow CookiesYour Opt Out Preference Signal is HonoredCookie Consent SettingsWhen you visit our website, we store cookies on your browser to collect information. The information collected might relate to you, your preferences or your device, and is mostly used to make the site work as you expect it to and to provide a more personalized web experience. However, you can choose not to allow certain types of cookies, which may impact your experience of the site and the services we are able to offer. Click on the different category headings to find out more and change our default settings according to your preference. You cannot opt-out of our Essential Cookies as they are deployed in order to ensure the proper functioning of our website (such as prompting the cookie banner and remembering your settings, to log into your account, to redirect you when you log out, etc.). For more information about the First and Third Party Cookies used please follow this link.Allow All Manage Cookie Consent SettingsEssential CookiesAlways ActiveEssential cookies, also sometimes called strictly necessary cookies, are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work. Performance Cookies  Performance Cookies These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. For example, they help us to know which pages are the most and least popular and see how visitors move around the site. Targeting Cookies  Targeting Cookies These cookies may be set through our site by our advertising partners. They may be used by those companies to build a profile of your interests and show you relevant adverts on other sites. They are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising/marketing.Back ButtonBack  Clear checkbox label labelApply CancelConsent Leg.Interest  Switch Label label  Switch Label label  Switch Label label Confirm My Choices\"}, {\"url\": \"https://www.komodohealth.com/industries/financial-services\", \"content\": \"Skip to main content\\n\\n\\n\\n\\n\\n\\t\\t\\t\\t\\n \\t\\t\\n\\t\\t\\n\\n\\n\\n\\t\\n\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tFinancial Services If It\\u2019s in the Earnings Call, It\\u2019s Already Priced InKomodo surfaces prescribing shifts, payer moves, and adoption signals weeks before they hit earnings. Act before the market reprices.Get a Demo\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tSee the Signal Before the Market DoesEarnings calls, syndicated reports, and legacy open claims all arrive after the opportunity has already repriced. Komodo reveals the same market-moving behavior weeks earlier: prescribing uptake, adherence curves, and payer coverage shifts, at weekly cadence across 10,000+ drugs.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tMarket-Complete Data, Not a PanelMost datasets start with open claims. Everyone has those. The Healthcare Map goes further: exclusive payer-sourced data gives you longitudinal visibility into specialty markets, treatment decisions, and care patterns. Updated in near-real time. Built to catch what others miss.Explore the Healthcare Map\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tAI That Shows Its WorkMost AI gives you an answer. Marmot gives you the answer and the methodology behind it. Every output comes with visible code, traceable logic, and results your team can reproduce and defend. Get to the right answer, the same way, every time. In a room where \\u201cthe model said so\\u201d doesn\\u2019t fly, that matters.Explore Marmot\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tA 5X Return, and a Signal No One Else SawA multi-stage healthcare investor saw a step-change in specialty oncology script volume weeks before it surfaced in syndicated data. They increased position pre-acquisition, ahead of consensus, and realized a 5X return in six months. Not a lucky bet. A signal only Komodo made visible.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tBuilt for Every Stage of the DealLandscape a therapeutic area in an afternoon, not three weeks. Pressure-test a thesis against real prescribing behavior, not modeled estimates. Benchmark a target against live payer and provider data. Catch a portfolio shift before it becomes a question at your next meeting.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tSee the Signals Before the Market DoesWalk through a live analysis in your therapeutic area with a Komodo expert. Not a generic demo. A working session on a real question.Get a Personalized Demo\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\n\\n\\t\\n\\n\\n\\t\\t\\t\\n\\t\\t\\n\\n        \\n        \\n\\t\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n  \\n  \\n  \\n  \\n  \\n  \\n  \\n  \\n\\nYour Opt Out Preference Signal is HonoredCookie Consent SettingsWhen you visit our website, we store cookies on your browser to collect information. The information collected might relate to you, your preferences or your device, and is mostly used to make the site work as you expect it to and to provide a more personalized web experience. However, you can choose not to allow certain types of cookies, which may impact your experience of the site and the services we are able to offer. Click on the different category headings to find out more and change our default settings according to your preference. You cannot opt-out of our Essential Cookies as they are deployed in order to ensure the proper functioning of our website (such as prompting the cookie banner and remembering your settings, to log into your account, to redirect you when you log out, etc.). For more information about the First and Third Party Cookies used please follow this link.Allow All Manage Cookie Consent SettingsEssential CookiesAlways ActiveEssential cookies, also sometimes called strictly necessary cookies, are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work. Performance Cookies  Performance Cookies These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. For example, they help us to know which pages are the most and least popular and see how visitors move around the site. Targeting Cookies  Targeting Cookies These cookies may be set through our site by our advertising partners. They may be used by those companies to build a profile of your interests and show you relevant adverts on other sites. They are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising/marketing.Back ButtonBack  Clear checkbox label labelApply CancelConsent Leg.Interest  Switch Label label  Switch Label label  Switch Label label Confirm My Choices\"}, {\"url\": \"https://www.komodohealth.com/solutions\", \"content\": \"Skip to main content\\n\\n\\n\\n\\n\\n\\t\\t\\t\\t\\n \\t\\t\\n\\t\\t\\n\\n\\n\\n\\t\\n\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tKomodo SolutionsHealthcare Analytics AI, Built for Every TeamKomodo turns the most complete view of U.S. healthcare into verified answers your team can use. One Healthcare Map. One AI platform. Every decision grounded.See What Your Team Can Do\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tLife SciencesThe launch readout, the protocol design, the payer dossier, the KOL prep. Marmot runs the analysis in minutes, backed by 330M+ real patient journeys and methodology your team can stand behind.Explore Life Sciences Solutions\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tFinancial ServicesHealthcare moves markets. See the signal first. Treatment adoption curves, prescribing shifts, and competitive dynamics from real patient journeys, before they show up in earnings calls.Explore Financial Services Solutions\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tConsultanciesFrameworks are table stakes. Evidence wins engagements. Ground every patient journey, market sizing, and launch benchmark in real-world data your clients cannot pull themselves, and defend it cold.Explore Consultancy Solutions\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tPartnershipsBuild your product, service or platform on the most complete view of US healthcare. Integrate the Healthcare Map, deploy Marmot as your AI engine, and give every customer answers nobody else can reproduce.Explore Partnership Solutions\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tPayersComplete member profiles. National benchmarks. Risk captured before the next coding cycle. Marmot turns the most complete view of U.S. healthcare into defensible risk models and utilization forecasts.Explore Payer Solutions\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tAgenciesWin the pitch. Keep the retainer. Back every brief, audience build, and media plan with real patient journeys and provider behavior. Your strategy holds up because the data does.Explore Agency Solutions\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u201cKomodo\\u2019s clinical alerts have revolutionized our way of doing business. We have relevant, accurate information at the precise moment we need it for our conversations with providers.\\u201d\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\tVP of Sales\\u00b7Large Biopharma\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tEvery Decision Your Team Makes Shapes Patient CareThat\\u2019s the work Komodo was built for. Bring us the question you are trying to answer. The trial you are trying to design. The signal you are trying to read. We will show you how Marmot delivers an answer you can act on today, built on the Healthcare Map only Komodo has.Talk to an Expert\\u00a0\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\n\\n\\t\\n\\n\\n\\t\\t\\t\\n\\t\\t\\n\\n        \\n        \\n\\t\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n  \\n  \\n  \\n  \\n  \\n  \\n  \\n  \\n\\nYour Opt Out Preference Signal is HonoredCookie Consent SettingsWhen you visit our website, we store cookies on your browser to collect information. The information collected might relate to you, your preferences or your device, and is mostly used to make the site work as you expect it to and to provide a more personalized web experience. However, you can choose not to allow certain types of cookies, which may impact your experience of the site and the services we are able to offer. Click on the different category headings to find out more and change our default settings according to your preference. You cannot opt-out of our Essential Cookies as they are deployed in order to ensure the proper functioning of our website (such as prompting the cookie banner and remembering your settings, to log into your account, to redirect you when you log out, etc.). For more information about the First and Third Party Cookies used please follow this link.Allow All Manage Cookie Consent SettingsEssential CookiesAlways ActiveEssential cookies, also sometimes called strictly necessary cookies, are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work. Performance Cookies  Performance Cookies These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. For example, they help us to know which pages are the most and least popular and see how visitors move around the site. Targeting Cookies  Targeting Cookies These cookies may be set through our site by our advertising partners. They may be used by those companies to build a profile of your interests and show you relevant adverts on other sites. They are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising/marketing.Back ButtonBack  Clear checkbox label labelApply CancelConsent Leg.Interest  Switch Label label  Switch Label label  Switch Label label Confirm My Choices\"}, {\"url\": \"https://www.komodohealth.com/industries/medtech\", \"content\": \"Skip to main content\\n\\n\\n\\n\\n\\n\\t\\t\\t\\t\\n \\t\\t\\n\\t\\t\\n\\n\\n\\n\\t\\n\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tSee the Medical Device Market Like Never BeforeObtain rich, granular insights by viewing the patient journey in real time \\u2014 across providers, care settings, and payers \\u2014 using our Healthcare Map\\u00ae and purpose-built softwareTalk to an Expert\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\tInsights at Your Fingertips \\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tAssess the Market, Accelerate TrialsUse real-world evidence (RWE) to assess volume by HCP and facility, case and payer mix, and readmission and re-operation rates. Expedite clinical trials and regulatory approvals using external control arms.Learn More About MapView\\u2122\\u00a0\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tAccelerate Commercial SuccessView volume by provider and across care sites (e.g., inpatient vs. ambulatory care centers) to optimize HCP targeting, timing, and messaging. Use clinical alerts to identify patients and engage HCPs.Learn More About Brand Performance and Clinical Alerts\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tInterested in Learning More? Let\\u2019s Connect!Find out how we can help you overcome your biggest healthcare challenges.Talk to an Expert\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tSurface KOLsUse a multifaceted approach that balances clinical volume, network and referral patterns, and scientific and industry engagement. Segment HCPs by academic vs. community-care setting.Learn More About KOL Profiling\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tExpedite Market Access With Real-World EvidencePower HEOR studies with robust patient-level insights that includes payer enrollment data. Leverage a flexible analytics environment and pre-built modules, or engage our analytics consulting team.Learn More About Custom Analytics\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u201cKomodo is committed to our discussions and partnership. We use MapView every day to leverage the incredible data and insights that help us drive strategic direction and tactical execution.\\u201d\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\tDirectorMedTech Company\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tLet\\u2019s ConnectFind out how you can gain a velocity advantage with Komodo Health.Talk to an Expert\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\n\\n\\t\\n\\n\\n\\t\\t\\t\\n\\t\\t\\n\\n        \\n        \\n\\t\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\t\\t\\t\\n\\t\\t\\t\\n\\n\\n\\nYour Opt Out Preference Signal is HonoredCookie Consent SettingsWhen you visit our website, we store cookies on your browser to collect information. The information collected might relate to you, your preferences or your device, and is mostly used to make the site work as you expect it to and to provide a more personalized web experience. However, you can choose not to allow certain types of cookies, which may impact your experience of the site and the services we are able to offer. Click on the different category headings to find out more and change our default settings according to your preference. You cannot opt-out of our Essential Cookies as they are deployed in order to ensure the proper functioning of our website (such as prompting the cookie banner and remembering your settings, to log into your account, to redirect you when you log out, etc.). For more information about the First and Third Party Cookies used please follow this link.Allow All Manage Cookie Consent SettingsEssential CookiesAlways ActiveEssential cookies, also sometimes called strictly necessary cookies, are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work. Performance Cookies  Performance Cookies These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. For example, they help us to know which pages are the most and least popular and see how visitors move around the site. Targeting Cookies  Targeting Cookies These cookies may be set through our site by our advertising partners. They may be used by those companies to build a profile of your interests and show you relevant adverts on other sites. They are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising/marketing.Back ButtonBack  Clear checkbox label labelApply CancelConsent Leg.Interest  Switch Label label  Switch Label label  Switch Label label Confirm My Choices\"}, {\"url\": \"https://www.komodohealth.com/solutions/publications-planning\", \"content\": \"Skip to main content\\n\\n\\n\\n\\n\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\n\\n\\n\\t\\n\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tCan Your Publications Keep Up With The Science?Mavens\\u00ae Scientific Publications Cloud is a Salesforce-powered work management solution for scientific publications teams that need to move fast.If you\\u2019ve struggled with low external portal adoption or showing the impact of publications, see what\\u2019s next when you connect the dots with people, data, and AI. See How We Implement In 30 Days\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tThere\\u2019s A Better Way To Manage PublicationsWhen your team is buried and authors are frustrated, it\\u2019s time to find a better way to work.Mavens\\u00ae Scientific Publications Cloud is a work management solution for scientific publications that gives your authors, reviewers, and leadership one place to work. Powered by Salesforce and purpose-built for regulated environments, you\\u2019ll have the flexibility and security you need to stop managing the process and start getting the science into the hands of people who need it.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tAbout Mavens\\u00ae Scientific Publications Cloud\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tA system that works the way your team actually works.Disconnected tools and teams are brought together with Mavens\\u00ae Scientific Publications Cloud. Implementations can be as short as 30 days with options for both out-of-the-box and complex configurations. You get the real-time information you need to make better decisions across everything from regions to agencies.\\u00a0\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n15+\\nyears of providing expert CRM and workflow solutions to Life Sciences\\n\\n\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t150+implementations globally for Top 20 and emerging pharmaceutical\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t5k+people collaborating on Mavens\\u00ae Scientific Publications Cloud\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tMavens\\u00ae Scientific Publications Cloud Features\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u00a0TransparentIncrease visibility into key milestones with a configurable timeline view.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u00a0\\u00a0ScalableEnterprise-grade scalability on Salesforce, supporting growth across the organization.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u00a0\\u00a0CollaborativeEnable authors and reviewers to collaborate on shared documents in real time.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u00a0IntegratedPre-built integrations include Altmetric for smarter decision-making on journal and congress selection.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u00a0\\u00a0AdaptableConfigurable to your SOPs and governance model, with security and role-based access across teams.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u00a0AI Powered by AgentforceGoverned AI workflows that speed publications planning, review, and decision-making.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tGet A Demo Now\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tScientific Publications Cloud AI Features\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tWhen you need to do more with less.\\nAre you AI-ready with your current system? With Mavens\\u00ae Scientific Publications Cloud, you are. Empower your team with practical and compliant AI directly where the work happens day-to-day.\\u00a0From intelligent predictive journal/congress target selection to automatic journal reformatting, we\\u2019re building AI features that work for scientific publications teams.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tGenerative Plain Language SummariesAI generated to translate complex scientific content into clear, accessible language for broader audiences.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\u00a0Automatic Document Quality Check AI reviews content against standards to flag gaps, inconsistencies, and potential risks before submission.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tHelper Agent Directly Embedded In AppConversational AI agent helps users navigate faster, answer questions, and surface relevant information.\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tWant To Learn More?Download this one-pager on Mavens\\u00ae Scientific Publications Cloud to learn more about connecting the dots between people, data, and AI.Instant Download\\t\\t\\t\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\t\\n\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\n\\t\\t\\t\\t\\t\\t\\t\\t\\tTalk To The Experts At MavensNow is the time to modernize medical affairs for scientific publications. If\\u00a0you want a system that is flexible and secure enough to stand the test of time, work with the team that has 15+ years of medical affairs and Salesforce experience at Mavens.See Why The Top 20 Use Mavens\"}]}",
    "company_name": "Komodohealth",
    "company_website": "https://komodohealth.com",
    "created_at": "2026-03-05 22:03:13",
    "job_site": "https://www.komodohealth.com/careers",
    "last_scan_at": "2026-06-14 17:30:14",
    "short_name": "komodohealth",
    "state": "WATCH",
    "state_history": "[{\"to_state\": \"TO_WATCH\", \"timestamp\": \"2026-03-06 02:25:28\", \"batch_id\": \"5fda8acb-9df9-4f8c-86ce-db8fcf546fbc\"}, {\"to_state\": \"TO_PARSE\", \"timestamp\": \"2026-03-07 05:21:11\", \"batch_id\": \"55e41a7e-9aa4-43cc-8e2e-5ac1eebdf6d6\"}, {\"to_state\": \"WATCH\", \"timestamp\": \"2026-03-09 04:11:19\", \"batch_id\": \"7dc70515-b023-4efb-9408-22db02163458\"}, {\"to_state\": \"ERROR_GAZE\", \"timestamp\": \"2026-04-08 02:08:31\", \"batch_id\": \"gaze-59e29c63-8133-43cc-9fb6-93fb8f496857\"}, {\"to_state\": \"ERROR_GAZE\", \"timestamp\": \"2026-04-30 11:56:03\", \"batch_id\": \"gaze-84b2096c-04d6-4b05-9509-2839ee575495\"}]",
    "state_updated_at": "2026-04-30 11:56:03",
    "updated_at": "2026-06-14 17:30:14"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"prefilter_company_notes\": \"PagerDuty is a well-established enterprise SaaS/cloud infrastructure platform company headquartered in San Francisco, fitting squarely in Susan's adjacent domain experience. Strong B+ profile across most vectors with no disqualifying signals. | Industry & Domain Alignment: B \\u2014 PagerDuty is an enterprise SaaS platform focused on incident management, AIOps, and operational automation for DevOps/engineering teams. This is squarely in the 'enterprise SaaS, cloud infrastructure/platforms' adjacent domain Susan has direct experience in. Not healthcare, so not A.\\n\\nRemote Work Compatibility: X \\u2014 The homepage does not provide any information about remote work policies, office requirements, or work location expectations. There are no career page details or location signals beyond the product itself.\\n\\nCompany Size & Stage: C \\u2014 PagerDuty serves 30,000+ companies, has 700+ integrations, and features enterprise customers like Zoom, FOX, and DraftKings. This is a publicly traded company (NYSE: PD) with likely well over 1,000 employees. However, as a tech-native SaaS company, it likely operates with product-team autonomy and modern engineering culture, warranting C rather than D.\\n\\nMission & Product Orientation: B \\u2014 Clear technical platform (Operations Cloud) with a meaningful mission around operational resilience, incident management, and reducing downtime. AI-powered, solving complex infrastructure problems for technical teams. Not healthcare-oriented but genuinely solving hard, meaningful problems.\\n\\nUS Presence & Time Zone Compatibility: A \\u2014 PagerDuty is headquartered in San Francisco, CA \\u2014 Pacific time zone, ideal for Susan.\", \"nav_links\": \"1: https://www.pagerduty.com/\\n2: https://www.pagerduty.com/on-tour\\n3: https://www.pagerduty.com\\n4: https://www.pagerduty.com/pricing/incident-management\\n5: https://www.pagerduty.com/search\\n6: https://www.pagerduty.com/de\\n7: https://www.pagerduty.com/fr\\n8: https://www.pagerduty.co.jp\\n9: https://www.pagerduty.com/contact-us\\n10: https://app.pagerduty.com\\n11: https://www.pagerduty.com/sign-up\\n12: https://www.pagerduty.com/platform/incident-management\\n13: https://www.pagerduty.com/ai\\n14: https://www.pagerduty.com/platform/automation\\n15: https://www.pagerduty.com/platform/ai-agents\\n16: https://www.pagerduty.com/platform/business-ops/status-pages\\n17: https://www.pagerduty.com/platform/generative-ai\\n18: https://www.pagerduty.com/platform/business-ops\\n19: https://www.pagerduty.com/platform/aiops\\n20: https://developer.pagerduty.com\\n21: https://www.pagerduty.com/services\\n22: https://www.pagerduty.com/security\\n23: https://www.pagerduty.com/enterprise\\n24: https://www.pagerduty.com/integrations\\n25: https://www.pagerduty.com/prompt-library\\n26: https://www.pagerduty.com/solutions/incident-management-transformation\\n27: https://www.pagerduty.com/solutions/operations-center-modernization\\n28: https://www.pagerduty.com/solutions/automation-coe\\n29: https://www.pagerduty.com/solutions/cx-operations\\n30: https://www.pagerduty.com/solutions/digital-resilience\\n31: https://www.pagerduty.com/solutions/scaled-service-ownership\\n32: https://www.pagerduty.com/solutions/remote-location-operations-automation\\n33: https://www.pagerduty.com/use-cases/security-incident-management\\n34: https://www.pagerduty.com/use-cases/llmops\\n35: https://www.pagerduty.com/use-cases/dataops\\n36: https://www.pagerduty.com/use-cases/finops\\n37: https://www.pagerduty.com/use-cases/complianceops\\n38: https://www.pagerduty.com/use-cases/crisisops\\n39: https://www.pagerduty.com/use-cases\\n40: https://www.pagerduty.com/industries/financial-services\\n41: https://www.pagerduty.com/industries/healthcare\\n42: https://www.pagerduty.com/industries/nonprofit\\n43: https://www.pagerduty.com/industries/government\\n44: https://www.pagerduty.com/industries/education\\n45: https://www.pagerduty.com/industries/retail\\n46: https://www.pagerduty.com/industries/ai-infrastructure\\n47: https://www.pagerduty.com/in-perspective\\n48: https://www.pagerduty.com/company/awards\\n49: https://careers.pagerduty.com/home\\n50: https://investor.pagerduty.com/overview/default.aspx\\n51: https://www.pagerduty.com/leadership\\n52: https://www.pagerduty.com/newsroom\\n53: https://www.pagerduty.com/company\\n54: https://www.pagerduty.com/impact-hub\\n55: https://www.pagerduty.com/assets/fy25-pagerduty-impact-report.pdf\\n56: https://www.pagerduty.com/resources\\n57: https://www.pagerduty.com/blog\\n58: https://www.pagerduty.com/demo\\n59: https://www.pagerduty.com/resources/?type=webinar\\n60: https://www.pagerduty.com/events\\n61: https://www.pagerduty.com/resources/?type=ebook\\n62: https://www.pagerduty.com/customer/tui\\n63: https://www.pagerduty.com/customer/zoom-video-communications\\n64: https://www.pagerduty.com/customer/spotify-backstage\\n65: https://www.pagerduty.com/customer/draftkings\\n66: https://www.pagerduty.com/customer/australian-bank\\n67: https://www.pagerduty.com/customer/vodafone\\n68: https://www.pagerduty.com/customer/fox\\n69: https://www.pagerduty.com/customers\\n70: https://university.pagerduty.com\\n71: https://community.pagerduty.com\\n72: https://www.pagerduty.com/ops-guides\\n73: https://support.pagerduty.com\\n74: https://www.pagerduty.com/on-tour/on-demand\\n75: https://www.pagerduty.com/platform/operations-cloud\\n76: https://www.pagerduty.com/request-a-demo\\n77: https://www.pagerduty.com/whats-new\\n78: https://www.pagerduty.com/try-pagerduty-aiops\\n79: https://www.pagerduty.com/contact-us/process-automation\\n80: https://www.pagerduty.com/contact-us/customer-service-operations\\n81: https://www.pagerduty.com/intervention\\n82: https://www.pagerduty.com/customer/zoom\\n83: https://www.pagerduty.com/customer/coxautomotive\\n84: https://www.pagerduty.com/digital-operations-management\\n85: https://www.pagerduty.com/foundation\\n86: https://investor.pagerduty.com\\n87: https://www.pagerduty.com/pagerduty-supplier-hub\\n88: https://www.pagerduty.com/careers\\n89: https://status.pagerduty.com\\n90: https://www.pagerduty.com/support\\n91: https://www.pagerduty.com/partner-with-pagerduty\\n92: https://www.pagerduty.com/legal\\n93: https://www.pagerduty.com/faq\\n94: https://www.pagerduty.com/accessibility-statement\\n95: https://www.pagerduty.com/university\\n96: https://www.facebook.com/PagerDuty\\n97: https://x.com/pagerduty\\n98: https://www.instagram.com/pagerduty\\n99: https://www.linkedin.com/company/pagerduty\\n100: https://www.pagerduty.com/privacy-policy\\n101: https://www.pagerduty.com/website-terms-of-use\\n102: https://www.pagerduty.com/privacy-policy/\\n103: https://www.pagerduty.com/assets/uk-modern-slavery-act-statement.pdf\\n104: https://www.pagerduty.com/ccpa\\n105: https://www.onetrust.com/products/cookie-consent\", \"parse_instructions\": {\"container\": \"table.table\", \"job_tag\": \"tr[data-action]\"}, \"culture_links_to_explore\": [\"56\", \"57\", \"54\", \"51\", \"100\"]}",
    "company_name": "Pagerduty",
    "company_website": "https://pagerduty.com",
    "created_at": "2026-03-05 22:03:13",
    "job_site": "https://careers.pagerduty.com/jobs/search",
    "last_scan_at": "2026-06-14 17:25:48",
    "short_name": "pagerduty",
    "state": "WATCH",
    "state_history": "[{\"to_state\": \"TO_WATCH\", \"timestamp\": \"2026-03-06 02:25:48\", \"batch_id\": \"5fda8acb-9df9-4f8c-86ce-db8fcf546fbc\"}, {\"to_state\": \"TO_PARSE\", \"timestamp\": \"2026-03-07 05:21:39\", \"batch_id\": \"55e41a7e-9aa4-43cc-8e2e-5ac1eebdf6d6\"}, {\"to_state\": \"WATCH\", \"timestamp\": \"2026-03-09 04:11:38\", \"batch_id\": \"7dc70515-b023-4efb-9408-22db02163458\"}, {\"to_state\": \"ERROR_GAZE\", \"timestamp\": \"2026-04-08 02:08:31\", \"batch_id\": \"gaze-59e29c63-8133-43cc-9fb6-93fb8f496857\"}, {\"to_state\": \"ERROR_GAZE\", \"timestamp\": \"2026-04-29 08:30:16\", \"batch_id\": \"gaze-19d2b4db-c667-4cd8-abae-49f03e927963\"}]",
    "state_updated_at": "2026-04-29 08:30:16",
    "updated_at": "2026-06-14 17:25:48"
  }
]
```

and the pragma table_info in staging:

```
[
  {
    "cid": 0,
    "dflt_value": null,
    "name": "short_name",
    "notnull": 0,
    "pk": 1,
    "type": "TEXT"
  },
  {
    "cid": 1,
    "dflt_value": null,
    "name": "state",
    "notnull": 1,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 2,
    "dflt_value": null,
    "name": "company_name",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 3,
    "dflt_value": null,
    "name": "company_website",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 4,
    "dflt_value": null,
    "name": "job_site",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 5,
    "dflt_value": null,
    "name": "batch_id",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 6,
    "dflt_value": null,
    "name": "batch_created_at",
    "notnull": 0,
    "pk": 0,
    "type": "TIMESTAMP"
  },
  {
    "cid": 7,
    "dflt_value": null,
    "name": "company_data",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 8,
    "dflt_value": "'[]'",
    "name": "agent_responses",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 9,
    "dflt_value": "CURRENT_TIMESTAMP",
    "name": "created_at",
    "notnull": 0,
    "pk": 0,
    "type": "TIMESTAMP"
  },
  {
    "cid": 10,
    "dflt_value": "CURRENT_TIMESTAMP",
    "name": "updated_at",
    "notnull": 0,
    "pk": 0,
    "type": "TIMESTAMP"
  },
  {
    "cid": 11,
    "dflt_value": null,
    "name": "state_updated_at",
    "notnull": 0,
    "pk": 0,
    "type": "TIMESTAMP"
  },
  {
    "cid": 12,
    "dflt_value": null,
    "name": "candidate_id",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 13,
    "dflt_value": null,
    "name": "last_scan_at",
    "notnull": 0,
    "pk": 0,
    "type": "TIMESTAMP"
  },
  {
    "cid": 14,
    "dflt_value": "'[]'",
    "name": "state_history",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  },
  {
    "cid": 15,
    "dflt_value": null,
    "name": "agent_responses_legacy",
    "notnull": 0,
    "pk": 0,
    "type": "TEXT"
  }
]
```

and the index list:

```
[
  {
    "name": "idx_company_name",
    "origin": "c",
    "partial": 0,
    "seq": 0,
    "unique": 0
  },
  {
    "name": "idx_company_state",
    "origin": "c",
    "partial": 0,
    "seq": 1,
    "unique": 0
  },
  {
    "name": "sqlite_autoindex_company_1",
    "origin": "pk",
    "partial": 0,
    "seq": 2,
    "unique": 1
  }
]
```

#### chuckles — 2026-06-14T17:36:10.634Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-629** | Table upsert wrong-keys error persists on origin/dev |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-14T17:21:19.319Z
## Git (fix-uat — bug dispatch)

| Ticket | `origin/…` |
|--------|------------|
| AST-629 | sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev |

— Chuckles

#### susan — 2026-06-14T17:19:43.072Z
@chuckles Issue persists on origin dev.  "columns must exactly match table layout (wrong keys)"

#### chuckles — 2026-06-14T05:53:01.295Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-626 (parent) | ftr/ast-626-table-upsert-ensure-schema-before-running |
| AST-627 | sub/AST-626/AST-627-schema-ensure-before-table-upsert-validation |

**Epic worktree:** `astral-AST-626/` — one active sub checked out at a time.

## Joan session (required for all store-* handoffs)

**Session id:** `f3720e1b-aba9-4cfa-ab9f-aadd1a101333`
**Parent:** AST-626

## Agent sessions (headless `--resume`)

| Ticket | Agent | Role | Session id |
|--------|-------|------|------------|
| AST-627 | Ada | engineer | `cb79add5-4e9a-42a3-888b-ef954e730c70` |
| AST-627 | Betty | qa | `b579a082-eb11-4e9f-891c-a4cbaa4cbb07` |
| AST-627 | Radia | review | `463a73ff-4530-4a41-ab4e-190b1d0d7570` |

**Parent:** AST-626

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
