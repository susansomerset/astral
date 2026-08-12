import { act, renderHook, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { setFmtTimezone } from "../../../../src/ui/frontend/src/lib/fmt"
import { AuthProvider } from "../../../../src/ui/frontend/src/contexts/AuthContext"
import {
  CandidateProvider,
  useCandidate,
} from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

function useCandidateState() {
  return useCandidate()
}

function providers(isAdmin: boolean) {
  mockedApi.mockImplementation(async (url: string) => {
    if (url === "/api/me") {
      return {
        ok: true,
        json: async () => ({ user_id: "u1", name: "User", is_admin: isAdmin }),
      } as Response
    }
    if (url === "/api/candidates") {
      return {
        json: async () => [
          {
            astral_candidate_id: "c1",
            state: "ACTIVE",
            candidate_data: { profile: { timezone: "America/New_York" } },
          },
          { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
        ],
      } as Response
    }
    throw new Error(url)
  })

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <AuthProvider>
        <CandidateProvider>{children}</CandidateProvider>
      </AuthProvider>
    )
  }
}

describe("CandidateProvider", () => {
  beforeEach(() => {
    localStorage.clear()
    document.title = "Astral"
    setFmtTimezone("UTC")
    resetStytchTestState()
    mockedApi.mockReset()
  })

  it("loads candidates, keeps a valid selection, and syncs timezone", async () => {
    const wrapper = providers(true)
    const { result } = renderHook(() => useCandidateState(), { wrapper })

    await waitFor(() => expect(result.current.candidates).toHaveLength(2))
    expect(result.current.selectedId).toBe("c1")
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c1")

    act(() => {
      result.current.setSelectedId("c2")
    })
    expect(result.current.selectedId).toBe("c2")
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c2")

    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "u1", name: "User", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") {
        return {
          json: async () => [
            {
              astral_candidate_id: "c2",
              state: "ACTIVE",
              candidate_data: { profile: { timezone: "America/Los_Angeles" } },
            },
          ],
        } as Response
      }
      throw new Error(url)
    })
    act(() => {
      result.current.refresh()
    })
    await waitFor(() => expect(result.current.candidates).toHaveLength(1))
    expect(result.current.selectedId).toBe("c2")
  })

  it("does not change selection when setSelectedId is called by a non-admin", async () => {
    const wrapper = providers(false)
    const { result } = renderHook(() => useCandidateState(), { wrapper })

    await waitFor(() => expect(result.current.candidates).toHaveLength(2))
    expect(result.current.selectedId).toBe("c1")

    act(() => {
      result.current.setSelectedId("c2")
    })
    expect(result.current.selectedId).toBe("c1")
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c1")
  })

  it("clears candidates when the request fails or payload is not an array", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "u1", name: "User", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") throw new Error("network")
      throw new Error(url)
    })
    const { result, unmount } = renderHook(() => useCandidateState(), {
      wrapper: providers(true),
    })
    await waitFor(() => expect(result.current.candidates).toEqual([]))
    unmount()

    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "u1", name: "User", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") return { json: async () => ({ bad: true }) } as Response
      throw new Error(url)
    })
    const { result: nonArray } = renderHook(() => useCandidateState(), {
      wrapper: providers(true),
    })
    await waitFor(() => expect(nonArray.current.candidates).toEqual([]))
  })

  it("leaves selection unset when the candidate list is empty", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "u1", name: "User", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") return { json: async () => [] } as Response
      throw new Error(url)
    })
    function Wrapper({ children }: { children: ReactNode }) {
      return (
        <AuthProvider>
          <CandidateProvider>{children}</CandidateProvider>
        </AuthProvider>
      )
    }
    const { result } = renderHook(() => useCandidateState(), { wrapper: Wrapper })
    await waitFor(() => expect(result.current.candidates).toEqual([]))
    expect(result.current.selectedId).toBeNull()
  })
})

function titleProviders(rows: Array<Record<string, unknown>>) {
  mockedApi.mockImplementation(async (url: string) => {
    if (url === "/api/me") {
      return {
        ok: true,
        json: async () => ({ user_id: "u1", name: "User", is_admin: true }),
      } as Response
    }
    if (url === "/api/candidates") {
      return { json: async () => rows } as Response
    }
    throw new Error(url)
  })
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <AuthProvider>
        <CandidateProvider>{children}</CandidateProvider>
      </AuthProvider>
    )
  }
}

describe("CandidateProvider — AST-1311 browser tab title", () => {
  beforeEach(() => {
    localStorage.clear()
    document.title = "Astral"
    setFmtTimezone("UTC")
    resetStytchTestState()
    mockedApi.mockReset()
  })

  it("sets Astral - Full Name from the selected row's full column", async () => {
    const wrapper = titleProviders([
      {
        astral_candidate_id: "c1",
        state: "ACTIVE",
        candidate_data: {},
        first: "Wrong",
        last: "Join",
        full: "Jolane Abrams",
      },
    ])
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.selectedId).toBe("c1"))
    expect(document.title).toBe("Astral - Jolane Abrams")
  })

  it("updates the title when the selected candidate changes", async () => {
    const wrapper = titleProviders([
      { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {}, full: "Jolane Abrams" },
      { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {}, full: "Ada Lovelace" },
    ])
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.candidates).toHaveLength(2))
    expect(document.title).toBe("Astral - Jolane Abrams")
    act(() => {
      result.current.setSelectedId("c2")
    })
    expect(document.title).toBe("Astral - Ada Lovelace")
  })

  it("restores the persisted selection's Full Name after load", async () => {
    localStorage.setItem("astral_selected_candidate", "c2")
    const wrapper = titleProviders([
      { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {}, full: "Jolane Abrams" },
      { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {}, full: "Ada Lovelace" },
    ])
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.selectedId).toBe("c2"))
    expect(document.title).toBe("Astral - Ada Lovelace")
  })

  it("falls back to Astral when full is missing, blank, or only first+last exist", async () => {
    const wrapper = titleProviders([
      { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {}, first: "Jolane", last: "Abrams" },
    ])
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.selectedId).toBe("c1"))
    expect(document.title).toBe("Astral")
  })

  it("resets to Astral when CandidateProvider unmounts", async () => {
    const wrapper = titleProviders([
      { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {}, full: "Jolane Abrams" },
    ])
    const { result, unmount } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(document.title).toBe("Astral - Jolane Abrams"))
    expect(result.current.selectedId).toBe("c1")
    unmount()
    expect(document.title).toBe("Astral")
  })
})

