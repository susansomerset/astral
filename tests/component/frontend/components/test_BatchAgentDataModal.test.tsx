import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import BatchAgentDataModal from "../../../../src/ui/frontend/src/components/BatchAgentDataModal"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

describe("BatchAgentDataModal", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("loads grouped blocks and timesheet totals", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url.startsWith("/api/agent_data/")) {
        return {
          json: async () => [
            { agent_data_id: "1", block_type: "SYSTEM", block_data: "{\"a\":1}", token_size: 1, task_key: "t", created_at: "now" },
            { agent_data_id: "2", block_type: "SYSTEM", block_data: "raw", token_size: 1, task_key: "t", created_at: "now" },
            { agent_data_id: "3", block_type: "CUSTOM", block_data: "x", token_size: 1, task_key: "t", created_at: "now" },
          ],
        } as Response
      }
      if (url.includes("/api/admin/timesheets")) {
        return {
          json: async () => [
            {
              cache_write_tokens: 1,
              cache_read_tokens: 2,
              total_no_cache_input_tokens: 3,
              total_output_tokens: 4,
              calc_cost_cache_write: 0.1,
              calc_cost_cache_read: 0.2,
              calc_cost_no_cache_input: 0.3,
              calc_cost_output: 0.4,
            },
          ],
        } as Response
      }
      throw new Error(url)
    })

    const onClose = vi.fn()
    renderWithProviders(<BatchAgentDataModal batchId="batch-1" onClose={onClose} />)
    await waitFor(() => expect(screen.getByText(/Tokens & Cost/)).toBeInTheDocument())
    expect(screen.getByText(/SYSTEM ×2/)).toBeInTheDocument()
    await userEvent.click(screen.getByText("CUSTOM"))
    expect(screen.getByDisplayValue("x")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))
    expect(onClose).toHaveBeenCalled()
  })

  it("shows empty and error states", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url.startsWith("/api/agent_data/")) {
        return { json: async () => [] } as Response
      }
      if (url.includes("/api/admin/timesheets")) {
        return { json: async () => [] } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<BatchAgentDataModal batchId="batch-2" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("No agent data blocks recorded for this batch.")).toBeInTheDocument())

    mockedApi.mockRejectedValueOnce(new Error("fail"))
    renderWithProviders(<BatchAgentDataModal batchId="batch-3" onClose={() => {}} />)
    await waitFor(() => expect(screen.queryByText("Loading…")).not.toBeInTheDocument())
  })

  it("covers sparse timesheets, single blocks, and null batch ids", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url.startsWith("/api/agent_data/")) {
        return {
          json: async () => [
            { agent_data_id: "1", block_type: "RESPONSE", block_data: "plain", token_size: 1, task_key: "t", created_at: "now" },
          ],
        } as Response
      }
      if (url.includes("/api/admin/timesheets")) {
        return { json: async () => [{}] } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<BatchAgentDataModal batchId="batch-4" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByDisplayValue("plain")).toBeInTheDocument())

    mockedApi.mockImplementation(async (url: string) => {
      if (url.startsWith("/api/agent_data/")) {
        return { json: async () => ({ bad: true }) } as Response
      }
      if (url.includes("/api/admin/timesheets")) {
        return { json: async () => "bad" } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<BatchAgentDataModal batchId="batch-5" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("No agent data blocks recorded for this batch.")).toBeInTheDocument())

    renderWithProviders(<BatchAgentDataModal batchId={null} onClose={() => {}} />)
    expect(screen.queryByText("Loading…")).not.toBeInTheDocument()
  })

  it("uses empty active tab when block_type is missing and still renders tabs", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url.startsWith("/api/agent_data/")) {
        return {
          json: async () => [
            {
              agent_data_id: "1",
              block_data: "orphan",
              token_size: 1,
              task_key: "t",
              created_at: "now",
            },
          ],
        } as Response
      }
      if (url.includes("/api/admin/timesheets")) {
        return {
          json: async () => [
            {
              cache_write_tokens: 0,
              cache_read_tokens: 0,
              total_no_cache_input_tokens: 0,
              total_output_tokens: 0,
              calc_cost_cache_write: 0,
              calc_cost_cache_read: 0,
              calc_cost_no_cache_input: 0,
              calc_cost_output: 0,
            },
          ],
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<BatchAgentDataModal batchId="batch-bad-type" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText(/Tokens & Cost/)).toBeInTheDocument())
    await waitFor(() => expect(screen.getByRole("textbox")).toHaveValue(""))
  })

  it("shows FEEDBACK tab when block type present (AST-725)", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url.startsWith("/api/agent_data/")) {
        return {
          json: async () => [
            {
              agent_data_id: "fb-1",
              block_type: "FEEDBACK",
              block_data: '{"vector_reviews":["bad"]}',
              token_size: 1,
              task_key: "grade_get",
              created_at: "now",
            },
          ],
        } as Response
      }
      if (url.includes("/api/admin/timesheets")) {
        return { json: async () => [] } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<BatchAgentDataModal batchId="batch-fb" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("FEEDBACK")).toBeInTheDocument())
    await waitFor(() => {
      const ta = document.querySelector(".batch-agent-data-textarea") as HTMLTextAreaElement
      expect(ta?.value).toContain("vector_reviews")
      expect(ta?.value).toContain("bad")
    })
  })
})
