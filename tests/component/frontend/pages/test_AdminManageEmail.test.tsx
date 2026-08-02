import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminManageEmail from "../../../../src/ui/frontend/src/pages/AdminManageEmail"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const ROWS = [
  {
    id: "m1",
    thread_id: "t1",
    subject: "Hello Astral",
    from_address: "sender@example.com",
    date: "Mon, 1 Jan 2026",
    unread: true,
    candidate_match: { matched: true, astral_candidate_id: "cand-ada" },
  },
  {
    id: "m2",
    thread_id: "t2",
    subject: "",
    from_address: "other@example.com",
    date: "Tue, 2 Jan 2026",
    unread: false,
    candidate_match: { matched: false, astral_candidate_id: null },
  },
]

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
      if (url === "/api/admin/inbox/messages") {
        return jsonResponse({ messages: ROWS })
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

  it("list Candidate column shows match bind or em dash (AST-1048)", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByRole("columnheader", { name: "Candidate" })).toBeInTheDocument()
    const matched = screen.getByText("Matched: cand-ada")
    expect(matched).toHaveClass("manage-email-match")
    const unmatchedRow = screen.getByText("other@example.com").closest("tr")
    expect(unmatchedRow).toBeTruthy()
    expect(unmatchedRow!.textContent).toContain("—")
  })

  it("per-row Create is retired (AST-1142); no Actions column", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.queryByRole("columnheader", { name: "Actions" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Create" })).not.toBeInTheDocument()
    expect(document.querySelector("button.manage-email-create")).toBeNull()
  })

  it("matched row: modal shows bind + raw HTML; no Create in modal (AST-1040/1051)", async () => {
    const raw = "<p>body html</p>"
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({ id: "m1", html_body: raw })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByTitle("Email body")).toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "Hello Astral", level: 2 })).toBeInTheDocument()
    const modalMatch = screen.getByText("Matched: cand-ada", {
      selector: ".manage-email-match--modal",
    })
    expect(modalMatch).toBeInTheDocument()
    expect(document.querySelector(".manage-email-actions")).toBeNull()
    const source = screen.getByTitle("Email body")
    expect(source.tagName).toBe("PRE")
    expect(source).toHaveClass("email-html-source")
    expect(source).toHaveTextContent(raw)
    expect(document.querySelector("iframe")).toBeNull()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages/m1")
  })

  it("unmatched row: modal omits match line; browse still works (AST-1051)", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m2") {
        return jsonResponse({ id: "m2", html_body: "" })
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
    // AST-1142: Create retired — Land Meteorite stays on the page chrome.
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
      if (url === "/api/admin/inbox/messages") {
        return jsonResponse({ messages: ROWS })
      }
    })
  }

  it("toolbar: Land Meteorite disabled until selection; select/clear without leaving page", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByText("0 selected")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Clear selection" })).toBeDisabled()

    const matchedRow = screen.getByText("Hello Astral").closest("tr")!
    const rowCheckbox = within(matchedRow).getByRole("checkbox")
    await userEvent.click(rowCheckbox)
    expect(screen.getByText("1 selected")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeEnabled()
    // Checkbox click must not open the message modal.
    expect(screen.queryByRole("heading", { name: "Hello Astral", level: 2 })).not.toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Select all" }))
    expect(screen.getByText("2 selected")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Clear selection" }))
    expect(screen.getByText("0 selected")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Land Meteorite" })).toBeDisabled()
  })

  it("Land Meteorite POSTs selected ids and shows outcomes; never create-job", async () => {
    let listCalls = 0
    mockApis(async (url, init) => {
      if (url === "/api/admin/inbox/messages") {
        listCalls += 1
        // After land, archive drops m1 from the list.
        return jsonResponse({
          messages: listCalls === 1 ? ROWS : [ROWS[1]],
        })
      }
      if (url === "/api/admin/inbox/land-meteorite" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        expect(body.message_ids).toEqual(["m1", "m2"])
        return jsonResponse({
          results: [
            {
              message_id: "m1",
              outcome: "archived",
              astral_candidate_id: "cand-ada",
            },
            {
              message_id: "m2",
              outcome: "skipped-unbound",
              astral_candidate_id: null,
            },
          ],
          total_processed: 1,
          total_passed: 1,
          total_failed: 0,
          total_errors: 0,
          total_skipped: 1,
        })
      }
      if (typeof url === "string" && url.includes("create-job")) {
        throw new Error("create-job must not be called after AST-1142")
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Select all" }))
    await userEvent.click(screen.getByRole("button", { name: "Land Meteorite" }))
    await waitFor(() =>
      expect(screen.getByText("Land Meteorite results")).toBeInTheDocument(),
    )
    expect(screen.getByText(/Hello Astral — archived \(cand-ada\)/)).toBeInTheDocument()
    expect(screen.getByText(/m2 — skipped-unbound/)).toBeInTheDocument()
    expect(
      screen.getByText(/Land Meteorite: passed 1, skipped 1, failed 0, errors 0/),
    ).toBeInTheDocument()
    expect(screen.getByText("0 selected")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith(
      "/api/admin/inbox/land-meteorite",
      expect.objectContaining({ method: "POST" }),
    )
    const createCalls = mockedApi.mock.calls.filter(
      ([u]) => typeof u === "string" && u.includes("create-job"),
    )
    expect(createCalls).toHaveLength(0)
    // Reload after success drops archived subject from the table.
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
