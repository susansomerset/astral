import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsSkipped from "../../../../src/ui/frontend/src/pages/JobsSkipped"
import { renderWithProviders } from "../test-utils"
import { installBaseApiMocks, jobsViewHandler, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const floorJob = {
  astral_job_id: "floor-1",
  job_title: "Floor Role",
  company: "Acme",
  state: "BUILD_ARTIFACTS",
  state_changed_at: "2026-01-02T00:00:00Z",
  latest_score: 0.42,
  dispatch_score_floor: 0.75,
  virtual_skip: true,
}

const failedJob = {
  astral_job_id: "fail-1",
  job_title: "Failed Role",
  company: "Beta",
  state: "FAILED_LIKE",
  state_changed_at: "2026-01-01T00:00:00Z",
  latest_score: 0.55,
  like_grades: [{ vector: "Technical (TE)", grade: "D", confidence: 0.2 }],
}

const skippedJob = {
  astral_job_id: "skip-1",
  job_title: "Skipped Role",
  company: "Gamma",
  state: "CANDIDATE_SKIPPED",
  state_changed_at: "2026-01-04T00:00:00Z",
  latest_score: 0.6,
  like_grades: [{ vector: "Technical (TE)", grade: "B", confidence: 0.5 }],
}

describe("JobsSkipped", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("renders floor and failed sections, selects rows, and retries", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [floorJob, failedJob]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByText(/Below dispatch score floor/)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /Below dispatch score floor/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /State/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Score/ }))
    await userEvent.click(screen.getByText("Floor Role"))
    await userEvent.click(screen.getByRole("button", { name: /Below dispatch score floor/ }))
    await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
    const checkbox = screen.getByRole("checkbox")
    await userEvent.click(checkbox)
    await userEvent.click(screen.getByRole("button", { name: "Retry (1)" }))
    await waitFor(() => expect(screen.getByText("1 jobs queued for retry")).toBeInTheDocument())
    await userEvent.click(checkbox)
    await userEvent.click(screen.getByRole("columnheader", { name: /TE/ }))
    await userEvent.click(screen.getByText("Failed Role"))
  })

  it("handles empty payloads and retry failures", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", { bad: true } as unknown as typeof failedJob[]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByText("No skipped jobs")).toBeInTheDocument())

    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/bulk_state") {
        return Promise.reject(new Error("network"))
      }
      return jobsViewHandler("skipped", [failedJob])(url, init)
    })
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByText(/Failed LIKE/)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
    await userEvent.click(screen.getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Retry (1)" }))
    await waitFor(() => expect(screen.getByText("Retry failed")).toBeInTheDocument())
  })

  it("shows Resurrect action on CANDIDATE_SKIPPED rows when section is expanded", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [skippedJob]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ })).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Resurrect" })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ }))
    expect(screen.getByRole("columnheader", { name: "Actions" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Resurrect" })).toBeInTheDocument()
  })

  it("resurrect on CANDIDATE_SKIPPED posts candidate_action review", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [skippedJob]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ }))
    await userEvent.click(screen.getByRole("button", { name: "Resurrect" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Return to review" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/jobs/skip-1/candidate_action",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ action: "review", notes: "" }),
        }),
      ),
    )
  })

  describe("AST-893 Expand One default", () => {
    it("opening a second section closes the first; no Expand all chrome", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [floorJob, failedJob]))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() => expect(screen.getByText(/Below dispatch score floor/)).toBeInTheDocument())
      expect(screen.queryByRole("button", { name: "Expand all" })).not.toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Collapse all" })).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /Below dispatch score floor/ }))
      expect(screen.getByText("Floor Role")).toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
      expect(screen.getByText("Failed Role")).toBeInTheDocument()
      expect(screen.queryByText("Floor Role")).not.toBeInTheDocument()
    })
  })
})