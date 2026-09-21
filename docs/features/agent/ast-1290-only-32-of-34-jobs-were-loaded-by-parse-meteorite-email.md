# AST-1290 — Only 32 of 34 jobs were loaded by parse_meteorite_email

<!-- linear-archive: AST-1290 archived 2026-09-09 -->

## Linear archive (AST-1290)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1290/only-32-of-34-jobs-were-loaded-by-parse-meteorite-email  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Bound meteorite email parse (`meteorite_email` / legacy `parse_meteorite_email`) silently dropped two of thirty-four Dice job links from a real inbox message — the parse result used for ingest had 32 jobs while the email listed 34. Operators cannot trust Land Meteorite / gaze_email when long link lists truncate without a failure signal. This epic restores completeness: every job link present for Ruth in that message must be available for ingest (titles may still be null).

## Functional scope

1. For `html_links` parse of a bound meteorite email, every job link that appears in the Ruth live payload link enumeration for that message must appear in the parse result that drives ingest — no silent loss of links (this UAT: 34 listed → 34 loaded; the two missing were `…/3628bf85-…` and `…/add50803-…`).
2. Incomplete title extract remains allowed: a job row may have a null/empty title when the link is present (already observed on several of the 32 returned rows).
3. Completeness is enforced for the ingest path — prompt tightening alone is not sufficient if the model can still omit trailing links from long lists; the product outcome is full link coverage into ingest attempts.
4. When `debug=True` on the gaze_email / meteorite_email path that builds the Ruth payload and applies the parse result, Style D detail shows links **found** in the payload enumeration and jobs **recorded** for ingest (counts plus which links are missing when counts differ); when `debug=False`, no new debug noise from this path.
5. `subject_url` and `subject_body` shapes stay as they are unless a shared helper is the only safe place for a completeness check that also applies there — do not redesign those shapes.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: link-hygiene / Ruth payload excludes and parse-mode literals stay in `METEORITE_EMAIL_INGEST_CONFIG` / `METEORITE_EMAIL_PARSE_CONFIG`, not inline magic sets. `pattern.batch.entity-claim-process-release` is **not** the primary shape here (mailbox parse is not an entity claim queue); cite only if a child wrongly pulls claim/release into scope.
* **New patterns proposed** — none. Completeness reconcile (or equivalent) after Ruth on an already-enumerated link list is a gaze_email / meteorite_email hardening, not a new catalog pattern unless Archie later wants it named.
* **Applicable statutes** — universal active set for product code; `astral.agent.do-task-delegation` (Ruth still via `do_task`; schema/validate stay on the agent path); `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` (excludes, modes, schema); `astral.standards.debug-contract-gated` (found/recorded Style D); `astral.standards.in-scope-only` (no Avail/dispatch rewrite, no qualify/scrape redesign); `astral.standards.dry-and-focused-functions`.

## Boundaries

* Does **not** fix [AST-1282](https://linear.app/astralcareermatch/issue/AST-1282/parse-meteorite-email-failing) (Avail vs `min_count` / scheduler skip for `parse_meteorite_email`) — separate Discussion on Astral Meteorite.
* Does **not** absorb [AST-1289](https://linear.app/astralcareermatch/issue/AST-1289/handling-datatype-issues-in-responses) (int→str soft-coerce on schema string fields) — adjacent LLM-response family, different failure mode.
* Does **not** rename seed keys (`parse_meteorite_email` → `meteorite_email` / `catch_meteorite_email`) or change Admin picker contracts — already covered by [AST-1212](https://linear.app/astralcareermatch/issue/AST-1212/rename-parse-meteorite-email-to-meteorite-email-rename-task-to) / [AST-1214](https://linear.app/astralcareermatch/issue/AST-1214/admin-catalogapi-hardcode-audit-alphabetical-task-key-lists-ui) / related Meteorite work.
* Does **not** change Playwright create/dedupe rules, non-job skip hygiene, or archive rules beyond whatever is required so omitted links still get an ingest attempt.
* Does **not** require titles for every link; null title + valid link is enough to count as loaded.
* Must not break [AST-1213](https://linear.app/astralcareermatch/issue/AST-1213/ai-payload-as-visible-text-and-links-rename-task-to-meteorite-email-ai) Ruth payload shape (visible text + `--- LINKS ---`) or re-widen Ruth excludes to strip click-tracking hosts.

## Acceptance criteria

1. Replaying the UAT message shape (34 Dice `job-detail` links in the Ruth payload enumeration) yields 34 jobs in the parse result used for ingest — including `3628bf85-8915-4525-93ff-2f05e09f9e39` and `add50803-2af1-4f26-aba5-3997c9db8905`.
2. A successful parse no longer silently returns fewer jobs than payload job links for `html_links`; if the model omits links, the product still covers those links for ingest (stub/null title allowed).
3. With `debug=True`, an incomplete Ruth `jobs` list vs payload links is visible as found vs recorded (and missing link ids) under Style D; with `debug=False`, this path adds no new debug lines.
4. Existing null-title job rows still validate and ingest; required `job_link` remains required.
5. [AST-1282](https://linear.app/astralcareermatch/issue/AST-1282/parse-meteorite-email-failing) Avail/scheduler behavior and [AST-1289](https://linear.app/astralcareermatch/issue/AST-1289/handling-datatype-issues-in-responses) datatype coercion are unchanged by this epic.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1: **html_links completeness — all payload job links land - Ada**

Own the end-to-end fix so `html_links` meteorite email parse cannot silently drop payload-enumerated job links before ingest (prompt tightening and/or post-parse reconcile on the gaze_email path as needed). Observable outcome: the 34-link UAT class loads 34 jobs (null titles OK). Does **not** own Avail/dispatch ([AST-1282](https://linear.app/astralcareermatch/issue/AST-1282/parse-meteorite-email-failing)), int→str coerce ([AST-1289](https://linear.app/astralcareermatch/issue/AST-1289/handling-datatype-issues-in-responses)), or seed rename.
**Citations:** `pattern.config.config-block`; `astral.agent.do-task-delegation`; `astral.config.config-source-of-truth`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

Monolith check: Functional scope has 5 capabilities and 1 child — intentional single vertical slice; payload assembly, Ruth result, completeness enforce, and Style D found/recorded must ship together so UAT can prove 34/34 without a half-applied pipeline.

---

## Original brief

```
1. https://www.dice.com/job-detail/801012b1-1801-42dc-a784-fecd2ae4f871  
2. https://www.dice.com/job-detail/fe9ffb32-07bb-4fbc-beff-99c45969e423  
3. https://www.dice.com/job-detail/6210dbdf-304e-400f-b73a-3e1dfc5993d4  
4. https://www.dice.com/job-detail/711e4efd-04ca-428a-9d15-954aa9d4850a  
5. https://www.dice.com/job-detail/1f5c5c4c-a427-48aa-8f3c-4168ee3f22e7  
6. https://www.dice.com/job-detail/f00dcb10-f309-42cc-ab4a-aaaffd6a90c4  
7. https://www.dice.com/job-detail/c375529b-543c-48e7-a87c-39fb762e402c  
8. https://www.dice.com/job-detail/a740e541-f52e-4fa6-b522-a10d6845f0a4  
9. https://www.dice.com/job-detail/42f5e734-b1eb-45d3-8493-f18e03107211  
10. https://www.dice.com/job-detail/8e6f94dc-df8b-47b6-a96f-2c10b61e965d  
11. https://www.dice.com/job-detail/5edf3075-df3b-4538-8013-b23a3499eac2  
12. https://www.dice.com/job-detail/cc5614d4-6ff1-4673-8571-e59bdb455736  
13. https://www.dice.com/job-detail/04dd50e5-7829-4187-997e-753a8f1114ad  
14. https://www.dice.com/job-detail/cf1b0f6b-df72-4267-9882-8df914eb31f8  
15. https://www.dice.com/job-detail/0f4fd8c7-3032-47de-9f06-c1602d5a1617  
16. https://www.dice.com/job-detail/1c6049e1-27c4-4a42-b9c8-3e3be446d4e8  
17. https://www.dice.com/job-detail/238439a6-65f4-4c03-99b1-449e21fbc882  
18. https://www.dice.com/job-detail/f97e3e2f-79cc-4217-a8ca-ea07be3cc44b  
19. https://www.dice.com/job-detail/50ac44a4-ca09-4a0e-8297-cbdbe058b9d8  
20. https://www.dice.com/job-detail/68e6f5a7-a112-4ded-b81f-7bbe427f7d97  
21. https://www.dice.com/job-detail/e4a8ade2-7394-41c1-83c6-32e8484edf44  
22. https://www.dice.com/job-detail/5056150a-47c5-483e-8943-ba06fa880d2e  
23. https://www.dice.com/job-detail/b87017d4-f536-40ef-bac1-c9980a4c075d  
24. https://www.dice.com/job-detail/e118abab-d44f-4284-8773-a31de4409586  
25. https://www.dice.com/job-detail/e2bf7ac5-ead5-4d9f-867c-176835f43381  
26. https://www.dice.com/job-detail/3465ba33-4099-4b94-9ebe-f100ff59b843  
27. https://www.dice.com/job-detail/4b9727f4-ddc0-4aab-ab6e-dd7f42d9888e  
28. https://www.dice.com/job-detail/e5536776-23c8-4c86-b9a3-60c29d32ce69  
29. https://www.dice.com/job-detail/62749deb-b3a9-4372-b1fe-ebe0e8be619e  
30. https://www.dice.com/job-detail/c797094a-2fea-406c-8c58-ad2d19471685  
31. https://www.dice.com/job-detail/cd599298-c4ce-418a-9a68-9efc1ecc56f6  
32. https://www.dice.com/job-detail/fc812fa4-8436-4e0e-93eb-931c52c67193  
33. https://www.dice.com/job-detail/3628bf85-8915-4525-93ff-2f05e09f9e39  
34. https://www.dice.com/job-detail/add50803-2af1-4f26-aba5-3997c9db8905
```

```
[
  {
    "job_link": "https://www.dice.com/job-detail/e4a8ade2-7394-41c1-83c6-32e8484edf44",
    "job_title": "Technical Lead / Solution Architect"
  },
  {
    "job_link": "https://www.dice.com/job-detail/5056150a-47c5-483e-8943-ba06fa880d2e",
    "job_title": "Technical Project Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/b87017d4-f536-40ef-bac1-c9980a4c075d",
    "job_title": "Technical Product Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/e118abab-d44f-4284-8773-a31de4409586",
    "job_title": "Technical Project Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/e2bf7ac5-ead5-4d9f-867c-176835f43381",
    "job_title": "Senior Technical Product Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/3465ba33-4099-4b94-9ebe-f100ff59b843",
    "job_title": "Senior Technical Program Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/4b9727f4-ddc0-4aab-ab6e-dd7f42d9888e",
    "job_title": "Product Owner / Technical Program Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/e5536776-23c8-4c86-b9a3-60c29d32ce69",
    "job_title": "Technical Program Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/62749deb-b3a9-4372-b1fe-ebe0e8be619e",
    "job_title": "Principal Technical Program Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/c797094a-2fea-406c-8c58-ad2d19471685",
    "job_title": null
  },
  {
    "job_link": "https://www.dice.com/job-detail/cd599298-c4ce-418a-9a68-9efc1ecc56f6",
    "job_title": null
  },
  {
    "job_link": "https://www.dice.com/job-detail/fc812fa4-8436-4e0e-93eb-931c52c67193",
    "job_title": null
  },
  {
    "job_link": "https://www.dice.com/job-detail/801012b1-1801-42dc-a784-fecd2ae4f871",
    "job_title": "Technical Project Manager / Scrum Master"
  },
  {
    "job_link": "https://www.dice.com/job-detail/fe9ffb32-07bb-4fbc-beff-99c45969e423",
    "job_title": "Senior Project Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/6210dbdf-304e-400f-b73a-3e1dfc5993d4",
    "job_title": "Portfolio Project Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/711e4efd-04ca-428a-9d15-954aa9d4850a",
    "job_title": "Agentic AI Solutions Architect"
  },
  {
    "job_link": "https://www.dice.com/job-detail/1f5c5c4c-a427-48aa-8f3c-4168ee3f22e7",
    "job_title": "Integrations Lead"
  },
  {
    "job_link": "https://www.dice.com/job-detail/f00dcb10-f309-42cc-ab4a-aaaffd6a90c4",
    "job_title": "Technical Lead / Technical Project Lead (Remote)"
  },
  {
    "job_link": "https://www.dice.com/job-detail/c375529b-543c-48e7-a87c-39fb762e402c",
    "job_title": null
  },
  {
    "job_link": "https://www.dice.com/job-detail/a740e541-f52e-4fa6-b522-a10d6845f0a4",
    "job_title": null
  },
  {
    "job_link": "https://www.dice.com/job-detail/42f5e734-b1eb-45d3-8493-f18e03107211",
    "job_title": null
  },
  {
    "job_link": "https://www.dice.com/job-detail/8e6f94dc-df8b-47b6-a96f-2c10b61e965d",
    "job_title": "Senior Business Analyst (Healthcare Domain and Strong SQL)"
  },
  {
    "job_link": "https://www.dice.com/job-detail/5edf3075-df3b-4538-8013-b23a3499eac2",
    "job_title": "Technical Program / Delivery Leader"
  },
  {
    "job_link": "https://www.dice.com/job-detail/cc5614d4-6ff1-4673-8571-e59bdb455736",
    "job_title": "Project Manager/Sr. Consultant"
  },
  {
    "job_link": "https://www.dice.com/job-detail/04dd50e5-7829-4187-997e-753a8f1114ad",
    "job_title": "AI Engineering Productivity"
  },
  {
    "job_link": "https://www.dice.com/job-detail/cf1b0f6b-df72-4267-9882-8df914eb31f8",
    "job_title": "Data & AI Solutions Architect"
  },
  {
    "job_link": "https://www.dice.com/job-detail/0f4fd8c7-3032-47de-9f06-c1602d5a1617",
    "job_title": "Generative AI / Agentic AI Architect"
  },
  {
    "job_link": "https://www.dice.com/job-detail/1c6049e1-27c4-4a42-b9c8-3e3be446d4e8",
    "job_title": "Product Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/238439a6-65f4-4c03-99b1-449e21fbc882",
    "job_title": "Program/ Portfolio Manager"
  },
  {
    "job_link": "https://www.dice.com/job-detail/f97e3e2f-79cc-4217-a8ca-ea07be3cc44b",
    "job_title": "Product Owner - Healthcare"
  },
  {
    "job_link": "https://www.dice.com/job-detail/50ac44a4-ca09-4a0e-8297-cbdbe058b9d8",
    "job_title": "Agile Product Owner – Healthcare Provider Transformation"
  },
  {
    "job_link": "https://www.dice.com/job-detail/68e6f5a7-a112-4ded-b81f-7bbe427f7d97",
    "job_title": "Product Owner – Healthcare Capitation"
  }
]
```

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1290 (parent) | ftr/AST-1290-only-32-of-34-jobs-were-loaded-by-parse_meteorite_email |
| AST-1294 | sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land |

**Epic worktree:** `astral-AST-1290/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/736e527d889436b64400586025595e17/cefbf8d3-2654-4aa3-97d7-ac02cd909c77/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/3b11b6b5-f63c-48c5-bcb0-8d72b116846f/store.db` |
| Radia | review | `/home/susan/.cursor/chats/736e527d889436b64400586025595e17/31baeae1-e4c4-492a-9f0e-73e97347e2ca/store.db` |

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
