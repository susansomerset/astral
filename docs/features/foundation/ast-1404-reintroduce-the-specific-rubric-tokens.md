# AST-1404 — Reintroduce the specific rubric tokens

<!-- linear-archive: AST-1404 archived 2026-09-09 -->

## Linear archive (AST-1404)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1404/reintroduce-the-specific-rubric-tokens  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Prompt authors can no longer name a specific rubric in agent task text. AST-723 collapsed every per-rubric prompt token into a single `{$RUBRIC_VECTORS}` that follows whichever task is running, so a GET prompt cannot ask for GET, a LIKE prompt cannot ask for LIKE, and a non-owner task cannot pull a named rubric at all. This epic puts five named tokens back on the prompt-token surface so Susan can insert the right rubric by name. Outcome: those five names are pickable and resolve to that rubric’s current vectors for the candidate in context.

## Functional scope

Prompt authors can insert `{$GET_RUBRIC}`, `{$DO_RUBRIC}`, `{$LIKE_RUBRIC}`, `{$JD_RUBRIC}`, and `{$PREFILTER_RUBRIC}` from the same token pickers already used for other prompt tokens.

At runtime, each named token is replaced with the current vectors for that named rubric for the candidate in context — GET, DO, LIKE, the job-description evaluate rubric, and the company-watch prefilter rubric — independent of which task is running. A GET token in a LIKE prompt still yields GET.

Named tokens serialize the same way the generic rubric token already serializes rubric rows, so authors see the same kind of rubric text they would from `{$RUBRIC_VECTORS}` when that token’s owner matches.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: token names and any owner pin live in the existing prompt-token registry (config as source of truth). Pickers already derive from that registry; do not invent a second list in the UI. Rubric body still comes from current rubric-vector rows via the existing rubric-token read path (same assembled shape consult and Artifacts already use).
* **New patterns proposed** — none. Pinning a named owner on a rubric token is a small extension of the existing `source: rubric` registry entry, not a new catalog shape.
* **Applicable statutes** — `astral.config.config-source-of-truth` (names and owner pins in config, not scattered); `astral.standards.no-hardcoded-sets` (no inline token-name sets); `astral.standards.in-scope-only` (do not restore unlisted rubric token names); `astral.layers.ui-config-driven-business-logic` (pickers read the registry); `astral.agent.do-task-delegation` (substitution stays on the existing prompt-resolution path inside `do_task`, not a new core/UI assembly).

## Boundaries

Does not restore `{$JOBLIST_RUBRIC}`, `{$COMPANY_PREFILTER}`, or `{$JOBDESC_RUBRIC}` as those names. `{$JD_RUBRIC}` is the job-description evaluate rubric only, not the meteorite dealbreaker rubric. `{$PREFILTER_RUBRIC}` is the company-watch prefilter rubric (the old company-prefilter token under the new name).

Does not add meteorite or job-list rubric tokens.

Does not retire `{$RUBRIC_VECTORS}`. That token still follows the running task’s rubric owner.

Does not change how rubric vectors are stored, crafted, scored, or shown on Artifacts. Does not change vector-feedback / craft-prompt feedback injection (AST-1378). Does not rewrite seed agent-task prompt bodies — tokens become available; Susan inserts them (or a later seed ticket does).

Does not break empty-candidate Ad Hoc silence (AST-1396): a named rubric token with no candidate in context must not spam missing-token warnings.

## Acceptance criteria

1. The five names `GET_RUBRIC`, `DO_RUBRIC`, `LIKE_RUBRIC`, `JD_RUBRIC`, and `PREFILTER_RUBRIC` appear in the Manage Agents and Manage Tasks prompt-token pickers.
2. Preview or run of a prompt containing `{$GET_RUBRIC}` (and each of the other four) with a candidate that has that rubric substitutes that rubric’s current vectors — not another rubric’s, and not an empty stub when vectors exist.
3. `{$GET_RUBRIC}` on a non-GET task still substitutes GET vectors (named pin, not running-task owner). Same independence for the other four names.
4. `{$RUBRIC_VECTORS}` still substitutes the running task’s owner rubric, unchanged.
5. `JOBLIST_RUBRIC`, `COMPANY_PREFILTER`, and `JOBDESC_RUBRIC` are not in the picker and are not registered.
6. Ad Hoc / preview with no candidate in context does not emit empty-token warnings for these names (same contract as AST-1396).

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

Functional scope has 3 capabilities and 1 child — intentional: picker, registry, and resolve are the same token-registry surface and must ship together for UAT.

#### 1: **Named rubric prompt tokens - Ada**

Register the five named tokens on the prompt-token registry, pin each to its rubric owner, and resolve them through the existing current-vector read path so picker + runtime substitution ship together. Does not rewrite seed prompt text, does not restore unlisted legacy names, and does not change `{$RUBRIC_VECTORS}`.
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`
**Estimate:** 3

---

## Original brief

We need {$GET_RUBRIC}, {$DO_RUBRIC}, {$LIKE_RUBRIC}, {$JD_RUBRIC}, {$PREFILTER_RUBRIC} available for agent prompt tokenization.  Others are not required at this time.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
