/**
 * AST-1728 bug-repro — AdminTelescope routed page (§6c).
 * Pre-fix: module missing → import fails red. Post-fix: page loads.
 */
import { describe, expect, it } from "vitest"

describe("AST-1728 AdminTelescope bug-repro", () => {
  it("AST-1728: AdminTelescope page module exports a component", async () => {
    const mod = await import(
      "../../../../src/ui/frontend/src/pages/AdminTelescope"
    )
    expect(mod.default).toBeTypeOf("function")
  })
})
