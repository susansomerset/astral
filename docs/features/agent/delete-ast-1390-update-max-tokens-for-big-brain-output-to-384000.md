# AST-1390 — Update max tokens for big brain output to 384,000

<!-- linear-archive: AST-1390 archived 2026-08-31 -->

## Linear archive (AST-1390)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1390/update-max-tokens-for-big-brain-output-to-384000  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 3  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1294; related: AST-1290

### Description

## Purpose

Big-brain DeepSeek hops currently share a modest output budget with Medium (same vendor model default, often further capped by a stored agent-row value). Thinking and the visible answer share that budget, so Big cannot actually think and finish. Susan wants Big to cook: DeepSeek Big output max tokens is 384,000.

## Functional scope

* **Big output budget is 384,000.** When the active provider is DeepSeek and the agent's brain setting is Big, the output token budget for that hop is 384,000. That number lives in product config on the Big DeepSeek tier — not on the shared v4-pro model default (Medium uses the same SKU and must keep its current default).
* **Stored agent max tokens cannot starve Big.** If an agent row or model default is lower than 384,000, a DeepSeek Big hop still sends at least 384,000. An agent-row value higher than 384,000 may still win (floor, not a hard cap).
* **Little and Medium unchanged.** Their budgets, models, and thinking flags stay as they are.
* **Debug honesty.** Existing `debug=True` hop traces already record the max tokens actually sent. After this change, a DeepSeek Big hop's debug line shows 384000 (or higher if the agent row is higher). No new debug shape.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — the 384,000 figure is a named config literal on the DeepSeek Big tier, not an inline magic number in core or the provider client.
  * `pattern.layers.import-discipline` — core resolves the budget and delegates the provider call; external does not own the product number.
* **New patterns proposed**
  * none
* **Applicable statutes**
  * universal orchestration set (git flow, status gates, Betty owns tests, engineer assignee through resolve, plan-is-bible) — this is product code.
  * `astral.config.config-source-of-truth` — behavior-driving limit lives in config literals.
  * `astral.standards.no-hardcoded-sets` — 384000 is a named config value, not a scattered literal.
  * `astral.agent.do-task-delegation` — budget is resolved on the shared agent hop path; callers do not pass vendor SKUs or token caps.
  * `astral.layers.core-vs-external-bright-line` — provider I/O stays in external; core decides the cap.
  * `astral.layers.import-direction` — no new layer violations to place the number.
  * `astral.standards.in-scope-only` — only Big DeepSeek output budget; no adjacent timeout/UI/thinking-policy work.
  * `astral.standards.debug-contract-gated` — no new ungated debug; existing debug max-tokens line must reflect the raised budget.
  * `astral.docs.features-single-file-per-ticket` — one plan doc on the child.
  * `astral.git.engineer-test-tree-ban` — product child does not edit tests.

## Boundaries

* **Not Anthropic Big.** 384,000 is DeepSeek's number from the vendor advice in the original brief. Anthropic Big (Opus) keeps its current default. Do not send 384,000 on Anthropic hops.
* **Do not change the shared v4-pro model default.** Medium also uses deepseek-v4-pro; raising that default would cook Medium too.
* **Do not reverse AST-1380 Decision A.** Craft-rubric DeepSeek Big hops still turn thinking off so JSON criteria are not starved. This epic raises the budget; it does not re-enable thinking on craft.
* **Do not change thinking, temperature, or top_p.** DeepSeek Big already enables thinking with max reasoning effort. Temperature is already omitted while thinking is on. The vendor snippet's `temperature: 0.0` / `top_p: 1.0` / `extra_body` are not additional product changes.
* **Do not change wall-time budgets.** Per-call provider timeout and gunicorn timeout stay as they are. Acceptance is that Big *requests* 384,000 tokens, not that a full 384k generation always finishes inside the current time box.
* **Not Admin UI / seed backfill.** Manage Agents display of default max tokens and rewriting stored agent-row max_tokens are out of scope — the hop floor covers runtime.
* **Must not break:** Little/Medium routing (AST-694 ladder), JSON `max_tokens` hard-fail (AST-903), craft 32,000 floor (still a floor; Big 384,000 is higher), timesheets, `active_provider` switching.

## Acceptance criteria

1. With DeepSeek active, a representative **Big** agent hop sends `max_tokens` of **at least 384000** to the provider — including when the agent row's stored max tokens is lower (e.g. 16000).
2. With DeepSeek active, a representative **Medium** hop still sends the current Medium budget (not 384000).
3. With DeepSeek active, a representative **Little** hop is unchanged.
4. With Anthropic active, Big still uses the existing Anthropic default — not 384000.
5. With `debug=True`, the existing max-tokens debug line on a DeepSeek Big hop shows 384000 (or the higher agent-row value).
6. Craft-rubric DeepSeek Big hops still disable thinking (AST-1380); they may now send 384000 because of the Big floor, which is fine.

## Dependencies and blockers

none. Adjacent Done work (AST-1379 / AST-1380 / AST-903) is already on `origin/dev`. In-flight Agent tickets AST-1294 / AST-1290 are html-link completeness — no overlap.

## Open questions

none.

## Proposed child tickets

One inseparable vertical slice — the 384,000 literal is useless unless the Big hop actually sends it, and the hop must not invent the number outside config.

#### 1: **DeepSeek Big output budget - Ada**

Owns the DeepSeek Big tier's 384,000 output budget in config and the shared agent hop applying it as a floor over agent-row / model default when provider is DeepSeek and brain is Big. Does not own Little/Medium, Anthropic, craft thinking policy, timeouts, or Admin UI.

**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.agent.do-task-delegation`, `astral.standards.in-scope-only`.

**Estimate: 3**

---

## Original brief

Let 'em cook!  😀

Advice from deepseek:

```
BRAIN_BIG: {
    "vendor_model": "deepseek-v4-pro",
    "reasoning_effort": "max",
    "max_tokens": 384000,
    "extra_body": {"thinking": {"type": "enabled"}},
    "temperature": 0.0,
    "top_p": 1.0
}
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
