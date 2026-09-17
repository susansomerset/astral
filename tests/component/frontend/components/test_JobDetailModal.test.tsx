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


describe("JobDetailModal — AST-1454 skipped-field editors", () => {
  const editablePayload = {
    ...jobPayload,
    state: "CANDIDATE_SKIPPED",
    fields_editable: true,
    legal_next_states: ["NEW", "FAILED_TECHNICAL"],
    job_data: {},
  }

  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockedCopy.mockResolvedValue(true)
  })

  function mockEditable(detail: Record<string, unknown> = editablePayload) {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/j1" && !init) {
        return { ok: true, json: async () => detail } as Response
      }
      if (url === "/api/jobs/j1" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}")) as Record<string, unknown>
        return {
          ok: true,
          json: async () => ({
            ...detail,
            ...body,
            job_data: {
              ...((detail.job_data as Record<string, unknown>) || {}),
              job_description: body.job_description ?? "",
            },
            fields_editable: body.state && body.state !== detail.state ? false : true,
            legal_next_states: body.state && body.state !== detail.state ? [] : detail.legal_next_states,
            state: (body.state as string) || detail.state,
          }),
        } as Response
      }
      if (url === "/api/jobs/j1/skip" && init?.method === "POST") {
        return { ok: true } as Response
      }
      throw new Error(`${url} ${init?.method || "GET"}`)
    })
  }

  it("editable: title/link inputs, state select, empty JD tab, Save PUT + onRefresh", async () => {
    mockEditable()
    const onRefresh = vi.fn()
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} onRefresh={onRefresh} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())

    const titleInput = screen.getByDisplayValue("Engineer")
    expect(titleInput.tagName).toBe("INPUT")
    await userEvent.clear(titleInput)
    await userEvent.type(titleInput, "Patched Title")

    expect(screen.getByDisplayValue("https://example.com").tagName).toBe("INPUT")
    expect(screen.getByRole("combobox")).toBeInTheDocument()
    expect(screen.getByRole("option", { name: "No change" })).toBeInTheDocument()
    expect(screen.getByRole("option", { name: "FAILED_TECHNICAL" })).toBeInTheDocument()
    expect(screen.getByRole("option", { name: "NEW" })).toBeInTheDocument()

    await userEvent.click(screen.getByText("Job Description"))
    const jd = screen.getByRole("textbox")
    expect(jd).toHaveValue("")
    await userEvent.type(jd, "pasted JD")

    await userEvent.click(screen.getByText("Info"))
    expect(screen.getByRole("button", { name: /^Copy$/ })).toHaveClass("btn", "secondary")
    expect(screen.getByRole("button", { name: "Already Skipped" })).toBeDisabled()

    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/jobs/j1",
        expect.objectContaining({
          method: "PUT",
          body: JSON.stringify({
            job_title: "Patched Title",
            job_link: "https://example.com",
            job_description: "pasted JD",
          }),
        }),
      ),
    )
    await waitFor(() => expect(onRefresh).toHaveBeenCalled())
    await waitFor(() => expect(screen.getByRole("heading", { name: "Patched Title" })).toBeInTheDocument())
  })

  it("non-editable: display-only Info, no Save, no empty JD tab", async () => {
    mockEditable({ ...jobPayload, fields_editable: false, legal_next_states: [] })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Save" })).not.toBeInTheDocument()
    expect(screen.queryByDisplayValue("Engineer")).not.toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument()
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument()
    await userEvent.click(screen.getByText("Job Description"))
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument()
    expect(screen.getByText(/Line one/)).toBeInTheDocument()
  })

  it("illegal transition: 409 shows error, reloads, still calls onRefresh", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/j1" && !init) {
        return { ok: true, json: async () => editablePayload } as Response
      }
      if (url === "/api/jobs/j1" && init?.method === "PUT") {
        return {
          ok: false,
          json: async () => ({ error: "Invalid transition: CANDIDATE_SKIPPED -> PASSED_JD" }),
        } as Response
      }
      throw new Error(url)
    })
    const onRefresh = vi.fn()
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} onRefresh={onRefresh} />)
    await waitFor(() => expect(screen.getByDisplayValue("Engineer")).toBeInTheDocument())
    await userEvent.selectOptions(screen.getByRole("combobox"), "NEW")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Invalid transition/)).toBeInTheDocument())
    await waitFor(() => expect(onRefresh).toHaveBeenCalled())
  })
})
