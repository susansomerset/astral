import { useState, type ReactNode } from "react"
import { getByPath } from "./FormFields"
import LabeledTextArea from "./LabeledTextArea"

/* ---- TabBar: reusable tab-switching strip ---- */

export interface Tab<K extends string = string> {
  key: K
  label: string
}

interface TabBarProps<K extends string> {
  tabs: Tab<K>[]
  active: K
  onChange: (key: K) => void
}

export function TabBar<K extends string>({ tabs, active, onChange }: TabBarProps<K>) {
  return (
    <div className="tabbed-ta-bar">
      {tabs.map(t => (
        <button
          key={t.key}
          className={`tabbed-ta-tab${t.key === active ? " active" : ""}`}
          onClick={() => onChange(t.key)}
        >
          {t.label}
        </button>
      ))}
    </div>
  )
}

/* ---- TabbedTextArea: TabBar + plain textarea per tab ---- */

export interface TextTab {
  label: string
  key: string
  disabled?: boolean
  placeholder?: string
}

interface TabbedTextAreaProps {
  tabs: TextTab[]
  values: Record<string, unknown>
  onChange: (key: string, value: string) => void
  customPanels?: Record<string, ReactNode>
}

export default function TabbedTextArea({ tabs, values, onChange, customPanels }: TabbedTextAreaProps) {
  const [active, setActive] = useState(0)
  const tab = tabs[active]
  const barTabs = tabs.map((t, i) => ({ key: String(i), label: t.label }))
  const custom = customPanels?.[tab.key]

  return (
    <div>
      <TabBar tabs={barTabs} active={String(active)} onChange={k => setActive(Number(k))} />
      {custom ?? (
        <LabeledTextArea
          label={tab.label}
          value={String(getByPath(values, tab.key) ?? "")}
          onChange={v => onChange(tab.key, v)}
          disabled={tab.disabled}
          placeholder={tab.placeholder}
          className="dep-input dep-textarea tabbed-ta-textarea"
        />
      )}
    </div>
  )
}
