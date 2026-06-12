// SYNC: Every route here must have a matching nav item in src/utils/config.py NAV_CONFIG.
//       If you add/remove/rename a route, update NAV_CONFIG to match.
import { Navigate, type RouteObject } from "react-router-dom"
import NavigationShell from "./components/NavigationShell"

// --- Jobs ---
import Recommended from "./pages/JobsRecommended"
import InReview from "./pages/JobsInReview"
import Skipped from "./pages/JobsSkipped"
import Applied from "./pages/JobsApplied"
import Responded from "./pages/JobsResponded"

// --- Companies ---
import WatchList from "./pages/CompaniesWatchList"
import NewList from "./pages/CompaniesNewList"
import InactiveList from "./pages/CompaniesInactiveList"
import Ignored from "./pages/CompaniesIgnored"
import WatchHistory from "./pages/CompaniesWatchHistory"

// --- Artifacts ---
import BaseResumeContent from "./pages/ArtifactsBaseResumeContent"
import CompanyWatchCriteria from "./pages/ArtifactsCompanyWatchCriteria"
import CompanySearchTerms from "./pages/ArtifactsCompanySearchTerms"
import JobListCriteria from "./pages/ArtifactsJobListCriteria"
import JobDescCriteria from "./pages/ArtifactsJobDescCriteria"
import GetJobCriteria from "./pages/ArtifactsGetJobCriteria"
import DoJobCriteria from "./pages/ArtifactsDoJobCriteria"
import LikeJobCriteria from "./pages/ArtifactsLikeJobCriteria"

// --- Candidate ---
import Profile from "./pages/CandidateProfile"
import CandidateIntake from "./pages/CandidateIntake"
import Strengths from "./pages/CandidateStrengths"
import Priorities from "./pages/CandidatePriorities"
import DealBreakers from "./pages/CandidateDealBreakers"
import Backstory from "./pages/CandidateBackstory"
import WritingPreferences from "./pages/CandidateWritingPreferences"
import BoardSearches from "./pages/CandidateBoardSearches"

// --- Admin ---
import ScheduledActions from "./pages/AdminScheduledActions"
import PerformanceMonitor from "./pages/AdminPerformanceMonitor"
import AgentTimesheets from "./pages/AdminAgentTimesheets"
import CostReconciliation from "./pages/AdminCostReconciliation"
import ManageCandidates from "./pages/AdminManageCandidates"
import AgentPrompts from "./pages/AdminAgentPrompts"
import TaskPrompts from "./pages/AdminTaskPrompts"
import AnthropicAdHoc from "./pages/AdminAnthropicAdHoc"
import DataManagement from "./pages/AdminDataManagement"

const routes: RouteObject[] = [
  {
    element: <NavigationShell />,
    children: [
      { index: true, element: <Navigate to="/jobs/recommended" replace /> },

      // Jobs
      { path: "jobs/in_review", element: <InReview /> },
      { path: "jobs/skipped", element: <Skipped /> },
      { path: "jobs/recommended", element: <Recommended /> },
      { path: "jobs/applied", element: <Applied /> },
      { path: "jobs/responded", element: <Responded /> },

      // Companies
      { path: "companies/watch_list", element: <WatchList /> },
      { path: "companies/new_list", element: <NewList /> },
      { path: "companies/inactive_list", element: <InactiveList /> },
      { path: "companies/ignored", element: <Ignored /> },
      { path: "companies/watch_history", element: <WatchHistory /> },

      // Artifacts
      { path: "artifacts/base_resume_content", element: <BaseResumeContent /> },
      { path: "artifacts/company_watch_criteria", element: <CompanyWatchCriteria /> },
      { path: "artifacts/company_search_terms", element: <CompanySearchTerms /> },
      { path: "artifacts/job_list_criteria", element: <JobListCriteria /> },
      { path: "artifacts/job_description_criteria", element: <JobDescCriteria /> },
      { path: "artifacts/get_job_criteria", element: <GetJobCriteria /> },
      { path: "artifacts/do_job_criteria", element: <DoJobCriteria /> },
      { path: "artifacts/like_job_criteria", element: <LikeJobCriteria /> },

      // Candidate
      { path: "candidate/profile", element: <Profile /> },
      { path: "candidate/intake", element: <CandidateIntake /> },
      { path: "candidate/strengths", element: <Strengths /> },
      { path: "candidate/priorities", element: <Priorities /> },
      { path: "candidate/deal_breakers", element: <DealBreakers /> },
      { path: "candidate/backstory", element: <Backstory /> },
      { path: "candidate/writing_preferences", element: <WritingPreferences /> },
      { path: "candidate/board_searches", element: <BoardSearches /> },
      // Admin
      { path: "admin/scheduled_actions", element: <ScheduledActions /> },
      { path: "admin/performance_monitor", element: <PerformanceMonitor /> },
      { path: "admin/agent_timesheets", element: <AgentTimesheets /> },
      { path: "admin/cost_reconciliation", element: <CostReconciliation /> },
      { path: "admin/manage_candidates", element: <ManageCandidates /> },
      { path: "admin/agent_prompts", element: <AgentPrompts /> },
      { path: "admin/task_prompts", element: <TaskPrompts /> },
      { path: "admin/anthropic_ad_hoc", element: <AnthropicAdHoc /> },
      { path: "admin/data_management", element: <DataManagement /> },

      // Catch-all
      { path: "*", element: <Navigate to="/jobs/recommended" replace /> },
    ],
  },
]

export default routes
