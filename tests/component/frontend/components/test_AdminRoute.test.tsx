import { render, screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"
import AdminRoute from "../../../../src/ui/frontend/src/components/AdminRoute"
import { useAuth } from "../../../../src/ui/frontend/src/contexts/AuthContext"

vi.mock("../../../../src/ui/frontend/src/contexts/AuthContext", () => ({
  useAuth: vi.fn(),
}))

const mockedUseAuth = vi.mocked(useAuth)

describe("AdminRoute", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset()
  })

  it("redirects non-admin users away from admin routes", () => {
    mockedUseAuth.mockReturnValue({
      user: { user_id: "u1", name: "User", is_admin: false },
      isAdmin: false,
      loading: false,
      refreshMe: () => {},
    })

    render(
      <MemoryRouter initialEntries={["/admin/secret"]}>
        <Routes>
          <Route path="/admin/secret" element={<AdminRoute><p>Admin panel</p></AdminRoute>} />
          <Route path="/jobs/recommended" element={<p>Jobs recommended</p>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText("Jobs recommended")).toBeInTheDocument()
    expect(screen.queryByText("Admin panel")).not.toBeInTheDocument()
  })

  it("renders admin content for admin users", () => {
    mockedUseAuth.mockReturnValue({
      user: { user_id: "admin-1", name: "Admin", is_admin: true },
      isAdmin: true,
      loading: false,
      refreshMe: () => {},
    })

    render(
      <MemoryRouter initialEntries={["/admin/secret"]}>
        <Routes>
          <Route path="/admin/secret" element={<AdminRoute><p>Admin panel</p></AdminRoute>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText("Admin panel")).toBeInTheDocument()
  })

  it("shows loading while auth is resolving", () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      isAdmin: false,
      loading: true,
      refreshMe: () => {},
    })

    render(
      <MemoryRouter initialEntries={["/admin/secret"]}>
        <Routes>
          <Route path="/admin/secret" element={<AdminRoute><p>Admin panel</p></AdminRoute>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText("Loading…")).toBeInTheDocument()
  })
})
