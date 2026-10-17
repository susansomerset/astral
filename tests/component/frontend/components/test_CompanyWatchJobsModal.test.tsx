import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompanyWatchJobsModal from "../../../../src/ui/frontend/src/components/CompanyWatchJobsModal"
import { renderWithProviders } from "../test-utils"
import { candidateId, installBaseApiMocks, jsonResponse } from "../pages/page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

vi.mock("../../../../src/ui/frontend/src/components/JobDetailModal", () => ({
  default: (props: { jobId: string | null; onClose: () => void; stacked?: boolean }) =>
    props.jobId == null ? null : (
      <div data-testid="job-detail-probe">
        JobDetailModal:{props.jobId}:stacked={String(!!props.stacked)}
        <button type="button" onClick={props.onClose}>Close job</button>
      </div>
    ),
}))

const mockedApi = vi.mocked(api)

const jobsUrl =
  `/api/companies/acme/jobs?bucket=active&candidate_id=${candidateId}`

describe("CompanyWatchJobsModal", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("AST-2321: loads bucket jobs and opens stacked JobDetailModal", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === jobsUrl) {
        return jsonResponse([
          {
            astral_job_id: "j-active-1",
            job_title: "Engineer",
            state: "ACTIVE",
            state_changed_at: "2026-03-15T12:00:00Z",
          },
          {
            astral_job_id: "j-active-2",
            job_title: "Analyst",
            state: "ACTIVE",
            state_changed_at: "2026-03-14T12:00:00Z",
          },
        ])
      }
      throw new Error(url)
    })
    renderWithProviders(
      <CompanyWatchJobsModal
        shortName="acme"
        bucket="active"
        bucketLabel="ACTIVE"
        candidateId={candidateId}
        onClose={() => {}}
      />,
    )
    expect(await screen.findByRole("heading", { name: "ACTIVE — acme" })).toBeInTheDocument()
    expect(await screen.findByText("Engineer")).toBeInTheDocument()
    expect(screen.getByText("Analyst")).toBeInTheDocument()
    await userEvent.click(screen.getByText("Engineer"))
    expect(screen.getByTestId("job-detail-probe").textContent).toContain(
      "JobDetailModal:j-active-1:stacked=true",
    )
  })

  it("AST-2321: empty bucket shows empty-state, not an error toast", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === jobsUrl) return jsonResponse([])
      throw new Error(url)
    })
    renderWithProviders(
      <CompanyWatchJobsModal
        shortName="acme"
        bucket="active"
        bucketLabel="ACTIVE"
        candidateId={candidateId}
        onClose={() => {}}
      />,
    )
    expect(await screen.findByText("No jobs in this bucket.")).toBeInTheDocument()
    expect(screen.queryByTestId("job-detail-probe")).not.toBeInTheDocument()
  })

  it("[bug-repro] AST-2326: no State column; phase grade dots when grades present", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === jobsUrl) {
        return jsonResponse([
          {
            astral_job_id: "j-graded",
            job_title: "Graded Role",
            state: "RECOMMENDED",
            state_changed_at: "2026-03-15T12:00:00Z",
            jd_grades: { JD: "A" },
          },
        ])
      }
      throw new Error(url)
    })
    renderWithProviders(
      <CompanyWatchJobsModal
        shortName="acme"
        bucket="active"
        bucketLabel="ACTIVE"
        candidateId={candidateId}
        onClose={() => {}}
      />,
    )
    expect(await screen.findByText("Graded Role")).toBeInTheDocument()
    expect(screen.queryByRole("columnheader", { name: "State" })).not.toBeInTheDocument()
    expect(document.querySelector(".recommended-analysis-lines")).toBeTruthy()
    expect(document.querySelectorAll(".grade-dot").length).toBeGreaterThan(0)
  })

  it("[bug-repro] AST-2326: all-jobs mode groups by title-cased state", async () => {
    const allUrl = `/api/companies/acme/jobs?bucket=all&candidate_id=${candidateId}`
    installBaseApiMocks(mockedApi, (url) => {
      if (url === allUrl) {
        return jsonResponse([
          {
            astral_job_id: "j-jl",
            job_title: "List Fail",
            state: "FAILED_JOBLIST",
            state_changed_at: "2026-03-15T12:00:00Z",
          },
          {
            astral_job_id: "j-rec",
            job_title: "Rec Role",
            state: "RECOMMENDED",
            state_changed_at: "2026-03-14T12:00:00Z",
          },
        ])
      }
      throw new Error(url)
    })
    renderWithProviders(
      <CompanyWatchJobsModal
        shortName="acme"
        bucket="all"
        bucketLabel="Jobs"
        candidateId={candidateId}
        onClose={() => {}}
      />,
    )
    expect(await screen.findByRole("heading", { name: "Jobs — acme" })).toBeInTheDocument()
    expect(screen.getByText("Failed Joblist")).toBeInTheDocument()
    expect(screen.getByText("Recommended")).toBeInTheDocument()
    expect(screen.queryByRole("columnheader", { name: "State" })).not.toBeInTheDocument()
  })
})
