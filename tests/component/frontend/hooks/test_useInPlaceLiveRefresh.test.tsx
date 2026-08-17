import { act, renderHook } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { useInPlaceLiveRefresh } from "../../../../src/ui/frontend/src/hooks/useInPlaceLiveRefresh"

describe("useInPlaceLiveRefresh (AST-1409)", () => {
  it("starts loading; later beginRefresh is silent unless showSpinner is true", () => {
    const { result } = renderHook(() => useInPlaceLiveRefresh())
    expect(result.current.loading).toBe(true)

    act(() => result.current.endRefresh())
    expect(result.current.loading).toBe(false)

    act(() => result.current.beginRefresh())
    expect(result.current.loading).toBe(false)
    act(() => result.current.beginRefresh(false))
    expect(result.current.loading).toBe(false)

    act(() => result.current.beginRefresh(true))
    expect(result.current.loading).toBe(true)
    act(() => result.current.endRefresh())
    expect(result.current.loading).toBe(false)
  })
})
