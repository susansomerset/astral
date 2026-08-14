# AST-1181 — Generate issues for Meteorite Changes

<!-- linear-archive: AST-1181 archived 2026-08-14 -->

## Linear archive (AST-1181)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1181/generate-issues-for-meteorite-changes  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

* Rename the task to meteorite_email
* When we send content to the AI, send just visible text and links as we do for JD scrapes
* Rename Job Review to Gaze Review as a grouping/section
* Add a sibling as "Meteorite Review"
* Update the grouping content in agent_task to group the meteorite content together.  
* Support task aliases in task config, where we add a "master_task_key" to the real task in config, but the alias can be used in the UI for different trigger states (instead of duplicating and making prompt management insane) and most importantly, organized under different groupings/sections so they can all sit together without replicating task content or logic.
* Confirm the UI reflects the groupings and sequences set in the agent_task table, and the UI populates an alphabetical listing of task keys (and aliases) wherever task_keys appear in dropdown lists.
* Verify there are no hard-coded or extraneous lists or sequences relating to this, the grouping and ordering should all be data-driven, and the config should handle aliases cleanly. 
* Review the changes recently made for evaluate_meteorite and incorporate the work in the test cases and validate against patterns and statutes.

### Comments

#### chuckles — 2026-08-05T23:09:25.462Z
[check-linear] answered — AST-1182–1186 standalone Enhancement, relatedTo this (not subissues)

#### susan — 2026-08-05T23:07:41.556Z
@chuckles Please move these tickets to be independent Enhancement-type issues, only related to this ticket, not subissues of it.

#### chuckles — 2026-08-05T21:46:15.484Z
[check-linear] answered — filed Discussion (assignee Susan): AST-1182, AST-1183, AST-1184, AST-1185, AST-1186

#### susan — 2026-08-05T21:43:54.070Z
@chuckles Please create new linear issues for this project based on my comments above and put them in discussion assigned to me.

---

_Implementation detail may live in git history on `origin/dev`._
