import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import IntakeTopicMenuPanel from "../../../../src/ui/frontend/src/components/IntakeTopicMenuPanel"
import api from "../../../../src/ui/frontend/src/lib/api"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const TOPIC_MENU_UI = {
  panel_title: "Confirm preamble with Estelle",
  accept_label: "Looks good — generate Topic Menu",
  send_label: "Send to Estelle",
  placeholder: "Tell Estelle what to change, or accept below.",
  generating_label: "Estelle is building your Topic Menu…",
  done_title: "Topic Menu ready",
}

function jsonResponse<T>(body: T, init: Partial<Response> = {}): Response {
  return { json: async () => body, ok: init.ok ?? true, status: init.status ?? 200, ...init } as Response
}

type PanelMockState = {
  firstOutcome?: "continue" | "accepted"
  acceptOutcome?: "continue" | "accepted"
  generateFail?: boolean
}

function installPanelMocks(state: PanelMockState = {}) {
  const confirmBodies: Record<string, unknown>[] = []
  let confirmCalls = 0
  const firstOutcome = state.firstOutcome ?? "continue"
  const acceptOutcome = state.acceptOutcome ?? "accepted"

  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/ui_config" && !init) {
      return jsonResponse({ topic_menu_gen: { ui: TOPIC_MENU_UI }, column_types: {} })
    }
    if (url === "/api/candidates/c1/topic-menu/confirm" && init?.method === "POST") {
      confirmCalls += 1
      const body = JSON.parse(String(init.body || "{}")) as Record<string, unknown>
      confirmBodies.push(body)
      const outcome = confirmCalls === 1 ? firstOutcome : acceptOutcome
      return jsonResponse({
        success: true,
        outcome,
        assistant_message:
          outcome === "continue"
            ? "Anything here you would change?"
            : "Great — generating next.",
        applied_patches: [],
        packet: {},
        batch_id: "intake-topic_menu_preamble_confirm-x",
        error: null,
      })
    }
    if (url === "/api/candidates/c1/topic-menu/generate" && init?.method === "POST") {
      if (state.generateFail) {
        return jsonResponse({ error: "generate failed" }, { ok: false, status: 500 })
      }
      return jsonResponse({
        success: true,
        menu: {
          topics: [
            {
              id: "t1",
              name: "Strengths",
              ask: "What is a recent win?",
              required: true,
              informs: ["strengths", "backstory"],
              status: "open",
            },
          ],
        },
        rejected_topic_count: 0,
        informs_covered: ["strengths", "backstory"],
        batch_id: "intake-topic_menu_generate-x",
        error: null,
      })
    }
    throw new Error(`unexpected api call: ${url}${init?.method ? ` ${init.method}` : ""}`)
  })

  return { confirmBodies, getConfirmCalls: () => confirmCalls }
}

describe("IntakeTopicMenuPanel (AST-1075)", () => {
  const onDone = vi.fn()
  const onCancel = vi.fn()

  beforeEach(() => {
    mockedApi.mockReset()
    onDone.mockReset()
    onCancel.mockReset()
  })

  it("loads ui_config labels and opens with Estelle confirm ask", async () => {
    installPanelMocks()
    renderWithProviders(
      <IntakeTopicMenuPanel candidateId="c1" onDone={onDone} onCancel={onCancel} />,
    )
    await waitFor(() =>
      expect(screen.getByText(TOPIC_MENU_UI.panel_title)).toBeInTheDocument(),
    )
    expect(screen.getByText("Anything here you would change?")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: TOPIC_MENU_UI.accept_label })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: TOPIC_MENU_UI.send_label })).toBeInTheDocument()
  })

  it("Accept → confirm accepted → generate → Done shows menu summary", async () => {
    const { getConfirmCalls } = installPanelMocks()
    renderWithProviders(
      <IntakeTopicMenuPanel candidateId="c1" onDone={onDone} onCancel={onCancel} />,
    )
    await screen.findByText("Anything here you would change?")
    await userEvent.click(screen.getByRole("button", { name: TOPIC_MENU_UI.accept_label }))
    await waitFor(() => expect(screen.getByText(TOPIC_MENU_UI.done_title)).toBeInTheDocument())
    expect(screen.getByText(/Strengths/)).toBeInTheDocument()
    expect(screen.getByText(/informs: strengths, backstory/)).toBeInTheDocument()
    expect(getConfirmCalls()).toBe(2)
    await userEvent.click(screen.getByRole("button", { name: "Done" }))
    expect(onDone).toHaveBeenCalled()
  })

  it("Send posts candidate message without generating until accepted", async () => {
    const { confirmBodies } = installPanelMocks({ acceptOutcome: "continue" })
    renderWithProviders(
      <IntakeTopicMenuPanel candidateId="c1" onDone={onDone} onCancel={onCancel} />,
    )
    await screen.findByText("Anything here you would change?")
    await userEvent.type(screen.getByPlaceholderText(TOPIC_MENU_UI.placeholder), "Fix my strengths")
    await userEvent.click(screen.getByRole("button", { name: TOPIC_MENU_UI.send_label }))
    await waitFor(() => expect(confirmBodies.length).toBe(2))
    expect(confirmBodies[1]).toEqual({ message: "Fix my strengths" })
    expect(screen.queryByText(TOPIC_MENU_UI.done_title)).not.toBeInTheDocument()
  })
})
