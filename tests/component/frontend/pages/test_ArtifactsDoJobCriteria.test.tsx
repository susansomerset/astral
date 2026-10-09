import { act, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsDoJobCriteria from "../../../../src/ui/frontend/src/pages/ArtifactsDoJobCriteria"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("ArtifactsDoJobCriteria", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      if (url === "/api/ui_config") return { ok: true, json: async () => ({ column_types: {} }) } as Response
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                do_rubric: [{ label: "Impact", content: "Ship features", importance: 4 }],
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("renders do job criteria editor", async () => {
    renderWithProviders(<ArtifactsDoJobCriteria />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Do Job Criteria" })).toBeInTheDocument())
  })

  it("AST-2068 AC4/AC2: one criterion steps back alone; an unchanged blur saves nothing", async () => {
    // Fake server: V01 has two versions (u-b current), V02 one. Only V01's current moves.
    const v01: Record<string, string> = { "u-a": "Ship v1", "u-b": "Ship v2" }
    let cur01 = "u-b"
    const map01 = () => ({
      "u-a": { created_at: "t", current: cur01 === "u-a" ? 1 : 0, position: 1 },
      "u-b": { created_at: "t", current: cur01 === "u-b" ? 1 : 0, position: 2 },
    })
    const rub = "/api/candidates/c1/rubric/do_rubric"
    const puts: string[] = []
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      if (url === "/api/ui_config") return { ok: true, json: async () => ({ column_types: {} }) } as Response
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                do_rubric: [
                  { code: "V01", label: "Impact", content: v01[cur01], importance: 4 },
                  { code: "V02", label: "Craft", content: "Keep", importance: 3 },
                ],
              },
            },
          }),
        } as Response
      }
      if (url === `${rub}/V01/versions`) return { ok: true, json: async () => ({ versions: map01() }) } as Response
      if (url === `${rub}/V02/versions`) {
        return { ok: true, json: async () => ({ versions: { "u-c": { created_at: "t", current: 1, position: 1 } } }) } as Response
      }
      if (url === `${rub}/V01/current` && init?.method === "PUT") {
        cur01 = JSON.parse(String(init.body)).rubric_vector_uuid
        return { ok: true, json: async () => ({ current: cur01, versions: map01() }) } as Response
      }
      if (url.startsWith("/api/candidates/c1/") && init?.method === "PUT") {
        puts.push(url)
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(`unexpected api call: ${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(<ArtifactsDoJobCriteria />)
    await waitFor(() => expect(screen.getAllByRole("button", { name: "Previous version" })).toHaveLength(2))
    expect(screen.getByText("2 of 2")).toBeInTheDocument()
    expect(screen.getByText("1 of 1")).toBeInTheDocument()
    // AC2: focus + blur on an unchanged body → no PUT.
    const body = screen.getByDisplayValue("Ship v2")
    await userEvent.click(body)
    await act(async () => { body.blur() })
    expect(puts).toHaveLength(0)
    // AC4: V01 back → previous body, "1 of 2", back disabled; V02 untouched.
    const [backV01] = screen.getAllByRole("button", { name: "Previous version" })
    await userEvent.click(backV01)
    await screen.findByDisplayValue("Ship v1")
    expect(screen.getByText("1 of 2")).toBeInTheDocument()
    expect(screen.getAllByRole("button", { name: "Previous version" })[0]).toBeDisabled()
    expect(screen.getByDisplayValue("Keep")).toBeInTheDocument()
    expect(cur01).toBe("u-a")
    expect(puts).toHaveLength(0)
  })
})
