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
    expect(navShell?.children?.some(child => child.path === "jobs/recommended")).toBe(true)
    expect(navShell?.children?.some(child => child.path === "candidate/board_searches")).toBe(false)
    expect(navShell?.children?.some(child => child.path === "candidate/title_patterns")).toBe(false)
    expect(navShell?.children?.some(child => child.path === "admin/data_management")).toBe(true)
  })

  it("exports route elements compatible with useRoutes", () => {
    expect(typeof useRoutes).toBe("function")
    expect(routes[1].element).toBeTruthy()
  })
})
