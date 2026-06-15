# AST-490 — Roster inflow

<!-- linear-archive: AST-490 archived 2026-06-15 -->

## Linear archive (AST-490)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-490/roster-inflow  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-180

### Description

## Purpose

Growing a candidate's company roster today is mostly manual — Susan adds employers one at a time and the existing pipeline only helps once a company is already on the list with a website. That does not scale as a way to *discover* new employers worth watching. This feature delivers an automated **roster inflow** path: generate and maintain candidate-specific discovery search terms, run periodic Google searches to widen the net, vet and resolve hits to homepages, grade homepages with a token-efficient encoded rubric prefilter, then advance qualifying companies through job-page locate and parse — using the **same dispatch, state-machine, and batch patterns as gazer/job workflows**. Google Custom Search is to roster as Playwright is to gazer.

## Functional scope

* **Company search terms artifact (Phase 0):** A candidate **artifact** (not a profile field) holding a line-break-delimited list of Google discovery query strings — central to roster growth. An AI craft task generates terms from candidate profile and context. The artifact is **regenerable from the Artifacts UI** or **editable directly** by the user, same as other craft artifacts. Phase 0 runs **on demand only** via dispatch.
* **Discovery search (Phase 1):** For each search term on the active candidate, run a **general Google Custom Search** (no domain/site filters). Request up to **100 results** with a **7-day date restrict**. Scheduled like **gaze**: **weekly per candidate**, configured explicitly in the task dispatcher alongside existing job tasks.
* **Search-hit vetting (Phase 1):** An AI task reviews discovery hits and, for each result, returns a proposed **company slug** (AI-assigned), **ignore**, and optionally a **website URL** when the search result already exposes one.
* **Ingest new companies (Phase 1):** Roster provides an ingest path (e.g. ingest_new_companies) that creates **NEW** company rows for accepted hits, scoped to the candidate. Before insert, **pattern-match candidate company URLs** against existing roster URLs for that candidate to skip duplicates. The 7-day date filter **minimizes but does not eliminate** repeat hits across weekly runs — dedupe handles what slips through.
* **Website-resolution search (Phase 2):** For **NEW** companies **without** a URL from Phase 1, run a follow-on Google search (up to **20 results**, **no date restrict**). State-machine driven like downstream job tasks.
* **Website selection (Phase 2):** An AI task picks the likely official homepage from resolution hits.
* **Website resolution outcomes:** **NEW → WEBSITE_FOUND** when a homepage is confirmed (from Phase 1 optional URL **or** Phase 2). **NEW → NO_WEBSITE** when resolution fails. When Phase 1 already supplied a URL, Phase 2 is **skipped** via an alternate state-machine path (not a separate code column).
* **Homepage prefilter (Phase 3):** Scrape homepage visible text; run updated **prefilter_company** returning **compact encoded rubric** (not narrative JSON). **Dealbreaker F → PREFILTER_FAILED**; all other outcomes → **PREFILTER_PASSED** with persisted rubric score. No threshold-based pass/fail at prefilter.
* **Job-page discovery (Phase 4):** **PREFILTER_PASSED** companies are eligible for locate_job_page via **dispatch_task score_floor** — same pattern as scored job tasks (candidate/UI filters by score; no extra orchestration code). Phase 4 does not auto-block below-floor companies in application logic.
* **Job-list parse (Phase 5):** Confirmed job pages use existing parse flow to obtain parse instructions and reach **WATCH** when successful.
* **Batch orchestration:** Phases 0–5 use existing **dispatch_tasks**, state registry, batch claim, and scheduler patterns. No parallel orchestration model.
* **Single epic delivery:** Full Phase 0–5 pipeline under AST-490; dispatch may decompose into child tickets but not phased partial release.

## Boundaries

* **Two ingest entry states:** **NEW** is inflow-only (discovery pipeline). **IMPORTED** remains the manual-import entry — if the candidate imported it, the product does not second-guess whether to watch it. **IMPORTED → NO_WEBSITE / NO_JOBSITE / WATCH** behavior is **out of scope** for this ticket.
* **Pattern fidelity (Susan directive):** Implementation must mirror gazer/job dispatch and state-machine patterns. Any plan that introduces **new DB columns**, novel batch mechanics, or divergent orchestration outside established config + dispatch_tasks must be **flagged to Susan before build**.
* **No domain filters:** Phase 1 and Phase 2 use open Google searches — not [AST-488](https://linear.app/astralcareermatch/issue/AST-488/use-company-search-criteria-to-search-for-companies-using-google-cse) site-restriction filters.
* **Prefilter change:** prefilter_company moves to encoded rubric output and dealbreaker-only failure; locate_job_page and parse_job_list flows unchanged aside from trigger states.
* **Not AST-488/489 deliverables:** CSE client exists; this wires it into roster product flow.
* **Not board scraping or tracker job ingest** (see related job-dedupe ticket for candidate-scoped job dedupe — separate scope).
* **Not multi-provider LLM routing** ([AST-491](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek)).
* **Not inflow review-queue UI in v1.**
* **Not** [AST-180](https://linear.app/astralcareermatch/issue/AST-180/revisit-no-job-site-states) **(NO_JOB_SITE fallback).**
* **Config discipline:** States, task keys, result limits (100 / 20), date restrict, scan interval, and score_floor live in config / dispatch_tasks — not inline magic numbers.

## Acceptance criteria

 1. Phase 0 craft task populates a candidate artifact with a non-empty line-break-delimited search-term list; user can regenerate or edit it in Artifacts UI.
 2. Phase 0 dispatch is on-demand only; Phase 1 dispatch runs weekly per candidate (7-day scan interval) via task dispatcher configuration.
 3. Phase 1 executes general Google CSE searches (no site filters), up to 100 results, with 7-day date restrict, using terms from the artifact.
 4. Phase 1 vetting returns slug, ignore, and optional URL per hit; ignored hits do not create company rows.
 5. ingest_new_companies (or equivalent roster ingest) creates **NEW** rows for accepted hits; URL pattern-match dedupe skips companies whose URLs already exist on the **candidate's** roster.
 6. When Phase 1 supplies a URL, the company reaches **WEBSITE_FOUND** without Phase 2 dispatch.
 7. Phase 2 runs only for **NEW** companies lacking a URL; searches return up to 20 results with no date restrict; selection task resolves **WEBSITE_FOUND** or **NO_WEBSITE**.
 8. Phase 3 prefilter uses encoded rubric output; dealbreaker F → **PREFILTER_FAILED**; otherwise → **PREFILTER_PASSED** with rubric score stored — regardless of non-dealbreaker grades.
 9. Phase 4 locate_job_page dispatch claims **PREFILTER_PASSED** companies using **score_floor** on the dispatch_task row (job-task pattern); below-floor companies remain **PREFILTER_PASSED** until claimed.
10. Phase 5 parse succeeds through existing locate/parse flows to the same terminal watching states as today's manual path.
11. Manual-import companies continue to enter at **IMPORTED**; this ticket does not change that path.
12. Each inflow phase is invokable as schedulable dispatch work — not ad-hoc scripts only.

## Dependencies and blockers

* [AST-489](https://linear.app/astralcareermatch/issue/AST-489/google-cse-integration-and-spike-script-use-company-search-criteria-to) (Done): Google CSE integration.
* [AST-491](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek) (Backlog, blocks per Linear): Unified AI dispatch / provider routing for all inflow AI tasks.
* Existing roster on origin/dev: find_job_page, select_job_page, parse_job_list (AST-461/469 split).
* craft_company_prefilter artifact required before Phase 3.
* Encoded rubric output pattern already used elsewhere in product.

## Open questions

None.

---

## Original brief

One of the most annoying things about this system is managing the company roster.

We need a flow that will grow the candidate's search net

Phase 0: Candidate "company search terms", similar to "title patterns" this is an addendum to candidate content that will be crafted by the AI when the candidate is onboarded.  Simple line-break delimited list of searches to perform for each candidate that should result in companies worth looking at.

AI Task: generate search terms for a candidate given the information we have about them, that will specifically generate strings like "healthcare startups diabetes", etc.

Phase 1: Google search "healthcare startups diabetes" or "company website for workflow automation platform SMB".

AI Task: return ids with <slug> or "ignore" for the search results.

Phase 2: Google search the slugs

AI Task: return the ids that are likely to be the website for the slug

Phase 3: Scrape the website homepage visible text

AI Task: return an encoded rubric on the website homepages

Phase 4: Find job page with score floor

AI Task: locate_job_page from webpage

Phase 5: Parse job page

AI Task: Get parse_instructions for job page.

### Comments

#### chuckles — 2026-06-02T17:32:53.460Z
[check-linear]

**AST-490 — roster inflow closed**

- Your **NEW** filter note: correct — the **8 ingested rows** are vet **`slug`** hits **without** `website`; **`NEW` + empty `company_website`** is expected (CSE hit URL lives in `inflow_discovery_notes`).
- **finish-up** already landed: **`origin/dev` @ `422b9014`**, parent **AST-490** + children **504–508** / **523** → **Done**, **`origin/ftr/AST-490-roster-inflow`** deleted.
- No further Chuckles action on this epic.

— Chuckles

#### chuckles — 2026-06-02T17:31:07.572Z
`origin/dev` @ 422b9014 — merge into `dev-<agent>`: `git fetch origin && git checkout dev-<agent> && git merge origin/dev` (not rebase unless Susan directs)
— Chuckles

#### susan — 2026-06-02T17:29:36.105Z
LOL Oh, hah I was filtering on NEW.  My bad!  Okay, we're ready to wrap this up.

#### chuckles — 2026-06-02T17:26:06.188Z
[check-linear]

**Triage — vet `website` vs what landed in `company`**

Your **8 DB rows** line up with vet **`slug`** rows that had **no `website` field** (e.g. `altek_technology`, `latamed_ai_corp`, `clinically_ai`, …). For those, code path is:

- `ingest_new_companies(..., website=None)` → **`state=NEW`**, **`company_website=""`**
- `inflow_discovery_notes` = **CSE hit URL** from the indexed discovery line (job board / news / listicle), **not** the optional vet `website` homepage

So for those eight, empty `company_website` matches the vet JSON you pasted — not a drop of a returned homepage.

**Rows where vet included `website`** (e.g. `regeneron`, `philips`, …): ingest **does** pass `website` through → `WEBSITE_FOUND` + `company_website` set (`roster.py` → `ingest_new_companies`, `run_inflow_discovery_batch` loop). If you do not see them in `company` at all, they were almost certainly **skipped**, not stored without URL:

1. **Slug already exists** on roster (`get_company` → skip)
2. **Normalized homepage URL already on candidate roster** (`duplicate URL` log in ingest)
3. Invalid `short_name` (must match `^[a-z0-9_]+$`)

~90 vet slugs vs **8 inserts** strongly suggests mass dedupe/skip, not a silent website strip.

**Quick checks on your DB:**

```sql
SELECT short_name, state, company_website FROM company
WHERE candidate_id='somerset' AND short_name IN ('regeneron','philips','ge_healthcare');
```

- **No rows** → skipped (dedupe / pre-existing slug); grep app log for `ingest_new_companies: duplicate URL` or `owned by another candidate`.
- **Row with empty `company_website` but vet had `website`** for that slug → file that slug back here; that would be a real bug (not what the eight rows show).

**Acceptance reminder (AC #6):** when vet **`website` is present and ingest succeeds**, row should be **`WEBSITE_FOUND`** with `company_website` populated — Phase 2 skipped.

No code change this pass (Chuckles triage only). If you have one slug that was **new**, vet had **`website`**, and DB row is **`NEW` with blank `company_website`**, `@chuckles` that slug and we can route a targeted fix.

#### susan — 2026-06-02T17:06:45.079Z
Hmm.  Looks like the website was returned but not stored in the company table:

```
{
  "results": [
    {
      "hit_index": 0,
      "action": "slug",
      "short_name": "altek_technology"
    },
    {
      "hit_index": 8,
      "action": "slug",
      "short_name": "regeneron",
      "website": "https://www.regeneron.com"
    },
    {
      "hit_index": 9,
      "action": "slug",
      "short_name": "optimum_healthcare_it",
      "website": "https://optimumhit.com"
    },
    {
      "hit_index": 15,
      "action": "slug",
      "short_name": "tieto",
      "website": "https://www.tieto.com"
    },
    {
      "hit_index": 17,
      "action": "slug",
      "short_name": "emids",
      "website": "https://www.emids.com"
    },
    {
      "hit_index": 21,
      "action": "slug",
      "short_name": "mastek",
      "website": "https://www.mastek.com"
    },
    {
      "hit_index": 24,
      "action": "slug",
      "short_name": "wolters_kluwer",
      "website": "https://www.wolterskluwer.com"
    },
    {
      "hit_index": 25,
      "action": "slug",
      "short_name": "legitscript",
      "website": "https://www.legitscript.com"
    },
    {
      "hit_index": 29,
      "action": "slug",
      "short_name": "kearney",
      "website": "https://www.kearney.com"
    },
    {
      "hit_index": 30,
      "action": "slug",
      "short_name": "ge_healthcare",
      "website": "https://www.gehealthcare.com"
    },
    {
      "hit_index": 33,
      "action": "slug",
      "short_name": "h1",
      "website": "https://h1.co"
    },
    {
      "hit_index": 34,
      "action": "slug",
      "short_name": "philips",
      "website": "https://www.philips.com"
    },
    {
      "hit_index": 39,
      "action": "slug",
      "short_name": "health_catalyst",
      "website": "https://www.healthcatalyst.com"
    },
    {
      "hit_index": 44,
      "action": "slug",
      "short_name": "ascent_healthcare",
      "website": "https://www.ascenthealthcare.com"
    },
    {
      "hit_index": 45,
      "action": "slug",
      "short_name": "agfa_healthcare",
      "website": "https://www.agfahealthcare.com"
    },
    {
      "hit_index": 47,
      "action": "slug",
      "short_name": "merik_solutions",
      "website": "http://meriksolutions.biz"
    },
    {
      "hit_index": 48,
      "action": "slug",
      "short_name": "johnson_and_johnson",
      "website": "https://www.jnj.com"
    },
    {
      "hit_index": 49,
      "action": "slug",
      "short_name": "conduktor",
      "website": "https://www.conduktor.io"
    },
    {
      "hit_index": 52,
      "action": "slug",
      "short_name": "paubox",
      "website": "https://www.paubox.com"
    },
    {
      "hit_index": 53,
      "action": "slug",
      "short_name": "valant",
      "website": "https://www.valant.io"
    },
    {
      "hit_index": 55,
      "action": "slug",
      "short_name": "enteros",
      "website": "https://www.enteros.com"
    },
    {
      "hit_index": 56,
      "action": "slug",
      "short_name": "humana",
      "website": "https://www.humana.com"
    },
    {
      "hit_index": 57,
      "action": "slug",
      "short_name": "intersystems",
      "website": "https://www.intersystems.com"
    },
    {
      "hit_index": 57,
      "action": "slug",
      "short_name": "59st_ventures",
      "website": "https://59stventures.com"
    },
    {
      "hit_index": 59,
      "action": "slug",
      "short_name": "availity",
      "website": "https://www.availity.com"
    },
    {
      "hit_index": 60,
      "action": "slug",
      "short_name": "latamed_ai_corp"
    },
    {
      "hit_index": 63,
      "action": "slug",
      "short_name": "docuware",
      "website": "https://start.docuware.com"
    },
    {
      "hit_index": 64,
      "action": "slug",
      "short_name": "liferay",
      "website": "https://www.liferay.com"
    },
    {
      "hit_index": 66,
      "action": "slug",
      "short_name": "mev_llc",
      "website": "https://mev.com"
    },
    {
      "hit_index": 67,
      "action": "slug",
      "short_name": "aidoc",
      "website": "https://www.aidoc.com"
    },
    {
      "hit_index": 69,
      "action": "slug",
      "short_name": "perficient",
      "website": "https://www.perficient.com"
    },
    {
      "hit_index": 74,
      "action": "slug",
      "short_name": "dupont",
      "website": "https://www.dupont.com"
    },
    {
      "hit_index": 75,
      "action": "slug",
      "short_name": "riskonnect",
      "website": "https://riskonnect.com"
    },
    {
      "hit_index": 78,
      "action": "slug",
      "short_name": "fpt_software",
      "website": "https://fptsoftware.com"
    },
    {
      "hit_index": 83,
      "action": "slug",
      "short_name": "inetum",
      "website": "https://www.inetum.com"
    },
    {
      "hit_index": 85,
      "action": "slug",
      "short_name": "smart_applications_international",
      "website": "https://smartapplicationsgroup.com"
    },
    {
      "hit_index": 88,
      "action": "slug",
      "short_name": "bitcot",
      "website": "https://www.bitcot.com"
    },
    {
      "hit_index": 89,
      "action": "slug",
      "short_name": "iqvia",
      "website": "https://www.iqvia.com"
    },
    {
      "hit_index": 92,
      "action": "slug",
      "short_name": "maxhub",
      "website": "https://www.maxhub.com"
    },
    {
      "hit_index": 93,
      "action": "slug",
      "short_name": "successive_digital",
      "website": "https://successive.tech"
    },
    {
      "hit_index": 94,
      "action": "slug",
      "short_name": "modirum_platforms",
      "website": "https://modirumplatforms.com"
    },
    {
      "hit_index": 95,
      "action": "slug",
      "short_name": "sirion",
      "website": "https://www.sirion.ai"
    },
    {
      "hit_index": 99,
      "action": "slug",
      "short_name": "pwc",
      "website": "https://www.pwc.com"
    },
    {
      "hit_index": 100,
      "action": "slug",
      "short_name": "clinically_ai"
    },
    {
      "hit_index": 101,
      "action": "slug",
      "short_name": "perceptive_inc",
      "website": "https://www.perceptive.com"
    },
    {
      "hit_index": 103,
      "action": "slug",
      "short_name": "butterfly_network",
      "website": "https://www.butterflynetwork.com"
    },
    {
      "hit_index": 105,
      "action": "slug",
      "short_name": "medcurity",
      "website": "https://medcurity.com"
    },
    {
      "hit_index": 105,
      "action": "slug",
      "short_name": "accountable_hq",
      "website": "https://www.accountablehq.com"
    },
    {
      "hit_index": 108,
      "action": "slug",
      "short_name": "calyx",
      "website": "https://calyx.wd1.myworkdayjobs.com"
    },
    {
      "hit_index": 116,
      "action": "slug",
      "short_name": "memed",
      "website": "https://memed.com.br"
    },
    {
      "hit_index": 117,
      "action": "slug",
      "short_name": "medical_informatics_engineering"
    },
    {
      "hit_index": 119,
      "action": "slug",
      "short_name": "health_samurai",
      "website": "https://www.health-samurai.io"
    },
    {
      "hit_index": 120,
      "action": "slug",
      "short_name": "akoode",
      "website": "https://www.akoode.com"
    },
    {
      "hit_index": 121,
      "action": "slug",
      "short_name": "cognizant",
      "website": "https://www.cognizant.com"
    },
    {
      "hit_index": 122,
      "action": "slug",
      "short_name": "desisle",
      "website": "https://www.desisle.com"
    },
    {
      "hit_index": 124,
      "action": "slug",
      "short_name": "cordys_analytics"
    },
    {
      "hit_index": 126,
      "action": "slug",
      "short_name": "intellivon",
      "website": "https://intellivon.com"
    },
    {
      "hit_index": 127,
      "action": "slug",
      "short_name": "quickblox",
      "website": "https://quickblox.com"
    },
    {
      "hit_index": 128,
      "action": "slug",
      "short_name": "ensodata",
      "website": "https://www.ensodata.com"
    },
    {
      "hit_index": 129,
      "action": "slug",
      "short_name": "qualhon_informatics",
      "website": "https://qualhon.com"
    },
    {
      "hit_index": 131,
      "action": "slug",
      "short_name": "kellton",
      "website": "https://www.kellton.com"
    },
    {
      "hit_index": 136,
      "action": "slug",
      "short_name": "saga_it",
      "website": "https://saga-it.com"
    },
    {
      "hit_index": 137,
      "action": "slug",
      "short_name": "foodsmart",
      "website": "https://www.foodsmart.com"
    },
    {
      "hit_index": 139,
      "action": "slug",
      "short_name": "illumina",
      "website": "https://www.illumina.com"
    },
    {
      "hit_index": 141,
      "action": "slug",
      "short_name": "castor",
      "website": "https://www.castoredc.com"
    },
    {
      "hit_index": 141,
      "action": "slug",
      "short_name": "viedoc",
      "website": "https://www.viedoc.com"
    },
    {
      "hit_index": 142,
      "action": "slug",
      "short_name": "appaxis",
      "website": "https://appaxis.com"
    },
    {
      "hit_index": 143,
      "action": "slug",
      "short_name": "omniscience",
      "website": "https://www.omniscience.bio"
    },
    {
      "hit_index": 144,
      "action": "slug",
      "short_name": "advenno",
      "website": "https://advenno.com"
    },
    {
      "hit_index": 146,
      "action": "slug",
      "short_name": "vatsa_solutions",
      "website": "https://vatsainc.com"
    },
    {
      "hit_index": 147,
      "action": "slug",
      "short_name": "vim",
      "website": "https://getvim.com"
    },
    {
      "hit_index": 148,
      "action": "slug",
      "short_name": "dassault_systemes",
      "website": "https://www.3ds.com"
    },
    {
      "hit_index": 149,
      "action": "slug",
      "short_name": "cliniciancore",
      "website": "https://cliniciancore.com"
    },
    {
      "hit_index": 154,
      "action": "slug",
      "short_name": "summus",
      "website": "https://www.summusglobal.com"
    },
    {
      "hit_index": 156,
      "action": "slug",
      "short_name": "teton",
      "website": "https://teton.ai"
    },
    {
      "hit_index": 157,
      "action": "slug",
      "short_name": "topcon_healthcare",
      "website": "https://topconhealthcare.eu"
    },
    {
      "hit_index": 158,
      "action": "slug",
      "short_name": "docusign",
      "website": "https://www.docusign.com"
    },
    {
      "hit_index": 159,
      "action": "slug",
      "short_name": "clinicon"
    },
    {
      "hit_index": 161,
      "action": "slug",
      "short_name": "wellsky",
      "website": "https://wellsky.com"
    },
    {
      "hit_index": 162,
      "action": "slug",
      "short_name": "wyn_health",
      "website": "https://www.wynsync.tech"
    },
    {
      "hit_index": 163,
      "action": "slug",
      "short_name": "digital_prizm",
      "website": "https://digitalprizm.net"
    },
    {
      "hit_index": 165,
      "action": "slug",
      "short_name": "central_data_storage",
      "website": "https://centraldatastorage.com"
    },
    {
      "hit_index": 168,
      "action": "slug",
      "short_name": "medi_assist_healthcare_services"
    },
    {
      "hit_index": 169,
      "action": "slug",
      "short_name": "axcess_io",
      "website": "https://axcess.io"
    },
    {
      "hit_index": 172,
      "action": "slug",
      "short_name": "graph_ai"
    },
    {
      "hit_index": 173,
      "action": "slug",
      "short_name": "narrativa",
      "website": "https://www.narrativa.com"
    },
    {
      "hit_index": 174,
      "action": "slug",
      "short_name": "triaxo",
      "website": "https://triaxo.com"
    },
    {
      "hit_index": 175,
      "action": "slug",
      "short_name": "doximity",
      "website": "https://www.doximity.com"
    },
    {
      "hit_index": 176,
      "action": "slug",
      "short_name": "compliancequest",
      "website": "https://www.compliancequest.com"
    },
    {
      "hit_index": 182,
      "action": "slug",
      "short_name": "ahex_technologies",
      "website": "https://ahex.co"
    },
    {
      "hit_index": 183,
      "action": "slug",
      "short_name": "cloudroots",
      "website": "https://cloudroots.co.in"
    },
    {
      "hit_index": 184,
      "action": "slug",
      "short_name": "abbott",
      "website": "https://www.abbott.com"
    },
    {
      "hit_index": 186,
      "action": "slug",
      "short_name": "medable",
      "website": "https://www.medable.com"
    },
    {
      "hit_index": 189,
      "action": "slug",
      "short_name": "neotas",
      "website": "https://www.neotas.com"
    },
    {
      "hit_index": 190,
      "action": "slug",
      "short_name": "digital_dividend",
      "website": "https://digital-dividend.com"
    }
  ]
}
```

Database output:

```
[
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://bebee.com/us/jobs/vice-president-of-product-management-altek-technology-company--theirstack-692704392\"}",
    "company_name": "altek_technology",
    "company_website": "",
    "created_at": "2026-06-02 16:53:00",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "altek_technology",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:00",
    "updated_at": "2026-06-02 16:53:00"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://www.eqs-news.com/news/corporate/latamed-ai-corp-to-attend-medica-2026-in-germany-as-company-advances-innovative-healthcare-technology-strategy/6db72178-3829-4cf5-9c3f-e11d1c368cbf\"}",
    "company_name": "latamed_ai_corp",
    "company_website": "",
    "created_at": "2026-06-02 16:53:00",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "latamed_ai_corp",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:00",
    "updated_at": "2026-06-02 16:53:00"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://jobs.ashbyhq.com/ClinicallyAI/bf9e329a-8eb3-4ef4-80a3-9eba8d3a26dd\"}",
    "company_name": "clinically_ai",
    "company_website": "",
    "created_at": "2026-06-02 16:53:01",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "clinically_ai",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:01",
    "updated_at": "2026-06-02 16:53:01"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://www.ziprecruiter.com/c/Medical-Informatics-Engineering-Enterprise-Health/Job/Senior-Product-Manager-Enterprise-Health-(Clinical-Domain)/-in-Fort-Wayne,IN?jid=54b14541883ef186\"}",
    "company_name": "medical_informatics_engineering",
    "company_website": "",
    "created_at": "2026-06-02 16:53:01",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "medical_informatics_engineering",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:01",
    "updated_at": "2026-06-02 16:53:01"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://apply.workable.com/cordys-analytics/j/9B0E54458D\"}",
    "company_name": "cordys_analytics",
    "company_website": "",
    "created_at": "2026-06-02 16:53:01",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "cordys_analytics",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:01",
    "updated_at": "2026-06-02 16:53:01"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://www.startuphub.ai/startups/clinicon\"}",
    "company_name": "clinicon",
    "company_website": "",
    "created_at": "2026-06-02 16:53:02",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "clinicon",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:02",
    "updated_at": "2026-06-02 16:53:02"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://zennivesh.substack.com/p/medi-assist-healthcare-services-a\"}",
    "company_name": "medi_assist_healthcare_services",
    "company_website": "",
    "created_at": "2026-06-02 16:53:02",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "medi_assist_healthcare_services",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:02",
    "updated_at": "2026-06-02 16:53:02"
  },
  {
    "agent_responses": "[]",
    "agent_responses_legacy": null,
    "batch_created_at": null,
    "batch_id": null,
    "candidate_id": "somerset",
    "company_data": "{\"inflow_discovery_notes\": \"https://www.bvp.com/atlas/graph-ai-a-service-firm-turned-ai-native-solution-for-pharma-and-life-sciences\"}",
    "company_name": "graph_ai",
    "company_website": "",
    "created_at": "2026-06-02 16:53:02",
    "job_site": null,
    "last_scan_at": null,
    "short_name": "graph_ai",
    "state": "NEW",
    "state_history": "[]",
    "state_updated_at": "2026-06-02 16:53:02",
    "updated_at": "2026-06-02 16:53:02"
  }
]
```

#### chuckles — 2026-06-02T16:39:17.008Z
[check-linear]

**No — keep `entity_type: "candidate"`.** Do not change it to `company` or anything else. That is the designed shape for **`inflow_discovery`**.

**Why it says "candidate":**
- Phase 1 is **one discovery batch per active candidate**, not one row per company. Dispatcher claim path (`dispatcher.py` → `entity_type == "candidate"`) passes the active candidate context as the sole entity — it does not scan the `candidate` table for multiple rows.
- **`trigger_state: LIVE_PROMPTS`** means the **candidate** must be in state `LIVE_PROMPTS` (not a company state).

**What "Available" actually counts (AST-525 on current `dev`):**
- Admin **Avail** = `count_eligible_for_dispatch_task` → for this task, **`count_candidate_inflow_discovery_eligible`**.
- Returns **0 or 1** (is this candidate eligible right now?), **not** a count of companies.
- Eligibility requires:
  1. Candidate `state == LIVE_PROMPTS`, and
  2. ≥1 **stale** row in the **`company_search_terms`** table (`last_scan_at` NULL or older than **`INFLOW_CONFIG.discovery.scan_interval_hours`** = **168h**).
- **`freq_hrs` and `dispatch_task.last_run_at` do not drive Avail** after AST-525 — your `last_run_at: 2026-06-02 16:23:25` only proves dispatch **ran**; Avail can still be **1** if stale terms remain.

**After your successful (non-crash) run, check:**
1. **Artifacts → Company search terms** — terms exist and synced to the table (AST-523).
2. **Roster → Companies** — any new **NEW** / **WEBSITE_FOUND** rows from vet **`slug`** actions (all **`ignore`** → no new companies, but terms should still have fresh `last_scan_at` if CSE succeeded).
3. If **Avail stays 1** immediately after run: open logs for CSE failures per term (failed CSE **does not** bump `last_scan_at`, so terms stay stale). Or you still have multiple terms and only some completed.

**Config row you pasted is correct as-is** — only flip **`auto_mode`** when you want the scheduler to pick it up without manual Run.

No code change this pass.

#### susan — 2026-06-02T16:24:49.240Z
Okay, well, it didn't crash!  That's great!  but, unfortunately, it still is looking at candidate table for available.  Do I need to change the entity type for the dispatch task?

```
[
  {
    "auto_mode": 0,
    "batch_call_mode": 0,
    "batch_id": null,
    "batch_size": 1,
    "candidate_id": "somerset",
    "debug": 0,
    "entity_type": "candidate",
    "freq_hrs": 168,
    "id": 5373,
    "last_run_at": "2026-06-02 16:23:25",
    "max_runs": 1,
    "min_count": 1,
    "score_floor": null,
    "skip_cache": 0,
    "sort_by": "updated_at",
    "task_key": "inflow_discovery",
    "trigger_state": "LIVE_PROMPTS",
    "updated_at": "2026-06-02 16:23:25"
  }
]
```

#### chuckles — 2026-06-02T16:15:35.661Z
[check-linear]

**Agent / brain tier:** Use **Medium** brain on an **Estelle-class** agent (same roster lane as **`find_company_website`** in `TASK_CONFIG`). This is relevance triage over a batch of CSE snippets — not rubric scoring (**Big**) and not a single-field extract. **Little** is OK if you want cheaper bulk runs once prompts are stable; start **Medium** for first UAT.

**Admin setup:** Task Prompts → **`vet_inflow_discovery`** → pick agent → assign **Agent** on the row (required — empty `agent_id` is what crashed dispatch).

---

### Draft prompts (paste into Manage Tasks)

**System** (or leave `{$SELECTED_AGENT}` if Estelle’s persona lives on the agent record):

You vet Google Custom Search hits for roster inflow. The candidate’s discovery queries are:

{$COMPANY_SEARCH_TERMS}

Only propose employers worth adding to this candidate’s watch list. Ignore directories, news, job boards, listicles, Wikipedia, social profiles, and pages that are not a specific company.

**User:**

Review every discovery hit in **CONTENT** below.

Each hit line is: `NNN|title|url|snippet` where **NNN** is the hit index (000, 001, …).

For each hit you care about, emit one result with:
- **`hit_index`**: integer matching the line prefix (e.g. 0 for `000|…`)
- **`action`**: **`slug`** to add the company, or **`ignore`** to skip
- **`short_name`**: required when `action` is **`slug`** — lowercase slug, **`[a-z0-9_]`** only (e.g. `acme_health`, `stripe`). This becomes the company primary key.
- **`website`**: optional when `action` is **`slug`** — canonical homepage URL if obvious from title/url/snippet. If omitted, the company is created as **NEW** and Phase 2 resolves the site later.

Rules:
- One result row per hit you **`slug`**; you may omit hits you **`ignore`** entirely or list them with `"action": "ignore"`.
- Do not **`slug`** duplicate employers under different names unless they are truly distinct companies.
- Prefer the official company site in **`website`** when the search result URL is already the homepage.

Respond with JSON only (no markdown fence):

```json
{
  "results": [
    {"hit_index": 0, "action": "slug", "short_name": "example_co", "website": "https://example.com"},
    {"hit_index": 3, "action": "ignore"}
  ]
}
```

**No-cache / live block:** runtime supplies the hit list automatically (`Discovery hits (index|title|url|snippet)` + lines). You do not author that in Admin.

---

**Code contract** (`src/core/roster.py` → `run_inflow_discovery_batch`): only **`action`: `"slug"`** (case-insensitive) ingests; **`ignore`** skips; anything else is logged and skipped. **`short_name`** must match `^[a-z0-9_]+$`. URL dedupe is downstream — you do not need to check the existing roster.

After saving prompts + agent, re-run **`inflow_discovery`**.

#### susan — 2026-06-02T16:14:40.719Z
Oh for Pete's sake!  LOL.  It's been too long since I've looked at this funnel.  Does the vet_inflow_discovery need a Big/Medium/Little brain agent?  Also, please draft a task prompt to the agent so they know what to expect, what to do, and what to return, according to the code in place.  Text in the comments here is fine.

#### chuckles — 2026-06-02T16:08:57.438Z
[check-linear]

**Root cause:** `sync_agent_tasks` on startup inserted a blank **`agent_task`** row for **`vet_inflow_discovery`** (empty **`agent_id`**). CSE ran; vet step called `do_task` → `_resolve_task_prompts` hard-fails when **`agent_id`** is unset. **Not a dispatcher/product bug** — same contract as **`craft_company_search_terms`** (AST-504 Stage 5 / Radia audit discuss item).

**Fix (Admin → Task Prompts):**

1. Open **`vet_inflow_discovery`** — assign an **Agent** (e.g. same agent you use for roster vetting tasks).
2. Add prompts. Response schema per **`TASK_CONFIG`**: `{ "results": [ { "hit_index": int, "action": "accept"|"ignore", "short_name"?: str, "website"?: str } ] }` — one entry per CSE hit index.
3. While there, confirm **`craft_company_search_terms`** also has Agent + prompts (Phase 0 Generate) if not already done.
4. Retry **`inflow_discovery`** after save.

**Also before Phase 4 smoke (per UAT steps):** Admin → Scheduled Actions — **`find_job_page`** row with **`trigger_state=PREFILTER_PASSED`** + **`score_floor`**.

No code change this pass; inbox item is Admin configuration on your local DB.

#### susan — 2026-06-01T00:48:01.903Z
```
[2026-06-01 00:22:24] INFO dispatch.scheduler: Dispatching inflow_discovery — 1 available, batch inflow_discovery-283e7ef5-6d02-4fa4-9884-5fceede3e98b
[2026-06-01 00:22:24] ERROR dispatch.scheduler: [inflow_discovery/inflow_discovery-283e7ef5-6d02-4fa4-9884-5fceede3e98b] crashed
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 415, in _dispatch_one
    await _tracked()
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 405, in _tracked
    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 491, in _run_dispatch_loop
    summary = await _run_task(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 334, in _run_task
    summary = await _run_unified(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 291, in _run_unified
    results = await _warm_then_gather(_one, entities, _SUMMARY_ZERO)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 54, in _warm_then_gather
    first = await one_fn(entities[0])
            ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 287, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/consult.py", line 1194, in run_consult_task
    return await roster.run_inflow_discovery_batch(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/roster.py", line 339, in run_inflow_discovery_batch
    api_result = await do_task(
                 ^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 1027, in do_task
    agent_row, agent_task_row = _resolve_task_prompts(task_key)
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 320, in _resolve_task_prompts
    raise ValueError(f"agent_task '{task_key}' has no agent_id assigned. Configure via Manage Tasks.")
ValueError: agent_task 'vet_inflow_discovery' has no agent_id assigned. Configure via Manage Tasks.
```

@chuckles

#### chuckles — 2026-05-28T18:59:15.475Z
## Manual test steps

**Prerequisites:** Local `dev` merged @ `af9d91f1` (ftr `a2a07783`). Restart app. Active candidate with profile + **`craft_company_prefilter`** artifact. Admin → Task Prompts: add **`craft_company_search_terms`** and **`vet_inflow_discovery`** rows before Phase 0 Generate / Phase 1 vet.

### Phase 0 — AST-504
1. Artifacts → **Company search terms**: Generate (or Regenerate), edit lines, autosave; confirm blank save rejected.
2. Confirm no **`inflow_discovery`** dispatch runs from Phase 0 alone (on-demand craft only).

### Phase 1 — AST-505
3. Ensure search-terms artifact non-empty; Admin → Scheduled Actions: **`inflow_discovery`** eligible for candidate (weekly / 168h).
4. Run dispatch (or consult path) once; confirm CSE hits vetted; accepted hits create **NEW** (or **WEBSITE_FOUND** when URL supplied).
5. Re-run with duplicate URL on roster — confirm dedupe skip.

### Phase 2 — AST-506
6. **NEW** company without URL → **`inflow_resolve_website`** → **WEBSITE_FOUND** or **NO_WEBSITE**.
7. **NEW** with URL from Phase 1 — Phase 2 should not re-run.

### Phase 3 — AST-507
8. **WEBSITE_FOUND** (inflow history) → prefilter → **PREFILTER_PASSED** + score, or **PREFILTER_FAILED** on dealbreaker F.
9. Manual **IMPORTED** path still **TO_WATCH** / **IGNORE** (legacy), not PREFILTER_*.

### Phases 4–5 — AST-508
10. Admin: **`find_job_page`** dispatch row with **`trigger_state=PREFILTER_PASSED`** and **`score_floor`** set.
11. Below-floor **PREFILTER_PASSED** companies stay unclaimed; at/above floor → locate → parse → **WATCH** terminal states.

### Boundaries
12. **IMPORTED** manual import unchanged. No inflow review-queue UI in v1.

`origin/ftr/AST-490-roster-inflow` @ `a2a07783` · local `dev` merged (§8). Sub branches deleted.

Radia audit: fix-now **0**; discuss items in audit comment above.

— Chuckles

#### chuckles — 2026-05-28T18:59:11.839Z
## Radia UAT reality-check — `origin/ftr/AST-490-roster-inflow` @ `a2a07783`

**Scope:** Parent definition + child plans AST-504–508 vs composite on ftr (504–508 rolled up; subs deleted).

### Parent acceptance criteria
| # | Verdict | Notes |
|---|---------|-------|
| 1–2 | PASS | Phase 0 artifact + craft task; on-demand only (no dispatch seed) |
| 3–6 | PASS | Phase 1 CSE/vet/ingest/NEW/URL shortcut — **Admin `vet_inflow_discovery` row required** for live vet |
| 7 | PASS | Phase 2 resolve for NEW without URL |
| 8 | PASS | Encoded prefilter → PREFILTER_PASSED/FAILED + score |
| 9–10 | PASS | PREFILTER_PASSED locate via `score_floor`; existing parse chain |
| 11 | PASS | IMPORTED path unchanged |
| 12 | PASS | All phases on dispatch_tasks / state machine |

### Child stage checklist
**AST-504–508:** PASS — product + Betty manifests green on publish refs; resolve-astral clean.

### Issues → sub-issues
| Sev | Topic | Action |
|-----|-------|--------|
| discuss | Admin Task Prompts | Seed `craft_company_search_terms`, `vet_inflow_discovery` before Generate/vet in UAT |
| discuss | Phase 4 dispatch row | Create `find_job_page` row with `trigger_state=PREFILTER_PASSED` + `score_floor` (no new seed key per AST-508) |
| discuss | Live CSE | `GOOGLE_CSE_*` env for Phases 1–2 smoke |
| advisory | AST-491 on dev | DeepSeek routing already on `origin/dev`; inflow AI tasks use existing agent path |

**Counts:** fix-now **0** · discuss **3** · advisory **1**

— Radia (via Chuckles orchestration)

#### chuckles — 2026-05-27T23:39:59.853Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-490 (parent) | ftr/AST-490-roster-inflow |
| AST-504 | sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task |
| AST-505 | sub/AST-490/AST-505-discovery-search-vet-slugs-and-ingest-new-companies |
| AST-506 | sub/AST-490/AST-506-website-resolution-search-and-selection |
| AST-507 | sub/AST-490/AST-507-encoded-prefilter-and-prefilter-states |
| AST-508 | sub/AST-490/AST-508-inflow-locate-and-parse-from-prefilter-passed |

Overlap ack: AST-491 merged to `origin/dev` (config, agent, database). Merge `origin/dev` into each sub before publish.

— Chuckles

#### chuckles — 2026-05-26T22:36:29.287Z
@susan Folded your inline answers into the definition. Two items still ambiguous before dispatch:

1. **Weekly dupes:** Your Q4 answer cut off at "the date filter…" — when Phase 1 resurfaces a company already on the candidate roster, skip entirely, refresh metadata only, or re-enter **NEW**?
2. **IMPORTED vs NEW:** Does manual import keep **IMPORTED**, or does all ingest converge on **NEW**?

— Chuckles

#### chuckles — 2026-05-26T22:09:38.317Z
@susan Updated definition for **Phase 0** (company search terms — AI at onboarding, line-break list parallel to title patterns). Removed the old "criteria authoring out of v1" boundary; Phase 1 now reads from that candidate list.

Revised open questions:

1. **Search terms storage:** profile field parallel to title_patterns vs candidate artifact?
2. **Phase 0 timing:** onboarding once, or re-runnable on demand / schedule?
3. **Site/domain restrictions:** AST-488 filters per candidate, per term, or global default?
4. **Slug rules:** AI-only, normalized from name, collision policy?
5. **Initial company state:** IMPORTED, WEBSITE_FOUND, or other after Phase 2?
6. **Score floor (Phase 4):** prefilter pass threshold, or separate gate?
7. **Shipping slices:** one epic (Phases 0–5) or 0–2 first?
8. **Cadence and triggers:** admin dispatch, scheduled, or lifecycle-gated?

— Chuckles

#### chuckles — 2026-05-26T21:54:43.044Z
@susan Open questions on **AST-490** — need your call before dispatch:

1. **Discovery query source:** Where do Phase 1 query strings come from in v1 — hardcoded/config exemplars, admin-entered dispatch parameters, a new candidate artifact, or Estelle-generated company_search_criteria (AST-488 follow-on)?
2. **Site/domain restrictions:** Should discovery searches use the AST-488 domain filters (LinkedIn company, Crunchbase, Builtin, Wellfound, Indeed) per query, per candidate, or a global default?
3. **Slug rules:** Who assigns the slug format — AI-only, normalized from company name, collision policy when slug already exists on the roster, max length/charset?
4. **Initial company state:** After website resolution (Phase 2), do new rows enter at IMPORTED, WEBSITE_FOUND, or another state?
5. **Score floor (Phase 4):** "Score floor" before job-page locate — prefilter rubric pass threshold (today's binary prefilter grading), or a separate gate?
6. **Shipping slices:** One epic with child tickets per phase, or ship discovery+ingest (Phases 1–2) before prefilter/locate/parse (Phases 3–5)?
7. **Cadence and triggers:** On-demand admin dispatch only, scheduled interval per candidate, or tied to candidate lifecycle (e.g. after CONTEXT_READY)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
