// SYNC: Every route here must have a matching nav item in src/utils/config.py NAV_CONFIG.
//       If you add/remove/rename a route, update NAV_CONFIG to match.
import { Navigate, Outlet, type RouteObject } from "react-router-dom"
import AdminRoute from "./components/AdminRoute"
import NavigationShell from "./components/NavigationShell"
import RequireAuth from "./components/RequireAuth"
import { CandidateProvider } from "./contexts/CandidateContext"
import { StateUiProvider } from "./contexts/StateUiContext"
import Authenticate from "./pages/Authenticate"

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

// --- Admin ---
import ScheduledActions from "./pages/AdminScheduledActions"
import PerformanceMonitor from "./pages/AdminPerformanceMonitor"
import AgentTimesheets from "./pages/AdminAgentTimesheets"
import VectorFeedback from "./pages/AdminVectorFeedback"
import CostReconciliation from "./pages/AdminCostReconciliation"
import ManageCandidates from "./pages/AdminManageCandidates"
import AgentPrompts from "./pages/AdminAgentPrompts"
import TaskPrompts from "./pages/AdminTaskPrompts"
import AnthropicAdHoc from "./pages/AdminAnthropicAdHoc"
import DataManagement from "./pages/AdminDataManagement"

const routes: RouteObject[] = [
  { path: "authenticate", element: <Authenticate /> },
  {
    element: (
      <RequireAuth>
        <StateUiProvider>
          <CandidateProvider>
            <Outlet />
          </CandidateProvider>
        </StateUiProvider>
      </RequireAuth>
    ),
    children: [
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

          // Admin
          { path: "admin/scheduled_actions", element: <AdminRoute><ScheduledActions /></AdminRoute> },
          { path: "admin/performance_monitor", element: <AdminRoute><PerformanceMonitor /></AdminRoute> },
          { path: "admin/agent_timesheets", element: <AdminRoute><AgentTimesheets /></AdminRoute> },
          { path: "admin/vector_feedback", element: <AdminRoute><VectorFeedback /></AdminRoute> },
          { path: "admin/cost_reconciliation", element: <AdminRoute><CostReconciliation /></AdminRoute> },
          { path: "admin/manage_candidates", element: <AdminRoute><ManageCandidates /></AdminRoute> },
          { path: "admin/agent_prompts", element: <AdminRoute><AgentPrompts /></AdminRoute> },
          { path: "admin/task_prompts", element: <AdminRoute><TaskPrompts /></AdminRoute> },
          { path: "admin/anthropic_ad_hoc", element: <AdminRoute><AnthropicAdHoc /></AdminRoute> },
          { path: "admin/data_management", element: <AdminRoute><DataManagement /></AdminRoute> },

          // Catch-all
          { path: "*", element: <Navigate to="/jobs/recommended" replace /> },
        ],
      },
    ],
  },
]

export default routes
