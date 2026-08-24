<!-- linear-archive: AST-1326 archived 2026-08-19 -->

## Linear archive (AST-1326)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1326/make-highlights-a-required-resume-section  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Abrams-style resumes treat Highlights as a first-class body section that must always exist and must sit above Experience—not as an optional extra operators may forget. After AST-1299, Highlights can be authored and emitted, but it is still optional in the required catalog, hop schema, and agent prompts, so craft/parse and base_resume_content can omit or bury it. This epic makes Highlights a required section with stable product order and aligns the craft/parse contracts so models and operators share that rule.

## Functional scope

* **Highlights is required.** Every valid resume structure includes the section id `highlights` (display title Highlights). It cannot be omitted or disabled. Candidates that lack it get it minted the same way other required sections appear in the default catalog.
* **Order above Experience.** On `/artifacts/base_resume_content` (and any structure UI that follows section order), Highlights sits immediately above Experience. The default catalog order encodes that placement; stored structures that already have Highlights are coerced so Highlights remains immediately above Experience.
* **Default format stays the Abrams treatment.** Required Highlights defaults to `bullet_list` (no new visual format). Operators may still change format within the closed format list where structure editing allows it for body sections.
* **Craft/parse response schema requires Highlights.** The shared craft-base / simple-resume-parse response schema includes `highlights` as a required string field (empty string allowed when the source has no highlight material).
* **Agent task prompts require Highlights above Experience.** `craft_resume_base` and `simple_resume_parse` agent_task prompt content instruct that Highlights is required and ordered immediately above Experience, and stay consistent with the schema (including segment count / field inventory language).

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: required ids, default order/format for Highlights, and schema field membership live in config (not inline sets in callers). `pattern.layers.import-discipline`: catalog/normalize in utils+core; prompts/schema in config + agent_task seed; UI remains a thin consumer of structure order. `pattern.ui.admin-endpoint`: structure and catalog continue to resolve from API/config; React does not invent required-id or format lists.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth` (required ids, default order/format, schema); `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.layers.import-direction`; `astral.layers.ui-config-driven-business-logic`; `astral.agent.do-task-delegation` (hop schema + prompts); `astral.seed.agent-tables-in-repo-json` / `astral.seed.archie-catalog-wins` (agent_task prompt updates).

## Boundaries

* Does **not** invent a new body format or typography treatment for Highlights — reuses `bullet_list` (and the closed format list).
* Does **not** reopen AST-1299’s open-extra model for arbitrary titles; only elevates `highlights` into the required set.
* Does **not** own AST-1201 (base-resume daisy chain) or AST-1205 (approve artifacts).
* Does **not** change draft_job_resume nested envelope / deviations work (AST-1268 family); job drafts still follow the candidate’s enabled base keys once Highlights is on the base.
* Does **not** strip historical optional sections (`prior_experience`, `education_certifications`, `technical_skills`) from candidates who have them.

## Acceptance criteria

1. A structure missing `highlights` fails normalize the same way a missing required section does today; `enabled=false` on Highlights is rejected.
2. Default / newly minted structures place Highlights immediately above Experience by `order` on base_resume_content.
3. A candidate who already had Highlights below Experience shows Highlights immediately above Experience after resolve/normalize (without the operator manually reordering).
4. Craft-base and simple-resume-parse response schemas require a `highlights` string; responses omitting the key fail schema validation.
5. `craft_resume_base` and `simple_resume_parse` agent_task prompts state that Highlights is required and sits above Experience, consistent with the schema field inventory / segment instructions.
6. HTML emit for Highlights continues via the existing `bullet_list` (or chosen closed format) path — no new visual language.

## Dependencies and blockers

none (AST-1299 alternative-sections catalog is Done).

## Open questions

none

## Proposed child tickets

#### 1!: **Required Highlights catalog and default order - Ada**

Elevate `highlights` into the required resume-structure catalog and default structure: present + enabled, default format `bullet_list`, order immediately above Experience; normalize/resolve mint and coerce order accordingly. Drives base_resume_content ordering. Does **not** own hop schema or agent_task prompt text (sibling #2).
**Citations:** `pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`
**Estimate:** 3

#### 2: **Craft/parse schema and agent_task prompts - Katherine**

Add required `highlights` to the shared craft-base / simple-resume-parse response schema; update those agent_task prompts so Highlights is required and ordered above Experience (segment inventory / instructions stay consistent with the schema). Does **not** own structure-catalog membership or UI order (sibling #1).
**Citations:** `pattern.config.config-block`, `astral.agent.do-task-delegation`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`
**Estimate:** 3

---

## Original brief

Please move Highlights above Experience in the base_resume_content screen.

Also confirm that Highlights are included in the response schema and agent_task prompt content to reflect this requirement.

### Comments

#### chuckles — 2026-08-12T13:59:08.331Z
AST-1333 REVIEW — Joan needs plan discuss on QUALITY CHECKLIST vs empty highlights.

#### chuckles — 2026-08-12T13:46:40.129Z
AST-1332 REVIEW — Radia: AST-1334 Modal/JAR regression on publish ref; Ada resolving merge with origin/dev.

#### chuckles — 2026-08-12T02:49:22.270Z
[thread-missing] Cursor chat `eed97427-964d-4806-8af0-7c8e8d6ed1d9` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/eed97427-964d-4806-8af0-7c8e8d6ed1d9/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `18084306-8dec-44a0-8306-0b94a9675db1`.

Watcher rule `define` on `AST-1326` (Thread owner `AST-1326`).

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/a15c56d23f73229fd59f82f4b345c208/d4d86f42-9241-47c2-81ee-448a82f718da/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/a15c56d23f73229fd59f82f4b345c208/24faa997-e5b8-441b-8f55-bd57a0d6aa3e/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/2cf51365-1bd5-457f-86e5-bb93cb412c8e/store.db` |
| Radia | review | `/home/susan/.cursor/chats/a15c56d23f73229fd59f82f4b345c208/356a803e-93f5-46e2-a3da-9bbf1a7a8355/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1326 (parent) | ftr/AST-1326-make-highlights-a-required-resume-section |
| AST-1332 | sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order |
| AST-1333 | sub/AST-1326/AST-1333-craft-parse-schema-and-agent-task-prompts |

**Epic worktree:** `astral-AST-1326/` — one active sub checked out at a time.
