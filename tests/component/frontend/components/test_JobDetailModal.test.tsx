import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobDetailModal from "../../../../src/ui/frontend/src/components/JobDetailModal"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const jobPayload = {
  astral_job_id: "j1",
  job_title: "Engineer",
  company: "Acme",
  job_link: "https://example.com",
  state: "NEW",
  state_changed_at: "2026-01-02T00:00:00Z",
  created_at: "2026-01-01T00:00:00Z",
  state_history: [{ to_state: "NEW", timestamp: "2026-01-01T00:00:00Z" }],
  job_data: { job_description: "Line one\n\n\nLine two" },
  agent_story: [
    {
      task_key: "grade",
      blocks: [{ type: "PROMPT", id: "1", content: "story" }],
    },
  ],
}

describe("JobDetailModal", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("loads job details, switches tabs, and skips a job", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/j1" && !init) {
        return { ok: true, json: async () => jobPayload } as Response
      }
      if (url === "/api/jobs/j1/skip" && init?.method === "POST") {
        return { ok: true } as Response
      }
      throw new Error(url)
    })
    const onClose = vi.fn()
    const onRefresh = vi.fn()
    renderWithProviders(<JobDetailModal jobId="j1" onClose={onClose} onRefresh={onRefresh} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    await userEvent.click(screen.getByText("Job Description"))
    expect(screen.getByText(/Line one/)).toBeInTheDocument()
    await userEvent.click(screen.getByText("grade"))
    expect(screen.getByDisplayValue("story")).toBeInTheDocument()
    await userEvent.click(screen.getByText("Info"))
    await userEvent.click(screen.getByRole("button", { name: "Skip This Job" }))
    await waitFor(() => expect(onRefresh).toHaveBeenCalled())
    expect(onClose).toHaveBeenCalled()
  })

  it("shows not-found and already-skipped states", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/missing") {
        return { ok: false } as Response
      }
      if (url === "/api/jobs/j2") {
        return {
          ok: true,
          json: async () => ({ ...jobPayload, job_link: null, job_data: {}, state: "CANDIDATE_SKIPPED" }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<JobDetailModal jobId="missing" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Job not found.")).toBeInTheDocument())

    renderWithProviders(<JobDetailModal jobId="j2" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Already Skipped" })).toBeDisabled())
  })
})
