import { type ReactNode, useEffect, useState } from "react"
import LabeledTextArea from "./LabeledTextArea"

export interface SideTab {
  id: string
  label: string
  content: string
  code?: string
  /** 1–10 rubric vector importance (AST-359); omit on non-rubric tabs. */
  importance?: number
}

interface SideTabPanelProps {
  tabs: SideTab[]
  editable?: boolean
  minTabs?: number
  maxTabs?: number
  onChange?: (tabs: SideTab[]) => void
  /** When provided, renders custom content for a tab instead of LabeledTextArea. */
  renderContent?: (tabId: string) => ReactNode
  /** Custom rail label (e.g. grade dots on Recommended report phase tabs). */
  renderTabLabel?: (tab: SideTab) => ReactNode
}

let _nextId = 0
function genId() { return `st_${Date.now()}_${_nextId++}` }

export default function SideTabPanel({
  tabs,
  editable = false,
  minTabs = 1,
  maxTabs = 15,
  onChange,
  renderContent,
  renderTabLabel,
}: SideTabPanelProps) {
  const [activeId, setActiveId] = useState(tabs[0]?.id ?? "")
  const [editingId, setEditingId] = useState<string | null>(null)

  // Sync activeId if tabs array is replaced (e.g. candidate switch without remount)
  useEffect(() => {
    if (tabs.length > 0 && !tabs.find(t => t.id === activeId)) {
      setActiveId(tabs[0].id)
    }
  }, [tabs, activeId])

  const activeTab = tabs.find(t => t.id === activeId) ?? tabs[0]

  function updateTab(id: string, patch: Partial<SideTab>) {
    onChange?.(tabs.map(t => t.id === id ? { ...t, ...patch } : t))
  }

  function moveTab(idx: number, dir: -1 | 1) {
    const target = idx + dir
    if (target < 0 || target >= tabs.length) return
    const next = [...tabs]
    ;[next[idx], next[target]] = [next[target], next[idx]]
    onChange?.(next)
  }

  function removeTab(id: string) {
    if (tabs.length <= minTabs) return
    const next = tabs.filter(t => t.id !== id)
    if (activeId === id) setActiveId(next[0]?.id ?? "")
    onChange?.(next)
  }

  function addTab() {
    if (tabs.length >= maxTabs) return
    const t: SideTab = { id: genId(), label: "New Criterion", content: "" }
    onChange?.([...tabs, t])
    setActiveId(t.id)
    setEditingId(t.id)
  }

  return (
    <div className="side-tab-panel">
      <div className="side-tab-list">
        {tabs.map((tab, i) => (
          <div
            key={tab.id}
            className={`side-tab-item${tab.id === activeId ? " active" : ""}`}
            onClick={() => setActiveId(tab.id)}
          >
            {editable && editingId === tab.id ? (
              <input
                className="side-tab-rename"
                value={tab.label}
                onChange={e => updateTab(tab.id, { label: e.target.value })}
                onBlur={() => setEditingId(null)}
                onKeyDown={e => { if (e.key === "Enter") setEditingId(null) }}
                autoFocus
                onClick={e => e.stopPropagation()}
              />
            ) : (
              <span
                className="side-tab-label"
                onDoubleClick={editable ? () => setEditingId(tab.id) : undefined}
              >
                {(renderTabLabel ?? (t => t.label))(tab)}
              </span>
            )}
            {editable && (
              <span className="side-tab-controls" onClick={e => e.stopPropagation()}>
                <button disabled={i === 0} onClick={() => moveTab(i, -1)} title="Move up">▲</button>
                <button disabled={i === tabs.length - 1} onClick={() => moveTab(i, 1)} title="Move down">▼</button>
                <button disabled={tabs.length <= minTabs} onClick={() => removeTab(tab.id)} title="Remove">×</button>
              </span>
            )}
          </div>
        ))}
        {editable && tabs.length < maxTabs && (
          <button className="side-tab-add" onClick={addTab}>+ Add</button>
        )}
      </div>
      <div className="side-tab-content">
        {activeTab && (
          renderContent
            ? renderContent(activeTab.id)
            : <LabeledTextArea
                label={activeTab.label}
                value={activeTab.content}
                onChange={v => updateTab(activeTab.id, { content: v })}
                onLabelChange={editable ? v => updateTab(activeTab.id, { label: v }) : undefined}
                code={activeTab.code}
                onCodeChange={editable ? v => updateTab(activeTab.id, { code: v }) : undefined}
              />
        )}
      </div>
    </div>
  )
}
