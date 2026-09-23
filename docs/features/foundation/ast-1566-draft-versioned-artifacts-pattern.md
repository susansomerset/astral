# AST-1566 — Draft versioned artifacts pattern

<!-- linear-archive: AST-1566 archived 2026-09-22 -->

## Linear archive (AST-1566)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1566/draft-versioned-artifacts-pattern  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

**Design stance:** Requirements-first from use cases — not grandfathering today's blob reads or coat-check paths. Circulatory-system pattern work; **no product code** in this epic.

**Susan 2026-09-01 (21:20):** Five `patt.artifact.*` pattern files, one Fable pass, all interdependent outputs from a single prompt. Child [AST-1567](https://linear.app/astralcareermatch/issue/AST-1567) holds system + task prompts (redrafted below).

### Pattern document structure (mandatory for all five files)

| § | Heading | Content |
| -- | -- | -- |
| **1** | **Abstract** | What the pattern is and why it exists |
| **2** | **Arc** | `2.n` lifecycle stages **before, during, after** — exemplify purpose |
| **3** | **Applications** | `3.n` when to apply |
| **4** | **Exceptions** | `4.n` when **not** to apply |
| **5** | **Implementation** | `5.n` rules, data definitions, architectural stipulations (today's SQLite platform; future refactors version the file) |

**Frontmatter: **`id`, `kind: pattern`, `scope`, `point` (match attached `patt.*` templates).

**Patterns MUST NOT:**

* List artifact **types/keys by name** (entity names as examples are OK).
* List configuration values that belong as keys in `config.py` / `ARTIFACT_CONFIG`.

### Five pattern files (deliverable)

| File | Purpose |
| -- | -- |
| `patt.artifact.catalog` | How artifact keys are managed; guidance for adding a new key (e.g. ticket "Support `candidate.artifacts.base_resume`" follows this pattern — **without** enumerating keys in the doc) |
| `patt.artifact.write-operative` | Write to `artifacts` table: artifact key + logical FKs (`entity_id`, `candidate_id`); correct `current` flag updates (`agent_task` retire+insert semantics) |
| `patt.artifact.read-operative` | Inputs: artifact key, `candidate_id`, `entity_id`, artifact key → direct table query (replaces abstracted `get_<entity>_data` json fetch for pinned rows) |
| `patt.artifact.read-current` | Inputs: artifact key (e.g. `artifacts.base_resume`), `candidate_id` → current content; **UI edit path** (serve read-current, persist via write-operative) |
| `patt.artifact.no-coat-check` | Anti-pattern: no lazy fetch-if-missing; missing data → component/state ingestion, not spaced LLM coat-check calls |

Draft output: `canon/directives/draft/` on `dev`. Template reference: four `patt.*` attachments on this ticket (`origin/claude-canon-revision`).

### Pass structure

| # | Ticket | Pass | Model | Status |
| -- | -- | -- | -- | -- |
| **1** | [AST-1567](https://linear.app/astralcareermatch/issue/AST-1567) | Draft all five `patt.artifact.*` files (brief prose) | **Fable** | **Discussion — Susan**; Todo + Chuckles when ready to run |
| **2** | *(optional)* | Red-team / enumeration | GPT-4.1/o3 + Gemini 2.5 Pro | After Susan approves drafts |

**Backlog (separate): **`patt.data.agent-data-slim-ref` — agent_data refs + RESPONSE only.

### Inputs (unchanged)

* Audits: [AST-1563](https://linear.app/astralcareermatch/issue/AST-1563), [AST-1564](https://linear.app/astralcareermatch/issue/AST-1564), [AST-1565](https://linear.app/astralcareermatch/issue/AST-1565).
* Grades carry runtime `artifact_id` for explainability; editable UI blobs versioned in `artifacts`; migration/backfill out of scope.

### Parent steps remaining

1. Susan reviews redrafted [AST-1567](https://linear.app/astralcareermatch/issue/AST-1567/outline-pass-versioned-entity-data-patterns) prompts → **Todo**, assignee **Chuckles** → Fable drafts five files in one session.
2. Susan approves drafts → optional red-team; land in `canon/directives/draft/`.
3. File backlog ticket for agent_data slim-ref.

## Done when

* Five draft `patt.artifact.*` files in `canon/directives/draft/` on `dev`.
* Susan sign-off on structure and interdependencies.
* Backlog ticket for agent_data slim-ref filed.
* No commits to `src/`.

## Risks / open questions

* **Fable slug** in Joan APIs — confirm at [AST-1567](https://linear.app/astralcareermatch/issue/AST-1567/outline-pass-versioned-entity-data-patterns) Todo.
* **Brevity gate** — elaboration/repetition across five files will blow context; prompts enforce terse canon.
* `ARTIFACT_CONFIG` lives in code/config, not in pattern prose — catalog pattern describes *process*, not key list.

---

## Original brief

Read the results of [AST-1563](https://linear.app/astralcareermatch/issue/AST-1563) , [AST-1564](https://linear.app/astralcareermatch/issue/AST-1564) , and [AST-1565](https://linear.app/astralcareermatch/issue/AST-1565) .

Then read the most recently updated pattern file in the canon/ folder, and synthesize a pattern that includes the following:

* all data entity content will point at the artifact_id that was current at the time of the execution, as a fk
* All content that is editable in the ui and stored in the '_data' json blob (strengths, base_resume, job_resume, like_rubric, job_cover_letter, etc.) are now versioned in the artifacts table
* Versioning works like it does for agent_task.
* Grades are saved with runtime artifact id's so that questions about why can be more clearly answered.
* 

Do not worry about data cleanup, that is handled separately.

Do not change the code.  Just establish the pattern.

### Comments

#### chuckles — 2026-09-01T21:23:22.996Z
[check-linear] Discussion — AST-1567 redrafted: five `patt.artifact.*` files, Fable single-pass, §1–§5 structure + system/task prompts in child Description (@susan review)

#### susan — 2026-09-01T21:20:56.150Z
The patterns files should be structured as :

§1 Abstract

§2 Arc

2.n lifecycle stages before, during and after the pattern to exemplify its purpose.

§3 Applications

3.n Cases of when to apply this pattern

§4 Exceptions

4.n Cases for when not to apply the pattern

§5 Implementation

5.n Specific implementation rules, data definitions and architectural stipulations that must be adhered to for the pattern to be consistently used and ratified.  This can be code-specific, component-specific, service-specific, as needed, and this is the section of the pattern document that may be amended over time as our platform evolves (e.g. how we do it today with SQLite database vs. a future Postgres server, we are only going to write for today's platform, and future platform refactors will create new versions of each related pattern file.

The patterns SHOULD NOT:

* list the artifact types by name.  Entities are okay, I think, to use as examples.
* list any configuration value that should be maintained as a key in config.py

Then, what we really need is five pattern files:

patt.artifact.catalog

Here we define how artifact keys are managed.  We do not list them in the pattern explicitly, we provide guidance for what it means to create a new artifact type, and how the code needs to be handled to adhere to the pattern.

This is the pattern that would be used for a ticket called "Support the candidate.artifacts.base_resume artifact", and follow the guidelines established int the pattern for how to complete the implementation of a new artifact key.

patt.artifact.write-operative

Here we make sure that every artifact is written to the artifacts table correctly, making sure the artifact key is identified with the logical FK's of entity id and candidate id, and how to make sure the current flag is correctly updated.

patt.artifact.read-operative

This will pass in the artifact key, the candidate id, the entity id (if the entity type is candidate, then this is the candidate_id again), and the artifact key.

This partially replaces "get\_<entity>\_data" from the original tracker/roster/candidate files, where the data can be fetched not by abstracting json but with a direct table query with the entity_id and the artifact_key (per the ARTIFACT_CONFIG list) as the two inputs.

patt.artifact.read-current

This would pass in an artifact key ("artifacts.base_resume") and the candidate ID, and return the current content from the artifacts table for that candidate ID and artifact key combination.

This is what we always use for editing content.  When the UI wants to edit a rubric, we serve it read-current, and write-operative whatever changes are made, if any.

patt.artifact.no-coat-check

We also need an anti-pattern for coat-check.  Coat check was once a handy mechanism to fetch-if-missing, but that is no longer how we run things.  If something needs fetching, there is a state that one of the core components will ingest and process, no more lazy fetches where the LLM calls get spaced out over time and we lose valuable cache windows.

@chuckles Please redraft the child record with a system prompt to explain what canon directives are, including patterns and statutes, and then a task prompt to produce these five pattern files as specified above.  I think Fable can just draft the files, themselves, they aren't very big, in the end.  But, encourage the agent to be brief.  Elaborations and repetitions will devastate the context windows.  Please make it clear to the agent in the system prompt that these outputs are used directly in engineering lifecycles for the software platform and agents will use them to decide how to implement a change where that pattern is relevant.  I still want all four outputs from one prompt because of the interdependencies, so make sure the task prompt explains that point.

#### chuckles — 2026-09-01T20:28:23.516Z
[check-linear] Discussion — four active `patt.*` templates from `claude-canon-revision` attached; AST-1567 outline pass will use that shape (Abstract / Arc / Canonical implementation / When this doesn't apply).

#### susan — 2026-09-01T20:27:09.470Z
@chuckles I don't want to muddy the child ticket, but we need to provide the structured outline making explicit reference to the structure of the recent patt. files from the claude-canon-revision branch.  Can you upload all four of those files to this ticket, please?

#### susan — 2026-09-01T18:59:08.394Z
Assign the new child to me in discussion mode and I'll passs it back to have you run it

#### chuckles — 2026-09-01T18:54:02.550Z
Fable for outline, Sonnet for prose — yes. Fable is the right “spatula” for scraping edges before we commit to canon prose; if Joan doesn’t expose Fable yet, **o3** or **Opus thinking** is the fallback for the same outline pass.

Description updated: child-ticket pass structure (outline → prose → optional red-team), Fable outline prompt embedded, runtime **read** (current-path pins) vs **write** (exact artifact_id) called out as separate outline sections, backlog ticket noted for agent_data slim-ref.

Next step when you move this to Todo: spawn **child 1** (outline pass only) with the Fable prompt in its Description.

#### susan — 2026-09-01T18:51:28.180Z
What would you think of using Fable for the first pass outline, then Sonnet for the prose?  This feels like I need the spatula to scrape the edges thinking through the pattern before we commit to prose.  Maybe we do a child ticket for each pass?  We are not following the traditional datt pattern but that's okay.

if not fable, what else would be best for deep thinking and contemplation of the various aspects to consider in the outline pass?

Let's start with a child ticket from this issue for the first pass outline and in that description proposed the system and task prompt and the model to use.

#### chuckles — 2026-09-01T18:25:14.557Z
Three-model workflow added to Description: **Sonnet** primary scribe, **GPT-4.1/o3** architecture red-team, **Gemini 2.5 Pro** enumeration sweep. **Canon scribe system prompt** is in the Description for Joan's APIs.

Also updated: outline-first gate before full prose, both patterns in one session, Estelle = surgical cache by id (freshen on conversation start), single rubric artifact_id per grade, canon on `dev` with directives/ layout. Your inline Risk answers folded in.

#### susan — 2026-09-01T18:24:12.844Z
Okay, @chuckles this looks pretty good, but I'm a little concerned about the calibration.  This pattern is going to be foundational to almost everything this platform does.  

it is not a body part.  It's the circulatory system, but it must be grounded in feasible architecture and code structure.  It's a very tall order.  

I just renewed us for more model use, so given the complexity of this task and its importance, I want you to talk about three llm models you would recommend we use to draft these patterns, and maybe draft a system prompt in this issue's description to be our canon scribe (we'll use Joan's APIs for her).

#### chuckles — 2026-09-01T17:14:35.376Z
Splitting into two draft patterns looks right: **`patt.data.versioning-entity-data`** (where editable bodies live + agent_task-style version history) and **`patt.data.entity-data-at-runtime`** (FK pins at execution, grade explainability, cache/latency rules for batch vs Contact Estelle). Audits inform the use-case matrix only — not grandfathered exceptions for today's direct blob reads.

Description changes: added **design stance** (requirements-first), **use-case matrix** (pipeline / UI / consult / Estelle), explicit **platform-performance** step (cache, memory, N+1, latency), **two-pattern draft** step replacing single-file assumption, and clarified that coat-check becomes artifact-resolution in target state. Risks updated for Estelle pagination and statute follow-ups.

Statutes deferred until pattern shape is stable — agree that's the right order.

#### susan — 2026-09-01T17:12:41.300Z
This is improtant and I'm not sure it's clear yet: do not treat the extant code as "approved exceptions" to this pattern.  Look at what is needed from each use case for entity data and plan the pattern accordingly. You may also see fit to draft multiple patterns, such as entity-data-at-runtime and versioning-entity-data.  

consider the elements of the platform as well, do take best advantage of cache as storage and managing memory, cpu load, latency etc. In your architectural design for the pattern.

Also of note: the code is not written yet for this, but Astral Contact (Estelle agent via slack) will need to be able to read and answer questions about a candidate, their company roster and their jobs in any state, in real time with the slack user (our candidate).

this may end up involving one or more statutes about data management, but let's start with the drafted pattern(s).

Please reply to this comment with your thoughts as well as noting what you changed in the description to reflect it.

#### chuckles — 2026-09-01T17:05:38.949Z
On **`origin/claude-canon-revision`**, active patterns are under **`canon/directives/active/`** — four files, all from the same 2026-08-31 reorg commit (no single file is newer than the rest):

- `patt.entity.batch-criteria.md`
- `patt.entity.batch-processing.md`
- `patt.task.daisy-chain.md`
- `patt.task.dispatch-retry.md`

Best structural template for the versioned-artifacts pattern: **`patt.entity.batch-criteria.md`** (Abstract / Arc / Canonical implementation / When this doesn't apply). New work on that branch drafts into **`canon/directives/draft/`**. Execution plan in Description updated to use this tree instead of legacy `canon/patterns/` on `dev`.

#### susan — 2026-09-01T16:59:10.630Z
@Chuckles I recently did some work on a different branch.  Can you find the latest pattern file on the origin Claude-canon-revision? In a folder called active, I believe.

---

_Implementation detail may live in git history on `origin/dev`._
