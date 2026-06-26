# AST-696 — Prefilter output with links

<!-- linear-archive: AST-696 archived 2026-06-23 -->

## Linear archive (AST-696)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-696/prefilter-output-with-links  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

| Ada | engineer | e2ccd503-7d62-41f0-9b26-5bb81b4d7f14 |
| Betty | qa | 854d67f9-b389-4953-8f0f-0c647e02f55f |
| Radia | review | e32c168a-d6cf-4e2c-90f2-8cf4ff01e48b |

Company prefilter asks the model to grade the homepage rubric **and** return enumerated navigation link indices for job-page discovery and optional culture follow-up. **AST-603** added multi-format normalization for prefilter responses, but production runs still lose link metadata: the prompt's **OUTPUT JSON DEFINITION** shows a grades-only `agent_payload` example, so models often omit link tails; when they do return compact encoded lines with bracket link indices (Susan's expected shape), the runtime does not reliably parse those tails into `possible_job_links` and `culture_links_to_explore`. Without persisted link indices, downstream roster steps cannot select a job page from the scraped nav list. This epic closes the prompt contract gap and restores end-to-end link capture for **prefilter_company**.

## Functional scope

* **Prompt schema example (**`link_set` **metadata):** The rendered **{$RESPONSE_SCHEMA}** block for **prefilter_company** must show a complete compact encoded example — grades **plus** two optional **link_set** tails — using Susan's canonical shape: `000|ERC2|MEA3|PGA2|[13]|[3,6,19]`. The first **link_set** is possible job page indices (1–5 ints from the enumerated nav list); the second is culture link indices (1–5 ints). Plain-language instructions in output-type payload text must describe **link_set** fields the same way (bracket lists appended after grade segments), not only grades-only lines.
* **Decode and normalize:** When **prefilter_company** returns compact encoded `agent_payload` strings, bracket **link_set** tails (`[13]`, `[3,6,19]`, comma lists inside brackets, and positional tails without `JOB:`/`CULT:` prefixes) must parse into `possible_job_links` and `culture_links_to_explore` on the decoded job row. Existing **AST-603** alternate shapes (dict JSON, letter-pipe, `JOB:`/`CULT:` prefixes, JSON string keys) continue to work — no regression.
* **Persist and consume:** Parsed link indices flow through the existing prefilter success path into `company_data.possible_job_links` and `company_data.culture_links_to_explore` (culture links on pass/watch only, per current roster rules). **find_job_page** and related roster steps can use the stored indices against the enumerated nav list captured during prefilter.
* **Empty/absent links:** When the model returns no link tails or empty bracket lists, prefilter still completes grading and state transitions; link fields normalize to empty lists (current behavior). Missing links must not fail an otherwise valid graded response.

## Boundaries

* **prefilter_company only** — no changes to other encoded consult tasks (qualify, evaluate, DO/GET/LIKE) unless they already share the same helper and a one-line fix is required for consistency.
* **No rubric content redesign** — vector definitions, dealbreaker thresholds, and **AST-507** pass/fail/score semantics stay as-is.
* **No UI work** — admin prompt paste and rubric editor copy are Susan's manual step if needed after the schema example lands; this epic delivers the config-driven schema example and runtime parsing only.
* **No new company states or dispatch rows** — roster state machine and **find_job_page** dispatch eligibility unchanged except they receive link data that was previously dropped.
* **Must not break** existing **AST-603** repro categories (dict JSON, letter-pipe, JSON string, `JOB:`/`CULT:` encoded tails).

## Acceptance criteria

1. Resolved **{$RESPONSE_SCHEMA}** for **prefilter_company** shows `agent_payload` example `000|ERC2|MEA3|PGA2|[13]|[3,6,19]` (or equivalent with bracket **link_set** tails documented in the same block) — not grades-only `000|ERC2|MEA3|PGA2`.
2. A model response `000|RCA3|MPB3|USA3|[59,60]|[51,46,53]` (matching live rubric vector count) decodes to `possible_job_links == [59, 60]` and `culture_links_to_explore == [51, 46, 53]`.
3. Susan's exact proposed example `000|ERC2|MEA3|PGA2|[13]|[3,6,19]` decodes with the same link field mapping (first tail → job links, second → culture links).
4. **AST-603** normalization paths still pass existing component tests — dict JSON, letter-pipe, `JOB:`/`CULT:` tails, and JSON-string payloads unchanged.
5. On prefilter pass (inflow or legacy watch path), `company_data` persisted after a successful run includes the parsed link lists when the model supplied them; UAT on a company with enumerated nav links shows non-empty `possible_job_links` when the model returns bracket tails.
6. Grades-only encoded responses (no link tails) still pass/fail prefilter and persist empty link lists — no new validation failures.

## Dependencies and blockers

* **AST-603** (Done) — consult-parity normalization and prefilter hydration; this epic extends that path for bracket **link_set** tails in compact encoded lines and fixes the prompt example.
* **AST-507** (Done) — encoded prefilter grading and inflow state semantics (unchanged).
* **AST-508** (Done) — locate dispatch consumes `prefilter_score`; benefits indirectly when job links are present.

None blocking start.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-696 (parent) | ftr/AST-696-prefilter-output-with-links |
| AST-697 | sub/AST-696/AST-697-prefilter-link-set-schema-and-bracket-decode |
| AST-698 | sub/AST-696/AST-698-uat-raw-response-missing-from-debug-logs-prefilter |
| AST-699 | sub/AST-696/AST-699-uat-possible-job-links-dropped-letter-pipe-brackets |

**Epic worktree:** `astral-AST-696/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| Ada | engineer | e4994c57-a608-41fd-b15a-42ae4918eef1 |

---

## Original brief

the Prefilter responses are not parsing the possible job links and culture links, and I think we need a response schema example for the a "link_set" type of metadata.

This is what the parsed prompt looks like now:

```
You are evaluating a company's homepage to determine if it's worth watching for job opportunities for Susan.

You will receive scraped text from a company homepage. Grade each vector in the rubric below based on what you can determine from the homepage content.

**Rules:**
1. Grade every vector in the rubric. Use only A, B, C, D, F, or X. No other values.
2. Use X when the homepage doesn't provide enough information to assess a vector. Don't guess.
3. Don't add vectors. Grade only what the rubric defines.
4. Default toward leniency. This is a prefilter — it's cheap to watch a company, expensive to miss one. Save your scrutiny for later stages.
5. Match the output schema exactly. If the shape is wrong, your work is lost.

**Your Rubric for evaluation:**

### Reality Check - Is this the website for a company that Susan might work at?
A == It is a typical website with content about products or services, a link to a careers page, etc.
B == It is an elaborate website that isn't clearly a company website, but at least it's about the company, such as a VC portfolio page.
C == It is a social media site for the company, but not their website.  Links might still be found to job openings from here.
D == This is a company website, but it doesn't look like the expected website for this company.
F == This is obviously not a company website, someone got confused in their previous research identifying the company.

### Mission & Product Orientation
A == Company has a clear product or platform with a mission oriented toward improving outcomes in healthcare, patient care, clinical systems, or human wellbeing through technology, e.g. 'AI-powered platform helping clinicians reduce diagnostic errors'
B == Company has a clear technical product or platform with a mission oriented toward solving complex, meaningful problems even if outside healthcare: infrastructure reliability, data governance, operational efficiency for technical teams, e.g. 'Developer platform that simplifies cloud-native application deployment'
C == Company has a product but mission is primarily commercial or generic without a strong problem-solving orientation, e.g. 'CRM platform for mid-market sales teams'
D == Company appears to be primarily a services or consulting firm, or the product is unclear and the homepage is mostly marketing language without substance, e.g. 'Digital transformation consultancy offering bespoke solutions'
F == Company mission is fundamentally misaligned with Susan's values such as surveillance tech, predatory lending, or weapons systems, e.g. 'Contract staffing agency placing temporary IT workers' or 'Facial recognition platform for law enforcement'
X == Cannot determine what the company builds or what its mission is from available information

### US Presence & Time Zone Compatibility
A == Company website is in English and hosted domestically (e.g. .com, .org, etc.)
B == Company website is in English, hosted elsewhere
F == Company website is hosted internationally (e.g. *.au, etc.) or the website is not in English
X == Can't read the page text

### POSSIBLE_JOB_LINKS
Provide in your response 1-5 link numbers from the enumerated list in order of likelihood to be the link to the company's job page.  This could be a careers subpage or a link to a known ATS.

### CULTURE_LINKS_TO_EXPLORE
If you have a good feeling about this company for Susan, include a list of 1-5 link numbers that you would like to click on to get more insight into the company's culture for downstream analysis.

## OUTPUT JSON DEFINITION
Provide your response in this format exactly:

{
  "agent_performance": {
    "status": "success | failure",
    "failure_note": "<failure_note>"
  },
  "agent_payload": "000|ERC2|MEA3|PGA2"
}
```

I think the agent_payload example needs to be `000|ERC2|MEA3|PGA2|[13]|[3,6,19]` so the runtime agent knows how to include the requested metadata of possible job links and culture pages.

### Comments

#### chuckles — 2026-06-16T04:42:18.866Z
[check-linear] User Testing — agreed; fixed-slot parse belongs in next epic (@susan)

Noted on the pattern concern: letter-pipe + rubric-width spillover is fragile. Next ticket should mirror **evaluate_jd** / **qualify_joblisting** — known post-rubric slots (job id, title, link, then optional tails) instead of inferring link fields from leftover tokens.

This epic stays as-is until you decide: assign parent back to Chuckles for one spillover fix-uat pass, or accept current UAT and scope the structural parse in the follow-on.

— Chuckles

#### susan — 2026-06-16T04:40:14.080Z
@Chuckles The pattern of this prefilter makes me deeply uneasy.  I think we had better solve this in the next ticket where we are using the same pattern as with evaluate_jd and qualify_joblisting.

#### chuckles — 2026-06-16T04:37:25.851Z
[check-linear] answered — left-to-right confirmed; spillover grade letter shifts link tails

Confirmed in `consult._job_from_letter_pipe`: fields are walked **left to right**, not peeled from the right. After `n` rubric grade slots are filled, every remaining pipe token goes to `link_fields` — first token → `possible_job_links`, rest → culture.

Your UAT shape `A|B|A|[35]|[22,34,…]` with **two** hydrated grade vectors matches spillover: if the live rubric artifact exposes **n=2** scoring vectors but the model returns **three** single-letter grades, the third `A` becomes `link_fields[0]` (parses empty), `[35]` lands in culture, and `possible_job_links` stays `[]`. AST-699 fixed position-prefix misrouting to encoded decode; it does not fix grade-count vs link-field alignment.

Next step is a fix-uat bug for parse alignment (grade segments vs link_set tails), not another re-test pass. Assign parent back to Chuckles when ready for `[fix]`.

— Chuckles

#### susan — 2026-06-16T04:36:08.475Z
@chuckles I'm not sure what you need me to do here.  The issue is still happening as described above.  Links chosen in the raw response but not parsed correctly.

Joblist parse handled this well, where the first three post-rubric strings were known to be external job id, job title and job link, and after that there were possibly additional metadata.

If you're using regex to "peel off" the right side of the response, rather than going in left to right, you may be opening yourself to logical issues you don't need.  Please check the code to confirm this before I assign the ticket back to you.

#### chuckles — 2026-06-16T04:24:29.514Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-699** | possible_job_links dropped from letter-pipe bracket tails |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-699** — _possible_job_links dropped from letter-pipe bracket tails_
- **Issue reported:** Prefilter runs show **culture_links_to_explore** populated but `possible_job_links` **always** `[]` in the parsed/hydrated job row, even when the raw model response clearly includes a job link index (often a **single-element bracket array** such as `[35]` or `[40]`).
- **Should now:** Letter-pipe and compact encoded prefilter payloads map the **first link_set tail after grade segments** to `possible_job_links` and the **second tail** to `culture_links_to_explore`. Single-element bracket arrays like `[35]` must parse to `[35]` on `possible_job_links`, not be dr
- **Quick check (this fix only):**
  1. Run prefilter batch with **debug=True** on companies in **WEBSITE_FOUND** (e.g. growtherapy, endorlabs, dataiku from Susan's 2026-06-16 batch).
  2. Inspect debug log raw `agent_payload` lines — confirm pattern `A|B|A|[N]|[[culture indices]]` (or similar).
  3. Inspect parsed job JSON in execution history — observe `possible_job_links: []` while culture list is populated.
  4. Confirm `company_data.possible_job_links` stays empty after pass/watch.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-16T04:16:16.095Z
I can now prove that we are not correctly parsing the content sent.  Specifically, the possible job links are getting choices sent back in the raw response, but they are lost in the parsing/hydration.  Possibly because it's sending a single element array, but in any event, it needs to be fixed.

```
--- [1/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "A",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        32,
        10,
        4,
        7,
        8,
        12
      ],
      "astral_job_id": "growtherapy"
    }
  ]
}

--- [2/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "A",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        54,
        51,
        52,
        53
      ],
      "astral_job_id": "firemon"
    }
  ]
}

--- [3/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "A",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        25,
        43,
        45,
        21,
        28,
        18
      ],
      "astral_job_id": "foxglove"
    }
  ]
}

--- [4/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "A",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        4,
        2,
        60,
        61,
        62
      ],
      "astral_job_id": "definitivehc"
    }
  ]
}

--- [5/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "B",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        18,
        16,
        46,
        50
      ],
      "astral_job_id": "ethos"
    }
  ]
}

--- [6/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "A",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        82,
        77,
        79,
        81,
        68,
        67
      ],
      "astral_job_id": "everbridge"
    }
  ]
}

--- [7/10] ---
{
  "jobs": [
    {
      "grades": [],
      "possible_job_links": [],
      "culture_links_to_explore": [
        40,
        31,
        42,
        99,
        39,
        98
      ],
      "astral_job_id": "gitlab"
    }
  ]
}

--- [8/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "B",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        35,
        22,
        34,
        39,
        52,
        53
      ],
      "astral_job_id": "endorlabs"
    }
  ]
}

--- [9/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "A",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        31,
        30,
        36,
        37,
        38,
        40
      ],
      "astral_job_id": "dataiku"
    }
  ]
}

--- [10/10] ---
{
  "jobs": [
    {
      "grades": [
        {
          "vector": "Mission & Product Orientation",
          "grade": "A",
          "confidence": 3
        },
        {
          "vector": "US Presence & Time Zone Compatibility",
          "grade": "C",
          "confidence": 3
        }
      ],
      "possible_job_links": [],
      "culture_links_to_explore": [
        40,
        39,
        63,
        64,
        113,
        114
      ],
      "astral_job_id": "coinbase"
    }
  ]
}
```

raw log content:

```
[2026-06-16 04:12:50] INFO src.core.agent:  |   "agent_payload": "A|B|A|[35]|[22,34,39,52,53]"
[2026-06-16 04:12:50] INFO src.core.agent:  | }
[2026-06-16 04:12:50] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=27
[2026-06-16 04:12:50] INFO src.core.agent:  | A|B|A|[35]|[22,34,39,52,53]
[2026-06-16 04:12:50] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=endorlabs
[2026-06-16 04:12:50] INFO src.core.agent: do_task index 1/1 endorlabs -> completed
[2026-06-16 04:12:50] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:50] INFO src.core.roster: [endorlabs] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:50] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.5s stop=end_turn tokens in=2088 out=52
[2026-06-16 04:12:50] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:50] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.5s stop_reason=end_turn
[2026-06-16 04:12:50] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=2088 cache_read=1408 cache_write=0 output=52
[2026-06-16 04:12:50] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:50] INFO src.external.deepseek:  | {
[2026-06-16 04:12:50] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:50] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:50] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:50] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:50] INFO src.external.deepseek:  |   "agent_payload": "A|A|A|[31]|[30,36,37,38,40]"
[2026-06-16 04:12:50] INFO src.external.deepseek:  | }
[2026-06-16 04:12:50] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=130
[2026-06-16 04:12:50] INFO src.core.agent:  | {
[2026-06-16 04:12:50] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:50] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:50] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:50] INFO src.core.agent:  |   },
[2026-06-16 04:12:50] INFO src.core.agent:  |   "agent_payload": "A|A|A|[31]|[30,36,37,38,40]"
[2026-06-16 04:12:50] INFO src.core.agent:  | }
[2026-06-16 04:12:50] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=27
[2026-06-16 04:12:50] INFO src.core.agent:  | A|A|A|[31]|[30,36,37,38,40]
[2026-06-16 04:12:50] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=dataiku
[2026-06-16 04:12:50] INFO src.core.agent: do_task index 1/1 dataiku -> completed
[2026-06-16 04:12:50] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:50] INFO src.core.roster: [dataiku] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:50] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.7s stop=end_turn tokens in=3330 out=52
[2026-06-16 04:12:50] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:50] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.7s stop_reason=end_turn
[2026-06-16 04:12:50] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=3330 cache_read=1408 cache_write=0 output=52
[2026-06-16 04:12:50] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:50] INFO src.external.deepseek:  | {
[2026-06-16 04:12:50] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:50] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:50] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:50] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:50] INFO src.external.deepseek:  |   "agent_payload": "A|C|A|[40]|[39,63,64,113,114]"
[2026-06-16 04:12:50] INFO src.external.deepseek:  | }
[2026-06-16 04:12:50] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=132
[2026-06-16 04:12:50] INFO src.core.agent:  | {
[2026-06-16 04:12:50] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:50] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:50] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:50] INFO src.core.agent:  |   },
[2026-06-16 04:12:50] INFO src.core.agent:  |   "agent_payload": "A|C|A|[40]|[39,63,64,113,114]"
[2026-06-16 04:12:50] INFO src.core.agent:  | }
[2026-06-16 04:12:50] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=29
[2026-06-16 04:12:50] INFO src.core.agent:  | A|C|A|[40]|[39,63,64,113,114]
[2026-06-16 04:12:50] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=coinbase
[2026-06-16 04:12:50] INFO src.core.agent: do_task index 1/1 coinbase -> completed
[2026-06-16 04:12:50] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:50] INFO src.core.roster: [coinbase] company state WEBSITE_FOUND -> WEBSITE_FOUND_RETRY (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:50] ERROR src.core.roster: [coinbase] prefilter error: No rubric description for vector 'US Presence & Time Zone Compatibility' grade C
[2026-06-16 04:12:50] INFO src.core.dispatcher:  | batch end summary={'total_processed': 10, 'total_passed': 8, 'total_failed': 1, 'total_errors': 1}
[2026-06-16 04:12:50] INFO src.core.dispatcher:  | runner returned summary={'total_processed': 10, 'total_passed': 8, 'total_failed': 1, 'total_errors': 1}
[2026-06-16 04:12:50] INFO src.core.dispatcher:  | iteration 1 summary processed=10 passed=8 failed=1 errors=1 accumulated={'total_processed': 10, 'total_passed': 8, 'total_failed': 1, 'total_errors': 1}
[2026-06-16 04:12:50] INFO src.core.dispatcher:  | loop stop: max_runs reached max_runs=1 run_count=1
[2026-06-16 04:12:48] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=gitlab in_run_next_chain=False
[2026-06-16 04:12:48] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:48] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:48] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:48] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:48] INFO src.core.agent: do_task index 1/1 endorlabs -> task start
[2026-06-16 04:12:48] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=endorlabs in_run_next_chain=False
[2026-06-16 04:12:48] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:48] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:48] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:48] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.9s stop=end_turn tokens in=4135 out=52
[2026-06-16 04:12:48] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:48] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.9s stop_reason=end_turn
[2026-06-16 04:12:48] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=4135 cache_read=1408 cache_write=0 output=52
[2026-06-16 04:12:48] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:48] INFO src.external.deepseek:  | {
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:48] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:48] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   "agent_payload": "A|A|A|[82]|[77,79,81,68,67]"
[2026-06-16 04:12:48] INFO src.external.deepseek:  | }
[2026-06-16 04:12:48] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=130
[2026-06-16 04:12:48] INFO src.core.agent:  | {
[2026-06-16 04:12:48] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:48] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:48] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:48] INFO src.core.agent:  |   },
[2026-06-16 04:12:48] INFO src.core.agent:  |   "agent_payload": "A|A|A|[82]|[77,79,81,68,67]"
[2026-06-16 04:12:48] INFO src.core.agent:  | }
[2026-06-16 04:12:48] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=27
[2026-06-16 04:12:48] INFO src.core.agent:  | A|A|A|[82]|[77,79,81,68,67]
[2026-06-16 04:12:48] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=everbridge
[2026-06-16 04:12:48] INFO src.core.agent: do_task index 1/1 everbridge -> completed
[2026-06-16 04:12:48] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:48] INFO src.core.roster: [everbridge] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:48] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.9s stop=end_turn tokens in=2758 out=55
[2026-06-16 04:12:48] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:48] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.9s stop_reason=end_turn
[2026-06-16 04:12:48] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=2758 cache_read=1408 cache_write=0 output=55
[2026-06-16 04:12:48] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:48] INFO src.external.deepseek:  | {
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:48] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:48] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   "agent_payload": "A00|B00|A00|[40]|[31,42,99,39,98]"
[2026-06-16 04:12:48] INFO src.external.deepseek:  | }
[2026-06-16 04:12:48] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=136
[2026-06-16 04:12:48] INFO src.core.agent:  | {
[2026-06-16 04:12:48] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:48] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:48] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:48] INFO src.core.agent:  |   },
[2026-06-16 04:12:48] INFO src.core.agent:  |   "agent_payload": "A00|B00|A00|[40]|[31,42,99,39,98]"
[2026-06-16 04:12:48] INFO src.core.agent:  | }
[2026-06-16 04:12:48] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=33
[2026-06-16 04:12:48] INFO src.core.agent:  | A00|B00|A00|[40]|[31,42,99,39,98]
[2026-06-16 04:12:48] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=gitlab
[2026-06-16 04:12:48] INFO src.core.agent: do_task index 1/1 gitlab -> completed
[2026-06-16 04:12:48] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:48] INFO src.core.roster: [gitlab] company state WEBSITE_FOUND -> IGNORE (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:48] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:48] INFO src.core.agent: do_task index 1/1 dataiku -> task start
[2026-06-16 04:12:48] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=dataiku in_run_next_chain=False
[2026-06-16 04:12:48] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:48] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:48] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:48] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:48] INFO src.core.agent: do_task index 1/1 coinbase -> task start
[2026-06-16 04:12:48] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=coinbase in_run_next_chain=False
[2026-06-16 04:12:48] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:48] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:48] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:48] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:48] INFO src.external.deepseek: LLM deepseek task=prefilter_company 2.3s stop=end_turn tokens in=5873 out=52
[2026-06-16 04:12:48] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:48] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=2.3s stop_reason=end_turn
[2026-06-16 04:12:48] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=5873 cache_read=1408 cache_write=0 output=52
[2026-06-16 04:12:48] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:48] INFO src.external.deepseek:  | {
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:48] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:48] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:48] INFO src.external.deepseek:  |   "agent_payload": "A|B|A|[35]|[22,34,39,52,53]"
[2026-06-16 04:12:48] INFO src.external.deepseek:  | }
[2026-06-16 04:12:48] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=130
[2026-06-16 04:12:48] INFO src.core.agent:  | {
[2026-06-16 04:12:48] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:48] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:48] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:48] INFO src.core.agent:  |   },
[2026-06-16 04:12:46] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:46] INFO src.external.deepseek:  | {
[2026-06-16 04:12:46] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:46] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:46] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:46] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:46] INFO src.external.deepseek:  |   "agent_payload": "A|A|A|[4]|[2,60,61,62]"
[2026-06-16 04:12:46] INFO src.external.deepseek:  | }
[2026-06-16 04:12:46] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=125
[2026-06-16 04:12:46] INFO src.core.agent:  | {
[2026-06-16 04:12:46] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:46] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:46] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:46] INFO src.core.agent:  |   },
[2026-06-16 04:12:46] INFO src.core.agent:  |   "agent_payload": "A|A|A|[4]|[2,60,61,62]"
[2026-06-16 04:12:46] INFO src.core.agent:  | }
[2026-06-16 04:12:46] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=22
[2026-06-16 04:12:46] INFO src.core.agent:  | A|A|A|[4]|[2,60,61,62]
[2026-06-16 04:12:46] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=definitivehc
[2026-06-16 04:12:46] INFO src.core.agent: do_task index 1/1 definitivehc -> completed
[2026-06-16 04:12:46] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:46] INFO src.core.roster: [definitivehc] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:46] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.8s stop=end_turn tokens in=2233 out=48
[2026-06-16 04:12:46] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:46] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.8s stop_reason=end_turn
[2026-06-16 04:12:46] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=2233 cache_read=1408 cache_write=0 output=48
[2026-06-16 04:12:46] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:46] INFO src.external.deepseek:  | {
[2026-06-16 04:12:46] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:46] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:46] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:46] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:46] INFO src.external.deepseek:  |   "agent_payload": "A|B|A|[18]|[16,46,50]"
[2026-06-16 04:12:46] INFO src.external.deepseek:  | }
[2026-06-16 04:12:46] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=124
[2026-06-16 04:12:46] INFO src.core.agent:  | {
[2026-06-16 04:12:46] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:46] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:46] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:46] INFO src.core.agent:  |   },
[2026-06-16 04:12:46] INFO src.core.agent:  |   "agent_payload": "A|B|A|[18]|[16,46,50]"
[2026-06-16 04:12:46] INFO src.core.agent:  | }
[2026-06-16 04:12:46] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=21
[2026-06-16 04:12:46] INFO src.core.agent:  | A|B|A|[18]|[16,46,50]
[2026-06-16 04:12:46] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=ethos
[2026-06-16 04:12:46] INFO src.core.agent: do_task index 1/1 ethos -> completed
[2026-06-16 04:12:46] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:46] INFO src.core.roster: [ethos] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:46] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:46] INFO src.core.agent: do_task index 1/1 gitlab -> task start
[2026-06-16 04:12:44] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:44] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:44] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:44] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.6s stop=end_turn tokens in=1852 out=52
[2026-06-16 04:12:44] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:44] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.6s stop_reason=end_turn
[2026-06-16 04:12:44] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=1852 cache_read=1408 cache_write=0 output=52
[2026-06-16 04:12:44] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:44] INFO src.external.deepseek:  | {
[2026-06-16 04:12:44] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:44] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:44] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:44] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:44] INFO src.external.deepseek:  |   "agent_payload": "A|A|A|[25]|[43,45,21,28,18]"
[2026-06-16 04:12:44] INFO src.external.deepseek:  | }
[2026-06-16 04:12:44] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=130
[2026-06-16 04:12:44] INFO src.core.agent:  | {
[2026-06-16 04:12:44] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:44] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:44] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:44] INFO src.core.agent:  |   },
[2026-06-16 04:12:44] INFO src.core.agent:  |   "agent_payload": "A|A|A|[25]|[43,45,21,28,18]"
[2026-06-16 04:12:44] INFO src.core.agent:  | }
[2026-06-16 04:12:44] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=27
[2026-06-16 04:12:44] INFO src.core.agent:  | A|A|A|[25]|[43,45,21,28,18]
[2026-06-16 04:12:44] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=foxglove
[2026-06-16 04:12:44] INFO src.core.agent: do_task index 1/1 foxglove -> completed
[2026-06-16 04:12:44] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:44] INFO src.core.roster: [foxglove] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:44] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:44] INFO src.core.agent: do_task index 1/1 ethos -> task start
[2026-06-16 04:12:44] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=ethos in_run_next_chain=False
[2026-06-16 04:12:44] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:44] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:44] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:44] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:44] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:44] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:44] INFO src.core.agent: do_task index 1/1 everbridge -> task start
[2026-06-16 04:12:44] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=everbridge in_run_next_chain=False
[2026-06-16 04:12:44] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:44] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:44] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:44] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:44] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:44] INFO src.external.deepseek: LLM deepseek task=prefilter_company 2.0s stop=end_turn tokens in=4656 out=50
[2026-06-16 04:12:44] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:44] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=2.0s stop_reason=end_turn
[2026-06-16 04:12:44] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=4656 cache_read=1408 cache_write=0 output=50
[2026-06-16 04:12:42] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:42] INFO src.core.agent: do_task index 1/1 firemon -> task start
[2026-06-16 04:12:42] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=firemon in_run_next_chain=False
[2026-06-16 04:12:42] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:42] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:42] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:42] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:42] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:42] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.6s stop=end_turn tokens in=4095 out=48
[2026-06-16 04:12:42] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:42] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.6s stop_reason=end_turn
[2026-06-16 04:12:42] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=4095 cache_read=1408 cache_write=0 output=48
[2026-06-16 04:12:42] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:42] INFO src.external.deepseek:  | {
[2026-06-16 04:12:42] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:42] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:42] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:42] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:42] INFO src.external.deepseek:  |   "agent_payload": "A|A|A|[54]|[51,52,53]"
[2026-06-16 04:12:42] INFO src.external.deepseek:  | }
[2026-06-16 04:12:42] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=124
[2026-06-16 04:12:42] INFO src.core.agent:  | {
[2026-06-16 04:12:42] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:42] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:42] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:42] INFO src.core.agent:  |   },
[2026-06-16 04:12:42] INFO src.core.agent:  |   "agent_payload": "A|A|A|[54]|[51,52,53]"
[2026-06-16 04:12:42] INFO src.core.agent:  | }
[2026-06-16 04:12:42] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=21
[2026-06-16 04:12:42] INFO src.core.agent:  | A|A|A|[54]|[51,52,53]
[2026-06-16 04:12:42] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=firemon
[2026-06-16 04:12:42] INFO src.core.agent: do_task index 1/1 firemon -> completed
[2026-06-16 04:12:42] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:42] INFO src.core.roster: [firemon] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:42] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:42] INFO src.core.agent: do_task index 1/1 foxglove -> task start
[2026-06-16 04:12:42] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=foxglove in_run_next_chain=False
[2026-06-16 04:12:42] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:42] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:42] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:42] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:42] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:42] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:42] INFO src.core.agent: do_task index 1/1 definitivehc -> task start
[2026-06-16 04:12:42] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=definitivehc in_run_next_chain=False
[2026-06-16 04:12:42] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:42] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:25] INFO src.core.dispatcher: dispatcher._run_unified index 6/10 ethos -> claimed
[2026-06-16 04:12:25] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:25] INFO src.core.dispatcher: dispatcher._run_unified index 7/10 endorlabs -> claimed
[2026-06-16 04:12:25] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:25] INFO src.core.dispatcher: dispatcher._run_unified index 8/10 definitivehc -> claimed
[2026-06-16 04:12:25] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:25] INFO src.core.dispatcher: dispatcher._run_unified index 9/10 dataiku -> claimed
[2026-06-16 04:12:25] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:25] INFO src.core.dispatcher: dispatcher._run_unified index 10/10 coinbase -> claimed
[2026-06-16 04:12:25] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:25] INFO src.core.agent: run_next chain entry: task=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:25] INFO src.core.agent: do_task index 1/1 growtherapy -> task start
[2026-06-16 04:12:25] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=growtherapy in_run_next_chain=False
[2026-06-16 04:12:25] INFO src.core.agent:  | token_overlay chain_entry=True caller_source=chain_entry parent=none caller_keys=CALLER_CACHE_A=empty,CALLER_CACHE_B=empty,CALLER_CACHE_C=empty,CALLER_CACHE_D=empty,CALLER_RESPONSE=empty,CALLER_SYSTEM=empty
[2026-06-16 04:12:25] INFO src.core.agent:  | job_context tokens=RESUME_SECTION_CATALOG
[2026-06-16 04:12:25] INFO src.core.agent: [DEBUG] do_task('prefilter_company'): brain_setting=Medium provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-06-16 04:12:25] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-06-16 04:12:25] INFO src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-06-16 04:12:25] INFO src.external.deepseek: LLM deepseek task=prefilter_company 1.6s stop=end_turn tokens in=3360 out=52
[2026-06-16 04:12:25] INFO src.external.deepseek: send_to_deepseek index 1/1 prefilter_company -> success
[2026-06-16 04:12:25] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=prefilter_company duration=1.6s stop_reason=end_turn
[2026-06-16 04:12:25] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=3360 cache_read=1408 cache_write=0 output=52
[2026-06-16 04:12:25] INFO src.external.deepseek:  | response_preview:
[2026-06-16 04:12:25] INFO src.external.deepseek:  | {
[2026-06-16 04:12:25] INFO src.external.deepseek:  |   "agent_performance": {
[2026-06-16 04:12:25] INFO src.external.deepseek:  |     "status": "success",
[2026-06-16 04:12:25] INFO src.external.deepseek:  |     "failure_note": ""
[2026-06-16 04:12:25] INFO src.external.deepseek:  |   },
[2026-06-16 04:12:25] INFO src.external.deepseek:  |   "agent_payload": "A|A|A|[32]|[10,4,7,8,12]"
[2026-06-16 04:12:25] INFO src.external.deepseek:  | }
[2026-06-16 04:12:25] INFO src.core.agent:  | raw_response task_key=prefilter_company lines=7 chars=127
[2026-06-16 04:12:25] INFO src.core.agent:  | {
[2026-06-16 04:12:25] INFO src.core.agent:  |   "agent_performance": {
[2026-06-16 04:12:25] INFO src.core.agent:  |     "status": "success",
[2026-06-16 04:12:25] INFO src.core.agent:  |     "failure_note": ""
[2026-06-16 04:12:25] INFO src.core.agent:  |   },
[2026-06-16 04:12:25] INFO src.core.agent:  |   "agent_payload": "A|A|A|[32]|[10,4,7,8,12]"
[2026-06-16 04:12:25] INFO src.core.agent:  | }
[2026-06-16 04:12:25] INFO src.core.agent:  | encoded_payload task_key=prefilter_company lines=1 chars=24
[2026-06-16 04:12:25] INFO src.core.agent:  | A|A|A|[32]|[10,4,7,8,12]
[2026-06-16 04:12:25] INFO src.core.agent: do_task(prefilter_company) completed successfully batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 index=growtherapy
[2026-06-16 04:12:25] INFO src.core.agent: do_task index 1/1 growtherapy -> completed
[2026-06-16 04:12:25] INFO src.core.agent:  | task_key=prefilter_company batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 success=True
[2026-06-16 04:12:25] INFO src.core.roster: [growtherapy] company state WEBSITE_FOUND -> TO_WATCH (batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0)
[2026-06-16 04:12:13] INFO dispatch.scheduler: Dispatching prefilter — 219 available, batch prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 1/1 prefilter -> loop iteration 1 starting
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | available=219 effective_min=1 max_runs=1 draining=False entity_batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_task index 1/1 prefilter -> running batch
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | batch_size=10 batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 entity_type='company' trigger_state='WEBSITE_FOUND'
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 company/WEBSITE_FOUND -> claimed 10 entity/entities
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | task_key=prefilter batch_id=prefilter-c1fd51c7-008a-4ab4-9df3-0bc82315b6d0 batch_call_mode=False dispatch batch_size=10 claim_cap=None claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_unified index 1/10 growtherapy -> claimed
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_unified index 2/10 gitlab -> claimed
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_unified index 3/10 foxglove -> claimed
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_unified index 4/10 firemon -> claimed
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-06-16 04:12:13] INFO src.core.dispatcher: dispatcher._run_unified index 5/10 everbridge -> claimed
[2026-06-16 04:12:13] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
```

#### chuckles — 2026-06-16T03:59:16.793Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-698** | raw model response missing from debug logs on prefilter runs |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-698** — _raw model response missing from debug logs on prefilter runs_
- **Issue reported:** With **debug=True** on company prefilter runs (`prefilter_company`), execution history / app log content no longer includes the **actual raw model response body**. Susan cannot see what the model returned when troubleshooting link_set / prefilter parse issues during UAT.
- **Should now:** When **debug=True**, each prefilter (and other `do_task`) hop logs the full raw API response text under the debug contract (summary line + truncated body via `debug_detail_block`), same as other entity types — not only pass/fail metadata or parsed summaries.
- **Quick check (this fix only):**
  1. Run a company through **prefilter_company** with **debug=True** (batch or ad-hoc).
  2. Open execution history / app log for that run.
  3. Observe missing or empty raw response payload in the log stream despite debug being on.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-16T03:49:09.438Z
It appears that the logging of raw responses got dropped when the debug flag is on.  Did that get conditionally set for job entity types or something?  I need to see the actual raw responses in the log content for these runs.  It's impossible to troubleshoot issues otherwise.

---

_Implementation detail may live in git history on `origin/dev`._
