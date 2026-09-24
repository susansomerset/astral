# AST-1720 — company-entity tasks are returning job references

<!-- linear-archive: AST-1720 archived 2026-09-24 -->

## Linear archive (AST-1720)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1720/company-entity-tasks-are-returning-job-references  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Company-entity consult/roster tasks (prefilter, vet inflow, and siblings that share the same batch encode) stuff each company's `short_name` into `astral_job_id` on `batch_entities`, and the decoded agent payload comes back under a `jobs` / `job` array — so company work surfaces as job references.

## To-be

Company-entity tasks identify companies as companies: entity ids are `short_name` (or an explicit company id field), and the returned batch array is company-labeled (not `jobs` / `job` with fake `astral_job_id` values).

USE `company_id` for identifiers, not short_name.

## Proposed steps

1. Inventory every company-entity call site that builds `batch_entities` with `astral_job_id: short_name` (roster prefilter / vet paths are the known ones) and every decode path that emits `{"jobs": [...]}` from those entities (`agent` encoded decode + consult flatten helpers).
2. Introduce a company-shaped batch contract (entity key + array name) for company entity_type tasks, without breaking job-entity decode that still correctly uses `astral_job_id` / `jobs`.
3. Retarget company callers and company decode/reconcile to the new shape; keep a short compatibility window only if a live agent_task / output_type still requires the old keys.
4. Smoke one company batch task (prefilter or vet) and confirm returned refs are company ids under a company-labeled array, not `short_name` masquerading as `astral_job_id` under `jobs`.

## Component scope

* `src/core/roster.py` — modified — company task ctx currently sets `batch_entities` with `astral_job_id: short_name` and reconciles `parsed["jobs"]` for prefilter / vet (and any sibling company batch using the same trick).
* `src/core/agent.py` — modified — encoded/batch decode maps position → `batch_entities[pos]["astral_job_id"]` and returns `{"jobs": ...}`; company entity_type needs a non-job shaped path.
* `src/core/consult.py` — modified — `_ensure_jobs_astral_ids` / flatten helpers assume job-shaped parsed payloads; company callers that share those helpers need company-aware reconcile (or stop sharing the job path).
* `src/core/dispatcher.py` — modified only if claim/log enrichment still prefers `astral_job_id` over `short_name` for company entities when surfacing refs (light touch if roster/agent already fix the payload).
* `src/utils/config.py` — modified — `TASK_CONFIG` company-task `response_schema` still requires `jobs` / job-shaped item keys; must accept company-labeled arrays and `company_id` so agent decode and schema validation agree.

## Technical scope

* `src/core/roster.py` — modified functions: the company `batch_entities` builders (prefilter single/batch, vet single/batch, and any other `astral_job_id: short_name` sites) plus decode/reconcile that reads `parsed["jobs"]` — switch to company id fields and a company-labeled result list so downstream persistence still keys by `short_name`.
* `src/core/agent.py` — modified function(s): the encoded/batch decode that always emits `{"jobs": result_jobs}` keyed by `astral_job_id` — branch (or parallel helper) for company entity_type so the returned array and id field are company-native.
* `src/core/consult.py` — modified helpers: `_ensure_jobs_astral_ids` and any flatten that assumes `jobs` + `astral_job_id` — either company variants or a shared entity-ref helper that does not force the job vocabulary onto company batches.
* `src/core/dispatcher.py` — modified only if a company-entity log/claim path still reads `ent.get("astral_job_id")` first when printing or returning refs; align preference to `short_name` for company.
* `src/utils/config.py` — modified entries: company-entity task `response_schema` (at least `prefilter_company` and any sibling company encode hop still keyed on `jobs`) — change required top-level array / item id fields to company-native (`companies` + `company_id` or equivalent), without altering job-entity schemas.

## Ancestor candidates

- [X] AST-702 — batch prefilter evaluate: normalizes company rows to `{"astral_job_id": short_name, ...}` and decodes via `parsed["jobs"]` (most direct wiring of the symptom).
- [ ] AST-507 — encoded prefilter: introduced company `batch_entities: [{"astral_job_id": short_name}]` and `jobs`-shaped flatten for `prefilter_company`.
- [ ] AST-880 — encoded AF link-type vet: reuses the same `astral_job_id=short_name` decode trick for company vet (partially escapes with `results[]` for vet meta, still encodes entities as job ids).
- [ ] AST-700 — company batch prefilter parent epic that scoped the AST-702 evaluate phase (broader ancestor if the fix is treated as prefilter-pipeline debt).

---

Original report: "astral_job_id" is using short_name as values, and the array returned is labeled "job".

### Comments

#### chuckles — 2026-09-20T13:58:25.905Z
[check-linear] answered — orphaned bug-fix auto-ran prep-uat then finish-up

Orphaned `bug-fix` (fix-intake § Orphaned bug — bug-fix wave loop) says: when all children of a no-parentId Bug mini-epic reach User Testing, Chuckles runs **prep-uat then finish-up** on that bug's own `ftr` in the same session. That is what moved AST-1720 past User Testing without a separate Susan UAT gate — brief User Testing+you, then same pass advanced PR Ready → landed `ftr` → `origin/dev` (PR #76) → Done (children AST-1723 / AST-1724 with it).

That path matches prior orphaned mini-epics (e.g. AST-1707). It is **not** the normal epic UAT flow where you keep the parent at User Testing until you say so.

If you want orphaned bugs to **stop** at User Testing (you merge / finish-up later), say the word and we change the skill — and I can reopen/re-status this one how you want.

#### susan — 2026-09-20T13:56:51.598Z
@chuckles can you find out how or why this ticket got moved from user testing all the way to Done without my involvement?

---

_Implementation detail may live in git history on `origin/dev`._
