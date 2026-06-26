import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import ListTableTruncatedCell from "../../../../src/ui/frontend/src/components/ListTableTruncatedCell"

describe("ListTableTruncatedCell (AST-647)", () => {
  it("renders plain text when under maxChars", () => {
    render(<ListTableTruncatedCell text="hello" maxChars={30} />)
    expect(screen.getByText("hello")).toBeInTheDocument()
    expect(screen.queryByTitle("hello")).not.toBeInTheDocument()
  })

  it("truncates with ellipsis and title tooltip when over maxChars", () => {
    const full = "A".repeat(50)
    render(<ListTableTruncatedCell text={full} maxChars={30} />)
    const el = screen.getByTitle(full)
    expect(el.textContent).toBe(`${"A".repeat(30)}\u2026`)
  })
})
