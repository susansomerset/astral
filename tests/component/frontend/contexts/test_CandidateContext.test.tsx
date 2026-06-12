import { act, renderHook, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { setFmtTimezone } from "../../../../src/ui/frontend/src/lib/fmt"
import {
  CandidateProvider,
  useCandidate,
} from "../../../../src/ui/frontend/src/contexts/CandidateContext"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

function useCandidateState() {
  return useCandidate()
}

describe("CandidateProvider", () => {
  beforeEach(() => {
    localStorage.clear()
    setFmtTimezone("UTC")
    mockedApi.mockReset()
  })

  it("loads candidates, keeps a valid selection, and syncs timezone", async () => {
    mockedApi.mockResolvedValue({
      json: async () => [
        {
          astral_candidate_id: "c1",
          state: "ACTIVE",
          candidate_data: { profile: { timezone: "America/New_York" } },
        },
        { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
      ],
    } as Response)

    const { result } = renderHook(() => useCandidateState(), {
      wrapper: ({ children }) => <CandidateProvider>{children}</CandidateProvider>,
    })

    await waitFor(() => expect(result.current.candidates).toHaveLength(2))
    expect(result.current.selectedId).toBe("c1")
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c1")

    act(() => {
      result.current.setSelectedId("c2")
    })
    expect(result.current.selectedId).toBe("c2")
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c2")

    mockedApi.mockResolvedValueOnce({
      json: async () => [
        {
          astral_candidate_id: "c2",
          state: "ACTIVE",
          candidate_data: { profile: { timezone: "America/Los_Angeles" } },
        },
      ],
    } as Response)
    act(() => {
      result.current.refresh()
    })
    await waitFor(() => expect(result.current.candidates).toHaveLength(1))
    expect(result.current.selectedId).toBe("c2")
  })

  it("clears candidates when the request fails or payload is not an array", async () => {
    mockedApi.mockRejectedValueOnce(new Error("network"))
    const { result, unmount } = renderHook(() => useCandidateState(), {
      wrapper: ({ children }) => <CandidateProvider>{children}</CandidateProvider>,
    })
    await waitFor(() => expect(result.current.candidates).toEqual([]))
    unmount()

    mockedApi.mockResolvedValueOnce({ json: async () => ({ bad: true }) } as Response)
    const { result: nonArray } = renderHook(() => useCandidateState(), {
      wrapper: ({ children }) => <CandidateProvider>{children}</CandidateProvider>,
    })
    await waitFor(() => expect(nonArray.current.candidates).toEqual([]))
  })

  it("leaves selection unset when the candidate list is empty", async () => {
    mockedApi.mockResolvedValueOnce({ json: async () => [] } as Response)
    const { result } = renderHook(() => useCandidateState(), {
      wrapper: ({ children }) => <CandidateProvider>{children}</CandidateProvider>,
    })
    await waitFor(() => expect(result.current.candidates).toEqual([]))
    expect(result.current.selectedId).toBeNull()
  })
})
