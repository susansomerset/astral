// SYNC: Every sidebar path in src/utils/config.py NAV_CONFIG must have a matching route here.
//       Deeplink-only (no NAV_CONFIG item): jobs/detail/:jobId, search (AST-2174), and paths
//       dropped from the sidebar by AST-2230 (Intake, Surfer, Processing, New List, …) — routes stay.
//       If you add/remove/rename a sidebar nav item, update NAV_CONFIG to match.
import { Outlet, type RouteObject } from "react-router-dom"
import AdminRoute from "./components/AdminRoute"
import JobsHomeRedirect from "./components/JobsHomeRedirect"
import NavigationShell from "./components/NavigationShell"
import RequireAuth from "./components/RequireAuth"
import { CandidateProvider } from "./contexts/CandidateContext"
import { StateUiProvider } from "./contexts/StateUiContext"
import Authenticate from "./pages/Authenticate"

// --- Jobs ---
import Recommended from "./pages/JobsRecommended"
import Processing from "./pages/JobsProcessing"
import Skipped from "./pages/JobsSkipped"
import Applied from "./pages/JobsApplied"
import JobsMeteorites from "./pages/JobsMeteorites"
import JobsJobDetail from "./pages/JobsJobDetail"

// --- Companies ---
import WatchList from "./pages/CompaniesWatchList"
import NewList from "./pages/CompaniesNewList"
import InactiveList from "./pages/CompaniesInactiveList"
import Ignored from "./pages/CompaniesIgnored"
import Meteorite from "./pages/CompaniesMeteorite"
import WatchHistory from "./pages/CompaniesWatchHistory"

// --- Artifacts ---
import BaseResumeContent from "./pages/ArtifactsBaseResumeContent"
import CompanyWatchCriteria from "./pages/ArtifactsCompanyWatchCriteria"
import CompanySearchTerms from "./pages/ArtifactsCompanySearchTerms"
import JobListCriteria from "./pages/ArtifactsJobListCriteria"
import JobDescCriteria from "./pages/ArtifactsJobDescCriteria"
import MeteoriteCriteria from "./pages/ArtifactsMeteoriteCriteria"
import GetJobCriteria from "./pages/ArtifactsGetJobCriteria"
import DoJobCriteria from "./pages/ArtifactsDoJobCriteria"
import LikeJobCriteria from "./pages/ArtifactsLikeJobCriteria"

// --- Candidate ---
import Profile from "./pages/CandidateProfile"
import CandidateIntake from "./pages/CandidateIntake"
import Strengths from "./pages/CandidateStrengths"
import BioSummary from "./pages/CandidateBioSummary"
import Priorities from "./pages/CandidatePriorities"
import DealBreakers from "./pages/CandidateDealBreakers"
import Backstory from "./pages/CandidateBackstory"
import IdealDay from "./pages/CandidateIdealDay"
import WritingPreferences from "./pages/CandidateWritingPreferences"
import CandidateSurferConsent from "./pages/CandidateSurferConsent"
import CandidateSurfer from "./pages/CandidateSurfer"

// --- Admin ---
import ScheduledActions from "./pages/AdminScheduledActions"
import PerformanceMonitor from "./pages/AdminPerformanceMonitor"
import AgentTimesheets from "./pages/AdminAgentTimesheets"
import TaskPerformance from "./pages/AdminTaskPerformance"
import VectorFeedback from "./pages/AdminVectorFeedback"
import CostReconciliation from "./pages/AdminCostReconciliation"
import ManageCandidates from "./pages/AdminManageCandidates"
import AgentPrompts from "./pages/AdminAgentPrompts"
import TaskPrompts from "./pages/AdminTaskPrompts"
import AnthropicAdHoc from "./pages/AdminAnthropicAdHoc"
import AdminTelescope from "./pages/AdminTelescope"
import DataManagement from "./pages/AdminDataManagement"
import ScheduledQueries from "./pages/AdminScheduledQueries"
import SessionResumePaste from "./pages/AdminSessionResumePaste"
import SessionCoverLetter from "./pages/AdminSessionCoverLetter"
import AdminManageEmail from "./pages/AdminManageEmail"
import AdminManageSlack from "./pages/AdminManageSlack"

// --- Search ---
import SearchResults from "./pages/SearchResults"
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
          { index: true, element: <JobsHomeRedirect /> },

          // Job Opportunities (sidebar) + deeplink-only Processing
          { path: "jobs/ready", element: <Recommended key="ready" view="ready" title="Ready to Apply" /> },
          { path: "jobs/review", element: <Recommended key="review" view="review" title="Recommendations" /> },
          { path: "jobs/applied", element: <Applied /> },
          { path: "jobs/processing", element: <Processing /> }, // deeplink-only — not in NAV_CONFIG
          { path: "jobs/skipped", element: <Skipped /> },
          { path: "jobs/meteorites", element: <JobsMeteorites /> },
          { path: "jobs/detail/:jobId", element: <JobsJobDetail /> },

          // Company (sidebar) + deeplink-only New/Inactive/Meteorite/Watch History lists
          { path: "companies/watch_list", element: <WatchList /> },
          { path: "companies/new_list", element: <NewList /> }, // deeplink-only
          { path: "companies/inactive_list", element: <InactiveList /> }, // deeplink-only
          { path: "companies/ignored", element: <Ignored /> },
          { path: "companies/meteorite_list", element: <Meteorite /> }, // deeplink-only
          { path: "companies/watch_history", element: <WatchHistory /> }, // deeplink-only

          // Criteria / Company / Candidate artifact paths (sidebar labels live in NAV_CONFIG)
          { path: "artifacts/base_resume_content", element: <BaseResumeContent /> },
          { path: "artifacts/company_watch_criteria", element: <CompanyWatchCriteria /> },
          { path: "artifacts/company_search_terms", element: <CompanySearchTerms /> },
          { path: "artifacts/job_list_criteria", element: <JobListCriteria /> },
          { path: "artifacts/job_description_criteria", element: <JobDescCriteria /> },
          { path: "artifacts/meteorite_criteria", element: <MeteoriteCriteria /> },
          { path: "artifacts/get_job_criteria", element: <GetJobCriteria /> },
          { path: "artifacts/do_job_criteria", element: <DoJobCriteria /> },
          { path: "artifacts/like_job_criteria", element: <LikeJobCriteria /> },

          // Candidate (sidebar) + deeplink-only Intake / Surfer / Surfer Consent
          { path: "candidate/profile", element: <Profile /> },
          { path: "candidate/surfer", element: <CandidateSurfer /> }, // deeplink-only
          { path: "candidate/intake", element: <CandidateIntake /> }, // deeplink-only
          { path: "candidate/strengths", element: <Strengths /> },
          { path: "candidate/bio_summary", element: <BioSummary /> },
          { path: "candidate/priorities", element: <Priorities /> },
          { path: "candidate/deal_breakers", element: <DealBreakers /> },
          { path: "candidate/backstory", element: <Backstory /> },
          { path: "candidate/ideal_day", element: <IdealDay /> },
          { path: "candidate/writing_preferences", element: <WritingPreferences /> },
          { path: "candidate/surfer_consent", element: <CandidateSurferConsent /> }, // deeplink-only

          // Admin
          { path: "admin/scheduled_actions", element: <AdminRoute><ScheduledActions /></AdminRoute> },
          { path: "admin/performance_monitor", element: <AdminRoute><PerformanceMonitor /></AdminRoute> },
          { path: "admin/agent_timesheets", element: <AdminRoute><AgentTimesheets /></AdminRoute> },
          { path: "admin/task_performance", element: <AdminRoute><TaskPerformance /></AdminRoute> },
          { path: "admin/vector_feedback", element: <AdminRoute><VectorFeedback /></AdminRoute> },
          { path: "admin/cost_reconciliation", element: <AdminRoute><CostReconciliation /></AdminRoute> },
          { path: "admin/manage_candidates", element: <AdminRoute><ManageCandidates /></AdminRoute> },
          { path: "admin/agent_prompts", element: <AdminRoute><AgentPrompts /></AdminRoute> },
          { path: "admin/task_prompts", element: <AdminRoute><TaskPrompts /></AdminRoute> },
          { path: "admin/anthropic_ad_hoc", element: <AdminRoute><AnthropicAdHoc /></AdminRoute> },
          { path: "admin/telescope", element: <AdminRoute><AdminTelescope /></AdminRoute> },
          { path: "admin/scheduled_queries", element: <AdminRoute><ScheduledQueries /></AdminRoute> },
          { path: "admin/data_management", element: <AdminRoute><DataManagement /></AdminRoute> },
          { path: "admin/session_resume_paste", element: <AdminRoute><SessionResumePaste /></AdminRoute> },
          { path: "admin/session_cover_letter", element: <AdminRoute><SessionCoverLetter /></AdminRoute> },
          { path: "admin/manage_email", element: <AdminRoute><AdminManageEmail /></AdminRoute> },
          { path: "admin/manage_slack", element: <AdminRoute><AdminManageSlack /></AdminRoute> },
          // Search (deeplink-only — no NAV_CONFIG item)
          { path: "search", element: <SearchResults /> },

          // Catch-all
          { path: "*", element: <JobsHomeRedirect /> },
        ],
      },
    ],
  },
]

export default routes
