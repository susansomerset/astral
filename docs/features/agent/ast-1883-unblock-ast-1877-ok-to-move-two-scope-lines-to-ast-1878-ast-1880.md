# AST-1883 — Unblock AST-1877: OK to move two Scope lines to AST-1878 / AST-1880

<!-- linear-archive: AST-1883 archived 2026-10-07 -->

## Linear archive (AST-1883)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1883/unblock-ast-1877-ok-to-move-two-scope-lines-to-ast-1878-ast-1880  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1851; blocks: AST-1877; related: AST-1878; related: AST-1880

### Description

Ada's plan for [AST-1877](https://linear.app/astralcareermatch/issue/AST-1877) (#1, catalogs + compat client) is otherwise done, but she's asking for two scope moves between sibling tickets. That changes the approved child split, so it needs your OK.

**1. Move "agent model field in repo-admin columns" from #1 to #2 (**[AST-1878](https://linear.app/astralcareermatch/issue/AST-1878)**).**
Adding the column name to `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` on #1 breaks Revert-to-file and export on #1's branch, because the DB column and the `agent.json` seed values only arrive in #2. Moving it means `config.py` is touched by #2 as well: a **second** named exception to the one-file-one-child rule (you approved only #4's).

**2. Give the leftover DeepSeek-named functions in** `src/utils/cost_calculator.py` **an owner.**
#1 has to keep `deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts` and `calculate_cost_components_deepseek` (as catalog-backed wrappers), because `deepseek.py` and `database.backfill_deepseek_agent_timesheet_costs` still import them. No later child has `cost_calculator.py` in scope, so parent AC 2's `deepseek` grep would keep hitting them. Proposed fix: add "delete the DeepSeek-named wrappers in `cost_calculator.py`" to #4 ([AST-1880](https://linear.app/astralcareermatch/issue/AST-1880)), and have #2 switch the backfill to `calculate_cost_components_from_counts`.

**Answer needed:** approve both moves, or say which one to change. Reply here and move this ticket to **Done**. The agents will amend the child Scopes. You don't need to edit anything or push.

Neither [AST-1877](https://linear.app/astralcareermatch/issue/AST-1877/modelserver-catalog-shared-compat-client-support-openrouter-api-models) nor the parent [AST-1851](https://linear.app/astralcareermatch/issue/AST-1851/support-openrouter-api-models-for-agent-work) is assigned to you. Ada keeps the child, and it waits behind this gate

Approved by Susan.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
