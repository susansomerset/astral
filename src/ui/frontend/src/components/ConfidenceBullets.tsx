/** AST-357: five dots under a grade; active count = confidence (0–5). */
export function ConfidenceBullets({ confidence }: { confidence?: number }) {
  const n =
    typeof confidence === "number" && confidence >= 0 && confidence <= 5
      ? Math.floor(confidence)
      : 0
  return (
    <div className="confidence-bullets" aria-hidden>
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className={`confidence-bullet${i < n ? " confidence-bullet--on" : ""}`}
        />
      ))}
    </div>
  )
}
