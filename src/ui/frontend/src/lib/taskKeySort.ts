/** Lexicographic task_key order (Python sorted() / SQLite ORDER BY task_key). Not locale-sensitive. */
export function compareTaskKeys(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0
}

export function sortedTaskKeys(keys: Iterable<string>): string[] {
  return [...keys].sort(compareTaskKeys)
}
