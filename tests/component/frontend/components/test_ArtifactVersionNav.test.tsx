import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import ArtifactVersionNav, { versionNavState } from "../../../../src/ui/frontend/src/components/ArtifactVersionNav"

// AST-2068: shared arrows + "N of M". Order comes from `position` only (AST-2067 JSON keys are uuid-sorted).
describe("ArtifactVersionNav", () => {
  it("versionNavState orders by position, not key order", () => {
    // Keys alphabetical (a, b, c) but chronology is c → a → b.
    const nav = versionNavState({
      a: { created_at: "t", current: 1, position: 2 },
      b: { created_at: "t", current: 0, position: 3 },
      c: { created_at: "t", current: 0, position: 1 },
    })
    expect(nav).toEqual({ position: 2, total: 3, backUuid: "c", forwardUuid: "b" })
  })

  it("versionNavState with no current row reports position 0 (the control then locks both arrows)", () => {
    expect(versionNavState({ a: { created_at: "t", current: 0, position: 1 } })).toMatchObject({ position: 0, total: 1 })
    expect(versionNavState({})).toEqual({ position: 0, total: 0, backUuid: null, forwardUuid: null })
  })

  it("renders nothing for an empty history", () => {
    const { container } = render(<ArtifactVersionNav position={0} total={0} onBack={() => {}} onForward={() => {}} />)
    expect(container).toBeEmptyDOMElement()
  })

  it("disables back at 1 of N and forward at N of N; middle fires both handlers", async () => {
    const onBack = vi.fn()
    const onForward = vi.fn()
    const { rerender } = render(<ArtifactVersionNav position={1} total={3} onBack={onBack} onForward={onForward} />)
    expect(screen.getByText("1 of 3")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Previous version" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Next version" })).toBeEnabled()
    rerender(<ArtifactVersionNav position={3} total={3} onBack={onBack} onForward={onForward} />)
    expect(screen.getByRole("button", { name: "Previous version" })).toBeEnabled()
    expect(screen.getByRole("button", { name: "Next version" })).toBeDisabled()
    rerender(<ArtifactVersionNav position={2} total={3} onBack={onBack} onForward={onForward} />)
    await userEvent.click(screen.getByRole("button", { name: "Previous version" }))
    await userEvent.click(screen.getByRole("button", { name: "Next version" }))
    expect(onBack).toHaveBeenCalledTimes(1)
    expect(onForward).toHaveBeenCalledTimes(1)
  })

  it("disabled prop and a missing current row lock both arrows but keep the indicator", () => {
    const { rerender } = render(
      <ArtifactVersionNav position={2} total={3} disabled onBack={() => {}} onForward={() => {}} />,
    )
    expect(screen.getByRole("button", { name: "Previous version" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Next version" })).toBeDisabled()
    rerender(<ArtifactVersionNav position={0} total={2} onBack={() => {}} onForward={() => {}} />)
    expect(screen.getByText("0 of 2")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Previous version" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Next version" })).toBeDisabled()
  })
})
