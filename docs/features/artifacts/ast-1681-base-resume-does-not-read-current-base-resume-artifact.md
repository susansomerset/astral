# AST-1681 — {$BASE_RESUME} does not read current base_resume artifact

<!-- linear-archive: AST-1681 archived 2026-09-24 -->

## Linear archive (AST-1681)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1681/dollarbase-resume-does-not-read-current-base-resume-artifact  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

When {$BASE_RESUME} is parsed, the result going into the prompt is blank.

## As-is

When a prompt containing `{$BASE_RESUME}` is resolved, the substituted value is empty (blank string) even when the candidate has a current base_resume operative artifact that should ground the token.

## To-be

`{$BASE_RESUME}` resolves to the section-id-keyed JSON body of the candidate’s current `candidate.artifacts.base_resume` operative artifact (same contract as AST-607 / AST-1587), not blank, whenever that current row exists and the token view carries a candidate id.

## Proposed steps

1. Confirm the dict passed into `resolve_tokens` → `format_base_resume_for_token` includes `_astral_candidate_id` / `astral_candidate_id` — after [AST-1587](https://linear.app/astralcareermatch/issue/AST-1587/base-resume-consumer-rewires-builder-token-live-helpers-implement), a missing cid makes the serialize path return `""` by design.
2. With cid present, confirm `get_candidate_current(cid, "candidate.artifacts.base_resume")` returns the operative body; if the current row is missing, blank is expected — fix save/hydrate or the call site that should have written current.
3. If agent/task token views omit the candidate id, thread it into the view the same way other craft paths already do before `resolve_tokens`.
4. Re-run a prompt that embeds `{$BASE_RESUME}` and confirm a non-empty section-id JSON payload lands in the model input.

## Component scope

* `src/core/candidate.py` — modified: `format_base_resume_for_token` / `candidate_id_for_current_read` / `load_pilot_base_resume_for_candidate` are where blank serialization originates after the current-read rewire.
* `src/utils/config.py` — modified only if the `resolve_tokens` `resume_sections_json` branch or token-view construction fails to pass a cid-bearing candidate dict into that serialize path.
* Agent/task token-view builders that feed `resolve_tokens` (likely under `src/core/` craft/consult paths that set `_astral_candidate_id`) — modified if the view omits candidate id while other tokens still resolve.

## Technical scope

* `src/core/candidate.py` — modified function(s): ensure `format_base_resume_for_token` (and helpers it relies on) load operative current when cid is present and do not collapse to empty for a recoverable view shape.
* `src/utils/config.py` — modified function only if needed: `resolve_tokens` / its serialize branch must hand a cid-bearing candidate dict to `format_base_resume_for_token`.
* Token-view construction — modified function(s) that build the candidate dict for prompt resolve so `_astral_candidate_id` is always set when an astral candidate is in scope.

## Ancestor candidates

- [X] [AST-1587](https://linear.app/astralcareermatch/issue/AST-1587/base-resume-consumer-rewires-builder-token-live-helpers-implement) — base-resume consumer rewires (`format_base_resume_for_token` → `get_candidate_current`; owns the `{$BASE_RESUME}` serialize path that returns blank on cid/operative miss)
- [ ] [AST-1576](https://linear.app/astralcareermatch/issue/AST-1576/generic-save-candidate-data-agent-craft-persist-rewire-implement) — generic `save_candidate_data` + `hydrate_operative_base_resume_for_response` on `get_candidate` (kept token/hydrate correct without denormalized blob write)
- [ ] [AST-1586](https://linear.app/astralcareermatch/issue/AST-1586/current-read-helper-get-hydrate-pattern-scope-revise-implement) — `get_candidate_current` helper that AST-1587’s token path depends on
- [ ] [AST-1585](https://linear.app/astralcareermatch/issue/AST-1585/ui-contact-pilot-base-resume-operative-resolve-implement) — Contact/UI operative resolve for `{$BASE_RESUME}` (pin/miss → gap, no blob fallback)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
