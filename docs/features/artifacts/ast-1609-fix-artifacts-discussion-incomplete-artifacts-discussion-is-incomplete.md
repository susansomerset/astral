# AST-1609 — fix artifacts discussion incomplete (artifacts discussion is incomplete)

<!-- linear-archive: AST-1609 archived 2026-09-22 -->

## Linear archive (AST-1609)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1609/fix-artifacts-discussion-incomplete-artifacts-discussion-is-incomplete  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1607 — artifacts discussion is incomplete  
**Blocked by / blocks / related:** parent: AST-1607

### Description

## What this implements

Fix incomplete Recommended Job Report Discussion: include `anticipate_scan` when it belongs on the build-artifacts discussion path, and only show section headers for hops that have actually run for the job (no hardcoded always-on slots).

## Citations

Ancestor epic AST-1541 (checked). Implementation context: AST-1550 hop walk / `report_discussion_sections`; AST-1551 Discussion pane.

## Scope

## Component scope

* `src/utils/config.py` — modified: `build_artifacts_discussion_hop_task_keys` (or successor) so the Discussion hop set can include `anticipate_scan` without a hardcoded key list.
* `src/ui/api/api_system.py` — modified only if section emission must change with the hop walk / soft-fail path for `report_discussion_sections`.
* `src/ui/frontend/src/components/JobDiscussionPane.tsx` — modified: stop rendering headers for hops with no run/RESPONSE for this job.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — modified only if section filtering or section derivation is wired at the modal rather than inside the pane.

## Technical scope

* `src/utils/config.py` — modified function: change how `build_artifacts_discussion_hop_task_keys` chooses its start / membership so `anticipate_scan` is reachable via live `run_next` (or equivalent live config), not excluded by a fixed start key alone.
* `src/ui/api/api_system.py` — modified function: `state_ui_manifest` Discussion section attach may need to follow the updated hop helper; still soft-fail to `[]` on walk failure.
* `src/ui/frontend/src/components/JobDiscussionPane.tsx` — modified component: filter `sections` (or equivalent) to hops present in this job’s `agent_story` / non-empty RESPONSE before passing to `ReportSectionList`.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — modified only if the filter/derive step lives at wire-up (`report_discussion_sections` + `agent_story`) instead of inside the pane.

## Acceptance criteria

- [X] Discussion can show `anticipate_scan` when that hop has run for the job.
- [X] Discussion does not show headers for build-artifacts hops that have not been run for the job yet.
- [X] Appearance is driven by live story/chain data — not a hardcoded always-visible section set.

## Implemented (make-fix)

- [X] `build_artifacts_discussion_hop_task_keys` — unique live `run_next` parent of `first_task_key` becomes walk start (else start at `first`).
- [X] `JobDiscussionPane` — pass only sections with non-empty RESPONSE to `ReportSectionList`.
- [X] `api_system.py` / `JobAnalysisReportModal.tsx` — unchanged (attach loop + modal wire-up already sufficient).

## Boundaries

Does not redesign Artifacts / Summary / Analysis tabs. Does not resurrect AST-1541's old ftr — this mini-parent ships on its own ftr off origin/dev.

## Notes for planning

Orphaned bug-fix child of AST-1607. Parent as-is/to-be and proposed steps are on AST-1607 Description. Patch the existing AST-1550/AST-1551 feature docs as plan-fix requires (never invent a new plan doc for the epic).

## Git branch (authoritative)

Parent `ftr/AST-1607-artifacts-discussion-incomplete`; child `sub/AST-1607/<this-id>-…`. Created at bug-fix dispatch.

## Radia review-fix (AST-1609)

**Overall:** Product CLEAN at `8e6b7074`. Named publish tip shares AST-1612/AST-1611 ancestry (DISCUSS hygiene). Chuckles accepts bundle for merge.

### Comments

#### radia — 2026-09-09T22:42:47.088Z
[review-fix] Product CLEAN at 8e6b7074 (unique-parent walk + RESPONSE filter). Named ref tip === AST-1612 (tests) — DISCUSS ref hygiene only. Chuckles accepts documented bundle; UT both children then merge-child into ftr.

#### ada — 2026-09-09T22:41:29.578Z
`origin/sub/AST-1607/AST-1609-fix-artifacts-discussion-incomplete` @ `3807d54c` · sibling AST-1612 [bug-repro] green

#### betty — 2026-09-09T22:24:19.940Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md § AST-1550 + docs/test-bible/frontend/components.md § AST-1551 — broken existing tests + missing repro coverage — TestAst1550DiscussionHopKeys asserts anticipate_scan excluded; JobDiscussionPane/JAR AST-1551 assert nine empty-story headers; need revise for unique-parent walk (~10) + filter-to-RESPONSE-only (0 headers when agentStory=[]) and cover anticipate_scan when story has RESPONSE

#### joan — 2026-09-09T22:24:08.360Z
[board-joan]  CANON: OK

#### ada — 2026-09-09T22:23:09.069Z
`origin/sub/AST-1607/AST-1609-fix-artifacts-discussion-incomplete` @ `5479188b` · hop start + filter

---

_Implementation detail may live in git history on `origin/dev`._
