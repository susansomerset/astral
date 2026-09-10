# AST-1458 — Job resume draft prompt is asking for bullet chars

<!-- linear-archive: AST-1458 archived 2026-09-09 -->

## Linear archive (AST-1458)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1458/job-resume-draft-prompt-is-asking-for-bullet-chars  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** None / 1  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The `draft_job_resume` Manage Tasks `user_prompt` currently embeds literal list-marker glyphs (`•`, `-`, `*`) when telling Judith that `accomplishments` entries must be bare strings in a JSON array. Susan wants those characters removed from the prompt text while keeping the same contract: accomplishment strings are plain text with no leading list markers. This is a prompt-wording-only fix in the repo seed catalog — no runtime validation, normalize, or builder changes.

## Functional scope

* Reword the `draft_job_resume` `user_prompt` so it no longer displays bullet/marker character literals; the instruction still requires `accomplishments` as an ordered array of plain strings (no markdown or list-prefix decoration in the JSON values).
* Leave all other draft-hop rules intact: nested `agent_payload.resume` + `deviations`, job-array experience contract, trace-to-base- materials discipline, and existing section-key alignment with the base resume.
* Does not change `craft_resume_base`, `finalize_job_resume`, `advise_job_resume`, or `check_job_resume` prompts unless Susan directs otherwise in a follow-up.

## Component scope

* `data/admin/agent_task.json` — **modified** — current (`current: 1`) `draft_job_resume` row `user_prompt` only.
* `tests/component/core/test_candidate.py` — **modified** (if needed) — extend existing Manage Tasks prompt contract tests so a regression cannot reintroduce literal marker glyphs in the draft prompt.

## Technical scope

* `data/admin/agent_task.json`: edit the `draft_job_resume` / `current: 1` `user_prompt` string — replace the accomplishments clause that names `` `•`/`-`/`*` `` prefixes with equivalent plain-language wording (e.g. bare strings, no list-marker prefixes) without embedding those glyphs; do not alter other task rows or hop metadata fields on that row.
* `tests/component/core/test_candidate.py`: if adding a guard, assert the draft `user_prompt` omits `` `•` ``, `` `-` ``, and `` `*` `` as instructional literals while still teaching array-only experience and the nested resume/deviations envelope (existing AST-1270 / AST-1349 assertions stay green).

## Architectural definition

* **Patterns to reuse** — no established pattern applies (Susan-owned prompt prose in repo seed JSON; no new reusable shape).
* **New patterns proposed** — none.
* **Applicable statutes**
  * [`astral.seed.archie-catalog-wins`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.archie-catalog-wins.md>) — lasting prompt content lives in committed `data/admin/agent_task.json`, not live DB edits alone.
  * [`astral.seed.agent-tables-in-repo-json`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.agent-tables-in-repo-json.md>) — `agent_task.json` is the authoritative seed for task prompt rows.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — touch only the named prompt row and any test that locks its wording; no validator or builder drift.

## Acceptance criteria

1. The current `draft_job_resume` `user_prompt` in `data/admin/agent_task.json` contains no literal `` `•` ``, `` `-` ``, or `` `*` `` characters used to illustrate list-marker prefixes.
2. The same prompt still instructs Judith that `experience` is a job array and `accomplishments` is an ordered array of plain strings (semantic unchanged from Susan's intent).
3. Existing component tests for draft-hop prompt contract (`TestAst1270…`, `TestAst1349…` Manage Tasks assertions) pass without weakening array-only experience or nested-envelope requirements.
4. A manual or dispatched `draft_job_resume` run still accepts well-formed nested resume JSON (no new validation failures introduced by this wording-only change).

## Open questions

(none)

## Proposed child tickets

#### 1: **draft_job_resume prompt — omit bullet marker glyphs - Katherine**

Reword the current `draft_job_resume` `user_prompt` so accomplishment guidance no longer embeds `` `•`/`-`/`*` `` literals; keep job-array experience rules, nested `resume`/`deviations` example, and trace-to-base-materials discipline unchanged. Add or extend a prompt contract test only if needed to prevent glyph regression.

**Citations:** [`astral.seed.archie-catalog-wins`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.archie-catalog-wins.md>), [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)

**Scope:** `data/admin/agent_task.json` — modify current `draft_job_resume` row `user_prompt` only (replace accomplishments clause that names marker glyphs with plain-language bare-string wording). `tests/component/core/test_candidate.py` — modify only if a new assertion is required to lock omission of marker glyph literals.

**Estimate: 1**

---

## Original brief

Just update the prompt to omit the characters

### Comments

#### chuckles — 2026-08-24T22:05:55.579Z
AST-1465 REVIEW — Joan: move glyph-regression test assertions to Betty qa-child manifest; engineer Stage 1 limited to agent_task.json.

---

_Implementation detail may live in git history on `origin/dev`._
