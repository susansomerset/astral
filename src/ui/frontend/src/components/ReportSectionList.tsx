import { useEffect, useMemo, type ReactNode } from "react"
import CollapsiblePanel from "./CollapsiblePanel"
import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"

export type ReportSectionDef = {
  section_id: string
  nav_label: string
  default_expanded: boolean
}

export type ReportSectionListProps = {
  sections: readonly ReportSectionDef[]
  /** Body for one section — AST-948 passes empty/null; siblings replace. */
  renderSection: (sectionId: string) => ReactNode
  /** Optional slot above the stack (e.g. Artifacts Generate/Cancel strip). */
  leading?: ReactNode
}

/** Expand-All collapsible section stack for Recommended Job Report tabs. */
export default function ReportSectionList({
  sections,
  renderSection,
  leading,
}: ReportSectionListProps) {
  const sectionKeys = useMemo(() => sections.map(s => s.section_id), [sections])
  const { isExpanded, onExpandedChange, setExpandedKeys } = useSectionExpandPolicy({
    expandAll: true,
    sectionKeys,
  })

  // Seed open sections from default_expanded whenever the section set / defaults change.
  const defaultKey = useMemo(
    () => sections.map(s => `${s.section_id}:${s.default_expanded ? "1" : "0"}`).join("|"),
    [sections],
  )
  useEffect(() => {
    setExpandedKeys(new Set(sections.filter(s => s.default_expanded).map(s => s.section_id)))
  }, [defaultKey, sections, setExpandedKeys])

  return (
    <div className="recommended-report-section-list">
      {leading}
      {sections.map(section => (
        <CollapsiblePanel
          key={section.section_id}
          label={section.nav_label}
          expanded={isExpanded(section.section_id)}
          onExpandedChange={next => onExpandedChange(section.section_id, next)}
        >
          {renderSection(section.section_id)}
        </CollapsiblePanel>
      ))}
    </div>
  )
}
