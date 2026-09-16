# AST-1444 — Remove navigation filter for selected candidate

<!-- linear-archive: AST-1444 archived 2026-09-09 -->

## Linear archive (AST-1444)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1444/remove-navigation-filter-for-selected-candidate  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators currently lose whole left-nav groups when the selected candidate has not reached a given pipeline state (Artifacts wait on resume-ready; Jobs and Companies wait on active search). That hides destinations they still need to inspect, and it hides *why* the list looks empty. This epic keeps the full candidate-facing nav visible for every selected candidate, and puts that candidate’s live state in the pinned chrome under the picker so the filter is no longer the only way to know where they stand.

## Functional scope

Every selected candidate sees the same candidate-facing left-nav groups: Jobs, Companies, Artifacts, and Candidate. Group-level “only show this section if the candidate is at or past this state” rules are gone.

The pinned candidate chrome shows the selected candidate’s full current state as read-only text immediately below the picker (wide dropdown and narrow picker). The value is the live stored state name, including retry and error companion states — not a shortened family, progress rank, or operator-editable control. Changing the selected candidate updates the line. No candidate selected (or an empty candidate list) means no state line.

## Architectural definition

**Patterns to reuse** — `pattern.config.config-block` (nav membership and remaining enablement stay declared in config, not invented in React); `pattern.ui.admin-endpoint` does not apply (no new admin surface). Nav resolution stays API-side: React still renders the served list with no extra visibility rules.

**New patterns proposed** — none.

**Applicable statutes** — the universal set (product UI). Scoped constraints: `astral.config.config-source-of-truth` (NAV_CONFIG remains the nav membership source; Code Rules §2.1 NAV_CONFIG paragraph must stay truthful after the gate removal); `astral.layers.ui-config-driven-business-logic` (do not move state-gating into the frontend); `astral.standards.no-hardcoded-sets` (do not replace config gates with a React allowlist); `astral.standards.in-scope-only`; `astral.ui.naming-conventions`; `astral.ui.frontend-file-placement`; `astral.idioms.require-auth-on-protected-endpoints` (existing nav fetch stays authenticated).

## Boundaries

Does not enable permanently disabled stub items (Applied, Responded stay in the list, not activatable).

Does not change admin-only grouping: Operations, Admin, and Tools still omit for non-admins.

Does not change who may switch the selected candidate.

Does not add state editing in the nav, and does not invent display aliases for state names.

Does not redesign or empty-state-fix Jobs, Companies, Artifacts, or Candidate pages for candidates who have not reached those pipeline stages — those routes may still be sparse; this epic only stops hiding the nav.

Does not change job or company nav counts, routes, or page content except as required to stop hiding groups.

Does not reopen three-segment admin nav (AST-1386) or pinned-chrome layout (AST-1369) beyond adding the read-only state line in existing chrome.

## Acceptance criteria

With a selected candidate whose state is before resume-ready, the Artifacts group is present in the left nav.

With a selected candidate whose state is before active search, the Jobs and Companies groups are present in the left nav.

The Candidate group remains present for every selected candidate.

Applied and Responded remain listed and not activatable.

A non-admin session still does not see Operations, Admin, or Tools.

When a candidate is selected, the pinned chrome shows that candidate’s exact current state name directly below the picker, and the operator cannot edit it there.

Selecting a different candidate updates the displayed state to that candidate’s current state.

On the narrow shell, the same read-only state line appears below the candidate picker control in the pinned chrome.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1: **Ungate candidate-facing nav by state - Ada**

Stop hiding Jobs, Companies, and Artifacts by selected-candidate state so every candidate gets the same candidate-facing list. Keep admin-only omit and permanently disabled stubs. Update the NAV_CONFIG contract so Code Rules still describe what the product actually does. Does not own the chrome state line (#2).
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`
**Estimate: 3**

#### 2: **Show selected candidate state under picker - Katherine**

Add a read-only live state name under the candidate picker in pinned chrome (wide and narrow). Uses the selected candidate’s stored state; does not gate nav and does not own NAV_CONFIG membership (#1).
**Citations:** `astral.ui.naming-conventions`, `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic` (do not reintroduce state gates in React)
**Estimate: 2**

---

## Original brief

Remove the navigation rule that says "Only show artifacts if…" so that all candidates get everything in the list, BUT, display the selected candidate's full current state below the dropdown as read only.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
