import { useRoutes } from "react-router-dom"
import { describe, expect, it } from "vitest"
import routes from "../../../src/ui/frontend/src/routes"

describe("routes", () => {
  it("defines the navigation shell and catch-all redirect", () => {
    expect(routes).toHaveLength(1)
    const shell = routes[0]
    expect(shell.children?.some(child => child.index)).toBe(true)
    expect(shell.children?.some(child => child.path === "*")).toBe(true)
    expect(shell.children?.some(child => child.path === "jobs/recommended")).toBe(true)
    expect(shell.children?.some(child => child.path === "candidate/board_searches")).toBe(true)
    expect(shell.children?.some(child => child.path === "candidate/title_patterns")).toBe(false)
    expect(shell.children?.some(child => child.path === "admin/data_management")).toBe(true)
  })

  it("exports route elements compatible with useRoutes", () => {
    expect(typeof useRoutes).toBe("function")
    expect(routes[0].element).toBeTruthy()
  })
})
