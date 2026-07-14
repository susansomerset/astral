import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import SectionExpandChrome from "../../../../src/ui/frontend/src/components/SectionExpandChrome"

describe("SectionExpandChrome", () => {
  it("renders Expand all / Collapse all and fires callbacks", async () => {
    const user = userEvent.setup()
    const onExpandAll = vi.fn()
    const onCollapseAll = vi.fn()
    render(<SectionExpandChrome onExpandAll={onExpandAll} onCollapseAll={onCollapseAll} />)

    const expandBtn = screen.getByRole("button", { name: "Expand all" })
    const collapseBtn = screen.getByRole("button", { name: "Collapse all" })
    expect(expandBtn).toHaveAttribute("type", "button")
    expect(collapseBtn).toHaveAttribute("type", "button")
    expect(expandBtn.closest(".section-expand-chrome")).toBeTruthy()

    await user.click(expandBtn)
    await user.click(collapseBtn)
    expect(onExpandAll).toHaveBeenCalledTimes(1)
    expect(onCollapseAll).toHaveBeenCalledTimes(1)
  })
})
