import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import RepoJsonDivergenceBanner from "../../../../src/ui/frontend/src/components/RepoJsonDivergenceBanner"
import { UserPromptProvider } from "../../../../src/ui/frontend/src/components/UserPrompt"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

function renderBanner(tableKey: "agent" | "agent_task" = "agent") {
  return render(
    <UserPromptProvider>
      <RepoJsonDivergenceBanner tableKey={tableKey} />
    </UserPromptProvider>,
  )
}

describe("RepoJsonDivergenceBanner", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("AST-783: hides banner when table is not diverged", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({
        agent: { diverged: false, repo_relative_path: "data/admin/agent.json" },
        agent_task: { diverged: false, repo_relative_path: "data/admin/agent_task.json" },
      }),
    } as Response)
    renderBanner("agent")
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/admin/repo_json/status"))
    expect(screen.queryByRole("button", { name: "Revert to file" })).not.toBeInTheDocument()
  })

  it("AST-783: shows warning and reverts after themed confirm", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/repo_json/status") {
        return {
          ok: true,
          json: async () => ({
            agent: { diverged: true, repo_relative_path: "data/admin/agent.json" },
            agent_task: { diverged: false, repo_relative_path: "data/admin/agent_task.json" },
          }),
        } as Response
      }
      if (url === "/api/admin/repo_json/revert/agent" && init?.method === "POST") {
        return { ok: true, json: async () => ({ ok: true, row_count: 1 }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderBanner("agent")
    await waitFor(() => expect(screen.getByRole("button", { name: "Revert to file" })).toBeInTheDocument())
    expect(screen.getByText(/agent personas/)).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Revert to file" }))
    await waitFor(() => expect(screen.getByRole("alertdialog")).toBeInTheDocument())
    const confirmButtons = screen.getAllByRole("button", { name: "Revert to file" })
    await userEvent.click(confirmButtons[confirmButtons.length - 1])

    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/admin/repo_json/revert/agent", { method: "POST" }),
    )
  })
})
