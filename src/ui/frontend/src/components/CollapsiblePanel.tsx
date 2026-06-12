import { type ReactNode, useState } from "react"

/**
 * Collapsible row with distinct slots for label, read-only metadata, and interactive actions.
 * Single- vs multi-open is owned by the parent: pass expanded + onExpandedChange together for coordinated groups.
 */
export interface CollapsiblePanelProps {
  label: ReactNode
  metadata?: ReactNode
  actions?: ReactNode
  defaultExpanded?: boolean
  children: ReactNode
  expanded?: boolean
  onExpandedChange?: (next: boolean) => void
}

export default function CollapsiblePanel(props: CollapsiblePanelProps) {
  const {
    label,
    metadata,
    actions,
    defaultExpanded = false,
    children,
    expanded: expandedProp,
    onExpandedChange,
  } = props
  const controlled = expandedProp !== undefined && onExpandedChange !== undefined
  const [inner, setInner] = useState(!!defaultExpanded)
  const expanded = controlled ? expandedProp : inner
  const setEx = (next: boolean) => {
    if (controlled) onExpandedChange(next)
    else setInner(next)
  }

  return (
    <div className={"collapsible-panel" + (expanded ? " is-expanded" : "")}>
      <div className="collapsible-panel-header">
        <button
          type="button"
          className="collapsible-panel-chevron-btn"
          aria-expanded={expanded}
          aria-label={expanded ? "Collapse section" : "Expand section"}
          onClick={() => setEx(!expanded)}
        >
          {expanded ? "▼" : "▶"}
        </button>
        <div
          className="collapsible-panel-label-wrap"
          tabIndex={0}
          role="button"
          aria-expanded={expanded}
          aria-label="Section title; use chevron or Enter/Space to expand when collapsed"
          onClick={() => {
            if (!expanded) setEx(true)
          }}
          onKeyDown={e => {
            if (!expanded && (e.key === "Enter" || e.key === " ")) {
              e.preventDefault()
              setEx(true)
            }
          }}
        >
          {label}
        </div>
        {metadata != null && metadata !== false && (
          <div className="collapsible-panel-metadata">{metadata}</div>
        )}
        {actions != null && (
          <div className="collapsible-panel-actions" onClick={e => e.stopPropagation()}>
            {actions}
          </div>
        )}
      </div>
      <div className="collapsible-panel-body" hidden={!expanded}>
        {children}
      </div>
    </div>
  )
}
