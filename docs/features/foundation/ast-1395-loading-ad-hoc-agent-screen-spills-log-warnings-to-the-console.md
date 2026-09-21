# AST-1395 — loading ad hoc agent screen spills log warnings to the console

<!-- linear-archive: AST-1395 archived 2026-08-31 -->

## Linear archive (AST-1395)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1395/loading-ad-hoc-agent-screen-spills-log-warnings-to-the-console  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Opening the Agent Ad Hoc admin screen (no candidate selected, no Test/run) causes `resolve_tokens` to walk task prompts such as `topic_menu_preamble_confirm` and `vet_inflow_discovery`. Candidate tokens (`{$FIRST_NAME}`, `{$FULL_NAME}`) have no source on that load, so the server console fills with WARNING lines of the form `Token {$FIRST_NAME} resolved to empty (path=first, task=…)`.

## To-be

Loading Agent Ad Hoc does not emit empty-token WARNINGs. Preview/list resolve on that page either skips substitution when there is no candidate in context, or treats expected-empty candidate tokens as silent. Real `do_task` / Test runs that have a candidate still warn when a name token is unexpectedly empty.

## Proposed steps

1. Confirm the Agent Ad Hoc page-load path (list or Preview API) is what calls `resolve_tokens` for those `task_key`s with no candidate.
2. Gate the empty-token WARNING: no candidate in context → do not warn (and/or do not resolve candidate-source tokens).
3. Leave the warning in place for actual runs that have a `candidate_id` but missing name fields.
4. Spot-check Manage Tasks preview so a real missing-name bug there still surfaces.

## Original brief

Token {$FIRST_NAME} resolved to empty (path=first, task=topic_menu_preamble_confirm)
Token {$FULL_NAME} resolved to empty (path=full, task=vet_inflow_discovery)
Token {$FIRST_NAME} resolved to empty (path=first, task=vet_inflow_discovery)
Token {$FIRST_NAME} resolved to empty (path=first, task=vet_inflow_discovery)
Token {$FIRST_NAME} resolved to empty (path=first, task=vet_inflow_discovery)
Token {$FIRST_NAME} resolved to empty (path=first, task=vet_inflow_discovery)

### Comments

#### susan — 2026-08-16T02:07:31.043Z
513

#### chuckles — 2026-08-16T02:04:55.127Z
Ancestor candidates (ranked — pick one, ask about one, or reject the lot):

1. AST-292 — Create Anthropic Ad Hoc. The screen itself.
2. AST-515 — Ad Hoc workbench Test/Preview (parent AST-514). Preview/assembly is the likely load-time call site; Preview-only is already called out as no-ledger.
3. AST-514 — Include Ad Hoc UI calls in Execution History. Parent of 515; owns `adhoc-` workbench semantics.
4. AST-538 — Improve quality of debug logging. Agent Ad Hoc rename + console contract while authoring from that screen; these WARNINGs are ungated noise on load.
5. AST-574 — Support tokens in Agent prompts. Runtime + admin preview resolve for `{$FIRST_NAME}` in agent/task assembly.
6. AST-631 — Runtime token resolution in agent content (child of 574). Wires `resolve_tokens` into preview paths.
7. AST-513 — Token gap correction. Owns the standard empty-token WARNING (`Token {$…} resolved to empty`).
8. AST-1103 — Replace "the candidate" with `{$FIRST_NAME}` in seeds (incl. preamble/topic-menu). Why those tasks now warn when resolved with no candidate.
9. AST-1075 — Estelle preamble confirm. Owns `topic_menu_preamble_confirm` (named in the log).
10. AST-879 / AST-880 / AST-815 — `vet_inflow_discovery` (named in the log). Company vet prompt, not the Ad Hoc load path.
11. AST-527 — Daisy-chain empty-token console warnings. Same log family, hop trigger not screen load.
12. AST-1148 — From-block resolve. Notes that `resolve_tokens` warns per empty token and would spam the log.
13. AST-1163 / AST-1192 — Empty `{$FIRST_NAME}` on `anticipate_scan`. Same warning, different cause (token-view with a candidate present).
14. AST-555 — Agent Ad Hoc nav rename (child of 538). Label only; weak.

no other ancestor candidate found in this round's four greps.

---

_Implementation detail may live in git history on `origin/dev`._
