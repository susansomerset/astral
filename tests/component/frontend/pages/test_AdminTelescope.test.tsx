/**
 * AST-1728 / AST-1730 / AST-1734 / AST-1744 — AdminTelescope page + panes + filters.
 */
import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminTelescope from "../../../../src/ui/frontend/src/pages/AdminTelescope"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const scrapePayload = {
  final_url: "https://example.com/final",
  text: "line1\n".repeat(80),
  scrape_meta: {
    bot_blocked: false,
    cookies_dismissed: true,
    issues: [],
    content_chars: 400,
  },
}

describe("AdminTelescope", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (String(url).includes("/api/admin/telescope") && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => scrapePayload,
        } as Response
      }
      return undefined
    })
  })

  it("AST-1728: AdminTelescope page module exports a component", async () => {
    const mod = await import(
      "../../../../src/ui/frontend/src/pages/AdminTelescope"
    )
    expect(mod.default).toBeTypeOf("function")
  })

  it("AST-1734: root unlocks page scroll (list-page height auto / overflow visible)", () => {
    renderWithProviders(<AdminTelescope />)
    const listPage = document.querySelector(".list-page") as HTMLElement | null
    if (listPage) {
      // Proposed fix: override .list-page height/overflow so .content can scroll.
      expect(listPage.style.height).toBe("auto")
      expect(listPage.style.overflow).toBe("visible")
    } else {
      // Acceptable alternative: drop list-page for free-flow shell (Agent Ad Hoc style).
      const heading = screen.getByRole("heading", { name: /^Telescope$/i })
      const wrap = heading.parentElement as HTMLElement
      expect(wrap.style.overflow).not.toBe("hidden")
      expect(wrap.style.height === "" || wrap.style.height === "auto").toBe(true)
    }
  })

  it("AST-1744: single Tag primary + Class always enabled; no Selector slot", async () => {
    const user = userEvent.setup()
    renderWithProviders(<AdminTelescope />)

    expect(screen.getByText(/^Tag \(optional\)/i)).toBeInTheDocument()
    expect(screen.getByText(/Class name \(optional\)/i)).toBeInTheDocument()
    // Separate Selector input removed — Tag is the only primary.
    expect(screen.queryByText(/^Selector \(optional\)/i)).not.toBeInTheDocument()

    const tagInput = screen.getByPlaceholderText(/div \/ span/i)
    await user.type(tagInput, "div")
    const classInput = screen.getByPlaceholderText(/no leading dot/i)
    expect(classInput).not.toBeDisabled()
  })

  it("AST-1746: AdminTelescope exposes optional Id filter control", () => {
    renderWithProviders(<AdminTelescope />)
    // Pre-fix: Class name exists; Id secondary filter is absent.
    expect(screen.getByText(/Class name/i)).toBeInTheDocument()
    expect(screen.getByText(/^Id\b/i)).toBeInTheDocument()
  })

  it("AST-1730: raw response is read-only scrollable wrapping textarea", async () => {
    const user = userEvent.setup()
    renderWithProviders(<AdminTelescope />)

    await user.type(screen.getByPlaceholderText("https://…"), "https://example.com")
    await user.click(screen.getByRole("button", { name: /Scrape/i }))

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Raw text/i })).toBeInTheDocument()
    })

    const areas = document.querySelectorAll(
      "textarea.admin-telescope-pre",
    ) as NodeListOf<HTMLTextAreaElement>
    expect(areas.length).toBeGreaterThanOrEqual(1)
    const raw = areas[0]
    expect(raw.readOnly).toBe(true)
    expect(raw.style.maxHeight).toBe("60vh")
    expect(raw.style.overflow).toBe("auto")
    expect(raw.style.whiteSpace).toBe("pre-wrap")
    expect(raw.style.wordBreak).toBe("break-word")
    expect(raw.value).toContain("line1")
  })

  it("AST-1730: full JSON dump uses the same read-only textarea shape", async () => {
    const user = userEvent.setup()
    renderWithProviders(<AdminTelescope />)

    await user.type(screen.getByPlaceholderText("https://…"), "https://example.com")
    await user.click(screen.getByRole("button", { name: /Scrape/i }))
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Show full JSON/i })).toBeInTheDocument()
    })
    await user.click(screen.getByRole("button", { name: /Show full JSON/i }))

    await waitFor(() => {
      const areas = document.querySelectorAll(
        "textarea.admin-telescope-pre",
      ) as NodeListOf<HTMLTextAreaElement>
      expect(areas.length).toBeGreaterThanOrEqual(2)
      const jsonPane = areas[areas.length - 1]
      expect(jsonPane.readOnly).toBe(true)
      expect(jsonPane.style.maxHeight).toBe("60vh")
      expect(jsonPane.style.overflow).toBe("auto")
      expect(jsonPane.style.whiteSpace).toBe("pre-wrap")
      expect(jsonPane.value).toContain('"final_url"')
    })
  })
})
