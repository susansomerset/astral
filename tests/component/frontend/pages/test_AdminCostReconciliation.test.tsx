import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CostReconciliation from "../../../../src/ui/frontend/src/pages/AdminCostReconciliation"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const csvHeader = "usage_date_utc,model,workspace,api_key,usage_type,context_window,token_type,cost_usd,cost_type,inference_geo,speed"
const csvRow = "2026-05-01,claude,ws,key,usage,200k,input_no_cache,1.25,standard,us,fast"

function fileInput() {
  return screen.getByLabelText("Anthropic Billing CSV").parentElement!.querySelector("input[type='file']") as HTMLInputElement
}

describe("AdminCostReconciliation", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    URL.createObjectURL = vi.fn(() => "blob:reconciliation")
    URL.revokeObjectURL = vi.fn()
  })

  it("rejects astral exports, loads billing csv, and exports composite csv", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/admin/config") {
        return {
          json: async () => ({
            reconciliation: {
              astral_export_markers: ["# astral export"],
              export_filename_prefix: "astral",
            },
          }),
        } as Response
      }
      if (url.startsWith("/api/admin/timesheets")) {
        return {
          json: async () => [
            {
              created_at: "2026-05-01T10:00:00Z",
              user_prompt_file: "task_a",
              est_cost: 1.1,
              tokens_input: 10,
              cache_read_tokens: 20,
              cache_creation_tokens: 5,
              tokens_output: 30,
            },
          ],
        } as Response
      }
    })

    renderWithProviders(<CostReconciliation />)
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/admin/config"))

    fireEvent.change(fileInput(), { target: { files: [new File(["row\n# astral export"], "astral.csv", { type: "text/csv" })] } })
    await waitFor(() => expect(screen.getByText(/looks like an Astral export/)).toBeInTheDocument())

    fireEvent.change(fileInput(), { target: { files: [new File([`${csvHeader}\n${csvRow}`], "billing.csv", { type: "text/csv" })] } })
    await waitFor(() => expect(screen.getByText(/1 CSV rows/)).toBeInTheDocument())
    expect(screen.getByText("task_a")).toBeInTheDocument()

    const anchorClick = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {})
    fireEvent.click(screen.getByRole("button", { name: "Export CSV" }))
    expect(anchorClick).toHaveBeenCalled()
    anchorClick.mockRestore()
  }, 15000)

  it("handles empty csv and failed timesheet fetch", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/admin/config") {
        return { json: async () => ({}) } as Response
      }
      if (url.startsWith("/api/admin/timesheets")) {
        throw new Error("timesheets failed")
      }
    })

    renderWithProviders(<CostReconciliation />)
    fireEvent.change(fileInput(), { target: { files: [new File(["header only"], "empty.csv", { type: "text/csv" })] } })
    await waitFor(() => expect(screen.queryByRole("button", { name: "Export CSV" })).not.toBeInTheDocument())
  }, 15000)
})
