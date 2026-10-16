/** One row of an AST-2067 version map; `position` is 1 = oldest. */
export interface VersionEntry {
  created_at: string
  current: number
  position: number
}

/** Version map keyed by row uuid (artifact_uuid / rubric_vector_uuid). */
export type VersionMap = Record<string, VersionEntry>

/**
 * Current position + neighbor uuids. Order comes from `position` only — the API's JSON keys
 * arrive sorted by uuid, not chronologically (AST-2067).
 */
// eslint-disable-next-line react-refresh/only-export-components -- pure helper shared by both editors with the control
export function versionNavState(versions: VersionMap) {
  const ids = Object.keys(versions)
  const cur = ids.find(id => versions[id].current === 1)
  const position = cur ? versions[cur].position : 0
  const at = (p: number) => ids.find(id => versions[id].position === p) ?? null
  return { position, total: ids.length, backUuid: at(position - 1), forwardUuid: at(position + 1) }
}

interface ArtifactVersionNavProps {
  position: number
  total: number
  onBack: () => void
  onForward: () => void
  disabled?: boolean
}

/** Shared back/forward arrows + "N of M" for every versioned editor (patt.artifact.ui-consistency). */
export default function ArtifactVersionNav({
  position,
  total,
  onBack,
  onForward,
  disabled = false,
}: ArtifactVersionNavProps) {
  if (total === 0) return null
  // No current row (should not happen) → indicator only, no moves.
  const off = disabled || position < 1
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, marginRight: 8 }}>
      <button
        type="button"
        className="icon-control"
        aria-label="Previous version"
        title="Previous version"
        disabled={off || position <= 1}
        onClick={onBack}
      >
        ←
      </button>
      <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
        {position} of {total}
      </span>
      <button
        type="button"
        className="icon-control"
        aria-label="Next version"
        title="Next version"
        disabled={off || position >= total}
        onClick={onForward}
      >
        →
      </button>
    </span>
  )
}
