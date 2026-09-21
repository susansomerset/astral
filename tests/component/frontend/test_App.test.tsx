import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

const appSrcPath = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../../src/ui/frontend/src/App.tsx",
)

describe("App data router — AST-1335", () => {
  it("wires createBrowserRouter + RouterProvider (no BrowserRouter)", () => {
    // Do not render <App /> here: RR7 data-router init navigates via undici Request and
    // throws unhandled AbortSignal under Node 24 + jsdom (exit 1 even when asserts pass).
    const src = readFileSync(appSrcPath, "utf8")
    expect(src).toMatch(/createBrowserRouter\s*\(\s*routes\s*\)/)
    expect(src).toMatch(/RouterProvider\s+router=\{router\}/)
    expect(src).not.toMatch(/\bBrowserRouter\b/)
  })
})
