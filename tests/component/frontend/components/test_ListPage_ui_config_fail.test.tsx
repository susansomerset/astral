import { render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

describe("ListPage ui_config failure (fresh module)", () => {
  beforeEach(() => {
    vi.resetModules()
    localStorage.clear()
  })

  it("uses empty column types when ui_config rejects", async () => {
    const api = (await import("../../../../src/ui/frontend/src/lib/api")).default
    vi.mocked(api).mockImplementation(async (url: string) => {
      if (url === "/api/system/ui_config") throw new Error("down")
      return { json: async () => ({ column_types: {} }) } as Response
    })
    const { default: ListPage } = await import("../../../../src/ui/frontend/src/components/ListPage")
    render(<ListPage title="UiFail" columns={[{ key: "name", label: "Name" }]} rows={[{ id: "1", name: "ok" }]} />)
    await waitFor(() => expect(screen.getByText("ok")).toBeInTheDocument())
  })
})
