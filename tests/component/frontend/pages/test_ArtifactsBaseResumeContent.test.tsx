import { fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { useCandidate } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import ArtifactsBaseResumeContent from "../../../../src/ui/frontend/src/pages/ArtifactsBaseResumeContent"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders } from "../test-utils"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const structureByCandidate: Record<
  string,
  { sections: { id: string; label: string }[]; accent_color: string | null }
> = {
  c1: {
    sections: [
      { id: "professional_summary", label: "Summary" },
      { id: "technical_skills", label: "Skills" },
    ],
    accent_color: "#445566",
  },
  c2: {
    sections: [{ id: "experience", label: "Work History" }],
    accent_color: null,
  },
}

const baseResumeByCandidate: Record<string, Record<string, string>> = {
  c1: {
    professional_summary: "Saved summary",
    technical_skills: "Saved skills",
    orphan_section: "Hidden orphan",
  },
  c2: { experience: "Candidate two body" },
}

function CandidateSelectC2() {
  const { setSelectedId } = useCandidate()
  return (
    <button type="button" onClick={() => setSelectedId("c2")}>
      Select c2
    </button>
  )
}

function installMocks(candidates: string[] = ["c1"]) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/me") {
      return {
        ok: true,
        json: async () => ({ user_id: "u1", name: "Test", is_admin: true }),
      } as Response
    }
    if (url === "/api/state_ui_manifest") {
      return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
    }
    if (url === "/api/candidates") {
      return {
        json: async () =>
          candidates.map(id => ({ astral_candidate_id: id, state: "CONTEXT_READY", candidate_data: {} })),
      } as Response
    }
    if (url === "/api/system/ui_config") {
      return {
        json: async () => ({
          column_types: {},
          base_resume_accent_palette: ["#112233", "#445566"],
        }),
      } as Response
    }
    const structureMatch = url.match(/^\/api\/candidates\/(c\d)\/resume_structure$/)
    if (structureMatch && !init) {
      const cid = structureMatch[1]
      return {
        json: async () => structureByCandidate[cid] ?? { sections: [], accent_color: null },
      } as Response
    }
    const candidateMatch = url.match(/^\/api\/candidates\/(c\d)$/)
    if (candidateMatch && !init) {
      const cid = candidateMatch[1]
      return {
        json: async () => ({
          candidate_data: { artifacts: { base_resume: baseResumeByCandidate[cid] ?? {} } },
        }),
      } as Response
    }
    const putMatch = url.match(/^\/api\/candidates\/(c\d)\/data$/)
    if (putMatch && init?.method === "PUT") {
      return { ok: true, json: async () => ({}) } as Response
    }
    throw new Error(`unexpected api call: ${url} ${init?.method ?? "GET"}`)
  })
}

describe("ArtifactsBaseResumeContent", () => {
  beforeEach(() => {
    localStorage.clear()
    resetStytchTestState()
    mockedApi.mockReset()
    installMocks()
  })

  it("renders structure-driven tabs and hides orphan base_resume keys", async () => {
    renderWithProviders(<ArtifactsBaseResumeContent />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Base Resume Content" })).toBeInTheDocument())
    expect(screen.getByDisplayValue("Saved summary")).toBeInTheDocument()
    expect(screen.queryByDisplayValue("Hidden orphan")).not.toBeInTheDocument()
    expect(mockedApi.mock.calls.some(([u]) => u === "/api/shapes/candidates")).toBe(false)
  })

  it("renders accent swatches and saves to resume_structure", async () => {
    renderWithProviders(<ArtifactsBaseResumeContent />)
    await waitFor(() => expect(screen.getByRole("group", { name: "Resume accent color" })).toBeInTheDocument())
    const selected = await screen.findByRole("button", { name: "#445566" })
    expect(selected).toHaveAttribute("aria-pressed", "true")
    fireEvent.click(screen.getByRole("button", { name: "#112233" }))
    await waitFor(() => expect(screen.getByText("Accent color saved")).toBeInTheDocument())
    const putCall = mockedApi.mock.calls.find(
      ([url, init]) => url === "/api/candidates/c1/data" && init?.method === "PUT",
    )
    expect(putCall).toBeTruthy()
    const body = JSON.parse(String(putCall?.[1]?.body))
    expect(body.artifacts.resume_structure.accent_color).toBe("#112233")
    expect(body.artifacts.base_resume).toBeUndefined()
  })

  it("loads different structure tabs when switching candidates", async () => {
    installMocks(["c1", "c2"])
    renderWithProviders(
      <>
        <CandidateSelectC2 />
        <ArtifactsBaseResumeContent />
      </>,
    )
    await waitFor(() => expect(screen.getByDisplayValue("Saved summary")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Select c2" }))
    await waitFor(() => expect(screen.getByDisplayValue("Candidate two body")).toBeInTheDocument())
    expect(screen.queryByDisplayValue("Saved summary")).not.toBeInTheDocument()
  })
})
