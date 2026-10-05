import { useRoutes } from "react-router-dom"
import { describe, expect, it } from "vitest"
import routes from "../../../src/ui/frontend/src/routes"

describe("routes", () => {
  it("defines authenticate, auth shell, and navigation routes", () => {
    expect(routes).toHaveLength(2)
    expect(routes[0].path).toBe("authenticate")
    const authShell = routes[1]
    expect(authShell.element).toBeTruthy()
    const navShell = authShell.children?.[0]
    expect(navShell?.element).toBeTruthy()
    expect(navShell?.children?.some(child => child.index)).toBe(true)
    expect(navShell?.children?.some(child => child.path === "*")).toBe(true)
    // AST-1975: Jobs → Ready / Review / Processing; Recommended, In Review, Responded retired
    for (const path of ["jobs/ready", "jobs/review", "jobs/processing", "jobs/applied", "jobs/skipped"]) {
      expect(navShell?.children?.some(child => child.path === path)).toBe(true)
    }
    for (const path of ["jobs/recommended", "jobs/in_review", "jobs/responded"]) {
      expect(navShell?.children?.some(child => child.path === path)).toBe(false)
    }
    expect(navShell?.children?.some(child => child.path === "jobs/meteorites")).toBe(true)
    expect(navShell?.children?.some(child => child.path === "candidate/board_searches")).toBe(false)
    expect(navShell?.children?.some(child => child.path === "candidate/title_patterns")).toBe(false)
    expect(navShell?.children?.some(child => child.path === "admin/data_management")).toBe(true)
  })

  it("exports route elements compatible with useRoutes", () => {
    expect(typeof useRoutes).toBe("function")
    expect(routes[1].element).toBeTruthy()
  })
})
