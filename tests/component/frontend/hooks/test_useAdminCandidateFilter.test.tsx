import { renderHook, act, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { AuthProvider } from "../../../../src/ui/frontend/src/contexts/AuthContext"
import { CandidateProvider } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import {
  navDefaultCandidateFilter,
  useAdminCandidateFilter,
} from "../../../../src/ui/frontend/src/hooks/useAdminCandidateFilter"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const twoCandidates = [
  { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { first: "Ada", last: "One" } },
  { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: { first: "Betty", last: "Two" } },
]

function wrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <CandidateProvider>{children}</CandidateProvider>
    </AuthProvider>
  )
}

describe("useAdminCandidateFilter", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return { ok: true, json: async () => ({ user_id: "u1", name: "Test", is_admin: true }) } as Response
      }
      if (url === "/api/candidates") return { json: async () => twoCandidates } as Response
      throw new Error(`unexpected ${url}`)
    })
  })

  it("navDefaultCandidateFilter maps null to All", () => {
    expect(navDefaultCandidateFilter(null)).toBe("")
    expect(navDefaultCandidateFilter("c1")).toBe("c1")
  })

  it("defaults local filter from nav selection", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    const { result } = renderHook(() => useAdminCandidateFilter(), { wrapper })
    await waitFor(() => expect(result.current.candidateFilter).toBe("c1"))
    expect(result.current.syncWithNav).toBe(true)
    await waitFor(() =>
      expect(result.current.candidates.map(c => c.astral_candidate_id)).toEqual(["c1", "c2"]),
    )
  })

  it("manual change pins filter and blocks nav sync", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    const { result } = renderHook(() => useAdminCandidateFilter(), { wrapper })
    await waitFor(() => expect(result.current.candidateFilter).toBe("c1"))

    act(() => result.current.setCandidateFilter(""))
    expect(result.current.candidateFilter).toBe("")
    expect(result.current.syncWithNav).toBe(false)
  })

  it("urlBacked honors explicit bookmark via urlPresentDisablesSync", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    let urlValue = "c2"
    const setValue = vi.fn((next: string) => {
      urlValue = next
    })
    const { result, rerender } = renderHook(
      () =>
        useAdminCandidateFilter({
          urlBacked: { value: urlValue, setValue },
          urlPresentDisablesSync: true,
        }),
      { wrapper },
    )
    await waitFor(() => expect(result.current.candidateFilter).toBe("c2"))
    expect(result.current.syncWithNav).toBe(false)

    act(() => result.current.setCandidateFilter(""))
    expect(setValue).toHaveBeenCalledWith("")
    rerender()
    expect(result.current.candidateFilter).toBe("")
  })

  it("direct urlBacked switch from c1 to c2 does not revert to nav default", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    let urlValue = "c1"
    const setValue = vi.fn((next: string) => {
      urlValue = next
    })
    const { result, rerender } = renderHook(
      () =>
        useAdminCandidateFilter({
          urlBacked: { value: urlValue, setValue },
          urlPresentDisablesSync: true,
        }),
      { wrapper },
    )
    await waitFor(() => expect(result.current.candidateFilter).toBe("c1"))

    act(() => result.current.setCandidateFilter("c2"))
    expect(setValue).toHaveBeenCalledWith("c2")
    rerender()
    expect(result.current.candidateFilter).toBe("c2")
    expect(result.current.syncWithNav).toBe(false)

    rerender()
    expect(result.current.candidateFilter).toBe("c2")
  })
})
