/**
 * AST-1254 — MV3 empty-shell placement + toolchain contract (no auth/capture).
 * AC1 load-unpacked remains a manual Chrome check; this file anchors AC2–AC4 + placement docs.
 */
import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

const repoRoot = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../../..")

function readRepo(...parts: string[]): string {
  return readFileSync(path.join(repoRoot, ...parts), "utf8")
}

describe("Extension MV3 scaffold — AST-1254", () => {
  it("package lives under src/ui/extension with Chrome + Firefox build scripts", () => {
    const pkg = JSON.parse(readRepo("src/ui/extension/package.json")) as {
      scripts: Record<string, string>
      devDependencies: Record<string, string>
    }
    expect(pkg.scripts.build).toBe("wxt build")
    expect(pkg.scripts["build:firefox"]).toBe("wxt build -b firefox")
    expect(pkg.scripts.dev).toBe("wxt")
    expect(pkg.scripts["test:component"]).toContain("vitest")
    expect(pkg.devDependencies.wxt).toMatch(/\^?0\.21/)
  })

  it("gitignore covers node_modules, .output, .wxt, and *.pem", () => {
    const gi = readRepo(".gitignore")
    expect(gi).toContain("src/ui/extension/node_modules/")
    expect(gi).toContain("src/ui/extension/.output/")
    expect(gi).toContain("src/ui/extension/.wxt/")
    expect(gi).toContain("src/ui/extension/*.pem")
  })

  it("wxt config pins Chrome key + gecko id and requests no capture permissions", () => {
    const cfg = readRepo("src/ui/extension/wxt.config.ts")
    expect(cfg).toContain("CHROME_EXTENSION_KEY")
    expect(cfg).toContain("surfer@astralcareermatch.com")
    expect(cfg).toContain("srcDir: 'src'")
    expect(cfg).not.toMatch(/host_permissions/)
    expect(cfg).not.toMatch(/\b(activeTab|scripting|storage|alarms)\b/)
  })

  it("background entrypoint is an empty shell (no network)", () => {
    const bg = readRepo("src/ui/extension/src/entrypoints/background.ts")
    expect(bg).toMatch(/defineBackground/)
    expect(bg).not.toMatch(/\bfetch\s*\(/)
    expect(bg).not.toMatch(/XMLHttpRequest/)
    expect(bg).not.toMatch(/page_intake/)
  })

  it("Vitest include points at tests/component/extension/", () => {
    const vitestCfg = readRepo("src/ui/extension/vitest.config.ts")
    expect(vitestCfg).toContain("tests/component/extension/**/*.test.{ts,tsx}")
  })

  it("Flask _DIST is frontend/dist only — extension .output is not mounted (AC3)", () => {
    const server = readRepo("src/ui/server.py")
    expect(server).toMatch(
      /_DIST\s*=\s*Path\(__file__\)\.parent\s*\/\s*"frontend"\s*\/\s*"dist"/,
    )
    expect(server).not.toMatch(/extension\/\.output|ui\/extension\/\.output/)
  })

  it("CODE_RULES and frontend-file-placement statute name the second client surface", () => {
    const rules = readRepo("docs/ASTRAL_CODE_RULES.md")
    expect(rules).toMatch(/extension\//)
    expect(rules).toMatch(/Python import-direction|governs Python only|Python only/i)

    const statute = readRepo(
      "canon/statutes/astral/ui/astral.ui.frontend-file-placement.md",
    )
    expect(statute).toContain("src/ui/extension/**")
    expect(statute).toContain("src/ui/extension/src/entrypoints/background.ts")
  })

  it("README documents load-unpacked Chrome path and Firefox build", () => {
    const readme = readRepo("src/ui/extension/README.md")
    expect(readme).toContain(".output/chrome-mv3")
    expect(readme).toContain("npm run build")
    expect(readme).toContain("npm run build:firefox")
    expect(readme).toMatch(/not.*served|Flask/i)
  })
})
