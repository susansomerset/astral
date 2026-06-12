import { renderHook, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import {
  StateUiProvider,
  useStateUi,
} from "../../../../src/ui/frontend/src/contexts/StateUiContext"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("StateUiProvider", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("loads the manifest from the API", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => STATE_UI_MANIFEST_FIXTURE,
    } as Response)

    const { result } = renderHook(() => useStateUi(), {
      wrapper: ({ children }) => <StateUiProvider>{children}</StateUiProvider>,
    })

    await waitFor(() => expect(result.current.loadState).toBe("ready"))
    expect(result.current.manifest?.jobs.in_review_sections[0].label).toBe("New")
  })

  it("leaves manifest null when the request fails", async () => {
    mockedApi.mockResolvedValue({ ok: false, json: async () => ({}) } as Response)
    const { result } = renderHook(() => useStateUi(), {
      wrapper: ({ children }) => <StateUiProvider>{children}</StateUiProvider>,
    })

    await waitFor(() => expect(result.current.loadState).toBe("error"))
    expect(result.current.manifest).toBeNull()
  })
})
