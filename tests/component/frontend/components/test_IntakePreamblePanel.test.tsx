import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import IntakePreamblePanel, {
  type PreambleMaterials,
} from "../../../../src/ui/frontend/src/components/IntakePreamblePanel"
import api from "../../../../src/ui/frontend/src/lib/api"
import { renderWithProviders } from "../test-utils"
import { AST1017_PREAMBLE_CONFIG } from "../fixtures/ast1017PreambleConfig"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const emptyMaterials: PreambleMaterials = {
  starting_resume_text: "",
  sample_cover_text: "",
  linkedin_profile_text: "",
}

function jsonResponse<T>(body: T, init: Partial<Response> = {}): Response {
  return { json: async () => body, ok: init.ok ?? true, status: init.status ?? 200, ...init } as Response
}

type PanelMockState = {
  materials?: PreambleMaterials
  validateOutcome?: "Valid" | "Try Again" | "Escalate" | "Nope"
  validateSuccess?: boolean
  putFail?: boolean
}

function installPanelMocks(state: PanelMockState = {}) {
  const validateBodies: Record<string, unknown>[] = []
  const putBodies: Record<string, unknown>[] = []
  const outcome = state.validateOutcome ?? "Valid"
  const success = state.validateSuccess ?? true

  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/ui_config" && !init) {
      return jsonResponse({ preamble: AST1017_PREAMBLE_CONFIG, column_types: {} })
    }
    if (url === "/api/candidates/c1/preamble/validate" && init?.method === "POST") {
      const body = JSON.parse(String(init.body)) as Record<string, unknown>
      validateBodies.push(body)
      return jsonResponse({
        success,
        outcome: success ? outcome : null,
        error: success ? null : "validation failed",
        batch_id: "preamble-preamble_validate_response-x",
      })
    }
    if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
      const body = JSON.parse(String(init.body)) as Record<string, unknown>
      putBodies.push(body)
      if (state.putFail) {
        return jsonResponse({ error: "put failed" }, { ok: false, status: 500 })
      }
      return jsonResponse({ ok: true })
    }
    throw new Error(`unexpected api call: ${url}${init?.method ? ` ${init.method}` : ""}`)
  })

  return { validateBodies, putBodies }
}

describe("IntakePreamblePanel (AST-1017)", () => {
  const onComplete = vi.fn()
  const onCancel = vi.fn()

  beforeEach(() => {
    mockedApi.mockReset()
    onComplete.mockReset()
    onCancel.mockReset()
  })

  it("shows Intro and first pending step prompt from ui_config", async () => {
    installPanelMocks()
    renderWithProviders(
      <IntakePreamblePanel
        candidateId="c1"
        initialMaterials={emptyMaterials}
        onComplete={onComplete}
        onCancel={onCancel}
      />,
    )
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.intro)).toBeInTheDocument(),
    )
    expect(screen.getByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled()
  })

  it("skips filled targets and Continue completes when no pending steps", async () => {
    const full: PreambleMaterials = {
      starting_resume_text: "resume",
      linkedin_profile_text: "linkedin",
      sample_cover_text: "cover",
    }
    installPanelMocks({ materials: full })
    renderWithProviders(
      <IntakePreamblePanel
        candidateId="c1"
        initialMaterials={full}
        onComplete={onComplete}
        onCancel={onCancel}
      />,
    )
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.intro)).toBeInTheDocument(),
    )
    expect(screen.queryByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Continue" }))
    expect(onComplete).toHaveBeenCalledWith(full)
  })

  it("Valid → PUT context field then advances; Try Again does not PUT", async () => {
    const { validateBodies, putBodies } = installPanelMocks()
    renderWithProviders(
      <IntakePreamblePanel
        candidateId="c1"
        initialMaterials={emptyMaterials}
        onComplete={onComplete}
        onCancel={onCancel}
      />,
    )
    await screen.findByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)
    await userEvent.type(screen.getByPlaceholderText(/Paste your answer/i), "My resume text")
    await userEvent.click(screen.getByRole("button", { name: "Submit" }))
    await waitFor(() => expect(putBodies).toHaveLength(1))
    expect(validateBodies[0]).toMatchObject({
      question: AST1017_PREAMBLE_CONFIG.steps[0].validation_question,
      answer: "My resume text",
      step_index: 1,
      step_total: 3,
    })
    expect(putBodies[0]).toEqual({ context: { raw_resume: "My resume text" } })
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.steps[1].prompt_1st_try)).toBeInTheDocument(),
    )
  })

  it("Try Again swaps to 2nd-try prompt without PUT", async () => {
    const { putBodies } = installPanelMocks({ validateOutcome: "Try Again" })
    renderWithProviders(
      <IntakePreamblePanel
        candidateId="c1"
        initialMaterials={emptyMaterials}
        onComplete={onComplete}
        onCancel={onCancel}
      />,
    )
    await screen.findByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)
    await userEvent.type(screen.getByPlaceholderText(/Paste your answer/i), "nope")
    await userEvent.click(screen.getByRole("button", { name: "Submit" }))
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_2nd_try)).toBeInTheDocument(),
    )
    expect(putBodies).toHaveLength(0)
    expect(onComplete).not.toHaveBeenCalled()
  })

  it("Escalate toasts and does not PUT or advance", async () => {
    const { putBodies } = installPanelMocks({ validateOutcome: "Escalate" })
    renderWithProviders(
      <IntakePreamblePanel
        candidateId="c1"
        initialMaterials={emptyMaterials}
        onComplete={onComplete}
        onCancel={onCancel}
      />,
    )
    await screen.findByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)
    await userEvent.type(screen.getByPlaceholderText(/Paste your answer/i), "ambiguous")
    await userEvent.click(screen.getByRole("button", { name: "Submit" }))
    await waitFor(() =>
      expect(screen.getByText(/needs human review/i)).toBeInTheDocument(),
    )
    expect(putBodies).toHaveLength(0)
    expect(screen.getByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)).toBeInTheDocument()
  })
})
