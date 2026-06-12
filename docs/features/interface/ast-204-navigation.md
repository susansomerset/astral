# AST-204 — Navigation

<!-- linear-archive: AST-204 archived 2026-06-03 -->

## Linear archive (AST-204)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-204/navigation  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** unassigned  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Wire up the NavigationShell to real routes and confirm all nav destinations resolve to their correct page components. This feature establishes the routing backbone — each destination renders its actual page component (even if that page is initially empty/stubbed), not a placeholder.

**Nav structure (from Interface design):**

Jobs

* Meteors
* New
* Skipped
* Applied
* Responded

Companies

* Watch List (with Seek and Import as in-screen functionality)
* Gazer Issues
* Ignored
* Watch History

Candidate

* Profile
* Strengths
* Goals
* Deal Breakers
* Experience
* Base Resume

Admin

* Manage Candidates
* Agent Prompts
* Task Prompts
* Rubrics
* Analysis Instructions
* Resume Framework

**Acceptance Criteria:**

* Every nav link routes to its own named page component
* Active link is visually highlighted in the sidebar
* Page components may be empty shells at this stage — content is implemented in subsequent features
* No broken routes; unknown paths redirect gracefully
* Navigation works correctly on refresh (Flask catch-all serves index.html for non-API routes)
* NavigationShell and routing confirmed working end-to-end on Railway

# Navigation

**Scope:** Create stub page components for all 24 nav destinations. Organized by section folder: pages/Jobs/, pages/Companies/, pages/Candidate/, pages/Admin/. Every stub renders a large winking emoji centered in the main content area. No Component Library usage in stubs — just the emoji. Real implementations come later per feature.

**Files (24 total):**

* Jobs: Meteors.tsx, New.tsx, Skipped.tsx, Applied.tsx, Responded.tsx
* Companies: WatchList.tsx, GazerIssues.tsx, Ignored.tsx, WatchHistory.tsx
* Candidate: Profile.tsx, Strengths.tsx, Goals.tsx, DealBreakers.tsx, Experience.tsx, BaseResume.tsx
* Admin: ScheduledActions.tsx, PerformanceMonitor.tsx, AgentTimesheets.tsx, ManageCandidates.tsx, AgentPrompts.tsx, TaskPrompts.tsx, ConsultRubrics.tsx, AnalysisInstructions.tsx, ResumeFramework.tsx

**Naming convention:** PascalCase for component files (React requirement), snake_case for route paths (Astral convention).

**Layer:** ui/src/pages/

## Metadata

* URL: [AST-214](https://linear.app/astralcareermatch/issue/AST-214/stub-page-files-for-all-nav-destinations)
* Identifier: [AST-214](https://linear.app/astralcareermatch/issue/AST-214/stub-page-files-for-all-nav-destinations)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Interface](https://linear.app/astralcareermatch/project/astral-interface-90277084a555). The user interface to combine all the features of Astral for independent candidate use.
* Created: 2026-02-28T15:05:07.411Z
* Updated: 2026-02-28T18:32:04.777Z

---

# Navigation

**Scope:** Wire all nav config entries to their stub page components via React Router and verify end-to-end navigation.

* Wire all nav config entries to their stub page components via React Router
* Active link visually highlighted in sidebar
* Unknown paths redirect gracefully (404 or redirect to default route)
* Navigation works correctly on page refresh (Flask catch-all serves index.html)
* Verified end-to-end: sidebar click -> route change -> correct stub with winking emoji

**Route mapping:**

* Jobs: /jobs/meteors, /jobs/new, /jobs/skipped, /jobs/applied, /jobs/responded
* Companies: /companies/watch_list, /companies/gazer_issues, /companies/ignored, /companies/watch_history
* Candidate: /candidate/profile, /candidate/strengths, /candidate/goals, /candidate/deal_breakers, /candidate/experience, /candidate/base_resume
* Admin: /admin/scheduled_actions, /admin/performance_monitor, /admin/agent_timesheets, /admin/manage_candidates, /admin/agent_prompts, /admin/task_prompts, /admin/consult_rubrics, /admin/analysis_instructions, /admin/resume_framework

**Layer:** ui/src/ (router config, NavigationShell integration)

## Metadata

* URL: [AST-215](https://linear.app/astralcareermatch/issue/AST-215/route-wiring-active-highlighting-and-refresh-handling)
* Identifier: [AST-215](https://linear.app/astralcareermatch/issue/AST-215/route-wiring-active-highlighting-and-refresh-handling)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Interface](https://linear.app/astralcareermatch/project/astral-interface-90277084a555). The user interface to combine all the features of Astral for independent candidate use.
* Created: 2026-02-28T15:05:08.935Z
* Updated: 2026-02-28T18:32:04.813Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
