import { RUBRIC_DEFAULT_IMPORTANCE } from "../lib/rubricDisplay"

interface LabeledTextAreaProps {
  label: string
  value: string
  onChange: (value: string) => void
  onLabelChange?: (label: string) => void
  code?: string
  onCodeChange?: (code: string) => void
  /** Rubric criterion importance (1–10); shown next to Code when setter provided (AST-359). */
  importance?: number
  onImportanceChange?: (value: number) => void
  /** Freeze parent rail order while importance dropdown is focused (avoid row jump while picking). */
  onImportanceFocus?: () => void
  onImportanceBlur?: () => void
  placeholder?: string
  disabled?: boolean
  className?: string
  /** Omit title row when an outer shell (e.g. CollapsiblePanel) already shows the label. */
  hideTitle?: boolean
}

export default function LabeledTextArea({
  label, value, onChange, onLabelChange, code, onCodeChange,
  importance, onImportanceChange, onImportanceFocus, onImportanceBlur,
  placeholder, disabled, className, hideTitle,
}: LabeledTextAreaProps) {
  const impVal =
    typeof importance === "number" && importance >= 1 && importance <= 10
      ? importance
      : RUBRIC_DEFAULT_IMPORTANCE

  return (
    <>
      {onCodeChange ? (
        <div className="artifact-criterion-meta-row">
          <label className="artifact-criterion-field artifact-criterion-field-code">
            <span className="artifact-criterion-field-label">Code</span>
            <input
              type="text"
              maxLength={2}
              value={code || ""}
              onChange={e => onCodeChange(e.target.value.toUpperCase())}
              placeholder="XX"
              style={{ fontFamily: "monospace", fontSize: 14 }}
            />
          </label>
          {onImportanceChange != null && (
            <label className="artifact-criterion-field artifact-criterion-field-importance">
              <span className="artifact-criterion-field-label">Importance</span>
              <select
                value={String(impVal)}
                title="Importance (1–10)"
                aria-label="Importance"
                onFocus={() => onImportanceFocus?.()}
                onBlur={() => onImportanceBlur?.()}
                onChange={e => onImportanceChange(Number(e.target.value))}
              >
                {Array.from({ length: 10 }, (_, j) => j + 1).map(n => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </label>
          )}
          {!hideTitle && (
            <label className="artifact-criterion-field artifact-criterion-field-grow">
              {/* Align editable title input with Code/Importance row bottoms (no extra caption vs SideTabPanel) */}
              <span className="artifact-criterion-field-label" aria-hidden>{"\u00a0"}</span>
              <input
                className="side-tab-heading side-tab-heading-editable"
                value={label}
                onChange={e => onLabelChange?.(e.target.value)}
              />
            </label>
          )}
        </div>
      ) : !hideTitle ? (
        <h3 className="side-tab-heading">{code ? `${label} (${code})` : label}</h3>
      ) : null}
      <textarea
        className={className ?? "dep-input dep-textarea side-tab-textarea"}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder ?? `Enter ${label.toLowerCase()}…`}
        disabled={disabled}
      />
    </>
  )
}
