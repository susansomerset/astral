# AST-1985 — Do not duplicate the candidate prefix when already present.

<!-- linear-archive: AST-1985 archived 2026-10-13 -->

## Linear archive (AST-1985)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1985/do-not-duplicate-the-candidate-prefix-when-already-present  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Original report (evidence, verbatim)

```
[astral-somerset][astral-somerset][astral-somerset][astral-somerset][astral-somerset]NOTE: Please see "AGENT MESSAGE" below for your system context prompt and instructions. Please review all of the following content thoroughly before proceeding with your work.
```

## As-is

The AST-1639 cache-isolation marker `[astral-<candidate id>]` is prepended by `_system_text_with_candidate_prefix` in `src/core/agent.py` unconditionally — it never checks whether the system text already begins with that marker. Any path that feeds already-prefixed system text back through the helper (workbench Test sending the prefixed `preview_prompt` system text back into `run_adhoc` / `_store_prompt_blocks`, re-running from a stored SYSTEM `agent_data` row, etc.) stacks another copy, so the system prompt sent to the provider and stored in `agent_data` grows `[astral-somerset][astral-somerset]…` — five copies in the sample above.

## To-be

The system prompt carries exactly one `[astral-<id>]` marker at byte zero, no matter how many times the text has passed through preview / store / assembly. If the text already starts with the marker, the helper leaves it alone instead of adding another copy. The wire text, the `preview_prompt` text, and the stored SYSTEM row stay byte-identical (the AST-1639 parity contract still holds).

## Proposed steps

1. Make `_system_text_with_candidate_prefix` idempotent: strip any leading run of `[astral-…]` markers from `system_content`, then prepend exactly one `[astral-<cid>]`. Keep the existing fail-closed `ValueError` on a missing or blank id.
2. **Open question for Susan:** should the strip remove only markers matching *this* candidate's id, or any leading `[astral-*]` marker? Removing any marker is safer for cache isolation, because a prompt carried over from another candidate would otherwise keep that candidate's id at byte zero. Matching only this id is narrower.
3. Leave every call site as-is: `do_task`, the workbench `run_adhoc` wrapper, `preview_prompt`, and assembly. Once the helper is idempotent, the existing "assembly prefixes again" store-site applications are harmless.
4. Betty adds a component test next to `TestAst1639CandidateIdSystemPrefix` showing that already-prefixed input (including a multi-prefixed input like the sample) comes out with exactly one marker. Existing AST-1639 tests must stay green.

## Component scope

* `src/core/agent.py` — modified: `_system_text_with_candidate_prefix` is the only place the marker is built, so making it idempotent fixes every caller (wire, store, preview) at once.
* `tests/component/core/test_agent.py` — modified (Betty-owned, test tree): new case(s) in the AST-1639 prefix suite for already-prefixed input.

## Technical scope

* `src/core/agent.py` — modified function `_system_text_with_candidate_prefix`: normalize away existing leading `[astral-…]` marker(s) before prepending exactly one, so repeated passes cannot stack copies. No new tables or fields, and no call-site signature changes.
* `tests/component/core/test_agent.py` — new test function(s) for idempotence: one already-prefixed input and one five-times-prefixed input should each come out with a single marker.

## Ancestor candidates

- [X] [AST-1639](https://linear.app/astralcareermatch/issue/AST-1639) — Candidate-id system-prompt prefix (child that introduced `_system_text_with_candidate_prefix`; doc `docs/features/agent/ast-1639-candidate-id-system-prompt-prefix.md`; Archive)
- [ ] [AST-1638](https://linear.app/astralcareermatch/issue/AST-1638) — Prefix every agent system prompt with the candidate ID for model-agnostic cache isolation (parent epic; doc `docs/features/agent/ast-1638-prefix-every-agent-system-prompt-with-the-candidate-id-for-model-agnostic-cache-isolation.md`; Archive)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
