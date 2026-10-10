import { readdirSync, readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

// Mirrors UI_CONFIG["themes"] (pinned server-side in test_config.py::TestAst2047ThemeRegistry).
const THEMES = {
  dark: { label: "Dark", profile_selectable: true },
  light: { label: "Light", profile_selectable: true },
}

// jsdom does not load App.css, so the palette contract is read from the stylesheet itself.
describe("App.css theme token blocks — AST-2047", () => {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..")
  const css = readFileSync(resolve(root, "src/ui/frontend/src/App.css"), "utf8")
  const blockRe = /(?:^|\n)(?::root,\s*)?\[data-theme="([\w-]+)"\]\s*\{([^}]*)\}/g
  // palette id -> { --token: value }
  const blocks = new Map(
    Array.from(css.matchAll(blockRe), m => [
      m[1],
      Object.fromEntries(Array.from(m[2].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g), d => [d[1], d[2].trim()])),
    ]),
  )

  it("Dark is :root and [data-theme=dark]; every registry id has a block", () => {
    expect(css).toMatch(/(?:^|\n):root,\s*\[data-theme="dark"\]\s*\{/)
    // AST-2122 retired the two alternates from the registry; their unregistered blocks stay in App.css
    // until AST-2123 deletes them, so this is a superset check — AST-2123 restores exact equality.
    expect([...blocks.keys()]).toEqual(expect.arrayContaining(Object.keys(THEMES)))
    expect([...blocks.keys()][0]).toBe("dark")
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

  it("[bug-repro] AST-2076: in light, the accent and nav group label resolve to the header colour", () => {
    // Follow var(--x) chains inside one block; the purple itself is a palette choice (UAT), so only equality is pinned.
    const resolveIn = (b: Record<string, string>, name: string) => {
      let v: string | undefined = b[name]
      for (let m; v && (m = v.match(/^var\((--[\w-]+)\)$/)); ) v = b[m[1]]
      return v
    }
    const b = blocks.get("light")!
    const heading = resolveIn(b, "--heading")
    expect(heading).toBeDefined()
    expect(resolveIn(b, "--accent-contrast"), "--accent-contrast").toBe(heading)
    expect(resolveIn(b, "--nav-group-label"), "--nav-group-label").toBe(heading)
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
