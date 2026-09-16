import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import type { CandidateInfo } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import AdminManageEmail from "../../../../src/ui/frontend/src/pages/AdminManageEmail"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const CANDIDATE_ADA: CandidateInfo = {
  astral_candidate_id: "cand-ada",
  state: "ACTIVE_SEARCH",
  candidate_data: {},
  first: "Ada",
}

const ROWS = [
  {
    id: "m1",
    thread_id: "t1",
    subject: "Hello Astral",
    from_address: "sender@example.com",
    date: "Mon, 1 Jan 2026",
    unread: true,
  },
  {
    id: "m2",
    thread_id: "t2",
    subject: "",
    from_address: "other@example.com",
    date: "Tue, 2 Jan 2026",
    unread: false,
  },
]

function candidatesResponse() {
  return jsonResponse([CANDIDATE_ADA])
}

function inboxListResponse() {
  return jsonResponse({ messages: ROWS })
}

function mockInboxUrl(url: string) {
  return url === "/api/admin/inbox/messages" || url.startsWith("/api/admin/inbox/messages?")
}

async function waitForCandidateAdaOption() {
  await waitFor(() =>
    expect(screen.getByRole("option", { name: "Ada" })).toBeInTheDocument(),
  )
}

async function selectCandidateAda() {
  await waitForCandidateAdaOption()
  await userEvent.selectOptions(
    screen.getByLabelText("Candidate", { selector: "select" }),
    "cand-ada",
  )
}

describe("AdminManageEmail — AST-1033 / AST-1040 / AST-1048 / AST-1051 (§6c routed page)", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
      if (url === "/api/candidates") return candidatesResponse()
      if (mockInboxUrl(url)) {
        return inboxListResponse()
      }
    })
  }

  it("renders Manage Email heading and inbox rows on first paint", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    expect(screen.getByRole("heading", { name: "Manage Email" })).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByText("sender@example.com")).toBeInTheDocument()
    expect(screen.getByText("Unread")).toBeInTheDocument()
    expect(screen.getByText("Read")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages")
  })

  it("per-row Create is retired (AST-1142); no Actions column", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.queryByRole("columnheader", { name: "Actions" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Create" })).not.toBeInTheDocument()
    expect(document.querySelector("button.manage-email-create")).toBeNull()
  })

  it("row modal shows assembled HTML; no Create in modal (AST-1040/1051/1538)", async () => {
    const assembled =
      '<header class="email-headers"><p class="email-from">From: a@x</p></header>\n' +
      '<section class="email-body"><p>body html</p></section>'
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({
          id: "m1",
          html_body: "<p>body html</p>",
          assembled_html: assembled,
        })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByTitle("Email body")).toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "Hello Astral", level: 2 })).toBeInTheDocument()
    expect(document.querySelector(".manage-email-match--modal")).toBeNull()
    expect(document.querySelector(".manage-email-actions")).toBeNull()
    const source = screen.getByTitle("Email body")
    expect(source.tagName).toBe("PRE")
    expect(source).toHaveClass("email-html-source")
    expect(source.textContent).toBe(assembled)
    expect(document.querySelector("iframe")).toBeNull()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages/m1")
  })

  it("empty-subject row: modal omits match line; browse still works (AST-1051)", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m2") {
        return jsonResponse({ id: "m2", html_body: "", assembled_html: "" })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("other@example.com")).toBeInTheDocument())
    const row = screen.getByText("other@example.com").closest("tr")
    expect(row).toBeTruthy()
    await userEvent.click(row!)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Message", level: 2 })).toBeInTheDocument(),
    )
    expect(document.querySelector(".manage-email-match--modal")).toBeNull()
    expect(document.querySelector(".manage-email-actions")).toBeNull()
    const source = screen.getByTitle("Email body")
    expect(source.tagName).toBe("PRE")
    expect(source).toHaveTextContent("")
  })

  it("list failure shows inline error + toast", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages") {
        return jsonResponse({ error: "blocked" }, false)
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getAllByText("blocked").length).toBeGreaterThanOrEqual(2))
    expect(screen.queryByRole("table")).not.toBeInTheDocument()
  })

  it("body fetch failure shows modal error without source panel", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({ error: "upstream" }, false)
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByText("upstream")).toBeInTheDocument())
    expect(screen.queryByTitle("Email body")).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Create" })).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeDisabled()
  })
})

describe("AdminManageEmail — AST-1142 (§6c multi-select + Land Meteorite)", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
      if (url === "/api/candidates") return candidatesResponse()
      if (mockInboxUrl(url)) {
        return inboxListResponse()
      }
    })
  }

  it("toolbar: Land Meteorite disabled until candidate filter + selection", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await waitForCandidateAdaOption()
    expect(screen.getByText("0 selected")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Clear selection" })).toBeDisabled()

    const matchedRow = screen.getByText("Hello Astral").closest("tr")!
    const rowCheckbox = within(matchedRow).getByRole("checkbox")
    await userEvent.click(rowCheckbox)
    expect(screen.getByText("1 selected")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeDisabled()

    await userEvent.selectOptions(
      screen.getByLabelText("Candidate", { selector: "select" }),
      "cand-ada",
    )
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByText("0 selected")).toBeInTheDocument()
    const rowAfterFilter = screen.getByText("Hello Astral").closest("tr")!
    await userEvent.click(within(rowAfterFilter).getByRole("checkbox"))
    expect(screen.getByText("1 selected")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeEnabled()

    await userEvent.click(screen.getByRole("button", { name: "Select all" }))
    expect(screen.getByText("2 selected")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Clear selection" }))
    expect(screen.getByText("0 selected")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeDisabled()
  })

  it("Land Meteorite POSTs selected ids with candidate_id and shows outcomes", async () => {
    let landed = false
    mockApis(async (url, init) => {
      if (mockInboxUrl(url)) {
        return jsonResponse({ messages: landed ? [ROWS[1]] : ROWS })
      }
      if (url === "/api/admin/inbox/land-meteorite" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        expect(body.message_ids).toEqual(["m1", "m2"])
        expect(body.candidate_id).toBe("cand-ada")
        landed = true
        return jsonResponse({
          results: [
            {
              message_id: "m1",
              outcome: "created",
              astral_candidate_id: "cand-ada",
            },
            {
              message_id: "m2",
              outcome: "skipped-other-candidate",
              astral_candidate_id: "cand-ada",
            },
          ],
          total_processed: 2,
          total_passed: 2,
          total_failed: 0,
          total_errors: 0,
          total_skipped: 0,
        })
      }
      if (typeof url === "string" && url.includes("create-job")) {
        throw new Error("create-job must not be called after AST-1142")
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await selectCandidateAda()
    await userEvent.click(screen.getByRole("button", { name: "Select all" }))
    await userEvent.click(screen.getByRole("button", { name: "Land Meteorite" }))
    await waitFor(() =>
      expect(screen.getByText("Land Meteorite results")).toBeInTheDocument(),
    )
    expect(screen.getByText(/Hello Astral — created \(cand-ada\)/)).toBeInTheDocument()
    expect(screen.getByText(/m2 — skipped-other-candidate \(cand-ada\)/)).toBeInTheDocument()
    expect(
      screen.getByText(/Land Meteorite: passed 2, skipped 0, failed 0, errors 0/),
    ).toBeInTheDocument()
    expect(screen.getByText("0 selected")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith(
      "/api/admin/inbox/land-meteorite",
      expect.objectContaining({ method: "POST" }),
    )
    await waitFor(() => expect(screen.queryByText("Hello Astral")).not.toBeInTheDocument())
  })

  it("Land Meteorite HTTP error shows inline feedback and keeps selection", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/inbox/land-meteorite" && init?.method === "POST") {
        return jsonResponse({ error: "message_ids is required" }, false)
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await selectCandidateAda()
    const matchedRow = screen.getByText("Hello Astral").closest("tr")!
    await userEvent.click(within(matchedRow).getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Land Meteorite" }))
    await waitFor(() =>
      expect(screen.getAllByText("message_ids is required").length).toBeGreaterThan(0),
    )
    expect(screen.getByText("1 selected")).toBeInTheDocument()
    expect(screen.queryByText("Land Meteorite results")).not.toBeInTheDocument()
  })
})

describe("AdminManageEmail — AST-1410 silent refetch", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("Land Meteorite list refetch keeps rows and skips Loading…", async () => {
    let postLandMessages: typeof ROWS | null = null
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") return candidatesResponse()
      if (mockInboxUrl(url)) {
        return jsonResponse({ messages: postLandMessages ?? ROWS })
      }
      if (url === "/api/admin/inbox/land-meteorite" && init?.method === "POST") {
        postLandMessages = [ROWS[1]]
        return jsonResponse({
          results: [{ message_id: "m1", outcome: "created", astral_candidate_id: "cand-ada" }],
          total_processed: 1,
          total_passed: 1,
          total_failed: 0,
          total_errors: 0,
          total_skipped: 0,
        })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await selectCandidateAda()
    const matchedRow = screen.getByText("Hello Astral").closest("tr")!
    await userEvent.click(within(matchedRow).getByRole("checkbox"))
    const inner = mockedApi.getMockImplementation()!
    let release: (value: Response) => void = () => {}
    let blockNextList = false
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (blockNextList && mockInboxUrl(url) && !init?.method) {
        blockNextList = false
        return new Promise<Response>((resolve) => { release = resolve })
      }
      return inner(url, init)
    })
    blockNextList = true
    const getsBefore = mockedApi.mock.calls.filter(
      ([u, init]) => mockInboxUrl(String(u)) && !init?.method,
    ).length
    const pending = userEvent.click(screen.getByRole("button", { name: "Land Meteorite" }))
    await waitFor(() => {
      const gets = mockedApi.mock.calls.filter(
        ([u, init]) => mockInboxUrl(String(u)) && !init?.method,
      )
      expect(gets.length).toBeGreaterThan(getsBefore)
    })
    expect(screen.getByText("Hello Astral")).toBeInTheDocument()
    expect(screen.queryByText("Loading…")).not.toBeInTheDocument()
    release({ ok: true, json: async () => ({ messages: [ROWS[1]] }) } as Response)
    await pending
    await waitFor(() => {
      const table = screen.getByRole("table")
      expect(within(table).queryByText("Hello Astral")).not.toBeInTheDocument()
      expect(within(table).getByText("other@example.com")).toBeInTheDocument()
    })
  })
})

describe("AdminManageEmail — AST-1558", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
      if (url === "/api/candidates") return candidatesResponse()
      if (mockInboxUrl(url)) {
        return inboxListResponse()
      }
    })
  }

  it("candidate filter defaults to All (empty value)", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    const select = screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement
    expect(select.value).toBe("")
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages")
  })

  it("selecting a candidate reloads with ?candidate_id=", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await selectCandidateAda()
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/admin/inbox/messages?candidate_id=cand-ada",
      ),
    )
  })

  it("table has no Candidate column header", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.queryByRole("columnheader", { name: "Candidate" })).not.toBeInTheDocument()
    expect(screen.getByRole("columnheader", { name: "Subject" })).toBeInTheDocument()
    expect(screen.getByRole("columnheader", { name: "From" })).toBeInTheDocument()
  })
})

describe("AdminManageEmail — AST-1538 (§6c assembled HTML + copy + dark purple)", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
    })
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
      if (url === "/api/candidates") return candidatesResponse()
      if (mockInboxUrl(url)) {
        return inboxListResponse()
      }
    })
  }

  it("ignores html_body when assembled_html missing (no body-only fallback)", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({ id: "m1", html_body: "<p>raw only</p>" })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByTitle("Email body")).toBeInTheDocument())
    expect(screen.getByTitle("Email body")).toHaveTextContent("")
    expect(screen.getByRole("button", { name: "Copy" })).toBeDisabled()
  })

  it("Copy clips assembled_html and toasts success", async () => {
    const assembled =
      '<header class="email-headers"><div class="email-subject"><h1>Hello Astral</h1></div></header>\n' +
      '<section class="email-body"><p>JD</p></section>'
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({
          id: "m1",
          html_body: "<p>JD</p>",
          assembled_html: assembled,
        })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByTitle("Email body").textContent).toBe(assembled))
    const copyBtn = screen.getByRole("button", { name: "Copy" })
    expect(copyBtn).toHaveClass("btn", "secondary")
    expect(copyBtn).toHaveAttribute("title", "Copy header+body HTML")
    await userEvent.click(copyBtn)
    await waitFor(() =>
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(assembled),
    )
    expect(screen.getByText("Copied to clipboard")).toBeInTheDocument()
  })

  it("email-html-source uses dark purple --bg-elevated (not #fff)", async () => {
    const { readFileSync } = await import("node:fs")
    const { resolve } = await import("node:path")
    const css = readFileSync(
      resolve(__dirname, "../../../../src/ui/frontend/src/App.css"),
      "utf8",
    )
    const block = css.match(/\.email-html-source\s*\{[^}]+\}/)
    expect(block).toBeTruthy()
    expect(block![0]).toMatch(/background:\s*var\(--bg-elevated\)/)
    expect(block![0]).not.toMatch(/background:\s*#fff\b/)
  })
})
