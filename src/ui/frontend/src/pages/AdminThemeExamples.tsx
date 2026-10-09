import { useEffect, useState, type CSSProperties } from "react"
import { ConfidenceBullets } from "../components/ConfidenceBullets"
import { getUiConfig, loadUiConfig } from "../lib/uiConfig"

// AST-2042: fixed sample, rendered once per registered palette. Built from the real shared
// classes (not look-alikes) so a token change shows here exactly as it does in the app.
const GRADES = ["A", "B", "C", "D", "F", "X"]
const SAMPLE_ROWS = [
  { company: "Acme Robotics", title: "Staff Engineer", grade: "A" },
  { company: "Globex", title: "Engineering Manager", grade: "C" },
]

export default function AdminThemeExamples() {
  const [, forceUpdate] = useState(0)
  useEffect(() => { loadUiConfig(() => forceUpdate(n => n + 1)) }, [])
  const themes = getUiConfig()?.themes
  const gradeSets = getUiConfig()?.theme_example_grade_sets

  if (!themes) return <p className="theme-examples-status">Loading...</p>

  return (
    <div className="theme-examples">
      <h1 className="dep-title">Theme Examples</h1>
      <div className="theme-examples-grid">
        {/* Registry order; each panel's data-theme scopes that palette's tokens to the panel. Read-only: no API writes. */}
        {Object.entries(themes).map(([id, theme]) => (
          <section key={id} className="theme-examples-panel" data-theme={id}>
            <h2 className="theme-examples-label">{theme.label}</h2>

            <div className="theme-examples-row">
              <span className="nav-link active">Ready</span>
              <span className="nav-link">Review</span>
              <span className="nav-link disabled">Applied</span>
            </div>

            <div className="theme-examples-row">
              <button type="button" className="btn primary">Save</button>
              <button type="button" className="btn primary in-flight">Generating</button>
              <button type="button" className="btn secondary">Cancel</button>
              <button type="button" className="btn danger">Delete</button>
            </div>

            <div className="list-page-table-wrap">
              <table className="list-page-table">
                <thead>
                  <tr><th>Company</th><th>Title</th><th>Grade</th></tr>
                </thead>
                <tbody>
                  {SAMPLE_ROWS.map(r => (
                    <tr key={r.company}>
                      <td>{r.company}</td>
                      <td>{r.title}</td>
                      <td><span className={`grade-dot dot-${r.grade.toLowerCase()}`}>{r.grade}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="dep-field">
              <label className="dep-field-label">Full Name</label>
              <input className="dep-input" readOnly value="Ada Lovelace" />
            </div>
            <div className="dep-field">
              <label className="dep-field-label">Timezone</label>
              <select className="dep-input dep-select" defaultValue="pacific">
                <option value="eastern">Eastern</option>
                <option value="pacific">Pacific</option>
              </select>
            </div>
            <div className="dep-field">
              <label className="dep-toggle">
                <input type="checkbox" defaultChecked />
                <span className="dep-toggle-label">Enabled</span>
              </label>
            </div>

            <div className="theme-examples-row">
              {GRADES.map(g => (
                <span key={g} className="theme-examples-grade">
                  <span className={`grade-dot dot-${g.toLowerCase()}`}>{g}</span>
                  <ConfidenceBullets confidence={3} />
                </span>
              ))}
            </div>

            {gradeSets && (
              <div className="theme-examples-grade-options">
                <span className="theme-examples-grade-options-label">Grade color options</span>
                {Object.entries(gradeSets).map(([gid, set]) => (
                  <div key={gid} className="theme-examples-grade-option">
                    {/* Inline custom properties override this panel's grade tokens for this row only. */}
                    <div className="theme-examples-row" style={set.tokens as CSSProperties}>
                      <span className="theme-examples-grade-option-name">{set.label}</span>
                      {GRADES.map(g => (
                        <span key={g} className={`grade-dot dot-${g.toLowerCase()}`}>{g}</span>
                      ))}
                    </div>
                    {/* Compact sample: Recommended Job List markup (buildPhaseListGradeRow, letterless gradeDot). */}
                    <div className="recommended-list-phase-grade-row" style={set.tokens as CSSProperties}>
                      {GRADES.map(g => (
                        <span key={g}><span className={`grade-dot dot-${g.toLowerCase()} grade-dot-letterless`} /></span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="toast toast-success toast-visible">Profile saved</div>
            <div className="toast toast-error toast-visible">Save failed</div>
            <div className="toast toast-info toast-visible">Copied to clipboard</div>

            <div className="modal-card">
              <div className="modal-header"><h2 className="modal-title">Confirm</h2></div>
              <div className="modal-body">Discard unsaved changes?</div>
              <div className="modal-footer">
                <button type="button" className="btn secondary">Keep editing</button>
                <button type="button" className="btn danger">Discard</button>
              </div>
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
