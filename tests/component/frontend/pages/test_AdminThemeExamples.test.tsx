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
      url === "/api/system/ui_config" ? jsonResponse({ column_types: {}, themes: THEMES, default_theme: "dark" }) : undefined,
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
        const differs = ["--bg-deep", "--bg-card", "--accent-gold"].some(k => a[k] !== b[k])
        expect(differs, `${lights[i]} vs ${lights[j]}`).toBe(true)
      }
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
