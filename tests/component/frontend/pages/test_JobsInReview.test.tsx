import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsInReview from "../../../../src/ui/frontend/src/pages/JobsInReview"
import { renderWithProviders } from "../test-utils"
import { baseCandidate, installBaseApiMocks, jobsViewHandler, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const jobs = [
  {
    astral_job_id: "j1",
    job_title: "Alpha Role",
    company: "Acme",
    state: "PASSED_JOBLIST",
    state_changed_at: "2026-01-02T00:00:00Z",
    latest_score: 0.88,
    joblist_grades: [{ vector: "Job List (JL)", grade: "A", confidence: 0.8 }],
  },
  {
    astral_job_id: "j2",
    job_title: "Beta Role",
    company: "Beta",
    state: "JD_READY",
    state_changed_at: "2026-01-01T00:00:00Z",
    latest_score: null,
    jd_grades: { JD: "B" },
  },
]

describe("JobsInReview", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("expands sections, sorts columns, and opens job details", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("in_review", jobs))
    renderWithProviders(<JobsInReview />)
    await waitFor(() => expect(screen.getByText(/Passed Job List/)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Job Title/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Score/ }))
    await userEvent.click(screen.getByText("Alpha Role"))
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j1"))
    await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
    await userEvent.click(screen.getByRole("button", { name: /JD Ready/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /JD/ }))
    await userEvent.click(screen.getByText("Beta Role"))
  })

  it("shows empty when jobs response is invalid", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("in_review", { bad: true } as unknown as typeof jobs))
    renderWithProviders(<JobsInReview />)
    await waitFor(() => expect(screen.getByText("No jobs in review")).toBeInTheDocument())
  })

  it("shows a legacy section for unmapped in-review state", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("in_review", [{
      astral_job_id: "j-legacy",
      job_title: "Legacy Role",
      company: "OldCo",
      state: "RETIRED_EXAMPLE_STATE",
      state_changed_at: "2026-01-01T00:00:00Z",
    }]))
    renderWithProviders(<JobsInReview />)
    await waitFor(() => expect(screen.getByText(/RETIRED EXAMPLE STATE.*legacy/i)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /RETIRED EXAMPLE STATE.*legacy/i }))
    expect(screen.getByText("Legacy Role")).toBeInTheDocument()
  })
})
