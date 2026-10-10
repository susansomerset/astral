/** AST-2128: the one grade mark every page renders. Accessible name = grade letter on every
 *  layout; the shape SVG ships undisplayed until the Shapes themes' CSS (AST-2129) reveals it. */

// Parent-brief geometry on a 0 0 100 100 viewBox, keyed by grade letter.
// X is a stroke-only cross — the theme CSS strokes it; the path itself has no fill intent.
const GRADE_SHAPE_PATHS: Record<string, string> = {
  A: "M50 6a44 44 0 1 0 0.01 0Z", // circle
  B: "M50 3L97 50L50 97L3 50Z", // diamond
  C: "M18 9H82Q91 9 91 18V82Q91 91 82 91H18Q9 91 9 82V18Q9 9 18 9Z", // rounded square
  D: "M50 6L96 90H4Z", // up triangle
  F: "M4 10H96L50 94Z", // down triangle
  X: "M20 20L80 80M80 20L20 80", // cross
}

export function GradeMark({
  grade,
  tooltip,
  letterless = false,
}: {
  grade: string
  tooltip?: string
  /** Compact colour-only mark (AST-1968): no visible letter, name still the grade. */
  letterless?: boolean
}) {
  const shape = GRADE_SHAPE_PATHS[grade.toUpperCase()]
  return (
    <span
      className={`grade-dot dot-${grade.toLowerCase()}${letterless ? " grade-dot-letterless" : ""}`}
      title={tooltip || undefined}
      role="img"
      aria-label={grade}
    >
      {/* display="none" is an SVG presentation attribute, so any App.css rule outranks it —
          Shapes themes show the SVG with plain CSS; every other theme keeps today's circle. */}
      {shape && (
        <svg viewBox="0 0 100 100" aria-hidden display="none">
          <path d={shape} />
        </svg>
      )}
      {letterless ? null : grade}
    </span>
  )
}

