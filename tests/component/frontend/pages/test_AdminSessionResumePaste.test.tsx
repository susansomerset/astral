import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import SessionResumePaste from "../../../../src/ui/frontend/src/pages/AdminSessionResumePaste"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const STRUCTURE = {
  sections: {
    experience: {
      id: "experience",
      title: "Experience",
      enabled: true,
      order: 0,
      job_agent_editable: true,
    },
  },
}

describe("AdminSessionResumePaste — AST-987", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.stubGlobal(
      "open",
      vi.fn(() => ({ closed: false, opener: {} as Window | null })),
    )
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:session-html"),
      revokeObjectURL: vi.fn(),
    })
  })

  // AST-1880: Parse runs on the selected candidate's key — the provider selects the first listed candidate.
  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
    candidates: Array<Record<string, unknown>> = [{ astral_candidate_id: "cand-9", full: "Ada Lovelace" }],
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
      if (url === "/api/candidates") return jsonResponse(candidates)
    })
  }

  it("renders page; Parse success enables Open HTML; failure never opens tab (§6c)", async () => {
    const parseBodies: unknown[] = []
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/parse" && init?.method === "POST") {
        parseBodies.push(JSON.parse(String(init.body)))
        return {
          ok: true,
          json: async () => ({
            success: true,
            resume_structure: STRUCTURE,
            base_resume: { experience: "Jobs from paste" },
          }),
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    expect(screen.getByRole("heading", { name: "Session Resume Paste" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Parse" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeDisabled()
    // Button order: Parse → View Parsed JSON → Open HTML (AST-1035).
    const rowButtons = screen.getAllByRole("button").filter(b =>
      ["Parse", "View Parsed JSON", "Open HTML"].includes(b.textContent || ""),
    )
    expect(rowButtons.map(b => b.textContent)).toEqual([
      "Parse",
      "View Parsed JSON",
      "Open HTML",
    ])

    const textarea = screen.getByPlaceholderText(/Paste full resume text/)
    fireEvent.change(textarea, { target: { value: "Full resume paste" } })
    await waitFor(() => expect(screen.getByRole("button", { name: "Parse" })).toBeEnabled())

    await userEvent.click(screen.getByRole("button", { name: "Parse" }))
    await waitFor(() => expect(screen.getByText("Parsed resume structure.")).toBeInTheDocument())
    // AST-1880 AC 8: selected candidate id rides on the wire; nothing else added.
    expect(parseBodies).toEqual([{ resume_text: "Full resume paste", candidate_id: "cand-9" }])
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeEnabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
    expect(window.open).not.toHaveBeenCalled()
    expect(JSON.parse(localStorage.getItem("session_resume:last_parse") || "null")).toEqual({
      resume_structure: STRUCTURE,
      base_resume: { experience: "Jobs from paste" },
    })
    expect(localStorage.getItem("session_resume:paste_text")).toContain("Full resume paste")
  })

  it("failed parse shows error and does not open HTML tab", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/parse" && init?.method === "POST") {
        return {
          ok: false,
          status: 500,
          json: async () => ({ success: false, error: "agent boom" }),
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    fireEvent.change(screen.getByPlaceholderText(/Paste full resume text/), {
      target: { value: "bad paste" },
    })
    await waitFor(() => expect(screen.getByRole("button", { name: "Parse" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Parse" }))
    await waitFor(() => expect(screen.getAllByText("agent boom").length).toBeGreaterThan(0))
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeDisabled()
    expect(window.open).not.toHaveBeenCalled()
  })

  it("AST-1880: no selected candidate keeps Parse disabled with a reason and never POSTs", async () => {
    mockApis(undefined, [])
    renderWithProviders(<SessionResumePaste />)
    fireEvent.change(screen.getByPlaceholderText(/Paste full resume text/), {
      target: { value: "Full resume paste" },
    })
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/candidates"))
    const parse = screen.getByRole("button", { name: "Parse" })
    expect(parse).toBeDisabled()
    expect(parse).toHaveAttribute("title", "Select a candidate first — Parse runs on their API key")
    await userEvent.click(parse)
    expect(mockedApi.mock.calls.some(([u]) => u === "/api/admin/session_resume/parse")).toBe(false)
  })

  it("View Parsed JSON shows lastParse payload; close keeps lastParse (AST-1035)", async () => {
    const payload = {
      resume_structure: STRUCTURE,
      base_resume: { experience: "Jobs from paste" },
    }
    localStorage.setItem("session_resume:paste_text", JSON.stringify("kept paste"))
    localStorage.setItem("session_resume:last_parse", JSON.stringify(payload))
    mockApis()
    renderWithProviders(<SessionResumePaste />)
    const viewBtn = await screen.findByRole("button", { name: "View Parsed JSON" })
    expect(viewBtn).toBeEnabled()
    await userEvent.click(viewBtn)
    const modal = screen.getByText("Parsed resume JSON").closest(".modal-card") as HTMLElement
    expect(modal).toBeTruthy()
    const pre = within(modal).getByText((_, el) => el?.tagName === "PRE")
    expect(pre.textContent).toBe(JSON.stringify(payload, null, 2))
    expect(pre.textContent).toContain("resume_structure")
    expect(pre.textContent).toContain("base_resume")
    // Close must not clear lastParse / disable Open HTML.
    await userEvent.click(within(modal).getByRole("button", { name: "Close" }))
    await waitFor(() => expect(screen.queryByText("Parsed resume JSON")).not.toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
    expect(JSON.parse(localStorage.getItem("session_resume:last_parse") || "null")).toEqual(payload)
  })

  it("Open HTML posts session JSON and opens blob tab", async () => {
    localStorage.setItem("session_resume:paste_text", JSON.stringify("kept paste"))
    localStorage.setItem(
      "session_resume:last_parse",
      JSON.stringify({
        resume_structure: STRUCTURE,
        base_resume: { experience: "Jobs" },
      }),
    )
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/html" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        expect(body.base_resume.experience).toBe("Jobs")
        return {
          ok: true,
          text: async () => "<html><body>session html</body></html>",
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() => expect(window.open).toHaveBeenCalledWith("blob:session-html", "_blank"))
    const openWin = vi.mocked(window.open).mock.results[0]?.value as { opener: Window | null }
    expect(openWin.opener).toBeNull()
    expect(screen.queryByText("Popup blocked — allow popups to open the HTML tab.")).not.toBeInTheDocument()
  })

  it("Open HTML error shows message and does not open tab", async () => {
    localStorage.setItem("session_resume:paste_text", JSON.stringify("kept paste"))
    localStorage.setItem(
      "session_resume:last_parse",
      JSON.stringify({
        resume_structure: STRUCTURE,
        base_resume: { experience: "Jobs" },
      }),
    )
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/html" && init?.method === "POST") {
        return {
          ok: false,
          status: 400,
          json: async () => ({ success: false, error: "base_resume content is required" }),
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() =>
      expect(screen.getAllByText("base_resume content is required").length).toBeGreaterThan(0),
    )
    expect(window.open).not.toHaveBeenCalled()
  })

  it("restores paste + last parse from localStorage on remount", async () => {
    localStorage.setItem("session_resume:paste_text", JSON.stringify("restored paste"))
    localStorage.setItem(
      "session_resume:last_parse",
      JSON.stringify({
        resume_structure: STRUCTURE,
        base_resume: { experience: "Restored" },
      }),
    )
    mockApis()
    renderWithProviders(<SessionResumePaste />)
    expect(screen.getByDisplayValue("restored paste")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeEnabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
  })

  // AST-1908: Save to Candidate — PUT the last parse to the existing candidate data route.
  const SAVE_PARSE = {
    resume_structure: STRUCTURE,
    base_resume: {
      summary: "Engineer.",
      experience: [
        { company: "Acme", title: "Lead", dates: "2020–2024", location: "Remote", accomplishments: ["Shipped A", "Shipped B"] },
        { company: "Beta", title: "Dev", dates: "2017–2020", location: "NYC", accomplishments: ["Built C"] },
      ],
    },
  }
  const ROW = ["Parse", "View Parsed JSON", "Open HTML", "Save to Candidate"]
  const seedParse = () => {
    localStorage.setItem("session_resume:paste_text", JSON.stringify("kept paste"))
    localStorage.setItem("session_resume:last_parse", JSON.stringify(SAVE_PARSE))
  }
  const putCalls = () =>
    mockedApi.mock.calls.filter(([u, i]) => u === "/api/candidates/cand-9/data" && i?.method === "PUT")
  // Resolve a pending fetch on demand so in-flight button states can be asserted.
  function deferred() {
    let resolve!: (r: Response) => void
    const promise = new Promise<Response>(res => { resolve = res })
    return { promise, resolve }
  }

  it("AST-1908 AC1: Save to Candidate is the fourth button; disabled with no parse, enabled with parse + candidate", async () => {
    mockApis()
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/candidates"))
    // No lastParse → disabled even with a candidate selected.
    expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeDisabled()
    const rowButtons = screen.getAllByRole("button").filter(b => ROW.includes(b.textContent || ""))
    expect(rowButtons.map(b => b.textContent)).toEqual(ROW)
  })

  it("AST-1908 AC1: no selected candidate keeps Save disabled with a parse present and never PUTs", async () => {
    seedParse()
    mockApis(undefined, [])
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/candidates"))
    const save = screen.getByRole("button", { name: "Save to Candidate" })
    expect(save).toBeDisabled()
    await userEvent.click(save)
    expect(mockedApi.mock.calls.some(([u]) => String(u).endsWith("/data"))).toBe(false)
  })

  it("AST-1908 AC1: Save disabled while Parse is in flight", async () => {
    seedParse()
    const parse = deferred()
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/parse" && init?.method === "POST") return parse.promise
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Parse" }))
    await waitFor(() => expect(screen.getByRole("button", { name: "Parsing…" })).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeDisabled()
    parse.resolve({ ok: true, json: async () => ({ success: true, ...SAVE_PARSE }) } as Response)
    await waitFor(() => expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled())
  })

  it("AST-1908 AC1: Save disabled while Open HTML is in flight", async () => {
    seedParse()
    const html = deferred()
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/html" && init?.method === "POST") return html.promise
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() => expect(screen.getByRole("button", { name: "Opening…" })).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeDisabled()
    html.resolve({ ok: true, text: async () => "<html></html>" } as Response)
    await waitFor(() => expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled())
  })

  it("AST-1908 AC2/AC6: one PUT with the exact parse body; Saving… locks the row; success toast", async () => {
    seedParse()
    const save = deferred()
    mockApis(async (url, init) => {
      if (url === "/api/candidates/cand-9/data" && init?.method === "PUT") return save.promise
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Save to Candidate" }))
    // Functional scope 1: Saving… label, every row button disabled while in flight.
    const saving = await screen.findByRole("button", { name: "Saving…" })
    expect(saving).toBeDisabled()
    for (const name of ["Parse", "View Parsed JSON", "Open HTML"]) {
      expect(screen.getByRole("button", { name })).toBeDisabled()
    }
    save.resolve({ ok: true, json: async () => ({ ok: true }) } as Response)
    await waitFor(() =>
      expect(screen.getByText("Saved parse as the candidate's base resume.").closest(".toast-success")).toBeTruthy(),
    )
    // AC2: exactly one PUT; sections only (no accent_color), base_resume untouched, no artifact_id.
    expect(putCalls()).toHaveLength(1)
    expect(JSON.parse(String(putCalls()[0][1]?.body))).toEqual({
      artifacts: {
        resume_structure: { sections: SAVE_PARSE.resume_structure.sections },
        base_resume: SAVE_PARSE.base_resume,
      },
    })
    expect(mockedApi.mock.calls.some(([u]) => String(u).startsWith("/api/admin/session_resume/save"))).toBe(false)
    expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled()
  })

  it("AST-1908 AC6: 400 error shows server message in toast + inline; Save re-enabled; parse kept", async () => {
    seedParse()
    mockApis(async (url, init) => {
      if (url === "/api/candidates/cand-9/data" && init?.method === "PUT") {
        return { ok: false, status: 400, json: async () => ({ error: "boom" }) } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Save to Candidate" }))
    await waitFor(() => expect(screen.getAllByText("boom").length).toBe(2))
    const [a, b] = screen.getAllByText("boom")
    expect([a, b].filter(el => el.closest(".toast-error"))).toHaveLength(1)
    expect([a, b].filter(el => el.tagName === "P" && !el.closest(".toast"))).toHaveLength(1)
    expect(screen.getByRole("button", { name: "Save to Candidate" })).toBeEnabled()
    expect(JSON.parse(localStorage.getItem("session_resume:last_parse") || "null")).toEqual(SAVE_PARSE)
  })

  it("AST-1908 AC8: intro copy names Save to Candidate as the writer, not 'does not save'", async () => {
    mockApis()
    renderWithProviders(<SessionResumePaste />)
    const intro = screen.getByText(/Paste a full resume, Parse to structure-keyed JSON/)
    expect(intro.textContent).not.toContain("does not save to the database")
    expect(intro.textContent).toMatch(/Parse and Open HTML do not save; Save to Candidate writes/)
  })
})
