import { useRef, useState, useEffect, useCallback, useMemo, type CSSProperties } from "react"

interface TokenTextareaProps {
  value: string
  onChange: (value: string) => void
  tokens: string[]
  rows?: number
  style?: CSSProperties
  placeholder?: string
  className?: string
}

export default function TokenTextarea({
  value, onChange, tokens, rows = 14, style, placeholder, className,
}: TokenTextareaProps) {
  const ref = useRef<HTMLTextAreaElement>(null)
  const [show, setShow] = useState(false)
  const [filter, setFilter] = useState("")
  const [sel, setSel] = useState(0)
  // cursor position where {$ starts
  const [triggerPos, setTriggerPos] = useState(-1)

  const filtered = useMemo(() => tokens.filter(t => t.startsWith(filter.toUpperCase())), [tokens, filter])

  const dismiss = useCallback(() => {
    setShow(false)
    setFilter("")
    setTriggerPos(-1)
    setSel(0)
  }, [])

  // Check for {$ trigger on every change / cursor move
  const checkTrigger = useCallback(() => {
    const ta = ref.current
    if (!ta) return
    const pos = ta.selectionStart
    const text = ta.value.substring(0, pos)
    // Find the last {$ before cursor that hasn't been closed with }
    const lastOpen = text.lastIndexOf("{$")
    if (lastOpen === -1) { dismiss(); return }
    const afterTrigger = text.substring(lastOpen + 2)
    // If there's a } between {$ and cursor, the token is already closed
    if (afterTrigger.includes("}")) { dismiss(); return }
    // Only allow uppercase letters and underscores in partial match
    if (!/^[A-Z_]*$/.test(afterTrigger)) { dismiss(); return }
    setTriggerPos(lastOpen)
    setFilter(afterTrigger)
    setSel(0)
    setShow(true)
  }, [dismiss])

  // Insert selected token, replacing the partial {$... text
  function insertToken(token: string) {
    const ta = ref.current
    /* v8 ignore next -- @preserve */
    if (!ta || triggerPos < 0) return
    const before = value.substring(0, triggerPos)
    const after = value.substring(ta.selectionStart)
    const inserted = `{$${token}}`
    onChange(before + inserted + after)
    dismiss()
    // Restore focus and cursor after React re-render
    requestAnimationFrame(() => {
      ta.focus()
      const newPos = triggerPos + inserted.length
      ta.setSelectionRange(newPos, newPos)
    })
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (!show || filtered.length === 0) return
    if (e.key === "ArrowDown") {
      e.preventDefault()
      setSel(s => Math.min(s + 1, filtered.length - 1))
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      setSel(s => Math.max(s - 1, 0))
    } else if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault()
      insertToken(filtered[sel])
    } else if (e.key === "Escape") {
      e.preventDefault()
      dismiss()
    }
  }

  // Close dropdown on outside click
  useEffect(() => {
    if (!show) return
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.parentElement?.contains(e.target as Node)) dismiss()
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [show, dismiss])

  return (
    <div style={{ position: "relative" }}>
      <textarea
        ref={ref}
        className={className}
        value={value}
        onChange={e => { onChange(e.target.value); setTimeout(checkTrigger, 0) }}
        onKeyUp={checkTrigger}
        onKeyDown={handleKeyDown}
        onClick={checkTrigger}
        rows={rows}
        style={{ fontFamily: "monospace", fontSize: 13, resize: "vertical", ...style }}
        placeholder={placeholder}
      />
      {show && filtered.length > 0 && (
        <div style={{
          position: "absolute", top: 0, left: 0, right: 0,
          maxHeight: 180, overflowY: "auto",
          background: "var(--bg-elevated)", border: "1px solid var(--border)",
          borderRadius: 4, zIndex: 100,
          boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
        }}>
          {filtered.map((token, i) => (
            <div
              key={token}
              onMouseDown={e => { e.preventDefault(); insertToken(token) }}
              style={{
                padding: "5px 10px", cursor: "pointer",
                fontFamily: "monospace", fontSize: 12,
                background: i === sel ? "var(--bg-card)" : "transparent",
                color: i === sel ? "var(--accent-gold)" : "var(--text-secondary)",
              }}
            >
              {"{$"}{token}{"}"}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
