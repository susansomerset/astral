import { render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"
import MeteoriteDetailModal from "../../../../src/ui/frontend/src/components/MeteoriteDetailModal"
import api from "../../../../src/ui/frontend/src/lib/api"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const SECTIONS = [
  { section_id: "meteorite_timestamps", nav_label: "Timestamps", default_expanded: true },
  { section_id: "meteorite_link", nav_label: "Link", default_expanded: true },
  { section_id: "meteorite_content", nav_label: "Content", default_expanded: true },
  { section_id: "meteorite_provenance", nav_label: "Provenance", default_expanded: false },
  { section_id: "meteorite_job", nav_label: "Linked Job", default_expanded: true },
]

function detail(overrides: Record<string, unknown> = {}) {
  return {
    id: 7,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-02T00:00:00Z",
    state_changed_at: "2026-01-03T00:00:00Z",
    estelle_notified_at: null,
    link: "https://jobs.example/m",
    classify_outcome: "QUALIFIED",
    content: '{"ok":true}',
    state: "LANDED",
    source_kind: "email",
    source_id: "msg-1",
    error: null,
    job_title: "Staff Eng",
    employer_name: "Acme",
    astral_job_id: "job-99",
    ...overrides,
  }
}

function renderModal(id: number | null) {
  return render(
    <MemoryRouter>
      <MeteoriteDetailModal meteoriteId={id} onClose={() => {}} />
    </MemoryRouter>,
  )
}

describe("MeteoriteDetailModal — AST-1749", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("returns null when closed", () => {
    const { container } = renderModal(null)
    expect(container.firstChild).toBeNull()
    expect(mockedApi).not.toHaveBeenCalled()
  })

  it("http(s) link is navigable; non-http is plain text", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return {
          ok: true,
          status: 200,
          json: async () => ({ sections: SECTIONS, meteorite: detail() }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    const { rerender } = renderModal(7)
    await waitFor(() =>
      expect(screen.getByRole("link", { name: "https://jobs.example/m" })).toBeInTheDocument(),
    )

    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/8") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            sections: SECTIONS,
            meteorite: detail({ id: 8, link: "inbox:folder/msg", astral_job_id: "" }),
          }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    rerender(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={8} onClose={() => {}} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByText("inbox:folder/msg")).toBeInTheDocument())
    expect(screen.queryByRole("link", { name: "inbox:folder/msg" })).not.toBeInTheDocument()
  })

  it("job deeplink present when astral_job_id set; absent when blank", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return {
          ok: true,
          status: 200,
          json: async () => ({ sections: SECTIONS, meteorite: detail() }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    const { rerender } = renderModal(7)
    await waitFor(() =>
      expect(screen.getByRole("link", { name: /Open job job-99/ })).toHaveAttribute(
        "href",
        "/jobs/detail/job-99",
      ),
    )

    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/9") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            sections: SECTIONS,
            meteorite: detail({ id: 9, astral_job_id: "   " }),
          }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    rerender(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={9} onClose={() => {}} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByText("Staff Eng — Acme")).toBeInTheDocument())
    expect(screen.queryByRole("link", { name: /Open job/ })).not.toBeInTheDocument()
  })

  it("404 shows honest error; no Save footer", async () => {
    mockedApi.mockImplementation(async () => {
      return { ok: false, status: 404, json: async () => ({ error: "meteorite not found" }) } as Response
    })
    renderModal(404)
    await waitFor(() => expect(screen.getByText("Meteorite not found")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: /save/i })).not.toBeInTheDocument()
  })
})
