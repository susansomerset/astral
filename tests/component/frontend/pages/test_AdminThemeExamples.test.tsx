import { readdirSync, readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { screen, within } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminThemeExamples from "../../../../src/ui/frontend/src/pages/AdminThemeExamples"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

// Mirrors UI_CONFIG["themes"] (pinned server-side in test_config.py::TestAst2047ThemeRegistry).
const THEMES = {
  dark: { label: "Dark", profile_selectable: true },
  light: { label: "Light", profile_selectable: true },
  light_parchment: { label: "Light (Parchment)", profile_selectable: false },
  light_slate: { label: "Light (Slate)", profile_selectable: false },
}

describe("AdminThemeExamples — AST-2047", () => {
  it("renders one labeled panel per registry id with the shared sample; read-only (§6c, AC6)", async () => {
    installBaseApiMocks(mockedApi, url =>
      url === "/api/ui_config" ? jsonResponse({ column_types: {}, themes: THEMES, default_theme: "dark" }) : undefined,
    )
    renderWithProviders(<AdminThemeExamples />)

    expect(await screen.findByRole("heading", { name: "Theme Examples" })).toBeInTheDocument()
    const panels = Array.from(document.querySelectorAll<HTMLElement>("section.theme-examples-panel"))
    expect(panels.map(p => p.dataset.theme)).toEqual(Object.keys(THEMES))

    panels.forEach((panel, i) => {
      const p = within(panel)
      expect(p.getByRole("heading", { level: 2, name: Object.values(THEMES)[i].label })).toBeInTheDocument()
      expect(panel.querySelector(".btn.primary")).not.toBeNull()
      expect(panel.querySelector("table.list-page-table tbody tr")).not.toBeNull()
      expect(panel.querySelector("select.dep-select")).not.toBeNull()
      expect(Array.from(panel.querySelectorAll(".theme-examples-grade .grade-dot"), d => d.textContent)).toEqual(
        ["A", "B", "C", "D", "F", "X"],
      )
      expect(panel.querySelector(".toast")).not.toBeNull()
    })

    // Viewing must not touch candidate_data.theme: every call is a read.
    for (const [, init] of mockedApi.mock.calls) {
      expect((init as RequestInit | undefined)?.method ?? "GET").toBe("GET")
    }
  })
})

// AST-2064: examples-only grade-color candidates; tokens override the panel's grade tokens per row.
const GRADE_SETS = {
  deep: { label: "Deep", tokens: { "--grade-a": "#1e7b34", "--grade-x": "#6b46c1", "--text-on-grade": "#ffffff" } },
  soft: { label: "Soft", tokens: { "--grade-a": "#b7e4c0", "--grade-x": "#ddd6fe", "--text-on-grade": "#1f1830" } },
}

describe("AdminThemeExamples — AST-2064 grade color options", () => {
  it("[bug-repro] each panel shows one labeled row per grade set with inline grade tokens; main grade row unchanged", async () => {
    // uiConfig caches at module level (the AST-2047 case above already loaded one) — fresh graph for this config.
    vi.resetModules()
    const freshApi = vi.mocked((await import("../../../../src/ui/frontend/src/lib/api")).default)
    // Both URLs: this sub's loader still calls /api/system/ui_config until sibling AST-2065's fix merges.
    const handler = (url: string) =>
      url === "/api/ui_config" || url === "/api/system/ui_config"
        ? jsonResponse({ column_types: {}, themes: THEMES, default_theme: "dark", theme_example_grade_sets: GRADE_SETS })
        : undefined
    installBaseApiMocks(mockedApi, handler)
    installBaseApiMocks(freshApi, handler)
    const Page = (await import("../../../../src/ui/frontend/src/pages/AdminThemeExamples")).default
    renderWithProviders(<Page />)

    expect(await screen.findByRole("heading", { name: "Theme Examples" })).toBeInTheDocument()
    const panels = Array.from(document.querySelectorAll<HTMLElement>("section.theme-examples-panel"))
    expect(panels).toHaveLength(Object.keys(THEMES).length)
    for (const panel of panels) {
      const options = panel.querySelector<HTMLElement>(".theme-examples-grade-options")
      expect(options, panel.dataset.theme).not.toBeNull()
      expect(within(options!).getByText("Grade color options")).toBeInTheDocument()
      const rows = Array.from(options!.querySelectorAll<HTMLElement>(".theme-examples-row"))
      expect(rows.map(r => r.querySelector(".theme-examples-grade-option-name")?.textContent)).toEqual(["Deep", "Soft"])
      rows.forEach((row, i) => {
        const set = Object.values(GRADE_SETS)[i]
        for (const [token, value] of Object.entries(set.tokens)) expect(row.style.getPropertyValue(token)).toBe(value)
        expect(Array.from(row.querySelectorAll(".grade-dot"), d => d.textContent)).toEqual(["A", "B", "C", "D", "F", "X"])
      })
      // The panel's own grade row stays exactly one A–X set (option rows must not reuse .theme-examples-grade).
      expect(Array.from(panel.querySelectorAll(".theme-examples-grade .grade-dot"), d => d.textContent)).toEqual(
        ["A", "B", "C", "D", "F", "X"],
      )
    }
  })
})

describe("AdminThemeExamples — AST-2077 compact grade-dot samples", () => {
  it("[bug-repro] each grade-color option has a letterless Recommended-list grade row beside it, in that option's tokens", async () => {
    // Same fresh-graph setup as AST-2064 (uiConfig caches at module level).
    vi.resetModules()
    const freshApi = vi.mocked((await import("../../../../src/ui/frontend/src/lib/api")).default)
    const handler = (url: string) =>
      url === "/api/ui_config" || url === "/api/system/ui_config"
        ? jsonResponse({ column_types: {}, themes: THEMES, default_theme: "dark", theme_example_grade_sets: GRADE_SETS })
        : undefined
    installBaseApiMocks(mockedApi, handler)
    installBaseApiMocks(freshApi, handler)
    const Page = (await import("../../../../src/ui/frontend/src/pages/AdminThemeExamples")).default
    renderWithProviders(<Page />)

    expect(await screen.findByRole("heading", { name: "Theme Examples" })).toBeInTheDocument()
    const panels = Array.from(document.querySelectorAll<HTMLElement>("section.theme-examples-panel"))
    expect(panels).toHaveLength(Object.keys(THEMES).length)
    for (const panel of panels) {
      const options = panel.querySelector<HTMLElement>(".theme-examples-grade-options")!
      const lettered = Array.from(options.querySelectorAll<HTMLElement>(".theme-examples-row"))
      const compact = Array.from(options.querySelectorAll<HTMLElement>(".recommended-list-phase-grade-row"))
      expect(compact, panel.dataset.theme).toHaveLength(Object.keys(GRADE_SETS).length)
      compact.forEach((row, i) => {
        const set = Object.values(GRADE_SETS)[i]
        // Beside its own option: shares a parent with lettered row i, and is not nested inside it.
        expect(row.parentElement).toBe(lettered[i].parentElement)
        for (const [token, value] of Object.entries(set.tokens)) expect(row.style.getPropertyValue(token)).toBe(value)
        // Recommended Job List markup (buildPhaseListGradeRow): <span><span class="grade-dot dot-<g> grade-dot-letterless"/></span>.
        const dots = Array.from(row.querySelectorAll<HTMLElement>(":scope > span > .grade-dot"))
        expect(dots.map(d => [...d.classList].sort())).toEqual(
          ["a", "b", "c", "d", "f", "x"].map(g => [`dot-${g}`, "grade-dot", "grade-dot-letterless"]),
        )
        expect(dots.every(d => d.textContent === "")).toBe(true)
      })
    }
  })
})

// jsdom does not load App.css, so the palette contract is read from the stylesheet itself.
describe("App.css theme token blocks — AST-2047", () => {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../../..")
  const css = readFileSync(resolve(root, "src/ui/frontend/src/App.css"), "utf8")
  const blockRe = /(?:^|\n)(?::root,\s*)?\[data-theme="([\w-]+)"\]\s*\{([^}]*)\}/g
  // palette id -> { --token: value }
  const blocks = new Map(
    Array.from(css.matchAll(blockRe), m => [
      m[1],
      Object.fromEntries(Array.from(m[2].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g), d => [d[1], d[2].trim()])),
    ]),
  )

  it("Dark is :root and [data-theme=dark]; one block per registry id", () => {
    expect(css).toMatch(/(?:^|\n):root,\s*\[data-theme="dark"\]\s*\{/)
    expect([...blocks.keys()]).toEqual(Object.keys(THEMES))
  })

  it("every Light block declares exactly the Dark token names, and the Lights pairwise differ (AC4)", () => {
    const darkNames = Object.keys(blocks.get("dark")!).sort()
    const lights = [...blocks.keys()].filter(id => id !== "dark")
    for (const id of lights) expect(Object.keys(blocks.get(id)!).sort(), id).toEqual(darkNames)
    for (let i = 0; i < lights.length; i++) {
      for (let j = i + 1; j < lights.length; j++) {
        const [a, b] = [blocks.get(lights[i])!, blocks.get(lights[j])!]
        const differs = ["--bg-deep", "--bg-card", "--accent-contrast"].some(k => a[k] !== b[k])
        expect(differs, `${lights[i]} vs ${lights[j]}`).toBe(true)
      }
    }
  })

  it("[bug-repro] AST-2076: in light and light_parchment, the accent and nav group label resolve to the header colour", () => {
    // Follow var(--x) chains inside one block; the purple itself is a palette choice (UAT), so only equality is pinned.
    const resolveIn = (b: Record<string, string>, name: string) => {
      let v: string | undefined = b[name]
      for (let m; v && (m = v.match(/^var\((--[\w-]+)\)$/)); ) v = b[m[1]]
      return v
    }
    for (const id of ["light", "light_parchment"]) {
      const b = blocks.get(id)!
      const heading = resolveIn(b, "--heading")
      expect(heading, id).toBeDefined()
      expect(resolveIn(b, "--accent-contrast"), `${id} --accent-contrast`).toBe(heading)
      expect(resolveIn(b, "--nav-group-label"), `${id} --nav-group-label`).toBe(heading)
    }
  })

  it("no hex or non-black rgba outside token blocks; every var(--x) is defined in a token block (AC5, App.css half)", () => {
    const body = css.replace(blockRe, "\n").replace(/\/\*[\s\S]*?\*\//g, "")
    expect(body.match(/#[0-9a-fA-F]{3,8}\b/g)).toBeNull()
    expect(body.match(/rgba?\((?!\s*0\s*,\s*0\s*,\s*0\s*,)[^)]*\)/g)).toBeNull()
    const defined = new Set([...blocks.values()].flatMap(b => Object.keys(b)))
    const undefinedRefs = [...new Set(Array.from(css.matchAll(/var\((--[\w-]+)/g), m => m[1]))].filter(n => !defined.has(n))
    expect(undefinedRefs).toEqual([])
  })

  it("AST-2049: no hex in .ts/.tsx source and every var(--x) in source is defined in a token block (AC9, epic-wide)", () => {
    const srcDir = resolve(root, "src/ui/frontend/src")
    const files = (readdirSync(srcDir, { recursive: true }) as string[])
      .filter(f => /\.(tsx?|css)$/.test(f) && !/\.test\./.test(f))
    const defined = new Set([...blocks.values()].flatMap(b => Object.keys(b)))
    const hexHits: string[] = []
    const undefinedRefs: string[] = []
    for (const f of files) {
      const text = readFileSync(resolve(srcDir, f), "utf8")
      // Leading char class skips HTML entities like &#9660; (same pattern as the ticket's rg).
      if (!f.endsWith(".css")) for (const m of text.matchAll(/["' ,(]#[0-9a-fA-F]{3,8}\b/g)) hexHits.push(`${f}: ${m[0]}`)
      for (const m of text.matchAll(/var\((--[\w-]+)/g)) if (!defined.has(m[1])) undefinedRefs.push(`${f}: ${m[1]}`)
    }
    expect(files.length).toBeGreaterThan(50)
    expect(hexHits).toEqual([])
    expect(undefinedRefs).toEqual([])
  })
})
