import { screen, waitFor } from "@testing-library/react"
import { Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"
import JobsHomeRedirect from "../../../../src/ui/frontend/src/components/JobsHomeRedirect"
import api from "../../../../src/ui/frontend/src/lib/api"
import { renderWithProviders } from "../test-utils"
import { candidateId, installBaseApiMocks, jsonResponse } from "../pages/page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

// NAV_CONFIG shape (AST-1974 counts): Jobs group in nav order — Ready, Review, Applied, Processing, Skipped.
const jobsNav = (counts: Record<string, number>) => [
  { label: "Candidate", items: [{ path: "/candidate/profile", count: 9 }] },
  {
    label: "Jobs",
    items: ["ready", "review", "applied", "processing", "skipped"].map(v => ({
      path: `/jobs/${v}`,
      count: counts[v] ?? 0,
    })),
  },
]

function renderHome() {
  renderWithProviders(
    <Routes>
      <Route path="/" element={<JobsHomeRedirect />} />
      <Route path="/jobs/:view" element={<p data-testid="landed" />} />
    </Routes>,
    { router: { initialEntries: ["/"] } },
  )
}

// AST-1975 AC: landing = first Jobs nav item with count > 0, else the first Jobs item.
describe("JobsHomeRedirect — AST-1975 landing page", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  const landedPath = () => screen.getByTestId("landed")

  it("fetches nav counts once for the selected candidate and leaves Loading", async () => {
    installBaseApiMocks(mockedApi, url =>
      url.startsWith("/api/nav_config") ? jsonResponse(jobsNav({ review: 3, processing: 5 })) : jsonResponse([]))
    renderHome()
    await waitFor(() => expect(landedPath()).toBeInTheDocument())
    const navCalls = mockedApi.mock.calls.filter(([u]) => String(u).startsWith("/api/nav_config"))
    expect(navCalls.map(([u]) => u)).toEqual([`/api/nav_config?candidate_id=${candidateId}`])
    expect(screen.queryByText("Loading…")).toBeNull()
  })

  it.each([
    [{ ready: 2, review: 3 }, "/jobs/ready"],
    // Ready 0 is skipped; later non-zero items don't outrank Review.
    [{ review: 3, processing: 5 }, "/jobs/review"],
    [{ skipped: 1 }, "/jobs/skipped"],
    [{}, "/jobs/ready"],
  ])("counts %j land on %s", async (counts, expected) => {
    installBaseApiMocks(mockedApi, url =>
      url.startsWith("/api/nav_config") ? jsonResponse(jobsNav(counts)) : jsonResponse([]))
    renderWithProviders(
      <Routes>
        <Route path="/" element={<JobsHomeRedirect />} />
        <Route path={expected} element={<p>{`at ${expected}`}</p>} />
      </Routes>,
      { router: { initialEntries: ["/"] } },
    )
    expect(await screen.findByText(`at ${expected}`)).toBeInTheDocument()
  })

  it("waits for candidate hydration before fetching nav counts", async () => {
    installBaseApiMocks(mockedApi, url =>
      url.startsWith("/api/nav_config") ? jsonResponse(jobsNav({ review: 1 })) : jsonResponse([]))
    const inner = mockedApi.getMockImplementation()!
    let release: () => void = () => {}
    const gate = new Promise<void>(resolve => { release = resolve })
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") await gate
      return inner(url, init)
    })
    renderHome()
    expect(await screen.findByText("Loading…")).toBeInTheDocument()
    expect(mockedApi.mock.calls.some(([u]) => String(u).startsWith("/api/nav_config"))).toBe(false)
    release()
    await waitFor(() => expect(landedPath()).toBeInTheDocument())
  })

  it("shows Navigation unavailable when nav_config fails", async () => {
    installBaseApiMocks(mockedApi, url =>
      url.startsWith("/api/nav_config") ? jsonResponse({ error: "boom" }, { ok: false, status: 500 }) : jsonResponse([]))
    renderHome()
    expect(await screen.findByText("Navigation unavailable.")).toBeInTheDocument()
    expect(screen.queryByTestId("landed")).toBeNull()
  })

  it("shows Navigation unavailable when the Jobs group has no items", async () => {
    installBaseApiMocks(mockedApi, url =>
      url.startsWith("/api/nav_config") ? jsonResponse([{ label: "Jobs", items: [] }]) : jsonResponse([]))
    renderHome()
    expect(await screen.findByText("Navigation unavailable.")).toBeInTheDocument()
  })
})
