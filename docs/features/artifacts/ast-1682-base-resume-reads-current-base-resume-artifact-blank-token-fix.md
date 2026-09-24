# AST-1682 — {$BASE_RESUME} reads current base_resume artifact (blank token fix)

<!-- linear-archive: AST-1682 archived 2026-09-24 -->

## Linear archive (AST-1682)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1682/dollarbase-resume-reads-current-base-resume-artifact-blank-token-fix  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1681 — {$BASE_RESUME} does not read current base_resume artifact  
**Blocked by / blocks / related:** parent: AST-1681

### Description

## What this implements

Make `{$BASE_RESUME}` resolve to the candidate’s current `candidate.artifacts.base_resume` operative body (non-blank when current exists and the token view carries a candidate id), instead of substituting an empty string into agent prompts.

## Citations

Approved ancestor **AST-1587** — `docs/features/foundation/ast-1587-base-resume-consumer-rewires-builder-token-live-helpers.md` (owns `format_base_resume_for_token` → `get_candidate_current` / `{$BASE_RESUME}` serialize path).

## Scope

### Component scope

* `src/core/candidate.py` — modified: `format_base_resume_for_token` / `candidate_id_for_current_read` / `load_pilot_base_resume_for_candidate` are where blank serialization originates after the current-read rewire.
* `src/utils/config.py` — modified only if the `resolve_tokens` `resume_sections_json` branch or token-view construction fails to pass a cid-bearing candidate dict into that serialize path.
* Agent/task token-view builders that feed `resolve_tokens` (likely under `src/core/` craft/consult paths that set `_astral_candidate_id`) — modified if the view omits candidate id while other tokens still resolve.

### Technical scope

* `src/core/candidate.py` — modified function(s): ensure `format_base_resume_for_token` (and helpers it relies on) load operative current when cid is present and do not collapse to empty for a recoverable view shape.
* `src/utils/config.py` — modified function only if needed: `resolve_tokens` / its serialize branch must hand a cid-bearing candidate dict to `format_base_resume_for_token`.
* Token-view construction — modified function(s) that build the candidate dict for prompt resolve so `_astral_candidate_id` is always set when an astral candidate is in scope.

## Acceptance criteria

- [X] 1\. When a prompt containing `{$BASE_RESUME}` is resolved for a candidate that has a current `candidate.artifacts.base_resume` operative artifact and a cid-bearing token view, the substitution is non-empty section-id-keyed JSON (AST-607 contract), not blank.
- [X] 2\. Missing operative current or missing candidate id still yields empty (no blob fallback) — same intentional gap contract as AST-1587 / AST-1585.

## Proposed change (implemented)

- [X] Tighten `is_candidate_token_view` to require `_astral_candidate_id` key present.
- [X] `_token_view_for_do_task` accepts `index`; when `get_candidate(index)` hits, return `build_candidate_token_view(row)`.
- [X] `config.py` audit — no change (`resume_sections_json` → `format_base_resume_for_token` only).
- [X] Contact pin block left untouched; index-as-cid recovery covers Estelle-shaped calls.

## Boundaries

Does not re-author prompts. Does not change `ARTIFACT_CONFIG` membership. Does not revive blob fallback for pilot base_resume. Does not own Contact pin paths beyond any shared helper already in scope.

## Notes for planning

Patch the existing AST-1587 feature doc — do not create a new plan doc. Parent AST-1681 Description has As-is / To-be / Proposed steps. Engineer: Hedy (AST-1587 implementer).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1681-base-resume-does-not-read-current-artifact`, child `sub/AST-1681/AST-1682-base-resume-token-reads-current`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-09-16T19:42:37.350Z
[code-rubric] PROCEED (Commit: f40d9e50) cid threading clean

Overall CLEAN. index-as-cid Contact path threads `_astral_candidate_id` into token view so `{$BASE_RESUME}` current-reads. Sibling AST-1683 [bug-repro] OK. No fix-now.

#### betty — 2026-09-16T19:27:07.694Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — Contact-shaped do_task(index=cid, ctx=None) / library blob without _astral_candidate_id → {$BASE_RESUME} current-read not exercised (AST-1587/607/1192 only cover pre-stamped cid or name tokens)

#### joan — 2026-09-16T19:26:24.279Z
[board-joan]  CANON: OK

context_tokens≈12000

#### hedy — 2026-09-16T19:24:42.277Z
`origin/sub/AST-1681/AST-1682-base-resume-token-reads-current` @ `0275638ee74745749a34d78fd580064a1ecda809` · cid threading plan

---

_Implementation detail may live in git history on `origin/dev`._
