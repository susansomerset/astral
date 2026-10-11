import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { copyJobSnapshotToClipboard } from "../../../../src/ui/frontend/src/lib/copyJobSnapshot"
import { buildPhaseListGradeRow } from "../../../../src/ui/frontend/src/lib/recommendedJobReport"
import JobDetailModal from "../../../../src/ui/frontend/src/components/JobDetailModal"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders, stubAuthPublicFetches } from "../test-utils"
import { CUT_TITLE, LONG_TITLE, expectFullTitleTooltip } from "../pages/job-title-cell"

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
    legal_next_states: ["NEW", "ERROR_GRADE_DO"],
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
            job_data: (detail.job_data as Record<string, unknown>) || {},
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

  it("editable: title/link inputs, state select, no JD tab or JD editor (AST-2133), Save PUT + onRefresh", async () => {
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
    expect(screen.getByRole("option", { name: "ERROR_GRADE_DO" })).toBeInTheDocument()
    expect(screen.getByRole("option", { name: "NEW" })).toBeInTheDocument()

    // AST-2133: JD is read-only composed text — empty job_data means no JD tab at all.
    expect(screen.queryByText("Job Description")).not.toBeInTheDocument()

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
          }),
        }),
      ),
    )
    await waitFor(() => expect(onRefresh).toHaveBeenCalled())
    await waitFor(() => expect(screen.getByRole("heading", { name: "Patched Title" })).toBeInTheDocument())
  })

  it("AST-2133 AC9: editable job with a composed JD shows it read-only — no JD textarea, Save PUT omits job_description", async () => {
    mockEditable({ ...editablePayload, job_data: { job_description: "Preamble\n\nScraped body" } })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    await userEvent.click(screen.getByText("Job Description"))
    // Info-tab inputs unmount with the tab switch, so any textbox here would be a JD editor.
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument()
    expect(screen.getByText(/Scraped body/)).toBeInTheDocument()

    await userEvent.click(screen.getByText("Info"))
    await userEvent.clear(screen.getByDisplayValue("Engineer"))
    await userEvent.type(screen.getByDisplayValue(""), "T2")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j1", expect.objectContaining({ method: "PUT" })),
    )
    const put = mockedApi.mock.calls.find(([, init]) => (init as RequestInit | undefined)?.method === "PUT")!
    const body = JSON.parse(String((put[1] as RequestInit).body)) as Record<string, unknown>
    expect(body).not.toHaveProperty("job_description")
    expect(body.job_title).toBe("T2")
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

describe("JobDetailModal — AST-1695 listing_href", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockedCopy.mockResolvedValue(true)
  })

  it("read-only BOT_BLOCKED_FETCH_JD: Link <a> from listing_href; raw job_link not wrapped", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/j1") {
        return {
          ok: true,
          json: async () => ({
            ...jobPayload,
            fields_editable: false,
            legal_next_states: [],
            job_link: "https://example.com/column",
            listing_href: "https://example.com/listing",
            state: "BOT_BLOCKED_FETCH_JD",
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    expect(screen.getByRole("link", { name: "https://example.com/listing" })).toHaveAttribute(
      "href",
      "https://example.com/listing",
    )
    expect(screen.queryByRole("link", { name: "https://example.com/column" })).not.toBeInTheDocument()
  })

  it("read-only: null listing_href → no Link <a> even when job_link is http(s)", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/j1") {
        return {
          ok: true,
          json: async () => ({
            ...jobPayload,
            fields_editable: false,
            legal_next_states: [],
            job_link: "https://example.com",
            listing_href: null,
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    expect(screen.queryByRole("link", { name: "https://example.com" })).not.toBeInTheDocument()
  })

  it("editable: Open listing row from listing_href beside job_link input", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/j1") {
        return {
          ok: true,
          json: async () => ({
            ...jobPayload,
            fields_editable: true,
            legal_next_states: ["NEW"],
            job_link: "paste-me",
            listing_href: "https://example.com/open",
            state: "BOT_BLOCKED_FETCH_JD",
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByDisplayValue("paste-me")).toBeInTheDocument())
    expect(screen.getByText("Open listing")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://example.com/open" })).toHaveAttribute(
      "href",
      "https://example.com/open",
    )
  })
})
describe("JobDetailModal — AST-1704 http(s)-only Link row", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockedCopy.mockResolvedValue(true)
  })

  it("renders http job_link as anchor", async () => {
    mockJobDetailApis()
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    await userEvent.click(screen.getByText("Info"))
    expect(screen.getByRole("link", { name: "https://example.com" })).toHaveAttribute(
      "href",
      "https://example.com",
    )
  })

  it("renders non-http job_link as plain text", async () => {
    const crumb = "From:a@x.com 9/17 14:05 Eastern To:b@y.com"
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/jobs/j1" && !init) {
        return { ok: true, json: async () => ({ ...jobPayload, job_link: crumb }) } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    await userEvent.click(screen.getByText("Info"))
    expect(screen.queryByRole("link", { name: crumb })).not.toBeInTheDocument()
    expect(screen.getByText(crumb)).toBeInTheDocument()
  })
})

describe("JobDetailModal — AST-1865 admin state-history row opens the run", () => {
  // Newest first: HOP (run_id beats claim batch_id), LEGACY (batch_id only), MANUAL (neither).
  const history = [
    { to_state: "MANUAL", timestamp: "2026-01-01T00:00:00Z" },
    { to_state: "LEGACY", timestamp: "2026-01-02T00:00:00Z", batch_id: "legacy-B" },
    { to_state: "HOP", timestamp: "2026-01-03T00:00:00Z", run_id: "hop-R", batch_id: "claim-C" },
  ]

  /** Passthrough auth so /api/me decides isAdmin; routes the run modal's log + agent-data fetches. */
  function mockRunApis(isAdmin: boolean) {
    stubAuthPublicFetches(true)
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/me") {
        return { ok: true, json: async () => ({ user_id: "u1", name: "Test User", is_admin: isAdmin }) } as Response
      }
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") return { json: async () => [] } as Response
      if (url === "/api/jobs/j1" && !init) {
        return { ok: true, json: async () => ({ ...jobPayload, state_history: history }) } as Response
      }
      const logs = url.match(/^\/api\/admin\/dispatch_ledger\/([^/]+)\/logs$/)
      if (logs) {
        return {
          ok: true,
          json: async () => [{
            id: 1, level: "INFO", logger_name: "src.core.agent",
            message: `log line for ${logs[1]}`, batch_id: logs[1], created_at: "2026-01-03T00:00:00Z",
          }],
        } as Response
      }
      const blocks = url.match(/^\/api\/agent_data\/([^/?]+)(?:\?|$)/)
      if (blocks) {
        return {
          json: async () => [{
            agent_data_id: "a1", block_type: "SYSTEM", block_data: `system prompt for ${blocks[1]}`,
            token_size: 1, task_key: "t", created_at: "2026-01-03T00:00:00Z",
          }],
        } as Response
      }
      if (url.startsWith("/api/admin/timesheets")) return { json: async () => [] } as Response
      if (/^\/api\/admin\/dispatch_ledger\/[^/]+$/.test(url)) return { ok: false } as Response
      throw new Error(url)
    })
  }

  const calledUrls = () => mockedApi.mock.calls.map(call => String(call[0]))

  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockedCopy.mockResolvedValue(true)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("AC4: admin clicks a run_id row → run logs + agent data fetched and rendered", async () => {
    mockRunApis(true)
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await userEvent.click(await screen.findByTitle("Open run hop-R"))

    expect(await screen.findByText("log line for hop-R")).toBeInTheDocument()
    expect(await screen.findByDisplayValue("system prompt for hop-R")).toBeInTheDocument()
    expect(calledUrls()).toContain("/api/admin/dispatch_ledger/hop-R/logs")
    // AST-2031 AC8: the job modal scopes the run's agent data to the open job
    expect(calledUrls()).toContain("/api/agent_data/hop-R?entity_id=j1")
    expect(calledUrls()).not.toContain("/api/agent_data/hop-R")
    // run_id wins: the claim batch id on the same row is never opened
    expect(calledUrls().some(url => url.includes("claim-C"))).toBe(false)
  })

  it("AC6: batch_id-only row opens that run; a row with neither id is not clickable", async () => {
    mockRunApis(true)
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    const legacy = await screen.findByTitle("Open run legacy-B")
    expect(screen.getByText("MANUAL").closest('[role="button"]')).toBeNull()

    await userEvent.click(legacy)
    expect(await screen.findByText("log line for legacy-B")).toBeInTheDocument()
    expect(calledUrls()).toContain("/api/admin/dispatch_ledger/legacy-B/logs")
    // AST-2031 AC8: the job modal scopes the run's agent data to the open job
    expect(calledUrls()).toContain("/api/agent_data/legacy-B?entity_id=j1")
    expect(calledUrls()).not.toContain("/api/agent_data/legacy-B")
  })

  it("AC5: non-admin → no clickable rows and no /api/admin/ request", async () => {
    mockRunApis(false)
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await screen.findByText("HOP")
    // Let /api/me resolve and settle before asserting absence, so this cannot pass on a pre-auth render
    await waitFor(() => expect(calledUrls()).toContain("/api/me"))
    await new Promise(resolve => setTimeout(resolve, 0))

    expect(screen.queryByTitle(/^Open run /)).not.toBeInTheDocument()
    for (const state of ["HOP", "LEGACY", "MANUAL"]) {
      expect(screen.getByText(state).closest('[role="button"]')).toBeNull()
    }
    await userEvent.click(screen.getByText("HOP"))
    expect(calledUrls().some(url => url.startsWith("/api/admin/"))).toBe(false)
  })
})

describe("JobDetailModal — AST-1973 Info-tab analysis", () => {
  // Detail payload shape after api_jobs._flatten_grades: *_grades / *_rubric at top level.
  // AST-1771 fixture: importance-then-grade order puts QC/B before EFW/A.
  const jdGrades = [
    { vector: "Embedded/Firmware/Hardware Domain", grade: "A", confidence: 5, reason: "fit" },
    { vector: "Quality Check", grade: "B", confidence: 4, reason: "ok" },
  ]
  const jdRubric = [
    { code: "EFW", label: "Embedded/Firmware/Hardware Domain", importance: 1, grade_descriptions: [] },
    { code: "QC", label: "Quality Check", importance: 5, grade_descriptions: [] },
  ]
  const partial = {
    ...jobPayload,
    state: "CANDIDATE_SKIPPED",
    jd_grades: jdGrades,
    jd_rubric: jdRubric,
    do_grades: [{ vector: "Delivery", grade: "C", confidence: 3 }],
  }

  const dotSig = (root: ParentNode) =>
    [...root.querySelectorAll(".grade-dot")].map(d => ({
      colour: [...d.classList].find(c => c.startsWith("dot-")),
      title: d.getAttribute("title"),
    }))

  async function renderInfo(detail: Record<string, unknown>) {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") return { json: async () => [] } as Response
      if (url === "/api/jobs/j1" && !init) return { ok: true, json: async () => detail } as Response
      throw new Error(url)
    })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Engineer" })).toBeInTheDocument())
    // Lines appear once the manifest provider resolves.
    await waitFor(() => expect(document.querySelectorAll(".recommended-analysis-line")).toHaveLength(4))
    const block = document.querySelector(".recommended-analysis-lines") as HTMLElement
    const lines = [...block.querySelectorAll(".recommended-analysis-line")] as HTMLElement[]
    const line = (label: string) =>
      lines.find(l => l.querySelector(".recommended-analysis-line-label")?.textContent === label)!
    return { block, lines, line }
  }

  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockedCopy.mockResolvedValue(true)
  })

  it("AC1/AC2: right column shows Analysis label, then JD/DO/GET/LIKE lines, then State History", async () => {
    const { block, lines } = await renderInfo(jobPayload)
    const cols = document.querySelectorAll(".entity-summary-top > .entity-summary-col")
    const right = cols[cols.length - 1]
    expect(block.closest(".entity-summary-col")).toBe(right)
    const labels = [...right.querySelectorAll(".entity-section-label")]
    expect(labels.map(l => l.textContent)).toEqual(["Analysis", "State History"])
    // DOM order: Analysis label → lines → State History label.
    expect(labels[0].compareDocumentPosition(block) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(block.compareDocumentPosition(labels[1]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    // Manifest order (report_phase_tabs) + phase_score_columns short labels.
    expect(lines.map(l => l.querySelector(".recommended-analysis-line-label")?.textContent))
      .toEqual(["JD", "DO", "GET", "LIKE"])
  })

  it("AC3: no phase grades → all four lines show an em dash and the modal still renders", async () => {
    const { block, lines } = await renderInfo(jobPayload)
    expect(block.querySelector(".grade-dot")).toBeNull()
    for (const l of lines) expect(l.textContent).toMatch(/\u2014$/)
    expect(screen.getByText("State History")).toBeInTheDocument()
  })

  it("AC3: JD + DO graded, GET + LIKE not → circles on JD/DO, em dash on GET/LIKE (skipped state, ungated)", async () => {
    const { line } = await renderInfo(partial)
    expect(line("JD").querySelectorAll(".grade-dot")).toHaveLength(2)
    expect(line("DO").querySelectorAll(".grade-dot")).toHaveLength(1)
    for (const label of ["GET", "LIKE"]) {
      expect(line(label).querySelector(".grade-dot")).toBeNull()
      expect(line(label).textContent).toBe(`${label}\u2014`)
    }
    for (const label of ["JD", "DO"]) expect(line(label).textContent).not.toContain("\u2014")
  })

  it("AC4: circle count, dot-* colours, order and titles equal the list's row builder", async () => {
    const { line } = await renderInfo(partial)
    const list = render(<>{buildPhaseListGradeRow(partial, "jd_grades")}</>).container
    expect(dotSig(line("JD"))).toEqual(dotSig(list))
    expect(dotSig(line("JD")).map(d => d.colour)).toEqual(["dot-b", "dot-a"])
    for (const d of dotSig(line("JD"))) expect(d.title).toBeTruthy()
    const listDo = render(<>{buildPhaseListGradeRow(partial, "do_grades")}</>).container
    expect(dotSig(line("DO"))).toEqual(dotSig(listDo))
  })

  it("AC5: modal circles carry no letter and the block has no confidence bullets", async () => {
    const { block } = await renderInfo(partial)
    const dots = block.querySelectorAll(".grade-dot")
    expect(dots).toHaveLength(3)
    for (const dot of dots) {
      expect(dot).toHaveClass("grade-dot-letterless")
      expect(dot.textContent).toBe("")
    }
    expect(block.querySelector(".confidence-bullets")).toBeNull()
    // Display-only: nothing clickable inside the block.
    expect(block.querySelector('[role="button"], button, a, .clickable')).toBeNull()
  })
})

// AST-1983 AC 5 / AC 6: Modal <h2> cuts the job title (JobTitleText); Info-tab Title field and edit input stay full.
describe("JobDetailModal — AST-1983 header title cut", () => {
  function mockDetail(detail: Record<string, unknown>) {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      if (url === "/api/candidates") return { json: async () => [] } as Response
      if (url === "/api/jobs/j1" && !init) return { ok: true, json: async () => detail } as Response
      throw new Error(url)
    })
  }

  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("AC5: header shows first 50 chars + … with the full-title tooltip; AC6: read-only Title field is full", async () => {
    mockDetail({ ...jobPayload, job_title: LONG_TITLE, fields_editable: false, legal_next_states: [] })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    const heading = await screen.findByRole("heading", { name: CUT_TITLE })
    expect(heading.textContent).toBe(CUT_TITLE)
    await expectFullTitleTooltip(within(heading).getByText(CUT_TITLE), heading.closest(".modal-overlay")!)
    await userEvent.click(screen.getByText("Info"))
    expect(screen.getByText(LONG_TITLE).closest(".modal-body")).toBeTruthy()
  })

  it("AC6: editable Title input holds the full title while the header is cut", async () => {
    mockDetail({ ...jobPayload, job_title: LONG_TITLE, state: "CANDIDATE_SKIPPED", fields_editable: true, legal_next_states: ["NEW"], job_data: {} })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    await screen.findByRole("heading", { name: CUT_TITLE })
    const input = screen.getByDisplayValue(LONG_TITLE)
    expect(input.tagName).toBe("INPUT")
  })

  it("empty title keeps the company / Job Detail header fallback", async () => {
    mockDetail({ ...jobPayload, job_title: "" })
    const { unmount } = renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    expect(await screen.findByRole("heading", { name: "Acme" })).toBeInTheDocument()
    unmount()
    mockDetail({ ...jobPayload, job_title: null, company: null })
    renderWithProviders(<JobDetailModal jobId="j1" onClose={() => {}} />)
    expect(await screen.findByRole("heading", { name: "Job Detail" })).toBeInTheDocument()
  })
})
