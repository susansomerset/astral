import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import IntakeChatModal, {
  type IntakeSessionDto,
  type IntakeSourceMaterials,
  type IntakeTranscriptEntry,
} from "../../../../src/ui/frontend/src/components/IntakeChatModal"
import CandidateIntake from "../../../../src/ui/frontend/src/pages/CandidateIntake"
import { renderWithProviders } from "../test-utils"
import { candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const defaultMaterials: IntakeSourceMaterials = {
  starting_resume_text: "Senior engineer resume body",
  sample_cover_text: "cover optional",
  linkedin_profile_text: "",
}

const HOLD_COPY = "One moment while we review your details before we begin…"
const INITIATE_USER_TEXT =
  "RESUME:\nSenior engineer resume body\n\nCOVER LETTER SAMPLE: cover optional\n\nLINKEDIN: (none)"

function sessionDto(overrides: Partial<IntakeSessionDto> = {}): IntakeSessionDto {
  const ready = overrides.ready_to_build ?? false
  const built = overrides.build_completed ?? false
  return {
    session_id: overrides.session_id ?? "sess-1",
    status: overrides.status ?? (built ? "built" : "active"),
    transcript: overrides.transcript ?? [],
    ready_to_build: ready,
    can_build: overrides.can_build ?? (ready && !built),
    build_completed: built,
    awaiting_agent: overrides.awaiting_agent ?? false,
  }
}

function transcriptEntry(
  role: "user" | "assistant",
  text: string,
  mode?: IntakeTranscriptEntry["mode"],
): IntakeTranscriptEntry {
  return { role, text, mode }
}

type IntakeMockState = {
  materials?: IntakeSourceMaterials
  activeSession?: IntakeSessionDto | null
  sessionCreateBodies?: Record<string, unknown>[]
  turnBodies?: Record<string, unknown>[]
  buildCalls?: string[]
  archiveCalls?: number
  /** Archive POST returns 500 — active session unchanged. */
  archiveFail?: boolean
  /** Archive POST returns 404 — treated as success; clears active. */
  archiveNotFound?: boolean
  /** Delay session POST resolve (hold copy regression). */
  delaySessionCreateMs?: number
  /** GET active returns awaiting until Nth call, then assistant (poll regression). */
  pollUntilAssistantAfterGets?: number
  /** Do not auto-resolve awaiting_agent on GET active (hold regressions). */
  stickyAwaiting?: boolean
  /** Capture last session POST RequestInit (unmount regression). */
  sessionCreateInits?: RequestInit[]
}

function installIntakeMocks(state: IntakeMockState = {}) {
  const materials = state.materials ?? defaultMaterials
  let active = state.activeSession === undefined ? null : state.activeSession
  const sessionCreateBodies = state.sessionCreateBodies ?? []
  const turnBodies = state.turnBodies ?? []
  const buildCalls = state.buildCalls ?? []
  let archiveCalls = state.archiveCalls ?? 0
  let activeGetCalls = 0
  const sessionCreateInits = state.sessionCreateInits ?? []
  const pollAfter = state.pollUntilAssistantAfterGets
  const stickyAwaiting = state.stickyAwaiting ?? false

  const resolveAwaitingAssistant = () => {
    if (!active?.awaiting_agent || stickyAwaiting) return
    active = sessionDto({
      session_id: active.session_id,
      transcript: [transcriptEntry("assistant", "Estelle welcomes you.", "initiate_candidate")],
      awaiting_agent: false,
    })
  }

  installBaseApiMocks(mockedApi, (url, init) => {
    if (url === `/api/candidates/${candidateId}` && !init) {
      return jsonResponse({ candidate_data: { context: materials } })
    }
    if (url === `/api/candidates/${candidateId}/intake/sessions/active` && !init) {
      if (pollAfter != null) {
        activeGetCalls += 1
        if (activeGetCalls < pollAfter) {
          return jsonResponse(
            sessionDto({ transcript: [], awaiting_agent: true }),
          )
        }
        active = sessionDto({
          transcript: [transcriptEntry("assistant", "Estelle arrived after poll", "initiate_candidate")],
          awaiting_agent: false,
        })
        return jsonResponse(active)
      }
      if (!active) {
        return jsonResponse({ error: "no_active_session" }, { ok: false, status: 404 })
      }
      resolveAwaitingAssistant()
      return jsonResponse(active)
    }
    if (url === `/api/candidates/${candidateId}/intake/sessions` && init?.method === "POST") {
      sessionCreateInits.push(init)
      const body = JSON.parse(String(init.body)) as IntakeSourceMaterials
      sessionCreateBodies.push(body)
      const created = sessionDto({
        transcript: [],
        awaiting_agent: true,
      })
      const delayMs = state.delaySessionCreateMs ?? 0
      const respond = () => {
        active = created
        return jsonResponse(active)
      }
      if (delayMs > 0) {
        return new Promise<Response>(resolve => setTimeout(() => resolve(respond()), delayMs))
      }
      return respond()
    }
    const turnMatch = url.match(
      new RegExp(`^/api/candidates/${candidateId}/intake/sessions/([^/]+)/turns$`),
    )
    if (turnMatch && init?.method === "POST") {
      const sessionId = turnMatch[1]
      const body = JSON.parse(String(init.body)) as { message?: string }
      turnBodies.push(body)
      active = sessionDto({
        session_id: sessionId,
        transcript: [
          ...(active?.transcript ?? []),
          transcriptEntry("user", body.message ?? "", "candidate_response"),
          transcriptEntry("assistant", "Follow-up question.", "candidate_response"),
        ],
        ready_to_build: true,
        can_build: true,
      })
      return jsonResponse(active)
    }
    const buildMatch = url.match(
      new RegExp(`^/api/candidates/${candidateId}/intake/sessions/([^/]+)/build$`),
    )
    if (buildMatch && init?.method === "POST") {
      buildCalls.push(buildMatch[1])
      active = sessionDto({
        session_id: buildMatch[1],
        transcript: active?.transcript ?? [],
        ready_to_build: true,
        can_build: false,
        build_completed: true,
        status: "built",
      })
      return jsonResponse(active)
    }
    if (
      url === `/api/candidates/${candidateId}/intake/sessions/active/archive` &&
      init?.method === "POST"
    ) {
      archiveCalls += 1
      if (state.archiveFail) {
        return jsonResponse({ error: "server error" }, { ok: false, status: 500 })
      }
      if (state.archiveNotFound) {
        active = null
        return jsonResponse({ error: "no active intake session" }, { ok: false, status: 404 })
      }
      active = null
      return jsonResponse({
        archived_session_id: "sess-archived",
        archived_at: "2026-06-05 12:00:00",
        intakes_old_count: 1,
      })
    }
    throw new Error(`unexpected api call: ${url}${init?.method ? ` ${init.method}` : ""}`)
  })

  return {
    sessionCreateBodies,
    sessionCreateInits,
    turnBodies,
    buildCalls,
    getArchiveCalls: () => archiveCalls,
    getActiveGetCalls: () => activeGetCalls,
    getActive: () => active,
    setActive: (s: IntakeSessionDto | null) => {
      active = s
    },
  }
}

const RESUME_DIALOG_NAME = "Resume Intake"

describe("CandidateIntake page", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("shows empty state when no candidate is selected", async () => {
    installBaseApiMocks(mockedApi, () => undefined)
    renderWithProviders(<CandidateIntake />)
    await waitFor(() =>
      expect(screen.getByText("Select a candidate to open Intake.")).toBeInTheDocument(),
    )
  })

  it("shows Start Intake confirm before modal (§6c routed page)", async () => {
    installIntakeMocks()
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: "Start Intake" })
    expect(dialog).toHaveTextContent(/saved resume and profile materials/i)
    expect(screen.queryByRole("heading", { name: "Candidate Intake" })).not.toBeInTheDocument()
    await userEvent.click(within(dialog).getByRole("button", { name: "Continue" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Intake" })).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Estelle welcomes you.")).toBeInTheDocument())
    expect(screen.queryByLabelText(/Original Resume Text/i)).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Start interview" })).not.toBeInTheDocument()
  })

  it("does not open modal when confirm is cancelled", async () => {
    installIntakeMocks()
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: "Start Intake" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Cancel" }))
    await waitFor(() =>
      expect(screen.queryByRole("heading", { name: "Candidate Intake" })).not.toBeInTheDocument(),
    )
  })

  it("redirects away when resume text is missing on candidate", async () => {
    installIntakeMocks({ materials: { ...defaultMaterials, starting_resume_text: "" } })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    await waitFor(() =>
      expect(screen.getByText("Add Original Resume Text on Profile before starting Intake.")).toBeInTheDocument(),
    )
    expect(screen.queryByRole("alertdialog", { name: "Start Intake" })).not.toBeInTheDocument()
  })

  it("shows resume dialog when active session exists (not Start Intake confirm)", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })
    expect(screen.getByText(/Would you like to continue your intake/i)).toBeInTheDocument()
    expect(screen.queryByRole("alertdialog", { name: "Start Intake" })).not.toBeInTheDocument()
    expect(screen.queryByRole("heading", { name: "Candidate Intake" })).not.toBeInTheDocument()
  })

  it("Continue resumes active session without archive or session create", async () => {
    const { getArchiveCalls, sessionCreateBodies } = installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })
    await userEvent.click(within(dialog).getByRole("button", { name: "Continue" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Intake" })).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Prior thread")).toBeInTheDocument())
    expect(getArchiveCalls()).toBe(0)
    expect(sessionCreateBodies).toHaveLength(0)
  })

  it("Start Over archives then auto-starts fresh session", async () => {
    const { getArchiveCalls, sessionCreateBodies } = installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })
    await userEvent.click(within(dialog).getByRole("button", { name: "Start Over" }))
    await waitFor(() => expect(getArchiveCalls()).toBe(1))
    await waitFor(() => expect(sessionCreateBodies).toHaveLength(1))
    await waitFor(() => expect(screen.getByText("Estelle welcomes you.")).toBeInTheDocument())
    expect(screen.queryByText("Prior thread")).not.toBeInTheDocument()
  })

  it("Start Over archive failure keeps resume dialog and does not open modal", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
      archiveFail: true,
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })
    await userEvent.click(within(dialog).getByRole("button", { name: "Start Over" }))
    await waitFor(() =>
      expect(screen.getByRole("alertdialog", { name: RESUME_DIALOG_NAME })).toBeInTheDocument(),
    )
    expect(screen.queryByRole("heading", { name: "Candidate Intake" })).not.toBeInTheDocument()
  })

  it("Start Over treats archive 404 as success and opens fresh session", async () => {
    const { sessionCreateBodies } = installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
      archiveNotFound: true,
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })
    await userEvent.click(within(dialog).getByRole("button", { name: "Start Over" }))
    await waitFor(() => expect(sessionCreateBodies).toHaveLength(1))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Intake" })).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Estelle welcomes you.")).toBeInTheDocument())
    expect(screen.queryByText("Prior thread")).not.toBeInTheDocument()
  })

  it("Start Over shows hold copy while initiate runs", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
      delaySessionCreateMs: 80,
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })
    await userEvent.click(within(dialog).getByRole("button", { name: "Start Over" }))
    await waitFor(() => expect(screen.getByText(HOLD_COPY)).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Estelle welcomes you.")).toBeInTheDocument())
  })

  it("dismiss resume dialog does not open modal", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })
    const overlay = dialog.closest(".user-prompt-overlay")
    expect(overlay).toBeTruthy()
    // Click overlay backdrop (not the centered card — card stopPropagation blocks dismiss)
    fireEvent.click(overlay!, { clientX: 4, clientY: 4 })
    await waitFor(() =>
      expect(screen.queryByRole("alertdialog", { name: RESUME_DIALOG_NAME })).not.toBeInTheDocument(),
    )
    expect(screen.queryByRole("heading", { name: "Candidate Intake" })).not.toBeInTheDocument()
  })
})

describe("IntakeChatModal", () => {
  const onClose = vi.fn()

  beforeEach(() => {
    mockedApi.mockReset()
    onClose.mockReset()
    vi.spyOn(window, "confirm").mockReturnValue(true)
  })

  it("auto-starts session with persisted materials when autoStart and no active session", async () => {
    const { sessionCreateBodies } = installIntakeMocks()
    renderWithProviders(
      <IntakeChatModal
        open
        autoStart
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByText("Estelle welcomes you.")).toBeInTheDocument())
    expect(sessionCreateBodies[0]).toEqual(defaultMaterials)
    expect(screen.queryByRole("button", { name: "Start interview" })).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/Original Resume Text/i)).not.toBeInTheDocument()
  })

  it("freshStart ignores stale active GET and creates session", async () => {
    const { sessionCreateBodies } = installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")],
      }),
    })
    renderWithProviders(
      <IntakeChatModal
        open
        autoStart
        freshStart
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(sessionCreateBodies).toHaveLength(1))
    await waitFor(() => expect(screen.getByText("Estelle welcomes you.")).toBeInTheDocument())
    expect(screen.queryByText("Prior thread")).not.toBeInTheDocument()
  })

  it("resumes active session on open without auto-start POST", async () => {
    const { sessionCreateBodies } = installIntakeMocks({
      activeSession: sessionDto({
        transcript: [
          transcriptEntry("assistant", "Prior thread", "initiate_candidate"),
          transcriptEntry("user", "Earlier reply", "candidate_response"),
        ],
      }),
    })
    renderWithProviders(
      <IntakeChatModal
        open
        autoStart
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByText("Prior thread")).toBeInTheDocument())
    expect(screen.getByText("Earlier reply")).toBeInTheDocument()
    expect(screen.queryByText(HOLD_COPY)).not.toBeInTheDocument()
    expect(sessionCreateBodies).toHaveLength(0)
  })

  it("hides initiate_candidate user payload; first bubble is assistant", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [
          transcriptEntry("user", INITIATE_USER_TEXT, "initiate_candidate"),
          transcriptEntry("assistant", "Estelle intro here", "initiate_candidate"),
        ],
      }),
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByText("Estelle intro here")).toBeInTheDocument())
    expect(screen.queryByText(/RESUME:/)).not.toBeInTheDocument()
    expect(screen.queryByText(HOLD_COPY)).not.toBeInTheDocument()
  })

  it("shows hold when active session has no assistant message", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("user", INITIATE_USER_TEXT, "initiate_candidate")],
        awaiting_agent: true,
      }),
      stickyAwaiting: true,
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByText(HOLD_COPY)).toBeInTheDocument())
    expect(screen.queryByText(/RESUME:/)).not.toBeInTheDocument()
  })

  it("shows hold when active session transcript is empty", async () => {
    installIntakeMocks({
      activeSession: sessionDto({ transcript: [], awaiting_agent: true }),
      stickyAwaiting: true,
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByText(HOLD_COPY)).toBeInTheDocument())
  })

  it("keeps Generate Profile disabled until can_build", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Not ready yet", "initiate_candidate")],
        ready_to_build: false,
        can_build: false,
      }),
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Generate Profile" })).toBeDisabled())
  })

  it("enables Generate Profile when can_build and still allows Send", async () => {
    const { turnBodies } = installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Ready when you are", "initiate_candidate")],
        ready_to_build: true,
        can_build: true,
      }),
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Generate Profile" })).toBeEnabled())
    const composer = screen.getByPlaceholderText("Reply…")
    await userEvent.type(composer, "One more detail")
    await userEvent.click(screen.getByRole("button", { name: "Send" }))
    await waitFor(() =>
      expect(turnBodies.some(b => b.message === "One more detail")).toBe(true),
    )
    expect(screen.getByText("Follow-up question.")).toBeInTheDocument()
  })

  it("runs build once and disables Generate Profile afterward", async () => {
    const { buildCalls } = installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Ready", "initiate_candidate")],
        ready_to_build: true,
        can_build: true,
      }),
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Generate Profile" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Generate Profile" }))
    await waitFor(() =>
      expect(screen.getByText("Profile generated — review on Profile and context screens.")).toBeInTheDocument(),
    )
    expect(buildCalls).toHaveLength(1)
    expect(screen.getByRole("button", { name: "Generate Profile" })).toBeDisabled()
    await userEvent.click(screen.getByRole("button", { name: "Generate Profile" }))
    expect(buildCalls).toHaveLength(1)
  })

  it("polls active session until assistant arrives after empty resume", async () => {
    installIntakeMocks({
      activeSession: sessionDto({ transcript: [], awaiting_agent: true }),
      stickyAwaiting: true,
      pollUntilAssistantAfterGets: 3,
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    expect(await screen.findByText(HOLD_COPY)).toBeInTheDocument()
    expect(await screen.findByText("Estelle arrived after poll", { timeout: 8000 })).toBeInTheDocument()
  })

  it("unmount during autoStart does not prevent session create fetch", async () => {
    const { sessionCreateInits } = installIntakeMocks({ delaySessionCreateMs: 100 })
    const { rerender } = renderWithProviders(
      <IntakeChatModal
        open
        autoStart
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(sessionCreateInits.length).toBe(1))
    rerender(
      <IntakeChatModal
        open={false}
        autoStart
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(sessionCreateInits).toHaveLength(1))
    expect(sessionCreateInits[0]?.signal).toBeUndefined()
  })

  it("offers New intake session after build with confirm", async () => {
    installIntakeMocks({
      activeSession: sessionDto({
        transcript: [transcriptEntry("assistant", "Done", "initiate_candidate")],
        ready_to_build: true,
        can_build: false,
        build_completed: true,
        status: "built",
      }),
    })
    renderWithProviders(
      <IntakeChatModal
        open
        candidateId={candidateId}
        materials={defaultMaterials}
        onClose={onClose}
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "New intake session" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "New intake session" }))
    const dialog = await screen.findByRole("alertdialog", { name: "New intake session" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Start new session" }))
    await waitFor(() => expect(screen.getByText("Estelle welcomes you.")).toBeInTheDocument())
  })
})
