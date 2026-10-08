import { readdirSync, readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it, vi } from "vitest"
import { resolveJobTitleTruncateChars } from "../../../../src/ui/frontend/src/lib/uiConfig"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({ default: vi.fn() }))

describe("uiConfig resolvers", () => {
  // AST-1982: served job_title_truncate_chars wins; falls back to 50 before load or on a bad value.
  it("resolveJobTitleTruncateChars uses the served value, else 50", () => {
    expect(resolveJobTitleTruncateChars({ column_types: {}, job_title_truncate_chars: 20 })).toBe(20)
    expect(resolveJobTitleTruncateChars({ column_types: {} })).toBe(50)
    expect(resolveJobTitleTruncateChars({ column_types: {}, job_title_truncate_chars: 0 })).toBe(50)
    expect(resolveJobTitleTruncateChars(null)).toBe(50)
  })
})

// AST-2065: Flask serves UI_CONFIG only at /api/ui_config (system_bp url_prefix "/api"). The old
// /api/system/ui_config fell through to the SPA catch-all, so every consumer silently got the fallback.
describe("uiConfig URL — AST-2065", () => {
  it("[bug-repro] loadUiConfig fetches /api/ui_config", async () => {
    // Fresh module graph: uiConfig caches the loaded config at module level.
    vi.resetModules()
    const api = vi.mocked((await import("../../../../src/ui/frontend/src/lib/api")).default)
    api.mockResolvedValue({ json: async () => ({ column_types: {} }) } as Response)
    const { loadUiConfig } = await import("../../../../src/ui/frontend/src/lib/uiConfig")
    await new Promise<void>(done => loadUiConfig(done))
    expect(api.mock.calls.map(([url]) => url)).toEqual(["/api/ui_config"])
  })

  it("[bug-repro] no frontend source references /api/system/ui_config", () => {
    const srcDir = resolve(dirname(fileURLToPath(import.meta.url)), "../../../../src/ui/frontend/src")
    const hits = (readdirSync(srcDir, { recursive: true }) as string[])
      .filter(f => /\.tsx?$/.test(f) && readFileSync(resolve(srcDir, f), "utf8").includes("/api/system/ui_config"))
    expect(hits).toEqual([])
  })
})
