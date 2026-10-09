import { readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({ default: vi.fn() }))

const LONG = "Principal Software Engineer, Distributed Platform Reliability \u2014 Zanzibar Office"
const EDGE = "Edge Title Exactly At The Fifty Character Limit ok"

// Fresh module graph per test: uiConfig keeps a module-level cache, so each test serves its own ui_config.
async function load(uiConfig: Record<string, unknown> = { column_types: {} }) {
  vi.resetModules()
  const api = (await import("../../../../src/ui/frontend/src/lib/api")).default
  vi.mocked(api).mockImplementation(async (url: string) => {
    if (url === "/api/ui_config") return { json: async () => uiConfig } as Response
    throw new Error(`Unhandled api ${url}`)
  })
  return (await import("../../../../src/ui/frontend/src/components/JobTitleText")).default
}

describe("JobTitleText (AST-1982)", () => {
  it("50-char title renders exactly — no wrapper, tooltip, or title attribute", async () => {
    const JobTitleText = await load()
    const { container } = render(<div data-testid="host"><JobTitleText title={EDGE} fallback="—" /></div>)
    const host = screen.getByTestId("host")
    expect(host.innerHTML).toBe(EDGE)
    await userEvent.hover(host)
    expect(screen.queryByRole("tooltip")).toBeNull()
    expect(container.querySelector("[title]")).toBeNull()
  })

  it("long title cut via the config length (fallback 50) with … and no native title", async () => {
    const JobTitleText = await load()
    const { container } = render(<JobTitleText title={LONG} fallback="—" />)
    expect(container.textContent).toBe(`${LONG.slice(0, 50)}\u2026`)
    expect(container.querySelector("[title]")).toBeNull()
  })

  it("hover opens one tooltip with the full title, portaled to body; mouse-out removes it", async () => {
    const JobTitleText = await load()
    const { container } = render(<table><tbody><tr><td><JobTitleText title={LONG} fallback="—" /></td></tr></tbody></table>)
    const span = screen.getByText(`${LONG.slice(0, 50)}\u2026`)
    await userEvent.hover(span)
    const tips = screen.getAllByRole("tooltip")
    expect(tips).toHaveLength(1)
    expect(tips[0].textContent).toBe(LONG)
    expect(tips[0]).toHaveClass("job-title-tooltip")
    expect(tips[0].parentElement).toBe(document.body)
    expect(container.contains(tips[0])).toBe(false)
    await userEvent.unhover(span)
    expect(screen.queryByRole("tooltip")).toBeNull()
  })

  it("any scroll closes an open tooltip", async () => {
    const JobTitleText = await load()
    render(<JobTitleText title={LONG} fallback="—" />)
    await userEvent.hover(screen.getByText(`${LONG.slice(0, 50)}\u2026`))
    expect(screen.getByRole("tooltip")).toBeInTheDocument()
    fireEvent.scroll(window)
    await waitFor(() => expect(screen.queryByRole("tooltip")).toBeNull())
  })

  it.each([null, undefined, ""])("empty title (%s) renders the caller's fallback", async (title) => {
    const JobTitleText = await load()
    const { container } = render(<JobTitleText title={title} fallback={<em>no title</em>} />)
    expect(container.innerHTML).toBe("<em>no title</em>")
  })

  it("cut length follows UI_CONFIG job_title_truncate_chars once ui_config loads", async () => {
    const JobTitleText = await load({ column_types: {}, job_title_truncate_chars: 20 })
    const { container } = render(<JobTitleText title={LONG} fallback="—" />)
    await waitFor(() => expect(container.textContent).toBe(`${LONG.slice(0, 20)}\u2026`))
    await userEvent.hover(screen.getByText(`${LONG.slice(0, 20)}\u2026`))
    expect(screen.getByRole("tooltip").textContent).toBe(LONG)
  })

  // jsdom does not load App.css, so the wrap / fixed-width / portal-layer contract is read from the rule itself.
  it("tooltip style wraps (white-space: normal) inside a fixed pixel max-width", () => {
    const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../../..")
    const css = readFileSync(resolve(root, "src/ui/frontend/src/App.css"), "utf8")
    const rule = css.match(/\.job-title-tooltip\s*\{([^}]*)\}/)?.[1] ?? ""
    expect(rule).toMatch(/white-space:\s*normal/)
    expect(rule).toMatch(/max-width:\s*\d+px/)
    expect(rule).toMatch(/position:\s*fixed/)
  })
})
