import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { copyJobSnapshotToClipboard } from "../../../../src/ui/frontend/src/lib/copyJobSnapshot"
import JobDetailModal from "../../../../src/ui/frontend/src/components/JobDetailModal"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

vi.mock("../../../../src/ui/frontend/src/lib/copyJobSnapshot", () => ({
  copyJobSnapshotToClipboard: vi.fn(),
}))

const mockedApi = vi.mocked(api)
const mockedCopy = vi.mocked(copyJobSnapshotToClipboard)

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

function mockJobDetailApis() {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/state_ui_manifest") {
      return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
    }
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
}

describe("JobDetailModal", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockedCopy.mockResolvedValue(true)
  })

  it("loads job details, switches tabs, and skips a job", async () => {
    mockJobDetailApis()
    const onClose = vi.fn()
    const onRefresh = vi.fn()
    renderWithProviders(<JobDetailModal jobId="j1" onClose={onClose} onRefresh={onRefresh} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    await userEvent.click(screen.getByText("Job Description"))
    expect(screen.getByText(/Line one/)).toBeInTheDocument()
    await userEvent.click(screen.getByText("grade"))
    expect(screen.getByDisplayValue("story")).toBeInTheDocument()
    await userEvent.click(screen.getByText("Info"))
    const skip = screen.getByRole("button", { name: "Skip This Job" })
    expect(skip).toHaveClass("btn", "secondary")
    await userEvent.click(skip)
    await waitFor(() => expect(onRefresh).toHaveBeenCalled())
    expect(onClose).toHaveBeenCalled()
  })

  it("shows not-found and already-skipped states", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
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

describe("JobDetailModal — AST-1421 snapshot Copy", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockJobDetailApis()
  })

  it("shows Copy on Info above Skip, then Copied after success, then Copy again", async () => {
    mockedCopy.mockResolvedValue(true)
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    const copyBtn = screen.getByRole("button", { name: /^Copy$/ })
    expect(copyBtn).toHaveClass("btn", "secondary")
    expect(copyBtn.closest(".entity-summary-actions")).toBeTruthy()
    expect(screen.getByRole("button", { name: "Skip This Job" })).toHaveClass("btn", "secondary")
    await userEvent.click(copyBtn)
    await waitFor(() => expect(mockedCopy).toHaveBeenCalledWith("j1"))
    await waitFor(() => expect(screen.getByRole("button", { name: /^Copied$/ })).toBeInTheDocument())
    await waitFor(
      () => expect(screen.getByRole("button", { name: /^Copy$/ })).toBeInTheDocument(),
      { timeout: 3000 },
    )
  })

  it("stays Copy when the helper returns false", async () => {
    mockedCopy.mockResolvedValue(false)
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("button", { name: /^Copy$/ })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /^Copy$/ }))
    await waitFor(() => expect(mockedCopy).toHaveBeenCalled())
    expect(screen.getByRole("button", { name: /^Copy$/ })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /^Copied$/ })).not.toBeInTheDocument()
  })
})
