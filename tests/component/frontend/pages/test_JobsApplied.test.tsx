import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsApplied from "../../../../src/ui/frontend/src/pages/JobsApplied"
import { renderWithProviders } from "../test-utils"
import { installBaseApiMocks, jobsViewHandler, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const appliedJob = {
  astral_job_id: "j-applied-1",
  job_title: "Applied Role",
  company: "Acme",
  state: "CANDIDATE_APPLIED",
  state_changed_at: "2026-01-03T00:00:00Z",
}

describe("JobsApplied — AST-1479 applied list home", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("loads view=applied rows and shows post-applied Actions (§6c)", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("applied", [appliedJob]))
    renderWithProviders(<JobsApplied />)
    await waitFor(() => expect(screen.getByText("Applied Role")).toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "Applied" })).toBeInTheDocument()
    expect(screen.getByRole("columnheader", { name: "Actions" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Reapply" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Interview" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Rejected" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Ghosted" })).toBeInTheDocument()
    expect(screen.queryByText("No records found.")).not.toBeInTheDocument()
  })

  it("shows empty state when the applied list is empty", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("applied", []))
    renderWithProviders(<JobsApplied />)
    await waitFor(() => expect(screen.getByText("No applied jobs yet")).toBeInTheDocument())
  })

  it("Interview → notes modal → candidate_action interview", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("applied", [appliedJob]))
    renderWithProviders(<JobsApplied />)
    await waitFor(() => expect(screen.getByText("Applied Role")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Interview" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Interview" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/jobs/j-applied-1/candidate_action",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ action: "interview", notes: "" }),
        }),
      ),
    )
  })

  it("failed candidate_action toasts the API error", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (
        typeof url === "string" &&
        url === "/api/jobs/j-applied-1/candidate_action" &&
        init?.method === "POST"
      ) {
        return jsonResponse({ error: "Illegal state transition" }, { ok: false, status: 409 })
      }
      return jobsViewHandler("applied", [appliedJob])(url, init)
    })
    renderWithProviders(<JobsApplied />)
    await waitFor(() => expect(screen.getByText("Applied Role")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Rejected" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Rejected" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Illegal state transition")).toBeInTheDocument())
    expect(screen.getByText("Applied Role")).toBeInTheDocument()
  })
})
