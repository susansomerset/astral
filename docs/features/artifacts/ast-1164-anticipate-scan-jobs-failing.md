# AST-1164 — anticipate_scan jobs failing

<!-- linear-archive: AST-1164 archived 2026-08-07 -->

## Linear archive (AST-1164)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1161; related: AST-1162

### Description

## Purpose

`anticipate_scan` is the entry hop of the resume artifact chain. A live run waited ~24 minutes on DeepSeek, then logged `stop=? tokens in=0 out=0` and `do_task(anticipate_scan) provider call failed` with an **empty** error string. Operators cannot tell timeout from hollow response from a silent provider failure, and Generate Artifacts cannot be trusted or retried with a clear reason. This epic hardens provider-call failure for that hop (and the shared LLM path it uses) so long empty waits and blank errors stop masking the real outcome.

## Functional scope

* Provider calls used by artifact hops (DeepSeek path that produced the pasted log; Anthropic mirror when it shares the same call/timeout shape) enforce a hard per-call time budget. A call that exceeds that budget fails promptly with a non-empty, classifiable timeout error — it does not sit for tens of minutes and then report zero tokens with a blank reason.
* When a provider returns without a usable stop reason, token usage, and/or content (the observed `stop=?` / `tokens in=0 out=0` shape), `do_task` fails with a **non-empty** error that names that hollowness. Logs never show a healthy-looking LLM summary followed by `provider call failed … error=` with nothing after the equals.
* On such a failure for `anticipate_scan` (and sibling artifact hops on the same provider path), the entity batch is released and the job lands on the configured artifact error/hold state so Generate Artifacts can be retried; Execution History / app_log shows the failure reason for that `batch_id`.
* With `debug=True` on the touched provider/`do_task` failure path: log what was **found** and what was **recorded** (duration, stop reason, token counts, error / failure class). Index headers use universal `index N/M` + primary identifier + outcome (Style D); working detail lines use the contract prefix (two spaces, pipe, two spaces); payloads >50 lines use first 15 / `<n lines omitted>` / last 15. Backend only.

## Architectural definition

* **Patterns to reuse** — `pattern.batch.entity-claim-process-release` (failure still claim/process/release; no orphaned claims); `pattern.dispatch.run-next-chain-authority` (`run_next` / hop order unchanged — harden call outcomes, not chain topology); `pattern.config.config-block` (timeouts / provider knobs stay config-owned when raised out of hardcodes).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.agent.do-task-delegation` (provider I/O stays in external; core consumes structured failure); `astral.batch.claim-process-release`; `astral.batch.batch-id-first`; `astral.dispatch.run-next-is-chain-authority`; `astral.layers.core-vs-external-bright-line`; `astral.layers.import-direction`; `astral.standards.debug-contract-gated`; `astral.standards.logging-via-utils`; `astral.standards.data-raises-caller-logs`; `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.standards.dry-and-focused-functions`; `astral.config.config-source-of-truth`; `astral.patterns.coat-check-never-store-empty` (do not treat empty provider payloads as successful hop output).

## Boundaries

* Does **not** fix hollow `{$FIRST_NAME}` / `{$LAST_NAME}` or empty `{$ANALYSIS_*}` tokens — that is [AST-1163](https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan) (related).
* Does **not** re-author `anticipate_scan` prompt prose in Manage Tasks.
* Does **not** change `run_next` chain membership, graduation maps, or BUILD_ARTIFACTS hop topology.
* Does **not** redesign timesheet/pricing schema beyond the failure classification needed so ops can see timeout vs hollow response vs balance refusal (AST-897) vs max_tokens (AST-903).
* Does **not** expand schedulability of `anticipate_scan`.
* Sibling UT on signature spacing ([AST-1161](https://linear.app/astralcareermatch/issue/AST-1161/signature-image-now-overlaps-name-text-in-signature) / [AST-1162](https://linear.app/astralcareermatch/issue/AST-1162/fix-signature-image-name-vertical-spacing-signature-image-now-overlaps)) is out of scope.

## Acceptance criteria

1. A provider call that exceeds the configured per-call time budget fails within that budget (plus the small existing grace already used around the wait) with a non-empty timeout error / failure class — not a ~20+ minute `stop=? tokens in=0 out=0` mystery with blank `error=`.
2. A provider outcome that yields `stop=?` and zero in/out tokens with no usable content causes `do_task` to return failure with a non-empty error string visible in the `provider call failed … error=` log line.
3. After such a failure on `anticipate_scan`, the job is not left batch-claimed; it is on the configured artifact error/hold state for that task, and the failure reason is visible against that `batch_id` in Execution History / app_log.
4. A debug-gated run of the fixed path shows found/recorded lines for duration, stop, tokens, and error/failure class on the failed call.
5. A healthy DeepSeek (or mirrored Anthropic) response with normal stop reason and token counts still completes `anticipate_scan` successfully when prompt context is otherwise valid.

## Dependencies and blockers

* **Related (not blocking):** [AST-1163](https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan) — hollow candidate name + ANALYSIS token context for the same hop. Fixing 1163 may reduce garbage prompts; this epic still owns provider timeout / empty-error / zero-token response hardening on its own.
* Prior failure-class patterns to reuse (already shipped): AST-897 (balance refusal), AST-903 (JSON max_tokens hard-fail).
* No open Linear blockers. Parallel Artifacts UT: [AST-1161](https://linear.app/astralcareermatch/issue/AST-1161/signature-image-now-overlaps-name-text-in-signature) — no functional dependency.

## Open questions

1. Confirm the split: [AST-1164](https://linear.app/astralcareermatch/issue/AST-1164/anticipate-scan-jobs-failing) = provider timeout / empty-error / zero-token response hardening; [AST-1163](https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan) = hollow name + ANALYSIS tokens — not a duplicate?
   1. Correct.
2. Which candidate id + job id produced batch `anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a` (for UAT replay)?
   1. Not applicable, just implement and I'll retest.
3. Timeout policy: keep the existing ~5 minute provider call budget but make failure/cancellation always surface cleanly, or raise/lower the budget via `ASTRAL_CONFIG` as part of this epic?
   1. Raise the timeout to 10 minutes, please.
4. Must the Anthropic mirror ship in the same epic, or DeepSeek-only until a matching Anthropic hang is seen?
   1. Both, actually, yes.

## Proposed child tickets

#### 1!: **Provider call budget + timeout failure class - Ada**

Enforce the hard per-call time budget on the DeepSeek path (and Anthropic mirror if #4 includes it) so over-budget calls fail with a non-empty timeout error / failure class instead of a long zero-token mystery. Does **not** own hollow-response classification (#2) or artifact hop release/debug (#3).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.layers.core-vs-external-bright-line`; `astral.agent.do-task-delegation`; `astral.standards.in-scope-only`.

#### 2!: **Empty / unusable provider response surfacing - Hedy**

When the provider returns `stop=?` / zero tokens / no usable content, fail `do_task` with a non-empty error (never blank `error=`) and do not log that outcome as a healthy LLM summary. Does **not** own timeout budget (#1).
**Citations:** `astral.agent.do-task-delegation`; `astral.standards.logging-via-utils`; `astral.patterns.coat-check-never-store-empty`; `astral.standards.dry-and-focused-functions`.

#### 3: **Artifact hop failure release + debug trail - Katherine**

After #1 and #2: on provider failure for `anticipate_scan` / shared artifact hops, ensure batch release + configured error/hold state, and AST-538-style debug found/recorded for UAT. Does **not** redesign LLM adapters beyond consuming their structured failures.
**Citations:** `pattern.batch.entity-claim-process-release`; `astral.batch.claim-process-release`; `astral.dispatch.run-next-is-chain-authority`; `astral.standards.debug-contract-gated`.

---

## Original brief

```
[2026-08-03 22:07:30] INFO src.external.deepseek: LLM deepseek task=anticipate_scan 1425.7s stop=? tokens in=0 out=0
[2026-08-03 22:07:30] ERROR src.core.agent: do_task(anticipate_scan) provider call failed batch_id=anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a error=
[2026-08-03 21:45:55] INFO src.core.agent: run_next chain entry: task=anticipate_scan batch_id=anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a
```

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1164 (parent) | ftr/AST-1164-anticipate-scan-jobs-failing |
| AST-1189 | sub/AST-1164/AST-1189-provider-call-budget-timeout |
| AST-1190 | sub/AST-1164/AST-1190-empty-unusable-provider-response |
| AST-1191 | sub/AST-1164/AST-1191-artifact-hop-failure-release-debug |

**Epic worktree:** `astral-AST-1164/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/599b03ad2762d6f2f020fff7185f6cd5/d909b801-0392-4067-a39c-b492b7d046a3/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/599b03ad2762d6f2f020fff7185f6cd5/1f7cacb4-2f55-48ee-92bf-3db7117a4472/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/599b03ad2762d6f2f020fff7185f6cd5/90212e85-e2fd-4fb9-8129-75deeb6cd69e/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/730f940e-fb54-4d44-9477-605e817dae23/store.db` |
| Radia | review | `/home/susan/.cursor/chats/599b03ad2762d6f2f020fff7185f6cd5/0f47cb81-a946-4fd5-8e3f-84d658dee3ae/store.db` |

### Comments

#### chuckles — 2026-08-03T22:42:38.144Z
@susan

1. Confirm the split: **AST-1164** = provider timeout / empty-error / zero-token response hardening; **AST-1163** = hollow name + ANALYSIS tokens — not a duplicate?
2. Which candidate id + job id produced batch `anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a` (for UAT replay)?
3. Timeout policy: keep the existing ~5 minute provider call budget but make failure/cancellation always surface cleanly, or raise/lower the budget via `ASTRAL_CONFIG` as part of this epic?
4. Must the Anthropic mirror ship in the same epic, or DeepSeek-only until a matching Anthropic hang is seen?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
