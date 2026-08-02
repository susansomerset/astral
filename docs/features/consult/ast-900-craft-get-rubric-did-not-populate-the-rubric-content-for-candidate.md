# AST-900 — craft get rubric did not populate the rubric content for candidate

<!-- linear-archive: AST-900 archived 2026-08-02 -->

## Linear archive (AST-900)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When a candidate's rubric is generated from the Artifacts UI, a successful backend run must leave the user with the generated criteria — either on screen for review, or recoverable if the wait was abandoned. On Jul 16 a `craft_get_rubric` generation for candidate `karfo` completed successfully (LLM ~178.5s, ledger COMPLETED, full criteria payload produced) yet the candidate's Get Job Criteria artifact was never populated. This epic finds where that successful result was dropped and closes the gap so a backend COMPLETED can no longer leave the user with nothing and no error.

## Functional scope

* Trace the `karfo` run end to end and document where the successful criteria payload was lost (browser delivery, review UI, Save path, or candidate artifact persist).
* A successful rubric generation launched from the artifact editor ends with the generated criteria visible for review in that editor, including long-running generations (multi-minute LLM waits).
* Keep the existing review-then-Save gate: Generate does not silently overwrite the stored candidate artifact until the user Saves.
* When a generation completes on the backend but the browser never receives or never keeps the result (navigate away, dropped connection, request killed mid-wait), the outcome is observable: the user sees an error, or can recover the completed generation when they return to the page. Backend COMPLETED with nothing user-visible is a defect.
* The fix applies to every rubric artifact page that uses this generate path (company prefilter, job list, job description, get, do, like) — not a get-only patch.
* Backend debug traceability on the generate path: when debug is on, the log shows what the generation produced and what was recorded, per the AST-538 debug contract (index headers plus working detail; long payloads truncated).

## Boundaries

* No changes to rubric prompts, response schema, criteria content, or grading semantics — the generated payload itself was correct.
* No auto-Save that overwrites the candidate artifact without user confirmation after Generate.
* No changes to the dispatcher batch consult paths (`grade_get` and siblings) — this is the candidate UI generate path only.
* Must not break base resume generation, which shares the same generate machinery but persists server-side.

## Acceptance criteria

* The root cause of the `karfo` drop is documented on this ticket or a child ticket.
* Generating Get Job Criteria for a candidate with an empty rubric ends with the criteria visible in the editor, and after Save they are present in the candidate's stored artifact.
* A generation that completes on the backend can no longer vanish without a user-visible trace: the editor shows the result or an error, or the completed result is recoverable when the user returns to the page.
* All rubric artifact pages exhibit the same corrected behavior.
* Base resume generation still parses and saves as before.

## Dependencies and blockers

None. ([AST-899](https://linear.app/astralcareermatch/issue/AST-899/something-is-wrong-with-the-qualify-job-listings-job), also in Discussion, may share LLM-provider behavior but does not block this work.)

## Open questions

None.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-900](https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate) (parent) | ftr/AST-900-craft-get-rubric-populate |
| [AST-901](https://linear.app/astralcareermatch/issue/AST-901/trace-and-harden-craft-rubric-generate-delivery-craft-get-rubric-did) | sub/AST-900/AST-901-trace-harden-craft-rubric-generate |
| [AST-902](https://linear.app/astralcareermatch/issue/AST-902/artifact-editor-surfaces-and-recovers-generated-rubric-criteria-craft) | sub/AST-900/AST-902-artifact-editor-recover-rubric |
| [AST-903](https://linear.app/astralcareermatch/issue/AST-903/uat-craft-get-rubric-json-parse-unterminated-string) | sub/AST-900/AST-903-uat-craft-get-json-parse |
| [AST-904](https://linear.app/astralcareermatch/issue/AST-904/uat-get-criteria-save-failed-and-content-lost-on-return) | sub/AST-900/AST-904-uat-get-criteria-save-lost |
| [AST-905](https://linear.app/astralcareermatch/issue/AST-905/uat-recover-rubric-only-when-criteria-empty-do-not-overwrite-edits) | sub/AST-900/AST-905-uat-recover-only-when-empty |
| [AST-906](https://linear.app/astralcareermatch/issue/AST-906/uat-get-rubric-save-still-failing-dolike-ok) | sub/AST-900/AST-906-uat-get-rubric-save-still-failing |

**Epic worktree:** `astral-AST-900/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 6ea03e76-27a9-4bf6-b94e-e4fcffbcc301 |
| Katherine | engineer | 23dfeac4-a2f3-41ba-81c8-092e678b8254 |
| Betty | qa | b410ff89-0269-4be0-a116-9f032213251a |
| Radia | review | 54dfd985-ae83-41b3-a3b5-0166317bcd8d |

---

## Original brief

```
[2026-07-16 19:07:31] INFO src.core.candidate: UI generate started task_key='craft_get_rubric' ledger_task_key=user-craft_get_rubric batch_id=user-craft_get_rubric-364310ef-168a-418c-aadc-9151f89ba647 candidate_id=karfo
[2026-07-16 19:07:31] INFO src.core.agent: run_next chain entry: task=craft_get_rubric batch_id=user-craft_get_rubric-364310ef-168a-418c-aadc-9151f89ba647
[2026-07-16 19:07:31] INFO src.external.deepseek: LLM deepseek task=craft_get_rubric 178.5s stop=end_turn tokens in=5159 out=12437
[2026-07-16 19:07:31] INFO src.core.agent: do_task(craft_get_rubric) completed successfully batch_id=user-craft_get_rubric-364310ef-168a-418c-aadc-9151f89ba647 index=karfo
[2026-07-16 19:07:31] INFO src.core.candidate: UI generate completed task_key='craft_get_rubric' batch_id=user-craft_get_rubric-364310ef-168a-418c-aadc-9151f89ba647 status=COMPLETED cost=0.013064355
```

Respose:

```
{
  "criteria": [
    {
      "label": "Title Alignment",
      "code": "TA",
      "content": "A == JD target title is a direct match or obvious peer to one of Justin's recent titles (e.g., \"Senior Product Manager,\" \"Manager, Product Management,\" \"Senior Program Manager,\" \"Product Manager - Technical,\" or \"Expansion Principal\"). Recruiter sees title match instantly.\nB == JD title is in the same family but not an exact match (e.g., JD says \"Technical Program Manager\" and Justin has \"Senior Program Manager\" or \"Product Manager — Technical\"; minor interpretation required). Or JD title is \"Director of Product\" and Justin's titles are manager-level but with demonstrated scope that suggests director-level readiness; recruiter gives benefit of the doubt.\nC == JD title is adjacent but requires the recruiter to read beyond the title line to see the connection (e.g., JD says \"Strategy & Operations Manager\" and Justin's recent titles are product management; the skills align but the title doesn't signal the function). Or JD is for a VP-level role and Justin's titles are at the senior manager/principal level; a hurried recruiter might miss the jump.\nD == Title mismatch is significant — e.g., JD is for an engineering manager, and Justin's titles are non-engineering (product/program) with no engineering management title in recent roles. Only a cover letter or resume rewrite reframing his technical leadership could salvage the screen.\nF == JD title represents a fundamentally different professional identity (e.g., \"Software Engineer,\" \"Chief Medical Officer,\" \"Head of Sales\") that Justin's resume cannot credibly bridge. No title in his career aligns.\nX == JD does not provide a clear target title or level; cannot evaluate.",
      "importance": 9
    },
    {
      "label": "Years of Experience Match",
      "code": "YE",
      "content": "A == JD's required years of experience fall within Justin's total (15+ years) ±1 year, and there is no \"overqualified\" penalty — e.g., JD asks for 12+ years, Justin has 15, a perfect match.\nB == JD requires slightly more or less than Justin's total, but not enough to raise flags — e.g., JD asks for 10+ years (Justin exceeds by 5 years) or 15+ years exact.\nC == JD asks for significantly fewer years (e.g., 5-7 years) making Justin appear potentially overqualified; or JD demands 20+ years and Justin has only 15 — recruiter may pause but continue reading.\nD == JD explicitly targets early-career (2-4 years) and Justin's 15+ years screams \"overqualified\" or \"priced out\"; the resume would likely be dropped without a compelling cover letter explaining the career shift. Or JD strictly requires 20+ years and Justin's experience falls well short, but he might still argue high-impact roles.\nF == JD requires a specific length of experience that Justin does not have and cannot claim, such as \"10+ years of licensed medical practice\" — a structural impossibility. (Justin's total years are usually sufficient.)\nX == JD does not specify years of experience.",
      "importance": 8
    },
    {
      "label": "Domain/Sector Relevance",
      "code": "DS",
      "content": "A == JD's primary domain (e.g., e-commerce logistics, smart home IoT, developer platforms, fintech, mobility/transportation) is one where Justin has recent, named, and demonstrably relevant experience at a top-tier company (Amazon Logistics, Alexa Smart Home, Via, Goldman Sachs fintech). Recruiter sees immediate industry credibility.\nB == JD's domain is adjacent to one of Justin's core areas (e.g., supply chain technology, SaaS platforms, data analytics, marketplaces, payments) — Justin's experience is transferable but not an exact hit. Recruiter connects the dots quickly.\nC == JD's domain is not in Justin's primary wheelhouse but there is a plausible overlap (e.g., healthcare tech, climate tech) where his analytics, ML, or operations experience might apply. Recruiter might give him a shot if the rest of the application is strong.\nD == JD targets a narrow domain that Justin's resume does not address at all (e.g., medical devices, semiconductor manufacturing, oil & gas). There is no surface-level signal, and only a strong cover letter or resume rework highlighting transferable skills might rescue the application.\nF == JD requires deep, non-transferable domain expertise (e.g., licensed pharmacist, nuclear engineering, specific government clearance) that Justin has no basis for and cannot acquire quickly. Structural mismatch.\nX == JD does not provide enough sector information to evaluate.",
      "importance": 8
    },
    {
      "label": "Functional Skill Match",
      "code": "FS",
      "content": "A == The JD's listed core responsibilities map directly to Justin's demonstrated strengths: product management, data analytics/ML, cross-functional leadership, program management, financial analysis, or P&L ownership. Multiple recent roles showcase these skills at the required level.\nB == The JD emphasizes a subset of Justin's skills and he has relevant experience, though not always as the primary function; e.g., JD wants a go-to-market strategist, and Justin's product roles included GTM but it's not his title.\nC == The JD's primary skill set is present but buried or secondary in Justin's resume; e.g., JD is a pure data science role, and Justin has \"Product & Analytics\" background but is not a full-time IC data scientist. Recruiter might consider if the resume is framed correctly.\nD == The JD requires a skill or function that Justin's resume either lacks or fails to surface (e.g., hardcore software development, UI/UX design, direct sales). The experience might exist in past but is not evident; a cover letter or resume reframe is needed to highlight it.\nF == The JD's core function is entirely absent from Justin's career (e.g., bench scientist, creative director, aircraft pilot). No amount of rewriting can create that experience.\nX == JD does not include a clear responsibilities section.",
      "importance": 9
    },
    {
      "label": "Technical Depth Positioning",
      "code": "TD",
      "content": "A == JD seeks a Technical Product Manager or ML/AI product role where current hands-on coding is not required but strong technical acumen is; Justin's resume clearly signals his ML systems ownership, operations research/engineering background, and \"technical\" designation in his title. Perfect positioning.\nB == JD is a standard product manager role where technical depth is a plus but not mandatory; Justin's engineering degree and technical PM title provide enough credibility.\nC == JD is for a Senior Software Engineer or Engineering Manager requiring recent hands-on coding; Justin's resume lacks evidence of recent software development (no languages listed, roles are more management/analytics). Recruiter may be skeptical but could be swayed if the JD values leadership over coding.\nD == JD is for a deeply technical IC role (e.g., Staff ML Engineer) where the resume cannot demonstrate the required hands-on technical skills; the \"Manager\" and \"Founder\" labels may actively hurt. Only a rewritten resume emphasizing technical contributions could move the needle.\nF == JD requires a specific technical certification or hands-on expertise that Justin does not and cannot credibly have (e.g., Python expert with 5+ years of production code). Structural gap.\nX == JD does not give enough technical requirements to assess.",
      "importance": 7
    },
    {
      "label": "ATS Keyword Coverage",
      "code": "AK",
      "content": "A == The JD's key terms (e.g., \"product roadmap,\" \"agile,\" \"SQL,\" \"stakeholder management,\" \"ML,\" \"P&L\") appear prominently and frequently in Justin's resume exactly as written or with obvious synonyms. An ATS would rank the resume very highly.\nB == Most JD keywords are present, but some specific jargon (e.g., \"Scrum,\" \"JIRA,\" \"OKRs\") is missing or paraphrased; still passes ATS screening with a strong score.\nC == About half the expected keywords are missing or buried; the ATS might borderline the resume, requiring recruiter manual review to salvage.\nD == The JD contains very specific terms (e.g., \"HIPAA compliance,\" \"Salesforce administration,\" \"CNC machining\") that do not appear in Justin's resume at all, even though he might have some exposure. ATS would reject outright unless a human intervenes; resume must be tailored.\nF == The JD uses a completely alien lexicon (e.g., \"patient care protocols,\" \"civil litigation procedures\") that Justin's professional history cannot match. No resume tailoring can fix this.\nX == JD does not provide enough language to evaluate ATS fit.",
      "importance": 8
    },
    {
      "label": "Recency of Relevant Experience",
      "code": "RE",
      "content": "A == The most relevant experience for the JD is within Justin's last 2 years (2024-2026): e.g., JD asks for developer ecosystem product management and he did exactly that at Alexa Smart Home in May-Jul 2025; or JD wants analytics leadership and his Amazon Logistics role ended May 2025. The experience is fresh.\nB == The most relevant experience is from his Amazon tenure (2021-2025) which is recent enough, but the current Founder role (2025-present) is less directly relevant; recruiter will count the Amazon experience as still current enough.\nC == The relevant experience is older (pre-2021) or the current Founder role is the only recent signal and it's not clearly analogous to the JD's function, forcing the recruiter to dig into earlier roles.\nD == The only directly relevant experience is 5+ years old and his most recent roles have moved away from that function (e.g., JD wants private equity analysis, but he's been in product since 2019). The resume screams \"out of practice.\" Only a cover letter explaining the pivot can save it.\nF == The JD demands very recent and continuous experience in a specific area (e.g., \"active hands-on Python development for the past 2 years\") that Justin's resume shows no trace of; structural gap.\nX == JD does not indicate a clear recency preference.",
      "importance": 7
    },
    {
      "label": "Scope & Scale Signals",
      "code": "SS",
      "content": "A == JD's implied scope (e.g., \"manage a $10B+ P&L,\" \"lead 20+ person teams,\" \"drive network-wide strategy\") is directly echoed in Justin's bullets: $15B+ operational resources, 25-person team, $60M+ savings, 400+ station network. Numbers match or exceed.\nB == JD scope is slightly less aggressive (e.g., leading a 5-person team, managing $50M budget) — Justin's scale exceeds requirements, but that might be seen as a positive.\nC == JD scope is moderately larger than his demonstrated numbers (e.g., \"managed 100+ person org,\" \"P&L > $100M\"), but he has adjacent signals that suggest he could scale; recruiter might be unsure.\nD == JD seeks a senior executive (VP/CXO) with clear evidence of leading large orgs (100+), and Justin's resume shows max team of 25 with no C-level title. The resume undersells his potential; a strong cover letter could argue readiness, but the numbers aren't there.\nF == JD mandates a scope of responsibility that Justin has no experience with and cannot claim (e.g., \"managed international supply chains across 20 countries\" — his cross-continent work might exist, but if the JD demands clear P&L ownership of that scope and his resume has none, it's a gap. Still, D might be more appropriate unless it's extreme.)\nX == JD does not provide enough scale information.",
      "importance": 7
    },
    {
      "label": "Leadership & Management Credibility",
      "code": "LM",
      "content": "A == JD emphasizes people management, cross-functional leadership, or team development, and Justin's resume clearly lists \"managed teams of up to 25,\" \"directed a 7-person analytics team,\" \"cross-functional alignment across engineering, UX, GTM.\" Recruiter sees proven people leader.\nB == JD wants some management experience, Justin has it, but it's not the central theme of his resume; still fine.\nC == JD is an IC role but mentions \"mentoring\" or \"influence without authority\"; Justin's heavy management signal might make recruiter wonder if he'd be happy as an IC, or it could be a plus. Ambiguous.\nD == JD is a hands-on individual contributor role with zero management expectations; Justin's resume over-emphasizes leadership and team management, potentially appearing overqualified or misaligned. A cover letter could clarify his IC intentions.\nF == JD requires that the candidate have no management experience (unlikely) or that the role is entry-level and cannot entertain someone with his leadership background. Nearly impossible.\nX == JD does not specify management requirements.",
      "importance": 6
    },
    {
      "label": "Geographic & Work-Model Compatibility",
      "code": "GC",
      "content": "A == JD is on-site in Seattle or remote within US/Pacific time zone; Justin's location is Seattle, WA, perfect match. Or explicitly remote and he's willing.\nB == JD is remote but prefers a specific time zone Justin can accommodate; minor friction.\nC == JD is on-site in a different US city (e.g., SF Bay Area, NYC) and does not mention relocation assistance; Justin might need to relocate, but it's plausible.\nD == JD is on-site in a location that would require significant relocation or international move (e.g., London, Paris) without clear relocation support; resume doesn't indicate willingness to relocate. Only a cover letter could address.\nF == JD is strictly on-site in a location where Justin cannot legally work or has explicitly stated he won't relocate (though we don't have that info; we assume he's mobile). Structural gap unlikely.\nX == JD does not specify location or work model.",
      "importance": 5
    },
    {
      "label": "Credential & Education Alignment",
      "code": "CE",
      "content": "A == JD requires or strongly prefers an MBA from a top-tier school or an engineering degree from a reputable institution; Justin has both (Wharton MBA, Princeton engineering). Perfect alignment.\nB == JD prefers an MBA or STEM degree but does not mandate it; Justin exceeds expectations.\nC == JD does not mention education; his credentials are a nice-to-have but don't directly help.\nD == JD demands a specific certification (e.g., PMP, CFA, AWS Solutions Architect) that Justin does not list; he could potentially acquire it, but resume lacks it now. Cover letter can address intent to certify.\nF == JD requires a professional license (e.g., CPA, law license, medical board certification) that Justin does not have and cannot obtain quickly. Structural disqualification.\nX == JD provides no education or certification requirements.",
      "importance": 5
    },
    {
      "label": "Career Trajectory & Coherence",
      "code": "CT",
      "content": "A == JD targets a generalist leadership role (e.g., \"Head of Product,\" \"VP of Operations,\" \"Chief of Staff\") where Justin's varied background (engineering, finance, operations, product, founding) is a strength and tells a story of versatile executive. Perfect fit.\nB == JD is for a product management role in a fast-growing startup; Justin's entrepreneurial and multi-functional background is seen as an asset, though his Amazon-to-founder transition raises mild questions about commitment.\nC == JD is a traditional corporate product management role (e.g., at a large company expecting consistent career progression). Justin's jump from finance to product to founder could be viewed as \"job hopping\" or lack of focus; recruiter may be neutral but cautious.\nD == JD requires a very stable, linear career path (e.g., \"10+ years of progressive experience in supply chain management at one company\"). Justin's varied roles and industries hurt his narrative; a cover letter is essential to tell a coherent story.\nF == JD requires a career path that Justin's resume contradicts fundamentally (e.g., \"must have spent last 10 years in public education administration\"). No amount of reframing can create that.\nX == JD does not provide enough context about company culture or career expectations.",
      "importance": 5
    }
  ]
}
```

### Comments

#### chuckles — 2026-07-18T17:24:03.518Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-905** | recover rubric only when criteria empty — do not overwrite edits |
| **AST-906** | Get rubric Save still failing (Do/Like OK) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-905** — _recover rubric only when criteria empty — do not overwrite edits_
- **Issue reported:** After Generate recovery / pending restore on rubric criteria pages, the product is **overwriting subsequent edits** the candidate makes. Returning to the page (or recovery) restores agent-generated criteria even when the editor already has rubric criteria the user has edited.
- **Should now:** Pending / agent-response recovery runs only when the candidate has **no** stored rubric criteria for that artifact. If criteria already exist (including after user edits), do not restore over them.
- **Quick check (this fix only):**
  1. Open a candidate Artifacts rubric page (e.g. Get Job Criteria) that already has criteria, or Generate then edit a criterion.
  2. Navigate away and return (or trigger pending recovery).
  3. Observe: edits / existing criteria are overwritten by restored agent generation.

**AST-906** — _Get rubric Save still failing (Do/Like OK)_
- **Issue reported:** Save for **Get** Job Criteria is **still failing** on UAT (candidate `karfo` / Get rubric). Susan reports Save for **Do** and **Like** appear to work; Get Save still fails. (Overwrite recovery made it hard to fully confirm Do/Like, but Get Save failure is confirmed.)
- **Should now:** After Get criteria are visible for review, Save persists them to the candidate's stored Get rubric artifact with a clear success path. Same Save reliability as Do/Like for equivalent rubric saves.
- **Quick check (this fix only):**
  1. Open candidate Artifacts → Get Job Criteria (e.g. `karfo`).
  2. Ensure criteria are on screen for review (Generate or existing).
  3. Click Save → Save fails for Get.
  4. Compare: Save on Do and/or Like rubric pages succeeds (or appears to).

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-18T17:02:25.058Z
Well, now it's OVERWRITING any subsequent edits that hte candidate makes to the changes, so we need to add a check to see if there are already rubric criteria and ONLY restore from the agent responses if there are NONE.

Meanwhile, the save to GET is STILL failing, but save for DO and LIKE seem to be working (can't tell, because of the overwriting issue.)

#### chuckles — 2026-07-16T23:06:00.683Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-903** | craft_get_rubric JSON parse Unterminated string |
| **AST-904** | Get criteria Save failed and content lost on return |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-903** — _craft_get_rubric JSON parse Unterminated string_
- **Issue reported:** On `/artifacts/get_job_criteria` for candidate `karfo`, Generate for Get Job Criteria failed with an Astral error diagnostic while craft_DO succeeded on the same session.
- **Should now:** A successful Get rubric generation returns parseable JSON with a complete `criteria` array, and the editor shows the criteria for review (or a clear recoverable error — not a truncated payload treated as success).
- **Quick check (this fix only):**
  1. Open candidate `karfo` → Artifacts → Get Job Criteria.
  2. Click Generate (or Regenerate).
  3. Observe Astral error diagnostic: Failed to parse JSON response / Unterminated string (Get fails; Do may still succeed).

**AST-904** — _Get criteria Save failed and content lost on return_
- **Issue reported:** On `/artifacts/get_job_criteria` for candidate `karfo`, after several Generate attempts produced a set of Get criteria on screen, clicking **Save** showed:
- **Should now:** After criteria are visible for review, Save persists them to the candidate's stored Get rubric artifact. If Save fails, the user sees a clear error and the completed generation remains recoverable when returning to the page (pending recovery or equivalent).
- **Quick check (this fix only):**
  1. Open candidate `karfo` → Artifacts → Get Job Criteria.
  2. Generate until criteria appear on screen for review.
  3. Click Save → observe toast/diagnostic "Save failed".
  4. Navigate away from Get Job Criteria, then return → criteria are gone (not recovered).

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-16T22:42:39.949Z
Got this error message for Get, but craft_DO returned fine:

```
Astral error diagnostic
timestamp: 2026-07-16T22:34:19.774Z
message: Failed to parse JSON response: Unterminated string starting at: line 43 column 20 (char 5489)
Original response (first 500 chars): {
  "agent_performance": {
    "status": "success",
    "failure_note": "",
    "vector_reviews": [
      "TARACAVK",
      "YERACOVK",
      "DSRACAVK",
      "TDRACOVK",
      "RERACOVK",
      "KWRACOVK",
      "SCRACAVK",
      "GWROCOVK",
      "CAROCOVK",
      "SSRACOVK",
      "FMRACOVK",
      "LMRACOVK"
    ]
  },
  "agent_payload": {
    "criteria": [
      {
        "label": "Title Alignment",
        "code": "TA",
        "content": "A == The JD's target title exactly matches or is 
Cleaned response (first 500 chars): {
  "agent_performance": {
    "status": "success",
    "failure_note": "",
    "vector_reviews": [
      "TARACAVK",
      "YERACOVK",
      "DSRACAVK",
      "TDRACOVK",
      "RERACOVK",
      "KWRACOVK",
      "SCRACAVK",
      "GWROCOVK",
      "CAROCOVK",
      "SSRACOVK",
      "FMRACOVK",
      "LMRACOVK"
    ]
  },
  "agent_payload": {
    "criteria": [
      {
        "label": "Title Alignment",
        "code": "TA",
        "content": "A == The JD's target title exactly matches or is 
route: /artifacts/get_job_criteria
astral_candidate_id: karfo
```

after several attempts, i got a set of get criteria to appear, but when I clicked the save button, I got this error, and when I navigated away and returned, the content was gone.

```
Astral error diagnostic
timestamp: 2026-07-16T22:41:36.804Z
message: Save failed
route: /artifacts/get_job_criteria
astral_candidate_id: karfo
```

#### chuckles — 2026-07-16T19:20:46.616Z
@susan — open questions on the definition:

1. What did the screen show after you clicked Generate — did "Generating..." resolve to visible criteria, an error toast, or did you leave the page during the ~3 minute wait?
2. Where was the Response JSON in your brief copied from (the agent data admin view, logs, elsewhere)?
3. If the criteria reached the browser but were lost because Save was never clicked: keep the review-then-Save gate as-is, or should the editor recover the last completed generation when you return to the page?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
