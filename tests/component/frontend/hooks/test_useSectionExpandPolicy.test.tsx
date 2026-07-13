import { renderHook, act } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { useSectionExpandPolicy } from "../../../../src/ui/frontend/src/hooks/useSectionExpandPolicy"

const KEYS = ["a", "b", "c"] as const

describe("useSectionExpandPolicy", () => {
  describe("Expand One (default)", () => {
    it("opens at most one section; opening another closes the first", () => {
      const { result } = renderHook(() => useSectionExpandPolicy({ sectionKeys: KEYS }))
      expect(result.current.showBulkChrome).toBe(false)
      expect(result.current.expandedKeys.size).toBe(0)

      act(() => result.current.onExpandedChange("a", true))
      expect([...result.current.expandedKeys]).toEqual(["a"])

      act(() => result.current.onExpandedChange("b", true))
      expect([...result.current.expandedKeys]).toEqual(["b"])
      expect(result.current.isExpanded("a")).toBe(false)
      expect(result.current.isExpanded("b")).toBe(true)
    })

    it("collapsing the open section leaves zero expanded", () => {
      const { result } = renderHook(() => useSectionExpandPolicy({ sectionKeys: KEYS }))
      act(() => result.current.onExpandedChange("a", true))
      act(() => result.current.onExpandedChange("a", false))
      expect(result.current.expandedKeys.size).toBe(0)
    })

    it("expandAll: false matches omit (Expand One)", () => {
      const { result } = renderHook(() =>
        useSectionExpandPolicy({ expandAll: false, sectionKeys: KEYS }),
      )
      expect(result.current.showBulkChrome).toBe(false)
      act(() => result.current.onExpandedChange("a", true))
      act(() => result.current.onExpandedChange("b", true))
      expect([...result.current.expandedKeys]).toEqual(["b"])
    })
  })

  describe("Expand All", () => {
    it("allows two or more sections open independently", () => {
      const { result } = renderHook(() =>
        useSectionExpandPolicy({ expandAll: true, sectionKeys: KEYS }),
      )
      expect(result.current.showBulkChrome).toBe(true)

      act(() => result.current.onExpandedChange("a", true))
      act(() => result.current.onExpandedChange("b", true))
      expect(result.current.isExpanded("a")).toBe(true)
      expect(result.current.isExpanded("b")).toBe(true)
      expect(result.current.expandedKeys.size).toBe(2)
    })

    it("collapsing one does not close siblings; full collapse reaches zero", () => {
      const { result } = renderHook(() =>
        useSectionExpandPolicy({ expandAll: true, sectionKeys: KEYS }),
      )
      act(() => result.current.onExpandedChange("a", true))
      act(() => result.current.onExpandedChange("b", true))
      act(() => result.current.onExpandedChange("a", false))
      expect(result.current.isExpanded("a")).toBe(false)
      expect(result.current.isExpanded("b")).toBe(true)

      act(() => result.current.collapseAllSections())
      expect(result.current.expandedKeys.size).toBe(0)
    })

    it("expandAllSections opens every section key", () => {
      const { result } = renderHook(() =>
        useSectionExpandPolicy({ expandAll: true, sectionKeys: KEYS }),
      )
      act(() => result.current.expandAllSections())
      expect([...result.current.expandedKeys].sort()).toEqual(["a", "b", "c"])
    })

    it("supports partial multi-open without expandAllSections", () => {
      const { result } = renderHook(() =>
        useSectionExpandPolicy({ expandAll: true, sectionKeys: KEYS }),
      )
      act(() => result.current.onExpandedChange("a", true))
      act(() => result.current.onExpandedChange("c", true))
      expect([...result.current.expandedKeys].sort()).toEqual(["a", "c"])
    })
  })
})
