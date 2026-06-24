# AST-694 — Deepseek brain model changes

<!-- linear-archive: AST-694 archived 2026-06-23 -->

## Linear archive (AST-694)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-694/deepseek-brain-model-changes  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

[AST-491](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek) landed DeepSeek brain tiers (Little / Medium / Big) on `origin/dev`, but the shipped DeepSeek mapping for **Medium** does not match Susan's current product intent: Medium should run on **deepseek-v4-pro** without thinking, not v4-flash with thinking. This epic retargets the config-driven DeepSeek tier table so the three brain settings match Susan's ladder—flash for lightweight work, pro without thinking for mid-tier, pro with thinking for the heaviest tier—without agents or admin users picking vendor SKUs directly.

## Functional scope

* **DeepSeek tier table:** Product configuration for `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"]` maps **Little**, **Medium**, and **Big** exactly as Susan specified: Little → `deepseek-v4-flash` with thinking off; Medium → `deepseek-v4-pro` with thinking off; Big → `deepseek-v4-pro` with thinking on.
* **Runtime routing:** When the active LLM provider is DeepSeek, every agent call that resolves a brain setting uses the updated tier mapping automatically—the shared agent dispatch path continues to resolve tier → vendor model and thinking flags from config; callers do not pass vendor SKUs.
* **Cost attribution:** DeepSeek timesheet rows for calls after deploy use pricing metadata for the vendor model actually invoked per tier (flash vs pro, thinking vs non-thinking), so admin cost views stay aligned with the new mapping.
* **Admin tier catalog:** Manage Agents continues to expose the three brain settings (Little / Medium / Big) from config; tier labels and agent assignments are unchanged—only what each tier resolves to at runtime under DeepSeek changes.
* **Anthropic parity preserved:** Anthropic tier mappings (Haiku / Sonnet / Opus equivalents) stay as shipped on `origin/dev`; this epic changes DeepSeek mappings only.

## Boundaries

* **Not in scope:** Switching `active_provider`, adding providers, changing TASK_CONFIG prompts/schemas/grading, or per-agent overrides outside the existing brain_setting column.
* **Not in scope:** Retargeting Anthropic tier mappings or changing the Little / Medium / Big tier names.
* **Not in scope:** Backfilling or recalculating historical timesheet costs for calls made under the old Medium mapping.
* **Must not break:** Agents still configured with Little / Medium / Big; Anthropic routing when `active_provider` is anthropic; batch locking, `agent_data`, dispatch ledger, and timesheet storage from AST-491 / AST-324.
* **Config discipline:** Allowed tiers and DeepSeek SKU/thinking flags remain literals in product config per code rules; API keys stay environment-only.

## Acceptance criteria

1. With `active_provider` set to DeepSeek, resolving **Little** yields vendor model `deepseek-v4-flash` with thinking disabled.
2. With `active_provider` set to DeepSeek, resolving **Medium** yields vendor model `deepseek-v4-pro` with thinking disabled.
3. With `active_provider` set to DeepSeek, resolving **Big** yields vendor model `deepseek-v4-pro` with thinking enabled.
4. A representative agent task configured as **Medium** completes successfully on DeepSeek after the change and logged call metadata shows `deepseek-v4-pro` without thinking mode.
5. A representative agent task configured as **Big** completes successfully on DeepSeek after the change and logged call metadata shows `deepseek-v4-pro` with thinking mode enabled.
6. New DeepSeek timesheet rows after deploy record costs using the pricing entry for the vendor model actually used (flash for Little; pro for Medium and Big).
7. With `active_provider` set to Anthropic, Little / Medium / Big still resolve to the existing Anthropic model aliases with no regression in a representative graded task.
8. Automated tests that assert DeepSeek tier resolution are updated to match the new Medium mapping and remain green on the epic branch.

## Dependencies and blockers

* [AST-491](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek) (Done on `origin/dev`): brain_setting tiers, DeepSeek client routing, and multi-provider timesheets must already be present—this epic is a mapping correction on that foundation.
* none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-694 (parent) | ftr/AST-694-deepseek-brain-model-changes |
| AST-695 | sub/AST-694/AST-695-deepseek-brain-tier-mapping-update |

**Epic worktree:** `astral-AST-694/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 00314c4a-a2d2-400d-91d3-07b851d07b15 |
| Betty | qa | 521c5245-b5bf-4b2f-88e5-010c13a5cc73 |
| Radia | review | be24c489-76ca-4f41-9b4c-e1c0c02e7099 |

---

## Original brief

Change the brain models to mean this:

1. Little: deepseek-v4-flash, no thinking
2. Medium: deepseek-v4-pro, no thinking
3. Big: deepseek-v4-pro, thinking

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
