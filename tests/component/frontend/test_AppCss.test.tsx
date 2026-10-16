import { readdirSync, readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

// Mirrors UI_CONFIG["themes"] (pinned server-side in test_config.py::TestAst2047ThemeRegistry).
const THEMES = {
  dark: { label: "Dark", profile_selectable: true },
  light: { label: "Light", profile_selectable: true },
  shapes_light: { label: "Shapes - Light", profile_selectable: true },
  shapes_dark: { label: "Shapes - Dark", profile_selectable: true },
}

// AST-2129: a Shapes twin shares its sibling's token block through a selector list — it has no block of its own.
const TWIN_OF: Record<string, string> = { shapes_dark: "dark", shapes_light: "light" }

// jsdom does not load App.css, so the palette contract is read from the stylesheet itself.
describe("App.css theme token blocks — AST-2047", () => {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..")
  const css = readFileSync(resolve(root, "src/ui/frontend/src/App.css"), "utf8")
  // A token block opens at line start with a selector list of only :root / [data-theme="<id>"] (AST-2129 twins),
  // so scoped rules like `:is([data-theme=…]) .grade-dot {` never count as blocks.
  const blockRe = /(?:^|\n)((?::root|\[data-theme="[\w-]+"\])(?:\s*,\s*(?::root|\[data-theme="[\w-]+"\]))*)\s*\{([^}]*)\}/g
  const parsed = Array.from(css.matchAll(blockRe), m => ({
    selector: m[1].replace(/\s+/g, " "),
    ids: Array.from(m[1].matchAll(/\[data-theme="([\w-]+)"\]/g), i => i[1]),
    tokens: Object.fromEntries(Array.from(m[2].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g), d => [d[1], d[2].trim()])),
  }))
  // palette id (the block's first [data-theme]) -> { --token: value }
  const blocks = new Map(parsed.map(b => [b.ids[0], b.tokens]))

  it("Dark is :root and [data-theme=dark]; one block per registry id", () => {
    expect(css).toMatch(/(?:^|\n):root,\s*\[data-theme="dark"\]/)
    // AST-2123 deleted the unregistered alternate blocks; AST-2129 twins ride a sibling's block, so the
    // blocks are exactly the non-twin registry ids.
    expect([...blocks.keys()]).toEqual(Object.keys(THEMES).filter(id => !(id in TWIN_OF)))
  })

  it("AST-2129 AC2: each Shapes twin sits on its sibling's block; every registry id on exactly one block", () => {
    expect(parsed.map(b => b.selector)).toEqual([
      ':root, [data-theme="dark"], [data-theme="shapes_dark"]',
      '[data-theme="light"], [data-theme="shapes_light"]',
    ])
    const allIds = parsed.flatMap(b => b.ids)
    expect([...allIds].sort()).toEqual(Object.keys(THEMES).sort())
    for (const [twin, sibling] of Object.entries(TWIN_OF)) {
      expect(parsed.find(b => b.ids.includes(twin))?.ids[0], twin).toBe(sibling)
    }
    // Shared, not copied: one declaration per palette (AC2's `git grep -c '--grade-a:'` = 2).
    expect(css.match(/--grade-a:/g)).toHaveLength(2)
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

  it("AST-2129 AC4 (token half): shape ring widths — Light 1.5px compact / 2.5px lettered, Dark 0, per grade", () => {
    for (const g of ["a", "b", "c", "d", "f", "x"]) {
      expect(blocks.get("light")![`--grade-${g}-shape-ring-width`], g).toBe("1.5px")
      expect(blocks.get("light")![`--grade-${g}-shape-ring-width-lettered`], g).toBe("2.5px")
      expect(blocks.get("dark")![`--grade-${g}-shape-ring-width`], g).toBe("0px")
      expect(blocks.get("dark")![`--grade-${g}-shape-ring-width-lettered`], g).toBe("0px")
    }
  })
})

// AST-2129: Shapes §9b rules. jsdom has no cascade (and no :is() / var() resolution), so these pin the
// declarations that produce AC 3–6; computed-style proof in a real browser stays with parent UAT.
describe("App.css Shapes grade marks — AST-2129", () => {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..")
  const css = readFileSync(resolve(root, "src/ui/frontend/src/App.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "")
  const SHAPES = ':is([data-theme="shapes_light"], [data-theme="shapes_dark"])'
  // Innermost rules only: [^{}] keeps @media wrappers out of the selector.
  const rules = Array.from(css.matchAll(/([^{}]+)\{([^{}]*)\}/g), m => ({
    selector: m[1].trim().replace(/\s+/g, " "),
    decls: Object.fromEntries(
      m[2].split(";").map(d => d.trim()).filter(Boolean).map(d => {
        const i = d.indexOf(":")
        return [d.slice(0, i).trim(), d.slice(i + 1).trim().replace(/\s+/g, " ")]
      }),
    ) as Record<string, string>,
  }))
  // Exactly one rule per selector, so a later duplicate can't silently override what's pinned here.
  const rule = (selector: string) => {
    const hits = rules.filter(r => r.selector === selector)
    expect(hits, selector).toHaveLength(1)
    return hits[0].decls
  }
  // calc(22px * N) -> N
  const ratio = (v: string) => Number(v.match(/^calc\(22px \* ([\d.]+)\)$/)?.[1])

  it("AC6: outside the Shapes themes the SVG is display:none; every other SVG/path grade rule is Shapes-scoped", () => {
    expect(rule(".grade-dot > svg")).toEqual({ display: "none" })
    const shapeRules = rules.filter(r => /grade-dot|dot-[abcdfx]/.test(r.selector) && /\b(svg|path)\b/.test(r.selector))
    expect(shapeRules.length).toBeGreaterThan(1)
    for (const r of shapeRules) {
      if (r.selector === ".grade-dot > svg") continue
      expect(r.selector.startsWith(`${SHAPES} `), r.selector).toBe(true)
    }
  })

  it("AC3: the circle is dropped and the SVG shown, unclipped, filling the box", () => {
    expect(rule(`${SHAPES} .grade-dot`)).toMatchObject({ background: "none", "box-shadow": "none" })
    expect(rule(`${SHAPES} .grade-dot > svg`)).toMatchObject({
      display: "block", overflow: "visible", width: "100%", height: "100%",
    })
    expect(rule(`${SHAPES} .grade-dot path`)).toMatchObject({
      "vector-effect": "non-scaling-stroke", "stroke-linejoin": "round",
    })
  })

  it.each(["a", "b", "c", "d", "f"])("AC3/AC4 %s: path fills with the grade fill; ring = grade ring colour at the shape ring width", g => {
    expect(rule(`${SHAPES} .dot-${g} path`)).toEqual({
      fill: `var(--grade-${g})`,
      stroke: `var(--grade-${g}-ring)`,
      "stroke-width": `var(--grade-${g}-shape-ring-width-lettered)`,
    })
    expect(rule(`${SHAPES} .grade-dot-letterless.dot-${g} path`)).toEqual({
      "stroke-width": `var(--grade-${g}-shape-ring-width)`,
    })
  })

  it("AC3/AC4 X: stroke-only cross in the X fill (20 lettered, 24 compact, round caps); ring = drop-shadows in --grade-x-ring", () => {
    expect(rule(`${SHAPES} .dot-x path`)).toEqual({
      fill: "none", stroke: "var(--grade-x)", "stroke-width": "20", "stroke-linecap": "round", "vector-effect": "none",
    })
    expect(rule(`${SHAPES} .grade-dot-letterless.dot-x path`)).toEqual({ "stroke-width": "24" })
    for (const [sel, width] of [
      [`${SHAPES} .dot-x > svg`, "--grade-x-shape-ring-width-lettered"],
      [`${SHAPES} .grade-dot-letterless.dot-x > svg`, "--grade-x-shape-ring-width"],
    ]) {
      const filter = rule(sel).filter
      expect(filter.match(/drop-shadow\(/g), sel).toHaveLength(4)
      expect(filter.match(/var\(--grade-x-ring\)/g), sel).toHaveLength(4)
      // Every offset reads the right ring width (compact vs lettered), and no other width token.
      expect([...new Set(Array.from(filter.matchAll(/var\((--grade-x-shape-ring-width[\w-]*)\)/g), m => m[1]))], sel).toEqual([width])
    }
  })

  it("AC5: letter at the brief's sizes (46/100, triangles 38/100) and at the triangle centroids; no glyph on X", () => {
    expect(ratio(rule(`${SHAPES} .grade-dot:is(.dot-a, .dot-b, .dot-c)`)["font-size"])).toBeCloseTo(0.46, 2)
    expect(ratio(rule(`${SHAPES} .grade-dot:is(.dot-d, .dot-f)`)["font-size"])).toBeCloseTo(0.38, 2)
    // One-sided padding shifts the flex-centred letter by half the padding: centre = 50% ± pad/2 (AC5: ±3%).
    const d = rule(`${SHAPES} .grade-dot.dot-d`)
    const f = rule(`${SHAPES} .grade-dot.dot-f`)
    expect(Math.abs(50 + (ratio(d["padding-top"]) * 100) / 2 - 63)).toBeLessThanOrEqual(3)
    expect(Math.abs(50 - (ratio(f["padding-bottom"]) * 100) / 2 - 39)).toBeLessThanOrEqual(3)
    // font-size 0, not visibility/display, so the span keeps its img role + accessible name (plan Stage 3 decision).
    expect(rule(`${SHAPES} .grade-dot.dot-x`)).toEqual({ "font-size": "0" })
  })
})
