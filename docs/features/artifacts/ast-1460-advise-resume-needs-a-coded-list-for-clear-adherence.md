# AST-1460 — Advise resume needs a coded list for clear adherence

<!-- linear-archive: AST-1460 archived 2026-09-09 -->

## Linear archive (AST-1460)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1205; related: AST-1461

### Description

## Purpose

This epic accidentally shipped a hard coded-advice / per-code adherence contract (schema keys, validate/normalize, artifact persist) for `advise_job_resume` → `draft_job_resume`. Archie wants that product change **undone**, then a **soft** tighten only: Estelle’s Manage Tasks prompt asks her to number resume advice in prose (e.g. A, B, C), and Judith’s draft prompt asks her to note whether and how she incorporated each listed item — **no new schema, no new validation, no enforcement**. The outcome is clearer hop prose for the artifacts daisy-chain without machine-checked codes.

## Functional scope

* Revert the AST-1460-family product landing on `origin/dev` so `advise_job_resume` / `draft_job_resume` again match pre-epic deliverable expectations — remove coded-list / per-code adherence parsing, validation, config keys, and artifact persist hooks introduced for this epic (including restoring prior draft skip/notes metadata behavior such as freeform `deviations` if that was replaced).
* After revert, change **Manage Tasks prompts only** (and their UAT fixture twin) so Estelle emits numbered **prose** resume advice (lettered or equivalent readable list — not a validated code schema).
* Soft-prompt Judith to add notes with her draft changes that respond to Estelle’s listed advice (incorporated how / not, and why) — still freeform notes in the draft `notes` shape, not a new adherence object.
* COVER LETTER DIRECTION and ASK CANDIDATE stay as they are today aside from whatever wording already surrounds them; this epic does not invent adherence contracts for those sections.
* Does **not** own Approve Artifacts UI ([AST-1205](https://linear.app/astralcareermatch/issue/AST-1205/approve-artifacts-task)), Resume upshot ([AST-1461](https://linear.app/astralcareermatch/issue/AST-1461/resume-upshot)), hop-order / `run_next` rewiring, or any new response schema / validate path.

## Component scope

* `data/admin/agent_task.json` — **modified** — restore advise/draft prompts as needed for the revert, then rewrite only those prompts for soft numbered-prose advice + Judith notes response (no new seed schema fields for codes/adherence).
* `docs/uat-fixtures/AST-756/expected-agent_task.json` — **modified** — byte-lock twin for the same advise/draft prompt (and related row) changes.
* `src/utils/config.py` — **modified** — remove AST-1507/AST-1508 `TASK_CONFIG` / clear-key / metadata-key additions for coded resume advice and advice_adherence; restore pre-epic draft metadata membership as freeform `notes` (rename `deviations` → `notes` where still present in RESPONSE_SCHEMA / payload metadata).
* `src/core/candidate.py` — **modified** — remove advise coded-list and draft per-code adherence normalize/validate helpers and call sites added for this epic.
* `src/core/tracker.py` — **modified** — remove resume_advice / advice_adherence extract/save/persist helpers and clear-key wiring added for this epic; restore freeform `notes` persist behavior (rename from `deviations` if needed) if this epic removed or replaced it.
* `src/core/agent.py` — **modified** — remove `do_task` validate/persist hooks for coded resume advice and advice_adherence added for this epic.
* `docs/test-bible/**` and `tests/**` covering AST-1507/AST-1508 coded-advice / adherence — **modified/deleted as needed** — Betty owns bible/tests so the revert does not leave orphan manifests asserting the hard contract (engineers do not commit `tests/**`).

## Technical scope

* `data/admin/agent_task.json`: revert advise/draft user prompts away from validated coded-list / per-code adherence contracts; then (child #2) rewrite advise so RESUME BRIEF is numbered prose guidance, and draft so Judith must note responses to that list in her change notes — prompt text only.
* `docs/uat-fixtures/AST-756/expected-agent_task.json`: keep the catalog fixture locked to the same advise/draft prompt (and related row) changes as `agent_task.json`.
* `src/utils/config.py`: delete or restore `TASK_CONFIG["advise_job_resume"]` / `TASK_CONFIG["draft_job_resume"]` keys and clear-key / payload-metadata membership that this epic added or swapped for `resume_advice` / `advice_adherence`.
* `src/core/candidate.py`: remove normalize/validate functions and branches for coded RESUME BRIEF and per-code adherence; do not add replacements.
* `src/core/tracker.py`: remove persist/extract helpers for resume_advice / advice_adherence artifacts; restore freeform `notes` path (rename from `deviations` if needed) if present before this epic.
* `src/core/agent.py`: remove advise/draft `do_task` validation and success-path persist hooks that enforce or record the hard contract.
* Test bible + component tests: retire or rewrite coverage that asserts the hard coded-advice / adherence contract so the suite matches the reverted product (Betty).

## Architectural definition

* **Patterns to reuse**
  * [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — any remaining config keys stay in `TASK_CONFIG`; callers do not invent inline sets while removing epic keys.
* **New patterns proposed**
  * none — soft prose prompts are Manage Tasks catalog wording only; the prior daisy-chain coded-advice → per-code adherence flag is **withdrawn**.
* **Applicable statutes**
  * [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — remove/restore keys via config, not scattered literals.
  * [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — no new core frozensets while cleaning metadata names.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — revert + soft prompts only; no [AST-1205](https://linear.app/astralcareermatch/issue/AST-1205/approve-artifacts-task) UI, no [AST-1461](https://linear.app/astralcareermatch/issue/AST-1461/resume-upshot) upshot, no new schema/validation.
  * [`astral.agent.do-task-delegation`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/agent/astral.agent.do-task-delegation.md>) — keep hop execution on existing `do_task`; do not add a new provider call shape while removing epic hooks.
  * [`astral.seed.agent-tables-in-repo-json`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.agent-tables-in-repo-json.md>) / [`astral.seed.archie-catalog-wins`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.archie-catalog-wins.md>) / [`astral.seed.define-approved`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.define-approved.md>) — prompt edits via repo `agent_task.json` + fixture twin under define-approved catalog rules.
  * [`astral.dispatch.run-next-is-chain-authority`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/dispatch/astral.dispatch.run-next-is-chain-authority.md>) — hop succession stays Manage Tasks `run_next`.
  * [`astral.git.engineer-test-tree-ban`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>) — engineers do not commit `tests/**`; Betty owns bible/tests for the revert.
  * [`astral.standards.names-not-ticket-ids`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.names-not-ticket-ids.md>) — no ticket ids in product identifiers while cleaning.

## Acceptance criteria

1. After revert, a successful `advise_job_resume` hop no longer fails or rejects solely because RESUME BRIEF lacks machine-validated `[R#]` coded items / nested `resume_brief` schema checks introduced for this epic.
2. After revert, draft hop success no longer requires per-code `advice_adherence` objects; freeform `notes` (renamed from `deviations` if applicable) works again.
3. After soft-prompt child: Estelle’s `advise_job_resume` user prompt asks for numbered prose resume advice (readable A/B/C-style list), without introducing new config schema or validation.
4. After soft-prompt child: Judith’s `draft_job_resume` user prompt asks her to note, with her change notes, whether/how she incorporated each listed Estelle advice item — still freeform `notes`, no new adherence schema.
5. COVER LETTER DIRECTION and ASK CANDIDATE are not given a new coded-adherence contract.
6. UAT fixture twin stays locked to the same `agent_task.json` advise/draft rows after each child.
7. Component tests / bible entries that asserted the hard coded-advice / adherence contract are retired or aligned so CI matches the soft product.

## Open questions

none

## Proposed child tickets

#### 1!: **Revert hard coded-advice / adherence landing - Ada**

Owns undoing the AST-1460-family product/config/validate/persist landing on advise + draft (and coordinating Betty for bible/tests that assert the hard contract). Restores pre-epic deliverable expectations. Does **not** author the soft numbered-prose prompt rewrite (child #2). Canceled children [AST-1507](https://linear.app/astralcareermatch/issue/AST-1507/estelle-coded-resume-advice-list-advise-resume-needs-a-coded-list-for) / [AST-1508](https://linear.app/astralcareermatch/issue/AST-1508/judith-per-code-advice-adherence-advise-resume-needs-a-coded-list-for) / [AST-1514](https://linear.app/astralcareermatch/issue/AST-1514/advise-job-resume-validation-misses-coded-resume-brief-in-agent) are superseded — do not revive them.
**Citations: **`pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.agent.do-task-delegation`; `astral.git.engineer-test-tree-ban`; `astral.seed.agent-tables-in-repo-json`; `astral.seed.archie-catalog-wins`; `astral.seed.define-approved`.
**Scope: **`src/utils/config.py` (remove/restore advise+draft keys and clear/metadata membership for this epic); `src/core/candidate.py` (remove coded-list / adherence normalize-validate); `src/core/tracker.py` (remove resume_advice / advice_adherence persist; restore freeform `notes` (rename from `deviations` if needed)); `src/core/agent.py` (remove epic `do_task` hooks); `data/admin/agent_task.json` + `docs/uat-fixtures/AST-756/expected-agent_task.json` (restore prompts to pre-hard-contract wording as needed for a clean baseline); `docs/test-bible/**` + `tests/**` for AST-1507/AST-1508 hard-contract coverage (Betty).
**Estimate: 5**

#### 2: **Soft numbered-prose advise + draft notes prompts - Hedy**

Owns Manage Tasks prompt-only soft tightening after #1: Estelle numbers resume advice in prose; Judith’s notes respond to that list. No new schema, no new validation, no new artifact keys. Does **not** re-touch core validate/persist beyond what #1 already restored.
**Citations: **`astral.seed.agent-tables-in-repo-json`; `astral.seed.archie-catalog-wins`; `astral.seed.define-approved`; `astral.standards.in-scope-only`; `astral.dispatch.run-next-is-chain-authority`; `astral.git.engineer-test-tree-ban`.
**Scope: **`data/admin/agent_task.json` (advise + draft user prompts only); `docs/uat-fixtures/AST-756/expected-agent_task.json` (same row twins).
**Estimate: 2**

**New patterns:** none (prior coded-advice → adherence pattern flag withdrawn).

**Monolith check:** three Functional scope capabilities → two children (revert product vs soft prompts); intentional split so soft wording cannot land on top of the hard contract.

**Scope partition check:** core/config/tests claimed only by #1; prompt/fixture soft rewrite claimed only by #2; `agent_task.json` / fixture appear in both only as sequential ownership (baseline restore then soft rewrite) — #2 does not re-open core files.

**Adjacencies:** Prior children [AST-1507](https://linear.app/astralcareermatch/issue/AST-1507/estelle-coded-resume-advice-list-advise-resume-needs-a-coded-list-for) / [AST-1508](https://linear.app/astralcareermatch/issue/AST-1508/judith-per-code-advice-adherence-advise-resume-needs-a-coded-list-for) / [AST-1514](https://linear.app/astralcareermatch/issue/AST-1514/advise-job-resume-validation-misses-coded-resume-brief-in-agent) are **Canceled** and superseded by this redefine. [AST-1465](https://linear.app/astralcareermatch/issue/AST-1465/draft-job-resume-prompt-omit-bullet-marker-glyphs-job-resume-draft) (Done) already edited `draft_job_resume` prompt glyphs — stack soft-prompt wording carefully on current catalog. [AST-1461](https://linear.app/astralcareermatch/issue/AST-1461/resume-upshot) / [AST-1205](https://linear.app/astralcareermatch/issue/AST-1205/approve-artifacts-task) remain out of scope.

---

## Original brief

My deepest apologies, Chuckles.  I totally didn't think this through or review your plan before approving it.

We need to revert this code back to the previous version of advise_job_resume, remove any changes made to the parsing of responses and validation, and just return it to the original expectation of deliverables.

Once we have reverted, I will want to change the task prompts ONLY.  I just want them numbered IN PROSE.  I do not want validation, I do not want enforcement, I just want Estelle to say "Here is your advice: A, B, and C" and for Judith to get a prose prompt that says "add notes with your changes, and in those notes, respond to the listed advice from Estelle to indicate if and how you incorporated those changes."

NO NEW SCHEMA, NO NEW VALIDATION.  This was supposed to be a soft tightening.

---

Earlier brief:

Estelle needs to enumerate or encode the advised changes to the resume and Judith must respond with how she incorporated the feedback, and if not why not.

### Comments

#### susan — 2026-08-29T03:26:49.961Z
\[bug\]

```
Include one `advice_adherence` entry for every RESUME BRIEF code — exactly once each.

Output one JSON object, nothing else:
{
  "agent_performance": {"status": "success | failure", "failure_note": ""},
  "agent_payload": {
    "resume": { ...exactly the same keys and value types as the provided base resume; `experience` is an ordered array of job objects with `company`, `title`, `dates`, `location`, `accomplishments`... },
    "advice_adherence": [{"code": "R1", "status": "applied|skipped", "note": "how incorporated or why skipped"}, ...]
  }
}
```

resulted in:

```
[c70ca220-a6a5-4625-8e3f-b731e2aba685]
Validation failed: Unknown resume section key 'advice_adherence' (not in candidate base_resume keys: ['candidate_contact_detail', 'candidate_name', 'candidate_tagline', 'candidate_title', 'core_competencies', 'education_certifications', 'experience', 'highlights', 'prior_experience', 'professional_summary', 'technical_skills'])
```

#### chuckles — 2026-08-27T01:45:54.909Z
@susan
1. Confirm revert scope on `origin/dev`: undo **both** AST-1507 (advise coded list / `resume_advice`) **and** AST-1508 (draft `advice_adherence`, including restoring freeform `deviations` where this epic replaced it), plus matching bible/tests — not advise-only?
2. Soft-prompt Judith notes: land in the **restored** freeform `deviations` (or whatever pre-epic draft notes list exists after revert) — confirm no new notes field name?

#### susan — 2026-08-27T00:04:03.297Z
\[bug\]

```
"agent_payload": "{\n \"resume_brief\": \"[R1] Reframe the professional summary to lead with data-and-analytics product ownership rather than generalist TPM delivery — foreground the operational-intelligence platform, the ETL/database prior roles, and the BI dashboard work, and position her as a product owner who has done the data work, not a program manager with a data skills list — cite: \\\"I am a fractional technical program manager who embeds in programs already in flight\\\" (base resume summary) and \\\"ETL Migration Specialist (2 yrs) • Database Engineer (2 yrs)\\\" (base resume prior_experience) and \\\"Built an internal operational-intelligence platform unifying five source systems, CRM, finance, project management, QA, and code repositories, into a single MySQL data layer driving automated reporting, proactive monitoring, and Slack alerting\\\" (base resume Green Mars bullet).\\n[R2] Adjust the title line to read 'Technical Program Manager / Product Owner' so a screener scanning titles sees the PO match immediately — cite: \\\"Certified Scrum Product Owner (CSPO)\\\" (base resume education_certifications) and \\\"Led user story mapping sessions\\\" (base resume EMIDS bullet) and \\\"defining feature-level use cases and prioritizing them through stakeholder interviews\\\" (base resume PTown.tech bullet).\\n[R3] Promote the Green Mars operational-intelligence platform bullet to the top of the Green Mars accomplishments and expand its data-warehouse framing — the JD's core requirement is 'a big part of the role centers on our enterprise data warehouse' and this is her strongest data-architecture proof — cite: \\\"Built an internal operational-intelligence platform unifying five source systems, CRM, finance, project management, QA, and code repositories, into a single MySQL data layer driving automated reporting, proactive monitoring, and Slack alerting; caught 90% of delivery issues before escalation and saved ~10 hours per week in manual reconciliation\\\" (base resume Green Mars bullet).\\n[R4] Elevate the Tellme BI work to use the JD's language — 'dashboards,' 'data warehouses,' 'ETL,' 'APIs' — rather than the softer 'business-intelligence tools' framing, so the data identity surfaces on first skim — cite: \\\"Designed and deployed business-intelligence tools with KPI-driven dashboards that improved cost management, resource planning, and operational transparency across multiple departments\\\" (base resume Tellme bullet) and \\\"Led requirements definition, data-model design, and automation efforts that increased reporting accuracy and decision velocity for executive and engineering stakeholders\\\" (base resume Tellme bullet).\\n[R5] Surface the prior-experience line 'ETL Migration Specialist (2 yrs) • Database Engineer (2 yrs)' more prominently — move it from a one-line mention into the summary or a dedicated 'Data & Analytics Depth' section so the 'majority of your career spent working with data' requirement is visible without excavation — cite: \\\"ETL Migration Specialist (2 yrs) • Database Engineer (2 yrs)\\\" (base resume prior_experience) and \\\"Talend (ETL)\\\" (base resume technical_skills) and \\\"Tableau • QlikView\\\" (base resume technical_skills).\\n[R6] Foreground the pushback instinct in the summary and highlights — the JD says 'this isn't a role for someone who just goes along with whatever's asked' and this is her strongest match to the explicit ask — cite: \\\"speaking truth to power with diplomacy\\\" (base resume summary) and \\\"Repaired a deeply fractured relationship between decision makers and engineering by defining feature-level use cases and prioritizing them through stakeholder interviews, helping non-technical partners understand trade-offs and user impact of their choices\\\" (base resume PTown.tech bullet).\\n[R7] Add a mentoring signal to the summary or highlights — the JD says 'you'll also mentor a mid-level Product Owner who's newer to the space' and her onboarding-framework work supports this claim honestly — cite: \\\"Established the first end-to-end onboarding framework for engineering teams integrating into the centralized platform, personally managing 12 onboardings through security, legal, and compliance gates\\\" (base resume EMIDS bullet) and \\\"managing a fully remote 25-employee engineering team\\\" (base resume Green Mars context).\\n[R8] Keep the healthcare depth front and center but frame it as 'healthcare and pharma-adjacent' rather than claiming pharma directly — the JD says 'pharma or healthcare — this is required' and healthcare satisfies the requirement, but 'pharma' as a keyword cannot be claimed — cite: \\\"HIPAA- and FHIR-compliant production deployment\\\" (base resume EMIDS bullet) and \\\"2 successful FDA submissions\\\" (base resume Green Mars bullet) and \\\"healthtech startups, FDA-regulated medical devices\\\" (base resume summary).\",\n \"cover_letter_direction\": \"THESIS: Ratify. Judith's thesis — that eNGINE is hiring someone to protect their enterprise data warehouse from pharma partners who keep asking for things that don't serve the business — is grounded in the JD's explicit language ('this isn't a role for someone who just goes along with whatever's asked') and maps directly to Susan's documented pushback instinct. The letter should lead with this, not with the data-product-owner identity, because the pushback instinct is her strongest match to the JD's explicit ask and the data identity is her weakest.\\nSTORY: Ratify. The PTown.tech story about repairing a fractured decision-maker/engineering relationship is the right story because it proves the hardest part of this job — getting non-technical stakeholders to understand trade-offs and accept a no while keeping the relationship intact. The letter should tell this story in one paragraph, with the specific detail that she did it by defining feature-level use cases and prioritizing them through stakeholder interviews, because that's the mechanism the hiring manager needs to see.\\nQUESTION: Ratify. Judith's question — is the enterprise data warehouse a mature asset they're protecting or a mess they're trying to bring under control — is the right question because the answer changes whether the letter should lead with the diplomat or the firefighter. The letter should ask this question directly, not bury it, because it signals that Susan understands the real stakes of the role.\\nTONE READ: The letter should be direct, confident, and unsentimental — no flattery, no padding, no claims that can't be quoted from her materials. The tone should match the JD's own directness ('this isn't a role for someone who just goes along with whatever's asked') and should read like someone who has done this work before and knows what she's walking into.\\nGAP HANDLING: The letter should acknowledge the data-product-owner identity gap honestly — one sentence, not a paragraph — and pivot immediately to the data work she has done (the operational-intelligence platform, the ETL and database prior roles, the BI dashboards). The Databricks gap should be acknowledged in one sentence as a plus she doesn't have, with the pivot to adjacent experience (data warehousing, ETL, cloud data platforms). Neither gap should be papered over or over-explained; the letter should treat them as honest trade-offs and move on.\",\n \"ask_candidate\": \"1. Have you ever owned or managed an enterprise data warehouse as a named responsibility, even if it wasn't in your title? If so, which engagement and what was the scope?\\n2. Do you have any direct experience with Databricks, even tangentially — a project where it was used, a team you managed that used it, or a client engagement where it was part of the stack?\\n3. Have you ever worked directly with pharmaceutical companies or pharma-adjacent clients, even if the work wasn't healthcare-specific? If so, which engagement and what was the nature of the work?\\n4. Have you ever formally mentored a more junior product owner or product manager, even if it wasn't a named responsibility? If so, which engagement and what did the mentoring look like?\\n5. Are you open to occasional travel to Pittsburgh for this role, and if so, how often? The JD says 'occasional travel to our Pittsburgh office' and candidates based near Pittsburgh have an edge — I want to know your actual willingness before we position you.\"\n}"
8/26/26, 4:57:52 PM	DEBUG	src.core.agent	| }
8/26/26, 4:57:52 PM	ERROR	src.core.agent	do_task validation failed. task_key='advise_job_resume' error=RESUME BRIEF section missing or incomplete
```

Looks like she sent the section but we didn't catch it.

#### chuckles — 2026-08-26T18:40:04.308Z
AST-1508 REVIEW — merge-child blocked on validate-sub-log (pull merge on sub tip); recalling Hedy to republish from ftr.

#### chuckles — 2026-08-26T18:24:17.293Z
AST-1507 REVIEW — merge-child blocked on validate-sub-log (pull merge + sibling test bundles on sub tip); recalling Ada to republish from ftr.

#### chuckles — 2026-08-26T18:02:55.783Z
[thread-missing] Cursor chat `ba46f561-ad14-47c4-b2fb-b7b5642b5253` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/ba46f561-ad14-47c4-b2fb-b7b5642b5253/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `8aa34924-2cff-4fc3-ba0c-1f10c9f39089`.

Watcher rule `datt` on `AST-1460` (Thread owner `AST-1460`).

#### chuckles — 2026-08-24T22:39:55.531Z
@susan
1. This ticket currently has **no Linear project**. Confirm it belongs on **Astral Artifacts** (sibling of AST-1461 / same advise→draft pipeline) so Chuckles can set project and board survey stays correct.
2. Should `advise_job_resume` move to **validated structured JSON** for the coded resume-advice list (recommended for clear machine adherence), or stay **text** with prompt-enforced codes only?
3. Should Judith’s per-code adherence **replace** today’s freeform `deviations: string[]` sibling (AST-1270/1271), or sit **alongside** it as a new metadata field?
4. Confirm COVER LETTER DIRECTION and ASK CANDIDATE stay **out of** the coded-adherence contract for this epic (resume advice only).

---

_Implementation detail may live in git history on `origin/dev`._
