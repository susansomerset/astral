# AST-1182 — Rename task to meteorite_email + AI payload as visible text/links

<!-- linear-archive: AST-1182 archived 2026-08-17 -->

## Linear archive (AST-1182)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Ruth’s meteorite-email parse task is the AI hop that turns inbound email content into job links/metadata for the gaze_email ingest path. Today that task is still named `parse_meteorite_email` and the caller feeds it raw HTML. Operators need a stable domain key (`meteorite_email`) and an AI payload that matches JD scrapes — visible text and links only — so prompts stay readable, tokens stay useful, and meteorite email parsing does not depend on markup noise.

## Functional scope

* Rename the existing Ruth meteorite-email parse task so every product identifier for that task is `meteorite_email` (config task key, agent_task seed identity, and all callers that invoke it). The old key `parse_meteorite_email` must not remain as a live product key.
* When that task is invoked, the AI live payload is visible text plus links only — the same content shape used for JD scrapes — not raw HTML markup.
* After rename and payload change, existing gaze_email parse shapes (HTML-link lists and subject+body paths) still reach Ruth and still produce the same class of outcomes (job links/metadata for ingest, or content/JD-link results for the subject+body path).

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — task key and parse-mode literals stay in config blocks; callers read config, do not redefine the key inline.
  * `pattern.layers.import-discipline` — core assembles the live payload and calls `do_task`; external/data ownership stays unchanged.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — task key / parse-mode literals live in config.
  * `astral.seed.agent-tables-in-repo-json` — agent_task seed row must rename with the product key.
  * `astral.agent.do-task-delegation` — gaze_email continues to invoke Ruth via `do_task`.
  * `astral.standards.names-not-ticket-ids` — domain key `meteorite_email`, not ticket-scoped names.
  * `astral.standards.no-hardcoded-sets` — no parallel hard-coded old/new key lists outside config.
  * `astral.standards.in-scope-only` — do not touch sibling grouping/alias/UI/evaluate work.
  * `astral.standards.debug-contract-gated` — if gaze_email / parse call sites with `debug=` are touched, keep Style D found/recorded detail.
  * `astral.standards.no-cross-contamination` / `astral.layers.import-direction` — honor layer boundaries on any payload-assembly change.

## Boundaries

* Does **not** own Gaze Review → Meteorite Review grouping or agent_task section reshuffles (**AST-1183**).
* Does **not** own `master_task_key` / task aliases (**AST-1184**).
* Does **not** own UI grouping/sequence verification or alphabetical task-key dropdowns (**AST-1185**).
* Does **not** own evaluate_meteorite test / statute fold-in (**AST-1186**).
* Does **not** change gaze_email dispatch shell, Gmail archive/trash, or Land Meteorite selected-ids entrypoints beyond the parse-task key and live-payload shape those paths already use.
* Does **not** change qualify_meteorite / evaluate_meteorite / other meteorite GDL tasks.
* Does **not** introduce Playwright scraping of email bodies; email → visible text/links is extraction from the message content, aligned with the JD-scrape *payload shape*, not a page scrape of the inbox.

## Acceptance criteria

* Product config and agent_task seed identify the Ruth meteorite-email parse task as `meteorite_email`; `parse_meteorite_email` is absent as a live task key / agent_task identity.
* All in-repo callers that invoked the old key now invoke `meteorite_email` (via config), and a dry run / known call path does not look up the old key.
* For both html_links-style and subject_body-style gaze_email shapes that call Ruth, the live content sent to the AI is visible text and links — not raw HTML as the primary payload.
* Those shapes still complete parse → ingest (or ignore/error) without requiring a second parallel task key.
* If backend `debug=True` paths for this hop are touched: per-message Style D index headers show what was found and what was recorded; long payloads truncate per the debug contract.

## Dependencies and blockers

* Related intake: **AST-1181** (Backlog; out of scope for this define — sibling bullets live on **AST-1183**–**AST-1186**).
* Soft awareness (not Linear blockedBy): **AST-1088** / **AST-1089** / **AST-1090** still User Testing under the current `parse_meteorite_email` / gaze_email stack — this epic renames and reshapes that task; land relative to that tip so UAT fixtures and call sites move together.
* Sibling Discussion tickets **AST-1183**–**AST-1186** are adjacent scope only; none block this definition.

## Open questions

none

## Proposed child tickets

#### 1!: **Rename parse_meteorite_email to meteorite_email - Ada**

Owns the product rename: config task key and related literals, agent_task seed identity, and every caller that still names `parse_meteorite_email`. Does **not** change the AI live-payload shape (sibling #2) or review groupings / aliases (AST-1183 / AST-1184).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.seed.agent-tables-in-repo-json`; `astral.standards.names-not-ticket-ids`; `astral.standards.no-hardcoded-sets`.

#### 2: **AI payload as visible text and links - Hedy**

After #1: assemble the `meteorite_email` live payload as visible text plus links (JD-scrape content shape, not raw HTML), and update agent_task prompts so Ruth expects that shape. Does **not** own the rename itself (sibling #1) or evaluate_meteorite / UI grouping work.
**Citations:** `pattern.layers.import-discipline`; `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

---

## Original brief

From AST-1181:

* Rename the task to `meteorite_email`
* When we send content to the AI, send just visible text and links as we do for JD scrapes

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1182 (parent) | ftr/AST-1182-rename-task-to-meteorite-email |
| AST-1212 | sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email |
| AST-1213 | sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links |

**Epic worktree:** `astral-AST-1182/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/9d990957670eabef66972baf0f6cbede/fbdb8b75-aaa7-4140-a450-0d5b82e29d6d/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/9d990957670eabef66972baf0f6cbede/d59950f7-6536-4216-bb8c-6ae460fbe3df/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/77657c69-3476-4b68-a386-0bb2ff5faed7/store.db` |
| Radia | review | `/home/susan/.cursor/chats/9d990957670eabef66972baf0f6cbede/68f6cae2-6e62-4293-9fe8-5b041b4161a8/store.db` |

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
