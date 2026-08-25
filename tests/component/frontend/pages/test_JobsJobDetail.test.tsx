import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { Route, Routes } from "react-router-dom"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsJobDetail from "../../../../src/ui/frontend/src/pages/JobsJobDetail"
import { renderWithProviders, stubAuthPublicFetches } from "../test-utils"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"

const navigate = vi.fn()

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom")
  return { ...actual, useNavigate: () => navigate }
})

const mockedApi = vi.mocked(api)

function fullUpshot() {
  return {
    take_get: "GET phase thought",
    take_do: "DO phase thought",
    take_like: "LIKE phase thought",
    take_jd: "JD phase thought",
    whole_jd_upshot: "Strong thematic fit.",
    segment_upshots: [],
    candidate_questions: [{ text: "What is the team size?" }],
    caveats: [{ text: "Remote only" }],
  }
}

function jobHandler(
  jobId: string,
  overrides: Record<string, unknown> = {},
): (url: string, init?: RequestInit) => Promise<Response> | Response | undefined {
  return (url, init) => {
    if (url === `/api/jobs/${jobId}` && !init) {
      return jsonResponse({
        astral_job_id: jobId,
        job_title: "Analyst",
        company: "Globex",
        state: "RECOMMENDED",
        state_changed_at: "2026-01-03T00:00:00Z",
        job_link: "https://jobs.example/apply",
        job_data: {
          job_description: "Full JD body text",
          analysis_upshot: fullUpshot(),
          jd_grades: [{ vector: "JD", grade: "A", reason: "Strong match" }],
        },
        ...overrides,
      })
    }
    if (url === "/api/companies/Globex") {
      return jsonResponse({ company_website: "https://globex.example", candidate_id: candidateId })
    }
    if (url === `/api/candidates/${candidateId}/resume_structure`) {
      return jsonResponse({
        sections: [{ id: "professional_summary", label: "Summary" }],
        accent_color: null,
      })
    }
    return undefined
  }
}

function renderDetail(path: string) {
  renderWithProviders(
    <Routes>
      <Route path="/jobs/detail/:jobId" element={<JobsJobDetail />} />
      <Route path="/jobs/recommended" element={<p>Recommended home</p>} />
    </Routes>,
    { router: { initialEntries: [path] } },
  )
}

async function waitForReportShell() {
  await waitFor(() => expect(document.querySelector(".recommended-report-tabs")).toBeTruthy())
}

describe("JobsJobDetail — AST-1481 deeplink modal host", () => {
  beforeEach(() => {
    localStorage.clear()
    navigate.mockReset()
    mockedApi.mockReset()
    stubAuthPublicFetches(true)
  })

  it("opens JobAnalysisReportModal for a loadable job deeplink", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-deeplink"))
    renderDetail("/jobs/detail/j-deeplink")
    await waitForReportShell()
    const bar = document.querySelector(".recommended-report-tabs") as HTMLElement
    expect(within(bar).getByRole("button", { name: "Summary" })).toHaveClass("active")
    expect(screen.getByText("Job Summary")).toBeInTheDocument()
    expect(document.querySelector(".side-tab-list")).toBeNull()
  })

  it("opens the modal for a skipped job (no recommended-only gate)", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-skipped", { state: "SKIPPED" }))
    renderDetail("/jobs/detail/j-skipped")
    await waitForReportShell()
    expect(screen.getByText("Job Summary")).toBeInTheDocument()
  })

  it("shows explicit 404 error UI with back link", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-missing" && !init) {
        return jsonResponse({ error: "Not found" }, { ok: false, status: 404 })
      }
      return undefined
    })
    renderDetail("/jobs/detail/j-missing")
    await waitFor(() => expect(screen.getByRole("heading", { name: "Job unavailable" })).toBeInTheDocument())
    expect(screen.getByText("Job not found")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Back to Recommended" })).toHaveAttribute("href", "/jobs/recommended")
    expect(document.querySelector(".recommended-report-tabs")).toBeNull()
  })

  it("shows API error message for other load failures", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-denied" && !init) {
        return jsonResponse({ error: "Forbidden" }, { ok: false, status: 403 })
      }
      return undefined
    })
    renderDetail("/jobs/detail/j-denied")
    await waitFor(() => expect(screen.getByText("Forbidden")).toBeInTheDocument())
    expect(screen.getByRole("link", { name: "Back to Recommended" })).toBeInTheDocument()
  })

  it("navigates to recommended when the report modal closes", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-close"))
    renderDetail("/jobs/detail/j-close")
    await waitForReportShell()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))
    expect(navigate).toHaveBeenCalledWith("/jobs/recommended")
  })

  it("redirects blank jobId to recommended", async () => {
    installBaseApiMocks(mockedApi, () => undefined)
    renderDetail("/jobs/detail/%20%20")
    await waitFor(() => expect(screen.getByText("Recommended home")).toBeInTheDocument())
  })

  it("prefetches job and aligns admin candidate before opening the modal", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    const callOrder: string[] = []
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/me") {
        return jsonResponse({ user_id: "u1", name: "Test User", is_admin: true })
      }
      if (url === "/api/candidates") {
        callOrder.push("candidates")
        return jsonResponse([
          { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} },
          { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
        ])
      }
      if (url === "/api/state_ui_manifest") {
        return jsonResponse(STATE_UI_MANIFEST_FIXTURE)
      }
      if (url === "/api/system/ui_config") {
        return jsonResponse({ column_types: {} })
      }
      if (url === "/api/jobs/j-align" && !init) {
        if (!callOrder.includes("candidates")) {
          return new Promise<Response>((resolve) => {
            const wait = () => {
              if (callOrder.includes("candidates")) {
                callOrder.push("job-prefetch")
                resolve(
                  jsonResponse({
                    astral_job_id: "j-align",
                    job_title: "Owner Role",
                    company: "Globex",
                    state: "RECOMMENDED",
                    job_data: { job_description: "JD", analysis_upshot: fullUpshot() },
                  }),
                )
              } else {
                setTimeout(wait, 5)
              }
            }
            wait()
          })
        }
        callOrder.push("job-prefetch")
        return jsonResponse({
          astral_job_id: "j-align",
          job_title: "Owner Role",
          company: "Globex",
          state: "RECOMMENDED",
          job_data: { job_description: "JD", analysis_upshot: fullUpshot() },
        })
      }
      if (url === "/api/companies/Globex") {
        callOrder.push("company")
        return jsonResponse({ candidate_id: "c2" })
      }
      if (url.startsWith("/api/candidates/") && url.endsWith("/resume_structure")) {
        return jsonResponse({ sections: [{ id: "professional_summary", label: "Summary" }], accent_color: null })
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderDetail("/jobs/detail/j-align")
    await waitForReportShell()
    expect(callOrder).toContain("company")
    expect(callOrder.indexOf("job-prefetch")).toBeLessThan(callOrder.indexOf("company"))
  })
})
