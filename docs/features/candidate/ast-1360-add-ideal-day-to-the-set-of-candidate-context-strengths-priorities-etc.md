# AST-1360 — Add "ideal_day" to the set of candidate context (strengths, priorities, etc.)

<!-- linear-archive: AST-1360 archived 2026-08-31 -->

## Linear archive (AST-1360)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidates already carry prose context (strengths, priorities, deal breakers, backstory) that shapes how Astral judges jobs. Ideal day is a missing peer: what a thriving workday looks like for this person. Without it, DO/LIKE/Job Description rubrics and Topic Menu outputs under-weight day-to-day fit. This epic adds `ideal_day` as first-class candidate context and wires it into the craft and Topic Menu surfaces that already consume the rest of that set.

## Functional scope

* **Context element.** Candidates can store an `ideal_day` context field — peer of strengths / priorities / deal breakers / backstory — as editable candidate prose with a prompt token so downstream tasks can read it.
* **Candidate edit surface.** Candidates (and admin) can view and edit Ideal Day the same way they edit the other gated-style context lists (dedicated Candidate nav entry + save path).
* **Craft rubric prompts.** Job Description, DO, and LIKE craft rubric prompts include Ideal Day alongside the existing context tokens so newly crafted rubrics can condition on day-to-day fit.
* **Topic Menu deliverables.** The closed Topic Menu informs / deliverables vocabulary includes `ideal_day`, so Estelle may invent topics that write toward Ideal Day, and preamble confirm/generate packets may see and patch that field when allowed by the existing whitelist pattern.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — extend `CANDIDATE_LIBRARY_CONFIG`, `TOKEN_SOURCES`, `TOPIC_MENU_CONFIG` / `TOPIC_MENU_GEN_CONFIG`, shapes/nav from config; do not scatter key names.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — library keys, tokens, informs catalog, packet/patch allowlists live in config.
  * `astral.standards.no-hardcoded-sets` — no inline ideal_day allowlists outside config.
  * `astral.layers.ui-config-driven-business-logic` — Candidate Ideal Day UI follows shapes/nav config, not ad-hoc field logic.
  * `astral.standards.in-scope-only` — only Job Description / DO / LIKE craft surfaces named here; no drive-by prompt edits.
  * `astral.seed.archie-catalog-wins` / `astral.seed.agent-tables-in-repo-json` — craft prompt text changes go through agent_task seed discipline.
  * `astral.standards.debug-contract-gated` — if save/merge paths with `debug=` are touched, Style D found/recorded lines.
  * Universal active set applies to product children at plan/review time (`orch.pipeline.plan-is-bible`, git/role universals, etc.).

## Boundaries

* Does **not** change GET, Job List, Meteorite, company-prefilter, or resume-craft prompts unless Susan expands scope later.
* Does **not** invent a new intake interview phase beyond Topic Menu informs + existing preamble confirm/generate allowlists.
* Does **not** change candidate state machine transitions or dispatch chains.
* Ideal Day **does** join the context completeness gate with strengths / priorities / deal_breakers / backstory (Susan: yes).
* Does **not** migrate or backfill prose into Ideal Day for existing candidates (empty until edited or Topic Menu writes it).
* Must not break existing Strengths / Priorities / Deal Breakers / Backstory edit, token resolve, or Topic Menu informs validation.

## Acceptance criteria

1. A candidate can save non-empty Ideal Day prose under candidate context and read it back after reload.
2. Ideal Day is reachable from Candidate navigation (label/path peer of Strengths) and editable with the same save semantics as the other context list pages.
3. Prompt token for Ideal Day resolves from `context.ideal_day` (empty string when unset).
4. Craft tasks for Job Description, DO, and LIKE rubrics include Ideal Day in their candidate-context prompt material (same class of inclusion as Strengths/Priorities today).
5. Topic Menu closed informs catalog accepts `ideal_day`; a topic may list it; generation/confirm allowlists treat it consistently with other context informs targets.
6. Context completeness gate requires Ideal Day populated alongside strengths / priorities / deal_breakers / backstory.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **Ideal Day library + token - Ada**

Add `ideal_day` to the candidate context library vocabulary, prompt token map, DATA_SHAPES / related config inventories, and candidate data-model docs so the field is a first-class peer of strengths/priorities. Does **not** own Candidate page UI (#2), Topic Menu catalog (#3), or craft prompt text (#4).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.
**Estimate: 2**

#### 2: **Ideal Day Candidate edit surface - Hedy**

Ship Candidate nav + Ideal Day edit page (peer of Strengths/Priorities) wired to the library key from #1. Does **not** own Topic Menu informs (#3) or craft prompts (#4). After #1.
**Citations:** `pattern.config.config-block`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`.
**Estimate: 2**

#### 3: **Topic Menu informs + Estelle allowlists - Katherine**

Extend Topic Menu closed informs / deliverables catalog with `ideal_day` and align Estelle preamble confirm/generate packet + patch allowlists so Ideal Day can be summarized, revised, and targeted by topics. Does **not** own craft rubric prompt text (#4). After #1.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.agent.do-task-delegation`.
**Estimate: 2**

#### 4: **Wire Ideal Day into JD / DO / LIKE craft prompts - Ada**

Update Job Description, DO, and LIKE craft rubric agent_task prompts (and any shared cache/context blocks those three use) so Ideal Day is included with the other candidate context tokens. Does **not** touch GET/joblist/meteorite craft prompts. After #1.
**Citations:** `astral.seed.archie-catalog-wins`; `astral.seed.agent-tables-in-repo-json`; `astral.standards.in-scope-only`.
**Estimate: 2**

---

## Original brief

Add a context element for ideal_day, and include it in the Job Description, DO and LIKE craft rubric prompts, as well as the output for the topic menu "deliverables".

### Comments

#### chuckles — 2026-08-14T19:08:48.091Z
AST-1367 REVIEW — merge dry-run blocked vs ftr; recalling Katherine for conflict on data/admin/agent_task.json + src/utils/config.py.

#### ada — 2026-08-14T18:59:11.002Z
🛑 Stage 0 blocked: TOKEN_SOURCES["IDEAL_DAY"] missing after sync-child

Step: Stage 0 prerequisite — assert TOKEN_SOURCES["IDEAL_DAY"]["path"] == "context.ideal_day"
Issue: After sync-child on `sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` @ `5034b1f9`, `TOKEN_SOURCES.get("IDEAL_DAY")` is None. `origin/ftr/AST-1360` not on origin yet; `origin/dev` ancestry on this tip does not include AST-1365 product (`IDEAL_DAY` registry).

Proposed resolutions:
1. Chuckles merge-child AST-1365 onto `origin/ftr/AST-1360`, then Ada re-runs sync-child + build-child
2. Land AST-1365 on `origin/dev` (prep-uat path) so sync-child picks it up
3. Need guidance — Ada will not invent IDEAL_DAY in config or hand-merge `sub/AST-1360/AST-1365-*` (plan forbids)

AST-1368 stays Plan Approved / assignee Ada pending unblock.

#### chuckles — 2026-08-13T19:17:20.749Z
@susan

1. Should `ideal_day` join the context completeness gate (required with strengths / priorities / deal_breakers / backstory), or stay optional until filled (draft default: optional / not gated)?

#### chuckles — 2026-08-13T19:17:14.616Z
1. Should `ideal_day` join the context completeness gate (required with strengths / priorities / deal_breakers / backstory), or stay optional until filled (draft default: optional / not gated)?

---

_Implementation detail may live in git history on `origin/dev`._
