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
import { AST1017_PREAMBLE_CONFIG } from "../fixtures/ast1017PreambleConfig"
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
  /** AST-1017 Ruth validate outcome (default Valid). */
  validateOutcome?: "Valid" | "Try Again" | "Escalate"
}

function installIntakeMocks(state: IntakeMockState = {}) {
  const materials: IntakeSourceMaterials = { ...(state.materials ?? defaultMaterials) }
  let active = state.activeSession === undefined ? null : state.activeSession
  const sessionCreateBodies = state.sessionCreateBodies ?? []
  const turnBodies = state.turnBodies ?? []
  const buildCalls = state.buildCalls ?? []
  const putBodies: Record<string, unknown>[] = []
  const validateBodies: Record<string, unknown>[] = []
  let archiveCalls = state.archiveCalls ?? 0
  let activeGetCalls = 0
  const sessionCreateInits = state.sessionCreateInits ?? []
  const pollAfter = state.pollUntilAssistantAfterGets
  const stickyAwaiting = state.stickyAwaiting ?? false
  const validateOutcome = state.validateOutcome ?? "Valid"

  const resolveAwaitingAssistant = () => {
    if (!active?.awaiting_agent || stickyAwaiting) return
    active = sessionDto({
      session_id: active.session_id,
      transcript: [transcriptEntry("assistant", "Estelle welcomes you.", "initiate_candidate")],
      awaiting_agent: false,
    })
  }

  installBaseApiMocks(mockedApi, (url, init) => {
    if ((url === "/api/ui_config" || url === "/api/system/ui_config") && !init) {
      return jsonResponse({
        preamble: AST1017_PREAMBLE_CONFIG,
        topic_menu_gen: {
          ui: {
            panel_title: "Confirm preamble with Estelle",
            accept_label: "Looks good — generate Topic Menu",
            send_label: "Send to Estelle",
            placeholder: "Tell Estelle what to change, or accept below.",
            generating_label: "Estelle is building your Topic Menu…",
            done_title: "Topic Menu ready",
          },
        },
        column_types: {},
      })
    }
    if (url === `/api/candidates/${candidateId}/topic-menu/confirm` && init?.method === "POST") {
      return jsonResponse({
        success: true,
        outcome: "continue",
        assistant_message: "Anything here you would change?",
        applied_patches: [],
        packet: {},
        batch_id: "intake-topic_menu_preamble_confirm-x",
        error: null,
      })
    }
    if (url === `/api/candidates/${candidateId}/topic-menu/generate` && init?.method === "POST") {
      return jsonResponse({
        success: true,
        menu: { topics: [{ id: "t1", name: "Story", ask: "Win?", required: true, informs: ["backstory"], status: "open" }] },
        rejected_topic_count: 0,
        informs_covered: ["backstory"],
        batch_id: "intake-topic_menu_generate-x",
        error: null,
      })
    }
    if (url === `/api/candidates/${candidateId}` && !init) {
      return jsonResponse({
        candidate_data: {
          context: {
            raw_resume: materials.starting_resume_text,
            raw_sample: materials.sample_cover_text,
            raw_profile: materials.linkedin_profile_text,
          },
        },
      })
    }
    if (url === `/api/candidates/${candidateId}/preamble/validate` && init?.method === "POST") {
      const body = JSON.parse(String(init.body)) as Record<string, unknown>
      validateBodies.push(body)
      return jsonResponse({
        success: true,
        outcome: validateOutcome,
        error: null,
        batch_id: "preamble-preamble_validate_response-x",
      })
    }
    if (url === `/api/candidates/${candidateId}/data` && init?.method === "PUT") {
      const body = JSON.parse(String(init.body)) as { context?: Record<string, string> }
      putBodies.push(body)
      const ctx = body.context ?? {}
      if (ctx.raw_resume != null) materials.starting_resume_text = ctx.raw_resume
      if (ctx.raw_profile != null) materials.linkedin_profile_text = ctx.raw_profile
      if (ctx.raw_sample != null) materials.sample_cover_text = ctx.raw_sample
      return jsonResponse({ ok: true })
    }
    if (url === `/api/candidates/${candidateId}/intake/sessions/active` && !init) {
      if (pollAfter != null) {
        activeGetCalls += 1
        if (activeGetCalls < pollAfter) {
          return jsonResponse(sessionDto({ transcript: [], awaiting_agent: true }))
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
      const created = sessionDto({ transcript: [], awaiting_agent: true })
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
    materials,
    sessionCreateBodies,
    sessionCreateInits,
    turnBodies,
    buildCalls,
    putBodies,
    validateBodies,
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

  it("shows Start Intake confirm then preamble Modal (§6c routed page)", async () => {
    installIntakeMocks()
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: "Start Intake" })
    expect(dialog).toHaveTextContent(/collect any missing source materials/i)
    expect(screen.queryByRole("heading", { name: "Candidate Intake" })).not.toBeInTheDocument()
    await userEvent.click(within(dialog).getByRole("button", { name: "Continue" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Intake" })).toBeInTheDocument())
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.intro)).toBeInTheDocument(),
    )
    expect(screen.getByText(AST1017_PREAMBLE_CONFIG.steps[1].prompt_1st_try)).toBeInTheDocument()
    expect(screen.queryByText("Estelle welcomes you.")).not.toBeInTheDocument()
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

  it("opens preamble when resume text is missing (no Profile hard-gate)", async () => {
    installIntakeMocks({
      materials: { starting_resume_text: "", sample_cover_text: "", linkedin_profile_text: "" },
    })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: "Start Intake" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Continue" }))
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)).toBeInTheDocument(),
    )
    expect(
      screen.queryByText("Add Original Resume Text on Profile before starting Intake."),
    ).not.toBeInTheDocument()
  })

  it("preamble Valid handoff opens Topic Menu confirm (§6c AST-1075)", async () => {
    const fullGaps: IntakeSourceMaterials = {
      starting_resume_text: "",
      sample_cover_text: "",
      linkedin_profile_text: "",
    }
    const { sessionCreateBodies, putBodies } = installIntakeMocks({ materials: fullGaps })
    localStorage.setItem("astral_selected_candidate", candidateId)
    renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })
    const dialog = await screen.findByRole("alertdialog", { name: "Start Intake" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Continue" }))
    await screen.findByText(AST1017_PREAMBLE_CONFIG.steps[0].prompt_1st_try)

    for (const answer of ["Resume body", "LinkedIn body", "Cover body"]) {
      await userEvent.clear(screen.getByPlaceholderText(/Paste your answer/i))
      await userEvent.type(screen.getByPlaceholderText(/Paste your answer/i), answer)
      await userEvent.click(screen.getByRole("button", { name: "Submit" }))
      await waitFor(() => expect(putBodies.length).toBeGreaterThan(0))
    }
    // AST-1075: mechanical preamble complete → Topic Menu phase (not legacy Estelle chat).
    await waitFor(() =>
      expect(screen.getByText("Confirm preamble with Estelle")).toBeInTheDocument(),
    )
    expect(screen.getByText("Anything here you would change?")).toBeInTheDocument()
    expect(sessionCreateBodies).toHaveLength(0)
    expect(screen.queryByText("Estelle welcomes you.")).not.toBeInTheDocument()
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
    const continueBtn = within(dialog).getByRole("button", { name: "Continue" })
    expect(continueBtn).toHaveClass("btn", "primary")
    await userEvent.click(continueBtn)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Intake" })).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Prior thread")).toBeInTheDocument())
    expect(getArchiveCalls()).toBe(0)
    expect(sessionCreateBodies).toHaveLength(0)
  })

  it("Start Over archives then opens preamble (not Estelle yet)", async () => {
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
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.intro)).toBeInTheDocument(),
    )
    expect(sessionCreateBodies).toHaveLength(0)
    expect(screen.queryByText("Prior thread")).not.toBeInTheDocument()
    expect(screen.queryByText("Estelle welcomes you.")).not.toBeInTheDocument()
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

  it("Start Over treats archive 404 as success and opens preamble", async () => {
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
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.intro)).toBeInTheDocument(),
    )
    expect(sessionCreateBodies).toHaveLength(0)
    expect(screen.queryByText("Prior thread")).not.toBeInTheDocument()
  })

  it("Start Over shows preamble Intro before Estelle hold/initiate", async () => {
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
    await waitFor(() =>
      expect(screen.getByText(AST1017_PREAMBLE_CONFIG.intro)).toBeInTheDocument(),
    )
    expect(screen.queryByText(HOLD_COPY)).not.toBeInTheDocument()
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
