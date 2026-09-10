# AST-680 — Why is src.external.anthropic still in the logs?

<!-- linear-archive: AST-680 archived 2026-06-23 -->

## Linear archive (AST-680)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-680/why-is-srcexternalanthropic-still-in-the-logs  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators tracing staging runs for DeepSeek-backed tasks (e.g. `select_job_page`) see log lines attributed to the Anthropic external module even though the active provider is DeepSeek and the call succeeded. That mismatch wastes UAT time, hides which client actually ran, and signals sloppy external-layer boundaries — work that should not have shipped. This epic restores trustworthy provider attribution in logs and tightens how we structure and review shared code across LLM external clients so the mistake cannot recur.

## Functional scope

* **Correct log attribution for DeepSeek calls.** When the active LLM provider is DeepSeek, every debug-contract and routine INFO line emitted for that API call must identify the DeepSeek client as its source — not the Anthropic client module. The `func_name`, `provider`, and task key in the message body may still appear; the logger/module prefix must match the executing provider.
* **Shared LLM helpers in utils.** Any helper used by both Anthropic and DeepSeek provider clients (debug emission, response text extraction, and other duplicated parsing utilities that fit the utils layer) must live under `utils/` per `ASTRAL_CODE_RULES` §3.3. Neither external client imports from the other. Each provider client owns its own logger identity; shared helpers must not hard-code a sibling external module name when emitting logs — the calling provider's module emits, or the helper receives caller context so attribution stays correct.
* **No regression for Anthropic provider.** When config selects Anthropic, existing call semantics, timesheet recording, and debug-contract shape ([AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)) remain unchanged; only attribution and shared-code placement are corrected.
* **Radia review gate for external cleanliness.** Extend Radia's review criteria (review-child skill or equivalent checklist) so Tests Passed reviews flag: (a) cross-external imports between LLM provider clients, (b) shared helpers that cause misleading log module names, (c) DeepSeek-active paths that still surface Anthropic module prefixes in operator-visible logs. Missing or inadequate checks on touched LLM external surfaces are fix-now, consistent with [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) review practice.
* **Debug contract preserved.** When `debug=True`, DeepSeek calls continue to emit Style D index headers (`index 1/1`), `|` detail lines (provider, model, task, duration, tokens, truncated response preview per [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)). Only the log source attribution changes — not the contract shape.

## Boundaries

* Does not change which provider `do_task` selects, brain-setting tier resolution, or timesheet cost math (AST-569/570 territory).
* Does not create a cross-external import exception or a third external module solely for LLM sharing — shared code that both clients need belongs in `utils/` only.
* Does not backfill debug logging in core, dispatcher, roster, or consult modules — only LLM external client modules, applicable utils helpers, and Radia review criteria.
* Does not add new providers beyond Anthropic and DeepSeek.
* Must not break the existing `send_to_anthropic` / `send_to_deepseek` observable success/failure contract or `record_timesheet` behavior.

## Acceptance criteria

1. Reproduce Susan's staging scenario: run `select_job_page` (or any representative DeepSeek dispatch task) with `debug=True` on the fixed build. Log prefix identifies the DeepSeek external module — **not** `src.external.anthropic` — while detail lines still show `provider=deepseek` and the correct vendor model.
2. Run a representative Anthropic-backed task with `debug=True`. Log prefix identifies the Anthropic external module; no DeepSeek module prefix appears.
3. Review of LLM external modules confirms no DeepSeek call path emits through the Anthropic module logger (including shared debug helpers).
4. Shared helpers used by both clients live in `utils/`; neither `anthropic` nor `deepseek` external module imports from the other.
5. Radia review criteria document includes explicit fix-now checks for external-layer provider attribution and cross-import hygiene on LLM wrapper diffs; a sample review comment template or checklist item is visible to the team.
6. Existing component tests for provider routing (`do_task` anthropic vs deepseek branches) remain green; add or adjust tests only where needed to lock attribution behavior.

## Dependencies and blockers

* Related (not blocking): AST-493 (DeepSeek client routing), AST-620 (external LLM wrapper debug backfill — introduced shared `_emit_llm_call_debug` in Anthropic module), AST-538/554 (debug logging contract).
* None required before start.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-680](https://linear.app/astralcareermatch/issue/AST-680/why-is-srcexternalanthropic-still-in-the-logs) (parent) | ftr/ast-680-llm-external-log-attribution |
| [AST-687](https://linear.app/astralcareermatch/issue/AST-687/llm-provider-log-attribution-and-shared-utils-helpers-why-is) | sub/AST-680/AST-687-llm-external-log-attribution |
| [AST-688](https://linear.app/astralcareermatch/issue/AST-688/radia-review-criteria-for-external-layer-cleanliness-why-is) | sub/AST-680/AST-688-radia-review-criteria-external-cleanliness |

**Epic worktree:** `astral-AST-680/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 130a87a7-8fe8-4ede-bb5b-bce1ed1f72eb |
| Betty | qa | ed52f548-9da7-4cb4-be44-e1bbbec0df0f |
| Radia | review | 13d041da-e594-4069-8bfd-838f5cecda4a |

---

## Original brief

We should be using deepseek.  If the externals need to share a function, then move the function to deepseek and update [anthropic.py](<http://anthropic.py>) to import from there to make sure there isn't confusion.

Also, tell Radia to update her review criteria to be sure we are using externals cleanly.  This is sloppy work and should not have landed.

[2026-06-15 18:58:08] INFO src.external.anthropic: send_to_deepseek index 1/1 select_job_page -> success

[2026-06-15 18:58:08] INFO src.external.anthropic:  | provider=deepseek model=deepseek-v4-flash task=select_job_page duration=77.7s stop_reason=end_turn
[2026-06-15 18:58:08] INFO src.external.anthropic:  | vendor=deepseek-v4-flash tokens fresh=4478 cache_read=512 cache_write=0 output=15041
[2026-06-15 18:58:08] INFO src.external.anthropic:  | response_preview:

### Comments

#### chuckles — 2026-06-15T19:08:10.057Z
@susan — one decision before dispatch:

1. **External import rule vs module home** — §3.3 says `external → utils` only. Today deepseek imports anthropic; your brief flips that. Approve: (a) your flip, (b) shared helpers in utils, (c) narrow rules exception for LLM pair, or (d) duplicate to avoid cross-external imports?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
