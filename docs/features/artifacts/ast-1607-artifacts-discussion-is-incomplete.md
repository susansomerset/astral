# AST-1607 — artifacts discussion is incomplete

<!-- linear-archive: AST-1607 archived 2026-09-22 -->

## Linear archive (AST-1607)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1607/artifacts-discussion-is-incomplete  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

On the Recommended Job Report Discussion tab, section headers come from the full build-artifacts hop list (`report_discussion_sections` / `build_artifacts_discussion_hop_task_keys`, starting at `resume_artifact_chain.first_task_key` / `contemplate_job`). That walk deliberately omits `anticipate_scan`, and the pane still renders a header for every listed hop even when that job has never run the hop (empty RESPONSE / no matching `agent_story` entry).

## To-be

Discussion headers reflect what actually ran for that job: include `anticipate_scan` when it is part of the build-artifacts discussion for the job, and do not show a section header for a hop that has not been run yet. Appearance of discussion elements is driven by live story / chain data for the job — not a hardcoded always-on section set.

## Proposed steps

1. Widen the Discussion hop source so `anticipate_scan` can appear when it belongs on the build-artifacts discussion path (today the walk starts at `first_task_key` and documents excluding it).
2. Gate which Discussion section headers render for a given job on that job’s `agent_story` (hop has actually run / has a usable RESPONSE) — drop empty always-on slots.
3. Keep labels from live `agent_task.task_name` (fallback `task_key`); do not hardcode a static hop list in UI or config for visibility.

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

## Ancestor candidates

- [X] AST-1541 — Add "Discussion" tab to Recommended Job modal (parent epic for Discussion tab)
- [ ] AST-1550 — Discussion tab config + story task_name (`build_artifacts_discussion_hop_task_keys` excludes `anticipate_scan`; always emits full `report_discussion_sections` on the global manifest)
- [ ] AST-1551 — Discussion pane on Recommended Job Report (renders every manifest section header even when RESPONSE is empty)

## Original report

There are headers for the build artifacts tasks, but it is missing anticipate_scan, and also it should not appear if those tasks have not been run for the job, yet. Don't hard-code the appearance of the discussion elements.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
