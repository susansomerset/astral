import { useCallback, useState } from "react"

export type SectionExpandPolicyOptions = {
  /** When true → Expand All. Omit or false → Expand One (default). */
  expandAll?: boolean
  /** Current section keys in render order (used by expandAllSections). */
  sectionKeys: readonly string[]
}

export type SectionExpandPolicy = {
  isExpanded: (key: string) => boolean
  onExpandedChange: (key: string, next: boolean) => void
  expandAllSections: () => void
  collapseAllSections: () => void
  /** True only when expandAll is true — pages render SectionExpandChrome when this is true. */
  showBulkChrome: boolean
  /** Imperative set for page effects (e.g. Scheduled Actions first-section auto-open, candidate-change reset). */
  setExpandedKeys: (
    keys: ReadonlySet<string> | ((prev: ReadonlySet<string>) => ReadonlySet<string>),
  ) => void
  expandedKeys: ReadonlySet<string>
}

export function useSectionExpandPolicy(options: SectionExpandPolicyOptions): SectionExpandPolicy {
  const { expandAll = false, sectionKeys } = options
  const [expandedKeys, setExpandedKeys] = useState<ReadonlySet<string>>(() => new Set())

  const isExpanded = useCallback((key: string) => expandedKeys.has(key), [expandedKeys])

  const onExpandedChange = useCallback(
    (key: string, next: boolean) => {
      setExpandedKeys(prev => {
        if (expandAll) {
          const n = new Set(prev)
          if (next) n.add(key)
          else n.delete(key)
          return n
        }
        // Expand One: at most one open; closing the open key → zero expanded
        if (next) return new Set([key])
        if (prev.has(key)) return new Set()
        return prev
      })
    },
    [expandAll],
  )

  const expandAllSections = useCallback(() => {
    setExpandedKeys(new Set(sectionKeys))
  }, [sectionKeys])

  const collapseAllSections = useCallback(() => {
    setExpandedKeys(new Set())
  }, [])

  return {
    isExpanded,
    onExpandedChange,
    expandAllSections,
    collapseAllSections,
    showBulkChrome: !!expandAll,
    setExpandedKeys,
    expandedKeys,
  }
}
