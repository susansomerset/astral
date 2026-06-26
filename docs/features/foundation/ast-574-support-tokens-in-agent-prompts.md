# AST-574 — Support tokens in Agent prompts

<!-- linear-archive: AST-574 archived 2026-06-23 -->

## Linear archive (AST-574)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-574/support-tokens-in-agent-prompts  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan authors reusable agent persona prompts in Manage Agents (for example Grace's system voice). Those prompts should personalize to the active candidate the same way task prompts do — using `{$FIRST_NAME}`, pronoun tokens, and other registered merge tokens — so one agent template works for every candidate without maintaining duplicate agent rows. Today, candidate tokens in agent `content` resolve only when that content is used directly as the system block; when a task's system prompt is `{$SELECTED_AGENT}` (the common pattern from [AST-305](https://linear.app/astralcareermatch/issue/AST-305/add-system-prompt-tab-to-manage-tasks)), the injected agent body is substituted raw and tokens like `{$FIRST_NAME}` reach the model unresolved. Manage Agents also lacks the token autocomplete authoring surface that Manage Tasks already has.

## Functional scope

* **Runtime resolution in agent content.** Whenever agent `content` becomes part of an assembled prompt — as the direct system block or as the value behind `{$SELECTED_AGENT}` — every `{$TOKEN}` in that agent body resolves using the same registry and call context as task prompt segments (candidate, config, output-type, and job-scoped tokens when a job is in scope for the call).
* `{$SELECTED_AGENT}` **path.** After the assigned agent's stored content is injected, that text is fully token-resolved before the model sees it; unresolved candidate tokens must not pass through when the outer prompt references `{$SELECTED_AGENT}`.
* **Cross-path parity.** Production agent calls, chain hops, Manage Tasks preview, and other admin preview paths that already resolve task prompts apply the same agent-body token rules so what Susan authors in Manage Agents matches runtime behavior.
* **Manage Agents authoring.** The Manage Agents add/edit content field uses the shared token autocomplete component and loads the token list appropriate for static agent templates: all registry tokens except chain/hop tokens (`{$CALLER_*}` and `{$SELECTED_AGENT}`), which remain task-prompt concerns only.
* **Candidate-scoped preview.** Manage Agents offers a resolved preview for the selected candidate (same candidate context as Manage Tasks) so Susan can verify persona copy before saving.

## Boundaries

* **No new tokens.** This ticket wires existing `TOKEN_SOURCES` into agent content resolution; pronoun tokens ship under [AST-573](https://linear.app/astralcareermatch/issue/AST-573/pronoun-selection) and become available in agent prompts automatically once registered.
* **No chain tokens in agent rows.** Agent templates are static persona text; `{$CALLER_*}` and `{$SELECTED_AGENT}` are not offered in the Manage Agents token picker and are not expected in agent `content`.
* **No nested agent indirection.** Does not resolve tokens inside a hypothetical agent body that itself references another agent; one assigned agent's `content` only.
* **No prompt backfill mandate.** Shipping resolution does not require updating every existing agent row — Susan edits templates as needed.
* **Task segments unchanged.** Behavior of task-only prompt fields beyond fixing agent-body resolution stays as today.
* **Must not break** tasks that use `{$SELECTED_AGENT}` with agent bodies that contain no merge tokens, or tasks that use agent `content` directly as the system block with tokens already resolving today.

## Acceptance criteria

1. An agent whose `content` is `Hi, you're Grace. You're helping {$FIRST_NAME} find a great role.` resolves `{$FIRST_NAME}` to the active candidate's first name in a production `do_task` call when that agent content is the direct system block.
2. Same agent content with a task `system_prompt` of `{$SELECTED_AGENT}` resolves `{$FIRST_NAME}` identically — the model never receives a literal `{$FIRST_NAME}` substring from the agent body on either path.
3. Manage Tasks preview for a task using `{$SELECTED_AGENT}` shows the same resolved agent-body text as production for the preview candidate.
4. Manage Agents edit UI provides token autocomplete for merge tokens (excluding chain/hop tokens listed in Boundaries).
5. Manage Agents resolved preview for the selected candidate shows agent `content` with tokens substituted; saving and reloading preserves the template with literal `{$TOKEN}` placeholders intact in storage.
6. Agent prompts that contain no merge tokens behave unchanged across all call paths.

## Dependencies and blockers

* Existing `TOKEN_SOURCES`, `resolve_tokens`, and agent/task prompt assembly ([AST-279](https://linear.app/astralcareermatch/issue/AST-279/establish-agent-tokens), [AST-304](https://linear.app/astralcareermatch/issue/AST-304/add-parsable-chain-tokens-to-resolve-tokens), [AST-305](https://linear.app/astralcareermatch/issue/AST-305/add-system-prompt-tab-to-manage-tasks), AST-455, AST-513).
* [AST-573](https://linear.app/astralcareermatch/issue/AST-573/pronoun-selection) (pronoun tokens) is related but not blocking — agent token resolution works for tokens that already exist; pronoun tokens become usable in agent prompts when [AST-573](https://linear.app/astralcareermatch/issue/AST-573/pronoun-selection) lands.
* None blocking definition approval.

## Open questions

none.

---

## Original brief

Example, "Hi, you're Grace. You're helping {$FIRST_NAME} find a great role for the next stage in {$POSSESSIVE_PRONOUN} career."

### Comments

#### chuckles — 2026-06-14T18:54:56.883Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-636** | Manage Agents {$ token autocomplete dropdown missing |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-14T18:32:56.816Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-574 (parent) | ftr/ast-574-support-tokens-in-agent-prompts |
| AST-631 | sub/AST-574/AST-631-runtime-token-resolution-in-agent-content |
| AST-632 | sub/AST-574/AST-632-manage-agents-token-autocomplete-and-preview |
| AST-636 | sub/AST-574/AST-636-uat-manage-agents-token-autocomplete-dropdown-missing |

**Epic worktree:** `astral-AST-574/` — one active sub checked out at a time.

**Parent:** AST-574

— Chuckles

#### susan — 2026-06-14T18:31:35.009Z
There is no token lookup list when I type {$ as there is for manage tasks. Please add that.

#### chuckles — 2026-06-14T17:49:10.403Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-574 (parent) | ftr/ast-574-support-tokens-in-agent-prompts |
| AST-631 | sub/AST-574/AST-631-runtime-token-resolution-in-agent-content |
| AST-632 | sub/AST-574/AST-632-manage-agents-token-autocomplete-and-preview |

**Epic worktree:** `astral-AST-574/` — one active sub checked out at a time.

**Parent:** AST-574

**Sequencing:** AST-632 blockedBy AST-631 (backend token resolution before Manage Agents UI).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
