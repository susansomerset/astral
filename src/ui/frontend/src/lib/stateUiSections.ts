export const LEGACY_STATE_LABEL_SUFFIX = " (legacy — not in current manifest)"

export function legacyStateSectionLabel(state: string): string {
  return `${state.replace(/_/g, " ")}${LEGACY_STATE_LABEL_SUFFIX}`
}

/** States present on rows but not listed in the manifest vocabulary for this view. */
export function unmappedJobStates(rows: Array<{ state: string }>, knownStates: Iterable<string>): string[] {
  const known = new Set(knownStates)
  const extra = new Set<string>()
  for (const row of rows) {
    if (row.state && !known.has(row.state)) extra.add(row.state)
  }
  return [...extra].sort()
}
