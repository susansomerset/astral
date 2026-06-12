# Roster scope: itemized changes from Linear feature issues

This doc itemizes the **scope differences** between (a) the Linear roster feature descriptions and (b) the current codebase, with focus on **company state** and **find_job_page vs parse_job_page**. It then assesses whether that scope is sound per ASTRAL_CODE_RULES and general engineering practice.

---

## 1. Company state machine

### 1.1 States in the feature docs (roster-features.csv)

Pipeline states implied by the five features:

| State | When set | Next step / meaning |
|-------|----------|----------------------|
| **imported** | After CSV/single import (Feature 1) | Input to Locate Company Website |
| **website_found** | After Locate Company Website success (Feature 2) | Input to Prefilter |
| **no_website** | After Locate Company Website failure | Terminal; manual review |
| **TO_WATCH** | After Prefilter WATCH (Feature 3) | Input to Locate Company Job Page |
| **TO_PARSE** | After Locate Company Job Page finds jobSite (Feature 4) | Input to Parse Company Job Page |
| **NO_JOBS** | Locate found job page but “no openings” | Terminal; has jobSite |
| **NO_JOB_SITE** | Locate could not find job site | Terminal; manual review |
| **NEW** | After Parse success (Feature 5) | Ready for Gazer |
| **CANNOT_PARSE_JOB_SITE** | Parse could not determine structure | Terminal; manual review |
| **BOT_BLOCKED** | Parse hit bot blocker/CAPTCHA | Terminal; may retry later |

Additional concepts in the docs:

- **prefilter**: WATCH | IGNORE | UNKNOWN (stored on company; IGNORE moves to “ignore” node).
- **batch_id**: Used for locking when processing by state (TO_WATCH, TO_PARSE).

### 1.2 States in the current code

**Data layer** (`src/data/database.py`):

- **ALLOWED_STATES** for company: `{'new', 'fix', 'watch', 'active', 'ignore', 'test'}`.
- **save_company(state=…)** rejects any state not in that set.

**Config** (`src/utils/config.py`):

- **response_type_to_state** (vetJobPage → company state):  
  `try_parse` → `new`, `no_jobs_msg` → `new`, `no_clue` → `fix`, `bot_block` → `fix`.

So today:

- Company state is **only** one of: new, fix, watch, active, ignore, test.
- There are **no** pipeline states like imported, website_found, TO_WATCH, TO_PARSE, NO_JOBS, NO_JOB_SITE, NEW, CANNOT_PARSE_JOB_SITE, BOT_BLOCKED in the DB.
- “NEW” in the docs is implemented as **state='new'** (same name, different role: “parse success” in docs vs “company ready / clear postings” in code).
- No **prefilter** or **batch_id** on company in the current schema.

### 1.3 Itemized scope change: company state

1. **Extend allowed company states** to include the pipeline states above (or a chosen subset), and persist them in the company table so batch/UI can filter by stage (e.g. TO_WATCH, TO_PARSE).
2. **Add company fields** (or equivalent): e.g. **prefilter**, **prefilterNotes**, **batch_id**, and any **job_site_notes**-style field if not already covered by companyData.
3. **Centralize state rules** in config: e.g. a single list of allowed company states and optional transition rules (per ASTRAL_CODE_RULES: config owns rules, core/data use them). Today only response_type_to_state exists; pipeline states are undocumented in code.
4. **Batch locking for company** (like Tracker for postings): e.g. set_batch_for_companies(state, batch_id, limit) and clear_batch, so Features 4 and 5 can “claim” companies by state (TO_WATCH, TO_PARSE) without double-processing.
5. **Migrate existing data**: Current companies in `new`/`fix`/`watch`/etc. need a clear mapping into the new state set (or we keep a hybrid during migration).

---

## 2. find_job_page vs parse_job_page functionality

### 2.1 In the feature docs

- **Feature 4 – Locate Company Job Page (find_job_page):**
  - **Input:** Companies with state=TO_WATCH, companyWebsite set.
  - **Output:** Only the **jobSite URL** and outcome.
  - **Outcomes:** TO_PARSE (found job list page), NO_JOBS (job page, no openings), NO_JOB_SITE (couldn’t find).
  - **Does not:** Extract selectors, run parseJobTag, or write container/jobItem/metadata_schema.

- **Feature 5 – Parse Company Job Page (parse_job_page):**
  - **Input:** Companies with state=TO_PARSE, jobSite set.
  - **Output:** Parsing config (container, jobItem, metadata_schema, parseType, jobTag) and validation result.
  - **Outcomes:** NEW (success), CANNOT_PARSE_JOB_SITE, BOT_BLOCKED.
  - **Does:** Navigate to jobSite, run parseJobTag (or “parse_job_list” task), validate extraction, save to company_data.

So in the **docs**, find and parse are **two separate stages**: find only discovers jobSite and sets state; parse runs later on TO_PARSE companies and writes parsing config.

### 2.2 In the current code

- **find_job_page()** in `src/core/roster.py`:
  - Does **discovery** (crawl → pickJobPages → vetJobPage → try_link/push_button recursion, etc.).
  - When vetJobPage returns **try_parse**, it **immediately** calls **_handle_try_parse_response**:
    - Extracts DOM, calls **_fetch_jobtag** (parseJobTag task), validates, then **_save_company_data(..., response_type="try_parse", parseType=..., jobTag=...)**.
  - So “find” currently **includes** “parse” for the try_parse branch; there is no TO_PARSE state or separate parse step.

- There is **no** separate **parse_job_page()** entrypoint or batch “parse TO_PARSE companies” flow. Parse logic exists only inside find_job_page → _handle_try_parse_response.

### 2.3 Itemized scope change: find vs parse

1. **Split find and parse into two stages:**
   - **find_job_page** (or equivalent): On try_parse, **stop at** “we have a jobSite and we know it’s a job list page.” Save company with **state=TO_PARSE**, jobSite, and **do not** call parseJobTag or save parseType/jobTag.
   - **parse_job_page** (new): Takes companies with state=TO_PARSE and jobSite; runs parseJobTag (and validation); saves company_data and sets state=NEW (or CANNOT_PARSE_JOB_SITE / BOT_BLOCKED).

2. **Config task name:** Docs mention a task “parse_job_list”; code uses **parseJobTag**. Decide one name and use it in config and issues (e.g. parseJobTag everywhere or introduce parse_job_list and migrate).

3. **Batch processing:** Feature 4 runs on TO_WATCH → find only → TO_PARSE/NO_JOBS/NO_JOB_SITE. Feature 5 runs on TO_PARSE → parse only → NEW/CANNOT_PARSE_JOB_SITE/BOT_BLOCKED. Current code has no batch-by-state for company; that’s part of this scope.

4. **Backward compatibility:** Any caller that today expects find_job_page to return with jobTag/parseType already set will need to either (a) call find then parse in sequence, or (b) keep an optional “find+parse in one call” path that we explicitly document as combined mode.

---

## 3. Soundness assessment

### 3.1 Alignment with ASTRAL_CODE_RULES

- **Layers:** Splitting find vs parse keeps **core** as orchestration (find_job_page, parse_job_page), **data** as persistence (save_company, batch locking, allowed states), **config** as single source for state lists and response_type_to_state (and any new company-state machine). That matches the proposed structure.
- **Config-driven behavior:** Extending config with company states and transitions (and optionally prefilter semantics) fits “config owns rules; core/data use them.”
- **Data layer:** Adding company states and batch_id (and prefilter fields) in the DB, with validation in the data layer and no business logic there, is consistent with the rules.
- **Core:** find_job_page and parse_job_page as distinct entrypoints improve single responsibility: one “discover jobSite,” one “produce parsing config.” Each can be tested and called independently.

So the **direction** of the scope (company state machine + find/parse split) is **sound** with ASTRAL_CODE_RULES.

### 3.2 General engineering perspective

- **State machine explicitness:** Defining allowed company states and transitions in one place (config + maybe a small doc) reduces bugs and makes the pipeline easier to reason about and to extend (e.g. retry rules for BOT_BLOCKED).
- **Separation of find vs parse:**  
  - **Re-run parse without re-finding:** Fix parsing (e.g. prompt or selector logic) and re-run parse on TO_PARSE companies without re-crawling.  
  - **Clearer failure handling:** NO_JOB_SITE vs CANNOT_PARSE_JOB_SITE are different problems; splitting find and parse makes that visible in state and in code.  
  - **Batch and cost control:** Parse can be run in batches (e.g. nightly) on all TO_PARSE; find can be run on TO_WATCH. Clear state boundaries make this easier.
- **Risk:** The current “find then immediately parse on try_parse” is a single atomic step. Splitting changes behavior for callers that assume one call returns a “ready for Gazer” company. Mitigation: document the new contract, and optionally keep a “find_and_parse” wrapper that does find then parse for the same company so existing scripts can opt in without rewriting.

**Conclusion:** The scope implied by the issues (company state machine + find vs parse split) is **sound** from an engineering perspective: clearer pipeline, better testability, and more flexible batching and retries. The main work is implementing the state set and batch locking, then refactoring find_job_page to stop at TO_PARSE and adding parse_job_page plus optional combined wrapper.

---

## 4. Summary table

| Area | Current code | Feature-issue scope | Scope change (itemized above) |
|------|--------------|---------------------|---------------------------------|
| Company state | new, fix, watch, active, ignore, test only | imported → website_found → TO_WATCH → TO_PARSE → NEW (+ failure states) | §1.3: extend states, add fields, config, batch locking, migration |
| find_job_page | Discovery + parse on try_parse (saves new + jobTag) | Discovery only; saves TO_PARSE (or NO_JOBS / NO_JOB_SITE) | §2.3: find stops at TO_PARSE; no parseJobTag in find |
| parse_job_page | Only inside _handle_try_parse_response | Standalone step on TO_PARSE → NEW / CANNOT_PARSE / BOT_BLOCKED | §2.3: new parse_job_page entrypoint; batch on TO_PARSE |
| Batch locking (company) | None | batch_id, claim/release by state | §1.3 (4), §2.3 (3) |

This file can live in `docs/linear-imports/` and be updated as implementation decisions are made (e.g. final state list, task naming, backward-compatibility strategy).

---

## 5. Feature 4 (Locate Company Job Page) implementation status

- **find stops at TO_PARSE:** Implemented. try_parse path saves TO_PARSE and job_site only; no parseJobTag in find.
- **Config:** Task keys renamed to find_job_site, vet_job_site; find_job_page_max_depth and locate_job_page_input_state added.
- **Batch CLI:** src/cli/locate_job_page.py — claim batch by state from config, await find_job_page per company, release in finally.
