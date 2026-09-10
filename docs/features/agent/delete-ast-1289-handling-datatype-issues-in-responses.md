<!-- linear-archive: AST-1289 archived 2026-08-19 -->

## Linear archive (AST-1289)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1289/handling-datatype-issues-in-responses  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

LLM batch responses sometimes echo job-slot indexes as bare numbers (`0`, `1`, `2`) while the task schema expects strings (`"000"` / `"001"` / slot text). Today that type nit rejects an otherwise-good envelope and burns the whole chunk. This epic makes ingest a little liberal on that index datatype so valid job rows still land, without treating the failure as scrape or bot blocking.

## Functional scope

1. When a response field is declared as string in the task schema and the model returns a whole number (integer, not boolean), ingest coerces it to a string before schema validation so the field does not fail on type alone.
2. Nested job items are included — a numeric `astral_job_id` (batch-slot echo) must not fail the whole `jobs` list when the rest of the item is otherwise valid.
3. Coercion is stringification of the number only; it does not invent zero-padding. Existing claim/slot binding that already maps digit slot echoes to claimed job ids continues to own identity resolution after validation.
4. Task schema field types stay string for these index/id fields — we do not flip the declared type to integer to match the model habit.
5. When `debug=True` on the agent path that validates/coerces, each coercion shows what was found (raw type/value) and what was recorded (string form) under Style D index detail; when `debug=False`, no new debug noise from this path.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: string vs number tolerance must not scatter magic type sets; declared response field types remain in `TASK_CONFIG` / task schema config. Soft-coerce stays beside the existing pre-validate list→string habit on the shared `do_task` validation path (`astral.agent.do-task-delegation`).
* **New patterns proposed** — none. This extends the existing pre-validate soft-coerce family (list→string already ships); int→string for schema `str` fields is the same shape, not a new catalog entry unless Archie later wants it named.
* **Applicable statutes** — universal active set; `astral.agent.do-task-delegation` (validation/coerce stays on the central agent response path); `astral.config.config-source-of-truth` (schema types remain config-owned); `astral.standards.in-scope-only` (no scrape/bot/qualify redesign); `astral.standards.debug-contract-gated` (Style D only when `debug=True`); `astral.standards.dry-and-focused-functions` (extend the existing coerce helper rather than a parallel validator).

## Boundaries

* Does **not** change scrape, bot-block, or qualify state machines — this is schema/type tolerance only.
* Does **not** accept dict/list/bool where the schema expects string (list→string remains the existing special case; dict stays hard-fail unless a separate schema ticket like AST-1144 flips the declared type).
* Does **not** rewrite claim-binding rules, zero-pad policy, or prompt catalogs except where a planner must document the coerce behavior for UAT.
* Does **not** loosen required-field presence, enums, grade/confidence bounds, or non-string schema types.
* Does **not** bury per-task schema flips for unrelated fields inside this epic.

## Acceptance criteria

1. A successful agent envelope whose `jobs[n].astral_job_id` is an integer batch-slot echo (e.g. `0`) validates and is available for downstream apply the same way an equivalent string slot echo already is — no `Field 'astral_job_id' must be str, got int` rejection for that case alone.
2. A chunk that previously failed solely for integer slot ids (while sibling chunks with string ids succeeded) no longer fails on that type nit; other real schema failures still reject.
3. Declared schema type for these fields remains string in config after the change.
4. With `debug=True`, a coerced integer slot id is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.
5. Boolean `true`/`false` and object values for string fields still fail validation (no accidental bool/dict soft-accept).

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1: **Soft-coerce numeric schema strings on do_task validate - Ada**

Own the pre-validate soft-coerce so integer values on schema-string fields (including nested `jobs[].astral_job_id` slot echoes) become strings before type checks; keep schema declarations as string; leave claim/slot binding and non-string type rules alone. Observable outcome: Deepseek-style integer slot ids no longer sink an otherwise-valid batch envelope. Does **not** own prompt rewrites, scrape/bot handling, or per-field schema type flips.
**Citations:** `pattern.config.config-block`; `astral.agent.do-task-delegation`; `astral.config.config-source-of-truth`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

Monolith check: Functional scope has 5 capabilities and 1 child — intentional single vertical slice; coerce-before-validate must ship with unchanged string schema contract and existing slot-id binding so UAT can prove ingest without a half-applied pipeline.

---

## Original brief

I think we can be a little bit liberal about ingesting indexed job items that are numbers not strings, so we don't reject a whole response on the basis of the index's data type.

```
jobs[0]: Field 'astral_job_id' must be str, got int

Deepseek sometimes returned batch-slot ids as bare integers (0, 1, 2) instead of the zero-padded strings ("000", "001", "002"). Two chunks of 3 jobs each failed that way → 6 errors. The other chunks that returned string ids went through fine (METEORITE_QUALIFIED).

So: schema/type nit from the LLM response, not scraping/bot blocking.
```

```
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": {
    "jobs": [
      {
        "astral_job_id": 0,
        "company_job_id": "9050070",
        "job_title": "Technical Business Analyst",
        "job_link": "https://www.dice.com/job-detail/c797094a-2fea-406c-8c58-ad2d19471685",
        "jd_text": "Job Summary:We are seeking an experienced Business Analyst to support ahigh-priority initiative to upgrade pharmacy claims processing systems from NCPDP Version D.0 to F6. The Business Analyst will partner with business stakeholders, pharmacy operations, compliance 
```

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1289 (parent) | ftr/AST-1289-handling-datatype-issues-in-responses |
| AST-1293 | sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings |

**Epic worktree:** `astral-AST-1289/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/5dce837c2f77f78e2b70bb95ff906c68/6977332a-3e4b-4172-b104-5c3085fa44fe/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/8bfbeece-55ba-4516-ab88-82e685f79b71/store.db` |
| Radia | review | `/home/susan/.cursor/chats/5dce837c2f77f78e2b70bb95ff906c68/f1bbe948-f59f-4f2e-b665-6fed031c3efb/store.db` |

### Comments

_No comments._

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/5dce837c2f77f78e2b70bb95ff906c68/6977332a-3e4b-4172-b104-5c3085fa44fe/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/8bfbeece-55ba-4516-ab88-82e685f79b71/store.db` |
| Radia | review | `/home/susan/.cursor/chats/5dce837c2f77f78e2b70bb95ff906c68/f1bbe948-f59f-4f2e-b665-6fed031c3efb/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1289 (parent) | ftr/AST-1289-handling-datatype-issues-in-responses |
| AST-1293 | sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings |

**Epic worktree:** `astral-AST-1289/` — one active sub checked out at a time.
