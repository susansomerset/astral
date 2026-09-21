export type SectionExpandChromeProps = {
  onExpandAll: () => void
  onCollapseAll: () => void
}

/** Bulk expand/collapse row for Expand All policy pages. */
export default function SectionExpandChrome(props: SectionExpandChromeProps) {
  const { onExpandAll, onCollapseAll } = props
  return (
    <div className="section-expand-chrome">
      <button type="button" className="btn secondary" onClick={onExpandAll}>
        Expand all
      </button>
      <button type="button" className="btn secondary" onClick={onCollapseAll}>
        Collapse all
      </button>
    </div>
  )
}
