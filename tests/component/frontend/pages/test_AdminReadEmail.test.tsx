import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminReadEmail from "../../../../src/ui/frontend/src/pages/AdminReadEmail"
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

describe("AdminReadEmail — AST-1033 / AST-1040 (§6c routed page)", () => {
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

  it("renders Read email heading and inbox rows on first paint", async () => {
    mockApis()
    renderWithProviders(<AdminReadEmail />)
    expect(screen.getByRole("heading", { name: "Read email" })).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByText("sender@example.com")).toBeInTheDocument()
    expect(screen.getByText("Unread")).toBeInTheDocument()
    expect(screen.getByText("Read")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages")
  })

  it("click row opens wide modal with escaped raw HTML source (AST-1040)", async () => {
    const raw = "<p>body html</p>"
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({ id: "m1", html_body: raw })
      }
    })
    renderWithProviders(<AdminReadEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByTitle("Email body")).toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "Hello Astral", level: 2 })).toBeInTheDocument()
    const source = screen.getByTitle("Email body")
    expect(source.tagName).toBe("PRE")
    expect(source).toHaveClass("email-html-source")
    expect(source).toHaveTextContent(raw)
    expect(document.querySelector("iframe")).toBeNull()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages/m1")
  })

  it("empty subject uses Message title; empty html still opens empty source panel", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m2") {
        return jsonResponse({ id: "m2", html_body: "" })
      }
    })
    renderWithProviders(<AdminReadEmail />)
    await waitFor(() => expect(screen.getByText("other@example.com")).toBeInTheDocument())
    const row = screen.getByText("other@example.com").closest("tr")
    expect(row).toBeTruthy()
    await userEvent.click(row!)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Message", level: 2 })).toBeInTheDocument(),
    )
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
    renderWithProviders(<AdminReadEmail />)
    await waitFor(() => expect(screen.getAllByText("blocked").length).toBeGreaterThanOrEqual(2))
    expect(screen.queryByRole("table")).not.toBeInTheDocument()
  })

  it("body fetch failure shows modal error without source panel", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({ error: "upstream" }, false)
      }
    })
    renderWithProviders(<AdminReadEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByText("upstream")).toBeInTheDocument())
    expect(screen.queryByTitle("Email body")).not.toBeInTheDocument()
  })
})
