import { act, renderHook } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { useLocalStorage } from "../../../../src/ui/frontend/src/lib/useLocalStorage"

describe("useLocalStorage", () => {
  it("reads stored JSON on mount", () => {
    localStorage.setItem("count", JSON.stringify(3))
    const { result } = renderHook(() => useLocalStorage("count", 0))
    expect(result.current[0]).toBe(3)
  })

  it("falls back when storage is missing or invalid", () => {
    const { result: missing } = renderHook(() => useLocalStorage("missing", "default"))
    expect(missing.current[0]).toBe("default")

    localStorage.setItem("broken", "{")
    const { result: broken } = renderHook(() => useLocalStorage("broken", "default"))
    expect(broken.current[0]).toBe("default")

    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked")
    })
    const { result: blocked } = renderHook(() => useLocalStorage("blocked", "default"))
    expect(blocked.current[0]).toBe("default")
  })

  it("swallows initial storage write failures", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("quota")
    })
    const { result } = renderHook(() => useLocalStorage("locked", "ok"))
    expect(result.current[0]).toBe("ok")
  })

  it("swallows JSON.stringify errors in the persistence effect", () => {
    const circular: Record<string, unknown> = {}
    circular.self = circular
    const { result } = renderHook(() => useLocalStorage("bad-json", circular as never))
    expect(result.current[0]).toBe(circular)
  })

  it("writes updates and tolerates quota errors", () => {
    const setItem = vi.spyOn(Storage.prototype, "setItem")
    const { result } = renderHook(() => useLocalStorage("flag", false))

    act(() => {
      result.current[1](true)
    })
    expect(localStorage.getItem("flag")).toBe("true")

    act(() => {
      result.current[1](prev => !prev)
    })
    expect(localStorage.getItem("flag")).toBe("false")

    setItem.mockImplementationOnce(() => {
      throw new Error("quota")
    })
    act(() => {
      result.current[1](true)
    })
    expect(result.current[0]).toBe(true)
    setItem.mockRestore()
  })
})
