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
import { resetStytchTestState, stytchTestState } from "../stytchMock"
import { stubAuthPublicFetches } from "../test-utils"

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

describe("CandidateProvider — AST-1481 alignSelectedCandidateForJobCompany", () => {
  beforeEach(() => {
    localStorage.clear()
    document.title = "Astral"
    setFmtTimezone("UTC")
    resetStytchTestState()
    stubAuthPublicFetches(true)
    mockedApi.mockReset()
  })

  function alignWrapper(isAdmin: boolean) {
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
            { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} },
            { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
          ],
        } as Response
      }
      if (url === "/api/companies/Globex") {
        return { ok: true, json: async () => ({ candidate_id: "c2" }) } as Response
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

  it("switches admin selection when company maps to another loaded candidate", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    const { result } = renderHook(() => useCandidateState(), { wrapper: alignWrapper(true) })
    await waitFor(() => expect(result.current.candidates).toHaveLength(2))
    await waitFor(() => expect(result.current.selectedId).toBe("c1"))
    await act(async () => {
      await result.current.alignSelectedCandidateForJobCompany("Globex")
    })
    expect(mockedApi.mock.calls.some(([url]) => url === "/api/companies/Globex")).toBe(true)
    await waitFor(() => expect(result.current.selectedId).toBe("c2"))
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c2")
  })

  it("no-ops for non-admin sessions", async () => {
    const { result } = renderHook(() => useCandidateState(), { wrapper: alignWrapper(false) })
    await waitFor(() => expect(result.current.selectedId).toBe("c1"))
    await act(async () => {
      await result.current.alignSelectedCandidateForJobCompany("Globex")
    })
    expect(result.current.selectedId).toBe("c1")
    expect(mockedApi.mock.calls.some(([url]) => url === "/api/companies/Globex")).toBe(false)
  })

  it("soft-fails when company lookup fails", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "u1", name: "User", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/companies/Globex") {
        return { ok: false, status: 404, json: async () => ({}) } as Response
      }
      throw new Error(url)
    })
    const { result } = renderHook(() => useCandidateState(), {
      wrapper: function Wrapper({ children }: { children: ReactNode }) {
        return (
          <AuthProvider>
            <CandidateProvider>{children}</CandidateProvider>
          </AuthProvider>
        )
      },
    })
    await waitFor(() => expect(result.current.selectedId).toBe("c1"))
    await act(async () => {
      await result.current.alignSelectedCandidateForJobCompany("Globex")
    })
    expect(result.current.selectedId).toBe("c1")
  })
})


describe("CandidateProvider — AST-1768 login-email candidate bind", () => {
  beforeEach(() => {
    localStorage.clear()
    document.title = "Astral"
    setFmtTimezone("UTC")
    resetStytchTestState()
    stubAuthPublicFetches(false)
    mockedApi.mockReset()
  })

  // Susan Somerset (c1) is stored/first; Jolane Abrams (c2) owns the login email.
  function bindWrapper(isAdmin: boolean, byEmail: (url: string) => Response) {
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
            { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {}, full: "Susan Somerset" },
            { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {}, full: "Jolane Abrams" },
          ],
        } as Response
      }
      if (url.startsWith("/api/candidates/by_email")) return byEmail(url)
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

  const byEmailCalls = () =>
    mockedApi.mock.calls.map(([url]) => String(url)).filter(u => u.startsWith("/api/candidates/by_email"))

  it("[bug-repro] non-admin: selects the candidate whose profile email matches the login", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    stytchTestState.session = { user_id: "u1" }
    stytchTestState.user = { emails: [{ email: "SooSomerset@gmail.com", verified: true }] }
    const wrapper = bindWrapper(false, () =>
      ({ ok: true, json: async () => ({ candidate_id: "c2" }) }) as Response,
    )
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.candidatesHydrated).toBe(true))
    expect(byEmailCalls()).toEqual([
      `/api/candidates/by_email?email=${encodeURIComponent("soosomerset@gmail.com")}`,
    ])
    expect(result.current.selectedId).toBe("c2")
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c2")
  })

  it("[bug-repro] uses the first verified email, not emails[0]", async () => {
    stytchTestState.session = { user_id: "u1" }
    stytchTestState.user = {
      emails: [
        { email: "unverified@example.com", verified: false },
        { email: "Verified@Example.com", verified: true },
      ],
    }
    const wrapper = bindWrapper(true, () =>
      ({ ok: true, json: async () => ({ candidate_id: "c2" }) }) as Response,
    )
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.selectedId).toBe("c2"))
    expect(byEmailCalls()).toEqual([
      `/api/candidates/by_email?email=${encodeURIComponent("verified@example.com")}`,
    ])
  })

  it("[bug-repro] binds once per login email — refresh and admin picker are not overridden", async () => {
    stytchTestState.session = { user_id: "u1" }
    stytchTestState.user = { emails: [{ email: "soosomerset@gmail.com", verified: true }] }
    const wrapper = bindWrapper(true, () =>
      ({ ok: true, json: async () => ({ candidate_id: "c2" }) }) as Response,
    )
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.selectedId).toBe("c2"))
    act(() => {
      result.current.setSelectedId("c1")
    })
    act(() => {
      result.current.refresh()
    })
    await waitFor(() => expect(result.current.candidatesHydrated).toBe(true))
    expect(result.current.selectedId).toBe("c1")
    expect(byEmailCalls()).toHaveLength(1)
  })

  it("keeps stored/first selection when lookup returns null or fails", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    stytchTestState.session = { user_id: "u1" }
    stytchTestState.user = { emails: [{ email: "shared@example.com", verified: true }] }
    const nullWrapper = bindWrapper(false, () =>
      ({ ok: true, json: async () => ({ candidate_id: null }) }) as Response,
    )
    const { result, unmount } = renderHook(() => useCandidateState(), { wrapper: nullWrapper })
    await waitFor(() => expect(result.current.candidatesHydrated).toBe(true))
    expect(result.current.selectedId).toBe("c1")
    unmount()

    const failWrapper = bindWrapper(false, () =>
      ({ ok: false, status: 500, json: async () => ({}) }) as Response,
    )
    const { result: failed } = renderHook(() => useCandidateState(), { wrapper: failWrapper })
    await waitFor(() => expect(failed.current.candidatesHydrated).toBe(true))
    expect(failed.current.selectedId).toBe("c1")
  })

  it("ignores a lookup id that is not in the loaded candidate list", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    stytchTestState.session = { user_id: "u1" }
    stytchTestState.user = { emails: [{ email: "ghost@example.com", verified: true }] }
    const wrapper = bindWrapper(false, () =>
      ({ ok: true, json: async () => ({ candidate_id: "c-deleted" }) }) as Response,
    )
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.candidatesHydrated).toBe(true))
    expect(result.current.selectedId).toBe("c1")
  })

  it("no Stytch user (local passthrough) → no lookup call", async () => {
    stubAuthPublicFetches(true)
    const wrapper = bindWrapper(false, () => {
      throw new Error("by_email must not be called")
    })
    const { result } = renderHook(() => useCandidateState(), { wrapper })
    await waitFor(() => expect(result.current.candidatesHydrated).toBe(true))
    expect(result.current.selectedId).toBe("c1")
    expect(byEmailCalls()).toHaveLength(0)
  })
})

describe("CandidateProvider — AST-2048 data-theme follows the selected candidate", () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute("data-theme")
    resetStytchTestState()
    mockedApi.mockReset()
  })

  // c1 stored Light, c2 has no theme → c2 falls back to :root Dark (no attribute).
  const rows = [
    { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { theme: "light" } },
    { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
  ]
  const root = () => document.documentElement.getAttribute("data-theme")

  it("sets the stored theme, flips on picker switch without reload, and clears on unmount (AC5/AC6)", async () => {
    const { result, unmount } = renderHook(() => useCandidateState(), { wrapper: titleProviders(rows) })
    await waitFor(() => expect(result.current.selectedId).toBe("c1"))
    await waitFor(() => expect(root()).toBe("light"))

    act(() => result.current.setSelectedId("c2"))
    expect(root()).toBeNull()

    act(() => result.current.setSelectedId("c1"))
    expect(root()).toBe("light")

    unmount()
    expect(root()).toBeNull()
  })

  it("no candidates loaded → no theme attribute", async () => {
    const { result } = renderHook(() => useCandidateState(), { wrapper: titleProviders([]) })
    await waitFor(() => expect(result.current.candidatesHydrated).toBe(true))
    expect(root()).toBeNull()
  })
})
